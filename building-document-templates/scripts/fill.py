"""Fill a registered template with content and emit a finished document.

Resolves a template from the gallery by client + doc-type (or an explicit path),
reads a data JSON keyed by the manifest's field names, and renders:

  * text  fields -> the value is dropped in wherever ``{{ field }}`` appears.
  * list  fields -> if the placeholder is alone on a paragraph (a bullet/row), that
                    paragraph is *duplicated* once per item so you get real bullets,
                    not one line with commas. Otherwise the items are joined inline.

The template's layout, styles, logos and masters are never touched — only the
placeholder text changes. Optionally exports the result to PDF.

Usage:
    python scripts/fill.py --client acme --doc-type quarterly-review \
        --data content.json --out out/acme-q4.docx [--export-pdf]
    python scripts/fill.py --template path/to/template.pptx --manifest path/to/manifest.json \
        --data content.json --out out/deck.pptx
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

import common as C


def _wrap_docx(elem, parent):
    from docx.text.paragraph import Paragraph
    return Paragraph(elem, parent)


def _wrap_pptx(elem, parent):
    from pptx.text.text import _Paragraph
    return _Paragraph(elem, parent)


def expand_list(paragraph, tag, items, wrap):
    """Duplicate a bullet/row paragraph once per list item, preserving order.

    The original paragraph becomes item[0]; each further item is a deep copy of the
    pristine (still-tagged) paragraph inserted right after the previous one.
    """
    if not items:
        paragraph._p.getparent().remove(paragraph._p)
        return
    template_p = copy.deepcopy(paragraph._p)   # pristine copy (still holds the tag)
    parent = paragraph._parent
    C.replace_in_paragraph(paragraph, tag, str(items[0]))
    anchor = paragraph._p
    for item in items[1:]:
        clone = copy.deepcopy(template_p)
        anchor.addnext(clone)                  # insert immediately after anchor...
        anchor = clone                         # ...advance so the next stays in order
        C.replace_in_paragraph(wrap(clone, parent), tag, str(item))


def _fill_row_element(tr, columns, item):
    """Replace each column field's {{ tag }} inside one <w:tr> clone from `item`
    (a dict keyed by the column field names). Preserves each cell's formatting."""
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    for p in tr.iter(qn("w:p")):
        para = Paragraph(p, None)
        for col in columns:
            val = item.get(col, "") if isinstance(item, dict) else ""
            C.replace_in_paragraph(para, C.placeholder(col), "" if val is None else str(val))


def expand_row_groups(doc, row_groups, data):
    """Clone a table's template ROW once per data item — real repeating rows.

    A row_group is {name, columns:[field,...]}. The template row is the <w:tr>
    whose cells hold those column tags. `data[name]` is a list of dicts keyed by
    the column field names. Empty/missing -> the template row is removed (header
    stays). This is what paragraph-level list expansion cannot do (it stacks
    paragraphs inside one cell instead of adding rows)."""
    import copy
    for g in row_groups:
        name, columns = g["name"], g["columns"]
        items = data.get(name) or []
        if isinstance(items, dict):
            items = [items]
        tag0 = C.placeholder(columns[0])
        template_tr = None
        for tbl in C.all_docx_tables(doc):
            for row in tbl.rows:
                if any(tag0 in c.text for c in row.cells):
                    template_tr = row._tr
                    break
            if template_tr is not None:
                break
        if template_tr is None:
            continue
        if not items:
            template_tr.getparent().remove(template_tr)
            continue
        pristine = copy.deepcopy(template_tr)     # still-tagged copy for the clones
        _fill_row_element(template_tr, columns, items[0])
        anchor = template_tr
        for item in items[1:]:
            clone = copy.deepcopy(pristine)
            anchor.addnext(clone)
            anchor = clone
            _fill_row_element(clone, columns, item)


def _is_empty(value):
    """Absent/None/blank/empty-list all count as 'no value supplied'."""
    return value is None or value == "" or value == []


def fill_paragraphs(paragraphs, data, fields, wrap):
    """Apply the manifest's fields to every paragraph.

    A REQUIRED field with no value is left as its ``{{ tag }}`` on purpose — it is
    NOT blanked. That way `validate.py`'s leftover-tag check fails the document
    instead of silently shipping a blank cell/bullet. An OPTIONAL field with no
    value fills blank (text) or drops the line (list). Returns (missing_required set,
    types dict).
    """
    types = {f["name"]: f.get("type", "text") for f in fields}
    required = {f["name"]: f.get("required", True) for f in fields}
    missing = {f["name"] for f in fields
               if required[f["name"]] and _is_empty(data.get(f["name"]))}

    # List expansion first (it restructures paragraphs), then plain text replacement.
    for name, ftype in types.items():
        if ftype != "list" or name in missing:   # missing+required -> leave the tag
            continue
        tag = C.placeholder(name)
        items = data.get(name) or []
        if isinstance(items, str):
            items = [items]
        # Snapshot: expansion mutates the tree, so collect target paragraphs first.
        targets = [p for p in paragraphs if C.para_text(p).strip() == tag]
        if targets:
            for p in targets:
                expand_list(p, tag, items, wrap)
        else:
            # Placeholder shares a line with other text -> join inline.
            joined = "; ".join(str(i) for i in items)
            for p in paragraphs:
                C.replace_in_paragraph(p, tag, joined)

    return missing, types


def render(fmt, template_path, data, manifest, out_path):
    fields = manifest["fields"]
    row_groups = manifest.get("row_groups", [])
    if fmt == "docx":
        from docx import Document
        doc = Document(str(template_path))
        # Row-group expansion FIRST — it clones <w:tr> rows, restructuring tables
        # before the paragraph-level passes run over the (new) paragraph set.
        if row_groups:
            expand_row_groups(doc, row_groups, data)
        paras = list(C.iter_docx_paragraphs(doc))
        wrap = _wrap_docx
        saver = doc
    else:
        from pptx import Presentation
        prs = Presentation(str(template_path))
        paras = list(C.iter_pptx_paragraphs(prs))
        wrap = _wrap_pptx
        saver = prs

    missing, types = fill_paragraphs(paras, data, fields, wrap)

    # Text pass (re-collect because list expansion changed the paragraph set).
    if fmt == "docx":
        paras = list(C.iter_docx_paragraphs(saver))
    else:
        paras = list(C.iter_pptx_paragraphs(saver))
    for name, ftype in types.items():
        if ftype == "list" or name in missing:    # missing+required -> leave the tag
            continue
        val = data.get(name, "")
        tag = C.placeholder(name)
        for p in paras:
            C.replace_in_paragraph(p, tag, "" if val is None else str(val))

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    saver.save(str(out))

    # Fill tags that live in cover-page / data-bound property parts (docProps +
    # customXml). These drive the cover title/subtitle/date/author and are not in
    # the body runs, so they need a separate pass over the saved package.
    prop_pairs = []
    for f in fields:
        name = f["name"]
        if name in missing:                     # leave the tag so validate.py fails
            continue
        val = data.get(name)
        if f.get("type", "text") == "list":
            items = val if isinstance(val, list) else ([val] if val else [])
            val = "; ".join(str(i) for i in items)
        prop_pairs.append((C.placeholder(name), "" if val is None else str(val)))
    C.patch_property_parts(out, out, C.ordered_replacer(prop_pairs))

    # SmartArt text tags live in the diagram parts (data + cached drawing), not in body
    # runs — fill them there too (no-op where the template has no SmartArt tags).
    C.patch_smartart_parts(out, out, C.ordered_replacer(prop_pairs))

    # Swap image/logo slots: {media_part: new_image_path} from image-type fields whose
    # data value is a path. Unset image slots keep the original picture.
    image_map = {f["media_part"]: data[f["name"]]
                 for f in fields
                 if f.get("type") == "image" and f.get("media_part")
                 and data.get(f["name"])}
    if image_map:
        C.swap_media_parts(out, out, image_map)
    return missing


def export_pdf(docx_or_pptx: Path):
    """Best-effort PDF export via LibreOffice; prints guidance if unavailable."""
    out_dir = docx_or_pptx.resolve().parent
    for exe in ("libreoffice", "soffice"):
        try:
            subprocess.run([exe, "--headless", "--convert-to", "pdf",
                            "--outdir", str(out_dir), str(docx_or_pptx)],
                           check=True, capture_output=True)
            print(f"PDF exported: {docx_or_pptx.with_suffix('.pdf')}")
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    print("NOTE: LibreOffice not found — open the file and Save As PDF, or install "
          "LibreOffice for headless export.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--client")
    ap.add_argument("--doc-type")
    ap.add_argument("--template", help="Explicit template path (bypasses the registry)")
    ap.add_argument("--manifest", help="Manifest for an explicit --template")
    ap.add_argument("--data", required=True, help="JSON of field_name -> value")
    ap.add_argument("--out", required=True)
    ap.add_argument("--export-pdf", action="store_true")
    args = ap.parse_args()

    if args.template:
        template_path = Path(args.template)
        man_path = Path(args.manifest) if args.manifest else template_path.parent / "manifest.json"
        manifest = C.load_manifest(man_path)
    elif args.client and args.doc_type:
        template_path, manifest = C.find_template(args.client, args.doc_type)
    else:
        sys.exit("Provide --client/--doc-type, or --template (+--manifest).")

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    fmt = manifest["format"]

    # Slides don't reflow: a value much longer than the field's example is the main
    # overflow risk (there is no autofit). Warn early; the render/vision pass decides.
    if fmt == "pptx":
        for f in manifest["fields"]:
            if f.get("type", "text") != "text":
                continue
            ex, val = f.get("example") or "", data.get(f["name"])
            if ex and isinstance(val, str) and len(val) > max(60, int(len(ex) * 1.5)):
                print(f"WARNING: '{f['name']}' is {len(val)} chars (example: {len(ex)}) — "
                      f"slide text does not autofit; check the rendered pages for overflow.")

    missing = render(fmt, template_path, data, manifest, args.out)

    print(f"Filled {manifest['template_id']} -> {args.out}")
    if args.export_pdf:
        export_pdf(Path(args.out))
    if missing:
        # The tags for these fields were left in the document on purpose, so
        # validate.py will also fail. Exit non-zero so an automated pipeline stops.
        print(f"ERROR: no value supplied for required fields {sorted(missing)}; "
              f"their placeholders were left in {args.out} — do not ship it.")
        sys.exit(2)


if __name__ == "__main__":
    main()

"""Smoke-test the bundled document scripts against generated fixtures.

Proves the scripts in THIS repo actually run and behave as documented (right exit
codes, right verdicts) — reproducibly, in CI or by hand. Generates real .docx/.pptx
fixtures and asserts each outcome. Focused on the Document Template Suite: the
templatize→build→fill→validate engine (incl. the document-property/cover pass and
image/logo slots), the docx/pptx producer validators, and the extractors.

Run from the repo root:
    python skill-builder/scripts/smoke_test_scripts.py

Requires: python-docx, python-pptx, pillow. Exits non-zero on any failure.
"""
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
results = []


def run(script_rel, *args, env=None):
    """Run a bundled script; return (exit_code, parsed_json_or_None)."""
    script = ROOT / script_rel
    if not script.exists():
        return None, None
    run_env = None
    if env:
        run_env = os.environ.copy()
        run_env.update({k: str(v) for k, v in env.items()})
    proc = subprocess.run([sys.executable, str(script), *[str(a) for a in args]],
                          capture_output=True, text=True, env=run_env)
    data = None
    try:
        data = json.loads(proc.stdout)
    except (ValueError, json.JSONDecodeError):
        pass
    return proc.returncode, data


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")


def make_fixtures(tmp):
    from docx import Document
    from pptx import Presentation
    from pptx.util import Inches
    from PIL import Image as PILImage

    # docx: bad (leftover tag) and good (heading + para)
    b = Document(); b.add_paragraph("Hi {{ name }}"); b.save(tmp / "bad.docx")
    g = Document(); g.add_heading("Title", 1); g.add_paragraph("ok"); g.save(tmp / "good.docx")

    # docx to templatize: a Label:value line + a bullet (text + list fields)
    t = Document(); t.add_heading("Weekly Update", 1)
    lp = t.add_paragraph(); lp.add_run("Client: ").bold = True; lp.add_run("Globex")
    t.add_paragraph("First achievement", style="List Bullet")
    t.save(tmp / "tmpl_src.docx")

    # docx whose title lives ONLY in a document property (data-bound cover analogue)
    tp = Document(); tp.add_heading("Body Heading", 1)
    tp.core_properties.title = "PROPCODE Report"
    tp.save(tmp / "tmpl_props.docx")

    # docx with an embedded image -> an image SLOT to swap
    PILImage.new("RGB", (120, 60), (10, 20, 200)).save(tmp / "orig_logo.png")
    PILImage.new("RGB", (120, 60), (200, 20, 10)).save(tmp / "new_logo.png")
    ti = Document(); ti.add_heading("Doc With Image", 1)
    ti.add_picture(str(tmp / "orig_logo.png")); ti.save(tmp / "tmpl_img.docx")

    # pptx: bad (lorem) and good
    pb = Presentation(); s = pb.slides.add_slide(pb.slide_layouts[0])
    s.shapes.title.text = "Lorem ipsum"; pb.save(tmp / "bad.pptx")
    pg = Presentation(); sg = pg.slides.add_slide(pg.slide_layouts[0])
    sg.shapes.title.text = "Real Title"; pg.save(tmp / "good.pptx")

    # pptx to templatize: title + TWO independent bullet lists (no interleave)
    pd = Presentation(); sd = pd.slides.add_slide(pd.slide_layouts[1])
    sd.shapes.title.text = "Globex"
    body = sd.placeholders[1].text_frame
    body.text = "Alpha one"; body.add_paragraph().text = "Alpha two"
    box = sd.shapes.add_textbox(Inches(1), Inches(4), Inches(5), Inches(2)).text_frame
    box.text = "Beta one"; box.add_paragraph().text = "Beta two"
    pd.save(tmp / "tmpl_deck.pptx")


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        make_fixtures(tmp)

        print("processing-word-documents/extract_docx.py")
        rc, d = run("processing-word-documents/scripts/extract_docx.py", tmp / "good.docx")
        check("docx extractor returns markdown", rc == 0 and d and "Title" in d["markdown"])

        print("authoring-word-documents/validate_docx.py")
        rc, d = run("authoring-word-documents/scripts/validate_docx.py", tmp / "bad.docx")
        check("docx validator fails on unfilled tag", rc == 1 and d and d["status"] == "FAILED")
        rc, d = run("authoring-word-documents/scripts/validate_docx.py", tmp / "good.docx")
        check("docx validator passes clean doc", rc == 0 and d and d["status"] == "OK")

        print("processing-powerpoint-files/extract_pptx.py")
        rc, d = run("processing-powerpoint-files/scripts/extract_pptx.py", tmp / "good.pptx")
        check("pptx extractor returns slides", rc == 0 and d and d["slides"][0]["title"] == "Real Title")

        print("building-powerpoint-decks/validate_pptx.py")
        rc, d = run("building-powerpoint-decks/scripts/validate_pptx.py", tmp / "bad.pptx")
        check("pptx validator fails on lorem", rc == 1 and d and d["status"] == "FAILED")
        rc, d = run("building-powerpoint-decks/scripts/validate_pptx.py", tmp / "good.pptx")
        check("pptx validator passes clean deck", rc == 0 and d and d["status"] == "OK")

        print("processing-documents/detect_type.py")
        rc, d = run("processing-documents/scripts/detect_type.py", tmp / "good.docx")
        check("type detector identifies docx", rc == 0 and d and d["detected_type"] == "docx")

        print("building-document-templates: templatize -> build -> fill -> validate")
        tdir = "building-document-templates/scripts"
        reg = tmp / "registry"
        env = {"TEMPLATE_REGISTRY": reg}
        rc, _ = run(f"{tdir}/templatize.py", "propose", "--file", tmp / "tmpl_src.docx",
                    "--out", tmp / "proposal.json")
        prop = json.loads((tmp / "proposal.json").read_text(encoding="utf-8")) if rc == 0 else {}
        names = {c["current_text"] for c in prop.get("candidates", [])}
        check("templatize propose extracts candidates", rc == 0 and "Globex" in names)
        (tmp / "reviewed.json").write_text(json.dumps({
            "format": "docx", "source_file": "tmpl_src.docx", "candidates": [
                {"current_text": "Globex", "suggest_name": "client_name",
                 "suggest_type": "text", "keep": "variable"},
                {"current_text": "First achievement", "suggest_name": "achievements",
                 "suggest_type": "list", "keep": "variable"},
            ]}), encoding="utf-8")
        rc, _ = run(f"{tdir}/templatize.py", "build", "--file", tmp / "tmpl_src.docx",
                    "--fields", tmp / "reviewed.json", "--client", "acme",
                    "--doc-type", "weekly", "--created", "2026-07-13", env=env)
        man = reg / "acme" / "weekly" / "manifest.json"
        check("templatize build registers template + manifest", rc == 0 and man.exists())
        (tmp / "content.json").write_text(json.dumps({
            "client_name": "Initech", "achievements": ["Alpha", "Beta", "Gamma"]}),
            encoding="utf-8")
        out_docx = tmp / "filled.docx"
        rc, _ = run(f"{tdir}/fill.py", "--client", "acme", "--doc-type", "weekly",
                    "--data", tmp / "content.json", "--out", out_docx, env=env)
        check("fill produces output document", rc == 0 and out_docx.exists())
        rc, d = run(f"{tdir}/validate.py", out_docx)
        check("validate passes a fully filled document", rc == 0 and d and d["status"] == "OK")
        rc, d = run(f"{tdir}/validate.py", tmp / "bad.docx")
        check("validate fails on a leftover template tag", rc == 1 and d and d["status"] == "FAIL")
        from docx import Document as _Doc
        filled_texts = [p.text for p in _Doc(str(out_docx)).paragraphs]
        check("fill expands a list field into separate items",
              all(x in filled_texts for x in ("Alpha", "Beta", "Gamma")))

        # missing REQUIRED field -> tag stays, fill exits non-zero, validate FAILs
        (tmp / "partial.json").write_text(json.dumps({"achievements": ["only this"]}),
                                          encoding="utf-8")
        out_partial = tmp / "partial.docx"
        rc, _ = run(f"{tdir}/fill.py", "--client", "acme", "--doc-type", "weekly",
                    "--data", tmp / "partial.json", "--out", out_partial, env=env)
        check("fill exits non-zero when a required field is missing",
              rc != 0 and out_partial.exists())
        rc, d = run(f"{tdir}/validate.py", out_partial)
        check("validate fails when a required field was left unfilled",
              rc == 1 and d and d["status"] == "FAIL")

        # document-property / data-bound-cover pass
        rc, _ = run(f"{tdir}/templatize.py", "propose", "--file", tmp / "tmpl_props.docx",
                    "--out", tmp / "props_prop.json")
        pp = json.loads((tmp / "props_prop.json").read_text(encoding="utf-8")) if rc == 0 else {}
        has_prop = any(c.get("source") == "property" and c["current_text"] == "PROPCODE Report"
                       for c in pp.get("candidates", []))
        check("propose surfaces a document-property (cover) candidate", rc == 0 and has_prop)
        (tmp / "props_reviewed.json").write_text(json.dumps({
            "format": "docx", "source_file": "tmpl_props.docx", "candidates": [
                {"current_text": "PROPCODE Report", "suggest_name": "doc_title",
                 "suggest_type": "text", "keep": "variable", "source": "property"},
            ]}), encoding="utf-8")
        rc, _ = run(f"{tdir}/templatize.py", "build", "--file", tmp / "tmpl_props.docx",
                    "--fields", tmp / "props_reviewed.json", "--client", "acme",
                    "--doc-type", "propdoc", "--created", "2026-07-13", env=env)
        tmpl_core = zipfile.ZipFile(reg / "acme" / "propdoc" / "template.docx").read("docProps/core.xml").decode()
        check("build injects the tag into docProps/core.xml", rc == 0 and "{{ doc_title }}" in tmpl_core)
        (tmp / "props_content.json").write_text(json.dumps({"doc_title": "NEWCODE Report"}),
                                                encoding="utf-8")
        out_props = tmp / "props_filled.docx"
        rc, _ = run(f"{tdir}/fill.py", "--client", "acme", "--doc-type", "propdoc",
                    "--data", tmp / "props_content.json", "--out", out_props, env=env)
        filled_core = zipfile.ZipFile(out_props).read("docProps/core.xml").decode()
        check("fill replaces the property tag with the value",
              rc == 0 and "NEWCODE Report" in filled_core and "{{ doc_title }}" not in filled_core)

        # image/logo slot: templatize an embedded image, fill with a replacement
        rc, _ = run(f"{tdir}/templatize.py", "propose", "--file", tmp / "tmpl_img.docx",
                    "--out", tmp / "img_prop.json")
        ip = json.loads((tmp / "img_prop.json").read_text(encoding="utf-8")) if rc == 0 else {}
        imgc = [c for c in ip.get("candidates", []) if c.get("source") == "image"]
        check("propose surfaces an image slot", rc == 0 and len(imgc) >= 1)
        if imgc:
            media = imgc[0]["media_part"]
            (tmp / "img_reviewed.json").write_text(json.dumps({
                "format": "docx", "source_file": "tmpl_img.docx", "candidates": [
                    {"current_text": imgc[0]["current_text"], "suggest_name": "logo",
                     "suggest_type": "image", "keep": "variable", "source": "image",
                     "media_part": media},
                ]}), encoding="utf-8")
            rc, _ = run(f"{tdir}/templatize.py", "build", "--file", tmp / "tmpl_img.docx",
                        "--fields", tmp / "img_reviewed.json", "--client", "acme",
                        "--doc-type", "imgdoc", "--created", "2026-07-13", env=env)
            orig = zipfile.ZipFile(reg / "acme" / "imgdoc" / "template.docx").read(media)
            (tmp / "img_content.json").write_text(
                json.dumps({"logo": str(tmp / "new_logo.png")}), encoding="utf-8")
            out_img = tmp / "img_filled.docx"
            rc, _ = run(f"{tdir}/fill.py", "--client", "acme", "--doc-type", "imgdoc",
                        "--data", tmp / "img_content.json", "--out", out_img, env=env)
            swapped = zipfile.ZipFile(out_img).read(media)
            check("fill swaps the image-slot media bytes",
                  rc == 0 and swapped != orig and len(swapped) > 0)

        # PPTX round-trip with TWO independent list fields
        rc, _ = run(f"{tdir}/templatize.py", "propose", "--file", tmp / "tmpl_deck.pptx",
                    "--out", tmp / "deck_prop.json")
        (tmp / "deck_reviewed.json").write_text(json.dumps({
            "format": "pptx", "source_file": "tmpl_deck.pptx", "candidates": [
                {"current_text": "Globex", "suggest_name": "client_name",
                 "suggest_type": "text", "keep": "variable"},
                {"current_text": "Alpha one", "suggest_name": "list_a",
                 "suggest_type": "list", "keep": "variable"},
                {"current_text": "Alpha two", "keep": "remove"},
                {"current_text": "Beta one", "suggest_name": "list_b",
                 "suggest_type": "list", "keep": "variable"},
                {"current_text": "Beta two", "keep": "remove"},
            ]}), encoding="utf-8")
        rc, _ = run(f"{tdir}/templatize.py", "build", "--file", tmp / "tmpl_deck.pptx",
                    "--fields", tmp / "deck_reviewed.json", "--client", "acme",
                    "--doc-type", "deck", "--created", "2026-07-13", env=env)
        deck_man = reg / "acme" / "deck" / "manifest.json"
        check("pptx templatize build registers template + manifest",
              rc == 0 and deck_man.exists())
        (tmp / "deck_content.json").write_text(json.dumps({
            "client_name": "Initech", "list_a": ["A1", "A2", "A3"],
            "list_b": ["B1", "B2"]}), encoding="utf-8")
        out_pptx = tmp / "deck_filled.pptx"
        rc, _ = run(f"{tdir}/fill.py", "--client", "acme", "--doc-type", "deck",
                    "--data", tmp / "deck_content.json", "--out", out_pptx, env=env)
        check("pptx fill produces output deck", rc == 0 and out_pptx.exists())
        rc, d = run(f"{tdir}/validate.py", out_pptx)
        check("pptx validate passes a fully filled deck",
              rc == 0 and d and d["status"] == "OK")
        from pptx import Presentation as _Prs
        deck_texts = [p.text for sl in _Prs(str(out_pptx)).slides
                      for sh in sl.shapes if sh.has_text_frame
                      for p in sh.text_frame.paragraphs]
        check("pptx fill expands two independent list fields",
              all(x in deck_texts for x in ("A1", "A2", "A3", "B1", "B2")))

    passed = sum(1 for _, ok in results if ok)
    print(f"\n{passed}/{len(results)} checks passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()

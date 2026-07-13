---
name: building-document-templates
description: Turn a client's existing Word (.docx) or PowerPoint (.pptx) file into a reusable, governed template — same layout, fonts, logos and styles, with the variable content swapped for placeholders — then fill it to produce consistent future documents from data. Use when the user asks to "create a template", "templatize this document/deck", "make this reusable", "build a standard format", or "produce the same kind of document again just with new content". Ships a tested engine (templatize → registry → fill → validate) plus placeholder/governance conventions, not just an empty copy.
---

# Building Document Templates

## Scope
Turn a real example document into a reusable **template + manifest**, register it in
a **gallery** keyed by client and document type, and **fill** it on demand to produce
consistent future documents. Covers Word (`.docx`) and PowerPoint (`.pptx`) end to
end. Excel and PDF are handled at the edges — see **Format support** below. The
one-off document itself is built with the relevant authoring skill; brand comes from
[producing-branded-documents](../producing-branded-documents/SKILL.md).

## Core principle: preserve + inject, never rebuild
A client's file **already is the template** — its layout, fonts, logos, slide masters
and styles are exactly what "consistent" means. Templatizing keeps that file intact
and only **swaps the variable text for `{{ placeholder }}` tags**. Never rebuild the
layout by hand and never re-solve OOXML internals. Filling later touches only the
placeholder text, so every produced document looks identical to the client's original.

## The engine
```text
scripts/
  templatize.py   # client file -> proposes fixed/variable split -> emits template + manifest
  fill.py         # template + data JSON -> finished document (+ optional --export-pdf)
  validate.py     # gate: no leftover tags, structure preserved
  render_pages.py # render docx/pptx/pdf -> one PNG per page for VISION inspection
  registry.py     # browse the gallery: list / find / show templates
  common.py       # format detection, placeholders, manifest I/O, registry paths, docProps
registry/                              # the template gallery (version-controlled)
  <client>/<doc-type>/
      template.docx|pptx               # the client's file, with placeholders
      manifest.json                    # fields, types, guidance, owner, version, changelog
```
Point `$TEMPLATE_REGISTRY` at a shared folder to keep the gallery outside the repo.

Dependencies: `pip install python-docx python-pptx` (already used across the office
skills). PDF export additionally needs LibreOffice (or Save-As-PDF from the app).

## Why "assisted" (propose → confirm → build)
One example can't reveal what's boilerplate and what changes each time — "Acme Q3 2026"
could mean client=Acme, quarter=Q3, or both. So templatize is **two steps**: it
*proposes* a fixed/variable split for a human or agent to confirm, then *builds*. Do
not promise fully-automatic detection; the confirm step is where correctness comes from.

## Workflow
```
Progress:
- [ ] 0. See it: render the source page-by-page and inspect layout, structure & branding
- [ ] 1. Propose: extract candidate variable fields from the example file
- [ ] 2. Review: confirm WITH THE USER what to preserve vs. vary; mark keep/name/type
- [ ] 3. Build: inject placeholders and register the template + manifest
- [ ] 4. Fill: supply data keyed by the manifest fields -> finished document
- [ ] 5. Validate: no leftover tags, structure intact (required)
- [ ] 6. QA by vision: render the OUTPUT page-by-page, compare to source, fix drift
```

**Step 0 — See it (vision).** Before deciding anything, *look* at the document —
`render_pages.py` gives you one PNG per page/slide to Read:
```bash
python scripts/render_pages.py client_qbr.docx --out-dir pages/   # prints PNG paths
```
Inspect each page for the layout, section structure, table styles, logos, colours and
the header/footer — the visual identity is what "consistent" means and what the
template must preserve. python-docx/pptx show text, not layout; only the render does.

**Step 1 — Propose.**
```bash
python scripts/templatize.py propose --file client_qbr.docx --out proposal.json
```
Reads the file and writes every candidate value (deduped — the same client name in
five places becomes one field), with a heuristic name (from `Label: value` lines) and
a suggested keep/type.

**Step 2 — Review (the assisted step). Confirm the preserve list with the user.**
Before editing, ask what must be *preserved* (brand colours, logos, cover, header/
footer, mandatory clauses, table styles) and what *varies* each time — then use their
answer to set the split. Offer to swap logos/images per client (see image placeholders
below). Edit `proposal.json`; for each candidate set:
- `keep`: `variable` (filled each time), `fixed` (boilerplate that stays), or `remove`
  (drop this line — use for surplus example bullets/rows a `list` field regenerates).
- `suggest_name`: a clean `snake_case` field name.
- `suggest_type`: `text` (default) or `list` (a repeating bullet/row).

For a repeating list, mark **one** representative line `variable` + `list` and mark the
other example lines `remove`.

**Step 3 — Build.**
```bash
python scripts/templatize.py build --file client_qbr.docx --fields proposal.json \
    --client globex --doc-type quarterly-review \
    --owner you@co.com --created 2026-07-13
```
Injects placeholders (longest values first, so `Q3 2026` is tagged before a bare `Q3`),
removes the lines you marked, and writes `template.<fmt>` + `manifest.json` into the
gallery. Pass `--created` explicitly (scripts have no clock).

**Step 4 — Fill.** Discover what a template needs, then fill it:
```bash
python scripts/registry.py show --client globex --doc-type quarterly-review
python scripts/fill.py --client globex --doc-type quarterly-review \
    --data content.json --out out/initech-q4.docx [--export-pdf]
```
`content.json` is `{field_name: value}` (a `list` field takes a JSON array — it expands
into real bullets/rows, not one comma-joined line). The document *content* can come
from a writing skill (e.g. `writing-status-reports`); this engine renders it into the
locked format.

**Step 5 — Validate (required).**
```bash
# note: the registry slugifies the doc-type, so the folder is quarterly_review (underscore)
python scripts/validate.py out/initech-q4.docx --template registry/globex/quarterly_review/template.docx
```
Fails with specific messages on any leftover `{{ tag }}`, empty content, or changed
structure (section/slide count). **Do not ship anything that isn't `"status": "OK"`.**

**Step 6 — QA by vision (required for anything shipped to a client).** `validate.py`
reads text; it cannot see layout. Render the output and Read every page:
```bash
python scripts/render_pages.py out/initech-q4.docx --out-dir out/pages/
```
Compare page-by-page against the Step 0 source renders: is the **cover** updated (not
just the body — cover text is often a data-bound property, see below), do tables/
bullets fit, are logos and colours intact, did a long value overflow? A clean
`validate.py` **plus** a clean vision pass is the real ship gate. This pass is what
catches a stale cover that the text-only validator reports as `OK`.

## Format support
| Format | Templatize | How |
|---|---|---|
| **Word `.docx`** | Yes | Run-aware in-place injection; list fields expand paragraphs. **Also fills document properties** (`docProps/core.xml` + `customXml` CoverPageProperties) so **data-bound cover pages** update, not just the body. |
| **PowerPoint `.pptx`** | Yes | Same engine over slides, shapes, tables and speaker notes (cover text is usually a normal text run and is handled directly). |
| **Excel `.xlsx`** | Not yet | Needs a different cell + *data-region* model (rows that grow). Planned; out of scope for this suite. |
| **PDF** | As **output**, not a source | Fill a `.docx`/`.pptx` then `--export-pdf`. An arbitrary flat PDF has no reliable structure to templatize. Filling existing **AcroForm** PDFs is planned. |

## Principles
1. **Preserve + inject** — the client's file is the template; only text changes.
2. **Separate fixed from variable** — confirmed by a human, not guessed blindly.
3. **Obvious, single-convention placeholders** (`{{ field }}`) — never shipped filled wrong.
4. **A manifest travels with every template** — a future agent fills from it without re-reading the whole document.
5. **Governed** — one gallery, one owner, versioned, with a change log.

## Common mistakes
- **Rebuilding the layout by hand** instead of injecting into the client's own file — drift and wasted effort.
- **Trusting auto-detection** — always confirm the fixed/variable split.
- **Leaving surplus example bullets** when creating a `list` field (mark them `remove`).
- **Placeholders that look like real content** — users ship `{{ client_name }}` or, worse, a leftover real client name.
- **No owner/version** — the template forks and rots.
- **Shipping without `validate.py`** — the one gate that catches unfilled tags.

## Validation checklist
- [ ] Fixed vs. variable confirmed by a person, not just the heuristic.
- [ ] Placeholders use the one `{{ field }}` convention; none look like real content.
- [ ] `list` fields expand to real bullets/rows; surplus examples removed.
- [ ] Manifest has every field with type, example, and guidance.
- [ ] No leftover real client data from the source example.
- [ ] Owner, version, change log present; `validate.py` returns `OK`.

## Edge cases
- **Same value in many places** (client name) → one field fills all occurrences by design.
- **Overlapping values** (`Q3` inside `Q3 2026`) → build tags longest-first to avoid clobbering.
- **Value spans formatting runs** → build consolidates into the first run so the tag stays intact; build warns if a value matched 0 times (check it manually).
- **Legal/regulated templates** → keep mandatory clauses `fixed`; control who owns the gallery entry.
- **Multi-variant (regions/languages)** → separate `doc-type` entries under one client, not divergent private copies.

## Images & logos (per-client swap)
Pictures are swappable too — the same "preserve the frame, inject the content" idea
applied to images. `propose` lists every embedded picture as an **image slot** (one per
media part; a logo reused on 30 slides is one slot that swaps everywhere), named by a
size/aspect heuristic (`logo_*`, `background_*`, `image_*`). Mark the ones a client should
replace `keep: variable`; leave furniture `fixed`. `build` records each as an `image`
field with its `media_part`; `fill` re-encodes the supplied asset to the slot's original
format and swaps the media bytes in place, so **references and geometry (position/size/
crop) are preserved**. Provide a path in the fill data (`{"client_logo": "acme.png"}`);
omit it to keep the original.
- **The heuristic name is a guess** — verify which slot is which by the Step-0 render (or
  map a shape to its media part) before marking it variable; a wide logo can look like a
  "background". The Step-6 vision pass confirms the swapped image sits right (not
  stretched, adequate text contrast over a new background).
- A vision/image model can **generate** a missing asset to a slot's spec, then fill it in.
- Needs `pip install pillow`. See [references/engine-design.md](references/engine-design.md).

## Related skills
- [authoring-word-documents](../authoring-word-documents/SKILL.md), [building-powerpoint-decks](../building-powerpoint-decks/SKILL.md) — build the one-off the template is learned from.
- [producing-branded-documents](../producing-branded-documents/SKILL.md) — brand/logo rendering pipeline.
- [running-mail-merge](../running-mail-merge/SKILL.md), [automating-document-generation](../automating-document-generation/SKILL.md) — bulk fills from a data source.
- [processing-word-documents](../processing-word-documents/SKILL.md), [processing-powerpoint-files](../processing-powerpoint-files/SKILL.md) — extract content to feed a fill.
- Detection heuristics, placeholder rules, per-format notes: [references/engine-design.md](references/engine-design.md).

## Examples
**Input:** "A client sent this quarterly review deck — set it up so we produce the same
deck each quarter with new numbers."
**Output:** `templatize.py propose` on the deck → confirm client name, period, and
metrics as variable and the bullet list as a `list` field → `build` registers
`globex/board-deck` (template.pptx + manifest.json) → next quarter, `registry.py show`
reveals the fields, `fill.py` renders a new deck from `content.json`, `validate.py`
confirms no placeholder was missed. Same masters, fonts, and layout every time — only
the content changes. See [examples/README.md](examples/README.md) for the full run.

# Template engine — design & internals

Reference for how `templatize`/`fill`/`validate` work under the hood. Read this when
extending the engine or debugging a fill. Everyday use is covered in `SKILL.md`.

## Placeholder convention
One form everywhere: `{{ field_name }}` (optional inner whitespace; names are
`[a-z0-9_]`). There is **no loop or branch syntax in the template**. Repetition
(bullets, table rows) is driven by the *manifest field type* at fill time, not by tags
in the document. This is deliberate: templatize learns from a **single example**, so
asking it to synthesize control-flow (`{% for %}`) would be fragile. Keeping templates
to bare value tags makes DOCX and PPTX behave identically and keeps every tag human-
readable.

## Run-aware, text-based replacement
Both python-docx and python-pptx expose paragraphs whose `.runs` each carry a settable
`.text`. `common.replace_in_paragraph`:
1. **Fast path** — if the value sits inside a single run, edit that run's text (keeps
   its formatting exactly).
2. **Slow path** — if the value spans several runs, concatenate them into the first run
   (keeping the first run's formatting) and blank the rest, so the injected `{{ tag }}`
   always lands in **one** run. A tag split across runs is the classic failure that
   silently breaks in-place fills; consolidation prevents it.

Replacement is **replace-all**: a client name appearing in five places becomes one
field that fills all five. Build injects **longest values first** so `Q3 2026` is
tagged before a bare `Q3` could clobber part of it.

## Assisted fixed/variable detection (`templatize propose`)
A single example is ambiguous, so `propose` only *suggests*; a human/agent confirms.
Heuristics:
- **`Label: value` lines** → the value is the candidate, the label stays fixed, and the
  field name is derived from the label (`Client:` → `client`).
- **Dates / money / quarters** → suggested names `date` / `amount` / `period`.
- **Long paragraphs** (> ~140 chars) default to `keep=fixed` (prose/boilerplate).
- Candidates are **deduped by exact text** (replace-all semantics) with an occurrence
  count and the surrounding context, so a reviewer can judge each one.

The reviewer sets `keep` ∈ {`variable`, `fixed`, `remove`}, a clean `snake_case`
`suggest_name`, and `suggest_type` ∈ {`text`, `list`}.

## List expansion (`fill`)
A `list` field's placeholder should sit **alone** on a paragraph (a bullet/row). At
fill time that paragraph is deep-copied once per item — the original becomes item 0 and
each further item is inserted immediately after the previous, preserving order and the
paragraph's style (so real bullets, not one comma-joined line). An empty list removes
the paragraph. If a `list` placeholder shares a line with other text, items are joined
inline as a fallback.

Turning N example bullets into one `list` field therefore needs the **other** example
bullets marked `keep=remove` so build deletes them; the single remaining tagged
paragraph is what fill duplicates.

## The manifest
`manifest.json` is the contract that lets a future fill happen without re-reading the
document:
```json
{
  "template_id": "globex/quarterly_review",
  "client": "globex", "doc_type": "quarterly_review",
  "format": "docx", "template_file": "template.docx",
  "source_file": "client_qbr.docx",
  "version": "1.0.0", "owner": "you@co.com", "created": "2026-07-13",
  "changelog": ["2026-07-13 v1.0.0 templatized from client_qbr.docx"],
  "fields": [
    {"name": "client_name", "type": "text", "example": "Globex Corporation",
     "guidance": "Fills: Client", "required": true},
    {"name": "achievements", "type": "list", "example": "Launched the new analytics portal",
     "guidance": "", "required": true}
  ]
}
```
`example` is the value seen in the source — a ready-made sample for whoever fills it.

## The registry (gallery)
`registry/<client>/<doc-type>/` holds `template.<fmt>` + `manifest.json`. Client and
doc-type are slugified (`board-deck` → `board_deck`) consistently on write and lookup,
so `--doc-type board-deck` always resolves. Set `$TEMPLATE_REGISTRY` to relocate the
gallery to a shared, version-controlled folder outside the repo.

## Validation
`validate.py` gates a filled file: no leftover `{{ }}`/`{% %}` tags anywhere (body,
tables, headers/footers, slides, notes), non-empty content, and — when `--template` is
given — unchanged section count (docx) / slide count (pptx). Exit code is non-zero
unless `status == "OK"`.

## Format notes & roadmap
- **DOCX / PPTX** — fully supported (body, tables, headers/footers, speaker notes).
- **XLSX** — not yet. A spreadsheet template needs a different model: named cell
  placeholders plus *data regions* (a marked row that grows by N data rows). The
  run/paragraph engine here does not map onto cells. Planned as a separate `xlsx` path.
- **PDF** — a flat PDF has no reliable text structure to inject into, so it is **not a
  templatize source**. It is an **output**: fill a `.docx`/`.pptx`, then
  `fill.py --export-pdf` (LibreOffice headless). Filling existing **AcroForm** (fillable)
  PDFs by field name is a planned separate path.

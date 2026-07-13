---
name: processing-word-documents
description: Ingest and extract content from Microsoft Word files (.docx/.doc) — text with heading hierarchy, tables, lists, headers/footers, footnotes, comments, and tracked changes — into clean, structured, model-readable form (usually Markdown). Use when the user gives you a Word document to read, summarize, extract from, or convert, or asks to "read/parse this .docx", "pull the tables from this Word doc", or "get the content out of this document". For creating Word docs use authoring-word-documents. Produces faithful structured content, not a lossy text dump.
---

# Processing Word Documents

## Scope
Reading `.docx`/`.doc` files into faithful, structured content: heading hierarchy,
tables, lists, and the easily-missed parts (headers/footers, footnotes, comments,
tracked changes). Ingestion, not authoring ([authoring-word-documents](../authoring-word-documents/SKILL.md)).
Usually reached via [processing-documents](../processing-documents/SKILL.md).

## Purpose
Extract a Word document's real content *and* structure so downstream tasks work on
an accurate representation — preserving the heading tree and tables a naive text dump
would flatten and lose.

## When to use this skill
- "Read / parse / extract from this Word document (.docx/.doc)."
- "Pull the tables / headings / content out of this doc."
- Ingesting a Word file before summarizing, comparing, or analyzing it.

## When NOT to use this skill
- Creating/formatting a Word doc → [authoring-word-documents](../authoring-word-documents/SKILL.md).
- PDF/PowerPoint/Excel → the matching processing skill via [processing-documents](../processing-documents/SKILL.md).
- Diffing two versions → comparing-documents.

## Inputs
- The `.docx`/`.doc` file and what you need (full content, specific tables/sections, metadata).

## Outputs
- Structured content — Markdown with heading hierarchy, tables as Markdown/CSV, lists
  preserved — plus extracted metadata and a note on anything dropped or uncertain.

## Workflow
```
Progress:
- [ ] 1. Open with a proven library (python-docx) or convert (mammoth/pandoc → Markdown)
- [ ] 2. Extract body: map Word heading styles to a heading hierarchy
- [ ] 3. Extract tables faithfully (rows/cols; note merged cells)
- [ ] 4. Capture headers/footers, footnotes, comments, tracked changes if relevant
- [ ] 5. Extract images/embedded objects if the task needs them
- [ ] 6. Verify against the source; note anything lossy (check the fidelity report)
```

The bundled `scripts/extract_docx.py` does steps 1–4 deterministically and emits a
fidelity report — prefer it over an ad-hoc read:

```bash
python scripts/extract_docx.py path/to/file.docx   # Markdown + tables + fidelity
```

**Step 1 — proven tooling, benchmarked to how strong models do it:** for structure
use `python-docx`; for a clean Markdown rendering use `mammoth` or `pandoc`. `.doc`
(legacy binary) must be converted to `.docx` first (LibreOffice/`textract`). Don't
hand-parse OOXML. **Step 2 — headings are structure:** map Heading 1/2/3 styles to
`#`/`##`/`###` so the hierarchy survives; fake (bold) headings won't carry over —
note that. **Step 3 — tables:** extract as real tables; flag merged/nested cells,
which are where extraction silently corrupts. **Step 4 — the missed parts:** headers/
footers, footnotes, comments, and *tracked changes* often carry meaning (e.g. review
docs) — decide whether to include accepted text, original, or both, and say which.

## Principles
1. **Structure over raw text** — preserve the heading tree and tables.
2. **Use proven libraries;** never hand-parse OOXML.
3. **Convert `.doc`→`.docx` first;** legacy binary isn't directly parseable.
4. **Don't forget headers/footers/footnotes/comments/tracked changes.**
5. **Verify tables;** merged cells and nesting corrupt silently.
6. **State what was dropped** (images, styling, uncertain tables).

## Decision framework
- **Need clean prose?** Convert to Markdown (mammoth/pandoc).
- **Need precise structure/tables/fields?** python-docx element walk.
- **Review document?** Decide tracked-changes handling explicitly (accepted vs. original).
- **`.doc` legacy?** Convert to `.docx` first, then process.

## Common mistakes
- **Flattening to raw text** — losing headings and tables.
- **Treating bold text as headings** (or missing that real headings use styles).
- **Silent table corruption** from merged/nested cells.
- **Ignoring tracked changes/comments** in a document that has them.
- **Hand-parsing OOXML** instead of using a library.
- **Failing on `.doc`** because it wasn't converted first.

## Validation checklist
- [ ] Opened with a proven library / converted cleanly.
- [ ] Heading hierarchy preserved (styles → levels).
- [ ] Tables extracted faithfully; merged cells flagged.
- [ ] Headers/footers, footnotes, comments, tracked changes handled per the task.
- [ ] Images/objects extracted if needed.
- [ ] Output spot-checked against the source; losses noted.

## Edge cases
- **Heavily formatted/legal docs:** multilevel numbering and defined terms — preserve numbering.
- **Forms with content controls:** read control values, not just visible text.
- **Corrupt/password-protected:** need repair/password; report if blocked.
- **Very large docs:** process by section; watch memory.
- **Equations/SmartArt/charts:** often not extractable as text — flag them.

## Related skills
- [processing-documents](../processing-documents/SKILL.md) — the router that reaches this.
- [authoring-word-documents](../authoring-word-documents/SKILL.md) — the authoring counterpart.
- summarizing-documents, comparing-documents.

## Examples
**Input:** "Extract the content and tables from this 40-page contract (.docx)."
**Output:** Converted to Markdown preserving the clause heading hierarchy; each
schedule table extracted as a Markdown table (two merged-cell tables flagged for
review); defined-term numbering preserved; tracked changes present — delivered as
accepted-text with a note that 6 unresolved changes exist and can be surfaced.

## Scripts
- [scripts/extract_docx.py](scripts/extract_docx.py) — **run this** to ingest a
  `.docx` deterministically. Emits Markdown (heading styles → `#`/`##`/`###`, tables as
  Markdown, paragraphs and tables in document order), structured `tables`, and a
  `fidelity` block flagging tracked changes, comments, footnotes, images, headers/
  footers, and merged table cells. Requires `python-docx`. Convert `.doc` → `.docx` first.

## Automation opportunities
- The bundled extractor already does `docx → Markdown + tables(JSON)`; chain its output
  into summarizing-documents or comparing-documents.

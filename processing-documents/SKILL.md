---
name: processing-documents
description: Identify a document's type and ingest it into clean, faithful, model-readable text, structure, and tables — routing PDF, Word, PowerPoint, Excel, CSV, and scanned/image files to the correct extraction method. Use when the user hands over a file to read, summarize, extract from, analyze, or convert and you need its contents — "read/ingest/parse this document", "what's in this file", "extract the text/tables/data". The document-awareness entry point to run BEFORE any content task. Produces extracted content with structure preserved and fidelity/confidence noted.
---

# Processing Documents

## Scope
The entry point for turning *any* incoming document into content a model can
reliably work with: detect the type, choose the right ingestion method, extract
text/structure/tables faithfully, and route to the format specialists. Reading and
routing — not authoring (see the `authoring-*`/`building-*` skills) or deep
single-format ops (those are the specialist skills below).

## Purpose
Prevent the most common quality failure in document work: acting on a document's
contents without ingesting it correctly. Establish document-type awareness first so
downstream tasks (summarize, extract, analyze, compare) run on accurate content.

## When to use this skill
- The user provides a file to read/summarize/extract/analyze/convert.
- "Read / ingest / parse this document", "what's in this file", "pull the tables/data".
- Mixed or unknown file types, or a batch of documents to process.
- Before any content task that depends on a document you haven't ingested.

## When NOT to use this skill
- Creating a new document → the matching `authoring-*` / `building-*` skill.
- You already have clean text and just need to act on it → the task skill (e.g. summarizing-documents).

## Inputs
- The file(s) and what you need from them (full text, specific fields, tables, structure).
- Any hint of type/quality (native vs. scanned, language).

## Outputs
- Faithful extracted content (text/markdown + tables + key structure/metadata),
  routed through the right specialist, with a note on fidelity and any
  low-confidence regions.

## Workflow
```
Progress:
- [ ] 1. Identify the file type (extension + magic bytes, not the name alone)
- [ ] 2. For PDFs, determine native-text vs. scanned
- [ ] 3. Route to the correct extraction method/skill
- [ ] 4. Extract preserving structure (headings, tables, order)
- [ ] 5. Verify the extraction against the source; note fidelity
- [ ] 6. Hand clean content to the downstream task
```

**Step 1 — detect, don't assume.** Confirm the real type by extension *and* signature
(a `.pdf` can be a scan; a `.xlsx` can be a renamed CSV). Run the bundled detector,
which reads magic bytes / container parts and returns the route:

```bash
python scripts/detect_type.py path/to/file   # -> detected_type + route_to (JSON)
``` **Step 2 — PDF text-layer
test:** if direct text extraction returns little/nothing, it's scanned → OCR.
**Step 3 — route** using the table below. **Step 5 — verify:** spot-check extracted
tables/numbers against the source; extraction is silently lossy (merged cells,
multi-column, reading order) — never trust it unchecked.

## Routing table
| Input | Route to |
|---|---|
| PDF with a text layer | processing-pdf-documents |
| Scanned PDF / image / photo of text | extracting-text-with-ocr |
| Word `.docx` / `.doc` | [processing-word-documents](../processing-word-documents/SKILL.md) |
| PowerPoint `.pptx` | [processing-powerpoint-files](../processing-powerpoint-files/SKILL.md) |
| Excel `.xlsx` / `.csv` | processing-excel-files |
| Plain text `.txt` / `.md` | Read directly |
| Unknown / other | Detect by signature; convert to a supported type; else report it can't be ingested |

## Principles
1. **Ingest before you reason.** Never act on a document's contents blind.
2. **Detect type by signature,** not just the extension.
3. **Preserve structure** — headings, tables, and order carry meaning.
4. **Verify extraction;** it's silently lossy.
5. **Report fidelity and confidence,** especially for scans/OCR.
6. **Route to the specialist;** this skill dispatches, it doesn't re-solve formats.

## Decision framework
- **Native text?** Direct extraction. **Scanned/image?** OCR first.
- **Need tables/data faithfully?** Use the format specialist, then verify cell-by-cell.
- **Batch/mixed types?** Detect + route per file; report per-file fidelity.
- **Corrupt/unsupported?** Say so; don't fabricate contents.

## Common mistakes
- **Trusting the extension** — processing a scan as if it had text (empty result).
- **Acting on un-ingested content** — summarizing a PDF you never actually read.
- **Losing tables/structure** by flattening to raw text.
- **No fidelity note** — passing lossy extraction downstream as if exact.
- **Re-implementing extraction** instead of routing to the specialist.

## Validation checklist
- [ ] File type confirmed by extension + signature.
- [ ] PDF native-vs-scanned determined; OCR applied if needed.
- [ ] Routed to the correct specialist skill.
- [ ] Structure (headings/tables/order) preserved.
- [ ] Extraction spot-checked against the source.
- [ ] Fidelity/confidence noted; low-confidence regions flagged.

## Edge cases
- **Mixed-content PDF (text + scanned pages):** OCR only the image pages.
- **Password-protected/encrypted:** need the password; respect restrictions.
- **Huge files:** stream/page-by-page; don't load whole into memory.
- **Multiple languages/scripts:** set language for OCR/extraction.
- **Renamed/mislabeled files:** the signature wins over the extension.

## Related skills
- Specialists: processing-pdf-documents, [processing-word-documents](../processing-word-documents/SKILL.md), [processing-powerpoint-files](../processing-powerpoint-files/SKILL.md), processing-excel-files, extracting-text-with-ocr.
- Downstream: summarizing-documents, comparing-documents.

## Examples
**Input:** "Summarize the attached report." (file is `report.pdf`)
**Output:** Detect PDF → test text layer (empty → it's scanned) → route to
extracting-text-with-ocr → extract text +
tables, flag two low-confidence figures → hand clean text to
summarizing-documents, noting the summary rests
on OCR with two figures to verify.

## Scripts
- [scripts/detect_type.py](scripts/detect_type.py) — **run this first.** Detects the
  true type by signature (magic bytes + OOXML container inspection), flags
  extension/signature mismatches, and returns the skill to route to. Stdlib only.

## Automation opportunities
- A single intake pipeline: detect → route → extract → validate → downstream task.
- Batch a folder of mixed files, emitting per-file extracted content + a fidelity report.

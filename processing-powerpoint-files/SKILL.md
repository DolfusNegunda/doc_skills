---
name: processing-powerpoint-files
description: Ingest and extract content from PowerPoint files (.pptx) — per-slide titles, body text in reading order, tables, speaker notes, and slide sequence — into clean, structured, model-readable form. Use when the user gives you a deck to read, summarize, or extract from, or asks to "read/parse this PowerPoint", "pull the text/notes from these slides", or "get the content out of this deck". For creating decks use building-powerpoint-decks. Produces faithful per-slide content including speaker notes, not just scraped text.
---

# Processing PowerPoint Files

## Scope
Reading `.pptx` files into faithful, structured content: per-slide title, body text
in correct reading order, tables, speaker notes, and slide order. Ingestion, not
authoring ([building-powerpoint-decks](../building-powerpoint-decks/SKILL.md)).
Usually reached via [processing-documents](../processing-documents/SKILL.md).

## Purpose
Extract what a deck actually communicates — including the speaker notes that carry
the real detail — organized by slide, so downstream tasks aren't working off a
jumbled scrape of text boxes.

## When to use this skill
- "Read / parse / extract from this PowerPoint (.pptx)."
- "Pull the text / speaker notes / tables from these slides."
- Ingesting a deck before summarizing or repurposing it.

## When NOT to use this skill
- Creating/designing a deck → [building-powerpoint-decks](../building-powerpoint-decks/SKILL.md).
- Other formats → the matching processing skill via [processing-documents](../processing-documents/SKILL.md).
- Story/narrative critique → reviewing-presentations.

## Inputs
- The `.pptx` file and what you need (all content, speaker notes, specific slides, tables).

## Outputs
- Structured per-slide content: `Slide N — title / body (in order) / tables / notes`,
  in slide sequence, plus extracted images if needed and a note on anything dropped.

## Workflow
```
Progress:
- [ ] 1. Open with python-pptx (proven library; don't hand-parse OOXML)
- [ ] 2. Iterate slides in order; per slide extract title + body text
- [ ] 3. Order text by shape position (top-to-bottom, left-to-right), not shape index
- [ ] 4. Extract tables and, crucially, speaker notes
- [ ] 5. Extract images/diagrams if the task needs them
- [ ] 6. Assemble in slide order; note un-extractable content (check fidelity)
```

The bundled `scripts/extract_pptx.py` does steps 1–4 deterministically (reading-order
sorted, notes included) and emits a fidelity block — prefer it over an ad-hoc read:

```bash
python scripts/extract_pptx.py path/to/deck.pptx   # per-slide JSON + fidelity
```

**Step 2–3 — reading order is the trap.** Shapes are stored in creation order, not
visual order; sort by position so the extracted text reads the way the slide does,
or the content comes out scrambled. **Step 4 — speaker notes are the goldmine:** the
on-slide text is often terse headlines while the notes hold the actual argument —
extract the notes, they're the most-missed and highest-value content. **Step 6 —
flag the un-extractable:** SmartArt, charts, grouped diagrams, and text baked into
images won't come out as text (OCR the image if needed) — say so.

## Principles
1. **Per-slide structure, in slide order.**
2. **Sort shapes by position** for correct reading order.
3. **Always extract speaker notes** — they carry the detail.
4. **Use python-pptx;** don't hand-parse OOXML.
5. **Flag un-extractable visuals** (SmartArt/charts/text-in-images).
6. **Tables as tables,** not flattened text.

## Decision framework
- **Need the argument, not just headlines?** Prioritize speaker notes.
- **Text baked into an image/diagram?** OCR it → extracting-text-with-ocr.
- **Data tables/charts?** Extract tables; note charts aren't text-extractable (get underlying data if available).
- **Repurposing to a doc?** Preserve slide order + notes as the narrative source.

## Common mistakes
- **Scrambled reading order** from using shape index instead of position.
- **Dropping speaker notes** — losing most of the substance.
- **Flattening tables** to text.
- **Silently missing SmartArt/chart/image text.**
- **Hand-parsing OOXML** instead of python-pptx.

## Validation checklist
- [ ] Slides processed in order; each labeled with its number/title.
- [ ] Body text in correct reading order (position-sorted).
- [ ] Speaker notes extracted.
- [ ] Tables preserved as tables.
- [ ] Images/diagrams handled or flagged (OCR where needed).
- [ ] Un-extractable content noted; output checked against the deck.

## Edge cases
- **Notes-heavy decks:** notes may exceed slide text — include fully.
- **Animation/build slides:** multiple overlapping text layers — capture all, note overlap.
- **Master/layout placeholders:** distinguish real content from template boilerplate.
- **Embedded video/audio:** not text; note presence.
- **Very large decks:** process in slide batches.

## Related skills
- [processing-documents](../processing-documents/SKILL.md) — the router that reaches this.
- [building-powerpoint-decks](../building-powerpoint-decks/SKILL.md) — the authoring counterpart.
- extracting-text-with-ocr, summarizing-documents.

## Examples
**Input:** "Summarize this 30-slide board deck."
**Output:** Per-slide extraction in order — title + position-sorted body + tables +
speaker notes (which held the real commentary); three data charts flagged as
non-extractable with a note to pull the source workbook; delivered to
summarizing-documents as slide-ordered content
so the summary follows the deck's actual argument.

## Scripts
- [scripts/extract_pptx.py](scripts/extract_pptx.py) — **run this** to ingest a `.pptx`
  deterministically. Emits per-slide JSON (title, position-sorted body, tables, speaker
  notes) + a fidelity block (slide/image counts, notes coverage). Requires `python-pptx`.

## Automation opportunities
- The bundled extractor already does `pptx → per-slide JSON (title/body/notes/tables)`;
  chain its output into summarization or a Word/report conversion.

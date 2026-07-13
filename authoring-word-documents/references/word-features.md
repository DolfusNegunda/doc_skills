# Word Feature How-To

Operational notes for the features that separate a professional .docx from a
typed one. Concept-level guidance — apply through the built-in docx capability,
not by editing OOXML.

## Contents
- Table of contents
- Section breaks
- Headers, footers, page numbers
- Fields and cross-references
- Figures and tables
- Accessibility
- Track changes and comments

## Table of contents
- Insert a TOC *field* built from Heading 1–3. It reads heading styles, so it only
  works if headings are styled.
- Update the field after any structural change. A TOC never reflects edits until updated.
- For long docs add a List of Figures / List of Tables built from Caption labels.

## Section breaks
Use section breaks (not page breaks) when you need to change, within one document:
orientation (portrait→landscape for a wide table), number of columns, page-number
format/restart, or different headers/footers. "Next Page" is the usual break type.

## Headers, footers, page numbers
- Different first page (title page with no number) and odd/even (mirrored) as needed.
- "Unlink from previous" a section's header/footer before giving it distinct content.
- Page numbers are fields — set format (1, i, A) per section.

## Fields and cross-references
- Cross-reference figures, tables, headings, and page numbers so they renumber on edit.
- Common fields: PAGE, NUMPAGES, DATE, TOC, SEQ (for captions), REF (cross-ref).
- Press update-all before final export; stale fields are the top review defect.

## Figures and tables
- Insert caption above tables, below figures. Caption label + SEQ field = auto number.
- Give tables a repeating header row and mark it as a header (accessibility + print).
- Keep table widths within page margins; use "autofit to window" and avoid fixed
  widths that overflow.

## Accessibility
- Real heading styles (screen-reader navigation).
- Alt text on every image and chart.
- Table header rows marked; avoid merged cells where possible.
- Meaningful hyperlink text (not "click here").
- Sufficient color contrast; never convey meaning by color alone.
- Set document language; run the accessibility checker before delivery.

## Track changes and comments
- For collaborative review, enable track changes; resolve or accept before final.
- Use comments for questions, not inline "TODO" text that can ship by accident.
- To compare two finished versions instead, see
  [../comparing-documents/SKILL.md](../../comparing-documents/SKILL.md).

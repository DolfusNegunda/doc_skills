# python-docx / OOXML Editing Patterns (Organization-Agnostic)

## Contents
- Design goal: one script, any organization's template
- Generic {{TOKEN}} replacement (paragraphs, tables, headers/footers, content controls)
- Locating repeating-list tables by heading text (not position)
- Safe run-aware text replacement
- Clearing multi-paragraph table cells
- Cloning table rows
- Swapping an entire table structure
- Logo swap (see companion file)
- Validation checklist after any edit

## Design goal: one script, any organization's template
The generation scripts in this repo's document-type skills must work **unmodified** against any organization's branded `.docx`, whether that template was copied from that organization's own real prior document or built from the shared generic neutral template.

Two techniques make this possible: (1) never hardcode a table's position — always locate it by the standardized heading text that precedes it, and (2) never hardcode a single-value field's location — always replace `{{TOKEN}}` placeholders generically across every place text can live in a `.docx` (paragraphs, table cells, headers/footers, and Word content controls).

## Generic {{TOKEN}} replacement (paragraphs, tables, headers/footers, content controls)
Some organizations' templates use Word's built-in "Cover Pages" gallery, which stores title/date text inside **content controls** (`w:sdt` elements) nested in floating text boxes — invisible to `doc.paragraphs`/`doc.tables`. A robust token-replacement pass must cover all four locations.

Use the generic replacement function implemented in `authoring-lessons-learned-docs/scripts/generate_lessons_learned.py` as the reference implementation.

## Locating repeating-list tables by heading text (not position)
Different organizations' templates will order sections differently, add extra sections, or use different table shapes. Never assume "the 3rd table is Positives." Instead, scan the document body in order and grab the first table that appears after a paragraph matching the section's standard heading text.

This works regardless of whether the organization's template uses Word's default `Heading 1/2/3` styles, custom numbered-heading styles, or even plain bold paragraphs — the match is on **text content**, not style.

## Safe run-aware text replacement
Word frequently splits one visible line across multiple `w:r` runs. Naive `paragraph.text = paragraph.text.replace(...)` collapses all runs into one and destroys formatting. Use a run-aware replacer.

## Clearing multi-paragraph table cells
Real-world table cells (e.g. a "Comment" cell holding a multi-bullet lesson) often contain **multiple paragraphs**, not one paragraph with line breaks. Replacing only `cell.paragraphs[0]`'s text leaves old paragraphs 2/3 behind. Always clear every paragraph beyond the first.

## Cloning table rows
To add N data rows to a table that ships with only one template data row, clone the template row's XML (preserves borders/shading/fonts).

## Swapping an entire table structure
Some sections support more than one valid table *shape* for the same content (e.g. a Lessons Learned "Deliverables" section might track proposal items with inline status notes, OR a simple document/status/notes list). Store each shape as a standalone `<w:tbl>` XML skeleton and swap the whole element in at generation time.

**Pitfall:** load skeletons with `docx.oxml.parse_xml`, never plain `lxml.etree.fromstring`, or later `table.rows` access will crash.

## Logo swap
See [logo-swap-procedure.md](logo-swap-procedure.md) for the full, organization-agnostic logo-swap code and its format-preservation rule.

## Validation checklist after any edit
- [ ] Re-open the saved file with `Document(output_path)`
- [ ] Print every table's rows and confirm no leftover source-document text remains in any cell
- [ ] Confirm each table's row count matches the input data length
- [ ] Extract `word/document.xml` from the saved `.docx` and search for the new title/date text to confirm token replacement reached the cover page
- [ ] Confirm the swapped logo's filename inside `word/media/` still uses the original required extension
- [ ] If deploying against a new organization's real template for the first time, run the heading-based lookup for every standard heading and confirm each one resolves before wiring up the full generation call

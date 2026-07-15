---
name: authoring-word-documents
description: Produce well-structured, professional Microsoft Word (.docx) documents — reports, manuals, contracts, proposals, and long-form docs — using styles, headings, tables of contents, sections, headers/footers, and cross-references. Use when the user asks to "create a Word doc", "write a report in Word", "format a .docx", generate a manual or contract, or needs a structured multi-page document. STEP 0 — before authoring anything, check the built-in template library (registry.py list): standard documents (business report, memo, meeting minutes, one-pager) exist as branded, fill-ready templates where you only write a content JSON — the safest path for any model. Author with python-docx only for bespoke documents.
---

# Authoring Word Documents

## Scope
Structured authoring of `.docx` files where layout, navigation, and consistency
matter. Covers document architecture (styles, headings, TOC, sections,
headers/footers, captions, cross-references) — not the prose craft (writing-reports)
or brand rendering (branding
comes from the shared brand packs — [../brands/README.md](../brands/README.md)).

## Purpose
Deliver a Word document a professional would accept without rework: every heading
uses a real style, the TOC updates itself, numbering is automatic, and the
structure survives edits.

## When to use this skill
- "Create/write a Word document / .docx" of more than a page.
- Reports, manuals, SOPs, contracts, proposals, whitepapers, handbooks.
- Documents needing a table of contents, numbered headings, or cross-references.
- Converting Markdown or plain text into a properly styled Word document.

## When NOT to use this skill
- Pure prose drafting with no formatting need → use the relevant writing skill.
- Data-heavy tabular output → engineering-excel-workbooks.
- Slides → [building-powerpoint-decks](../building-powerpoint-decks/SKILL.md).
- Fixed-layout final artifacts → processing-pdf-documents.

## Inputs
- Content (draft prose, Markdown, bullet outline, or a brief).
- Document type and intended audience.
- Any house template (`.dotx`) or brand spec; if none, use built-in styles.
- Requirements: TOC? page numbers? two columns? landscape tables? approvals block?

## Outputs
- A single `.docx` with: a style-driven heading hierarchy, an auto TOC (if
  requested), consistent body/caption/quote styles, headers/footers with page
  numbers, and figure/table numbering.
- A short changelog of structural decisions when converting from another format.

## Step 0 — Fill a built-in template before you build (decision gate)
The suite ships branded, fill-ready document templates in the document-template
registry — `business_report`, `memo`, `meeting_minutes`, `one_pager` — each with a
real style architecture, logo header, legal footer, and repeating table rows where
content repeats. If the requested document matches one, **do not author it**; run the
deterministic fill path (safe for any model, however small):

```bash
cd ../building-document-templates
python scripts/registry.py list                                          # what exists
python scripts/registry.py scaffold --builtin business-report --out content.json
# edit content.json (field-by-field guidance is printed by scaffold)
python scripts/fill.py --client _builtin --doc-type business_report --data content.json --out out.docx
python scripts/validate.py out.docx --template registry/_builtin/business_report/template.docx \
    --manifest registry/_builtin/business_report/manifest.json           # must be OK
python scripts/render_pages.py out.docx --out-dir pages/                 # vision pass, every page
```

The library is generated per brand pack by
[scripts/build_doc_library.py](scripts/build_doc_library.py) (see
[../brands/README.md](../brands/README.md)); externally sourced templates join it via
[../building-document-templates/references/external-intake.md](../building-document-templates/references/external-intake.md).
Continue below **only** when no template fits.

## Workflow
```
Progress:
- [ ] 0. Check the built-in library first (registry.py list) — fill, don't build, when a template fits
- [ ] 1. Confirm type, audience, length, and required structural features
- [ ] 2. Build the outline (heading hierarchy) before any prose
- [ ] 3. Apply named styles — never manual/direct formatting for structure
- [ ] 4. Add front matter (title, TOC) and back matter (appendix, glossary)
- [ ] 5. Insert headers/footers, page numbers, section breaks
- [ ] 6. Number and caption figures/tables; add cross-references
- [ ] 7. Validate against the checklist; update all fields
- [ ] 8. Validate & repair: run the validator, fix every error, re-run until clean
```

**Step 1 — Frame it.** Restate document type, audience, approximate length, and
which structural features are required. This prevents rework.

**Step 2 — Outline first.** Draft the full heading tree (H1/H2/H3) before writing
body text. The outline is the document; prose fills it.

**Step 3 — Style, don't format.** Map every element to a *named style* (Heading 1,
Heading 2, Normal, Caption, Quote, List Bullet). Direct formatting (bold a line to
fake a heading) breaks the TOC, navigation, and accessibility. Use the built-in
`docx` generation capability; do not hand-edit OOXML.

**Step 4 — Front & back matter.** Add title page/block, an auto-generating TOC
field, and any appendices, glossary, or references section.

**Step 5 — Sections & running heads.** Use section breaks to change orientation,
columns, or headers/footers per chapter. Add page numbers.

**Step 6 — Number & reference.** Caption figures and tables with sequence fields
("Figure 1", "Table 3"); use cross-references so numbers renumber automatically.

**Step 7 — Finalize.** Update all fields (TOC, cross-refs, numbering), run the
validation checklist, and hand off. Finish with proofreading-text.

**Step 8 — Validate & repair (mandatory before delivery).** Run the bundled
validator, read its JSON `errors`, fix each, and **re-run until `status` is `OK`**:

```bash
python scripts/validate_docx.py path/to/file.docx
```

It fails on unfilled template tags and leftover placeholders, and warns when there
are no heading styles, images lack alt text, or the page size is neither Letter nor
A4. Note: field results (TOC/cross-refs) only populate once Word opens and updates
fields — the validator checks content, not rendered field output.

## Principles
1. **Structure is data.** Styles make a document machine-navigable and re-brandable.
2. **Automate every number.** TOC, page numbers, figure/table numbers, and
   cross-references must be fields, not typed values.
3. **One style per meaning.** If two things look the same, they should share a style.
4. **Separate content from presentation.** Restyling should never require retyping.

## Decision framework
- **Template exists?** Use it and inherit its styles. Otherwise define a minimal
  style set (Title, H1–H3, Body, Caption, Quote, List).
- **Recurring layout?** → [building-document-templates](../building-document-templates/SKILL.md).
- **Same doc every period from data?** → register it as a template and loop `fill.py` over the data ([building-document-templates](../building-document-templates/SKILL.md)).

## Common mistakes
- **Fake headings** (manually bolded text) — breaks TOC and accessibility. Use styles.
- **Manual page numbers or "Table 1" typed by hand** — they rot on every edit.
- **Spaces/blank lines for layout** — use paragraph spacing and page breaks.
- **Inconsistent list styles** mixing bullets and dashes — pick one, style it.
- **Images inline without captions or alt text** — caption and describe every figure.

## Validation checklist
- [ ] Every heading uses a heading *style* (verify via the navigation/outline pane).
- [ ] TOC generates and matches the headings; fields updated.
- [ ] Page numbers present and correct across section breaks.
- [ ] All figures/tables numbered and captioned; cross-references resolve.
- [ ] No manual formatting standing in for a style.
- [ ] Images have alt text; tables have header rows marked.
- [ ] Spelling/grammar pass complete; consistent terminology.
- [ ] Opens cleanly and prints/exports to PDF without layout breaks.

## Edge cases
- **Very long docs (100+ pages):** split into master/sub-documents or chapters;
  keep a single style source of truth.
- **Legal documents:** use multilevel numbered lists (1, 1.1, 1.1.1) and defined
  terms; never renumber clauses manually.
- **RTL or multilingual:** set language per run for correct spell-check and hyphenation.
- **Accessibility-mandated:** styles, alt text, table headers, and reading order
  are requirements, not niceties.

## Related skills
- writing-reports, writing-proposals, writing-policies — the prose that fills the structure.
- formatting-documents — consistency rules.
- comparing-documents — track changes between versions.

## Reference files
- [references/style-architecture.md](references/style-architecture.md) — the standard style set and when to use each.
- [references/word-features.md](references/word-features.md) — TOC, sections, cross-references, fields, accessibility how-to.

## Scripts
- [scripts/validate_docx.py](scripts/validate_docx.py) — **run this** before delivery.
- [scripts/build_doc_library.py](scripts/build_doc_library.py) — **Step 0 source.** Generates
  the built-in fill-ready document library (business_report, memo, meeting_minutes, one_pager)
  into the document-template registry from a brand pack (`--brand <name-or-path>`), each with its manifest.
  Fails on unfilled tags / placeholders; warns on missing heading styles, images with
  no alt text, and non-Letter/A4 page size. JSON report, non-zero exit on error →
  drives the Step 8 loop. Requires `python-docx`.

## Examples
**Input:** "Turn this 12-page Markdown spec into a Word document with a TOC."
**Output:** `.docx` with Title style on the H1, Heading 1–3 mapped from `#`/`##`/`###`,
an auto TOC after the title, code blocks in a monospace style, captioned tables,
and footer page numbers — delivered with a one-line note on the style mapping used.

## Templates
- [templates/report-skeleton.md](templates/report-skeleton.md) — heading skeleton for a standard business report.

## Automation opportunities
- Generate the doc from a Markdown/JSON source so content and layout regenerate together.
- For periodic reports, register the document as a template and drive `fill.py` from the data source.
- Store the style set as a `.dotx` template for one-click reuse.

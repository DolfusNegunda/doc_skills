# Example: derive a canonical FAMILY template (row-groups + cover + residue check)

This is the worked example for the **family model** — the default operating mode of
the skill. It takes one exemplar of a document *family* (here a fictional "Project
Status Report") and derives the ONE canonical template that every future file of that
family fills, with **variable-count tables** and a **source-residue** guard. All data
is invented (company *Northwind Traders*, project *PRJ-0042*), so the derived template
and this run are safe to publish.

Everything here is produced by the committed scripts — no binary is checked in. Run
the four commands and you reproduce the template, the fill, and a clean validation.

```bash
cd building-document-templates
export TEMPLATE_REGISTRY=/tmp/family-demo          # keep it out of the shared gallery

# 0. Generate the neutral example exemplar (family_source.docx) — reproducible.
python examples/make_family_example.py

# 0b. SEE IT: render the source and read every page before deciding anything.
python scripts/render_pages.py examples/family_source.docx --out-dir /tmp/src-pages/

# 1. PROPOSE — extracts text candidates, cover PROPERTY leaves, image slots, AND
#    detects each data-table as a ROW-GROUP candidate (variable row counts).
python scripts/templatize.py propose --file examples/family_source.docx \
    --out /tmp/proposal.json
#    -> "Detected 3 table(s) as row-group candidates: team / deliverables / metrics"

# 2. REVIEW — the assisted step. See examples/family-reviewed-proposal.json for the
#    result. The decisions made there:
#      - doc_title / doc_subtitle (cover PROPERTY leaves) + report_subtitle +
#        report_date + summary   -> keep=variable  (the cover/body text fields)
#      - every TABLE CELL value  -> keep=fixed      (owned by a row-group, not a field)
#      - section headings & table headers -> keep=fixed (boilerplate that stays)
#      - the 3 row_group_candidates -> keep=variable, named team / deliverables / metrics
#        (each table's first body row becomes the repeating template row; the surplus
#         example rows are dropped via drop_rows)

# 3. BUILD --family — inject placeholders, turn the 3 tables into repeating row-groups,
#    record source_terms, and register the canonical under registry/_families/.
python scripts/templatize.py build --file examples/family_source.docx \
    --fields examples/family-reviewed-proposal.json \
    --family project-status --owner you@co.com --created 2026-07-14 \
    --source-terms "Northwind Traders,PRJ-0042,Widget Assembly Line,2024/01/15"
#    -> _families/project_status  (5 fields, 3 row-group(s), docx)
#    The manifest it writes is committed here as examples/family-manifest.json — note
#    the `row_groups` and `source_terms` blocks that the fill/validate steps consume.

# 4. FILL — a DIFFERENT project's content (examples/family-content.json) with DIFFERENT
#    row counts (team 3, deliverables 2, metrics 4 — the source had 2/3/2).
python scripts/fill.py \
    --template "$TEMPLATE_REGISTRY/_families/project_status/template.docx" \
    --manifest "$TEMPLATE_REGISTRY/_families/project_status/manifest.json" \
    --data examples/family-content.json --out /tmp/status-out.docx

# 5. VALIDATE — MUST be status OK with an EMPTY source_residue (the --manifest carries
#    the source_terms). "No leftover tags" alone is not enough; residue proves reuse.
python scripts/validate.py /tmp/status-out.docx \
    --template "$TEMPLATE_REGISTRY/_families/project_status/template.docx" \
    --manifest "$TEMPLATE_REGISTRY/_families/project_status/manifest.json"

# 6. QA BY VISION — render the OUTPUT and read every page (mandatory). Confirm the cover
#    updated (title/subtitle/date), tables grew/shrank to the new row counts, banded
#    styling + bold first column preserved, and NO "Northwind Traders / PRJ-0042" survives.
python scripts/render_pages.py /tmp/status-out.docx --out-dir /tmp/out-pages/
```

## What this example proves (the family capabilities)
- **Row-groups**: one canonical table row is cloned per data item, so the team,
  deliverables and metrics tables each render a different number of rows than the
  source exemplar had — filled from `examples/family-content.json`.
- **Data-bound cover**: the cover title/subtitle live in `docProps` (not body runs);
  `propose` surfaces them as property leaves and `build`/`fill` tag and fill them, so
  the cover updates instead of keeping the exemplar's client.
- **Source-residue guard**: `source_terms` are recorded at build time; `validate.py`
  fails the fill if any survive. Here the output is residue-clean.
- **The derivation is the documented engine** — no bespoke per-family script. The same
  `propose → build --family → fill → validate` works for any family (Lessons Learned,
  Change Note, Signoff…); only the review decisions differ.

The simpler per-client run (no families/row-groups) is in [README.md](README.md).

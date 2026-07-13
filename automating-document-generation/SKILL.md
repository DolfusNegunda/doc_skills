---
name: automating-document-generation
description: Design pipelines that turn structured data plus templates into finished documents (Word, PDF, PowerPoint, Excel) programmatically and repeatably — for recurring reports, contracts, statements, and batches. Use when the user asks to "automate document generation", "auto-generate reports/contracts", "produce documents from data", or build a repeatable document pipeline. Goes beyond mail merge with logic, multiple outputs, and validation. Produces a reliable generation workflow, not a single document.
---

# Automating Document Generation

## Scope
Repeatable, programmatic document production: data + templates → finished documents,
with logic, multiple formats, and validation. The scaled, logic-driven layer above
[running-mail-merge](../running-mail-merge/SKILL.md); it orchestrates the authoring
capabilities rather than reimplementing file formats.

## Purpose
Eliminate manual document assembly for anything recurring or high-volume — monthly
reports, contracts, statements, certificates — with a pipeline that's correct,
validated, and maintainable.

## When to use this skill
- "Automate document generation" / "auto-generate reports, contracts, statements."
- "Produce documents from this data on a schedule / in a batch."
- Recurring documents that are currently assembled by hand.
- Cases with conditional content, multiple output formats, or many data sources.

## When NOT to use this skill
- Simple one-template, one-list personalization → [running-mail-merge](../running-mail-merge/SKILL.md).
- A single document → the relevant authoring skill.
- Just designing the template → [building-document-templates](../building-document-templates/SKILL.md).

## Inputs
- The data source(s) and schema; the template(s) with placeholders.
- The generation logic (conditionals, sections included/excluded, calculations).
- Output format(s), naming/storage convention, and trigger (schedule/event/manual).

## Outputs
- A generation pipeline: data → validate → populate template(s) → render →
  validate output → store/deliver — plus the produced documents and a run report.

## Workflow
```
Progress:
- [ ] 1. Define inputs, outputs, logic, and trigger
- [ ] 2. Design the template(s) with machine-readable placeholders
- [ ] 3. Build the data → validation → population step
- [ ] 4. Implement conditional logic and calculations
- [ ] 5. Render to the required format(s)
- [ ] 6. Validate outputs; quarantine failures
- [ ] 7. Schedule/trigger; log every run
```

**Step 1 — Specify.** Nail down data in, documents out, the rules between, and what
triggers a run. Ambiguity here produces wrong documents at scale — the worst failure mode.

**Step 2 — Templates.** Use templates with machine-readable placeholders (`{{field}}`,
sections, loops), built on styles (see [building-document-templates](../building-document-templates/SKILL.md)).

**Step 3 — Data & validation.** Ingest and **validate before generating**: schema,
required fields, types, ranges, referential integrity. Bad data must fail loudly at
the front, not surface in a shipped document.

**Step 4 — Logic.** Implement conditional sections (include a clause only if X),
repeats (line items), and calculations (totals, tax) in the pipeline, not by hand.
Ride on proven libraries (e.g. `docxtpl`, `python-docx`, `openpyxl`, a PDF/HTML
renderer); never hand-assemble file internals.

**Step 5 — Render.** Produce the required format(s). Generate to a review-friendly
format first if human sign-off is needed, then final.

**Step 6 — Validate output.** Check each document: no unfilled placeholders, totals
reconcile, required sections present, renders correctly. **Quarantine failures** with
a report; never silently emit a broken document.

**Step 7 — Operate.** Schedule or event-trigger; log inputs, outputs, and errors per
run so a wrong document can be traced and reproduced.

## Principles
1. **Validate input before generating, and output before delivering.** Two gates.
2. **Logic in the pipeline,** not in manual edits.
3. **Templates are styled and machine-readable;** don't hand-build files.
4. **Fail loudly and quarantine;** a wrong document at scale is worse than none.
5. **Log every run** for traceability and reproducibility.

## Decision framework
- **One template + one flat list?** → [running-mail-merge](../running-mail-merge/SKILL.md) is simpler.
- **Conditionals / repeats / calculations?** Full pipeline.
- **Multiple formats (docx + PDF + xlsx)?** Render step per format from one data model.
- **Recurring on a schedule?** Automate the trigger and logging.
- **Human sign-off required?** Generate to draft, gate on approval, then finalize.

## Common mistakes
- **No input validation** — bad data becomes wrong documents at scale.
- **No output validation** — unfilled placeholders or wrong totals ship.
- **Logic done by hand** after generation — defeats the automation.
- **Hand-assembling file formats** instead of using proven libraries.
- **No run logging** — a bad batch can't be traced or reproduced.
- **No quarantine path** — one bad record breaks or corrupts the whole run.

## Validation checklist
- [ ] Inputs, outputs, logic, and trigger specified.
- [ ] Input validated (schema, required, types, ranges) before generation.
- [ ] Templates styled with machine-readable placeholders.
- [ ] Conditional logic and calculations implemented and tested.
- [ ] Output validated: no leftover placeholders; totals/sections correct; renders.
- [ ] Failures quarantined with a report; no silent bad output.
- [ ] Each run logged (inputs, outputs, errors) and reproducible.

## Edge cases
- **Regulated documents (statements, contracts):** validate legal/financial fields per record; keep an audit trail.
- **Partial data:** define behavior — skip, default, or quarantine.
- **Very large batches:** stream/batch; monitor memory and time; checkpoint.
- **Template changes mid-cycle:** version templates; record which version produced which document.
- **Multi-language output:** parameterize locale; validate each language renders.

## Related skills
- [running-mail-merge](../running-mail-merge/SKILL.md) — the simpler case.
- [building-document-templates](../building-document-templates/SKILL.md), [producing-branded-documents](../producing-branded-documents/SKILL.md).
- writing-reports, generating-data-reports — content the pipeline emits.

## Examples
**Input:** "Auto-generate monthly client statements: fees, usage, and a summary,
per client, as branded PDFs."
**Output:** Pipeline that pulls per-client data, validates it (all required fields,
totals reconcile), populates a styled template with conditional sections and
calculated totals, renders branded PDFs named by client + period, validates each
(no empty placeholders, totals match source), quarantines 3 clients with missing
usage data into a report, and logs the run — ready to schedule monthly.

## Automation opportunities
- Schedule the whole run; deliver via storage/email connectors.
- Add reconciliation checks (totals vs. source) as a hard gate.
- Reuse one data model to emit Word, PDF, and Excel in a single run.

---
name: running-mail-merge
description: Generate personalized documents in bulk from a template and a data source — letters, certificates, labels, invoices, and personalized emails — with correct field mapping, formatting, and pre-send validation. Use when the user asks to "do a mail merge", "generate personalized letters/certificates/labels", "create documents for each row", or bulk-personalize from a spreadsheet. Produces validated, per-recipient documents, not one document with visible merge fields.
---

# Running Mail Merge

## Scope
Bulk personalization: combining one template with a data source (spreadsheet/CSV/
database) to produce one tailored document per record — letters, certificates,
labels, envelopes, invoices, and personalized emails. Data-into-template at record
scale; template design is [building-document-templates](../building-document-templates/SKILL.md).

## Purpose
Produce many correct, personalized documents fast, with clean field mapping and a
validation gate so no one receives a letter addressed to "Dear [FirstName]".

## When to use this skill
- "Do a mail merge" / "generate personalized letters, certificates, labels, invoices."
- "Create a document for each row / each recipient."
- Bulk personalized emails from a recipient list.

## When NOT to use this skill
- One-off personalized document → the relevant authoring skill.
- Complex data → document logic at scale → [automating-document-generation](../automating-document-generation/SKILL.md).
- Designing the template → [building-document-templates](../building-document-templates/SKILL.md).
- Sending the emails live requires an MCP connector; this skill prepares them.

## Inputs
- The template (with merge fields) and the data source with a clean header row.
- The mapping of data columns → template fields; output format (individual files,
  one combined doc, print, email).

## Outputs
- Personalized documents (per record or combined), field-mapped and formatted, with
  a validation report on missing/malformed data and any records held back.

## Workflow
```
Progress:
- [ ] 1. Clean and validate the data source
- [ ] 2. Confirm the template and its merge fields
- [ ] 3. Map data columns to fields exactly
- [ ] 4. Preview several records, including edge cases
- [ ] 5. Handle blanks/conditionals/formatting
- [ ] 6. Validate the full run; hold back bad records
- [ ] 7. Generate output in the required format
```

**Step 1 — Clean data first.** Merge quality = data quality. One header row, one
record per row, consistent formats (dates, currency, capitalization), no blanks in
required fields, no duplicates. Fix the data before merging.

**Step 2–3 — Template & mapping.** Confirm every merge field in the template maps to
a real column. A mismatched or misspelled field name is the classic merge failure.

**Step 4 — Preview edge cases.** Preview not just record 1 but records with long
names, missing optional fields, special characters, and different formats. Problems
hide in the tail, not the first row.

**Step 5 — Blanks & conditionals.** Decide how blanks render (skip a line, default
text) and use conditional fields where content varies (e.g. title, pluralization).
Format numbers/dates/currency in the output, not as raw values.

**Step 6 — Validate the run.** Before producing everything, check for records with
missing required fields, malformed data, or would-be-empty documents. **Hold back
bad records** with a report rather than sending broken output.

**Step 7 — Generate.** Produce the required format — individual files (for archiving/
emailing), one combined document (for review/print), labels/envelopes, or drafted
emails.

## Principles
1. **Data quality is everything.** Clean and validate before you merge.
2. **Map fields exactly;** verify every field resolves.
3. **Preview edge cases,** not just the first record.
4. **Validate and hold back** bad records — never ship a broken merge.
5. **Format in the output,** not the source (dates, currency, case).

## Decision framework
- **Archiving/emailing each?** Individual files (named by a key field).
- **Reviewing/printing?** One combined document.
- **Physical mail?** Labels/envelopes merge.
- **Content varies by record?** Conditional (IF) merge fields.
- **Complex logic/format?** → [automating-document-generation](../automating-document-generation/SKILL.md).

## Common mistakes
- **Merging dirty data** — blanks, duplicates, inconsistent formats → broken documents.
- **Field name mismatches** — fields show as blank or literal `«Field»`.
- **Previewing only record 1** — edge cases fail unseen.
- **Raw number/date formats** ("0.5" instead of "50%", serial dates).
- **No validation gate** — recipients get "Dear ,".
- **Duplicates** — someone gets two letters.

## Validation checklist
- [ ] Data has one header row, one record per row, no required blanks, no duplicates.
- [ ] Dates, currency, and case are consistent.
- [ ] Every template merge field maps to a real column and resolves.
- [ ] Multiple records previewed, including long/blank/special-character cases.
- [ ] Blank-field and conditional behavior defined and correct.
- [ ] Numbers/dates/currency formatted in the output.
- [ ] Records with missing required data held back and reported.
- [ ] Output format matches the need (files / combined / labels / email).

## Edge cases
- **Missing optional fields:** conditional lines so no orphan labels or blank gaps.
- **Special characters / non-Latin names:** verify encoding renders correctly.
- **Very large runs:** batch and spot-check; watch memory/time.
- **Regulated content (invoices, statements):** validate totals and legal fields per record.
- **Personalized email:** confirm addresses valid; use a connector to send; respect consent/opt-out.

## Related skills
- [building-document-templates](../building-document-templates/SKILL.md) — the template it consumes.
- [automating-document-generation](../automating-document-generation/SKILL.md) — for complex logic/scale.
- engineering-excel-workbooks / engineering-google-sheets — clean the data source.
- drafting-business-email — email content.

## Examples
**Input:** "Generate 200 course-completion certificates from this attendee sheet."
**Output:** Data cleaned (deduped, names title-cased, dates standardized); template
fields mapped to Name/Course/Date; edge cases previewed (long names fit); 6 records
with blank names held back and reported; 194 individual PDFs generated, each named
by attendee ID, ready to email.

## Automation opportunities
- Trigger the merge whenever the source data updates.
- Add a validation gate that auto-quarantines incomplete records.
- Pipe individual outputs to an email connector for personalized sending.

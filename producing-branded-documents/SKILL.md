---
name: producing-branded-documents
description: Produce branded Word/PDF deliverables (starting with weekly project updates) from standard templates, with a fixed company layout, headers/footers, and per-client logos. Use when creating a weekly project update, status report, or any client-facing document that must follow the company's standard look with the correct client logo.
---

# Producing Branded Documents

Generate deliverables that look identical across every team — fixed layout,
header/footer, logo placement, colors, fonts — while swapping in a
**client-specific logo** and each project's content.

## Core principle: separate the invariant from the variable

- **Invariant** (same for everyone): layout, header/footer, logo position/size,
  colors, fonts, boilerplate. Lives in the **template file** + `assets/brand/`.
- **Variable** (per project/client): the content, and *which* logo. Supplied as
  **data** (JSON) at fill time.

Never rebuild layout by hand and never re-solve Word internals — fill a template.
That is what guarantees consistency.

## When to use this skill
- Producing a weekly project update or status report for a client
- Any client-facing document that must carry the standard look + the right logo
- Onboarding a new client's logo into the deliverable set

## What's in this skill

```text
assets/
  templates/weekly-project-update.docx   # The standard layout (invariant)
  logos/company.png                      # Fallback logo
  logos/clients/<client-key>.png         # Per-client logos
  brand/brand-spec.md                    # Colors, fonts, logo/page rules
scripts/
  make_template.py                       # (Re)build a template from the brand spec
  fill_docx.py                           # Fill a template with data + client logo
  validate_output.py                     # Gate: no leftover tags, logo present
  export_pdf.py                          # Optional: docx -> PDF (needs LibreOffice)
references/template-catalog.md           # Which template + its data fields
examples/sample_update.json              # Example input
```

## Workflow

Copy this checklist and track progress:

```
Deliverable progress:
- [ ] 1. Confirm the client logo exists (assets/logos/clients/<key>.png)
- [ ] 2. Prepare the data JSON (see references/template-catalog.md)
- [ ] 3. Fill: python scripts/fill_docx.py --data <data>.json --out <file>.docx
- [ ] 4. Validate: python scripts/validate_output.py <file>.docx  (must be OK)
- [ ] 5. (Optional) Export PDF: python scripts/export_pdf.py <file>.docx
```

**Step 1 — Logo.** Confirm `assets/logos/clients/<client-key>.png` exists. If
not, add it (transparent PNG, ≥300px tall) — no code changes needed. Without it,
fill falls back to `company.png` and warns.

**Step 2 — Data.** Build the JSON for the deliverable. Fields and an example are
in [references/template-catalog.md](references/template-catalog.md) and
[examples/sample_update.json](examples/sample_update.json). The *content* can come
from the `writing-status-reports` skill — this skill renders it.

**Step 3 — Fill.**
```bash
python scripts/fill_docx.py --data examples/sample_update.json \
    --out examples/output/globex-week-27.docx
```
Logo selection: explicit `--logo` → else `clients/<client_key>.png` → else
`company.png`. Overall status is auto-colored (Green/Amber/Red).

**Step 4 — Validate (required).** Run `validate_output.py`. It fails with specific
messages if any `{{ tag }}` is unfilled or the logo is missing. **Do not ship a
document that doesn't return `"status": "OK"`.**

**Step 5 — PDF (optional).** `export_pdf.py` converts via LibreOffice. If it isn't
installed, the script prints setup options (install LibreOffice, or Save As PDF
from Word). Author in Word; distribute as PDF.

## Changing the look (rebranding)

Edit `assets/brand/brand-spec.md`, then rebuild:
`python scripts/make_template.py`. Every future deliverable inherits the change.
Because templates live here (version-controlled), teams can't drift onto private
copies.

## Dependencies

`pip install docxtpl Pillow` (pulls in python-docx and jinja2). PDF export also
needs LibreOffice, or Microsoft Word for manual Save-As-PDF.

## Related
- `writing-status-reports` — generates the *content* this skill renders.
- `formatting-to-brand` — lightweight brand styling when not using a template.
- Design rationale: see the branded-templates design notes.

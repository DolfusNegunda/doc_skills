# Intake: registering an externally sourced template as a built-in

Professionally designed templates from outside the suite — a deck downloaded from
Microsoft Create, a document bought from a template gallery, or a file another team
polished — can join the built-in library so any agent can fill them. The engine
treats them exactly like a client file: **preserve and inject, never rebuild.**

> Licensing: only register templates the org may reuse and redistribute internally.
> Note the source and license in `--owner`/changelog if in doubt.

## Where files land

Drop the source file in `building-document-templates/incoming/` (gitignored — source
files never enter version control; only the tagged template + manifest do, and only
when they contain no client data).

## The sequence (capable-model / human task)

```bash
cd building-document-templates

# 1. Propose: scan the file for variable-text candidates, image slots, tables.
python scripts/templatize.py propose --file incoming/annual-report.pptx --out proposal.json

# 2. Review proposal.json — the judgment step.
#    - keep: variable | fixed | remove       (sample text you'd replace -> variable)
#    - suggest_name: snake_case field names  (title, section_heading, kpi1_value…)
#    - suggest_type: text | list             (bullet runs -> list)
#    - activate row-group candidates for repeating table rows (docx)
#    External templates ship with LOREM/sample content: everything sample is `variable`.

# 3. Build into the _builtin namespace. source_terms = distinctive sample strings
#    (fake company names, lorem fragments) so an unedited fill FAILS validation.
python scripts/templatize.py build --file incoming/annual-report.pptx --fields proposal.json \
    --builtin annual-report --source-terms "Contoso,Lorem ipsum,Adventure Works" \
    --owner you@company.com

# 4. Prove it fills before anyone depends on it.
python scripts/registry.py scaffold --builtin annual-report --out /tmp/content.json --with-examples
#    ...edit /tmp/content.json with real-ish values...
python scripts/fill.py --client _builtin --doc-type annual-report --data /tmp/content.json --out /tmp/test.pptx
python scripts/validate.py /tmp/test.pptx --template registry/_builtin/annual_report/template.pptx \
    --manifest registry/_builtin/annual_report/manifest.json
python scripts/render_pages.py /tmp/test.pptx --out-dir /tmp/pages   # vision pass, every page
```

After step 4 the template shows up in `registry.py list` under **Built-in templates**
and small models can fill it via scaffold → fill → validate → render.

## Improving the manifest by hand

`propose` can't know intent. Before or after `build`, edit the manifest's fields so a
small model fills them correctly first try:

- `example` — a realistic, complete value (these double as `scaffold --with-examples` content).
- `guidance` — one sentence on HOW to fill ("3–5 bullets, assertions not topics").
- `required: false` for optional slots (image swaps, secondary captions).

## Boundaries (same as everywhere in the engine)

- Native charts and variable-count SmartArt are flagged, not fillable — prefer
  templates that carry tables/images instead, or accept fixed visuals.
- PPTX tables can't grow rows via row-groups (docx only) — a pptx table's rows are
  per-cell fields or a `list` field per column.
- If the template's look degrades when filled (autofit off, tight boxes), fix the
  source file in Office first, then re-run the sequence.

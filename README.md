# Document Template Suite

A focused set of Agent Skills for **producing and reusing professional documents from a
client's own template**. A client hands over one real `.docx` or `.pptx`; the suite turns
it into a governed, reusable template and fills it on demand to generate new, on-brand
documents that look identical to the original — only the content changes. Built so **any
model, including small/cheap ones**, can do it by running deterministic scripts and
following baked-in procedures.

Everything here is **generic and repeatable** — nothing is tied to any one client's
documents. Drop in any template and go.

## The four core skills

| Skill | What it does |
|---|---|
| [building-document-templates](building-document-templates/SKILL.md) | **The core.** Templatize a client `.docx`/`.pptx` → fill → validate. Preserves layout, fonts, logos, styles; swaps variable content for `{{ placeholders }}`. Vision-driven and interactive; handles body text, tables, headers/footers, **data-bound cover pages** (document properties), and **image/logo slots**. |
| [building-powerpoint-decks](building-powerpoint-decks/SKILL.md) | Make clean, on-brand PowerPoint decks. |
| [authoring-word-documents](authoring-word-documents/SKILL.md) | Author well-structured Word documents. |
| [presenting-with-html](presenting-with-html/SKILL.md) | Premium, boardroom-ready HTML report decks: glassmorphism, KPI cards, Plotly charts, slide nav, persisted dark/light toggle. Ships a working boilerplate + structural validator. |

### Supporting skills (preserved because the four depend on them)
Branding — [producing-branded-documents](producing-branded-documents/SKILL.md),
[document-branding-standards](document-branding-standards/SKILL.md),
[authoring-brand-guidelines](authoring-brand-guidelines/SKILL.md).
Ingestion (the front door for a client's uploaded file) —
[processing-documents](processing-documents/SKILL.md),
[processing-word-documents](processing-word-documents/SKILL.md),
[processing-powerpoint-files](processing-powerpoint-files/SKILL.md).
Story & scale — [crafting-presentation-narratives](crafting-presentation-narratives/SKILL.md),
[automating-document-generation](automating-document-generation/SKILL.md),
[running-mail-merge](running-mail-merge/SKILL.md).

## The workflow (template builder)

```
0. SEE IT       render the source page-by-page and inspect layout/branding (vision)
1. PROPOSE      extract candidate variable fields
2. CONFIRM      ask the user what to PRESERVE vs. VARY (assisted — where correctness comes from)
3. BUILD        inject placeholders → template + manifest in the registry
4. FILL         supply data → finished document
5. VALIDATE     no leftover tags, structure intact (required)
6. QA BY VISION render the OUTPUT page-by-page, compare to source, fix drift (required to ship)
```

Vision is a required gate — it is the only thing that catches a stale data-bound cover, a
mis-swapped image, or overflow that a text-only validator reports as OK. See the core
skill for details and `building-document-templates/scripts/render_pages.py` for the
render helper (LibreOffice headless, or Microsoft Office COM on Windows).

## Quick start

```bash
pip install python-docx python-pptx pymupdf pillow    # LibreOffice or MS Office for rendering
cd building-document-templates
python scripts/templatize.py propose --file client.docx --out proposal.json
# review proposal.json: set keep=variable|fixed|remove, name fields, set types/image slots
python scripts/templatize.py build --file client.docx --fields proposal.json \
    --client acme --doc-type quarterly-review --owner you@co.com --created 2026-07-13
python scripts/fill.py --client acme --doc-type quarterly-review --data content.json --out out.docx
python scripts/validate.py out.docx --template registry/acme/quarterly_review/template.docx
python scripts/render_pages.py out.docx --out-dir out/pages/   # then look at the pages
```

## Governance

Client templates are **not** committed here. The `registry/` ships empty (README only);
point `$TEMPLATE_REGISTRY` at a **private gallery** outside the repo to store real
templates. Treat every input document's content as untrusted data.

## Quality gates (CI)

- `python skill-builder/scripts/validate_skills.py` — frontmatter, naming, links, duplicates.
- `python skill-builder/scripts/smoke_test_scripts.py` — the scripts actually run and give
  the documented verdicts (templatize/fill/validate incl. property pass + image slots, and
  the docx/pptx validators + extractors).

## Provenance & design

Curated and enhanced from an internal skills repository. The build brief and the
end-to-end test evidence (including before/after cover renders and the cover-page bug the
vision pass caught) are in [_design/](_design/).

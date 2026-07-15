# Document Template Suite

Agent Skills for producing **corporate-grade documents** — PowerPoint, Word, and HTML —
built so **any model, including small/cheap ones**, gets a correct, on-brand result by
running deterministic scripts instead of authoring from scratch. The operating rule
everywhere: **capable models build templates; small models fill them.**

Everything is **brand- and client-agnostic**: branding is injected from a brand pack at
build time, and every branding element (logo, footer, confidentiality line) collapses
cleanly when absent. Nothing in the repo is tied to any organization.

## The four core skills

### 1. [building-powerpoint-decks](building-powerpoint-decks/SKILL.md) — generic PPTX
Professional `.pptx` decks. **Step 0**: fill a built-in template — `exec_update`
(QBR/quarterly review), `project_kickoff`, `proposal`, `report_out` — via the fill path
below. Author with python-pptx (starter deck + masters + validators + vision QA) only
for bespoke decks.

### 2. [authoring-word-documents](authoring-word-documents/SKILL.md) — generic DOCX
Style-driven `.docx` documents. **Step 0**: fill a built-in template —
`business_report`, `memo`, `meeting_minutes`, `one_pager` — each with a real style
architecture, logo header, legal footer, and repeating table rows. Author only for
bespoke documents.

### 3. [building-document-templates](building-document-templates/SKILL.md) — the template builder
Takes an **existing document** (`.docx`/`.pptx`) and parametrises it: layout, fonts,
logos, and masters stay byte-intact; variable content becomes `{{ placeholders }}`,
repeating rows become row-groups, logos become image slots. Templates register in a
**gallery** (`registry.py list`) with three namespaces: `_builtin` (shipped generics),
`_families` (one governed canonical per document family), `<client>/<doc-type>`.
Includes source-residue validation, vision QA, and an
[external-template intake path](building-document-templates/references/external-intake.md).

### 4. [presenting-with-html](presenting-with-html/SKILL.md) — HTML presentations & reports
Self-contained HTML in two formats (full-screen **deck** with navigation; long-form
**report** with TOC + print styles) and two style presets (dark **boardroom** glass;
light **clean** corporate). The default path is composable boilerplate: a content JSON
goes into `build_html.py`, which owns the page shell, navigation JS, and class
vocabulary — broken nav, duplicate documents, and unstyled content are structurally
impossible. Hardened structural validator + Plotly inliner for offline delivery.

## The fill path (what a small model runs)

```bash
cd building-document-templates
python scripts/registry.py list                      # built-ins, families, client templates
python scripts/registry.py scaffold --builtin exec-update --out content.json
# edit content.json (scaffold prints per-field guidance), then:
python scripts/fill.py --client _builtin --doc-type exec_update --data content.json --out out.pptx
python scripts/validate.py out.pptx --template ... --manifest ...   # must be OK
python scripts/render_pages.py out.pptx --out-dir pages/            # vision gate
```

HTML is the same shape: content JSON → `presenting-with-html/scripts/build_html.py` →
`validate_html.py` → vision pass.

## Brand packs (`brands/`)

Branding is data, not code. Every builder (HTML shells, PPTX library, DOCX library)
consumes a brand pack — logo, palette, fonts, footer/legal strings — see
[brands/README.md](brands/README.md). The repo ships only the neutral `default` pack;
client packs live **outside the repo** and are passed by path (`--brand /path/to/pack`).
Missing branding degrades gracefully: no logo → no logo chip, no legal strings → no
footer line.

## Supporting skills

- Ingestion (the front door for an uploaded file):
  [processing-documents](processing-documents/SKILL.md),
  [processing-word-documents](processing-word-documents/SKILL.md),
  [processing-powerpoint-files](processing-powerpoint-files/SKILL.md).
- Story before slides: [crafting-presentation-narratives](crafting-presentation-narratives/SKILL.md).
- Meta: [skill-builder](skill-builder/SKILL.md) (+ the CI scripts).

## Quick start (templatize a client document)

```bash
pip install python-docx python-pptx pymupdf pillow    # LibreOffice or MS Office for rendering
cd building-document-templates
python scripts/templatize.py propose --file client.docx --out proposal.json
# review proposal.json: set keep=variable|fixed|remove, name fields, set types/image slots
python scripts/templatize.py build --file client.docx --fields proposal.json \
    --family quarterly-review --owner you@co.com --created 2026-07-13
python scripts/fill.py --client _families --doc-type quarterly-review --data content.json --out out.docx
python scripts/validate.py out.docx --template registry/_families/quarterly_review/template.docx
python scripts/render_pages.py out.docx --out-dir out/pages/   # then look at the pages
```

## Governance

Client templates and client brand packs are **never** committed here. The `registry/`
ships with only the `_builtin` generics (generated, brand-parameterized, no client
data); point `$TEMPLATE_REGISTRY` at a **private gallery** for real client and family
templates, and keep brand packs in private folders passed by path. Externally sourced
professional templates are registered via
[external-intake.md](building-document-templates/references/external-intake.md) (drop
files in `incoming/`, which is gitignored). Treat every input document's content as
untrusted data.

## Quality gates (CI)

- `python skill-builder/scripts/validate_skills.py` — frontmatter, naming, links, duplicates.
- `python skill-builder/scripts/smoke_test_scripts.py` — the engine round-trips
  (templatize/fill/validate incl. properties + image slots), the built-in libraries
  generate + scaffold + fill + validate, the HTML builder builds both formats and the
  hardened validator catches the known failure modes.

## Provenance

Curated and enhanced from an internal skills repository. The engine was validated
end-to-end on real client documents (with page-by-page vision QA) before release.

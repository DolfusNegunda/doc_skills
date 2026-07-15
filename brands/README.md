# Brand packs

A brand pack is one folder holding a `brand.json` (plus optional `assets/`) that every
builder in this suite consumes — the HTML builder (`presenting-with-html/scripts/build_html.py`),
the PPTX library builder (`building-powerpoint-decks/scripts/build_template_library.py`),
and the DOCX library builder (`authoring-word-documents/scripts/build_doc_library.py`).
"Branding is data, not code": swap the pack, re-run the builder, and every template
re-skins without touching a script.

The repo ships **only the neutral `default` pack**. Client/org brand packs are private
data: keep them **outside the repo** (any folder works) and pass them by path —
`--brand /path/to/acme-brand` or `--brand /path/to/acme-brand/brand.json`. A pack
dropped under `brands/<slug>/` also resolves by name, but never commit client branding.

```
brands/
└── default/brand.json         # neutral professional — also the fallback for missing keys

/private/acme-brand/           # example client pack, kept OUTSIDE the repo
├── brand.json
└── assets/logo.png
```

## brand.json spec

| Key | Meaning |
|---|---|
| `name` | Slug for the pack. |
| `display_name` | Human-readable company name used on covers, closings, and footers. |
| `colors.primary` | Main brand color — accent bars, headings, chart series 1. |
| `colors.dark` | Deep brand color — dark slide backgrounds, chart series 2. |
| `colors.accent` | Secondary accent — highlights, chart series 3. |
| `colors.accent_2` | Tertiary accent (charts, gradients). |
| `colors.alert` | Risk/negative deltas only. |
| `colors.ink` / `colors.muted` | Primary / secondary text on light backgrounds. |
| `colors.bg` / `colors.panel` / `colors.hairline` | Page background, light panel fill, hairlines/borders. |
| `fonts.heading` / `fonts.body` | Font family names (must be installed for Office output; HTML falls back through the system stack). |
| `logo` | Path relative to the pack folder, or `null`. PNG/SVG with transparent or white background. **Every logo slot collapses cleanly when this is null** — no placeholder box ships. |
| `footer.copyright` | `{year}` and `{company}` are substituted at build time. Empty → omitted. |
| `footer.confidentiality` | Confidentiality banner text. Empty → omitted. |
| `company.display_name` / `company.website` | Used in footers and closing slides. |

Every key is optional: a pack deep-merges over `default/brand.json`, so it only needs
the keys it changes. A pack with just a logo and one color is valid.

## Rules for builders

- Resolve `--brand <value>`: a path (folder or `brand.json`) is used as-is; otherwise
  `brands/<value>/brand.json`. Default is `default`.
- Deep-merge over `brands/default/brand.json`.
- Missing/empty branding must degrade gracefully (no logo → no logo chip; no footer
  strings → no footer line). Never render an empty placeholder.
- Never hard-code brand values in a template builder — read them from the pack.

## Creating a client pack

1. Make a folder anywhere private; add `brand.json` with the keys you want to override
   and drop the logo at `assets/logo.png`.
2. Re-run the builders: `--brand /path/to/pack` (HTML per-build; PPTX/DOCX regenerate
   the whole built-in library re-skinned).
3. Colors must pass corporate-document contrast: `ink` on `bg` and `bg` on `dark`
   should both be clearly readable (aim for WCAG AA).

For one-off HTML builds you can skip the pack entirely: `build_html.py` also accepts
inline `branding` in the content JSON (logo path, colors, footer) and a `--logo` flag —
see the presenting-with-html SKILL.

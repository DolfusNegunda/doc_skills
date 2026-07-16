# presenting-with-html — quick reference (fill runs)

**Cold start (1 request, not 33):** `GET /repos/<owner>/<repo>/tarball/<branch>` → extract → use the whole `presenting-with-html/` folder. `brands/` optional (embedded neutral fallback).

**Loop:** scaffold → fill → `--validate-only` → build `--inline-plotly` → `validate_html.py` (must be `"status":"OK"`) → `render_screenshots.py` + Read every PNG.

```
python scripts/build_html.py --scaffold deck --out content.json     # --minimal for short updates; report likewise
python scripts/build_html.py --content content.json --validate-only
python scripts/build_html.py --content content.json --out out.html --inline-plotly   # --lite = small CDN build
python scripts/validate_html.py out.html
python scripts/render_screenshots.py out.html --out-dir shots       # no browser -> follow printed disclosure
```

**Top level:** `format` (deck|report) · `style` (boardroom|clean|executive) · `meta` · `slides` (deck) / `sections` (report) — never `blocks`. Optional: `brand`, `branding` {logo, colors, footer}.

**meta:** title, title_accent, eyebrow, lead, author, date, kpis[≤4 {label, value, delta?, down?}]. Generates the title slide/hero — don't add one.

**Blocks** (exact field names; prose accepts `**b**` `*i*` `` `c` `` `[t](https://u)`):
| type | required | entries |
|---|---|---|
| section (deck) | heading | |
| bullets / agenda | heading, items | str or {text, sub?} |
| kpi | kpis | {label, value, delta?, down?} |
| cards | heading, cards | {heading, text, big?, accent?} |
| chart | heading, chart | {chart_type, categories, series[{name, values}]} or {plotly:{data,layout}} |
| table | heading, columns, rows | rows match columns len |
| two-col | heading, left, right | sub-block: text/bullets/chart/table/kpi/image |
| text | heading, paragraphs | |
| quote | quote | attribution? |
| timeline | heading, milestones | {title, label?, description?, done?} |
| comparison | heading, left+right | {title, items} each side |
| image / feature | src (+paragraphs for feature) | alt?, caption?, image_side? |
| callout | text | style: takeaway/recommendation/action/info/warning |
| team | heading, people | {name, role?, photo?, email?, note?} |
| status | heading, statuses | {label, status: green/amber/red, note?} |
| steps | heading, steps | str or {title, description?} |
| definitions | heading, terms | {term, definition} |
| contact / closing | heading | contacts {name, role?, email?, phone?} / lead?, cards? |

**Gotchas:** (1) `title_accent` renders ONLY as an exact substring of `title`. (2) Deck uses `slides`, report uses `sections` — `blocks` is nothing. (3) **Never Read the built HTML back** (~5–6 MB inlined) — verify via `validate_html.py` JSON + grep-style checks only. (4) Raw `plotly` passthrough keeps authored colors (no theme restyle); all charts are static build-time snapshots.

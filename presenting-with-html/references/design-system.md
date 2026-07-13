# Executive HTML report — design system

The full spec behind [../SKILL.md](../SKILL.md). The boilerplate
[../assets/deck-template.html](../assets/deck-template.html) already implements all of
this — read this when adapting or extending it.

## Aesthetic
Modern, premium, boardroom-ready — a strategy deck, not an exported notebook. Clean,
visually strong, uncluttered, CEO-viewable. Ingredients: radial/layered gradient
background, translucent glass panels with blur, rounded corners, soft shadows, large
typography, generous spacing, high-contrast KPI cards, cool-toned accents (cyan / purple
/ blue), muted secondary text for narrative.

## Design tokens (parallel dark + light sets — both required)
Define as CSS variables under `:root[data-theme="dark"]` and `:root[data-theme="light"]`.
Default to **dark**. Every surface (cards, tables, charts, HUD, nav) reads from tokens so
the toggle restyles the whole report, not just the page background.

| Token | Dark | Light |
|---|---|---|
| `--bg-0` / `--bg-1` | deep navy `#0b1020` / `#131a2e` | `#eef2f9` / `#dbe4f3` |
| `--text` / `--muted` | `#e8ecf5` / `#8b93a7` | `#0f172a` / `#54617a` |
| `--accent` / `-2` / `-3` | cyan `#22d3ee` / purple `#a78bfa` / blue `#60a5fa` | `#0891b2` / `#7c3aed` / `#2563eb` |
| `--glass-bg` / `--glass-border` | `rgba(255,255,255,.055)` / `.12` | `rgba(255,255,255,.62)` / `rgba(15,23,42,.10)` |
| `--card-bg` | `rgba(255,255,255,.05)` | `rgba(255,255,255,.72)` |
| `--grid` (chart/table lines) | `rgba(255,255,255,.08)` | `rgba(15,23,42,.10)` |
| `--shadow` | `0 24px 60px -20px rgba(0,0,0,.65)` | `0 24px 60px -24px rgba(30,50,90,.35)` |

Background = layered radial glows over a linear gradient of `--bg-0`→`--bg-1`.
Glass panel = `--glass-bg` + 1px `--glass-border` + `backdrop-filter: blur(18px) saturate(140%)` + `--shadow`, radius 24px.

## Slide model
Presentation deck, not a scrolling page. One full-viewport `.slide` per section; content
centered in a glass `.slide-inner` that scrolls internally when long; consistent margins.
Only `.slide.active` is visible. Typical sequence:
1. **Hero** — eyebrow, very large gradient title, one-sentence lead, 3–4 KPI cards.
2. **Executive highlights** — grid of highlight cards (title + 1 sentence + one number).
3. **Overall chart** — the headline trend.
4. **Detail slides** — one per company/segment: KPI row (Jan/Feb/Mar/Q1), a chart, a short
   CEO note (active users, top user, direction of spend, concentration), optional top-N table.
5. **Appendix table** (optional).
6. **Closing** — conclusion paragraph + 1–2 recommendation cards.

## Components
- **KPI card** — uppercase muted label, prominent value (`clamp(1.8rem,3vw,2.6rem)`, weight 800),
  optional delta (accent up / pink down). 4-up grid, 2-up on mobile.
- **Highlight / recommendation card** — title, muted explanation, optional big number.
- **Chart panel** — chart wrapped in a `--card-bg` glass container; strong heading + short note above.
- **Table** — rounded container, sticky high-contrast header, subtle row separators, muted
  body, first column emphasized, internal scroll for long tables. Compact in detail slides;
  full dumps only in an appendix.

## Charts (Plotly)
Transparent `paper_bgcolor`/`plot_bgcolor`; `font.color`, axis `gridcolor` and series colors
pulled from the theme tokens; `hovermode: 'x unified'`; clean axis labels; friendly month
labels (`Jan`,`Feb`,`Mar`); legend horizontal below; `displayModeBar:false`,
`responsive:true`. Register each chart with a `build(themeColors)` renderer and call
`Plotly.react` on theme toggle so charts restyle. Useful types: grouped bar by month,
company-by-month, user-by-month, provider reference, total line over grouped bars.

## Navigation & theme (HUD)
Required: prev/next buttons **and** ←/→ keyboard nav. Recommended: `n / N` counter,
click-to-jump progress dots, a short hint. `showSlide(i)` wraps both ends, toggles the
active slide + dot, updates the counter, **resets `.slide-inner` scrollTop**, and
**dispatches a `resize` event** so Plotly re-fits. Theme toggle is always visible, defaults
dark, persists via `localStorage`, restyles the whole report (incl. re-rendering charts).

## Responsiveness
Desktop-first but must work on small screens: reduce slide/panel padding, KPI cards → 2-up
or stacked, two-column → one column, smaller nav buttons, hide the hint. Readability first.

## Storytelling
Overview → key insights → overall patterns → supporting breakdowns → actionable conclusion.
The report must answer: what happened? where did it concentrate? how did it change over
time? what should leadership do next? Never ship a beautiful report with no clear message.

## Reuse
Cost, adoption, company-by-company usage, user-level usage, provider spend, and executive
governance reports. Adapt the content; keep the premium slide experience unless the user
explicitly asks for a plain/tabular document.

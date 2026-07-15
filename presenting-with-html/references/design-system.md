# Presenting with HTML — design system

The full spec behind [../SKILL.md](../SKILL.md). Two boilerplates implement all of this and
**share an identical core** — read this when adapting or extending either:
- [../assets/deck-template.html](../assets/deck-template.html) — slide deck (`data-format="deck"`).
- [../assets/report-template.html](../assets/report-template.html) — long-form report (`data-format="report"`).

## Two formats, one system
Both formats draw from the **same shared core** so org output looks consistent regardless of
who made it or which format they chose:
- **Shared (identical in both files):** the design-token block (dark + light), the theme
  toggle JS (persist via `localStorage`, restyle everything incl. charts), and the
  chart-registration core (`themeColors()`, `baseLayout()`, `registerChart()`,
  theme-aware `Plotly.react`). KPI cards, `.card`, `.chart-panel`, and tables are styled
  the same.
- **Deck-specific:** absolute-positioned `.slide`s, one visible at a time; HUD with
  prev/next buttons, ←/→ keys, dots, counter; `showSlide()` resets scroll and dispatches
  `resize`.
- **Report-specific:** document flow; `.report-section` blocks with `id` anchors; a sticky
  `.toc` built from the sections with `IntersectionObserver` scroll-spy; a back-to-top
  button; and an `@media print` stylesheet.

**Format is chosen at generation time** (SKILL step 0) from the user's request, not toggled
in-page. When extending, keep the shared core byte-for-byte identical between the two files.

## Aesthetic
Modern, premium, uncluttered — a polished product, not an exported notebook. Works for a
board deck *and* a detailed team report. Ingredients: radial/layered gradient background,
translucent glass panels with blur, rounded corners, soft shadows, large typography,
generous spacing, high-contrast KPI cards, cool-toned accents (cyan / purple / blue), muted
secondary text for narrative.

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

### Brand colors (org swap)
The palette above is a neutral default. To align a deliverable with org branding, change
**only** the accent trio (`--accent` / `--accent-2` / `--accent-3`) in *both* the dark and
light `:root` blocks — every chart series, gradient title, dot, and active-TOC marker reads
from them, so the whole piece re-skins from three values. Keep the neutral bg/text/glass
tokens unless a brand demands otherwise, and re-run the vision QA to confirm contrast holds
in both themes. For the authoritative palette see
[../../brands/README.md](../../brands/README.md).

## Slide model (deck format)
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

## Report model (long-form format)
A scrolling document, not slides. A two-column grid: a sticky `.toc` sidebar (collapses above
the content on mobile) and a `.content` column of stacked `.report-section` glass panels.
Each section has a unique `id` and a `data-toc` label; the TOC and `IntersectionObserver`
scroll-spy are built from whatever sections exist. Use it when content is detailed or meant
to be printed. Typical sequence:
1. **Hero** (`.report-section.hero`, transparent) — eyebrow, gradient title, lead, 3–4 KPIs.
2. **Highlights** — grid of cards.
3. **Overall trend** — headline chart + a narrative paragraph (`p.body`) below it.
4. **Detail sections** — as many as needed; each a KPI row + chart + note + table. Reports
   carry far more detail than a deck; dense tables live inline in their section, not an appendix.
5. **Recommendations / conclusion.**
A report should still advance one message per section and stay uncluttered — long ≠ a dump.

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

## Navigation & theme
**Theme (both formats):** the toggle is always visible, defaults dark, persists via
`localStorage`, and restyles the whole page incl. re-rendering charts. Deck and report use
distinct storage keys (`deck-theme` / `report-theme`) so mixed deliverables don't clash.

**Deck HUD:** prev/next buttons **and** ←/→ keyboard nav; recommended `n / N` counter,
click-to-jump dots, a short hint. `showSlide(i)` wraps both ends, toggles the active
slide + dot, updates the counter, **resets `.slide-inner` scrollTop**, and **dispatches a
`resize` event** so Plotly re-fits.

**Report navigation:** a sticky `.toc` whose links (`href="#id"`) jump to sections;
`IntersectionObserver` highlights the current section's link (`.active`); a back-to-top
button appears after scrolling. No slide machinery.

## Charts offline (delivery)
Templates load Plotly from a CDN for instant authoring preview, but a delivered file must be
self-contained (email / SharePoint / air-gapped / strict CSP). Before sharing, inline the
library with `scripts/vendor_plotly.py --inline <file>` (see SKILL step 8). The validator
warns while an external CDN `<script src>` remains.

## Accessibility & print
- **Reduced motion:** both templates honor `@media (prefers-reduced-motion: reduce)` —
  transitions/animations off, smooth-scroll disabled.
- **Contrast:** the token sets are tuned for AA-ish contrast in both themes; re-check after a
  brand-color swap.
- **Keyboard/semantics:** real `<button>`/`<a>` elements with `aria-label`s; TOC is a `<nav>`.
- **Print (report):** the `@media print` block forces a light, ink-friendly palette, hides
  the toggle/TOC/back-to-top, and avoids breaking sections across pages — so File→Print /
  Save-as-PDF is clean. Charts reflow to the print size in Chromium (Edge/Chrome), which
  fires a resize on the print-media switch — verified via `--print-to-pdf`. (Decks are for
  screen; print the report format when a PDF is needed.)

## Responsiveness
Desktop-first but must work on small screens. **Deck:** reduce slide/panel padding, KPI
cards → 2-up or stacked, two-column → one column, smaller nav buttons, hide the hint.
**Report:** the TOC moves above the content (`grid-template-columns:1fr`) and the same card
restacking applies. Readability first.

## Storytelling
Overview → key insights → overall patterns → supporting breakdowns → actionable conclusion.
The deliverable must answer: what happened? where did it concentrate? how did it change over
time? what should the audience do next? Never ship a beautiful piece with no clear message.

## Reuse
For anyone in the org, not just executives: cost/adoption reviews, project and team status
reports, usage/spend breakdowns, provider comparisons, governance write-ups, research
summaries, KPI dashboards. Adapt the content; choose **deck** for click-through/live
presentation and **report** for detailed or printable material — keep the premium,
theme-aware, self-contained experience in both.

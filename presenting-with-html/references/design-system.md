# Presenting with HTML — design system

The full spec behind [../SKILL.md](../SKILL.md). The builder assembles every deliverable from
these shared shells — read this when adapting or extending the design:
- [../assets/shells/deck.html](../assets/shells/deck.html) — slide-deck shell (`data-format="deck"`).
- [../assets/shells/report.html](../assets/shells/report.html) — long-form report shell (`data-format="report"`).

## Two formats, one system
Both formats draw from the **same shared core** so org output looks consistent regardless of
who made it or which format they chose:
- **Shared (same token vocabulary in both files, bar a couple of format-specific tokens like deck-only `--tint`):** the design-token block (light + dark),
  the theme toggle JS (persist via `localStorage`, restyle everything incl. charts), and the
  chart-registration core (`themeColors()`, `baseLayout()`, `registerChart()`, theme-aware
  `Plotly.react`). KPI cards, `.card`, chart panels, callouts, quotes, and tables read from
  the same tokens and are styled the same.
- **Deck-specific:** a fixed 16:9 `.stage` scaled to fit; absolute-positioned `.slide`s, one
  visible at a time; a per-slide branded `.slide-foot`; HUD with prev/next buttons, ←/→ keys,
  progress rail, counter; `showSlide()` toggles the active slide and dispatches `resize`.
- **Report-specific:** a branded `.masthead` and footer band; document flow; `.report-section`
  blocks with `id` anchors; a sticky numbered `.toc` built from the sections with
  `IntersectionObserver` scroll-spy; a back-to-top button; and an `@media print` stylesheet.

**Format is chosen at generation time** (SKILL step 0) from the user's request, not toggled
in-page. When extending, keep the shared **core** tokens identical between the two files.

## Aesthetic
Modern, restrained, corporate — a polished product, not an exported notebook, and not the old
glassmorphism look. Works for a board deck *and* a detailed team report. Ingredients: a **flat
single-color background**, **flat branded panels** separated by **hairline borders**, restrained
shadows, generous whitespace, large confident typography, tabular numerics for figures, a
**single brand accent** driving charts and markers, and **semantic green/red deltas**. Muted
secondary text carries the narrative. **Light-first** by default; the `boardroom` preset loads
dark-first (both palettes always ship — the toggle is live in either).

## Design tokens (parallel light + dark sets — both required)
Defined as CSS variables under `:root, :root[data-theme="light"]` (the default) and
`:root[data-theme="dark"]`. The builder fills the brand-driven holes (`{{ light_accent_1 }}`,
`{{ ink }}`, `{{ dark_bg_0 }}`, …) from the brand pack; the preset (`--style`) sets which theme
loads first via `default_theme`. Every surface (panels, tables, charts, HUD, masthead, footer)
reads from tokens so the toggle restyles the whole deliverable, not just the background.

| Token | Role | Light | Dark |
|---|---|---|---|
| `--brand` | primary brand accent (headings rules, active markers) | `accent_1` | `accent_1` |
| `--accent` / `-2` / `-3` | chart series / secondary accents | brand trio | brand trio |
| `--bg` | flat page background | pack bg | dark base |
| `--panel` / `--panel-2` | primary / subtle surface | `#FFFFFF` / 4% brand tint | 6% / 3.5% white over `--bg` |
| `--text` / `--muted` / `--faint` | text hierarchy | ink / muted / 62% muted | `#EAEEF7` / `#9AA4BC` / `#6C7590` |
| `--hair` / `--hair-strong` | hairline borders / dividers | 20% / 34% muted | `rgba(255,255,255,.10)` / `.17` |
| `--pos` / `--neg` | semantic up / down deltas | `#0E8A5F` / `#C4384B` | `#3FCF97` / `#F0708A` |
| `--tint` *(deck only)* | section/quote slide backdrop | 7% brand | 16% brand over `--bg` |
| `--grid` | chart / table gridlines | 20% muted | `rgba(255,255,255,.10)` |
| `--shadow` | restrained elevation | soft, low-alpha | soft, low-alpha |

**Back-compat aliases** are kept in both shells so older component CSS still resolves:
`--glass-bg → --panel`, `--glass-border → --hair`, `--card-bg → --panel-2`. There is **no**
`backdrop-filter`, blur, or gradient background any more — panels are flat with a 1px `--hair`
border and a restrained `--shadow`.

### Brand colors (org swap)
The palette is filled from a **brand pack**, not hand-edited in the shell. To align a deliverable
with org branding, supply a pack in [../../brands/](../../brands/README.md) (or an inline
`branding` object in the content JSON with `colors`) — its accent(s) flow into `--brand` /
`--accent*` in *both* the light and dark sets, so every chart series, heading rule, dot, and
active-TOC marker re-skins from the pack. Never edit the shell CSS to rebrand. With no pack, the
builder falls back to a neutral default. Re-run the vision QA after a swap to confirm contrast
holds in both themes.

## Slide model (deck format)
A presentation deck, not a scrolling page. A fixed **1920×1080 `.stage`** (maps 1:1 to
PPTX/PDF) is centered in a fullscreen `.viewport` and **scaled to fit** the window. Each
section is one absolutely-positioned `.slide` (`inset:0`); only `.slide.active` is visible.
Content sits in a `.slide-pad`; every slide carries a branded `.slide-foot` (logo · slide title ·
`NN / NN` · confidentiality). Slide-type variants restyle the pad: `.slide.title` and
`.slide.closing` center their content; `.slide.section` and `.slide.quote` use the `--tint`
backdrop. Typical sequence:
1. **Title** — eyebrow, large title, one-sentence lead, an edge-to-edge KPI band (3–4 KPIs).
2. **Executive highlights** — grid of highlight cards (title + 1 sentence + one number).
3. **Overall chart** — the headline trend.
4. **Detail slides** — one per company/segment: KPI row, a chart, a short note, optional table.
5. **Appendix table** (optional).
6. **Closing** — conclusion + 1–2 recommendation cards.

## Report model (long-form format)
A scrolling document, not slides. A full-width branded `.masthead` (logo + title + meta + theme
toggle) tops the page; a footer band closes it. The body is a two-column grid: a sticky numbered
`.toc` sidebar (collapses above the content on mobile) and a `.content` column of stacked, flat
`.report-section` blocks separated by hairlines. The cover section carries an edge-to-edge
`.kpi-band`. Each section has a unique `id` and a `data-toc` label; the `.toc` and
`IntersectionObserver` scroll-spy are built from whatever sections exist. Typical sequence:
1. **Cover** — eyebrow, title, lead, KPI band.
2. **Highlights** — grid of cards.
3. **Overall trend** — headline chart with a narrative paragraph (`p.body`) beside/below it.
4. **Detail sections** — as many as needed; KPI row + chart + note + table inline (not an
   appendix — reports carry far more detail than a deck).
5. **Recommendations / conclusion.**
A report still advances one message per section and stays uncluttered — long ≠ a dump.

## Components
- **KPI** — uppercase `.label`, prominent `.value` (tabular numerics), optional `.delta`
  colored `--pos` (up) / `--neg` (down). Rendered edge-to-edge as a `.kpi-band` on covers, or
  as a row inside sections.
- **Card** (`.card`) — flat panel, hairline border; title, muted explanation, optional big number.
- **Chart panel** — chart on a flat `--panel-2` surface; strong heading + short note above.
- **Callout** (`.callout` + kind) — left-accent panel. Kinds: `takeaway`, `recommendation`,
  `info` use `--brand`; `action`, `warning` use `--neg`.
- **Quote** (`.quote-wrap`) — brand left-accent bar; large serif `.quote-text` + muted `.quote-attr`.
- **Table** — flat container, high-contrast header, hairline row separators, muted body, first
  column emphasized, internal scroll for long tables. Compact in detail sections.

## Charts (Plotly)
Transparent `paper_bgcolor`/`plot_bgcolor`; `font.color`, axis `gridcolor` and series colors
pulled from the theme tokens (`--brand`/`--accent*`/`--grid`); `hovermode: 'x unified'`; clean
axis labels; friendly month labels (`Jan`,`Feb`,`Mar`); legend horizontal below;
`displayModeBar:false`, `responsive:true`. Register each chart with a `build(themeColors)`
renderer and call `Plotly.react` on theme toggle so charts restyle. Useful types: grouped bar by
month, company-by-month, provider reference, total line over grouped bars.

## Navigation & theme
**Theme (both formats):** the toggle is always visible, persists via `localStorage`, and
restyles the whole page incl. re-rendering charts. It defaults to the preset's `default_theme`
(`boardroom` → dark; `clean` / `executive` → light). Deck and report use distinct storage keys
(`deck-theme` / `report-theme`) so mixed deliverables don't clash.

**Deck HUD:** prev/next buttons **and** ←/→ keyboard nav; a progress `.rail` and `.slide-count`
counter; click-to-jump dots. `showSlide(i)` wraps both ends, toggles the active slide + dot,
updates the counter, and **dispatches a `resize` event** so Plotly re-fits. (Slides are a fixed
non-scrolling stage, so there is no per-slide scroll to reset.)

**Report navigation:** a sticky numbered `.toc` whose links (`href="#id"`) jump to sections;
`IntersectionObserver` highlights the current section's link (`.active`); a `.to-top` button
appears after scrolling. No slide machinery.

## Charts offline (delivery)
Shells load Plotly from a CDN for instant authoring preview, but a delivered file must be
self-contained (email / SharePoint / air-gapped / strict CSP). Before sharing, inline the
library with `scripts/vendor_plotly.py --inline <file>` (or build with `--inline-plotly`). The
validator warns while an external CDN `<script src>` remains.

## Accessibility & print
- **Reduced motion:** both shells honor `@media (prefers-reduced-motion: reduce)` —
  transitions/animations off, smooth-scroll disabled.
- **Contrast:** the token sets are tuned for AA-ish contrast in both themes; re-check after a
  brand-color swap.
- **Keyboard/semantics:** real `<button>`/`<a>` elements with `aria-label`s; TOC is a `<nav>`.
- **Print (report):** the `@media print` block forces a light, ink-friendly palette (flat white
  panels, hairlines, no shadow), hides the toggle/TOC/back-to-top, and avoids breaking sections
  across pages — so File→Print / Save-as-PDF is clean. The deck stage prints one slide per page.
  (Decks are for screen; print the report format when a PDF is needed.)

## Responsiveness
The deck `.stage` scales to any window via a transform, so decks fit any screen without reflow.
**Report:** desktop-first but must work small — the `.toc` moves above the content
(`grid-template-columns:1fr`) and cards restack (4-up → 2-up → stacked). Readability first.

## Storytelling
Overview → key insights → overall patterns → supporting breakdowns → actionable conclusion.
The deliverable must answer: what happened? where did it concentrate? how did it change over
time? what should the audience do next? Never ship a beautiful piece with no clear message.

## Reuse
For anyone in the org, not just executives: cost/adoption reviews, project and team status
reports, usage/spend breakdowns, provider comparisons, governance write-ups, research
summaries, KPI dashboards. Adapt the content; choose **deck** for click-through/live
presentation and **report** for detailed or printable material — keep the flat, brand-driven,
theme-aware, self-contained experience in both.

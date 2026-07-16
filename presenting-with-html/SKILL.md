---
name: presenting-with-html
description: "Build a polished, self-contained HTML report or presentation — for anyone in the org, from a team status update to a board deck. Two formats (a slide DECK with full navigation, or a long-form REPORT with sticky TOC and print/PDF styles) times three style presets (dark-first BOARDROOM glassmorphism, light-first CLEAN corporate, or EXECUTIVE editorial serif) from one component system — KPI cards, charts, tables, timelines, comparisons, quotes, figures — with theme-aware Plotly and a persisted dark/light toggle. DEFAULT PATH: write a content JSON and run scripts/build_html.py — the builder owns the HTML shell, navigation, and styling. Branding is injected from a brand pack OR an inline branding object (logo path + colors in the content JSON); with no branding, every placeholder collapses to the neutral default. Use when the user asks for an HTML report, presentation, dashboard, web-based slide deck, or a detailed HTML document to fill with content."
---

# Presenting with HTML

**Fill-only run? Read [QUICKREF.md](QUICKREF.md) instead** (top-level keys, exact block
fields, the gates, the gotchas — 40 lines). Read this full file only for bespoke work or
when a gate fails.

## Scope
Turn content or data into a **premium, self-contained HTML deliverable** that reads as one
design system — glassmorphism, KPI cards, interactive theme-aware Plotly charts, a
persisted light/dark toggle. Two formats, chosen per request:

- **Deck** — full-screen slides in a glass panel with a full HUD (arrow buttons, ←/→ keys,
  progress dots, slide counter). Best when the audience clicks through, presents live, or
  wants a boardroom feel. One message per slide.
- **Report** — a long-form scrolling document with a sticky table of contents, scroll-spy,
  and print/PDF styles. Best for detailed reports read top-to-bottom, referenced, or
  printed — many sections, dense tables, thorough narrative.

And three **style presets**, chosen per build (`--style` or `"style"` in the content JSON):

- **boardroom** (default) — dark-first glassmorphism, gradient accents; the premium
  presented-live look.
- **clean** — light-first, flat white panels, hairline borders, solid accents,
  print-oriented; what most client-facing corporate reports expect.
- **executive** — light-first editorial: warm paper, serif display headings, squared
  corners, hairline rules; the annual-report / formal board-pack look.

All presets share the identical component vocabulary and support the dark/light toggle.

For PowerPoint use [../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md);
nail the story first with [../crafting-presentation-narratives/SKILL.md](../crafting-presentation-narratives/SKILL.md).

## Core principle: content in, document out — never edit the shell
**The default path is the builder.** You write a `content.json` (structured slides/sections);
`scripts/build_html.py` assembles the finished file from verified shells and components. The
builder owns the single `<head>/<style>/<script>`, the HUD/TOC, the theme system, and the
entire class vocabulary — so duplicate documents, invented CSS classes, dead nav buttons,
and stale counters are **structurally impossible**. Branding (logo, palette, fonts, footer)
comes from a brand pack in [../brands/](../brands/README.md) and is applied at build time.

Never author a full HTML page from scratch, and never append content to a template file —
if a layout truly doesn't fit the block types, use the bespoke path at the end of this file.

## Requirements — check before you start
- **Use the whole skill folder** (`scripts/`, `assets/`, `schema/`, `examples/`). The builder
  assembles from `assets/shells/` + `assets/components/`; with a partial checkout it stops
  and says which files are missing. Fetching from GitHub on a cold start: one archive
  request (`GET /repos/<owner>/<repo>/tarball/<branch>`, then extract) beats pulling 30+
  file blobs individually — cheaper, and survives ephemeral scratch directories being wiped.
- **Never Read the built HTML back into context** — with inlined Plotly it is ~5–6 MB.
  Verify through `validate_html.py`'s JSON verdict and targeted grep-style checks
  (e.g. does the file contain a heading string), then the screenshot vision pass.
- The repo-root [../brands/](../brands/README.md) directory is **optional**: without it the
  builder falls back to embedded neutral defaults (a client pack passed by *path* still works).
- **Never edit the scripts, shells, or components to get past an error** — a path failure or
  missing asset means your checkout or invocation is wrong, not the engine. Fix that, or stop
  and say what is missing. A patched engine invalidates every guarantee this skill makes.
- Field names in `content.json` are **exact**. Run `build_html.py --list` for the per-block
  field reference, and `build_html.py --content content.json --validate-only` to check the
  JSON before building — unknown fields are rejected with a did-you-mean suggestion, so one
  fix cycle is enough.

## Workflow (default: build from content)
```
Progress:
- [ ] 0. Choose format (deck vs report) + style (boardroom/clean/executive) from the request signals
- [ ] 1. Story: overview -> insights -> patterns -> breakdowns -> conclusion (one message per slide/section)
- [ ] 2. Scaffold: python scripts/build_html.py --scaffold deck --out content.json   (report likewise)
- [ ] 3. Fill content.json; prose fields accept **bold**, *italic*, `code`, [label](https://url)
- [ ] 4. Build self-contained: python scripts/build_html.py --content content.json --out out.html --inline-plotly
- [ ] 5. Validate: python scripts/validate_html.py out.html  -> must be "OK"
- [ ] 6. Vision QA: python scripts/render_screenshots.py out.html --out-dir shots, then Read every PNG
```
While iterating on content, drop `--inline-plotly` for instant rebuilds; the **final** build
must include it (or run `vendor_plotly.py --inline out.html`) so the deliverable is
self-contained. The validator gives the same verdict either way.

**Step 0 — Choose the format and style.** Signals: "deck / slides / present / walk the board
through it" → deck. "report / document / detailed / read / print / PDF / email / share the
write-up" → report. **When the request carries clear signals, proceed and state the choice**
("Building this as a long-form printable report since you said report + printable") — don't
burn a round-trip confirming the obvious. **Ask only when genuinely ambiguous** ("slide deck
to click through, or a long-form report to scroll/print?"). When still unsure, default to
**deck** for ≤ ~7 messages of mostly-visual content, **report** for detailed/reference
material or anything printed. Style: "premium / boardroom / impressive / dark" → `boardroom`;
"corporate / conservative / client-facing / printable / clean" → `clean`; "annual report /
editorial / formal / board pack" → `executive`. Default boardroom for decks; for reports
that will be printed or sent to a client, prefer `clean` or `executive`.

**Step 1 — Story first.** Decide the narrative before writing JSON. Every slide/section
advances one message and the deliverable must answer: what happened, where did it
concentrate, how did it change, what to do next. A beautiful deliverable with no message fails.

**Steps 2–3 — Scaffold, then fill the content JSON.**
`build_html.py --scaffold deck|report --out content.json` emits a skeleton with the exact
field names — replace every value, delete blocks you don't need, duplicate ones you need
more of. That's cheaper than reading an example; the full contract is
[schema/content.schema.json](schema/content.schema.json) and complete worked inputs are in
[examples/](examples/) if you want one. Essentials:

- `meta` (title, `title_accent`, eyebrow, lead, author, date, up to 4 `kpis`) generates the
  title slide / hero — don't add one yourself.
- Deck blocks: `section` (numbered divider), `bullets`, `kpi`, `cards`, `chart`, `table`,
  `two-col`, `text`, `quote`, `timeline`, `comparison`, `image`, `closing` — plus the
  office set: `agenda` (numbered contents), `callout` (Key takeaway / Recommendation /
  Action required box), `team` (people cards with photo slot), `status` (RAG rows),
  `contact` (structured thank-you/contacts), `steps` (numbered process), `feature`
  (image+text row), `definitions` (term/definition list). Report blocks: the same minus
  `section`; each may set `toc` for its contents-panel label.
- Charts are a simple spec — `{"chart_type": "bar|line|area|pie|scatter", "categories":
  [...], "series": [{"name", "values"}]}` — converted to theme-aware Plotly that restyles on
  the theme toggle. Raw `{"plotly": {"data", "layout"}}` passthrough exists for exotic charts
  but **keeps its authored colors — it does not restyle on the toggle** (the builder warns).
  All charts are **static build-time snapshots**: no live data connection; rebuild to refresh.
- Deck slides don't auto-shrink: the builder warns on overflow risk (too many bullets/rows/
  chars per slide) with a *split this slide* message — heed it; the vision gate is authoritative.
- `image` blocks embed the file base64 (self-contained); paths resolve relative to the
  content JSON. `timeline` takes ordered `milestones`; `comparison` takes titled
  `left`/`right` item lists; `quote` is a pull-quote with optional attribution.
- Keep deck slides to one message: ~5 bullets, ≤4 KPIs, one chart. Push dense tables into a
  report or an appendix slide.
- Field names are exact (`items` not `bullets`, `heading` not `title`, `milestones` not
  `events`). Check cheaply before building:
  `python scripts/build_html.py --content content.json --validate-only`.
- **Safe inline rich text** in prose fields (paragraphs, bullets, card/table text, quotes,
  milestone descriptions, leads, notes): `**bold**`, `*italic*`, `` `code` ``, and
  `[label](https://url)` (https/http/mailto/# only). Values are escaped first, so raw HTML
  never enters the document — a `<b>` tag renders as literal text. Headings, KPI values,
  and labels stay plain.

**Step 4 — Build (self-contained by default).** Include `--inline-plotly` on the final
build so the deliverable needs nothing from the network (emailed/SharePoint/air-gapped/CSP);
drop it while iterating for instant rebuilds. If the CDN is blocked, run
`vendor_plotly.py --fetch` once and the vendored copy is reused offline. When the user
explicitly doesn't need offline safety and wants a small file, build with **`--lite`**
(CDN-linked, ~50 KB instead of ~5 MB; charts need internet at view time). Branding, three
ways (all optional — with none, placeholders collapse and the neutral default renders):

1. **Brand pack**: `--brand <name-or-path>` — a folder with `brand.json` (+ logo), see
   [../brands/README.md](../brands/README.md). Client packs live outside the repo, passed by path.
2. **Inline `branding` object** in the content JSON — the low-friction path when the user
   hands over a logo and colors in-conversation:
   `"branding": {"logo": "logo.png", "display_name": "Acme", "colors": {"primary": "#0A6"},
   "footer": {"confidentiality": "INTERNAL USE ONLY"}}`. Deep-merged over the pack; theme
   token sets and chart colors re-derive automatically.
3. **`--logo path.png`** — quickest logo-only override.

The builder validates the JSON first and prints precise, fixable errors.

**Step 5 — Validate (required).** `python scripts/validate_html.py out.html` reads
`data-format` and applies the right checks: document integrity (one DOCTYPE/html/body,
nothing after `</html>`, unique IDs, no live `data-sample` content, classes actually
defined), both theme token sets, persisted toggle, theme-aware charts, no leftover
placeholders; deck nav / report TOC + print styles. Fix every error; **ship only on
`"status": "OK"`.** The validator blanks vendored-library `<script>` bodies before the
placeholder scan, so it gives the same verdict before and after `--inline-plotly`.

**Step 6 — QA by vision (required before delivery).** The validator reads structure, not
looks. One command produces the full set of screenshots:

```
python scripts/render_screenshots.py out.html --out-dir shots
```

It auto-detects the browser and format, then shoots a **full pass in the default theme**
(every slide / section) plus a **spot pass in the other theme** (first page + chart-bearing
pages — charts are the only theme-sensitive components). Read every PNG: premium feel, KPIs
and charts scale in, contrast in both themes, nothing overflowing (deck) or a broken
TOC/print layout (report). `--second-theme full` for full double coverage when the user will
present in both themes.

*QA hooks (also usable by hand):* `?theme=dark|light` forces a theme; `?slide=N` (1-based)
opens a deck on slide N; report sections are addressable as `#section-id`. Defaults:
boardroom = dark, clean/executive = light; toggle persists to `localStorage`
`deck-theme` / `report-theme`.

**If no browser can run in the environment** (missing system libs, no root — it happens in
sandboxes), `render_screenshots.py` detects it, runs a **structural self-check** instead, and
prints a REQUIRED DISCLOSURE paragraph. Deliver only with that disclosure attached verbatim;
never hack the environment or the scripts to fake the gate, and never skip it silently.

## Principles
1. **Match the format to the use.** Deck = full-viewport slides for clicking/presenting;
   report = a scrolling document with a TOC for detailed, printable material.
2. **Both themes are first-class.** Parallel dark/light token sets; the toggle restyles
   everything (cards, tables, charts, nav), defaults dark, and persists across reloads.
3. **KPIs dominate; narrative supports.** Big numbers up top; muted commentary beside them.
4. **Charts make one point,** are theme-aware, and re-render on toggle (and slide change in a deck).
5. **Premium, uncluttered, self-contained** — use the real-estate well; inline Plotly before sharing.

## Common mistakes
- Hand-editing a template or built file instead of editing `content.json` and rebuilding —
  the historical failure mode is a second document appended after `</html>` with invented
  class names and duplicate IDs. The validator now fails all of that; the builder makes it
  impossible.
- **Patching the builder/validator scripts** to get past a path error, missing asset, or
  validation failure. A field-test model did exactly this — the fix was fetching the full
  skill folder, not editing the engine. If blocked, stop and report what's missing.
- Guessing content field names (`bullets`/`title`/`events`) instead of running `--list` and
  `--validate-only` first.
- Forcing the wrong format: a dense reference report crammed into slides, or a click-through
  presentation flattened into one long scroll.
- Overstuffed slides — walls of bullets or three charts on one slide. Split them.
- Shipping without the validate → vision → inline-Plotly gates.
- Inconsistent numbers between deliverables built from different content files — reuse one
  content.json (or one source of numbers) per engagement.

## Validation checklist
- [ ] Format chosen deliberately (`data-format` deck or report) and fits the audience/use.
- [ ] Hero has eyebrow, large title, one-sentence lead, 3–4 KPI cards (from `meta`).
- [ ] **Deck:** full-screen slides; one message each; nav works (prev/next **and** ←/→; counter + dots; scroll resets).
- [ ] **Report:** ≥2 anchored sections; sticky TOC with scroll-spy; `@media print` clean; scrolls (no viewport lock).
- [ ] Toggle persists, defaults dark, and restyles cards, tables, charts, and nav in both themes.
- [ ] Style preset fits the audience (boardroom vs clean); branding applied if supplied
      (logo, palette, footer/confidentiality) — or cleanly absent if not.
- [ ] `validate_html.py` returns `OK`; vision pass clean in both themes.
- [ ] Plotly inlined for delivery — single self-contained file, CSP-safe.

## Bespoke path (capable models only, layouts the blocks can't express)
Copy [assets/deck-template.html](assets/deck-template.html) or
[assets/report-template.html](assets/report-template.html) and **edit the content in place**
— keep the CSS tokens, nav, and JS. Every sample block carries a `data-sample` attribute:
remove it from each block as you replace its content (the validator fails while any remain).
Add/remove `<section class="slide">` / `<section class="report-section" id="...">` blocks
only; never a second `<html>`, `<style>`, or `<script>` block, never a class the stylesheet
doesn't define. All gates (validate → vision → inline) still apply.

## Reference & assets
- [scripts/build_html.py](scripts/build_html.py) — the builder (default path); `--scaffold` emits a skeleton, `--list` shows the vocabulary, `--validate-only` checks content.
- [scripts/render_screenshots.py](scripts/render_screenshots.py) — one-command vision-QA screenshots (full default theme + spot second theme).
- [assets/styles/](assets/styles/) — the `clean` and `executive` preset overrides (boardroom is the base).
- [schema/content.schema.json](schema/content.schema.json) — the content contract.
- [examples/deck-content.json](examples/deck-content.json) / [examples/report-content.json](examples/report-content.json) — complete working inputs.
- [assets/shells/](assets/shells/) + [assets/components/](assets/components/) — what the builder assembles (do not edit casually; they define the class vocabulary).
- [../brands/README.md](../brands/README.md) — brand packs (logo, palette, fonts, footer).
- [assets/deck-template.html](assets/deck-template.html) / [assets/report-template.html](assets/report-template.html) — bespoke-path boilerplates.
- [references/design-system.md](references/design-system.md) — tokens, layouts, component specs.
- [scripts/validate_html.py](scripts/validate_html.py) — the required, mode-aware structural gate.
- [scripts/vendor_plotly.py](scripts/vendor_plotly.py) — fetch/inline Plotly for offline, CSP-safe delivery.

## Related skills
- [../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md) — the PowerPoint counterpart.
- [../building-document-templates/SKILL.md](../building-document-templates/SKILL.md) — reusable Office templates (built-ins + client families).
- [../crafting-presentation-narratives/SKILL.md](../crafting-presentation-narratives/SKILL.md) — story before slides.

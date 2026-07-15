---
name: presenting-with-html
description: Build a polished, self-contained HTML report or presentation — for anyone in the org, from a team status update to a board deck. Two formats (a slide DECK with full navigation, or a long-form REPORT with sticky TOC and print/PDF styles) times two style presets (dark-first BOARDROOM glassmorphism, or light-first CLEAN corporate) from one component system — KPI cards, charts, tables, timelines, comparisons, quotes, figures — with theme-aware Plotly and a persisted dark/light toggle. DEFAULT PATH: write a content JSON and run scripts/build_html.py — the builder owns the HTML shell, navigation, and styling, so the output is correct by construction. Branding is injected from a brand pack OR an inline branding object (logo path + colors in the content JSON); with no branding supplied, every branding placeholder collapses and the neutral default renders. Use when the user asks for an HTML report, presentation, dashboard, web-based slide deck, or a detailed HTML document to fill with content.
---

# Presenting with HTML

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

And two **style presets**, chosen per build (`--style` or `"style"` in the content JSON):

- **boardroom** (default) — dark-first glassmorphism, gradient accents; the premium
  presented-live look.
- **clean** — light-first, flat white panels, hairline borders, solid accents,
  print-oriented; what most client-facing corporate reports expect.

Both presets share the identical component vocabulary and support the dark/light toggle.

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

## Workflow (default: build from content)
```
Progress:
- [ ] 0. Choose format (deck vs report) + style (boardroom vs clean) from the request; ask if unstated
- [ ] 1. Story: overview -> insights -> patterns -> breakdowns -> conclusion (one message per slide/section)
- [ ] 2. Discover the vocabulary: python scripts/build_html.py --list  (formats, block types, brands)
- [ ] 3. Write content.json (see examples/deck-content.json / examples/report-content.json)
- [ ] 4. Build: python scripts/build_html.py --content content.json --out out.html --brand <name>
- [ ] 5. Validate: python scripts/validate_html.py out.html  -> must be "OK"
- [ ] 6. QA by vision: open in a browser (or headless screenshot) and Read each slide/section, both themes
- [ ] 7. Deliver self-contained: rebuild with --inline-plotly (or vendor_plotly.py --inline out.html)
```

**Step 0 — Choose the format and style.** Pick from the user's request; **if unstated, ask**
("slide deck to click through, or a long-form report to scroll/print?"). Signals: "deck /
slides / present / walk the board through it" → deck. "report / document / detailed / read /
print / PDF / share the write-up" → report. When still unsure, default to **deck** for
≤ ~7 messages of mostly-visual content, **report** for detailed/reference material or
anything printed. Style: "premium / boardroom / impressive / dark" → `boardroom`;
"corporate / conservative / client-facing / printable / clean" → `clean`. Default boardroom
for decks; for reports that will be printed or sent to a client, prefer `clean`.

**Step 1 — Story first.** Decide the narrative before writing JSON. Every slide/section
advances one message and the deliverable must answer: what happened, where did it
concentrate, how did it change, what to do next. A beautiful deliverable with no message fails.

**Step 3 — Write the content JSON.** The contract is
[schema/content.schema.json](schema/content.schema.json); start from the matching example in
[examples/](examples/). Essentials:

- `meta` (title, `title_accent`, eyebrow, lead, author, date, up to 4 `kpis`) generates the
  title slide / hero — don't add one yourself.
- Deck blocks: `section` (numbered divider), `bullets`, `kpi`, `cards`, `chart`, `table`,
  `two-col`, `text`, `quote`, `timeline`, `comparison`, `image`, `closing`. Report blocks:
  the same minus `section`; each may set `toc` for its contents-panel label.
- Charts are a simple spec — `{"chart_type": "bar|line|area|pie|scatter", "categories":
  [...], "series": [{"name", "values"}]}` — converted to theme-aware Plotly that restyles on
  the theme toggle. Raw `{"plotly": {"data", "layout"}}` passthrough exists for exotic charts.
- `image` blocks embed the file base64 (self-contained); paths resolve relative to the
  content JSON. `timeline` takes ordered `milestones`; `comparison` takes titled
  `left`/`right` item lists; `quote` is a pull-quote with optional attribution.
- Keep deck slides to one message: ~5 bullets, ≤4 KPIs, one chart. Push dense tables into a
  report or an appendix slide.

**Step 4 — Build.** Branding, three ways (all optional — with none, placeholders collapse
and the neutral default renders):

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
`"status": "OK"`.** A CDN-Plotly warning is expected until step 7.

**Step 6 — QA by vision (required before delivery).** The validator reads structure, not
looks. Open the file in a browser and view every slide/section in **both** dark and light. A
headless screenshot works for an automated look (Chromium/Edge `--headless=new
--screenshot`), then Read the image — confirm the premium feel, KPIs and charts scale in,
text has contrast in both themes, and nothing overflows (deck) or has a broken TOC/print
layout (report).

**Step 7 — Self-contained delivery (required before sharing).** Charts load Plotly from a
CDN while authoring, but an emailed/SharePoint/air-gapped file must not depend on the
network. Rebuild with `--inline-plotly`, or run
`python scripts/vendor_plotly.py --inline out.html`. The result is a single self-contained
`.html`. (Run `vendor_plotly.py --fetch` once to vendor the library locally if your
environment blocks the CDN.)

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
- [scripts/build_html.py](scripts/build_html.py) — the builder (default path); `--list` shows the vocabulary.
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

---
name: presenting-with-html
description: Build a polished, boardroom-ready HTML report or presentation as a self-contained slide deck — dark/light glassmorphism, KPI cards, interactive Plotly charts, arrow/keyboard/dot navigation, and a persisted theme toggle. Use when the user asks for an executive/leadership HTML report, a web-based slide deck, an "HTML dashboard/report" for CEO viewing, or a reusable premium HTML deck to fill with content. Ships a working boilerplate deck, a structural validator, and the full design system.
---

# Presenting with HTML

## Scope
Turn content or data into a **premium, slide-based HTML report** that feels like a modern
strategy deck — not an exported notebook or a long scrolling page. One self-contained
`.html` file: dark-gradient/glassmorphism styling, full-screen slides, KPI cards,
interactive Plotly charts, and a full HUD (arrow buttons, ←/→ keys, progress dots, slide
counter, persisted light/dark toggle). For PowerPoint decks use
[../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md); nail the
story first with [../crafting-presentation-narratives/SKILL.md](../crafting-presentation-narratives/SKILL.md).

## Core principle: adapt the boilerplate, don't reinvent it
[assets/deck-template.html](assets/deck-template.html) is a complete, working, verified
deck that already implements the whole pattern (both themes, nav, theme-aware Plotly,
responsive). **Copy it and replace the content** — text, KPI numbers, chart data, table
rows, and the set of slides. Keep the CSS design tokens, the HUD, and the JS behavior.
Add or remove `<section class="slide">` blocks freely; dots and the counter update
automatically. Never hand-roll a plain scrolling page unless the user explicitly asks for
a plain/tabular document.

## Workflow
```
Progress:
- [ ] 1. Story: overview -> insights -> patterns -> breakdowns -> conclusion (one message per slide)
- [ ] 2. Copy assets/deck-template.html; set the hero (eyebrow, title, lead, 3-4 KPIs)
- [ ] 3. Fill slides: highlights grid, overall chart, per-company/segment detail, closing recs
- [ ] 4. Wire charts: Plotly, theme-aware colors, friendly labels, unified hover
- [ ] 5. Keep BOTH themes premium; default dark; toggle persists and restyles charts
- [ ] 6. Validate: python scripts/validate_html.py report.html  -> must be "OK"
- [ ] 7. QA by vision: open in a browser (or headless screenshot) and Read each slide, both themes
```

**Step 1 — Story first.** Decide the narrative before styling. Every slide advances one
message and the deck must answer: what happened, where did it concentrate, how did it
change, what should leadership do next. A beautiful deck with no message fails.

**Step 6 — Validate (required).**
```bash
python scripts/validate_html.py report.html
```
Checks the deck structure, navigation (buttons + keyboard), a persisted toggle with BOTH
theme token sets, Plotly present when charts are used, and no leftover placeholders
(`{{ }}`, lorem ipsum, TODO/TBD). Fix every error; **ship only on `"status": "OK"`.**

**Step 7 — QA by vision (required before delivery).** The validator reads structure, not
looks. Open the file in a browser and view every slide in **both** dark and light. A
headless screenshot works for an automated look (Chromium/Edge `--headless=new
--screenshot`), then Read the image — confirm the glass/gradient premium feel, KPIs and
charts scale into the slide, text has contrast in both themes, and nothing overflows.

## Principles
1. **Slides, not scroll.** Full-viewport slides in a glass panel; internal scroll for long detail.
2. **Both themes are first-class.** Parallel dark/light token sets; the toggle restyles
   everything (cards, tables, charts, HUD), defaults dark, and persists across slides/reloads.
3. **KPIs dominate; narrative supports.** Big numbers up top; muted commentary beside them.
4. **Charts make one point,** are theme-aware, and re-render on toggle and slide change.
5. **Premium, uncluttered, CEO-ready** — text and charts use the slide real-estate well.

## Common mistakes
- A long scrolling page instead of a slide deck.
- A theme toggle that only recolors the page background, leaving cards/charts/tables wrong.
- Charts that don't restyle on theme change or don't re-fit on slide change (missing the
  `resize` dispatch / `Plotly.react`).
- Tiny or overflowing charts/text that waste the slide; raw data dumps outside an appendix.
- Shipping with leftover boilerplate content or a message-less "pretty" deck.

## Validation checklist
- [ ] Full-screen slides in glass panels; one message per slide; premium and uncluttered.
- [ ] Hero has eyebrow, large title, one-sentence lead, 3–4 KPI cards.
- [ ] Nav works: prev/next buttons **and** ←/→ keys; counter + click-to-jump dots; scroll resets.
- [ ] Toggle persists, defaults dark, and restyles cards, tables, charts, and HUD in both themes.
- [ ] Charts are Plotly, theme-aware, friendly labels, and re-render on toggle/slide change.
- [ ] Responsive: KPIs/columns restack on small screens; readable first.
- [ ] `validate_html.py` returns `OK`; vision pass clean in both themes.

## Reference & assets
- [assets/deck-template.html](assets/deck-template.html) — the working boilerplate to copy.
- [references/design-system.md](references/design-system.md) — tokens, slide types,
  component specs, chart/navigation/theme details.
- [scripts/validate_html.py](scripts/validate_html.py) — the required structural gate.

## Related skills
- [../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md) — the PowerPoint counterpart.
- [../crafting-presentation-narratives/SKILL.md](../crafting-presentation-narratives/SKILL.md) — story before slides.

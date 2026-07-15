---
name: presenting-with-html
description: Build a polished, self-contained HTML report or presentation — for anyone in the org, from a team status update to a board deck. Two formats from one design system: a slide DECK (full-screen slides, arrow/keyboard/dot navigation) or a long-form REPORT (scrolling document with a sticky table of contents and print/PDF styles). Both share dark/light glassmorphism, KPI cards, and interactive theme-aware Plotly charts with a persisted theme toggle. Use when the user asks for an HTML report, presentation, dashboard, web-based slide deck, or a detailed HTML document to fill with content. Ships working boilerplates for both formats, a mode-aware structural validator, and a helper to inline Plotly for offline delivery.
---

# Presenting with HTML

## Scope
Turn content or data into a **premium, self-contained HTML deliverable** that reads as one
design system — glassmorphism, KPI cards, interactive theme-aware Plotly charts, a
persisted light/dark toggle. It is for **everyone in the org**, not just executives, and it
handles **detailed** content as readily as a summary. Two formats, chosen per request:

- **Deck** — full-screen slides in a glass panel with a full HUD (arrow buttons, ←/→ keys,
  progress dots, slide counter). Best when the audience clicks through, presents live, or
  wants a boardroom feel. One message per slide.
- **Report** — a long-form scrolling document with a sticky table of contents, scroll-spy,
  and print/PDF styles. Best for detailed reports read top-to-bottom, referenced, or
  printed — many sections, dense tables, thorough narrative.

For PowerPoint use [../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md);
nail the story first with [../crafting-presentation-narratives/SKILL.md](../crafting-presentation-narratives/SKILL.md).

## Core principle: adapt the boilerplate, don't reinvent it
Two complete, working, verified boilerplates that share the **same design tokens, theme JS,
and chart-registration core** so their output is visually one system:

- [assets/deck-template.html](assets/deck-template.html) — the slide deck (`data-format="deck"`).
- [assets/report-template.html](assets/report-template.html) — the long-form report (`data-format="report"`).

**Copy the one that matches the chosen format and replace the content** — text, KPI numbers,
chart data, table rows, and the set of slides/sections. Keep the CSS design tokens, the
navigation, and the JS behavior. In the deck add/remove `<section class="slide">`; in the
report add/remove `<section class="report-section" id="...">` — dots/counter (deck) and the
TOC/scroll-spy (report) update automatically. Do not hand-roll a layout from scratch.

## Step 0 — Choose the format
Pick from the user's request; **if unstated, ask** ("slide deck to click through, or a
long-form report to scroll/print?"). Signals: "deck / slides / present / walk the board
through it" → deck. "report / document / detailed / read / print / PDF / share the write-up"
→ report. When still unsure, default to **deck** for ≤ ~7 messages of mostly-visual content,
**report** for detailed/reference material or anything meant to be printed.

## Workflow
```
Progress:
- [ ] 0. Choose format (deck vs report) from the request; ask if unstated
- [ ] 1. Story: overview -> insights -> patterns -> breakdowns -> conclusion (one message per slide/section)
- [ ] 2. Copy the matching template; set the hero (eyebrow, title, lead, 3-4 KPIs)
- [ ] 3. Fill slides/sections: highlights, overall chart, per-segment detail, closing recs
- [ ] 4. Wire charts: Plotly, theme-aware colors, friendly labels, unified hover
- [ ] 5. Keep BOTH themes premium; default dark; toggle persists and restyles charts
- [ ] 6. Validate: python scripts/validate_html.py report.html  -> must be "OK"
- [ ] 7. QA by vision: open in a browser (or headless screenshot) and Read each slide/section, both themes
- [ ] 8. Make self-contained for delivery: python scripts/vendor_plotly.py --inline report.html
```

**Step 1 — Story first.** Decide the narrative before styling. Every slide/section advances
one message and the deliverable must answer: what happened, where did it concentrate, how did
it change, what to do next. A beautiful deliverable with no message fails.

**Step 6 — Validate (required).**
```bash
python scripts/validate_html.py report.html
```
Reads `data-format` and applies the right checks. **Format-agnostic (both modes):** BOTH
theme token sets, a persisted toggle, Plotly present when charts are used, theme-aware
re-render, no leftover placeholders (`{{ }}`, lorem ipsum, TODO/TBD). **Deck:** slide
structure + navigation (buttons + keyboard + dots). **Report:** ≥2 anchored `.report-section`
blocks, an in-page TOC, scroll-spy, and `@media print` styles. Fix every error; **ship only
on `"status": "OK"`.** A warning that Plotly loads from the CDN is expected until step 8.

**Step 7 — QA by vision (required before delivery).** The validator reads structure, not
looks. Open the file in a browser and view every slide/section in **both** dark and light. A
headless screenshot works for an automated look (Chromium/Edge `--headless=new
--screenshot`), then Read the image — confirm the glass/gradient premium feel, KPIs and
charts scale in, text has contrast in both themes, and nothing overflows (deck) or has a
broken TOC/print layout (report).

**Step 8 — Self-contained delivery (required before sharing).** The templates load Plotly
from a CDN so charts work instantly while authoring — but an emailed/SharePoint/air-gapped
file, or one under a strict org CSP, must not depend on the network. Inline the library:
```bash
python scripts/vendor_plotly.py --inline report.html      # folds Plotly into the file
```
The result is a single self-contained `.html`. (Run `--fetch` once to vendor the library
locally if your environment blocks the CDN; see the script header.)

## Principles
1. **Match the format to the use.** Deck = full-viewport slides for clicking/presenting;
   report = a scrolling document with a TOC for detailed, printable material. Don't force a
   dense report into slides, or turn a live-presentation deck into a wall of scroll.
2. **Both themes are first-class.** Parallel dark/light token sets; the toggle restyles
   everything (cards, tables, charts, nav), defaults dark, and persists across reloads.
3. **KPIs dominate; narrative supports.** Big numbers up top; muted commentary beside them.
4. **Charts make one point,** are theme-aware, and re-render on toggle (and on slide change in a deck).
5. **Premium, uncluttered, self-contained** — use the real-estate well; inline Plotly before sharing.

## Common mistakes
- Forcing the wrong format: a dense reference report crammed into slides, or a click-through
  presentation flattened into one long scroll.
- A theme toggle that only recolors the page background, leaving cards/charts/tables wrong.
- Charts that don't restyle on theme change, or (deck) don't re-fit on slide change — missing
  the `resize` dispatch / `Plotly.react`.
- Tiny or overflowing charts/text; raw data dumps with no structure (put bulk tables in a
  report section or a deck appendix).
- A report with no TOC/anchors or broken print layout; a deck with broken navigation.
- Shipping with leftover boilerplate, a message-less "pretty" deliverable, or a live CDN
  dependency (not self-contained — run step 8).

## Validation checklist
- [ ] Format chosen deliberately (`data-format` deck or report) and fits the audience/use.
- [ ] Hero has eyebrow, large title, one-sentence lead, 3–4 KPI cards.
- [ ] **Deck:** full-screen slides; one message each; nav works (prev/next **and** ←/→; counter + dots; scroll resets).
- [ ] **Report:** ≥2 anchored sections; sticky TOC with scroll-spy; `@media print` clean; scrolls (no viewport lock).
- [ ] Toggle persists, defaults dark, and restyles cards, tables, charts, and nav in both themes.
- [ ] Charts are Plotly, theme-aware, friendly labels, re-render on toggle (and slide change in a deck).
- [ ] Responsive: KPIs/columns restack on small screens; readable first.
- [ ] `validate_html.py` returns `OK`; vision pass clean in both themes.
- [ ] Plotly inlined for delivery (`vendor_plotly.py --inline`) — single self-contained file, CSP-safe.

## Reference & assets
- [assets/deck-template.html](assets/deck-template.html) — the slide-deck boilerplate to copy.
- [assets/report-template.html](assets/report-template.html) — the long-form report boilerplate to copy.
- [references/design-system.md](references/design-system.md) — shared tokens, both formats'
  layouts, component specs, chart/navigation/theme details, and the brand-color swap.
- [scripts/validate_html.py](scripts/validate_html.py) — the required, mode-aware structural gate.
- [scripts/vendor_plotly.py](scripts/vendor_plotly.py) — fetch/inline Plotly for offline, CSP-safe delivery.

## Related skills
- [../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md) — the PowerPoint counterpart.
- [../crafting-presentation-narratives/SKILL.md](../crafting-presentation-narratives/SKILL.md) — story before slides.

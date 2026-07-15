# Deck Anatomy

Reusable layouts, slide types, and the typography/spacing rules that keep a deck
consistent. The shipped [../assets/starter-template.pptx](../assets/starter-template.pptx)
implements all of this — copy it and refill rather than rebuilding a master from scratch.

## Contents
- The core layout set
- Slide types
- Typography
- Color and spacing
- Chart rules on slides
- Brand tokens (swap)
- Verify by rendering

## The core layout set
Define these on the slide master; build every slide from one of them. The starter deck
ships one worked example of each.
1. **Title** — deck title, subtitle, presenter, date.
2. **Section divider** — big number/word, section name.
3. **Content** — headline title + body (bullets or single visual).
4. **Two-column** — text | visual, or compare A | B.
5. **Full-bleed visual** — one image/chart with a short caption.
6. **Closing** — summary/ask + contact/next steps.

## Slide types (by job)
- **Takeaway slide:** one message, one supporting visual.
- **Evidence slide:** one chart making one point, directly labeled.
- **Process slide:** left-to-right or top-down diagram, ≤6 steps.
- **Comparison slide:** table or small multiples, aligned units.
- **Quote/impact slide:** one line, large, whitespace around it.

## Typography
- Two type roles max: a display font for titles, a clean sans for body.
- Live-talk minimums: title ≥32pt, body ≥24pt. Never below 18pt on any slide.
- Left-align body text; avoid center-aligned paragraphs and justified text.
- Max ~6 bullets, ~6 words each as a guide — fewer is better.

## Color and spacing
- One accent color for emphasis; neutrals for everything else.
- Keep ≥5% margin of empty space around all edges; do not fill to the bezel.
- Align every object to a shared grid; use guides, not eyeballing.
- Consistent gap between bullets and between objects.

## Chart rules on slides
- One point per chart; put the point in the slide title.
- Remove gridlines, chart borders, redundant legends, and excess decimals.
- Label series/values directly rather than forcing a legend lookup.
- Bar for comparison, line for trend, no pie beyond 2–3 slices, never 3-D.
- Highlight the one series that matters; grey the rest.

## Brand tokens (swap)
The starter deck's look is defined by a small set of tokens — `PALETTE` (background,
ink, muted, accent×3, hairline, panel) and `FONT` — at the top of
[../scripts/build_starter_template.py](../scripts/build_starter_template.py). Change
those and regenerate to re-skin the entire deck, the same way the HTML skill swaps its
`--accent` tokens. This keeps company identity as data, not code: for a real org, drop
their `.potx`/theme in place of the neutral default rather than hand-editing slides.
Keep two type roles and one accent for emphasis; don't introduce per-slide colors.

## Verify by rendering
Structure is necessary but not sufficient. `validate_pptx.py` reads markup; it cannot
see autofit shrink, clipped or overlapping text, or off-brand color, and it cannot
resolve font sizes inherited from the master. Always finish with
[../scripts/render_pptx.py](../scripts/render_pptx.py) and Read every slide — the same
render-and-look discipline the HTML skill applies in a browser.

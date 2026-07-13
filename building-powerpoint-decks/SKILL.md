---
name: building-powerpoint-decks
description: Build clean, on-brand Microsoft PowerPoint (.pptx) decks from content or an outline — using slide masters, consistent layouts, readable typography, and purposeful visuals. Use when the user asks to "make a PowerPoint", "create slides / a deck", "turn this into a presentation", or build a pitch/board/training deck. Produces a professional, consistent .pptx. For the narrative and story arc first, pair with crafting-presentation-narratives.
---

# Building PowerPoint Decks

## Scope
Turning approved content into a professional `.pptx`: slide architecture, master/
layout use, typography, visual hierarchy, charts, and consistency. The story and
message design come first from
[crafting-presentation-narratives](../crafting-presentation-narratives/SKILL.md);
brand application from [producing-branded-documents](../producing-branded-documents/SKILL.md).

## Purpose
Produce a deck that is visually consistent, readable from the back of a room, and
built on masters so it can be restyled or extended without manual cleanup.

## When to use this skill
- "Make a PowerPoint / deck / slides / presentation."
- "Turn this document/outline into slides."
- Pitch, board, sales, training, or status decks.
- Cleaning up an inconsistent existing deck.

## When NOT to use this skill
- The message/argument isn't settled yet → [crafting-presentation-narratives](../crafting-presentation-narratives/SKILL.md) first.
- Detailed data tables/models → engineering-excel-workbooks.
- A read-not-present document → use a report skill.
- Google-native → building-google-slides.

## Inputs
- The narrative/outline (or content to structure), one key message per slide.
- Audience, setting (presented live vs. sent to read), and time limit.
- Brand assets or template; if none, a clean minimal theme.
- Data for any charts.

## Outputs
- A `.pptx` built on a slide master with consistent layouts, one idea per slide,
  legible type, and charts that make one point each.
- Optional speaker notes and a title/agenda/section structure.

## Workflow
```
Progress:
- [ ] 1. Lock the narrative: one message per slide, in order
- [ ] 2. Set up the master and 3–5 reusable layouts
- [ ] 3. Draft slides as headlines (the takeaway is the title)
- [ ] 4. Add supporting visuals; one point per chart
- [ ] 5. Apply consistent type, spacing, and color
- [ ] 6. Add title, agenda, section dividers, and speaker notes
- [ ] 7. Review for legibility, consistency, and slide count
- [ ] 8. Validate & repair: run the validator, fix every error, re-run until clean
```

**Step 1 — Narrative locked.** Do not open slide design until the story is set.
Each slide earns its place by advancing one message.

**Step 2 — Master first.** Define the slide master and a small set of layouts
(title, section, content, two-column, full-bleed image, chart). Everything inherits
from these; never format slides individually.

**Step 3 — Headline slides.** Write the *takeaway* as the slide title ("EMEA
margin recovered to 18%"), not a topic label ("EMEA margin"). The body supports it.

**Step 4 — Visuals with one job.** Each chart/diagram makes exactly one point;
strip gridlines, legends, and decimals that don't serve it. Follow dataviz
principles for chart clarity.

**Step 5 — Consistency.** Same fonts, sizes, colors, and alignment everywhere.
Align to a grid; keep generous margins.

**Step 6 — Wayfinding.** Title, agenda, and section dividers orient the audience.
Put detail in speaker notes, not on the slide.

**Step 7 — Review.** Read every slide from across the room; cut any slide that
doesn't advance the argument.

**Step 8 — Validate & repair (mandatory before delivery).** Run the bundled
validator, read its JSON `errors`, fix each, and **re-run until `status` is `OK`**:

```bash
python scripts/validate_pptx.py path/to/deck.pptx
```

It fails on leftover placeholder text (`lorem ipsum`, `TBD`, `{{tag}}`, …) and warns
on empty slides, title-less slides, and wall-of-text slides. Design judgment (the
checklist below) still applies — the script catches the mechanical misses.

## Principles
1. **One idea per slide.** If a slide has two messages, split it.
2. **The title is the message,** not the topic.
3. **Slides support the speaker; they are not the document.** Detail → notes/appendix.
4. **Consistency via masters,** never per-slide formatting.
5. **Signal over decoration.** Every element must earn its pixels.

## Decision framework
- **Presented live?** Minimal text, big visuals, notes carry detail.
- **Sent to read?** Slightly denser is OK, or send a document instead.
- **Data point?** Chart. **Process?** Diagram. **Comparison?** Table or small multiples.
- **>20 content slides for a 20-min talk?** Cut — ~1 slide/minute is the ceiling.

## Common mistakes
- **Wall-of-text slides** — the audience reads instead of listening.
- **Topic titles** instead of takeaway titles.
- **Per-slide formatting** that drifts — fix the master instead.
- **Chartjunk**: 3-D bars, dual axes, rainbow palettes, unlabeled axes.
- **Tiny fonts** (<24pt body for live talks).
- **Inconsistent alignment** — objects nudged by hand off any grid.

## Validation checklist
- [ ] Every slide has one clear message stated in the title.
- [ ] All slides use master layouts; no orphan formatting.
- [ ] Fonts, sizes, colors, and alignment are consistent throughout.
- [ ] Body text ≥24pt for live presentation; readable from the back.
- [ ] Each chart makes one point and is labeled directly.
- [ ] Agenda + section dividers present; slide count fits the time.
- [ ] Images high-resolution; alt text set; color-contrast sufficient.
- [ ] Speaker notes carry the detail, not the slides.

## Edge cases
- **Board/exec decks:** lead with the ask/recommendation; appendix holds backup.
- **Sent-not-presented:** consider a document; if slides, add enough context to stand alone.
- **Large data:** summarize on-slide, link the full workbook.
- **Accessibility:** reading order set, alt text, no color-only meaning, captions on media.

## Related skills
- [crafting-presentation-narratives](../crafting-presentation-narratives/SKILL.md) — story before slides.
- building-google-slides — Google equivalent.
- [producing-branded-documents](../producing-branded-documents/SKILL.md) — brand application.
- designing-dashboards — for live data views.

## Reference files
- [references/deck-anatomy.md](references/deck-anatomy.md) — layouts, slide types, and typography rules.

## Scripts
- [scripts/validate_pptx.py](scripts/validate_pptx.py) — **run this** before delivery.
  Fails on leftover placeholder text; warns on empty / title-less / wall-of-text
  slides. JSON report, non-zero exit on error → drives the Step 8 loop. Requires `python-pptx`.

## Examples
**Input:** "Turn this 6-page strategy memo into a 10-slide board deck."
**Output:** Title → Agenda → 1 recommendation slide (the ask) → 3 evidence slides
with one chart each → risks → timeline → next steps → appendix. Every title is the
takeaway; all slides on two master layouts; detail in speaker notes.

## Templates
- [templates/slide-outline.md](templates/slide-outline.md) — a fill-in slide-by-slide outline.

## Automation opportunities
- Generate the deck from a structured outline (Markdown/JSON) so content and layout regenerate.
- Reuse a master `.potx` template across the org for instant brand consistency.
- Pipe chart data from a workbook so figures refresh with the source.

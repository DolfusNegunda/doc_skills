---
name: building-powerpoint-decks
description: Build clean, on-brand Microsoft PowerPoint (.pptx) decks from content or an outline — using slide masters, consistent layouts, readable typography, and purposeful visuals. Use when the user asks to "make a PowerPoint", "create slides / a deck", "turn this into a presentation", or build a pitch/board/training deck. STEP 0 — before authoring anything, check the built-in template library (registry.py list): standard deck shapes (exec update/QBR, kickoff, proposal, report-out) exist as branded, fill-ready templates where you only write a content JSON — the safest path for any model. Author with python-pptx only for bespoke decks. For the narrative and story arc first, pair with crafting-presentation-narratives.
---

# Building PowerPoint Decks

## Scope
Turning approved content into a professional `.pptx`: slide architecture, master/
layout use, typography, visual hierarchy, charts, and consistency. The story and
message design come first from
[crafting-presentation-narratives](../crafting-presentation-narratives/SKILL.md);
brand application from the shared brand packs ([../brands/README.md](../brands/README.md)).

## Purpose
Produce a deck that is visually consistent, readable from the back of a room, and
built on masters so it can be restyled or extended without manual cleanup.

## Step 0 — Fill a built-in template before you build (decision gate)
The suite ships fill-ready deck templates in the document-template registry:

- **`flex_deck`** — the universal composable deck. Its `body` is an ORDERED list of
  typed entries (agenda, bullets, numbered steps, stat cards, two-col, team, timeline,
  native **chart** from data, native **table**, image evidence, quote, section divider)
  in ANY mix and order — the scaffold prints the full type menu. Charts/tables are real
  editable PowerPoint objects built from the entry's data, styled from the brand pack.
  Prefer this whenever the content wants varied visuals or a custom slide sequence.
- **`exec_update`, `project_kickoff`, `proposal`, `report_out`** — fixed-shape decks
  for their standard narratives, with repeatable topic/finding/evidence slide groups.

All are brand-pack-driven and built by `build_template_library.py`. If the requested
deck matches any of these, **do not author slides at all**; run the deterministic fill
path (safe for any model, however small):

```bash
cd ../building-document-templates
python scripts/registry.py list                                        # what exists
python scripts/registry.py scaffold --builtin exec-update --out content.json
# edit content.json (scaffold prints per-field guidance AND a slide guide:
# what each slide is for, which are repeatable, which are optional)
python scripts/fill.py --client _builtin --doc-type exec_update --data content.json --out out.pptx
python scripts/validate.py out.pptx --client _builtin --doc-type exec_update   # must be OK
# (same selector as fill.py — resolves the template+manifest gates automatically;
#  do NOT substitute building-powerpoint-decks/validate_pptx.py, which is the
#  authoring-path style checker and skips the manifest gates)
python ../building-powerpoint-decks/scripts/render_pptx.py out.pptx    # vision pass, every slide
```

**Templates are expandable, not fixed.** A manifest `slide_group` marks a slide as a
repeating unit: its scaffold key is a **list of objects, one object per slide**. The
engine clones the designer slide byte-for-byte per entry — same layout, theme, and art —
so more content means more slides of the same kind, never a crammed slide. Match content
to slide shape: one topic (heading + 3–6 bullets) per `topic_slides` entry; one chart
image per `evidence_slides` entry. Optional groups (`min: 0`, e.g. evidence visuals)
disappear entirely when their list is empty or the key is omitted — no orphan
placeholder slide. Never paste two topics into one entry, and never clone slides by
hand — the entry count IS the slide count.

The library is generated per brand pack by
[scripts/build_template_library.py](scripts/build_template_library.py) (see
[../brands/README.md](../brands/README.md)); externally sourced templates join it via
[../building-document-templates/references/external-intake.md](../building-document-templates/references/external-intake.md).
Continue below **only** when no template fits (bespoke structure, unusual format).

## The layout gallery (bespoke visual decks)
[assets/layout-gallery.pptx](assets/layout-gallery.pptx) is a de-branded, 147-slide
professional layout library — one showcase slide per layout (covers, agendas, processes,
roadmaps, funnels, pyramids, comparisons, maps…), content in empty placeholders, neutral
CLIENT-LOGO chips where an org logo goes. For a bespoke deck: **shortlist slides from
[assets/layout-gallery-index.md](assets/layout-gallery-index.md)** (per-slide category,
text/picture slot counts, size hints), **render your shortlist and look**
(`render_pptx.py` — the index tells you what a slide is for; only vision tells you it
fits), then copy the gallery, delete everything else, and type into the placeholders —
never rebuild the diagrams. Avoid slides whose art encodes quantities (fixed donut/bar
percentages) unless your numbers match the art. Fill-ready templates CAN be curated
from it with [scripts/derive_gallery_templates.py](scripts/derive_gallery_templates.py),
but gallery-derived templates are **fixed-layout** (no repeatable slide groups) — a live
field test showed small models pick them over the expandable library and cram content;
the generated library above is the fill path. Curate from the gallery only for a
deliberate, fixed-shape deck.

## Core principle: adapt the starter deck, don't reinvent it
[assets/starter-template.pptx](assets/starter-template.pptx) is a complete, styled,
16:9 deck with one example of each core layout (title, section divider, content,
two-column, chart/evidence, closing). **Copy it and replace the content** — titles,
bullets, chart data — keeping the geometry, palette, and type scale. It is the PPTX
analog of the HTML skill's boilerplate: starting from a working, on-brand deck beats
building a master from a blank file every time. Regenerate or restyle it with
[scripts/build_starter_template.py](scripts/build_starter_template.py); the brand is a
few tokens (`PALETTE`, `FONT`) at the top — change them and every slide re-skins, or
drop the org's real `.potx` over the theme ("branding is data, not code").

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
- [ ] 0. Check the built-in library first (registry.py list) — fill, don't build, when a template fits
- [ ] 1. Lock the narrative: one message per slide, in order
- [ ] 2. Copy assets/starter-template.pptx (or the org .potx); confirm the layouts you need
- [ ] 3. Draft slides as headlines (the takeaway is the title)
- [ ] 4. Add supporting visuals; one point per chart
- [ ] 5. Apply consistent type, spacing, and color
- [ ] 6. Add title, agenda, section dividers, and speaker notes
- [ ] 7. Review for legibility, consistency, and slide count
- [ ] 8. Validate: run validate_pptx.py, fix every error, re-run until clean
- [ ] 9. Vision QA: render_pptx.py, then Read every slide — fix overflow/overlap/off-brand, re-render
```

**Step 1 — Narrative locked.** Do not open slide design until the story is set.
Each slide earns its place by advancing one message.

**Step 2 — Start from the starter.** Copy [assets/starter-template.pptx](assets/starter-template.pptx)
(or the organization's own `.potx`) and build on its layouts. Everything inherits
from the master/theme; never format slides individually from a blank file.

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

**Step 8 — Validate & repair (mandatory).** Run the bundled validator, read its JSON
`errors`, fix each, and **re-run until `status` is `OK`**:

```bash
python scripts/validate_pptx.py path/to/deck.pptx
```

It fails on leftover placeholder text (`lorem ipsum`, `TBD`, `{{tag}}`, …) and warns
on empty / title-less / wall-of-text slides, shapes that overflow the slide, explicit
sub-18pt fonts, and low-DPI images. It reads *markup only* — it cannot resolve fonts
inherited from the master, or see autofit shrink, overlap, or off-brand color.

**Step 9 — Vision QA (mandatory before delivery).** Exactly like the HTML skill opens
its deck in a browser: the validator reads structure, not looks. Render every slide
and **Read each image**:

```bash
python scripts/render_pptx.py path/to/deck.pptx
```

This exports one PNG per slide (Microsoft PowerPoint via COM on Windows/Office; falls
back to instructions for LibreOffice `--convert-to pdf`). Read every slide and confirm:
text fits with no clipping/autofit-shrink/overlap, titles are the takeaway, alignment
is consistent, each chart makes its one point, and color/contrast is on-brand. Fix in
the deck and re-render. The two gates are complementary — ship only when both are clean.

## Principles
1. **One idea per slide.** If a slide has two messages, split it.
2. **The title is the message,** not the topic.
3. **Slides support the speaker; they are not the document.** Detail → notes/appendix.
4. **Consistency via masters,** never per-slide formatting.
5. **Signal over decoration.** Every element must earn its pixels.
6. **See it before you send it.** A deck that passes the structural gate can still look
   broken; render it and Read every slide. Structure gate + vision gate, both mandatory.

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

## Portability (self-contained delivery)
A deck sent to another machine can lose its look if fonts or images aren't inside the
file — the analog of inlining Plotly in the HTML skill. Before sending:
- **Images:** embed, don't link (python-pptx embeds by default; never reference a local path).
- **Fonts:** embed them — PowerPoint → File ▸ Options ▸ Save ▸ *Embed fonts in the file*.
  This is a manual PowerPoint step; python-pptx cannot embed fonts. If you can't embed,
  stick to fonts every recipient has (e.g. the Office defaults) so nothing substitutes.

## Validation checklist
- [ ] Every slide has one clear message stated in the title.
- [ ] All slides use master/starter layouts; no orphan formatting.
- [ ] Fonts, sizes, colors, and alignment are consistent throughout.
- [ ] Body text ≥24pt for live presentation; readable from the back.
- [ ] Each chart makes one point and is labeled directly.
- [ ] Agenda + section dividers present; slide count fits the time.
- [ ] Images high-resolution; alt text set; color-contrast sufficient.
- [ ] Speaker notes carry the detail, not the slides.
- [ ] `validate_pptx.py` returns `OK`; **vision pass** (render + Read) clean — no overflow, overlap, or off-brand color.
- [ ] Portable: images embedded; fonts embedded or safe defaults only.

## Edge cases
- **Board/exec decks:** lead with the ask/recommendation; appendix holds backup.
- **Sent-not-presented:** consider a document; if slides, add enough context to stand alone.
- **Large data:** summarize on-slide, link the full workbook.
- **Accessibility:** reading order set, alt text, no color-only meaning, captions on media.

## Related skills
- [crafting-presentation-narratives](../crafting-presentation-narratives/SKILL.md) — story before slides.
- building-google-slides — Google equivalent.
- designing-dashboards — for live data views.

## Reference files
- [references/deck-anatomy.md](references/deck-anatomy.md) — layouts, slide types, and typography rules.

## Assets
- [assets/starter-template.pptx](assets/starter-template.pptx) — the styled 16:9 boilerplate to copy (Step 2).

## Scripts
- [scripts/validate_pptx.py](scripts/validate_pptx.py) — **Step 8 gate.** Fails on leftover
  placeholder text; warns on empty / title-less / wall-of-text slides, overflowing shapes,
  explicit sub-18pt fonts, and low-DPI images. JSON report, non-zero exit on error. `python-pptx`.
- [scripts/render_pptx.py](scripts/render_pptx.py) — **Step 9 vision QA.** Renders one PNG
  per slide (PowerPoint COM; LibreOffice fallback) so you can Read the actual look. `pywin32`.
- [scripts/build_starter_template.py](scripts/build_starter_template.py) — (re)generates the
  starter deck; edit `PALETTE`/`FONT` to re-brand. `python-pptx`.
- [scripts/build_template_library.py](scripts/build_template_library.py) — **Step 0 source.**
  Generates the built-in fill-ready deck library (exec_update, project_kickoff, proposal,
  report_out) into the document-template registry from a brand pack (`--brand <name-or-path>`), each with
  its manifest. `python-pptx` + `pillow`.

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

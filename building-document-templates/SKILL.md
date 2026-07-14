---
name: building-document-templates
description: Turn a client's existing Word (.docx) or PowerPoint (.pptx) file into a reusable, governed template — same layout, fonts, logos and styles, with the variable content swapped for placeholders — then fill it to produce consistent future documents from data. Governs a FAMILY system: one canonical template per document family (Lessons Learned, Change Note, Kickoff, Signoff…) that later files converge to, rather than a divergent per-file clone. Use when the user asks to "create a template", "templatize this document/deck", "make this reusable", "build a standard format", or "produce the same kind of document again just with new content". Ships a tested engine (templatize → registry → fill → validate, with table-row expansion, source-residue checks and unsupported-object flagging) plus placeholder/governance conventions, not just an empty copy.
---

# Building Document Templates

## HARD RULES (read first — violating these produced broken output)
1. **Use the engine. Never hand-edit the file.** You MUST go through
   `templatize.py` → `fill.py`. Do **not** open the document and set text yourself
   (no `text_frame.text = …`, no `paragraph.text = …`, no rebuilding shapes/slides,
   no writing your own python-docx/pptx edit script). Naive text-setting **strips run
   formatting** (bold, size, font, colour) — it is exactly why a filled cover title
   comes out in the wrong font. The engine's replacement preserves the run's formatting;
   your hand edit will not.
2. **Build INTERACTIVELY — confirm EVERY section AND every image with the user.** The
   build is a conversation, not a silent pass. Go section by section (cover, intro,
   objectives, DoV/scope, team, timeline, communication, next steps, appendix…) and ask
   the user what varies vs. stays. Then go IMAGE by IMAGE: present each embedded picture
   and confirm preserve (branding: logos, cover art, brand bars) vs. placeholder
   (project-specific: timelines, Gantt charts, screenshots, milestone trackers). Do not
   silently leave project-specific content (sections OR images) with the previous
   project's data. Heuristics mis-classify (a milestone tracker embedded as a JPEG XR
   image looked like "furniture") — the per-image confirmation is what catches this.
   If a section/image needs new content, it must become a field/placeholder.
3. **Vision-QA is mandatory.** After filling, render the output with `render_pages.py`
   and Read every page. Confirm: title/heading fonts preserved, the cover updated,
   logos swapped where intended, nothing overflows or misaligns, no stale content.
4. **Swap logos and fix metadata explicitly.** A client logo that should change must be
   an **image slot**; the document Title/date on a cover is often a **property** — set
   both up as fields, or they silently keep the source client's values.
5. **Never claim a change you did not verify by rendering.** Report only what the vision
   pass confirms.
6. **Converge to the canonical family template — don't fork.** A new file of a known
   family (Lessons Learned, Change Note, Kickoff, Signoff…) must map onto that family's
   ONE canonical template (extract its content → fill), producing the family's consistent
   style. Only create a new subtype for a genuine *structural* reason, recorded in
   governance — never because two files merely differ in content or minor layout.
7. **Flag unsupported objects — never fake success.** SmartArt/diagram text and native
   charts are NOT fillable (python-docx/pptx can't see their text). `propose` and
   `validate` surface these; when a page depends on them, say what can and cannot be
   templated and require a rebuild-or-accept decision. Do not report a deck as fully
   templated when its team-cards/agenda/timeline are SmartArt.

## Scope
Turn a real example document into a reusable **template + manifest**, register it in
a **gallery** keyed by client and document type, and **fill** it on demand to produce
consistent future documents. Covers Word (`.docx`) and PowerPoint (`.pptx`) end to
end. Excel and PDF are handled at the edges — see **Format support** below. The
one-off document itself is built with the relevant authoring skill; brand comes from
[producing-branded-documents](../producing-branded-documents/SKILL.md).

## Core principle: preserve + inject, never rebuild
A client's file **already is the template** — its layout, fonts, logos, slide masters
and styles are exactly what "consistent" means. Templatizing keeps that file intact
and only **swaps the variable text for `{{ placeholder }}` tags**. Never rebuild the
layout by hand and never re-solve OOXML internals. Filling later touches only the
placeholder text, so every produced document looks identical to the client's original.

## Family-template system (the operating model)
The goal is not per-file cloning — it is **one canonical template per document family**
that every future file of that family converges to, so all Lessons Learned look alike,
all Change Notes look alike, etc.

- **First time (bootstrap):** the user gives a real file → identify its **family** →
  analyse it visually + structurally → if ≥2 exemplars exist, compare them to separate
  what's fixed (structure/branding) from what varies (content) → build the canonical
  template + manifest → register it under `registry/_families/<family>/`.
- **Next time (reuse):** identify the family → **extract the new file's content** into a
  `content.json` keyed to the family schema → fill the canonical template → validate
  (leftover tags + structure + **source-residue** + unsupported flags) → visual QA →
  deliver only if residue-clean and visually clean.

Convergence rule: a divergent source layout (e.g. a Lessons-Learned deliverables table
with a different column set) is **absorbed** into the canonical schema, not preserved as
a fork. Subtypes exist only for a real structural reason and are recorded in governance.

## The engine
```text
scripts/
  templatize.py   # client file -> proposes fixed/variable split (+ flags unsupported objects) -> template + manifest
  fill.py         # template + data JSON -> finished document; expands LIST bullets AND table ROW-GROUPS (+ optional --export-pdf)
  validate.py     # gate: no leftover tags, structure preserved, SOURCE-RESIDUE check, unsupported-object surface
  render_pages.py # render docx/pptx/pdf -> one PNG per page for VISION inspection (faithful: shows logos/branding/graphics)
  registry.py     # browse the gallery: list / find / show templates
  common.py       # format detection, placeholders, manifest I/O, docProps, image slots, unsupported-object detection
registry/
  _families/<family>/                  # GOVERNED canonical family templates (Lessons Learned, Change Note, …)
      template.docx|pptx               # branding/structure preserved, all content -> placeholders/row-groups
      manifest.json                    # fields, row_groups, source_terms, owner, version, changelog
  <client>/<doc-type>/                 # optional per-client instances (default is: fill the family template, don't fork)
```
Point `$TEMPLATE_REGISTRY` at a shared folder to keep the gallery outside the repo.

**Engine capabilities added for the family system:**
- **Table-row expansion (`fill.py`)** — a `row_group` in the manifest (`{name, columns:[field,…]}`)
  makes the fill clone a table's template `<w:tr>` once per data item (real repeating rows),
  where the old list expansion only stacked paragraphs in one cell. `data[group]` is a list
  of dicts keyed by the column fields; an empty list removes the template row (header stays).
- **Source-residue check (`validate.py`)** — `--source-terms` / manifest `source_terms`
  fails the fill if source-exemplar content (client/project/code/dates/domain terms) survives.
  "No leftover tags" ≠ "successfully reused". Use project-IDENTIFYING terms, not recurring people.
- **Unsupported-object flagging (`common.iter_unsupported_objects`)** — surfaces SmartArt/chart
  text that cannot be filled, in `propose` (warning) and `validate` (informational).

Dependencies: `pip install python-docx python-pptx` (already used across the office
skills). PDF export additionally needs LibreOffice (or Save-As-PDF from the app).

## Why "assisted" (propose → confirm → build)
One example can't reveal what's boilerplate and what changes each time — "Acme Q3 2026"
could mean client=Acme, quarter=Q3, or both. So templatize is **two steps**: it
*proposes* a fixed/variable split for a human or agent to confirm, then *builds*. Do
not promise fully-automatic detection; the confirm step is where correctness comes from.

## Workflow
```
Progress:
- [ ] 0. See it: render the source page-by-page and inspect layout, structure & branding
- [ ] 1. Propose: extract candidate variable fields from the example file
- [ ] 2. Review: confirm WITH THE USER what to preserve vs. vary; mark keep/name/type
- [ ] 3. Build: inject placeholders and register the template + manifest
- [ ] 4. Fill: supply data keyed by the manifest fields -> finished document
- [ ] 5. Validate: no leftover tags, structure intact (required)
- [ ] 6. QA by vision: render the OUTPUT page-by-page, compare to source, fix drift
```

**Step 0 — See it (vision).** Before deciding anything, *look* at the document —
`render_pages.py` gives you one PNG per page/slide to Read:
```bash
python scripts/render_pages.py client_qbr.docx --out-dir pages/   # prints PNG paths
```
Inspect each page for the layout, section structure, table styles, logos, colours and
the header/footer — the visual identity is what "consistent" means and what the
template must preserve. python-docx/pptx show text, not layout; only the render does.

**Step 1 — Propose.**
```bash
python scripts/templatize.py propose --file client_qbr.docx --out proposal.json
```
Reads the file and writes every candidate value (deduped — the same client name in
five places becomes one field), with a heuristic name (from `Label: value` lines) and
a suggested keep/type.

**Step 2 — Review (the assisted step). Confirm the preserve list with the user.**
Before editing, ask what must be *preserved* (brand colours, logos, cover, header/
footer, mandatory clauses, table styles) and what *varies* each time — then use their
answer to set the split. Offer to swap logos/images per client (see image placeholders
below). Edit `proposal.json`; for each candidate set:
- `keep`: `variable` (filled each time), `fixed` (boilerplate that stays), or `remove`
  (drop this line — use for surplus example bullets/rows a `list` field regenerates).
- `suggest_name`: a clean `snake_case` field name.
- `suggest_type`: `text` (default) or `list` (a repeating bullet/row).

For a repeating list, mark **one** representative line `variable` + `list` and mark the
other example lines `remove`.

**Step 3 — Build.**
```bash
python scripts/templatize.py build --file client_qbr.docx --fields proposal.json \
    --client globex --doc-type quarterly-review \
    --owner you@co.com --created 2026-07-13
```
Injects placeholders (longest values first, so `Q3 2026` is tagged before a bare `Q3`),
removes the lines you marked, and writes `template.<fmt>` + `manifest.json` into the
gallery. Pass `--created` explicitly (scripts have no clock).

**Step 4 — Fill.** Discover what a template needs, then fill it:
```bash
python scripts/registry.py show --client globex --doc-type quarterly-review
python scripts/fill.py --client globex --doc-type quarterly-review \
    --data content.json --out out/initech-q4.docx [--export-pdf]
```
`content.json` is `{field_name: value}` (a `list` field takes a JSON array — it expands
into real bullets/rows, not one comma-joined line). The document *content* can come
from a writing skill (e.g. `writing-status-reports`); this engine renders it into the
locked format.

**Step 5 — Validate (required).**
```bash
# note: the registry slugifies the doc-type, so the folder is quarterly_review (underscore)
python scripts/validate.py out/initech-q4.docx --template registry/globex/quarterly_review/template.docx
```
Fails with specific messages on any leftover `{{ tag }}`, empty content, or changed
structure (section/slide count). **Do not ship anything that isn't `"status": "OK"`.**

**Step 6 — QA by vision (required for anything shipped to a client).** `validate.py`
reads text; it cannot see layout. Render the output and Read every page:
```bash
python scripts/render_pages.py out/initech-q4.docx --out-dir out/pages/
```
Compare page-by-page against the Step 0 source renders: is the **cover** updated (not
just the body — cover text is often a data-bound property, see below), do tables/
bullets fit, are logos and colours intact, did a long value overflow? A clean
`validate.py` **plus** a clean vision pass is the real ship gate. This pass is what
catches a stale cover that the text-only validator reports as `OK`.

## Format support
| Format | Templatize | How |
|---|---|---|
| **Word `.docx`** | Yes | Run-aware in-place injection; list fields expand paragraphs. **Also fills document properties** (`docProps/core.xml` + `customXml` CoverPageProperties) so **data-bound cover pages** update, not just the body. |
| **PowerPoint `.pptx`** | Yes | Same engine over slides, shapes, tables and speaker notes (cover text is usually a normal text run and is handled directly). |
| **Excel `.xlsx`** | Not yet | Needs a different cell + *data-region* model (rows that grow). Planned; out of scope for this suite. |
| **PDF** | As **output**, not a source | Fill a `.docx`/`.pptx` then `--export-pdf`. An arbitrary flat PDF has no reliable structure to templatize. Filling existing **AcroForm** PDFs is planned. |

## Principles
1. **Preserve + inject** — the client's file is the template; only text changes.
2. **Separate fixed from variable** — confirmed by a human, not guessed blindly.
3. **Obvious, single-convention placeholders** (`{{ field }}`) — never shipped filled wrong.
4. **A manifest travels with every template** — a future agent fills from it without re-reading the whole document.
5. **Governed** — one gallery, one owner, versioned, with a change log.

## Common mistakes
- **Rebuilding the layout by hand** instead of injecting into the client's own file — drift and wasted effort.
- **Trusting auto-detection** — always confirm the fixed/variable split.
- **Leaving surplus example bullets** when creating a `list` field (mark them `remove`).
- **Placeholders that look like real content** — users ship `{{ client_name }}` or, worse, a leftover real client name.
- **No owner/version** — the template forks and rots.
- **Shipping without `validate.py`** — the one gate that catches unfilled tags.

## Validation checklist
- [ ] Fixed vs. variable confirmed by a person, not just the heuristic.
- [ ] Placeholders use the one `{{ field }}` convention; none look like real content.
- [ ] `list` fields expand to real bullets/rows; surplus examples removed.
- [ ] Manifest has every field with type, example, and guidance.
- [ ] No leftover real client data from the source example.
- [ ] Owner, version, change log present; `validate.py` returns `OK`.

## Edge cases
- **Same value in many places** (client name) → one field fills all occurrences by design.
- **Overlapping values** (`Q3` inside `Q3 2026`) → build tags longest-first to avoid clobbering.
- **Value spans formatting runs** → build consolidates into the first run so the tag stays intact; build warns if a value matched 0 times (check it manually).
- **Legal/regulated templates** → keep mandatory clauses `fixed`; control who owns the gallery entry.
- **Multi-variant (regions/languages)** → separate `doc-type` entries under one client, not divergent private copies.

## Images & logos (per-client swap)
Pictures are swappable too — the same "preserve the frame, inject the content" idea
applied to images. `propose` lists every embedded picture as an **image slot** (one per
media part; a logo reused on 30 slides is one slot that swaps everywhere), named by a
size/aspect heuristic (`logo_*`, `background_*`, `image_*`). Mark the ones a client should
replace `keep: variable`; leave furniture `fixed`. `build` records each as an `image`
field with its `media_part`; `fill` re-encodes the supplied asset to the slot's original
format and swaps the media bytes in place, so **references and geometry (position/size/
crop) are preserved**. Provide a path in the fill data (`{"client_logo": "acme.png"}`);
omit it to keep the original.
- **The heuristic name is a guess** — verify which slot is which by the Step-0 render (or
  map a shape to its media part) before marking it variable; a wide logo can look like a
  "background". The Step-6 vision pass confirms the swapped image sits right (not
  stretched, adequate text contrast over a new background).
- A vision/image model can **generate** a missing asset to a slot's spec, then fill it in.
- Needs `pip install pillow`. See [references/engine-design.md](references/engine-design.md).

## Project-specific images & charts → placeholders (not baked in)
A reusable template must NOT carry the source project's figures. During the interactive
build, classify every embedded image:
- **Preserve** (branding/design): logos, cover artwork, brand bars, dividers.
- **Placeholder** (project-specific content): timeline/Gantt charts, milestone trackers,
  screenshots, result figures. Replace the media with a labelled placeholder and register
  an **optional image field** (`{{ figure }}` slot) — at fill time the user supplies a new
  image or leaves the placeholder, so the figure "can exist or not". Never ship the
  source's chart.
- Watch for **charts/tables embedded AS images** (e.g. a milestone tracker saved as a
  picture) — they look like real content but carry stale data the text residue check
  can't see. Confirm each with the user.
- **JPEG XR (`.wdp`) limitation:** a PNG placeholder can't be encoded into a `.wdp` part,
  so such a slot renders BLANK (effectively removed) rather than showing the placeholder
  box. Acceptable ("placeholder or removed"); a true placeholder needs format conversion.

## Now supported (previously limitations)
- **Variable-count table rows** — `row_group` fields expand a table's template row per
  data item (proven on Lessons Learned: one canonical template filled from differently-
  sized source files, rows growing to match). Word `.docx` only.
- **Reuse safety** — the source-residue check catches stale source content that a
  leftover-tag check alone misses.

## Known limitations (state these honestly; don't fake them)
- **SmartArt / diagram text and native charts are not fillable.** Content inside a
  SmartArt/diagram (`diagrams/data*.xml`) or chart (`charts/chart*.xml`) is invisible to
  python-docx/pptx, so the fill keeps the source's text. The engine now **detects and
  flags** these (`propose` warning, `validate` surface) — do not claim success on a page
  that depends on them. Workaround: rebuild those slides with normal shapes/tables so they
  become fillable, or accept them as static and say so.
- **PPTX row-groups not yet supported.** Table-row expansion is `.docx` only; repeating
  rows / team cards / timelines in decks are not auto-cloned (flag them).
- **Data-bound cover DATE fields can be unreachable.** A cover date rendered from a Word
  DATE field or a non-standard content control (not a docProps/CoverPageProperties leaf)
  is not in any text run or scanned property, so the fill can't update it and residue
  can't match it — the vision-QA pass must catch it. (Cover title/subtitle/PublishDate
  bound to docProps ARE handled.)
- **No text autofit.** Filling a fixed box with content *longer* than the original can
  overflow — keep replacements close to the original length; vision-QA catches it.
  (Shorter is always safe.)
- **Whole-paragraph fields lose inline emphasis.** A whole paragraph that had a bold
  phrase mid-sentence takes the paragraph's base run formatting when filled (size/font/
  colour preserved, mid-sentence bold not). Split into smaller fields if inline bold matters.

## Related skills
- [authoring-word-documents](../authoring-word-documents/SKILL.md), [building-powerpoint-decks](../building-powerpoint-decks/SKILL.md) — build the one-off the template is learned from.
- [producing-branded-documents](../producing-branded-documents/SKILL.md) — brand/logo rendering pipeline.
- [running-mail-merge](../running-mail-merge/SKILL.md), [automating-document-generation](../automating-document-generation/SKILL.md) — bulk fills from a data source.
- [processing-word-documents](../processing-word-documents/SKILL.md), [processing-powerpoint-files](../processing-powerpoint-files/SKILL.md) — extract content to feed a fill.
- Detection heuristics, placeholder rules, per-format notes: [references/engine-design.md](references/engine-design.md).

## Examples
**Input:** "A client sent this quarterly review deck — set it up so we produce the same
deck each quarter with new numbers."
**Output:** `templatize.py propose` on the deck → confirm client name, period, and
metrics as variable and the bullet list as a `list` field → `build` registers
`globex/board-deck` (template.pptx + manifest.json) → next quarter, `registry.py show`
reveals the fields, `fill.py` renders a new deck from `content.json`, `validate.py`
confirms no placeholder was missed. Same masters, fonts, and layout every time — only
the content changes. See [examples/README.md](examples/README.md) for the full run.

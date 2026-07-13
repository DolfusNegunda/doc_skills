---
name: authoring-brand-guidelines
description: Create or maintain a company or product brand style guide covering logo usage, color palette, typography, imagery, voice and tone, and do/don't examples. Use when writing a brand guide, brand book, style guide, visual identity document, or updating brand standards after a rebrand.
---

# Authoring Brand Guidelines

Write the **human-facing brand guide** — the document designers, marketers, and
vendors read to understand how the brand looks, sounds, and behaves. The output
is prose with rules, rationale, and do/don't examples, not a config file.

## Overview

A brand guide answers "how do we present ourselves?" for people. It sets out the
logo rules, the palette with exact values, the type system, imagery direction,
and the voice — each with enough context that someone new can make on-brand
decisions without asking. This skill provides the standard structure, a
fill-in-the-blanks template, and a completed example so the guide is authored
once and stays maintainable.

**This skill vs. `producing-branded-documents`.** They are siblings with
different audiences:

| | This skill | producing-branded-documents |
|---|---|---|
| Produces | A brand *guide* people read | Branded *deliverables* (Word/PDF) |
| Brand data lives in | Prose sections with rationale | `assets/brand/brand-spec.md`, a terse machine-readable spec that scripts render from |
| Changes when | The brand identity changes | A deliverable is needed or the spec is rebranded |

The guide and the machine spec MUST agree: the same hex colors, the same fonts,
the same logo sizing rules. Whenever you edit one, check the other (see the
consistency step in the workflow).

## When to use this skill

- Writing a new brand guide or brand book from scratch
- Updating an existing guide after a rebrand, logo refresh, or palette change
- Adding a missing section (e.g., voice and tone) to a partial guide
- Converting scattered brand rules (emails, slides, tribal knowledge) into one
  authoritative document

Do **not** use it to generate a client report or status document — that is
`producing-branded-documents`.

## Core principles

1. **Exact values, always.** Every color gets a hex code (plus RGB/CMYK if print
   matters); every font gets a name, weight, and size range. "Our blue" is not a
   rule; `#2E86AB` is.
2. **Rules come with rationale.** A one-line "why" beside each rule ("minimum
   clear space keeps the logo legible at small sizes") makes rules survive
   personnel changes and reduces exception requests.
3. **Show, don't only tell.** Pair every major rule with a do/don't example.
   Misuse examples (stretched logo, off-palette buttons) prevent more mistakes
   than correct examples alone.
4. **One source of truth per fact.** State each value exactly once in the guide;
   elsewhere, link to that section. Duplicated values drift.
5. **Guide and spec move together.** If the guide says headings are navy
   `#1F3A5F` Calibri, `producing-branded-documents/assets/brand/brand-spec.md`
   must say the same — and vice versa.

## Workflow

Copy this checklist and track progress:

```
Brand guide progress:
- [ ] 1. Gather inputs: logo files, existing colors/fonts, any prior brand rules
- [ ] 2. Confirm scope: which sections apply (see references/guide-structure.md)
- [ ] 3. Copy assets/brand-guide-template.md to the target location
- [ ] 4. Fill each section — exact values, rationale, do/don't pairs
- [ ] 5. Cross-check against producing-branded-documents/assets/brand/brand-spec.md
- [ ] 6. Review: no placeholder brackets left, every color has a hex, every rule has a why
```

**Step 1 — Gather.** Collect what exists: logo files and variants, hex values in
use (check the machine spec first — it may already be authoritative), fonts,
photography, and any informal rules. Ask the user for anything missing rather
than inventing brand facts.

**Step 2 — Scope.** Not every company needs every section. A B2B services firm
may skip packaging; a product company may need app-icon rules. Use
[references/guide-structure.md](references/guide-structure.md) to decide which
sections to include and what belongs in each.

**Step 3 — Template.** Start from
[assets/brand-guide-template.md](assets/brand-guide-template.md). Keep its
heading structure; delete sections that are out of scope rather than leaving
them empty.

**Step 4 — Fill.** Replace every `[bracketed placeholder]`. Write rules in
imperative voice ("Use the horizontal lockup on light backgrounds"), attach a
short rationale, and give at least one do/don't pair per major section. See
[examples/example-brand-guide.md](examples/example-brand-guide.md) for the
target density and tone.

**Step 5 — Consistency check.** Compare the guide's colors, fonts, and logo
rules against `producing-branded-documents/assets/brand/brand-spec.md`. If they
differ, resolve with the user which is correct, then update **both** files. If
the spec changes, remind the user to regenerate templates per that skill's
instructions.

**Step 6 — Review.** Search the draft for `[` to catch leftover placeholders.
Confirm every color has a hex code, every font a weight and size, and every
rule a rationale or example.

## Examples

- [examples/example-brand-guide.md](examples/example-brand-guide.md) — a short
  completed guide for a fictional consultancy, using the same palette and fonts
  as the starter machine spec so the two demonstrably agree.

Typical requests this skill handles:
- "Write us a brand guide — here's our logo and these three colors."
- "We changed our accent color to teal; update the brand guide." (Also update
  the machine spec — step 5.)
- "Add a voice and tone section to our existing style guide."

## Anti-patterns

- **Colors without codes.** Named colors ("our navy") with no hex value make
  the guide unenforceable and let the guide and spec silently diverge.
- **Rules without rationale.** Bare prohibitions get ignored or argued with; a
  one-line why makes them stick.
- **Updating the guide but not the spec** (or vice versa). Documents rendered
  by `producing-branded-documents` then contradict the published brand.
- **Encyclopedic first drafts.** A 60-page guide nobody reads is worse than 8
  focused pages. Start with the core sections; grow on demand.
- **Inventing brand facts.** If the user hasn't supplied a secondary palette or
  a tagline, ask — never fabricate values that will be treated as canonical.
- **Duplicating values across sections.** State the palette once; the buttons
  section links to it instead of restating hex codes that will drift.

## Related skills

- `producing-branded-documents` — renders Word/PDF deliverables from the
  machine-readable `assets/brand/brand-spec.md`. Keep that spec in lockstep
  with the guide this skill authors.
- `skill-builder` — conventions for skills in this repo, including frontmatter rules.

## Reference files

- [references/guide-structure.md](references/guide-structure.md) — the standard
  sections of a brand guide and what each contains; read when deciding scope or
  reviewing completeness.
- [assets/brand-guide-template.md](assets/brand-guide-template.md) —
  fill-in-the-blanks template; the starting point for every new guide.
- [examples/example-brand-guide.md](examples/example-brand-guide.md) — a
  completed example showing target length, tone, and do/don't style.

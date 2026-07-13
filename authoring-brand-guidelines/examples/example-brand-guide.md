# Harborline Consulting Brand Guidelines

**Version:** 1.0 · **Owner:** Marketing Operations · **Last updated:** 2026-07-08

> Example note: Harborline is a fictional consultancy. This guide deliberately
> uses the same colors and fonts as the starter machine spec in
> `producing-branded-documents/assets/brand/brand-spec.md`, so the two files
> demonstrate what "guide and spec in lockstep" looks like.

## 1. Brand foundation

- **Mission:** Harborline helps mid-market operators turn messy data into
  confident decisions.
- **Personality:** steady, not stiff · plainspoken, not blunt · expert, not
  showy.
- **Audience:** operations and finance leaders who are busy, skeptical of
  consulting jargon, and judge us by clarity.

## 2. Logo

### Variants
| Variant | File | Use when |
|---|---|---|
| Primary lockup (mark + wordmark) | `assets/logos/company.png` | Default on white/light backgrounds |
| Icon-only anchor mark | `logo-mark.svg` | Avatars, favicons, spaces under 24 px tall |
| Reversed (white) | `logo-reversed.svg` | Navy or photographic backgrounds |

### Rules
- **Clear space:** keep clear space equal to the anchor mark's height on all
  sides. *Why:* the mark's thin strokes blur when crowded.
- **Minimum size:** 24 px tall on screen; 10 mm in print. Below that, use the
  icon-only mark.
- **In documents:** header, top-left, 0.5 in tall, width scaling
  proportionally — matching the machine spec exactly so rendered deliverables
  and this guide never disagree.

### Never
- Stretch, squash, or rotate the logo.
- Recolor it — only the navy primary and the white reversed version exist.
- Add drop shadows, outlines, or gradients.
- Place the navy lockup on the accent blue (fails contrast).
- Set "Harborline" in another font next to the mark.

## 3. Color palette

### Primary
| Name | Hex | RGB | Role |
|---|---|---|---|
| Harbor Navy | `#1F3A5F` | 31, 58, 95 | Headings, logo, header/footer rules |
| Channel Blue | `#2E86AB` | 46, 134, 171 | Accents, links, table headers — emphasis only |

### Functional
| Name | Hex | Role |
|---|---|---|
| Body text | `#222222` | Default text |
| Muted | `#666666` | Captions, footers, secondary text |
| On track | `#2E7D32` | RAG status: green |
| At risk | `#F9A825` | RAG status: amber |
| Off track | `#C62828` | RAG status: red |

### Usage
- Navy dominates; Channel Blue should never exceed roughly 10% of a layout.
  *Why:* a mostly-navy page reads calm and senior; a mostly-blue page reads
  like a template demo.
- Tints: navy at 10% opacity is allowed for table row striping; no other tints.
- **Accessibility:** body text `#222222` on white passes WCAG AA. Never set
  body copy in Channel Blue — reserve it for short accents and links.

## 4. Typography

| Style | Typeface | Weight | Size | Notes |
|---|---|---|---|---|
| Title | Calibri | Bold | 22 pt | Sentence case |
| Section heading | Calibri | Bold | 13 pt | Sentence case, Harbor Navy |
| Body | Calibri | Regular | 10.5 pt | Left-aligned, single spacing |
| Caption | Calibri | Regular | 9 pt | Muted `#666666` |

- **Fallbacks:** Calibri → Arial → sans-serif.
- *Why Calibri:* installed on every company machine and identical to the
  document-rendering spec, so Word/PDF deliverables and marketing pages match.
- Bold is for headings and single key figures; italics only for publication
  titles. Never underline anything that is not a link.

## 5. Voice and tone

| Trait | This means | This doesn't mean |
|---|---|---|
| Plainspoken | Short sentences, concrete numbers, no filler | Curt or dismissive |
| Steady | Calm statements of risk with a recommended action | Burying bad news |
| Expert | Show the analysis, cite the data | Jargon or name-dropping frameworks |

**Tone by context:** proposals may warm up slightly; status reports stay
neutral and factual; anything legal or contractual drops contractions.

**Mechanics:** first person plural ("we"), contractions allowed outside legal
text, sentence-case headings, Oxford comma. Banned: "leverage" (as a verb),
"synergy", "best-in-class", "circle back".

**Before/after:**
- Before: "We will leverage best-in-class methodologies to drive synergies
  across your data estate."
- After: "We'll combine your billing and CRM data so your team stops
  reconciling them by hand."

## 6. Do / don't gallery

| Do | Don't |
|---|---|
| Navy headings on a white page, one Channel Blue accent rule under the title | Channel Blue headings and navy body text — inverts the hierarchy |
| Reversed white logo on a full-bleed navy cover | Navy logo on the navy cover ("it's subtle" is not a variant) |
| "Revenue rose 12% after the pricing change." | "We leveraged the pricing initiative to drive double-digit uplift." |
| RAG chips using the three functional colors only | Custom "orange-ish" status colors invented per report |

## 7. Assets and governance

- **Asset locations:** logos in `producing-branded-documents/assets/logos/`;
  document templates in `producing-branded-documents/assets/templates/`.
- **Machine spec:** `producing-branded-documents/assets/brand/brand-spec.md`
  carries these same values for automated document rendering. A change to any
  color, font, or logo rule updates both files in the same change, and
  templates are regenerated per that skill's instructions.
- **Requesting changes:** open a request with Marketing Operations; changes
  ship as a new version with a changelog entry.
- **Changelog:**
  - 2026-07-08 — 1.0 — initial version.

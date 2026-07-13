# Brand Guide Structure Reference

## Contents
- How to use this reference
- Core sections (almost every guide needs these)
  - Brand foundation
  - Logo
  - Color palette
  - Typography
  - Voice and tone
  - Do/don't gallery
- Extended sections (include when in scope)
  - Imagery and photography
  - Iconography and illustration
  - Layout and spacing
  - Digital applications
  - Print and packaging
  - Co-branding and partnerships
- Housekeeping sections
- Sizing the guide

## How to use this reference

Each entry below says what the section contains, what "done" looks like, and
common gaps. Include a section only when the brand actually has rules for it —
an empty or hand-wavy section erodes trust in the whole guide. When trimming,
keep all six core sections; cut from the extended list first.

## Core sections

### Brand foundation
One page: mission or purpose, brand personality (3–5 adjectives), and the
audience. This is the "why" that every later rule traces back to.
- **Done when:** a new hire could explain in one sentence what the brand stands
  for and who it speaks to.
- **Common gap:** vague personality words ("innovative", "quality") with no
  contrast — say what the brand is *not* as well ("confident, not boastful").

### Logo
The most-referenced section. Cover:
- **Variants:** primary lockup, horizontal/stacked, icon-only mark, and
  mono/reversed versions — with when each is allowed.
- **Clear space:** minimum padding around the logo, defined relative to the
  logo itself (e.g., "the height of the mark's x-height"), not in pixels.
- **Minimum size:** smallest reproduction size for print and screen.
- **Backgrounds:** which variant goes on light, dark, photographic, and
  colored backgrounds.
- **Misuse:** an explicit don't list — no stretching, recoloring, rotating,
  effects, or redrawing.
- **Files:** where approved logo files live and which format to use where
  (SVG for screens, PNG with transparency for documents, vector for print).
- **Done when:** every rule has a measurement or a named variant, and the
  misuse list has at least five concrete items.
- **Common gap:** no rule for the logo at very small sizes (favicons, avatars).

### Color palette
- **Primary palette:** each color with a name, hex, RGB, and (if print is in
  scope) CMYK/Pantone. State each color's role (headings, accents, backgrounds).
- **Secondary/functional palette:** success/warning/error or RAG colors, muted
  text, borders.
- **Usage ratios:** rough proportions (e.g., "primary navy dominates; accent
  blue is for emphasis only") prevent rainbow layouts.
- **Accessibility:** required contrast pairs (e.g., "body text `#222222` on
  white passes WCAG AA; never set body text in the accent color").
- **Done when:** every color that appears anywhere in brand output is listed
  with an exact value and a role.
- **Common gap:** tints/shades — state whether opacity steps of the primaries
  are allowed and which ones.

### Typography
- **Typefaces:** primary and fallback fonts, where each is licensed/available.
  Prefer fonts installed everywhere for internal documents (the machine spec in
  `producing-branded-documents` uses Calibri for exactly this reason).
- **Type scale:** sizes and weights for title, headings, body, captions.
- **Rules:** line length, alignment (usually left), casing conventions for
  headings, when bold/italic are permitted.
- **Done when:** someone could style a document correctly from the table alone.
- **Common gap:** no fallback stack for environments where the brand font is
  missing.

### Voice and tone
- **Voice:** the brand's constant personality in words — 3–5 traits, each with
  a one-line "this means / this doesn't mean".
- **Tone:** how voice flexes by context (marketing vs. support vs. legal).
- **Mechanics:** person ("we"/"you"), contractions, jargon policy, formatting
  conventions (Oxford comma, sentence-case headings), banned words/phrases.
- **Done when:** each trait has a rewritten before/after example sentence.
- **Common gap:** voice sections that describe values but never show a sentence.

### Do/don't gallery
A consolidated set of paired examples across logo, color, type, and copy. In a
markdown guide, describe each pair concretely ("Don't: logo recolored to the
accent blue on a navy background"). This section catches the mistakes the rules
above didn't anticipate.

## Extended sections

### Imagery and photography
Photography style (candid vs. staged, lighting, color grading), subject matter,
diversity and representation standards, stock-photo policy, and image treatment
(overlays, duotones). Include when the brand publishes visual content regularly.

### Iconography and illustration
Icon style (stroke weight, corner radius, filled vs. outline), grid size,
illustration palette and character, and the approved icon source. Include for
product or app brands.

### Layout and spacing
Grid systems, margin conventions, spacing scale, and rules for slides and
one-pagers. For rendered internal documents, defer to the templates in
`producing-branded-documents` rather than restating page geometry here — link,
don't duplicate.

### Digital applications
Website/app specifics: button styles, link colors, favicon/app icon, email
signature format, social media avatar and banner sizes. Include per channel the
company actually uses.

### Print and packaging
Paper stocks, Pantone equivalents, business card and letterhead layouts,
packaging dielines. Include only when print is a real output.

### Co-branding and partnerships
Logo lockups with partner brands, ordering, separators, relative sizing, and
whose guide wins on shared materials. Include once the company regularly
co-publishes.

## Housekeeping sections

Every guide should end with:
- **Version and ownership:** who owns the guide, how to request changes, and a
  short changelog.
- **Asset index:** where logo files, fonts, and templates live (paths or links).
- **Machine-spec pointer:** an explicit note that
  `producing-branded-documents/assets/brand/brand-spec.md` is the
  machine-readable counterpart and must be updated in the same change as any
  color, font, or logo rule here.

## Sizing the guide

- **Starter (small company, internal focus):** core six sections, ~6–10 pages.
- **Standard (external marketing):** core + imagery + digital, ~15–25 pages.
- **Full brand book:** everything above, usually split into chapters.

Start at the smallest size that covers real decisions people face; a guide
grows credibly, but an aspirational empty section never gets filled.

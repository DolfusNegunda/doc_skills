# Word Style Architecture

The minimum viable style set for any professional document, and the rule for each.

## Contents
- The standard style set
- Paragraph vs. character styles
- Multilevel numbering
- Style inheritance and "based on"
- Migration from a hand-formatted doc

## The standard style set

| Style | Use for | Key settings |
|---|---|---|
| Title | Document title only (once) | Large, distinct from H1 |
| Subtitle | Optional strapline under title | Lighter weight |
| Heading 1 | Top-level sections / chapters | Page-break-before for chapters |
| Heading 2 | Sub-sections | Keep-with-next on |
| Heading 3 | Minor headings | Keep-with-next on |
| Normal / Body Text | Default paragraphs | 1.15–1.5 line spacing, space after |
| List Bullet / List Number | Bulleted / numbered lists | Consistent indent, one marker style |
| Quote / Intense Quote | Block quotations, callouts | Indented, italic or shaded |
| Caption | Figure/table captions | Small, above tables / below figures |
| Header / Footer | Running heads, page numbers | |
| TOC 1–3 | Auto TOC entries | Do not edit manually |
| Code / Source | Monospace technical text | Non-proportional font, no spell-check |

## Paragraph vs. character styles
- **Paragraph styles** control the whole paragraph (headings, body, lists).
- **Character styles** format spans inside a paragraph (Emphasis, Strong, Code
  inline, Defined Term). Use character styles instead of raw bold/italic when the
  emphasis carries meaning you may later restyle.

## Multilevel numbering
For legal/technical docs, attach a *list style* to the heading styles so H1→"1",
H2→"1.1", H3→"1.1.1" renumber automatically. Never type clause numbers. Define the
numbering once at the list-style level, not per paragraph.

## Style inheritance and "based on"
Set Body Text as the base; base other styles on it so a font change cascades.
Keep the inheritance shallow (2–3 levels) to avoid surprise cascades.

## Migration from a hand-formatted doc
1. Select all → clear direct formatting is too aggressive; instead map region by region.
2. Apply Heading styles to every fake (bolded) heading first — this restores the outline.
3. Replace manual "Figure 1" text with caption fields.
4. Insert the TOC field last; update all fields.
5. Verify in the outline/navigation pane that the hierarchy is correct.

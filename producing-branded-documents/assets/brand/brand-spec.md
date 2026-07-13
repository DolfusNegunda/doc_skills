# Brand Spec (the invariant)

This is the single source of truth for how every branded deliverable looks. Edit
values here, then regenerate templates (`python scripts/make_template.py`) so all
future documents inherit the change. This is a starter spec — replace with your
company's real brand.

## Colors
| Role | Hex |
|---|---|
| Primary (headings, header/footer rule) | `#1F3A5F` (navy) |
| Accent (rules, table header) | `#2E86AB` (blue) |
| Body text | `#222222` |
| Muted (captions, footer) | `#666666` |
| RAG — Green / On track | `#2E7D32` |
| RAG — Amber / At risk | `#F9A825` |
| RAG — Red / Off track | `#C62828` |

## Typography
- Body: **Calibri** 10.5pt
- Headings: **Calibri** bold, 13pt (section), 22pt (title)
- Use only fonts installed on all machines (Calibri/Arial are safe). Avoid
  fonts that render differently across systems.

## Logo rules
- Position: **header, top-left**, in a fixed frame.
- Height: **0.5 in** (width scales proportionally). Do not stretch.
- Client logos live in `assets/logos/clients/<client-key>.png`.
- Fallback: `assets/logos/company.png` when no client logo exists.
- Provide logos as PNG with transparent background, ≥ 300px tall for crispness.

## Page
- Margins: top/bottom 0.8 in, left/right 0.9 in.
- Footer: centered "Confidential — <company>  |  Page N".
- Header right: "CONFIDENTIAL" + client name.

## Naming key for client logos
Client key = client name, lowercased, spaces → hyphens.
Example: "Globex Corporation" → `globex-corporation.png` (or set `client_key`
explicitly in the data to `globex` and name the file `globex.png`).

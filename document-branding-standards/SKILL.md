---
name: document-branding-standards
description: Define and apply a company's document branding profile (logo, header/footer, base template) so standardized process documents can be generated for any organization without hardcoding one company's branding. Use this as the shared foundation before building or using any document-type skill (lessons learned, change notes, signoffs, presentations), and use its onboarding procedure when adding support for a new organization.
---

# Document Branding Standards

Shared foundation for generating standardized process documents (Lessons
Learned, Change Notes, Signoffs, Presentations, etc.) for **any**
organization. This skill defines the *branding profile* concept that keeps
company-specific identity completely separate from the document-generation
engine, so a document-type skill built once can be deployed at any company
by swapping in that company's own profile — no code changes required.

This skill is deliberately organization-agnostic. If you're looking for a
concrete worked example of a filled-in profile, see
[examples/bsc-profile/](examples/bsc-profile/PROFILE.md).

## When to use this skill
- Building a new document-type skill (read this first — it defines the
  contract every document-type skill relies on)
- Onboarding a new organization/deployment: turning that org's existing
  branded documents into a reusable branding profile
- Reviewing whether a generated document correctly picked up an org's
  branding

## Core principles
1. **Branding is data, not code.** A company's logo, name, footer/legal
   text, and base template are supplied as a *profile* (a folder of
   assets + a small config), never hardcoded into a document-type skill's
   script. The same generation script must work unmodified for every
   organization's profile.
2. **Prefer the organization's own real document as the base template.**
   Don't invent a company's branding from scratch when they already have
   branded Word documents. Copying a real prior document and editing it
   programmatically is the only reliable way to preserve embedded fonts,
   theme colors, header/footer XML, and Word content controls — hand-built
   templates lose fidelity. Use the **generic neutral template** (shipped
   with each document-type skill) only when an organization has no
   existing branded document to start from.
3. **Locate content by standardized heading text, never by position.**
   Different organizations' templates will have different table shapes,
   heading styles, and section ordering. Generation scripts must find each
   repeating-list section by searching for its standard heading text (see
   [references/docx-editing-patterns.md](references/docx-editing-patterns.md)),
   not by assuming "table 3 is always Positives." This is what allows one
   script to work against arbitrarily different real-world templates.
4. **Single-value fields are `{{TOKEN}}` placeholders, replaced generically.**
   Project name, org name, dates, etc. are plain `{{PLACEHOLDER}}` tokens
   in the base template, replaced by a generic find/replace pass that
   checks paragraphs, table cells, headers/footers, AND Word content
   controls — never a hardcoded reference to one specific paragraph.

## What a "branding profile" consists of
| Element | Required? | Notes |
|---|---|---|
| Organization name | Yes | Plain text, used in `{{ORG_NAME}}` token replacement |
| Base template `.docx` | Yes | Either the org's own real branded document (preferred) or the shared generic neutral template (fallback) |
| Logo image | Recommended | Swapped into the base template's first header image slot (`word/media/image1.*`) — see [references/logo-swap-procedure.md](references/logo-swap-procedure.md) |
| Footer/legal text | Optional | Only needed if building a NEW base template from scratch for an org with none; otherwise it's already baked into their supplied template |
| Color palette / fonts | Optional | Only relevant if building a new template from scratch; irrelevant when reusing a real org document as the base |

A profile is stored as a small folder: `profiles/{org-slug}/` containing
`logo.*` and (if not using the shared generic template) `base-template.docx`.
See [examples/bsc-profile/](examples/bsc-profile/PROFILE.md) for a complete,
filled-in profile built from BSC's real documents.

## Onboarding a new organization
Follow this procedure whenever a document-type skill needs to be deployed
for a company that hasn't used it before:
```
Org onboarding progress:
- [ ] 1. Ask whether the org has an existing branded Word document to reuse
- [ ] 2. If yes: extract its logo, confirm section headings match the standard skeleton
- [ ] 3. If no: use the shared generic neutral template as the base, ask for a logo image only
- [ ] 4. Confirm/insert {{TOKEN}} placeholders for singular fields if missing
- [ ] 5. Save the profile (logo + base template) under profiles/{org-slug}/
- [ ] 6. Run the document-type skill's generation script against a small test data set
- [ ] 7. Validate the output (see validation checklist in docx-editing-patterns.md)
```
Full step-by-step detail: [references/org-onboarding-checklist.md](references/org-onboarding-checklist.md).

## Reference files
- [references/docx-editing-patterns.md](references/docx-editing-patterns.md)
  — Organization-agnostic python-docx/OOXML patterns: generic `{{TOKEN}}`
  replacement (including Word content controls), heading-based table
  lookup, multi-paragraph cell clearing, row cloning, and table-skeleton
  swapping.
- [references/logo-swap-procedure.md](references/logo-swap-procedure.md) —
  Exact steps and code for replacing an organization's logo image inside
  any `.docx` package.
- [references/org-onboarding-checklist.md](references/org-onboarding-checklist.md)
  — Step-by-step procedure for turning a new organization's real documents
  (or lack thereof) into a usable branding profile.
- [examples/bsc-profile/PROFILE.md](examples/bsc-profile/PROFILE.md) — A
  complete worked example profile (Business Science Corporation), showing
  what a filled-in profile looks like end to end.

---
name: presenting-with-html
description: Build generic, good-looking HTML presentations and reusable, composable HTML boilerplate for slide decks and web-based decks. Use when the user asks for an HTML slide deck, a self-contained web presentation, reveal.js/impress-style slides, or a reusable HTML deck template/boilerplate to fill with content.
---

# Presenting with HTML

## Status: PLACEHOLDER (stub)

This skill is intentionally a stub. The real procedure will be formalised from a
context the user will supply (an existing HTML-presentation approach / boilerplate they
want captured as a repeatable skill). Do **not** invent the implementation — wait for
that context, then author this skill with the house style in
[../skill-builder/SKILL.md](../skill-builder/SKILL.md).

## Scope (intended)
- Produce clean, on-brand **HTML presentations** (self-contained decks that open in a
  browser) from content or an outline.
- Provide **composable boilerplate**: reusable slide/section building blocks that
  assemble into a deck, so structure and styling regenerate consistently.
- Sit alongside the other suite skills as the HTML counterpart to
  [../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md).

## To formalise this skill (when the context arrives)
1. Capture the boilerplate (layout system, base CSS, slide components) into `assets/`.
2. Write the workflow: outline → assemble components → fill content → preview/QA.
3. Add a validator/preview step if one fits (e.g. render + vision-check the deck).
4. Fill in scope, principles, common mistakes, and a validation checklist.

## Related skills
- [../building-powerpoint-decks/SKILL.md](../building-powerpoint-decks/SKILL.md) — the PowerPoint counterpart.
- [../crafting-presentation-narratives/SKILL.md](../crafting-presentation-narratives/SKILL.md) — the story before the slides.

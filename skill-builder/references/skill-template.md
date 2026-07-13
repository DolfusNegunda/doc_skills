# Skill Template

Copy the block below into a new `skill-name/SKILL.md` and delete every section
you don't need. A skill with only Overview + When to Use + Process is often
enough. Sections are ordered simple → complex; keep the body under ~500 lines and
move anything long into `references/`.

````markdown
---
name: skill-name-here
description: What this skill does and when to use it, in third person, with trigger terms.
---

# [Skill Name]

## Overview
2-3 sentences: what this skill helps accomplish and the value it adds.

## When to use this skill
- [Specific trigger condition or request phrasing]
- [Another trigger]
- [Another trigger]

## Core principles
1. **[Principle]**: [one-line explanation]
2. **[Principle]**: [one-line explanation]
3. **[Principle]**: [one-line explanation]

## Process
For complex or fragile work, give a checklist Claude can copy and track:

```
Progress:
- [ ] Step 1: ...
- [ ] Step 2: ...
- [ ] Step 3: ...
```

**Step 1 — [Name].** [What to do. Concrete action.]

**Step 2 — [Name].** [What to do.]

**Step 3 — [Name].** [What to do, plus how to verify it worked.]

## Examples
Show input → output pairs when output quality depends on seeing examples.

**Input:** [example input]
**Output:**
```
[example output]
```

## Anti-patterns
- **[Mistake]** — [why it's wrong]. Instead: [correct approach].

## Reference files
- [references/guide.md](references/guide.md) — [what it covers]
- [scripts/validate.py] — Run to [purpose]: `python scripts/validate.py <args>`
````

## Choosing the level of detail

- **High freedom** (prose steps): many valid approaches; context decides. E.g.
  "Analyze the code structure, check for edge cases, suggest improvements."
- **Medium freedom** (parameterized pattern/pseudocode): a preferred pattern
  with some variation allowed.
- **Low freedom** (exact command): fragile, must-be-exact, order matters. E.g.
  "Run exactly: `python scripts/migrate.py --verify --backup`. Do not add flags."

## Feedback-loop pattern

For quality-critical output, build a validate → fix → repeat loop:

```
1. Produce the artifact
2. Validate it (run a script, or check against a reference)
3. If it fails: read the error, fix, re-validate
4. Only proceed when validation passes
```

**If the skill produces or ingests a real file** (`.docx`/`.xlsx`/`.pptx`/`.pdf`/
`.csv`), this loop must be backed by a bundled, tested script — a `validate_*.py`
for producers (fails non-zero on the format's real failure modes) or an
`extract_*.py` for processors (deterministic read + fidelity self-check). A tested
tool a weak model runs beats prose it must interpret. See the "Determinism" section
of [authoring-checklist.md](authoring-checklist.md); working examples:
`office/engineering-excel-workbooks/scripts/validate_workbook.py` and
`office/processing-excel-files/scripts/extract_workbook.py`.

## Progressive disclosure reminders

- Link reference files **one level deep** from `SKILL.md` — reference files
  should not link onward to yet more files (Claude may only partially read them).
- For any reference file over ~100 lines, put a "Contents" list at the top.
- Say whether Claude should **execute** a script ("Run `x.py`") or **read** it
  ("See `x.py` for the algorithm").
- Use forward slashes in all paths, even on Windows (`references/guide.md`).

---
name: skill-builder
description: Create well-structured, portable Agent Skills (SKILL.md files) and organize a shared skills repository. Use when the user wants to author a new skill, write or fix a SKILL.md, correct YAML frontmatter, structure references and supporting files, or asks "create a skill for X".
---

# Skill Builder

Author new skills that Claude can discover and use reliably, following the
[Agent Skills](https://agentskills.io) open standard. This skill is the
starting point and house style for our internal skills repository.

## Core principles

1. **The description is the product.** It is the only part loaded until a skill
   triggers. It must state *what* the skill does **and** *when* to use it, in
   third person. Weak descriptions are the #1 reason a good skill never fires.
2. **Be concise.** Claude is already smart. Only add what Claude doesn't already
   know. Every line in `SKILL.md` competes for context once loaded.
3. **Progressive disclosure.** Keep `SKILL.md` under ~500 lines. Push long
   material (full templates, deep references, examples) into separate files and
   link them one level deep.
4. **Match freedom to fragility.** Give step-by-step commands for fragile,
   must-be-exact operations; give general direction where many paths work.
5. **Portable first.** `name` and `description` work everywhere. Everything else
   is a runtime extension — see [references/frontmatter.md](references/frontmatter.md).

## When to build a skill

Build one when you keep pasting the same procedure, checklist, or domain context
into chat, or when a piece of team knowledge should be reusable across people and
sessions. Don't build one for a one-off task or for a single fact.

## Workflow

Copy this checklist and track progress:

```
Skill build progress:
- [ ] 1. Scope: one sentence on what problem it solves and its boundaries
- [ ] 2. Name it (lowercase-hyphens, gerund preferred, no "claude"/"anthropic")
- [ ] 3. Write the description (what + when + trigger terms, third person)
- [ ] 4. Draft the body from references/skill-template.md, kept lean
- [ ] 5. Split long content into references/ (one level deep)
- [ ] 6. Validate against references/authoring-checklist.md
- [ ] 7. Test: does it trigger on real requests and produce the right output?
```

**Step 1 — Scope.** Write one sentence: what this solves and what's in/out of
scope. If you can't, the skill is too broad — split it.

**Step 2 — Name.** Directory name = skill name. Lowercase letters, numbers,
hyphens only; max 64 chars. Prefer gerund form (`processing-invoices`,
`authoring-dbt-models`). Never include the words `claude` or `anthropic`.

**Step 3 — Description.** This drives discovery. Follow the recipe and examples
in [references/frontmatter.md](references/frontmatter.md). Test: reading only the
description, would Claude know both *what it does* and *when to reach for it*?

**Step 4 — Draft the body.** Start from
[references/skill-template.md](references/skill-template.md). Delete every section
you don't need. State what to do, not background theory.

**Step 5 — Split.** When a section gets long (templates, schemas, extended
examples), move it to `references/NAME.md` and link it from `SKILL.md`. Keep all
links **one level deep** — reference files should not chain into other files.
Use `scripts/` for code Claude executes, `assets/` for files it outputs.

**Step 6 — Validate.** Run the automated gate, then the human checklist. Execute
`python skill-builder/scripts/validate_skills.py` from the repo root: it checks
frontmatter, naming, description quality, trailing newlines, broken cross-links,
and duplicate names across every skill, and exits non-zero on any error. Then run
through [references/authoring-checklist.md](references/authoring-checklist.md) for
the judgment items the script can't check, and avoid the traps in
[references/anti-patterns.md](references/anti-patterns.md).

**Step 7 — Test.** Give a fresh Claude a realistic request. Confirm the skill
triggers, finds the right reference files, and produces correct output. Refine
the description first if it fails to trigger.

## Skill anatomy

```text
skill-name/
├── SKILL.md            # Required. Frontmatter + lean instructions.
├── references/         # Optional. Docs Claude reads on demand.
│   └── guide.md
├── scripts/            # Optional. Code Claude executes (not read into context).
│   └── validate.py
└── assets/             # Optional. Templates/files the skill outputs.
```

Only `SKILL.md` is required. Reference files cost zero context tokens until read,
so bundle generously — but only link what earns its place.

## Frontmatter (the short version)

```yaml
---
name: skill-name
description: What it does and when to use it, in third person, with trigger terms.
---
```

`name` + `description` are the only required, universally portable fields. Do not
quote simple strings, use 2-space indentation, and end the file with a single
newline. For optional fields (`allowed-tools`, `metadata`, `license`,
`disable-model-invocation`, etc.), which environments honor them, and the exact
character limits, see [references/frontmatter.md](references/frontmatter.md).

## Reference files

- [references/frontmatter.md](references/frontmatter.md) — Full frontmatter rules,
  the description recipe, portable vs. runtime-specific fields, and validation.
- [references/skill-template.md](references/skill-template.md) — Copy-paste
  starting template with every optional section explained.
- [references/authoring-checklist.md](references/authoring-checklist.md) —
  Pre-publish quality gate (human judgment items).
- [scripts/validate_skills.py] — Run to enforce the mechanical gate (frontmatter,
  naming, links, duplicates): `python skill-builder/scripts/validate_skills.py`.
- [references/anti-patterns.md](references/anti-patterns.md) — Common mistakes
  and what to do instead.
- [examples/authoring-dbt-models/SKILL.md](examples/authoring-dbt-models/SKILL.md)
  — A complete, data-engineering worked example built with this skill.

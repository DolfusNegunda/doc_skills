# YAML Frontmatter Reference

## Contents
- The two required fields
- Writing the description (the highest-leverage field)
- Naming rules
- Optional fields: portable vs. runtime-specific
- YAML formatting rules
- Validation checklist

## The two required fields

Every `SKILL.md` needs exactly these, between `---` markers at the very top:

```yaml
---
name: skill-name
description: What the skill does and when to use it, in third person.
---
```

| Field         | Required | Rules |
| ------------- | -------- | ----- |
| `name`        | Yes      | Max 64 chars. Lowercase letters, numbers, hyphens only. No XML tags. Cannot contain the reserved words `claude` or `anthropic`. |
| `description` | Yes      | Non-empty, max 1024 chars. No XML tags. Must describe *what* it does and *when* to use it. |

These two fields are portable — they work identically in Claude Code, the Claude
API, and claude.ai. Prefer them alone unless you have a concrete reason to add more.

## Writing the description (the highest-leverage field)

At startup Claude sees **only** the name and description of every skill. It picks
which skill to load from the description alone. A vague description means a good
skill never fires.

**Recipe:** `<what it does>` + `. Use when <triggers/contexts/keywords>.` in
**third person**.

Good:
```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```
```yaml
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

Avoid:
```yaml
description: Helps with documents          # vague — no triggers, no specifics
description: I can help you process PDFs    # first person — hurts discovery
description: You can use this for reports    # second person — hurts discovery
```

Test: reading only the description, would Claude know both what it does and when
to reach for it? Include the concrete terms a user would actually say.

## Naming rules

- Directory name = skill name = what the user types (`/skill-name`).
- Lowercase letters, numbers, hyphens; max 64 chars.
- Prefer **gerund form**: `processing-pdfs`, `authoring-dbt-models`,
  `reviewing-migrations`. Noun phrases (`pdf-processing`) are acceptable.
- Avoid vague names (`helper`, `utils`, `tools`) and the reserved words
  `claude` / `anthropic`.

## Optional fields: portable vs. runtime-specific

The two required fields are all you need for a portable skill. The fields below
are **runtime-specific** — an environment silently ignores fields it doesn't
recognize, so a field that helps in Claude Code may do nothing on claude.ai.

### Claude Code extensions
Honored when the skill runs in Claude Code (see the frontmatter reference at
https://code.claude.com/docs/en/skills):

| Field | Purpose |
| ----- | ------- |
| `allowed-tools` | Pre-approves the listed tools so Claude uses them without a permission prompt while the skill is active. Space/comma-separated string or YAML list. Does **not** restrict other tools. |
| `disallowed-tools` | Removes tools from the pool while the skill is active. |
| `disable-model-invocation` | `true` = only a human can invoke it (`/name`); Claude won't auto-trigger it. Use for actions with side effects (deploy, commit). |
| `user-invocable` | `false` = hide from the menu; only Claude invokes it. Use for background knowledge. |
| `model`, `effort`, `context: fork`, `argument-hint`, `arguments` | Advanced execution controls. |

> Note on `allowed-tools`: some older guidance (written for the **claude.ai skill
> upload** flow, where SKILL.md is placed under `/mnt/skills/...`) states that
> `allowed-tools` is unsupported. That is correct **for that upload environment
> only** — the claude.ai/API validator accepts just `name` and `description`.
> Claude Code fully supports `allowed-tools`. Know your target runtime.

### Broadly-tolerated optional fields
- `license` — e.g. `MIT`, `Apache-2.0`, `Proprietary`.
- `metadata` — an object for arbitrary extra fields (author, version, tags).
  Everything non-standard goes **inside** `metadata`, correctly indented:

```yaml
---
name: skill-name
description: What it does and when to use it.
license: Proprietary
metadata:
  author: Data Engineering Team
  version: 1.0
  tags:
    - data
    - internal
---
```

Note the indentation: keys under `metadata:` are indented 2 spaces; list items
under `tags:` are indented a further 2 spaces. Do **not** put `author`,
`version`, or `tags` at the top level — nest them under `metadata`.

## YAML formatting rules

1. Frontmatter opens with `---` on line 1 and closes with `---`.
2. Use 2-space indentation. Never tabs.
3. Don't quote simple strings. Quote a value only if it contains YAML-special
   characters at the start or that break parsing (`:` followed by space, leading
   `[ { > | @ &  * # ? ! %` etc.).
4. Field order convention: `name` → `description` → `license` → `metadata`.
5. No trailing whitespace. End the file with a single newline.

## Validation checklist

- [ ] Starts with `---` and the block is closed with `---`
- [ ] Has non-empty `name` and `description`
- [ ] `name`: lowercase/numbers/hyphens, ≤64 chars, no `claude`/`anthropic`
- [ ] `description`: ≤1024 chars, third person, states what **and** when
- [ ] Any extra fields are either known runtime fields or nested under `metadata`
- [ ] 2-space indentation, no tabs, no trailing whitespace
- [ ] File ends with a single newline

If a runtime reports malformed frontmatter, strip to `name` + `description` only,
confirm it loads, then re-add optional fields one at a time.

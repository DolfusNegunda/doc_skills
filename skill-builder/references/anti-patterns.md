# Anti-Patterns

Common skill-authoring mistakes and what to do instead.

## Discovery

**Vague description.** `description: Helps with data` gives Claude nothing to
match on. → State what it does and the specific triggers: `Validate and
document dbt models. Use when adding or editing dbt models, or reviewing model
tests.`

**First/second person description.** "I can help you..." / "You can use this..."
hurts discovery because the description is injected into the system prompt. →
Write in third person.

**Kitchen-sink skill.** One skill that "does all data engineering" won't trigger
reliably and can't be described crisply. → One skill, one job. Split it.

## Frontmatter

**Top-level `author` / `version` / `tags`.** These aren't standard fields. →
Nest them under `metadata:` with 2-space indentation.

**Assuming a field is universal.** `allowed-tools` works in Claude Code but is
ignored by the claude.ai upload validator; `metadata` is tolerated broadly but
read by few runtimes. → Know your target runtime; keep portable skills to
`name` + `description`.

**Tabs or ragged indentation.** Breaks YAML parsing. → 2 spaces per level, always.

## Content

**Explaining what Claude already knows.** Paragraphs defining what a PDF, JSON,
or SQL JOIN is waste context. → Assume Claude is smart; add only what it lacks
(your conventions, your schema, your rules).

**A 500-line monolith.** Everything crammed into `SKILL.md` bloats context every
time it loads. → Progressive disclosure: lean `SKILL.md`, details in `references/`.

**Offering too many options.** "Use pandas, or polars, or pyspark, or duckdb..."
paralyzes. → Give one default with an escape hatch: "Use polars. For datasets
over memory, use duckdb instead."

**Time-sensitive instructions.** "Before August 2025 use the old API..." goes
stale. → Document the current way; move deprecated info to an "Old patterns"
section.

**Inconsistent terminology.** Mixing "field / column / attribute" for one concept
confuses Claude. → Pick one term and use it throughout.

## Structure

**Deeply nested references.** `SKILL.md` → `a.md` → `b.md` → `c.md`. Claude may
only partially read chained files. → Keep every reference one level deep from
`SKILL.md`.

**Windows-style paths.** `references\guide.md` breaks on non-Windows runtimes. →
Always forward slashes: `references/guide.md`.

**Ambiguous script intent.** Not saying whether Claude should run or read a
script. → Be explicit: "Run `validate.py`" vs. "See `validate.py` for the logic."

**Assuming packages are installed.** "Use the requests library" when it may not
be present. → List required packages and installation, or bundle a script.

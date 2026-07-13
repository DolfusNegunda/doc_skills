# Authoring Checklist

Run through this before publishing a skill to the repo.

## Discovery (does it trigger?)
- [ ] `description` states both **what** the skill does and **when** to use it
- [ ] `description` is third person (not "I can..." / "You can...")
- [ ] `description` includes the concrete terms a user would actually say
- [ ] `name` is lowercase-hyphens, ≤64 chars, gerund/noun-phrase, no `claude`/`anthropic`

## Frontmatter (does it parse?)
- [ ] Opens and closes with `---`
- [ ] Only `name` + `description` unless a specific optional field is needed
- [ ] Extra fields nested under `metadata` (not top-level author/version/tags)
- [ ] 2-space indentation, no tabs, no trailing whitespace, ends with one newline
- [ ] Confirmed against [frontmatter.md](frontmatter.md) rules

## Content (is it lean and clear?)
- [ ] `SKILL.md` body under ~500 lines
- [ ] No content Claude already knows (no explaining what a PDF/JSON/SQL is)
- [ ] Consistent terminology throughout (pick one term per concept)
- [ ] Concrete examples, not abstract descriptions
- [ ] No time-sensitive info (or isolated in an "old patterns" section)
- [ ] Freedom level matches task fragility (exact commands where it's fragile)

## Structure (is it navigable?)
- [ ] Long material split into `references/`, linked from `SKILL.md`
- [ ] All reference links are **one level deep** (no chains of references)
- [ ] Reference files >100 lines start with a "Contents" list
- [ ] Forward slashes in every path (`references/x.md`, not `references\x.md`)
- [ ] Scripts marked as **execute** vs. **read**; required packages listed

## Determinism (does it ship a tool where prose isn't enough?)
- [ ] If the skill **produces** a file (`.docx`/`.xlsx`/`.pptx`/`.pdf`/`.csv`), it
      bundles a `scripts/validate_*.py` that checks the real failure modes, emits a
      machine-readable report, and exits non-zero on error
- [ ] If the skill **ingests/processes** a file, it bundles a `scripts/extract_*.py`
      that reads it deterministically and reports fidelity (what it could not read)
- [ ] The `## Workflow` wires the **produce → validate → fix → re-validate loop**
      (for producers) or **ingest → fidelity self-check** (for processors) — not a
      one-time "run the linter" step
- [ ] Every bundled script was actually run and tested, not just written
- [ ] Rationale: a cheap model runs a tested tool more reliably than it interprets
      prose — determinism is the whole point of the library

## Content correctness (is it actually right?)
- [ ] Every load-bearing claim — formulas, algorithm steps, framework definitions —
      checked against a primary source (a wrong formula a cheap model follows is a Blocker)
- [ ] Named frameworks match their real definition (RICE is a *product* not a sum; CRAAP
      has 5 elements; MERGE needs one row per key) — and the frontmatter names only methods
      the body actually teaches (the validator flags the common cases)
- [ ] Worked-example arithmetic reproduces (ROI/NPV figures actually compute)
- [ ] Contested pop-wisdom is framed as one option, not stated as settled fact
- [ ] "Always/never" absolutes are true absolutes, not overstated defaults
- [ ] See [../../docs/correctness-audit-process.md](../../docs/correctness-audit-process.md)
      for the periodic library-wide claim-audit

## Testing (does it work?)
- [ ] Tested on a realistic request with a fresh Claude — it triggered
- [ ] It found and used the right reference files
- [ ] Output was correct; fragile steps had a validation/feedback loop
- [ ] If it didn't trigger, the description was tightened first

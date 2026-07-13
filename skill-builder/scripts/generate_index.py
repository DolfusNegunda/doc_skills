#!/usr/bin/env python3
"""Regenerate skills-index.md — a complete flat index of every skill.

Run from the repo root:  python skill-builder/scripts/generate_index.py
Reads name + description from each SKILL.md, groups by top-level category, and
writes skills-index.md. Keeps the flat "read this first" index in sync with the
library so it never drifts. Re-run whenever a skill is added, moved, or renamed.
"""
import os, re

REPO = os.path.abspath(".")
IGNORE = {".git", "skills_repo-starter", "node_modules"}
CATS = {
    "skill-builder": "Meta",
    "office": "Office",
    "review": "Review",
    "business": "Business",
    "research": "Research",
    "software-engineering": "Software Engineering",
    "data-engineering": "Data Engineering",
    "ai-engineering": "AI Engineering",
    "reasoning": "Reasoning & Decision-Making",
    "productivity": "Productivity",
}


def when_to_use(desc):
    """Extract a concise 'when to use' phrase, breaking only on real sentence
    boundaries (a .!? followed by whitespace/end) so 'SKILL.md' / '.docx' don't
    truncate it."""
    end = r".*?[.!?](?=\s|$)"
    m = (re.search(r"Use (?:this |it )?when" + end, desc, re.I)
         or re.search(r"Use " + end, desc, re.I)
         or re.search(end, desc))
    phrase = (m.group(0) if m else desc).strip()
    phrase = re.sub(r"\s+", " ", phrase)
    return phrase if len(phrase) <= 240 else phrase[:237] + "..."


skills = []
for dp, dns, fns in os.walk(REPO):
    if set(os.path.relpath(dp, REPO).replace("\\", "/").split("/")) & IGNORE:
        continue
    dns[:] = [d for d in dns if d not in IGNORE]
    if "SKILL.md" in fns:
        rel = os.path.relpath(os.path.join(dp, "SKILL.md"), REPO).replace("\\", "/")
        # skip example skills nested inside another skill's examples/
        if "/examples/" in rel:
            continue
        raw = open(os.path.join(dp, "SKILL.md"), encoding="utf-8").read()
        fm = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
        if not fm:
            continue
        name = re.search(r"^name:\s*(.+)$", fm.group(1), re.M)
        desc = re.search(r"^description:\s*(.+)$", fm.group(1), re.M)
        if not (name and desc):
            continue
        cat = CATS.get(rel.split("/")[0], "Other")
        skills.append((cat, name.group(1).strip(), when_to_use(desc.group(1).strip()), rel))

order = ["Meta", "Office", "Review", "Business", "Research", "Software Engineering",
         "Data Engineering", "AI Engineering", "Reasoning & Decision-Making",
         "Productivity", "Other"]
lines = [
    "# Skills Index",
    "",
    "Read this first. It maps every skill in this repo. Open a skill's `SKILL.md`",
    "(and its `references/`) only when the current task needs it — never load every",
    "skill's body up front.",
    "",
    "Regenerate after adding, moving, or renaming a skill:",
    "`python skill-builder/scripts/generate_index.py`",
    "",
    f"**{len(skills)} skills** across {len([c for c in order if any(s[0]==c for s in skills)])} groups.",
    "",
]
for cat in order:
    rows = sorted([s for s in skills if s[0] == cat], key=lambda s: s[1])
    if not rows:
        continue
    lines += [f"## {cat}", "", "| Skill | When to use | Path |", "|---|---|---|"]
    for _, name, wtu, path in rows:
        wtu = wtu.replace("|", "\\|")
        lines.append(f"| {name} | {wtu} | [{path}]({path}) |")
    lines.append("")

open(os.path.join(REPO, "skills-index.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines).rstrip() + "\n")
print(f"Wrote skills-index.md with {len(skills)} skills.")

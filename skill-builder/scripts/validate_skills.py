#!/usr/bin/env python3
"""Validate Agent Skills for discovery + consistency.

Run from the repo root:  python skill-builder/scripts/validate_skills.py [path]//
(path defaults to ".", the whole repo).

For every folder containing a SKILL.md it checks:
  - frontmatter parses (--- delimited) and has name + description
  - name == folder name, kebab-case, <=64 chars, no "claude"/"anthropic"
  - description length in [20, 1024]; third person; includes a "when to use" cue
  - no tabs in frontmatter; file ends with exactly one trailing newline
  - every relative markdown link resolves to an existing file
  - no duplicate skill names across the repo

Exits non-zero if any ERROR is found; WARNINGS are advisory and do not fail.
This is the automated half of skill-builder Step 6 (Validate). It is language-
and runtime-agnostic and reads only name+description-relevant structure, so it
stays valid as the catalog grows.
"""
import os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
IGNORE = {".git", "skills_repo-starter", "node_modules"}
errors, warns, names = [], [], {}


def rel_links(text):
    for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        t = m.group(1).strip()
        if t.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield t.split("#")[0]


skill_dirs = []
for dirpath, dirnames, files in os.walk(ROOT):
    if set(dirpath.replace("\\", "/").split("/")) & IGNORE:
        continue
    dirnames[:] = [d for d in dirnames if d not in IGNORE]
    if "SKILL.md" in files:
        skill_dirs.append(dirpath)

for d in sorted(skill_dirs):
    sp = os.path.join(d, "SKILL.md")
    folder = os.path.basename(d.rstrip("/\\"))
    with open(sp, encoding="utf-8") as f:
        raw = f.read()
    if not raw.endswith("\n"):
        errors.append(f"{sp}: no trailing newline")
    if raw.endswith("\n\n"):
        warns.append(f"{sp}: multiple trailing newlines")
    fm = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
    if not fm:
        errors.append(f"{sp}: missing/malformed frontmatter")
        continue
    block = fm.group(1)
    if "\t" in block:
        errors.append(f"{sp}: tab in frontmatter")
    name_m = re.search(r"^name:\s*(.+)$", block, re.M)
    desc_m = re.search(r"^description:\s*(.+)$", block, re.M)
    if not name_m:
        errors.append(f"{sp}: no name")
        continue
    if not desc_m:
        errors.append(f"{sp}: no description")
        continue
    name, desc = name_m.group(1).strip(), desc_m.group(1).strip()
    if name != folder:
        errors.append(f"{sp}: name '{name}' != folder '{folder}'")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        errors.append(f"{sp}: name not kebab-case: '{name}'")
    if len(name) > 64:
        errors.append(f"{sp}: name >64 chars")
    if "claude" in name or "anthropic" in name:
        errors.append(f"{sp}: name contains claude/anthropic")
    names.setdefault(name, []).append(sp)
    if not (20 <= len(desc) <= 1024):
        errors.append(f"{sp}: description length {len(desc)} out of [20,1024]")
    if re.search(r"\b(I can|I will|you can|you should|we can)\b", desc, re.I):
        warns.append(f"{sp}: description may not be third person")
    if not re.search(r"\b(use (this|when)|when the user|when you)\b", desc, re.I):
        warns.append(f"{sp}: description may lack a 'when to use' cue")
    # Frontmatter-vs-body correctness heuristic: if the description advertises a
    # named, distinctive framework/method, the body should actually use it - otherwise
    # discovery mis-routes a request to a skill that never delivers the promised method
    # (the RACI/Kotter/SIFT over-claim class). Curated to distinctive proper-noun methods
    # so it does not false-positive on generic domain terms. Advisory only.
    body = raw[fm.end():]
    NAMED_METHODS = [
        "RACI", "RAPID", "RICE", "WSJF", "MoSCoW", "SWOT", "TOWS", "PESTLE",
        "BATNA", "ZOPA", "ADKAR", "Kotter", "CRAAP", "SIFT", "DMAIC", "DACI",
        "Kano", "Eisenhower", "Pomodoro", "MECE", "Fermi",
    ]
    for method in NAMED_METHODS:
        pat = rf"\b{re.escape(method)}\b"
        if re.search(pat, desc, re.I) and not re.search(pat, body, re.I):
            warns.append(f"{sp}: description names '{method}' but the body never uses "
                         "it - align the frontmatter with the method actually taught")
    # Script-gap heuristic: LOCAL document-producing/processing skills should ship a
    # script. Scoped to the office/ category (where local file production lives) and to
    # name prefixes that imply real file I/O AND an actual format mention, so it does
    # not fire on procedure skills (software/data/AI engineering, reasoning, etc.) that
    # merely mention a format. Google Workspace skills are exempt: they operate via API
    # and produce cloud documents, so the offline-script pattern does not apply.
    # Advisory only, never an error.
    top_cat = os.path.relpath(d, ROOT).replace("\\", "/").split("/")[0]
    if top_cat == "office" and "google" not in name and name.startswith(
            ("authoring-", "building-", "engineering-", "processing-",
             "producing-", "generating-", "running-", "automating-", "extracting-")):
        if re.search(r"\.(docx|xlsx|xlsm|pptx|pdf|csv)\b", raw, re.I) and \
                not os.path.isdir(os.path.join(d, "scripts")):
            warns.append(f"{sp}: produces/processes a file format but ships no "
                         "scripts/ - consider a validate_*/extract_* script "
                         "(see authoring-checklist 'Determinism')")
    for link in rel_links(raw):
        if not os.path.exists(os.path.normpath(os.path.join(d, link))):
            errors.append(f"{sp}: broken link -> {link}")

for name, paths in names.items():
    if len(paths) > 1:
        errors.append(f"duplicate skill name '{name}': {paths}")

# Canonical count is the CATALOG (excludes worked examples nested under examples/),
# matching generate_index.py and skills-index.md's "read this first" header. Worked
# examples are still fully validated above; they just don't count toward the headline.
examples = [d for d in skill_dirs if "examples" in d.replace("\\", "/").split("/")]
catalog = len(skill_dirs) - len(examples)
print(f"Scanned {len(skill_dirs)} SKILL.md ({catalog} catalog skills"
      + (f" + {len(examples)} worked example{'s' if len(examples) != 1 else ''}"
         if examples else "") + f") under {ROOT}")
print(f"\nERRORS ({len(errors)}):")
for e in errors:
    print("  [X]", e)
print(f"\nWARNINGS ({len(warns)}):")
for w in warns:
    print("  [!]", w)
sys.exit(1 if errors else 0)

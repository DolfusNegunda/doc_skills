#!/usr/bin/env python3
"""Fail if a live leadership doc states a stale total skill count or smoke-test count.

WHY THIS EXISTS: the total-skill headline in leadership docs (e.g. "87 skills") drifted
silently when five categories were added, because nothing tied the prose number to
reality. This guard makes that class of error fail CI instead of shipping.

Both canonical numbers are DERIVED, never hand-set:
  - total skills   = the CATALOG count (every SKILL.md except worked examples under an
                     examples/ dir and the skills_repo-starter snapshot) — identical to
                     skills-index.md's generated header and validate_skills.py's catalog line.
  - smoke-test N   = the number of check() assertions in smoke_test_scripts.py.

Only LIVE docs are checked. Dated benchmark records and REBENCHMARK-REQUEST.md are
archival — their historical numbers are correct-as-of-then and intentionally exempt.

Run from repo root:  python skill-builder/scripts/check_docs_fresh.py
Exits non-zero on any drift.
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
IGNORE_DIRS = {".git", "skills_repo-starter", "node_modules"}

# Live docs whose headline numbers must track reality. Dated benchmarks and the
# rebenchmark request are deliberately excluded (archival).
LIVE_DOCS = [
    "README.md", "ONBOARDING.md",
    "docs/LEAD-BRIEF.md", "docs/README.md", "docs/USER-GUIDE.md",
    "docs/skills-catalog.md", "docs/skill-selection-rationale.md",
    "docs/skills-library.html",
]

# A number >= this modifying "skill(s)" is a library TOTAL, not a per-category count
# (the largest single category is 42). Anything in [43, total) is therefore a stale total.
CATEGORY_CEILING = 43


def catalog_count():
    n = 0
    for dp, dns, fs in os.walk(ROOT):
        parts = set(dp.replace("\\", "/").split("/"))
        if parts & IGNORE_DIRS:
            continue
        dns[:] = [d for d in dns if d not in IGNORE_DIRS]
        if "SKILL.md" in fs and "examples" not in parts:
            n += 1
    return n


def smoke_check_count():
    src = open(os.path.join(ROOT, "skill-builder/scripts/smoke_test_scripts.py"),
               encoding="utf-8").read()
    return len(re.findall(r"(?m)^\s+check\(", src))  # indented calls, not the def


def main():
    total = catalog_count()
    checks = smoke_check_count()
    errors = []

    # "<n> ... skill(s)" where n is in the library-total range
    total_pat = re.compile(r"(\d+)(?:\s+[\w\"'./-]+){0,4}\s+skills?\b", re.I)
    # "<a>/<b>" appearing on a line that mentions checks/smoke/fixtures
    ratio_pat = re.compile(r"(\d+)\s*/\s*(\d+)")

    for rel in LIVE_DOCS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read()
        for m in total_pat.finditer(text):
            n = int(m.group(1))
            if CATEGORY_CEILING <= n and n != total:
                errors.append(f"{rel}: stale total skill count '{m.group(0).strip()}' "
                              f"(canonical is {total})")
        for line in text.splitlines():
            if re.search(r"\b(check|smoke|fixture)", line, re.I):
                for rm in ratio_pat.finditer(line):
                    a, b = int(rm.group(1)), int(rm.group(2))
                    if a == b and a != checks:
                        errors.append(f"{rel}: stale smoke-test count '{rm.group(0)}' "
                                      f"(canonical is {checks}/{checks})")

    print(f"Canonical: {total} catalog skills, {checks}/{checks} smoke checks")
    if errors:
        print(f"\nSTALE ({len(errors)}):")
        for e in errors:
            print("  [X]", e)
        sys.exit(1)
    print("All live docs are fresh.")
    sys.exit(0)


if __name__ == "__main__":
    main()

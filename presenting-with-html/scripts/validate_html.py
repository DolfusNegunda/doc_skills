"""Gate an HTML executive report before it ships.

Structural check (no browser needed) that the report follows the premium slide-deck
pattern: slide deck markup, working navigation, a persisted light/dark toggle with
BOTH theme token sets, Plotly present when charts are used, and no leftover
placeholders. Deterministic and cheap — pair it with an actual browser open (and a
headless screenshot for a vision pass) before delivery.

Usage:
    python scripts/validate_html.py report.html

Prints a JSON report; exit 0 only when status == "OK".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDERS = re.compile(r"\{\{.*?\}\}|lorem\s+ipsum|\bTODO\b|\bTBD\b|\bFIXME\b", re.I)


def check_html(html: str) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict = {}

    def need(name, cond, msg):
        checks[name] = bool(cond)
        if not cond:
            errors.append(msg)

    def want(name, cond, msg):
        checks[name] = bool(cond)
        if not cond:
            warnings.append(msg)

    # ---- Slide deck structure ----
    need("deck", 'class="deck"' in html or "class='deck'" in html,
         "No .deck container — the report must be a slide deck, not a scrolling page.")
    n_slides = len(re.findall(r'class="[^"]*\bslide\b', html))
    checks["n_slides"] = n_slides
    need("slides", n_slides >= 2, f"Found {n_slides} .slide sections; need at least 2.")
    need("active_slide", re.search(r'class="[^"]*\bslide\b[^"]*\bactive\b', html) is not None,
         "No slide marked .active — one slide must be visible on load.")

    # ---- Navigation ----
    need("nav_prev", re.search(r'class="[^"]*\bnav-btn\b[^"]*\bprev\b', html) is not None,
         "Missing previous-slide button (.nav-btn.prev).")
    need("nav_next", re.search(r'class="[^"]*\bnav-btn\b[^"]*\bnext\b', html) is not None,
         "Missing next-slide button (.nav-btn.next).")
    need("keyboard", "ArrowRight" in html and "ArrowLeft" in html,
         "No left/right arrow-key navigation (ArrowLeft/ArrowRight handlers).")
    need("show_slide", re.search(r"function\s+showSlide|showSlide\s*=", html) is not None,
         "No showSlide() navigation function.")
    want("dots", re.search(r'class="[^"]*\b(progress|dot)\b', html) is not None,
         "No progress dots (.progress/.dot) — recommended for wayfinding.")
    want("counter", re.search(r'class="[^"]*\bslide-count\b', html) is not None,
         "No slide counter (.slide-count) — recommended.")
    want("resize_dispatch", "resize" in html and "dispatchEvent" in html,
         "No resize dispatch on slide change — embedded charts may not re-fit.")
    want("scroll_reset", "scrollTop" in html,
         "No scroll reset on slide change — long slides keep their scroll position.")

    # ---- Theme (both token sets + persistence) ----
    need("theme_toggle", re.search(r'class="[^"]*\btheme-toggle\b|id="themeToggle"', html) is not None,
         "No visible light/dark theme toggle.")
    has_dark = re.search(r'data-theme=.?dark|:root\s*\{', html) is not None
    has_light = re.search(r'data-theme=.?light', html) is not None
    need("theme_both", has_dark and has_light,
         "Theme tokens must exist for BOTH dark and light (found dark=%s light=%s)." % (has_dark, has_light))
    want("theme_persist", "localStorage" in html,
         "Theme choice is not persisted (no localStorage) — it will reset on reload.")

    # ---- Charts ----
    uses_charts = re.search(r'\bchart\b|Plotly|data-chart', html) is not None
    checks["uses_charts"] = uses_charts
    if uses_charts:
        need("plotly", "Plotly" in html or "plotly" in html,
             "Charts referenced but Plotly is not included (CDN <script> or inlined lib).")
        want("plotly_theme", re.search(r"relayout|Plotly\.react|themeColors|build\(", html) is not None,
             "Charts may not restyle when the theme changes — re-render/relayout on toggle.")

    # ---- Content hygiene ----
    leftovers = sorted(set(m.group(0) for m in PLACEHOLDERS.finditer(html)))
    checks["placeholders"] = leftovers
    if leftovers:
        errors.append(f"Leftover placeholder/boilerplate text: {leftovers}")

    return errors, warnings, checks


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", help="Path to the .html report")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        sys.exit(f"file not found: {path}")
    html = path.read_text(encoding="utf-8", errors="ignore")
    errors, warnings, checks = check_html(html)

    report = {
        "file": str(path),
        "status": "OK" if not errors else "FAIL",
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()

"""Gate an HTML report before it ships — deck OR long-form.

Structural check (no browser needed) that the report follows the premium
presenting-with-html pattern. The skill ships two formats:

  * deck   — full-screen slides, arrow/keyboard/dot navigation (the boardroom deck)
  * report — a long-form scrolling document with a table of contents and print styles

The format is read from `data-format="deck|report"` on the <html> element and
defaults to "deck" when the marker is absent (so older decks still validate).

Some checks are FORMAT-AGNOSTIC and enforced in both modes — document integrity
(one DOCTYPE/html/body, nothing after </html>, unique element IDs, no live
data-sample template content, classes actually defined), both theme token sets,
a persisted toggle, Plotly present when charts are used, theme-aware chart
re-render, and no leftover placeholders. The rest are mode-specific: a deck must
have slide/nav structure; a report must have sections, an in-page TOC/anchors,
and print styles.

Deterministic and cheap — pair it with an actual browser open (and a headless
screenshot for a vision pass) before delivery.

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
CDN_PLOTLY = re.compile(r'src\s*=\s*["\']https?://[^"\']*plot(?:ly|\.ly)[^"\']*["\']', re.I)
UNPINNED_PLOTLY = re.compile(r'plotly-latest(?:\.min)?\.js', re.I)
ID_ATTR = re.compile(r'<[a-zA-Z][^>]*\bid\s*=\s*["\']([^"\']+)["\']')
CLASS_ATTR = re.compile(r'<[a-zA-Z][^>]*\bclass\s*=\s*["\']([^"\']+)["\']')
CSS_CLASS = re.compile(r'\.(-?[_a-zA-Z][_a-zA-Z0-9-]*)')
DATA_SAMPLE = re.compile(r'<[a-zA-Z][^>]*\bdata-sample\b')
# Classes toggled/created by the standard shell JS rather than authored in markup.
JS_MANAGED_CLASSES = {"active", "down", "show", "dot"}
# A <script> body this large is a vendored library (inlined Plotly ~4.7MB), not
# authored code — its internals (shader comments carry TODO/FIXME) must not trip
# the placeholder scan.
VENDORED_SCRIPT_MIN = 50_000
SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)


def _without_vendored_scripts(text: str) -> tuple[str, int]:
    """Blank the bodies of vendored-library <script> blocks; keep authored ones."""
    n = 0

    def repl(m):
        nonlocal n
        if len(m.group(1)) >= VENDORED_SCRIPT_MIN:
            n += 1
            return "<script></script>"
        return m.group(0)

    return SCRIPT_BLOCK.sub(repl, text), n


def detect_format(html: str) -> str:
    m = re.search(r'data-format\s*=\s*["\']?(deck|report)', html, re.I)
    return m.group(1).lower() if m else "deck"


def check_html(raw: str) -> tuple[list[str], list[str], dict]:
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

    # Strip HTML comments for STRUCTURAL checks so how-to-use guidance
    # (e.g. `<section class="report-section" id="...">` in a comment) isn't
    # miscounted as real markup. The placeholder scan still runs on `raw`.
    html = re.sub(r"<!--.*?-->", "", raw, flags=re.S)

    fmt = detect_format(html)
    checks["format"] = fmt

    # ================= DOCUMENT INTEGRITY (both modes) =================
    # These catch the "concatenated a second document onto the boilerplate" failure
    # mode: duplicated shells, duplicate IDs that silently break every JS hook, and
    # template sample content shipped live.
    need("single_doctype", len(re.findall(r"<!DOCTYPE", html, re.I)) == 1,
         "Exactly one <!DOCTYPE> required — more than one means two documents were "
         "concatenated into this file.")
    for tag in ("html", "head", "body"):
        n_open = len(re.findall(rf"<{tag}\b", html, re.I))
        checks[f"n_{tag}"] = n_open
        need(f"single_{tag}", n_open <= 1,
             f"Found {n_open} <{tag}> tags — a valid page has one. Content was appended "
             f"instead of replacing the template's sample content.")
    m_end = re.search(r"</html\s*>", html, re.I)
    trailing = html[m_end.end():].strip() if m_end else ""
    need("nothing_after_html", not trailing,
         f"Markup found after </html> ({len(trailing)} chars) — the file contains a second, "
         "orphaned document that browsers render unstyled or not at all.")

    ids = ID_ATTR.findall(html)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    checks["duplicate_ids"] = dupes
    need("unique_ids", not dupes,
         f"Duplicate element IDs {dupes} — getElementById binds only the first, so nav "
         "buttons/counters/theme toggles silently break.")

    n_samples = len(DATA_SAMPLE.findall(html))
    checks["sample_blocks"] = n_samples
    need("no_sample_content", n_samples == 0,
         f"{n_samples} block(s) still carry the data-sample marker — the template's example "
         "content is shipping live. Replace the content AND remove each data-sample attribute.")

    # Classes referenced in markup but never defined in <style> render unstyled —
    # usually invented class names. Warning (heuristic: JS-managed and SVG cases exist).
    defined = set()
    for style_block in re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I):
        defined |= set(CSS_CLASS.findall(style_block))
    used = set()
    for cls in CLASS_ATTR.findall(html):
        used |= set(cls.split())
    undefined = sorted(used - defined - JS_MANAGED_CLASSES)
    checks["undefined_classes"] = undefined
    want("classes_defined", not undefined,
         f"Classes used in markup but not defined in any <style>: {undefined} — they will "
         "render unstyled (typo or invented class name?).")

    # ================= FORMAT-AGNOSTIC INVARIANTS (both modes) =================
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
             "Charts referenced but Plotly is not included (inline lib, local file, or CDN <script>).")
        want("plotly_theme", re.search(r"relayout|Plotly\.react|themeColors|build\(", html) is not None,
             "Charts may not restyle when the theme changes — re-render/relayout on toggle.")
        # Self-contained delivery: an external CDN dep is a warning, not a failure.
        # Fold it in with:  python scripts/vendor_plotly.py --inline <file>
        want("plotly_selfcontained", CDN_PLOTLY.search(html) is None,
             "Plotly loads from an external CDN — not self-contained/CSP-safe. Before delivery run "
             "`python scripts/vendor_plotly.py --inline <file>` to inline the library.")
        want("plotly_pinned", UNPINNED_PLOTLY.search(html) is None,
             "Plotly is loaded as 'plotly-latest' — deprecated and non-reproducible. Pin a "
             "version (the shells use 2.35.2) or inline the library.")

    # ---- Content hygiene (scan raw text incl. comments) ----
    # Vendored libraries (an inlined Plotly) legitimately contain TODO/FIXME in
    # their own comments — blank those script bodies so only authored content is
    # scanned. Validation therefore works the same before and after --inline-plotly.
    scannable, n_vendored = _without_vendored_scripts(raw)
    checks["vendored_scripts_skipped"] = n_vendored
    leftovers = sorted(set(m.group(0) for m in PLACEHOLDERS.finditer(scannable)))
    checks["placeholders"] = leftovers
    if leftovers:
        errors.append(f"Leftover placeholder/boilerplate text: {leftovers}")

    # ================= MODE-SPECIFIC CHECKS =================
    if fmt == "deck":
        _check_deck(html, need, want, checks)
    else:
        _check_report(html, need, want, checks)

    return errors, warnings, checks


def _check_deck(html, need, want, checks):
    # ---- Slide deck structure ----
    # The deck shell scales a fixed 1920x1080 .stage canvas to fit (non-scrolling);
    # legacy decks used a .deck container. Accept either — both guarantee a slide
    # deck rather than a scrolling page.
    need("deck",
         any(f'class="{c}"' in html or f"class='{c}'" in html for c in ("stage", "deck")),
         "No slide-deck container — deck format needs a fixed .stage (or legacy .deck) "
         "canvas, not a scrolling page.")
    # Token-exact count: `\bslide\b` alone also matches slide-inner /
    # slide-count (the hyphen is a word boundary) and inflates the number.
    n_slides = sum(1 for m in re.finditer(r'class="([^"]*)"', html)
                   if "slide" in m.group(1).split())
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


def _check_report(html, need, want, checks):
    # ---- Long-form report structure ----
    n_sections = len(re.findall(r'class="[^"]*\breport-section\b', html))
    checks["n_sections"] = n_sections
    need("sections", n_sections >= 2,
         f"Found {n_sections} .report-section blocks; a report needs at least 2.")
    # Sections must be anchorable and the page must link to them (in-page TOC).
    ids = set(re.findall(r'<section[^>]*class="[^"]*\breport-section\b[^"]*"[^>]*\bid="([^"]+)"', html))
    ids |= set(re.findall(r'<section[^>]*\bid="([^"]+)"[^>]*class="[^"]*\breport-section\b', html))
    checks["section_ids"] = sorted(ids)
    need("section_anchors", len(ids) >= 2,
         "Report sections need unique id anchors so the TOC and deep links work.")
    need("toc", re.search(r'class="[^"]*\btoc\b|id="toc"', html) is not None,
         "No table of contents (.toc / #toc) — required for a navigable long-form report.")
    anchor_links = set(re.findall(r'href="#([^"]+)"', html))
    want("toc_links", len(anchor_links & ids) >= 2 or "data-toc" in html,
         "TOC does not appear to link to section anchors (href=\"#id\" or data-toc entries).")
    want("scrollspy", "IntersectionObserver" in html,
         "No scroll-spy (IntersectionObserver) — the TOC won't track the current section.")
    # ---- Print / PDF ----
    need("print_styles", re.search(r"@media\s+print", html) is not None,
         "No @media print block — long-form reports must be printable / PDF-clean.")
    # Only a lock on the PAGE (an html/body rule, or inline on <body>) blocks
    # scrolling; overflow:hidden on cards/figures/chart panels is normal clipping.
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I))
    body_locked = any(
        re.search(r"(?:^|[\s,}])(?:html|body)\s*(?:,[^{]*)?$", sel.strip(), re.I)
        and re.search(r"overflow(?:-y)?\s*:\s*hidden", rule, re.I)
        for sel, rule in re.findall(r"([^{}]+)\{([^{}]*)\}", css)
    ) or re.search(r"<body[^>]*style\s*=\s*['\"][^'\"]*overflow(?:-y)?\s*:\s*hidden", html, re.I)
    want("no_horizontal_overflow", not body_locked,
         "The page itself sets overflow:hidden on html/body — a report must scroll.")


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
        "format": checks.get("format"),
        "status": "OK" if not errors else "FAIL",
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()

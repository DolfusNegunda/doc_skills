"""Make presenting-with-html reports self-contained (offline / CSP-safe).

The templates load Plotly from a CDN so charts work instantly while you author.
Before you SHIP a report — email, SharePoint, an air-gapped machine, or anywhere
an org content-security policy blocks external scripts — fold the library into the
file so it needs nothing from the network.

Two operations:

  1. Vendor the library once (download it next to the templates):
         python scripts/vendor_plotly.py --fetch
     Saves assets/vendor/plotly.min.js. Point a template's <script src> at it for
     local preview, or use it as the source for --inline below.

  2. Inline the library into a finished report (produces one self-contained file):
         python scripts/vendor_plotly.py --inline report.html
         python scripts/vendor_plotly.py --inline report.html --out report.final.html
     Replaces the CDN/local <script src="...plotly..."> tag with an inline
     <script>…library…</script>. If a vendored copy exists it is reused; otherwise
     the library is downloaded once.

Network note: downloading reaches cdn.plot.ly. If your environment blocks that
(offline or CSP), fetch plotly.min.js on a machine that can, drop it at
assets/vendor/plotly.min.js, and re-run --inline; it will reuse the local copy
without any network access.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.request import urlopen

PLOTLY_VERSION = "2.35.2"
PLOTLY_URL = f"https://cdn.plot.ly/plotly-{PLOTLY_VERSION}.min.js"

SKILL_ROOT = Path(__file__).resolve().parent.parent
VENDOR_PATH = SKILL_ROOT / "assets" / "vendor" / "plotly.min.js"

# <script ... src="...plotly...">...</script>  (src may carry other attrs)
SCRIPT_TAG = re.compile(
    r'<script\b[^>]*\bsrc\s*=\s*["\'][^"\']*plot(?:ly|\.ly)[^"\']*["\'][^>]*>\s*</script>',
    re.I,
)


def load_library(prefer_vendored: bool = True) -> str:
    """Return the Plotly library source — from the vendored copy if present, else download."""
    if prefer_vendored and VENDOR_PATH.exists():
        return VENDOR_PATH.read_text(encoding="utf-8")
    try:
        with urlopen(PLOTLY_URL, timeout=60) as resp:  # noqa: S310 (fixed, trusted URL)
            return resp.read().decode("utf-8")
    except Exception as exc:  # network blocked, offline, CSP, etc.
        raise SystemExit(
            f"Could not download Plotly from {PLOTLY_URL} ({exc}).\n"
            f"Fetch it on a connected machine and save it to:\n  {VENDOR_PATH}\n"
            f"then re-run — the vendored copy is reused without network access."
        )


def fetch() -> None:
    VENDOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    lib = load_library(prefer_vendored=False)
    VENDOR_PATH.write_text(lib, encoding="utf-8")
    print(f"Vendored Plotly {PLOTLY_VERSION} -> {VENDOR_PATH} ({len(lib):,} bytes)")
    print('Reference it locally with:  <script src="vendor/plotly.min.js"></script>')


def inline(html_path: Path, out_path: Path | None) -> None:
    html = html_path.read_text(encoding="utf-8")
    if not SCRIPT_TAG.search(html):
        if "Plotly" in html and "<script>" in html:
            raise SystemExit(f"{html_path}: no external Plotly <script src> found — it looks already inlined.")
        raise SystemExit(f"{html_path}: no Plotly <script src=...> tag to replace.")
    lib = load_library()
    # Guard against the sequence </script> inside the library breaking the tag.
    safe = lib.replace("</script>", "<\\/script>")
    replacement = f"<script>/* Plotly {PLOTLY_VERSION} — inlined for self-contained delivery */\n{safe}\n</script>"
    new_html = SCRIPT_TAG.sub(lambda _m: replacement, html, count=1)
    target = out_path or html_path
    target.write_text(new_html, encoding="utf-8")
    print(f"Inlined Plotly {PLOTLY_VERSION} into {target} ({len(new_html):,} bytes). File is now self-contained.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fetch", action="store_true", help="Download Plotly to assets/vendor/plotly.min.js")
    g.add_argument("--inline", metavar="HTML", help="Fold Plotly into the given report HTML")
    ap.add_argument("--out", metavar="HTML", help="With --inline: write here instead of in place")
    args = ap.parse_args()

    if args.fetch:
        fetch()
    else:
        html_path = Path(args.inline)
        if not html_path.exists():
            sys.exit(f"file not found: {html_path}")
        inline(html_path, Path(args.out) if args.out else None)


if __name__ == "__main__":
    main()

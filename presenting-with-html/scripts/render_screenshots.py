"""Screenshot every slide/section of a built deliverable for the vision-QA gate.

One command replaces the browser trial-and-error that dominates QA cost:

    python scripts/render_screenshots.py out.html --out-dir shots

It reads the file's data-format, then drives a headless Chromium-family browser
through the shells' QA hooks (?slide=N for decks, ?theme=dark|light for both).
Decks are shot one slide per invocation; reports are shot ONCE per theme with a
very tall window and sliced into page-sized PNGs (fragment/scroll captures are
unreliable in headless browsers), blank tail segments dropped automatically.

  * FULL pass in the document's default theme (every slide / every page)
  * SPOT pass in the other theme (first pages / first + chart slides) — charts
    are the only theme-sensitive components, so this catches theme bugs at a
    fraction of the image cost. Override with --second-theme full|none.

Then Read/inspect each PNG. The browser is auto-detected (Edge, Chrome,
Chromium); pass --browser to point at one explicitly. Screenshots run one
browser invocation at a time (parallel headless launches hang on some hosts).
If no browser exists, this exits non-zero with a clear message — deliver only
with an explicit caveat that the vision gate could not run; never skip silently.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BROWSER_CANDIDATES = [
    "msedge", "chrome", "chromium", "chromium-browser", "google-chrome",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser(explicit: str | None) -> str | None:
    if explicit:
        p = shutil.which(explicit) or (explicit if Path(explicit).exists() else None)
        if not p:
            sys.exit(f"browser not found: {explicit}")
        return p
    for cand in BROWSER_CANDIDATES:
        p = shutil.which(cand) or (cand if Path(cand).exists() else None)
        if p:
            return p
    return None


def no_browser_fallback(path: Path) -> None:
    """Locked-down environments (no Chromium, missing system libs, no root): the
    vision gate CANNOT run. Never fake it, never patch around it, never skip it
    silently — run the structural self-check and attach the disclosure verbatim
    to the delivery so the recipient knows what was and wasn't verified."""
    import subprocess as sp
    here = Path(__file__).resolve().parent
    print("No browser available — running the structural self-check instead "
          "(NOT a substitute for looking at the pages):")
    r = sp.run([sys.executable, str(here / "validate_html.py"), str(path)],
               capture_output=True, text=True)
    print(f"  validate_html.py: {'OK' if r.returncode == 0 else 'FAIL — fix errors first'}")
    html = path.read_text(encoding="utf-8", errors="ignore")
    print(f"  charts registered: {html.count('data-chart=')}   "
          f"embedded images: {html.count('data:image/')}   "
          f"file size: {path.stat().st_size / 1e6:.1f} MB")
    print("\nREQUIRED DISCLOSURE — deliver only with this text attached:")
    print("  The mandatory visual QA pass could not be performed in this environment")
    print("  (no headless browser could run). Structural validation passed, but layout,")
    print("  theme contrast, overflow, and chart rendering have NOT been visually")
    print("  verified - please open the file and check each page before distributing.")
    sys.exit(3)


def shoot(browser: str, url: str, out_png: Path, size: str, timeout: int) -> bool:
    # reduced-motion: the shells disable entry animations under it, so the
    # capture is never mid-fade.
    cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-prefers-reduced-motion", "--disable-smooth-scrolling",
           f"--window-size={size}", f"--screenshot={out_png}", url]
    try:
        subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False
    for _ in range(80):     # the PNG can land on disk well after the process exits
        if out_png.exists():
            return True
        time.sleep(0.25)
    return False


def slice_page(tall_png: Path, out_dir: Path, prefix: str, seg_h: int,
               keep: int | None = None) -> list[str]:
    """Slice a tall full-page capture into page-sized PNGs; drop blank tails.
    keep=N limits to the first N segments (the spot pass)."""
    from PIL import Image, ImageStat
    im = Image.open(tall_png)
    w, h = im.size
    names: list[str] = []
    n = 0
    for top in range(0, h, seg_h):
        seg = im.crop((0, top, w, min(top + seg_h, h)))
        # variance of the content column: blank background is ~0, content >100
        probe = seg.crop((int(w * 0.2), 0, int(w * 0.92), seg.height)).convert("L")
        if ImageStat.Stat(probe).var[0] < 10:
            continue
        n += 1
        if keep is not None and n > keep:
            break
        name = f"{prefix}_p{n:02d}.png"
        seg.save(out_dir / name)
        names.append(name)
    tall_png.unlink(missing_ok=True)
    return names


def deck_targets(html: str) -> tuple[int, set[int]]:
    """(slide count, 1-based slide numbers that carry a chart)."""
    slides = re.findall(r'<section[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>', html)
    bodies = re.split(r'<section[^>]*class="[^"]*\bslide\b[^"]*"[^>]*>', html)[1:]
    chart_slides = {i + 1 for i, b in enumerate(bodies) if "data-chart" in b}
    return len(slides), chart_slides


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="Built .html deliverable")
    ap.add_argument("--out-dir", default="shots", help="Directory for the PNGs (default: shots)")
    ap.add_argument("--browser", default=None, help="Browser executable (default: auto-detect)")
    ap.add_argument("--second-theme", choices=("spot", "full", "none"), default="spot",
                    help="Coverage for the non-default theme (default: spot = first page + chart pages)")
    ap.add_argument("--size", default="1400,900", help="Window size WxH (default: 1400,900)")
    ap.add_argument("--page-height", type=int, default=14000,
                    help="Tall-capture height for reports (default: 14000)")
    ap.add_argument("--timeout", type=int, default=60, help="Seconds per screenshot (default: 60)")
    args = ap.parse_args()

    path = Path(args.file).resolve()
    if not path.exists():
        sys.exit(f"file not found: {path}")
    html = path.read_text(encoding="utf-8", errors="ignore")

    fmt_m = re.search(r'data-format\s*=\s*["\']?(deck|report)', html, re.I)
    fmt = fmt_m.group(1).lower() if fmt_m else "deck"
    theme_m = re.search(r'data-theme\s*=\s*["\'](dark|light)', html, re.I)
    default_theme = theme_m.group(1).lower() if theme_m else "dark"
    other_theme = "light" if default_theme == "dark" else "dark"

    browser = find_browser(args.browser)
    if browser is None:
        no_browser_fallback(path)
    # Absolute: headless Chromium resolves --screenshot against ITS OWN cwd.
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    base_url = path.as_uri()
    stem = path.stem
    shots: list[tuple[str, str]] = []   # (url, png name)

    ok, failed = [], []

    def do_shot(url, name):
        good = shoot(browser, url, out_dir / name, args.size, args.timeout)
        (ok if good else failed).append(name)
        print(("  ok    " if good else "  FAIL  ") + name)
        return good

    if fmt == "deck":
        n, chart_slides = deck_targets(html)
        if n == 0:
            sys.exit("no .slide sections found — is this a built deck?")
        for i in range(1, n + 1):
            do_shot(f"{base_url}?theme={default_theme}&slide={i}",
                    f"{stem}_{default_theme}_s{i:02d}.png")
        if args.second_theme != "none":
            spot = range(1, n + 1) if args.second_theme == "full" else \
                sorted({1, *list(chart_slides)[:2]})
            for i in spot:
                do_shot(f"{base_url}?theme={other_theme}&slide={i}",
                        f"{stem}_{other_theme}_s{i:02d}.png")
    else:
        # One tall capture per theme, sliced into page-sized segments.
        width, seg_h = (int(x) for x in args.size.split(","))
        tall = f"{width},{args.page_height}"
        passes = [(default_theme, None)]
        if args.second_theme != "none":
            passes.append((other_theme, None if args.second_theme == "full" else 4))
        for theme, keep in passes:
            tall_png = out_dir / f"_tall_{stem}_{theme}.png"
            if shoot(browser, f"{base_url}?theme={theme}", tall_png, tall,
                     max(args.timeout, 90)):
                for name in slice_page(tall_png, out_dir, f"{stem}_{theme}", seg_h, keep):
                    ok.append(name)
                    print("  ok    " + name)
            else:
                failed.append(f"_tall_{stem}_{theme}.png")
                print(f"  FAIL  full-page capture ({theme})")

    print(f"\n{len(ok)} screenshot(s) -> {out_dir}  "
          f"(format {fmt}, full {default_theme} + {args.second_theme} {other_theme})")
    print("Now Read each PNG and check: contrast in both themes, charts drawn, "
          "nothing overflowing or misaligned, branding present/absent as intended.")
    if failed:
        sys.exit(f"{len(failed)} capture(s) failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()

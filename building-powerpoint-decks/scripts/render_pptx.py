"""Render a .pptx to one PNG per slide for the mandatory vision-QA pass.

The structural validator (validate_pptx.py) reads the deck's *markup* — it cannot
see overflowing text, overlapping shapes, autofit shrink, off-brand color, or a
chart that renders wrong. This script produces the images you then Read, exactly
like the presenting-with-html skill opens its deck in a browser. Structure gate +
vision gate together; neither substitutes for the other.

Usage:
    python scripts/render_pptx.py deck.pptx                 # -> deck.pptx.render/Slide1.PNG ...
    python scripts/render_pptx.py deck.pptx --out shots     # custom output dir
    python scripts/render_pptx.py deck.pptx --width 2000    # px width per slide (default 1600)

Then Read each PNG and check: text fits (no clipping/overlap/autofit shrink),
titles are the takeaway, alignment is consistent, charts make their one point,
color/contrast is on-brand. Fix in the deck and re-render.

Rendering path: Microsoft PowerPoint via COM (Windows + Office — the org's setup).
Prints a JSON report; exit 0 on success. If PowerPoint/pywin32 is unavailable,
falls back to instructions for the LibreOffice path:
    soffice --headless --convert-to pdf deck.pptx   (then rasterize the PDF)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def render_with_powerpoint(pptx: Path, outdir: Path, width: int) -> list[str]:
    import win32com.client  # pywin32; Windows + PowerPoint only

    # 4:3 = 10x7.5in, 16:9 = 13.333x7.5in — keep the deck's own aspect ratio.
    # PowerPoint exports at the height implied by width and the slide aspect.
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    rendered: list[str] = []
    try:
        # WithWindow=False keeps it off-screen; ReadOnly avoids lock prompts.
        pres = ppt.Presentations.Open(str(pptx), True, False, False)
        try:
            aspect = pres.PageSetup.SlideHeight / pres.PageSetup.SlideWidth
            height = int(round(width * aspect))
            outdir.mkdir(parents=True, exist_ok=True)
            for i, slide in enumerate(pres.Slides, start=1):
                target = outdir / f"Slide{i:02d}.png"
                slide.Export(str(target), "PNG", width, height)
                rendered.append(str(target))
        finally:
            pres.Close()
    finally:
        ppt.Quit()
    return rendered


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="Path to the .pptx deck")
    ap.add_argument("--out", help="Output directory for PNGs (default: <deck>.render)")
    ap.add_argument("--width", type=int, default=1600, help="Pixel width per slide (default 1600)")
    args = ap.parse_args()

    pptx = Path(args.file).resolve()
    if not pptx.exists():
        sys.exit(f"file not found: {pptx}")
    outdir = Path(args.out).resolve() if args.out else pptx.with_suffix(pptx.suffix + ".render")

    rendered: list[str] = []
    last_exc: Exception | None = None
    for attempt in range(3):
        try:
            rendered = render_with_powerpoint(pptx, outdir, args.width)
            break
        except ImportError:
            sys.exit(
                "PowerPoint COM path needs pywin32 on Windows with Office installed.\n"
                "Fallback (LibreOffice): soffice --headless --convert-to pdf "
                f'"{pptx}"\nthen rasterize the PDF (e.g. pdftoppm -png deck.pdf slide).'
            )
        except Exception as exc:  # COM automation is single-instance and flaky
            last_exc = exc
            if attempt < 2:
                print(f"PowerPoint COM attempt {attempt + 1} failed ({exc}) — PowerPoint "
                      "may be busy with another render; retrying in 5s...")
                time.sleep(5)
    if not rendered and last_exc is not None:
        print(f"render failed via PowerPoint COM after 3 attempts: {last_exc}")
        print("\nThe vision gate CANNOT run without a renderer. Do NOT substitute a "
              "programmatic text read of the deck — it cannot see overflow, overlap, "
              "autofit shrink, or broken charts.")
        print("\nREQUIRED DISCLOSURE — deliver only with this text attached:")
        print("  The mandatory visual QA pass could not be performed in this environment")
        print("  (PowerPoint/LibreOffice rendering unavailable). Structural validation")
        print("  passed, but layout, text fit, and chart rendering have NOT been visually")
        print("  verified - please open the deck and check each slide before distributing.")
        sys.exit(3)

    report = {
        "file": str(pptx),
        "status": "OK" if rendered else "FAILED",
        "out_dir": str(outdir),
        "n_slides": len(rendered),
        "images": rendered,
        "next": "Read each PNG; check overflow, alignment, titles-as-takeaway, chart clarity, on-brand color.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(0 if rendered else 1)


if __name__ == "__main__":
    main()

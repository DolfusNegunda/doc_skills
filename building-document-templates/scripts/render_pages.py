"""Render a .docx / .pptx / .pdf to one PNG per page/slide — for VISION inspection.

The template engine only reasons about *text* and *properties*. It cannot see
layout, spacing, a stale cover, an overflowing table, a logo in the wrong place, or
a mis-swapped image. Those are caught by *looking* at the rendered pages. This helper
produces the images so an agent can Read them:

  * before templatizing — understand the source's structure, layout and branding
    page by page, so the fixed/variable split and the preserve decisions are informed;
  * after filling — QA the output page by page against the source, catching anything
    validate.py (text-only) cannot see. This is the gate that caught a data-bound
    cover staying stale while the body updated.

Rendering path (first that works):
  1. LibreOffice headless (`soffice`/`libreoffice --convert-to pdf`) — cross-platform,
     the repo's documented converter.
  2. Microsoft Office COM via PowerShell (Windows only) — Word/PowerPoint SaveAs PDF.
  3. If the input is already a .pdf, skip straight to rasterizing.
Then PyMuPDF (`fitz`) rasterizes the PDF to PNGs (falls back to `pdftoppm`).

Usage:
    python scripts/render_pages.py INPUT.docx --out-dir pages/ [--dpi 110]
    # prints one PNG path per line; Read them to inspect.

Deps: PyMuPDF (`pip install pymupdf`). Plus LibreOffice OR (on Windows) Office.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Word/PowerPoint SaveAs format codes for PDF (used by the COM fallback).
_WD_PDF = 17
_PP_PDF = 32


def _to_pdf_libreoffice(src: Path, out_dir: Path) -> Path | None:
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        return None
    try:
        subprocess.run([exe, "--headless", "--convert-to", "pdf",
                        "--outdir", str(out_dir), str(src)],
                       check=True, capture_output=True, timeout=180)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    pdf = out_dir / (src.stem + ".pdf")
    return pdf if pdf.exists() else None


def _to_pdf_office_com(src: Path, out_dir: Path) -> Path | None:
    """Windows fallback: drive Word/PowerPoint via PowerShell to SaveAs PDF."""
    if sys.platform != "win32":
        return None
    pdf = out_dir / (src.stem + ".pdf")
    ext = src.suffix.lower()
    s, p = str(src).replace("'", "''"), str(pdf).replace("'", "''")
    if ext in (".docx", ".doc", ".rtf"):
        ps = (f"$w=New-Object -ComObject Word.Application;$w.Visible=$false;"
              f"$d=$w.Documents.Open('{s}',$false,$true);"
              f"try{{$d.Fields.Update()|Out-Null}}catch{{}};"
              f"$d.SaveAs([ref]'{p}',[ref]{_WD_PDF});$d.Close($false);$w.Quit()")
    elif ext in (".pptx", ".ppt"):
        ps = (f"$a=New-Object -ComObject PowerPoint.Application;"
              f"$d=$a.Presentations.Open('{s}',$true,$false,$false);"
              f"$d.SaveAs('{p}',{_PP_PDF});$d.Close();$a.Quit()")
    else:
        return None
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       check=True, capture_output=True, timeout=240)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None
    return pdf if pdf.exists() else None


def to_pdf(src: Path, out_dir: Path) -> Path:
    if src.suffix.lower() == ".pdf":
        return src
    pdf = _to_pdf_libreoffice(src, out_dir) or _to_pdf_office_com(src, out_dir)
    if not pdf:
        sys.exit("Could not convert to PDF: install LibreOffice (headless) or, on "
                 "Windows, have Microsoft Office available. See this script's header.")
    return pdf


def rasterize(pdf: Path, out_dir: Path, dpi: int, prefix: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        import fitz  # PyMuPDF
    except ImportError:
        # Fallback: pdftoppm if present.
        if shutil.which("pdftoppm"):
            subprocess.run(["pdftoppm", "-r", str(dpi), "-png", str(pdf),
                            str(out_dir / prefix)], check=True)
            return sorted(out_dir.glob(f"{prefix}*.png"))
        sys.exit("Need PyMuPDF (`pip install pymupdf`) or pdftoppm to rasterize.")
    doc = fitz.open(str(pdf))
    paths = []
    for i, page in enumerate(doc):
        out = out_dir / f"{prefix}{i + 1:03d}.png"
        page.get_pixmap(dpi=dpi).save(str(out))
        paths.append(out)
    return paths


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Path to .docx / .pptx / .pdf")
    ap.add_argument("--out-dir", default="pages", help="Directory for the PNGs")
    ap.add_argument("--dpi", type=int, default=110, help="Raster DPI (90-150 typical)")
    ap.add_argument("--prefix", default="page-", help="PNG filename prefix")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"file not found: {src}")
    out_dir = Path(args.out_dir)

    with tempfile.TemporaryDirectory() as tmp:
        pdf = to_pdf(src, Path(tmp))
        pages = rasterize(pdf, out_dir, args.dpi, args.prefix)

    for p in pages:
        print(p)
    print(f"# {len(pages)} page(s) rendered to {out_dir} — Read each to inspect.",
          file=sys.stderr)


if __name__ == "__main__":
    main()

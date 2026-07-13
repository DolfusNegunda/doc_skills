"""Optional: convert a filled .docx/.pptx to PDF for distribution.

PDF is an EXPORT stage, not a template. This wraps LibreOffice headless
conversion. If LibreOffice is not installed, it prints setup guidance and exits
non-zero rather than failing silently.

Usage:
    python scripts/export_pdf.py examples/output/globex-week-27.docx
    # writes examples/output/globex-week-27.pdf
"""
import shutil
import subprocess
import sys
from pathlib import Path


def find_soffice():
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    # common Windows install location
    for c in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"):
        if Path(c).exists():
            return c
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/export_pdf.py <file.docx|file.pptx>")
    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"ERROR: not found: {src}")

    soffice = find_soffice()
    if not soffice:
        print(
            "LibreOffice not found. PDF export needs it. Options:\n"
            "  - Install LibreOffice (https://www.libreoffice.org/) and re-run, or\n"
            "  - Open the .docx in Microsoft Word and use File > Save As > PDF, or\n"
            "  - Use the Word desktop app's 'Export' if running in an Office environment."
        )
        sys.exit(2)

    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir",
         str(src.parent), str(src)],
        check=True,
    )
    print(f"PDF written: {src.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()

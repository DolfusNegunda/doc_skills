"""Detect a document's real type by signature and recommend the ingestion route.

The router's deterministic first step: never trust the extension alone (a .pdf can be
a scan, a .xlsx can be a renamed CSV). Reads magic bytes / container structure and
maps the file to the correct processing skill. Stdlib only — no dependencies.

Prints JSON: detected type, how it was detected, and the skill to route to.
Exits 0 on a confident detection, 2 when the type cannot be determined.

Usage:
    python scripts/detect_type.py path/to/file
"""
import json
import sys
import zipfile
from pathlib import Path

ROUTE = {
    "pdf": "extracting-text-with-ocr OR processing-pdf-documents (test text layer)",
    "docx": "processing-word-documents",
    "xlsx": "processing-excel-files",
    "pptx": "processing-powerpoint-files",
    "doc": "convert .doc -> .docx first, then processing-word-documents",
    "legacy-office": "convert to the modern format first (LibreOffice/pandoc)",
    "csv": "processing-excel-files",
    "text": "read directly (plain text/markdown)",
    "image": "extracting-text-with-ocr (if it is a photo/scan of text)",
    "zip": "unknown OOXML/zip — inspect contents",
    "unknown": "cannot ingest — report to the user",
}


def sniff_ooxml(path):
    """Distinguish docx/xlsx/pptx by the parts inside the OOXML zip."""
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
    except zipfile.BadZipFile:
        return None
    if "word/document.xml" in names:
        return "docx"
    if "xl/workbook.xml" in names:
        return "xlsx"
    if "ppt/presentation.xml" in names:
        return "pptx"
    if "[Content_Types].xml" in names:
        return "zip"  # some OOXML-family zip
    return "zip"


def looks_like_text(head):
    try:
        head.decode("utf-8")
        return b"\x00" not in head
    except UnicodeDecodeError:
        return False


def detect(path):
    with open(path, "rb") as f:
        head = f.read(8)
    ext = path.suffix.lower().lstrip(".")

    if head.startswith(b"%PDF"):
        return "pdf", "magic bytes %PDF"
    if head.startswith(b"PK\x03\x04"):  # zip container -> maybe OOXML
        ooxml = sniff_ooxml(path)
        if ooxml:
            return ooxml, "zip container part inspection"
        return "zip", "zip container (unrecognized parts)"
    if head.startswith(b"\xd0\xcf\x11\xe0"):  # OLE compound (legacy .doc/.xls/.ppt)
        return "legacy-office", "OLE compound-document signature"
    if head.startswith(b"\x89PNG") or head.startswith(b"\xff\xd8\xff") or head[:6] in (b"GIF87a", b"GIF89a"):
        return "image", "image magic bytes"

    # Text-family: decide CSV vs plain text by delimiter presence.
    with open(path, "rb") as f:
        sample = f.read(65536)
    if looks_like_text(sample):
        text = sample.decode("utf-8", errors="replace")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if ext == "csv" or ("," in first_line or ";" in first_line or "\t" in first_line):
            return "csv", "text with delimiters"
        return "text", "decodable UTF-8 text"
    return "unknown", "no known signature"


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/detect_type.py <file>")
    path = Path(sys.argv[1])
    if not path.exists():
        sys.exit(f"file not found: {path}")

    detected, how = detect(path)
    ext = path.suffix.lower().lstrip(".")
    # Flag a mismatch between the extension and the true signature.
    ext_family = {"docx": "docx", "xlsx": "xlsx", "pptx": "pptx", "pdf": "pdf",
                  "csv": "csv", "txt": "text", "md": "text"}.get(ext)
    mismatch = bool(ext_family) and ext_family != detected and not (
        detected == "zip" and ext_family in {"docx", "xlsx", "pptx"})

    report = {
        "file": str(path),
        "extension": ext,
        "detected_type": detected,
        "detected_by": how,
        "extension_matches_signature": (not mismatch),
        "route_to": ROUTE.get(detected, ROUTE["unknown"]),
    }
    if mismatch:
        report["warning"] = (
            f"Extension '.{ext}' does not match the signature ('{detected}'); "
            "trust the signature.")
    print(json.dumps(report, indent=2))
    sys.exit(0 if detected != "unknown" else 2)


if __name__ == "__main__":
    main()

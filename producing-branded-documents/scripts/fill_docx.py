"""Fill the standard Word template with one project's data + client logo.

The template holds the invariant (layout, header/footer, logo frame, brand);
this script supplies the variable (content + which logo). Logo selection:
  1. explicit --logo path, else
  2. assets/logos/clients/<client_key>.png, else
  3. assets/logos/company.png  (fallback; a warning is printed)

Usage:
    python scripts/fill_docx.py --data examples/sample_update.json \
        --out examples/output/globex-week-27.docx
"""
import argparse
import json
import sys
from pathlib import Path

from docx.shared import Inches
from docxtpl import DocxTemplate, InlineImage, RichText

BASE = Path(__file__).resolve().parents[1]
LOGO_HEIGHT_IN = 0.5

# RAG status -> color (hex). Applied to the "Overall status" cell.
RAG_COLORS = {"green": "2E7D32", "amber": "F9A825", "red": "C62828",
              "on track": "2E7D32", "at risk": "F9A825", "off track": "C62828"}


def resolve_logo(data, explicit):
    if explicit:
        p = Path(explicit)
        if not p.exists():
            sys.exit(f"ERROR: --logo path not found: {p}")
        return p
    key = (data.get("client_key") or data.get("client_name", "")).strip().lower().replace(" ", "-")
    candidate = BASE / "assets" / "logos" / "clients" / f"{key}.png"
    if candidate.exists():
        return candidate
    fallback = BASE / "assets" / "logos" / "company.png"
    print(f"WARNING: no client logo for '{key}', using fallback {fallback.name}")
    return fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=str(BASE / "assets" / "templates" / "weekly-project-update.docx"))
    ap.add_argument("--data", required=True, help="JSON file with the project content")
    ap.add_argument("--logo", default=None, help="Explicit logo path (overrides lookup)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    tpl = DocxTemplate(args.template)

    logo_path = resolve_logo(data, args.logo)
    status_text = str(data.get("overall_status", "")).strip()
    rt = RichText()
    rt.add(status_text or "—", bold=True,
           color=RAG_COLORS.get(status_text.lower(), "222222"))

    context = {
        "logo": InlineImage(tpl, str(logo_path), height=Inches(LOGO_HEIGHT_IN)),
        "company_name": data.get("company_name", "ACME Consulting"),
        "client_name": data.get("client_name", ""),
        "project_name": data.get("project_name", ""),
        "week": data.get("week", ""),
        "report_date": data.get("report_date", ""),
        "prepared_by": data.get("prepared_by", ""),
        "overall_status": rt,
        "summary": data.get("summary", ""),
        "accomplishments": data.get("accomplishments", []),
        "in_progress": data.get("in_progress", []),
        "blockers": data.get("blockers", []),
        "upcoming": data.get("upcoming", []),
        "notes": data.get("notes", ""),
    }
    tpl.render(context)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tpl.save(out)
    print(f"Document written: {out}  (logo: {logo_path.name})")


if __name__ == "__main__":
    main()

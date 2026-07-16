"""Generate the built-in PPTX template library — professional decks a small model FILLS.

Each template is a complete, branded, 16:9 deck whose variable text is already
`{{ tagged }}`, written straight into the document-template registry together with a
hand-authored manifest (fields with examples + guidance). Template and manifest come
from the same code, so they can never drift. The fill path is the standard engine:

    python ../building-document-templates/scripts/registry.py show --client _builtin --doc-type exec_update
    python ../building-document-templates/scripts/registry.py scaffold --builtin exec_update --out content.json
    python ../building-document-templates/scripts/fill.py --client _builtin --doc-type exec_update \
        --data content.json --out out.pptx
    python ../building-document-templates/scripts/validate.py out.pptx --template <registry>/_builtin/exec_update/template.pptx

Branding is data, not code: every color, font, logo, and footer string comes from a
brand pack (see ../../brands/README.md). Re-run with a different --brand to re-skin
the whole library.

    python scripts/build_template_library.py                    # all templates, default brand
    python scripts/build_template_library.py --brand path/to/client-pack   # re-skin for a client
    python scripts/build_template_library.py --only exec_update # one template

Templates: exec_update (QBR/quarterly review), project_kickoff, proposal, report_out.
Requires python-pptx + pillow.
"""
from __future__ import annotations

import argparse
import copy
import io
import json
import os
import sys
import zipfile
from datetime import date
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_ROOT.parent
BRANDS = REPO_ROOT / "brands"
DEFAULT_REGISTRY = REPO_ROOT / "building-document-templates" / "registry"

SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.9)
CONTENT_W = SW - 2 * MARGIN


def tag(name: str) -> str:
    return "{{ " + name + " }}"


# ---------------- Brand pack ----------------

def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _deep_merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load_brand(name_or_path: str | None) -> dict:
    default = json.loads((BRANDS / "default" / "brand.json").read_text(encoding="utf-8"))
    default["_dir"] = BRANDS / "default"
    if not name_or_path or name_or_path == "default":
        return default
    p = Path(name_or_path)
    if p.suffix == ".json" and p.exists():
        pack_file, pack_dir = p, p.parent
    elif p.is_dir() and (p / "brand.json").exists():
        pack_file, pack_dir = p / "brand.json", p
    elif (BRANDS / name_or_path / "brand.json").exists():
        pack_dir = BRANDS / name_or_path
        pack_file = pack_dir / "brand.json"
    else:
        known = sorted(d.name for d in BRANDS.iterdir() if (d / "brand.json").exists())
        sys.exit(f"Unknown brand '{name_or_path}'. Available: {', '.join(known)}")
    pack = _deep_merge(default, json.loads(pack_file.read_text(encoding="utf-8")))
    pack["_dir"] = pack_dir
    return pack


def rgb(hex_str: str) -> RGBColor:
    return RGBColor.from_string(hex_str.lstrip("#"))


class Style:
    """Brand pack resolved into the handful of drawing tokens the slides use."""

    def __init__(self, brand: dict):
        c = brand["colors"]
        self.bg = rgb(c["bg"])
        self.ink = rgb(c["ink"])
        self.muted = rgb(c["muted"])
        self.accent = rgb(c["primary"])
        self.accent2 = rgb(c["accent"])
        self.dark = rgb(c["dark"])
        self.panel = rgb(c["panel"])
        self.hair = rgb(c["hairline"])
        self.light = rgb("#F5F7FA")
        self.font = brand["fonts"]["body"]
        self.font_h = brand["fonts"]["heading"]
        year = date.today().year
        f = brand.get("footer", {})
        cop = (f.get("copyright") or "").replace("{year}", str(year)) \
                                        .replace("{company}", brand.get("display_name", ""))
        conf = f.get("confidentiality", "")
        self.footer = "   ·   ".join(x for x in (cop, conf) if x)
        logo_rel = brand.get("logo")
        self.logo_bytes = (brand["_dir"] / logo_rel).read_bytes() if logo_rel else None


# ---------------- Drawing helpers ----------------

def _txt(slide, st, left, top, width, height, text, size, *, color=None, bold=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=None, spacing=1.0):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = font or st.font
    r.font.color.rgb = color if color is not None else st.ink
    return box


def _bullet_para(p, char="•"):
    """Give a paragraph a real PowerPoint bullet (survives fill.py's list expansion,
    which deep-copies the paragraph XML per item)."""
    pPr = p._p.get_or_add_pPr()
    buFont = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial", "pitchFamily": "34", "charset": "0"})
    buChar = pPr.makeelement(qn("a:buChar"), {"char": char})
    pPr.append(buFont)
    pPr.append(buChar)


def _list_box(slide, st, left, top, width, height, list_tag, size=20, color=None):
    """A textbox whose single paragraph is exactly `{{ tag }}` — fill.py clones the
    (bulleted) paragraph once per list item, giving real repeating bullets."""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.line_spacing = 1.2
    p.space_after = Pt(10)
    _bullet_para(p)
    r = p.add_run()
    r.text = list_tag
    r.font.size = Pt(size)
    r.font.name = st.font
    r.font.color.rgb = color if color is not None else st.ink
    return box


def _rect(slide, left, top, width, height, color, *, rounded=False):
    shape = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape, int(left), int(top), int(width), int(height))
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


TITLE_ONLY = 5  # layout with a real title placeholder; everything else is free


def _slide(prs, st, *, dark=False):
    s = prs.slides.add_slide(prs.slide_layouts[TITLE_ONLY])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = st.dark if dark else st.bg
    return s


def _title(slide, st, text, *, left=MARGIN, top=Inches(1.15), width=CONTENT_W,
           height=Inches(1.3), size=32, color=None, bold=True, spacing=1.05):
    ph = slide.shapes.title
    ph.left, ph.top, ph.width, ph.height = int(left), int(top), int(width), int(height)
    tf = ph.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.line_spacing = spacing
    p.text = text
    r = p.runs[0]
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = st.font_h
    r.font.color.rgb = color if color is not None else st.ink
    return ph


def _accent_bar(slide, st, top=MARGIN):
    _rect(slide, MARGIN, top, Inches(0.9), Inches(0.14), st.accent)


def _footer(slide, st, *, dark=False):
    if st.footer:
        _txt(slide, st, MARGIN, SH - Inches(0.42), CONTENT_W, Inches(0.3), st.footer, 8.5,
             color=st.light if dark else st.muted)


def _logo(slide, st, *, top=Inches(0.55), left=None, height=Inches(0.6)):
    """Logo on a white chip so it reads on light AND dark slides."""
    if not st.logo_bytes:
        return
    from PIL import Image
    img = Image.open(io.BytesIO(st.logo_bytes))
    ratio = img.width / img.height
    w = int(height * ratio)
    x = int(left) if left is not None else int(SW - MARGIN - w)
    pad = Inches(0.09)
    _rect(slide, x - pad, top - pad, w + 2 * pad, height + 2 * pad, rgb("#FFFFFF"), rounded=True)
    slide.shapes.add_picture(io.BytesIO(st.logo_bytes), x, int(top), height=int(height))


def _eyebrow(slide, st, text, top=Inches(1.7), *, color=None):
    _txt(slide, st, MARGIN, top, CONTENT_W, Inches(0.45), text, 15,
         color=color if color is not None else st.accent, bold=True)


# ---------------- Slide constructors ----------------

def title_slide(prs, st, eyebrow, title, subtitle, footnote):
    s = _slide(prs, st)
    _rect(s, 0, 0, Inches(0.28), SH, st.accent)
    _logo(s, st)
    _eyebrow(s, st, eyebrow)
    _title(s, st, title, top=Inches(2.2), height=Inches(1.9), size=42, spacing=1.0)
    _txt(s, st, MARGIN, Inches(4.25), CONTENT_W, Inches(1.0), subtitle, 22, color=st.muted)
    _txt(s, st, MARGIN, Inches(6.35), CONTENT_W, Inches(0.5), footnote, 15, color=st.muted)
    _footer(s, st)
    return s


def divider_slide(prs, st, number, heading, note):
    s = _slide(prs, st, dark=True)
    _txt(s, st, MARGIN, Inches(2.0), Inches(3.0), Inches(1.8), number, 88,
         color=st.accent2, bold=True)
    _title(s, st, heading, top=Inches(4.1), height=Inches(1.2), size=38, color=st.bg)
    _txt(s, st, MARGIN, Inches(5.4), CONTENT_W, Inches(0.9), note, 18, color=st.light)
    _footer(s, st, dark=True)
    return s


def bullets_slide(prs, st, heading, list_tag, *, intro=None, size=20):
    s = _slide(prs, st)
    _accent_bar(s, st)
    _title(s, st, heading)
    top = Inches(2.6)
    if intro:
        _txt(s, st, MARGIN, top, CONTENT_W, Inches(0.9), intro, 17, color=st.muted, spacing=1.25)
        top = Inches(3.5)
    _list_box(s, st, MARGIN, top, CONTENT_W, SH - top - Inches(0.7), list_tag, size=size)
    _footer(s, st)
    return s


def text_slide(prs, st, heading, body_tag):
    s = _slide(prs, st)
    _accent_bar(s, st)
    _title(s, st, heading)
    _txt(s, st, MARGIN, Inches(2.6), CONTENT_W, Inches(4.0), body_tag, 19,
         color=st.ink, spacing=1.35)
    _footer(s, st)
    return s


def kpi_slide(prs, st, heading, kpis):
    """kpis: list of (label_tag, value_tag, delta_tag)."""
    s = _slide(prs, st)
    _accent_bar(s, st)
    _title(s, st, heading)
    n = len(kpis)
    gap = Inches(0.3)
    w = (CONTENT_W - gap * (n - 1)) / n
    top, h = Inches(2.9), Inches(2.6)
    for i, (label, value, delta) in enumerate(kpis):
        x = MARGIN + i * (w + gap)
        _rect(s, x, top, w, h, st.panel, rounded=True)
        pad = Inches(0.25)
        _txt(s, st, x + pad, top + Inches(0.3), w - 2 * pad, Inches(0.4), label, 12,
             color=st.muted, bold=True)
        _txt(s, st, x + pad, top + Inches(0.85), w - 2 * pad, Inches(0.9), value, 30,
             color=st.ink, bold=True)
        _txt(s, st, x + pad, top + Inches(1.9), w - 2 * pad, Inches(0.45), delta, 13,
             color=st.accent)
    _footer(s, st)
    return s


def two_list_slide(prs, st, heading, left_label, left_tag, right_label, right_tag):
    s = _slide(prs, st)
    _accent_bar(s, st)
    _title(s, st, heading)
    half = (CONTENT_W - Inches(0.6)) / 2
    top = Inches(2.7)
    for label, ltag, x in ((left_label, left_tag, MARGIN),
                           (right_label, right_tag, MARGIN + half + Inches(0.6))):
        _txt(s, st, x, top, half, Inches(0.4), label, 13, color=st.accent, bold=True)
        _list_box(s, st, x, top + Inches(0.55), half, Inches(3.6), ltag, size=17)
    _footer(s, st)
    return s


def visual_slide(prs, st, heading, caption_tag, placeholder_png):
    """Image slot: the picture is swapped by fill.py through the manifest's
    image-type field (media_part). Geometry is preserved on swap."""
    s = _slide(prs, st)
    _accent_bar(s, st)
    _title(s, st, heading)
    img_top, img_h = Inches(2.55), Inches(3.7)
    s.shapes.add_picture(io.BytesIO(placeholder_png), int(MARGIN), int(img_top),
                         width=int(CONTENT_W), height=int(img_h))
    _txt(s, st, MARGIN, img_top + img_h + Inches(0.15), CONTENT_W, Inches(0.5),
         caption_tag, 14, color=st.muted)
    _footer(s, st)
    return s


def closing_slide(prs, st, eyebrow, statement_tag, list_tag):
    s = _slide(prs, st, dark=True)
    _rect(s, 0, 0, Inches(0.28), SH, st.accent)
    _logo(s, st, top=Inches(0.55))
    _eyebrow(s, st, eyebrow, top=Inches(1.4), color=st.accent2)
    _title(s, st, statement_tag, top=Inches(1.95), height=Inches(1.7), size=32, color=st.bg)
    _list_box(s, st, MARGIN, Inches(3.9), CONTENT_W, Inches(2.6), list_tag, size=19, color=st.light)
    _footer(s, st, dark=True)
    return s


# ---------------- Placeholder visual (image slot content) ----------------

def placeholder_chart_png(st) -> bytes:
    """A branded 'replace me' visual for image slots — obvious in any vision pass."""
    from PIL import Image, ImageDraw
    W, H = 1600, 480
    img = Image.new("RGB", (W, H), tuple(st.panel))
    d = ImageDraw.Draw(img)
    heights = [0.45, 0.62, 0.5, 0.74, 0.66, 0.88, 0.8]
    n = len(heights)
    bw = W // (n * 2)
    base = H - 70
    for i, hgt in enumerate(heights):
        x0 = int(W * 0.06) + i * 2 * bw
        col = tuple(st.accent) if i % 2 == 0 else tuple(st.accent2)
        d.rectangle([x0, base - int(hgt * (H - 150)), x0 + bw, base], fill=col)
    d.rectangle([0, 0, W - 1, H - 1], outline=tuple(st.muted), width=2)
    d.text((int(W * 0.06), 18), "SAMPLE VISUAL - swap via the manifest's image field "
           "(fill.py) or replace before shipping", fill=tuple(st.ink))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------- Field helper ----------------

def F(name, example, guidance, *, type="text", required=True, media_part=""):
    return {"name": name, "type": type, "example": example, "guidance": guidance,
            "required": required, "media_part": media_part}


# ---------------- Template definitions ----------------
# Examples deliberately use the fictional client "Acme Mining" and fictional people —
# they are also the manifest's source_terms, so a fill that ships the examples
# verbatim FAILS validate.py's source-residue check.

SOURCE_TERMS = ["Acme Mining", "Jane Mokoena", "Sipho Dlamini"]


def build_exec_update(prs, st, png):
    """The expandable base deck. Fixed frame (title, KPIs, divider, risks,
    closing) + two slide GROUPS the fill engine clones per content entry:
    evidence slides (optional, image slot each) and topic slides (repeatable)."""
    title_slide(prs, st, tag("report_eyebrow"), tag("report_title"),
                tag("report_subtitle"), tag("author_line"))
    kpi_slide(prs, st, tag("kpi_heading"), [
        (tag("kpi1_label"), tag("kpi1_value"), tag("kpi1_delta")),
        (tag("kpi2_label"), tag("kpi2_value"), tag("kpi2_delta")),
        (tag("kpi3_label"), tag("kpi3_value"), tag("kpi3_delta")),
        (tag("kpi4_label"), tag("kpi4_value"), tag("kpi4_delta")),
    ])
    divider_slide(prs, st, "01", tag("section_heading"), tag("section_note"))
    visual_slide(prs, st, tag("evidence_heading"), tag("evidence_caption"), png)   # group: evidence_slides
    bullets_slide(prs, st, tag("topic_heading"), tag("topic_points"))              # group: topic_slides
    two_list_slide(prs, st, tag("risks_heading"), "RISKS", tag("risks"),
                   "MITIGATIONS", tag("mitigations"))
    closing_slide(prs, st, "DECISIONS REQUESTED", tag("closing_statement"), tag("next_steps"))

    fields = [
        F("report_eyebrow", "EXECUTIVE REVIEW · Q3 2026", "Small uppercase kicker on the title slide: report kind + period."),
        F("report_title", "Q3 2026 Business Update", "The deck's title. Keep under ~8 words."),
        F("report_subtitle", "Performance against target, the drivers behind it, and the decisions we need this quarter.", "One-sentence framing under the title."),
        F("author_line", "Prepared by Finance & Operations · 15 October 2026", "Author/team and date."),
        F("kpi_heading", "The quarter at a glance", "Headline over the four KPI cards."),
        F("kpi1_label", "REVENUE", "KPI 1 label (short, uppercase)."), F("kpi1_value", "$4.82m", "KPI 1 value (big number)."), F("kpi1_delta", "▲ 9% vs Q2", "KPI 1 movement."),
        F("kpi2_label", "GROSS MARGIN", "KPI 2 label."), F("kpi2_value", "63.4%", "KPI 2 value."), F("kpi2_delta", "▲ 1.2 pts", "KPI 2 movement."),
        F("kpi3_label", "NEW CLIENTS", "KPI 3 label."), F("kpi3_value", "14", "KPI 3 value."), F("kpi3_delta", "▲ 5", "KPI 3 movement."),
        F("kpi4_label", "NPS", "KPI 4 label."), F("kpi4_value", "58", "KPI 4 value."), F("kpi4_delta", "▼ 3", "KPI 4 movement."),
        F("section_heading", "What moved the needle", "Dark section-divider heading."),
        F("section_note", "The drivers behind the quarter — and the drags.", "One muted line under the divider heading."),
        F("risks_heading", "Top risks and how we contain them", "Headline over the risks/mitigations columns."),
        F("risks", "Key-person dependency on the logistics engagement", "3–5 risk bullets, ranked.", type="list"),
        F("mitigations", "Shadow resourcing in place from October", "One mitigation per risk, same order.", type="list"),
        F("closing_statement", "Approve the Q4 plan: hire ahead of demand and fund the client-success recovery", "The single closing ask, one sentence."),
        F("next_steps", "Two senior delivery hires approved by 31 October — Jane Mokoena", "3–5 decision/next-step bullets with owners and dates.", type="list"),
    ]
    slide_groups = [
        {"name": "evidence_slides", "slide_index": 3, "min": 0, "max": 3,
         "purpose": "Evidence visuals — one chart image per slide. Omit the key (or pass []) for no visual slides at all.",
         "fields": [
             F("evidence_heading", "Revenue tracked above target from August", "Assertion headline — state the takeaway, not the chart type."),
             F("evidence_visual", "", "PNG/JPG path for this slide's chart (e.g. exported from Plotly/matplotlib at 2x). Swapped preserving geometry; omit to keep the placeholder.", type="image", required=False),
             F("evidence_caption", "Monthly revenue vs plan, $m. Source: finance close, Oct 2026.", "Small caption under the visual: units + source."),
         ]},
        {"name": "topic_slides", "slide_index": 4, "min": 1, "max": 6,
         "purpose": "One topic per slide — highlights, wins, workstream updates, lowlights. Add one entry per topic; each becomes its own slide in the same design.",
         "fields": [
             F("topic_heading", "Executive highlights", "This slide's headline — one topic, stated as a message."),
             F("topic_points", "Both flagship accounts of Acme Mining renewed multi-year", "3–6 bullets for this topic; one message each.", type="list"),
         ]},
    ]
    slides = [
        {"index": 0, "name": "Title", "purpose": "Cover — eyebrow, title, subtitle, author line."},
        {"index": 1, "name": "KPI cards", "purpose": "The quarter at a glance: exactly four KPIs (label, value, delta)."},
        {"index": 2, "name": "Section divider", "purpose": "Dark chapter break into the narrative."},
        {"index": 3, "name": "Evidence visual", "group": "evidence_slides",
         "purpose": "Assertion headline + chart image + source caption."},
        {"index": 4, "name": "Topic bullets", "group": "topic_slides",
         "purpose": "One message per slide, 3–6 bullets. Use one entry per topic — never cram two topics on one slide."},
        {"index": 5, "name": "Risks & mitigations", "purpose": "Two ranked columns, one mitigation per risk."},
        {"index": 6, "name": "Closing / decisions", "purpose": "Single closing ask + next steps with owners and dates."},
    ]
    return {"fields": fields, "slide_groups": slide_groups, "slides": slides}


def build_project_kickoff(prs, st, png):
    title_slide(prs, st, "PROJECT KICKOFF · " + tag("kickoff_date"), tag("project_name"),
                tag("project_tagline"), tag("presenter_line"))
    bullets_slide(prs, st, "Agenda", tag("agenda_items"))
    bullets_slide(prs, st, "Definition of victory", tag("dov_points"), intro=tag("dov_intro"))
    bullets_slide(prs, st, "Project deliverables", tag("deliverables"))
    bullets_slide(prs, st, "Meet the team", tag("team_members"))
    bullets_slide(prs, st, "Project approach", tag("milestones"), intro=tag("approach_note"), size=18)
    two_list_slide(prs, st, "How we stay in sync", "COMMUNICATION", tag("comms_plan"),
                   "TRACKING", tag("tracking_items"))
    bullets_slide(prs, st, tag("topic_heading"), tag("topic_points"))   # group: topic_slides
    closing_slide(prs, st, "NEXT STEPS", tag("closing_note"), tag("next_steps"))
    fields = [
        F("kickoff_date", "3 November 2026", "Kickoff meeting date."),
        F("project_name", "Haulage Transition Simulation Study", "The project's name — the big title."),
        F("project_tagline", "Simulating the fleet transition to trolley-assist across three sites.", "One sentence: what the project does."),
        F("presenter_line", "Jane Mokoena · Engagement Lead", "Presenter name and role."),
        F("agenda_items", "Project introduction and objectives", "4–7 agenda bullets in running order.", type="list"),
        F("dov_intro", "The project is a success when the client can make the transition decision with confidence.", "One sentence framing what success means."),
        F("dov_points", "A validated simulation model of current haulage operations", "3–6 'delivered when' bullets.", type="list"),
        F("deliverables", "Simulation model with baseline and transition scenarios", "The contractual deliverables, one per bullet.", type="list"),
        F("team_members", "Jane Mokoena — Engagement Lead (consultant) — 60%", "One bullet per person: Name — Role (org) — Allocation.", type="list"),
        F("approach_note", "Three sprints from data audit to scenario report, demos at each gate.", "One line summarising the delivery approach."),
        F("milestones", "Sprint 1 (Weeks 1–2) — Data audit & model scaffold — Data-readiness memo", "One bullet per milestone/sprint: name (timing) — activities — deliverable.", type="list"),
        F("comms_plan", "Weekly 30-min progress call — Thursdays 10:00", "Meeting cadences, channels, escalation path.", type="list"),
        F("tracking_items", "Shared progress tracker updated every Friday", "How progress/risks/actions are tracked.", type="list"),
        F("closing_note", "Data access and site contacts unlock sprint 1 — here's what we need this week", "One-sentence closing framing the immediate asks."),
        F("next_steps", "Data extract of 12 months' dispatch records — Sipho Dlamini — by Friday", "3–5 action bullets with owners and dates.", type="list"),
    ]
    slide_groups = [
        {"name": "topic_slides", "slide_index": 7, "min": 0, "max": 4,
         "purpose": "Extra topic slides before the close (risks, assumptions, data needs, ways of working) — one topic per slide. Omit for the standard kickoff.",
         "fields": [
             F("topic_heading", "What we need from your team", "This slide's headline — one topic."),
             F("topic_points", "A named data owner per site by week 1", "3–6 bullets for this topic.", type="list"),
         ]},
    ]
    slides = [
        {"index": 0, "name": "Title", "purpose": "Cover — project name, tagline, presenter."},
        {"index": 1, "name": "Agenda", "purpose": "4–7 items in running order."},
        {"index": 2, "name": "Definition of victory", "purpose": "What success means + 'delivered when' bullets."},
        {"index": 3, "name": "Deliverables", "purpose": "The contractual deliverables."},
        {"index": 4, "name": "Team", "purpose": "One bullet per person: name — role — allocation."},
        {"index": 5, "name": "Approach & milestones", "purpose": "Delivery approach + one bullet per sprint/milestone."},
        {"index": 6, "name": "Comms & tracking", "purpose": "Two columns: cadence/channels vs tracking."},
        {"index": 7, "name": "Extra topic", "group": "topic_slides",
         "purpose": "Optional additional topics, one per slide."},
        {"index": 8, "name": "Closing / next steps", "purpose": "Immediate asks with owners and dates."},
    ]
    return {"fields": fields, "slide_groups": slide_groups, "slides": slides}


def build_proposal(prs, st, png):
    title_slide(prs, st, "PROPOSAL · " + tag("proposal_date"), tag("proposal_title"),
                "Prepared for " + tag("client_name"), tag("author_line"))
    bullets_slide(prs, st, "Context and challenge", tag("pain_points"), intro=tag("problem_statement"))
    bullets_slide(prs, st, "Our approach", tag("approach_steps"), intro=tag("approach_summary"))
    bullets_slide(prs, st, "Scope and deliverables", tag("scope_items"))
    bullets_slide(prs, st, "The team", tag("team_members"))
    bullets_slide(prs, st, "Timeline and investment", tag("investment_lines"), intro=tag("investment_summary"), size=18)
    bullets_slide(prs, st, tag("topic_heading"), tag("topic_points"))   # group: topic_slides
    closing_slide(prs, st, "WHY US", tag("value_statement"), tag("value_points"))
    fields = [
        F("proposal_date", "20 November 2026", "Proposal date."),
        F("proposal_title", "Fleet Optimisation Study", "Short engagement title."),
        F("client_name", "Acme Mining", "The prospective client's name."),
        F("author_line", "Meridian Advisory · jane.mokoena@example.com", "Issuing team + contact."),
        F("problem_statement", "Haulage costs rose 18% while fleet utilisation fell — the operating model, not the fleet size, is the constraint.", "1–2 sentence statement of the client's problem."),
        F("pain_points", "Cycle times vary 2.3x between shifts for the same route", "3–5 evidence bullets of the pain.", type="list"),
        F("approach_summary", "A three-phase engagement: baseline the operation, simulate the options, land the change.", "One sentence on the shape of the work."),
        F("approach_steps", "Phase 1 (Weeks 1–3): data audit and baseline model", "One bullet per phase: name (timing) — what happens.", type="list"),
        F("scope_items", "Validated simulation model of the current operation", "What's in scope, one deliverable per bullet.", type="list"),
        F("team_members", "Jane Mokoena — Engagement Lead — simulation & mining ops", "One bullet per person: Name — Role — relevant expertise.", type="list"),
        F("investment_summary", "Eight weeks, three consultants, fixed fee.", "One line: duration, team size, commercial model."),
        F("investment_lines", "Phase 1 — Weeks 1–3 — $48k", "One bullet per phase or line item: phase — timing — fee.", type="list"),
        F("value_statement", "We've done this transition twelve times in mining — we start with the answer's shape, not a blank page", "The single 'why us' sentence."),
        F("value_points", "Twelve comparable engagements in the last five years", "3–5 differentiator bullets.", type="list"),
    ]
    slide_groups = [
        {"name": "topic_slides", "slide_index": 6, "min": 0, "max": 4,
         "purpose": "Extra topic slides before the close (case studies, assumptions, risks, references) — one topic per slide. Omit for the standard proposal.",
         "fields": [
             F("topic_heading", "A comparable engagement, delivered", "This slide's headline — one topic."),
             F("topic_points", "Similar scope delivered for a tier-1 operator in 2025", "3–6 bullets for this topic.", type="list"),
         ]},
    ]
    slides = [
        {"index": 0, "name": "Title", "purpose": "Cover — engagement title, client, contact."},
        {"index": 1, "name": "Context & challenge", "purpose": "Problem statement + evidence of the pain."},
        {"index": 2, "name": "Approach", "purpose": "Shape of the work + one bullet per phase."},
        {"index": 3, "name": "Scope & deliverables", "purpose": "What's in scope, one per bullet."},
        {"index": 4, "name": "Team", "purpose": "Name — role — relevant expertise."},
        {"index": 5, "name": "Timeline & investment", "purpose": "Duration, team size, fee per phase."},
        {"index": 6, "name": "Extra topic", "group": "topic_slides",
         "purpose": "Optional additional topics, one per slide."},
        {"index": 7, "name": "Closing / why us", "purpose": "The single 'why us' sentence + differentiators."},
    ]
    return {"fields": fields, "slide_groups": slide_groups, "slides": slides}


def build_report_out(prs, st, png):
    title_slide(prs, st, "PROJECT REPORT · " + tag("report_date"), tag("report_title"),
                tag("report_subtitle"), tag("author_line"))
    text_slide(prs, st, "Executive summary", tag("executive_summary"))
    divider_slide(prs, st, "01", tag("findings_heading"), tag("findings_note"))
    bullets_slide(prs, st, tag("finding_heading"), tag("finding_points"))          # group: finding_slides
    visual_slide(prs, st, tag("evidence_heading"), tag("evidence_caption"), png)   # group: evidence_slides
    bullets_slide(prs, st, "Recommendations", tag("recommendations"))
    closing_slide(prs, st, "CONCLUSION", tag("conclusion_statement"), tag("next_steps"))
    fields = [
        F("report_date", "12 December 2026", "Report-out date."),
        F("report_title", "Haulage Transition Study — Results", "Deck title."),
        F("report_subtitle", "What we found, what it means, and what to do next.", "One-sentence framing."),
        F("author_line", "Prepared for Acme Mining · Meridian Advisory", "Audience + issuing team."),
        F("executive_summary", "The study validated that a phased trolley-assist transition cuts haulage cost per tonne by 14% at current diesel prices, with payback inside 30 months. The binding constraint is substation capacity at the north pit, not fleet availability.", "3–5 sentence executive summary — findings first, then implication."),
        F("findings_heading", "What the analysis showed", "Dark divider heading for the findings chapter."),
        F("findings_note", "Three findings drive the recommendation.", "One muted line under the divider."),
        F("recommendations", "Commit to the phased transition starting north pit Q2 2027", "3–5 recommendation bullets, ranked, with owners where known.", type="list"),
        F("conclusion_statement", "The case is made — the next 90 days decide whether the savings start in 2027", "Single closing takeaway sentence."),
        F("next_steps", "Board decision on phase 1 capex — Sipho Dlamini — by 31 January", "3–5 next-step bullets with owners and dates.", type="list"),
    ]
    slide_groups = [
        {"name": "finding_slides", "slide_index": 3, "min": 1, "max": 5,
         "purpose": "One finding (or finding theme) per slide, stated as an assertion with its supporting bullets.",
         "fields": [
             F("finding_heading", "Cost per tonne falls 14% in the phased scenario", "The finding as an assertion headline."),
             F("finding_points", "Savings hold across the sensitivity range tested", "2–5 supporting bullets for this finding.", type="list"),
         ]},
        {"name": "evidence_slides", "slide_index": 4, "min": 0, "max": 3,
         "purpose": "Evidence visuals — one chart image per slide. Omit the key (or pass []) for no visual slides.",
         "fields": [
             F("evidence_heading", "Cost per tonne by scenario", "Assertion headline for this visual."),
             F("evidence_visual", "", "PNG/JPG path for this slide's chart. Swapped preserving geometry; omit to keep the placeholder.", type="image", required=False),
             F("evidence_caption", "Simulated cost per tonne, 12-month horizon. Source: study model v2.1.", "Caption: units + source."),
         ]},
    ]
    slides = [
        {"index": 0, "name": "Title", "purpose": "Cover — date, title, subtitle, audience."},
        {"index": 1, "name": "Executive summary", "purpose": "3–5 sentences: findings first, then implication."},
        {"index": 2, "name": "Section divider", "purpose": "Dark chapter break into the findings."},
        {"index": 3, "name": "Finding", "group": "finding_slides",
         "purpose": "One finding per slide — assertion headline + supporting bullets."},
        {"index": 4, "name": "Evidence visual", "group": "evidence_slides",
         "purpose": "Chart image + source caption backing the findings."},
        {"index": 5, "name": "Recommendations", "purpose": "Ranked recommendation bullets with owners."},
        {"index": 6, "name": "Closing / conclusion", "purpose": "Single takeaway + next steps with owners and dates."},
    ]
    return {"fields": fields, "slide_groups": slide_groups, "slides": slides}


TEMPLATES = {
    "exec_update": (build_exec_update, "Executive/quarterly business update (QBR): KPIs, evidence, highlights, risks, decisions."),
    "project_kickoff": (build_project_kickoff, "Project kickoff: agenda, definition of victory, deliverables, team, approach, comms."),
    "proposal": (build_proposal, "Client proposal: problem, approach, scope, team, investment, why-us."),
    "report_out": (build_report_out, "Project results report-out: executive summary, findings, evidence, recommendations."),
}


# ---------------- Build + register ----------------

def media_part_for(pptx_path: Path, image_bytes: bytes) -> str:
    """Locate the package media part holding exactly these bytes (the image slot)."""
    with zipfile.ZipFile(pptx_path) as z:
        for name in z.namelist():
            if name.startswith("ppt/media/") and z.read(name) == image_bytes:
                return name
    return ""


def build_one(name: str, brand: dict, registry: Path, owner: str, created: str) -> Path:
    builder, description = TEMPLATES[name]
    st = Style(brand)
    png = placeholder_chart_png(st)

    prs = Presentation()
    prs.slide_width = int(SW)
    prs.slide_height = int(SH)
    spec = builder(prs, st, png)
    if isinstance(spec, list):                       # older builders return just fields
        spec = {"fields": spec, "slide_groups": [], "slides": []}
    fields = spec["fields"]
    slide_groups = spec.get("slide_groups", [])
    slides_meta = spec.get("slides", [])

    dest = registry / "_builtin" / name
    dest.mkdir(parents=True, exist_ok=True)
    tpl = dest / "template.pptx"
    prs.save(str(tpl))

    # Wire image-slot fields (global AND per-group) to their package media part.
    slot = media_part_for(tpl, png)
    for f in fields + [gf for g in slide_groups for gf in g["fields"]]:
        if f["type"] == "image" and not f["media_part"]:
            f["media_part"] = slot

    manifest = {
        "template_id": f"_builtin/{name}",
        "client": "_builtin",
        "doc_type": name,
        "format": "pptx",
        "template_file": "template.pptx",
        "source_file": f"generated by building-powerpoint-decks/scripts/build_template_library.py (brand '{brand['name']}')",
        "version": "1.0.0",
        "owner": owner,
        "created": created,
        "changelog": [f"{created}: generated with brand pack '{brand['name']}'"],
        "description": description,
        "fields": fields,
        "row_groups": [],
        "slide_groups": slide_groups,
        "slides": slides_meta,
        "source_terms": SOURCE_TERMS,
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    n_slides = len(prs.slides._sldIdLst)
    n_fields = len(fields) + sum(len(g["fields"]) for g in slide_groups)
    groups_note = (" (+" + ", ".join(f"{g['name']} ×{g.get('min', 1)}–{g.get('max') or '∞'}"
                                     for g in slide_groups) + ")") if slide_groups else ""
    print(f"Registered _builtin/{name}: {n_slides} slides{groups_note}, {n_fields} fields -> {dest}")
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand", default="default", help="Brand pack name under brands/ (or a path)")
    ap.add_argument("--only", choices=sorted(TEMPLATES), help="Build a single template")
    ap.add_argument("--registry", default=os.environ.get("TEMPLATE_REGISTRY", str(DEFAULT_REGISTRY)),
                    help="Registry root (default: building-document-templates/registry or $TEMPLATE_REGISTRY)")
    ap.add_argument("--owner", default="", help="Recorded in each manifest")
    ap.add_argument("--created", default=date.today().isoformat())
    args = ap.parse_args()

    brand = load_brand(args.brand)
    registry = Path(args.registry)
    names = [args.only] if args.only else sorted(TEMPLATES)
    for name in names:
        build_one(name, brand, registry, args.owner, args.created)
    print(f"\nDiscover:  python ../building-document-templates/scripts/registry.py list")
    print(f"Fill:      scaffold -> fill.py -> validate.py -> render_pages.py (see the SKILL)")


if __name__ == "__main__":
    main()

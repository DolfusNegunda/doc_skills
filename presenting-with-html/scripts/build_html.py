"""Assemble a finished HTML deck or report from a content JSON — the fill path.

This is the presenting-with-html analog of the document-template engine's fill.py:
the author (human or model, however small) writes ONLY structured content; this
script owns the document shell — the single <head>/<style>/<script>, the HUD/TOC,
the theme system, and the entire class vocabulary. Duplicate documents, invented
CSS classes, dead nav buttons, and stale counters are structurally impossible.

Usage:
    python scripts/build_html.py --content content.json --out out.html
    python scripts/build_html.py --content content.json --out out.html --brand path/to/client-pack --inline-plotly
    python scripts/build_html.py --content content.json --validate-only   # check fields before building
    python scripts/build_html.py --list          # formats, block types, field names, brands

Content JSON (see schema/content.schema.json and examples/*.json):

    {
      "format": "deck" | "report",
      "style":  "boardroom" | "clean",       # optional preset; --style overrides
      "brand":  "default",                   # optional pack name/path; --brand overrides
      "branding": { "logo": "path", "display_name": "...", "colors": {...},
                    "footer": {...} },       # optional INLINE branding, merged over the
                                             # pack; every element collapses when absent
      "meta":   { "title": "...", "title_accent": "...", "eyebrow": "...",
                  "lead": "...", "author": "...", "date": "...",
                  "kpis": [ {"label","value","delta","down"} ] },
      "slides" | "sections": [ { "type": "...", ... }, ... ]
    }

Block types (deck + report unless noted):
    section  (deck)   {heading, note?}                          — numbered divider
    bullets           {heading, note?, items:[str|{text,sub}]}
    kpi               {heading?, note?, kpis:[{label,value,delta?,down?}]}
    cards             {heading, note?, cards:[{heading,text,big?,accent?}]}
    chart             {heading, note?, chart:{...}, body?}
    table             {heading, note?, columns:[...], rows:[[...]], body?}
    two-col           {heading, note?, left:{...}, right:{...}}  — sub-blocks:
                      text|bullets|chart|table|kpi|image (no nested two-col)
    text              {heading, note?, paragraphs:[str]}
    quote             {heading?, quote, attribution?}            — pull-quote / callout
    timeline          {heading, note?, milestones:[{label?,title,description?,done?}]}
    comparison        {heading, note?, left:{title,items}, right:{title,items}}
    image             {heading?, note?, src, alt?, caption?}     — embedded base64, self-contained
    closing           {heading, lead?, eyebrow?, cards?}

Chart spec (converted to theme-aware Plotly; restyles on theme toggle):
    {"chart_type": "bar"|"line"|"area"|"pie"|"scatter",
     "categories": [...], "series": [{"name": "...", "values": [...]}],
     "stacked": false, "y_title": "", "short": false}
    or raw passthrough: {"plotly": {"data": [...], "layout": {...}}}

The title slide (deck) / hero section (report) is generated from `meta` — it is
not a block type. After building, gate with validate_html.py and a vision pass.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"
SHELLS = ASSETS / "shells"
COMPONENTS = ASSETS / "components"
BRANDS = SKILL_ROOT.parent / "brands"

# Mirror of brands/default/brand.json so the builder works from a partial checkout
# (skill folder pulled without the repo-root brands/ directory). A named --brand
# still requires the real brands/ tree.
EMBEDDED_DEFAULT_BRAND = {
    "name": "default",
    "display_name": "Default (neutral professional)",
    "colors": {"primary": "#2563EB", "dark": "#0F172A", "accent": "#0891B2",
               "accent_2": "#7C3AED", "alert": "#DC2626", "ink": "#0F172A",
               "muted": "#54617A", "bg": "#FFFFFF", "panel": "#F1F5F9",
               "hairline": "#E2E8F0"},
    "fonts": {"heading": "Segoe UI", "body": "Segoe UI"},
    "logo": None,
    "footer": {"copyright": "", "confidentiality": ""},
    "company": {"display_name": "", "website": ""},
}

TOKEN_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")
DECK_TYPES = ("section", "bullets", "kpi", "cards", "chart", "table", "two-col", "text",
              "quote", "timeline", "comparison", "image", "closing")
REPORT_TYPES = ("bullets", "kpi", "cards", "chart", "table", "two-col", "text",
                "quote", "timeline", "comparison", "image", "closing")
SUB_TYPES = ("text", "bullets", "chart", "table", "kpi", "image")
CHART_TYPES = ("bar", "line", "area", "pie", "scatter")
STYLES = {
    "boardroom": {"default_theme": "dark",
                  "blurb": "dark-first glassmorphism — the boardroom look"},
    "clean": {"default_theme": "light",
              "blurb": "light-first flat corporate — conservative, print-oriented"},
    "executive": {"default_theme": "light",
                  "blurb": "light-first editorial serif — the annual-report look"},
}

# Exact field vocabulary per block type. Anything else is rejected with a
# suggestion — small models get ONE precise fix cycle instead of guessing
# field names across rebuilds. ("toc" is report-only but harmless on decks.)
_COMMON = {"type", "heading", "note", "toc"}
BLOCK_FIELDS = {
    "section": _COMMON,
    "bullets": _COMMON | {"items"},
    "kpi": _COMMON | {"kpis"},
    "cards": _COMMON | {"cards"},
    "chart": _COMMON | {"chart", "body"},
    "table": _COMMON | {"columns", "rows", "body"},
    "two-col": _COMMON | {"left", "right"},
    "text": _COMMON | {"paragraphs"},
    "quote": _COMMON | {"quote", "attribution"},
    "timeline": _COMMON | {"milestones"},
    "comparison": _COMMON | {"left", "right"},
    "image": _COMMON | {"src", "alt", "caption"},
    "closing": _COMMON | {"lead", "eyebrow", "cards"},
}
SUB_FIELDS = {
    "text": {"type", "heading", "paragraphs", "text"},
    "bullets": {"type", "items"},
    "chart": {"type", "chart"},
    "table": {"type", "columns", "rows"},
    "kpi": {"type", "kpis"},
    "image": {"type", "src", "alt", "caption", "heading"},
}
META_FIELDS = {"title", "title_accent", "eyebrow", "lead", "author", "date", "kpis"}
TOP_FIELDS = {"format", "style", "brand", "branding", "meta", "slides", "sections"}
ENTRY_FIELDS = {
    "kpis": {"label", "value", "delta", "down"},
    "cards": {"heading", "text", "big", "accent"},
    "milestones": {"label", "title", "description", "done"},
}
# Common wrong-name -> right-name corrections; the first candidate valid for the
# block at hand wins. Applied ONLY when the wrong name is not itself valid there.
ALIASES = {
    "title": ("heading", "label"), "header": ("heading",), "name": ("heading", "label", "title"),
    "bullets": ("items",), "points": ("items",), "list": ("items",),
    "metrics": ("kpis",), "stats": ("kpis",), "kpi": ("kpis",),
    "text": ("paragraphs",), "body_text": ("paragraphs",), "content": ("paragraphs",),
    "image": ("src",), "path": ("src",), "file": ("src",),
    "events": ("milestones",), "steps": ("milestones",),
    "subtitle": ("lead",), "description": ("note",), "date": ("label",),
}


def _key_errors(obj: dict, allowed: set, where: str) -> list[str]:
    """Reject unknown keys with a did-you-mean hint and the valid vocabulary."""
    import difflib
    errs = []
    for k in obj:
        if k in allowed:
            continue
        hint = next((c for c in ALIASES.get(k, ()) if c in allowed), None)
        if not hint:
            close = difflib.get_close_matches(k, sorted(allowed), n=1, cutoff=0.6)
            hint = close[0] if close else None
        dym = f' — did you mean "{hint}"?' if hint else ""
        errs.append(f'{where}: unknown field "{k}"{dym} (valid: '
                    + ", ".join(sorted(allowed - {"type"})) + ")")
    return errs

_partials: dict[str, str] = {}


def partial(rel: str) -> str:
    if rel not in _partials:
        _partials[rel] = (COMPONENTS / rel).read_text(encoding="utf-8").rstrip("\n")
    return _partials[rel]


def sub(template: str, mapping: dict) -> str:
    """Replace every {{ token }} present in `mapping`; unknown tokens are left
    (they surface in the final no-leftover check, i.e. a builder bug, not user error)."""
    return TOKEN_RE.sub(
        lambda m: str(mapping[m.group(1)]) if m.group(1) in mapping else m.group(0), template)


def esc(v) -> str:
    return html.escape(str(v), quote=True)


# ---------------- Safe inline mini-markup ----------------
# Prose fields may carry **bold**, *italic*, `code`, and [label](url). The value
# is FULLY escaped first, then only these four patterns are converted — so the
# only tags that can ever reach the output come from this whitelist. Unsafe URL
# schemes (javascript: etc.) are left as visible plain text.

INLINE_CODE = re.compile(r"`([^`]+)`")
INLINE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
INLINE_EM = re.compile(r"(?<!\*)\*([^*\s][^*]*)\*(?!\*)")
INLINE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
SAFE_URL = re.compile(r"^(https?://|mailto:|#)", re.I)


def rich(v) -> str:
    s = esc(v)
    s = INLINE_CODE.sub(r"<code>\1</code>", s)
    s = INLINE_BOLD.sub(r"<strong>\1</strong>", s)
    s = INLINE_EM.sub(r"<em>\1</em>", s)

    def link(m):
        label, url = m.group(1), m.group(2)
        return f'<a href="{url}">{label}</a>' if SAFE_URL.match(url) else m.group(0)

    return INLINE_LINK.sub(link, s)


# ---------------- Brand pack ----------------

def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _deep_merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load_brand(name_or_path: str | None) -> dict:
    default_file = BRANDS / "default" / "brand.json"
    if default_file.exists():
        default = json.loads(default_file.read_text(encoding="utf-8"))
        default["_dir"] = BRANDS / "default"
    else:
        # Partial checkout (skill folder without the repo-root brands/): fall back
        # to the embedded neutral defaults instead of crashing.
        default = json.loads(json.dumps(EMBEDDED_DEFAULT_BRAND))
        default["_dir"] = SKILL_ROOT
        print(f"NOTE: {default_file} not found (partial checkout?) — using embedded "
              "neutral defaults. Named brand packs need the repo-root brands/ directory; "
              "a client pack passed by PATH still works.")
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
        known = sorted(d.name for d in BRANDS.iterdir()
                       if (d / "brand.json").exists()) if BRANDS.exists() else []
        sys.exit(f"Unknown brand '{name_or_path}'. Available: {', '.join(known) or '(none — brands/ missing)'} "
                 f"(or pass a path to a brand folder / brand.json).")
    pack = _deep_merge(default, json.loads(pack_file.read_text(encoding="utf-8")))
    pack["_dir"] = pack_dir
    return pack


def apply_inline_branding(brand: dict, branding: dict | None, base_dir: Path,
                          logo_override: str | None) -> dict:
    """Merge the content JSON's optional `branding` object (and a --logo override)
    over the resolved pack. Relative logo paths resolve against the content file's
    directory. Everything is optional — absent branding keeps the pack/defaults,
    and every branding element collapses cleanly when unset."""
    if branding:
        if not isinstance(branding, dict):
            sys.exit('"branding" must be an object (logo/display_name/colors/fonts/footer/company)')
        brand = _deep_merge(brand, {k: v for k, v in branding.items() if k != "logo"})
        if branding.get("logo"):
            p = Path(branding["logo"])
            brand["logo"] = str(p if p.is_absolute() else (base_dir / p).resolve())
    if logo_override:
        brand["logo"] = str(Path(logo_override).resolve())
    return brand


# ---------------- Color math (hex in, hex/rgba out) ----------------

def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _hex(r: float, g: float, b: float) -> str:
    return "#%02X%02X%02X" % (round(r), round(g), round(b))


def mix(c1: str, c2: str, t: float) -> str:
    """t=0 -> c1, t=1 -> c2."""
    (r1, g1, b1), (r2, g2, b2) = _rgb(c1), _rgb(c2)
    return _hex(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)


def lighten(c: str, t: float) -> str:
    return mix(c, "#FFFFFF", t)


def rgba(c: str, a: float) -> str:
    r, g, b = _rgb(c)
    return f"rgba({r},{g},{b},{a})"


def shell_tokens(brand: dict, page_title: str) -> dict:
    c = brand["colors"]
    light = [c["primary"], c["accent_2"], c["accent"]]
    return {
        "page_title": esc(page_title),
        "font_body": brand["fonts"]["body"],
        "font_heading": brand["fonts"]["heading"],
        "ink": c["ink"], "muted": c["muted"],
        "light_accent_1": light[0], "light_accent_2": light[1], "light_accent_3": light[2],
        "dark_accent_1": lighten(light[0], 0.35),
        "dark_accent_2": lighten(light[1], 0.35),
        "dark_accent_3": lighten(light[2], 0.35),
        "dark_bg_0": mix(c["dark"], "#0B1020", 0.72),
        "dark_bg_1": mix(c["dark"], "#131A2E", 0.72),
        "light_bg_0": mix(c["primary"], "#EEF2F9", 0.94),
        "light_bg_1": mix(c["primary"], "#DBE4F3", 0.92),
        "dark_glow": rgba(lighten(c["primary"], 0.30), 0.18),
        "light_glow": rgba(c["primary"], 0.24),
        "glow_2": rgba(lighten(c["accent"], 0.25), 0.15),
        "alert_soft": lighten(c["alert"], 0.30),
    }


def file_data_uri(p: Path) -> str:
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "svg": "image/svg+xml", "gif": "image/gif", "webp": "image/webp"
            }.get(p.suffix.lstrip(".").lower(), "image/png")
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode('ascii')}"


def logo_data_uri(brand: dict) -> str | None:
    rel = brand.get("logo")
    if not rel:
        return None
    p = Path(rel) if Path(rel).is_absolute() else brand["_dir"] / rel
    if not p.exists():
        sys.exit(f"Brand '{brand['name']}' names a logo that does not exist: {p}")
    return file_data_uri(p)


def footer_line(brand: dict, sep: str = "  ·  ") -> str:
    year = datetime.now().year
    f = brand.get("footer", {})
    bits = []
    cop = (f.get("copyright") or "").replace("{year}", str(year)) \
                                    .replace("{company}", brand.get("display_name", ""))
    if cop:
        bits.append(cop)
    if f.get("confidentiality"):
        bits.append(f["confidentiality"])
    site = brand.get("company", {}).get("website")
    if site:
        bits.append(site)
    return esc(sep.join(bits))


# ---------------- Content validation ----------------

def validate_content(doc: dict) -> list[str]:
    errs: list[str] = []

    def need(cond, msg):
        if not cond:
            errs.append(msg)

    fmt = doc.get("format")
    need(fmt in ("deck", "report"), 'format must be "deck" or "report"')
    meta = doc.get("meta")
    need(isinstance(meta, dict) and meta.get("title"), 'meta.title is required')
    key = "slides" if fmt == "deck" else "sections"
    other = "sections" if fmt == "deck" else "slides"
    if doc.get(other) is not None:
        errs.append(f'a {fmt} uses "{key}", not "{other}"')
    blocks = doc.get(key)
    need(isinstance(blocks, list) and blocks, f'"{key}" must be a non-empty list of blocks')
    if errs:
        return errs

    errs += _key_errors(doc, TOP_FIELDS, "top level")
    errs += _key_errors(meta, META_FIELDS, "meta")
    for j, entry in enumerate(meta.get("kpis") or []):
        if isinstance(entry, dict):
            errs += _key_errors(entry, ENTRY_FIELDS["kpis"], f"meta.kpis[{j}]")

    allowed = DECK_TYPES if fmt == "deck" else REPORT_TYPES
    for i, b in enumerate(blocks):
        where = f"{key}[{i}]"
        if not isinstance(b, dict) or b.get("type") not in allowed:
            errs.append(f"{where}: type must be one of {', '.join(allowed)} "
                        f"(got {b.get('type') if isinstance(b, dict) else type(b).__name__!r})")
            continue
        t = b["type"]
        errs += _key_errors(b, BLOCK_FIELDS[t], f"{where} ({t})")
        for group, fields in ENTRY_FIELDS.items():
            for j, entry in enumerate(b.get(group) or []):
                if isinstance(entry, dict):
                    errs += _key_errors(entry, fields, f"{where}: {group}[{j}]")
        if t in ("section", "bullets", "cards", "chart", "table", "two-col", "text",
                 "timeline", "comparison", "closing"):
            if not b.get("heading"):
                errs.append(f"{where} ({t}): heading is required")
        if t == "bullets":
            if not b.get("items"):
                errs.append(f"{where}: items is required")
            for j, it in enumerate(b.get("items") or []):
                if isinstance(it, dict):
                    errs += _key_errors(it, {"text", "sub"}, f"{where}: items[{j}]")
        if t == "kpi" and not b.get("kpis"):
            errs.append(f"{where}: kpis is required")
        if t == "cards" and not b.get("cards"):
            errs.append(f"{where}: cards is required")
        if t == "chart":
            errs += chart_errors(b.get("chart"), where)
        if t == "table":
            cols, rows = b.get("columns"), b.get("rows")
            if not cols or not isinstance(rows, list) or not rows:
                errs.append(f"{where}: columns and rows are required")
            else:
                for j, r in enumerate(rows):
                    if not isinstance(r, list) or len(r) != len(cols):
                        errs.append(f"{where}: rows[{j}] must have {len(cols)} cells to match columns")
        if t == "two-col":
            for side in ("left", "right"):
                s = b.get(side)
                if not isinstance(s, dict) or s.get("type") not in SUB_TYPES:
                    errs.append(f"{where}.{side}: a sub-block with type in {', '.join(SUB_TYPES)} is required")
                else:
                    errs += _key_errors(s, SUB_FIELDS[s["type"]], f"{where}.{side} ({s['type']})")
                    if s["type"] == "chart":
                        errs += chart_errors(s.get("chart"), f"{where}.{side}")
        if t == "text" and not b.get("paragraphs"):
            errs.append(f"{where}: paragraphs is required")
        if t == "quote" and not b.get("quote"):
            errs.append(f"{where}: quote text is required")
        if t == "timeline":
            ms = b.get("milestones")
            if not isinstance(ms, list) or not ms:
                errs.append(f"{where}: milestones must be a non-empty list of "
                            "{label?, title, description?, done?}")
            else:
                for j, m in enumerate(ms):
                    if not isinstance(m, dict) or not m.get("title"):
                        errs.append(f"{where}: milestones[{j}] needs at least a title")
        if t == "comparison":
            for side in ("left", "right"):
                s = b.get(side)
                if (not isinstance(s, dict) or not s.get("title")
                        or not isinstance(s.get("items"), list) or not s["items"]):
                    errs.append(f"{where}.{side}: needs {{title, items:[...]}}")
        if t == "image" and not b.get("src"):
            errs.append(f"{where}: src (path to a png/jpg/svg) is required")

    # `{{` in content collides with the template-token syntax the validator polices.
    flat = json.dumps(doc)
    if "{{" in flat:
        errs.append('content values must not contain "{{" (reserved template syntax)')
    return errs


def chart_errors(spec, where: str) -> list[str]:
    if not isinstance(spec, dict):
        return [f"{where}: chart spec object is required"]
    if "plotly" in spec:
        p = spec["plotly"]
        if not isinstance(p, dict) or not isinstance(p.get("data"), list):
            return [f"{where}: chart.plotly must be {{data:[...], layout:{{...}}}}"]
        return []
    errs = []
    if spec.get("chart_type") not in CHART_TYPES:
        errs.append(f"{where}: chart_type must be one of {', '.join(CHART_TYPES)}")
    if not isinstance(spec.get("categories"), list) or not spec.get("categories"):
        errs.append(f"{where}: chart.categories must be a non-empty list")
    series = spec.get("series")
    if not isinstance(series, list) or not series:
        errs.append(f"{where}: chart.series must be a non-empty list of {{name, values}}")
    else:
        n = len(spec.get("categories") or [])
        for j, s in enumerate(series):
            if not isinstance(s, dict) or "name" not in s or not isinstance(s.get("values"), list):
                errs.append(f"{where}: chart.series[{j}] must be {{name, values}}")
            elif n and len(s["values"]) != n:
                errs.append(f"{where}: chart.series[{j}].values must have {n} items to match categories")
    return errs


# ---------------- Rendering ----------------

class ChartBook:
    """Collects chart specs during rendering; emits the registerChart JS calls."""

    def __init__(self):
        self.specs: list[dict] = []

    def add(self, spec: dict) -> str:
        self.specs.append(spec)
        return f"c{len(self.specs) - 1}"

    def to_js(self) -> str:
        return "\n".join(chart_js(f"c{i}", s) for i, s in enumerate(self.specs))


def chart_js(cid: str, spec: dict) -> str:
    if "plotly" in spec:
        data = json.dumps(spec["plotly"]["data"])
        layout = json.dumps(spec["plotly"].get("layout", {}))
        return (f"  registerChart('[data-chart=\"{cid}\"]', t => ({data}), {layout});")
    ctype = spec["chart_type"]
    cats = json.dumps(spec["categories"])
    extra = {}
    if spec.get("stacked") and ctype in ("bar", "area"):
        extra["barmode"] = "stack"
    if spec.get("y_title"):
        extra["yaxis"] = {"title": {"text": spec["y_title"]}}
    traces = []
    if ctype == "pie":
        values = json.dumps(spec["series"][0]["values"])
        n = len(spec["categories"])
        colors = ", ".join(f"t.accents[{i % 3}]" for i in range(n))
        traces.append("{ type: 'pie', labels: " + cats + ", values: " + values +
                      ", hole: .45, textinfo: 'label+percent', marker: { colors: [" + colors + "] } }")
    else:
        for i, s in enumerate(spec["series"]):
            name = json.dumps(str(s["name"]))
            vals = json.dumps(s["values"])
            col = f"t.accents[{i % 3}]"
            if ctype == "bar":
                traces.append("{ type: 'bar', name: " + name + ", x: " + cats + ", y: " + vals +
                              ", marker: { color: " + col + " } }")
            elif ctype == "line":
                traces.append("{ type: 'scatter', mode: 'lines+markers', name: " + name +
                              ", x: " + cats + ", y: " + vals +
                              ", line: { color: " + col + ", width: 3 }, marker: { color: " + col + " } }")
            elif ctype == "area":
                stack = ", stackgroup: 'a'" if spec.get("stacked") else ""
                traces.append("{ type: 'scatter', mode: 'lines', fill: 'tozeroy', name: " + name +
                              ", x: " + cats + ", y: " + vals +
                              ", line: { color: " + col + ", width: 2 }" + stack + " }")
            else:  # scatter
                traces.append("{ type: 'scatter', mode: 'markers', name: " + name +
                              ", x: " + cats + ", y: " + vals +
                              ", marker: { color: " + col + ", size: 9 } }")
    joined = ",\n    ".join(traces)
    extra_js = ", " + json.dumps(extra) if extra else ""
    return (f"  registerChart('[data-chart=\"{cid}\"]', t => ([\n    {joined}\n  ]){extra_js});")


def kpi_row(kpis: list, margin: bool = True) -> str:
    cards = []
    for k in kpis:
        delta = ""
        if k.get("delta"):
            down = " down" if k.get("down") else ""
            delta = f'<div class="delta{down}">{esc(k["delta"])}</div>'
        cards.append(sub(partial("shared/kpi_card.html"),
                         {"label": esc(k.get("label", "")), "value": esc(k.get("value", "")),
                          "delta": delta}))
    n = len(kpis)
    cols = " cols-2" if n == 2 else (" cols-3" if n == 3 else "")
    style = "" if margin else ' style="margin-top:16px"'
    return f'<div class="kpi-row{cols}"{style}>' + "".join(cards) + "</div>"


def cards_grid(cards: list) -> str:
    out = []
    for c in cards:
        big = ""
        if c.get("big") is not None:
            accent = " accent" if c.get("accent") else ""
            big = f'<div class="big{accent}">{esc(c["big"])}</div>'
        out.append(sub(partial("shared/card.html"),
                       {"heading": esc(c.get("heading", "")), "text": rich(c.get("text", "")), "big": big}))
    return '<div class="grid">' + "\n".join(out) + "</div>"


def bullets_list(items: list) -> str:
    lis = []
    for it in items:
        if isinstance(it, dict):
            s = f'<div class="sub">{rich(it["sub"])}</div>' if it.get("sub") else ""
            lis.append(f"<li>{rich(it.get('text', ''))}{s}</li>")
        else:
            lis.append(f"<li>{rich(it)}</li>")
    return '<ul class="bullets">' + "\n".join(lis) + "</ul>"


def table_html(columns: list, rows: list) -> str:
    header = "".join(f"<th>{esc(c)}</th>" for c in columns)
    body = "\n".join("<tr>" + "".join(f"<td>{rich(v)}</td>" for v in r) + "</tr>" for r in rows)
    return sub(partial("shared/table.html"), {"header_cells": header, "rows": body})


def chart_panel(spec: dict, charts: ChartBook, short: bool = False) -> str:
    cid = charts.add(spec)
    is_short = short or bool(spec.get("short"))
    return sub(partial("shared/chart.html"), {"chart_id": cid, "short": " short" if is_short else ""})


def heading_html(block: dict) -> str:
    note = f'<p class="section-note">{rich(block["note"])}</p>' if block.get("note") else ""
    return sub(partial("shared/heading.html"), {"heading": esc(block.get("heading", "")), "note": note})


def figure_html(block: dict, base_dir: Path) -> str:
    p = Path(block["src"])
    p = p if p.is_absolute() else (base_dir / p)
    if not p.exists():
        sys.exit(f"image block: file not found: {p} (paths resolve relative to the content JSON)")
    size = p.stat().st_size
    if size > 2_500_000:
        print(f"WARNING: {p.name} is {size / 1e6:.1f} MB and gets embedded base64 — "
              "resize/compress it for a lean deliverable.")
    caption = (f'<figcaption class="figure-caption">{esc(block["caption"])}</figcaption>'
               if block.get("caption") else "")
    alt = block.get("alt") or block.get("caption") or block.get("heading") or "figure"
    return sub(partial("shared/figure.html"),
               {"src": file_data_uri(p), "alt": esc(alt), "caption": caption})


def timeline_html(milestones: list) -> str:
    items = []
    for m in milestones:
        done = " done" if m.get("done") else ""
        label = f'<div class="tl-label">{esc(m["label"])}</div>' if m.get("label") else ""
        body = f'<div class="tl-body">{rich(m["description"])}</div>' if m.get("description") else ""
        items.append(f'<div class="tl-item{done}">{label}'
                     f'<div class="tl-title">{esc(m["title"])}</div>{body}</div>')
    return sub(partial("shared/timeline.html"), {"items": "\n".join(items)})


def compare_html(block: dict) -> str:
    def lis(side):
        return "\n".join(f"<li>{rich(i)}</li>" for i in side["items"])
    return sub(partial("shared/compare.html"), {
        "left_title": esc(block["left"]["title"]), "left_items": lis(block["left"]),
        "right_title": esc(block["right"]["title"]), "right_items": lis(block["right"]),
    })


def quote_html(block: dict) -> str:
    attr = (f'<div class="quote-attr">— {esc(block["attribution"])}</div>'
            if block.get("attribution") else "")
    return sub(partial("shared/quote.html"),
               {"quote": rich(block["quote"]), "attribution": attr})


def sub_block(spec: dict, charts: ChartBook, base_dir: Path) -> str:
    t = spec["type"]
    if t == "text":
        h = f"<h3>{esc(spec['heading'])}</h3>" if spec.get("heading") else ""
        paras = spec.get("paragraphs") or ([spec["text"]] if spec.get("text") else [])
        body = "".join(f"<p>{rich(p)}</p>" for p in paras)
        return f'<div class="card">{h}{body}</div>'
    if t == "bullets":
        return bullets_list(spec.get("items", []))
    if t == "chart":
        return chart_panel(spec["chart"], charts, short=True)
    if t == "table":
        return table_html(spec.get("columns", []), spec.get("rows", []))
    if t == "kpi":
        return kpi_row(spec.get("kpis", []), margin=False)
    if t == "image":
        return figure_html(spec, base_dir)
    raise ValueError(f"unsupported sub-block type {t!r}")


def block_body(block: dict, charts: ChartBook, base_dir: Path) -> str:
    """The inner content of a body block — shared verbatim by deck slides and
    report sections so both formats stay one design system."""
    t = block["type"]
    parts = [heading_html(block)] if (block.get("heading") or block.get("note")) else []
    if t == "bullets":
        parts.append(bullets_list(block["items"]))
    elif t == "kpi":
        parts.append(kpi_row(block["kpis"]))
    elif t == "cards":
        parts.append(cards_grid(block["cards"]))
    elif t == "chart":
        parts.append(chart_panel(block["chart"], charts))
        if block.get("body"):
            parts.append(f'<p class="body">{rich(block["body"])}</p>')
    elif t == "table":
        parts.append(table_html(block["columns"], block["rows"]))
        if block.get("body"):
            parts.append(f'<p class="body">{rich(block["body"])}</p>')
    elif t == "two-col":
        left = sub_block(block["left"], charts, base_dir)
        right = sub_block(block["right"], charts, base_dir)
        parts.append(f'<div class="two-col">\n<div>{left}</div>\n<div>{right}</div>\n</div>')
    elif t == "text":
        parts.append("".join(f'<p class="body">{rich(p)}</p>' for p in block["paragraphs"]))
    elif t == "quote":
        parts.append(quote_html(block))
    elif t == "timeline":
        parts.append(timeline_html(block["milestones"]))
    elif t == "comparison":
        parts.append(compare_html(block))
    elif t == "image":
        parts.append(figure_html(block, base_dir))
    else:
        raise ValueError(f"unhandled block type {t!r}")
    return "\n".join(parts)


def title_html_for(meta: dict) -> str:
    title = str(meta["title"])
    accent = meta.get("title_accent")
    if accent and accent in title:
        pre, _, post = title.partition(accent)
        return f'{esc(pre)}<span class="accent">{esc(accent)}</span>{esc(post)}'
    return esc(title)


def byline(meta: dict) -> str:
    bits = [meta[k] for k in ("author", "date") if meta.get(k)]
    return esc("  ·  ".join(str(b) for b in bits))


def slugify(text: str, used: set) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "section"
    base, i = s, 2
    while s in used:
        s, i = f"{base}-{i}", i + 1
    used.add(s)
    return s


def style_tokens(style: str) -> dict:
    css = ""
    if style != "boardroom":
        css = (ASSETS / "styles" / f"{style}.css").read_text(encoding="utf-8").rstrip() + "\n"
    return {"style_name": style,
            "default_theme": STYLES[style]["default_theme"],
            "style_css": css}


def build_deck(doc: dict, brand: dict, style: str, base_dir: Path) -> str:
    meta = doc["meta"]
    charts = ChartBook()
    slides = []

    extras = kpi_row(meta["kpis"]) if meta.get("kpis") else ""
    foot = byline(meta)
    slides.append(sub(partial("deck/title.html"), {
        "active": " active",
        "eyebrow": esc(meta.get("eyebrow", "")),
        "title_html": title_html_for(meta),
        "lead": rich(meta.get("lead", "")),
        "extras": extras,
        "footnote": f'<p class="footnote">{foot}</p>' if foot else "",
    }))

    section_no = 0
    for block in doc["slides"]:
        t = block["type"]
        if t == "section":
            section_no += 1
            slides.append(sub(partial("deck/section.html"), {
                "active": "",
                "number": f"{section_no:02d}",
                "heading": esc(block["heading"]),
                "note": esc(block.get("note", "")),
            }))
        elif t == "closing":
            extras = cards_grid(block["cards"]) if block.get("cards") else ""
            foot = footer_line(brand)
            slides.append(sub(partial("deck/closing.html"), {
                "active": "",
                "eyebrow": esc(block.get("eyebrow", "Next steps")),
                "heading": esc(block["heading"]),
                "lead": rich(block.get("lead", "")),
                "extras": extras,
                "footnote": f'<p class="footnote">{foot}</p>' if foot else "",
            }))
        else:
            slides.append(sub(partial("deck/slide.html"),
                              {"active": "", "body": block_body(block, charts, base_dir)}))

    logo = logo_data_uri(brand)
    mark = (f'<div class="brand-mark"><img src="{logo}" '
            f'alt="{esc(brand.get("display_name", "brand"))} logo"></div>') if logo else ""
    conf = brand.get("footer", {}).get("confidentiality", "")
    tokens = shell_tokens(brand, str(meta["title"]))
    tokens.update({
        "brand_mark": mark,
        "slides": "\n".join(slides),
        "confidential": f'<div class="confidential">{esc(conf)}</div>' if conf else "",
        "charts_js": charts.to_js(),
    })
    tokens.update(style_tokens(style))
    return sub((SHELLS / "deck.html").read_text(encoding="utf-8"), tokens)


def build_report(doc: dict, brand: dict, style: str, base_dir: Path) -> str:
    meta = doc["meta"]
    charts = ChartBook()
    used_ids: set = set()
    sections = []

    logo = logo_data_uri(brand)
    hero_logo = (f'<div class="hero-logo"><img src="{logo}" '
                 f'alt="{esc(brand.get("display_name", "brand"))} logo"></div>') if logo else ""
    extras = kpi_row(meta["kpis"]) if meta.get("kpis") else ""
    foot = byline(meta)
    used_ids.add("overview")
    sections.append(sub(partial("report/hero.html"), {
        "id": "overview", "toc": "Overview",
        "logo": hero_logo,
        "eyebrow": esc(meta.get("eyebrow", "")),
        "title_html": title_html_for(meta),
        "lead": rich(meta.get("lead", "")),
        "extras": extras,
        "footnote": f'<p class="footnote">{foot}</p>' if foot else "",
    }))

    for block in doc["sections"]:
        t = block["type"]
        if t == "closing":
            body_parts = [f'<div class="eyebrow">{esc(block.get("eyebrow", "Next steps"))}</div>',
                          f"<h2>{esc(block['heading'])}</h2>"]
            if block.get("lead"):
                body_parts.append(f'<p class="lead">{rich(block["lead"])}</p>')
            if block.get("cards"):
                body_parts.append(cards_grid(block["cards"]))
            body = "\n".join(body_parts)
        else:
            body = block_body(block, charts, base_dir)
        sec_id = slugify(block.get("heading", t), used_ids)
        sections.append(sub(partial("report/section.html"), {
            "id": sec_id,
            "toc": esc(block.get("toc") or block.get("heading")
                       or t.replace("-", " ").capitalize()),
            "body": body,
        }))

    tokens = shell_tokens(brand, str(meta["title"]))
    tokens.update({
        "sections": "\n".join(sections),
        "report_footer": footer_line(brand),
        "charts_js": charts.to_js(),
    })
    tokens.update(style_tokens(style))
    return sub((SHELLS / "report.html").read_text(encoding="utf-8"), tokens)


# ---------------- CLI ----------------

REQUIRED_FIELDS = {
    "section": "heading", "bullets": "heading, items", "kpi": "kpis",
    "cards": "heading, cards", "chart": "heading, chart", "table": "heading, columns, rows",
    "two-col": "heading, left, right", "text": "heading, paragraphs", "quote": "quote",
    "timeline": "heading, milestones", "comparison": "heading, left+right {title, items}",
    "image": "src", "closing": "heading",
}


def scaffold_doc(fmt: str) -> dict:
    """A ready-to-edit skeleton — replace every value, delete blocks you don't
    need, duplicate ones you need more of. Cheaper to fill than reading examples."""
    kpi = {"label": "", "value": "", "delta": ""}
    blocks = [
        {"type": "bullets", "heading": "", "note": "", "items": ["", "", ""]},
        {"type": "kpi", "heading": "", "kpis": [dict(kpi), dict(kpi), dict(kpi)]},
        {"type": "chart", "heading": "", "note": "",
         "chart": {"chart_type": "bar", "categories": ["", ""],
                   "series": [{"name": "", "values": [0, 0]}]}},
        {"type": "table", "heading": "", "columns": ["", ""], "rows": [["", ""]]},
        {"type": "timeline", "heading": "",
         "milestones": [{"label": "", "title": "", "description": ""}]},
        {"type": "closing", "heading": "", "lead": "",
         "cards": [{"heading": "", "text": ""}]},
    ]
    if fmt == "deck":
        blocks.insert(0, {"type": "section", "heading": "", "note": ""})
    else:
        blocks.insert(0, {"type": "text", "heading": "", "paragraphs": ["", ""]})
    return {
        "format": fmt,
        "style": "boardroom",
        "meta": {"title": "", "title_accent": "", "eyebrow": "", "lead": "",
                 "author": "", "date": "", "kpis": [dict(kpi), dict(kpi), dict(kpi)]},
        ("slides" if fmt == "deck" else "sections"): blocks,
    }


def missing_assets() -> list[str]:
    """The files the builder assembles from. Missing ones mean a partial checkout —
    the fix is fetching the whole skill folder, never editing this script."""
    required = [SHELLS / "deck.html", SHELLS / "report.html",
                COMPONENTS / "shared", COMPONENTS / "deck", COMPONENTS / "report",
                ASSETS / "styles" / "clean.css"]
    return [str(p.relative_to(SKILL_ROOT)) for p in required if not p.exists()]


def list_catalog() -> None:
    brands = sorted(d.name for d in BRANDS.iterdir() if (d / "brand.json").exists()) \
        if BRANDS.exists() else []
    print("Formats:")
    print("  deck    — full-screen slides, arrow/dot navigation (presented live)")
    print("  report  — long-form scrolling document, sticky TOC, print-ready")
    print("\nStyles:")
    for name, meta in STYLES.items():
        print(f"  {name:10} — {meta['blurb']}")
    print(f"\nDeck block types:   title(auto from meta), {', '.join(DECK_TYPES)}")
    print(f"Report block types: hero(auto from meta), {', '.join(REPORT_TYPES)}")
    print("\nBlock fields (exact names — anything else is rejected with a suggestion):")
    for t in BLOCK_FIELDS:
        optional = sorted(BLOCK_FIELDS[t] - {"type"}
                          - set(re.split(r"[,+ ]+", REQUIRED_FIELDS[t].replace("{title, items}", ""))))
        print(f"  {t:11} required: {REQUIRED_FIELDS[t]:35} optional: {', '.join(optional)}")
    print("  kpis entries: {label, value, delta?, down?}   cards entries: {heading, text, big?, accent?}")
    print("  milestones entries: {title, label?, description?, done?}   bullet items: str or {text, sub?}")
    print(f"Two-col sub-blocks: {', '.join(SUB_TYPES)}")
    print(f"Chart types:        {', '.join(CHART_TYPES)}  (or raw {{plotly:{{data,layout}}}})")
    print(f"\nBrand packs: {', '.join(brands) or '(none found)'}  "
          "(client packs: pass a path; inline: a 'branding' object in the content JSON or --logo)")
    print(f"\nExamples: {SKILL_ROOT / 'examples'}")
    print("Build:    python scripts/build_html.py --content content.json --out out.html "
          "[--style clean] [--brand <name-or-path>] [--logo logo.png]")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--content", help="Path to the content JSON")
    ap.add_argument("--out", help="Output .html path")
    ap.add_argument("--brand", default=None,
                    help="Brand pack name (brands/<name>/) or path; overrides content.json's")
    ap.add_argument("--style", default=None, choices=sorted(STYLES),
                    help="Style preset (default: content.json's 'style', else 'boardroom')")
    ap.add_argument("--logo", default=None,
                    help="Logo image path — overrides pack/inline branding; omit for no logo")
    ap.add_argument("--inline-plotly", action="store_true",
                    help="Fold the Plotly library into the file (self-contained delivery)")
    ap.add_argument("--validate-only", action="store_true",
                    help="Check the content JSON (fields, types, chart specs) without building")
    ap.add_argument("--scaffold", choices=("deck", "report"),
                    help="Emit a skeleton content JSON to edit (with --out, writes the file)")
    ap.add_argument("--list", action="store_true", help="Show formats, block types, and brands")
    args = ap.parse_args()

    if args.list:
        list_catalog()
        return
    if args.scaffold:
        text = json.dumps(scaffold_doc(args.scaffold), indent=2, ensure_ascii=False)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
            print(f"Scaffold written to {args.out} — fill every value, delete unused blocks, "
                  "duplicate blocks you need more of (--list shows all types). Prose fields "
                  "accept **bold**, *italic*, `code`, [label](https://url). Then check with "
                  f"--content {args.out} --validate-only.")
        else:
            print(text)
        return
    if not args.content or (not args.out and not args.validate_only):
        ap.error("--content and --out are required (or --validate-only / --list)")

    content_path = Path(args.content)
    if not content_path.exists():
        sys.exit(f"content file not found: {content_path}")
    try:
        doc = json.loads(content_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{content_path} is not valid JSON: {e}")

    errors = validate_content(doc)
    if errors:
        print(f"Content validation FAILED ({len(errors)} problem(s)):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(2)
    if args.validate_only:
        n_blocks = len(doc.get("slides") or doc.get("sections") or [])
        print(f"Content OK: {doc['format']} '{doc['meta']['title']}', {n_blocks} blocks "
              f"({', '.join(sorted({b['type'] for b in (doc.get('slides') or doc.get('sections'))}))})")
        return

    missing = missing_assets()
    if missing:
        sys.exit("Builder assets missing (incomplete checkout): " + ", ".join(missing) + "\n"
                 "Fetch the WHOLE presenting-with-html folder (scripts/, assets/, schema/, "
                 "examples/). Do NOT edit this script or improvise the missing files — "
                 "the shells/components define the verified class vocabulary.")

    style = args.style or doc.get("style") or "boardroom"
    if style not in STYLES:
        sys.exit(f"Unknown style {style!r}. Available: {', '.join(sorted(STYLES))}")
    brand = load_brand(args.brand or doc.get("brand"))
    brand = apply_inline_branding(brand, doc.get("branding"), content_path.parent.resolve(),
                                  args.logo)
    base_dir = content_path.parent.resolve()
    html_out = (build_deck(doc, brand, style, base_dir) if doc["format"] == "deck"
                else build_report(doc, brand, style, base_dir))

    # Belt-and-braces: the builder must never emit template syntax.
    leftover = sorted(set(TOKEN_RE.findall(html_out)))
    if leftover:
        sys.exit(f"internal error: unresolved shell tokens {leftover} — report this as a bug")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_out, encoding="utf-8")
    n_blocks = len(doc.get("slides") or doc.get("sections") or [])
    print(f"Built {doc['format']} '{doc['meta']['title']}' -> {out} "
          f"({n_blocks} content blocks + auto title/hero, style '{style}', brand '{brand['name']}')")

    if args.inline_plotly:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            import vendor_plotly
        except ImportError:
            print("WARNING: scripts/vendor_plotly.py is missing (partial checkout) — the file "
                  "was built and works, but loads Plotly from the pinned CDN. Restore the full "
                  "skill folder and re-run with --inline-plotly before offline delivery.")
        else:
            vendor_plotly.inline(out, None)
    else:
        print("NOTE: Plotly loads from the CDN. Before delivery run "
              f"`python scripts/build_html.py --content {content_path} --out {out} --inline-plotly` "
              "or `python scripts/vendor_plotly.py --inline <file>`.")

    print("Next: python scripts/validate_html.py " + str(out) + "  (then a vision pass in both themes)")


if __name__ == "__main__":
    main()

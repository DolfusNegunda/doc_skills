# Test-run evidence — document-template suite

Validated on 2026-07-13 against the real client files in `docs.zip`
(`C:\Users\DolfusNegunda\Downloads\docs`). These runs de-risk the approach the
[AGENT-PROMPT.md](AGENT-PROMPT.md) tells the implementing agent to build on.

## Environment fact (important)
- **LibreOffice / `soffice` is NOT installed** on this machine, and `pdftoppm` is absent.
- **Microsoft Office COM works** (Word 16.0, PowerPoint 16.0 via PowerShell).
- Python has `python-docx`, `python-pptx`, `PyMuPDF` (`fitz`).
- Proven vision loop: **Office COM → PDF → PyMuPDF → PNG → Read**. Baked into
  `office/building-document-templates/scripts/render_pages.py` (LibreOffice first,
  Office COM fallback on Windows).

## Runs (all end-to-end: render → understand → templatize → fill → validate → vision-QA)

| # | Source file | Format | Result |
|---|---|---|---|
| 1 | `Templates starter/RI1949 Lessons Learned.docx` | docx, 8 pp | Header + team table injected; **cover initially stayed stale** (see below); fixed; validate `OK` |
| 2 | `Templates starter/KM Logistics Study - Scope of Work - V2.pptx` | pptx, 33 sl | Title/revision injected; background image + Albemarle/BSC logos preserved; validate `OK` |
| 3 | `Templates starter/KM Logistics Study - Analysis Sprint 2 - Preliminary Results.pptx` | pptx, 25 sl | Title + deliverable subtitle injected; same template family as #2 (repeatability); validate `OK` |

Fills used a *different* fictional project each time (e.g. `RI.2027` /
"Globex Port Throughput Study", "Nevada Lithium Brine Logistics Study") to prove reuse,
not edit-in-place.

## The key finding — why vision QA is a required gate
On run #1, filling `project_code` `RI.1949 → RI.2027` updated the metadata table and the
team table, **but the cover stayed `RI.1949`** — and `validate.py` (text-only) still
reported `"status": "OK"`. **Only the page-by-page vision pass caught it.**

Root cause: the cover is a Word **cover-page building block** whose content controls are
**data-bound** to package properties — `docProps/core.xml` `dc:title` and a
`customXml` `CoverPageProperties/PublishDate` — not to body text. The run-based engine
never reached them.

## Engine fix already landed (in `office/building-document-templates/`)
The same `{{ tag }}` machinery now flows through those property parts
(`common.py`: `iter_property_leaves`, `patch_property_parts`, `ordered_replacer`;
wired into `templatize.py` propose+build, `fill.py`, `validate.py`). Re-run proved the
cover code **and** date update with all branding preserved; `validate.py` `OK`;
**27/27 repo smoke checks still pass** (no regression). `render_pages.py` added for the
vision passes.

## Image/logo swap — IMPLEMENTED and PROVEN for BOTH formats (2026-07-13)
Implemented as image SLOTS in the engine (`common.iter_image_slots` +
`common.swap_media_parts`, wired through propose/build/fill). Proven end-to-end **through
the engine path** (propose → build → fill → render → Read):
- **PPTX**: the Albemarle cover logo → replacement "ACME CORP" box, exact position/size,
  BSC logo + title + background untouched.
- **DOCX**: the cover BSC logo → replacement box, geometry preserved, Albemarle untouched.
Mechanism: re-encode the supplied asset to the slot's **original format** (Pillow) and
overwrite the media-part bytes; every reference and the shape geometry are preserved.
(An initial manual pptx spike used relationship-retarget — also valid — but the shipped
engine uses media-byte replacement, which swaps a reused logo everywhere in one go.)
Observed real defects the **vision pass** catches that text validation never would: a dark
replacement background made overlaid title text low-contrast; heuristic slot names can
mislabel a wide logo as a "background".

## Test coverage added
Smoke suite went 27 → **32/32**: three checks for the property/cover pass (propose surfaces
a `docProps/core.xml` candidate → build injects the tag → fill replaces it) and two for
image slots (propose surfaces an image slot → fill swaps the media bytes). Previously the
property and image code had zero automated coverage.

## Still open (the agent implements — see AGENT-PROMPT.md)
- Image-slot **refinements**: better slot identification (show the user a cropped render of
  each slot; map media part → slides), aspect-distortion warning, text-contrast check.
- Word **field codes** with cached results and **text boxes** (`w:txbxContent`).
- Image-slot refinements (see above); Word field codes / text boxes.

The four-skill new repo was built and self-validated across the `docs.zip` folder groups;
`presenting-with-html` is fully built from the user's design pattern (boilerplate +
validator + design system, verified in a headless browser), not a stub.

## docs.zip folder groups (each folder = a document TYPE; each file = a client/version)
```
docs/change note/       3 × .docx   (Advanced Trolley Assist, Anglo Haulage, KMC Simulation)
docs/lessons learned/   3 × .docx   (RI1819/1839, RI1935, RI1949)
docs/Project Kickoff/   3 × .pptx   (Anglo Haulage, DPMM Fragmentation, Proudfoot Alex AI)
docs/Project signoff/   3 × .docx   (DPM BlastAnalyser, KM Logistics, RI1839)
docs/Templates starter/ 2 × .pptx + 1 × .docx  (the three validated above)
```
Study the *repetition within each folder*: what is boilerplate (same every file =
`fixed`) vs. what changes per project (= `variable`/`list`). That is exactly the
fixed/variable split the template must encode — and it must generalise to any future
client's own document, not just these.

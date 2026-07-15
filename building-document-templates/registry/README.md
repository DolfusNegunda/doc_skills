# Template gallery

Three namespaces:

- `_builtin/<name>/` — **shipped generic templates** (committed to git; no client data).
  Generated per brand pack by `building-powerpoint-decks/scripts/build_template_library.py`
  and `authoring-word-documents/scripts/build_doc_library.py`; externally sourced
  templates join via `templatize.py build --builtin <name>`
  (see `../references/external-intake.md`).
- `_families/<family>/` — the governed canonical template per document family
  (created by `templatize.py build --family <name>`; not committed).
- `<client>/<doc-type>/` — per-client instances (the exception; not committed).

Each entry is `{template.<fmt>, manifest.json}`. Browse with `scripts/registry.py list`,
emit a fill-ready content file with `scripts/registry.py scaffold`, and set
`$TEMPLATE_REGISTRY` to relocate the gallery (client/family templates belong in a
private gallery outside the repo).

# Example: templatize a quarterly review, then fill it for a new client

A full run of the engine on a Word doc. The same four commands work on a `.pptx`.
Commands are run from the skill root; `$TEMPLATE_REGISTRY` is set so this example
doesn't touch the shared gallery.

```bash
export TEMPLATE_REGISTRY=/tmp/demo-registry

# 0. Generate the example client file (client_qbr.docx) — reproducible, no binary in git
python examples/make_example_docx.py   # writes examples/client_qbr.docx

# 1. Propose — extract candidate fields from the client's file
python scripts/templatize.py propose --file client_qbr.docx --out proposal.json

# 2. Review — edit proposal.json (see reviewed-proposal.json for the result):
#    - Client / Prepared by / Period / Date  -> keep=variable
#    - the summary sentence                   -> keep=variable, name=summary
#    - first achievement bullet               -> keep=variable, type=list, name=achievements
#    - the other two bullets                  -> keep=remove   (the list regenerates them)
#    - the two $ figures                       -> keep=variable (revenue, net_new_arr)
#    - headings & table labels                -> keep=fixed / deleted

# 3. Build — inject placeholders and register the template + manifest
python scripts/templatize.py build --file client_qbr.docx --fields reviewed-proposal.json \
    --client globex --doc-type quarterly-review \
    --owner you@co.com --created 2026-07-13

# 4. Fill — a DIFFERENT client's content, keyed by the manifest fields
python scripts/registry.py show --client globex --doc-type quarterly-review
python scripts/fill.py --client globex --doc-type quarterly-review \
    --data content.json --out out/initech-q4.docx

# 5. Validate — must print "status": "OK" before shipping
python scripts/validate.py out/initech-q4.docx \
    --template "$TEMPLATE_REGISTRY/globex/quarterly_review/template.docx"
```

`reviewed-proposal.json` and `content.json` in this folder are the exact inputs used
above. The template preserves the original layout, styles, and table; only the
placeholder text changes — so `initech-q4.docx` is visually identical to the client's
original with Initech's content and a four-item achievements list expanded into real
bullets.

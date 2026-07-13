"""Browse the template gallery.

The gallery lives under registry/<client>/<doc_type>/ and holds one template file
plus a manifest.json per entry. This tool lets a future agent (or person) discover
what already exists and see exactly which fields a template needs — so the next
document of that kind is a fill, not a rebuild.

Usage:
    python scripts/registry.py list                       # everything, grouped by client
    python scripts/registry.py list --client acme         # one client's templates
    python scripts/registry.py find --client acme --doc-type quarterly-review
    python scripts/registry.py show --client acme --doc-type quarterly-review  # + fields
"""
from __future__ import annotations

import argparse
import json
import sys

import common as C


def _iter_manifests():
    if not C.REGISTRY.exists():
        return
    for man in sorted(C.REGISTRY.glob("*/*/manifest.json")):
        try:
            yield man, C.load_manifest(man)
        except (json.JSONDecodeError, OSError):
            continue


def cmd_list(args):
    entries = [(m, d) for m, d in _iter_manifests()
               if not args.client or d.get("client") == C.slugify(args.client)]
    if not entries:
        print("No templates registered yet." if not args.client
              else f"No templates for client '{args.client}'.")
        return
    current = None
    for _man, d in entries:
        if d["client"] != current:
            current = d["client"]
            print(f"\n{current}")
        print(f"  - {d['doc_type']:30}  {d['format']:5}  {len(d['fields'])} fields  "
              f"v{d.get('version', '?')}")


def cmd_find(args):
    try:
        tpl, manifest = C.find_template(args.client, args.doc_type)
    except FileNotFoundError as e:
        sys.exit(str(e))
    print(json.dumps({"template": str(tpl), "manifest_id": manifest["template_id"],
                      "format": manifest["format"],
                      "fields": [f["name"] for f in manifest["fields"]]}, indent=2))


def cmd_show(args):
    try:
        tpl, manifest = C.find_template(args.client, args.doc_type)
    except FileNotFoundError as e:
        sys.exit(str(e))
    print(f"{manifest['template_id']}  ({manifest['format']}, v{manifest.get('version', '?')})")
    print(f"  template : {tpl}")
    print(f"  source   : {manifest.get('source_file', '—')}")
    print(f"  owner    : {manifest.get('owner', '—')}   created: {manifest.get('created', '—')}")
    print(f"  fields   ({len(manifest['fields'])}):")
    for f in manifest["fields"]:
        req = "" if f.get("required", True) else " (optional)"
        ex = f" e.g. {f['example'][:40]!r}" if f.get("example") else ""
        print(f"    - {f['name']:24} {f.get('type','text'):10}{req}{ex}")
    print("\n  Build a data.json with these keys, then:")
    print(f"    python scripts/fill.py --client {manifest['client']} "
          f"--doc-type {manifest['doc_type']} --data data.json --out out.{manifest['format']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.add_argument("--client", default=None)
    p.set_defaults(func=cmd_list)

    for name in ("find", "show"):
        s = sub.add_parser(name)
        s.add_argument("--client", required=True)
        s.add_argument("--doc-type", required=True)
        s.set_defaults(func=cmd_find if name == "find" else cmd_show)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

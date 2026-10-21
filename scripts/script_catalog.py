#!/usr/bin/env python3
"""List and explain identity/session/Git scripts; verify their generated index."""
from pathlib import Path
import argparse
import json
import sys

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import core_bootstrap  # noqa: E402,F401
from everagent_core import catalog  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("list", "show", "check", "render"), default="list")
    parser.add_argument("id", nargs="?")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    source = _SCRIPTS / "script-catalog.json"
    value = catalog.load_catalog(source)
    errors = catalog.validate_catalog(value, roots={value["repository"]: _SCRIPTS.parent})
    expected = catalog.render_index(value, source_sha256=catalog.catalog_hash(source))
    output = _SCRIPTS / "SCRIPT_INDEX.md"
    if args.command == "render" and not errors:
        output.write_text(expected, encoding="utf-8")
    elif args.command == "check" and (not output.is_file() or output.read_text(encoding="utf-8") != expected):
        errors.append("generated script index is stale")
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False))
        return 1
    if args.command == "show":
        rows = [row for row in value["scripts"] if row["id"] == args.id or row["entrypoint"] == args.id
                or any(a["path"] == args.id for a in row["aliases"])]
        if not rows:
            parser.error("unknown script")
        print(json.dumps(rows[0], ensure_ascii=False, indent=2))
    elif args.command == "list":
        print(json.dumps(value, ensure_ascii=False) if args.json else expected)
    else:
        print("script catalog: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

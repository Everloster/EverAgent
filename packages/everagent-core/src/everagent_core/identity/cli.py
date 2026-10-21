"""Identity CLI shared by the installed core and repository entrypoints."""
import argparse
import json
import sys
from . import inspect_identity, source_sha256


def main(arguments=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("inspect", "declare-model"), default="inspect")
    parser.add_argument("--model")
    parser.add_argument("--user-confirmed", action="store_true",
                        help="只在用户明确指定当前模型后使用")
    parser.add_argument("--ttl-seconds", type=int, default=14400)
    output = parser.add_mutually_exclusive_group()
    for flag in ("json", "name", "email", "git-ident"):
        output.add_argument("--" + flag, action="store_true")
    args = parser.parse_args(arguments)
    value = {**inspect_identity(), "source_sha256": source_sha256()}
    if args.command == "declare-model":
        from . import declarations, models
        if not args.model or not value.get("harness_resolved"):
            parser.error("声明需要明确 --model 和已识别的当前 harness")
        try:
            value = declarations.declare_model(value["cli"], args.model,
                      user_confirmed=args.user_confirmed, ttl_seconds=args.ttl_seconds,
                      hint=models.hint_fingerprint(value["cli"]))
        except ValueError as exc:
            parser.error(str(exc))
        print(json.dumps(value, ensure_ascii=False))
        return 0
    if args.model or args.user_confirmed:
        parser.error("模型声明参数只用于 declare-model")
    if args.json:
        encoded = json.dumps(value, ensure_ascii=False) + "\n"
    elif args.name:
        encoded = value["name"] + "\n"
    elif args.email:
        encoded = value["email"] + "\n"
    elif args.git_ident:
        encoded = value["name"] + "\t" + value["email"] + "\n"
    else:
        encoded = "name=" + value["name"] + "\nemail=" + value["email"] + "\n"
    buffer = getattr(sys.stdout, "buffer", None)
    if buffer:
        buffer.write(encoded.encode("utf-8"))
    else:
        sys.stdout.write(encoded)
    return 0 if not args.git_ident or value["commit_ready"] else 1

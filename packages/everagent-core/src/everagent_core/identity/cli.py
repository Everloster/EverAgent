"""Identity CLI shared by the installed core and repository entrypoints."""
import argparse
import json
import sys
from . import diagnose_identity, inspect_identity, source_sha256


def main(arguments=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("inspect", "diagnose", "declare", "declare-model"), default="inspect")
    parser.add_argument("--model")
    parser.add_argument("--device")
    parser.add_argument("--harness")
    parser.add_argument("--form", choices=("cli", "desktop", "web"))
    parser.add_argument("--user-confirmed", action="store_true",
                        help="只在用户明确指定当前缺失事实后使用")
    parser.add_argument("--ttl-seconds", type=int, default=14400)
    output = parser.add_mutually_exclusive_group()
    for flag in ("json", "name", "email", "git-ident"):
        output.add_argument("--" + flag, action="store_true")
    args = parser.parse_args(arguments)
    facts = {key: getattr(args, key) for key in ("device", "harness", "form", "model") if getattr(args, key)}
    if args.command == "diagnose":
        if facts or args.user_confirmed or args.name or args.email or args.git_ident:
            parser.error("diagnose 只返回当前调用方诊断；使用 --json，不接受声明或 Git 身份输出参数")
        print(json.dumps({**diagnose_identity(), "source_sha256": source_sha256()}, ensure_ascii=False))
        return 0
    value = {**inspect_identity(), "source_sha256": source_sha256()}
    if args.command == "declare":
        from . import config, declarations
        observed = {"harness": value.get("cli") if value.get("cli_source") != "user-declared" else None,
                    "model": value.get("model") if value.get("current_model_confirmed") else None}
        if observed["harness"]:
            observed["form"] = config.rule(observed["harness"]).get("form")
        try:
            result = declarations.declare_facts(facts, user_confirmed=args.user_confirmed,
                                               ttl_seconds=args.ttl_seconds, observed=observed)
        except ValueError as exc:
            parser.error(str(exc))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    if args.command == "declare-model":
        if set(facts) - {"model"}:
            parser.error("declare-model 仅兼容模型；其他用户事实使用 declare")
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
    if facts or args.user_confirmed:
        parser.error("声明参数只用于 declare / declare-model")
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

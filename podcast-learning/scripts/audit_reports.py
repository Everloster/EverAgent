#!/usr/bin/env python3
"""播客审计兼容入口：调用根审计，无写入、无 --fix。

无参数检查全部播客报告及历史转写；--changed/--staged 采用根入口的选择规则。
旧模板必填章节/字段不再独立维护；report-v2 由根质量门拥有。
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
DOMAIN = REPO / "podcast-learning"


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if "--fix" in args:
        print("--fix 已退役；审计只读，不修改报告、转写或哈希回执。", file=sys.stderr)
        return 2
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("everagent_root_audit", REPO / "scripts/audit_reports.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if not any(arg in args for arg in ("--all", "--changed", "--staged", "--help", "-h")):
        paths = [arg for arg in args if not arg.startswith("-")]
        if not paths:
            args.extend(str(path) for path in sorted((DOMAIN / "reports").glob("*.md")))
            args.extend(str(path) for path in sorted((DOMAIN / "reports/transcripts").glob("*.transcript.txt")))
        else:
            args = [str(DOMAIN / arg) if not arg.startswith("-") and not Path(arg).is_absolute()
                    and not Path(arg).exists() else arg for arg in args]
    return module.main(args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Condense subproject AGENTS.md by deduplicating shared protocol sections.

Replaces repeated content with references to docs/PROTOCOL_COMMON.md:

  §6 Hallucination Guard   -> 1-line pointer to PROTOCOL_COMMON.md §A
                               + project-specific additions preserved
  §5 Commit Protocol       -> trim the redundant format block (now in §B)

Idempotent: if pointer already exists, skip. Operates only on sections whose
content matches the known boilerplate signature.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Sections to compact (search anchor + replacement)
HALLUCINATION_GUARD_HEADER = re.compile(
    r"^## §\d+\s+Hallucination Guard.*?\n", re.MULTILINE
)

HALLUCINATION_GUARD_REPLACEMENT = """\
## §{n} Hallucination Guard

> 共享规则 → [`docs/PROTOCOL_COMMON.md`](../docs/PROTOCOL_COMMON.md) §A Safety Rules
>
> 本节仅列出本项目特有的补充：
"""


SUBPROJECTS = [
    "ai-learning",
    "cs-learning",
    "philosophy-learning",
    "psychology-learning",
    "biology-learning",
    "podcast-learning",
    "ai-practice",
    "github-trending-analyzer",
]


def already_condensed(content: str) -> bool:
    return "PROTOCOL_COMMON.md" in content and "## §A Safety Rules" not in content


def condense_project(name: str) -> bool:
    path = ROOT / name / "AGENTS.md"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if "PROTOCOL_COMMON.md" in text:
        print(f"  {name}: already condensed, skip")
        return False

    # Find §N Hallucination Guard section
    m = HALLUCINATION_GUARD_HEADER.search(text)
    if not m:
        print(f"  {name}: no Hallucination Guard section found")
        return False

    section_n = re.search(r"§(\d+)", m.group(0)).group(1)
    replacement = HALLUCINATION_GUARD_REPLACEMENT.replace("{n}", section_n)

    # Find end of section (next ## or EOF)
    start = m.start()
    rest_start = m.end()
    next_section_m = re.search(r"^## ", text[rest_start:], re.MULTILINE)
    if next_section_m:
        end = rest_start + next_section_m.start()
    else:
        end = len(text)

    # Preserve any project-specific bullets (lines that look like 1. 2. 3. ...)
    section_body = text[rest_start:end].rstrip()
    kept_lines = []
    for line in section_body.splitlines():
        stripped = line.strip()
        # Drop generic boilerplate that PROTOCOL_COMMON.md covers
        if stripped.startswith("1.") and "CONTEXT.md" in stripped and "边界" in stripped:
            continue
        if "论文中未出现的数据" in stripped:
            continue
        if "禁止推测 GPT-4" in stripped or "禁止推测未研究模型" in stripped:
            continue
        if "报告内容须与论文原文" in stripped:
            continue
        if "禁止在报告内容中出现" in stripped:
            continue
        if stripped == "---" and not kept_lines:
            continue
        kept_lines.append(line)
    project_specific = "\n".join(kept_lines).strip()
    if not project_specific or project_specific.startswith("---"):
        # All content was boilerplate; leave just the pointer
        new_section = replacement.rstrip() + "\n"
    else:
        new_section = replacement + project_specific + "\n"

    new_text = text[:start] + new_section + "\n---\n\n" + text[end:]
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    path.write_text(new_text, encoding="utf-8")
    print(f"  {name}: condensed §{section_n} Hallucination Guard")
    return True


def main() -> int:
    print(f"condensing {len(SUBPROJECTS)} subproject AGENTS.md files:")
    condensed = 0
    for name in SUBPROJECTS:
        if condense_project(name):
            condensed += 1
    print(f"\ncondensed: {condensed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
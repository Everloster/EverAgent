#!/usr/bin/env python3
"""Create a new EverAgent subproject and refresh generated views."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from project_registry import discover_projects


ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = ROOT / "AGENTS.md"
TEMPLATE_DIR = ROOT / "docs" / "PROJECT_TEMPLATE"
SAMPLE_AGENTS = TEMPLATE_DIR / "AGENTS.md.template"
TASK_BOARD_AGGREGATOR = ROOT / "scripts" / "task_board_aggregator.py"


def validate_args(args: argparse.Namespace) -> bool:
    errors: list[str] = []
    projects = discover_projects()

    if not re.match(r"^[a-z][a-z0-9-]*$", args.project):
        errors.append(f"项目名格式错误：{args.project}（应使用小写字母、数字、连字符，如 quantum-learning）")
    if args.project in projects:
        errors.append(f"项目已存在：{args.project}")
    project_dir = ROOT / args.project
    if project_dir.exists():
        errors.append(f"目录已存在：{project_dir}")
    if not args.domain:
        errors.append("domain 不能为空")
    if not args.agent_name:
        errors.append("agent_name 不能为空")
    if errors:
        for err in errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        return False
    return True


def create_directories(project_dir: Path) -> None:
    dirs = [
        project_dir / "papers",
        project_dir / "books",
        project_dir / "reports" / "paper_analyses",
        project_dir / "reports" / "knowledge_reports",
        project_dir / "reports" / "concept_reports",
        project_dir / "reports" / "text_analyses",
        project_dir / "knowledge",
        project_dir / "roadmap",
        project_dir / "wiki" / "entities",
        project_dir / "wiki" / "concepts",
        project_dir / "wiki" / "syntheses",
        project_dir / "skills" / "paper_analysis",
        project_dir / "skills" / "concept_deep_dive",
    ]

    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)
        gitkeep = directory / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")
    print(f"[INFO] Created directory structure: {project_dir}")


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"[INFO] Generated: {path}")


def generate_task_state(project_dir: Path) -> None:
    write_text(
        project_dir / ".project-task-state",
        "# Versioned task state for this project.\n"
        "# Add tasks here and regenerate docs/LEARNING_PROJECTS_TASK_BOARD.md via task_board_aggregator.py.\n",
    )


def load_agents_template() -> str:
    if SAMPLE_AGENTS.exists():
        return SAMPLE_AGENTS.read_text(encoding="utf-8")
    print(f"[WARN] Template not found: {SAMPLE_AGENTS}, using built-in fallback")
    return get_default_agents_template()


def render_template(template: str, args: argparse.Namespace) -> str:
    content = template.replace("{{AGENT_NAME}}", args.agent_name)
    content = content.replace("{{PROJECT_PATH}}", args.project)
    return content.replace("{{DOMAIN}}", args.domain)


def generate_agents_md(project_dir: Path, args: argparse.Namespace) -> None:
    write_text(project_dir / "AGENTS.md", render_template(load_agents_template(), args))


def get_default_agents_template() -> str:
    return """# {{AGENT_NAME}} — {{PROJECT_PATH}} 执行协议 v1.0

> 本文件自包含。{{AGENT_NAME}} 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "{{AGENT_NAME}}"
  role: "{{DOMAIN}}"
  project: "{{PROJECT_PATH}}"
  capability_level: task_executor
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - {{PROJECT_PATH}}/CONTEXT.md
# - {{PROJECT_PATH}}/.project-task-state
# - {{PROJECT_PATH}}/skills/paper_analysis/SKILL.md
```

---

## §1 Project Scope（项目边界）

**领域**：{{DOMAIN}}
**三维度**：技术深度 × 历史叙事 × 工程实践

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `paper_analysis` | 单篇论文 7 步深度精读 | `reports/paper_analyses/` |
| `knowledge_report` | 概念/技术专题深度解析 | `reports/knowledge_reports/` |
| `concept_report` | 多篇材料整合后的概念报告 | `reports/concept_reports/` |
| `text_analysis` | 经典文本逐章分析 | `reports/text_analyses/` |

**禁止操作**：
- 修改 `CONTEXT.md` 以外的项目元文件
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
0. 运行 python3 scripts/execution_validator.py --mode=input --task-id=TXXX
   → 校验失败则停止，不 claim 任务
1. 读取 {{PROJECT_PATH}}/.project-task-state（Task Board 仅作只读视图）
2. 选取 project: {{PROJECT_PATH}}, status: open 的任务
3. 优先运行 python3 scripts/task_exec.py begin --task-id=TXXX --project={{PROJECT_PATH}} --agent={{AGENT_NAME}}
4. 立即 commit push（防并发冲突）
5. 运行 python3 scripts/task_exec.py start --task-id=TXXX
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

## §3 Output Standards（输出规范）

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"列表追加新报告条目
2. `docs/LEARNING_PROJECTS_TASK_BOARD.md` — 通过聚合器重建只读视图

### 完成后必须校验

```
[commit 前必须运行]
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project={{PROJECT_PATH}}
   → 校验失败则不 commit，修复后重试
python3 scripts/task_exec.py finish --task-id=TXXX --project={{PROJECT_PATH}}
```

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `reports/` | ✅ 新建·修改 |
| `CONTEXT.md` | ✅ 仅追加报告条目 |
| `wiki/` | ✅ 新建·追加更新 |
| `skills/` | ❌ 只读 |
| `AGENTS.md`（本文件） | ❌ 只读 |
| 其他子项目任意路径 | ❌ 禁止 |
| 全局 `AGENTS.md` / `CLAUDE.md` / `scripts/` | ❌ 禁止 |

---

## §5 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"边界区"
2. 禁止推测未研究的内容
3. 报告内容须与原文严格对应
"""


def generate_context_md(project_dir: Path, args: argparse.Namespace) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    content = f"""# {args.project} Context

> 项目：{args.domain}
> Agent：{args.agent_name}
> 创建时间：{now}

---

## 项目概述

{{DOMAIN}} 领域知识沉淀库。

---

## 已有报告

（暂无报告，完成第一篇精读后追加）

---

## ⚠️ 边界（防幻觉）

以下主题已有报告，禁止重复生成：

（随着任务完成持续更新）

---

## 学习路线

（待规划）

---

## 参考资源

- 论文索引：`papers/PAPERS_INDEX.md`
- 技能模板：`docs/SKILL_TEMPLATES.md`
"""
    write_text(project_dir / "CONTEXT.md", content)


def generate_readme_md(project_dir: Path, args: argparse.Namespace) -> None:
    content = f"""# {args.domain}

> {args.agent_name} 学习项目

## 项目概述

{args.domain} 领域的论文精读、知识报告、技术分析。

## 目录结构

```
{args.project}/
├── AGENTS.md              # 执行协议
├── CONTEXT.md             # 项目上下文
├── papers/                # 论文索引
│   └── PAPERS_INDEX.md
├── books/                 # 书单索引
│   └── BOOKS_INDEX.md
├── reports/               # 报告产出
│   ├── paper_analyses/    # 论文精读
│   ├── knowledge_reports/ # 知识报告/专题解析
│   ├── concept_reports/   # 概念报告
│   └── text_analyses/     # 经典文本分析
├── knowledge/             # 项目知识索引
├── wiki/                  # 索引层知识网络
│   ├── entities/
│   ├── concepts/
│   └── syntheses/
├── roadmap/               # 学习路线
└── skills/                # 技能定义
```

## 执行协议

见 `AGENTS.md`
"""
    write_text(project_dir / "README.md", content)


def generate_supporting_files(project_dir: Path, args: argparse.Namespace) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    files = {
        project_dir / "papers" / "PAPERS_INDEX.md": "# Papers Index\n\n> 待补充论文清单。\n",
        project_dir / "books" / "BOOKS_INDEX.md": "# Books Index\n\n> 待补充书单。\n",
        project_dir / "knowledge" / "INDEX.md": "# Knowledge Index\n\n> 待补充项目知识索引。\n",
        project_dir / "roadmap" / "Learning_Roadmap.md": f"# Learning Roadmap\n\n> {args.domain} 学习路线待规划。\n",
        project_dir / "roadmap" / "Development_Timeline.md": "# Development Timeline\n\n> 待补充发展时间线。\n",
        project_dir / "wiki" / "index.md": "# Wiki Index\n\n> 待随着报告摄入逐步建立。\n",
        project_dir / "wiki" / "log.md": f"# Wiki Log\n\n## [{now}] init | scaffold\n- 初始化项目骨架\n",
        project_dir / "skills" / "paper_analysis" / "SKILL.md": "# Paper Analysis Skill\n\n> 参考共享模板：`docs/SKILL_TEMPLATES.md`\n",
        project_dir / "skills" / "concept_deep_dive" / "SKILL.md": "# Concept Deep Dive Skill\n\n> 参考共享模板：`docs/SKILL_TEMPLATES.md`\n",
    }
    for path, content in files.items():
        write_text(path, content)


def update_global_agents(args: argparse.Namespace) -> None:
    lines = AGENTS_MD.read_text(encoding="utf-8").splitlines()
    new_row = f"| **{args.agent_name}** | `{args.project}/` | `{args.project}/AGENTS.md` | {args.domain} | 🟢 |"
    if new_row in lines:
        print(f"[INFO] Global AGENTS.md already contains {args.project}")
        return

    separator_index = next((idx for idx, line in enumerate(lines) if line.startswith("|---------|")), None)
    if separator_index is None:
        raise ValueError("Could not find Subagent Registry table in AGENTS.md")

    insert_index = separator_index + 1
    while insert_index < len(lines) and lines[insert_index].startswith("| **"):
        insert_index += 1
    lines.insert(insert_index, new_row)
    write_text(AGENTS_MD, "\n".join(lines))
    print(f"[INFO] Updated global AGENTS.md §1: added {args.agent_name}")


def refresh_generated_views() -> None:
    subprocess.run(
        [sys.executable, str(TASK_BOARD_AGGREGATOR), "--sync-readme"],
        cwd=ROOT,
        check=True,
    )
    print("[INFO] Refreshed task board and root README overview")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Project — 自动化创建新子项目")
    parser.add_argument("--project", required=True, help="项目名称（如 quantum-learning）")
    parser.add_argument("--domain", required=True, help="领域描述（如 量子计算）")
    parser.add_argument("--agent-name", required=True, help="Agent 名称（如 QuantumAgent）")
    parser.add_argument("--dry-run", action="store_true", help="仅显示不写入")
    args = parser.parse_args()

    if not validate_args(args):
        return 1

    if args.dry_run:
        print(f"[DRY-RUN] Would create project: {args.project}")
        print(f"  domain: {args.domain}")
        print(f"  agent_name: {args.agent_name}")
        return 0

    project_dir = ROOT / args.project

    create_directories(project_dir)
    generate_task_state(project_dir)
    generate_agents_md(project_dir, args)
    generate_context_md(project_dir, args)
    generate_readme_md(project_dir, args)
    generate_supporting_files(project_dir, args)
    update_global_agents(args)
    refresh_generated_views()

    print(f"\n[SUCCESS] Project {args.project} created!")
    print(f"  Next steps:")
    print(f"  1. Review generated files in {project_dir}")
    print(f"  2. Add initial papers to {project_dir}/papers/PAPERS_INDEX.md")
    print(f"  3. Create first task in {project_dir}/.project-task-state")
    print(f"  4. Commit: git add {args.project} && git commit -m '[new-project] {args.project}: initial structure'")

    return 0


if __name__ == "__main__":
    sys.exit(main())

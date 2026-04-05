#!/usr/bin/env python3
"""
Create Project — 自动化创建新子项目

功能：
  1. 按模板创建目录结构
  2. 生成自包含的 AGENTS.md（基于模板）
  3. 生成初始 CONTEXT.md
  4. 自动更新全局 AGENTS.md §1
  5. 自动更新 Task Board 项目进度
  6. 自动更新 README.md

用法：
  python3 scripts/create_project.py --project={name} --domain={domain} --agent-name={AgentName}
  python3 scripts/create_project.py --project=quantum-learning --domain=量子计算 --agent-name=QuantumAgent

返回码：
  0  成功
  1  失败
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Project paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
AGENTS_MD = ROOT / "AGENTS.md"
README_MD = ROOT / "README.md"
TASK_BOARD = ROOT / "docs" / "LEARNING_PROJECTS_TASK_BOARD.md"
TEMPLATE_DIR = ROOT / "docs" / "PROJECT_TEMPLATE"
SAMPLE_AGENTS = TEMPLATE_DIR / "AGENTS.md.template"

PROJECTS = {
    "ai-learning": ROOT / "ai-learning",
    "cs-learning": ROOT / "cs-learning",
    "philosophy-learning": ROOT / "philosophy-learning",
    "psychology-learning": ROOT / "psychology-learning",
    "biology-learning": ROOT / "biology-learning",
    "github-trending-analyzer": ROOT / "github-trending-analyzer",
}


def validate_args(args: argparse.Namespace) -> bool:
    """验证参数"""
    errors: list[str] = []

    # 检查项目名格式
    if not re.match(r"^[a-z][a-z0-9-]*$", args.project):
        errors.append(f"项目名格式错误：{args.project}（应使用小写字母、数字、连字符，如 quantum-learning）")

    # 检查是否已存在
    if args.project in PROJECTS:
        errors.append(f"项目已存在：{args.project}")

    # 检查目录是否已存在
    project_dir = ROOT / args.project
    if project_dir.exists():
        errors.append(f"目录已存在：{project_dir}")

    # 检查 domain 是否为空
    if not args.domain:
        errors.append("domain 不能为空")

    # 检查 agent_name 是否为空
    if not args.agent_name:
        errors.append("agent_name 不能为空")

    if errors:
        for err in errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        return False

    return True


def create_directories(project_dir: Path) -> None:
    """创建项目目录结构"""
    dirs = [
        project_dir / "papers",
        project_dir / "books",
        project_dir / "reports" / "paper_analyses",
        project_dir / "reports" / "knowledge_reports",
        project_dir / "reports" / "concept_reports",
        project_dir / "reports" / "text_analyses",
        project_dir / "knowledge",
        project_dir / "roadmap",
        project_dir / "skills" / "paper_analysis",
        project_dir / "skills" / "concept_deep_dive",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        # 创建 .gitkeep 文件
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("", encoding="utf-8")

    print(f"[INFO] Created directory structure: {project_dir}")


def generate_agents_md(project_dir: Path, args: argparse.Namespace) -> Path:
    """从模板生成 AGENTS.md"""
    if not SAMPLE_AGENTS.exists():
        print(f"[WARN] Template not found: {SAMPLE_AGENTS}, creating default AGENTS.md")

    # 读取模板或创建默认内容
    if SAMPLE_AGENTS.exists():
        template = SAMPLE_AGENTS.read_text(encoding="utf-8")
    else:
        template = get_default_agents_template()

    # 替换占位符
    content = template.replace("{{AGENT_NAME}}", args.agent_name)
    content = content.replace("{{PROJECT_PATH}}", args.project)
    content = content.replace("{{DOMAIN}}", args.domain)

    # 写入文件
    agents_md = project_dir / "AGENTS.md"
    agents_md.write_text(content, encoding="utf-8")
    print(f"[INFO] Generated: {agents_md}")

    return agents_md


def get_default_agents_template() -> str:
    """获取默认 AGENTS.md 模板"""
    return """# {{AGENT_NAME}} — {{PROJECT_PATH}} 执行协议 v1.0

> 本文件自包含。{{AGENT_NAME}} 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "{{AGENT_NAME}}"
  role: "{{DOMAIN}}"
  project: "{{PROJECT_PATH}}"
  capability_level: task_executor
```

---

## §1 Project Scope

**领域**：{{DOMAIN}}

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `paper_analysis` | 单篇论文 7 步深度精读 | `reports/paper_analyses/` |
| `knowledge_report` | 概念/技术专题深度解析 | `reports/knowledge_reports/` |

---

## §2 Task Execution Protocol

### 2.1 领取任务

```
0. 运行 python3 scripts/execution_validator.py --mode=input --task-id=TXXX
1. 读取 docs/LEARNING_PROJECTS_TASK_BOARD.md
2. 选取 project: {{PROJECT_PATH}}, status: open 的任务
3. 将 status 改为 claimed
4. 立即 commit push
5. 将 status 改为 in_progress
```

### 完成后必须校验

```
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project={{PROJECT_PATH}}
```

---

## §3 Hallucination Guard

1. 执行前必须读取 `CONTEXT.md` 的"边界区"
2. 禁止推测未研究的内容
"""


def generate_context_md(project_dir: Path, args: argparse.Namespace) -> Path:
    """生成初始 CONTEXT.md"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    content = f"""# {{PROJECT_PATH}} Context

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

    content = content.replace("{{AGENT_NAME}}", args.agent_name)
    content = content.replace("{{PROJECT_PATH}}", args.project)
    content = content.replace("{{DOMAIN}}", args.domain)

    context_md = project_dir / "CONTEXT.md"
    context_md.write_text(content, encoding="utf-8")
    print(f"[INFO] Generated: {context_md}")

    return context_md


def generate_readme_md(project_dir: Path, args: argparse.Namespace) -> Path:
    """生成项目 README.md"""
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
├── reports/               # 报告产出
│   ├── paper_analyses/    # 论文精读
│   ├── knowledge_reports/ # 知识报告
│   └── concept_reports/    # 概念报告
├── knowledge/             # 离线知识库
├── roadmap/               # 学习路线
└── skills/                # 技能定义
```

## 执行协议

见 `AGENTS.md`
"""

    readme_md = project_dir / "README.md"
    readme_md.write_text(content, encoding="utf-8")
    print(f"[INFO] Generated: {readme_md}")

    return readme_md


def update_global_agents(args: argparse.Namespace) -> None:
    """更新全局 AGENTS.md §1 Subagent Registry"""
    if not AGENTS_MD.exists():
        print(f"[WARN] Global AGENTS.md not found: {AGENTS_MD}")
        return

    text = AGENTS_MD.read_text(encoding="utf-8")

    # 查找 Subagent Registry 表格
    # 表格格式：| **Agent名** | `path` | `path/AGENTS.md` | 领域 | 🟢/🟡/🔴 |
    new_row = f"| **{args.agent_name}** | `{args.project}/` | `{args.project}/AGENTS.md` | {args.domain} | 🟢 |"

    # 在表格末尾（最后一个 | --- | 行之后）插入新行
    # 找到最后一个 | --- | 行
    pattern = r"(\| ---+ \| ---+ \| ---+ \| ---+ \| ---+ \|)\n"
    match = re.search(pattern, text)
    if match:
        insert_pos = match.end()
        text = text[:insert_pos] + new_row + "\n" + text[insert_pos:]
        AGENTS_MD.write_text(text, encoding="utf-8")
        print(f"[INFO] Updated global AGENTS.md §1: added {args.agent_name}")
    else:
        print(f"[WARN] Could not find Subagent Registry table in AGENTS.md")


def update_task_board(args: argparse.Namespace) -> None:
    """更新 Task Board 项目进度概览"""
    if not TASK_BOARD.exists():
        print(f"[WARN] Task Board not found: {TASK_BOARD}")
        return

    text = TASK_BOARD.read_text(encoding="utf-8")

    # 新项目行
    new_row = f"| `{args.project}` | 🟢 新建 | 0 | 0 | 0% | — |"

    # 在项目进度概览表格中添加新行
    # 查找表格的最后一行（最后一个 | --- | 之前的真实数据行）
    pattern = r"(\| ---+ \| ---+ \| ---+ \| ---+ \| ---+ \| ---+ \|)\n"
    match = re.search(pattern, text)
    if match:
        insert_pos = match.start()
        text = text[:insert_pos] + new_row + "\n" + text[insert_pos:]
        TASK_BOARD.write_text(text, encoding="utf-8")
        print(f"[INFO] Updated Task Board: added {args.project}")
    else:
        print(f"[WARN] Could not find project progress table in Task Board")


def update_readme(args: argparse.Namespace) -> None:
    """更新根目录 README.md 项目表格"""
    if not README_MD.exists():
        print(f"[WARN] README.md not found: {README_MD}")
        return

    text = README_MD.read_text(encoding="utf-8")

    # 新项目行
    new_row = f"| {args.agent_name} | {args.domain} | `/{args.project}/` | 🟢 |"

    # 查找项目表格并添加新行（如果有的话）
    # 简单起见，只在文件末尾追加
    text += f"\n{new_row}\n"

    README_MD.write_text(text, encoding="utf-8")
    print(f"[INFO] Updated README.md: added {args.project}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Project — 自动化创建新子项目")
    parser.add_argument("--project", required=True, help="项目名称（如 quantum-learning）")
    parser.add_argument("--domain", required=True, help="领域描述（如 量子计算）")
    parser.add_argument("--agent-name", required=True, help="Agent 名称（如 QuantumAgent）")
    parser.add_argument("--dry-run", action="store_true", help="仅显示不写入")
    args = parser.parse_args()

    # 验证
    if not validate_args(args):
        return 1

    if args.dry_run:
        print(f"[DRY-RUN] Would create project: {args.project}")
        print(f"  domain: {args.domain}")
        print(f"  agent_name: {args.agent_name}")
        return 0

    project_dir = ROOT / args.project

    # 1. 创建目录结构
    create_directories(project_dir)

    # 2. 生成 AGENTS.md
    generate_agents_md(project_dir, args)

    # 3. 生成 CONTEXT.md
    generate_context_md(project_dir, args)

    # 4. 生成 README.md
    generate_readme_md(project_dir, args)

    # 5. 更新全局 AGENTS.md §1
    update_global_agents(args)

    # 6. 更新 Task Board
    update_task_board(args)

    # 7. 更新 README.md
    update_readme(args)

    print(f"\n[SUCCESS] Project {args.project} created!")
    print(f"  Next steps:")
    print(f"  1. Review generated files in {project_dir}")
    print(f"  2. Add initial papers to {project_dir}/papers/PAPERS_INDEX.md")
    print(f"  3. Create first task in Task Board")
    print(f"  4. Commit: git add {args.project} && git commit -m '[new-project] {args.project}: initial structure'")

    return 0


if __name__ == "__main__":
    sys.exit(main())

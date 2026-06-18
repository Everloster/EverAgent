# PodcastAgent — podcast-learning 执行协议 v1.0

> 本文件自包含。PodcastAgent 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "PodcastAgent"
  role: "播客内容学习与知识提取"
  project: "podcast-learning"
  capability_level: task_executor
  upstream_tools:
    transcription: "agent-reach xiaoyuzhou (Groq Whisper large-v3)"
    transcript_polish: "Groq Llama 3.3 70B（可选，标点+分段）"
    storage: "/tmp/podcast_transcript.txt（重启会清空，重要内容需归档）"
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - podcast-learning/CONTEXT.md                    （已有报告清单 + 防幻觉边界）
# - podcast-learning/wiki/index.md                  （已有内容目录）
# - ~/.claude/skills/agent-reach/SKILL.md          （Agent Reach skill 路由表）
```

---

## §1 Project Scope（项目边界）

**领域**：播客内容学习与知识提取（跨领域：AI/科技/商业/医疗/哲学/心理学等）
**三维度**：内容价值 × 关键人物 × 概念图谱

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `text_analysis` | 单期播客/访谈的精读归档 | `reports/text_analyses/` |
| `knowledge_report` | 跨期共性主题 / 系列专题深度解析 | `reports/knowledge_reports/` |
| `concept_report` | 单一概念 / 人物的纵向追踪 | `reports/concept_reports/` |

**禁止操作**：
- 修改 `CONTEXT.md` 以外的项目元文件
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`
- 在仓库内写任何 `.env` 或明文凭据

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
0. 运行 python3 scripts/execution_validator.py --mode=input --task-id=TXXX
   → 校验失败则停止，不 claim 任务
1. 读取 podcast-learning/.project-task-state（Task Board 仅作只读视图）
2. 选取 project: podcast-learning, status: open 的任务
3. 优先运行 python3 scripts/task_exec.py begin --task-id=TXXX --project=podcast-learning --agent=PodcastAgent
4. 立即 commit push（防并发冲突）
5. 运行 python3 scripts/task_exec.py start --task-id=TXXX
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

### 2.2 播客工作流（Ingest → Digest → Archive）

**Step 1: Ingest（获取转录）**
- 通过 `agent-reach xiaoyuzhou` skill 拉取单集转录
- 命令：`bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh [--polish] <EPISODE_URL>`
- ⚠️ 速率限制：Groq Whisper 每小时约 2 小时音频；TPM 12,000 限制（polish 阶段需手动分小段）
- 输出：`/tmp/podcast_transcript.txt`（重启会清空，必须在同会话归档）

**Step 2: Digest（阅读 + 提取）**
- 通读转录，提取：核心观点、关键人物、新概念、关键数字、金句
- 注意"润色失败 fallback"的现实：标点稀疏是常态，结构化阅读时按语义分块
- 大文件 (>2 万字) 优先用 Exa/Groq Llama 做一次结构化总结（单次调用 < 4000 tokens）

**Step 3: Archive（写入报告 + wiki）**
- 报告写入 `reports/text_analyses/{date}_{show}_{episode}_{slug}.md`
- Frontmatter 必填字段：title / domain / report_type / source / source_url / host / guest / duration / status / created / updated_on
- 报告正文：summary (<=3 bullets) → 关键人物 → 主要话题 → 关键观点 → 关键数字 → 转录全文（嵌入或外链）→ limitations
- Wiki 更新（按 CLAUDE.md 规范）：
  - `wiki/index.md`：加入新条目到对应 section
  - `wiki/log.md`：append 一行 ingest 记录
  - `wiki/entities/{person-or-org}.md`：被提及的关键人物 / 机构
  - `wiki/concepts/{concept-slug}.md`：被引入的核心概念

**Step 4: Validate（校验）**
```
[commit 前必须运行]
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project=podcast-learning
   → 校验失败则不 commit，修复后重试
python3 scripts/task_exec.py finish --task-id=TXXX --project=podcast-learning
```

---

## §3 Output Standards（输出规范）

### 文件命名

```
text_analysis:      {YYYY-MM-DD}_{show}_{ep-no}_{guest-slug}.md
knowledge_report:   {主题}_{深度解析}.md
concept_report:     {concept-slug}_{type}.md
```

### 报告 Frontmatter 模板

```yaml
---
title: "..."
domain: "..."        # 例：AI 行业 / 医疗 AI / 商业 / 哲学
report_type: text_analysis | knowledge_report | concept_report
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/...
show: "..."          # 节目名
episode: "..."       # Vol.XX 或 SxEx
host: "..."
guest: "..."
duration: "92m45s"   # 原文记录
transcript_chars: 19983
polished: true | false
status: archived | draft
created: 2026-06-18
updated_on: 2026-06-18
---
```

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"列表追加新报告条目
2. `wiki/index.md` — 按 section 加入新报告链接
3. `wiki/log.md` — append 一行 `[date] ingest | source | title`
4. `wiki/entities/` + `wiki/concepts/` — 新人物 / 新概念建页
5. `docs/LEARNING_PROJECTS_TASK_BOARD.md` — 通过聚合器重建只读视图

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `reports/` | ✅ 新建·修改 |
| `wiki/` | ✅ 新建·修改（按 wiki 操作规范） |
| `CONTEXT.md` | ✅ 仅追加报告条目 |
| `skills/` | ❌ 只读 |
| `AGENTS.md`（本文件） | ❌ 只读 |
| 其他子项目任意路径 | ❌ 禁止 |
| 全局 `AGENTS.md` / `CLAUDE.md` / `scripts/` | ❌ 禁止 |
| `.env` | ❌ 绝对禁止 |

---

## §5 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"边界区"，已列出报告禁止重复生成
2. 转录中未出现的引用、数据、人物言论禁止推测
3. 关键引用必须保留原文（哪怕标点残缺），不能重写
4. 若转录质量极差（polish 失败 + 内容难以理解），在报告 limitations 中标注，不强行总结
5. 跨项目引用需用户明确授权（CLAUDE.md 规则：默认不跨项目交叉引用）

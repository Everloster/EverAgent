# Learning Projects Task Board

> 本文件为自动生成视图，由 `scripts/task_board_aggregator.py` 维护
> **请勿直接编辑**，编辑将覆盖
> 任务权威源：各项目的 `.project-task-state`，以及根目录的 `/.project-task-state`（global 任务）
> 更新日期：**2026-06-18**

---

## 使用原则

1. 同一时间同一子项目只允许一个 Agent 写入。
2. 领取前先运行 `python3 scripts/execution_validator.py --mode=input --task-id=TXXX --project=<project>`。
3. 输入校验通过后立即获取项目锁：`python3 scripts/project_lock.py acquire --project=<project> --task-id=TXXX --agent=<AgentName>`。
4. 完成任务后先运行输出校验，再提交、推送，最后释放项目锁。
5. `claimed` / `in_progress` / `help_needed` 超过 72h 的任务会显示在“超时任务”区块，建议改为 `abandoned` 或人工 `reopen`。

---

## 项目进度概览

| 项目 | 当前状态 | 论文/文本精读 | 知识/概念报告 | 知识报告比 |
|------|----------|:---:|:---:|:---:|
| `ai-learning` | 🟢 | 40 | 31 | 44% |
| `ai-practice` | 🔴 | 0 | 0 | 0% |
| `biology-learning` | 🟡 | 11 | 4 | 27% |
| `cs-learning` | 🟢 | 24 | 6 | 20% |
| `philosophy-learning` | 🟡 | 13 | 3 | 19% |
| `podcast-learning` | 🔴 | 1 | 0 | 0% |
| `psychology-learning` | 🟡 | 12 | 4 | 25% |

---

## 任务队列

### 最近完成（自动生成）

```yaml
- id: T057
  project: ai-practice
  type: maintenance
  target: "SkillOS 技能库策展小型实验复现"
  value: "在 ai-practice 中实现一个可本地运行的 SkillRepo + heuristic curator 缩尺实验，模拟 grouped task streams、技能新增/更新/删除、reuse 对后续任务成功率和步数的影响，并产出实验笔记与 wiki 更新"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: EverAgent
  claimed_at: 2026-05-13T17:37:22+08:00
  started_at: 2026-05-13T17:37:26+08:00
  done_at: 2026-05-13T17:50:10+08:00

- id: T056
  project: ai-learning
  type: paper_analysis
  target: "SkillOS: Learning Skill Curation for Self-Evolving Agents (2026)"
  value: "精读 arXiv:2605.06614，聚焦自进化 Agent 的 SkillRepo、SkillCurator、grouped task streams、composite reward 与 GRPO 训练配方，并更新 CONTEXT/PAPERS_INDEX/wiki"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: EverAgent
  claimed_at: 2026-05-13T17:36:23+08:00
  started_at: 2026-05-13T17:36:36+08:00
  done_at: 2026-05-13T17:50:06+08:00

- id: T055
  project: cs-learning
  type: knowledge_report
  target: "Tailscale / WireGuard / VPN 原理"
  value: "系统梳理现代 VPN、WireGuard、NAT 穿透、DERP 中继、私有组网、ACL 与 Zero Trust 网络访问模型；面向 iPad + Termius 远程连接 MacBook 的工程实践"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: EverAgent
  claimed_at: 2026-05-09T16:30:46+08:00
  started_at: 2026-05-09T16:30:49+08:00
  done_at: 2026-05-09T16:34:55+08:00

- id: T053
  project: ai-learning
  type: knowledge_report
  target: "1M Long Context 在预训练、后训练与线上推理阶段的技术含义"
  value: "围绕 1M 上下文窗口，系统拆解预训练中的长序列建模/位置编码/注意力机制，后训练中的长上下文检索与指令对齐，线上推理中的 token budget/KV cache/prefill 延迟/RAG 取舍，并沉淀 wiki 概念页"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: EverAgent
  claimed_at: 2026-05-07T12:26:49+08:00
  started_at: 2026-05-07T12:26:56+08:00
  done_at: 2026-05-07T12:38:16+08:00
  context_links:
    - ai-learning/AGENTS.md
    - ai-learning/CONTEXT.md
    - ai-learning/skills/concept_deep_dive/SKILL.md
    - ai-learning/reports/knowledge_reports/Long_Context_1M_三阶段深度解析_20260507.md
    - ai-learning/wiki/concepts/long_context_systems.md

- id: T054
  project: ai-practice
  type: maintenance
  target: "Long Context 1M 机制缩尺代码模拟实验"
  value: "在 ai-practice 中新增可运行长上下文机制实验：用小模型/小窗口模拟预训练 max_seq_len 与位置编码、后训练 needle-in-a-haystack SFT 数据、推理阶段 full-context vs RAG prompt packing/token budget/KV cache 成本观测，并产出实验笔记与 wiki 更新"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: EverAgent
  claimed_at: 2026-05-07T12:26:49+08:00
  started_at: 2026-05-07T12:26:56+08:00
  done_at: 2026-05-07T12:38:16+08:00
  context_links:
    - ai-practice/AGENTS.md
    - ai-practice/CONTEXT.md
    - ai-practice/LEARNING_PATH.md
    - ai-practice/skills/experiment_analysis/SKILL.md
    - ai-practice/src/long_context_simulation.py
    - ai-practice/experiments/exp_006_long_context_1m_simulation.md
    - ai-practice/wiki/concepts/long_context_simulation.md

- id: T052
  project: biology-learning
  type: maintenance
  target: "扩充女童初潮提前与中枢性性早熟报告：纳入2022中国专家共识PDF全文与国际前沿论文分析"
  value: "基于用户提供的2022中国CPP专家共识PDF，补充诊断阈值、检查参数、治疗指征、监测安全性，并增加权威前沿论文逐篇分析"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-05-05T11:31:50+08:00
  started_at: 2026-05-05T11:31:52+08:00
  done_at: 2026-05-05T11:35:39+08:00
  context_links:
    - biology-learning/reports/concept_reports/女童初潮提前与中枢性性早熟_深度研究报告.md
    - biology-learning/wiki/concepts/central_precocious_puberty.md

- id: T051
  project: biology-learning
  type: concept_report
  target: "女童月经初潮提前与中枢性性早熟：国内临床经验、国际诊疗进展与家庭决策指南"
  value: "围绕三年级女童来月经/初潮提前问题，结合中国临床共识与国际前沿研究，完成临床决策导向深度研究报告"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-05-05T11:19:19+08:00
  started_at: 2026-05-05T11:19:22+08:00
  done_at: 2026-05-05T11:23:38+08:00
  context_links:
    - biology-learning/AGENTS.md
    - biology-learning/CONTEXT.md
    - biology-learning/reports/concept_reports

- id: T046
  project: ai-learning
  type: knowledge_report
  target: "LLM 国内外主流评估体系详解"
  value: "系统解读大模型基准评测、国内外主流评测网站与 leaderboard、以及评测项与应用场景的匹配优先级"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-29T11:03:11+08:00
  started_at: 2026-04-29T11:03:12+08:00
  done_at: 2026-04-29T11:09:44+08:00
  context_links:
    - reports/knowledge_reports/LLM_评估体系_深度解析_20260429.md
    - wiki/concepts/llm_evaluation_systems.md

- id: T043
  project: ai-learning
  type: knowledge_report
  target: "MIT 2026 AI 三条主线：LLMs+、世界模型、Agent 编排"
  value: "基于 MIT Technology Review EmTech AI 2026 Top 10 与 TechTarget 访谈，系统化拆解 LLMs+、World Models、Agent Orchestration 三条主线及 AAIF/MCP/Agents.md 标准化趋势"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-27T12:02:00+08:00
  started_at: 2026-04-27T12:03:00+08:00
  done_at: 2026-04-27T12:20:00+08:00
  context_links:
    - reports/knowledge_reports/MIT_2026_AI_三条主线_深度研究报告.md
    - wiki/concepts/llms_plus.md
    - wiki/concepts/world_models.md
    - wiki/concepts/agent_orchestration.md

- id: T049
  project: biology-learning
  type: paper_analysis
  target: "Shen et al. (2023) Effects of exercise on circadian rhythms in humans"
  value: "基于 Frontiers 官方开放全文完成 P07 运动对人体昼夜节律影响综述精读，更新 CONTEXT/PAPERS_INDEX/wiki"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-04-25T22:35:17+08:00
  started_at: 2026-04-25T22:35:17+08:00
  done_at: 2026-04-25T22:35:17+08:00
  context_links:
    - biology-learning/AGENTS.md
    - biology-learning/CONTEXT.md
    - biology-learning/papers/PAPERS_INDEX.md
    - biology-learning/reports/paper_analyses/P07_youngstedt_exercise_circadian_2023.md

```

### Global Tasks

```yaml
- id: T012
  project: global
  type: maintenance
  target: "github-trending-analyzer 周报自动化"
  value: "目前靠手动触发, 可用 schedule 技能自动化"
  priority: P3
  required_capability: full_admin
  status: open
  claimed_by: null
  claimed_at: null

```

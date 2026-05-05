# Learning Projects Task Board

> 本文件为自动生成视图，由 `scripts/task_board_aggregator.py` 维护
> **请勿直接编辑**，编辑将覆盖
> 任务权威源：各项目的 `.project-task-state`，以及根目录的 `/.project-task-state`（global 任务）
> 更新日期：**2026-05-05**

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
| `ai-learning` | 🟢 | 39 | 30 | 43% |
| `ai-practice` | 🔴 | 0 | 0 | 0% |
| `biology-learning` | 🟡 | 11 | 4 | 27% |
| `cs-learning` | 🟢 | 24 | 5 | 17% |
| `philosophy-learning` | 🟡 | 12 | 3 | 20% |
| `psychology-learning` | 🟡 | 12 | 3 | 20% |

---

## 任务队列

### 最近完成（自动生成）

```yaml
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

- id: T048
  project: ai-learning
  type: paper_analysis
  target: "Silver et al. (2017) AlphaZero self-play reinforcement learning"
  value: "基于本地 PDF 24_alphago_zero_2017.pdf 的实际 AlphaZero 内容完成精读，更新 CONTEXT/PAPERS_INDEX/wiki"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-25T22:35:01+08:00
  started_at: 2026-04-25T22:35:01+08:00
  done_at: 2026-04-25T22:35:01+08:00
  context_links:
    - ai-learning/AGENTS.md
    - ai-learning/CONTEXT.md
    - ai-learning/papers/24_alphago_zero_2017.pdf
    - ai-learning/reports/paper_analyses/43_alphago_zero_2017.md

- id: T047
  project: biology-learning
  type: paper_analysis
  target: "Thomas et al. (2020) Circadian rhythm phase shifts caused by timed exercise vary with chronotype"
  value: "基于 JCI Insight/PMC 开放全文完成 P05 定时运动与时型相位移动精读，更新 CONTEXT/PAPERS_INDEX/wiki"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-04-25T22:01:07+08:00
  started_at: 2026-04-25T22:01:11+08:00
  done_at: 2026-04-25T22:01:14+08:00
  context_links:
    - biology-learning/AGENTS.md
    - biology-learning/CONTEXT.md
    - biology-learning/papers/PAPERS_INDEX.md
    - biology-learning/reports/paper_analyses/P05_thomas_exercise_phase_chronotype_2020.md

- id: T050
  project: ai-learning
  type: paper_analysis
  target: "Hinton, Vinyals & Dean (2015) Distilling the Knowledge in a Neural Network"
  value: "基于本地 PDF 23_distilling_2015.pdf 完成知识蒸馏原始论文精读，更新 CONTEXT/PAPERS_INDEX/wiki"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: NeuronAgent
  claimed_at: 2026-04-25T22:00:32+08:00
  started_at: 2026-04-25T22:00:37+08:00
  done_at: 2026-04-25T22:00:51+08:00
  context_links:
    - ai-learning/AGENTS.md
    - ai-learning/CONTEXT.md
    - ai-learning/papers/23_distilling_2015.pdf
    - ai-learning/reports/paper_analyses/42_distilling_2015.md

- id: T045
  project: ai-practice
  type: maintenance
  target: "同步 exp_005 后的 ai-practice 上下文与 wiki 导航"
  value: "ai-practice 已有 exp_005 MoE Transformer 教学笔记；检查 README/CONTEXT/wiki/index/log 是否一致，补齐导航和边界说明，不新增实验"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: PracticeAgent
  claimed_at: 2026-04-24T18:03:29+08:00
  started_at: 2026-04-24T18:03:29+08:00
  done_at: 2026-04-24T18:03:30+08:00
  context_links:
    - ai-practice/AGENTS.md
    - ai-practice/CONTEXT.md
    - ai-practice/README.md
    - ai-practice/wiki/index.md
    - ai-practice/experiments/exp_005_moe_transformer.md

- id: T043
  project: biology-learning
  type: maintenance
  target: "修正 CONTEXT 防幻觉边界与导航状态"
  value: "biology-learning 已新增 P02/P03/P04/P17/P26 等报告，但 CONTEXT 边界仍称除 P01/P08/P09/P25 外其余未独立精读；需要修正边界、下一步推荐与导航描述，保持与已有报告一致"
  priority: P1
  required_capability: task_executor
  status: done
  claimed_by: BioAgent
  claimed_at: 2026-04-24T18:03:29+08:00
  started_at: 2026-04-24T18:03:29+08:00
  done_at: 2026-04-24T18:03:29+08:00
  context_links:
    - biology-learning/AGENTS.md
    - biology-learning/CONTEXT.md
    - biology-learning/reports/paper_analyses
    - biology-learning/reports/concept_reports

- id: T044
  project: philosophy-learning
  type: maintenance
  target: "清理 CONTEXT 防幻觉边界重复条目并同步最新覆盖"
  value: "philosophy-learning CONTEXT 的防幻觉边界存在重复条目，且最新 Gettier/Russell/Singer 等完成情况需要让边界描述更一致；只做元信息维护，不新增报告"
  priority: P2
  required_capability: task_executor
  status: done
  claimed_by: SocratesAgent
  claimed_at: 2026-04-24T18:03:29+08:00
  started_at: 2026-04-24T18:03:29+08:00
  done_at: 2026-04-24T18:03:29+08:00
  context_links:
    - philosophy-learning/AGENTS.md
    - philosophy-learning/CONTEXT.md
    - philosophy-learning/reports/text_analyses
    - philosophy-learning/wiki/index.md

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

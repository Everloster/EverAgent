# Agent Harness / 进化式 Harness（脚手架与自动优化）

> 维护日期：2026-07-07 | 分类：AI Agent / Scaffolding / 自进化
> 关联报告：`reports/paper_analyses/46_evolve_the_harness_2026.md`、`reports/knowledge_reports/Agent_Harness_三大设计流派解析.md`、`reports/knowledge_reports/Agent_自进化技术路径深度解析.md`、`reports/knowledge_reports/Agent_Harness请求全链路_深度解析_20260709.md`（报文级请求全链路 + 上下文膨胀治理）

---

## 概念定义

**Agent Harness（脚手架 / 驾驭框架）** 是包裹在 LLM **外面**的所有工程结构，它本身不产生智能，而是**约束、引导、组织**模型能力。区别于模型权重（训练学到的固定数值）和单次调用的激活值，Harness 是"模型之外、可被人直接编辑"的那一层。

一个 Agent 系统的三层：
| 层 | 内容 | 可变性 |
|----|------|--------|
| ① 模型权重 | 训练得到的参数 | 靠训练/微调改（贵） |
| **② Harness** | **系统提示词、few-shot、工具定义、校验/后处理代码、编排逻辑** | **直接编辑（便宜）** |
| ③ 激活 | 单次前向的当下神经活动 | 随输入自然变化 |

**Harness 内部再分两类**（这是关键区分）：
- **②a 提示词类（prompt playbook）**：系统提示、指导语、few-shot——软的、靠模型理解、**模型专属、换模型会失效**。
- **②b 确定性代码类（deterministic code）**：工具、校验器、后处理修复——硬的写死逻辑、**零 token、可跨模型迁移**。

---

## 核心洞察：进化 Harness ≠ 训练模型

「不要训模型，进化 harness」指**只优化第②层，冻结①层权重**。Niklaus (2026) 一手实证：

- 同一冻结模型（DeepSeek-V4-Pro）在法律基准 LAB 上，held-out 通过率 **63.4%→80.1%**（只改 harness）。
- **最强 6 处改动里 5 处是 ②b 确定性代码，不是 ②a 提示词**（"mismanaged geniuses hypothesis"：模型是马虎的天才，失分多在交付格式而非能力）。
- 贡献最大的单点：`deliverable_landing_gate`——把写错目录/名字的交付文件挪回正确位置，纯代码零 token。
- **迁移性**：代码类改动跨模型迁移好（同家族小号 +14.4 点）；提示词 playbook 不跨家族（异构模型仅 +0.4 点，甚至倒扣）。

> ⚠️ **辟谣**："harness 与模型无关"是错的——Pi 框架比原版 LAB 低 18 点、prompt 换家族失效，说明 **harness 与模型强耦合**。正确表述是"**harness 的优化空间被严重低估**"。

---

## Harness 会被 Bitter Lesson 反杀吗？

见讨论型报告《Bitter Lesson vs Agent Harness 推演与网上观点审阅》（深度专业版）与《AI 越来越强，我们给它搭的脚手架会被自己淘汰吗？》（`reports/knowledge_reports/Bitter_Lesson_vs_Harness_科普讲解_20260720.md`，师傅/徒弟类比科普版）。结论：**分层判生死**——
- **会被砍（"how"/知识层）**：提示词 playbook、固定编排/DAG、专职子代理固定分工、补模型缺陷的 workaround（如 JSON retry）。判据：填补的是"会被 scaling 填平的能力缺口"。
- **砍不到（"what"/底座层）**：高风险场景的确定性**安全闸门**（如 never-push）、工具/环境接口、self-reinforcing 的极简工具（todo_write）、**进化循环本身（=Search，Sutton 钦点）**。
- **两把镰刀**：模型 scaling（agentic-RL 训掉"自我管理赤字"）+ 环境生态适配（MCP/agent-native API 从另一头溶解胶水层）。
- 业界共识（PostHog/Tavily/Minh Pham）：harness 应是"**thin interface to scalable compute, not where you hide the intelligence**"。

---

## 进化式优化的机制（Meta-Harness loop）

```
现有 harness 跑 dev → 评判打分 → 挑失败案例
  → 提议者(强模型)提出一处 harness 改动
  → 新旧各跑 N 遍取均值 → 新的高 ≥ min_delta 才晋级
  → 循环
```

**打分公式决定进化方向**（Niklaus 版）：
```
score = pooled_criterion_rate + 0.5×all_pass_rate − 0.005×tokens_per_million
```
带 **token 惩罚项** → 天然偏好零 token 的确定性代码。**奖励函数塞什么，就进化出什么形态。**

**家族谱系**：GEPA（进化提示词）、AlphaEvolve/ShinkaEvolve（进化代码）、Darwin Gödel Machine（自改 agent）、Karpathy autoresearch（进化训练配方）、Meta-Harness loop（进化 harness，冻结模型）。

**成本数字（2026-07-19 核实）**：优化后 DeepSeek V4 Pro 跑 100 任务约 $77.3 vs Sonnet 4.6 $546.9 ≈ **1/7 成本**（一手图表数据）。口径：同一条 token 轨迹 × 刊例价估算、仅 agent rollout 不含 judge、基线专指 Sonnet 4.6。详见报告 46 追问深入节。

---

## 相关概念

- [[./agent_systems.md|Agent Systems]]：Harness 是 Agent 系统"LLM+Tools+Memory"三要素的组织层。
- [[./agent_orchestration.md|Agent Orchestration]]：编排是 Harness 的一部分。
- [[./agent_observability.md|Agent Observability]]：进化循环依赖对失败案例的可观测。

---

## 参考文献

- Joel Niklaus, "Don't Train the Model, Evolve the Harness", HuggingFace Space, 2026-07-01
- Meta-Harness loop, arXiv:2603.28052, 2026
- Harvey, Legal Agent Benchmark (LAB), 1251 tasks
- Andrej Karpathy, `karpathy/autoresearch` & `nanochat`, 2026

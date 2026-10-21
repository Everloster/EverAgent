---
title: "ALTK-Evolve：学习型 Memory 如何让 Agent 在服务任务中持续改进"
domain: "ai-learning"
report_type: "text_analysis"
status: "completed"
updated_on: "2026-10-22"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["agent_memory", "memory_middleware", "self_improving_agents", "altk_evolve", "tau2_bench", "context_engineering"]
related_concepts: ["procedural_memory", "experience_distillation", "reliability_evaluation", "memory_governance"]
related_entities: ["ibm_research", "agenttoolkit", "sierra_research"]
---

# ALTK-Evolve：学习型 Memory 如何让 Agent 在服务任务中持续改进

> 核心原文：IBM Research，[ALTK-Evolve learns a customer-service playbook from experience](https://huggingface.co/blog/ibm-research/altk-evolve-bc)，2026-10；配套技术报告：[Memory as Middleware for Self-Improving AI Agents](https://arxiv.org/abs/2609.32091)，2026-09-25；实现：[AgentToolkit/altk-evolve](https://github.com/AgentToolkit/altk-evolve)。
>
> 核验日期：2026-10-21。本文将 IBM 的实验结果、系统愿景与本文分析分开表述；排行榜位置只代表 IBM 保存的 2026-10-12 快照。

## x → f → f(x)

- **x：作者在解决什么问题？** Agent 每次启动都像失忆：它会重复犯错，而把所有经验直接塞进 prompt 又会造成成本、冲突和上下文污染。
- **f：作者的回答是什么？** 把执行轨迹蒸馏为带来源、适用条件和支持次数的行为规则，经过去重与冲突处理后按任务取回；进一步把这套能力抽成可跨 Agent、跨存储工作的 Memory middleware。
- **f(x)：接受这个答案后该怎么做？** 把“记住更多”改成“有门槛地学习、按需取回、持续评估、可撤销治理”。记忆必须同时接受效果、成本与控制三条约束。

---

## 一页结论

ALTK-Evolve 最有价值的地方不是又做了一个向量库，而是把 Agent Memory 重新定义为一个**经验编译与治理层**：原始轨迹是源材料，guideline 是可执行的中间表示，检索负责按任务装载，support count、provenance、namespace 与 visibility 则负责控制它何时可信、影响谁、能否共享。

实验给出了一个很强、但边界清楚的信号：在 τ²-bench 的政策约束型客服任务中，只给 stock ReAct Agent 追加从训练任务中自动提炼的 guidelines，不更新模型权重，也不使用人工标注，GPT-4.1 的 Retail `Pass^4` 从 **57.5% 提升到 67.5%**；Airline 的最佳 `Pass^4` 从 **35.0% 提升到 45.0%**。这说明部署侧经验可以显著改善“同一任务多次都做对”的可靠性。

同时，更多记忆并不恒定更好。Retail 需要 292 条 lossless guidelines 才获得最佳结果；Airline 反而是 14 条高支持规则比 101 条完整规则更可靠。**[推测] Memory dosage 是一个需要按领域验证的控制参数。** 第 6 节把 dosage 连同准入（admission）、治理（governance）与评估（evaluation）收成一条可落地的闭环。

这项工作还没有证明 Agent 会开放式地“越用越聪明”。它证明的是：在有可验证结果、任务分布相近、训练与测试隔离的环境里，把历史轨迹提炼成程序性规则，能够提升后续任务表现。跨分布迁移、长期遗忘、恶意经验、错误规则传播与真实生产治理仍是开放问题。

---

## 1. 证据是什么，强到什么程度

| 来源 | 提供的证据 | 主要边界 |
|---|---|---|
| [S1：IBM 博客](https://huggingface.co/blog/ibm-research/altk-evolve-bc) | τ²-bench Retail/Airline 的 held-out 与 leaderboard 结果、成本、轮次数、guideline 数量 | 厂商自报；博客未给 held-out 置信区间或第三方复现；排行榜为时间点快照 |
| [S2：Memory middleware 技术报告](https://arxiv.org/abs/2609.32091) | 六类系统问题、参考架构、AppWorld 评估与未完成方向 | preliminary IBM Technical Report，尚非同行评审定论 |
| [S3：altk-evolve 仓库](https://github.com/AgentToolkit/altk-evolve) | MCP 工具、文件/pgvector/Milvus 后端、namespace、visibility、provenance 等实现表面 | 有实现不等于已验证全部论文主张；当前 README 还警告 dashboard/API 没有认证，不适合直接暴露到生产网络 |
| [S4：τ²-bench](https://github.com/sierra-research/tau2-bench) | 政策约束型客服任务、工具与最终数据库状态判定 | 仍是模拟用户和有限领域，不能直接代表真实客服生产流量 |

S1 的实验比单次成功率更重视可靠性。每个测试任务运行四次：

- **Mean Accuracy**：四次尝试的平均成功率；
- **Pass⁴**：同一任务四次全部成功才算通过。

这一区分很重要。一个 Agent 平均 75% 成功，仍可能在同类真实请求中每四次错一次；`Pass^4` 更接近“能不能稳定托付”。

---

## 2. ALTK-Evolve 到底怎样“学习”

### 2.1 它学习的是程序性规则，不是模型权重

从一次执行到下一次执行的完整流水线可以压缩为六步：

1. **Capture**：保存 Agent 的任务轨迹、工具调用、结果和失败；
2. **Extract**：从轨迹中识别任务与子任务，提炼可复用经验；
3. **Generalize**：去掉具体人名、订单号等一次性实体，保留操作结构；
4. **Consolidate**：聚类、去重、合并相似经验，并处理冲突；
5. **Retrieve**：根据新任务召回适用 guideline；
6. **Inject**：把规则作为 prompt 级上下文交给 Agent。

例如，一次失败可能被编译成：“修改订单前先验证身份；若没有邮箱，则用姓名与邮编调用指定查询工具。”这不是事实型知识，而是“遇到什么条件时按什么顺序行动”的程序性记忆。

**关键是区分三种数据形态：原始轨迹、gist 与 guideline。** 这条流水线上流动着三种性质不同的对象，把它们混为一谈，就会误判“记忆里到底存了什么、丢掉了什么”：

| 形态 | 是什么 | 怎么产生 | 信息损失 | 在系统中的角色 |
|---|---|---|---|---|
| 原始轨迹 | 一次任务的完整执行历史：指令、工具调用、中间结果、失败 | Capture 阶段保存 | 相对完整，但一次性、体积大 | 事实源与审计凭据，一切复核的最终依据 |
| gist | 按用途生成的摘要，保留指向 durable original 的指针 | 从轨迹中按当前用途提炼 | 有损：只保留该用途需要的切片 | 回查索引——需要时沿指针回到原始轨迹 |
| guideline | 带适用条件、支持度与来源的程序性规则 | 从一个或多个轨迹经 Extract → Generalize → Consolidate 提炼 | 有损：抽象与合并会抹掉细节和前置条件 | 程序性记忆的载体，与其他 typed entity 一样可被检索并进入上下文 |

一句话概括：**轨迹是账本，事实与摘要是索引，guideline 是最接近“可执行策略”的形态——但不是唯一会影响行为的记忆。** 在 middleware 的设计里，semantic facts、episodic/tool gists 与 procedural guidelines 都是可被 Retrieve 召回并进入上下文的 typed entities；它们共享 provenance、ownership、visibility 这类通用 entity metadata，guideline 特有的是 category、rationale、steps、support count 等程序性字段。因此回溯不必固定走 guideline → gist → 轨迹的链路，每类 entity 都通过 source task/session provenance 指回产生它的任务与会话。这也预先解释了 5.2 节的“lossless”：它只表示 consolidation 后不再按 support 阈值裁剪，绝不表示从轨迹到 guideline 的提炼是无损的。

这条路径的优势是更新快、可解释、可删除，也不需要重新训练模型。代价是每次调用都可能增加输入 token，而且自然语言规则之间可能冲突。

### 2.2 support count 是经验的粗粒度置信度

每条 guideline 记录它从多少个不同训练任务中被提取出来。IBM 比较三档：

| 配置 | Retail | Airline | 含义 |
|---|---:|---:|---|
| baseline | 0 | 0 | 不追加经验 |
| sup3 | 31 | 14 | 只保留至少被 3 个任务支持的规则 |
| lossless | 292 | 101 | 保留 consolidation 后所有规则，support ≥ 1 |

support 不是严格概率。多个任务可能高度相似，同一错误也可能被模型重复概括；但它至少把“一次偶然心得”和“反复出现的规律”区分开，为记忆 admission、排序和淘汰提供了一个可计算信号。

### 2.3 Middleware 比“一个 Memory Store”多了什么

S2 把问题拆成六个系统关注点：

1. **双向可插拔**：上接 Claude Code、Codex、IBM Bob 等不同 host，下接文件、pgvector、Milvus 等后端；
2. **Host-native interposition**：通过 hook、plugin、instruction import 或 MCP，在执行前 recall、执行后 capture；
3. **多租户隔离**：按用户、项目、任务和记忆类型划 namespace；
4. **写路径一致性**：新增经验不能只 append，要决定 add、merge、supersede、quarantine 或 reject；
5. **共享与 provenance**：私有默认、显式发布，并保留来源任务、创建方式和 owner；
6. **生命周期治理**：支持查看、审批、过期、压缩、删除和审计。

因此，真正的抽象不是 `save(text)` / `search(query)`，而是：**什么经验有资格改变未来行为，以及谁能看见、撤销和追责这种影响。**

S2 的 Table 2 也明确区分“已实现”和“研究方向”。当前实现已经覆盖多 host/后端、namespace、基本 visibility/provenance、generalize/cluster/consolidate 与删除；仍待解决的包括统一 host/store 标准、sidecar、层级与角色权限、正式事务语义、federation policy、完整 audit trail，以及 retention/eviction policy。论文的 middleware 蓝图明显大于当前产品覆盖。

---

## 3. τ²-bench：提升发生在哪里

### 3.1 GPT-4.1 held-out test 结果

| 领域 | 配置 | Mean Accuracy | Pass⁴ |
|---|---|---:|---:|
| Retail，40 个测试任务 | baseline | 78.1% | 57.5% |
|  | sup3 | 78.8% | 60.0% |
|  | lossless | **82.5%** | **67.5%** |
| Airline，20 个测试任务 | baseline | 57.5% | 35.0% |
|  | sup3 | 60.0% | **45.0%** |
|  | lossless | **65.0%** | 40.0% |

Retail 中，完整规则集同时提高平均成功率和稳定性。Airline 中，完整规则集的平均成功率最高，但 `Pass^4` 低于精简规则集。**[推测]** 这可能意味着长尾规则在部分任务上有帮助，也会在另一些任务上制造干扰或冲突。

实验控制也较干净：Agent 使用 τ²-bench 原生 ReAct scaffold；Agent 模型为 GPT-4.1，用户模拟器为 GPT-5.5；每个任务四次试验；train 轨迹产生 guidelines，test 使用固定规则。核心变量是追加的 guideline block。

### 3.2 成本增加在输入侧，没有增加对话轮数

| 领域 | baseline 成本/会话 | lossless 成本/会话 | 增幅 |
|---|---:|---:|---:|
| Retail | $0.084 | $0.139 | +65% |
| Airline | $0.081 | $0.107 | +32% |

这里的两个表不是同一总体：成本来自 **full base split（train ∪ test）** 上 Agent 与用户模拟器合计的每会话 LLM 成本；轮次数来自 **held-out test split**，并且只比较同一 task、同一 seed 在 baseline 与 guideline 两侧都成功的 matched runs。

在这组 matched runs 上，lossless 的平均 assistant turns 反而略少：Retail 为 **10.59 → 10.16（n=111）**，Airline 为 **9.15 → 8.82（n=40）**。这说明规则主要通过减少试错改善路径，而成本来自每轮重复携带更长的 prompt。Prompt caching 可能降低实际成本，但 S1 没有给出启用缓存后的实测账单。

### 3.3 强模型仍能从外部经验获益

IBM 还用 GPT-5.5 在 Airline 的 20 个 held-out tasks 上重新提炼并使用自己的 guidelines：

| 配置 | Accuracy | Pass⁴ |
|---|---:|---:|
| baseline | 72.5% | 55.0% |
| sup2，103 条 | 80.0% | 70.0% |
| lossless，146 条 | **82.5%** | **70.0%** |

这个单一 Airline/GPT-5.5 设置为“外部 Memory 只是在给弱模型打补丁”提供了一个反例；它还不足以证明所有强模型和领域都能获得同等收益。至少在这里，基础模型更强后，部署环境的具体政策、工具顺序和失败经验仍能提供增量。

**S1 另报了一组 leaderboard 数字，口径与上表不同，必须一眼区分。** 读到 ALTK-Evolve 的任何 τ²-bench 数字时，先问三个问题：哪套样本？是否 held-out？提交状态如何？

| 数字 | 样本 | 是否 held-out | 含义 |
|---|---|---|---|
| Retail lossless `Pass^4 = 67.5%`（§3.1 表） | 40 个 held-out test 任务 × 4 次试验 | 是 | train/test 隔离下的泛化结果 |
| Retail `Pass^4 = 67.54%`（[PR #542](https://github.com/sierra-research/tau2-bench/pull/542) submission） | 114 个 full base（train ∪ test）任务 × 4 次试验 | 否 | 包含提炼 guidelines 所用的 train tasks，是提交口径成绩 |
| Airline `Pass^4 = 82.0%`（[PR #551](https://github.com/sierra-research/tau2-bench/pull/551) submission） | 50 个 full base 任务 × 4 次试验 | 否 | 同上；Agent 为 GPT-5.5 |

注意一个容易踩的坑：67.54% 四舍五入后恰好等于 held-out Retail 的 67.5%。两个数字样本不同、含义不同，数值相同纯属巧合，不能互相印证。

提交状态也要一并读出：在 IBM 保存的 2026-10-12 快照中，Retail 67.5% 高于 RAFT-30B-A3B 的 61.4%，Airline 82.0% 位于首位；但截至本次复核，两个 PR 仍为 open，submission 标记为 custom、`modified_prompts=true`，预期显示为 `Unverified`。PR 附有逐任务 trajectories，但本报告没有逐条重放。因此这些数字应理解为项目方提交的 full-base 快照，不能写成独立复现或已正式合并的长期 SOTA。

---

## 4. AppWorld 给了第二种验证

S2 在 AppWorld Test-Normal 上使用同一 GPT-4.1 Agent 与推理循环，只改变是否接入 Memory：

| 指标 | 无 Memory | altk-evolve |
|---|---:|---:|
| Aggregate task-goal completion | 69.6% | 73.2% |
| Aggregate scenario-goal completion | 50.0% | 64.3% |
| Hard scenario-goal completion | 19.1% | 47.6% |

task-goal 衡量单任务完成；scenario-goal 要求一个场景内所有任务都完成，因此对连锁错误更敏感。**[推测]** 提升集中在 scenario 与 hard tier，可能说明 Memory 的最大价值不是让简单任务再高几分，而是减少长链路中的重复失误；这与 τ²-bench 的 `Pass^4` 方向一致。

不过 S2 明确把结果称为 feasibility signal，而非完整评估。报告没有展示跨模型、跨组织、长期在线漂移与恶意记忆条件下的系统性结果。

---

## 5. 最容易误读的三点

### 5.1 “自我改进”不等于自主改写模型

这里没有权重更新。改进来自外部规则被再次注入上下文。它更接近自动生成并维护 runbook，而不是模型能力永久增长。

### 5.2 “lossless”不代表没有信息损失

S1 的 lossless 指 consolidation 后不再按 support 阈值裁剪，并不意味着从原始轨迹到 guideline 的 LLM 提炼无损。抽象、聚类和合并本身都可能遗漏条件或制造过度泛化。

### 5.3 排名提升不等于生产风险已经解决

τ²-bench 的最终数据库状态提供了强验证器，这是这类学习能成功的重要前提。开放式知识工作往往没有同样明确的 reward；如果成功判定不可靠，系统可能把侥幸成功、错误自评或被攻击的轨迹固化为规则。

---

## 6. 对实际 Agent 系统的可用设计

把 §2–§5 的证据收拢成一条可落地的运营闭环，它依次回答四个问题：什么经验有资格进来（admission）、进来后用多少（dosage）、谁能看见与撤销（governance）、怎么知道它仍在帮忙（evaluation）。四个阶段首尾相接，评估的产出回流为准入端的降权、隔离与淘汰决策：

```text
① Admission 准入 ──► ② Dosage 剂量与取回 ──► ③ Governance 治理
        ▲                                            │
        │                                            ▼
        └────────── ④ Evaluation 评估 ◄──────────────┘
```

**① Admission：什么经验有资格改变未来行为。**

- 前置条件是可验证结果——工具执行后的状态、测试、人工反馈或明确 outcome；没有可靠验证器的任务不应进入这个闭环（见 §5.3）；
- 对失败轨迹做 quality-weighted admission：错误动作不能被固化成正向策略，但失败原因、自我反思、failure count 与负面约束（“此路不通”）同样是有价值的记忆；successful recovery 只是高价值信号之一，不是唯一信号；
- 各类记忆按 §2.1 的形态分工入位：轨迹作事实源、gist 作摘要索引、guideline 作程序规则；所有 entity 共享 source task/session provenance 与 ownership/visibility，guideline 额外记录 support、反例、版本与 category/rationale/steps 等程序性字段。

**② Dosage：注入多少，何时注入。**

- 记忆剂量是按领域标定的控制参数，不是越多越好：Retail 需要 292 条 lossless 规则才到最佳，Airline 反而 14 条高支持规则更稳（§3.1）；
- 部署时至少对比三档——高 support 小核心、按任务检索 Top-k、完整集合——并同时看成功率、稳定性（如 Pass⁴）、输入 token 与延迟，而不是只看平均分。

**③ Governance：谁能看见，能否撤销。**

- 按类型与作用域隔离：事实、偏好、程序、政策不混在一个向量池，namespace 与 visibility 是最小实现；
- 默认私有，个人经验升级为项目或组织规则前走审批与回滚；
- 过期不只按时间：依赖的 API、政策或模型版本变更时，相关 guideline 自动进入待复核状态。

**④ Evaluation：怎么知道它仍在帮忙。**

- 持续运行无 Memory 对照组，否则模型升级、工具变化与 Memory 收益会混在一起、无法归因；
- 对照中失败的规则降权或隔离，结果回流到 ①，形成闭环。

对 Context Engineering 最直接的启示是：长期上下文不应只追求积累速度，还要有**编译、选择、过期和回放评估**。Memory 层的产出应该是可验证的 context patch，而不是不断膨胀的常驻 prompt。

---

## 7. 局限与未解决问题

1. τ²-bench 只有 Retail 40 个与 Airline 20 个 held-out tasks，样本有限，且用户由模型模拟；
2. 结果来自项目方自报；full-base leaderboard PR 附有逐任务 trajectories，但本报告未逐条重放，held-out 表也没有置信区间或第三方独立复现；
3. guideline extraction 与执行共享模型时，可能存在共同偏差；
4. support count 没有处理任务相关性、来源质量和反例强度；
5. 长期运行中的 stale memory、规则循环依赖、撤销语义和污染恢复尚未被实证解决；
6. 多租户共享会放大隐私泄露与 memory poisoning 风险；
7. AppWorld 与 τ²-bench 都有明确验证器，结论不能直接外推到研究、写作或战略判断；
8. S2 是 preliminary technical report，系统愿景大于当前实现覆盖。

---

## 8. 思考与追问

### 8.1 真正应该学习的单位是什么？

单条 guideline 方便检索，却容易丢失前置条件。更稳的单位可能是“触发条件 + 动作 + 验证器 + 失败反例 + 适用版本”的小型策略对象。下一步评估应比较自然语言规则、结构化策略与可执行检查器三种表示。

### 8.2 support 应怎样升级为可信度？

重复出现不等于正确。可以把可信度拆为：独立任务支持数、成功后验证强度、跨模型复现、最近一次命中、反例数量和来源权限。这样才能避免一个高频错误被“多数票”固化。

### 8.3 什么时候该忘记？

§6 的治理与评估阶段给出了机制（依赖版本变更触发待复核、对照失败降权隔离），但机制背后的研究问题仍未解：遗忘的信号与代价怎么权衡？一条规则多久未被命中才值得降权？工具 API 半年一变和政策逐周微调，显然需要不同的遗忘时钟；而错误丢弃一条仍然有效的规则，代价未必小于保留一条过时规则。这些权衡目前没有实证数据（见 §7 第 5 条）。

### 8.4 最值得做的下一项实验

在同一批真实 Agent 任务上比较四组：无 Memory、全部常驻、按 support 核心、按任务检索 Top-k。固定模型与 Harness，连续测成功率、重复成功率、输入 token、总轮次、错误类型和过期规则命中率。这个实验能回答 ALTK-Evolve 留下的核心工程问题：**什么时候学习型 Context 真正改善了系统，什么时候只是把历史包袱自动化。**

---

## 参考来源

1. IBM Research. [ALTK-Evolve customer-service benchmark post](https://huggingface.co/blog/ibm-research/altk-evolve-bc).
2. Jayaram et al. [Memory as Middleware for Self-Improving AI Agents](https://arxiv.org/abs/2609.32091), 2026.
3. AgentToolkit. [altk-evolve](https://github.com/AgentToolkit/altk-evolve).
4. Sierra Research. [τ²-bench](https://github.com/sierra-research/tau2-bench); [paper](https://arxiv.org/abs/2506.07982).
5. τ²-bench. [Retail leaderboard submission PR #542](https://github.com/sierra-research/tau2-bench/pull/542).
6. τ²-bench. [Airline leaderboard submission PR #551](https://github.com/sierra-research/tau2-bench/pull/551).


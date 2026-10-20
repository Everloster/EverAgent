---
title: "Plan or Retrieve First：大规模工具发现为何需要复杂度自适应路由"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-10-20"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["tool_discovery", "agent_routing", "retrieval", "plan_then_retrieve", "toolbench"]
related_concepts: ["agent_harness", "tool_use", "context_engineering"]
related_entities: ["apple"]
---

# Plan or Retrieve First：大规模工具发现为何需要复杂度自适应路由

> 论文：Mingfei Zhang、Amit Surana、Ziauddin Majid、Chenxi Wang、Michael Xu，[Plan or Retrieve First? A Scale Study of Tool Discovery Architectures](https://arxiv.org/abs/2610.19068)，Apple，2026。官方摘要页：[Apple Machine Learning Research](https://machinelearning.apple.com/research/plan-retrieve-tool-discovery)。

## 一句话总结

面对近 5 万个工具，**直接按用户原话检索适合明确的单工具请求，先把任务拆成抽象能力再检索适合复杂多工具请求；固定只用 RtP 会损失复杂任务召回，固定只用 PtR 会让简单任务质量下降并增加 token 与延迟。**

## 1. 研究问题

Agent 无法把数万个 tool schema 全部塞进上下文，因此必须先发现少量候选工具。主流做法是 Retrieve-then-Plan（RtP）：先把用户 query 做 embedding，检索相似 API，再交给模型规划。论文研究另一条路径 Plan-then-Retrieve（PtR）：模型先在看不到真实工具表的情况下生成若干 **Abstract Tool Stubs**，再拿这些“假想函数签名”去检索真实 API。

作者真正要回答的不是“规划和检索谁应该先”，而是：

```text
当 query 与真实 API 名称的耦合强弱、任务所需工具数和 registry 规模变化时，
哪种发现架构能以更低成本召回正确工具？
```

## 2. 两种架构

设：

- `q`：用户请求；
- `T`：工具注册表；
- `d_t`：工具 `t` 的文档；
- `sim(a,b)`：embedding cosine similarity；
- `k`：交给 planner 的候选工具数；
- `π`：planner 基于 query 和候选工具生成的执行计划。

### 2.1 Retrieve-then-Plan

论文把它写成：

```text
R_RtP(q) = TopK_{t∈T} sim(q, d_t)
π_RtP = π(q, R_RtP(q))
```

它保留用户原话中的产品名、proper noun 和具体操作词。优点是无额外 LLM 调用，缺点是一个 query embedding 很难同时表达多个子目标。

### 2.2 Plan-then-Retrieve

PtR 先生成 stubs：

```text
S(q) = {s1, …, sm}
R_PtR(q) = TopK_{t∈T} max_{s∈S(q)} sim(s, d_t)
π_PtR = π(q, R_PtR(q))
```

每个 stub 表示一个推测的能力，例如把“规划伦敦旅行，找酒店、做 IP forensic、换汇”拆成 `hotel_search`、`ip_forensics`、`currency`。这些名字通常并不存在，作用是把复合意图拆成多个检索锚点。

## 3. 实验设计

| 项目 | 设置 |
|---|---|
| 工具注册表 | ToolBench 去重后的 **46,984** 个 API endpoint、50 类 |
| G1 | 单工具请求，`n=200` |
| G2 | 同类别多工具请求，`n=200` |
| G3 | 跨类别多工具请求，`n=100` |
| 主实验检索预算 | `k=5` |
| Embedding / Index | GTE-base + FAISS exact nearest-neighbor |
| Planner / Stub 模型 | Gemini 2.5 Flash，temperature=0 |
| 重复 | PtR 与 planner 指标跑 4 次；RtP retrieval 为确定性 |

主要指标是相对 ToolBench gold trajectory 的 retrieval recall 与 precision。论文还报告 pass rate，但**没有实际调用 API，也没有评估参数正确性和最终答案质量**。作者以 planner 至少 **96%** 的 tool-selection fidelity 论证 retrieval 是下游行为的上界代理。

## 4. 核心结果：出现复杂度交叉

### 4.1 主结果（Table 3）

| 子集 | 指标 | RtP | PtR | 判断 |
|---|---|---:|---:|---|
| G1 | Recall | **0.372** | 0.289±0.010 | RtP 胜，`p=0.002` |
| G1 | Precision | **0.274** | 0.209±0.008 | RtP 胜，`p<0.001` |
| G1 | Pass rate | **0.884±0.015** | 0.840±0.024 | RtP 胜，`p=0.022` |
| G2 | Recall | 0.143 | **0.188±0.007** | PtR 胜，`p<0.001` |
| G2 | Precision | 0.167 | **0.204±0.007** | PtR 胜，`p=0.039` |
| G2 | Pass rate | 0.747±0.015 | **0.855±0.020** | PtR 胜，`p<0.001` |
| G3 | Recall | 0.160 | 0.172±0.008 | PtR 方向性领先，`p=0.080`，不显著 |
| G3 | Pass rate | 0.732±0.010 | **0.820±0.014** | PtR 胜，`p<0.001` |

逐 query 比较也出现翻转：G1 中 RtP 赢 **63** 条、PtR 赢 33 条；G2 中 PtR 赢 **69** 条、RtP 赢 30 条（Figure 2）。

### 4.2 交叉不是某个 k 的偶然结果

Table 1 从 `k=1` 测到 `k=20`：

- G1 始终 RtP 更高；在 `k=5` 为 0.372 vs 0.279，在 `k=20` 为 0.524 vs 0.444；
- G2 始终 PtR 更高；优势从 `k=1` 的 +0.014 扩大到 `k=20` 的 +0.066；
- G3 方向上也多为 PtR 更高，但样本较少。

注册表从约 1k 扩到 47k API 时，G1/G2 的交叉方向也保持不变；tool-selection divergence 从 1k 时的 88% 上升到 47k 时的 98%（Figure 3 / Table 10）。

## 5. 为什么会交叉：Intent–Registry Coupling

论文把机制解释为 query 与真实工具名称的耦合程度。

### G1：原话就是最好的检索键

单工具 query 常直接包含产品、API 或 proper noun。“从 Reddit 找 programming memes”中的 `Reddit` 是强信号。PtR 把它抽象成 `reddit_api_client` 或更泛化的能力名，反而破坏了精确匹配。

### G2/G3：一个 embedding 装不下多个子目标

G2 gold trajectory 平均需要 **6.5** 个 API，G1 为 5.2。PtR 每个 query 生成约 2.4–2.5 个 stub，各自锚定一个功能子需求，因此能覆盖多面意图。即便每个 stub 不完全正确，多 stub 的覆盖仍可能找回更多 gold tools。

## 6. “幻觉”在这里既是 bug 也是 feature

PtR 生成的 stub 名称有 **79%–99%** 是跨 query 唯一的，说明模型不是回忆真实 API，而是在现场发明函数名。更值得警惕的是，正确与错误匹配的 cosine similarity 几乎相同：G1 为 **0.874 vs 0.872**。Embedding 无法告诉系统这个 stub 是否“想对了”。

| 子集 | Stubs/query | 唯一名称 | Stub top-1 命中相关 API |
|---|---:|---:|---:|
| G1 | 2.1 | 98.6% | 40.6% |
| G2 | 2.4 | 93.6% | 38.3% |
| G3 | 2.5 | 79.1% | 24.8% |

看似很低的单 stub 命中率并未阻止 PtR 在复杂任务上领先，因为多个 stub 能覆盖不同功能域。但同一机制会伤害包含明确品牌词的简单 query。

这是一条重要的 Agent 工程原则：**中间表示不必字面真实才有用，但必须知道它在哪些任务分布上会系统性失真。**

## 7. 成本：PtR 不是免费的“更聪明”

PtR 多一次串行 LLM 调用，因此同时增加 token 和 wall-clock latency。Table 8：

| 子集 | RtP tokens | PtR tokens | 增幅 | Recall 变化 |
|---|---:|---:|---:|---:|
| G1 | ~226 | ~396 | **+75%** | **−0.072** |
| G2 | ~238 | ~429 | **+80%** | **+0.042** |
| G3 | ~221 | ~450 | **+104%** | +0.017 |

所以“永远先规划”是错误的。论文估算：若 G1 走 RtP、G2/G3 走 PtR，可节省约 **16% 总推理 token**，相当于减少约 **36% PtR discovery-call 开销**，同时保持每类任务中更优架构的 retrieval 质量。

作者提出的最低成本路由信号，是 RtP 本来就会产生的 top-1 cosine similarity：

- 高分、集中：query 可能明确点名工具，继续 RtP；
- 低分、分散：query 可能是抽象多目标任务，切到 PtR。

但论文没有真正训练或验证这个 classifier，这仍是后续建议。

## 8. 跨模型复现与不稳定部分

作者用 gpt-oss-120b 保持 embedding、index、数据和 `k=5` 不变进行复现（Table 11）：

- G1 仍由 RtP 领先：recall 0.372 vs 0.259±0.012；
- G2 仍由 PtR 领先：0.143 vs 0.194±0.003；
- G3 却轻微反转为 RtP 领先：0.160 vs 0.146±0.008，`p=0.035`。

因此可靠结论是 G1/G2 的复杂度交叉，而不是“所有跨类别任务都应 PtR”。G3 只有 100 条，且行为随模型变化。

## 9. 论文局限

1. 只测 ToolBench 与一种 API 命名分布，企业内部工具、MCP server、skills 和文档质量可能不同。
2. 评估是 retrieval proxy，没有执行工具、检查参数或最终任务成功率。
3. PtR 实际探索约 2–2.5 倍候选，再压回 top-k；虽然预算等价消融支持结构性解释，但两条路径计算并不完全对称。
4. 主要实验用 Gemini 2.5 Flash；gpt-oss 只初步验证，G3 已显示模型依赖。
5. 论文报告 token 开销，没有测真实端到端延迟、缓存和并发条件。
6. Stub calibration 与复杂度路由都停留在建议，未被实证验证。

## 10. 对 EverAgent 的直接启示

这篇论文可以把“按需加载”进一步细化为两种路由：

### 明确、单领域请求：直接检索

例如“更新顶尖技术博客渠道”“修改报告元数据”“查询设备服务 owner”。用户已经给出对象和动作，继续抽象会损失 proper noun，应直接命中对应 skill 或 owner。

### 复合、跨领域请求：先生成能力 stubs

例如“根据三份原文重构双仓，同时保持公开/私有隔离并建立评估”。可以先形成：

```text
context-owner audit
private/public boundary check
skill routing redesign
behavior replay evaluation
report evidence review
```

再分别检索相关 owner，而不是用整句只取一个最相似文档。

### 下一轮重构应先实验，不能直接上线

可用现有 `evals/ace-report-tasks.json` 把任务分成：

- explicit single-owner；
- multi-owner same-domain；
- cross-repo multi-domain。

比较直接路由与 stub 路由的 owner recall、无关文件读取、工具调用、token 与最终质量。论文已经警告：stubs 会抹掉 proper noun，因此产品名、路径、命令和显式 skill 名必须原样保留。

## 思考与追问

### 1. 我真正理解了什么？

工具发现不是一个固定检索问题，而是由任务复杂度决定的路由问题。先规划并不天然更聪明；它用更多成本换取多意图分解，同时可能破坏最有价值的原始词面信号。

### 2. 我还没搞懂什么？

- 用 top-1 similarity 做复杂度门时，阈值能否跨 embedding 模型和 registry 迁移？
- 企业内部工具具有更统一的命名规范，是否会削弱 PtR 的收益？
- 当参数正确性和执行失败进入评估后，retrieval recall 的领先是否仍能转化为 task success？

### 3. 下一步读什么或做什么？

把复杂度自适应路由与 Deep Review 的分段预算合并：先判断任务需要哪些 owner，再按每个部分的风险和信息密度分配复核资源。

## 来源

- [arXiv HTML](https://arxiv.org/html/2610.19068v1) · [PDF](https://arxiv.org/pdf/2610.19068)
- [Apple 官方摘要页](https://machinelearning.apple.com/research/plan-retrieve-tool-discovery)

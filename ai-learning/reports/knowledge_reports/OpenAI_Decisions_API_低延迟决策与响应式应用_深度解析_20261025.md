---
title: "OpenAI Decisions API：低延迟决策端点的请求模型、能力边界与可迁移价值"
domain: "ai-learning"
report_type: "概念深度解析"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["OpenAI", "Decisions-API", "gpt-6-luna", "classification", "routing", "latency", "agent-harness"]
---

# OpenAI Decisions API：低延迟决策端点的请求模型、能力边界与可迁移价值

> **一句话结论**：Decisions API 是 OpenAI 在 2026-10 推出并 GA 的**专用决策端点**（`POST /v1/decisions`，目前唯一支持模型 `gpt-6-luna`），它把「有界答案」的判定（probability / choice / score）从通用生成任务中剥离出来，官方宣称「比走 Responses API 的 GPT‑6 Luna 快最多 10×」且**只按输入 token 计费（$0.10/百万，缓存输入 $0.01/百万，无输出计费）**；但这个「10×」是**厂商自报、只有上限值、没有延迟分布与负载口径**，而且端点**不执行任何动作、不能请求工具、不支持文件/音频**——它本质是「把分类/路由/打分做成一次低延迟 API 调用」，而不是 agent。已有工具调用及其结果可以作为输入证据，这与“由模型发起工具调用”是两回事。

> **阅读边界**：本文实际读取了 OpenAI 一手材料：产品博客《Build more responsive apps with the Decisions API》、官方开发指南《Decisions》与《Connect voice to Decisions》、`POST /v1/decisions` 的 API 参考、官方 Changelog 与官方定价页。**未做实测，未在任何环境调用该 API**；所有性能与成本数字均为 OpenAI 官方口径。

---

## 目录

1. [问题定义：它到底解决什么](#1-问题定义它到底解决什么)
2. [请求与响应模型](#2-请求与响应模型)
3. [请求生命周期与状态机](#3-请求生命周期与状态机)
4. [三种问题类型与最小集成伪代码](#4-三种问题类型与最小集成伪代码)
5. [能力与限制矩阵](#5-能力与限制矩阵)
6. [官方性能与成本数字的口径表](#6-官方性能与成本数字的口径表)
7. [替代路线比较（6 条）](#7-替代路线比较6-条)
8. [适合与不适合的场景](#8-适合与不适合的场景)
9. [对 EverAgent 的迁移实验与 eval 指标](#9-对-everagent-的迁移实验与-eval-指标)
10. [Limitations](#10-limitations)
11. [思考与追问](#11-思考与追问)
12. [附录 A：来源清单](#附录-a来源清单)
13. [附录 B：字段速查](#附录-b字段速查)

---

## 1. 问题定义：它到底解决什么

### 1.1 官方给出的定位（一手）

博客与开发指南的表述高度一致：

- 官方定位：「应用与 agent 在工作流中会做**许多小决策**——如何给输入分类、把请求路由到哪、下一步采取什么动作。**单个看都很简单，但规模上它们的延迟与成本会累加。**」
- 能力定位：「Decisions API 评估文本、图像与 JSON，返回**有类型**的答案，**比走 Responses API 快约 10×**。」
- 官方给出的三个返回类型：**probability（条件成立的概率）、choice（从固定集合中选一个）、score（按 rubric 打分）**。

**因此它解决的不是「让模型更聪明」，而是三件更工程化的事**：

| 真实问题 | Decisions 的做法 |
|---|---|
| **延迟**：分类/路由这类小决策被塞进通用生成请求，用户要等模型「写一段话」 | 端点直接返回类型化答案，不生成自由文本 |
| **成本**：通用请求按输出 token 计费，而小决策的输出可能比输入还贵 | **只按输入 token 计费，无输出 token 费用** |
| **工程复杂度**：每个小决策都要自己写解析、清洗、重试 | 答案类型由服务端保证（probability/choice/score/refusal） |

### 1.2 它明确**不**解决的问题（官方自己划的边界）

- 开发指南直接写：「**你的应用自己执行这些答案所选择的任何动作。**」→ **API 不执行工具、不产生副作用**。
- 开发指南把 Decisions 与 Responses API 的两种用法并列：「当你需要生成符合自己 JSON schema 的对象（抽取字段、写解释）时用 **Structured Outputs**；当你需要模型请求带参数的工具调用时用 **function calling**。」
- 「快 10×」是**相对 Responses API 处理同类判定任务**的对比，而不是相对任何规则系统。

### 1.3 官方的使用场景（一手，都是「小而密集」的判定）

| 场景 | 团队 | 判定的形态 |
|---|---|---|
| 降低响应时间、提升交互性 | dots 团队 | 未展开 |
| 给交易描述分类 | Personal Finance 团队 | **choice**（分类） |
| 按主题分类报道，并判断其「强化还是挑战关键叙事」并打分 | Communications 团队 | **choice + score** |
| 准确归因 AI 成本 | 客户 | 分类/聚合类判定 |
| 让语言学习体验更具交互性 | 客户 | 实时判定 |

> **注意这个场景分布**：全部是「**每个工作流里反复发生、答案集合有限、判定结果直接驱动下一步动作**」的判定 —— 而不是需要推理链、需要写解释、需要调工具的任务。

---

## 2. 请求与响应模型

### 2.1 请求：三段式（官方 API 参考原文）

| 字段 | 作用（官方描述） |
|---|---|
| `model` | 评估请求的模型。**目前只支持 `gpt-6-luna`**。 |
| `input` | **共享证据**：一个文本字符串，或**有序的消息 / 工具调用 / 工具输出数组**。 |
| `questions` | 要评估什么：每个问题含类型、指令，以及（视类型）允许的选项或分数档位。**每次请求可问 1–400 个问题**（公测期为 200）。 |

补充参数（API 参考）：

| 参数 | 语义 |
|---|---|
| `prompt_cache_key` | 由调用方提供，**按 key 分区缓存复用** |
| `prompt_cache_options` | `{ mode: "implicit"（默认） \| "explicit", ttl: "30m" }`；`ttl` 目前**只支持 30m** |
| `safety_identifier` | 不透明的终端用户标识（按已验证 org 作用域），**不是**认证用户身份 |

### 2.2 响应：`answers` 数组，按问题顺序返回

官方 API 参考给出的类型联合：

```
Decision object { answers, model, usage }

answers: array of
    Predicate { name, probability, type }              # type: "predicate"
  | Choice    { name, choice, confidence, probabilities, type }   # type: "choice"
  | Score     { name, score, confidence, probabilities, type }     # type: "score"
  | Refusal   { name, type }                          # type: "refusal"
```

- **顺序保证**：「Answers come back in the same order.」
- **每题可独立拒答**：官方原文「**任何问题都可能返回 refusal 而不是答案；其它问题仍然可以拿到答案。**」refusal 携带该问题的 `name`（若未命名则为 `null`）。
- **Choice 的值是带类型的**：「a string and a boolean with the same text are distinct」→ 返回的 `choice` 可能是 string 或 boolean。
- **Score 的概率明细带 label**：`probabilities: array of { label, probability, value }`；`value` 是该档位的数值索引。
- **usage**：`{ input_tokens, input_tokens_details { cache_write_tokens, cached_tokens }, output_tokens, … }` → **接口会报告 output_tokens，但官方明确不对输出计费**。

### 2.3 输入内容矩阵（官方指南）

| 输入条目 | 支持的内容 |
|---|---|
| user 消息 | 文本、图像、JSON |
| developer / system 消息 | **仅输入文本**（system 消息被当作 developer 消息处理） |
| assistant 消息 | 输出文本或 refusal |
| function / custom tool 输出 | 文本与图像，**必须与对应的 tool call 用 `call_id` 匹配** |

**不支持**：文件、音频、item 引用。

### 2.4 JSON 输入（`input_json`）

- 用 `input_json` 内容部件直接传结构化证据，JSON 放在 `data` 里，可与文本/图像并存于同一条 user 消息；
- **`input_json` 仅支持 `user` 角色**；
- **`data` 内部的 `role` / `image_url` 之类键只是普通数据**，不会创建消息、不会去取图；
- JSON 输入**不改变响应格式**（答案仍按所选问题类型返回）。

---

## 3. 请求生命周期与状态机

```
        ┌──────────────── 客户端（你的应用）────────────────┐
        │                                                 │
  ①组装  │  model=gpt-6-luna                              │
  请求  │  input = 文本 | 消息数组（含 tool call/output） │
        │  questions[1..400] = predicate / choice / score │
        └───────────────┬─────────────────────────────────┘
                        │  POST /v1/decisions
                        ▼
        ┌────────── OpenAI 侧 ────────────────────────────┐
        │ ②缓存查找                                      │
        │   implicit 模式：1 个隐式断点 + 最近 3 个显式断点 │
        │   explicit 模式：仅最近 4 个显式断点             │
        │   匹配时最多考虑最近 80 个断点                   │
        │   TTL = 30m；key 由 prompt_cache_key 分区        │
        │      ├─ 命中 → 读缓存（$0.01/M）                  │
        │      └─ 未命中 → 处理并写缓存（写入价更高）        │
        │                     │                            │
        │ ③ Luna 评估每个 question（共享同一份 input）      │
        │                     │                            │
        │ ④ 产出 answers[]（按问题顺序）                   │
        │   predicate{probability} | choice{choice,         │
        │   confidence, probabilities} | score{score,        │
        │   confidence, probabilities} | refusal{name,type} │
        │                     │                            │
        │ ⑤ 返回 { answers, model, usage }                │
        └───────────────┬─────────────────────────────────┘
                        ▼
        ┌──────────── 客户端（继续掌控）─────────────────┐
        │ ⑥你的应用自己执行动作：路由、分类、打分、写库、 │
        │   调下游工具 —— API 不执行任何副作用            │
        │ ⑦可选：若与 GPT-Live 集成，Live 侧也会收到      │
        │   decision.event（decision.completed），          │
        │   按 question name 读取答案；answer=none 表示不动作│
        └────────────────────────────────────────────────┘
```

### 3.1 关键状态语义（官方原文支撑）

| 状态 | 语义 | 应用侧必须处理的事 |
|---|---|---|
| **正常答案** | typed answer | 直接消费 |
| **单题 refusal** | 该题拒答，**其它题仍有答案** | **不能把整次请求当成失败**；要为 refusal 单独设计分支（fallback 到规则/人工/强模型） |
| **缓存命中** | 只读缓存上下文 | 延迟更低、单价 $0.01/M；但**缓存有 30 分钟 TTL** |
| **缓存未命中** | 处理并写入缓存 | 首次更贵、可能更慢 |
| **请求失败（HTTP/网络）** | 端点级错误 | 需自己实现重试与降级；**官方指南未在已读部分给出端点专属错误语义**（见 Limitations） |

### 3.2 GPT-Live 集成的状态流（官方《Connect voice to Decisions》）

- **两种接入方式**：
  - **native delegation**：Live **直接**调用 Decisions，**省掉一次「Live→你的应用→Decisions」的往返**；
  - **custom delegation**：Live 通知你的应用，由你的应用去调 Decisions。
- **事件驱动**：`session.triggers` 可挂在 `session.input_transcript.delta` 或 `session.output_transcript.delta` 上 → 触发一次决策 → 收到 `decision.event`。
- **读取方式**：在 `decision.event` 中找 `event.type == "decision.completed"`，再**按 question name** 读 `event.decision.answers`；答案 `none` 表示「该动作不做」。
- **会话内可改问题**：发 `session.update` 后**必须等 `session.updated`** 再为该步骤加入 decision item；**delegation 类型在创建 session 时固定**。
- **事件过滤注意点**：若过滤 WebRTC 事件，需要放行 `session.delegation.created`、`decision.event` 及对应 transcript 事件；**Live 只在对应的 transcript 事件被放行时才投递触发结果**。

---

## 4. 三种问题类型与最小集成伪代码

### 4.1 语义定义（官方指南原文要点）

| 类型 | 用途 | 返回 |
|---|---|---|
| `predicate` | 判定一个条件是否成立（如「有无可见损伤」「这段内容是否相关」） | `probability`：0–1 的成立概率估计 |
| `choice` | 从**无序**的固定集合中选一个（如部门、内容类别） | `choice`（你提供的值）+ `confidence` + 各选项 `probabilities` |
| `score` | 对**有序**档位打分（如严重程度） | `score`：**各档位数值索引的概率加权平均**（可落在档位之间）+ `confidence` + 每档 `probabilities` |

官方明确区分：`choice` 用于无序类别，`score` 用于有序档位；**两者都返回离散选项上的概率分布**，只是聚合方式不同。

### 4.2 最小集成伪代码（依据官方 curl / JS / Go / Java 示例归纳）

```python
# 伪代码：一次请求，共享证据 + 多个问题（官方 curl 示例等价形式）
resp = client.decisions.create(
    model="gpt-6-luna",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "Inspect the product in this photo."},
                {"type": "input_image", "image_url": "data:image/png;base64,..."},
            ],
        }
    ],
    questions=[
        {
            "type": "predicate",
            "name": "visible_damage",
            "instructions": "Does the product have visible damage, such as a crack, tear, or dent? "
                            "Ignore shadows and damage to the packaging.",
        },
        {
            "type": "choice",
            "name": "department",
            "instructions": "Which department should handle this complaint?",
            "choices": [
                {"value": "billing",    "description": "Payments, invoices, and refunds."},
                {"value": "technical",  "description": "Problems using the product."},
                {"value": "shipping",   "description": "Delivery and tracking."},
                {"value": "other",      "description": "Requests outside these categories."},
            ],
        },
    ],
)

answers = {a.name: a for a in resp.answers}   # 按 name 索引（name 是官方约定的唯一标识）

# ① predicate → 阈值判断（阈值是应用侧策略，不是 API 保证）
damage = answers["visible_damage"]
if damage.type == "predicate" and damage.probability >= 0.8:
    route_to("returns")

# ② choice → 取被选值；注意值可能是 string 或 boolean
dept = answers["department"]
if dept.type == "choice":
    route_to(dept.choice)          # 可能仍是 boolean，注意类型
else:
    route_to("manual_review")      # ③ 单题 refusal 的兜底分支

# ④ usage 只用于观测与计费对账
print(resp.usage.input_tokens, resp.usage.input_tokens_details.cached_tokens)
```

### 4.3 官方示例中已验证的调用形态（读到的代码）

- **cURL**：`curl https://api.openai.com/v1/decisions -H "Authorization: …" -H "Content-Type: application/json" -d '{...}'`；
- **JavaScript（Node）**：`const decision = await client.decisions.create({ model, input, questions })`；
- **Go**：`decision.Answers[0].AsAny()` 做类型分派，命中 `openai.DecisionAnswerScore` / `openai.DecisionAnswerRefusal`；
- **Java**：`client.decisions().create(DecisionCreateParams.builder().model("gpt-6-luna").input(...).addQuestion(Score.builder()...))`。

> **SDK 形态结论**：官方示例覆盖 **Python / Node / Go / Java**，且 Go 示例显示答案在 SDK 层是**可类型分派的联合类型**（`DecisionAnswerScore`、`DecisionAnswerRefusal` 等），说明「typed answer」是 SDK 层面的强类型承诺，而不只是 JSON 约定。[分析者推导]

### 4.4 图像与候选对比的官方写法

- `input` 放**所有问题共享的证据**；**每个问题要不同的图像**，就把该问题的 `instructions` 设成 `input_text` / `input_image` 部件数组（**不要 message wrapper、不要 role**）；
- **每个候选图像要单独一个问题**（每个问题各自对照同一份共享参考图）；
- 问题图像与 `input` 中的图像**共享同一请求的图像数量上限**。

---

## 5. 能力与限制矩阵

### 5.1 GA 相对公测新增的能力（官方指南「What's new」）

| 能力 | 状态 |
|---|---|
| Prompt caching（复用共享输入并享缓存折扣） | GA 新增 |
| 问题指令中带图像（每题各带图） | GA 新增 |
| 原生 JSON 输入（`input_json`） | GA 新增 |
| 每请求问题数上限 **400**（公测期 200） | GA 新增 |
| 托管图像输入（公网 HTTP/HTTPS URL + base64 data URL） | GA 新增 |
| 会话历史评估（消息 + function/custom tool 调用与输出） | GA 新增 |
| 组织用量上报（token 用量与请求数） | GA 新增 |
| 原生 GPT‑Live 集成 | GA 新增 |
| Private Link（私网连接） | GA 新增 |

博客另列：美欧推理驻留（inference residency）、亚洲若干区域扩容。

### 5.2 限制矩阵（读到的官方事实）

| 维度 | 事实 | 出处 |
|---|---|---|
| **模型** | **只支持 `gpt-6-luna`**（API 参考与指南均写明「currently, only `gpt-6-luna`」） | API 参考 / 指南 |
| **回答类型** | 只有 probability / choice / score（外加 refusal）；**不能生成自由文本或自定义 JSON schema 对象** | 指南 |
| **动作执行** | **API 不执行动作**，由应用执行 | 指南 |
| **工具** | 输入侧可含 tool call / tool output 作为证据；**没有让模型请求工具的能力** | 指南 / API 参考 |
| **输入类型** | 不支持文件、音频、item 引用 | 指南 |
| **system 消息** | 仅输入文本，且被当作 developer 消息处理 | 指南 |
| **JSON 输入** | 仅 `user` 角色支持 `input_json` | 指南 |
| **问题数** | 1–400 / 请求 | API 参考 |
| **缓存 TTL** | `prompt_cache_options.ttl` **目前只支持 `30m`** | API 参考 |
| **缓存断点** | implicit：1 隐式 + 最近 3 显式；explicit：最多 4 显式；匹配最多看最近 80 个断点 | API 参考 |
| **计费** | 只按输入 token；**无输出 token 费用** | 博客 |
| **区域** | 美欧驻留；ZDR 面向合资格客户；Private Link 可用 | 博客 / 指南 |
| **错误语义** | 单题 refusal（其它题照常作答）；**端点级错误码/重试建议在已读文档段落中未见**（见 Limitations） | API 参考 |

> **值得注意的口径冲突**：博客说「For 30-minute and 12-hour cached writes, read our pricing guide」，而 API 参考里 Decisions 的 `prompt_cache_options.ttl` **当前只允许 `30m`**；官方定价页确有 12 小时缓存写入价（2.5× 输入价），Changelog 也记录 **Oct 20** 起 Responses API 可选 12 小时缓存。→ **Decisions 端点是否已支持 12h TTL，在已读一手材料中并不明确**，不能想当然。[待验证]

---

## 6. 官方性能与成本数字的口径表

### 6.1 性能声明

| 数字 | 官方原文口径 | 口径缺口 |
|---|---|---|
| **「比 Responses API 快最多 10×」** | 博客：「up to 10x faster than GPT‑6 Luna through the Responses API」；指南：「returns typed answers about 10x faster than the Responses API」；Changelog（Oct 6）：「Turn text and images into typed answers 10x faster than the Responses API」 | **只有上限值（up to）**；**没有**：基线任务的输入规模/问题数、输出规模、端到端还是首 token、P50/P95/P99、并发条件、是否含网络往返与缓存命中、测试日期与地区。**因此不能当作可复现的性能承诺，只能当作「同一模型在专用端点上可显著更快」的定性信号** |
| 延迟改善的定性机制 | 端点不生成自由文本、只按输入计费、可用缓存 | 机制合理，但官方未给出分项延迟拆解 |

### 6.2 成本数字

| 项 | 官方数字 | 口径说明 |
|---|---|---|
| 输入 | **$0.10 / 百万 token** | 与定价页 `gpt-6-luna` 标准档短上下文输入价一致（$0.10） |
| 缓存输入 | **$0.01 / 百万 token** | 与定价页 `gpt-6-luna` 缓存输入价一致（$0.01）；即缓存输入为输入价的 **1/10** |
| 30 分钟缓存写入 | 定价页 `gpt-6-luna` 为 **$0.125 / 百万**（= 1.25× 输入价） | Decisions 的 ttl 目前仅 `30m` |
| 12 小时缓存写入 | 定价页为 **$0.25 / 百万**（= 2.5× 输入价） | **Decisions 是否可用 12h TTL 未明确**（见 §5.2） |
| 输出 | **不计费** | 但 `usage` 仍报告 `output_tokens` |
| 长上下文 | 定价页 `gpt-6-luna` 长上下文：输入 $0.20、缓存 $0.02、30m 写 $0.25、12h 写 $0.50 | 官方未说明 Decisions 的输入规模上限或是否分长/短上下文计价 → [待验证] |

**对照参照（同为 gpt-6-luna 走 Responses API）**：标准档输出价 **$0.50 / 百万 token**，即 Decisions 的「无输出计费」相当于把输出侧单价**直接归零**。

### 6.3 一个可自行验算的成本模型

下面只讨论**标准处理、短上下文、无区域加价**。设普通输入 token 为 `U`，缓存命中 token 为 `C`，30 分钟缓存写入 token 为 `W30`，12 小时缓存写入 token 为 `W12`，输出（答案）token 为 `O`：

```
Decisions 成本 = U × 0.10/百万 + C × 0.01/百万
               + W30 × 0.125/百万 + W12 × 0.25/百万
Responses 成本 = 上述输入与缓存成本 + O × 0.50/百万
```

`W12` 只用于展示定价结构；Decisions 当前是否允许 12 小时 TTL 仍待验证。若比较双方使用**同一模型、同一缓存状态与同一处理档位**，Decisions 相对 Responses API 的结构性节省才可写为 `O × $0.50/百万`，再加上「不写自由文本」带来的延迟收益。[分析者推导] 原先只写缓存命中成本会漏掉首次填充缓存的写入费用。

> **这个推导给出一条重要的选型判据**：**当判定所需的输出很短（一个标签、一个分数）时，Decisions 的成本优势主要是「省掉输出」；当输出本来就短、瓶颈在输入规模时，优势主要来自延迟与缓存，而非单价。**

---

## 7. 替代路线比较（6 条）

| 路线 | 相对 Decisions 的优势 | 相对 Decisions 的劣势 | 官方文档给出的边界 |
|---|---|---|---|
| **A. Responses API + Structured Outputs** | 生态成熟、可产出任意 JSON schema 对象与**文字解释**；工具链、eval、缓存、批处理齐全 | 更贵（输出计费）、更慢（要生成解释） | 官方指南原文：需要「符合自己 JSON schema 的对象（抽取字段或书面解释）」时用 Structured Outputs |
| **B. Responses API + function calling** | 模型可**带参数请求工具**，能做多步交互 | 同样有输出成本与生成延迟；工具调用需要模型「决定调用」 | 官方指南原文：需要「模型请求带参数的工具调用」时用 function calling |
| **C. Predicted Outputs / Fast mode / 背景模式 / Batch API**（OpenAI 侧其它降延迟手段） | 可复用既有 Responses API 管线；Batch 适合离线、Fast/Ultrafast 模式降低首 token 延迟、Background 适合长任务 | 仍是 Responses API 的延迟/成本结构；Batch 非实时 | 官方文档另有独立指南（fast-mode / background / batch / predicted-outputs） |
| **D. 传统规则引擎 / 正则 / 关键词 / 判别式分类器** | **确定性、零边际成本、零网络延迟、可审计、可解释**；对枚举类、可枚举规则的判定优于任何模型 | 无语义理解；规则维护有成本；覆盖率随场景线性下降 | 官方博客未与规则系统对比（这是**该声明的空白**，也是选型时最该自己测的基线） |
| **E. 客户端侧预测 / 本地缓存 / 本地启发式 gate** | 零延迟、零成本；可用历史频率先挡掉大部分请求 | 需要维护本地状态与失效策略；对新样本无效 | 与 D 同属「不调用 API」路线 |
| **F. 自托管小模型（小型 encoder / 蒸馏分类器）** | 边际成本极低、可离线、可微调、可做大批量离线标注 | 需要运维与算力；质量上限低于前沿模型；训练数据是长期投入 | 与 Cloudflare 的 Workers AI 经验相呼应：低风险流量下沉自有推理可与前沿模型共存 |

**三条最关键的边界提醒**：

1. **Decisions 与 A/B 不互斥**：判定 → 若不确定 → 转 Responses API 做解释或工具调用，是官方给出的自然分工；本文建议把它当作**两级路由**，而不是二选一。
2. **与 D/E 的比较是官方文档的空白**：官方从未把 Decisions 与规则引擎放在同一张延迟/成本表里。**任何「Decisions 更快」的结论都不应被当作「比规则系统快」**。
3. **与 F 的比较同样缺失**：自托管小模型在分类任务上常常更便宜；Decisions 的优势更多在**免运维 + 语义理解 + 概率输出**。

---

## 8. 适合与不适合的场景

### 8.1 适合

| 场景 | 为什么适合（对应官方能力） |
|---|---|
| **分类与路由**（工单归部门、内容归类、意图识别） | `choice` 直接返回你定义的取值 + 概率分布 |
| **条件判定**（这段是否相关、是否存在可见缺陷、是否需要人工复核） | `predicate` 返回 0–1 概率，阈值策略在应用侧 |
| **有序打分**（严重度、叙事是否强化关键叙事、可信度） | `score` 返回档位概率加权平均 |
| **需要「低延迟 + 低成本」的批量小判定** | 一次请求可问 1–400 题，共享同一份输入，只按输入计费 |
| **实时语音/交互中的动作选择**（是否追问澄清、路由、升级、表情/手势） | GPT‑Live 原生集成，native delegation 省一次往返；transcript 触发 |
| **需要「带概率的判定」而非硬标签** | 三种类型都返回概率信息，可做阈值/校准/分流 |

### 8.2 不适合

| 场景 | 原因 |
|---|---|
| **需要自由文本输出、解释、字段抽取** | 必须用 Responses API + Structured Outputs（官方明确） |
| **需要模型调用工具、带参数执行动作** | 用 function calling；Decisions 只返回判定，动作由应用执行 |
| **需要长文档/文件/音频作为证据** | 输入侧不支持文件、音频、item 引用 |
| **开放式判断**（「这段代码好不好」「这个设计是否合理」） | 答案空间无界，predicate/choice/score 都会强行压缩 |
| **需要严格 schema 的复杂结构输出** | Decisions 只有三种答案类型 |
| **需要长上下文（数十万 token 级）判定** | 官方未公布输入上限与长上下文计价口径 → [待验证] |
| **离线批量标注** | Batch API 成本更低；Decisions 未见批处理路径 |
| **需要 12 小时缓存 TTL 的复用场景** | Decisions 的 ttl 目前只支持 30m |

---

## 9. 对 EverAgent 的迁移实验与 eval 指标

### 9.1 候选迁移点（按「判定密度」排序）

| # | 场景 | 判定形态 | 价值假设 |
|---|---|---|---|
| 1 | **播客/博客候选材料入库前的分流**：`predicate`（是否值得精读/与本仓主题相关）+ `choice`（归入哪个项目/方向）+ `score`（信息密度档位） | 三型混合 | 把「强模型精读」的成本集中到少数高价值样本上 |
| 2 | **日报条目筛选**：`predicate`（是否值得进入日报）+ `choice`（归类）+ `score`（重要性档位） | 三型混合 | 日报是高频小判定，最贴合该端点的成本/延迟形状 |
| 3 | **多 Agent harness 的下一步动作选择**：`choice`（继续检索 / 调工具 / 交给强模型 / 直接回答） | choice | 把「路由决策」从强模型回合里剥离出主路径 |
| 4 | **报告章节的证据强度标注**：`score`（证据充分性档位） | score | 可作为报告初稿的**辅助信号**（不替代 evidence sidecar） |
| 5 | **交互式 TUI/播客追问的实时分流**：是否需要澄清、是否继续深挖 | predicate | 低延迟决策改善交互体感 |

> **边界提醒**：EverAgent 的 report-v2 流程要求「关键 claim 可追溯到来源」——**Decisions 只能产出判定，不能产出可追溯证据**。因此它适合做**门控/分流/打标**，不适合做「证据判定者」。这是最重要的一条边界。

### 9.2 建议的迁移实验（可执行）

**实验 0（前置）：先测「不用模型会怎样」**
- 建一个 baseline：纯规则/关键词/路径启发式的分流器（路线 D/E）。如果规则基线已经解决 80% 的样本，Decisions 的收益上限就很小。

**实验 1：Decisions vs 强模型直接判定**
- 抽取 200–500 条历史样本（有人工标注的优先：被采纳的报告、被退稿的候选、被标为不相关的材料）；
- 三组对照：① 规则基线 ② Decisions（gpt-6-luna）③ 强模型（Responses API + Structured Outputs）；
- 记录：延迟 P50/P95、成本/条、判定一致率与错误类型（漏 vs 误纳）。

**实验 2：两级路由（Decisions → 强模型）**
- 只有当 Decisions 的概率落在 **[低阈, 高阈]** 区间时才升级到强模型；阈值用实验 1 的数据选；
- 目标：把强模型调用量降到 X%，同时保持「最终结论」的准确率不下降。

**实验 3：多题批处理是否真的省**
- 把同一份材料的 N 个判定问题合并成**一次请求**（1–400 题），对比 N 次单题请求的延迟与成本；注意缓存命中会影响两者。

**实验 4：拒答与不确定性处理**
- 统计 refusal 率；构造「应当拒答/应当转人工」的样本集，验证应用侧分支是否被正确触发。

### 9.3 eval 指标（建议）

| 指标 | 定义 | 为什么需要 |
|---|---|---|
| **一致率 / Cohen's κ** | Decisions 判定 vs 人工标注（或强模型判定） | 判定型任务的最小验收 |
| **混淆矩阵：漏 vs 误纳** | 应进入日报/报告却判否（漏）vs 不应进入却判是（误纳） | **两者的业务代价不同**，必须分开报，不能只看 accuracy |
| **概率校准（Brier score / 可靠性曲线）** | predicate 的概率是否可信 | 阈值策略依赖概率有意义；若概率不可信，阈值就只是分类器 |
| **延迟 P50/P95** | 端到端（含网络） | 官方只有「快 10×」的上限声明，需自测分布 |
| **成本/判定 与 成本/被采纳条目** | 后者才是业务口径 | 「每条判定 0.1 分钱」不等于「每篇报告更便宜」 |
| **拒答率与拒答质量** | refusal 频率、refusal 样本上人工判定的应拒率 | 拒答是安全阀，其质量决定回退策略是否可靠 |
| **相对强模型的「单位有效产出成本」** | （总成本）/（最终被采纳且正确的条目数） | 唯一能回答「这个端点值不值」的指标 |
| **回归集固化** | 固定版本化的判定样本集 + 期望输出 | 换模型/改 prompt/换端点后能立刻回归 |

### 9.4 一条纪律建议（与本仓其它报告一致）

**任何引入新判定层的改动，都必须同时提交「它替代了什么、判定标准是什么、错判的代价由谁承担」**——否则项目会退化成一个「多了一层模型、但没人说得清它做了什么」的管线。

---

## 10. Limitations

1. **「快 10×」缺乏可复现口径**：官方三处（博客 / 指南 / Changelog）都只有上限值，无基线任务、无延迟分布、无负载与并发条件、无测试日期与地区。**这是厂商自报的宣传性对比，不能当作独立性能验证。**
2. **本文未做任何实测**：没有调用该 API、没有测延迟、没有核算真实成本。所有性能与成本数字均为 OpenAI 官方口径。
3. **本文对官方开发指南的读取被工具截断**：已读到请求/响应模型、三种问题类型、JSON 输入、图像输入与会话历史评估；**未读到**指南后半部分（prompt caching 章节全文、用量监控、限制章节等），这些内容以 API 参考与博客交叉补足，**可能存在遗漏**。
4. **未读到端点专属的错误码与重试语义**：官方有独立的 *Error codes* 指南，但 Decisions 端点的具体错误分类与退避建议在已读材料中未出现 → 应用必须自建兜底。
5. **12 小时缓存 TTL 对 Decisions 是否可用未明确**：博客提到 12h 缓存写入定价，API 参考却限定 `ttl` 仅 `30m` → [待验证]
6. **输入规模上限与长上下文计价未公布** → [待验证]
7. **只支持 `gpt-6-luna`**：没有模型选择空间，也无法用更便宜的模型做分层；也无法用更强模型做「不确定时升级」的常规路径（升级需切到 Responses API）。
8. **答案类型受限**：无法产出解释、无法产出自定义 JSON schema 对象、无法请求工具。
9. **概率的语义未定义**：官方未说明 `probability`/`confidence` 是何种校准方式、是否可跨问题比较、是否随问题措辞敏感；**把它当作「可设阈值的概率」使用前必须自测校准**。
10. **选择偏差风险**：官方展示的内部用例（dots、Personal Finance、Communications）与客户案例均为**精选成功案例**，没有失败案例或对照。
11. **与规则引擎/自托管小模型的对比缺失**：官方从未把 Decisions 放进同一张延迟/成本对照表；任何「比传统方案快/省」的判断都必须自建基线。
12. **无输出计费不等于无输出成本**：接口报告 `output_tokens`，说明答案本身仍有生成成本（未被计价）；厂商可能随时调整计费结构。
13. **图像上限未给出**：指南只说「问题图像与 input 图像共享请求的图像数量上限」，但未给出具体数字 → [待验证]
14. **本文对 SDK 强类型、缓存与成本模型的推论标注为 [分析者推导]**，未经实测或官方明文确认；成本公式只适用于同处理档位、同上下文档位和同缓存状态的对照，实际账单还可能包含缓存写入、区域加价与不同处理模式价格。

---

## 11. 思考与追问

1. **「10×」的基线到底是什么？** 同一个 gpt-6-luna、同样输入、只是把「写一段解释」换成「返回一个标签」——这算不算公平对比？如果 Decisions 的对照是「让 Responses API 用 Structured Outputs 只输出一个标签」，差距还有多少？**这个数字如果按最严格的对照重算，可能远小于 10×。**
2. **输出的计价被归零后，模型会「少想」吗？** Decisions 固定使用 gpt-6-luna，但判定答案只有一行。**服务侧是否仍进行未反映在答案长度里的推理计算？** 这决定了“无输出收费”与真实算力成本之间有多大差距。
3. **概率的可校准性如何？** 如果 `probability` 与人类判断的「真实度」不单调相关，那么基于阈值的自动分流会产生难以察觉的偏差；而官方没给校准数据。**这是该端点最该被独立评测、却最没人评测的维度。**
4. **多问题批处理的收益上限在哪？** 一次 400 题共享同一份输入，理论上输入成本可摊薄；但若每题都需要不同证据（图像在指令里），输入就会膨胀。**「共享证据 + 多题」与「每题独立证据」的成本曲线如何？**
5. **与 Agent 的分工怎么划？** 官方给的是「决策层」，但现代 harness 里「决策」往往与「执行」交织（选工具 → 调工具 → 看结果 → 再决策）。**把决策抽成一次无状态 API 调用，是否会破坏 agent 的连续推理？**
6. **对 EverAgent 而言，最有价值的用法可能不是「判定」而是「守门」**：让 Decisions 负责**快速否掉明显不值得精读的材料**，把强模型预算留给少数候选。**这需要一个能持续维护的负样本集** —— 谁能提供它？
7. **与本地小模型比，值不值？** 许多分类任务可由小型 encoder 或蒸馏分类器以更低边际成本完成。**Decisions 的溢价买到了什么** —— 免运维？语义理解？概率分布？把这三项分别定价，才好决策。
8. **「refusal 是正常返回而非错误」这一设计，对 harness 意味着什么？** 传统 harness 把「没有结论」当异常；Decisions 把它当**一等答案**。EverAgent 的 harness 是否需要引入同样的「per-question 拒答」语义（而不是整次调用失败）？
9. **如果 Decisions 与 Responses API 的价格结构继续分化**（输出免费、输入照收），会不会催生一批「把上下文塞进输入、把推理外包给端点」的用法？以及：**大输入 + 小输出** 的决策形态，反而可能比生成任务更适合 Decisions —— 值得专门验证。
10. **官方没有公布失败案例**：当判定「难到模型拒答」或「选项之间本就模糊」时的表现，是这个端点真实价值的关键一环。**谁来公开这份数据？**

---

## 附录 A：来源清单

| ID | 来源 | 类型 | 用途 |
|---|---|---|---|
| S01 | OpenAI 官方博客 — *Build more responsive apps with the Decisions API*（2026-10） `https://openai.com/index/decisions-api` | 一手（厂商） | 产品定位、GA 声明、官方用例、内部团队与客户案例、定价摘要、区域与 ZDR 声明 |
| S02 | OpenAI 官方开发指南 — *Decisions* `https://developers.openai.com/api/docs/guides/decisions`（含 `.md` 版本） | 一手（官方文档） | 请求三段式、三种问题类型、会话历史评估、JSON 输入、图像输入与按题配图、choice/score 示例、GA 新增能力清单 |
| S03 | OpenAI 官方 API 参考 — *Create decision*（`POST /v1/decisions`） `https://developers.openai.com/api/reference/resources/decisions/methods/create` | 一手（官方文档） | 响应 schema（Predicate/Choice/Score/Refusal）、答案顺序与拒答语义、usage 字段、缓存参数（key/mode/ttl/断点规则）、问题数 1–400、输入条目类型 |
| S04 | OpenAI 官方指南 — *Connect voice to Decisions* `https://developers.openai.com/api/docs/guides/decisions-voice` | 一手（官方文档） | GPT‑Live 原生集成语义（native vs custom delegation）、`session.triggers` 配置、事件类型与读取方式、会话内改题约束 |
| S05 | OpenAI 官方 Changelog `https://developers.openai.com/api/docs/changelog` | 一手（官方文档） | 时间线：Oct 6 公测（gpt-6-luna，10× 表述）、Oct 15 GPT‑Live 原生集成、Oct 20 12 小时 prompt caching（Responses API） |
| S06 | OpenAI 官方定价页 `https://developers.openai.com/api/docs/pricing` | 一手（官方文档） | `gpt-6-luna` 标准档短/长上下文价格：输入 $0.10 / 输出 $0.50 / 缓存输入 $0.01 / 30m 写 $0.125 / 12h 写 $0.25（长上下文翻倍） |

**证据分级**：S01 是厂商对外发布（含宣传性对比）；S02–S06 是官方技术文档（对 API 语义、schema、参数与价格为事实性一手证据）。**性能对比（10×）仅 S01/S02/S05 有，且无方法学细节，本文一律按「厂商自报」处理。**

---

## 附录 B：字段速查

| 位置 | 字段 | 取值 / 说明 |
|---|---|---|
| 请求 | `model` | 仅 `gpt-6-luna` |
| 请求 | `input` | 文本字符串，或消息/工具调用/工具输出的有序数组 |
| 请求 | `questions[]` | 1–400 个；`predicate` / `choice` / `score` |
| 请求 | `questions[].name` | 唯一名，响应会回显（≤1,048,576 字符） |
| 请求 | `questions[].instructions` | 字符串，或 `input_text` / `input_image` 部件数组 |
| 请求 | `questions[].choices[]` | `{ value, description }`（choice 型） |
| 请求 | `questions[].levels[]` | `{ label, description }`（score 型，有序） |
| 请求 | `prompt_cache_key` | 缓存分区键 |
| 请求 | `prompt_cache_options` | `{ mode: implicit\|explicit, ttl: "30m" }` |
| 请求 | `safety_identifier` | 不透明终端用户标识（非认证身份） |
| 响应 | `answers[]` | 按问题顺序；每题可能是 predicate / choice / score / refusal |
| 响应 | `answers[].probability` | predicate 的 0–1 概率 |
| 响应 | `answers[].choice` | choice 型被选值（string 或 boolean） |
| 响应 | `answers[].score` | score 型：档位索引的概率加权平均 |
| 响应 | `answers[].confidence` | choice / score 的置信度 |
| 响应 | `answers[].probabilities[]` | 各选项/档位的概率（choice 为 `{probability, value}`，score 为 `{label, probability, value}`） |
| 响应 | `answers[].type` | `"predicate"` / `"choice"` / `"score"` / `"refusal"` |
| 响应 | `usage.input_tokens` / `input_tokens_details.cached_tokens` / `cache_write_tokens` / `output_tokens` | 用量与缓存对账 |
| Live | `session.triggers[].event_type` | `session.input_transcript.delta` / `session.output_transcript.delta` |
| Live | 事件 `decision.event` → `event.type` | `decision.completed`；答案按 question name 读取，`none` 表示不动作 |

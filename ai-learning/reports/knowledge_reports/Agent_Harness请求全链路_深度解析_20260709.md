---
title: "客户端→网关→Harness→LLM→工具 请求全链路深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-07-09"
semantic_tags: ["agent_harness", "function_calling", "tool_use", "agentic_loop", "context_management", "prompt_caching", "kv_cache", "streaming", "sse", "context_editing", "compaction"]
related_concepts: ["agent_harness", "kv_cache", "long_context_systems", "rag", "agent_orchestration", "agent_systems", "agent_observability"]
related_entities: ["openai", "anthropic"]
---

# 客户端 → 网关 → Harness → LLM → 工具：一次带工具的对话，到底怎么"有来有回"？

> **这篇是什么**：把"LLM + Agent Harness 工程"这套东西，从**一次请求怎么走**的角度讲透。不停留在概念，而是落到**真实报文的字段**和**官方文档写的循环伪代码**，回答两个最容易含糊的问题。
>
> **要澄清的两个核心问题**：
> 1. 加上 Harness 后，中间要调用工具时，**Harness / LLM / 工具三方到底是如何"有来有回"交互的**？
> 2. LLM 是无状态的，那在一次长对话里反复调工具，**输入 token 是不是单向越滚越大、最终逼近上下文上限**？如果是，工业界怎么治？
>
> **怎么读**：只想要结论 → 看「🎯 两句话直答」+「🔧 一次工具往返的报文级全景」。想搞清 token 为什么膨胀、怎么治 → 看「📈 token 膨胀」+「🧹 四类治理机制」。想校正几个常见误解 → 看「🧠 四个容易踩的认知误区」。
>
> **证据边界**：所有带 `报文`/`字段名`/`具体数值` 的结论都来自 OpenAI / Anthropic 官方文档原文（链接见文末），逐条标了出处。标 `[推测]` 的是推断，非官方定论。

---

## 🎯 两句话直答

> **问题一**：三方交互的本质是一个 **`messages` 数组不断追加、Harness 反复回发的 `while` 循环**。LLM 每轮只输出"要调哪个工具、参数是什么"（一个结构化对象），**它自己不执行**；Harness 执行完把结果作为一条新消息**追加**回数组，再把**全量数组**重新发给 LLM，直到 LLM 输出"不带工具调用的纯文本"才收尾。这就是 Anthropic 官方写的 `while stop_reason == "tool_use"` 循环。
>
> **问题二**：**原生不做优化时，输入 token 确实单向膨胀**，根因就是"LLM 无状态"。现代解法分两个层次：① **推理侧的 prompt caching**——不减文本，但把重复前缀的计费打到 **0.1 倍**、并省掉重复 prefill 计算；② **上下文侧的 context editing / compaction**——真的把老消息删掉或压成摘要，官方示例能把 ~100k tokens 压回 ~2–3k。二者正交，通常叠加使用。

---

## 🧩 先对齐概念：Harness 到底是哪一层

**Agent Harness = 夹在客户端和 LLM 推理服务之间的编排/调度层**，它持有 `messages`、拼 prompt、执行工具、控制循环。普通单次问答用不到这一层，只有带工具调用、需要多轮自主行动的 Agent 才依赖它。本库 `wiki/concepts/agent_harness.md` 有独立词条，这里不展开定义。

一个必须先立起来的**铁律**，它极其重要：

> **LLM 是一个无状态的纯推理函数。** 它没有网络、不能读写文件、不能调数据库、不记得上一轮。它唯一能做的事是：读入一段 `messages`，输出下一段 token。所谓"调用工具"，模型输出的**只是一个结构化的意图**（"我想调 `get_sales`，参数 `{month:6}`"），真正的执行由 Harness 代劳。

这条铁律是理解**两个问题**的总钥匙：正因为无状态，所以①每轮都得把全量历史重发（→ 有来有回靠 Harness 搬运），②历史只增不减（→ token 膨胀）。

---

## 🔧 一次工具往返的报文级全景（回答问题一）

概念图人人会画，但"有来有回"的实体其实是**一条条带特定字段的报文**。下面用两家官方文档的真实字段，把一次工具往返从头到尾走一遍。举个贯穿全篇的例子：用户问"查一下 2026 年 6 月杭州空调销量"。

### 阶段 0：客户端 → 网关（一次请求，之后静默）

客户端把 `文本 + 图片 + 会话ID` 经 HTTP/SSE/WebSocket 发给网关；网关转发给 Harness。**客户端此后只需保持连接等最终流**——后续所有循环都在服务端内部完成。注意"等最终流"不等于"看不到中间步骤"，这点在误区 ① 会澄清。

### 阶段 1：Harness 组装 → 首次请求 LLM

Harness 把 `system + tools schema + (RAG) + 历史 messages + 本轮 user` 打包发给 LLM。

**一个关键事实：工具定义本身要吃 token，而且每轮都带。** 以 Anthropic 官方"tool use system prompt token 计费表"为例，仅仅"启用工具"这个动作，就会往每次请求里注入一段固定开销：

> Claude Opus 4.8：`tool_choice` 为 auto/none 时 **290 tokens**；为 any/tool 时 **410 tokens**。（Anthropic Tool use docs, "Tool use system prompt token count" 表格原文）

这引出问题二的一个细节：**system + tools 属于"永久固定占用"，每轮都重复携带、重复计费**。

### 阶段 2：LLM 首轮输出 —— "我要调工具"（不是自然语言）

这里是全链路最该看清楚的地方——**模型返回的不是答案，而是一个"调用意图"的结构化对象**。两家 API 的报文形态：

**OpenAI（Chat Completions）**：assistant 消息里带 `tool_calls` 数组，每个元素结构为——

```jsonc
{
  "role": "assistant",
  "tool_calls": [{
    "id": "call_abc123",
    "type": "function",
    "function": { "name": "get_sales", "arguments": "{\"month\":6,\"city\":\"Hangzhou\"}" }
  }]
}
```

> 注意 `arguments` 是一个**字符串化的 JSON**，不是对象——用的时候要 `JSON.parse`。（OpenAI Function calling docs 原文示例）
>
> Responses API 里换了名字：是一个 `type:"function_call"` 的 item，配 `call_id` 字段。（OpenAI Responses/Agents docs）

**Anthropic（Messages）**：响应的 `stop_reason` 变成 `"tool_use"`，`content` 里出现一个块——

```jsonc
{
  "stop_reason": "tool_use",
  "content": [
    { "type": "text", "text": "我需要先查一下销量……" },
    { "type": "tool_use", "id": "toolu_01A...", "name": "get_sales", "input": {"month":6,"city":"Hangzhou"} }
  ]
}
```

> Anthropic 的 `input` 直接是对象（不像 OpenAI 是字符串），且 `stop_reason:"tool_use"` 是循环是否继续的**判据信号**。（Anthropic Tool use docs 原文）

### 阶段 3：Harness 执行工具 → 把结果作为**新消息**追加

Harness 解析上面的意图、鉴权、沙盒执行真实 API，然后把结果**回填成一条专门角色的消息**，靠 ID 与刚才的调用配对：

**OpenAI**：追加 `{"role":"tool", "tool_call_id":"call_abc123", "content":"{...查询结果...}"}`。

**Anthropic**：在一条 **user** 消息里放一个块 `{"type":"tool_result", "tool_use_id":"toolu_01A...", "content":"..."}`。

> 关键点：`tool_call_id` / `tool_use_id` 是"哪次调用对应哪个结果"的**绑定锚**，模型靠它把结果和自己发出的调用对齐。（两家文档均有原文）

### 阶段 4：Harness 把**全量数组**重新发给 LLM（第二轮）

这就是"有来有回"的机械核心——**没有魔法，就是把追加过 tool 结果的整个 `messages` 再 POST 一次**。Anthropic 官方把这个循环写成伪代码：

> ```python
> while response.stop_reason == "tool_use":
>     tool_results = run_tools(response)          # 执行工具
>     messages.append(assistant_message)          # 追加模型的 tool_use
>     messages.append(tool_results_message)        # 追加 tool_result
>     response = client.messages.create(...)       # 带全量 messages 再请求
> ```
> 循环退出条件：`stop_reason` 变为 `end_turn` / `max_tokens` / `stop_sequence` / `refusal` 之一。（Anthropic Tool use "Handling the tool use loop" 原文）

OpenAI Agents SDK 的 `Runner.run()` 把同一个循环讲得更细：

> 每轮：(1) 调 LLM；(2) 若输出是**目标类型的纯文本且无工具调用** → 判为 **final output**，结束；若是 **handoff** → 换 agent 重跑；若有 **tool_calls** → 执行工具、追加结果、重跑；(3) 超过 `max_turns` → 抛 `MaxTurnsExceeded`。（OpenAI Agents SDK "Running agents / The agent loop" 原文）

### 阶段 5：LLM 输出纯文本 → Harness 收尾、流式推客户端

模型判断信息够了，输出**不带 tool_calls 的纯文本**（OpenAI `finish_reason:"stop"` / Anthropic `stop_reason:"end_turn"`），Harness 跳出循环，流式把文本推给客户端，并把全链路持久化。

### 一张表看清"有来有回"的四类消息角色

| 角色 | OpenAI 字段 | Anthropic 形态 | 谁产生 | 装什么 |
|---|---|---|---|---|
| system | `role:"system"` | 顶层 `system` 参数 | Harness | 规则、角色、（部分）工具约束 |
| user | `role:"user"` | `role:"user"` | 用户/Harness | 用户输入；**也用来回填 tool_result（Anthropic）** |
| assistant（纯文本） | `role:"assistant"` + `content` | `role:"assistant"` + `text` 块 | LLM | 最终答案 / 思考 |
| assistant（工具调用） | `tool_calls[]` | `tool_use` 块 + `stop_reason:"tool_use"` | LLM | **调用意图**（不执行） |
| tool 结果 | `role:"tool"` + `tool_call_id` | user 消息里的 `tool_result` 块 + `tool_use_id` | Harness | 工具真实返回 |

---

## 🧠 四个容易踩的认知误区

理解了主链路后，有四个点特别容易想当然、进而误判系统行为。逐个澄清：

### 误区 ① ❌ "客户端完全看不到中间工具调用、中间推理轮次"

很多人以为客户端只能收到最终答案，中间步骤在协议层就"看不见"。**这是错的**——现代流式 API **原生就把工具调用事件推给客户端**：

- **OpenAI SSE**：流式响应里会吐 `response.function_call_arguments.delta` 事件——即工具参数**逐字符**地流给前端。（OpenAI streaming / Responses streaming docs 原文事件名）
- **Anthropic streaming**：`content_block_start` / `content_block_delta` 会把 `tool_use` 块的 `input_json_delta` 流出来。（Anthropic streaming docs）

**现实反证**：在 Claude / ChatGPT / 各家 Agent 产品里**亲眼能看到** "正在调用搜索""正在读取文件"这类中间步骤，本 CLI 也会把每个 tool call 显示出来。所以正确表述是：**"中间步骤是否展示是产品的 UI 选择，不是协议层的限制"**。"默认折叠"不等于"技术上看不到"。

### 误区 ② ⚠️ "KV Cache / prompt caching 只是提速，不影响成本"

一个常见的半对认知："缓存不减少传输的 token、也不解决上下文超限，只是让推理内部算得快些"。前半句对——**缓存确实不改变你传给 LLM 的文本长度，也不解决窗口上限**。但它漏了最关键的一点：**prompt caching 直接砍计费**。Anthropic 官方定价乘数：

> - 5 分钟缓存**写入** = 基础输入价 **1.25×**；1 小时写入 = **2×**；
> - 缓存**读取**（cache hit）= 基础输入价 **0.1×**。默认 TTL 5 分钟。（Anthropic Prompt caching docs 原文乘数）

也就是说：一次长对话里，重复的前缀（system + tools + 老历史）在缓存命中时**只按 1/10 价格计费**，同时省掉重复 prefill 计算。所以对问题二里"成本暴涨"的担忧——**prompt caching 是第一道、也是最省事的减负阀**（它改的是"单价"，不是"数量"）。

> 补充机制细节：缓存按 `tools → system → messages` 的**前缀顺序**命中；随着对话增长，自动缓存断点会**向前移动**覆盖更多内容。（Anthropic Prompt caching docs）

### 误区 ③ ⚠️ "上下文治理只能靠 Harness（客户端）自己写代码"

滑动窗口、摘要压缩，很多人默认必须在 **Harness（客户端侧）自己实现**。但 2025–2026 年 Anthropic 已经把这套能力**下沉到 API 服务端**，Harness 只需开个开关：

- **Context editing（`clear_tool_uses_20250919`）**：服务端自动清除**老的工具调用/结果**。官方示例配置：`trigger.input_tokens=30000`（超 3 万触发）、`keep.tool_uses=3`（保留最近 3 次工具往返）、`clear_at_least.input_tokens=5000`、`exclude_tools`（指定工具豁免）。beta header：`context-management-2025-06-27`。（Anthropic context editing docs 原文配置）
- **Compaction（`compaction_control`）**：默认 `context_token_threshold=100000`，触发后注入一段总结 prompt，把历史**替换成一个 `<summary>` 块**。官方示例里 **~100k tokens 被压回 ~2–3k**。这里的"总 token"= `input + cache_creation + cache_read + output` 四项之和。（Anthropic compaction docs 原文）

关键在于：**服务端 edit（如 `compact_20260112`）比客户端手动删更优**，因为它裁剪的同时**保持前缀缓存不失效**；客户端手动删历史反而会打断缓存前缀、触发昂贵的重新写入。

### 误区 ④ ⚠️ "循环最大轮次固定是 5~10 轮" & token 计费能简单相加

两个常被想当然的数值细节：

**其一，"最大迭代轮次"没有普适默认值。** 它因框架而异：

- OpenAI Agents SDK 的 `max_turns` **有默认上限但可配**，且**可设 `max_turns=None` 直接关闭限制**；超限抛 `MaxTurnsExceeded`。（OpenAI Agents SDK docs）
- Anthropic 的 agentic loop 本身**没有硬编码轮数**，靠 `stop_reason` 自然收敛；只有**服务端工具**（如 web search）内部循环打满迭代帽时，才返回 `stop_reason:"pause_turn"` 让你续跑。（Anthropic docs）

所以正确说法是"**上限可配置，不同框架默认值不同，也可关闭**"。

**其二，token 用量不能把各字段简单相加。** 工具返回的大表格/日志往往占绝大多数 token（这正是 context editing 优先清工具结果的原因），但算成本时有个真实陷阱：

> 一次响应 usage 为 `input_tokens: 63000, cache_read_input_tokens: 270000`，某些 SDK 会**错误地把两者相加**得到 334,400，而实际计费口径并非简单相加。（Anthropic docs 案例）

结论：**"这轮到底花了多少 token"不能想当然地把各字段相加**——尤其在有缓存和服务端工具时。

---

## 📈 问题二正解：token 为什么单向膨胀

**结论先行：会膨胀，而且是必然的。** 核心因果：

```
LLM 无状态  ⇒  每轮必须重发全量历史  ⇒  历史只增不减  ⇒  输入 token 单向上涨
                                              ⇒  ① prefill 变慢（输入越长越慢）
                                              ⇒  ② 计费上涨（按输入 token 计价）
                                              ⇒  ③ 逼近上下文窗口硬上限 → 溢出报错
```

量级感：一次 10 轮工具调用的任务，最后一轮送入 LLM 的输入可能是第一轮的 **8~10 倍** `[推测]`（量级合理，但非实测，见文末待办）。

一个容易忽略的**放大器**：**多模态**。图片编码后的 token 远高于等价文本，长对话里塞几张图会**急速**打满窗口，值得单独注意。

还有一个**窗口口径**：上下文窗口是 **输入 + 输出 的总和上限**，不是只算输入。所以工程上要预留 10%~20% 给输出，Harness 会设一个"输入安全阈值"（如 800k / 1M）提前触发裁剪。

---

## 🧹 四类治理机制：怎么阻止上下文无限膨胀

按**"改数量" vs "改单价"**两个正交维度归类，这是理解各机制关系的关键：

| 机制 | 改的是 | 谁来做 | 官方锚点 | 代价/缺点 |
|---|---|---|---|---|
| **① Prompt caching** | **单价**（不减 token） | 服务端，Harness 开关 | 命中 = 基础价 **0.1×**；写入 1.25×/2×（Anthropic）| 有 TTL（默认 5 分钟）；前缀一变即失效 |
| **② 滑动窗口裁剪** | 数量（删最老） | Harness | 通用做法 | 丢早期关键背景 → 答偏 |
| **③ 摘要/Compaction** | 数量（压成摘要） | Harness **或服务端** | `compaction` 默认阈值 100k，压到 ~2–3k（Anthropic）| 摘要有信息损失；需一次额外 LLM 调用 |
| **④ Context editing / 工具结果过滤** | 数量（清老工具结果）| **服务端自动** | `clear_tool_uses_20250919`，trigger 3万/keep 3次（Anthropic）| 清掉的工具历史模型不再可见 |

**两轴正交、通常叠加**：①（改单价）和 ②③④（改数量）解决的是不同问题——前者让"重发全量历史"不那么贵，后者让"历史"本身不那么大。现代做法优先用 ②③④ 里的**服务端版本**，因为它们**保持前缀缓存不失效**，能和 ① 协同；反之，客户端手动删历史会打断缓存前缀、触发昂贵的重新写入。

---

## 🔗 和本库已有报告的关系（不重复造轮子）

- 循环范式/ReAct/协议层 → 见 `Agent_ReAct_ToolUse_深度解析_20260409.md`（本篇是它的**系统链路侧**补充：那篇讲"为什么这么设计"，本篇讲"报文和请求怎么走"）。
- KV Cache 的注意力机制原理 → `wiki/concepts/kv_cache.md` & `KV_Cache_深度解析_20260330.md`。
- 长上下文系统工程 → `wiki/concepts/long_context_systems.md` & `Long_Context_1M_三阶段深度解析_20260507.md`。
- RAG 注入 → `wiki/concepts/rag.md`。
- Harness 概念词条 → `wiki/concepts/agent_harness.md`（本报告已回链）。

---

## 💭 思考与追问

1. **我真正理解了什么？**
   我把"有来有回"这个模糊直觉，落成了**报文级的确定机械过程**：一个 `messages` 数组的追加—重发循环，退出判据是两家文档白纸黑字的 `stop_reason`/`finish_reason`。同时确认了 token 膨胀的因果链（无状态 → 全量重发 → 单向膨胀）**必然成立**，并把治理拆成正交的两轴——**"改单价"（prompt caching，0.1 折）** vs **"改数量"（窗口/摘要/context editing）**。最有价值的收获是校正了四个常见认知误区，其中最关键的三个：客户端"看不到中间步骤"（错，流式协议原生可见）、缓存"只提速"（漏了 10 倍降价）、上下文治理"只能客户端写"（漏了服务端自动 compaction/context editing）。

2. **我还没搞懂什么？**（汇入 open-questions）
   - **compaction 的摘要质量如何保证不丢关键约束？** 官方把 100k 压到 2–3k，压缩比 ~40×，那些被丢掉的工具中间结果里若含后续步骤依赖的关键事实，模型如何不"断片"？有没有可证伪的失败模式基准？
   - **prompt caching 的前缀失效边界在哪？** 只要 system/tools/老历史里改一个字节，整段缓存就失效重写（1.25×）。那么"动态 RAG 每轮注入不同片段"是不是会**系统性地打穿缓存**、让 0.1 折形同虚设？RAG 该放前缀还是放尾部？
   - **服务端 context editing 清掉的工具历史，与客户端持久化的全量历史，二者一致性怎么对账？** 观测/审计（`agent_observability`）时以哪份为准？

3. **下一步读什么 / 做什么？**
   - 落一个**最小可运行 demo**（B 类 `ai-practice`）：Python + OpenAI function calling 真跑一次两轮工具循环，打印每轮 `messages` 的真实 token 数，把本报告"8~10 倍膨胀"的 `[推测]` 换成**实测曲线**。
   - 读 Anthropic context editing / compaction 的**完整 API reference**（本报告用的是文档正文示例），核对 `compact_20260112` 服务端 edit 与客户端手动裁剪对缓存命中率的实测差异。
   - 追一份 OpenAI Responses API 流式事件全表，把"客户端可见中间步骤"从"协议支持"推进到"事件字段级清单"。

---

## 📚 参考来源

- OpenAI · Function calling（Chat Completions / Responses）
  https://platform.openai.com/docs/guides/function-calling
- OpenAI · Agents SDK — Running agents / the agent loop
  https://openai.github.io/openai-agents-python/running_agents/
- OpenAI · Streaming responses（SSE 事件，`response.function_call_arguments.delta`）
  https://platform.openai.com/docs/guides/streaming-responses
- Anthropic · Tool use（tool_use / tool_result / agentic loop / stop_reason）
  https://docs.claude.com/en/docs/build-with-claude/tool-use
- Anthropic · Streaming Messages（content_block_delta / input_json_delta）
  https://docs.claude.com/en/docs/build-with-claude/streaming
- Anthropic · Prompt caching（0.1× 读 / 1.25×·2× 写 / 前缀顺序）
  https://docs.claude.com/en/docs/build-with-claude/prompt-caching
- Anthropic · Context editing & Compaction（clear_tool_uses / compaction_control）
  https://docs.claude.com/en/docs/build-with-claude/context-editing

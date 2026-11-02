---
title: "Google API Gateway 流式响应：协议机制、兼容性与工程边界"
domain: "cs-learning"
report_type: "concept_report"
status: "completed"
updated_on: "2026-11-02"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["api_gateway", "response_streaming", "sse", "http", "backpressure", "ai_infrastructure"]
---

# Google API Gateway 流式响应：协议机制、兼容性与工程边界

一个模型已经生成了第一句话，用户却还在等待整个回答。这未必是模型慢：后端、网关、SDK 或界面中的任何一层，都可能把已经到达的数据攒起来，等全部完成才交付。**流式响应解决的是“产出什么时候可见”，不自动解决“产出得更快”。**

Google 在 [2026 年 10 月 22 日的文章](https://developers.googleblog.com/streaming-comes-to-api-gateway-real-time-and-ai-ready-apis-without-changing-your-spec)中宣布 API Gateway 的流式支持进入 Public Preview。它的价值是：不再为了实时交互绕开原有的鉴权、路由和观测入口。但标题里的“无需修改 API 规范”需要分层理解：

- **网关能力开关不要求新增流式专属注解**；不代表后端协议、超时、客户端解析和业务契约都不用调整。
- **SSE 默认总时限仍是 15 秒**；最长 3,600 秒不是默认时长，持续发送心跳也不会重置这个总时限。
- **普通流式代理、模型路由、内置 MCP 端点不是同一张能力表**。普通网关支持 WebSocket/gRPC，不代表模型路由或 MCP 转换层也支持。
- 本地实验中，边生成边发送把首条有效内容的中位等待从约 **418 毫秒降到 107 毫秒**，但全部完成仍约 **418 毫秒**。这是人为设置生成间隔的机制演示，**不是 Google Cloud 性能测试**。

本文以原文为研究对象，结合 2026-11-02 实际读取的官方配置文档、HTTP/SSE/gRPC 规范及本地实验，回答一个更实际的问题：怎样让流式接口既尽早反馈，又在断流、超时、慢消费者和权限约束下保持可解释的行为？

## 一、原文真正解决的是“双轨入口”

原文的论证可以重构为三步。

**问题：治理入口与实时体验发生冲突。** 传统请求—响应模式通常等待完整结果；模型输出、任务进度和交互会话却希望增量交付。按作者对旧产品的描述，团队为了流式体验绕开网关，形成普通接口受统一治理、流式接口另走一条路径的局面。这是厂商对自身产品演进的说明，不是“所有 API 网关过去都不支持流式”的行业结论。

**机制：把增量转发纳入同一个入口。** 新网关在后端产生数据时逐步转发，而不是必须等到响应结束。原文列出的模式包括 SSE、HTTP 响应流、WebSocket，以及 gRPC 服务端流和双向流；原有 API key 校验、JWT 校验、到后端的服务账号认证、路径路由、Cloud Logging 与 Cloud Monitoring 集成继续适用。

**结果：实时接口可以重新进入统一治理路径。** 但“仍有鉴权和日志”并不能推出“每个 token 都已计费审计”“每条事件都重新鉴权”或“中途取消必然终止模型计算”。这些是另一层实现合同，原文没有给出相应保证。

原文还将 API Gateway 定位为较轻量的 AI 入口，把更广泛的 AI 策略与全生命周期管理指向 Apigee，把 agent 连接治理指向 Agent Gateway，并讨论组合使用。应把它理解为产品分工，而不是所有能力可以在一份配置里任意相加。[来源：原文的 AI workloads 与 API contract 小节](https://developers.googleblog.com/streaming-comes-to-api-gateway-real-time-and-ai-ready-apis-without-changing-your-spec)。

## 二、“流式”至少涉及三层边界

先沿一次模型回答走一遍：模型生成文本片段，应用把片段编码为事件，HTTP 层承载字节，网关向客户端转发，客户端解析事件，界面再更新文字。每一层看到的“块”都可能不同。

### 1. HTTP 分块不等于业务事件

HTTP/1.1 的 chunked transfer coding 让发送方不必事先知道整个响应长度，使用长度前缀组织一连串数据块，以零长度块结束。它是**传输分帧**；中间节点可以解码、重新分块。HTTP/2 则用 DATA frame 承载正文，不能继续使用 HTTP/1.1 的 chunked transfer coding。[RFC 9112 §7.1](https://www.rfc-editor.org/rfc/rfc9112.html#section-7.1)、[RFC 9113 §8.1](https://www.rfc-editor.org/rfc/rfc9113.html#section-8.1)。

因此：

- 一个模型 token 不保证对应一个 SSE 事件。
- 一个 SSE 事件不保证对应一个 HTTP chunk、HTTP/2 frame 或一次客户端读取。
- 一次读取可能包含多个事件，也可能只包含半个事件，甚至半个 UTF-8 汉字。
- 仅看到 `Transfer-Encoding: chunked`，不能证明用户已获得低延迟的增量反馈：应用仍可以先攒完整个结果，再发送一个大块。

最后一点会在本地实验中直接复现。

### 2. SSE 定义事件，不定义模型任务

Server-Sent Events 是服务端到客户端的单向事件流。其媒体类型是 `text/event-stream`，文本使用 UTF-8；空行结束一个事件，多条 `data:` 行以换行连接，`event:` 可命名事件，`id:` 可提供恢复游标，冒号开头的行是注释。[WHATWG HTML：SSE 解析与处理规则](https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream)。

下面是本文实验使用的**应用自定义协议片段**，不是所有模型接口的通用格式：

```text
id: 1
event: delta
data: {"text":"流"}

id: 5
event: done
data: {"complete":true}

```

`done` 在这里是应用约定，不是 SSE 内建的成功标志。同样，某些 OpenAI-compatible 接口使用的 `data: [DONE]` 是上层约定，不是 SSE 标准要求；Google 的 vLLM 示例确实展示了这一结束标志。[官方流式示例](https://docs.cloud.google.com/api-gateway/docs/streaming-configure#stream-responses-from-an-llm)。

### 3. 不同交互模式不应只凭“实时”选协议

| 模式 | 交互特点 | 需要自己定义的部分 |
| --- | --- | --- |
| HTTP 响应流 / NDJSON | 同一响应逐步返回；NDJSON 通常按行组织 JSON | 每条记录的结构、错误与结束语义 |
| SSE | 服务端单向事件，适合输出与进度 | 业务事件、保留历史、恢复与去重 |
| WebSocket | 双向消息会话，适合双方持续交互 | 消息协议、确认、重连后的会话恢复 |
| gRPC streaming | 类型化 RPC；服务端流、客户端流和双向流是不同方法形态 | deadline、最终状态与业务幂等性 |

gRPC 规范保证一次 RPC 内对应消息流的顺序，但这不是跨断线、跨新 RPC 的恰好一次交付保证。客户端和服务端甚至可能对一次调用是否成功得出不同结论：服务端已经发完，客户端却在 deadline 后才收到。[gRPC 核心概念与生命周期](https://grpc.io/docs/what-is-grpc/core-concepts/)。

不要把原文“这些应用需要双向连接”的概括套到每个场景：模型逐字输出和任务进度通常只需要服务端单向流；协作编辑、实时语音会话才更可能需要持续双向交互。

## 三、“不改规范”为什么仍可能需要改配置和客户端

### 能力开关与已有配置是两件事

原文说，没有新的流式专属扩展、注解或独立描述文件。这意味着可以沿用既有 API 描述方式，而不是承诺任意现有规范都已经适合长连接。

[官方配置文档](https://docs.cloud.google.com/api-gateway/docs/streaming-configure)明确要求：

- gRPC 后端使用 `h2`。
- 这个产品的 WebSocket 后端路径使用 `http/1.1`，进行 Upgrade 握手。不要把这一产品要求外推为所有 WebSocket 实现只能如此。
- SSE 与增量 HTTP 响应可以使用 HTTP/1.1 或 `h2`；文档推荐 `h2`。
- 长响应需要配置既有的 `deadline` 字段，而不是期待启用 streaming 自动延长它。

OpenAPI 2.0 在 `x-google-backend` 中配置这些字段；OpenAPI 3.x 使用 `x-google-api-management.backends` 中的命名后端，再由 `x-google-backend` 引用。**这些是已有配置机制，恰好说明“不新增规范语言”与“不调整规范文件”不能画等号。**

### 传输兼容不等于业务兼容

原先承诺返回一个完整 JSON 对象的接口，如果改成多个 SSE 事件，旧客户端的整包 JSON 解析就会失败。即使最终文字完全相同，响应媒体类型、解析方式、错误语义和完成时刻都变了。

[工程建议] 已有非流式消费者时，应通过明确的请求选项、媒体类型协商或单独版本保留旧合同，不能仅凭网关接受同一份 OpenAPI 就认定兼容。规范可以描述业务，但并不因此执行所有业务校验：Google 的 [OpenAPI 3.x 限制](https://docs.cloud.google.com/api-gateway/docs/openapi-v3-limitations)还说明，参数、类型等多项定义不会被网关强制执行，OAuth scopes 也不会被检查。需要的字段校验和细粒度授权仍要落实到服务。

### 浏览器 EventSource 不是任意模型 API 的万能客户端

原生 `EventSource` 构造接口只有 URL 和 `withCredentials` 选项，没有 POST body 或任意 `Authorization` header 的配置入口；其标准提供自动重连与 `Last-Event-ID` 机制。[WHATWG EventSource 接口](https://html.spec.whatwg.org/multipage/server-sent-events.html#the-eventsource-interface)。

模型接口常见的是带 JSON 请求体的 POST。这样的接口通常应使用支持流式读取的 SDK，或使用 `fetch` 配合成熟的 SSE 解析器；不能把普通 EventSource 示例不加改造地套上去，也不能假定换成 `fetch` 后自动继承 EventSource 的重连行为。不要为了绕过 header 限制，把长期凭据塞进 URL。

## 四、最容易误读的数字：一小时是上限，不是默认值

以下口径来自 [streaming 配置文档](https://docs.cloud.google.com/api-gateway/docs/streaming-configure#set-the-stream-deadline)，并与 [gcloud 创建命令说明](https://docs.cloud.google.com/sdk/gcloud/reference/api-gateway/gateways/create)交叉核验，适用于 streaming-enabled gateway。

| 请求类型 | `deadline` 约束什么 | 默认与上限 |
| --- | --- | --- |
| 非流式 HTTP | 整个请求的总时长 | 默认 15 秒；最高 3,600 秒 |
| SSE / HTTP 响应流 | 整个响应的总时长 | 默认 15 秒；最高 3,600 秒 |
| gRPC streaming | 消息之间的空闲间隔 | 默认 300 秒；最高 3,600 秒；总时长固定最多 3,600 秒 |
| WebSocket | 消息之间的空闲间隔 | 默认 300 秒；低于 300 秒的设置被忽略；总时长固定最多 3,600 秒 |

对 SSE 来说，这个网关层没有另一个独立生效的 idle timeout；**总 deadline 不会因为有数据持续到达而重新计时**。这不排除你的后端、负载均衡器、客户端或其它中间层另外设置空闲超时。

设想后端每秒发一次进度：若 SSE 的 `deadline` 保持默认，约 15 秒仍会截止，而不是靠心跳一直活到一小时。心跳可以帮助处理其它链路的空闲检测或应用存活判断，却不能改变网关的总时限。

[推测] 从设计约束推导， 实际可用时长受链路上最早触发的约束限制，不能只检查网关。总时限和空闲时限还应分别比较，不能把二者机械合成同一种计时器。官方示例把网关设为 **570 秒**、后端服务设为 **600 秒**，意图是让网关的时限先到；这个例子不是所有服务都应该采用的固定配置。

## 五、三种产品功能，必须分别判断

### 普通网关流式代理

它负责把已经支持相应协议的后端纳入统一入口。它不会让只会一次性生成完整 JSON 的应用，自动变成有进度事件、可恢复游标的任务系统。

### 模型路由

[模型路由官方说明](https://docs.cloud.google.com/api-gateway/docs/model-routing-overview)描述的是：接收 OpenAI-compatible 请求，检查 JSON 中的 `model`，按照配置匹配目标，转码后发往 Model Garden 中支持的 MaaS 模型。它不是基于任务难度自动挑选“最好模型”的智能策略。

这条路径有单独限制：

- 要求 OpenAPI 3.x；同一路由器引用的模型需共享规定的后端 hostname。
- 支持**响应侧 SSE**，不支持请求侧流式、gRPC、WebSocket 或 Gemini Live。
- 同一份规范不能混合模型路由与普通路由操作。
- 文档要求请求显式携带 `model`；Preview 中缺少该字段的处理存在已知问题，客户端不能依赖理想的拒绝行为。

所以，“普通流式网关支持 WebSocket”不能推导出“模型路由可以透明承载双向实时语音”。同理，原文说外部自托管流式后端也能工作，不能推导出其**托管模型路由器**可随意路由任意外部模型地址。

### 网关内置 MCP 转换

[内置 MCP 功能](https://docs.cloud.google.com/api-gateway/docs/mcp-overview)是把已有 REST API 暴露成 MCP 工具：接收 JSON-RPC，完成鉴权和映射，调用 REST 后端，再转换响应。它不是单纯把任意 MCP 服务逐字节透传。

官方明确列出：不支持流式或长时间工具调用；同一 API config 中 MCP 与 Model Routing 互斥。流式配置文档进一步说明，**只加 `--enable-streaming` 不会让这个 MCP 端点流式输出，其响应仍是单个 `application/json` 正文**。[MCP 限制](https://docs.cloud.google.com/api-gateway/docs/mcp-overview#limitations)、[Streaming 限制](https://docs.cloud.google.com/api-gateway/docs/streaming-configure#limitations)。

因此，这里不能把“streaming + model routing + MCP”理解成同一条调用路径上三项能力任意组合。对于自己托管的远端 MCP 服务能否以普通路由透传、具体 Streamable HTTP 行为如何，本文没有实测，不将内置转换端点的限制扩展成 MCP 标准本身的限制。

## 六、可靠的流式接口，需要一个“完成合同”

### 已经返回 200，后面仍然可能失败

HTTP 最终状态和响应头一旦发出，就不能再把已经发出的 `200` 改成另一个最终状态。失败可能发生在第一个事件之后、最后一个事件之前。gRPC 有最终状态与 trailing metadata；SSE 的业务协议则需要自行约定错误和结束事件。

[工程建议] 应用至少区分三种结果：

1. 收到约定的成功结束标志，业务完成。
2. 收到明确的业务错误事件，业务失败。
3. 流关闭或网络出错，但没收到结束标志，**结果未知或不完整**。

不要把“TCP/HTTP 读到 EOF”直接当成“模型完整回答”。也不要把最后半个 JSON 或缺少空行的 SSE 事件强行补齐；SSE 标准要求丢弃未完整终止的事件。

### 重连只是恢复传输，不自动恢复任务

EventSource 会在符合其规则的断流场景重连，并携带已记录的 `Last-Event-ID`。但标准没有替服务端保存历史，也没有替应用执行去重或恢复计算。[WHATWG 重连处理](https://html.spec.whatwg.org/multipage/server-sent-events.html)。

[工程建议] 对可恢复任务，可以设计：

- 稳定的 `job_id` 标识计算任务，而不是把任务绑定到某一条连接。
- 服务端保留带单调序号的事件记录，并规定保留时间与游标过期行为。
- 客户端提交自己**已处理**的位置，按事件 ID 去重；不要只记录已经收到但尚未持久处理的位置。
- 恢复失败时明确返回“历史不可恢复”，由应用决定重新查询最终结果还是重新发起任务。

对于下单、写文件等带副作用的工具，重发请求可能重复执行；幂等键或业务去重应该保护的是实际副作用，不只是输出文字。恢复同一个任务与重新采样一次模型回答不是同一件事。

本报告的实验仅用静态事件表演示“带游标取剩余事件”，没有实现持久任务、自动重连或恰好一次执行。

### 取消也要穿过整条调用链

[待验证] 真实部署需要检查：用户关闭页面后，网关是否及时感知，后端是否收到取消，模型任务是否停止，以及结算如何记录。只看到客户端连接关闭，不能证明 GPU 工作已结束；HTTP/2 的流量控制也不能代替业务取消。

## 七、性能与治理的重心从“请求数”扩展到“在途工作”

### 慢消费者会把流式优势变成缓冲积压

只要生产速率长期大于消费速率，待发送队列就会增长。HTTP/2 有逐流和连接级流量控制，但它是**逐跳**的：客户端—网关与网关—后端分别控制各自连接，标准没有保证远端模型生成调度随客户端消费自动同步。[RFC 9113 §5.2](https://www.rfc-editor.org/rfc/rfc9113.html#section-5.2)。

[推测] 从逐跳机制推导， 如果中间层不停读取上游，再把数据堆进无界应用队列，即使底层协议有流控，应用仍可能耗尽内存。因此需要有界队列、暂停读取、明确的丢弃或终止策略，并验证取消传播。限速应配合并发与预算控制，而不只限制连接建立次数。

可以用一组**假设值，不是产品配额或实测容量**理解量级：稳定状态下，每秒开始 50 个请求、平均持续 60 秒，平均在途量约为 `50 × 60 = 3,000`。若每条连接仅预留 64 KiB 应用队列，也已有 **187.5 MiB**，还没算 TLS、运行时、网关及后端开销。这个估算来自到达率与平均驻留时间的关系，不能作为容量保证。

### 首字节、首条有效内容、完整结果是三种指标

原文明确说，网关的 request latency 对流式连接衡量的是流的生命周期，不是 time-to-first-byte。于是长连接启用后，延迟曲线变高可能只反映业务持续更久，不能立即断言体验退化。

[工程建议] 至少同时观察：

- 响应头或首字节到达时间：主要定位接入与前置等待。
- 首条**有效内容**到达时间：不能用空事件或心跳冒充；模型侧的 TTFT 也应明确从哪里开始计时。
- 有效事件间隔及长时间无进展比例。
- 总时长、业务成功结束率、无结束标志断流率。
- 当前活跃流数、缓冲队列、取消后仍存活的工作、任务或 token 预算消耗。

分位数还应区分冷启动、正常完成、用户取消和超时。本文没有测量这些云端分位数，也不提供虚构 SLO。

### 保留鉴权，不等于完成所有 AI 治理

网关身份校验与后端服务账号认证属于不同信任边界：前者回答“谁能进入”，后者回答“网关以什么身份访问服务”。流式支持保留这两层，但不自动证明每个工具参数合法、每条事件被内容审查、每个消费者的 token 成本被限制。

[工程建议] 开始昂贵计算前先完成必要鉴权与预算检查；长任务还要定义权限撤销、凭据过期后的行为。需要全量内容检查才能决定是否放行的场景，与立即逐段外发存在直接张力：已经发送出去的内容无法靠后续拦截撤回。这是产品安全策略的选择，不能由传输开关替代。

## 八、本地实验：同样叫 chunked，体验为什么完全不同

### 实验设置与复现

实验使用 Python **3.14.5** 标准库，在本机回环地址上运行 HTTP/1.1 服务；不访问云资源、不调用真实模型。服务端按顺序产出“流、式、响、应”四个事件，每个事件前等待 **0.1 秒**，最后发应用自定义 `done` 事件。

两种模式都立即发送响应头，都使用 chunked transfer coding：

- `stream`：每个业务事件产生后即发送，并故意拆成两个 HTTP chunk。
- `buffered`：在同一个服务进程中模拟整包缓冲，攒完全部业务事件才发送正文。

客户端每次最多读取 7 字节，先增量解码 UTF-8，再按事件边界解析。两种模式交替运行，各 5 次；计时从发起 HTTP 请求前开始，首条有效内容定义为完整 `delta` 事件解析完成。

[实验源码](./assets/api_gateway_streaming_20261102/streaming_lab.py) · [完整实测输出](./assets/api_gateway_streaming_20261102/results.json)

从仓库根目录复现：

```bash
python3 cs-learning/reports/knowledge_reports/assets/api_gateway_streaming_20261102/streaming_lab.py
```

脚本也支持 `--output <新JSON路径>`，已有文件不会被覆盖。不要把此实验服务或其简化 SSE 解析器用于生产。

### 结果一：更早可见，不等于更早算完

下表为每种模式 5 次的**各项中位数**，单位毫秒；不同列不一定来自同一次请求。

| 模式 | 响应头收到 | 首条有效内容 | HTTP 响应结束 |
| --- | ---: | ---: | ---: |
| 边产出边发 | 1.918 | 107.420 | 417.859 |
| 全部缓冲后发 | 1.376 | 418.001 | 418.295 |

缓冲模式甚至很早就发出了响应头，但用户仍看不到有效内容。两种模式总耗时相近，是因为相同的四次人工等待没有消失；差异在于内容可见的时间。

这些数字由本机调度、回环网络和人为等待共同决定，只支持机制判断。它们不能证明 Google API Gateway 的附加延迟、并发容量或真实模型速度。

### 结果二：半包不能当作事件解析

测试覆盖了测试字节流的 **221 个单切分位置**，另外验证逐字节喂入、多行 `data:` 合并，以及未用空行结束的事件被丢弃。即使切分发生在汉字编码中间，增量解码后的事件仍保持一致。

这个测试只覆盖实验声明的 LF 换行子集，不覆盖完整 SSE 的 CR、CRLF、BOM、`retry` 等规则。生产环境应采用成熟解析库；实验保留简化实现，是为了让“传输边界不同于业务边界”可观察，而不是重新造一套 EventSource。

### 结果三：HTTP 成功结束，也可能只有半个回答

`/cut` 在事件 1、2 后发送合法的 HTTP chunked 结束块。客户端得到 **HTTP 200**、正常 EOF 和“流式”，但未收到 `done`，因此标记 `semantic_complete: false`。

随后客户端显式携带 `Last-Event-ID: 2` 请求静态事件表，收到 3、4、5，补成“流式响应”。这证明需要区分 HTTP 完整性与业务完整性，也演示了游标的作用；它没有证明网络重连会自动继续原计算，更没有证明副作用恰好执行一次。

## 九、怎样迁移：先确认真实模式，再验证整条链路

### 创建方式与默认模式不能混为一谈

原文给出的 Preview 入口是创建新网关时加参数。以下是官方命令模板，**本文没有执行云端创建**：

```bash
gcloud api-gateway gateways create GATEWAY_ID \
  --api=API_ID \
  --api-config=CONFIG_ID \
  --location=REGION \
  --enable-streaming
```

已创建网关不能原地切换 streaming mode。当前读取的文档还补充：省略参数不等于明确关闭，由 API config 与平台默认值共同解析；配置 Model Router 时会产生 streaming gateway。因此，验收应读取实际状态，而不是猜测命令省略参数的后果：

```bash
gcloud api-gateway gateways describe GATEWAY_ID --location=REGION
```

确认输出的 `effectiveStreamingMode` 是 `EFFECTIVE_STREAMING_MODE_ENABLED`。[官方启用与验证说明](https://docs.cloud.google.com/api-gateway/docs/streaming-configure#enable-streaming-on-a-gateway)。原文关于 GA 时无需 opt-in 的表述是计划，不能据此断言已经 GA。

### hostname 更可预测，但迁移成本没有消失

新流式网关使用 `GATEWAY_ID-PROJECT_NUMBER.REGION.gateway.dev` 形态，便于事先生成配置；既有非流式 hostname 和早期流式 hostname 有不同形态。官方说明早期 `run.app` 形态的网关不会自动迁移。可预测性改进不等于原有 URL 保持不变。[hostname 与兼容限制](https://docs.cloud.google.com/api-gateway/docs/streaming-configure#limitations)。

[工程建议] 迁移采用新旧路径并行验证，保留能回退的旧消费者路径；检查调用地址、允许列表和身份 audience 等绑定。对于原先必须使用自定义域名或指定接入拓扑的服务，先确认预览限制，再决定能否迁移。

原文列出初始 Preview 不支持 Cloud console 启用、Terraform，以及通过 Serverless NEG / 外部 Application Load Balancer 的自定义域名。此次读取的配置文档仍明确列出 Terraform、Serverless NEG 与该负载均衡/自定义域名路径的限制；Console 部分只按原文的初始发布状态记录，没有独立验证其现状。**修改 DNS 名称本身不能替代负载均衡集成、路由和 TLS 证书支持。**

### 上云验收应验证行为，而不是只验证开关

下面是部署前可执行的验收设计，**不是已经完成的云端测试**：

1. **增量性**：对比直连后端和经过网关的首条有效内容、事件间隔；`curl -N` 可关闭 curl 的输出缓冲，但不能证明其它层没有缓冲。
2. **协议与内容**：确认实际媒体类型、客户端与后端协议、半包与多事件读取；不要手动把 HTTP/1.1 的 chunked header 当成 HTTP/2 必需项。
3. **边界时间**：验证 SSE 总 deadline、WebSocket/gRPC 空闲间隔和绝对上限；心跳持续发送时也测试 SSE 截止。
4. **失败与恢复**：首事件前失败、中途失败、合法 EOF 但缺结束事件、游标过期、重复事件及非幂等任务重试。
5. **资源释放**：客户端取消、慢速读取和断网之后，检查应用队列与后端计算是否及时释放。
6. **治理与回退**：无效凭据、调用预算、日志脱敏、真实 hostname、旧客户端兼容与回退路径。

任何涉及创建网关、部署服务、授予 IAM 权限或产生云账单的动作，都应单独授权。本次学习没有进行这些操作。

## 十、局限与可迁移的判断

本文验证的是三类不同证据：**厂商发布主张、官方文档中的配置与限制、标准和本地实验揭示的机制**。它们不能相互冒充。

- 没有 Google Cloud 部署或账号权限验收；未实测 WebSocket、gRPC、HTTP/2、云端鉴权、超时与取消传播。
- 博客与各文档页脚更新时间不一致；以读取时实际内容作对照，不根据日期先后臆测功能已上线或已修复。本文仅将“已支持”用于明确的官方口径，不视为独立生产验证。
- 本地实验不含真实网关、反向代理、压缩、TLS、跨地域网络和模型冷启动，也没有并发压力测试。
- 不给出未经测量的吞吐上限、P95/P99 或成本节省比例。Preview 的计费与功能限制可能变化，采购和上线应重新核验。

能迁移到其它系统的判断是：**流式是端到端属性；规范兼容是分层属性；成功必须有业务完成条件；资源与治理必须覆盖整个在途工作，而不只覆盖连接建立瞬间。**

## 思考与追问

### 我真正理解了什么？

“网关支持流式”意味着中间层不必再成为整包交付的强制障碍，但低延迟体验仍需要后端、传输、解析和渲染协同。最危险的误判不是漏配一个开关，而是把传输连通误当作业务正确：默认 15 秒与一小时上限、HTTP 200 与完整回答、重连与恢复任务，分别是不同问题。

### 我还没搞懂什么？

在这个产品的真实链路中，慢消费者的背压能传多远？客户端断开后，网关、服务和模型计算各需要多久停止？哪一层能够可靠区分用户取消、超时和业务完成？现有文档不能替代这些实测，尤其不能由“Cloud Monitoring 已集成”推出答案。

### 下一步读什么或做什么？

优先沿[官方流式教程](https://docs.cloud.google.com/api-gateway/docs/streaming-configure)在获授权的测试环境完成第九节验收，先测 SSE 的首条内容、15 秒默认截止和取消传播，再决定是否研究 WebSocket/gRPC。协议层继续阅读 [RFC 9113 的流量控制](https://www.rfc-editor.org/rfc/rfc9113.html#section-5.2)与 [WHATWG 的重连、事件 ID 和解析规则](https://html.spec.whatwg.org/multipage/server-sent-events.html)，把恢复合同落实到一个持久任务，而不是只做“页面逐字出现”的演示。

## 来源与核验范围

以下公开来源均于 **2026-11-02** 实际读取；长规范仅核验列明章节，不声称通读全文。

1. [Google Developers Blog：Streaming comes to API Gateway](https://developers.googleblog.com/streaming-comes-to-api-gateway-real-time-and-ai-ready-apis-without-changing-your-spec)，2026-10-22。全文；发布动机、支持模式、保持原有治理能力、hostname、Preview 边界与产品分工。
2. [Configure streaming for LLM responses and other traffic](https://docs.cloud.google.com/api-gateway/docs/streaming-configure)。正文；后端协议、deadline、实际模式、示例与限制。
3. [gcloud api-gateway gateways create](https://docs.cloud.google.com/sdk/gcloud/reference/api-gateway/gateways/create)。创建参数、默认选择与协议相关超时行为。
4. [Overview of model routing](https://docs.cloud.google.com/api-gateway/docs/model-routing-overview)。请求流程与限制；不使用其产品收益表述作为独立性能证据。
5. [Model Context Protocol overview](https://docs.cloud.google.com/api-gateway/docs/mcp-overview)。REST 到 MCP 的转换机制、流式限制与配置互斥。
6. [OpenAPI 3.x feature limitations](https://docs.cloud.google.com/api-gateway/docs/openapi-v3-limitations)。参数/类型和 scopes 不强制执行的边界。
7. [WHATWG HTML：Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html)。§9.2.1—9.2.6 的接口、重连、编码与事件解析。
8. [RFC 9112：HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112.html#section-7.1)。§7.1 的分块、结束与逐连接性质。
9. [RFC 9113：HTTP/2](https://www.rfc-editor.org/rfc/rfc9113.html#section-5.2)。§5.2、§8.1 的逐跳流控与 DATA frame。
10. [gRPC：Core concepts, architecture and lifecycle](https://grpc.io/docs/what-is-grpc/core-concepts/)。RPC 流类型、顺序、最终状态、deadline 与取消。
11. [本地实验源码](./assets/api_gateway_streaming_20261102/streaming_lab.py)与[运行输出](./assets/api_gateway_streaming_20261102/results.json)。两种发送模式各 5 次、221 个单切分位置及语义不完整/游标恢复案例；只支持本文明确限定的机制结论。

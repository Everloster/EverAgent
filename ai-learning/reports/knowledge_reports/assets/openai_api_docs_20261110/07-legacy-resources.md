# Legacy & resources｜历史接口、迁移与资源

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md)

本卷用于查阅历史接口、了解退役时间和迁移已有应用，也保留 GPT Actions 与官方教程入口。涉及旧产品的操作，应先看弃用时间表，再阅读具体指南。

## Lifecycle｜更新与弃用

<a id="doc-10"></a>
### API changelog｜API 更新日志
[原文](https://developers.openai.com/api/docs/changelog)

更新日志按日期记录模型、接口、SDK 和工具的变化，可以用来查某项功能何时发布、参数何时调整。历史条目中的价格、推荐型号和“最新”都属于当时的产品情况；准备接入时，还要对照当前模型卡和指南。

<a id="doc-12"></a>
### Deprecations｜弃用与停止服务
[原文](https://developers.openai.com/api/docs/deprecations)

Legacy 表示接口或模型不再积极更新，deprecated 表示已宣布退役，shutdown／sunset 表示停止提供服务。弃用页列出通知日期、停止时间及建议替代方案；Models API 也可返回可选的 `shutdown_date`。

按本次快照，Assistants 已于 2026 年 8 月 26 日停用，Videos／Sora API 已于 9 月 24 日停用。Evals 已进入只读阶段，Evals、Agent Builder 和可复用 prompts 计划于 11 月 30 日关闭。保留这些文档，是为了帮助维护和迁移旧应用。

## Legacy APIs and migration｜旧接口与迁移

<a id="doc-8"></a>
### Assistants migration guide｜Assistants 迁移
[原文](https://developers.openai.com/api/docs/assistants/migration)

Assistants API 已停止提供服务，新集成使用 Responses。迁移时，将 Thread 中的对话整理为 Conversation，将 Run 改为 Response，将运行步骤改为输入和输出 Items，并由应用明确管理工具循环。

历史数据需要使用应用已经保存的副本。此页早期方案还使用可复用 prompt objects，而它们也进入了退役流程；配置和提示应结合 prompt-object 迁移指南，转入应用代码管理。

<a id="doc-49"></a>
### Completions API｜旧文本补全
[原文](https://developers.openai.com/api/docs/guides/completions)

旧 Completions API 接收自由文本 `prompt`，从 `choices.text` 返回补全文字，也支持用 `suffix` 指定后缀、在中间插入内容。它与基于消息的 Chat Completions、基于 Items 的 Responses 使用不同请求结构。

页面示例中的旧模型已经停止服务。`max_tokens`、`best_of` 和 `suffix` 等参数保留作历史参考，迁移时按目标接口重新组织请求。

## Agent Builder｜可视化工作流与迁移

| 原文 | 中文导读 |
|---|---|
| <a id="doc-19"></a>[Agent Builder](https://developers.openai.com/api/docs/guides/agent-builder) | Agent Builder 用节点和有类型连接构造工作流，可以预览运行、发布版本，再接入 ChatKit 或导出 Agents SDK 代码。产品处于退役过渡期；ChatKit 继续提供，新工作流应按迁移路线部署。 |
| <a id="doc-137"></a>[Node reference](https://developers.openai.com/api/docs/guides/node-reference) | Start 定义工作流输入，Agent 配置模型和指令，Note 保存说明；File search、MCP 和 Guardrails 提供工具与检查。If/else、While 和 Human approval 控制流程，Transform 与 Set state 处理数据及状态。可用这些定义读懂已有工作流，再准备迁移。 |
| <a id="doc-177"></a>[Safety in building agents](https://developers.openai.com/api/docs/guides/agent-builder-safety) | 提示注入会让不可信材料试图改变 Agent 的指令，工具调用还可能泄露私有数据。应用可通过区分 developer 与 user 输入、约束数据结构、设置工具审批和检查 trace 来降低风险；这些措施需结合使用并在实际流程中验证。 |
| <a id="doc-123"></a>[Migrate from Agent Builder](https://developers.openai.com/api/docs/guides/agent-builder/migrate-from-agent-builder) | 迁移 Agent Builder 时，先从工作流导出完整的 Python 或 TypeScript Agents SDK 代码。可以把它放入自己的应用继续部署，也可以作为材料重建 Workspace Agent。控制流、触发器、工具、认证和权限仍需逐项测试，导出不保证所有行为自动无损迁移。 |

## Evals｜过渡期评估平台

| 原文 | 中文导读 |
|---|---|
| <a id="doc-98"></a>[Getting started with datasets](https://developers.openai.com/api/docs/guides/evaluation-getting-started) | Datasets 可以从 CSV 导入，也可以在界面中录入样本，再配置提示、生成输出、添加人工意见和 grader。数据字段分别提供任务输入与参考答案，评语用于指出具体问题。该托管功能已进入只读过渡期。 |
| <a id="doc-231"></a>[Working with evals](https://developers.openai.com/api/docs/guides/evals) | Evals API 用 `data_source_config` 定义测试数据结构，用 `testing_criteria` 定义评分标准，再以输入样本创建 run。运行后查询状态、用量和报告，分析失败样本。JSONL、模板变量和 webhook 的示例按平台过渡期规则保留。 |
| <a id="doc-102"></a>[Graders](https://developers.openai.com/api/docs/guides/graders) | Grader 将模型结果与参考答案比较，可以用字符串检查、文本相似度、模型评分或 Python 代码实现。模板从 `item` 和 `sample` 读取数据。评分器应先用人工判断校准，并处理约束及运行错误；它随所依赖的评估和微调流程过渡。 |
| <a id="doc-84"></a>[Evaluate external models](https://developers.openai.com/api/docs/guides/external-models) | Evals 曾支持平台提供的第三方模型和用户配置的兼容端点，后者需要相应凭据。功能资格、管理员开关、费用和限额各有规定。发送给外部模型的数据由第三方处理，适用其服务条款；平台本身的退役时间也需一并核对。 |
| <a id="doc-155"></a>[Prompt optimizer](https://developers.openai.com/api/docs/guides/prompt-optimizer) | Prompt optimizer 利用数据集中的输出、人工评语和 grader 结果修改提示。反馈越具体，越容易定位需要改进的行为；优化后的提示仍需回到测试集检查，因为部分输入可能退步。数据集驱动的托管优化器随 Evals 平台退役。 |
| <a id="doc-199"></a>[Trace grading](https://developers.openai.com/api/docs/guides/trace-grading) | Trace grading 对一次 Agent 运行中的决策、工具调用和交接设置评分或标签，用来定位失败步骤。再对多条 trace 运行同一评估，可以比较提示或编排改动，而不仅看最终回答是否合格。 |

新的开源评估入口见 [Production：Promptfoo](06-production.md#doc-97)；一般评估设计见 [Evaluation best practices](06-production.md#doc-85)。

## Fine-tuning｜微调

本组解释文档所保留的微调方法与工作流，不把历史模型表当成当前可用列表。自助微调不再向新用户开放；既有合格用户的训练窗口和推理寿命还取决于具体基础模型。

| 原文 | 中文导读 |
|---|---|
| <a id="doc-129"></a>[Model optimization](https://developers.openai.com/api/docs/guides/model-optimization) | 改进模型输出，可以先建立评估基线，调整提示和上下文，再按任务考虑微调。用代表性测试观察改动效果，再据错误修改提示或训练数据。此页涉及的托管 Evals 和微调工作流正在转入历史文档，使用资格与时间表见弃用页。 |
| <a id="doc-192"></a>[Supervised fine-tuning](https://developers.openai.com/api/docs/guides/supervised-fine-tuning) | 监督微调使用代表性的输入与理想输出训练模型。先整理为规定的 JSONL 格式，上传并创建训练任务，再用独立评估检查结果和 checkpoint。数据也可以包含结构化输出或工具调用；训练完成后仍需验证目标任务表现与安全要求。 |
| <a id="doc-79"></a>[Direct preference optimization](https://developers.openai.com/api/docs/guides/direct-preference-optimization) | DPO 为同一个 prompt 提供较受偏好和较不受偏好的回答，让模型学习语气、重点或其他偏好。它可与 SFT 结合使用，训练数据和安全检查分别有格式要求。方法说明保留在此，平台资格和基础模型期限按退役时间表处理。 |
| <a id="doc-221"></a>[Vision fine-tuning](https://developers.openai.com/api/docs/guides/vision-fine-tuning) | 视觉微调把图像输入加入 SFT 样本，可使用图像 URL 或 base64 data URL。训练前要检查格式、尺寸、内容限制和被跳过的原因，并根据需要设置 detail 与预算。训练后的质量仍需用目标图像任务验证。 |
| <a id="doc-92"></a>[Fine-tuning best practices](https://developers.openai.com/api/docs/guides/fine-tuning-best-practices) | 微调效果不足时，先检查剩余错误对应的训练样本：信息是否齐全、标注是否一致、分布是否接近实际请求。数据质量清楚后，再考虑样本数量、epochs、学习率和 batch size。训练与测试应分开，多轮权重和超长样本也要按规则处理。 |

## GPT Actions｜Custom GPT 的外部接口

这些是 ChatGPT Custom GPT 的产品集成说明，不是直接调用 Responses 的同一套配置。

| 原文 | 中文导读 |
|---|---|
| <a id="doc-4"></a>[GPT Actions](https://developers.openai.com/api/docs/actions/introduction) | GPT Actions 让 Custom GPT 根据自然语言请求调用外部 REST API。开发者提供 OpenAPI schema、认证配置和使用说明，模型选择操作并生成参数，Action 执行后把结果交回。它可用于检索资料，也可在外部应用中创建或修改记录。 |
| <a id="doc-2"></a>[Getting started](https://developers.openai.com/api/docs/actions/getting-started) | 天气示例先根据经纬度查询对应网格，再用网格位置取得预报。开发者编写并测试 OpenAPI schema，配置认证，在 GPT 编辑器中添加 Action，再用代表性问题测试。接口能调用之后，还需检查 GPT 是否选择了正确操作和参数。 |
| <a id="doc-3"></a>[Authentication](https://developers.openai.com/api/docs/actions/authentication) | Action 可配置为无认证、API key 或每用户 OAuth。无认证适合公开接口，API key 适合应用级访问，OAuth 则允许用户以自己的身份授权。认证回调、token 和 state 需要同时在 GPT 编辑器及第三方服务中正确配置。 |
| <a id="doc-1"></a>[Data retrieval](https://developers.openai.com/api/docs/actions/data-retrieval) | GPT Actions 可以调用 SaaS 的搜索与取回接口，也可以通过中间层查询关系数据库或向量数据库。前者传入结构化查询，后者通常先生成查询 embedding。中间层需要保留用户对原始资料的访问权限，不能仅凭共享服务身份开放所有文档。 |
| <a id="doc-7"></a>[Sending and returning files](https://developers.openai.com/api/docs/actions/sending-files) | Action 接收对话文件时，使用 `openaiFileIdRefs` 取得包含文件信息和短期下载链接的对象。返回文件使用 `openaiFileResponse`，可内嵌 base64 数据或提供 URL。上传与返回的数量、大小、格式和超时要求分别规定。 |
| <a id="doc-6"></a>[Production notes](https://developers.openai.com/api/docs/actions/production) | 公开的 Action 接口需要处理限流、超时和有效 HTTPS 连接，并遵守 schema 与 payload 限制。`x-openai-isConsequential` 影响操作确认方式。接口应返回与请求相关的数据，说明文字也应准确限定操作用途。 |
| <a id="doc-5"></a>[GPT Actions library](https://developers.openai.com/api/docs/actions/actions-library) | Actions 示例库位于 OpenAI Cookbook，包含直接连接 SaaS 的方案，也包含用云函数做预处理、过滤或数据库连接的中间层方案。可从相近应用的示例起步，再按第三方接口的当前认证和参数调整。 |
| <a id="doc-13"></a>[GPT Release Notes](https://developers.openai.com/api/docs/gpts/release-notes) | GPT Release Notes 记录 GPTs 的部分产品变化，例如商店、用户反馈、版本恢复和 Action 文件能力。它是尽力维护的历史列表，查 ChatGPT 的完整变化应继续查看对应发布说明。 |

## Resources and tutorials｜资源与官方教程

| 原文 | 中文导读 |
|---|---|
| <a id="doc-9"></a>[Overview of OpenAI Crawlers](https://developers.openai.com/api/docs/bots) | OAI-SearchBot 用于搜索，GPTBot 用于训练相关抓取，OAI-AdsBot 与 ChatGPT-User 则有各自用途。站点可通过对应 robots.txt 规则分别控制自动抓取；允许搜索和允许训练抓取是独立选择，用户触发的访问另按其说明处理。 |
| <a id="doc-242"></a>[Supported countries and territories](https://developers.openai.com/api/docs/supported-countries) | 支持地区页列出 OpenAI 服务开放的国家和地区。部署或提供服务前应查看当前列表及例外说明；在支持范围之外访问或提供访问，可能导致账号被限制。 |
| <a id="doc-243"></a>[Meeting minutes](https://developers.openai.com/api/docs/tutorials/meeting-minutes) | 会议纪要教程先转写录音，再分别生成摘要、关键点、行动项和情绪分析，最后导出 Word 文档。将这些请求分开，便于检查每一步的结果。原文提供相应语言的 SDK 和 DOCX 库示例，本导读未执行程序。 |
| <a id="doc-244"></a>[Web QA with embeddings](https://developers.openai.com/api/docs/tutorials/web-qa-embeddings) | 网站问答教程先收集有权抓取的网页文字，分块后生成 embedding 并保存索引。用户提问时，用相同的 embedding 模型检索相关片段，再交给模型组织回答。示例以简单文件存储展示原型流程，可据此扩展知识库应用。 |

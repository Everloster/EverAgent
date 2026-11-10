# Models｜模型、文本、提示与多模态

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md)

本卷说明怎样选模型、组织输入和读取输出，并整理文本、图像、向量及各代模型的专门指南。旧版本页面保留在最后，方便维护已有集成。模型名称和产品状态以本导读的来源日期为背景。

## Model catalog and selection｜目录与选型

<a id="doc-237"></a>
### Models｜模型目录
[原文](https://developers.openai.com/api/docs/models)

模型目录按用途提供入口。通用模型可处理推理、写作、代码和图像理解；图像生成、语音、embedding、安全及开放权重模型则各有专门用途。

选择模型后，继续阅读对应模型卡，核对支持的端点、输入输出形式、上下文窗口和价格。目录首页的推荐只是选型起点，实际效果仍需用自己的任务比较。

<a id="doc-238"></a>
### All models｜完整模型列表
[原文](https://developers.openai.com/api/docs/models/all)

完整列表同时收录当前模型、已弃用模型和已停止服务的模型，便于查找具体型号及维护旧应用。列表按通用、图像、音频、专业领域、开放权重和 embedding 等用途分组。找到名称后，还要查看模型卡中的可用状态与迁移说明。

<a id="doc-239"></a>
### Compare models｜模型比较
[原文](https://developers.openai.com/api/docs/models/compare)

比较页将选中模型的上下文窗口、最大输出和支持端点放在同一张表里。Markdown 导出只包含当时显示的比较组合；其他模型与更细的能力差异需要继续查看模型卡。

<a id="doc-240"></a>
### Pricing｜价格
[原文](https://developers.openai.com/api/docs/pricing)

价格按模型、处理速度、上下文长度和输入输出类型分别计算。文本通常以百万 token 为单位，语音、工具、容器和存储则可能按时长、调用或容量计费。

估算一次任务的费用时，要把输入、输出、缓存读写和工具使用分别计入，并检查 Batch、Flex、Fast、Ultrafast 及地域等条件。原文价格表保留了当前报价和部分历史费用，可按实际使用的模型及模式查询。

<a id="doc-130"></a>
### Model selection｜模型选择
[原文](https://developers.openai.com/api/docs/guides/model-selection)

选模型时，先确定任务需要的质量、响应速度、调用频率和可接受成本，再用相同输入比较候选模型。推理强度应单独调整，避免同时改变模型和 effort 后无法判断差异来自哪里。

写作任务可以看受众、语气和有用细节；代码任务看测试和修改结果；计算机操作看实际保存的状态。模型目录和产品页面分别说明 API 与 ChatGPT 中的可用性、工具和限额。

## Text and code｜文本与代码

<a id="doc-195"></a>
### Text generation｜文本生成
[原文](https://developers.openai.com/api/docs/guides/text)

文本生成通过 Responses API 提交 `input`，并用 `instructions` 或消息角色说明行为要求。结果保存在 `output` 数组中，可能同时包含文字、工具调用和推理条目。读取文字时，可以用 SDK 的 `output_text`，或按条目类型提取。

`instructions` 作用于当前生成请求；使用响应 ID 续接时，仍要提供本轮需要的指令。生产提示适合放进应用代码，连同模型快照一起做版本管理、测试和发布。

<a id="doc-45"></a>
### Code generation｜代码生成
[原文](https://developers.openai.com/api/docs/guides/code-generation)

可以直接使用 Codex 在项目中编写、审查和调试代码，也可以在自己的应用中调用具备代码能力的模型。前者已有 Agent 的执行环境与交互入口，后者由应用自行组织模型调用和工作流。

模型选择、前端提示和项目接入分别有专门指南。需要完整编程 Agent 时，可沿 Codex 文档继续；只需要代码生成或问答能力时，从 API 集成开始。

<a id="doc-191"></a>
### Structured model outputs｜结构化输出
[原文](https://developers.openai.com/api/docs/guides/structured-outputs)

Structured Outputs 使用 JSON Schema 约束生成结果的结构，例如必填字段和枚举值。JSON mode 只保证 JSON 语法；函数工具中的 schema 则用于约束调用参数。

SDK 可以从类型定义生成 schema 并解析结果。使用时还要处理拒绝、截断和不符合业务含义的数据；支持的 schema 是 JSON Schema 的子集，对根对象、`required` 和 `additionalProperties` 等有具体限制。支持的模型可通过 `configuration_update` 在会话中更换输出格式。

<a id="doc-18"></a>
### Advanced usage｜高级用法（含旧接口资料）
[原文](https://developers.openai.com/api/docs/guides/advanced-usage)

较早的 Chat Completions 集成可通过固定 `seed` 和其他参数提高输出可重复性，并用 `system_fingerprint` 观察服务端配置变化。配置改变后，即使请求参数相同，结果仍可能变化。

页面还保留 token 估算、frequency／presence penalties 与 logprobs 等用法。它们主要对应旧接口和模型，当前请求应先核对具体参数是否受支持。

## Prompting｜提示设计

<a id="doc-156"></a>
### Prompting｜概览
[原文](https://developers.openai.com/api/docs/guides/prompting)

Prompting 是向模型提供输入的过程。整体角色与语气可以放在较高优先级的指令中，具体任务、材料和示例放在相应输入里。稳定前缀有利于缓存，清晰的组织也方便团队维护。

把提示当作应用代码管理：使用命名模块和明确参数构造动态内容，每次修改都走测试及发布流程。已有可复用 prompt objects 的应用可按迁移指南转到代码管理。

<a id="doc-153"></a>
### Prompt engineering｜提示工程
[原文](https://developers.openai.com/api/docs/guides/prompt-engineering)

提示应把任务、材料和期望结果表达清楚。消息角色确定指令优先级，Markdown 或 XML 分隔可以帮助区分指令、示例与待处理内容。需要模型依据外部材料回答时，将相关上下文提供给它，并预留上下文窗口。

示例用于展示期望行为，数量和细节按任务需要选择。模型版本和提示修改都应经过代表性测试。代码、前端、长任务与推理模型的提示习惯有所不同，可再参考对应专题。

<a id="doc-43"></a>
### Citation Formatting｜引用格式
[原文](https://developers.openai.com/api/docs/guides/citation-formatting)

引用系统先决定引用的粒度：整篇文档容易使用，段落或块更精确，行范围则能定位到具体证据。随后为材料提供稳定的来源 ID 和位置标识，说明何时引用、采用什么格式，再解析模型返回的引用。

托管搜索自带引用信息；自建检索或直接注入材料时，应用需要维护来源映射和显示方式。引用指向的材料与模型声称的依据是否一致，也应在展示前检查。

<a id="doc-124"></a>
### Migrate from prompt objects｜迁移可复用提示对象
[原文](https://developers.openai.com/api/docs/guides/prompting/migrate-from-prompt-object)

可复用 prompt objects 正在退役。迁移时，将原有 prompt 的内容、变量和版本移入代码库，用命名函数及明确参数生成 `instructions` 和 `input`，由代码审查、测试、发布和回滚管理变化。

静态内容尽量保留在前面，动态材料追加在后面，以维持缓存前缀。旧 `v1/prompts` 的时间表与迁移工具见原文及 Deprecations。

<a id="doc-154"></a>
### Prompt generation｜生成提示与 Schema
[原文](https://developers.openai.com/api/docs/guides/prompt-generation)

Playground 的 Generate 功能可以根据任务描述生成提示、函数定义和结构化输出 schema。生成提示时使用 meta-prompt，告诉模型怎样创建或改进提示；生成 schema 时使用 meta-schema，约束输出的 JSON 与函数格式。

原文展示文本、音频和 schema 的生成模板。生成结果还需要清理、验证并在实际任务中测试，尤其要检查字段约束是否符合应用需求。

<a id="doc-94"></a>
### Frontend prompt instructions｜前端提示模板
[原文](https://developers.openai.com/api/docs/guides/frontend-prompt)

这份前端提示模板面向 GPT-5.5。它要求模型先理解受众与使用场景，沿用已有设计体系，再选择布局、控件、文字和视觉材料。业务工具重视信息组织和重复操作，游戏等内容可以更有表现力。

模板还要求补全控件状态、检查响应式布局和资源加载，并在真实页面中验证操作。可以借鉴这些要求，但具体视觉风格和控件规则仍需按项目设计约定调整。

<a id="doc-158"></a>
### Prompting guidance for GPT-5.6 Sol｜GPT-5.6 提示指南
[原文](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6)

GPT-5.6 的提示应交代目标、重要约束、可用证据和完成条件，再给模型选择执行方式的空间。可以从已有可用提示出发，一次删去一类重复指令、无用示例或工具，再用同一组任务比较结果。

权限、工具路由、来源要求和长期任务状态应具体说明。推理强度、输出长度和 PTC 按工作负载调整；提示更短或工具更多本身都不是效果改善的证据。

## Reasoning｜推理

<a id="doc-168"></a>
### Reasoning models｜推理模型
[原文](https://developers.openai.com/api/docs/guides/reasoning)

推理模型在给出回答前使用内部推理 token，帮助规划、多步求解和工具使用。`reasoning.effort` 调整推理投入，支持的模型还提供 standard／pro mode。预算和费用需要同时考虑可见输出与内部推理 token。

跨轮续接时，`reasoning.context` 决定使用当前轮或兼容的历史推理。状态可以通过保存的响应或加密条目传递，原始内部推理文本不会因此公开。重放 assistant 消息时，也要保留 `phase`，区分中间进度与最终回答。

<a id="doc-113"></a>
### Keep the prefix unchanged｜保持前缀不变
[原文](https://developers.openai.com/api/docs/guides/preserved-reasoning)

多轮任务中，尽量保留已有上下文前缀，把新要求和结果追加到后面。缓存从请求开头匹配，修改前面的内容会影响之后的复用；采用相应机制的新模型还会剔除前缀变化之后的推理条目，可能需要重新推理。

例如修改旧指令、缩短工具结果或替换历史摘要，都可能改变前缀。原文针对指令、effort、schema、工具和压缩给出了追加式处理方法，也说明怎样用缓存诊断检查变化。

<a id="doc-167"></a>
### Reasoning best practices｜推理最佳实践（旧代比较）
[原文](https://developers.openai.com/api/docs/guides/reasoning-best-practices)

这份早期指南对比 o-series 推理模型与当时的非推理 GPT 模型：前者适合复杂规划、模糊问题和跨材料判断，后者适合较直接、重视速度与成本的执行任务。

提示应明确目标、约束和材料边界。文中的客户案例与型号反映当时的产品情况，当前推理参数和模型支持请结合 Reasoning models 及各代指南。

## Images｜图像

<a id="doc-108"></a>
### Images and vision｜图像理解
[原文](https://developers.openai.com/api/docs/guides/images-vision)

视觉模型可以分析输入图像并返回文字。Responses 和 Chat Completions 支持相应的图像理解；Images API 及 Responses 的图像工具用于生成或编辑图片。

图像可按接口要求通过 URL、base64 或文件 ID 提供。`detail`、尺寸及 patch／tile 规则决定处理方式和输入成本，具体限制因模型而异。小字、旋转图像、精确空间定位和医疗图像等任务存在限制，需要根据实际用途核对结果。

<a id="doc-106"></a>
### Image input token and cost calculator｜图像输入费用计算器
[原文](https://developers.openai.com/api/docs/guides/image-cost-calculator)

图像输入计算器根据模型、原图尺寸和 detail，估算一张图片需要的输入 token 与费用，并显示缩放和分块过程。超过模型的图像限制时，会提示无法处理。

估算只包括这张图的标准输入费用；其他提示、输出、缓存、长上下文和地域附加项需另算。图像生成和编辑使用专门的生成费用计算器。

<a id="doc-104"></a>
### Image generation｜图像生成与编辑
[原文](https://developers.openai.com/api/docs/guides/image-generation)

图像生成可以直接调用 Images API 的生成或编辑端点，也可以在 Responses 对话中使用图像工具。后者便于结合文字、参考图和前后文，连续修改同一张图片。

提示可指定主体和构图，编辑时可用参考图、mask 或图中标记。输出可配置尺寸、质量、格式和透明背景，部分模型还支持 SVG、GIF 与逐步返回图像。不同模式有各自限制和费用；页面同时保留较早模型的历史配置。

<a id="doc-107"></a>
### Image prompting｜图像提示指南
[原文](https://developers.openai.com/api/docs/guides/image-prompting)

描述图像时，先交代主体、构图、风格和限制。编辑已有图片时，明确要改什么、哪些部分保持不变，每轮集中调整一个问题，再检查结果。

原文按模型版本提供对照示例，涵盖文字呈现、参考图、产品透明图、风格迁移、人物一致性及多轮编辑。新版还区分质量和复杂度参数，并展示 SVG、GIF 和 markup 编辑。视觉差异需要结合原文图片一起看。

## Specialized models｜专门模型

<a id="doc-219"></a>
### Vector embeddings｜向量嵌入
[原文](https://developers.openai.com/api/docs/guides/embeddings)

Embedding 将文本表示为一组浮点数。内容越相关，向量在所选距离度量下通常越接近，因此可以用于搜索、聚类、推荐、分类和异常检测。

向 embeddings 端点发送文字及模型名称，取得向量后，由应用保存并计算相似度。可以按模型支持调整维度，在存储、检索速度和效果之间取舍。原文提供文本与代码搜索、问答和可视化示例，并解释输入计数和向量数据库的使用。

<a id="doc-133"></a>
### Moderation｜内容审核
[原文](https://developers.openai.com/api/docs/guides/moderation)

Moderation 可以单独审核文本或图片，也可以在生成请求中返回审核信号。结果包含总体标记、类别、分数和适用输入类型，供应用过滤、送审或执行自己的内容策略。

不同工作流的错误处理和流式结果时机需要分别处理。原文明确要求不要将已知或疑似儿童性虐待材料发送到 Moderation API，它不用于识别或处置这类材料；相关流程见专门的儿童安全指南。

## Model-specific guides｜各代模型指南

这些页面用于理解特定代际的参数、提示与迁移。其旧示例和发布时间语境应保留，当前可用性回模型目录与 Deprecations 核对。

| 原文 | 中文导读 |
|---|---|
| <a id="doc-216"></a>[Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model/gpt-6-astra) | GPT-6 系列按 Astra、Sol、Terra、Luna 提供不同取舍。当前家族指南说明异步工具调用、steering、会话中配置更新和安全监测；迁移时核对推理、工具端点、采样参数、缓存及地域支持。 |
| <a id="doc-215"></a>[Using GPT-5.6](https://developers.openai.com/api/docs/guides/latest-model/gpt-5.6) | GPT-5.6 用 Sol、Terra、Luna 区分能力与成本定位，并加入 PTC、多 Agent beta、显式缓存和跨轮推理等功能。Pro 与 `max` effort 适合进一步测试；迁移还需检查默认推理和图像 detail 的变化。 |
| <a id="doc-214"></a>[Using GPT-5.5](https://developers.openai.com/api/docs/guides/latest-model/gpt-5.5) | GPT-5.5 建议从保留产品要求的简短提示开始，用实际任务调整推理、回答长度和工具说明。默认推理、图像预处理及长任务 `phase` 都会影响迁移结果，不能只沿用旧模型的完整提示堆叠。 |
| <a id="doc-213"></a>[Using GPT-5.4](https://developers.openai.com/api/docs/guides/latest-model/gpt-5.4) | GPT-5.4 把代码能力纳入通用模型，并提供大上下文、计算机操作、tool search、压缩与 custom tools。接入时需同时检查变体、参数兼容和 `phase`；大小模型的提示与成本取舍分别处理。 |
| <a id="doc-212"></a>[Using GPT-5.3-Codex](https://developers.openai.com/api/docs/guides/latest-model/gpt-5.3-codex) | 直接通过 API 构建 GPT-5.3-Codex 编程 Harness 时，可参考这里的指令、AGENTS.md、补丁、Shell、计划、图像和压缩配置。长任务需要保留 assistant 的 `phase`，各项建议按该版本使用。 |
| <a id="doc-211"></a>[Using GPT-5.2](https://developers.openai.com/api/docs/guides/latest-model/gpt-5.2) | GPT-5.2 的指南涵盖 `xhigh`、上下文压缩、回答详略、custom tools、grammar 和允许工具集合。迁移时先保留既有推理水平，再测试调整，并检查前置状态消息和结构化提取的处理。 |
| <a id="doc-210"></a>[Using GPT-5.1](https://developers.openai.com/api/docs/guides/latest-model/gpt-5.1) | GPT-5.1 增加 `none` 推理模式，适合重视延迟且不需要额外推理的任务。提示可以调整语气、输出和任务完成要求；代码部分说明 apply_patch 与 Shell 的使用，并通过失败轨迹改进提示。 |
| <a id="doc-209"></a>[Using GPT-5](https://developers.openai.com/api/docs/guides/latest-model/gpt-5) | 初代 GPT-5 提供推理强度、回答详略、工具前置说明和主动性控制，也支持自由文本 custom tools。原文结合代码与前端任务，展示如何调整提示，并记录 Cursor 的早期应用经验。 |
| <a id="doc-208"></a>[Using GPT-4.1](https://developers.openai.com/api/docs/guides/latest-model/gpt-4.1) | GPT-4.1 倾向于按字面遵循明确指令。提示可以具体说明任务、工具 schema 和长上下文中材料的组织方式，需要时再加入规划要求。原文另提供 diff 与 apply_patch 示例，适用于这一代非推理模型。 |

## Migration guides｜迁移操作指南

| 原文 | 中文导读 |
|---|---|
| <a id="doc-204"></a>[Upgrading to GPT-5.4](https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p4) | 迁往 GPT-5.4 时，先查明模型调用及相关提示，判断只改型号是否足够。长任务还需检查 `phase` 和输出格式；如果需要接口或实现变更，应先明确这些额外工作。 |
| <a id="doc-205"></a>[Upgrading to GPT-5.5](https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p5) | 迁往 GPT-5.5 时，保留有意固定的历史示例、测试基线和低成本路线，只调整目标调用及相关提示。验证结构化输出、工具语义、`phase`、推理档位和延迟，再按回归结果修改。 |
| <a id="doc-206"></a>[Upgrading to GPT-5.6 Sol](https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p6-sol) | 迁往 GPT-5.6 时，按每处调用的质量、成本和延迟选择家族成员。检查默认 effort、Chat Completions 工具兼容、缓存、图像与 PDF detail 及模型路由；先保住原有行为，再按需要采用新功能。 |

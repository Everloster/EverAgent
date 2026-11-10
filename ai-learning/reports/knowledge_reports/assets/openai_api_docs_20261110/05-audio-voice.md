# Audio & voice｜音频与语音

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md)

语音应用可以直接对话，也可以把转写、文本处理和语音生成分开。本卷按这些用法整理会话、连接、工具、提示与计费规则。

## Overview｜总览

<a id="doc-32"></a>
### Audio and voice｜音频路线
[原文](https://developers.openai.com/api/docs/guides/audio)

新建连续语音对话应用时，官方建议从 GPT-Live 开始：它可以边听边说，让后端同时处理推理和工具任务。需要 Realtime 的会话与工具模型时，也可以直接使用 Realtime API。

已有录音用文件转写；正在到达的音频用实时转写；同声传译用专门的翻译会话；朗读文字用语音生成接口。这些路线可能都使用 WebRTC 或 WebSocket，但握手、凭据和事件格式需按各自接口配置。

<a id="doc-223"></a>
### Voice agents｜语音 Agent
[原文](https://developers.openai.com/api/docs/guides/voice-agents)

语音 Agent 常见的组织方式有三种。GPT-Live 负责持续交谈，把任务交给独立后端；Realtime 在一个会话中处理声音、推理和工具；串联式流程则依次完成语音转文字、文本 Agent 和文字转语音，方便检查或替换每个环节。

评估时既要检查任务是否完成，也要看用户实际听到的回答、语言质量、延迟和连接稳定性。可以先用录音测试，再逐步加入多轮对话、打断和工具等待场景。

## GPT-Live

<a id="doc-99"></a>
### Getting started with GPT-Live｜快速开始
[原文](https://developers.openai.com/api/docs/guides/live)

GPT-Live 把语音交谈与后台工作分开。语音模型倾听、说话，并决定何时请求后端帮助；后端负责查询、推理、调用工具和完成任务。用户可以在后端工作时继续说话。

Responses delegation 由 Live 管理对指定 Responses 模型的请求和上下文；client delegation 由应用运行自己的模型、Agent 或服务。应用负责权限、确认和任务记录，也决定用户打断后是否取消后台工作。浏览器的首次连接可以从 WebRTC 示例开始。

<a id="doc-157"></a>
### Prompting GPT-Live｜语音提示
[原文](https://developers.openai.com/api/docs/guides/live-prompting)

GPT-Live 的提示应说明角色、说话方式、如何回应打断，以及何时将任务交给后端。具体业务步骤和工具规则放在后端指令中。可以分别调整口音、语速、耐心程度和工具等待期间的交流方式。

Backchannel 指用户说话时简短的倾听反馈，例如“嗯”。原文提供相应模板和试听，建议按代表性对话检验效果。语音模型停止说话后，应用仍需独立处理正在运行的后台任务。

<a id="doc-119"></a>
### Managing GPT-Live sessions｜会话管理
[原文](https://developers.openai.com/api/docs/guides/live-conversations)

创建 Live session 时选择模型、声音和 delegation mode，并提供指令及必要的文字历史。模型、声音和委派模式在本次会话中固定；允许更新的配置与新增上下文通过对应事件提交。

应用应分别记录转写文本、已播放音频和后台任务进度。上下文追加成功只表示被接受，声音是否播完仍要看播放状态。会话可以按配置保存、分叉或在结束后重新建立；不再交谈时应关闭连接，并收集最终用量。

<a id="doc-77"></a>
### Delegation and tools｜委派与工具
[原文](https://developers.openai.com/api/docs/guides/live-delegation)

Live 可以把工作委派给 Responses，也可以通知应用自行处理。Responses delegation 会准备对话上下文并调用指定后端，后续事件包装在 `response.event` 中；应用按内部事件类型处理，同时保留 delegation ID。

Client delegation 只发送委派信息，应用需要组合转写和任务状态，再调用自己的工作流。工具函数、权限和业务记录仍由应用负责。回传思考进度、可说给用户的说明或新增指令时，要使用对应的更新类型，并处理用户纠正及迟到、过期的结果。

<a id="doc-125"></a>
### Migrate to GPT-Live｜迁移到 GPT-Live
[原文](https://developers.openai.com/api/docs/guides/live-migration)

从 Realtime 或串联式语音应用迁移到 Live 时，可以保留现有工具、权限检查和任务记录，将倾听、说话和对话衔接交给 Live，把任务步骤留在后端。

迁移需要同时调整连接、音频事件、工具结果和转写处理。依赖原始声音的判断不能只改用文字转写；要求播放前检查的内容也需要保留相应缓冲和审批。验证时应使用原应用的代表性对话，检查打断、纠正、工具动作及最终业务状态。

<a id="doc-101"></a>
### GPT-Live partner integrations｜合作伙伴集成
[原文](https://developers.openai.com/api/docs/guides/live-partner-integrations)

已有语音框架可以通过合作伙伴集成接入 GPT-Live。LiveKit 提供语音 Agent 插件；Twilio、Telnyx 和 Bandwidth 提供电话连接；Daily/Pipecat 提供相应的语音服务接入。

安装、凭据和包版本由伙伴文档维护，OpenAI 文档说明通用的 session 与 delegation 行为。选择支持 GPT-Live 的版本，并检查音频格式、打断、后端任务和挂断流程；现有 Realtime 集成不能直接假定兼容。

## Realtime API

<a id="doc-100"></a>
### Getting started with the Realtime API｜Realtime 入门
[原文](https://developers.openai.com/api/docs/guides/realtime)

Realtime API 直接处理语音输入和语音输出，同时保存对话状态并调用工具。浏览器应用可以先让后端创建临时客户端凭据，再由前端建立 `RealtimeSession`，通过 WebRTC 连接。业务能力写在 `RealtimeAgent` 的工具、交接和校验配置中。

服务端可以使用 WebSocket。已有 beta 集成迁往正式接口时，要一起更新 client secrets、calls 入口、session 类型、音频配置和事件名称，不能只更换地址。

<a id="doc-159"></a>
### Prompting Realtime models｜Realtime 提示指南
[原文](https://developers.openai.com/api/docs/guides/voice-prompting)

Realtime 提示应说明 Agent 的职责、决策条件、工具用法和需要遵守的限制。先用简短提示测试，发现具体行为问题后再补充规则。

原文分别保留 Realtime 2 与 1.5 的建议，涵盖推理强度、说话前的简短说明、回复长度、工具确认、错误恢复、背景声和人工接管。对姓名、编号和邮箱等需要准确输入的内容，应设计逐项确认流程。GPT-Live 的后端委派另用其专门提示指南。

<a id="doc-163"></a>
### Realtime conversations｜实时会话
[原文](https://developers.openai.com/api/docs/guides/realtime-conversations)

Realtime Session 保存模型、声音和其他会话配置；Conversation 保存用户输入与模型输出的条目；Response 表示一次生成。应用发送客户端事件发起操作，并接收服务端事件处理文字、音频、图片和工具调用。

WebRTC 使用媒体轨道传输声音，WebSocket 使用音频缓冲事件。可以由 VAD 划分轮次，也可以手动提交。用户打断后，应同步截断尚未播放的音频和相应会话内容；模型生成完成与用户听完是两个不同的时间点。

<a id="doc-222"></a>
### Voice activity detection｜语音活动检测
[原文](https://developers.openai.com/api/docs/guides/realtime-vad)

VAD 自动判断用户何时开始和停止说话。`server_vad` 主要根据声音与静音分段，可调阈值、前置缓冲和静音长度；`semantic_vad` 根据话语是否完整决定何时结束一轮，可调 eagerness。

在支持的会话中，还能分别控制是否自动创建回复、是否打断当前输出。转写模型的支持不同，不能把同一套 VAD 配置用于所有 transcription session；有些模型要求关闭轮次检测并由应用提交音频。

<a id="doc-166"></a>
### Realtime with tools｜实时工具与 MCP
[原文](https://developers.openai.com/api/docs/guides/realtime-mcp)

Realtime 中的函数工具由应用执行并返回 `function_call_output`；MCP 工具则由 API 连接远程服务器。工具可以设置在 session 层供整个会话使用，也可以只提供给一次 response。

MCP 接入还需要处理工具列表、审批和失败事件，可以重用先前定义的 server label。`response.done` 到达时，某些 MCP 调用可能仍在执行；后续依赖这些结果的生成要等待相应调用完成。

## Build with voice｜语音能力与成本

<a id="doc-63"></a>
### Connect voice to Decisions｜连接结构化决策
[原文](https://developers.openai.com/api/docs/guides/decisions-voice)

Live 可以直接调用 Decisions，在用户仍说话时完成低延迟判断。也可以通过 `session.triggers`，在输入或输出转写更新时触发预设问题。

Decisions 从应用给出的选项中选择，应用执行动作、检查实际状态，再将结果交给 Live。问题可以在运行中更新，但要等待对应的 `session.updated`，再使用新配置。返回结果应关联原始事件，避免把迟到的判断应用到已经变化的场景。

<a id="doc-70"></a>
### Custom voices｜自定义声音
[原文](https://developers.openai.com/api/docs/guides/custom-voices)

自定义声音可以从文字描述生成，也可以根据授权同意录音和参考样本创建。文字生成的声音用于 GPT-Live；录音创建的声音可在获得相应资格的语音产品中使用，两条路线的支持范围和限制不同。

创建后用 voice ID 引用声音。录音路线要求同意语句和样本匹配，并遵守录音格式、数量和生命周期规则。应用应明确说明声音由 AI 生成，避免冒充他人。

<a id="doc-67"></a>
### Cost optimization｜语音成本优化
[原文](https://developers.openai.com/api/docs/guides/voice-latency-cost)

GPT-Live 的语音部分按活动会话时长计费，后端模型和工具另计。用户说话、助手说话、双方沉默和等待后端都算活动时间。静音不会关闭会话，结束后应关闭连接并读取最终用量。

时长更新是累计值，不能逐条相加。WebRTC 初始化收取的时长也已经抵扣到运行会话中，不应重复加算。Realtime 则按相应 token 和转写用量计费。优化时应同时看上下文长度、工具等待、闲置连接与每项任务的总成本。

## Connections｜连接

<a id="doc-227"></a>
### WebRTC｜媒体轨道与事件通道
[原文](https://developers.openai.com/api/docs/guides/voice-webrtc)

WebRTC 用媒体轨道传输麦克风声音和生成的音频，用数据通道传输 JSON 事件。浏览器生成 SDP offer，可信后端使用 API key 向服务端换取 answer，再交给浏览器完成连接。

GPT-Live 的 HTTP 创建流程已经启动 session，客户端等待 `session.started` 后发送命令，无须再发送 `session.start`。Realtime 另有统一接口和临时密钥两条连接方式，使用对应的会话配置和事件。

<a id="doc-228"></a>
### WebRTC with WARP｜加速握手
[原文](https://developers.openai.com/api/docs/guides/realtime-webrtc-warp)

WARP 通过 DTLS 1.3、SPED、SNAP 和预协商数据通道，减少建立语音连接所需的网络往返。客户端可以只启用已经支持的部分优化；完整 WARP 需要这些能力共同配合。

原生客户端与浏览器的支持和启用方式不同，其中若干规范仍处于草案或实验阶段。GPT-Live 在创建 session 的请求体中使用 `transport.dcid`，Realtime 使用自己的参数方式。未支持 WARP 的客户端仍可按标准 WebRTC 连接。

<a id="doc-230"></a>
### WebSockets｜服务端音频连接
[原文](https://developers.openai.com/api/docs/guides/voice-websockets)

GPT-Live 的主 WebSocket 同时传输音频和控制事件。连接后先发送 `session.start`，配置模型、声音、音频格式和委派方式；收到 `session.started` 后再发送音频及其他命令。

音频字节必须与所声明的格式一致，修改格式字段不会自动完成重采样。应用负责采集、编解码、播放和缓冲，并在结束时正确关闭。Realtime 的 WebSocket 使用另一套 URL、session 和音频缓冲事件。

<a id="doc-193"></a>
### Telephony and SIP｜电话与 SIP
[原文](https://developers.openai.com/api/docs/guides/voice-sip)

电话应用通过 SIP 服务商把呼叫接到 OpenAI，信令使用 TLS，GPT-Live 音频使用 SRTP。GPT-Live 支持入站和出站流程：应用配置号码及 trunk，接收并验证来电 webhook，决定接受或拒绝，再通过 sideband 管理会话和后台任务。

应用应确认实际接通状态，避免重复处理同一事件；接通后可处理按键事件、转接和挂断。Realtime 的入站流程使用自己的事件与接口。区域地址、网络范围、回拨和费用条件应按所用 API 及电话服务商的配置核对。

<a id="doc-184"></a>
### Server-side controls｜服务端控制
[原文](https://developers.openai.com/api/docs/guides/voice-server-controls)

Sideband WebSocket 让可信后端连接到已有的 WebRTC 或 SIP 会话，接收事件、运行私有工具并更新会话。原来的连接继续承载主音频，两条连接共享同一个 session。

工具执行、权限检查和业务规则由应用实现，应为每种动作确定一个处理方，避免重复执行。需要播放前审核时，还要在音频播放路径上设置缓冲和检查；增加 sideband 本身不会阻止声音到达用户。

## Audio processing｜音频处理

<a id="doc-201"></a>
### Transcription｜转写路线
[原文](https://developers.openai.com/api/docs/guides/transcription)

转写把声音变成文字。已完成的录音使用文件转写，当前推荐起点是 `gpt-transcribe`；麦克风、通话或持续媒体流使用实时转写，推荐起点是 `gpt-live-transcribe`。

已上传文件也可以流式返回文字，这与持续接收新音频是不同需求。语言识别、说话人标签、时间戳和字幕格式的支持取决于模型；从旧模型迁移前，应核对应用实际依赖的输出字段。

<a id="doc-90"></a>
### File transcription｜文件转写
[原文](https://developers.openai.com/api/docs/guides/speech-to-text)

文件转写将录音上传到 `/v1/audio/transcriptions`，取得完整文本或流式文字结果。可以通过 prompt、keywords 和 languages 提供领域词语、专有名称及语言背景，提高识别的针对性。长录音需要按文件限制分段处理。

当前指南推荐 `gpt-transcribe`。页面中的说话人标签、词级时间戳、字幕和英文翻译示例部分使用旧模型，保留到相应停用日期。迁移时应逐项检查所需格式和字段，而不是只替换模型名称。

<a id="doc-164"></a>
### Realtime transcription｜实时转写
[原文](https://developers.openai.com/api/docs/guides/realtime-transcription)

实时转写持续接收麦克风或通话音频，在声音到达时返回文字片段，提交一轮音频后再返回该轮最终文本。应用需要建立 transcription session，追加音频，并在轮次边界提交。

结果按 item ID 配对，不同轮次的完成事件可能乱序。上下文提示和 delay 设置会影响准确率与延迟；时间戳、说话人标签和置信度等字段要按模型支持核对。`gpt-live-transcribe` 不使用 `server_vad` 或 `semantic_vad`，轮次由应用提交。

<a id="doc-165"></a>
### Realtime translation｜实时翻译
[原文](https://developers.openai.com/api/docs/guides/realtime-translation)

实时翻译使用专门的 translation session，持续接收原语音，在说话过程中返回译文音频和文字片段。它从音频流直接开始翻译，不需要普通对话中的 `response.create`。

WebRTC 和 WebSocket 各有连接方式。关闭输入后仍需接收剩余译文。多方或双向翻译时，应分别组织语言方向和音轨，避免把译文重新送回原输入。

<a id="doc-196"></a>
### Text to speech｜文本转语音
[原文](https://developers.openai.com/api/docs/guides/text-to-speech)

Speech API 接收 `model`、`input` 和 `voice`，把文本转换为指定格式的语音，也支持流式返回。应用需要向听众说明声音由 AI 生成。

此页保留的 `tts-1`、`tts-1-hd` 和 `gpt-4o-mini-tts` 已弃用，计划于 2027 年 1 月 6 日停止。迁往 `gpt-realtime-2.1-mini` 时，应改用 Realtime API 流程；该模型不能直接填入旧 `/v1/audio/speech` 请求。

<a id="doc-33"></a>
### Audio in Chat Completions｜聊天接口中的音频
[原文](https://developers.openai.com/api/docs/guides/audio-chat-completions)

已有 Chat Completions 应用可以选择支持音频的模型，并在 `modalities` 及对应内容字段中启用音频输入或输出。每次请求处理给定的多模态内容，适合给现有聊天功能增加声音。

需要持续倾听、会话打断和实时工具交互时，应使用 GPT-Live 或 Realtime 的会话接口。

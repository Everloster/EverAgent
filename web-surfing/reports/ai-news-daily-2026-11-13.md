---
title: "AI 行业日报 · 2026-11-13"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-13"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.virxact.com/daily"
---

# AI 日报 · 2026年11月13日

今天先看三件事。

- 英伟达董事会宣布，黄仁勋即日辞去总裁、首席执行官和董事职务；首席财务官 Colette Kress 兼任临时首席执行官，董事会另设首位董事长，并开始物色正式继任者。第三财季财报仍按原计划于美国时间 11 月 17 日发布。

- 谷歌发布 Gemini 4 Hydrogen，定位为面向日常编码和智能体流程的快速模型，同日向开发者接口、Gemini 应用和谷歌搜索推出，并在 Antigravity 里加入可在不同模型间自动切换的 Orchestrator；接口价格为每百万输入词元 1.5 美元。

- Thinking Machines Lab 按一周前的承诺，以允许商用的 Apache 2.0 许可在 Hugging Face 公开 Inkling 2 Small 权重。这是总参数 5940 亿、激活 170 亿的混合专家模型，可接收图像输入；此前一周只能经其 Tinker 平台在线使用，不能下载。

## 英伟达宣布 CEO 交接：黄仁勋辞任，Kress 暂代

英伟达美国时间 11 月 12 日发布[公告](https://nvidianews.nvidia.com/news/nvidia-announces-ceo-transition)：黄仁勋辞去总裁、首席执行官和董事会成员职务，即刻生效。首席财务官 Colette Kress 出任临时首席执行官，同时继续担任财务官，直到选定正式继任者；董事会将考虑内部和外部人选。

董事会同时任命 Synopsys 前首席执行官 Harvey C. Jones 为公司历史上首位董事长。公告称公司运营、客户承诺和产品路线图预计不受影响，财报日期不变。公告没有说明辞任原因。本刊 11 月 9 日报过董事会就“外国情报行动”报道启动独立调查，公告未提及调查结论。

TechCrunch 同日[报道](https://techcrunch.com/2026/11/12/democrats-launch-nvidia-investigation-write-scathing-letter-on-huangs-scheme-with-trump/)称黄仁勋是被迫离开，并称他已同意到共和党主导的众议院委员会闭门作证；这些属于媒体说法，公司公告用的是“辞任”。该消息在 Hacker News 约 2,895 分，是采集时的首页第一。

## 谷歌发布 Gemini 4 Hydrogen：主打快速执行

谷歌美国时间 11 月 12 日在[官方博客](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen/)发布 Gemini 4 Hydrogen。它与 Carbon、Argon 同属 Gemini 4，定位是写代码、跑测试、验证改动这类快速执行工作，可单独用，也可给大模型当执行引擎。价格在 100 万词元上下文内统一为输入每百万 1.5 美元、输出 7.5 美元。

谷歌称它在 Artificial Analysis 智能指数上默认档得 51，略高于 Argon 的 50，最高档为 54；相比 Gemini 3.8 Flash，Terminal-Bench 4.1 从 18.2% 升至 57%，任务完成快约 2.5 倍，捏造性陈述减少五倍以上。这些都是谷歌自报，本期未读模型卡全文。

同日 Antigravity 加入 Orchestrator，可在同一会话里在 Carbon 和 Hydrogen 之间自动切换；谷歌称在 Terminal-Bench 4.0 上接近 Carbon 的成功率，平均少用 24% 额度、快 19%。免费版 Gemini 应用会在合适时自动选用 Hydrogen，谷歌搜索也改由它驱动。这些对比同样是谷歌自报。博客帖在 Hacker News 约 453 分。

## Inkling 2 Small 权重以 Apache 2.0 开放

Thinking Machines Lab 11 月 12 日在 [Inkling 2 Small 发布页](https://thinkingmachines.ai/news/inkling-2-small/)加注更新：权重已可在 [Hugging Face](https://huggingface.co/thinkingmachines/Inkling-2-Small) 下载，许可为 Apache 2.0，另有 MXFP8 版本，开发者可自行部署、微调并商用。11 月 5 日发布时只能经其 Tinker 平台使用，公司当时说要等外部安全测试和红队完成后再开放。

模型参数没有变化：总参数 5940 亿、激活 170 亿，上下文 100 万词元，支持图像输入和可调推理强度。公司列出 SGLang、vLLM、Unsloth 等推理与微调支持，以及英伟达、Together、Cloudflare 等多家接口服务商。Artificial Analysis 智能指数 31 分，出自公司页面引用。

需要注意，[模型卡](https://thinkingmachines.ai/model-card/inkling-2-small/)写明 NVFP4 主版本需要至少 500GB 合计显存（例如两张 B300 或四张 H200），MXFP8 版需要至少 800GB，个人电脑跑不动。公司也承认，它在内部对齐评测上仍落后于闭源的 GPT-6.1 Sol。本刊 11 月 6 日报过该模型发布与“权重待测试”，此次是兑现开放。

## Claude 可作为参会者进入视频会议

Anthropic 11 月 12 日[推出](https://claude.com/blog/claude-meetings) Claude Meetings 测试版，先面向 Team 和 Enterprise 套餐，目前只支持 Google Meet。Claude 以可见参会者身份入会，可在会中回答口头或聊天提问，经许可调用已连接的工具，和与会者一起写文档、画白板，会后留下笔记和待办。

公司写明的边界是：默认在有外部人员受邀时不入会，外部人员中途加入则自动离开，管理员可改；只保存文字记录、摘要和屏幕描述，不存音频；口头提问时会逐次确认说话人。零数据保留、HIPAA 配置和自管密钥的组织暂不可用。官方提醒入会前应确认所有人同意被转录。

## World Labs 世界模型 Atlas 向所有人开放

李飞飞创办的 World Labs 于 11 月 12 日把 [Atlas](https://worldlabs.ai/atlas) 开放给所有用户，同时提供网页应用与开发者接口。Atlas 是该公司 9 月发布的“全模态”世界模型，接受文字、图像、视频和三维输入，可从照片重建可漫游的场景，或从文字生成场景。

随同开放的有四个工具：从照片重建场景并设定镜头路径的 Viewfinder，用灰盒搭场景的 Chisel，把高斯泼溅点云转成网格的 Splats to Mesh，以及重新打光的 Relight；接口可接入 Blender。模型闭源、只能托管调用，开放页未列价格和网格质量数据。AMD 9 月宣布收购 World Labs，交易尚未完成。

## 热榜上，网页指南和安全工具升温

[GitHub 热榜](https://github.com/trending)在北京时间 11 月 13 日约 09:12 采集，当时页面列出 13 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。设计系统 meta/astryx 仍居当天增量首位，但较昨日放缓；技能包与安全类仓库继续在前列。

[meta/astryx](https://github.com/meta/astryx) 当天约增加 1,830，总星约 26,551。[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 约增加 816；Chrome 团队的 [modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) 约增加 739，比昨日明显加快；[openai/codex-security](https://github.com/openai/codex-security) 约增加 643。新面孔里，[CopilotKit/OpenBot](https://github.com/CopilotKit/OpenBot) 给每个智能体同事配一台独立电脑，约增加 298；[Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code) 自称可免费使用多种编码工具，约增加 415，其合规性未经核实。记账应用 sure、nvm、Node.js 等与人工智能无直接关系。全表在文末。

## 三个人怎么说

**Will DePue**，前 OpenAI 研究员，参与过 Sora 与 o3、4o 后训练。他[发帖](https://x.com/willdepue/status/2120992457630326841)介绍自己的[报告](https://unemploymentlabs.com/checkpoint-forensics)：从公开权重中的初始化痕迹推断，DeepSeek、月之暗面、MiniMax 和蚂蚁集团的六个新模型是在英伟达 Blackwell 芯片上初始化的。帖发于北京时间 11 月 13 日 05:29，属个人研究结论；报告自己也写明不能证明芯片所在地或是否违反出口管制。

**Simon Willison**，独立开发者，Datasette 作者、Django 共同作者。他[写道](https://x.com/simonw/status/2121039423441981444)，Gemini 4 的定价很让人困惑：Argon 与 Carbon 单价相同，Hydrogen 只便宜 25%，而前两者 12 月 1 日起价格将翻倍；他还说 Hydrogen 画的鹈鹕明显更差。帖发于北京时间 11 月 13 日 08:36，属个人测评，价格表见其[博客](https://simonwillison.net/2026/Nov/12/llm-gemini/)。

**Ethan Mollick**，宾夕法尼亚大学沃顿商学院教授，研究人工智能。他[宣布](https://x.com/emollick/status/2121001056637431873)所在实验室开源 [Primer](https://gail.wharton.upenn.edu/primer/)：教师用对话讲清一节课，系统中的多个智能体生成可玩的教学模拟。帖发于北京时间 11 月 13 日 06:03，属其团队发布；项目页写明它是实验原型，尚未在课堂条件下评估。

## 另外几则

**Anthropic 上市页公布第三季度数字。** Anthropic 的 [IPO 页面](https://ipo.anthropic.com/us/)列出第三季度营收 170 亿美元、调整后经营利润率 15%、经营利润率负 3%，净亏损 233 亿美元，其中 219 亿美元为可转债等公允价值变动的非现金费用。页面写明预计美国东部时间 11 月 18 日定价、19 日在纳斯达克以 ANT 挂牌，但须视监管批准而定。本刊 11 月 11 日报过路演启动。

**Opus 5.5 成为 Claude 默认模型。** Anthropic 11 月 12 日[发文](https://claude.com/blog/using-claude-opus-5-5-as-your-daily-driver-for-knowledge-work)称，Claude Opus 5.5 已成为 Pro、Max、Ultra 和 Team 套餐的默认模型，并建议把它作为研究、分析与写作的日常主力。接口价格为输入每百万词元 4 美元、输出 20 美元，默认中等思考强度。文中的对比测试是公司内部测试。

**民主党议员就英伟达对华芯片销售发起问询。** 据 TechCrunch，众议员 Richard Neal 与参议员 Ron Wyden 致信商务部长 Howard Lutnick，要求保存相关记录，并质疑政府处理英伟达对华销售与新加坡客户 Megaspeed 的方式。作为少数党，他们可提问但不能强制作答。信中关于“违法”的说法是议员指控。

**Replit Agent 可代企业采购和投放广告。** Replit 11 月 12 日[宣布](https://replit.com/blog/replit-agent-ads-commerce)，Replit Agent 可借 Stripe 的 Link 与 Visa 代企业下单采购，下单前须由用户确认最终金额；也可在 Replit 内创建并投放谷歌广告。采购功能先向美国 Core 和 Pro 用户开放，仅限一次性购买。文中创业者营收案例为公司提供。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

英伟达：公告日期为 2026 年 11 月 12 日，标题 “NVIDIA Announces CEO Transition”。Kress 自 2013 年 9 月起任首席财务官，此前在思科和微软任职近 25 年；Jones 被描述为有 30 多年创业与投资经历。第三财季（2027 财年）财报定于太平洋时间 11 月 17 日约 13:20 发布、14:00 电话会。TechCrunch 报道发布于太平洋时间 11 月 12 日 14:42（北京时间 11 月 13 日 06:42），文中关于被迫离任、婚外情与间谍指控、作证安排的说法均为媒体报道或议员指控，本期未读 AP 原文（WebFetch 超时）。Hacker News 上 AP 报道帖约 2,895 分、2,737 条评论。

Gemini 4 Hydrogen：四档思考强度为 low、medium、high（默认）和新增的 xhigh。谷歌还自报 HLE-Diamond 58.8%、Vals Tax Agent Bench 52.3%（第一）、MKA 53.4%、Agents' Last Exam v1.1 71.6%，Agent Arena 第 5；安全方面称智能体越权最多减少 81%、内部诚实评测 96.7%、Gray Swan 间接提示注入基准抗性提升 2.3 倍以上。合作方测试称比 3.8 Flash 快 2 至 2.8 倍、词元少 12% 至 23%。以上均为谷歌或其合作方自报。Antigravity 帖在 Hacker News 约 289 分。

Inkling 2 Small：Hugging Face 接口显示 thinkingmachines/Inkling-2-Small 许可字段为 apache-2.0，最后修改于 2026-11-12T21:35Z（北京时间 11 月 13 日 05:35），采集时约 93 个赞。发布页更新列出的训练后工具为 Miles、SkyRL 与 Snowflake Cortex Training，接口服务商为 NVIDIA、Fireworks、Together、Baseten、Nebius、Modal 和 Cloudflare。模型卡称该模型以 NVFP4 原生精度预训练、中训练和后训练。基准表中多数分数注明取自第三方评测方，但汇总与比较对象由公司选择。

Claude Meetings：博客发布日期 2026 年 11 月 12 日。测试期内，笔记、转录和会中回答对 Team 与 Enterprise 免费，但调用已连接工具的回答计入套餐用量；会中生成的文档和白板免费至 2027 年 2 月 10 日。合作方 Gong、Attention、Granola、Fireflies.ai、Otter 的转录对接写的是“即将”。

Atlas：World Labs 博客列表把 “Atlas: Releasing our next generation world model” 标为 2026 年 11 月 12 日；9 月 1 日的技术博客称 Atlas 是多模态自回归扩散 Transformer，可生成最长 1 分钟、1440p 视频。李飞飞个人账号于北京时间 11 月 13 日 02:11 发帖称“Atlas 现已向所有人开放”。AMD 收购 World Labs 的约 82 亿美元金额出自智东西报道，本期未回 AMD 原文核对，正文不写金额。

Will DePue 报告：发布于 2026 年 11 月 12 日，作者署名 Will DePue（Unemployment Labs）。报告称在约 6 万亿种“随机种子与芯片布局”组合中搜索，六个模型的最强证据在 49 至 1,385 sigma；在 B300 上复现了 DeepSeek-V4-Flash 的未训练权重，在租用的 GB200 上复现了 Kimi K3 的保留行；并称其方法与 24 个开发者公开过硬件的模型一致。报告明确写出：只能说明初始化所用硬件，不能确定芯片所在地、获取方式或是否违反出口管制；也不能完全排除特殊配置的 AMD MI300X（DeepSeek-V4-Flash 已排除）。他在帖中称结果经 OpenAI 和 Anthropic 资深研究员独立验证，本期无法核实。复现脚本“可应审阅者请求提供”。Hacker News 该帖约 145 分。

Simon Willison 的价格表：Carbon 与 Argon 至 11 月 30 日为输入 2 美元、输出 10 美元，12 月 1 日起为 4 美元、20 美元；Hydrogen 为 1.5 美元、7.5 美元。他还写 Hydrogen 约为 Claude Haiku 5.5 和 GPT-6 Luna（均为 0.10 美元、0.50 美元）的 15 倍。Carbon/Argon 调价本期未回谷歌定价页核对。

Hacker News（采集约北京时间 11 月 13 日 09:12）：Anthropic IPO 页面约 809 分；Microsoft 365 服务降级约 475 分；Rust 1.100 约 394 分；面向小型和旧设备运行大模型的 smolmaxxing 约 277 分；Jane Street 调整工程面试约 167 分；Apple Foundation Models framework 页面约 116 分（页面无日期，本期未判断是否为新发布，未写入正文）；Edge0-145B 约 23 分，未展开。Lex Fridman 北京时间 11 月 13 日 05:04 发帖称英伟达放走黄仁勋是“巨大错误”，属个人观点，未列入“三个人”。

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11 月 13 日 09:12；当时页面 13 行）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) | 2,972 / +739 | TypeScript | 让编码智能体跟上最新网页最佳实践 |
| [openai/codex-security](https://github.com/openai/codex-security) | 12,428 / +643 | TypeScript | 查找、验证和修复安全漏洞的 Codex Security 命令行与 SDK |
| [nvm-sh/nvm](https://github.com/nvm-sh/nvm) | 96,014 / +63 | Shell | Node 版本管理器，与人工智能无直接关系 |
| [pookjw/HermesEnabler](https://github.com/pookjw/HermesEnabler) | 1,540 / +218 | Objective-C | 在任意 Apple Watch 上启用爱马仕表盘，与人工智能无直接关系 |
| [we-promise/sure](https://github.com/we-promise/sure) | 13,925 / +967 | Ruby | 个人记账应用，与人工智能无直接关系 |
| [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) | 29,816 / +151 | TypeScript | 运行在终端里的开源编码智能体 |
| [ashhart/TensorFold](https://github.com/ashhart/TensorFold) | 1,940 / +54 | Zig | 支持 Metal、CUDA、Vulkan 的大模型推理引擎 |
| [nodejs/node](https://github.com/nodejs/node) | 123,601 / +62 | JavaScript | Node.js 运行时，与人工智能无直接关系 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 116,676 / +816 | JavaScript | 给编码智能体的工程技能 |
| [meta/astryx](https://github.com/meta/astryx) | 26,551 / +1,830 | TypeScript | 面向智能体的开源设计系统 |
| [CopilotKit/OpenBot](https://github.com/CopilotKit/OpenBot) | 11,620 / +298 | TypeScript | 每个 AI 同事配有自己的浏览器、文件和工具 |
| [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code) | 69,297 / +415 | Python | 自称可免费使用多种编码智能体工具，合规性未核实 |
| [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp) | 134,563 / +176 | C++ | C/C++ 大模型推理 |

来源覆盖：已阅读 AIHOT 11 月 13 日页（第 206 期，12 件大事、快讯 7 条；页面还写 17 个来源、7 件一手发布）、Hacker News 首页、GitHub 热榜及三位个人 X 原帖；正文关键事实以公司公告、官方博客、模型卡或研究报告原文为依据。原入口 aihot.virxact.com/daily 本期 301 跳转到 aihot.news/moved/daily 后返回 403，改从 aihot.news/daily 取得页面。AI Digest 中文版此前已确认停更于 2026-10-23，本期快速访问页面仍显示停更说明，未重试。AIHOT 快讯中的 OpenAI 自动化红队、Epoch AI 华为数据中心分析、Figma 三维变换、谷歌智能眼镜预购、OpenRouter 本地化与防循环教程等，本期未逐条回原文，未写入；“Grok Bot 1.0 发布”一条同样未回原文，未写入。

</details>

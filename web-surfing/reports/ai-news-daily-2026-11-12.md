---
title: "AI 行业日报 · 2026-11-12"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-12"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.virxact.com/daily"
---

# AI 日报 · 2026年11月12日

今天先看三件事。

- 谷歌推出 Gemini Decisions API，由新模型 Gemini Decision 1 驱动。一次前向计算可对文本、图像、音频、视频和 PDF 评估最多 1000 道是非、选择题和评分题，官方称端到端延迟 150 至 250 毫秒，输入每百万词元 0.10 美元，不收输出词元费用。

- 亚马逊云科技发布本地模拟器 AWS Emulator，可在自己的电脑上用同一套接口测试应用，不必接上真实云账号。公司称全部代码由自主智能体编写，团队没有写过或审过其中任何一行；这是亚马逊自己的说法。

- 谷歌 DeepMind 发布 AlphaGenome 2，用来预测 DNA 变异如何影响特定类型的人类细胞。非商业研究可经接口使用；公司写明，它尚未通过临床或诊断用途的验证。

## 谷歌发布 Decisions API：一次计算给出封闭式判断

谷歌于美国时间 11 月 11 日在[官方博客](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-decisions-api/)介绍 Gemini Decisions API，以及专用模型 Gemini Decision 1。它面向工具选择、策略检查、模型路由和内容打分这类有边界的选择，经 Google AI Studio 的 Gemini 接口提供，要的是封闭选项而不是长文本。

官方写法是：一份最多 25.6 万词元的多模态输入，可同时附上最多 1000 道彼此独立的是非、多选（2 至 255 项）或等级评分题；模型不做逐词生成，而是一次前向计算给出概率和 0 到 1 的置信度。端到端延迟写的是 150 至 250 毫秒，模型计算中位时延 50 至 100 毫秒，且该延迟数字仅适用于上下文不超过 1.6 万词元、每请求 1 至 100 道题的情形。

价格为输入每百万词元 0.10 美元、输出不收费，共享输入只计一次。谷歌称在自建的路由、推理、排序和多模态套件上该模型领先，校准误差最低，综合成本约为用 Interactions API 调用 Gemini 3.5 Flash-Lite 的五分之一。这些比较和 Notebook、Stitch、搜索安全层等内部用例，都出自谷歌自己。该帖在 Hacker News 约 255 分。

## 亚马逊称 AWS Emulator 的代码全部由智能体写成

亚马逊云科技 11 月 11 日推出 [AWS Emulator](https://www.aboutamazon.com/news/aws/how-autonomous-ai-agents-built-aws-emulator)，可在本地用现有的命令行和软件开发工具包访问模拟出来的云接口，不必部署、也不必开账号。资深首席工程师 Matthew Goldberg 写到：全部代码由自主智能体编写，团队没有写过或审过其中任何一行。

他描述的工作方式是三组智能体分别维护测试、找问题和改代码。测试先对照真实云服务调通，再拿来衡量模拟器是否一致；代码要经过编译、安全检查和保真度回归等关卡。文章写到仓库起初按 438 份公开 API 模型搭了一个空的服务端，测试“有好几万项”，并称每天有数以千计的问题被修复。

源码以 CC0 发布在 [GitHub](https://github.com/aws/aws-emulator)，未实现的接口返回 501。公开仓库里还有智能体已修复和仍未对齐的问题目录。这是公司对开发过程的自述，本期没有独立复核提交记录或保真度测试。该仓库链接在 Hacker News 约 649 分。

## 百度发布 ERNIE 5.5 Flash Preview，权重将于 11 月 25 日前开源

百度文心 11 月 11 日发布 [ERNIE 5.5 Flash Preview](https://ernie.baidu.com/zh/release/ernie-5-5-flash-preview/)，这是此前开源的 Base 模型的首个后训练版本，总参数 2800 亿、激活参数 140 亿，上下文 100 万词元。中文公告写明，接口已在千帆平台上线，权重将于 11 月 25 日前开源；英文页补充将采用 Apache 2.0 许可。

官方展示了它在游戏开发、三维建模、知识工作和视频创作中的智能体成果，并说明用到了外部素材和工具。公司同时提醒：这是后训练过程中的中间版本，可能仍有训练不足带来的能力缺陷，正式版还会继续改。演示效果和基准分数都是百度自报，权重是否已出现在第三方推理仓库，不以本公告为准。

11 月 7 日本刊报过 ERNIE 5.5 Flash Base 开源，这是之后的首个对话与智能体版本。

## Runway 以 Apache 2.0 开放 Praxis-1 权重

Runway 于 11 月 11 日宣布，世界动作模型 [Praxis-1](https://runwayml.com/news/company-news/praxis-1-is-now-available) 的权重、推理和微调代码均以 Apache 2.0 开放，包括商用。它在 9 月首次亮相，这次把同一套模型交给所有开发者。官方称这是 270 亿参数的混合专家扩散变换器，同时预测视频和动作。

在英伟达 RoboLab-120 榜上，Praxis-1 在 1200 次试验中成功率为 46.2%，高于 FLUX 3 Action 的 42.9%、Cosmos3 Nano 的 36.8% 和 π0.5 的 28.0%；数据标注为 2026 年 11 月。公司还称，在训练中未见过的 Google RT-1 机器人上微调后，SimplerEnv 成功率达到 80.0%，高于原版 RT-1 策略的 52.4%。这些数字均来自 Runway。

## DeepMind 发布 AlphaGenome 2：把变异效应细到细胞类型

谷歌 DeepMind 11 月 11 日发布 [AlphaGenome 2](https://deepmind.google/blog/alphagenome-2-deciphering-how-cells-read-dna-to-better-understand-disease/)。上一代按组织整体数据做并行预测，这一代改成条件式架构，一次针对一种组织、细胞类型或状态。训练数据包括超过 1.07 亿个单细胞样本，覆盖 68 种组织；文中也写“逾 1 亿”。

在 TenK10K 这张 28 种原代免疫细胞图谱上，公司称它识别出的因果变异约占 30%，上一代在单细胞数据上微调后为 16%；方向正确的基因效应为 43% 对 23%。研究者可上传自己的单细胞数据、不必重新训练。接口即日起对非商业研究开放，商业研究需申请预览。谷歌写明：该模型仅供研究，尚未获准用于临床或诊断。

## 热榜上，设计系统仍居首，安全和计划类仓库新入列

[GitHub 热榜](https://github.com/trending)在北京时间 11 月 12 日约 09:13 采集，当时页面列出 10 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。与昨日相比，技能包仓库仍在前列，但名单已换成 10 行。

[meta/astryx](https://github.com/meta/astryx) 当天约增加 2,776，总星约 25,016，连续多日居前。[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 约增加 787；[vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) 约增加 708；家居助手 [ha-mcp](https://github.com/homeassistant-ai/ha-mcp) 约增加 645。新面孔里，[shadcn/improve](https://github.com/shadcn/improve) 用更强模型给较弱模型写执行计划，约增加 361；Chrome 团队的现代网页指南源码约增加 159；[openai/codex-security](https://github.com/openai/codex-security) 约增加 52。记账应用 sure 约增加 1,078，算法仓库 TheAlgorithms/Java 约增加 51，两者与人工智能无直接关系。全表在文末。

## 三个人怎么说

**Sebastian Raschka**，机器学习研究者，著有从零构建大模型的教材。他引用一条讨论评测风气的帖子，[写道](https://x.com/rasbt/status/2120519373999816955)：改进模型是 hillclimbing，测量改进是 benchmarking，把数字做得更好看是 benchmaxxing。帖发于北京时间 11 月 11 日 22:09，属个人评论。

**Jim Fan**，英伟达机器人研究负责人、杰出科学家，GEAR 实验室共同负责人。他[发帖](https://x.com/DrJimFan/status/2120540201994846253)展示 GR00T 2 在真实灵巧手上完成化学实验并自行清理的录像，强调未经剪辑、为 1 倍速，并说会继续发布不加速的机器人视频。帖发于北京时间 11 月 11 日 23:32，属团队工作的个人展示；模型能力以官方说明和完整录像为准，不能单凭片段外推。

**Lucas Beyer**，Meta 研究员，曾在 OpenAI、DeepMind 和 Google Brain 工作。他引用 Claude 官方账号关于白板、表格与数据产品上线的帖子，[评论](https://x.com/giffmana/status/2120593715328917554)说，一家做 AI 安全的公司产品品味一直不错，让他觉得有些奇怪。帖发于北京时间 11 月 12 日 03:05，属个人观感；这些产品本刊昨日已作介绍。

## 另外几则

**OpenAI 第三季度营收（媒体转述）。** The Decoder 11 月 11 日[撰文](https://the-decoder.com/enterprise-sales-push-openais-quarterly-revenue-to-10-billion-though-it-still-trails-anthropic/)，转述《华尔街日报》和 The Information：OpenAI 第三季度营收环比约增 50%、至 100 亿美元，调整后经营亏损由 101 亿升至 109 亿美元，其中不含 26 亿美元股票薪酬。文中还写 Anthropic 同期营收 170 亿美元，含股票薪酬的经营亏损 5.67 亿美元。本期未读到两家原报，也不是公司官方财报。

**Claroc 称近九成五 Grok 应用可被打开。** The Decoder 11 月 11 日[转述](https://the-decoder.com/grok-built-apps-exposed-patient-data-plaintext-passwords-and-spacexsis-own-sales-pipeline/)安全公司 Claroc 的报告：在仍在线的 37,571 个 Grok 构建应用中，35,578 个（94.7%）无需登录即可访问。公司方面（该文称为 SpaceXSI，并写明原为 xAI）回应称，应用在创建者分享前是私密的，发布需多步确认，员工账号默认“仅自己可见”。Claroc 认为最后一步仍预选“有链接的人可访问”，并说明自己也出售面向 AI 应用的安全产品。本期未读到 Claroc 原文。

**针对 xAI 的集体诉讼。** 彭博社 11 月 11 日[报道](https://www.bloomberg.com/features/2026-grok-sexualized-childhood-photos/)，多名未成年人起诉 xAI，指 Grok 被用来把普通照片改成儿童性虐待材料。这是原告主张，尚未经法院认定。本期未能打开该文全文，不以转述补充细节。

**美联航禁止 AI 助手代客订票。** 美国联合航空 11 月 11 日表示，将在自有平台及代理、聚合渠道限制未经授权的第三方个人 AI 助手代客操作，理由包括账号与支付信息外泄、误下单或动用里程，以及值机等动作可能违反联邦行李申报规定。这是航司政策声明，[CBS News](https://www.cbsnews.com/news/united-airlines-bans-ai-agents-booking-flights/) 作了报道。分析师关于搜索成本与渠道控制的评论，属于个人判断。

**多智能体协作基准 MAMUBench。** Anthropic Fellows 项目 11 月 11 日[发文](https://alignment.anthropic.com/2026/worse-together/)称，在共享预算、诊所排班、团体订餐或出行、合并队列四类模拟环境中，由一个智能体服务所有用户，群体结果普遍好过每人各派一个智能体。两个 Claude 模型的差距约 10 至 45 个百分点。其中三个环境将作为 MAMUBench 公开。数字来自该团队实验。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

Gemini Decisions API：模型标识为 gemini-decision-1；三种题型分别是 noul（是非）、choice（多选）和 score（有序评分）。延迟“几乎不随 1 至 100 道题变化”的表述，限定在多模态输入、上下文不超过 1.6 万词元。输入按请求共享部分只计一次，各题的说明和选项词元另计；官方还提到 Google AI Studio 有可用于原型的免费额度。生态集成称正在对接 OpenRouter、LangChain、Vercel、LiteLLM 等，Google Cloud 上的 Gemini 支持“即将推出”。领先幅度和“约便宜 5 倍”均为谷歌自建套件上的比较。

AWS Emulator：Goldberg 一文发布于 2026 年 11 月 11 日。三组智能体之外，合并前还有编码规范、安全和保真度检查；他写“如果没有这道合并关卡，我们不会信任智能体正在构建的东西”。文章提到早期版本曾自行编写 Python 解释器以支持 Lambda，后来被要求改用现有库。Hacker News 采集时该仓库帖约 649 分，页上标题为 “AWS emulator”。

ERNIE 5.5 Flash Preview：中文公告日期为 2026 年 11 月 11 日；英文页同样写 11 月 11 日，并写明权重“即将”以 Apache 2.0 开源。千帆文档在同日更新中已列出 ernie-5.5-flash-preview，上下文 1M。公告中的游戏、建模和视频案例均声明使用了外部素材或生成工具，不能理解为纯由该模型单独画出或渲染。

Praxis-1：Runway 称可在 GitHub、Hugging Face（带 LeRobot）、vLLM-Omni 和托管推理服务 Reactor 上使用，并覆盖 H100、B200、RTX 5090、RTX PRO 6000 和机器人端的 Jetson Thor。RoboLab-120 数字标注为 “Data as of November 2026; Success rate across 1,200 episodes”。“胜过所有开源权重 VLA”是公司表述。

AlphaGenome 2：训练数据同时包含人类和小鼠的整体与单细胞样本。文中既写 “more than 100 million individual cell profiles across 68 tissues”，后文又写 “over 107 million”。TenK10K 比较对象是“在单细胞数据上微调后的原版 AlphaGenome 以及其他专用工具”。公司还称可做跨模态补全，例如从单细胞基因活性推断染色质可及性，并能在未见过的新冠 mRNA 疫苗研究数据上区分活化与静息 T 细胞。这些都是 DeepMind 自报，本期未读技术论文全文。

OpenAI 财务转述：The Decoder 还写，上一季度营收增速为 17% 至 18%，一年前营收 39 亿美元；调整后经营利润率由第二季度的负 150% 变为负 109%，一年前为负 97%；ChatGPT 周活跃用户 12 亿、付费用户 1 亿（新增 2200 万）；广告产品在 8 月达到 10 亿美元年化收入。总裁 Greg Brockman 称企业业务在第三季度翻倍，已占营收大头。以上均转自该文对《华尔街日报》和 The Information 的转述，本期未核对原报。

Claroc：报告称约十分之一的开放应用含敏感、内部或个人信息，约 2% 被列为尤其严重，并估计 650 至 800 个应用含私人数据；确认例子包括重症监护汇报、超过 3,500 人的医院员工名单，以及工时应用源码中的 18 个明文密码账户。24 个员工应用已被下线。该文称还识别出 30 个受影响组织，其中 6 个为财富 500 强，名称未公布。Claroc 建议默认改为“仅自己可见”，并用难以猜测的路径代替可被被动 DNS 检索的独立子域名。

Hacker News（采集约北京时间 11 月 12 日 09:13）：AWS emulator 约 649 分；Gemini Decisions API 约 255 分；美联航禁止 AI 助手代订约 333 分；《华尔街日报》关于英伟达董事会接近决定是否罢免黄仁勋的报道约 453 分，这是未证实的媒体报道，本刊 11 月 9 日已报过董事会启动独立调查，不把标题写成既成事实。Apple 机器学习博客关于检索与 RAG 的文章约 148 分，本期未展开。个人博客称智能体发现未登记玛雅遗址的帖约 920 分，未经独立考古核实，未写入正文。

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11 月 12 日 09:13；当时页面 10 行）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [meta/astryx](https://github.com/meta/astryx) | 25,016 / +2,776 | TypeScript | 面向智能体的开源设计系统 |
| [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | 70,265 / +278 | Python | LLM 驱动的多市场股票分析系统 |
| [GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) | 1,763 / +159 | TypeScript | Chrome 团队现代网页指南的源码仓 |
| [shadcn/improve](https://github.com/shadcn/improve) | 10,889 / +361 | （页面未标） | 用更强模型审计代码库，为较弱模型写执行计划 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 115,962 / +787 | JavaScript | 给编码智能体的工程技能 |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | 49,878 / +708 | Rust | 给智能体用的浏览器自动化命令行 |
| [we-promise/sure](https://github.com/we-promise/sure) | 12,968 / +1,078 | Ruby | 个人记账应用，与人工智能无直接关系 |
| [homeassistant-ai/ha-mcp](https://github.com/homeassistant-ai/ha-mcp) | 7,379 / +645 | Python | 用 AI 助手配置 Home Assistant |
| [openai/codex-security](https://github.com/openai/codex-security) | 11,743 / +52 | TypeScript | OpenAI 的 Codex Security 命令行与 TypeScript 工具包 |
| [TheAlgorithms/Java](https://github.com/TheAlgorithms/Java) | 67,029 / +51 | Java | Java 算法实现合集，与人工智能无直接关系 |

来源覆盖：已阅读 AIHOT 11 月 12 日页（12 件大事、快讯 6 条；页面还写 10 个来源、7 件一手发布）、Hacker News 首页、GitHub 热榜及三位个人 X 原帖；正文关键事实以公司公告、官方博客或可核转述为依据。AI Digest 中文版此前已确认停更于 2026-10-23，本期未重试。AIHOT 及聚合渠道还提到 Anthropic 招股书修订稿中与微软、谷歌的算力承诺数字，该修订稿本刊昨日已引用；本期再次访问美国证交会原文被自动访问限制拦截，未重新核验具体数字，故不单列。ChatGPT Business Hub、Cursor Projects 多人协作等条目本期未读到官方原文，未写入。英伟达人事后续只有媒体报道，无公司确认，不作为头条。

</details>

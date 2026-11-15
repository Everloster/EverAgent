---
title: "AI 行业日报 · 2026-11-15"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-15"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.virxact.com/daily"
---

# AI 日报 · 2026年11月15日

今天先看三件事。

- Cursor 于 11 月 13 日公布安全事件调查：攻击者利用 Fireworks 侧暴露的访问密钥，读到用于训练的编程智能体轨迹，并在 10 月 29 日把恶意 Claude Code 扩展放入扩展市场缓存，最多约 5,000 名用户可能收到。公司称事件已受控。

- Thinking Machines Lab 11 月 13 日发表端到端 4-bit 训练技术报告，称在 Inkling 2 Small 上从预训练到强化学习全程使用同一套数值配方。公司自报，最大任务相对全程 MXFP8，预训练墙钟时间加快 8%，强化学习加快 20%。

- 美联储 11 月 13 日发布金融稳定报告。纽约联储工作人员在 9 月至 10 月向 23 名市场联系人做的调查中，87% 将人工智能列为显著风险，高于春季的 50%。该汇总只反映受访者看法，不代表美联储的观点。

## Cursor 公布调查：恶意扩展最多波及约五千用户

Cursor 在 11 月 13 日的[博客](https://cursor.com/blog/security-incident-update)中补充了 10 月 29 日事件的调查结果。公司称，攻击始于 Fireworks 暴露了一把由 Cursor 签发给该供应商的访问密钥，攻击者据此从只读存储桶中复制数据。桶里是有限的编程智能体轨迹，大多来自 2025 年、且未开启隐私模式的会话。

其中少量轨迹含有未被脱敏的凭证，公司称因此暴露应用程序接口凭证的客户不到 0.01%。攻击者随后进入 Cursor 使用的部分软件服务，接触到部分已归档的非生产代码库、有限的客户支持数据、产品使用指标，以及部分编程智能体对话摘要和用户发给支持团队的凭证。

10 月 29 日，攻击者用从内部系统暴露数据中窃取的凭证，把未经授权的 Anthropic Claude Code 扩展副本放到了为 Cursor 扩展市场提供服务的缓存上。公司强调这不是 Anthropic 发布的版本，也不是 Anthropic 产品的漏洞，开源市场 Open VSX 中从未出现该恶意软件。

公司称，当天最多约 5,000 名请求了特定缓存版本的用户可能收到恶意构建，该构建在线约 11 小时后被撤下；涉及版本为 Anthropic.claude-code 2.1.312 和 2.1.313。10 月 30 日已发布安全通告。公司还称：开启隐私模式的提示词与代码未受影响；未开启隐私模式时，轨迹被暴露的用户不到 0.05%，并已逐一通知；生产系统和正式更新的签发密钥未被访问。以上均为 Cursor 自报。

## 端到端 4-bit 训练：同一套配方从预训练用到强化学习

Thinking Machines Lab 的 Jack Cook 等人 11 月 13 日在[官方博客](https://thinkingmachines.ai/blog/end-to-end-4-bit-training/)发表训练方法说明：他们在英伟达 GB300 上训练 Inkling 2 Small 时，专家层前向使用 NVFP4，反向使用 MXFP8，并配合重新量化和随机舍入以降低梯度偏差。

公司称，这是他们所知最大的、从头到尾采用原生 4-bit 前向传播训练的模型，数值设置从预训练一直用到最后一轮强化学习，交付量化检查点时不必再校准。在最大的训练任务中，该配方相对全程 MXFP8 训练，预训练墙钟时间加快 8%，强化学习加快 20%。

预训练 Inkling 2 Small 时，计算效率大约损失 2%：也就是达到同等损失，大约相当于比 MXFP8 少用 2% 的浮点运算次数，以此来换取 NVFP4 带来的速度。强化学习阶段则称端到端明显加快，奖励没有可察觉的差别。这些数字和比较均来自该公司，本期未做独立复现。Inkling 2 Small 开放权重已在 11 月 13 日日报中写过，本期只补充这份训练方法说明。

## 美联储报告：受访人士最常提到的风险是人工智能

美联储 11 月 13 日发布[《金融稳定报告》](https://www.federalreserve.gov/publications/files/financial-stability-report-20261113.pdf)，数据大体截至 10 月 28 日。报告中的“显著风险调查”由纽约联储工作人员在 9 月至 10 月收集，共 23 名联系人，来自经纪自营商、银行、投资基金和咨询机构。

在被问及未来 12 至 18 个月可能冲击美国金融体系的因素时，87% 的受访者提到人工智能，高于春季（3 月至 4 月、20 名联系人）的 50%；其次是风险资产回调 52%、长期利率上升 48%，网络攻击和财政可持续性均为 43%。受访者把人工智能风险分成三类：估值偏高及盈利不及预期可能引发调整，人工智能相关的网络安全风险，以及复杂的人工智能融资形式。

报告另设专栏讨论数据中心扩张中的杠杆：与先进计算相关的债务发行到 2026 年 10 月已超过 6,800 亿美元，约为 2023 年全年 1,300 亿美元的五倍；这类借款占非金融投资级公司债发行的比重，从 2023 年的不足 6% 升至 2026 年的约 31%。

截至 10 月，与先进计算相关的存量公共债务估计超过 1.1 万亿美元。上述债务发行口径包含可追踪的 144A 私募，但不包含 4(a)(2) 私募，因此并不是全部私募。调查结果不代表美联储的官方判断。

## 请愿要求恢复黄仁勋职务，签名已逾 11.5 万

TechCrunch 11 月 14 日（美国太平洋时间下午 1:41，北京时间 15 日 05:41）[报道](https://techcrunch.com/2026/11/14/elon-musk-other-tech-execs-sign-petition-calling-on-nvidia-to-reinstate-jensen-huang/)，一份要求英伟达在独立调查查明事实期间恢复黄仁勋职务的请愿，截至周六下午已获得超过 11.5 万个签名。

请愿网站列出的签名者包括 5,965 名在职员工、1,108 名前员工和 63,063 名股东；报道点名马斯克、Replit 首席执行官 Amjad Masad、Epic Games 首席执行官 Tim Sweeney 和 Y Combinator 首席执行官 Garry Tan 已联署。员工与股东身份来自请愿网站的自行标注，本期未逐一核实。这是对已在 11 月 13 日日报写过的领导层变动的后续，并不等于董事会已改变决定。

## Nathan Lambert：开源模型少了关键支持者

研究者 Nathan Lambert 11 月 14 日在 Interconnects 发表[文章](https://www.interconnects.ai/p/open-source-ai-without-jensen)（发布于北京时间 20:23），讨论黄仁勋辞职后美国开放权重模型生态可能出现的空档。他认为，英伟达对开源模型的资金支持很可能随之减少，公司眼下更需要稳住运营并向客户交货；开放模型仍需要有人在监管压力和融资困难时出面协调。这是个人分析，不是英伟达的政策说明。

## 热榜上，网页指南仍是当天增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11 月 15 日约 09:13 采集，当时页面列出 15 个仓库，数字为当时所示。上榜只表示关注，不是当天发布；数字只保留采集时原页所示，不外推到其他时点。

[GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) 当天约增加 1,231，总星约 6,067，仍是增量最高，但较昨日约 1,925 的增量有所放缓。[alibaba/open-code-review](https://github.com/alibaba/open-code-review) 约增加 893，总星约 51,448。[ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) 约增加 664，总星约 56,315。

新面孔里，[dream-num/univer](https://github.com/dream-num/univer) 面向办公与智能体，约增加 495；[QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) 是终端里的编码智能体，当天增加不多；[Tencent/LoopForge](https://github.com/Tencent/LoopForge) 用于编排编码智能体工作流，总星约 915。[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) 自称能减少智能体词元，页面当时总星为 120,082，其效果声明未经核实。记账应用 sure、监控工具 uptime-kuma 和无线审计工具 airgorah 与人工智能无直接关系。全表在文末。

## 三个人怎么说

**Nathan Lambert**，Interconnects 作者，Trillium Labs 创始人、主管，此前在艾伦人工智能研究所共同负责 Olmo。他[写道](https://x.com/natolambert/status/2121581040972255257)，黄仁勋之后，开放模型世界主要面临两件事：华盛顿的政治支持在后退；没有他的托底，做开放模型的人必须更快找到能赚钱的产品，而且影响会比人们预想的来得更早。帖发于北京时间 11 月 14 日 20:28，属个人判断，并指向他同日的文章。

**Sebastian Raschka**，机器学习研究者，著有从零实现大语言模型的教材。他[写道](https://x.com/rasbt/status/2121613812990095543)，Inkling 2 Small 比他原先想的更有意思：用了类似 Kimi K3 的注意力残差，但没有混合线性注意力，可供年底讨论架构趋势时参考。帖发于北京时间 11 月 14 日 22:38，属个人技术观察。

**Ethan Mollick**，宾夕法尼亚大学沃顿商学院教授，研究人工智能。他[写道](https://x.com/emollick/status/2121751565845360769)，自己汇总了一个名为 SatBench 的观察：实验室自 2023 年以来引用的 173 个主要基准里，已有 63% 被“做满”（基本上被打穿），而且饱和速度逐年加快。帖发于北京时间 11 月 15 日 07:46。这是他本人的统计和定义，不是一篇经过同行评审的论文，口径和样本需自行核验。

## 另外几则

**亚洲多国政府回应英伟达领导层变动。** TechCrunch 11 月 14 日[报道](https://techcrunch.com/2026/11/14/asian-governments-react-to-nvidia-ceo-jensen-huangs-exit/)：韩国科技部称，英伟达已重申将向韩国供应 26 万块先进 GPU，并继续联合人工智能项目；台湾经济部长 Kung Ming-shin 认为此事不太可能显著改变全球人工智能产业增长；日本经济产业省表示将密切关注英伟达。这些均为政府对媒体的表态，不是新的供货合同文本。

**Anthropic 首席执行官谈算力两难。** 据 The Decoder 11 月 14 日[报道](https://the-decoder.com/anthropic-ceo-amodei-admits-theres-a-huge-uncertainty-in-whats-going-to-happen-next-year-days-before-a-record-ipo/)，Dario Amodei 周五在纽约摩根大通的投资者活动上说，算力是公司“最深的商业两难”，需要提前一到两年采购，但谁也不知道明年收入是否跟得上；买少了会限制客户和新技术，买多了则可能把财务摊子铺得过大。报道还转述了彭博关于承诺金额和上市规模的数字，本期未回彭博原文，不写入正文。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

Cursor：官方博客日期为 2026 年 11 月 13 日，标题 “An update on our recent security incident”。公司称已切断 Fireworks 的推理与数据访问并轮换相关凭证，重建了扩展市场，并请外部取证协助调查；最后一次攻击活动出现在 11 月 1 日并已被阻断，公司认为事件已受控。若曾在 10 月 29 日曝光窗口内安装或更新到被篡改的 2.1.312 或 2.1.313 版本，仅卸载扩展可能不够，需按 10 月 30 日安全通告处理持久化项并轮换凭证。10 月 30 日通告还写明，恶意代码试图收集主机信息并安装反向 SSH 隧道；在多数未以管理员权限启动 Cursor 的主机上，开启本地 SSH 服务这一步会因权限不足而失败。以上均为 Cursor 自报。

端到端 4-bit 训练：文章署名为 Jack Cook，并注明与 Thinking Machines 其他同事合作，日期 2026 年 11 月 13 日。NVFP4 在 GB300 上的峰值算力表由公司给出，本期未核对其硬件标称。前向量化主要针对混合专家层。公司称该配方在监督微调与强化学习中无需改动。上述速度、计算效率和奖励比较均相对全程 MXFP8，且为公司自报。

美联储报告：文件名为 financial-stability-report-20261113.pdf，文首注明信息大体截至 2026 年 10 月 28 日。87%、52%、48%、43%、43% 与春季 50% 均来自报告开篇的调查对照图；箱文 5.1 写明秋季为 23 名联系人、春季图注为 20 名。债务发行数字来自箱文 2.2，并写明未开始的租赁（未折现）超过 1 万亿美元，承购合约和残值担保等其他义务（未折现）超过 2 万亿美元；文中也提到超大规模云厂商与芯片设计商之间存在“循环融资”现象。报告还写明，广泛股票估值指标仍处历史区间上端。本文未使用部分转述中“银行风险敞口接近 1 万亿美元”的说法，因在原文中未找到对应表述。

请愿：TechCrunch 报道时间为 2026-11-14 13:41 PST（北京时间 11 月 15 日 05:41），作者 Anthony Ha；文中“截至周六下午”对应 11 月 14 日。请愿要求在独立调查查明事实期间让黄仁勋回来，并要求调查公平、向公众提供更多信息。

Nathan Lambert 文章：页面元数据 datePublished 为 2026-11-14T12:23:15+00:00（北京时间 20:23）。

Hacker News（采集约北京时间 11 月 15 日 09:13）：一篇称 Lovable 应用泄露护照信息和逾 20 万条私信的报道约 623 分，本期未回作者原文，未写入正文。Show HN“用约 200 行纯 Jax 实现 DeepSeek V3”约 167 分，属个人演示。谷歌 /teamwork 博文约 158 分，已在 11 月 14 日日报写过。一篇密歇根大学关于生成式人工智能处理非英语文本能耗的报道约 174 分，本期未回论文原文。一篇称英伟达借循环融资维持 GPU 高价的 TechSpot 聚合报道约 144 分，属第三方指称，未作为独立事实展开。首页前列还有 SpaceX 星舰回收、PyPI 页面改版和意大利对 Meta 罚款等，与本期主题无直接关系。

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11 月 15 日 09:13；当时页面 15 行；页面日期头为 2026-11-15 01:13:13 GMT）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [backnotprop/plannotator](https://github.com/backnotprop/plannotator) | 11,141 / +408 | TypeScript | 用于规划、批注并把反馈一次性交给智能体的工作区 |
| [GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) | 6,067 / +1,231 | TypeScript | 让编码智能体跟上最新网页最佳实践 |
| [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) | 4,827 / +553 | Python | 面向股票投资者的 Claude Code 技能 |
| [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 56,315 / +664 | TypeScript | 给编码智能体用的 Chrome 开发者工具 |
| [alibaba/open-code-review](https://github.com/alibaba/open-code-review) | 51,448 / +893 | Go | 阿里巴巴规模上使用的代码审查工具：确定性流水线加大模型智能体 |
| [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) | 30,350 / +64 | TypeScript | 运行在终端里的开源编码智能体 |
| [dream-num/univer](https://github.com/dream-num/univer) | 24,505 / +495 | TypeScript | 把编辑、计算、协作和文件处理提供给人或智能体的办公软件开发包 |
| [ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) | 17,371 / +9 | TypeScript | 把智能体接入前端应用的交互协议 |
| [ashhart/TensorFold](https://github.com/ashhart/TensorFold) | 2,165 / +37 | Zig | 面向 Metal、CUDA 和 Vulkan 的大模型推理引擎 |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 120,082 / +227 | Go | 自称用更短的说法减少编码智能体词元，其效果声明未经核实 |
| [louislam/uptime-kuma](https://github.com/louislam/uptime-kuma) | 94,245 / +430 | JavaScript | 自建监控工具，与人工智能无直接关系 |
| [we-promise/sure](https://github.com/we-promise/sure) | 15,321 / +659 | Ruby | 个人记账应用，与人工智能无直接关系 |
| [Tencent/LoopForge](https://github.com/Tencent/LoopForge) | 915 / +33 | Go | 自建工作流，用于编排编码智能体并加入人工批准 |
| [Likely7/Veyra-NRVideo](https://github.com/Likely7/Veyra-NRVideo) | 2,277 / +420 | C++ | 自称结合超分、DLSS 5 与补帧的视频增强工具，其声明未经核实 |
| [martin-olivier/airgorah](https://github.com/martin-olivier/airgorah) | 5,877 / +270 | Rust | 无线网络安全审计工具，与人工智能无直接关系 |

来源覆盖：已阅读 AIHOT 11 月 15 日页（第 208 期，6 件大事、快讯 1 条；页面写 6 个来源、2 件一手发布）、Hacker News 首页、GitHub 热榜及三位个人 X 原帖；正文关键事实以 Cursor 调查博客、Thinking Machines Lab 训练报告、美联储 2026 年 11 月金融稳定报告 PDF、TechCrunch 请愿报道、Interconnects 原文和 The Decoder 对周五讲话的报道为依据。原入口 aihot.virxact.com/daily 本期返回 301 并转到 aihot.news，仍从 aihot.news/daily 取得页面。AI Digest 中文版此前已确认停更于 2026-10-23，本期快速访问页面仍显示停更说明，未重试。ChatGPT Wallet、llama.cpp v1.0.0、英伟达 GR00T 2、DeepSeek 应用能力接口、Sierra Poppy 和谷歌 /teamwork 已在 11 月 14 日日报写过，本期不重复。部分聚合页提到的美团 LongCat-2.5 与 Nex-N2.6，回官方页面后分别对应更早的 11 月 10 日开源或上线，超出本期 48 小时窗口，未写入正文。

</details>

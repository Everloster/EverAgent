# AI 行业日报 · 2026-10-09

四源：AIHOT ✅ · GitHub Trending ⚠️ · AI Digest ❌ · HN ✅（本期五个重点一手页全部直读成功，状态说明见文末折叠块）
覆盖 2026-10-09（含 10-07/10-08 发布、今日仍在前排发酵的条目，逐条标注日期） · [上期日报 →](./ai-news-daily-2026-10-08.md)

---

## 今日要点

1. **OpenAI 撤回 3 篇数学论文**：一个符号错误连带两篇，另修正 14 篇
2. **数学界组织化抵制**：AHM 声明敦促停止与 OpenAI 合作，经陶哲轩博客发布
3. **ARTEX 取证剖面**：CrowdStrike 披露疑似单人用 AI 渗透工具攻击韩国银行
4. **OpenAI 营收缺口**：FT 披露年化近 500 亿美元，比外界预期少约 200 亿
5. **Anthropic Cyber Mission**：11 家伙伴防御计划 + 免费开源扫描 OSS Scanner
6. **ts-rust**：Opus 5.5 两周移植 TS 编译器，作者一行代码未读
7. **Waymo 首次发债**：50 亿美元债务融资，PIMCO 与 Blackstone 牵头
8. **端侧语音识别**：Whistle 把语音转文本压到 16.9 MB，登顶 HN
9. **Claude Dashboards 与 Motion**：实时仪表盘与动画讲解进入对话
10. **Trending 缩至 9 仓**：rea 三连登顶，日增 +7,738 全榜第一

---

## 头条 1 · 📄 OpenAI 数学线第三幕：撤回三篇 + 数学界组织化抵制——发布协议的撤回机制首次实战运转

**三句话速读**：OpenAI 在 10-07 撤回 722 篇数学手稿中的 3 篇，原因是一个符号错误及其向两篇依赖论文的级联。同一窗口，Association for Human Mathematics（AHM）发布声明，敦促数学家停止与 OpenAI 合作。声明经陶哲轩博客以客座文形式发布，撤回与抵制两条线在 24 小时内并拢。

**关键事实**
- Retraction Watch 报道：一个符号错误使一篇手稿的论证失效，并连带两篇使用其构造的论文；三篇均已带「the gap」说明撤回。
- OpenAI 同时修订了另外 14 篇手稿：证明修补、陈述更正、假设与依赖关系澄清、一处过时引用更正。
- OpenAI 发言人称错误在审计中发现；AGMAI 顾问小组建议「不等完全形式化」就发布，约 50% 的结果未经确认即发布。
- Retraction Watch 引述背景：此前对 09-08 Navier–Stokes 发布表达关切的联署研究者已超 8,000 人。
- AHM 声明原句：「一次性发布 700 多个文件不是学术的展示，而是力量的展示」；敦促数学家停止与 OpenAI 合作。
- 陶哲轩以客座文转发该声明于个人博客，并注明文本「最初以其他文件格式写成、经 AI 转换」。
- HN 条目「OpenAI withdraws three mathematical results」305 分 / 572 评论（1 day ago）。

**细读与质疑**
- 撤回与修订被 MIT 数学家 Andrew Sutherland 称为「负责任的做法」，但他同时认为这远不足以赢回失去的信任。
- 「陶哲轩主持 AHM」的说法不准确：一手文本显示是 guest post 转发；评论区有人要求 Tao 置顶澄清自己非 AHM 成员。
- 评论区呈现数学界内部分裂：有代数几何博士生公开反对声明，也有人（曾研究被解问题的数学家）表示解脱。
- AHM 声明本身经 AI 转换格式——抵制 AI 发布模式的文本由 AI 完成格式转换，是一处值得记录的张力。
- 约 50% 未验证发布、错误审计发现，均为 OpenAI 发言人单方口径，无独立核验。
- 撤回仍未回应 10-08 对抗论文的核心主张：Lean 形式化与自然语言证明是否对应。

**来源** · [Retraction Watch（本期直读，10-08T22:20Z，一手）](https://retractionwatch.com/2026/10/08/openai-withdraws-preprints-722-manuscripts-unsolved-math-problems) · [陶哲轩博客（本期直读，guest post，一手）](https://terrytao.wordpress.com/2026/10/07/ahm-statement-on-openais-october-6-release-of-mathematical-documents) · [HN 讨论 item 50002650（检索命中）](https://news.ycombinator.com/item?id=50002650) · [The Guardian（检索快照，学界关切口径）](https://www.theguardian.com/technology/2026/oct/07/openai-mathematical-findings-concerns) · 历史线：[10-08 日报头条 1（对抗论文）](./ai-news-daily-2026-10-08.md) · [10-07 日报头条 2（OpenAI 数学发布）](./ai-news-daily-2026-10-07.md)

---

## 头条 2 · 🔒 CrowdStrike 披露 ARTEX 事件：AI 渗透工具攻击的第一次完整取证剖面

**三句话速读**：CrowdStrike Intelligence 披露，一名疑似中文使用者于 9 月底至 10 月初用开源 agentic 渗透工具 ARTEX 攻击多家韩国金融机构。取证线索来自一个暴露的开放目录，其中含 Claude Code 会话记录与 ARTEX 配置。这是本日报追踪的韩国银行攻击事件线首次拿到工具与技术栈级的公开细节。

**关键事实**
- 活动时间为 2026 年 9 月底至 10 月初，造成数据外泄；未归因到已知威胁组织，证据指向经济动机的疑似中文使用者。
- 发现路径：香港 IP 上的开放目录暴露了 Claude Code 会话历史、Claude memory 文件与 ARTEX 配置文件。
- ARTEX 为 Autumn-27 开发的开源 LLM 多 agent 自主渗透系统；该实例以 DeepSeek v4.1-flash 为主后端，GLM-5.3 与 Grok 4.6 补充，疑似经 API 转售商 xcai.pro 接入。
- 会话记录显示行为者向 Claude 询问韩国数据泄露信息的销赃渠道与 Telegram 数据销售群。
- 因滥用，Autumn-27 宣布 ARTEX 停止更新并转闭源，称恶意使用违背工具初衷。
- 数据口径分层：Shinhan Bank 超 25,000 条记录泄露（The Decoder/AIHOT 口径）；首尔官方称共约 68,000 人数据被盗（WSJ 标题口径）。

**细读与质疑**
- CrowdStrike 自己声明：提示中泄露的 Telegram 账号等个人细节「不能确定归属该行为者」——单人归因仍是「likely」级。
- 25,000（Shinhan 单家）与 68,000（首尔官方总量）两组数字的包含关系未见任何一方说明。
- 「七家机构受害」仅见于低可信快照，未获权威来源确认，本期不采用。
- WSJ 与韩联社原文均未直读，上列外部数字停留在快照与标题级。
- 攻击者用 Claude 问销赃渠道说明通用助手在攻击链中的角色仍是「咨询」而非「执行」——与 ARTEX 的自主执行分工明确。

**来源** · [The Hacker News（本期直读，10-08T14:12Z，一手）](https://thehackernews.com/2026/10/artex-ai-pentesting-tool-used-in-data.html) · [AIHOT 10-09 期头条（直读，The Decoder 口径，25,000 条）](https://aihot.virxact.com/daily/2026-10-09) · [WSJ（检索快照，标题级，68,000 人口径）](https://www.wsj.com/world/asia/hackers-use-chinese-ai-tool-to-hit-south-korean-banks-exposing-new-risk-5d4d3885) · [韩联社 YNA（检索快照）](https://en.yna.co.kr/view/AEN20261008002200320) · 历史线：[10-07 日报头条 6（韩国官方表态）](./ai-news-daily-2026-10-07.md)

---

## 头条 3 · 🏢 FT：OpenAI 年化营收近 500 亿美元，比外界预期少约 200 亿——AI 股当日齐跌

**三句话速读**：金融时报查阅给投资者的文件，OpenAI 截至 9 月底年化营收接近 500 亿美元。此前外界广泛引用的数字约为 700 亿美元，缺口约 200 亿。报道发布当日，纳斯达克 100 收跌 1.4%，英伟达跌 2.9%，甲骨文跌 5.5%。

**关键事实**
- FT 报道经 CNBC 确认：OpenAI 向投资者披露 9 月底年化营收「接近 500 亿美元」。
- 此前外界估算约 700 亿美元（Quartz 单源另作 680 亿口径）；缺口约 200 亿美元。
- OpenAI 归因于统计口径差异：Anthropic 计入 AWS、谷歌云等合作方销售收入，OpenAI 剔除该部分。
- 市场反应（IT之家口径）：纳斯达克 100 收跌 1.4%，英伟达 -2.9%，甲骨文 -5.5%；CNBC 确认 AI 硬件股当日下挫。

**细读与质疑**
- FT 原文付费墙未直读，全部数字停留在多源快照交叉层（CNBC/Yahoo/Quartz/ksl 同向）。
- 「接近 500 亿」是区间表述而非精确值；「approaching」的弹性未获说明。
- 口径差异成立的话，OpenAI 与 Anthropic 的营收数字不可直接对比——此前各期日报引用的营收对比均需加此脚注。
- 市场下跌与该报道之间是时序归因而非因果证明，当日并无其他同等量级宏观事件。

**来源** · [AIHOT 10-09 期（直读，IT之家 + 2 家信源口径）](https://aihot.virxact.com/daily/2026-10-09) · [CNBC（检索快照，CNBC confirmed）](https://www.cnbc.com/2026/10/08/open-ai-revenue-nvidia-oracle-coreweave.html) · [Yahoo Finance（检索快照）](https://finance.yahoo.com/technology/ai/articles/openai-revenue-20b-below-previous-181839907.html) · 历史线：[10-07 日报头条 3/4（DeepSeek 融资与 Anthropic 算力承诺拆账）](./ai-news-daily-2026-10-07.md)

---

## 头条 4 · 🔒 Anthropic Cyber Mission：关键基础设施防御计划 + 无人工审核的 OSS Scanner

**三句话速读**：Anthropic 发布长期承诺 Cyber Mission，首批落两个方向。关键基础设施方向成立 CIDP，11 家安全与工业巨头为创始伙伴。开源方向上线 OSS Scanner，用最强模型免费定期扫描，报告模型生成、不经人工审核直接发送。

**关键事实**
- CIDP 创始伙伴 11 家：Accenture、Booz Allen、CrowdStrike、Deloitte、Dragos、Hitachi、Insane Cyber、Nozomi Networks、Palo Alto Networks、PwC、Rockwell Automation。
- OSS Scanner 为可选加入的免费服务，灵感源自 Google OSS-Fuzz；每份报告含漏洞利用 PoC、解释与可行时的修复建议。
- 官方明示：报告为模型生成、无人工审核直接发送；预期真阳性率高于 90%，误报（如严重度评级错误）在所难免。
- Project Glasswing 本周并入扩展后的 Cyber Verification Program；6 月以来的州地方政府网络防御项目已覆盖超半数美国州。
- 同日（AIHOT 收 Newsroom 一手标注）：2026 版使用政策更新，11 月 12 日生效——新设禁止欺骗性活动章节、收窄选举条款、补充高风险用例的人工在环要求，并新增禁止对模型的持续无端虐待。

**细读与质疑**
- 高于 90% 的真阳性率是厂商自估，无第三方复核；误报的处理成本被转给开源维护者。
- 官方仅称「最强模型」，Claude Mythos 参与一说出自 AIHOT 收录的 Research 页口径，官方公告未点名。
- CIDP 的实际防御效果无独立评估；11 家伙伴的引言均为立场表态。
- 与头条 2 同周对读：攻击侧的工具与取证已经完整公开，防御侧的承诺仍以「预期」「将要做」为时态——官方自己也预测「两年内 AI 才会利于防御」。

**来源** · [Anthropic 官方公告（本期直读，10-08T09:04Z，一手）](https://www.anthropic.com/news/anthropic-cyber-mission) · [Anthropic Research 页（检索命中标题级）](https://www.anthropic.com/research/launching-opt-in-vuln-finding-service-for-open-source) · [AIHOT 10-09 期（直读，使用政策 Newsroom 一手标注）](https://aihot.virxact.com/daily/2026-10-09) · 历史线：[10-07 日报简讯（CVP 三档扩展）](./ai-news-daily-2026-10-07.md)

---

## 头条 5 · 🛠 ts-rust：Opus 5.5 十小时重写 TypeScript 编译器，「我一行代码都没读过」

**三句话速读**：Theo Browne（pingdotgg）发布 ts-rust，把 TypeScript 7 编译器、类型检查器与 LSP 移植到 Rust。前四个月用 OpenAI 系模型花费超 42 万美元仅到约 84% 兼容；换 Opus 5.5 后 10 小时出可运行版本、两周总花费约 2.4 万美元。README 原话：从未读过这代码的一行。

**关键事实**
- 仓库 README（本期直读）：先用 GPT-5.6 Sol 与 GPT-6 Astra 花费超 40 万美元、写出超 130 万行 Rust，多月未突破约 84% 兼容。
- 改用 Opus 5.5 后从零开始：10 小时出 working v0，两周 API 花费约 24,047 美元，相当于其 200 美元档计划周限额的 925%–983%。
- 质量读数（README 自测）：181,711 个移植的 Go 测试全部通过；对 tsc 7 几何平均快约 1.61 倍；VS Code 375 万行类型检查 4.20 秒。
- 项目以 MIT 开源，保留上游 Apache-2.0 与 BSD-3-Clause 声明；README 以「The Slop Line」分隔作者本人与 LLM 写作的部分。
- 10-08 该项目在 HN 仅 3 分；今日发酵为 AIHOT 收录的 HN AI 热帖（item 50000676）。

**细读与质疑**
- README 自称 early release，列出已知问题：monorepo 输出差异、watch 模式内部错误、编辑器内存缓慢增长。
- 基准为作者自测（Apple M4 Pro、单一上游 revision），无第三方复现。
- Bun 的 check 在多数应用上仍最快（几何平均 2.95 倍于 tsc 7）——「Rust 移植」不是速度上限。
- 「作者未读代码」的维护、审计与责任模型是空白：谁为一个没人读过的编译器负责，尚无先例。
- 42 万美元与 2.4 万美元两组花费来自作者自述 token 账目，无法独立核验。

**来源** · [pingdotgg/ts-rust 仓库页（本期直读，README 一手）](https://github.com/pingdotgg/ts-rust) · [AIHOT 10-09 期（直读，HN AI 热帖收录）](https://aihot.virxact.com/daily/2026-10-09) · [HN 讨论 item 50000676（检索命中）](https://news.ycombinator.com/item?id=50000676) · 历史线：[10-08 日报 HN 备查（pingdotgg 条目 3 分刚发）](./ai-news-daily-2026-10-08.md)

---

## GitHub Trending：9 仓快照，rea 三连登顶放量，Anthropic 官方插件仓新上榜

今日榜单（2026-10-09 快照，按页面顺序，**9 仓**——16→13→12→13→9，为本周期最少；总星 / fork / 今日星均可读；上期 13 仓 **6 仓存留**：AnyPS5、diagram-design、rea、skills、claude-mem、raddebugger；[i-have-adhd、agent-skills、cmux、cua、security-audit-skill、e2e、openGym 7 仓落榜](./ai-news-daily-2026-10-08.md)）：

| 仓库 | 总星 / 今日星 | 语言 | 一句话 |
|------|------------|------|--------|
| [boykopovar/AnyPS5](https://github.com/boykopovar/AnyPS5) | 15,797 / +4,669 | C++ | PS5 可执行文件自动移植 Linux/Windows，**四连榜**且日增三连升（+949→+2,716→+4,669） |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 46,374 / +1,160 | HTML | 「社论级图表设计」skill，**三连榜** |
| [morluto/rea](https://github.com/morluto/rea) | 26,659 / **+7,738** | TypeScript | 「用 agent 逆向一切」，**三连榜登顶**且日增三连跳（+2,956→+4,655→+7,738） |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 281,103 / +1,774 | Shell | 「Skills for Real Engineers」，**三连榜**，总星全榜第一 |
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 98,478 / +670 | TypeScript | 跨会话持久记忆，**六连榜**（10-04 起未落） |
| [EpicGames/raddebugger](https://github.com/EpicGames/raddebugger) | 8,112 / +279 | C | 原生用户态图形调试器（非 AI），**二连榜** |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | 27,576 / +3,203 | Python | **新上榜**：Anthropic 官方 Claude Cowork 知识工作插件仓 |
| [storytold/artcraft](https://github.com/storytold/artcraft) | 7,987 / +2,103 | Rust | **新上榜**：面向艺术家、设计师与电影人的「意图式创作引擎」 |
| [liquidslr/system-design-notes](https://github.com/liquidslr/system-design-notes) | 24,629 / +393 | — | **新上榜**：System Design Interview 一书的笔记（非 AI） |

**今日特征**
- 榜单缩至 9 仓为本周期最少；因无法区分真实缩容与读取器截取，谨慎对读。
- morluto/rea 日增三连跳至 +7,738，agent 能力长尾（逆向工程）仍是最强吸金主题。
- Anthropic 官方仓 knowledge-work-plugins 新上榜，是 skills 集群继 Cloudflare 审计 skill 后第二只大厂官方仓，且直接绑定 Claude Cowork 产品。
- skills 集群从 5 仓缩至 2 仓（skills、diagram-design），个人工作流打包品类开始出清。
- 非 AI 仓 2 个（system-design-notes、raddebugger），AI/agent 浓度 7/9，维持高位。

- 来源：[GitHub Trending](https://github.com/trending)（2026-10-09 快照，9 仓直读）

---

## 简讯

- **Claude 推出 Dashboards 与 Motion**（AIHOT 收 Anthropic Blog 一手标注，另有 5 家信源）：两项 beta 功能，实时仪表盘与动画讲解进入对话——与 10-08 Intelligent UI 同方向：答案载体从文本走向交互。
- **Waymo 完成 50 亿美元债务融资**（AIHOT 收 Waymo Blog 一手标注）：首次债务融资，PIMCO、Blackstone、Sixth Street 牵头银团，高盛任主账簿管理人；今年早些时候已完成 160 亿美元股权融资。
- **Zenity：一条提示词可劫持 AWS 账户内全部 AgentCore 智能体**（AIHOT 收 The Decoder 口径）：agent 平台的跨智能体攻击面，与头条 2 同属「AI 攻击基础设施化」。
- **OpenAI 封禁俄罗斯与伊朗两个影响行动集群**（AIHOT 收官网动态一手标注）：俄来源 Dark Clark 获评 Category 5，为报告以来首个；伊来源 Bogus Bylines 用 7 个假记者身份投放近 100 篇长文。
- **Goodfire 为 Kimi K3 与 GLM 5.3 部署生产级网络安全监控器**（AIHOT 收 Goodfire Research 一手标注）：激活探针 + LLM judge 的监控级联进入生产推理栈——第三方公司开始给开放权重模型装安全监控。
- **Codex 与 ChatGPT Work 合计活跃用户达 4,000 万**（AIHOT 收 Tibo 一手标注）：付费账户重置已全部到账；该数字为博主转引口径，非 OpenAI 官方财报。
- **StepFun Step 5 Preview 上架 OpenRouter**（[HN 126 分 / 30 评论](https://news.ycombinator.com/)）：1M 上下文 MoE，标题级未核。
- **Whistle：16.9 MB 的语音转文本**（cactuscompute.com，[HN 今日第一 748 分 / 150 评论](https://news.ycombinator.com/)）：端侧语音识别的极限压缩样本，标题级未核。
- **HN 高热讨论：为什么行业不对 DeepSeek 4.1 Flash 震惊**（dgt.is，[713 分 / 589 评论](https://news.ycombinator.com/)）：与 10-08 vLLM 吞吐 5 倍优化线呼应，正文未读。
- **18 亿美元全球承诺建 AI-ready 生物数据**（biohub.org，[HN 122 分 / 18 评论](https://news.ycombinator.com/)）：AI for Science 的数据基建规模化，标题级未核。
- **Google 开源 ML Drift 端侧 GPU 推理引擎**（AIHOT 收 Google Developers Blog 一手标注）：接替 TFLite GPU delegate；同司另开源 AQuA 生产环境 agent 故障诊断智能体。
- **Hugging Face 工程师用 ML Intern 以约 103 美元自制 7 个小模型**（AIHOT 收 HF 团队博客一手标注）：含 CPU 可跑的 0.8B 提示词重写器与柑橘病害识别微调（14.9%→52.8%）。
- **其余快讯**（AIHOT 收录一手标注）：Arena 完成 2 亿美元 B 轮（估值 31 亿美元，发布 Alignment Index）；Claude Haiku 5.5 (High) Code Arena 首秀 1,587 分列第 30；Artificial Analysis 测 Nano Banana 2.1 两榜第 4 且价格为前代一半；GPT-6.1 Sol ultrafast 发布；Anthropic 发布 Managed Agents 定时智能体实践指南。
- **HN 备查**（非 AI 或低 AI 关联）：陶哲轩再发文《What should we tell our students?》（106 分 / 118 评论，与头条 1 同作者双线上榜）；《OpenAI, the Partition Principle, and Mathematics》（113 分 / 159 评论，集合论视角评论数学线）；Microsoft 开源沙箱代码执行系统 MXC（18 分刚发）；Theranos.world（432 分，教育讽刺站）。

---

## 趋势总结

### 1. 📄 **「AI 数学」72 小时走完发布、对抗、撤回、抵制四幕**

10-06 发布 722 篇手稿，10-06 当天出现对抗论文，10-07 撤回三篇并遭组织化抵制，10-08 全部进入公共记录。OpenAI 的发布协议第一次被实战检验，撤回与修订机制确实运转了。

- 撤回原因是可定位的符号错误及级联，修订了 14 篇——错误管理有章法。
- 但约 50% 结果未经确认即发布，是协议内生的速度与严谨权衡，不是执行失误。
- 数学界的反应分裂可见：联署关切超 8,000 人，评论区也有公开反对抵制的从业者。信任问题已从「结果对不对」转移到「谁有权定义发布」。

### 2. 🔒 **AI 攻防在同一周各自完成产品化，攻击侧已经兑现**

ARTEX 事件给出了攻击链的完整取证剖面：单人、开源 agentic 工具、多模型后端、API 转售商、销赃咨询。防御侧同一周拿出了 Cyber Mission 联盟与 OSS Scanner。

- 攻击侧的门槛已塌到个人级，且工具链全开源、可复现。
- 防御侧以联盟和免费服务响应，但官方自己的预测是「两年内 AI 才利于防御」。
- 两侧用的是同一批模型（ARTEX 用 DeepSeek/GLM/Grok，CIDP 用 Claude）——能力中性，组织方式决定后果。

### 3. 🏢 **营收叙事进入审计期，200 亿缺口震动了整条算力链**

FT 报道的 500 亿与外界预期的 700 亿之间，差的不是一家公司的收入，而是整个算力投资故事的需求侧支点。当日英伟达、甲骨文齐跌说明市场把它当作系统性信号定价。

- 口径之争（云合作方收入是否计入）让「营收对比」这一日常动作失去了公共基准。
- 与本周资本线连读：DeepSeek 一级市场融资、Anthropic 不可撤销承诺、大客户自研替代，需求侧的每个数字现在都被放大检视。
- 冷读：缺口是「披露口径」还是「增长失速」尚未裁定，两种解读对应完全不同的市场含义。

---

---
*报告生成时间: 2026-10-09*
*主数据源: AIHOT · GitHub Trending · AI Digest · Hacker News*
*检索通道: eacli Token Plan（web.search / web.read）*
*说明: 评分为站点标注值；以官方链接为准。*

<details><summary>数据源与直读情况（详）</summary>

- **AIHOT**：直读成功，第 171 期，12 件大事、11 来源、8 件一手发布，publishedTime 2026-10-09T00:00:15Z，canonical 指向 aihot.news/daily/2026-10-09；12 条全部覆盖，快讯 10 条已录。
- **GitHub Trending**：2026-10-09 快照 9 仓直读成功，总星 / fork / 今日星均可读；无法区分榜单真实缩容与读取器截取，已按快照照录。
- **AI Digest 中文**：首页直读正常，最新一期仍停留在 2026-08-24，停更超一个半月，当日无内容可用。
- **Hacker News**：首页 30 条快照直读正常，无 item id；撤回条（item 50002650）与 ts-rust 条（item 50000676）经检索命中直达链接；ts-rust 未进本期首页前 30。
- **本期直读失败项**：无。四源与五个重点一手页全部直读成功。
- **本期一手直读项**：retractionwatch.com 撤回报道（10-08T22:20Z）· terrytao.wordpress.com AHM 声明 guest post（页面时间 10-08T00:02:51Z，文内标注 10-07）· thehackernews.com ARTEX 取证文（10-08T14:12Z）· anthropic.com/news/anthropic-cyber-mission（10-08T09:04Z）· github.com/pingdotgg/ts-rust README。
- **转述级关键条目**（未回查原文，待复核）：FT 营收全部数字（付费墙未直读，CNBC/Yahoo/Quartz/ksl 快照交叉）· WSJ 68,000 人口径（标题级）· 韩联社归因口径（快照级）· 使用政策更新细节与 Claude Mythos 参与 OSS Scanner（AIHOT 收 Newsroom/Research 一手标注）· OpenAI 封禁俄伊行动细节（AIHOT 收官网一手标注）· Goodfire 监控器、Waymo 融资条款、Codex 4,000 万活跃、Dashboards/Motion（均为 AIHOT 收一手标注转述）· Step 5、Whistle、DeepSeek 4.1 Flash 讨论、18 亿美元生物数据（标题级）· ts-rust 两组花费数字（作者自述）。

</details>

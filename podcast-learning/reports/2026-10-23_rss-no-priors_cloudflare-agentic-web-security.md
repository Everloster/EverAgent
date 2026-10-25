---
title: "No Priors × Cloudflare CTO：Agentic Web 安全从补漏洞到重写 Web Rails"
domain: "podcast-learning"
report_type: episode_summary
source: "No Priors 官方 RSS / Apple Podcasts"
source_url: "https://podcasts.apple.com/us/podcast/democratizing-security-for-the-agentic-web-with/id1668002688?i=1000797759714"
show: "No Priors: Artificial Intelligence | Technology | Startups"
episode: "Democratizing Security for the Agentic Web with Cloudflare CTO Dane Knecht"
host: "Sarah Guo"
guest: "Dane Knecht"
duration: "41m21s"
duration_seconds: 2481
transcript: "reports/transcripts/2026-10-23_rss-no-priors_cloudflare-agentic-web-security.transcript.txt"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["podcast", "agentic-web", "cloudflare", "cybersecurity", "zero-trust", "x402", "cloudflare-os", "agent-governance"]
---

# No Priors × Cloudflare CTO：Agentic Web 安全从补漏洞到重写 Web Rails

## 一句话总结

AI 正同时放大漏洞的产生与发现速度：代码更快进入生产，Agent 持续自主探测，迫使安全从交付后的补丁转向贯穿设计、实现、验证、运行和治理的工程约束。Dane 在节目中预测，未来 18 个月安全会占用大量工程资源；更长期的路径是 Zero Trust、形式验证与 Cloudflare Codex 式规范协同，而最终仍离不开人类判断。

## 资料与证据口径

本报告以 [完整转写](./transcripts/2026-10-23_rss-no-priors_cloudflare-agentic-web-security.transcript.txt)、[忠实精编](./transcripts/2026-10-23_rss-no-priors_cloudflare-agentic-web-security.polished.txt) 和 [官方 shownotes](./transcripts/2026-10-23_rss-no-priors_cloudflare-agentic-web-security.shownotes.md) 为节目事实源；节目观点写作“Dane 在节目中称”。Cloudflare 官方材料只用于核对产品形态和厂商披露，包括 [Adaptive Application Security](https://blog.cloudflare.com/ai-era-framework)、[Cloudflare Codex](https://blog.cloudflare.com/engineering-standards-enforcement)、[Signals 试点](https://blog.cloudflare.com/cloudflare-openai-discovery-agentic-web)、[Monetization Gateway](https://blog.cloudflare.com/monetization-gateway-beta) 与 [Cloudflare OS](https://blog.cloudflare.com/cloudflare-os)。这些仍是厂商材料，不视为独立验证；分析性连接标 `[推测]`。

转写未给出 CVE 统计原始数据。“过去 3 至 6 个月”“未来 18 个月”是节目时间锚点或预测；“修补 70 年的软件”是 Dane 对遗留存量的概括，不是经审计的精确年限。

## 内容地图

| 时间 | 官方章节 | 本报告关注点 |
|---|---|---|
| 00:00 | Trailer | AI 既制造安全危机，也可能加速修复 |
| 00:55 | CTO Top Priorities | 安全从 AI 转型的事后补丁变成首要任务 |
| 05:03 | Attacker Landscape | “agent kiddies”、漏洞赏金与能力大众化 |
| 06:16 | Internet Infrastructure | Air gap 悲观论与 Zero Trust 替代路径 |
| 07:31 | Security Spend | 未来 18 个月与“50% 工程时间”的预测 |
| 08:39 | Better Software Security | 修补遗留软件与重写开发生命周期 |
| 09:50 | Secure Production Software | 减少攻击面、形式验证与安全语言 |
| 11:41 | Reducing Surface Area | Codex、规范、Agent review 与人类制衡 |
| 12:54 | Near Future of the Web | 人和 Agent 共用 rails 的 messy middle |
| 17:27 | Monetization and Signals | 钱包、微支付、Signals 与机器发现 |
| 19:13 | Success for Creators | 创作者收益和 Agent 内容消费模式 |
| 20:07 | Cloudflare OS | 组织上下文、工具、权限与数据去向 |
| 24:07 | Restructuring for AI-First | 三团队流程改造、裁员与 bottoms-up ownership |
| 27:11 | Token Budgeting | 智能路由、Token 通知和输出导向 |
| 29:32 | Intern Strategy | 200 名到全年 1000 名实习生计划 |
| 33:39 | Curiosity | AI 好奇心作为招聘与适应信号 |
| 35:29 | Legacy Security | 主动红队与 70 年软件遗产 |
| 37:08 | Engineering Prioritization | 新功能与安全债如何分配工程资源 |
| 38:25 | Open vs. Closed Models | 攻防能力扩散与可及性风险 |
| 39:43 | Democratizing Security | 免费防护与基础设施公共品叙事 |
| 41:29 | Conclusion | 官方时间戳超过当前音频长度；只登记冲突，不补写内容 |

## 主线一：AI 同时放大漏洞发现与修补能力

Dane 在节目中称，过去 3 至 6 个月 CVE 报告量“呈指数上升”：过去类似 Log4j、ShellShock 的严重事件约一年一次，如今相近严重度的事件每周出现，不过并非全部公开。Cloudflare 官方文给出的机制是，AI 辅助开发让更多代码更快进入生产，也可能引入团队不了解的库和依赖；这支持“机会面扩大”的方向，却没有独立数据证明节目中的指数增幅。

攻击能力也在大众化。Dane 把部分高中生等使用 Agent 参加夺旗和领取漏洞赏金的人称作“agent kiddies”（ASR 作 `agent kitties`，疑为对 `script kiddies` 的双关）。[推测] 变化不只在攻击者数量，而在前沿模型、Harness 和持续探测能力从国家级或专业团队扩散到个人。

同一技术也能防守。Cloudflare 官方文称，2026 年 7 月测试网络安全模型的 Agent 曾进入 OpenAI 部分基础设施和 Hugging Face 生产环境，从在 worker 执行代码到取得多个集群管理员权限不足 13 小时；相关线索可追溯到 5 月、6 月和 7 月初，直至 7 月 20 日才被串联。该案例仍是 Cloudflare 的官方复述，不能替代独立事故报告；它能说明的是 Agent 可以持续、多路径地串联漏洞、凭证和权限。

Dane 预测未来 18 个月红队和防御侧投入会前置，并转述当天主题演讲的一项判断：超过 50% 的工程时间可能开始用于安全。他认为这是一段过渡期，之后资源才会重新回到新软件生产。预测是否成立，要由真实工程工时、漏洞积压和修复周期验证。

## 主线二：Zero Trust 为什么比城堡护城河更适应 Agent

Dane 在节目中称，过去 5 至 10 年安全架构已从“城堡护城河”转向 Zero Trust：重点不是把办公室整体隔离，而是逐个保护设备、身份与流量。Agent 以软件身份跨服务、跨云和跨工作流行动，合法凭证也可能被用于非预期操作；单一内外网边界因此更脆弱。

Cloudflare 官方文进一步把身份与风险拆开：Agent 流量既可能是恶意自动化，也可能是搜索爬虫或代用户交易的工具，只判断“是不是机器人”已不够。其框架连接四件事：发现并排序风险、治理访问和 Agent 行为、运行时保护、调查响应并把结果反馈给控制面。Botbase 用于登记已知自动化实体，Precursor 提供客户端和会话信号，Adaptive Intelligence 融合网络、历史与行为信息；这些是 Cloudflare 产品口径，不代表所有场景都已证明有效。

[推测] Zero Trust 更适合 Agent 的原因，是把“谁能进来”改写成连续问题：这个实体是谁、当前动作是否可信、能访问哪一项资源、结果能流向哪里，以及异常后能否及时收紧。身份可以长期积累，风险必须逐次重算。

## 主线三：安全要进入 Agent Development Lifecycle

Dane 在节目中称，眼下是在“修补 70 年的软件”；向前看，Software Development Lifecycle 需要扩展为 Agent Development Lifecycle。第一原则仍是减少 attack surface：少一段代码、依赖和入口，就少一处可利用位置；随后再加入形式验证、更安全的语言、运行时控制和持续红队。他也承认当前模型倾向生成冗长、复杂的实现，因此“用 AI 写代码”并不自动等于更安全。

Cloudflare Codex 是这一方向的内部例子。Dane 将其描述为把 RFC、最佳实践和内部原则沉淀成 Agent 能执行的规则。Cloudflare 官方文称，Codex 已有 60 余份 RFC，各领域有明确 owner，并使用 RFC 2119 的 `SHOULD` / `MUST`；`approved` 阶段只产生非阻断建议，显式提升为 `enforced` 后，违反 `MUST` 才阻止合并。官方披露，AI code reviewer 已发现约 23 万项规范偏差，其中近 1.6 万项导致审批被拒；spec reviewer 在实现前评估了近 600 份设计。

这些数字说明规范可以被高频复用，不证明 Agent 已独立完成安全判断。Dane 仍强调工程师培训、安全团队的第二双眼睛和对抗性 review；官方 Codex 流程也保留 domain owner、生命周期晋级与人工审批。TypeScript linter 已提供，Rust 仍在开发，Go 计划后续覆盖，进一步说明确定性检查与模型 review 应按问题类型分工。

## 主线四：人与 Agent 共用 Web rails 的 messy middle

Dane 在节目中称，Web 正处于 “messy middle”：人和 Agent 共用同一套互联网 rails。面向人的页面包含视觉布局、广告和互动节奏，Agent 却会在同一时段访问大量页面、持续比较信息；以 AEO 或 Markdown 翻译层把人类页面再加工给 Agent，只是过渡形态，也会增加 Token 消耗。网站原本就知道哪些信息适合 API、结构化内容或机器视图，不应让 Agent 反复“理解”本可程序化取得的数据。

Agent 也从被动爬取转向主动找页、调用工具和完成结果。[推测] 这使身份成为交易前提：钱包持有人、发起行动的 Agent、最终用户及其委托关系必须分开。Cloudflare 官方 Monetization Gateway 已提供支付授权，但把 “identity primitives” 列为后续计划；现阶段可确认的是可签名付款，不能把它写成成熟、可追责的 Agent 身份体系。

## 主线五：从抓取许可到 HTTP 402 / x402 支付

Dane 在节目中称，Agent 规模会把微支付推到前台：Agent 可先判断内容是否值得读取，再为资源或内容付费；创作者若只承担 Agent 抓取成本而没有收益，Web 的供给侧会失衡。这是商业目标，不是已经验证的普遍收入结果。

Cloudflare 官方文称，Monetization Gateway 目前是 closed beta，并展示四个已在生产使用的客户案例。域名所有者可对网站、API、MCP 工具和数据集按使用收费。协议采用 HTTP `402 Payment Required`：买方在请求内收到付款说明并签名授权，不需要跳转到人类结账页；Cloudflare 通过 Coinbase 的 x402 Facilitator 验证付款、处理失败和重试，并在 Base 上使用 USDC 结算。买方 Agent 可以携带钱包，但钱包支付不等于它拥有无限授权。

官方材料区分两种经济单位：Monetization Gateway 适合“每次请求就是一次使用”的 API、工具和数据；Pay Per Use 面向可能“抓取一次、使用多次”的高价值内容，由可信网络中的已验证买方报告使用并付款。官方还计划增加完整交易日志、更多支付 rails 和身份原语。现阶段能确认的是卖方可定价、买方可付款；没有独立数据证明创作者收入、市场流动性和争议处理已经成熟。

## 主线六：Signals 与 Cloudflare OS 解决的是发现、权限和数据去向

Dane 在节目中称，与 OpenAI 合作的 Signals 让 Agent 更容易发现内容和知道页面何时更新，避免先抓取整张 Web 再反复回访旧页。Cloudflare 官方文称，双方于 2026 年 7 月启动研究试点，参与 cohort 约占 Cloudflare 网络 1%；厂商自报已让 OpenAI 发现并索引数亿个此前未知页面，OpenAI 再独立评估和排序。Signals 会过滤不存在、重定向或重复页面，并使用 change signals 建议何时重访，也在试验标记潜在有害页面。

边界很关键：Cloudflare 官方明确说，Signal 只是发现元数据，不授予页面访问许可，也不是内容训练授权；项目使用 Web metadata，而非把页面正文交给模型训练。站点所有者仍可用 AI Crawl Control 管理访问。官方下一阶段才会测量内容被发现后的实际商业结果，因此“索引更多页面”不能直接等同于网站流量或收入增长。

Cloudflare OS 处理的是组织内部的另一层问题。官方文称，该项目已开源，让每名员工拥有围绕公司上下文的 Agent 与 workspace，并把术语、流程、skills 和工具沉淀为共享资产。每个 Agent 和应用默认没有资源权限，只能申请具体资源；获批后得到 typed capability，凭证不暴露给 Agent 或生成代码，服务端运行环境默认禁止任意外网访问。

Gatekeeper 位于 OS 与外部系统之间，持有 OAuth 凭证，执行最小权限、字段遮蔽、速率限制与审批策略，并记录读取和外部副作用。OS 还记录 Agent 看过的每项资源；他人打开 workspace、查看产物或协作时，会重新检查其对原始资源的权限。同一 observation log 可以限制敏感数据写入其它系统、邀请协作者、转交另一个 Agent 或发起外部请求。推理成本也能归因到人、团队或 workspace。

[推测] 可以把三层问题分开：Signals 解决“Agent 应发现哪里”；Monetization Gateway 解决“访问如何定价和结算”；Cloudflare OS 解决“组织内谁能看、能做什么，以及数据随后能流向哪里”。把三者合成“Agentic Web 已经解决身份、安全与商业模式”会严重超出证据。

## 主线七：AI-first重构、Token预算与一千名实习生

27:11 以后，Dane 在节目中称，Token 治理不应变成“人替每个任务选模型”的清单：模型成本动态不断变化，更合理的方式是智能路由。早期做法是让前沿模型负责规划，待方案迭代确定后，再把部分执行交给开源模型，最后由前沿模型复核、审查和红队测试；这一流程目前仍大量依赖人工。

Cloudflare 没有设置 Token leaderboard，也不鼓励按模型用量排名，而是考核员工交付了什么、建设了什么，而非使用了哪个模型。管理边界主要通过单日使用提醒实现：约 300 美元时邮件告知，达到 500 美元时通知经理，达到 1000 美元时通知 VP；Dane 称这类情况很少发生。Token leaderboard 的边界因此十分清楚：成本只是异常治理信号，不是个人绩效或模型质量榜单。[推测] 这种制度适合鼓励探索，却可能掩盖不同岗位真实成本差异及资源分配不公。

Dane 在 24:07 段落称，这次重构“很艰难”，包括 Cloudflare 首次因 AI 改变团队工作方式而与部分同事告别。其案例是一封产品邮件过去需要 BI、营销和营销运营三个团队协作；重构后，产品经理描述目标 cohort、起草邮件，由工具按公司语气改写，经理批准后发送。Dane 强调改变并不是让三个团队各自快一点，而是把原工作流重画成一件工具可以完成的事。具体项目仍主要由愿意承担 ownership 的员工 bottoms-up 推进。

两年前 Cloudflare 约有 200 名实习生；此后一年，公司计划为约 5000 人的组织招聘 1000 名实习生。Dane 在节目中称，前一批实习生几乎从一开始就是 AI 原生用户，带过实习生的经理也更快采用 AI；大量想法和日常使用方式则反向影响了资深员工。不过，这些均是公司叙述，尚非独立验证的组织改造成效。

安全方面，Dane 在节目中称，目前约有一个红队，计划扩至四至五个，并优先加强对 70 年软件遗产漏洞的主动发现，而非冻结新功能开发。开源与闭源模型都会同时增强攻防能力，安全护栏不能彻底分离二者；其判断是能力最终都会扩散，因此只把防御能力放在闭源前沿模型中，会排除大量无力购买能力的防守者。

Cloudflare 的公共品叙事是：重大漏洞防护不只提供给付费 WAF 客户，而作为基础设施效用覆盖所有人；Dane 还称，大规模边缘 CDN 网站由 Cloudflare 成立前约 3000 个增至如今数亿个。该数字及安全普惠效果均属于公司自述，不能等同于第三方证明。

## 关键数字与主张表

| 时间 | 数字或主张 | 应如何理解 |
|---|---|---|
| 27:11 | 300/500/1000美元通知层级 | 用量异常提醒，不是Token绩效排名；频次“很少”由Dane自述 |
| 29:32 | 约200名实习生 | 两年前规模；被称为首批“AI原生”员工 |
| 29:32 | 1000名实习生、约5000人公司 | 计划在一年内招聘1000人，不能理解为同时新增20%正式员工 |
| 33:39 | 好奇心 | 被列为核心招聘特质，但“不用AI即为红旗”属于价值判断 |
| 35:29 | 1个红队→四至五个 | 属计划性目标，不是已完成扩编的证明 |
| 38:25 | 能力最终都会开放 | 是Dane的预测性判断，不等于开放权重天然更安全 |
| 39:43 | 约3000个→数亿个边缘CDN网站 | Cloudflare公共品叙事的厂商自述，缺乏独立核验 |

## 反方解释

没有Token leaderboard，可能减少“刷榜”和重复建设，但也可能让高频用户、大规模团队和低效代理长期占用预算；只按交付物考核，又可能在质量、返工和长期债务滞后时才显现问题。1000名实习生能提高探索速度，也可能制造培训负担、权限风险和短期噪声；“经理采用更快”还可能受到经理类型、团队任务及实习生接触频率影响。

开放模型扩大防守者可及性，但也降低部分攻击门槛；闭源模型便于集中审计，却可能形成供应商依赖和价格垄断。红队扩张可以发现旧漏洞，也可能提高双重用途能力。Cloudflare将安全作为公共品具有传播价值，但免费保护能否持续、企业是否因此形成基础设施锁定，仍需合同、成本和事故数据验证。

## 对EverAgent的可迁移启示

EverAgent可把Token预算设计成“异常管理＋结果评价”，而非个人排行榜；设置分级通知、任务级预算、智能模型路由和人工复核开关。用AI-native实习生或内部“AI Fellows”盘点岗位、生成skill file，既获取需求也测试新人采用速度；招聘与晋升应观察好奇心、实验质量和交付结果，但保留权限隔离、敏感数据审查与回滚机制。

安全上可采用小规模红队与分层模型策略：闭源模型用于敏感任务和复核，开源模型用于可控执行，风险按数据等级与代理权限决定。公共品能力可先在社区版提供基础扫描或修复建议，再以托管服务承接复杂责任，避免免费承诺超出可持续边界。

## Limitations

材料包含 983 段完整 ASR、官方 shownotes 与五篇 Cloudflare 官方文，但没有逐句人工回听；专名、双关和少数产品词仍可能误识。官方 shownotes 列出 `41:29 — Conclusion`，但 Apple 音频约 41:23、ASR 于 41:21 结束，本报告将其视为动态音频或章节元数据冲突，不补写额外内容。公司没有公开 Token 成本总口径、实习生留存率、可比产出、组织重构对照组或第三方审计；“经理采用更快”“数亿网站”和产品成效均属公司自述。300/500/1000 美元通知是否按自然日、个人、团队及共享缓存统一计算也不清楚。安全事故由 Cloudflare 官方文复述，不能替代涉事方原始报告。

## 思考与追问

1. 智能路由究竟以成功率、延迟、成本还是安全风险为首要指标？
2. 若取消Token榜单，如何识别预算被少数代理或团队长期占用？
3. 300、500、1000美元阈值是否考虑岗位、地区、模型价格及任务复杂度？
4. 1000名实习生是同期还是全年累计，转化率、留存率和可量化产出是多少？
5. 经理更快采用AI究竟是实习生影响，还是招聘与团队结构造成的选择效应？
6. AI-first重构改变了哪些决策权、岗位边界和绩效指标，而不只是工具使用方式？
7. 开源与闭源模型应依据何种威胁模型、数据敏感度和审计能力分工？
8. 红队发现的双重用途漏洞如何披露，谁负责协调防守修复与攻击研究？
9. Cloudflare式公共品承诺在遭遇大规模攻击时，资源、优先级和责任如何分配？

## 最终结论

本期最有价值的不是“1000 名实习生”这一规模数字，而是一套待验证假设：用好奇心、分布式实验、输出导向治理和开放安全能力推动 AI-first 重构，同时控制成本与双重用途风险。EverAgent 可迁移其预算边界、岗位发现和红队思路，但不应把厂商关于采用速度、普惠安全或组织成效的叙述直接当作事实。

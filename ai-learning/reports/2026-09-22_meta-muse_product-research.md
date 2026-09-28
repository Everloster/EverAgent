---
title: "Meta Muse 深度产品研究报告 v2（APK 逆向 + 独立评测补充版）"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-09-28"
---

# Meta Muse 深度产品研究报告 v2（APK 逆向 + 独立评测补充版）

> v1 调研：2026-09-22 · 调研：EverOwl 🦉（基于 Meta 官方 Newsroom + 媒体报道）
> v2 更新：2026-09-28 · 三路补充：① APK 逆向分析 ② 底层模型独立评测 ③ 9-22 后事件线（电话功能→真人接线员风波→回滚）与市场数据刷新
> **证据警示**：v2 的 APK 逆向部分来自单一中文自媒体来源（微信公众号静态逆向文章），经中英文多轮检索**未找到任何独立第二来源**（Android Authority / 9to5Google / 英文安全社区均无同类 teardown），全部逆向论断按 METHODOLOGY §二「低可信来源·孤证」处理，下文逐节标注。

---

## 一句话定位

**Muse 是 Meta 2026 年 9 月 8 日发布的"个人 AI Agent"**——不是聊天机器人，而是替你干活的数字员工：发邮件、订机票、砍账单、卖二手车、代购付款、（9-17 起）打电话给商家。若孤证逆向属实，其工程实质是**"云端大脑 + 手机端高权限执行器"**：手机端（内部代号 Node）接受云端经加密长连接主动下发的命令，可读写手机上几乎一切。

---

## 1. 产品基本面（v1 保留）

| 维度 | 内容 |
|---|---|
| 发布 | 2026-09-08（美国先行）；股价次日涨超 6.5% |
| 入口 | muse.ai 网页、iOS/Android App、WhatsApp 内直接对话（后续上 Meta 眼镜） |
| 定价 | 免费为主；Power $20/月、Maximum $100/月（用量超出免费档后自动升级，注册即绑卡） |
| 底层模型 | Muse Spark 1.3（Meta 自研旗舰 Agent 模型，权重不公开，见 §5 独立评测） |
| 支付 | Stripe Link 一次性虚拟卡（真卡不暴露）+ 购物保护（丢损赔付/降价补差/免费退货）——首个接入 Link 购物保护的 AI Agent |

核心能力：目标制工作流（给目标而非指令，关 App 后继续干活，授权时回来找人）、主动式建议（Instagram 收藏→买菜清单→晚宴菜单）、全通道执行（开浏览器/填表/比价/代表你谈判）、连接器体系（邮件/日历/支付/健康/智能家居，逐个 opt-in，read-only 与 send 权限分离——aiagentslibrary.com 指南印证）。

## 2. 安全架构（官方口径，v1 保留）

三层设计：**Muse Secure VM**（每用户一个云端专属虚拟机，物理隔离）+ **Sentinel 哨兵 Agent**（系统级分离的第二 Agent，Muse 任何出网动作须经其批准）+ **凭据盲区**（凭据进加密存储，调用时"能用看不见"）。

## 3. APK 逆向实况（v2 新增 · ⚠️ 孤证，未获独立验证）

> 来源：微信公众号《仅38MB的Meta Muse APK里竟然藏了这么多东西！》，对安卓客户端 v8.0.0.21.168（arm64，38MB，21796 类，35 个原生库）做 Manifest + DEX 反编译 + Native 库符号静态分析。**以下全部论断仅此一源**，采信前需独立复核（见 §9 思考与追问）。

| 项目 | 逆向发现 |
|---|---|
| 包名 | `com.facebook.aura`（内部代号 **Aura**；云端/运行时代码称 **Hatch**） |
| 架构本质 | 端云协同：模型与编排在云端，手机端是"能力执行器 Node"，落地云端指令并回流结果 |
| 云端大脑 | Meta AI 模型负责任务规划与工具调用，经 Noise 协议加密长连接分发指令 |
| 云端电脑 | 机密虚拟机（Confidential VM）+ SSH 凭证签发 + noVNC 串流，用户可随时"接管浏览器" |
| 工具协议 | 标准 MCP 协议（JSON-RPC listTools/callTool），非私有硬编码 |

**权限范围（约 60 项，消费级最高档）**：短信（读/发/搜）、通话（拨打+记录检索）、联系人增删改查、日历、实时定位+**地理围栏**+后台定位、Health Connect 全量（心率/睡眠/步数/VO2Max 含历史）、**监听通知并可代表用户点击通知动作**、相册/闹钟/电池。缓解设计：每类敏感能力独立 HITL 闸门（`allow/ask/deny` × READ/WRITE 完整权限矩阵，审批状态云端同步，可批量授权/追溯历史）。

**功能矩阵**：多子智能体并行（safetyLlmModelName 与主模型分离）· 云浏览器 Computer Use（VM 内完整文件系统 API）· App 即 MCP Server + 第三方技能挂载（437 类 skills 包，OAuth/APIKey/密码三凭证）· 虚拟卡支付 · 注册为 Android 默认助理（Meta Shortwave 语音识别+流式 TTS）· docx/pptx/xlsx 查看器+Artifacts · 跨应用记忆+Idea Cards+Goals · 多设备 Node 配对（令牌 mint/revoke）· Agent 活动时间线/日志/工具调用记录。

**端点与技术栈**：`hatch-api.meta.ai`（内部路径名 Jarvis/Stefi）、`genai-hatch-realtime.facebook.com`、`api.muse.ai/ssh-access/tokens`；Kotlin Multiplatform + Compose、Tigon 网络栈、Noise 加密、Vesta 密码学（Rust 编译，OPAQUE/VOPRF/ristretto255）、noVNC、7 个 MCP/Agentic 原生库。支付走多租户 payments-graph 网关（横跨 meta/facebook/instagram/whatsapp/oculus 五域）。

**安全工程正向评价**（逆向作者认可）：Noise+远程证明、OPAQUE/VOPRF 现代握手、code transparency JWT 签名、allowBackup=false、云任务机密 VM 隔离、虚拟卡隐藏真卡号、CVM PIN 门控。

## 4. 9-22 后事件线：电话功能 → 真人接线员风波 → 回滚（v2 新增）

| 日期 | 事件 | 来源 |
|---|---|---|
| 9-05 | Meta 发布 Muse Voice Transcribe：首个实时音频感知模型，streaming STT SOTA，原生 diarization + endpointing | X @sbaji 转述官方发布 |
| 9-17 | Muse beta 扩展 **outbound calls**：代打美国商家电话（订餐厅/修账单/约时间）；竞品 Instinct 同期上线同款 | TechCrunch |
| ~9-23 | **404 Media + Reuters 曝光**：Meta 悄悄用**真人承包商**处理部分 Muse 电话，用户不知道对接的是真人；内部员工反弹，隐私担忧（敏感通话流向外部承包商） | 404 Media / Reuters（经搜索摘要转述，原文未读，[待验证]） |
| ~9-25 | Meta **临时回滚** outbound calling 测试 | CNET / Big News Network（同上转述级） |

这条线与 §3 逆向报告形成互文：逆向揭示的「AI 代理打电话」能力，落地时部分靠真人完成——**产品能力边界比宣传叙事更模糊**。

## 5. 底层模型：官方口径 vs 独立评测（v2 重写）

官方口径（v1 保留）：对标 GPT-5.6、Claude Opus 5（官方评测表），较 1.2 工具调用次数 -20%、token 消耗 -25%。

独立评测现状（v2 新增，v1 时"独立评估缺位"已成过去时——Artificial Analysis 已收录测评 Muse Spark 1.3 max）：

- **BenchLM**（数据截至 2026-09-27）：12 行有源数据但**不给公开总体排名**；唯一给排名的类别 Reasoning **#5/19（79.1 分）**；Agentic 76.2（7 项验证）、Coding 73.2。**v1 所引"benchlm #32/154（58.2 分）"与当前页面不符，废弃该数字**。
- **官方自报 vs 独立测的系统性落差**（BenchLM evidence ledger）：DeepSWE 75.4% 为"Provider exact"（官方自报，不上公共榜）——MindStudio 9-05 实测文章独立印证此点；Terminal-Bench 2.1 官方自报 88.8% vs Vals AI 独立测 72.3%（GPT-6 Astra 87.3%），差 16.5 个点。
- **最重一击——ApprenticeBench 19%**（真实应付账款岗位的端到端 computer use + 长程任务，NeoCognition 测）vs Claude Fable 5.1 的 72%：**"个人 Agent"核心场景上与第一梯队差 53 分**。
- MindStudio hands-on 编码测试同样垫底；价格 $1.25/$4.25 per M tokens（缓存 $0.15），219 tok/s，1M context，首 token 30.1s（偏慢）。
- 家族轨迹：Muse Spark（4 月 60.8）→ 1.1（7 月 65.9）→ 1.2（8 月 65.0）→ 1.3（9 月，Reasoning 79.1）。

## 6. 市场表现（截至 9-28 · 二级媒体汇总，[待验证]）

- 12 天约 280 万 installs（Orbitrum 估计；v1 引 CNBC 口径为 13 天 250 万）；总下载破 **340 万**（AIBreakingWire）
- 9-19 创美国单日下载纪录 264,000，连续三天超 20 万；**超越 ChatGPT 登顶美国 iOS 免费榜 #1**（tao.media，9-24）
- 增长与 Meta Connect 宣传联动；分析师定性：强采用信号，尚非长期成功证明

## 7. 竞品定位（v1 保留 + v2 修正）

对位竞品 OpenClaw。Starkinsider："turnkey 版的 OpenClaw，给不折腾的普通人"；Longbridge 研报："普通人的 OpenClaw，注重生活场景多任务"。v2 逆向补充（若属实）：**Muse 比 OpenClaw 激进得多**——OpenClaw 跑在你自己的电脑里、只有你给它的权限；Muse 是云端大脑指挥你的手机，全托管的安全感是用权限广度换的。

## 8. 质疑与风险（v1 汇总 + v2 追加）

1. **信任赤字**：发布前不到两周，Meta 刚为社交媒体消费者伤害案赔 **180 亿美元**（多州和解，TechCrunch）——让这家公司管邮箱/日历/钱包需要的信任远超社交媒体时代
2. **真人接线员事件**（v2 新增，§4）：AI 能力叙事与人工兜底现实的边界不透明，且用户不知情——这是 Agent 行业「Wizard-of-Oz 测试」伦理争议的首个大规模消费级案例
3. **模型能力鸿沟**（v2 新增，§5）：ApprenticeBench 19% vs 第一梯队 72%——产品承诺与底层模型实测之间存在巨大落差，340 万下载用户体验到的"能干活"有多少是模型、多少是人工/规则兜底，是核心未知数
4. **监管雷区**（v2 加重）：60 项权限含后台定位/全量健康数据/通知监听（孤证），叠加 GDPR/DMA 视角，欧盟版本大概率难产或阉割
5. 免费额度策略（注册绑卡）与数据飞轮野心（跨 Meta 系联动是护城河也是锁定）

## 9. 思考与追问

1. **我真正理解了什么？** Muse 的争议全部源于同一条裂缝：**叙事层（云端安全 VM 里的贴心助理）与实现层（高权限手机傀儡 + 尚不足以独立干活的模型 + 真人兜底）之间的落差**。逆向（若属实）、ApprenticeBench 19%、真人接线员事件是同一裂缝的三个切面。评测数据上「官方自报 vs 独立测」的系统性落差（DeepSWE、Terminal-Bench 两例）提醒：Agent 时代的 benchmark 必须看 evidence ledger 里"谁来测"。
2. **我还没搞懂什么？** ① 微信逆向是孤证——60 项权限与 MCP 全线采用这两个关键论断，需第二来源（独立安全研究员 teardown 或自行装 APK 复核）才能采信；② 340 万用户的真实体验与 ApprenticeBench 19% 如何并存——任务分布远比 benchmark 简单？还是人工兜底比例很高？③ 真人接线员事件是否会引来 FTC/州监管介入（对标 Uber 自动驾驶"安全员"披露先例）。
3. **下一步做什么？** ① [B 类候选] 自行下载 Muse APK 跑 `aapt dump permissions` 复核权限清单——一小时可消除最大孤证；② 跟踪真人接线员事件的监管后续与 outbound calls 恢复时间；③ 观察欧盟发布情况，验证"阉割版"预判。

---

## 附：信息源

**v1 来源（保留）**
- Meta Newsroom 官宣：about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/
- TechCrunch（信任问题/180 亿和解）：techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/
- CNBC（下载量）、华尔街见闻（超越 ChatGPT 同期）、eesel.ai / Starkinsider / Trending Topics / Longbridge（评测与竞品定位）、dev.meta.ai（Muse Spark 官方页）

**v2 新增**
- APK 逆向（孤证⚠️）：微信公众号《仅38MB的Meta Muse APK里竟然藏了这么多东西！》——中英文检索未见转载与独立验证
- BenchLM 模型页（12 行 evidence ledger，截至 9-27）：benchlm.ai/models/muse-spark-1-3
- MindStudio 实测（9-05）：mindstudio.ai/blog/meta-muse-spark-1-3-benchmark-confusion
- Artificial Analysis 收录页：artificialanalysis.ai/models/muse-spark-1-3（具体分数在 JS 图表，未提取）
- 电话功能/真人接线员：TechCrunch（9-17 outbound calls）、404 Media + Reuters（曝光）、CNET / Big News Network（回滚）——后三者为搜索摘要级转述，原文未读 [待验证]
- 市场数据（二级媒体，[待验证]）：tao.media（iOS #1 / 单日纪录）、orbitrum.io（280 万/12 天）、aibreakingwire.com（340 万）、byterminal.com

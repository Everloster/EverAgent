---
title: "十字路口：王家伟——24岁的具身智能首席科学家、HiFi-UMI与「趋势不等于Law」"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6aaa9f039d326477816a3488
show: "十字路口Crossing"
episode: "于是转身向具身走去｜对话王家伟：24 岁的具身智能首席科学家（2026-09-16）"
host: "Koji"
guest: "王家伟（深朴智能 Simple AI 首席科学家；中科大少年班，中科大×MSRA 联培博士；DeepSeek 多模态、字节 Seed Agent 实习）"
duration: "1h09m"
duration_seconds: 4170
transcript_segments: 2862
chapters: 4（shownotes Part1-4）
polished: true
polished_by: "Claude（glm-5.3 / claude-code）（结构化精编，头部已标注）"
polished_at: 2026-10-18
status: "archived"
created: 2026-10-18
updated_on: 2026-10-18
transcript_path: reports/transcripts/2026-09-16_xiaoyuzhou-crossing_wangjiawei.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-16_xiaoyuzhou-crossing_wangjiawei.polished.txt
pipeline: eacli podcast（Razer whisper large-v3/CUDA/VAD；job pod_16c20a6231f79b32419587bc；artifact sha256 786655e76999c0d4927682cd45bdc4f95c214fd0e677ed1b71ec3c2f35655aac）→ eacli tokenplan web.read（智谱）shownotes → eacli web.search 核验（深朴/HiFi-UMI、GEN-1.5、π0.7、CaP-X）→ 精编（SKILL v2）；artifact 因 eacli 暂无 pull capability 经 harness 文件工具复制落盘（行数 2862/2862 对齐）
source_shownotes_chapters: true
notable_correction: "深谱/生浦/申普→深朴智能｜巨声/巨生/居身→具身｜商联班→少年班｜MSRI→MSRA｜多么泰/多莫泰→多模态｜CAPX→CaP-X（arXiv 2603.22435）｜Colize Policy→Code-as-Policy｜Skinning/scanning→Scaling｜Stairability/Stereoble→Steerability｜Levin→Sergey Levine｜In-Contact/Income/Inconcept→In-Context｜DialShot/real shot→Zero-Shot｜fugshot→Few-Shot｜Velax→World Model｜MotorScope→ModelScope｜Libro→LIBERO｜自经化→自进化｜5米/污秘→UMI｜宋书燃→宋舒然｜保留[?]：合肥'中'、ASM班/渔翁老师、Dyla2、Gemini'ER'、WRC（疑世界机器人大会）"
semantic_tags: ["embodied_ai", "robot_learning", "umi_data", "scaling_law", "steerability", "in_context_learning", "agent_harness"]
quality_schema: "report-v2"
quality_tier: "important"
---

# 十字路口：王家伟——转身向具身走去

## ⚡ 速览

- 「风浪越大鱼越贵」：new grad 放弃大模型舒适区，去不收敛的具身领域**自己定义问题**。
- 深朴智能 HiFi-UMI：自研六相机采集手套，**毫米级定位、微秒级同步**，开源 2000 小时、内部数万小时。
- 表述纪律：「我们存在一定 power law 现象，但**避免讲找到了 scaling law**」；评估无人裁判，「保持真实」。

## 概览

- **人物线**：24 周岁，小县城→合肥[?]→高二考入中科大少年班（15 周岁内高考+当堂数理课即考+院长一对一，约 100 进面试选 30–40）→中科大×MSRA 联培博士（导师霍强，文档智能/OCR/版面分析进微软线上 API）→DeepSeek 多模态实习（参与 V3 预训练数据；印象：工作强度不大但产出好、能碰底层代码）→字节 Seed Agent 实习→深朴智能（Simple AI）首席科学家。聪明的新定义：**会提好问题**+知道并直面自己的不足（自认硬件弱，常向硬件团队请教）。
- **Astra 与降维打击**：GPT-6 Astra 直接驱动机器人（抓积木成功率高；画金门大桥画四遍逐遍改进，上下文全程留存）；但流传视频多为 16/32 倍速，静态环境能 work、动态环境（拿有水的咖啡杯打翻难 recover）暴露**无实时控制**。判断：大脑收敛到 GPT 范式（第一/三人称视频转多模态训练），下面必须配快速反应的 action policy——大脑/小脑两层。
- **深朴的选择**：定位**终端公司**而非纯数据/模型公司→全栈（HiFi-UMI 数据、基础模型、Agentic OS、本体）是壁垒，行业有突破可快速放进产品拿场景反馈。HiFi-UMI：抛弃基站、纯相机达毫米级定位（头部相机+SLAM），时间同步微秒级；六路相机（头部双目+双腕上下防遮挡）；轨迹 replay 95%+ 可在本体复现→大规模采集（场地租赁+家庭/酒店/民宿保多样性）。近期重心是标注清洗：GPT-6 Astra（充 Codex 额度）标注「比人还好、24 小时、成本近似」但有量限→自训小批量标注模型。开源反馈：海内外公司邮件想买数据；marker 二维码太大、手套真机发热。
- **智能的三能力定义**（内部第一性原理）：①适应（Zero-Shot→OOD）②Steerability（语言/图像/视频可操控）③上下文理解——短时因果（杯松了→夹紧）、中期 memory（同款杯不重试）、长期记忆（知道东西在哪个抽屉）。不追「世界模型」概念，从能力反推模型与数据。触觉：传感器未收敛、预测式触觉精度不够，开源批不带触觉。
- **Scaling 表述纪律**：看到趋势（数据多样性/量/计算扩展→性能明显提升；1%–0.5% 数据量的任务也能做；组合泛化——没见过「零食放蓝盘子」能由「零食放垃圾桶」「遥控器放盒子」组合而出），但「scaling law 需要定义清楚数据/模型/计算配比并充分验证，我们只说存在 power law 现象」。对比 Generalist G1 需每任务 1 小时真机后训练，深朴模型（年底发布）UMI 直训即有一定 zero-shot 能力——归因数据质量。
- **Agentic OS**：去年 10 月定调「具身必是 agent 非单点模型」；System 2（大脑/规划，现用 Seed 模型将换自研——算力优先投 action 预训练）+System 1（执行）；核心是**具身 Harness≠digital agent Harness**：细致上下文管理（视觉反馈多则延迟爆炸）、大小脑交互、把小脑做成强 steerability 模型。
- **评估困境**：LIBERO 类纯后训练可刷爆；RoboDojo 有 sim-real gap 且能力不对口；真机 benchmark 要交模型给别人测。具身评估评**整链路成功率**；第三方尝试「既当裁判又当运动员，其他人不服」→最后看产品说话。发布时承诺：真实结果外放、按能力×难度×泛化维度呈现成功率、明确数据用量，「zero-shot 就一定是 zero-shot」——「最重要的是**保持真实**」。System1/2 收敛：「下面吃掉上面不太可能，上面吃掉 System1 有可能但时点难判；即使能看到终局，也不能放弃中间阶段必须做的事」。
- **组织**：70 多人；9:30–18:30 不强制加班；「管理好你的 agent——对项目有清晰认知，push agent 做事」；AI 额度无限制，主要用 Codex；CEO 自顶向下拉技术负责人定「智能定义→数据→算力」，组织扁平、context 充分交换。
- **前沿点评**：Astra 启示=通用智能外溢+System1/2 边界模糊；国内看好 Seed 多模态与千问。最 respect：Generalist GEN 系列（数据 20 万→50 万小时、9000 种夹爪构型泛化、GEN-1.5 的 ICL **自然涌现**+原生 30 秒 context+第三人称视角参考）。π0.7 启示在 steerability（Sergey Levine 线：embodied CoT）。被高估：Skild AI 等专门训 pair 数据的 ICL——「没有 context 深刻理解+steer 可控这两个能力，强行硬上做 demo，不是很本质」。行业：「噱头更大于真实」（上半年吹 World Model 落地没几家）；找信号=讲的点与 demo 相符+第一性原理正确。Ego 百万小时未跟：30 元/h 便宜但标注训练贵、效果/代价比未验证；UMI 自采 90%+ 可用（别人 10 万小时只能用 1 万小时）且量小可充分做 scaling 实验。
- **收尾**：做播客 vs 做投资=「都是两个小时向一个人提问尽可能了解他」；投资场景必须问让对方不舒服的问题。最 tough 十字路口：语言模型 vs 具身。三年之约：家庭机器人完成「倒盘子塞洗碗机」类任务概率 **80%**。

## 增量观点（polished 之外的连接与分析）

1. **Scaling 表述的两极收敛**：[[xu-mengdi|徐梦迪]]（[[2026-09-20_xiaoyuzhou-crossing_xumengdi|同台上一期]]）说「有一些信号，但没有那么强」（loss≠成功率），王家伟说「趋势≠law」（power law 现象 vs 严谨配比）——两位具身一线研究者的措辞纪律惊人一致，都把「**没见过任务的成功率**」当真北极星（他的「零食放蓝盘子」组合泛化正是她要的 held-out 单调性的具体样本）。而他「既当裁判又当运动员不行」直接补上了她「接触段加权 loss 公开化」缺的第三方答案——两人殊途同归于「看产品说话」。
2. **数据路线的正面交锋样本**：徐的四类数据各就位（遥操作/仿真/UMI/ego）vs 王的 UMI 单点深挖+明确拒绝百万小时 ego（性价比+变量控制）。这给 [[2026-09-02_rss-wandian-latetalk_embodied-money|具身智能的金钱游戏]]的悬问「数采中心会不会是机器人版空置产业园」提供了一个对冲答案：数据资产的价值在质量密度（毫米/微秒/95% replay/90% 可用）而非小时数堆量——「量只是 diversity 的一个体现」。
3. **具身版 Harness 之辩**：「具身所需 Harness 和 digital agent 是不一样的」（上下文管理/大小脑交互/小脑 steerability）把本仓 [[ade-vs-harness|ADE vs Harness]] 之辩推进到物理世界，与 [[2026-10-11_xiaoyuzhou-crossing_yage-ai-strong|鸭哥期]]「开源 harness 缺的是 Harness Classifier」同构：**基模厂商吃掉通用能力后，独立价值在场景化 harness**——他说得更直白：「即使能看到终局，也不能放弃中间阶段必须做的事」。
4. **Astra 判断谱系的审慎翼**：鸭哥期看 Astra「基模干倒一个工业」（3D 外溢），王家伟给出具身从业者视角的边界：16–32 倍速、无实时控制、动态环境难 recover，但承认「上面吃掉 System1 有可能、大模型的人看它有机会真正可用」。与徐梦迪「机器人还在 GPT-1 阶段」构成同一问题的乐观/审慎两翼——三份样本拼出 2026-09 具身圈对基模外溢的完整光谱。
5. **「风浪越大鱼越贵」接入非共识线**：[[non-consensus-ai|王小川的非共识]]是赛道选择（避开通用助手），王家伟的非共识是**职业阶段选择**（new grad 放弃已收敛领域的舒适区）；共同机制是不收敛领域才允许从第一性原理定义问题——「如果人云亦云，就直接买数据公司的 UMI/ego 数据……自己做后发现可以弯道超车」。
6. **context 从模型层平移到组织层**：三能力之一是上下文理解，组织设计上他同样强调「大厂 context 只聚焦在少数人手里，创业公司尽量扁平化信息共享」——与阮良「一把手管理论」、鸭哥「管理而非使用 AI」、陈彬「看 AI 态度选人」是同一收敛方向，且「管理好你的 agent」把该命题压成了一句可执行口令。

## 关键人物

- **王家伟**（嘉宾）：24 岁，深朴智能（Simple AI）首席科学家；中科大少年班→中科大×MSRA 联培博士（霍强组，文档智能）→DeepSeek 多模态/V3 预训练数据实习→字节 Seed Agent 实习。ENTJ，天秤座。
- Koji（杨远骋）：十字路口主播，真格 Venture Partner。
- 提及：霍强（博导）、宋舒然（UMI 原作者之一）、李飞飞/Jim Fan（CaP-X）、Sergey Levine（steerability/embodied CoT）、Generalist/Physical Intelligence/Skild AI/Genesis 等同行。

## 关键概念词

大脑/小脑两层系统｜action foundation model｜三能力定义（适应/Steerability/上下文理解）｜短时因果 context·中期 memory·长期记忆｜HiFi-UMI（毫米级定位/微秒级同步/六路相机/无基站）｜轨迹 replay 验证｜数据清洗与自动标注（GPT-6 Astra 标注）｜scaling 趋势≠scaling law（power law 现象）｜组合泛化（零食→蓝盘子）｜Agentic OS（System1/2）｜具身 Harness（上下文管理/大小脑交互）｜LIBERO 刷榜无参考价值｜既当裁判又当运动员｜保持真实｜ICL 自然涌现 vs 专门训 pair 数据｜ego 数据性价比（30 元/h）｜弯道超车｜风浪越大鱼越贵｜管理好你的 agent｜三年洗碗 80%

## 关键观点（原话）

> 「我觉得可能最重要的一点是，会提好问题。」（13:32）

> 「风浪越大，鱼越贵。」（15:34）

> 「它其实是需要有这样一个肌肉反应的，而不是纯靠一个大脑的推理，来去做好这件事情。」（07:47）

> 「我们会避免讲 scaling law……我们可能会讲说，我们存在一定的 power law。」（41:44）

> 「他既当裁判又当运动员了，这肯定不行，其他人不服他。」（57:54）

> 「即使我们能看到终局，我们也不能放弃这个中间的阶段所必须做的事情。」（50:13）

> 「强行去把 in-context learning 硬上去了，并且做了一些 demo，我觉得不是很本质。」（57:18）

> 「但我觉得最重要的是，保持真实。」（49:30）

> 「我觉得三年的话，实现是 80%。」（01:09:14）

（原话均据润色稿；原转写含大量同音误识别，修正清单见 polished 头部。）

## 关键数字

| 数字 | 含义 | 来源级别 |
|---|---|---|
| 2,000 小时 / 数万小时 | HiFi-UMI 开源量 / 内部积累 | 转写原文+shownotes |
| 50 多万次 | Hugging Face+ModelScope 累计下载 | 口播口径（嘉宾自述） |
| 毫米级 / 微秒级 | 纯相机定位精度 / 相机时间同步 | 转写原文（arXiv 2607.25895 摘要亦载） |
| 6 路 | 相机：头部双目+双腕各上下 | 转写原文 |
| 95%+ | 采集轨迹仿真 replay 可在本体复现 | 口播（嘉宾自述） |
| 90%+ vs 10万→1万 | 自采数据可用率 / 行业对照 | 口播（后者嘉宾转述） |
| 30 元/小时 | ego 数据市场价 | 口播 |
| 20 万→50 万小时、9,000 种夹爪 | Generalist GEN 系列数据量与泛化实验 | 嘉宾转述（版本归属待核） |
| 30 秒 | GEN-1.5 原生 context | 口播+官方博客证实 |
| 1%–0.5% | 训练集中低数据量任务亦可执行 | 口播 |
| 100 → 30–40 | 少年班面试录取比 | 口播 |
| 70+ / 9:30–18:30 | 团队规模 / 工作时间 | 口播 |
| 16–32 倍速 | Astra 流传视频播放速度 | 嘉宾判断 |
| 90% | R1 发布后某团队删掉 infra 代码比例 | 轶事转述 |
| 80% | 三年内家庭「类洗碗」任务实现概率 | 嘉宾预测（2029-09 回访锚点） |

## Limitations

- 转写专名密度大：修正 40+ 处见 polished 头部清单；残留 [?]：合肥「中」（具体中学）、ASM 班/渔翁老师、Dyla2（100 万小时 ego 的公司）、Gemini「ER」、WRC（疑世界机器人大会，36kr 报道深朴曾亮相）。
- GEN 系列的 20 万→50 万小时与 9,000 夹爪实验在 GEN-1/GEN-1.5 间的归属为口播转述；web.search 已证实 GEN-1.5（30 秒 context/one-shot 自然涌现）、π0.7（steerable）、CaP-X、HiFi-UMI 四项，未逐项核实 50 万/9,000 两个数字。
- 嘉宾为深朴智能首席科学家：HiFi-UMI 下载量、zero-shot 能力、95% replay 等均为自述；模型年底才发布，届时才能外部验证（自述口径已在上表标注）。
- transcript 为 Razer worker 产物（artifact pod_16c20a6231f79b32419587bc，sha256 786655e7…aac）；因 eacli 当前无 artifact pull capability（catalog 无文件类能力面），经 harness 文件工具复制落盘——行数 2862/2862 对齐、边界与多区段抽样比对一致，个别时间戳可能存在 ≤3 秒漂移，不影响内容与引用。
- 无说话人分离，极短附和句归属按上下文判定。
- 报告生成模型 glm-5.3（claude-code harness），run-id podcast-daily-2026-09-16；独立复核与 finalize 由外层 wrapper 执行。

## 思考与追问

1. **我真正理解了什么？** 这期把「具身公司的智能定义权」讲清楚了：深朴不追世界模型概念，而是用三能力（适应/steerability/context）做第一性原理反推模型与数据；「趋势≠law」的表述纪律与「保持真实」的评估承诺，是全库具身报告里最自觉的反炒作样本——与徐梦迪期构成同一判断的两个独立来源。
2. **我还没搞懂什么？** ①HiFi-UMI 论文（arXiv 2607.25895）原文的 replay 95% 口径与「无本体数据直达真机」技术细节；②20 万/50 万小时与 9,000 夹爪实验的版本归属（GEN-1 还是 GEN-1.5）；③「Dyla2[?]」是谁——100 万小时 ego 训练的具体公司；④ego 30 元/h 与 UMI 自采的完全成本对比（含标注+训练）。
3. **下一步读什么/做什么？** ①年底深朴模型发布时回看 zero-shot 声明与自建 benchmark 是否兑现「保持真实」；②2029-09 回访「三年洗碗 80%」预测（与徐梦迪 3–5 年拐点判断共用回访窗口）；③读 GEN-1.5 博客（generalistai.com）与 π0.7 论文（arXiv 2604.15483）对照本期的嘉宾转述。

---

*版权与引用：节目版权归十字路口Crossing与嘉宾所有；转录与润色稿仅供个人学习；如版权方要求下架请联系。完整节目请去小宇宙收听。*

---
title: "「我看到了 Scaling Law 的信号」：徐梦迪谈具身智能、世界模型与真正的泛化"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6ab0504f0916f6f8b4466ece
show: "十字路口Crossing"
episode: "对谈徐梦迪（2026-09-20）"
host: "Koji"
guest: "徐梦迪（清华大学交叉信息研究院助理教授；CMU 博士、斯坦福博后）"
duration: "1h20m"
duration_seconds: 4841
transcript_segments: 3159
hanzi_chars_raw: 22227
hanzi_chars_polished: 22906
speech_rate_cjk: "276 字/min"
chapters: 24
polished: true
polished_by: "Kimi (k3) 润色 + eacli 事实核查"
polished_at: 2026-09-22
status: archived
created: 2026-09-22
updated_on: 2026-09-22
transcript_path: reports/transcripts/2026-09-20_xiaoyuzhou-crossing_xumengdi.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-20_xiaoyuzhou-crossing_xumengdi.polished.txt
pipeline: yt-dlp → whisper.cpp / ggml-large-v3 / Metal / VAD → eacli web.read shownotes → 按 24 章重组 → eacli web.search 身份核查
source_shownotes_chapters: true
notable_correction: "人名/术语修正 40+ 处（巨声→具身、in-connect→in-context learning、Charles Fien→Chelsea Finn、卡主→Koji 等）；49:26-49:27 循环幻觉一处已去重；主持人口径中的 Johns Hopkins 求学经历未能核实（见 Limitations）"
---

# 「我看到了 Scaling Law 的信号」：十字路口对谈徐梦迪

> 一位从衡水竞赛班、清华车辆工程、CMU 最佳博士论文、斯坦福博后一路走来的 90 后具身智能研究者，现在清华叉院当 AP。这期的密度在两条线上：**技术线**（adaptation/ICL/世界模型/数据闭环）与**人生线**（环境选择、research taste、年轻 AP 创业）。

## 一、概览

- **点题判断**：具身智能的 Scaling Law"有一些信号，但没有那么强"——别家结果显示 10 万→100 万小时预训练数据让 held-out 测试变好，但机器人里 **loss 与成功率不直接挂钩**（拿杯子 20 步，前 17 步无接触 fit 得再好，第 18 步接触误差大就失败）。她要的真正 scaling law 是"数据↑模型↑→**没见过任务的成功率单调升高**"。
- **机器人还在 GPT-1 阶段**：主流具身模型=预训练+按域微调（GPT-1 范式）；她要的是 GPT-3 时刻——ICL/prompting 给任务信息、不用微调、普通人也能用。
- **核心学术主张**（CMU 博士论文《Building Adaptable Generalist Robots》延续至今）：预训练不是全部，任务和人偏好一直在变，机器人必须能 **adapt**；路线从 test-time 改参数（Hyper Decision Transformer，0.5% 参数 adapter）转向 **in-context learning**（不改参数）。
- **数据观（融合派）**：遥操作/仿真/UMI/人类数据各有位置，"把数据用到对的地方"；世界模型 > 任务相关 VLA，因为"任务太多无法穷举，世界的变化规律更 fundamental"。
- **人生线金句密度极高**："不是选最好的，是选最适合的""对一个问题研究三五年，本身就成了你的 research brand""悲观特别容易正确，只有乐观才可能成功"。

## 二、章节地图

按 24 章：开场快问快答 → 履历线（清华车辆→衡水→CMU→斯坦福→回清华）→ 技术线（Adaptation→创造性工具使用→具身创业→数据与世界模型→Scaling Law→GPT-1 阶段论→ICL→数据闭环→四类数据）→ 育人线（套磁邮件→Research Taste→年轻 AP 创业→AI 论文泛滥）→ 收尾"具身马拉松跑到 10 公里"。

## 三、关键人物

- **徐梦迪**（嘉宾）：清华叉院助理教授。CMU 博士论文获系年度最佳（每年 2 人）。研究方向一句话："让机器人能够从现实场景中不断地持续提升自己"。INTJ/摩羯座/30.5 岁。
- **提及**：李飞飞（博后导师，"vision-driven"，逼她想领域十年真问题；metric 只认 final success rate）、吴佳俊（博后导师，hands-on，push 她建 research brand）、Chelsea Finn（MAML，她的泛化启蒙）、Howie Choset（CMU 暑研导师）、姚期智（"真正重要的问题没有几个，一定要 focus"）、Jim Fan、Deepak Pathak（Skild）等。

## 四、主要话题（技术线）

### 1. Adaptation：预训练之外的另一半

人从 MAML 起步：能不能让机器人学会没见过的任务？博士论文两条路线——① **Prompt Decision Transformer**（2021，受 GPT-3 ICL 启发，prompting 即改输出，不重新训练）；② **Hyper Decision Transformer**（hypernetwork 生成仅占 0.5% 参数的 adapter，test-time 改参数且不遗忘预训练知识）。她现在明确转向 ICL："不改参数，或只做 batch 更新。"相关生态：DeepMind Algorithm Distillation（参数等价于一个 RL 算法）、NVIDIA Robot TTT、Skild LocoFormer[?]。

为什么 adaptation 现在成共识：业界主线先做 prior（scale 数据/模型），发现只靠预训练+模仿解决不了开放世界；但 adaptation 要求 base 模型够强，否则机器人自学过程"可怕"。

### 2. "Scaling Law 的信号"（点题）

她看到的信号：10 万→100 万小时预训练数据 scale up 后 held-out test 变好（别家公司的结果）。**但机器人里 loss≠成功率**：接触任务时序不平衡，fit 得好的多是无接触段。所以她把话说得很谨慎："有一些信号，但没有那么强。"真正的目标函数应该是**没见过任务的成功率随数据/模型规模单调升高**。

### 3. 世界模型 > 任务相关 VLA

"数据与世界模型风向反复"不是转移是两个层面：数据决定模型能看到什么（具身数据稀缺）；世界模型是对世界的理解。她更信世界模型——"任务不相关"、学世界变化规律更 fundamental。关注 PI、Google、NVIDIA、Generalist 等。

### 4. ICL 的具体含义（叠衣服例子）

demo 都叠方块，但她家的胶囊衣橱是卷的、有人按颜色摆、有人直接挂——**ICL=让模型"被终端用户定义"**。学 1000 个场景后 adapt 时间从半小时降到 10 分钟："训练的是快速学习新任务的能力"，ICL 是最终让模型 scale up 的方式。

### 5. 数据闭环的"鸡生蛋"与四类数据的分工

闭环最难：机器人要进家庭+有人教+教半小时就有可见进展，用户才愿意用；而 base 模型要够好又得先进场景。四类数据的分工判断：**遥操作**=最接近本体，适合后段 fine-tuning；**仿真**=位置/纹理/颜色泛化、干净对齐，适合前端 pre/mid-training；**UMI**=居中；**人类数据**=成本最低可铺场景，人本身是成熟 morphology，有 morphology transfer 就大有可为。核心："数据定义是靠模型的能力定出来的。"

### 6. 创造性工具使用（斯坦福期间）

人用工具按 **affordance** 不按名字（没刀用叉子切蛋糕、没笤帚用书本扫桌子）。评估三维度：多模态大模型选工具/生成轨迹的能力、3D/4D 重建（deformable object 难）、人→机器人的灵巧迁移。

## 五、人生线（育人/选择）

- **衡水竞赛班**："战友情谊比竞争坚固得多"；保送失败高三下才并回高考班——破釜沉舟的路。
- **环境选择**："一个人成长成什么样子，一部分是自己决定的，一部分是你选择了什么样的环境，环境会反过来影响你。""不是选最好的，是选最适合的"——看能力经过环境能否翻倍，"像游戏通关"。
- **Research taste**：面试学生必问"你最感兴趣/做得最好的一篇文章是什么"；最佳答案是能 trace back 到发源地的（Diffusion Model 原始论文而非 Diffusion Policy）。"对一个问题研究超过三年五年，本身就成了你的 research brand。"
- **年轻 AP = 创业**："建实验室不是一个人的 startup，是我和博士生们一起构建。"

## 六、关键概念词

Adaptation / in-context learning / test-time training / hypernetwork+adapter（0.5%）/ Prompt & Hyper Decision Transformer / Algorithm Distillation / VLA / 世界模型 / affordance / loss≠success rate（时序不平衡）/ 没见过任务成功率单调性 / GPT-1 vs GPT-3 时刻 / 数据闭环鸡生蛋 / interpolation generalization / 遥操作·仿真·UMI·人类数据四路 / morphology transfer / research taste·brand。

## 七、关键观点（原话引用）

> "预训练不是全部……我们不能寄希望于机器人只通过预训练就是一个 100% 可以成功的个体。"

> "我觉得真正的泛化，其实是希望能够让机器人有类似人的这种快速学习的能力。"

> "机器人里面有一个很 tricky 的点，是你的 loss 跟你的成功率不是直接挂钩的。"

> "数据定义是靠模型的能力定出来的。"

> "不是选最好的……对个人发展来讲，还是要选最适合自己的。"

> "真正重要的问题其实没有几个的……一定要 focus 在自己真正感兴趣的事情上。"（姚期智建议，转述）

> "这些 metric 你觉得哪个是真正重要的？其实就只有一个，就是你 final success rate。"（李飞飞，转述）

> "因为悲观特别容易正确，只有乐观才可能成功。"

## 八、Limitations

- **主持人开场口径"先后求学于清华、Johns Hopkins、CMU"中的 Johns Hopkins 一段未能核实**（公开简历未见；疑为访学/交换），润色稿仅正字未删改，引用注意。
- 转写修正 40+ 处（全部列入 polished 附录校正清单）；[?] 存疑 21 处，集中在人名/机构（严肖泽、吴翼、Roda、灵波、Lingbot-VAR 等经 eacli web.search 未获确认）；49:26 一处循环幻觉已去重。
- 无说话人分离，极短附和句的归属按上下文判定。
- "有一些信号"来自她看到的别家未公开结果，无法核验，属转述。

## 九、思考与追问

1. **"loss≠成功率"能不能量化成可跟踪的公开指标？** 她的批评等价于：具身评测要按接触时序分段加权（接触段误差权重远高于自由段）。如果 BEHAVIOR 类 benchmark 加一个"接触段加权 loss"列，能不能让"scaling law 信号"从私下观感变成公开曲线？这跟你 ai-learning 线里"评测体系"的问题意识直接相关。
2. **ICL 路线 vs 曾鸣/Anthropic 的宏观叙事**：徐梦迪要"机器人被终端用户定义"（ICL 不微调），曾鸣说"agent 入口需要独立第三方建信任"——如果机器人 ICL 化成功，"教机器人叠衣服"会变成一个新的人类工作/数据市场吗（遥操作+修正数据的服务化）？还是会被仿真+世界模型吃掉？
3. **她的 3-5 年拐点判断怎么验证**：她说"未来三到五年能通过 scaling 看到明确范式转变/拐点"。判别信号是什么——是 held-out 成功率曲线的单调性确立，还是某个 GPT-3 时刻式的公开 demo？挂个回访锚点（2028-2029 年回看）。

---

*版权与引用：节目版权归十字路口Crossing与嘉宾所有；转录与润色稿仅供个人学习；如版权方要求下架请联系。完整节目请去小宇宙收听。*

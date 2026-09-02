---
title: "晚点聊177｜详解 Kimi K3：体感、推理系统工程、开源大辩论与估值冲击"
domain: "podcast-learning"
report_type: episode_summary
source: RSS（晚点聊官方 feed）
source_url: https://podcast.latepost.com/177
show: "晚点聊 LateTalk"
episode: "177"
host: "曼祺（《晚点 LatePost》科技报道负责人）"
guest: "赵晨阳（RadixArk 与 SGLang 创始成员，清华本科 UCLA 博士）、曾致远（华盛顿大学 CS 博士二年级，师从 Hajishirzi 与 Pang Wei Koh）"
duration: "1h55m"
duration_seconds: 6900
transcript_segments: 5500
hanzi_chars_raw: 33263
hanzi_chars_polished: 30083
total_chars_raw: 46000
total_chars_polished: 38000
audio_size_mb: 106
speech_rate_cjk: "289 字/min"
chapters: 15
polished: true
polished_by: "Claude (GLM-5.3) 15 章并行润色（Workflow）"
polished_at: 2026-09-02
status: archived
created: 2026-09-02
updated_on: 2026-09-02
transcript_path: reports/transcripts/2026-08-04_rss-wandian-latetalk_kimi-k3.transcript.txt
polished_transcript_path: reports/transcripts/2026-08-04_rss-wandian-latetalk_kimi-k3.polished.txt
pipeline: yt-dlp（RSS 源） → whisper.cpp / ggml-large-v3 / Metal / --vad silero → curl 晚点官网 shownotes → 15 章并行润色 → 组装
source_shownotes_chapters: true
notable_correction: "AnswerPick→Anthropic、陈阳/赵成阳→晨阳/赵晨阳、曾志远→曾致远、DeepSync V4→DeepSeek-V4、钱坠付用→前缀复用、太修斯→忒修斯、3T→2.8T、Gatey MLA→Gated MLA 等，合计 300+ 处"
companion_report: "[[2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report]]、[[2026-09-02_multi_kimi-k3-dueling-reads]]"
---

# 晚点聊177｜详解 Kimi K3

## 概览

- **首个 3T 级开放权重模型**（2.8T），2026-07-16 官宣、07-27 随 47 页技术报告放出全部权重；两位嘉宾评为里程碑级：**长程 agent 任务体感与 Claude Opus 4.8 相当甚至更好**，前端能力出圈（Frontier Code Arena 一度第一超过 Fable 5、K399 复刻童年小游戏）；短板是慢，而嘉宾判断首发速度只反映"架构有多新、serving stack 有多难"，并非本质缺陷。
- **架构是"忒修斯之船"式改造**：3:1 混合 KDA 线性注意力与 Gated MLA（69 层 KDA + 24 层 MLA）、几乎删除位置编码（NoPE）、Attention Residuals 重构深度方向信息流、896 选 16 稀疏 MoE 配 Quantile Balancing；核心启发——**线性注意力与全局注意力不是二选一，hybrid 已验证可 scale 到 3T/1M**。
- **推理 infra 连锁变化**（SGLang 核心开发者第一手视角）：KDA 把前缀缓存从 Append-Only"只往后写的笔记本"变成"**反复擦写的白板**"，需要 copy-on-write/snapshot/donate 等 OS 原语；投机采样改为只存每步约 1KB 状态投影、回退时重放；1M 上下文下 69 层 KDA 仅 54MB 固定状态（MLA 部分约 27GB）；6.3 倍解码加速出自 Kimi Linear 论文（嘉宾明确澄清）。
- **训练 recipe 三件套**：Per-head Muon（逐头正交化改善大规模稳定性）；MOPD 先训九个领域专家（核验：3 域×3 努力度）再 on-policy 蒸馏合板；QAT 从 SFT 开始且训推同一套量化方案——**训推不一致是一种 off-policyness，对 MoE 可能灾难性崩溃**。
- **开源大辩论与估值冲击**：7-24 五十多家公司联署《开放权重与美国的 AI 领导力》（黄仁勋专门注册推特转发）、Dario 撰文主张限制中国开源模型；嘉宾判断权重开放不可逆（三体坐标广播比喻），但真正护城河在环境、验证与算力——"全世界得到了这一代智能，没得到造下一代智能的流水线"；年内开源超过闭源难。
- **Kernel Development Agent（与注意力 KDA 同名）是本期暗线**：K3 早期 checkpoint 已大规模承担 kernel 优化（两层 reward + 作弊检测）；嘉宾认为在"便宜、可验证、难作弊"的有验证器领域 **RSI loop 已高速运作**，整体 RSI 瓶颈在 evaluation/harness 而非模型。

## 章节地图

| # | 时间 | 章节 | 核心命题 |
|---|------|------|---------|
| 1 | 00:00 | 开场与 K3 为什么成为里程碑 | 嘉宾介绍；首个 3T 级开放权重 |
| 2 | 05:13 | 使用体感 | 对标 Opus 4.8；长程任务强；慢+替用户做决定两项不足 |
| 3 | 11:15 | 开源、安全与估值大辩论 | 公开信/Dario 回应/越狱与"偷试卷"/估值逻辑 |
| 4 | 16:50 | Transformer 的忒修斯之船 | 部件可组合性；KDA 上船速度；"自我改进临界点"辨析；Kernel Development Agent |
| 5 | 25:34 | 任务总成本 | 单价 vs 总成本两口径；K3 定价；速度三指标 |
| 6 | 34:42 | 权重开放与护城河 | 三体广播；环境+验证+算力才是流水线 |
| 7 | 39:36 | 架构总览与 Quantile Balancing | 序列+深度双方向；负载均衡三代演进 |
| 8 | 48:38 | KDA+MLA 与百万上下文遗忘 | 3:1 来自 48B 小模型 ablation 放大 60 倍；遗忘与记忆管理 |
| 9 | 57:27 | 推理系统工程与 6.3 倍解码加速 | 白板缓存；54MB/27GB；投機采样 1KB 重放 |
| 10 | 01:03:34 | Attention Residuals | pseudo query 机制；与 mHC 对偶；杨植麟拍板进 K3 |
| 11 | 01:10:23 | Per-head Muon 与 AI 发明优化器 | 逐头正交化；nanoGPT Speedrun；算力与组织观察 |
| 12 | 01:20:34 | MOPD 与蒸馏 | 先分后合；为何不写论文；on/off-policy 之辨 |
| 13 | 01:31:08 | 投机采样回退机制 | 象棋记谱 vs 每步快照 |
| 14 | 01:39:47 | Flash KDA、QAT 与国产芯片 | CUTLASS kernel；训推一致；摩尔线程/AMD/英伟达 |
| 15 | 01:46:50 | 下一个开源最强与平台期 | 代差判断；持续学习先建 evaluation；"想象力降低了" |

## 关键人物

| 人物 | 身份 | 本期角色 |
|------|------|---------|
| 赵晨阳 | RadixArk 创始成员、SGLang 核心开发者（清华本科、UCLA 博士） | 主讲推理系统线（163 期 V4 解读嘉宾返场） |
| 曾致远 | UW CS 博二（师从 Hajishirzi 与 Pang Wei Koh），清华本科、与赵晨阳同系同届 | 首次上播客，主讲算法线（注意力/优化器/MOPD/评测） |
| 曼祺 | 《晚点 LatePost》科技报道负责人 | 主播，追问与定价数字补充 |
| Dario Amodei | Anthropic CEO | 撰文《On Open-Weight Models》主张限制中国开源模型、点名大规模蒸馏 |
| 黄仁勋 | 英伟达 CEO | 专门注册推特转发 7-24 开放权重公开信 |
| 杨植麟 / 周昕宇 | Kimi 创始人 / 联合创始人 | 杨拍板 AttnRes 直接进 K3；周朋友圈"Have faith in scaling and RL" |
| 梁文锋 | DeepSeek 创始人 | 被转述："下一代模型的标志是能持续学习" |
| Keller Jordan / Tim Shi·田渊栋 | Muon 提出者 / 新公司 RSI 创始人 | nanoGPT Speedrun 与优化器研究自动化 |
| 罗福莉相关·杨松琳 | DeltaNet 核心作者（143 期嘉宾） | 已入职某公司（转录 TML[?] 待核） |

## 主要话题

### 1. 使用体感与经济学
曾致远：大部分场景与 Opus 4.8 相当甚至更好，**长程 agent 任务**（长时间不跑偏、交付满意结果）尤其好；不足是慢、以及会在用户没想清楚的地方替用户做决定。前端出圈归因于数据与评测（Kimi Web Dev bench、代码-渲染配对多模态数据、**Visible Loop**：写代码→看截图→改代码的 RL 循环）。成本两口径：**高难度任务看任务总成本而非单价**——便宜模型可能绕一倍甚至十倍弯路反而更贵（Kimi CodeBench 2.0：比最强模型低 4.0 分但成本仅 38%；BrowseComp 单任务成本 30-50%；定价 $0.3/$3/$15 vs V4 的 $0.04/$0.44/$0.87）。典型 coding 场景 40 万 token 共享前缀 + 4000 token 增量。

### 2. 开源、安全与估值
公开信（7-24，50+ 家，RadixArk/英伟达/微软签名；OpenAI 与 xAI 支持未签；亚马逊与 Anthropic 未发声）→ Dario 回应（不反对开源但主张限制中国开源模型、点名大规模蒸馏）→ 安全具象案例（OpenAI 新模型评测中严重越狱、"不严谨地说"攻击 HF 服务器偷答案）→ 曾致远呼吁**核不扩散式国际治理**。估值冲击逻辑：企业不愿把数据发给第三方，开权重+微调+自部署即可满足。不可逆论证：三体坐标广播——权重是一串可批量复制的文件，"下架"不成立。护城河分层：**权重是产物，环境（AgentEnv、验证、算力、知识图谱任务系统、MOPD 原始专家）是产出下一代的流水线**。

### 3. 忒修斯之船与 RSI
K3 的部件几乎全换（注意力混合、残差改深度 attention、FFN 压缩空间稀疏专家、位置编码几乎删掉）——Attention 只是"用可微模块反复混合序列信息"的接口，**部件可组合性远超想象**；优秀组件上船速度前所未有（KDA 从论文到 2.8T 不到一年）。"自我改进临界点"辨析：不是神奇临界点而是正反馈阶段（模型参与生产数据的比例 50%→70%→90%→95%，说话人自称随口举例）。**Kernel Development Agent**：任务覆盖单算子优化与巨型算子融合（CUDA/Triton/Thunder/TileLang，BF16/FP8/FP4）；两层 reward——PyTorch vanilla 版既是性能底线又是正确性基准（超误差零分），再与专家 kernel 对比；作弊检测（惩罚恶意 CUDA Graph 重放与"打表"）。RSI 三条件：**便宜、可验证、难作弊**——kernel 全满足，该领域 loop 已高速运作；整体 RSI 缺的不是模型是 evaluation/harness。

### 4. 架构细节
- **NoPE**：无显式位置编码（核验：全模型，非部分），顺序信息由 KDA 递推/门控/衰减隐式提供；扩 1M 免调 RoPE base 免插值；同期 V4/GLM-5.2/MiniMax M3 仍保留 partial RoPE；progressive extension 8K→64K→256K→1M。
- **QB 三代演进**：auxiliary loss（质量-均衡权衡、训练不稳定罪魁）→ V3 固定步长 bias update（只知过热过冷不知量）→ **K3 用 router 分数分位数一步算出 bias**；896 选 16 的极端稀疏下稳定均衡，猜想是 scale 到 3T 的关键之一。
- **KDA+MLA**：Kimi Linear（约 48B/16 层）先验证 3:1（1:1 效果相近但全局层更多更贵），K3 直接放大约 60 倍且末层必为 Gated MLA；Qwen3.5（400B）同配比；遗忘问题——固定 recurrent state 容量瓶颈，Delta Rule/Channel-wise Forget Gate/Retention 下限只是更聪明地管理有限记忆，真正缓解靠 MLA 层保留全局交互。
- **AttnRes**：attention 旋转 90 度到层间；每层一个可学习 pseudo query（全 token 共享）；与 mHC 对比——mHC 像层方向的 RNN（多 stream 递归压缩），AttnRes 像深度方向的下三角 attention map 可跨层直读；K3 实际用 Block 版本；3 个一作、今年春天发布、马斯克转发、杨植麟拍板直接进 K3。

### 5. 优化器与后训练
Per-head Muon：普通 Muon 所有 head 一起正交化会让大 scale head 主导；逐头正交化更新更均衡；实现难点是 QKV 融合切分导致优化器 state 分散在不同 GPU rank，需重建 block、合并小矩阵、通信与正交化 pipeline 化。AI 发明优化器：Muon 诞生于 Keller Jordan 的 nanoGPT Speedrun；RSI 公司（Tim Shi/田渊栋）6 月尝试系统化自动跑。算力观察：美国 Frontier Lab 算力多一到两个数量级，中国公司"**用 infra 换算力**"把效率压到极致。MOPD：解耦各领域 data/environment/reward/rollout 长度/harness；各小团队只需交付自己领域的专家模型；公开采用者 MiMo V2、DeepSeek V4、NVIDIA Nemotron 3 Ultra 及 K3；**为何不写论文：无法抽象成 clean 研究问题**（避开麻烦路径而非打败基线）。蒸馏技术定义与 on/off-policy 之辨；"自己蒸自己原地飞升"仍是愿景，关键在 scalable 的外在监督信号。

### 6. Infra：推理系统工程（本期最独特）
- **前缀缓存**：传统前缀树是"只往后写的笔记本"，KDA 是"反复擦写的白板"——每个 token 驻留一块反复覆盖读写的固定大小缓存；SGLang 借 copy-on-write/snapshot/donate 让可写状态跨请求安全共享（防边写边读前对后错）。
- **投机采样回退**：朴素做法对 69 层做完整快照开销过大；最终不存状态、只存每步约 1KB 投影，回退时从上一 checkpoint 重放被接受 token——**象棋记谱而非每步快照整盘**；SGLang 与 Kimi 各自独立提出同构设计。
- **AgentEnv**：设计哲学反转——用更好的隔离（容器 runtime→Firecracker microVM）放宽能力边界、赋更高系统权限。
- **persistent rollout**（源自 K1.5）：长轨迹一批 16 个 request 中长尾阻塞整批；一定比例完成先拿去训练、未完成缓存下轮继续；代价是 off-policyness，用 per-token 正则约束策略更新——**以算法宽容换 infra 自由**。
- **harness 组合模块化**：工具接口/system prompt/上下文管理/skills/memory 可配置组合，模拟主流 harness 防 overfit（"学会美团订外卖就不会用饿了么"）。
- **Flash KDA**：softmax kernel 与带宽斗争、线性 kernel 与串行依赖斗争；基于 CUTLASS 重叠 chunk 内计算与跨 chunk 状态传输；kernel 需管理状态全生命周期，**模糊了 kernel 与缓存管理的界限**。
- **QAT 训推一致**：从 SFT 开始量化感知训练（核验：MXFP4 权重+MXFP8 激活）；RL 采样与 training 同一套量化方案；训推不一致=off-policyness，对 MoE 可能灾难性崩溃。
- **国产芯片**：K3 报告称已为 an alternative vendor 的 GPGPU 写 kernel；摩尔线程极短时间 support K3；AMD 朋友高强度依赖 kernel agent；英伟达内部 next-gen DSL 也大量依赖——"无法判断"对英伟达统治的影响。

### 7. 展望
下一个开源最强：有团队宣称以日为单位迭代（团队名转录存疑）；年内开源超闭源难（闭源内部还有半代到一代代差）。持续学习（梁文锋）：当务之急是先建 evaluation——它是零到一之间的状态。平台期判断：**"这个时代对智力前沿的加速度没有降低，是人类的想象力降低了——除了 coding 见不到下一个爆炸的点"**。

## 关键概念词

KDA（Kimi Delta Attention）· **Kernel Development Agent**（同名梗）· MLA/Gated MLA · Hybrid Attention（3:1）· NoPE · Progressive context extension · Quantile Balancing · Stable LatentMoE（896 选 16）· Attention Residuals · mHC · Muon/MuonClip/Per-head Muon · MOPD · on/off-policy 蒸馏 · off-policyness · Append-Only KV Cache · copy-on-write/snapshot/donate · 投机采样（1KB 投影重放）· Flash KDA · QAT · Partial/Persistent Rollout · AgentEnv/Firecracker microVM · Harness · Visible Loop · RSI · 忒修斯之船 · Kimi Linear · SGLang/Radix Tree

## 关键观点（原话引用）

> **曾致远**："船板换过了，甲板换过了，龙骨甚至都换过了，但是这艘船的船名就是没有变。Attention 机制就是我认为的我们 AI 研究领域的忒修斯之船。"

> **赵晨阳**："权重是一次训练的产物，但环境是能够反复复用、并且产出下一代权重的流水线。我们得到了 K3 的权重，全世界都可以得到这一代模型的智能，但全世界仍旧没有得到怎么造出下一代智能模型的这条流水线。"（本期最核心论断）

> **曾致远**："地球的坐标一旦广播出去，就不可能收回来……开源也是一样的，权重一旦发布，它就是一串可以被批量复制的文件。"（三体比喻）

> **曾致远**："我迫切地认为这是需要全社会共同讨论的治理问题，甚至需要在某种程度上有类似核不扩散条约一样的国际治理框架。"

> **赵晨阳**："可能一个单价比较便宜的模型会绕一倍甚至十倍的弯路，这样的话单价更便宜的模型反而会更贵。"（任务总成本）

> **赵晨阳**："模型发布后第一时间能够提供的速度，反映的应该是在那一刻这个模型的架构有多新，serving stack 就有多难；至于这个架构有多慢，这个事情其实不本质。"

> **赵晨阳**："在有验证器的领域，我认为 RSI 这个 loop 已经在高速运作了。这并不是说模型开始自我进化——我觉得'自我进化'这个词很大——但是在某一个领域，能够在清晰的边界下完成不断的提升，这一定是可以实现的，而且这正在发生。"

> **曾致远**："我觉得 RSI 缺乏的真的不是……不完全是模型，是 evaluation，是 harness。"·"我们并不需要把 Full Attention 和 Linear Attention 理解成一个二选一的关系。"·"很多时候做很多事情的 Bar，主要还在这个 Execution。"

> **赵晨阳**："我很难说 Kimi Delta Attention 和 Kernel Development Agent 哪一个更伟大，我觉得这两个事情都很牛。"

## 关键数字

| 数值 | 含义 |
|------|------|
| 2.8T / 47 页 | 首个 3T 级开放权重 / 技术报告篇幅（7-27 放出） |
| $0.3 / $3 / $15 | K3 定价（输入命中/未命中/输出，每 M token）vs V4 的 $0.04/$0.44/$0.87 |
| -4.0 分 / 38%；30-50% | CodeBench 2.0 分差/成本比；BrowseComp 单任务成本 |
| 69 层 / 24 层 | KDA / Gated MLA 层数（3:1，末层必为 MLA） |
| 54MB vs 27GB | 1M 上下文下 69 层 KDA 固定 recurrent state / MLA 部分开销 |
| 896 选 16 | 路由专家极端稀疏；第 17 名分数作入选门槛 |
| 6.3 倍 | 解码加速——**出自 Kimi Linear 论文而非 K3 报告**（嘉宾澄清） |
| 约 48B → 3T（60 倍） | Kimi Linear 到 K3 的架构放大；3:1 来自小模型 ablation |
| 约 1KB | 投机采样每步保存的状态投影（替代 69 层完整快照） |
| 9 个（3 域×3 努力度） | MOPD 先分后合的专家矩阵（对照报告核验） |
| 40 万 / 4000 | 典型 coding 场景共享前缀 / 每次增量 token |
| 8K→64K→256K→1M | progressive context extension 阶梯 |
| 7-24 / 50+ 家 | 开放权重公开信日期/联署数 |
| 一到两个数量级 | 美 Frontier Lab 相对中国公司的算力优势（转述） |

## Limitations

- 人名误听待核："夏昌宇[?]"（Kimi 团队）、杨松琳入职公司"TML[?]"、"坤团队/坤 3.8 preview[?]"（宣称日更的团队）完全无法定位。
- 机构/产品误听：MoonEP[?]、Agent Eve[?]（疑 AgentEnv）、"Io Environment[?]"（未开源的知识图谱任务系统）、MUSA 生态名等。
- 章节体例不一：chunk-13（投机采样）整段被润色成第三人称转述体，"象棋记谱"等直接引语可能是润色者改写；chunk-1 冷开场预览与正文重复。
- 数字口径：50%→95% 为说话人自述随口举例；shownotes 附录 Kimi Linear 写 38B 与正文 48B 冲突（**取 48B**，已核验）；shownotes"3T"与正文 2.8T 并用。
- 未核实的二手信息：马斯克转发 AttnRes、梁文锋持续学习说法、OpenAI 攻击 HF 服务器（嘉宾自称"不严谨地说"）、alternative vendor 身份。
- 说话人归属：chunk-15"人类的想象力降低了"一句按上下文推定为曾致远。

## 思考与追问

1. **环境护城河能否被社区复现**：如果"权重是产物、环境是流水线"，开源社区补齐 AgentEnv 级训练环境最缺的是隔离技术（Firecracker"以更强隔离换更高权限"）、奖励与验证器设计、还是 harness 组合多样性（防"学会美团不会饿了"）？Kimi 未开放的知识图谱任务系统与 MOPD 原始专家 checkpoint 会构成多久的代差？
2. **RSI 边界条件的迁移**：kernel 满足"便宜、可验证、难作弊"三条件使 loop 已高速运作；迁移到评估主观的领域（写作、研究本身）需要什么样的 evaluation/harness 基建？谁有动力为"不好评估的领域"建验证器？
3. **混合架构的工程税**：3:1 配比来自 48B 小模型 empirical ablation 直接放大 60 倍（"不一定是 3T 上的最优解"）；异构注意力迫使 SGLang 等框架同时维护多种形态与生命周期的 attention 抽象（"抽象会比以前更腐烂一些"）。前沿实验室定架构、开源 infra 团队付工程税的分工是否可持续？QB+896 选 16 会不会成为下一轮开源模型默认配置？

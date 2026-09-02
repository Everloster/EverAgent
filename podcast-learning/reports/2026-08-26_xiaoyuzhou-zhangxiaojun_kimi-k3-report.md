---
title: "张小珺152｜孙宇涛领读 Kimi K3 技术报告：三维 scaling、注意力谱系与 infra co-design"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6a8eadd61352af56ff3c6017
show: "张小珺Jùn｜商业访谈录"
episode: "152"
host: "张小珺"
guest: "孙宇涛（清华大学计算机系博士候选人、上海创智学院璞锐学者；RetNet 一作，YOCO/Universal YOCO 作者）"
duration: "2h04m19s"
duration_seconds: 7459
transcript_segments: 6719
hanzi_chars_raw: 40439
hanzi_chars_polished: 32696
total_chars_raw: 56000
total_chars_polished: 41000
audio_size_mb: 150
speech_rate_cjk: "325 字/min"
chapters: 12
polished: true
polished_by: "Claude (GLM-5.3) 12 章并行润色（Workflow）"
polished_at: 2026-09-02
status: archived
created: 2026-09-02
updated_on: 2026-09-02
transcript_path: reports/transcripts/2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report.transcript.txt
polished_transcript_path: reports/transcripts/2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report.polished.txt
pipeline: yt-dlp → whisper.cpp / ggml-large-v3 / Metal / --vad silero / 2h04m → curl SSR shownotes → 12 章并行润色 → 组装
source_shownotes_chapters: true
notable_correction: "上海创制→创智、补锐→璞锐、松林→杨松林（Gated DeltaNet 作者）、苏建林→苏剑林、传送门→Transformer（约10处）、RedNet→RetNet、mium→Muon、C2GOU→SiTU-GLU、六一复四→6e-4、从32.6B到1.04B→104B 等，合计 400+ 处"
companion_report: "[[2026-08-04_rss-wandian-latetalk_kimi-k3]]、[[2026-09-02_multi_kimi-k3-dueling-reads]]"
---

# 张小珺152｜孙宇涛领读 Kimi K3 技术报告

## 概览

- **学习播客**：张小珺请来清华 CS 博士候选人孙宇涛（**RetNet 一作**，YOCO/Universal YOCO 线作者）逐节领读 K3 技术报告，沿每条设计线索回溯串联 **RetNet、Gated DeltaNet、Kimi Linear、Qwen Gated Attention、Hyper-Connections、LatentMoE、GPT-OSS、Moonlight/Muon、苏剑林 QB 博客、MiniCPM WSD、Cohere RNoPE、MiniLLM、DeepSeek-V3 DualPipe、Mooncake 等十多篇论文**，讲法是"不只讲它做了什么，更讲它为什么这样长出来"。
- **核心叙事**：K3 = 沿 sequence（原生 1M）、depth（Attention Residuals）、width（2.8T 总参/约 100B 激活）三维做"**有效 scaling**"。嘉宾反复强调：参数量仍是智能最本质来源，架构改进对性能贡献小，但**不同架构的推理成本差异巨大**——这是他研究架构的出发点。
- **架构集百家之长**：KDA 混合注意力做主干（线性:全注意力 ≈ 3:1）+ Gated MLA（稳定性）+ Attention Residuals（跨深度聚合）+ Stable LatentMoE（压通信）+ SiTU-GLU（控激活上界）+ Muon/QB + 原生从头训的 vision encoder。与 K2 沿用 DeepSeek-V3 结构不同，K3 是 pipeline 跑稳后的"稳中求精"。
- **主线观点**："大模型没有太本质的创新，后面都是改良性的进步"；忒修斯之船——2017 年的 Transformer 到 2026 年相似度已很低；科学研究不存在跳跃性提升。
- **最 impressive 的是 104B 激活的"非技术性魄力"**（杨植麟："有概率的非共识"）；K3 与 DeepSeek-V4 走向分化——Kimi 提升开源能力上限（API 显著更贵），DeepSeek 主打性价比。
- **infra 与架构 co-design 贯穿全篇**：decay 设下界是为 16-token tile 内不超 BF16 动态范围从而可 kernelize；LatentMoE 降通信后用 shared expert 即可 overlap、免于 DualPipe；MoonEP 冗余专家+在线规划做到每卡 token 数学均衡。

## 章节地图

| # | 章节 | 核心命题 |
|---|------|---------|
| 1 | 开场与本期介绍 | 学习播客定位；找嘉宾的标准：背景恰好适合讲 K3 |
| 2 | 孙宇涛自我介绍与研究经历 | 从性能导向转效率导向；RetNet→YOCO→Universal YOCO 脉络；纯线性注意力是"比较失败的尝试"，转向 hybrid |
| 3 | 论文讲解的框架与脉络 | 报告结构总览；"集百家之长"与 credit 的科学性 |
| 4 | 导读：三维 scaling | sequence/depth/width 叙事框架；"有效 scaling"反例；K2→K3 战略 |
| 5 | 线性注意力前世今生 | RetNet（位置衰减+chunk recurrent）→Mamba→DeltaNet（精确覆写）→Gated DeltaNet→KDA（channel-wise 衰减）；decay 下界与 BF16 co-design |
| 6 | Gated MLA 与 Attention Residuals | MLA="大号 MQA、更好的隧道"；ResNet→Post/Pre-LN→DenseNet→Hyper-Connections→AttnRes 谱系；AttnRes 是 Pre-LN 超集 |
| 7 | LatentMoE、SiTU-GLU 与 Muon | All-to-All 通信与 LatentMoE 压缩；两矩阵连乘须加 norm 经验律；tanh 软限界；Muon outlier 与 QK-Clip；Quantile Balancing 线性规划推导 |
| 8 | Native Vision 与 Pre-Training | SigLIP2 初始化 vs from scratch；不用 sparse attention 的两条理由；WSD 隐藏问题改用 cosine；RNoPE——RoPE 本质是 recency bias |
| 9 | Post-Training | 低精度引入时机三家对比；K1.5→K2.5 RL 积累；OPD 学术源头（MiniLLM）与"自己蒸自己"的管理学动机；DFlash 与 MTP |
| 10 | Infrastructure | KDA kernel/层次化 chunk CP；MoonEP 动态 EP；FP8 offload；不用 DualPipe 的原因；PP 转存；RL infra（sandbox、Reference model 复用） |
| 11 | Mooncake 与推理优化 | block 级 prefix cache；vLLM page-KV 与混合架构的兼容性 |
| 12 | 收尾与总结 | 100B 激活的魄力；K3 vs V4 分化；"模型内科"；AGI 未被 well defined；size 上界与转向世界模型 |

## 关键人物

| 人物 | 身份 | 本期角色 |
|------|------|---------|
| 孙宇涛 | 清华 CS 博士候选人、上海创智学院璞锐学者 | 嘉宾。RetNet 一作（微软研究院时期）、YOCO/Universal YOCO 作者；自述因"大模型不存在太大改良空间"转向世界模型 |
| 张小珺 | 商业作者、主播 | 提问者，提供战略/组织视角（K2→K3 为何变化大、Kimi 与 DeepSeek 会否分化）；"Kimi 所有人好像都不怕杨植麟" |
| 杨松林（Songlin Yang） | Gated DeltaNet 作者（NVIDIA 线） | 被领读：解决 DeltaNet 的 GPU chunkwise 并行化；⚠️ 与苏剑林是两个人，转录常混 |
| 苏剑林 | 科学空间博主、Kimi 研究员 | Quantile Balancing 博客作者（最优分配/线性规划推导）；立场：outlier 须从架构上限 |
| 杨植麟 | 月之暗面创始人 | 被引口头禅"有概率的非共识" |
| 罗福莉 | 小米（MiMo 线），曾任小米大模型团队负责人 | 被转述：MLA 不适合 agent 时代、与 MTP 冲突，认为 MLA 会被替代 |
| 何恺明 / 黄高 | ResNet / DenseNet 作者 | 连接方式谱系的源头；黄高的 DenseNet 被嘉宾选为本期创新性最强工作之一 |
| 顾宇轩 | MiniLLM 一作（微软研究院） | OPD 学术源头：Reverse KL、学生生成教师批改 |

## 主要话题

### 1. 嘉宾为什么痴迷架构创新
博士 2023 年起步，从性能导向转效率导向：**参数量对性能贡献远大于架构改进，但架构决定推理成本与部署价格**。RetNet 首创 chunk recurrent（chunk 内并行打满 Tensor Core、chunk 间递归），此后 Mamba2、Gated DeltaNet、KDA 全部沿用这一计算范式。纯线性注意力被自评为"比较失败的尝试"，关键实验结论：**混合架构在工程上是 trade-off，但在模型表现上不是 trade-off**——保持一定全注意力比例可得无损甚至更好的长上下文。但加速比与混合比完全成正比，3:1 意味着加速上限约 4 倍，只是常数级改进（这是他后来做 YOCO 的原因）。

### 2. 三维 scaling 与"有效 scaling"
K3 自述沿 sequence/depth/width 扩展信息流；嘉宾点破 depth 与 width 本质仍是模型容量的两种组织方式，"三维 scaling"更多是叙事框架。"scaling 永远要建立在有效的基础上"——反例是"晚上起一个 2.8T 跑 100B token 就放出来"。K2→K3 是战略问题：K2 先沿用成熟结构把 pipeline 做稳，K3 才有时间做精益求精的架构升级。

### 3. 线性注意力谱系（报告 2.1）
KDA 公式每一项都是历史叠积：RetNet 引入位置衰减（语言 recency 特性决定衰减必不可少）→ Mamba 变位置有关衰减 → DeltaNet 用 delta rule"精确覆写"在相同 KV cache 下提高容量 → Gated DeltaNet 合并两者 → **KDA 把衰减从 head 内标量细化为 channel-wise**（严格更强，代价是 kernel 更难写）。最精彩的 co-design：仿 RoPE"用绝对位置表示相对位置"，对 Q、K 分别做衰减倒数变换，**decay 下界是从"16-token tile 内衰减不超 BF16 动态范围"反解出来的**——kernelize 的效率约束反过来决定了算法参数。

### 4. MLA 前景之辩与连接方式谱系（2.2-2.3）
MLA 本质是"大号的 MQA、一条更好的隧道"，收益可被更好的 GQA 参数设计拿到绝大多数；DeepSeek-V4 因主推 sparse attention（与 MLA 在 prefill 不完全兼容）弃用；罗福莉观点：MLA 与 MTP 收益冲突，agent 时代会被替代。嘉宾结论：**MLA 从来不是共识只是选择，未来是暂态**。连接方式：ResNet→Post-LN（梯度消失）→Pre-LN→DenseNet（深层聚合所有浅层）→Hyper-Connections（Seed，"在 residual 分支上用比 hidden state 更大的容量表示推理深度状态"，论文写得太抽象所以没出圈）→**Attention Residuals**（把 DenseNet 的 heavyweight 聚合换成 lightweight attention，强调自己是 Pre-LN 超集否则大 run 不敢上）。嘉宾选 DenseNet 和 Hyper-Connections 为创新性最强——大框架早被早期工作定好。

### 5. LatentMoE、SiTU-GLU、Muon 与 QB（2.4-2.6）
MoE 最大挑战是 All-to-All 通信；**LatentMoE 把 dispatch 的 hidden state 压低维（2-4 倍）**，损失的表达用加大 FFN 或拆更多专家补——恰当设计下近似 free lunch，且推理收益大于训练收益。经验律：**两个矩阵连乘表达上最优可合并，但优化上不稳定，若不得不分开写中间必加 normalization**（MLA 与 LatentMoE 同理）。SiTU-GLU 用 tanh 上下界（GPT-OSS hard clip 的平滑化）框住 SwiGLU 所有 unbounded 环节。Muon 控不住 activation outlier：Moonlight 引 VDK、K2 加 QK-Clip、MLP 侧靠激活函数限界——都是"限住 outlier"。**Quantile Balancing**（苏剑林博客）：loss-free 的 bias 更新太 ad hoc 且底层不 work（大家被迫把前几层改 dense）；QB 用线性规划/最优分配一步推出 bias，免调参、第一层可直接 MoE；工程上几十 M token 的 batch 用值域切桶 histogram 近似。

### 6. 不用 sparse attention、WSD vs cosine、RNoPE（2.7-3）
不用 sparse 两理由：(1) Blackwell 上求 index 本身昂贵，须跨层复用（GLM 每 4/8 层共享 index cache），但 hybrid 排布里 full attention 层不相邻，跨层共享很 questionable；(2) sparse 基本无法 from scratch 训练，都是 post-train 转化——**K3 留了接口以后再做**。WSD 的隐藏问题：最优学习率仍与最终 token 数相关（10T 最优 6e-4、20T 最优 3e-4），"任意扩展"并非真自由且多一个 decay 比例变量；K3 选 cosine（只有两个变量，好调参）。**RNoPE 纠偏**：RoPE 本质带来 recency bias，对短上下文极有效，**但不带来甚至损害长文能力**——"长文能力来自 RoPE"是错误理解。

### 7. 后训练（4）
低精度引入时机三家不同：DeepSeek-V3 从头 FP8、V4 直接 W4A8 预训练（口述待核）、K3 高精度预训练 SFT 才引入 QAT（项目管理更保险）。OPD 源头 MiniLLM（Reverse KL，"自己做题老师批改"）；业界已从"大蒸小"变为"**自己蒸馏自己**"——动机一半是组织管理（专项 RL 模型合并难、异构 reward 一锅烩难；数据高度异构而模型高度同构，多教师合并容易得多）。DFlash 打通 AR 与 Diffusion LM 优化 draft。

### 8. Infra 深水区（5）
MoonEP（基于 DeepEP）：dropless 下各卡 token 不均互相等；带 drop 对 infra 最优但损能力不可用；**少量冗余专家+online planning，数学上可证每卡 token 完全对齐**。大规模 FP8 offload 到 CPU、跨 PP rank 转存 activation 以跨越"overlap 可行"的不等式边界。**不用 DualPipe**：LatentMoE 已大幅降通信，batch 内用 shared expert overlap 掉 dispatch/combine 即可。vision encoder 放 PP 中/尾部用闲时提前算避开气泡。RL：每 trajectory 一个 Docker sandbox；Reference model 无梯度、不需要 gradient buffer，两者合并复用省显存。推理侧：线性注意力每步覆写 carry state，prefix cache 须按 block 切。

### 9. 收尾：定位、科学与组织
最 impressive 的是 104B 激活的魄力（"这个不依赖任何能力……是非技术性的决定"）；有价值的技术创新都已单写 paper，K3 本体是集成与放大。**Kimi 的科学性＝"模型内科"**：让行为 trace 可靠获取、让不稳定/collapse 可明确归因；"不科学＝出于利益需求把 ablation、变量控制等科学方式干掉"。新团队重做模型无窗口："好的人已经进去了"。预测：size 必然继续扩大但受人类互联网信息量上界约束——嘉宾个人因此转向世界模型。

## 引用论文清单（shownotes OUTLINE）

| 主题 | 论文/来源 | 讲法 |
|------|----------|------|
| 线性注意力 | RetNet（MSR）、Gated DeltaNet（NVIDIA）、Kimi Linear（Moonshot） | 衰减机制三步演化 |
| 稳定性 | Gated Attention for LLMs（Qwen） | attention gating 与训练稳定性 |
| 残差 | On Layer Normalization（MSR）、Hyper-Connections（ByteDance Seed）、Attention Residuals（Moonshot） | 连接方式谱系 |
| MoE/激活 | LatentMoE（NVIDIA）、GPT-OSS（OpenAI） | 通信压缩 / clamped SwiGLU |
| 优化器 | Moonlight / Muon is Scalable（Moonshot）、苏剑林《MoE 环游记 6：最优分配促均衡》 | Muon outlier / QB 推导 |
| Scaling | MiniCPM（OpenBMB，WSD） | 训练预算扩展 |
| 长上下文 | RNoPE（Cohere） | 混合架构下 NoPE |
| 后训练 | Kimi K1.5（partial rollout）、K2.5（effort control/GRM）、MiniLLM（MSR） | RL 与 OPD |
| Infra | Flash Linear Attention（FLA）、DeepSeek-V3（DualPipe）、Mooncake（MTE） | kernel/分布式/显存 |

## 关键概念词

MoE（2.8T/104B）· 线性注意力 · RetNet · chunk recurrent · DeltaNet/delta rule · Gated DeltaNet · **KDA**（channel-wise 衰减）· hybrid attention（3:1）· MLA · Gated MLA · Attention Residuals · Hyper-Connections/mHC · Pre-LN/Post-LN · DenseNet · Stable LatentMoE · SiTU-GLU · Muon · QK-Clip · loss-free routing · **Quantile Balancing** · WSD · RNoPE/NoPE · on-policy distillation · MTP/Draft Model · DFlash · EP/All-to-All · MoonEP · DualPipe · CP（层次化 chunk）· QAT · FP8 offload · block 级 prefix cache · YOCO · loop LM/Universal YOCO · 忒修斯之船 · 模型内科

## 关键观点（原话引用）

> **孙宇涛**："模型的参数量永远是最主要的一个因素，模型架构本身的改进，相对于模型参数量本身的提升，带来的性能提升是相当微小的。但不同的架构在模型推理方面的性能差异是巨大的。"（研究动机）

> **孙宇涛**："混合注意力虽然从架构上来讲是一种 trade-off，但从最后模型本身的表现来说并不是一个 trade-off。"（hybrid 被大规模采用的原因）

> **孙宇涛**："MLA 本身就是 MQA 的一个等价的形式……它只是一条更好的隧道。"（回答 V4 为何弃 MLA）

> **孙宇涛**："RoPE 本质上带来的是 recency bias……RoPE 并不带来任何长文能力，它甚至是损害长文能力的。"（长上下文节纠偏）

> **孙宇涛**："他们把这个激活搞得特别特别大，足足有 100B……这个决定是一个非技术性的决定，但是这个是要有一定的魄力的。"（K3 最 impressive 之处，引杨植麟"有概率的非共识"）

> **孙宇涛**："科学研究是不存在跳跃性的提升的，只是说大家习惯把这个技术渐进提升的某些节点看成一个 milestone。"

> **孙宇涛**："2017 年这个船刚开始行驶的时候是 Transformer……到 2026 年，它跟 Transformer 的相似度已经是很低了，你是不是还把这个东西叫做 Transformer？"（忒修斯之船）

> **孙宇涛**："AGI 最大的问题就是它没有被 well defined，所以只要能够定义，它就能达到。"

> **孙宇涛**："Kimi 其实在公开里边，是大家认可的、最强调'模型内科'的一个团队……如果大家是这样的 motivation，你的判断方式自然而然就是科学。"

## 关键数字

| 数值 | 含义 |
|------|------|
| 2.8T / 约 100B（104B） | K3 总参 / 激活——嘉宾眼中 K3 最核心的成就与魄力 |
| 1T / 32.6B（K2） | K2 规模；K3 总参不到 3 倍、激活超 3 倍 |
| 2.5 倍 | K3 相对 K2 的 scaling efficiency（官方口径疑非固定 data，综合架构+recipe+数据；外部核验：同验证损失下 FLOPs 约 40%） |
| 1M | 原生上下文长度 |
| 3:1 / 约 4 倍 | 线性:全注意力混合比 / 该配比下加速比上限 |
| 16 token | KDA tile——decay 须在区间内不超 BF16 动态范围，由此反解衰减系数上限 |
| 6e-4 / 3e-4 | 10T 与 20T token 各自最优学习率（WSD 并非真自由的论据） |
| 4M～几十 M token | 单 batch 规模——QB 切桶近似的原因 |
| 1000 TPS vs 300-400 | 小米方案（TileLang+TileRT+DFlash）vs 传统 vLLM 吞吐 |
| 32K→8K | vision encoder 接入前后 token 压缩（encoder 内部不压缩故单独开 CP） |
| 每 4/8 层 | GLM index cache 跨层共享粒度 |

## Limitations

- **人名混同**：转录"松林"指 Gated DeltaNet 作者杨松林（Songlin Yang），"苏建林/苏剑林"指科学空间博主苏剑林——**两人不同**，已分列；引用须核对语境。
- 嘉宾口误/待核：①"K3 之前最大开源模型是千问 72B"与事实不符（DeepSeek-V3 671B、K2 1T 均更早更大），疑为"V3 之前"口误，**引用须剔除**；② Qwen3-Next/3.5/3.6 用 Gated Attention、V4 用 W4A8 预训练、GLM-5 用 DSSA、小米 1000 TPS 归属均为嘉宾口述未核；③ K3 QB 按值域切桶"也有可能是我理解错"（嘉宾自述）。
- 术语 [?] 若干：VDK（Moonlight/Muon 稳定性组件）、s3sjd（疑 loss-free）、UQ（疑 YOCO）、MiMo-V2-Flash 等；口语含混词约 10 处保留原样。
- 12 分钟切块边界为时间粗切（shownotes 仅 3 个时间锚点），chunk-01 有一段后文内容错位插入（已标注），chunk-07 章节号与 shownotes 有漂移。
- 张小珺部分插话被压缩为间接转述，个别判断归属（leader taste、不怕杨植麟）不完全可分。
- **NoPE 口径**：本期说"下掉长上下文 full attention 的 RoPE"偏保守——经对照报告外部核验，K3 是全模型无显式位置编码（NoPE），见 [[2026-09-02_multi_kimi-k3-dueling-reads]]。

## 思考与追问

1. **推理效率的下一档**：3:1 混合把加速比锁死在约 4 倍，sparse attention 又因 Blackwell 上 index 昂贵、跨层共享 questionable、无法 from scratch 被 K3 放弃——下一代继续压低全注意力比例 vs full attention sparse 化（post-train 转化+index cache 跨层复用），哪条天花板更高？K3 留下的 sparse 接口暗示什么路线图？
2. **"模型内科"能否操作化**：K3 弃 WSD 改 cosine 的理由是"少一个变量好调参"，scaling efficiency 2.5 倍又是综合口径——frontier 训练的真正瓶颈可能是实验次数与归因能力而非单点算法。要把这类 know-how 从团队私有经验变成可迁移的行业科学，需要什么样的 trace 采集、变量控制与 benchmark 协议？
3. **改良性曲线的离场信号**：嘉宾判断"无本质创新、皆改良性进步"且 size 受互联网信息量上界约束，本人转向世界模型——从 2.8T 再上 一个数量级，最先把死的会是数据、并行训练 infra（MoonEP 均衡上限、FP8 offload 不等式边界）、还是后训练"能力定义"的供给？这个个人选择是不是"什么时候该离开一条改良性曲线"的可推广信号？

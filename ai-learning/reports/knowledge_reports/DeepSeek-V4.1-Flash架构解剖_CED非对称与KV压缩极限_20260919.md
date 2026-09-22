---
title: "DeepSeek-V4.1-Flash 架构解剖 — CED 非对称设计与 KV Cache 压缩极限"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-09-19"
---

# DeepSeek-V4.1-Flash 架构解剖：CED 非对称设计与 KV Cache 压缩的技术与产业分析

**背景文章**：虚拟灵枢《DeepSeek突然掏出552B新架构！显存暴砍87%，硅谷惊呼：这是外星科技》（2026-09）[原文](https://mp.weixin.qq.com/s/Lxe3z3ON9ZSUBjcqsUZaGg) | **一手来源**：DeepSeek-V4.1-Flash 官方技术报告（51 页 PDF，随 HF 仓库发布，2026-09-10）[HuggingFace](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)（[报告 PDF](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf)；**无 arXiv 编号**，报告随仓库直接发布）

> 标注约定：`[报告 §x px]`（官方技术报告原文，页码已逐节核对）、`[已核实]`（第三方可验证来源）、`[源文]`（虚拟灵枢表述）、`[评]/[推测]`（本报告分析）。本报告与我此前的《才华埋葬在昨天》研究共享 V4.1 事件背景，但聚焦架构本身。

---

## 开头三行：x → f → f(x)

- **x**：Agent 时代的负载特征是"读极长的前文、写相对短的答案"，而 KV cache 随上下文线性膨胀、撑爆 HBM——推理的成本瓶颈从算力（FLOPs）变成了显存（内存墙）。模型架构该如何响应这种非对称负载？
- **f**：DeepSeek 的回答是**把非对称性直接刻进架构**：CED（Causal Encoder-Decoder）把 40 层劈成 20 层轻量编码器（prefill 激活 8B）+ 20 层解码器（decode 激活 16B），decoder 的全局 KV 不再逐层自算、而是由编码器末层隐状态经层相关投影直接生成 [报告 §2.2 p9]；再叠加 CSA2 跨层复用（Full/Reindex/Reuse）、FP4 KV 量化、Engram 196B 条件记忆卸载、SWA Bounded Replay，把全局 KV cache 压到 **890 字节/token（V4-Flash 的 1/4）**、持久化 KV 压到 **1/8** [报告摘要 p1 / §3.2.1 p19]。
- **f(x)**：接受 f 后，"1M 上下文 Agent"的单位经济学被重写：全局小抄只记一次且记在花销最低的层。验证状态：效率数字为官方口径（基线 V4-Flash，同序列长度），第三方复现尚无；**代价在官方数据里已可见——长文理解基准 LongBench-V2 上 V4.1-Flash-Base（45.2）低于 V4-Pro-Base（51.5）** [报告 Table 1 p24]，"压缩不降级"并非全称成立（§4.2）。

---

## 一、一手核实：自媒体转述 vs 官方报告

逐条核对（报告 PDF 51 页逐节查证）：

| 源文表述 | 核实结果 | 官方口径 |
|---|---|---|
| 552B 总参、8B/16B 激活 | ✅ 属实 | 552B backbone 参数（另有 196B Engram 不计入）；prefill 8B/token、decode 16B/token [报告摘要 p1] |
| 45T token 从零预训练、多模态 | ✅ 属实 | 45T token 多模态语料从头预训练 [摘要 p1 / §4.2.2 p22] |
| 9月10日发布、近 50 页报告、全套权重 | ✅ 属实 | HF lastModified 与 PDF 生成时间均为 2026-09-10；报告 51 页；**MIT 许可证**（权重+仓库）[已核实：HF 模型卡] |
| KV 缓存 890 字节/token、前代 1/4 | ✅ 属实（措辞修正） | **全局 KV cache（始终驻留 HBM）= 890 B/token ≈ V4-Flash 的 1/4**；报告不用"-75%"措辞，基线是 **V4-Flash** 而非笼统"前代" [§3.2.1 p19] |
| 持久化存储 -87.5% | ✅ 属实（口径需明确） | 持久化对象是**用于跨会话 prefix 复用的 KV（SSD/host memory）**：不再持久化 SWA KV（约减半）× 全局 KV 压至 1/4 ≈ **1/8**（即 -87.5%）[§3.2.1 p19]；另有图 1(b) 口径：相对 DeepSeek-V1 降约 437 倍 |
| 20 层编码器 + 20 层解码器 | ✅ 属实 | 40 层 = 20 层 causal encoder + 20 层 decoder [§2.2 p9] |
| "解码器共享编码器顶层表征" | ⚠️ **机制转述失真** | **不是交叉注意力**：decoder 各层 global KV 由**编码器末层（第 L/2 层）隐状态经层相关投影矩阵直接生成**（报告 Eq. 1），SWA 分支仍逐层常规计算；效果 = prefill 只需算前半层，复杂度 O(NL)→约 O(NL/2)；灵感来自 YoCo（Sun et al. 2024）[§2.2 p9] |
| CSA2 三类层 + FP4 | ✅ 属实（细节见 §2.2） | Full/Reindex/Reuse 静态指派 + 层级索引 + FP4（E2M1 + 每 16 通道一个 E4M3 scale，NVFP4 风格）[§2.3 p9–11 / §2.4.4 p14] |
| Engram 196B 卸载到 DRAM/**SSD** | ⚠️ **部分失真** | 推理时从 **host DRAM 经后台 RDMA 预取**（与首个 Transformer block 计算重叠）；训练按行分片；RL rollout 期间驻留 GPU——**报告未提 SSD 卸载** [§3.1.3 p18]。Engram 论文确有 Zipf 分层设想（高频入 HBM/DRAM、长尾入 NVMe SSD）[已核实：arXiv:2601.07372]，但那是论文愿景而非 V4.1 落地口径 |
| 64K 冷启动平滑扩到 1M | ✅ 属实且更激进 | 稀疏注意力**从头**以 64K 训练（无 dense warmup），在 34T token 处扩到 1M；batch 固定 100.6M token，LR 2.6e-4 余弦衰减 [§4.2.2 p22] |
| Agent 编程超越 V4-Pro | ✅ 属实 | Terminal-Bench 2.1 90.6 vs 87.9、DeepSWE v1.1 74.2 vs 62.7、Codeforces 3471 vs 3348 [Table 3 p33–34]；但 Terminal-Bench 3.0/4.0 落后 Opus-5.0，报告承认科学向 agent 任务与巨型模型有差距 |
| "外星科技"说法 | ❌ **无出处** | 三轮中英文检索均无来源；最接近的是 V4 时期海外"像魔法一样"的转述 [未查到，间接证据] |
| Nemo Chen 长文 | ❌ **未定位到原文** | 多轮检索未命中；只有同向的间接佐证（模型卡自述"后训练实质变化全在数据管线"）[未查到]——引用需谨慎 |

[评] 自媒体的总体失真模式：**数字大致对、机制全靠比喻、出处常杜撰**。"共享顶层表征"被读者自然脑补成交叉注意力（T5 式），但真实机制更激进——decoder 的全局 KV **根本不是 decoder 自己算的**，是编码器末层表征的投影，这比"共享"更省也更值得玩味。

---

## 二、架构深读（主菜）

### 2.1 CED：把"读长写短"刻进骨架

传统 encoder-decoder（T5）为 seq2seq 翻译设计，靠交叉注意力让 decoder 逐步查询 encoder 输出；decoder-only 主流则让所有层对全部历史 token 自注意力，KV 逐层逐头缓存——这就是"小抄太厚"的来源：N 个 token × L 层 × KV 两份。

CED 的洞察 [报告 §2.2 p9，评]：
1. **负载非对称**：Agent 负载中 prefill（读几十万个 token 的仓库/日志）远长于 decode（写 patch/命令）。让 prefill 只经过 20 层轻量编码器（8B 激活），decode 才走 20 层较重的解码器（16B 激活）——读题与答题匹配差异化算力。
2. **KV 非对称**：decoder 层不为自己看到的长上文逐层建全局 KV；全局 KV 由编码器末层隐状态 H_{L/2} 经层相关投影 W_KV/W_Z 一次生成（Eq. 1）。**逐层 × 逐位置的全局小抄塌缩成"一次投影、多层复用"**——这就是"全局笔记只记一次"的数学含义。
3. **为什么这不等于退回 encoder-decoder**：CED 全程因果（causal encoder 前缀可见性），无交叉注意力的逐查询机制；decoder 对历史的访问被压缩进投影注入 + SWA 局部窗口（128）。代价是 decoder 对长上文的"任意位置精细读写"能力被削弱——它只能通过编码器末层的"摘要性表征"接触历史。[评] 这是用**长文精细检索能力换内存**的赌注，§4.2 的 LongBench-V2 降级正是赌注的价签。

### 2.2 CSA2：层间协作的稀疏注意力

CSA2 的三模式是**静态指派**而非动态路由 [报告 §2.3 p9–11 / §4.2.1 p21–22]：

- **Full 层**：自算 main KV + indexer + Top-K 选择（完整小抄）；
- **Reindex 层**：复用最近层的 main KV/indexer K，但用自己的 indexer Q **重新打分选新 Top-K**（借笔记、自己划重点）；
- **Reuse 层**：main KV 和 Top-K 索引全盘复用，不做索引计算（连划重点都省了）。三模式都自算 Q 与 SWA KV。

层级分配：前 2 层纯 SWA；encoder 其余 18 层压缩率 m=2，3 组×6 层（组内 1 Full + 5 Reuse）；decoder 20 层压缩率 m=1，5 组×4 层（首组 1 Full + 3 Reuse，其余 1 Reindex + 3 Reuse）；indexer 32 头、head dim 128、Top-K=512。decoder 另有 **Hierarchical Sparse Indexer**：首个 Full 层选出 Top-512 并按块（8 位置/块）构成至多 2048 块 ≈ 16384 位置的候选池，后续 Reindex 层只在池内打分——**索引代价与上下文长度解耦**，且 post-training 引入、训练感知。

FP4 量化细节 [§2.4.4 p14]：E2M1 + 每 16 通道一个 E4M3 scale（NVFP4 风格），RoPE 之后量化，post-training 阶段 QAT；indexer Q/K 的 FP4 沿袭自 V4；**SWA KV 因量化敏感仍保留 FP8**——精度兜底的答案是：敏感路径不硬压，量化只落在全局 KV 上，且 QAT 让训练感知量化误差。

### 2.3 Single-Pass mHC 与 Engram、Bounded Replay

- **Single-Pass mHC** [报告 §2.4.1 p12–13]：mHC 在相邻 block 间维护 n=4 条残差流（Sinkhorn-Knopp 20 次迭代约束），混合系数逐 token 预测。原版因数据依赖需 3 个 kernel、激活访存 (4n+4)d；Single-Pass 把输入混合系数**滞后一个 block**（用 A_{l-1} 代 A_{l}）消除依赖，融合为单 kernel Mega-mHC，访存 (2n+2)d——**激活访存减半、达到理论下界**。源文"四车道拆收费站"的比喻方向正确。
- **Engram 196B** [报告 §2.4.2 p13 + 独立论文 arXiv:2601.07372（梁文锋署名，2026-01 首版）]：本质是**经典 N-gram embedding 的现代化**——N-gram 阶 {2,3,4}、8 个哈希头、每头约 16M 条目、FP8 存储，按输入 token 确定性寻址的 O(1) 条件记忆，与 MoE 的"条件计算"轴互补（论文原话："a new axis of sparsity"）。与外部 RAG 的区别：检索在模型内部、嵌入与主干联合训练。论文自证收益：MMLU +3.4、BBH +5.0、Multi-Query NIAH 84.2→97.0，并提出 MoE 计算 vs Engram 记忆的 **U 型稀疏分配 scaling law**。卸载开销：论文称 100B 级表卸载 host memory 开销 <3%（前向即可确定索引 → 异步预取 → 用前序层计算窗口掩蔽）。
- **Bounded Replay** [报告 §2.2 p9 / §3.2.2 p20]：每层 SWA 窗口仅 128 token；持久化缓存只存全局 KV，SWA KV 改放分钟级 TTL 的分布式内存池；恢复时不精确重放 L×128 个 token，只重放**最近 128 个**并截断窗口、接受近似状态——post-training 中模拟 replay 做训练感知适配，报告称质量影响可忽略。[评] 这是"省存储花重算"的教科书取舍：重放 128 token 的 FLOPs 是常数级（与上下文长度无关），省下的持久化是线性级——**上下文越长越划算**，正是 Agent 长会话负载的定向优化。

---

## 三、横向对比：效率架构赛道的趋同与分化

| 维度 | **DeepSeek-V4.1-Flash** | GLM-5.3-Flash | Kimi K3 | DeepSeek-V4-Pro |
|---|---|---|---|---|
| 总参/激活 | 552B / prefill 8B、decode 16B（CED 非对称） | 320B / 18B | 2.8T / 104B | 1.6T / 49B |
| 层数/结构 | 40 层 = 20 因果编码器 + 20 解码器 | 45 层（34 KDA + 11 DSA，3:1 交错） | 93 层（69 KDA + 24 Gated MLA，3:1） | 61 层（CSA/HCA 交错） |
| KV 压缩路线 | CSA2 跨层复用 + FP4 KV + SWA128 不持久化；**890 B/token** | KDA 线性 + DSA 稀疏 + IndexPool（4 个 indexer key 池化为 1）；KV ↓4.44× vs GLM-5.3 | KDA 线性注意力 + AttnRes 深度检索；1M 解码最高 6.3× | CSA（压缩+DSA top-k+shared-KV MQA）+ HCA（128:1 压缩 dense）；KV = V3.2 的 10% |
| MoE | 384 routed + 1 shared，激活 6 | 288 routed + 1 shared，激活 8 | 896 routed + 2 shared，激活 16 | 384 routed + 1 shared，激活 6 |
| 上下文 | 1M（YaRN，64K 从头训、34T 处扩 1M） | 1M | 1M | 1M，最大输出 384K |
| 特色组件 | Engram 196B 条件记忆、Mega-mHC、原生多模态 | mHC、MTP、FP8 权重 | AttnRes、MXFP4/MXFP8 QAT | mHC、Muon |
| 许可证 | MIT | 开源（zai-org） | 开源（moonshotai） | MIT |

[均已核实：各模型 HF config.json / 官方文档 / arXiv 2606.19348（V4）、2607.24653（K3）、docs.z.ai（GLM）]

**谱系修正（重要）**：我此前《才华埋葬在昨天》报告引二手来源称 V4 采用 "high-rank MQA"——**V4 论文中并无此术语**，实际是 CSA（序列维压缩 + DSA top-k）与 HCA（激进压缩 dense）交错混合 + shared-KV MQA + **低秩** indexer [已核实：arXiv:2606.19348 §2.3]。本报告以此为准确口径。

**趋同与分化** [评]：
- **趋同**：四家全部放弃"标准 MHA + 全量 KV"，收敛到同一设计空间的三件套——**稀疏选择（top-k/indexer）× 低秩或线性压缩（MLA/KDA）× 局部窗口（SWA）**；mHC 类多流残差也在 DeepSeek 与 GLM 间扩散。KV cache 战已从"压每个 token 的字节"（MLA 时代）进入"压层与层之间的冗余"（CSA2 跨层复用、IndexPool 池化）时代。
- **分化**：DeepSeek 走**最激进的架构重构**（CED 劈开 prefill/decode），Kimi K3 走**线性注意力主导**（69/93 层 KDA），GLM 走**中间混合**（34 线性 + 11 稀疏）。分化点是赌注不同：CED 赌"读写非对称是常态"，线性注意力赌"序列建模可以大部分线性化"，混合派赌"两种负载都要保"。
- **与 MiMo 资源观的对照**（任务书指定问题）：同一周里，DeepSeek 压推理成本（KV 极致压缩 → 单 token 服务成本下降）、小米烧训练算力（RL Scaling ~$3 万/小时直播）。[评] 这不是分歧而是**同一终局的两端**：Agent 商业模型 = （训练成本摊销 + 单任务推理成本）× 任务量；MiMo 在抬高"能力上限"端，DeepSeek 在压低"单位成本"端。moomoo 社区长文的观察值得引用：模型越高效、单位任务所需 memory 越少，对"模型越大→算力需求越多"的算力叙事本身是冲击 [已核实：moomoo 2026-09]。反方观点同样存在：可靠性（错误累积）而非推理单价才是 Agent 商用瓶颈（阿里云开发者社区 2026-08；Braintrust 对 1781 次生产 Agent 运行的分析称"框架比模型对成功率影响大 7 倍" [已核实：wallstreetcn 转引]）。

---

## 四、批判性分析

### 4.1 "-87.5% 存储"的口径拆解

- 持久化的是**跨会话 prefix 复用的 KV**（SSD/host memory 层），不是模型权重、不是全部缓存 [报告 §3.2.1]。
- 分解：SWA KV 不持久化（约减半）× 全局 KV 压至 1/4 ≈ 1/8。**这不是纯压缩收益，一半是"不存了"的策略**——SWA 不持久化的代价是恢复时 Bounded Replay 的近似状态，官方称质量影响可忽略（训练感知适配）。
- Engram 放 DRAM 算不算省？[评] 这是**成本转嫁而非消除**：HBM → DRAM 的价差（约一个数量级）是真实收益，但"196B 参数不占显存"的叙事不该让人忘记它仍占主机内存与 RDMA 带宽。HN 本地运行派的两极反馈佐证了这一点：企业私有化派欢呼"RAM 比 VRAM 便宜"，实测派报告 Mac Mini 23 秒/token、Qwen 同类 Engram SSD 卸载 prefill 掉近半 [已核实：HN 49639090/49668224]。**卸载路线的体验强依赖内存/互连配置，官方 <3% 开销的前提是数据中心级 RDMA 预取环境**。

### 4.2 8B 激活读 1M：阅读质量降级了吗？

- 官方长上下文数据只有 **LongBench-V2：V4.1-Flash-Base 45.2 < V4-Pro-Base 51.5**（V4-Flash-Base 44.7）[报告 Table 1 p24]——[评] **源文"性能反超旗舰"只在 Agent 编程基准上成立；长文理解上官方自己的数据就显示了降级**（相对 Pro）。自媒体只字未提。
- 独立验证：无 RULER/NIAH 式逐长度检索复现 [未查到]；HF 讨论区 #31 是社区在**索要**长上下文评测；源文未提的 RULER 成绩系杜撰。第三方实测质疑集中在 agent 行为而非长文理解（#46：V4.1-Flash 的 agent 记忆写入量是 V4-Flash 的 10–12 倍、反复读回自身记忆文件、会做无人要求的联网搜索 [已核实：HF discussions/46]——"阅读"行为模式确实变了）。
- [评] 结论：**"890 B/token 不降级"目前既未被官方全称证明（LongBench-V2 降了），也无独立复现**；CED 把长文精细检索能力换成内存的赌注，需要逐长度评测才能定价。

### 4.3 CED 对推理生态的适配成本

- **SGLang Day-0 支持**（2026-09-10 同日，联合 Miles RL 框架），为 CED/CSA2 新增跨层共享 KV、两层级候选选择、Engram GPU/host 放置等机制 [已核实：lmsys.org 博客]。
- **vLLM 发布 9 天后仍在收尾**：tracking issue #56400 下一长串进行中工作（sparse indexer、Engram all-to-all/prefetch、PP 阶段边界、SWA bounded replay、ROCm segfault）；triage 明确"`DeepseekV41ForCausalLM` 是与 V4 不同的独立架构——独立的树、tokenizer 模式、解析器与 config 类"，并新设 `DSv4.1` 标签 [已核实：GitHub vllm-project/vllm#56400]。
- [评] **非对称架构确实是生态逆行成本**：decoder-only 同质层假设深嵌在推理框架的调度器、KV 管理器、PP 切分里，CED 把这层假设打破了。但另一个事实同样真实：SGLang 的 Day-0 支持是**官方共建**的产物——DeepSeek 已经把"架构发布"升级成"架构 + 参考实现 + 框架共建"的打包发布，生态逆行成本由官方主动预付了一部分。这正是刘胜与那篇随笔（《才华埋葬在昨天》）里算子工程师价值的另一面：架构创新越激进，配套工程越重。

### 4.4 训练侧的一句大实话

官方模型卡自述：后训练"所有实质变化都在数据管线：大规模自动合成 agent 任务与环境" [已核实：HF 模型卡]——（问题、环境、验证器）三元组自动合成、多智能体互写测试与清洗泄漏 [源文转述方向属实]。这与 MiMo 报告（本仓 2026-09-17）中"环境/harness 成为训练基础设施一等公民"的判断互证：**2026 年下半的行业共识收敛为"算法趋同、环境与数据工程分胜负"**。

---

## 五、与 EverAgent 已有知识联动

- **[[kv_cache]] / [[attention_mechanism]] / [[sparse_activation]] / [[moe_architecture]] / [[long_context_systems]]**：本报告是 kv_cache 页的"压缩极限"案例库，已新建 [[kv_compression_architectures]] 概念页收纳谱系（MLA→NSA→DSA→CSA→CSA2、KDA、IndexPool）。
- **《才华埋葬在昨天》研究（2026-09-16）**：事件背景互证——刘胜与写的正是 V4 系 high-rank MQA（本文已修正术语）主 attention 算子；"架构越激进、配套工程越重"与"算子工程师转业"是同一枚硬币。
- **《MiMo-V2.6 公开 RL 训练》研究（2026-09-17）**：资源观对照——一个压推理成本、一个烧训练算力，同指 Agent 经济学终局（§三末）。
- 修正记录：V4 注意力机制口径以本报告 §三谱系修正为准（二手来源 "high-rank MQA" 术语不准确）。

---

## 六、思考与追问

1. **我真正理解了什么？** V4.1-Flash 的本质是"把 Agent 负载的非对称性（读长写短、KV 线性膨胀）逐层翻译成架构决策"：CED 翻译负载非对称，CSA2 翻译层间冗余，Bounded Replay 翻译存储与重算的价差，Engram 翻译"记忆 vs 计算"的稀疏分配。四个组件不是孤立创新，是同一个成本函数的四个偏导数。同时我也核实了自媒体的典型失真模式：数字大致对、机制靠比喻、出处会杜撰（"外星科技"与 Nemo Chen 长文均无源）。
2. **我还没搞懂什么？** ①CED 的 decoder 只靠编码器末层投影接触历史，理论上会损失长文精细检索——损失曲线（按上下文长度）长什么样？官方只有 LongBench-V2 一个点；②CSA2 三模式的静态指派是怎么定的（搜索结果？手工？），组内 1 Full + 5 Reuse 的比例依据；③Engram 的 U 型稀疏分配律在 552B+196B 这个规模上的最优配比怎么定。
3. **下一步读什么 / 做什么？** ①精读 Engram 论文（arXiv:2601.07372），把"条件记忆作为第三条稀疏轴"和 U 型分配律做成独立概念页；②跟踪 vLLM #56400 收尾与第三方逐长度长上下文复现（RULER/NIAH），验证 §4.2 的降级幅度；③把 DeepSeek 注意力谱系（MLA→NSA→DSA→CSA→CSA2）与 Kimi/GLM 的线性注意力路线整理成 wiki syntheses 页"KV 压缩战争 2024–2026"。

---

## 来源清单（本报告联网检索，eacli Token Plan-first：web.read / web.search / repo.public；官方报告 PDF 已全文核对）

**一手**
- [DeepSeek-V4.1-Flash HF 仓库（权重 MIT、51 页技术报告 PDF）](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)；[deepseek-recipe（prompt 编码工具，MIT）](https://github.com/deepseek-ai/deepseek-recipe)；[官方 X 公告](https://twitter.com/deepseek_ai/status/2097930608790167907)
- [Engram 论文 arXiv:2601.07372（Conditional Memory via Scalable Lookup）](https://arxiv.org/abs/2601.07372)；[github.com/deepseek-ai/Engram](https://github.com/deepseek-ai/Engram)
- [DeepSeek-V4 技术报告 arXiv:2606.19348](https://arxiv.org/abs/2606.19348)；[NSA arXiv:2502.11089](https://arxiv.org/abs/2502.11089)；[DeepSeek-V3 arXiv:2412.19437](https://arxiv.org/abs/2412.19437)

**生态与第三方**
- [SGLang Day-0 支持博客](https://www.lmsys.org/blog/2026-09-10-deepseek-v41/)；[vLLM tracking issue #56400](https://github.com/vllm-project/vllm/issues/56400)；[recipes.vllm.ai](https://recipes.vllm.ai)
- [HF discussions：#46 agent 记忆写入异常](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/discussions/46)、#39、#35、#31；[HN 主帖（1015 分/577 评论）](https://news.ycombinator.com/item?id=49639090)；[Enclave 安全评测博客](https://enclave.ai/blog/deepseek-v41-flash-is-now-our-best-hacking-model)；[zartbot 架构解读](https://zartbot.github.io/blog/model_arch/dsv41flash_arch/en.html)；[buildfastwithai 评测](https://www.buildfastwithai.com/blogs/deepseek-v4-1-flash-review)

**对照模型**
- [Kimi K3 技术报告 arXiv:2607.24653](https://arxiv.org/html/2607.24653v1) + [config.json](https://huggingface.co/moonshotai/Kimi-K3/raw/main/config.json)；[GLM-5.3-Flash 官方文档](https://docs.z.ai/guides/vlm/glm-5.3-flash) + [config.json](https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/config.json)；[V4-Pro config.json](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/raw/main/config.json)

**产业讨论**
- [moomoo 社区长文：V4.1-Flash 之后的算力叙事冲击](https://www.moomoo.com)；[阿里云开发者社区：Agent 可靠性瓶颈（2026-08-25）](https://developer.aliyun.com)；[华尔街见闻转 Braintrust 1781 次生产 Agent 运行分析](https://wallstreetcn.com)

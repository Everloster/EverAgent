# AI 系统学习路径规划

> 适用人群：有一定编程基础，希望系统深入学习 AI 技术的学习者
> 总时长规划：约 6-12 个月（可按节奏调整）
> 更新日期：2026-03-23

---

## 学习路径总览

```
Phase 1          Phase 2          Phase 3          Phase 4
数学与基础   →   深度学习核心   →   大模型与NLP   →   前沿专题
(4-6周)         (6-8周)           (8-10周)          (持续进行)
```

---

## Phase 1：数学与机器学习基础（4-6 周） — 📊 0%

### 目标
建立扎实的数学基础，理解传统机器学习核心算法

### 数学基础
- **线性代数**：矩阵运算、特征值分解、SVD
- **概率统计**：贝叶斯定理、概率分布、最大似然估计
- **微积分**：偏导数、链式法则（反向传播的基础）
- **信息论**：熵、KL散度、交叉熵

### 机器学习基础
- 监督学习：线性回归、逻辑回归、SVM、决策树
- 无监督学习：K-Means、PCA
- 模型评估：交叉验证、过拟合、正则化
- **推荐教材**：Andrew Ng《机器学习》课程（Coursera）

### 本阶段里程碑
- [ ] 能手推反向传播算法
- [ ] 用 sklearn 实现经典 ML 算法
- [ ] 理解梯度下降的各种变体（SGD, Adam, AdaGrad）

---

## Phase 2：深度学习核心（6-8 周） — 📊 33%

### 目标
掌握深度学习核心架构，能读懂并实现主流模型

### 2.1 神经网络基础（1-2周）
- 全连接网络（MLP）
- 激活函数：Sigmoid, ReLU, GELU
- 批归一化（Batch Normalization）
- Dropout 正则化
- **论文**：`AlexNet (2012)`

### 2.2 卷积神经网络 CNN（1-2周）
- 卷积操作、池化、感受野
- ResNet 残差连接（解决梯度消失）
- 目标检测：YOLO 系列思想
- **论文**：`ResNet (2015)`, `AlexNet (2012)`

### 2.3 序列模型与注意力（2-3周）
- RNN / LSTM / GRU（理解即可）
- Attention 机制（Bahdanau, 2014）
- **Transformer 架构**（重点！）：Self-Attention, MHA, FFN
- **论文**：`Attention Is All You Need (2017)` ⭐ **精读**

### 2.4 生成模型（1-2周）
- VAE（变分自编码器）
- GAN 生成对抗网络
- Diffusion 扩散模型
- **论文**：`GAN (2014)`, `DDPM (2020)`

### 本阶段里程碑
- [ ] 手写 Transformer（从零实现）
- [ ] 用 PyTorch 训练图像分类模型
- [x] 读懂并能讲解 Attention Is All You Need

---

## Phase 3：大语言模型与 NLP（8-10 周） — 📊 0%

### 目标
深入理解 LLM 全技术栈，从预训练到部署

### 3.1 词向量与早期 NLP（0.5周）
- Word2Vec, GloVe
- ELMo（上下文词向量）
- **论文**：`Word2Vec (2013)`

### 3.2 预训练语言模型（2周）
- BERT：双向 Transformer，MLM 任务
- GPT 系列：自回归预训练
- T5：Encoder-Decoder 统一框架
- **论文**：`BERT (2018)` ⭐, `GPT-3 (2020)` ⭐ **精读**

### 3.3 大模型训练技术（2周）
- Scaling Laws（模型/数据/计算的幂律关系）
- 分布式训练：数据并行、模型并行、流水线并行
- 混合精度训练（FP16/BF16）
- FlashAttention（高效注意力实现）
- **论文**：`Scaling Laws (2020)` ⭐

### 3.4 对齐与指令微调（2周）
- SFT（监督微调）
- RLHF（人类反馈强化学习）
- PPO / DPO 算法
- Constitutional AI (Anthropic)
- **论文**：`InstructGPT (2022)` ⭐ **精读**

### 3.5 高效微调与部署（1周）
- LoRA / QLoRA（参数高效微调）
- 量化：INT8, INT4
- vLLM / Ollama（高效推理框架）

### 3.6 推理增强（1-2周）
- Chain-of-Thought (CoT) 提示
- Tree of Thoughts (ToT)
- Reasoning Models（OpenAI o1, DeepSeek-R1）
- **论文**：`Chain-of-Thought (2022)` ⭐

### 3.7 Infra 与数据工程（2-3周）⭐ 新增模块

> 这是《AI演义》中强调最多、但传统学习路径最容易忽视的维度。大模型的成功 60% 在算法，40% 在工程与数据。

#### 分布式训练与工程基础（1-1.5周）
- **数据并行**：AllReduce、梯度同步、通信瓶颈
- **模型并行**：张量并行（Tensor Parallelism）、流水线并行（Pipeline Parallelism）
- **ZeRO 优化**：切分优化器状态/梯度/参数，解决单卡显存不足
  - ZeRO-1：优化器状态切分
  - ZeRO-2：+ 梯度切分
  - ZeRO-3：+ 参数切分（支持万亿参数模型）
- **混合精度训练**：FP16/BF16 + Loss Scaling，节省显存并加速
- **FlashAttention**：IO-aware 重计算，降低注意力层显存峰值
- **工程框架**：DeepSpeed、Megatron-LM、FSDP（PyTorch 原生）
- **论文**：`ZeRO (2019)` ⭐, `FlashAttention (2022)` ⭐, `MegaScale (2024)`

#### 数据工程与数据质量（1-1.5周）
- **数据量 vs 数据质量的争论**：
  - Chinchilla 定律：数据应与参数规模同步增长（不是越大参数越好）
  - The Bitter Lesson 启示：规模最终会赢，但质量决定效率
- **数据采集与清洗管线**：
  - Common Crawl → 去重 → 质量过滤 → 语言检测
  - 案例：RefinedWeb（Falcon 数据集）、LAION-5B（图文数据）
- **数据配比策略**：
  - 领域采样权重（代码 vs 网页 vs 书籍）
  - 合成数据的使用（Self-Instruct, Magpie 流水线）
- **数据飞轮**：模型生成 → 人工审核 → 反哺训练
- **论文**：`RefinedWeb (2023)`, `LAION-5B (2022)`, `Tulu 3 (2024)`

#### Scaling Laws 实践（0.5周）
- 给定算力预算，如何选最优参数量和数据量？
- Chinchilla 修正的 Kaplan 定律（20 tokens/参数 vs 1:1的争议）
- 实践工具：计算 FLOPs = 6ND（N参数量，D数据量）
- 理解 Emergent Abilities（涌现能力）与 phase transitions

### 本阶段里程碑
- [ ] 用 HuggingFace 微调一个 LLM
- [ ] 实现 RAG 系统
- [ ] 能分析和复现 RLHF 训练流程
- [ ] 【新增】能用 DeepSpeed ZeRO-3 启动一个多卡训练任务
- [ ] 【新增】能设计并实现一条数据清洗 pipeline（去重+质量过滤）
- [ ] 【新增】给定算力预算，能用 Scaling Laws 估算最优实验配置

---

## Phase 4：前沿专题（持续进行） — 📊 进行中

### 4.1 多模态 AI
- CLIP（文本-图像对齐）
- GPT-4V / Gemini（视觉语言模型）
- Sora（视频生成）
- **论文**：`CLIP (2021)`, `DALL-E 系列`

### 4.2 AI Agent 系统
- ReAct 框架（推理+行动）
- Tool Use / Function Calling
- Multi-Agent 系统
- MCP（Model Context Protocol）
- RAG + Agent 架构

### 4.3 AI 安全与对齐
- 对齐问题：Goodhart's Law, Mesa-Optimization
- 红队测试（Red Teaming）
- 可解释性（Mechanistic Interpretability）

### 4.4 推理模型与 Test-Time Compute
- OpenAI o1/o3 架构思路
- DeepSeek-R1 开源推理
- MCTS 在 LLM 中的应用

---

## 每周学习节奏建议

| 时间 | 活动 |
|------|------|
| 周一-周三 | 阅读论文 / 学习理论（2-3小时/天）|
| 周四-周五 | 动手实践 / 代码实现（2-3小时/天）|
| 周六 | 撰写学习笔记 / 论文分析报告 |
| 周日 | 复习回顾 / 规划下周 |

---

## 推荐工具与资源

### 编程环境
- Python + PyTorch（主力框架）
- Jupyter Notebook（实验记录）
- HuggingFace Transformers（模型库）

### 学习平台
- [Arxiv](https://arxiv.org) — 最新论文
- [Papers With Code](https://paperswithcode.com) — 论文+代码+排行榜
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- [Andrej Karpathy YouTube](https://www.youtube.com/@AndrejKarpathy) — 强烈推荐

### 实践项目建议
1. **从零实现 GPT-2**（Karpathy nanoGPT）
2. **构建 RAG 问答系统**
3. **LoRA 微调 LLaMA**
4. **实现扩散模型生成图像**
5. **搭建 AI Agent with Tool Use**

---

## 🎯 下一步行动（Next Actions）

基于当前进度，推荐的下一步：

1. **Phase 2 收尾**：完成 Transformer 从零实现（nanoGPT），标记 Phase 2 完成
2. **Phase 3 启动**：开始 BERT/GPT-3 精读（报告已有），进入 HuggingFace 实践
3. **补充 Phase 1**：用 sklearn 完成一个完整的 ML pipeline 实践

> 上次更新：2026-03-26

---

## 项目文件结构

```
ai-learning/
├── roadmap/
│   ├── AI_Development_Timeline.md      # 近20年时间线 + 硬件彩票分析
│   └── Learning_Roadmap.md            # 本文件：4阶段 + Infra模块
├── papers/                            # 30篇 PDF + 32篇索引
│   ├── PAPERS_INDEX.md
│   └── 01~32_*.pdf
├── skills/
│   ├── paper_analysis/SKILL.md        # 论文7步分析法
│   └── knowledge_deep_dive/SKILL.md   # 知识5层解析法
├── reports/
│   ├── AI演义_笔记分析与项目整合报告.md
│   ├── paper_analyses/
│   │   ├── 01_transformer_2017_分析报告.md  ✅
│   │   └── 26_tulu3_2024_后训练分析报告.md  ✅
│   └── knowledge_reports/
│       ├── self_attention_深度解析.md       ✅
│       ├── RLHF_深度解析.md                ✅
│       └── AI关键人物图谱.md               ✅
└── notes/
    └── AI演义_36篇论文.pdf
```

## 相关报告导读

学习本路径时，以下报告可作为深度补充：

- **Phase 2.3 Transformer** → [Self-Attention 深度解析](../reports/knowledge_reports/self_attention_深度解析.md)
- **Phase 3.4 RLHF** → [RLHF 深度解析](../reports/knowledge_reports/RLHF_深度解析.md) + [InstructGPT 论文分析](../reports/paper_analyses/01_transformer_2017_分析报告.md)
- **Phase 3.7 Infra与数据** → [Tulu 3 后训练全流程](../reports/paper_analyses/26_tulu3_2024_后训练分析报告.md)（DPO/RLVR 实践）
- **贯穿全程的人文视角** → [AI关键人物图谱](../reports/knowledge_reports/AI关键人物图谱.md)
- **理解架构竞争的底层逻辑** → [AI发展时间线·硬件彩票章节](./AI_Development_Timeline.md)

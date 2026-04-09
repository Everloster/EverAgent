# Test-time Compute

> 所属分类：核心概念（Core Concept）
> 相关报告：[Test_Time_Compute_深度解析_20260409.md](../reports/knowledge_reports/Test_Time_Compute_深度解析_20260409.md)
> 关联概念：Chain-of-Thought / PRM / MCTS / GRPO / RLHF

## 什么是 Test-time Compute？

Test-time Compute（推理时计算）是指在大语言模型推理阶段，主动分配额外计算资源来提升输出质量的技术统称。其核心思想是：对于复杂问题，不依赖预先训练更多数据，而是在回答时"多花时间思考"。

## 与 Training-time Scaling 的核心对比

| 维度 | Training-time Scaling | Test-time Compute |
|------|----------------------|-------------------|
| **发生时机** | 模型预训练阶段（一次性） | 每次推理请求时（按需） |
| **计算归属** | 数月预训练成本，分摊到所有请求 | 每次请求独立付出 |
| **Scaling 曲线** | 幂律，规模越大越强 | 存在收益递减拐点（约 15-20 步推理后） |
| **解决的问题** | 知识广度、基础能力 | 推理深度、多步决策 |
| **代表模型** | GPT-4 / Claude 3 / LLaMA | o1/o3 / DeepSeek-R1 |
| **典型延迟** | 预训练数月 | 推理秒到分钟级 |

关键洞察：**两者互补，而非替代**。Training-time scaling 解决"模型知道什么"，Test-time Compute 解决"模型如何有效地思考"。

## 核心技术要素

1. **Chain-of-Thought（CoT）**：显式推理链作为内部工作记忆，是 test-time compute 的理论基础（Wei et al., 2022）
2. **Process Reward Model（PRM）**：评估每个推理步骤的质量，引导推理方向；区别于 ORM（只评估最终答案）
3. **MCTS（Monte Carlo Tree Search）**：树搜索探索多条推理路径，UCB1 平衡探索与利用
4. **GRPO（Group Relative Policy Optimization）**：DeepSeek-R1 使用的 RL 训练算法，用组内相对排名替代 learnable critic
5. **Thinking Budget**：思考 token 上限，模型学习 learned stopping criterion 判断何时已充分思考

## 典型代表

- **OpenAI o1/o3**：Extended CoT + RL 训练；AIME 2024 数学从 <10% 提升至 ~70%
- **DeepSeek-R1**：开源；GRPO + 镜象概率；QwQ-32B 同期发布
- **Google Gemini Thinking**：Gemini 1.5 Pro/Ultra 内置扩展推理模式
- **AlphaCode 2**：MCTS + 大规模采样，Codeforces 竞赛级编程

## 工程权衡

- **成本**：o1 API 约是 GPT-4o 的 30-60 倍
- **延迟**：推理时间从 ms 级变为秒到分钟级
- **适用范围**：主要在数学、编程、逻辑推理等有明确正确答案的领域有效
- **陷阱**：过度思考（Over-thinking）、PRM 标注成本高

## 前沿研究方向

- 更高效的 test-time scaling 策略
- Reasoning model 蒸馏（小模型继承推理能力）
- 多模态 reasoning（视觉、科学推理）
- 自适应思考预算（learned stopping criterion）

---

## 引用

- Wei et al., 2022: Chain-of-Thought Prompting Elicits Reasoning in LLMs
- OpenAI o1 Technical Report, 2024
- DeepSeek-R1, 2025: Incentivizing Reasoning Capability via RL
- Wang et al., 2023: Self-Consistency Improves CoT
- Yao et al., 2023: Tree of Thoughts

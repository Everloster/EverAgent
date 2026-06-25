---
title: "投机解码 Speculative Decoding：用小模型给大模型加速 2-3 倍而不改变输出"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-06-25"
---

# 投机解码 Speculative Decoding：用小模型给大模型加速 2-3 倍而不改变输出

> **研究问题**：大模型逐 token 生成很慢（解码 K 个 token 要串行跑 K 次）。投机解码号称能加速 2-3 倍**且输出分布完全不变（lossless）**——这怎么可能？小模型「猜」、大模型「验」的机制是什么？为什么验证能并行、加速从哪来？接受/拒绝采样如何保证输出分布严格等价？
>
> **所属项目**：AI Learning → LLM 推理优化
>
> **报告类型**：知识深度解析（knowledge_report），5 层 + 公式逐符号拆解
>
> 创建日期：2026-06-25

---

## 📋 摘要（先看这 3 句话）

1. **核心思想**：用一个便宜的 draft 模型 $p$ 自回归地「猜」出 K 个候选 token，再用昂贵的 target 模型 $q$ **一次并行前向**同时验证这 K 个 token。被接受的连续 token 直接采纳，第一个被拒绝处「截断重采」。来源：Leviathan, Kalman & Matias (2023, ICML), *Fast Inference from Transformers via Speculative Decoding*。
2. **加速来源是「访存瓶颈」**：低 batch 下 LLM 推理是 **memory-bandwidth bound**（瓶颈在把参数从 HBM 搬到 SRAM，不是算力）。验证 K 个 token 的一次前向，和生成 1 个 token 的访存成本几乎相同——于是「多验几个几乎不花额外时间」。原论文在 T5-XXL 上实测 **2×–3× 加速，输出与标准解码完全一致**。
3. **lossless 的关键是「修正过的拒绝采样」**：接受概率取 $\min(1, q(x)/p(x))$，被拒绝时从残差分布 $\text{norm}(\max(0, q-p))$ 重采。这套规则在数学上保证最终样本严格服从 target 分布 $q$——**加速不以牺牲质量为代价**，这是它区别于「小模型蒸馏」的本质。

---

## 🔍 层次一：5 岁小孩也能懂的类比

> 你（大教授，很慢但权威）要写一句话。助理（实习生，很快但偶尔出错）抢先把接下来 5 个词猜着写在草稿纸上："今天 天气 很 好 啊"。
>
> 你不必一个词一个词地想，而是**扫一眼这 5 个词**：前 4 个「今天 天气 很 好」你认可，第 5 个「啊」你不喜欢，想改成「呢」。于是你**一次性采纳前 4 个**，把「啊」划掉换成「呢」，然后实习生从「呢」之后继续猜。
>
> 关键：你「扫一眼 5 个词」花的时间，和你「自己想 1 个词」差不多——因为对你这种大脑袋来说，瓶颈是「调动整个知识库」（搬参数），多看几个词几乎不额外费劲。所以只要实习生猜得够准，整体就快了好几倍。

**核心直觉**：让便宜的模型先猜一串，让昂贵的模型一次性批量验证——猜对的白赚，猜错的兜底。

---

## 📖 层次二：概念定义与基本原理

**正式定义**：

投机解码是一种**无损推理加速**算法：给定 target 模型 $q$（慢、准）和 draft 模型 $p$（快、近似），每一步先用 $p$ 自回归生成 $K$ 个草稿 token，再用 $q$ 并行计算这 $K$ 个位置的 logits，通过修正的拒绝采样决定接受多少，从而**在不改变 $q$ 输出分布的前提下**，平均每次 target 前向产出 > 1 个 token。

**两个支撑性事实**（论文的立论基础）：

1. **难任务里混着易子任务**：很多 token 是「容易的」（如代码里的 `for i in range(`、英文里的 `the`/`a`），便宜模型就能预测准。
2. **低 batch 推理是访存瓶颈**：解码时瓶颈是把模型参数从 HBM 读到计算单元，而非浮点运算。因此「batch=1 跑一次」和「batch=K 跑一次」耗时接近——**并行验证 K 个 token 近乎免费**。

**与相关概念的区别**：

| 概念 | 与投机解码的区别 |
|------|----------------|
| 模型蒸馏 | 蒸馏是训练出一个更小模型**永久替代**大模型，**改变输出分布**；投机解码输出与大模型**严格一致** |
| 量化 | 量化压缩参数精度（可能损质量）；投机解码不动参数、不损质量 |
| 并行解码 / Medusa | Medusa 用大模型自带的多个「草稿头」代替独立 draft 模型，是投机解码的变体而非对立物 |

---

## ⚙️ 层次三：算法与公式逐符号拆解（核心）

### 主循环（每一轮）

记 target 模型 $q$、draft 模型 $p$、当前已确定前缀 $x_1,\dots,x_n$、前瞻步数 $K$。

**第 1 步：draft 自回归猜 K 个**

$$\tilde{x}_t \sim p(x \mid x_1,\dots,x_n,\tilde{x}_1,\dots,\tilde{x}_{t-1}), \quad t=1,\dots,K$$

- $\tilde{x}_t$：draft 猜的第 $t$ 个候选 token
- 注意这步是**串行**的（draft 要一个个猜），但 draft 便宜，所以快

**第 2 步：target 一次并行算 K+1 组 logits**

$$q(x\mid x_1,\dots,x_n),\ q(x\mid x_1,\dots,x_n,\tilde{x}_1),\ \dots,\ q(x\mid x_1,\dots,x_n,\tilde{x}_1,\dots,\tilde{x}_K)$$

- 一次前向（batch 维度放这 K+1 个前缀）就拿到全部，这是**加速的物理来源**
- 为什么是 K+1：除了验证 K 个草稿，还顺带拿到「全部接受后下一个 token」的分布，可以白赚第 K+1 个

**第 3 步：逐个接受 / 拒绝（修正的拒绝采样）**

对 $t=1,\dots,K$，采样 $r \sim U[0,1]$，若

$$r < \min\!\left(1,\ \frac{q(\tilde{x}_t \mid x_1,\dots,x_{n+t-1})}{p(\tilde{x}_t \mid x_1,\dots,x_{n+t-1})}\right)$$

则**接受** $\tilde{x}_t$；否则**拒绝并停止**（后面的草稿全扔掉）。

- $\frac{q}{p}$：target 和 draft 对同一个 token 的概率比
- 直觉：draft 高估了某个 token（$p > q$）时，按比例概率拒绝；draft 低估或一致（$p \le q$）时必接受（因为 $\min$ 取 1）
- 一旦拒绝就截断：保证「被接受的前缀」是连续的

**第 4 步：拒绝处从残差分布重采**

被拒绝的位置，从

$$x_{n+t} \sim \text{norm}\big(\max(0,\ q(x) - p(x))\big)$$

重新采一个 token。

- $\max(0, q-p)$：把 target 比 draft「多出来」的概率质量留下，负的清零
- $\text{norm}(\cdot)$：归一化成合法分布
- 这一步是 lossless 的数学核心——它精确补偿了拒绝带来的分布偏差

### 为什么输出分布严格等于 $q$？

**[原论文 Theorem 证明，此处给直觉]**：接受规则 $\min(1, q/p)$ 加上残差重采 $\text{norm}(\max(0,q-p))$，两部分概率质量加起来，使任意 token $x$ 最终被输出的概率恰好等于 $q(x)$。这是经典拒绝采样的变体，因此**投机解码的输出与「直接从 $q$ 采样」分布完全相同**——这就是「无损」的严格含义。

---

## 💻 层次四：最小实现（伪代码）

```python
def speculative_step(prefix, draft_p, target_q, K):
    # 1. draft 串行猜 K 个
    draft_tokens, draft_probs = [], []
    cur = prefix
    for _ in range(K):
        dist = draft_p(cur)                 # draft 分布 p(·|cur)
        tok = sample(dist)
        draft_tokens.append(tok); draft_probs.append(dist[tok])
        cur = cur + [tok]

    # 2. target 一次并行算 K+1 组 logits
    q_dists = target_q.parallel(prefix, draft_tokens)  # 长度 K+1

    # 3-4. 逐个接受 / 拒绝 / 残差重采
    out = []
    for t in range(K):
        r = uniform(0, 1)
        if r < min(1, q_dists[t][draft_tokens[t]] / draft_probs[t]):
            out.append(draft_tokens[t])     # 接受
        else:
            resid = normalize(relu(q_dists[t] - draft_dist_t))  # 残差分布
            out.append(sample(resid))       # 拒绝并重采，截断
            return out
    out.append(sample(q_dists[K]))          # 全接受，白赚第 K+1 个
    return out
```

> 关键点：`target_q.parallel(...)` 是一次前向（batch=K+1），这是加速的来源；`return out`（在拒绝处提前返回）实现「截断」。

---

## 🔬 层次五：前沿进展与工程注意事项

**实测加速（精确数字）**：
- **Leviathan et al. 2023**：T5-XXL 上 **2×–3×** 加速，输出与标准 T5X 实现完全一致。
- **Chen et al. 2023**（DeepMind，arXiv:2302.01318）：Chinchilla 70B 上约 **2×** 加速。

**加速不均匀（重要工程现实）**：
- 加速幅度取决于 draft 与 target 分布的**对齐程度**（接受率）。代码生成（HumanEval）「易 token」多、加速更大；摘要（XSum）加速较小。来源：Chen et al. 2023 的分领域观察。
- **[2025 新研究]** Sandler et al. (2025, arXiv:2510.02128) 指出加速在不同任务/语言间**不均等**：draft 拟合差的任务（如某些低资源语言）加速更少，提出这是一种「计算不公平」，并给出缓解方法（平均改善公平指标约 12%）。

**主要变体（演化谱系）**：
- **Tree-based / SpecInfer / Medusa**：不只猜一条直链，而是猜一棵 draft token **树**，提高接受率。Medusa 用 target 自带的多个草稿头省掉独立 draft 模型。
- **Recursive Speculative Decoding (RSD, 2024)**：用「无放回采样」（Gumbel-Top-k / Stochastic Beam Search）最大化 draft 树的多样性。

**工程注意事项**：
- draft 模型选型是关键：太弱→接受率低→白跑；太强→draft 本身慢→省不下。常用「同系列小模型」（如 T5-small 配 T5-XXL）。
- $K$ 的取舍：$K$ 太大→draft 串行开销上升 + 后段接受率衰减；太小→并行红利吃不满。

---

## ✅ 知识检验题

**基础级**：
1. 投机解码为什么能「加速但不改变输出」？一句话。
2. draft 模型和 target 模型各扮演什么角色？

**进阶级**：
3. 为什么「target 并行验证 K 个 token」几乎不比「生成 1 个 token」更慢？（提示：访存瓶颈）
4. 接受概率 $\min(1, q/p)$ 中，当 draft 高估某 token（$p>q$）时会发生什么？

**专家级**：
5. 证明（或解释）为什么「$\min(1,q/p)$ 接受 + $\text{norm}(\max(0,q-p))$ 重采」能让输出分布严格等于 $q$。
6. 为什么代码生成的加速比文本摘要更大？这对「投机解码在所有任务上同等有用」这个说法有何修正？

---

## 📚 学习资源推荐

**原始论文（必读）**：
- Leviathan, Kalman, Matias (2023). Fast Inference from Transformers via Speculative Decoding. *ICML 2023*, PMLR 202:19274-19286. https://arxiv.org/abs/2211.17192
- Chen et al. (2023). Accelerating Large Language Model Decoding with Speculative Sampling. arXiv:2302.01318. https://arxiv.org/abs/2302.01318

**综述与解读**：
- Xia et al. (2024). Unlocking Efficiency in LLM Inference: A Survey of Speculative Decoding. arXiv:2401.07851. https://arxiv.org/abs/2401.07851
- acganesh, *Speculative decoding for LLM inference*（含正确性证明的清晰推导）。https://acganesh.github.io/posts/speculative_decoding/

**前沿**：
- Sandler et al. (2025). The Disparate Impacts of Speculative Decoding. arXiv:2510.02128.

---

## 🤔 思考与追问

1. **我真正理解了什么？**
   投机解码的加速本质不是「算得快」而是「访存红利」——因为低 batch 推理卡在搬参数上，target 一次前向并行验 K 个 token 几乎不额外花钱。lossless 不是近似，而是由「修正拒绝采样」**严格保证**输出分布等于 target。它与蒸馏/量化的根本区别就在这个「严格无损」。

2. **我还没搞懂什么？**
   - 残差分布 $\text{norm}(\max(0,q-p))$ 的完整正确性证明，我只理解了直觉，没有逐步推完测度上的等式。
   - 树形投机（SpecInfer/Medusa）的接受率收益如何量化？树的分支数 vs 验证开销的最优点在哪？
   - draft/target 的最优容量比（draft 多大最划算）有没有理论刻画，还是纯经验调？

3. **下一步读什么 / 做什么？**
   - 精读 Chen et al. 2023 原文，把残差分布的正确性证明逐步推一遍（已汇入 open-questions）。
   - 做一篇 **Medusa** 的概念报告，对比「独立 draft 模型」vs「自带草稿头」的工程权衡——可与现有 `kv_cache.md`、`llm_inference_engines.md` 概念页关联。
   - 关联阅读：访存瓶颈 → 已有 `kv_cache.md`，二者都是「推理是 memory-bound」这一事实的产物，值得在 wiki 里建交叉链接。

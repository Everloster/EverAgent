---
title: "GRPO 缩尺模拟实验：与 T060 推理模型三大流派联动的代码复现"
type: experiment_analysis
status: done
experiment_id: exp_008
script: src/grpo_simulation.py
stage: 4
prerequisites: ["transformer_architecture", "grpo_concept", "sft_vs_rlhf"]
updated_on: 2026-06-21
---

# exp_008：GRPO 缩尺模拟实验

## 实验摘要

> 一句话：用一个 2-token 的小策略在 toy 算术题上完整跑通 **GRPO 训练循环**（组内采样 → 规则化奖励 → 组内相对优势 → PPO-clip 策略更新 + KL 惩罚），并与 ai-learning 报告 T060《推理模型三大流派详解》第 3.3 / 4.4 节的 GRPO 算法盒与 R1 规则化奖励公式一一对应，验证"无 Critic + 组内均值基线"算法在小规模下也能产出与论文一致的 reward / entropy / KL 曲线。

---

## Step 1 实验目标

### 1.1 验证的问题

T060（[推理模型三大流派详解_20260621.md](../../ai-learning/reports/knowledge_reports/推理模型三大流派详解_20260621.md)，§3.3 DeepSeek R1 路线，§4.4 简化 GRPO 实现）描述了 R1 训练的关键三件套：

1. **GRPO 算法**：用组内相对奖励代替 Critic；
2. **规则化奖励**：accuracy + format 两段加和（无 Reward Model）；
3. **R1 训练曲线**：reward 从 ~0 上升、policy entropy 下降、KL 偏离参考策略。

本实验在 **ai-practice 不跑真实 LLM 的前提下**，把上述三件套压缩到 2-token 的字符级小策略里完整复现，让读者看到：

- 训练曲线形状（reward 上升 / entropy 下降 / KL 上升）是否与 T060 §3.3 描述一致；
- "无 Critic" 的工程含义：组内均值替代 Critic 网络，显存与算力开销的来源是什么；
- 规则化奖励的设计取舍：accuracy vs format 的强度比例如何影响学习走向；
- 失败 case：没有 prompt 条件化时，policy 退化为"全选同一个常见答案"的局部最优。

### 1.2 与已有实验的对应关系

- `exp_004`（Qwen2.5-3B GRPO 微调）：在真实 3B 模型上跑 GRPO；本实验在 toy 字符策略上重做同一组公式。
- `exp_006`（Long Context 1M 缩尺模拟）：用"小输入展示真实系统的工程形状"；本实验同样的工程取舍：模型小、算法真、曲线真。
- `exp_007`（SkillOS 缩尺模拟）：用 deterministic 任务流模拟真实策略回路；本实验与之同构，把 RL 训练循环压缩到 CPU。

### 1.3 为什么不在 ai-practice 跑真实 GRPO

跑 Qwen2.5-3B GRPO 微调（exp_004）需要：
- 8GB+ 显存的 GPU（本机当前无 torch / CUDA）；
- 1-2 小时训练时间；
- HF 镜像 + Unsloth + 4-bit 量化工具链。

本实验目标不是"训一个真模型"，而是"让 GRPO 的算法结构在 CPU 上可观察"。教学场景下，**看算法形状比训真模型更有学习价值**。

---

## Step 2 实现方法

### 2.1 任务

**Toy GSM8K 算术题**：20 道形如 `"What is a + b?"` / `"What is a - b?"` / `"What is a times b?"` 的题，约束 `max_value=4` 并过滤掉 `ground_truth > 9` 的题（确保答案是一个 0-9 的数字）。

### 2.2 模型

**TinyPolicy**（"模型"只是一个 2-token 的 categorical policy）：

| 超参数 | 值 | 含义 |
|--------|-----|------|
| `vocab_size` | 11 | 字符 `"0123456789="` |
| `max_answer_len` | 2 | 答案形式 `"X="`（1 个数字 + 1 个等号） |
| `theta` shape | `[2, 11]` | 每位置对每个 token 的 logit |
| 初始偏置 | `pos0: 数字 +0.5`，`pos1: "=" +1.5` | 打破初始对称 |

策略用 softmax 输出每个位置上的 token 概率分布，独立从左到右采样（无自回归条件依赖，因答案只有 2 个 token）。

### 2.3 训练目标（T060 §3.3 + §4.4 复现）

**规则化奖励**（T060 §4.4 简化版 reward_correctness_and_format）：
```python
r = acc_reward + fmt_reward
acc_reward = 1.0 if extracted == ground_truth else 0.0
fmt_reward = 0.1 if "=" in text else 0.0
```

**组内相对优势**（T060 §3.3 GRPO 公式）：
```python
A_i = (r_i - mean_r_group) / (std_r_group + 1e-8)
```

**GRPO 损失**（DeepSeekMath Shao et al. 2024）：
```python
L = -E_i [ min(ρ_i A_i, clip(ρ_i, 1-ε, 1+ε) A_i) ] + β KL(π_θ || π_ref)
ρ_i = π_θ(o_i|x) / π_ref(o_i|x)
```

**关键归一化**（DeepSeekMath 论文 §4.2）：组内累积梯度除以 `group_size`，再对 prompt batch 求平均。这让学习率与 `group_size` 和 batch 大小解耦，是 GRPO 相对 PPO 的算法级优势。

### 2.4 训练配置（默认参数）

| 参数 | 值 | 说明 |
|------|-----|------|
| `steps` | 80 | GRPO 更新步数 |
| `num_prompts` | 20 | 唯一 prompt 数 |
| `group_size` (G) | 8 | 每个 prompt 采样数 |
| `clip_eps` | 0.2 | PPO clip 范围 |
| `kl_beta` | 0.005 | KL 惩罚权重 |
| `lr` | 1.0 | 学习率 |
| `shared_gt` | 7 | 共享 ground truth（toy 单答案模式） |

### 2.5 量化指标

| 指标 | 公式 | 物理意义 |
|------|------|----------|
| `mean_reward` | group 内奖励均值 | 主训练目标 |
| `reward_std` | group 内奖励标准差 | 组内方差 = GRPO 优势信号强度 |
| `accuracy` | group 中 `acc==1.0` 的样本比例 | 答对的题目占比 |
| `format_rate` | group 中含 `"="` 的样本比例 | 格式对齐进度 |
| `policy_entropy` | `Σ -p log p` over 22 个 (pos, tok) 单元 | 策略不确定性（应随训练下降） |
| `kl_to_ref` | `Σ p_θ (log p_θ - log p_ref)` | 与初始参考策略的距离 |

---

## Step 3 关键发现

### 3.1 Canonical run：shared-gt 模式

```
[step    1] mean_r=0.0744 std_r=0.0697 acc=0.03 fmt=0.43 H=4.445 KL=0.0000 loss=0.0000
[step   80] mean_r=1.0662 std_r=0.0585 acc=0.97 fmt=0.97 H=0.135 KL=3.3870 loss=-0.0330
```

训练曲线（`ai-practice/images/grpo/grpo_curves.png`）：

| 阶段 | step | mean_r | acc | H | KL | 解读 |
|------|------|--------|-----|---|----|------|
| 初始 | 1 | 0.07 | 0.03 | 4.45 | 0.00 | 随机策略；format 0.43 来自初始 bias |
| 探索 | 1-10 | 0.07 → 0.34 | 0.03 → 0.25 | 4.45 → 2.73 | 0 → 0.85 | 策略迅速偏向 "="，开始试 digit 7 |
| 收敛 | 10-20 | 0.34 → 1.00 | 0.25 → 0.91 | 2.73 → 0.66 | 0.85 → 2.87 | 关键拐点：acc 从 25% 跳到 91% |
| 稳定 | 20-80 | ~1.07 | ~0.97 | ~0.15 | ~3.39 | 策略完全坍缩到 "7=" |

**关键观察**：
- **奖励曲线呈现 S 形**（sigmoid-like），符合 T060 §3.3 描述的 R1 训练曲线："前 100-200 步 reward 接近 0（探索），之后 reward 快速上升"。
- **policy entropy 单调下降**（4.45 → 0.13），与 PPO/GRPO 理论一致：策略从均匀分布坍缩到 one-hot 分布。
- **KL 单调上升**（0 → 3.39），量化"策略偏离参考"的程度；`β·KL` 项是防止完全坍缩的刹车。
- **accuracy 在 5-10 步内从 0.03 跳到 0.91**：这是组内相对优势的爆发性信号——一旦有几次采样偶然碰到正确数字 7，高 advantage 把 logits 推高，吸引更多采样，形成正反馈。

### 3.2 Failure case：mixed-gt 模式（无 prompt 条件化）

```
[step    1] mean_r=0.0556 std_r=0.0462 acc=0.01 fmt=0.43 H=4.440 KL=0.0000 loss=0.0000
[step   80] mean_r=0.2913 std_r=0.1941 acc=0.19 fmt=0.97 H=1.700 KL=1.8433 loss=1.5750
```

| 阶段 | step | mean_r | acc | H | KL | 解读 |
|------|------|--------|-----|---|----|------|
| 初始 | 1 | 0.06 | 0.01 | 4.44 | 0.00 | 随机 |
| 探索 | 1-20 | 0.06 → 0.23 | 0.01 → 0.13 | 4.44 → 2.63 | 0 → 0.98 | 策略学 "=" 很快 |
| 平台 | 20-80 | ~0.25-0.30 | ~0.15-0.20 | ~1.7-2.5 | ~1.5-1.8 | 策略坍缩到单一最常见 digit，acc 上限 ≈ 0.20 |

**关键观察**：
- **accuracy 平台在 ~0.20 而非 1.0**：因为 policy 是 prompt-independent，只能输出一个"最安全"的 digit（20 个 prompt 里 ground truth 分布偏向中间数字）。
- **KL 平台在 ~1.8 而非 3.4**：策略没有"完全确信"地坍缩，因为不同 group 内的正确数字不同，组内方差推着策略在多个 digit 之间犹豫。
- **格式奖励 0.97 / acc 0.19**：策略优先利用了"="格式奖励（容易拿），对 acc 奖励的拟合能力受限于 prompt 独立结构。

**这个失败 case 的工程含义**：真实 LLM 之所以能"按 prompt 答不同的题"，是因为它有 prompt 条件化的 Transformer 注意力。本 toy policy 没有这种结构，因此**对每个 prompt 都只能给同一个答案**。这个限制对应了 T060 §3.3 提到的关键训练经验：**"组内方差推着策略移动 + 强 Prompt 条件化能力是 GRPO 在 LLM 上有效的两个前提"**。

### 3.3 与 T060 报告的对应关系

| T060 节 | 报告内容 | 本实验对应实现 | 文件位置 |
|---------|---------|---------------|----------|
| §3.3 GRPO 算法核心 | `advantage = (r - mean_r) / std_r` | `advantages = (r_arr - mean_r) / std_r` | `src/grpo_simulation.py` L290 |
| §3.3 Rule-based reward | accuracy + format 加和 | `r = info["acc"] + info["fmt"]` | `src/grpo_simulation.py` L226 |
| §3.3 PPO-clip | `min(ρ·A, clip(ρ, 1-ε, 1+ε)·A)` | `surr = min(ratio*adv, clipped_val*adv)` | `src/grpo_simulation.py` L323-325 |
| §3.3 KL 惩罚 | `β · KL(π_θ || π_ref)` | `loss_total += kl_beta * kl` | `src/grpo_simulation.py` L355 |
| §4.4 规则化奖励盒 | `reward_correctness_and_format` | 完整复现（acc=1, fmt=0.1） | `src/grpo_simulation.py` L203-226 |
| §4.4 GRPOConfig | `num_generations=64, beta=0.04` | toy 化：`group_size=8, kl_beta=0.005` | `src/grpo_simulation.py` L410-420 |
| §5.3 训练曲线 | R1 训练中 reward 从 0 上升到 ~0.9 | 0.07 → 1.07 (含 format reward) | `images/grpo/grpo_curves.png` |
| §5.3 KL 行为 | KL 应随训练上升，防止策略跑太远 | KL 0 → 3.4 真实观察到 | 同上 |

### 3.4 训练曲线可视化

主图保存在 `ai-practice/images/grpo/grpo_curves.png`（共享 ground truth 模式，4 子图）：

```text
[Mean Reward]   0.07 ──────────╮
                            │   ╰──── 1.07  (sigmoid-shaped)

[Accuracy]      0.03 ─────╮
                          ╰────── 0.97  (jump at step 10-20)

[Policy Entropy] 4.45 ╮
                       ╰────────── 0.14  (collapse)

[KL to Ref]      0.00 ╭────────── 3.39  (monotone increase)
```

Failure case 图：`ai-practice/images/grpo_mixed/grpo_curves.png`（mixed-gt 模式，acc 平台在 0.20）。

---

## Step 4 代码参考

### 4.1 核心实现位置

| 模块 | 文件:行 | 说明 |
|------|---------|------|
| Policy 采样 | `src/grpo_simulation.py` L149-159 | `TinyPolicy.sample()` |
| 规则化奖励 | `src/grpo_simulation.py` L203-226 | `reward_function()` |
| 组内优势 | `src/grpo_simulation.py` L286-296 | 跨 prompt 的均值/方差归一 |
| GRPO 梯度 | `src/grpo_simulation.py` L298-342 | score-function 梯度 + KL 梯度 |
| 训练主循环 | `src/grpo_simulation.py` L407-429 | `run()` 内的 for 循环 |
| PNG 绘图 | `src/grpo_simulation.py` L460-520 | 用 PIL 手画 4 子图 |

### 4.2 可复用的关键函数/类

- `TinyPolicy`：通用的 categorical policy，可用于任何离散动作空间的 RL 实验。
- `reward_function(answer_ids, prompt)`：R1 风格的 accuracy+format 奖励，可扩展到 GSM8K、 MATH 等任务（只需改 `extract_integer`）。
- `grpo_update(...)`：单步 GRPO 更新，可独立调用做 ablations（改 group_size / kl_beta / clip_eps）。
- `_save_plot(...)`：纯 PIL 的曲线绘制，不依赖 matplotlib，可作为其他教学脚本的轻量级可视化模板。

### 4.3 关键算法注释

**GRPO 梯度的"组内归一"**（`src/grpo_simulation.py` L335-342）：
```python
# Per-prompt average (DeepSeekMath normalisation).
prompt_grad /= max(group_size, 1)
grads += prompt_grad
# Per-step average across the number of prompts.
grads /= max(len(prompts), 1)
```
这一归一化是 GRPO 论文 §4.2 的核心：让学习率与 group size / batch size 解耦，避免"组越大步长越大"。

**Sample reuse 的关键修复**（`src/grpo_simulation.py` L264, L295, L317）：
```python
# Store the actual sampled ids in step 1.
all_sampled_ids.append(ids)
...
# In gradient step, REUSE these ids (not re-sample!).
ids = all_sampled_ids[flat_idx]
```
如果重新采样，gradient 和 advantage 就完全解耦，训练会原地踏步。**这是实现 GRPO 时最容易踩的坑**。

---

## Step 5 局限性与下一步

### 5.1 已知局限

1. **Toy policy 没有 prompt 条件化**：每个 prompt 都从同一个 `θ` 采样。共享 ground truth 模式下没问题，但 mixed-gt 模式会卡在 ~20% acc。这**不是 GRPO 算法的失败，而是 toy 模型的容量上限**——真实 LLM 通过 self-attention 实现 prompt 条件化。
2. **每位置独立采样**：`θ[pos]` 之间没有依赖，相当于非自回归 toy。这与真实 LLM 的自回归采样不同，但 GRPO 损失公式完全一样。
3. **CPU-only**：为了在没有 torch 的环境下可运行，用 numpy 手写。真实 GRPO 在 GPU 上用 TRL/unsloth 框架。
4. **无 critic 是真的无**：R1 论文的关键卖点，本实验直接复现了——没有任何额外的 value 网络。
5. **奖励函数 hard-coded**：固定 1.0/0.1/0.0 的奖励结构。真实 R1 在训练中动态调整 accuracy vs format 权重（"冷启动 → 全场景偏好"）。

### 5.2 规模缩放观察（"scale-down" 视角）

| 维度 | 本 toy 实验 | 真实 R1 训练 | 缩尺倍数 |
|------|------------|------------|---------|
| 参数量 | 22 (θ 大小) | 671B (DeepSeek-V3) | 3.0 × 10¹⁰ |
| 训练 tokens | ~50K (80 步 × 20 prompts × ~30 token/prompt) | 数十亿 | 10⁵ |
| 训练时间 | < 5 秒 | 2-5 天 × 16 H100 | 10⁴-10⁵ |
| Group size | 8 | 64 | 8× |
| Beta (KL) | 0.005 | 0.04 | 0.125× |
| 显存 | < 1 MB | 8 × 80 GB H100 = 640 GB | 6 × 10⁸ |

缩尺不是均匀的——KL 系数在小模型上必须调小，否则参考策略的束缚会盖过准确率信号。

### 5.3 下一步实验方向

- **加 prompt 条件化**：把 `θ` 替换为 `θ(prompt_hash)`，或加一个极小的 `Embedding(prompt) → θ_bias`，让 mixed-gt 模式也能 acc → 1.0。
- **对比 PPO（带 Critic）vs GRPO（无 Critic）**：在同一个 toy 上实现 PPO baseline，对比 loss 曲线形状、最终 acc、计算量。
- **Group size 消融**：跑 `G=2, 4, 8, 16, 32`，观察训练稳定性和收敛速度（与 T060 §3.3 提到的"推荐 G=8 或 16"对齐）。
- **R1-Zero 模式**：去掉 format reward，只留 accuracy reward，观察策略是否还能学（这模拟 R1-Zero 的"纯 RL"路径）。
- **与 exp_004 联动**：把本脚本生成的训练曲线，与 `notebooks/04_qwen25_grpo_finetuning.ipynb` 在 Qwen2.5-3B 上的真实 GRPO 曲线对比（即使只跑 100 步），验证形状一致性。

---

## §6 思考题与延伸

1. **组内方差消失时 GRPO 会发生什么？** 当 G 个回答的奖励全部相等（例如所有都答对或都答错），`std_r ≈ 0`，优势约等于 0，策略不更新。这对应真实训练中"探索失败的 group"——R1 论文用 rejection sampling 跳过这些 group。能否在 toy 上复现？
2. **β 增大会怎样？** 把 `kl_beta` 从 0.005 提到 0.1，KL 会被压住，但 accuracy 上升更慢。是否存在最优 β 与 group size 的关系？
3. **Reward shaping 的影响？** 把 format reward 从 0.1 改成 1.0，策略会过度拟合 "=" 格式（这次 toy 里 format_rate 会先冲到 1.0，acc 滞后）。这正是 R1 论文 §3.3 提到的 "format reward 主导 vs accuracy reward 主导" 的工程取舍。
4. **真实 LLM 的"prompt 条件化"在 toy 中如何近似？** 用 `(prompt_text → tiny hash → θ_bias)` 加一个浅层 bias 就能让 mixed-gt 模式 acc 上升。是否要做？

---

## §7 参考资料

### 7.1 一手论文
- **DeepSeekMath (Shao et al. 2024)**：[arxiv.org/abs/2402.03300](https://arxiv.org/abs/2402.03300) — GRPO 原始论文
- **DeepSeek-R1 (DeepSeek-AI 2025)**：[arxiv.org/abs/2501.12948](https://arxiv.org/abs/2501.12948) — GRPO 在 R1 上的应用
- **PPO (Schulman et al. 2017)**：[arxiv.org/abs/1707.06347](https://arxiv.org/abs/1707.06347) — GRPO 的 baseline 算法
- **TRL GRPOTrainer**：[huggingface.co/docs/trl/grpo_trainer](https://huggingface.co/docs/trl/grpo_trainer) — 工业级实现

### 7.2 配套知识报告
- **T060 推理模型三大流派详解**：[ai-learning/reports/knowledge_reports/推理模型三大流派详解_20260621.md](../../ai-learning/reports/knowledge_reports/推理模型三大流派详解_20260621.md) — 本实验的理论依据
- **RLHF 深度解析**：[ai-learning/reports/knowledge_reports/RLHF_深度解析.md](../../ai-learning/reports/knowledge_reports/RLHF_深度解析.md) — RLHF → GRPO 的演进
- **Test_Time_Compute 深度解析**：[ai-learning/reports/knowledge_reports/Test_Time_Compute_深度解析_20260409.md](../../ai-learning/reports/knowledge_reports/Test_Time_Compute_深度解析_20260409.md) — Test-time scaling 的基础

### 7.3 本项目内 cross-reference
- **exp_004**：[experiments/exp_004_qwen25_grpo_finetune.md](exp_004_qwen25_grpo_finetune.md) — 真实 Qwen2.5-3B GRPO 微调
- **wiki 概念页**：[wiki/concepts/grpo.md](../wiki/concepts/grpo.md) — GRPO 概念讲解
- **scripts 源文件**：[src/grpo_simulation.py](../src/grpo_simulation.py) — 本实验代码
- **运行产物**：
  - `images/grpo/grpo_curves.png` — canonical 训练曲线
  - `images/grpo/grpo_run.json` — 完整 step-by-step 指标
  - `images/grpo/grpo_summary.txt` — 文本格式 step 表 + 最终样本
  - `images/grpo_mixed/grpo_curves.png` — failure case 曲线

---

## §8 实验产物清单

| 类型 | 路径 | 大小 |
|------|------|------|
| 代码 | `ai-practice/src/grpo_simulation.py` | ~13 KB |
| 教学笔记 | `ai-practice/experiments/exp_008_grpo_simulation.md` | 本文件 |
| 训练曲线 (PNG) | `ai-practice/images/grpo/grpo_curves.png` | ~20 KB |
| 训练曲线 (PNG, failure case) | `ai-practice/images/grpo_mixed/grpo_curves.png` | ~20 KB |
| 完整指标 (JSON) | `ai-practice/images/grpo/grpo_run.json` | ~37 KB |
| 完整指标 (JSON, failure case) | `ai-practice/images/grpo_mixed/grpo_run.json` | ~37 KB |
| 文本摘要 | `ai-practice/images/grpo/grpo_summary.txt` | ~6 KB |
| 文本摘要 (failure case) | `ai-practice/images/grpo_mixed/grpo_summary.txt` | ~6 KB |

---

**执行者**：PracticeAgent / claude-sonnet-4.6  
**日期**：2026-06-21  
**任务**：T068（ai-practice maintenance）  
**配套报告**：T060（[推理模型三大流派详解_20260621.md](../../ai-learning/reports/knowledge_reports/推理模型三大流派详解_20260621.md)）

---
topic: "训练方法：RLHF·DPO·RLVR·SFT"
related_papers: ["#04 InstructGPT 2022", "#26 Tulu3 2024"]
last_updated: "2026-03-26"
---

# LLM 后训练方法深度解析

## RLHF 完整流程

### 核心问题
预训练的大语言模型（如 GPT-3）存在：
- **不遵循指令**：倾向续写而非回答问题
- **有害输出**：生成有害、虚假、有偏见内容
- **缺乏有用性**：回答冗长、跑题或不实用

RLHF（人类反馈强化学习）通过人类偏好信号对模型进行对齐。

### 三阶段流程

#### 阶段 1：监督微调（SFT）
**目标**：让模型学会"指令遵循"的基本格式

**过程**：
- 人工标注员编写 (指令, 高质量回答) 对
- InstructGPT 使用 ~13K 数据对
- 标准交叉熵损失微调

#### 阶段 2：奖励模型训练（RM）
**目标**：学习函数 r(prompt, response) → 分数，预测人类偏好

**数据收集**：
- 对同一 prompt，用 SFT 模型生成 4-9 个回答
- 人工标注员排序这些回答
- 生成比较对 (response_winner, response_loser)

**训练损失**（Ranking Loss）：
```
L = -E[log σ(r(x, y_w) - r(x, y_l))]
```

y_w（更好回答）获得更高分数。

**架构**：通常是较小语言模型（6B）顶部加线性层输出标量。

#### 阶段 3：PPO 强化学习优化
**算法**：PPO（Proximal Policy Optimization），稳定的策略梯度方法

**优化目标**：
```
maximize: E[r(x, y)] - β · KL(π_RL || π_SFT)
```

- **r(x, y)**：奖励模型分数（越高越好）
- **KL 散度惩罚**：防止偏离 SFT 模型太远，避免"奖励黑客"（Reward Hacking）
- **β**：KL 惩罚系数，权衡对齐与保持预训练知识

**为什么需要 KL 约束？** 没有 KL，模型可能找到奖励模型漏洞，生成高分但低质的输出。

### RLHF 挑战

| 挑战 | 说明 |
|------|------|
| 奖励黑客 | 模型找到奖励模型漏洞，生成虚高分数但实际低质的输出 |
| 标注者偏差 | 人类标注不一致，受文化背景影响，社会偏见 |
| 成本高昂 | 需要大量人工标注，速度慢，成本高 |
| 分布偏移 | 训练分布与实际使用分布不一致，导致泛化差 |
| 过度拒绝 | 模型过度谨慎，对合理请求也拒绝（安全对齐的副作用）|

---

## DPO 与改进方案

### DPO（Direct Preference Optimization，2023）

**核心洞察**：RLHF 的目标函数可以被重写为**二元分类损失**，无需单独奖励模型和 PPO！

**数学形式**：
```
L = -E[log σ(β · log(π_θ(y_w|x)/π_ref(y_w|x))
            - β · log(π_θ(y_l|x)/π_ref(y_l|x)))]
```

- y_w = 被偏好回复，y_l = 被拒绝回复
- π_θ = 待训练模型，π_ref = 参考模型（通常是 SFT 模型）

**直观理解**：同时提高好回复的概率，压低坏回复的概率，但无需中间的奖励模型。

**优势**：
- **无需奖励模型训练**
- **无需 PPO 的复杂采样**，直接用成对数据微调
- **训练更稳定**
- **代码简单**，只需标准语言建模损失+参考模型
- **显存高效**

**发现**：On-Policy 数据（用自己模型生成）> Off-Policy 数据（他人模型），偏好对质量 > 数量。

---

## Tulu 3 后训练三阶段（2024）

Allen Institute 发布最完整的开源后训练流程。

### 整体架构
```
Llama 3.1（基座）
    ↓
Stage 1: SFT（监督微调）
    ↓ 生成 ~939K 高质量指令-回复对
    ↓
Stage 2: DPO（直接偏好优化）
    ↓ 学习人类偏好
    ↓
Stage 3: RLVR（可验证奖励 RL）
    ↓ 在可自动验证的任务上 RL
    ↓
Tulu 3（性能媲美 GPT-4o-mini 和 Claude 3.5 Haiku）
```

### Stage 1：SFT 数据工程

**数据来源与配比**（总 ~939K 样本）：

| 来源 | 占比 | 特点 |
|------|------|------|
| Magpie（合成） | 60% | 模型自生成指令-回复，无人工 |
| FLAN Collection | 15% | 传统 NLP 任务 |
| StackExchange | 10% | 真实问答（编程、数学）|
| No Robots | 8% | 人工标注高质量对话 |
| 其他开源 | 7% | WizardLM-evol 等 |

**Magpie 数据合成**（核心创新）：
```python
prompt_template = "<|user|>\n"  # 仅用对话开头
instruction = llama3.generate(prompt_template)  # 模型续写指令
response = llama3.generate(instruction)         # 再自己回答
```

**优势**：海量、低成本、高多样性
**劣势**：质量参差，可能放大基座偏见

**数据质量过滤**：
1. MinHash LSH 去重
2. 有害内容分类过滤
3. LLM 指令跟随质量评分
4. 长度分布控制

### Stage 2：DPO 实现

相比 PPO 的三阶段，DPO 直接用偏好对微调。

**偏好数据**：
- On-Policy：用 SFT 阶段模型生成多个回复，人工/GPT-4 标注
- Ultrafeedback：大规模开源偏好数据集
- β=0.1（超参，控制 KL 惩罚强度）

### Stage 3：RLVR（可验证奖励强化学习）

**核心创新**：只在有**客观正确答案**的任务上做 RL，避免奖励黑客。

**思路对比**：
```
传统 RLHF：
  奖励 ← 人工标注偏好 ← 训练奖励模型 ← PPO（易被黑客）

RLVR：
  奖励 ← 任务的客观结果（代码测试通过？数学答案对？）
  优势：无法被黑客，信号精确可靠
```

**适合 RLVR 的任务**：
- ✓ 数学（答案一致性）
- ✓ 代码（单元测试通过）
- ✓ 逻辑推理（结论正确性）
- ✓ 结构化输出（JSON 格式合法）

**不适合**：创意写作、开放对话、风格偏好、模糊的安全边界

**实现**：
```python
for batch in training_data:
    responses = model.generate(batch.prompt, num_samples=8)

    rewards = []
    for response in responses:
        if task == "math":
            reward = 1.0 if extract_answer(response) == batch.answer else 0.0
        elif task == "code":
            reward = run_tests(response, batch.test_cases)  # 0~1
        rewards.append(reward)

    # 用 GRPO 更新模型
    baseline = mean(rewards)
    advantages = [r - baseline for r in rewards]
    loss = policy_gradient_loss(responses, advantages)
    optimizer.step(loss)
```

**GRPO（Group Relative Policy Optimization）**：
- 不需要单独价值函数网络
- 用同批次平均奖励作 baseline
- 超参数少，内存高效
- 适合稀疏/二元奖励

### 性能对标（Tulu 3 70B vs 商业模型）

| 基准 | Tulu 3 70B | GPT-4o-mini | Claude 3.5 Haiku |
|------|-----------|-------------|-----------------|
| MMLU | ~82% | ~82% | ~82% |
| GSM8K（数学）| ~92% | ~91% | ~90% |
| HumanEval（代码）| ~85% | ~87% | ~88% |
| AlpacaEval 2.0 | ~50% | ~50% | ~48% |

**阶段贡献**（消融）：
```
基座 Llama 3.1 70B
  ↓ +SFT
  大幅提升指令跟随（+20-30% on IFEval）
  ↓ +DPO
  提升对话质量和安全（+15% on AlpacaEval）
  ↓ +RLVR
  进一步提升数学和代码（+5-8%），不损害其他能力
```

---

## RLVR vs OpenAI o1

2024年出现两种 RL 路线：

| 维度 | RLVR（Tulu 3）| o1（OpenAI）|
|------|--------|-----------|
| RL 应用范围 | 可验证任务 | 广泛推理链 |
| 推理方式 | 直接回答 | Chain-of-Thought（长思维链）|
| 推理成本 | 正常 | 极高（token 数 10-100倍）|
| 开放性 | 完全开源 | 闭源 |
| 定位 | 通用指令跟随 | 专攻复杂推理 |

**核心差异**：o1 在推理时投入大量计算（Test-Time Compute），Tulu 3 在训练时通过 RL 提升能力。

---

## Constitutional AI（Anthropic）

改进传统 RLHF 的标注偏差问题：
- 不依赖人工排序标注
- 用 AI（如 Claude）自动评分，遵循一套"宪法"原则（安全、有用、诚实）
- 成本更低，速度更快，质量相当甚至超越人工

---

## 技术路线总结

**2022 年**：InstructGPT 开创 RLHF PPO 范式
**2023 年**：DPO 简化 RLHF，无需奖励模型
**2024 年**：RLVR（Tulu 3）和 o1（长推理）并行发展

当前趋势：
1. **DPO 已成主流**，更稳定高效
2. **RLVR 成为新热点**，适合有明确评估标准的任务
3. **Chain-of-Thought RL** 探索复杂推理
4. **Constitutional AI** 解决标注偏差

实践建议：无监督微调优先用 DPO；在代码/数学等可验证任务上尝试 RLVR；对齐和安全考量用 Constitutional AI 思路。

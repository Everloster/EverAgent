---
title: "Test-time Compute · Reasoning Models 深度解析"
domain: "ai-learning"
report_type: "concept_deep_dive"
status: "completed"
updated_on: "2026-04-09"
---

# Test-time Compute · Reasoning Models 深度解析

> 生成日期：2026-04-09 | 难度：⭐⭐⭐⭐⭐（专家级）
> 注意：本文严格区分「公开事实」与「合理推测」

## 🎯 知识定位

```
主题：Test-time Compute（推理时计算）与 Reasoning Models
所属领域：LLM/Reasoning · 推理增强
难度等级：⭐⭐⭐⭐⭐（专家级）
学习前置：Chain-of-Thought（CoT）、强化学习基础、Scaling Laws
关联概念：CoT / PRM / MCTS / GRPO / Self-Correction
```

## 🔍 层次一：类比

**考试 vs 复习**：传统方式（Training-time Compute）靠考前大量练习希望直接写出答案；Test-time Compute 是考时慢慢思考、画图、尝试不同方法——OpenAI o1/o3 和 DeepSeek-R1 就是这种"会考试"的 AI，代价是单次回答的计算量是普通模型的数十倍。

## 📖 层次二：核心定义

**Test-time Compute**：在推理阶段主动分配额外计算资源来提升输出质量的技术。公开事实：OpenAI 2024年9月技术报告明确将 o1 描述为"test-time scaling"范式产品。

**与 Training-time Scaling 的本质区别**：

| 维度 | Training-time Scaling | Test-time Compute |
|------|----------------------|-------------------|
| 发生时机 | 训练阶段 | 推理阶段 | 
| 计算归属 | 一次性预训练成本 | 每次请求付出 |
| Scaling 曲线 | 幂律，规模越大越好 | 存在收益递减拐点 |
| 适用场景 | 知识记忆、基础能力 | 多步推导、复杂决策 |

关键洞察（公开Benchmark数据）：AIME 2024 数学竞赛题上，o1-preview ~40%、o1 ~60%、o3-mini-high ~70%+；GPT-4o 等普通模型不足 10%。

## ⚙️ 层次三：技术细节

**OpenAI o1/o3（公开事实）**：2024年9月发布，AIME 2024 ~60%、GPQA Diamond ~85%、Codeforces #859。o3：ARC-AGI 87.5%、SWE-Bench >25%。内部架构不推测。

**DeepSeek-R1（2025年1月官方）**：GRPO（Group Relative Policy Optimization）—— PPO 变体，用 group 内相对排名估计 advantage，节省约 50% 内存。镜象概率：R1-Zero 训练中正确路径概率上升、错误路径对称下降，说明 RL 在相对概率空间有效修正。蒸馏：800K 推理样本微调 Qwen-7B，MATH 上超过 GPT-4o。QwQ-32B 同年发布。

**PRM vs ORM**：

| | ORM | PRM |
|--|-----|-----|
| 评估粒度 | 只看最终答案 | 每步质量 |
| 训练信号 | 稀疏 | 密集 |
| 标注成本 | 低 | 高 |
| 代表工作 | RLHF | Math-Shepherd, DeepSeek-R1 |

**Test-time Scaling 拐点**（合理推测）：问题需超过约 15-20 个推理步骤时，test-time compute 边际收益显著超过 scaling 预训练。

**MCTS**：AlphaCode（DeepMind 2022）将推理建模为树搜索，UCB1 选择节点扩展，PRM 评估路径价值。

**思考预算**（合理推测）：o1 API 的 `max_completion_tokens` 控制上限；模型学习 learned stopping criterion——难题用尽预算，简单问题提前终止。

## 💻 层次四：代码实现

### Self-Consistency（推理时 ensemble）

```python
from collections import Counter

def self_consistency_reasoning(model, tokenizer, prompt, n_samples=16, temperature=0.8):
    """多次采样 + 多数投票：test-time compute 最基础形式"""
    paths = []
    for _ in range(n_samples):
        input_ids = tokenizer.encode(f"{prompt}\nLet's think step by step.", return_tensors="pt")
        with model.no_grad():
            output_ids = model.sample(input_ids, max_new_tokens=512, temperature=temperature)
        paths.append(tokenizer.decode(output_ids[0], skip_special_tokens=True))
    answers = [p.split("The answer is")[-1].strip().split()[0] if "The answer is" in p else p.strip().split(".")[-1] for p in paths]
    return Counter(answers).most_common(1)[0][0], paths
```

### 简化版 MCTS

```python
import math
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class MCTSNode:
    state: str; parent: Optional['MCTSNode']; action: str
    children: List['MCTSNode']; visits: int = 0
    value: float = 0.0; reward: float = 0.0

class SimpleMCTS:
    def ucb1(self, node, parent_visits, c=1.414):
        if node.visits == 0: return float('inf')
        return node.value/node.visits + c*math.sqrt(math.log(parent_visits)/node.visits)

    def search(self, problem, n_simulations=100, max_depth=20):
        root = MCTSNode(state=problem, parent=None, action="", children=[])
        for _ in range(n_simulations):
            node = root
            while node.children:
                if len(node.children) < 4: break
                node = max(node.children, key=lambda c: self.ucb1(c, node.visits))
            if len(node.state.split()) < max_depth:
                node = self.expand(node)
            self.backpropagate(node, node.reward)
        return max(root.children, key=lambda n: n.value/max(n.visits,1)).state
```

### GRPO 训练步骤

```python
import torch
import torch.nn.functional as F

class GRPO:
    """Group-relative advantage（组内相对排名）替代 learnable critic，节省 50% 内存"""
    def compute_advantages(self, rewards):
        t = torch.tensor(rewards)
        return (t - t.mean()) / (t.std() + 1e-8)  # 组内相对排名

    def grpo_loss(self, log_probs_new, log_probs_old, advantages):
        ratio = torch.exp(log_probs_new - log_probs_old)
        clipped = torch.clamp(ratio, 0.8, 1.2)
        return -(torch.min(ratio * advantages, clipped * advantages)).mean()
```

## 🔬 层次五：前沿进展

| 模型 | 形式 | 公开信息 |
|------|------|---------|
| OpenAI o1/o3 | Extended CoT + RL | 2024年9月发布，数学/编程 benchmark 大幅领先 |
| DeepSeek-R1 | GRPO + 镜象概率 | 2025年1月开源 |
| Google Gemini Thinking | 扩展推理 | 2024年 Gemini 1.5 Pro/Ultra 内置 |
| AlphaCode 2 | MCTS + 采样 | DeepMind 2024 Codeforces |

**工程陷阱**：o1 API 成本是 GPT-4o 的 30-60 倍；推理时间数十秒到分钟；过度思考引入错误；PRM 标注成本高。

**Scaling Laws 关系**："训练时给模型知识，推理时给模型思考时间"——两者互补，非替代。

## ✅ 知识检验题

**基础**：1) Test-time Compute 定义与核心区别？ 2) CoT 为何只在 ≥100B 模型上涌现？ 3) o1 在 AIME 上从 <10% 提升到 ~60% 的主要原因？

**进阶**：4) PRM vs ORM 本质区别？ 5) 镜象概率现象说明了什么？ 6) 何时 test-time compute 比 scaling 预训练更划算？

**专家**：7) 生产系统分层推理架构设计？ 8) 从零训练 reasoning model 的 PRM 策略？ 9) 设计 test-time scaling 实验？

## 📚 学习资源

- [CoT 2022](https://arxiv.org/abs/2201.11903) | [OpenAI o1](https://openai.com/index/openai-o1/) | [Self-Consistency 2023](https://arxiv.org/abs/2203.11171)
- [DeepSeek-R1](https://arxiv.org/abs/2501.12599) | [GRPO](https://arxiv.org/abs/2502.03324) | [ToT 2023](https://arxiv.org/abs/2305.10601)
- [Math-Shepherd](https://arxiv.org/abs/2312.08935) | [AlphaCode 2](https://arxiv.org/abs/2403.19132)

## 📊 报告总结

- Test-time Compute 解决"推理深度"而非"知识广度"，是 training-time scaling 的补充
- o1/o3 和 DeepSeek-R1 证明了"推理时多思考"范式的工程可行性
- Web 搜索不可用；o1/o3 内部架构不推测；scaling 拐点数据为合理外推

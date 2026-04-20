# ai-practice Wiki Index

> 每次实验 ingest 后更新。按学习阶段分类，与 LEARNING_PATH.md 对应。

---

## 阶段 1 相关概念

| 概念 | 文件 | 一句话说明 |
|------|------|---------|
| Transformer 从零实现 | [transformer_from_scratch.md](concepts/transformer_from_scratch.md) | 纯 PyTorch 实现注意力、位置编码、Pre-LN 残差 |
| 分词 / Tokenization | [tokenization.md](concepts/tokenization.md) | BPE 子词分词，TikToken vs AutoTokenizer |

## 阶段 4 相关概念

| 概念 | 文件 | 一句话说明 |
|------|------|---------|
| LoRA 参数高效微调 | [lora_peft.md](concepts/lora_peft.md) | 低秩矩阵分解，0.5% 参数量完成微调 |
| GRPO 强化学习 | [grpo.md](concepts/grpo.md) | 无 Critic 的 PPO 变体，组内相对奖励 |
| SFT vs RLHF | [sft_vs_rlhf.md](concepts/sft_vs_rlhf.md) | 监督模仿 vs 强化学习探索的权衡 |
| Unsloth 框架 | [unsloth_framework.md](concepts/unsloth_framework.md) | Triton kernel 加速，2-5x 训练提速 |

## Entities（模型·框架）

| 实体 | 文件 | 类型 |
|------|------|------|
| Qwen 系列模型 | [../entities/qwen_series.md](entities/qwen_series.md) | 阿里云开源 LLM 系列 |

## Syntheses（综合查询存档）

（暂无，每当跨 ≥3 个概念综合查询时存档至此）

---

## 概念关系图

```
tokenization ──→ transformer_from_scratch ──→ lora_peft ──→ grpo
                                                          ↘ sft_vs_rlhf
                                           unsloth ──────→ grpo
```

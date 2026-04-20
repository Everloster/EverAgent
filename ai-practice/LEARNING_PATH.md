# LLM 工程实践学习路径

> 本路径覆盖从"手写 Transformer"到"微调大模型"的完整工程链，共 4 个阶段。
> 每个阶段独立可学，但建议按顺序完成。

---

## 总览

```
阶段 1 ──→ 阶段 2 ──→ 阶段 3 ──→ 阶段 4
Transformer    HF 生态    预训练模型    GRPO 微调
原理与实现     工程实践    快速上手      参数高效对齐
（基础）       （工具）    （应用）      （进阶）
```

---

## 阶段 1：Transformer 原理与从零实现

**Notebook**：[notebooks/01_transformer_from_scratch.ipynb](notebooks/01_transformer_from_scratch.ipynb)
**教学笔记**：[experiments/exp_001_transformer_from_scratch.md](experiments/exp_001_transformer_from_scratch.md)
**核心代码**：[src/model.py](src/model.py)

### 你将学到什么

- 缩放点积注意力（Scaled Dot-Product Attention）的数学原理和代码实现
- 多头注意力（Multi-Head Attention）的设计动机
- 位置编码（Positional Encoding）的正弦/余弦方案
- Pre-LN 与 Post-LN 的区别及其训练稳定性影响
- 自回归语言模型的训练与文本生成

### 前置知识（必须）

- [ ] Python 基础（列表、函数、类）
- [ ] PyTorch 基础：Tensor 操作、`nn.Module`、`autograd`
- [ ] 线性代数：矩阵乘法（`@`）、转置（`.T`）
- [ ] 概率：softmax、交叉熵损失

### 不需要提前了解的内容

- HuggingFace 或任何预训练模型库
- GPU 或 CUDA（CPU 可以运行教学规模的模型）
- Transformer 的理论（本实验会从头建立直觉）

### 预计时间：4-6 小时

### 硬件要求：CPU 即可（GPU 会快 5-10x）

### 学习成果检查点

完成阶段 1 后，你应该能回答：
1. 注意力权重矩阵的形状是什么？为什么要除以 √d_head？
2. 多头注意力相比单头有什么优势？
3. 为什么语言模型需要下三角 mask？
4. Pre-LN 结构中，LayerNorm 在残差连接的哪个位置？

---

## 阶段 2：Transformers 库快速上手

**Notebook**：[notebooks/02_transformers_library.ipynb](notebooks/02_transformers_library.ipynb)
**教学笔记**：[experiments/exp_003_transformers_library.md](experiments/exp_003_transformers_library.md)

### 你将学到什么

- HuggingFace `transformers` 库的三层 API（pipeline → AutoClass → 底层模型）
- 如何用一行代码完成情感分析、文本生成等常见 NLP 任务
- `AutoTokenizer` 和 `AutoModelForSequenceClassification` 的使用
- 预训练模型与手写模型的性能差距（why 工业规模重要）

### 前置知识

- [ ] 完成阶段 1（推荐，非必须）
- [ ] Python 环境管理（pip install）

### 预计时间：1-2 小时

### 硬件要求：无 GPU 需求（CPU 推理较慢但可用）

### 学习成果检查点

1. `pipeline("sentiment-analysis")` 和 `AutoModelForSequenceClassification` 哪个更灵活？哪个更简单？
2. `torch_dtype="auto"` 的作用是什么？
3. 同样是 Transformer，阶段 1 的教学模型和 BERT-base 的参数量差多少倍？

---

## 阶段 3：HuggingFace 生态工程实践

**Notebook**：[notebooks/03_huggingface_api.ipynb](notebooks/03_huggingface_api.ipynb)
**教学笔记**：[experiments/exp_002_huggingface_basics.md](experiments/exp_002_huggingface_basics.md)
**工具脚本**：[src/load_local_dataset.py](src/load_local_dataset.py)

### 你将学到什么

- 如何下载和管理 HuggingFace Hub 上的模型（包括国内镜像配置）
- 本地缓存扫描与路径管理
- `datasets` 库的加载与处理
- 离线使用 HuggingFace 模型（无需每次联网）

### 前置知识

- [ ] Python 文件系统操作（`os.path`、`pathlib`）

### 预计时间：30-60 分钟

### 硬件要求：稳定网络连接（首次下载）

### 注意

本阶段以 Qwen2.5-3B-Instruct 为示例，首次下载约需 **6GB 磁盘空间**（4-bit 量化版约 2GB）。
国内用户请先配置 HF 镜像：
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

---

## 阶段 4：参数高效微调与 RLHF 对齐

**Notebook**：[notebooks/04_qwen25_grpo_finetuning.ipynb](notebooks/04_qwen25_grpo_finetuning.ipynb)
**教学笔记**：[experiments/exp_004_qwen25_grpo_finetune.md](experiments/exp_004_qwen25_grpo_finetune.md)

### 你将学到什么

- LoRA（低秩适应）的原理与配置（lora_rank 的作用）
- 4-bit NF4 量化：如何在有限显存下运行大模型
- GRPO 强化学习微调：与 SFT 的对比，奖励函数设计
- Unsloth 框架加速训练
- 模型保存与 LoRA 权重加载

### 前置知识

- [ ] 了解 Transformer 架构（完成阶段 1 或有等效知识）
- [ ] 理解 LoRA 基本概念（见 [wiki/concepts/lora_peft.md](wiki/concepts/lora_peft.md)）
- [ ] 了解什么是强化学习（基本概念即可）

### 预计时间：4-8 小时（含模型下载和训练时间）

### 硬件要求：GPU ≥ 8GB 显存（4-bit 量化），推荐 24GB+（16-bit）

### 注意

- 若没有 GPU，可以阅读 notebook 理解流程，但无法实际运行训练
- 首次运行前，先完成阶段 3 配置 HF 镜像并下载 Qwen2.5-3B

### 学习成果检查点

1. LoRA 为什么能大幅减少可训练参数量？rank=64 意味着什么？
2. 4-bit 量化相比 16-bit，精度损失大约有多少？
3. GRPO 为什么不需要 Critic 网络？Group 大小如何影响训练稳定性？
4. 训练完成后，如何合并 LoRA 权重到基础模型？

---

## 推荐学习顺序

### 完整路径（推荐）
```
阶段 1 → 阶段 2 → 阶段 3 → 阶段 4
```
适合：从零开始系统学习 LLM 工程

### 快速路径（有 PyTorch 基础）
```
阶段 1（快速过，重点关注注意力机制）→ 阶段 4
```
适合：已经了解深度学习，希望快速进入微调实践

### 工程师路径（不关心原理）
```
阶段 3 → 阶段 2 → 阶段 4
```
适合：只想用预训练模型做应用开发

---

## 章节地图

| 阶段 | Notebook | 教学笔记 | Wiki 概念 | 难度 |
|------|---------|---------|---------|------|
| 1 | [01_transformer_from_scratch](notebooks/01_transformer_from_scratch.ipynb) | [exp_001](experiments/exp_001_transformer_from_scratch.md) | [transformer_from_scratch](wiki/concepts/transformer_from_scratch.md) · [tokenization](wiki/concepts/tokenization.md) | ⭐⭐ |
| 2 | [02_transformers_library](notebooks/02_transformers_library.ipynb) | [exp_003](experiments/exp_003_transformers_library.md) | — | ⭐ |
| 3 | [03_huggingface_api](notebooks/03_huggingface_api.ipynb) | [exp_002](experiments/exp_002_huggingface_basics.md) | — | ⭐ |
| 4 | [04_qwen25_grpo_finetuning](notebooks/04_qwen25_grpo_finetuning.ipynb) | [exp_004](experiments/exp_004_qwen25_grpo_finetune.md) | [grpo](wiki/concepts/grpo.md) · [lora_peft](wiki/concepts/lora_peft.md) · [sft_vs_rlhf](wiki/concepts/sft_vs_rlhf.md) · [unsloth](wiki/concepts/unsloth_framework.md) | ⭐⭐⭐⭐ |

---

## 后续扩展方向

完成 4 个阶段后，可以探索：

- **LoRA rank 消融实验**：rank=8 vs 16 vs 64 的微调效果对比
- **SFT vs GRPO 对比**：相同数据量下，两种方法在 GSM8K 上的准确率差异
- **vLLM 推理加速**：对比 `use_vllm=True/False` 的推理吞吐量（tokens/s）
- **更大规模 Transformer**：将 `d_model` 从 64 扩展到 256，观察训练曲线变化
- **量化精度对比**：4-bit vs 8-bit vs 16-bit 在推理准确率和速度上的权衡

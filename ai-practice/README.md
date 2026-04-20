# AI Practice — LLM 工程实践教程

> 从"手写 Transformer"到"微调大模型"的完整工程实践路径。
> 4 个阶段，涵盖 LLM 核心工程技能。

---

## 你将学到什么

| 阶段 | 内容 | 技术栈 |
|------|------|--------|
| 1 — 原理 | 从零实现 Transformer 语言模型 | PyTorch、TikToken |
| 2 — 工具 | Transformers 库三层 API | HuggingFace Transformers |
| 3 — 生态 | HuggingFace Hub 模型与数据集管理 | huggingface_hub、datasets |
| 4 — 微调 | Qwen2.5-3B GRPO 强化学习微调 | Unsloth、TRL、PEFT |

---

## 快速开始

```bash
# 1. 检查你的硬件环境
python src/check_hardware.py

# 2. 阅读学习路径，选择入口
cat LEARNING_PATH.md

# 3. 配置环境（按各阶段需求安装）
cat SETUP.md

# 4. 打开第一个 Notebook
jupyter notebook notebooks/01_transformer_from_scratch.ipynb
```

---

## 前置知识

**必须掌握**：
- Python（列表、函数、类、文件操作）
- PyTorch 基础（Tensor、`nn.Module`、梯度计算）

**推荐了解**（不强制）：
- 矩阵乘法和 softmax 函数
- 什么是语言模型（predict next token）

**不需要提前了解**：
- Transformer 论文
- HuggingFace 生态
- GPU/CUDA

---

## 目录结构

```
ai-practice/
├── LEARNING_PATH.md          ← 从这里开始！学习路径和章节地图
├── SETUP.md                  ← 环境配置指南
├── CONTEXT.md                ← 已有实验清单（防重复）
│
├── notebooks/                ← 可运行的 Jupyter Notebooks
│   ├── 01_transformer_from_scratch.ipynb   （阶段 1）
│   ├── 02_transformers_library.ipynb        （阶段 2）
│   ├── 03_huggingface_api.ipynb             （阶段 3）
│   └── 04_qwen25_grpo_finetuning.ipynb      （阶段 4）
│
├── src/                      ← 可复用的 Python 模块
│   ├── model.py              # 完整 Transformer 实现（教学版）
│   ├── inference.py          # 交互式推理脚本
│   ├── check_hardware.py     # 硬件兼容性检查
│   └── load_local_dataset.py # 数据集加载工具
│
├── experiments/              ← 教学笔记（每个 notebook 对应一篇）
│   ├── exp_001_transformer_from_scratch.md
│   ├── exp_002_huggingface_basics.md
│   ├── exp_003_transformers_library.md
│   └── exp_004_qwen25_grpo_finetune.md
│
├── wiki/                     ← 概念知识库
│   ├── index.md              # 概念索引
│   └── concepts/             # 核心概念深度解析
│       ├── transformer_from_scratch.md
│       ├── grpo.md
│       ├── lora_peft.md
│       ├── unsloth_framework.md
│       ├── sft_vs_rlhf.md
│       └── tokenization.md
│
├── data/                     ← 训练数据
│   └── sales_textbook.txt    # 阶段 1 训练数据
│
└── images/                   ← 架构图
    └── *.png
```

---

## 章节地图

```
01_transformer_from_scratch ─┐
                              ├─→ 02_transformers_library
                              └─→ 03_huggingface_api ──→ 04_qwen25_grpo_finetuning
```

详见 [LEARNING_PATH.md](LEARNING_PATH.md)。

---

## 学习资源索引

| 资源类型 | 链接 | 说明 |
|---------|------|------|
| 学习路径 | [LEARNING_PATH.md](LEARNING_PATH.md) | 4 阶段路径、时间估算、前置知识 |
| 环境配置 | [SETUP.md](SETUP.md) | pip 安装命令、镜像配置、常见报错 |
| 概念索引 | [wiki/index.md](wiki/index.md) | 核心概念快速查阅 |
| Transformer 教学笔记 | [experiments/exp_001](experiments/exp_001_transformer_from_scratch.md) | 含思考题和参考资料 |
| GRPO 教学笔记 | [experiments/exp_004](experiments/exp_004_qwen25_grpo_finetune.md) | 含实际训练数值 |

---

*EverAgent 项目 `ai-practice` 子模块 | PracticeAgent 负责 | 执行协议见 `AGENTS.md`*

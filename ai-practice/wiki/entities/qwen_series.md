# Qwen 系列模型（通义千问）

> 类型：模型系列 | 开发方：Alibaba Cloud（阿里巴巴）

---

## 基本信息

- **全名**：Qwen（通义千问，Tongyi Qianwen）
- **开发方**：Alibaba Cloud / Qwen Team
- **开源协议**：Qwen 系列大部分模型采用 Apache 2.0 或 Qwen 自定义协议

## 在 ai-practice 中使用的版本

| 模型 | 参数量 | 实验 | 用途 |
|------|--------|------|------|
| Qwen2.5-3B-Instruct | 30亿 | exp_002, exp_004 | HuggingFace 下载实践；GRPO 微调 |

## Qwen2.5-3B-Instruct 规格

- **架构**：仅解码器 Transformer（GQA 注意力）
- **上下文长度**：32,768 tokens（原生）
- **训练数据**：18T tokens（Qwen2.5 系列）
- **特点**：Instruct 版本经过 SFT + RLHF 对齐，适合指令跟随

## HuggingFace 信息

- **repo_id**：`Qwen/Qwen2.5-3B-Instruct`
- **下载方式**：`snapshot_download()` 或 `from_pretrained()`
- **国内镜像**：`HF_ENDPOINT=https://hf-mirror.com`（见 exp_002）

# 多模态理解模型（Multimodal Understanding Models）

## 简介

多模态理解（vision + text → text）是 LLM 下一阶段能力边界，2024-05 至 2026-06 不到 26 个月从"外挂视觉头"演化为"原生统一架构"。四大代表：OpenAI GPT-4o / Anthropic Claude 3.5 Vision / Google Gemini 2.5 / Alibaba Qwen2.5-VL。

## 核心特征

- **原生多模态预训练**：模态在 token 层面融合（GPT-4o、Gemini）vs Adapter 外挂（Claude 早期、LLaVA）
- **长上下文**：128K → 200K → 1M → 2M 三级跨越
- **视觉 Agent**：Computer Use（Claude 2024-10）开启 GUI 自动化
- **开源追平闭源**：Qwen2.5-VL 72B 13 项评测超越 GPT-4o / Claude 3.5

## 四家核心差异

| 厂商 | 旗舰 | 架构 | 上下文 | 核心优势 |
|------|------|------|--------|----------|
| OpenAI | GPT-4o | 原生 omni early fusion | 128K→1M | 实时音视频 + 生态 |
| Anthropic | Claude 3.5 Sonnet | Adapter → 后期融合 | 200K | 文档理解 + 计算机操作 |
| Google | Gemini 2.5 Pro | 原生多模态 + 稀疏 MoE | 1M-2M | 长视频 + Vision Arena #1 |
| Alibaba | Qwen2.5-VL 72B | 原生 + M-RoPE | 128K | 开源 + 视觉 Agent |

## 关键 Benchmark

- MMMU（大学级多模态）：Gemini 2.5 Pro 81.7% > GPT-4o 69.1%
- ChartQA（图表问答）：Claude 3.5 Sonnet 90.8% > Qwen2.5-VL 88.8%
- DocVQA（文档问答）：Qwen2.5-VL 96.5% > Claude 3.5 Sonnet 95.2%

## 关键演化节点

- 2020-10 · CLIP（OpenAI）：对比学习图文对齐
- 2023-04 · LLaVA（Microsoft）：视觉 Instruction Tuning
- 2023-12 · Gemini 1.0：原生多模态首发
- 2024-05 · GPT-4o：原生 omni + 实时音频
- 2024-10 · Claude 3.5 Sonnet Computer Use：开启 GUI Agent
- 2025-01 · Qwen2.5-VL 72B：开源追平闭源
- 2025-03 · Gemini 2.5 Pro：Vision Arena 登顶

## 相关链接

- 报告：`ai-learning/reports/knowledge_reports/多模态理解模型对比_GPT4o_Claude_Gemini_QwenVL_20260621.md`
- 推理模型：`concepts/test_time_compute.md`
- 多模态生成：`concepts/generative_models_evolution.md`
- 世界模型：`concepts/world_models.md`
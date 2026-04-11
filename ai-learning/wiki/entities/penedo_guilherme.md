# Guilherme Penedo

> RefinedWeb 第一作者，Technology Innovation Institute (TII)，Falcon LLM 核心贡献者

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | Guilherme Penedo |
| 机构 | Technology Innovation Institute (TII), Abu Dhabi, UAE |
| 核心贡献 | RefinedWeb 数据集，Falkon LLM 预训练 |
| 代表作 | "The RefinedWeb Dataset for Falkon LLM" (2023) |

## 学术脉络

```
TII (Technology Innovation Institute)
    └── Falkon LLM 系列 (2023)
         ├── Falkon-1B/7B/40B
         ├── 在 RefinedWeb 上训练
         └── 开源 LLM 新基准（超越 LLaMA）

    └── RefinedWeb (2023, Penedo et al.)
         ├── 5T tokens 高质量文本
         ├── Progressive Quality Filtering
         └── 为 Falkon 提供数据基础
```

## 核心贡献：RefinedWeb

### 数据工程方法论

```
RefinedWeb 的 6 阶段流水线：
  1. URL 去重（~50% 去除率）
  2. 文本提取（high-precision HTML parser）
  3. 语言识别（FastText，英文置信度 > 0.65）
  4. 质量过滤（统计特征 + LM perplexity + 结构分析）
  5. 毒性过滤（保守，关键词 + 二分类模型）
  6. 文档级去重（MinHash + LSH）

核心洞察：
  "Progressive filtering > single-pass filtering"
  → 不同维度的问题用不同工具检测
  → 只删除明确有问题的样本
```

## 在本项目中的关联

- 直接关联报告：`30_refinedweb_2023.md`
- 关联论文：Scaling Laws (#05) — 数据规模理论基础；The Pile — 数据集对比
- 概念关联：`high_quality_pretraining_data.md`（高质量预训练数据）

## Falkon LLM 的成就

| 模型 | MMLU | HellaSwag | 数据集 |
|------|------|-----------|--------|
| LLaMA-7B | 35.1 | 71.3 | The Pile |
| **Falkon-7B** | **37.4** | **74.8** | RefinedWeb |
| LLaMA-65B | 48.8 | 78.6 | The Pile |
| **Falkon-40B** | **55.8** | **81.4** | RefinedWeb |

RefinedWeb 的高质量数据让 Falkon-7B 超越 LLaMA-7B。

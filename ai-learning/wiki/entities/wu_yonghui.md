# Yonghui Wu

> GNMT (Google Neural Machine Translation System) 第一作者，Google Brain

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | Yonghui Wu |
| 机构 | Google Brain |
| 核心贡献 | GNMT — Google 神经机器翻译系统，Seq2seq 工业化 |
| 代表作 | "Google's Neural Machine Translation System" (2016) |

## 学术脉络

```
Google Brain 研究员
    └── GNMT (2016)
         ├── 深层 LSTM (8+8 layers) + 残差连接
         ├── WordPiece 分词
         ├── Attention 机制
         └── 工业部署于 Google Translate (2016.11)
```

## 核心贡献：GNMT

### 主要技术成就

```
1. 深层残差 LSTM：
   - 8 层 Encoder + 8 层 Decoder
   - 残差连接使深层网络训练可行

2. WordPiece 分词：
   - 子词级 tokenization
   - 解决 OOV 问题
   - 成为后续 LLM tokenizer 的基础

3. 工业级部署：
   - 首次 NMT 在 billion 级别生产系统运行
   - 中英翻译 BLEU 提升 60%
```

## 在本项目中的关联

- 直接关联报告：`39_google_translate_2016.md`
- 关联论文：Transformer (#01) — 技术传承关系
- 概念关联：`neural_machine_translation.md`

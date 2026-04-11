# Technology Innovation Institute (TII)

> 阿联酋技术创新研究院，Falcon LLM 与 RefinedWeb 的诞生地

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | Technology Innovation Institute (TII) |
| 所在地 | Abu Dhabi, UAE（阿布扎比） |
| 隶属于 | 阿联酋先进技术委员会 (ATC) |
| 核心成果 | Falcon LLM、RefinedWeb 数据集 |

## 核心产品

### Falcon LLM 系列

```
Falcon-1B / Falcon-7B / Falcon-40B (2023.03)：
  - 首个超越 LLaMA 的开源大模型
  - 训练数据：RefinedWeb（5T tokens）
  - 开源后下载量超过 100 万次

Falcon 2 (2023.11)：
  - Falkon-7B/11B/180B
  - 继续使用 RefinedWeb 扩展版
  - 180B 版本采用 mixture-of-experts

开源许可：
  - Falkon-7B/40B：TII Falcon License
  - Falkon-2：Apache 2.0
```

### RefinedWeb 数据集

```
RefinedWeb (2023.06)：
  - 5T tokens（GPT-2 tokenizer）
  - 来自 CommonCrawl 的高质量清洗数据
  - 包含英文（3.5T）和多语言（1.5T）版本

构建方法论：
  1. URL 去重
  2. 文本提取
  3. 语言识别
  4. 质量过滤（Progressive Multi-level）
  5. 毒性过滤
  6. 文档级去重
```

## 在本项目中的关联

- 直接关联报告：`30_refinedweb_2023.md`
- 关联实体：Guilherme Penedo、RefinedWeb
- 概念关联：`high_quality_pretraining_data.md`

## 战略意义

```
TII 的崛起代表了：
  1. 海湾国家的 AI 战略布局
     → 阿联酋将 AI 列为国家战略
     → TII 是核心技术研发机构

  2. 开源 AI 的全球扩散
     → AI 能力不再集中于中美
     → 中东成为新的 AI 玩家

  3. 数据即护城河
     → RefinedWeb 证明了数据质量的重要性
     → TII 的竞争优势建立在高质量数据工程上
```

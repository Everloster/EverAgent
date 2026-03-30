# EverAgent 全局变更记录

> 记录各子项目的研究进展与重大变更

---

## 2026-03-30

### 项目优化（任务1，Claude Sonnet 4.6）
- 全量重写 `docs/LEARNING_PROJECTS_TASK_BOARD.md`：同步至当前实际内容量，修正所有过时任务建议
- 修复 `cs-learning/CONTEXT.md` 防幻觉漏洞：CSP #18 报告已存在但未录入，错误地出现在"下一步推荐"中
- 补充 CHANGELOG 缺失的 03-27、03-28 条目
- 更新 `README.md` 全局内容量数据

### ai-learning
- 新增 KV Cache 深度解析（推理工程核心机制·GQA/MQA/PagedAttention）

### cs-learning
- 确认 TCP/IP (#19) 报告（03-27 已完成）正式录入 CONTEXT.md

### philosophy-learning
- 新增 亚里士多德《尼各马可伦理学》文本分析（eudaimonia·功能论证·德性习惯论·与康德义务论对照）

---

## 2026-03-28

### ai-learning
- 新增 Word2Vec (2013) 论文精读报告
- 新增 DINOv2 (2023) 论文精读报告 + DINOv2 深度解析知识报告

### psychology-learning
- 新增 Tversky & Kahneman (1974) 启发式与偏差论文精读报告
- 新增 Bandura Bobo 娃娃实验 (1961) 论文精读报告

### philosophy-learning
- 新增 康德《道德形而上学基础》文本分析（绝对命令·义务论奠基）

### biology-learning
- 新增 Social Jetlag 与代谢综合征 (2017) 论文精读报告

---

## 2026-03-27

### cs-learning
- 新增 TCP/IP (1974, Cerf & Kahn) 论文精读报告
- 新增 Lamport Clocks (1978) 论文精读报告
- 新增 GFS (2003) 论文精读报告
- 新增 Dynamo (2007) 论文精读报告
- 新增 Spanner (2012) 论文精读报告
- 新增 Paxos Made Simple (2001) 论文精读报告
- 新增 Kafka (2011) 论文精读报告
- 新增 UNIX (1974) 论文精读报告
- 新增 ZooKeeper (2010) 论文精读报告
- 新增 FFS (1984) 论文精读报告
- 新增 Byzantine Generals (1982) 论文精读报告
- 新增 CSP (1978, Hoare) 论文精读报告
- 新增 Raft (2014) 论文精读报告

### psychology-learning
- 新增 Festinger & Carlsmith (1959) 认知失调实验精读报告
- 新增 Kahneman & Tversky (1979) 前景理论精读报告
- 新增 Seligman & Maier (1967) 习得性无助精读报告
- 新增 Darley & Latané (1968) 旁观者效应精读报告
- 新增 Asch (1951) 从众实验精读报告
- 新增 Zimbardo (1971) 斯坦福监狱实验精读报告
- 新增 Rosenhan (1973) 精神病诊断实验精读报告

### ai-learning
- 新增 AlexNet (2012) 论文精读报告
- 新增 ViT (2020) 论文精读报告
- 新增 CLIP (2021) 论文精读报告
- 新增 LLaMA (2023)、LLaMA-2 (2023)、Mistral 7B (2023) 论文精读报告
- 新增 Swin Transformer (2021)、MAE (2022)、FlashAttention (2022) 论文精读报告
- 新增 LoRA 深度解析、Scaling Laws 深度解析知识报告

### biology-learning
- 新增 Social Jetlag and Obesity (2012) 论文精读报告
- 新增 Sleep GH (1988)、GH Sleep Physiology (1996) 论文精读报告

### philosophy-learning
- 新增 柏拉图《理想国》洞穴比喻文本分析
- 新增 柏拉图《美诺》文本分析
- 新增 知识跨时代比较概念报告

---

## 2026-03-26

### ai-learning
- 新增 DDPM (2020) 论文精读报告
- 新增 GAN (2014) 论文精读报告

### github-trending-analyzer
- 新增 2026-03-25 daily trending 报告 + 4 篇 Repo 深度分析

---

## 2026-03-25

### ai-learning
- 新增 ResNet (2015)、InstructGPT (2022)、Chain-of-Thought (2022) 论文精读报告
- 新增 LoRA 深度解析、Scaling Laws 深度解析
- 新增 Scaling Laws (2020) 论文精读报告

### cs-learning
- 新增 Bigtable (2006) 论文精读报告

### github-trending-analyzer
- 规范化技能文档·修复报告质量·建立变更记录

---

## 2026-03-24

### cs-learning
- 新增 Turing (1950)、Shannon (1948)、MapReduce (2004) 论文精读报告
- 新增 CS 关键人物图谱
- 创建 CS 发展时间线与学习路径规划

### psychology-learning
- 新增 Miller (1956)、Milgram (1963) 论文精读报告
- 新增心理学关键人物图谱
- 创建心理学发展时间线与学习路径规划

### philosophy-learning
- 新增 Gettier (1963)、Descartes Meditations (1641) 文本分析
- 新增哲学关键人物图谱
- 创建哲学发展时间线与学习路径规划

---

## 2026-03-23

### 项目初始化
- 创建 EverAgent 仓库，建立三层上下文架构（AGENTS.md → CONTEXT.md → 报告文件）
- ai-learning：导入 32 篇论文索引、Transformer/BERT/GPT-3 精读报告、知识库
- biology-learning：创建项目结构，完成「晚型人作息与力量训练」概念报告
- 建立防幻觉边界规则与离线知识库体系

---

## 格式约定
- 按日期倒序排列（最新在前）
- 每个子项目独立一节
- 变更描述简洁，一行一项

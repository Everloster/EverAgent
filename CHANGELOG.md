# EverAgent 全局变更记录

> 记录各子项目的研究进展与重大变更

---

## 2026-04-22

### 基础设施重构 v2.0（Trae Kimi-2.6）
- **Phase 0 模块化**：提取 `scripts/ea_common.py` 共享库，统一时间/YAML/路径工具
- **Phase 1 事件溯源**：新增 `scripts/ea_events.py`，所有任务状态变更自动记录到 `events/`，支持完整审计追溯
- **Phase 2 语义元数据**：扩展报告 frontmatter 规范，新增 `semantic_tags`、`related_concepts`、`related_entities`
- **Phase 3 声明式任务 DSL**：新增 `scripts/ea_task_dsl.py`，支持 `tasks/T*.yaml` 自描述任务定义，含依赖图、资源声明、质量门禁
- **Phase 4 实时 Dashboard**：新增 `scripts/ea_dashboard.py`（FastAPI + SSE），提供暗色主题 Web UI 实时展示任务状态、Agent 性能、事件流
- **Phase 5 自进化引擎**：新增 `scripts/ea_evolution.py`，自动分析任务完成时间、Agent 成功率、项目健康度，生成优化建议任务
- **CLI 集成**：`everagent.py` 新增 `evolve` 和 `dashboard` 子命令，统一入口
- 新增示例任务 `tasks/T030.yaml`（Agent 可观测性架构设计）

---

## 2026-04-21

### 新增子项目：ai-practice（Claude Sonnet 4.6）
- 从 Neverland/ML 迁移，创建第 7 个子项目 `ai-practice`（LLM 工程实践教学）
- 注册 PracticeAgent，写入全局 AGENTS.md §1 注册表 & docs/agents_registry.yaml
- 4 个 notebook 按阶段重命名（01_transformer → 04_qwen25_grpo）
- 删除空目录（papers/, books/, reports/, knowledge/）
- 全部 experiments/ 改写为 6 节教学笔记格式（含 WHY 部分 + 思考题 + 参考资料）
- Wiki 概念页面从 ~30 行深化至 150+ 行（新增 lora_peft.md、tokenization.md）
- 新建 LEARNING_PATH.md（4 阶段路线）、SETUP.md（环境配置指南）、skills/experiment_analysis/SKILL.md
- `03_huggingface_api.ipynb` 大幅改写：补全中文注释 + 镜像配置 + 错误处理说明
- README.md 从 Agent 任务说明改写为学生指南

### 全局
- README.md 项目总览更新：6 个子项目 → 7 个子项目，新增 ai-practice 行

---

## 2026-04-01

### 项目优化（任务1，Claude Opus 4.6）
- 修复 7 个报告文件的 YAML frontmatter 缺失（Byzantine Generals、Rosenhan 补全 frontmatter；KV Cache、DINOv2、Kant、Aristotle、Bandura 补齐字段）
- 同步 Task Board 已完成列表（+ZeRO/Chord/Harlow），更新 P1/P2 推荐池
- README 数据同步至实际数量（ai:24, cs:19, philosophy:7, psychology:12）
- 清理 5 个 CONTEXT.md 防幻觉区：移除已完成标记堆积，只保留未研究项
- 新增 biology-learning/roadmap/Learning_Roadmap.md（4 阶段学习路径）
- 引入 Git LFS 管理 31 个 PDF 文件（164MB），添加 LFS 用量监控（700MB WARN / 950MB ERROR）
- 新增 pre-commit hook：提交前自动运行 validate_workspace.py
- 删除 ai-learning ZeRO 重复文件（25_zero_2019_分析报告.md）
- 统一报告文件命名规范（移除中文后缀 `_分析报告`）

### ai-learning
- 新增 MoE #21（2017）稀疏门控混合专家论文精读
- 新增 ZeRO #25（2019）分布式训练内存优化论文精读

### cs-learning
- 新增 Chord #28（2001）P2P 查找协议论文精读
- 新增 Chubby #29（2006）分布式锁服务论文精读

### philosophy-learning
- 新增 Nagel（1974）What Is It Like to Be a Bat? 文本分析

### psychology-learning
- 新增 Harlow（1958）恒河猴实验论文精读

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

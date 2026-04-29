# LLM Evaluation Systems

> 所属分类：核心概念（Core Concept）
> 相关报告：[LLM_评估体系_深度解析_20260429.md](../../reports/knowledge_reports/LLM_评估体系_深度解析_20260429.md)
> 关联概念：LLMs+ / Agent Systems / Test-time Compute / RAG / Long Context

## 什么是 LLM 评估体系？

LLM 评估体系是用于衡量大语言模型能力、风险、成本与适用场景的一组 benchmark、leaderboard、评测协议和私有任务集。它不是单一榜单，而是一个多维诊断框架。

核心思想：**先定义场景，再选择评测**。通用聊天、中文客服、代码代理、工具调用、长文档问答、科学推理、多模态文档和安全高风险应用，对应的有效评测完全不同。

## 主流评估范式

| 范式 | 代表评测 | 适合判断 |
|------|----------|----------|
| 静态闭卷 | MMLU / C-Eval / CMMLU | 基础知识与考试式推理 |
| 动态去污染 | LiveBench / LiveCodeBench / HLE | 前沿模型区分、抗背题 |
| 偏好评测 | Chatbot Arena / MT-Bench / SuperCLUE | 开放式回答体验 |
| 代码工程 | BigCodeBench / SWE-bench | 编程与真实 repo 修复 |
| 工具调用 | BFCL / τ-bench / GAIA | API、工具、agent 工作流 |
| 多模态 | MMMU / MMBench / DocVQA | 图文、文档、图表理解 |
| 安全对齐 | HELM Safety / HarmBench / JailbreakBench | 风险、拒答、越狱鲁棒性 |

## 读榜原则

1. **总榜不是场景答案**：子榜和任务分布比 overall ranking 更重要。
2. **偏好不等于正确**：Arena 高分说明用户更喜欢，不保证事实、数学、代码都正确。
3. **静态高分不等于真实执行**：MMLU/C-Eval 高分不能替代 SWE-bench、BFCL、WebArena 等工作流评测。
4. **Agent 榜包含 harness 能力**：SWE-bench/WebArena/OSWorld 成绩往往是模型与系统工程共同结果。
5. **企业必须自建私有 eval**：公开榜只做初筛，最终要用真实业务任务、成本、延迟、安全和合规评测决策。

## 场景优先级速查

| 场景 | 优先看 |
|------|--------|
| 通用聊天 | LMArena / MT-Bench / WildBench |
| 中文应用 | SuperCLUE / C-Eval / CMMLU / OpenCompass |
| 科学推理 | GPQA / HLE / AIME / LiveBench |
| 代码补全 | BigCodeBench / LiveCodeBench / HumanEval |
| Coding Agent | SWE-bench Verified/Pro / BigCodeBench |
| 工具调用 | BFCL / τ-bench / GAIA |
| 长文档 | LongBench / RULER / 私有文档集 |
| 多模态文档 | MMMU / DocVQA / ChartQA / VHELM |
| 高风险行业 | HELM Safety / HarmBench / 私有红队集 |

## 开放问题

- 如何在动态 benchmark 与可复现之间取得平衡？
- 如何减少 LLM-as-Judge 的裁判偏差？
- 如何区分底座模型能力与 agent harness 工程能力？
- 如何把公开 benchmark 转化为企业可维护的持续评测流水线？
- 如何评估长期任务中的权限、安全、审计与失败恢复？

## 关键引用

- Stanford HELM: Holistic Evaluation of Language Models
- LMSYS / LMArena: Chatbot Arena and MT-Bench
- OpenCompass: Universal Evaluation Platform for Foundation Models
- C-Eval / CMMLU / SuperCLUE: Chinese LLM evaluation suites
- LiveBench: contamination-resistant dynamic benchmark
- SWE-bench: real-world software issue resolution
- BFCL: Berkeley Function Calling Leaderboard


# Agent Systems（智能体系统）

> 维护日期：2026-04-09 | 分类：AI Agent / LLM 推理增强

---

## 概念定义

**Agent System（智能体系统）** 是以大语言模型（LLM）为核心理推理引擎，通过**工具调用**（Tool Use）与外部环境交互，同时维持**记忆状态**（Memory），以自主完成复杂多步任务的系统性架构。

Agent Systems 的核心三要素：
1. **LLM（大脑）**：负责推理、规划、决策
2. **Tools（手足）**：搜索、计算、API 调用、文件操作等
3. **Memory（记忆）**：短期上下文 + 长期向量记忆

---

## ReAct vs. Tool Use vs. MCP：区分与联系

这是三个不同层次的概念：

### ReAct（范式层）

**ReAct = Reasoning + Acting**，由 Yao et al. (Google Research, 2022) 提出，是一种让 LLM 交替生成推理步骤（Thought）和动作指令（Action）的**思考框架**。

ReAct 的核心循环：
```
Thought: 我需要查什么？
  → Action: search[关键词]
  → Observation: 搜索结果
  → Thought: 基于结果继续推理
  → ... 直到完成
```

关键洞察：ReAct 的 Action 输出的是**自然语言描述**（如 "search[北京天气]"），这意味着 Action 的格式是自由文本，存在歧义性。

### Tool Use / Function Calling（执行层）

Tool Use 是 LLM 调用外部工具的**能力统称**。Function Calling 是 OpenAI 在 2023 年 6 月引入的**结构化工具调用格式**，用预定义 JSON Schema 约束工具名称和参数。

**联系**：Function Calling 是 ReAct 中 Action 步骤的一种**工程化实现方式**。ReAct Loop 的 Action 可以通过 Function Calling 来执行。

**区别**：ReAct 用自然语言描述动作（"调用搜索"），Function Calling 用 JSON Schema 约束动作（`{"name": "search", "arguments": {"query": "北京天气"}}`）。两者是**互补关系**，而非替代关系。

### MCP（协议层）

**MCP = Model Context Protocol**，由 Anthropic 于 2024 年 11 月发布，是连接 AI 应用与外部工具/数据源的**开放标准协议**。

MCP 的定位是**工具生态的"USB-C"**：
- USB-C：一种通用接口，适配所有设备
- MCP：一种通用协议，适配所有 Agent 和工具

**与 Tool Use 的关系**：MCP 是比 Tool Use 更上层的协议。Tool Use 定义的是"如何调用一个工具"，MCP 定义的是"如何让不同 Agent 发现和使用来自不同来源的工具"。

**三层架构总结**：
```
顶层：ReAct（思考框架：如何组织推理-动作循环）
中层：Function Calling / Tool Use（执行机制：如何调用具体工具）
底层：MCP（协议标准：如何让工具被统一发现和使用）
```

---

## 核心原理

### Agent 架构

一个典型 Agent 的工作流程：

```
用户输入
  → 理解任务（LLM 推理）
  → 决定是否调用工具
  → [如需工具] 通过 Function Calling 或 MCP 调用外部工具
  → 收集观察结果（Observation）
  → 继续推理
  → ... 循环
  → 生成最终回答
```

### 记忆系统

Agent 的记忆分为两层：
- **短期记忆（Short-term）**：对话上下文窗口（ChatML），受限于 LLM 的上下文长度
- **长期记忆（Long-term）**：向量数据库（Chroma、Milvus、Pinecone），存储实体知识、对话摘要

---

## 关键技术节点

| 时间 | 技术 | 意义 |
|------|------|------|
| 2022 | ReAct (Yao et al.) | 提出推理-动作交替框架 |
| 2023.06 | OpenAI Function Calling | 结构化工具调用工程化 |
| 2023 | AutoGPT / BabyAGI | 自主 Agent 框架开源 |
| 2024.11 | Anthropic MCP | 工具协议标准化 |
| 2024.09 | OpenAI o1 | 内部 CoT，推理时验证 |
| 2025.01 | DeepSeek-R1 | RL Scaling for Reasoning |

---

## 相关概念

- [[./chain_of_thought.md|CoT]]：ReAct 的 Thought 步骤继承 CoT 的推理思想
- [[./rlhf.md|RLHF]]：Agent 对齐训练的核心方法
- [[./transformer_architecture.md|Transformer]]：LLM 的底层架构

---

## 参考文献

- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models", arXiv:2210.03629, 2022
- Anthropic, "Model Context Protocol", https://modelcontextprotocol.io/, 2024
- OpenAI, "Function Calling", https://platform.openai.com/docs/guides/function-calling, 2023
- Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools", arXiv:2302.04761, 2023


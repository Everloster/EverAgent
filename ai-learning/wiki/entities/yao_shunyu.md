# 姚顺雨（Shunyu Yao）

> ReAct 第一作者，00后研究者代表，SWE-bench 作者，Princeton → Meta AI

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | Shunyu Yao（姚顺雨） |
| 机构 | Princeton University → Meta AI |
| 出生 | 00后 |
| 核心贡献 | ReAct（推理+行动协同）、SWE-bench（软件工程任务基准） |
| 代表作 | "ReAct: Synergizing Reasoning and Acting in Language Models" (2022) |

## 学术脉络

```
Princeton 研究生
    └── ReAct (Yao et al., 2022)
         ├── 推理 + 行动协同的 Agent 框架
         ├── 显著提升多步推理任务准确率
         └── 成为 Agent 系统理论基础

    └── SWE-bench
         ├── 软件工程任务的真实评测基准
         ├── GitHub Issues + PR + 测试用例
         └── LLM 编程能力评估标准
```

## 核心贡献：ReAct

### 主要创新

1. **Thought + Action + Observation 循环**：让 LLM 在推理过程中交替进行思考和行动
2. **统一的 prompting 框架**：同一格式适用于多跳问答、文本游戏、网页导航
3. **自我纠错能力**：通过 Observation 验证 Thought，错误时重新规划

### 技术成就

| 任务 | 超越基线 | 具体效果 |
|------|---------|---------|
| HotpotQA | > CoT | EM 33.3 → 34.7 |
| ALFWorld | > CoT | 40% → 71% 成功率 |
| WebShop | 显著超越随机 | 27.5 → 59.1 分 |

## 在本项目中的关联

- 直接关联报告：`17_react_2022.md`
- 关联论文：CoT (#10) — ReAct 的推理基础
- 概念关联：`agent_systems.md`、`bitter_lesson.md`（搜索扩展视角）
- 后续：LangChain、Claude Agent、MCP 协议

## 00后新生代研究者代表

姚顺雨代表了新一代 AI 研究者的风格：
- **实用主义**：不追求理论优雅，追求实际有效
- **系统思维**：从框架角度设计 Prompt，而非单点优化
- **工程导向**：代码+基准数据集并行推进
- **大模型原生**：生于 GPT-3/4 时代，天然将 LLM 作为基础设施

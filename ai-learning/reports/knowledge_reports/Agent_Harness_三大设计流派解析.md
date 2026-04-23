---
title: "Agent Harness 三大设计流派解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-04-22"
---

# Agent Harness 三大设计流派解析

## 目录

- [引言](#引言)
- [Layer 1 直觉类比：什么是 Agent Harness](#layer-1-直觉类比什么是-agent-harness)
- [Layer 2 形式定义：Harness 的核心问题与解决框架](#layer-2-形式定义harness-的核心问题与解决框架)
- [Layer 3 变体全景：三大流派诞生背景与演化路径](#layer-3-变体全景三大流派诞生背景与演化路径)
  - [流派一：everything-claude-code —— 配置即一切，分工即架构](#流派一everything-claude-code--配置即一切分工即架构)
  - [流派二：deer-flow —— 图编排，企业级状态管理](#流派二deer-flow--图编排企业级状态管理)
  - [流派三：Archon —— 工作流即代码，确定性优先](#流派三archon--工作流即代码确定性优先)
- [Layer 4 工程实现：核心架构对比](#layer-4-工程实现核心架构对比)
  - [everything-claude-code 架构剖析](#everything-claude-code-架构剖析)
  - [deer-flow 架构剖析](#deer-flow-架构剖析)
  - [Archon 架构剖析](#archon-架构剖析)
- [Layer 5 前沿动态：当前研究边界与未解问题](#layer-5-前沿动态当前研究边界与未解问题)
- [总结与选型指南](#总结与选型指南)

---

## 引言

随着大语言模型能力的爆发，AI Agent 从实验室概念快速走向生产环境。当模型本身的智能已经足够强大，开发者开始意识到——真正限制 Agent 落地的瓶颈，往往不是模型能力，而是**模型周围的脚手架**。

这个"脚手架"，在业界被统称为 **Agent Harness**（驾驭框架）。它不产生智能，而是约束智能、引导智能、组织智能，让大模型的能力沿着可预期的轨道释放。

开源社区诞生了大量不同设计哲学的 Agent Harness 项目，其中最具代表性的三个流派：

1. **everything-claude-code**（配置化分工流派）—— 源自 Anthropic Claude Code 生态，以专业化分工和增量配置为核心
2. **deer-flow**（图编排流派）—— 基于 LangGraph 构建，面向企业级多用户并发场景
3. **Archon**（工作流化流派）—— YAML 定义全流程，确定性可重复优先

本文从 5 层理解模型出发，系统对比这三大流派的设计哲学、架构实现、适用场景。

---

## Layer 1 直觉类比：什么是 Agent Harness

可以用三个生活中的例子来类比不同 Harness 的设计哲学：

- **everything-claude-code** 就像是一个**现代化办公室**——每个人有明确分工，有共享文档和规则手册，新任务来了自动分配给合适的人，不需要重新装修办公室。你只需要把规则和技能放在正确的位置，系统自然运转。

- **deer-flow** 就像是一个**现代化城市交通系统**——每个路口有红绿灯，每条道路有方向，状态被精确管理，多辆车可以同时行驶互不干扰。支持复杂的路径规划和动态路由，适合大规模人流物流。

- **Archon** 就像是一个**工厂流水线**——你预先定义好每一道工序，每个工序做什么、验收标准是什么、不合格怎么办，全都是固定的。原材料进去，成品出来，每次都一样，不会因为工人"心情"变化而出错。

这三个类比恰好对应了三种设计思路：
- **分工配置** vs **图编排** vs **工作流定义**
- **弹性灵活** vs **状态可控** vs **确定性重复**

---

## Layer 2 形式定义：Harness 的核心问题与解决框架

### 核心定义

**Agent Harness** 是运行在 LLM 之上的一层基础设施，负责：

1. **状态管理**：维护对话历史、任务进度、上下文窗口
2. **工具编排**：决定何时调用工具、如何处理返回结果
3. **流程控制**：循环、分支、条件判断、人类介入节点
4. **并发隔离**：多用户/多任务同时运行时互不干扰
5. **可观测性**：日志、审计、调试、错误追踪

**核心公式**：

```
Agent 行为 = 模型能力 × Harness 结构
```

相同的基础模型，不同的 Harness 设计，会产生完全不同的产出质量和一致性。

### Harness 必须回答的五个问题

| 问题 | everything-claude-code | deer-flow | Archon |
|------|------------------------|-----------|--------|
| 谁来做决策？ | 模型+专职分工 | 图状态机 | 工作流定义 |
| 如何保证可重复？ | 配置约定 | 状态持久化 | YAML 固化流程 |
| 复杂度从哪来？ | 配置增量增长 | 图节点扩展 | 工作流组合 |
| 谁拥有最终控制权？ | 人类通过配置 | 框架通过状态 | 人类通过工作流 |
| 适合规模 | 中小团队单项目 | 企业级多用户 | 规模化生产 |

---

## Layer 3 变体全景：三大流派诞生背景与演化路径

### 流派一：everything-claude-code —— 配置即一切，分工即架构

**诞生背景**：

everything-claude-code 诞生于 2025 年 Anthropic 黑客松，作者 Affaan Mustafa 在 8 小时内用 Claude Code 构建了完整产品，随后开源了他积累 10 个月的生产环境配置体系 <ref>https://github.com/affaan-m/everything-claude-code</ref>。项目上线后迅速爆发，3 个月获得 136K+ Star，成为 Claude Code 生态最受欢迎的配置集合。

**核心问题**：

Claude Code 本身是极简的 CLI Agent，空白画布交给用户自由发挥。但大多数用户不知道如何配置才能发挥最大效能——新手从空白开始，需要很长时间摸索出最佳实践。everything-claude-code 回答的问题是：**一个成熟的 AI 编程环境，应该预装哪些分工、技能、规则？**

**设计哲学**：

> "专业分工比全能选手靠谱。"

核心信条：

1. **分工至上**：38 个专职 Agent，每个只干一件事（planner、architect、code-reviewer、security-reviewer 等）<ref>https://m.toutiao.com/group/7624848551880770099/</ref>
2. **增量配置**：通用规则 + 语言专用规则按需加载，避免上下文膨胀
3. **持续学习**：Instinct System 自动提取编码模式，越用越懂你
4. **自动降级**：根据任务复杂度自动选择模型（Haiku/Sonnet/Opus），节省 Token 成本
5. **安全前置**：AgentShield 扫描提示注入和命令注入风险，安全不是事后补救

**演化路径**：

- **阶段 1**（2025 Q3）：纯配置集合，开箱即用
- **阶段 2**（2025 Q4）：支持插件化安装，跨平台共享
- **阶段 3**（2026 Q1）：v1.0.0 正式发布，支持 MCP 和 hooks 扩展

### 流派二：deer-flow —— 图编排，企业级状态管理

**诞生背景**：

deer-flow 是基于 LangGraph 构建的企业级 Agent 框架，起源于社区对"Claude Code 极简架构能否满足生产需求"的追问。当开发者想把 Agent 能力通过 Web 服务暴露给多用户，才发现简单的 Agent Loop 根本应对不了并发、状态隔离、断点恢复这些问题 <ref>https://juejin.cn/post/7626562216192884790</ref>。

**核心问题**：

Claude Code 的极简架构适合单用户 CLI 场景，但在企业级多用户 Web 应用中，面临三个无法回避的挑战：

1. **状态管理困境**：多用户并发，每个人的对话历史需要隔离存储
2. **断点恢复需求**：服务重启后，用户能从上次中断的地方继续
3. **可观测性要求**：开发者需要追踪 Agent 的每一步决策

deer-flow 回答的问题是：**如何用 LangGraph 解决企业级场景下的状态管理复杂性？**

**设计哲学**：

> "复杂场景需要系统化框架，简单性来自正确的抽象，不是省略。"

核心信条：

1. **显式状态**：所有状态都存储在图节点中，不是隐式维护在对话历史里
2. **持久化**：内置检查点机制，任意节点可断点恢复
3. **流式输出**：支持 Token 级流式响应，用户体验流畅
4. **并发可控**：LangGraph 运行时天然支持多线程并发隔离
5. **可观测性**：每个节点的决策都可追踪、可调试

**演化路径**：

- **前驱**：LangGraph 提供图编排基础能力
- **阶段 1**：封装 Claude Code 最佳实践到 LangGraph 范式
- **阶段 2**：解决多用户并发和状态持久化问题
- **当前**：企业级生产案例验证中

### 流派三：Archon —— 工作流即代码，确定性优先

**诞生背景**：

Archon 由 coleam00 创建于 2025 年底，定位是"全球第一个开源 AI 编码工作流构建器" <ref>https://github.com/coleam00/Archon</ref>。项目诞生直接针对一个业界痛点——**AI 心情问题**。

**核心问题**：

当你对 AI 代理说"修复这个 bug"，结果完全不可预测：
- 它可能跳过规划步骤直接编码
- 它可能忘记运行测试就提交
- 它可能把 PR 描述写错地方
- 每次运行结果都不一样，完全取决于模型当天的"心情"

Archon 回答的问题是：**如何让 AI 编码从"随心所欲"变成"确定性生产力"？** <ref>https://www.cnblogs.com/gyc567/p/19854582</ref>

**设计哲学**：

> "结构决定一切，AI 只负责智能。人类定义流程，AI 执行流程。"

就像 Dockerfile 把基础设施变成可重复的镜像，GitHub Actions 把 CI/CD 变成标准化流水线——Archon 把 AI 编码变成可重复、可隔离、可组合的生产级工作流。

核心信条 <ref>https://deepwiki.com/coleam00/Archon</ref>：

1. **可重复**：同样的工作流，每次执行顺序完全一致
2. **隔离执行**：每次运行自动创建独立的 Git worktree，多任务并行互不冲突
3. **可组合**：确定性节点（Bash、测试、Git）和 AI 节点（规划、编码、审查）自由混用
4. **可移植**：工作流定义在 `.archon/workflows/` 下，随代码提交，处处运行一致
5. **人类始终可控**：interactive 审批关卡，随时可以介入审查

**演化路径**：

- **v1**（2025 Q4）：基础 YAML 工作流引擎 + Git worktree 隔离
- **v2**（2026 Q1）：Web UI 可视化工作流编辑器 + 多平台适配器
- **v3**（2026 Q2）：MCP 集成 + 知识管理集成，当前活跃开发中

---

## Layer 4 工程实现：核心架构对比

### everything-claude-code 架构剖析

**目录结构**：

```
everything-claude-code/
├── agents/              # 38 个专职 Agent
│   ├── planner/         # 输出执行计划
│   ├── architect/       # 审核架构决策
│   ├── code-reviewer/   # 代码质量审查
│   ├── security-reviewer/ # 安全扫描
│   └── ...
├── skills/              # 156 个可复用技能
│   ├── tdd/             # 测试驱动开发
│   ├── code-review/     # 代码审查规范
│   ├── continuous-learning/ # 持续学习
│   └── ...
├── rules/               # 34 条规则
│   ├── common/          # 通用规则
│   ├── typescript/      # TypeScript 专用
│   ├── python/          # Python 专用
│   └── ...
├── hooks/               # 20+ 生命周期钩子
│   ├── pre-session/     # 会话启动前
│   ├── post-session/    # 会话结束后
│   └── ...
└── commands/            # 72 个 Slash 命令
```

**核心机制：Instinct System** 持续学习 <ref>https://m.toutiao.com/group/7624848551880770099/</ref>：

```python
# 伪代码：Instinct System 工作流程
def on_session_end(session_history):
    # 1. 自动提取编码模式
    patterns = extract_coding_patterns(session_history)
    # 2. 写入技能文件
    save_to_instinct_skills(patterns)
    # 3. 下次会话启动自动加载
    return

def on_session_start():
    # 加载已经学到的模式作为系统提示
    instincts = load_saved_instincts()
    inject_to_system_prompt(instincts)
```

**Token 节省策略**：

- 模型自动降级：简单修改用 Haiku，节省 95%；日常开发用 Sonnet，节省 60%
- 分层规则加载：通用规则 always loaded，语言专用规则按需加载
- MAX_THINKING_TOKENS 限制：大多数任务不需要深度思考，节省思考开销

**安全机制：AgentShield**：

- 1282 个测试用例，98% 覆盖率
- 检测 CLAUDE.md 提示注入风险
- 检测 MCP 服务器配置漏洞
- 检测 Hook 脚本命令注入
- 检测依赖项已知 CVE

**数据统计** <ref>https://aicoding.juejin.cn/post/7598499504170139686</ref>：

- 38 个专业 Agent
- 156 个技能
- 72 个 Slash 命令
- 34 条规则
- 20+ 自动化 Hooks
- 22.7K+ GitHub Stars（持续增长中）

### deer-flow 架构剖析

**整体架构** <ref>https://juejin.cn/post/7626562216192884790</ref>：

```
┌─────────────────────────────────────────────────────────────┐
│                         Web 前端                             │
├─────────────────────────────────────────────────────────────┤
│                    DeerFlow Orchestrator                    │
├─────────────────────────────────────────────────────────────┤
│                    LangGraph Runtime                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│  │  规划节点  │  │  执行节点  │  │  审核节点  │  ...         │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘              │
│        │              │              │                     │
│        └──────────────┼──────────────┘                     │
│                      ↓                                      │
│               状态检查点持久化                               │
└─────────────────────────────────────────────────────────────┘
```

**与 Claude Code 极简架构对比**：

| 维度 | Claude Code 原生 | deer-flow + LangGraph |
|------|----------------|---------------------|
| 状态管理 | 本地文件，单用户 | 数据库，多用户隔离 |
| 并发支持 | 不支持 | 原生支持 |
| 断点恢复 | 手动 | 自动检查点 |
| 可观测性 | 基础 | 完整节点追踪 |
| 适用场景 | CLI 单用户 | 企业级 Web 服务 |

**核心源码节点类型**：

```python
# 伪代码：LangGraph 节点定义
class PlanningNode(BaseNode):
    def run(self, state):
        # 拆解用户需求为子任务
        tasks = llm.plan(user_requirement=state.user_requirement)
        state.tasks = tasks
        return state

class ExecutionNode(BaseNode):
    def run(self, state):
        # 执行当前任务，调用工具
        result = tool_executor.execute(state.current_task)
        state.history.append(result)
        return state

class ReviewNode(BaseNode):
    def run(self, state):
        # 代码质量审查
        review_result = llm.review(state.code_diff)
        if review_result.passed:
            state.move_to_next_task()
        else:
            state.need_fix = True
        return state
```

**状态持久化机制**：

LangGraph 内置 Saver 接口，支持：
- 内存存储（开发测试）
- SQLite 持久化（单节点生产）
- PostgreSQL 持久化（集群部署）
- 任意节点保存检查点，随时恢复

### Archon 架构剖析

**系统架构** <ref>https://www.cnblogs.com/gyc567/p/19854582</ref>：

```
平台适配器（Web UI / Telegram / GitHub / CLI）
          ↓
      Orchestrator（路由 + AI 查询 + 会话管理）
          ↓
   ┌──────┼──────┐
Command Handler  AI Assistant Clients  Isolation Providers
          ↓
     数据库（SQLite / PostgreSQL）
```

**YAML 工作流示例**（伪代码）：

```yaml
# .archon/workflows/fix-github-issue.yaml
name: "Fix GitHub Issue"
description: "自动修复 GitHub Issue 并创建 PR"

steps:
  - name: "classify-issue"
    type: "ai"
    prompt: "分类这个 issue 是 bug/feature/question"
    output: "issue_type"

  - name: "investigate"
    type: "ai"
    prompt: "调查代码库，定位问题原因，输出修复计划"
    output: "plan"

  - name: "implement"
    type: "loop"
    condition: "not plan.done"
    steps:
      - name: "fix-step"
        type: "ai"
        prompt: "执行修复计划的当前步骤"

  - name: "verify"
    type: "shell"
    command: "run-tests"
    pass_condition: "exit_code == 0"

  - name: "code-review"
    type: "parallel-ai"
    agents: [security-reviewer, style-reviewer, performance-reviewer]
    aggregator: "collect-all-feedback"

  - name: "create-pr"
    type: "git"
    action: "create-pull-request"
    template: ".github/PULL_REQUEST_TEMPLATE.md"
```

**隔离机制：Git worktree**：

每个工作流运行自动创建独立的 Git worktree：

```python
# 伪代码：隔离机制
def run_workflow(workflow, issue):
    # 1. 创建独立 worktree
    worktree_path = create_git_worktree(
        base_repo=current_repo,
        branch=f"archon/fix-{issue.number}-{uuid()}"
    )
    # 2. 在隔离环境中执行
    result = workflow.execute(cwd=worktree_path)
    # 3. 完成后合并回主分支
    merge_back_to_main(result)
    # 4. 清理 worktree
    cleanup_worktree(worktree_path)
    return result
```

这种设计带来三个好处：
1. 多工作流并行运行，互不干扰
2. 即使失败，也不会污染主分支工作区
3. 全程可审计，每个步骤都有完整 git 记录

**设计核心：AI 是执行者，不是决策者**：

Archon 的设计非常清晰：
- **人类**决定：流程是什么、每个阶段做什么、验收标准是什么
- **AI**只做：在给定节点提供智能、生成内容、解决具体问题
- **结构**约束：流程不会因为 AI"心情"变化而乱序

这和"让 AI 自主决定下一步做什么"的思路完全相反。Archon 认为，软件开发流程是已知的，不需要 AI 去发现流程——AI 只需要执行。

---

## Layer 4 工程实践总结：关键数字与对比

### 三大流派关键数据对比

| 维度 | everything-claude-code | deer-flow | Archon |
|------|------------------------|-----------|--------|
| 诞生年份 | 2025 | 2025 | 2025 |
| 核心依赖 | Claude Code | LangGraph | Claude Code + Bun |
| 主要维护者 | Affaan Mustafa | 社区 | coleam00 |
| GitHub Stars | ~23K | ~2K | ~5K |
| 配置方式 | 声明式配置 | 图节点编程 | YAML 工作流 |
| 学习曲线 | 低（开箱即用） | 中（需要懂 LangGraph） | 中（定义工作流） |
| 扩展方式 | 添加 Agent/Skill | 添加图节点 | 添加工作流步骤 |
| 并发支持 | 单会话 | 多会话隔离 | Git worktree 隔离 |
| 确定性 | 中等（依赖模型） | 高（状态可追溯） | 非常高（流程固定） |

### Token 开销对比

| 流派 | 启动开销 | 运行时开销 | 渐进加载 |
|------|---------|-----------|----------|
| everything-claude-code | ~500 tokens（仅元数据） | 按需加载 Skill | ✅ 三级渐进 |
| deer-flow | ~1000 tokens | 稳定，状态持久化 | ✅ 节点按需 |
| Archon | ~300 tokens（工作流定义） | 按步骤加载 | ✅ 流式分步 |

所有三个现代流派都理解"渐进披露"（progressive disclosure）的重要性——不把所有内容一次性塞进上下文，只在需要时加载。

### 适用场景对比

| 场景 | 推荐流派 | 原因 |
|------|---------|------|
| 个人开发者 Claude Code 日常使用 | everything-claude-code | 开箱即用，技能丰富 |
| 企业级多用户 Agent Web 应用 | deer-flow | LangGraph 状态管理成熟，并发隔离 |
| 规模化 AI 辅助开发流水线 | Archon | 确定性流程，Git 级别隔离，适合 CI/CD 集成 |
| 团队统一 AI 编码规范 | everything-claude-code | 配置即规范，易于共享 |
| 复杂多步骤任务自动化 | Archon | YAML 定义清晰，可审计可重复 |
| 研究性动态 Agent 行为 | deer-flow | 图编排灵活，支持复杂条件分支 |

---

## Layer 5 前沿动态：当前研究边界与未解问题

### 当前研究边界

1. **Harness 即产品**：越来越多从业者意识到，在 AI 编程时代，Harness 本身就是产品——模型是基础设施，Harness 才是差异化竞争力。

2. **技能生态化**：从单体 Agent 到可复用技能集市——一个技能只解决一个问题，跨项目跨平台复用。everything-claude-code 和 claude-skills 都在往这个方向走。

3. **确定性 vs 灵活性之争**：Archon 代表的"流程固定"流派和传统的"AI 自主决策"流派正在激烈争论。谁对？可能取决于场景——探索性项目需要灵活，生产流水线需要确定性。

4. **记忆即 Harness 组件**：claude-mem 等项目把持久化记忆变成 Harness 的一等公民，跨会话记忆自动注入正在成为标配。

### 未解问题

1. **工作流发现问题**：Archon 用户需要自己写 YAML 工作流，社区能否沉淀出一套通用的高质量工作流集市？类似于 GitHub Actions marketplace，能否成功？

2. **分工粒度问题**：everything-claude-code 的 38 个 Agent 分工是不是太细了？会不会带来协调开销？最优分工粒度在哪里？

3. **状态爆炸问题**：LangGraph 支持任意复杂的图，但状态越多，维护成本越高。多大的图复杂度是可接受的？有没有量化指标？

4. **人类介入时机**：什么时候该让 AI 自主运行，什么时候该让人审批？不同类型的项目最佳控制点在哪里？

5. **跨 Harness 兼容**：不同 Harness 之间能否互操作？一个在 everything-claude-code 定义的 Skill，能否直接在 Archon 中使用？标准正在形成中。

---

## 总结与选型指南

三大流派代表了三种完全不同的设计哲学：

| 流派 | 核心哲学 | 一句话总结 |
|------|---------|-----------|
| everything-claude-code | 配置分工 | 把最佳实践预配置好，开箱即用，专业分工提效 |
| deer-flow | 图编排 | 用显式状态管理解决企业级并发问题 |
| Archon | 工作流固化 | YAML 定义流程，把 AI 编码变成确定性流水线 |

不存在"最好"的流派，只存在"最适合你场景"的流派：

- **如果你是个人开发者**，刚用上 Claude Code，想要提升效率——选 **everything-claude-code**，直接装插件，5 分钟生效。

- **如果你在做企业级多用户 Agent 产品**——选 **deer-flow**，LangGraph 的状态管理和并发隔离能力已经经过生产验证。

- **如果你想把团队的 AI 开发流程标准化**，让每个人都跑相同的流程——选 **Archon，工作流提交到 repo，全团队一致。

这三个流派不是互斥的，而是互补的：你可以用 everything-claude-code 的 Skill，在 Archon 的工作流中调用，本质上是不同层级的抽象——Skill 是能力单元，工作流是流程编排。

未来趋势很清晰：Agent Harness 正在从"框架"变成"基础设施"，就像 Docker 把容器化变成标准化基础设施一样，Harness 也会把 AI Agent 的运行变成标准化、可重复、可审计的基础设施。

那一天，开发者不会再说"试试让 AI 写这个"，而是说"运行这个工作流，AI 会搞定"。这就是确定性的价值。

---

**数据来源**：

- everything-claude-code: <https://github.com/affaan-m/everything-claude-code>
- Archon: <https://github.com/coleam00/Archon>
- deer-flow 分析: <https://juejin.cn/post/7626562216192884790>
- Archon 中文解读: <https://www.cnblogs.com/gyc567/p/19854582>
- everything-claude-code 深度解读: <https://m.toutiao.com/group/7624848551880770099/>

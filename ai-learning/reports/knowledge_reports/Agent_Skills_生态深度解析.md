---
title: "Agent Skills 生态深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-04-22"
---

# Agent Skills 生态深度解析

## 目录

- [引言](#引言)
- [Layer 1 直觉类比：Skills 是什么](#layer-1-直觉类比skills-是什么)
- [Layer 2 形式定义：Skill 的规范与结构](#layer-2-形式定义skill-的规范与结构)
- [Layer 3 变体全景：从 Karpathy CLAUDE.md 到可复用技能树](#layer-3-变体全景从-karpathy-claudemd-到可复用技能树)
  - [起点：Karpathy 的 LLM 编程陷阱观察](#起点karpathy-的-llm-编程陷阱观察)
  - [转化：从一条推文到 CLAUDE.md](#转化从一条推文到-claudemd)
  - [标准化：Anthropic Agent Skills 规范](#标准化anthropic-agent-skills-规范)
  - [生态化：everything-claude-code 的 156 个技能](#生态化everything-claude-code-的-156-个技能)
  - [平台化：agentskills.io 与跨平台兼容](#平台化agentskillsio-与跨平台兼容)
- [Layer 4 工程实现：Skill 作为 Harness 组件](#layer-4-工程实现skill-作为-harness-组件)
  - [Skill 与 MCP 的关系](#skill-与-mcp-的关系)
  - [Skill 与 System Prompt 的关系](#skill-与-system-prompt-的关系)
  - [Skill 渐进加载机制](#skill-渐进加载机制)
  - [Skill 树结构示例](#skill-树结构示例)
- [Layer 5 前沿动态：Skills 生态的未来](#layer-5-前沿动态skills-生态的未来)
- [总结](#总结)

---

## 引言

2026 年 1 月，一个名为 `CLAUDE.md` 的 Markdown 文件冲上了 GitHub Trending 日榜第一。它没有任何代码，只有四条行为准则，却在一周内新增了 44,465 颗星，总星数达到 61.6K。

这个文件源自 Andrej Karpathy 对 LLM 编程陷阱的观察，由华人开发者 Jiayuan Zhang 将其转化为结构化指令。它的爆火揭示了一个深刻趋势——**在 AI Agent 时代，约束模型行为的"技能"（Skills），正在成为一种新的软件形态**。

从一条推文到 CLAUDE.md，从单个文件到 156 个技能的标准化生态，再到跨平台兼容的 agentskills.io 协议——Agent Skills 正在经历从个人经验到公共基础设施的演化。

本文将沿着这条演化路径，深度解析 Skills 生态的五个层次。

---

## Layer 1 直觉类比：Skills 是什么

想象你是一家公司的 HR。新员工入职时，你需要给他三样东西：

1. **公司手册**（System Prompt）：公司文化、行为准则、着装要求——这些始终有效
2. **岗位说明书**（Skill）：前端开发岗位需要 React 规范，测试岗位需要 TDD 流程——这些是按需加载的
3. **外部工具权限**（MCP）：Jira 账号、Slack 通道、GitHub 权限——这些是调用外部服务的

Agent Skills 就是"岗位说明书"——它不是告诉 Agent 你是谁，而是告诉 Agent **在特定场景下该怎么做**。

一个 Skill 可能包含：
- 如何做代码审查（检查什么、怎么写反馈）
- 如何执行 TDD（Red-Green-Refactor 的具体步骤）
- 如何写技术文档（结构模板、术语表）
- 如何处理 PDF（提取文本、填写表单）

关键洞察：**Skills 是可交换的**——今天你用 TDD Skill，明天你换成 BDD Skill，Agent 的行为模式就变了，不需要重写整个系统。

---

## Layer 2 形式定义：Skill 的规范与结构

### Anthropic Agent Skills 标准格式

根据 Anthropic 官方定义 <ref>https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills</ref>，一个 Skill 是一个目录，包含：

```
skill-name/
├── SKILL.md              # 核心文件，YAML frontmatter + 指令
├── references/           # 参考资料（可选）
│   └── api_reference.md
├── templates/            # 模板文件（可选）
│   └── pr_template.md
└── assets/               # 静态资源（可选）
    └── diagram.png
```

**SKILL.md 必须包含**：

```yaml
---
name: "skill-name"
description: "一句话描述这个技能是做什么的"
version: "1.0.0"
license: "MIT"
---

# 详细指令内容

## 使用场景
什么时候应该触发这个 skill。

## 操作步骤
1. 第一步...
2. 第二步...

## 注意事项
- 不要...
- 必须...
```

### 渐进披露三级结构

Skill 的核心设计哲学是**渐进披露**（progressive disclosure）——像一本好手册，从目录到章节到附录，只在需要时加载 <ref>https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills</ref>：

| 层级 | 内容 | 何时加载 | Token 开销 |
|------|------|---------|-----------|
| Level 1 | YAML frontmatter（name + description） | Agent 启动时 | ~30-50 tokens |
| Level 2 | SKILL.md 正文 | Agent 判断相关时 | 数百 tokens |
| Level 3 | references/、templates/ 等附加文件 | Agent 需要深入时 | 按需加载 |

这种设计让 Agent 可以同时"知道"成百上千个 Skill，但只在需要时加载具体内容，上下文窗口永远不会被撑爆。

### 核心公式

```
Agent 能力 = 基础模型能力 + Σ(已加载 Skills)
```

一个 Agent 可以安装任意数量的 Skills，但同一时间只有被判定为"相关"的 Skills 会被加载到上下文中。

---

## Layer 3 变体全景：从 Karpathy CLAUDE.md 到可复用技能树

### 起点：Karpathy 的 LLM 编程陷阱观察

2025 年 1 月 26 日，Andrej Karpathy 在 X 上发了一条长帖，详细吐槽了 AI 编程 Agent 的各种毛病 <ref>https://github.com/forrestchang/andrej-karpathy-skills</ref>：

> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

> "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."

> "They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task."

这三段话精准概括了 LLM 编程的三大陷阱：
1. **盲目假设**：不确认就执行，错了也不自知
2. **过度工程**：写 1000 行解决 100 行就能搞定的问题
3. **副作用污染**：修改 A 的时候顺手改了不相关的 B

### 转化：从一条推文到 CLAUDE.md

当天，开发者 Jiayuan Zhang 动手把这条推文转化为结构化指令 <ref>http://m.toutiao.com/group/7630844972815712803/</ref>：

1. 先用 Claude Code 把帖子自动转化为 skills 文件，生成约 800 行描述
2. 然后让 Claude 自己审查自己
3. 最后砍成约 70 行的干净指令

产物就是 `CLAUDE.md`，四条原则直接对应 Karpathy 的三大陷阱：

| 原则 | 对应陷阱 | 核心指令 |
|------|---------|---------|
| Think Before Coding | 盲目假设 | 不确定时停下来问，不猜 |
| Simplicity First | 过度工程 | 没被要求的功能不写 |
| Surgical Changes | 副作用污染 | 只动被要求动的部分 |
| Goal-Driven Execution | 全部 | 给目标不给步骤，让 AI 自己循环验证 |

这个转化的精妙之处在于：它把**经验观察**变成了**可执行指令**。Karpathy 说的是"LLM 有这些毛病"，CLAUDE.md 说的是"当你遇到这些情况时，按以下规则执行"。

### 标准化：Anthropic Agent Skills 规范

2025 年 12 月 18 日，Anthropic 将 Agent Skills 发布为开放标准 <ref>https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills</ref>，核心设计包括：

1. **目录结构标准化**：`SKILL.md` + `references/` + `templates/` + `assets/`
2. **YAML frontmatter 元数据**：name、description、version、license
3. **渐进披露加载**：三级加载机制，上下文永不溢出
4. **代码执行能力**：Skill 可以包含脚本，Agent 按需执行

**关键设计决策**：为什么用目录而不是单个文件？

因为复杂 Skill 需要多文件组织。以 PDF Skill 为例：
- `SKILL.md`：核心指令（何时使用、基本操作）
- `references/api_reference.md`：PDF 库 API 详细说明
- `references/forms.md`：表单填写专用指南
- `templates/extraction_template.md`：文本提取模板

Agent 处理"提取 PDF 文本"时，只需要加载 `SKILL.md`；处理"填写 PDF 表单"时，才需要额外加载 `forms.md`。

### 生态化：everything-claude-code 的 156 个技能

everything-claude-code 项目将 Skills 生态推向了前所未有的规模 <ref>https://m.toutiao.com/group/7624848551880770099/</ref>：

**技能分类统计**：

| 类别 | 数量 | 代表技能 |
|------|------|---------|
| 测试与质量 | ~25 | test-driven-development, systematic-debugging |
| 开发与架构 | ~30 | mcp-builder, artifacts-builder, skill-creator |
| 文档与文件处理 | ~20 | pdf, docx, requesting-code-review |
| 协作与工作流 | ~25 | using-git-worktrees, subagent-driven-development |
| 安全与性能 | ~15 | security-audit, performance-optimization |
| 媒体与内容 | ~15 | medium-content-pro, video-editing |
| 数据与分析 | ~15 | data-pipeline, sql-optimization |
| 元技能 | ~11 | skill-creator, continuous-learning |

**技能之间的依赖关系**：

```
skill-creator (元技能)
├── test-driven-development
├── code-review
└── continuous-learning
    └── project-specific-instincts
```

元技能（Meta Skills）是最高级的 Skill——它教 Agent 如何创建新的 Skill。这意味着 Skill 生态可以自我扩展。

### 平台化：agentskills.io 与跨平台兼容

随着 Skills 生态壮大，跨平台兼容成为刚需。claude-skills 项目推动了 agentskills.io 标准 <ref>https://github.com/alirezarezvani/claude-skills/pull/529</ref>：

**兼容平台矩阵**（截至 2026 年 4 月）：

| 平台 | 安装方式 | 格式转换 |
|------|---------|---------|
| Claude Code | 原生插件 | 无需转换 |
| Codex CLI | sync-codex-skills.py | 自动 |
| Gemini CLI | sync-gemini-skills.py | 自动 |
| OpenClaw | openclaw-install.sh | 自动 |
| Hermes Agent | sync-hermes-skills.py | 无需转换（原生兼容） |
| Cursor / Aider | scripts/convert.sh | 自动 |

**标准化收益**：

一个 Skill 作者只需要写一次 `SKILL.md`，就可以自动分发到 12 个 AI 编程工具。这类似于 npm 包对 JavaScript 生态的意义——**一次编写，到处运行**。

---

## Layer 4 工程实现：Skill 作为 Harness 组件

### Skill 与 MCP 的关系

这是最容易混淆的两个概念。官方对比 <ref>https://github.com/karanb192/awesome-claude-skills</ref>：

| 维度 | Skills | MCP Servers |
|------|--------|-------------|
| 目的 | 任务特定工作流 | 外部工具集成 |
| 设置 | Git clone 到 ~/.claude/skills/ | 安装并配置 MCP server |
| 激活 | 自动（上下文感知） | 显式工具调用 |
| 最佳场景 | TDD、调试、代码审查 | API、数据库、文件系统 |
| 可移植性 | 跨平台（CLI、Web、API） | 平台依赖 |
| Token 成本 | 30-50 直到加载 | 每次调用 |

**关键区别**：
- **MCP** 给 Agent **新的能力**（调用外部 API、查询数据库）
- **Skill** 给 Agent **新的行为模式**（如何做 TDD、如何审查代码）

两者互补：一个做 TDD 的 Agent 需要 TDD Skill（知道怎么做）+ MCP（调用测试框架）。

### Skill 与 System Prompt 的关系

| 维度 | System Prompt (CLAUDE.md) | Skill |
|------|--------------------------|-------|
| 作用范围 | 全局，始终有效 | 按需，场景触发 |
| 内容 | 项目规范、行为准则 | 特定任务流程 |
| 修改频率 | 低频（项目级） | 高频（任务级） |
| 示例 | "使用 TypeScript strict mode" | "执行 Red-Green-Refactor 循环" |

**最佳实践**：
- System Prompt 定义"你是谁、你的价值观"
- Skill 定义"在这个场景下你具体怎么做"

### Skill 渐进加载机制

```python
# 伪代码：Skill 加载决策流程
def decide_skills_to_load(user_message, installed_skills):
    # Step 1: 所有技能的元数据始终在系统提示中
    skill_metadata = [s.name + ": " + s.description for s in installed_skills]
    
    # Step 2: Agent 判断哪些技能与当前任务相关
    relevant_skills = llm.classify_relevance(
        message=user_message,
        skill_metadata=skill_metadata
    )
    
    # Step 3: 加载相关技能的 SKILL.md 正文
    for skill in relevant_skills:
        skill_content = read_file(skill.path + "/SKILL.md")
        inject_to_context(skill_content)
    
    # Step 4: 如果任务需要，加载技能的附加文件
    for skill in relevant_skills:
        if needs_deep_reference(skill, user_message):
            for ref in skill.references:
                ref_content = read_file(ref.path)
                inject_to_context(ref_content)
    
    return context
```

**Token 预算管理**：

假设一个 Agent 安装了 50 个 Skills：
- 启动时加载：50 × 40 tokens（元数据）= 2,000 tokens
- 任务时加载：2-3 个相关 Skill × 500 tokens = 1,500 tokens
- 总计：~3,500 tokens

如果不使用渐进加载，50 个 Skill 全部塞进上下文：50 × 500 = 25,000 tokens——直接占满上下文窗口。

### Skill 树结构示例

一个典型的项目 Skill 树：

```
~/.claude/skills/
├── superpowers/              # 技能集合（ obra/superpowers ）
│   ├── test-driven-development/
│   │   └── SKILL.md
│   ├── systematic-debugging/
│   │   └── SKILL.md
│   └── using-git-worktrees/
│       └── SKILL.md
├── karpathy-skills/          # Karpathy 准则
│   └── SKILL.md
├── pdf/                      # Anthropic 官方 Skill
│   ├── SKILL.md
│   ├── references/
│   │   ├── api_reference.md
│   │   └── forms.md
│   └── templates/
│       └── extraction_template.md
└── my-project-specific/      # 项目私有 Skill
    └── SKILL.md
```

**Skill 优先级**：
1. 项目私有 Skill（最高优先级，覆盖全局）
2. 用户安装的个人 Skill
3. 系统默认 Skill（最低优先级）

---

## Layer 5 前沿动态：Skills 生态的未来

### 当前研究边界

1. **Skill 自动生成**：从代码库自动提取项目特定的 Skill。claude-mem 的 Instinct System 已经在这个方向上探索——自动分析会话历史，提取编码模式写入 Skill。

2. **Skill 市场**：类似于 VS Code Extension Marketplace，一个集中的 Skill 分发平台。agentskills.io 正在往这个方向演化。

3. **Skill 版本管理**：当 Skill 更新时，如何通知用户？如何处理 Breaking Changes？目前还是空白地带。

4. **Skill 组合优化**：多个 Skill 同时触发时，如何避免冲突？如何确定优先级？这需要更复杂的编排逻辑。

### 未解问题

1. **Skill 发现问题**：用户安装了 50 个 Skill，怎么知道哪个 Skill 适合当前任务？元数据描述是否足够精准？

2. **Skill 质量评估**：社区 Skill 良莠不齐，如何建立质量评级体系？谁来审核？

3. **Skill 与模型能力的边界**：某些任务到底是该用 Skill（教 Agent 怎么做）还是等模型自己学会？边界在哪里？

4. **Skill 的知识产权**：一个优秀的 TDD Skill 凝聚了作者多年的工程经验，如何保护创作者权益？开源协议是否足够？

5. **Skill 的测试**：如何自动化测试一个 Skill 是否有效？目前只能靠人工验证。

### 演化趋势预测

**短期（6 个月）**：
- Skill 数量爆发，预计主流平台支持 500+ 官方/社区 Skill
- Skill 安装从命令行走向 GUI 市场
- 项目级 Skill（.claude/skills/）成为项目配置的一部分

**中期（1-2 年）**：
- Skill 标准统一，agentskills.io 成为事实标准
- Skill 自动生成工具成熟，新项目可以"一键生成项目专属 Skill"
- Skill 与 CI/CD 集成，Skill 变更触发自动化测试

**长期（3-5 年）**：
- Skill 可能演化为一种新的"软 API"——不是调用函数，而是调用行为模式
- 不同公司的核心竞争力可能体现在其私有 Skill 库的质量上
- "Skill 工程师"可能成为新岗位，专门设计和优化 Agent 行为模式

---

## 总结

Agent Skills 生态的演化，完美诠释了"从个人经验到公共基础设施"的技术演进路径：

```
Karpathy 推文（个人观察）
    ↓
CLAUDE.md（结构化指令）
    ↓
Anthropic Agent Skills 标准（官方规范）
    ↓
everything-claude-code 156 Skills（生态爆发）
    ↓
agentskills.io（跨平台标准）
    ↓
???（未来：Skill 市场 + 自动生成 + 质量评级）
```

这个演化的核心驱动力是：**模型能力已经足够强，瓶颈在于如何约束和引导模型行为**。

Skills 提供了一种优雅的解决方案——不是通过硬编码控制 Agent，而是通过可交换的、渐进加载的、社区共享的"行为模块"来塑造 Agent。

从 Harness 视角看，Skills 是 Harness 的**可插拔组件**。一个 Harness（如 Claude Code）提供运行环境，Skills 提供具体行为。同一个 Harness，加载不同的 Skills，就变成了完全不同的 Agent。

这意味着：**未来区分 Agent 质量的，可能不是底层模型，而是 Skill 库的深度和广度**。

就像今天区分开发者的不是 IDE，而是插件配置和代码片段库——明天区分 AI Agent 的，将是其 Skill 生态的丰富程度。

---

**数据来源**：

- Karpathy CLAUDE.md: <https://github.com/forrestchang/andrej-karpathy-skills>
- Anthropic Agent Skills 官方博客: <https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills>
- awesome-claude-skills: <https://github.com/karanb192/awesome-claude-skills>
- claude-skills 跨平台 PR: <https://github.com/alirezarezvani/claude-skills/pull/529>
- everything-claude-code 深度解读: <https://m.toutiao.com/group/7624848551880770099/>
- Karpathy 准则中文解读: <http://m.toutiao.com/group/7630844972815712803/>

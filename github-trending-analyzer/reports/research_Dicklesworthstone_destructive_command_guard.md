# Dicklesworthstone/destructive_command_guard

> The Destructive Command Guard (dcg) is for blocking dangerous git and shell commands from being executed by agents. [README]

## 项目概述

**dcg（Destructive Command Guard）** 是一个用 Rust 编写的**高性能"命令拦截钩子"**，专门在 AI 编码 Agent（Claude Code、Codex CLI、Gemini CLI、GitHub Copilot CLI、Cursor、Hermes、Grok 等）**真正执行命令之前**，拦截并阻断 `git reset --hard`、`rm -rf ./src`、`DROP TABLE users` 这类会瞬间摧毁未提交工作的破坏性命令 [README]。它以 PreToolUse hook 形式挂进各 Agent，核心卖点是**亚毫秒级延迟 + 零配置开箱即用 + 50+ 安全规则包（packs）**，并对"数据 vs 执行"做上下文区分（`grep "rm -rf"` 放行、`rm -rf /` 拦截）[README][代码]。项目创建于 2026-01-07，半年内已累积 3,489 stars [API]，是 2026 年"Agent 安全护栏"赛道里工程完成度最高的单点工具之一。

## 基本信息

| 指标 | 数值 |
|------|------|
| Stars | 3,489 [API] |
| Forks | 126 [API] |
| 语言 | Rust（占比 91.3%，另有 Shell 8.9%、PowerShell 3.2%、Python 0.16%）[API] |
| 开源协议 | MIT（`Cargo.toml` 声明 `license = "MIT"`；GitHub 元数据显示 NOASSERTION，因根目录 LICENSE 文件含自定义头未被识别）[代码][API] |
| 创建时间 | 2026-01-07 [API] |
| 最近更新 | 2026-07-13（push 于 2026-07-11）[API] |
| 最新发布 | v0.6.5（2026-07-03）[API] |
| 贡献者 | 2（作者 Dicklesworthstone 1,752 提交 + dependabot[bot] 8 提交）[API] |
| Rust edition | 2024（rust-version ≥ 1.85）[代码] |
| GitHub | [https://github.com/Dicklesworthstone/destructive_command_guard](https://github.com/Dicklesworthstone/destructive_command_guard) |

## 技术分析

### 技术栈

`Cargo.toml` 揭示了一套"为低延迟而生"的依赖组合 [代码]：

- **多模式字符串匹配**：`aho-corasick`（关键词快速拒绝）+ `memchr`（SIMD 加速的字节扫描）+ `regex` / `fancy-regex`（`RegexSet` 并行匹配）——这是"亚毫秒级"的技术基础 [代码]。
- **AST 结构匹配**：`ast-grep-core` + `ast-grep-language`，内置 7 种 tree-sitter 语法（bash / python / javascript / typescript / ruby / go / php），用于扫描 heredoc 和内联脚本里的破坏性操作 [代码]。
- **Agent 集成**：`rust-mcp-sdk`（MCP server 模式）+ `tokio`（多线程运行时），使 dcg 既能做 stdin/stdout 钩子，也能作为 MCP 服务暴露 [代码]。
- **配置与产物**：`serde` / `serde_yaml` / `toml` / `toml_edit`（保留格式编辑）/ `schemars`（生成 JSON Schema 供编辑器自动补全）/ `fsqlite`（FrankenSQLite，带 FTS5，用于历史记录）[代码]。
- **CLI/TUI 体验**：`clap` + `clap_complete`（补全）+ `ratatui` + `colored`（富终端面板）+ `self_update`（自更新）[代码]。
- **安全约束**：`src/lib.rs` 顶部 `#![cfg_attr(not(test), forbid(unsafe_code))]`——生产代码**禁用 unsafe** [代码]。

### 架构设计

`src/lib.rs` 的文档注释直接画出了主评估管线 [代码]：

```
Configuration (env → project → user → system → defaults)
        ↓
Evaluator (hook 模式与 CLI 的统一入口)
        ↓
Pack Registry (Core / Database / K8s / Cloud / ... 50+ 规则包)
        ↓
Pattern Matching (Quick Reject via memchr → Safe Patterns → Destructive Patterns)
```

`src/evaluator.rs` 的模块文档进一步列出了**严格有序的 7 步评估流程** [代码]：

1. **Config block overrides**——显式 block 规则优先于 allow；
2. **Config allow overrides**——显式 allow 放行未被 block 的命令；
3. **Heredoc / 内联脚本**——抽取并 AST 扫描嵌入代码（**fail-open**，出错则放行）；
4. **Quick rejection**——无相关关键词则跳过整个 pack 评估（性能关键路径）；
5. **Context sanitization**——屏蔽已知安全的字符串参数，降低误报；
6. **Command normalization**——剥离 git/rm 二进制的绝对路径（防 `/usr/bin/rm` 绕过）；
7. **Pack registry**——按启用的 packs 逐一检查（先 safe 后 destructive）。

**heredoc 检测是本项目最有辨识度的技术创新**。`src/heredoc.rs` 实现了"三层瀑布"架构 [代码]：

```
Tier 1 触发检测 (<100μs, RegexSet 并行, 零分配, 要求零漏报)
   ↓ 命中
Tier 2 内容抽取 (<1ms, 有界内存/时间, 出错→放行+告警)
   ↓ 成功
Tier 3 AST 匹配 (<5ms, ast-grep 结构匹配 → 命中则 BLOCK)
```

设计哲学写在注释里：**Tier 1 追求最大召回（宁可误触发也不漏），把误报交给 Tier 2/3 精筛**——这正是安全护栏"宁误拦、不漏拦"的正确取向 [代码]。整体又贯彻 **fail-open**（超时/解析失败一律放行），把"绝不干扰正常工作流"放在"绝不漏拦"之上，是对开发者体验的务实妥协 [代码][README]。

### 核心功能

- **50+ 安全规则包**：`src/packs/` 下有 **27 个分类目录**、共 **89 个非测试 pack 源文件**，覆盖 database / kubernetes / containers / cloud（AWS/GCP/Azure）/ terraform / secrets / dns / cdn / payment / windows 等 [代码]。README "50+ packs" 的说法与代码一致且偏保守 [代码][README]。
- **上下文智能识别**：靠第 5 步 context sanitization 区分"命令里的数据"与"要执行的命令"[代码]。
- **多 Agent 原生适配**：README 列出对 Claude Code、Codex CLI 0.125.0+（专门处理 Codex 拒绝未知字段、从 `turn_id` 识别 payload）、Gemini、Copilot CLI、Cursor、Hermes、Grok（原生 `~/.grok/hooks/`）等 10+ 宿主的适配 [README]。
- **辅助模式**：`dcg explain "<cmd>"` 解释为何被拦、`scan` 模式供 CI/pre-commit、SARIF 输出（`src/sarif.rs`）、模拟（`src/simulate.rs`）、历史记录（`src/history/` + SQLite）[代码][README]。

## 社区活跃度

### 贡献者分析

本质上是**单作者项目**：Dicklesworthstone（Jeffrey Emanuel）贡献 1,752 次提交，占绝对主导；另一名 `Dowwie` 列在 authors 但未出现在 contributors 统计中，其余仅 dependabot[bot]（8 次）[API][代码]。这意味着**巴士因子 = 1**，是当前最大的可持续性风险。

### Issue/PR 活跃度

- Issues：开放 7 / 已关闭 83（共 90，不含 PR）[API]。
- PR：累计 99 个 [API]。
- 关闭率约 92%（83/90），且最近开放的 issue 集中在 2026-07-11~13（Codex 集成失败、误报、pack 建议、指数级复杂度预处理等），说明**用户在真实使用中持续反馈、作者响应密集** [API]。

### 最近动态

近期开放 issue 反映项目正处于"广泛接入各 Agent 后的打磨期"：VsCode Copilot Chat 面板支持、Codex CLI 0.14x 静默失败、heredoc 散文误报（false positive）、命令预处理的指数级复杂度（潜在 ReDoS 风险）等 [API]。这些是"功能已铺开、正在填坑"的典型信号。

## 发展趋势

### 版本演进

发版极其频繁：近 12 个正式版从 v0.4.11（2026-05-01）到 v0.6.5（2026-07-03），**两个月内 12 个 release**，全部为正式版（无 prerelease），且由 `github-actions[bot]` 自动发布——说明有成熟的 release 自动化流水线 [API][代码]。仍在 0.x，API 未冻结。

### Roadmap

`src/heredoc.rs` 注释里 "Tier 3: AST Pattern Matching (future)" 表明 AST 层仍在演进 [代码]；`docs/` 下有大量 ADR（adr-001-heredoc-scanning、adr-002-robot-mode-api）和 design 文档，显示作者以**文档驱动**的方式规划扩展（custom packs、lazy pack registry、graduated response 等）[代码]。

### 社区活跃度趋势（量化）

**关键量化信号**：过去 52 周共 1,759 次提交，全窗口周均 **33.8 次/周**；但**最近 8 周仅 71 次，周均降至 8.9 次/周**——约为全年均值的 **26%** [API]。结合"创建于 1 月、5-6 月高频发版"的节奏，可判断项目已**度过初期爆发式开发，进入维护/打磨期**，开发强度明显回落（这是客观数据，非负面评价）[API]。

## 竞品对比

dcg 处在"AI Agent 命令级安全护栏"这一细分赛道。同类可分两层：**① 同类专用护栏/防火墙**、**② 通用 LLM guardrail 库**（定位不同，仅供参照）。以下数据均为 `gh` 实测 [API]：

| 项目 | Stars | 语言 | 协议 | 最近推送 | 定位 |
|------|-------|------|------|---------|------|
| **Dicklesworthstone/destructive_command_guard** | **3,489** | **Rust** | **MIT** | **2026-07-11** | **命令级拦截钩子（本项目）** |
| snyk/agent-scan | 2,773 | Python | Apache-2.0 | 2026-07-13 | Agent 供应链/安全扫描（Snyk 出品）[API] |
| invariantlabs-ai/invariant | 432 | Python | Apache-2.0 | 2026-01-12 | Agent 行为分析/护栏（已趋停更）[API] |
| protectai/llm-guard | 3,165 | Python | MIT | 2026-07-08 | 通用 LLM 输入/输出 guardrail 库 [API] |
| guardrails-ai/guardrails | 7,138 | Python | Apache-2.0 | 2026-07-10 | 通用 LLM 输出校验框架 [API] |
| NVIDIA-NeMo/Guardrails | 6,674 | Python | NOASSERTION | 2026-07-13 | 对话式 AI 护栏（NVIDIA）[API] |

**差异化分析**：
- **技术路线独特**：通用 guardrail 库（guardrails-ai/llm-guard/NeMo）几乎都是 Python、聚焦"LLM 文本输入输出校验"；dcg 是**唯一用 Rust 做命令级、亚毫秒拦截**的专用工具，定位精准且性能维度无对手 [API][代码]。
- **接入面最广**：搜索到的 Claude hook 类竞品（如 zcaceres/claude-git-reset 2★、sirhappy/git-guardian 1★）基本是脚本级玩具，星数与工程完成度都远不及 dcg [API]。
- **相对短板**：Python 生态的通用护栏在"语义级/意图级"防护上更灵活，dcg 走的是"规则+AST"的确定性路线——胜在快与准，弱在无法理解自然语言级的恶意意图（也不追求这个）[推测]。

## 总结评价

### 优势

1. **性能维度独一档**：Rust + memchr/aho-corasick/RegexSet + 三层 heredoc 瀑布，把安全护栏的延迟压到亚毫秒，且生产代码禁用 unsafe [代码]。
2. **工程完成度高**：89 个 pack 文件 / 27 分类、完善的 ADR 与 design 文档、自动化 release 流水线、SARIF/scan/explain/history 全套辅助能力 [代码][API]。
3. **接入生态最广**：原生适配 10+ 主流 AI 编码 Agent，且针对 Codex 拒绝未知字段等真实差异做了精细处理 [README]。
4. **设计哲学清醒**：fail-open + "Tier 1 零漏报、误报后筛" 的取舍，恰当平衡了"绝不干扰工作流"与"尽量不漏拦" [代码]。

### 劣势

1. **巴士因子 = 1**：几乎全部提交来自单一作者，长期可持续性依赖个人 [API]。
2. **开发强度回落**：最近 8 周周均提交仅为全年均值的 26%，需观察是进入稳定维护期还是热度消退 [API]。
3. **确定性路线的天花板**：基于规则/AST 的匹配无法理解自然语言级意图，面对刻意混淆或全新攻击面需要不断补 pack；近期已有"指数级复杂度预处理"这类 ReDoS 隐患 issue [API][推测]。
4. **协议识别瑕疵**：GitHub 将 license 显示为 NOASSERTION（实为 MIT），可能影响部分合规扫描的自动识别 [代码][API]。

### 适用场景

- **强烈推荐**：任何让 AI Agent 自主执行 shell/git 命令的团队或个人，尤其是 Claude Code / Codex / Cursor 重度用户——零配置即可挡掉绝大多数"手滑级"灾难。
- **推荐**：需要在 CI/pre-commit 阶段静态拦截危险命令的工程（用 `scan` 模式 + SARIF）。
- **需评估**：对"语义级/意图级"防护有强需求的场景，dcg 应与通用 LLM guardrail 组合使用，而非替代 [推测]。

---
*报告生成时间: 2026-07-13*
*研究方法: github-deep-research 多轮深度研究*

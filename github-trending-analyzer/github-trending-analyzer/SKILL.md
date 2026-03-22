---
name: "github-trending-analyzer"
description: "Analyzes GitHub trending repositories by day/week/month using deep research. Invoke when user asks to analyze GitHub trending projects or generate trending reports."
---

# GitHub 热点项目分析

对 GitHub Trending 页面的热点项目进行深度分析，生成结构化的趋势报告。

## 触发条件

- 用户请求分析 GitHub 热点项目
- 用户请求生成 GitHub trending 报告
- 用户询问当前 GitHub 上的热门项目趋势

## 支持的 Agent 平台

本技能设计为跨平台兼容，支持以下 Agent 平台：

| 平台 | 状态 | 安装方式 |
|------|------|---------|
| **Trae** | ✅ 原生支持 | 放置于 `.trae/skills/github-trending-analyzer/` 目录 |
| **Claude Code** | ✅ 兼容 | 放置于 `~/.claude/skills/github-trending-analyzer/` 目录 |
| **Cursor** | ✅ 兼容 | 放置于 `.cursor/skills/github-trending-analyzer/` 目录 |
| **OpenClaw** | ✅ 兼容 | 放置于项目 skills 目录 |
| **其他 Agent** | ✅ 兼容 | 放置于对应平台的 skills 目录 |

### 平台差异说明

| 功能 | Trae | Claude Code | Cursor | 其他 |
|------|------|-------------|--------|------|
| Python 脚本执行 | ✅ | ✅ | ✅ | ✅ |
| 深度研究技能 | `github-deep-research` | 需手动实现 | 需手动实现 | 需手动实现 |
| 技能调用语法 | `Skill("name")` | 直接调用 | 直接调用 | 平台特定 |

## 环境配置

### 可选环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `GITHUB_TOKEN` | GitHub API Token，避免速率限制 | 无 |
| `TRENDING_REPORTS_DIR` | 报告输出目录 | `./github-trending-reports` |

### 跨平台兼容性

本技能支持以下操作系统：
- ✅ macOS (Darwin)
- ✅ Linux
- ✅ Windows

所有路径使用 `pathlib.Path` 处理，自动适配不同操作系统的路径分隔符。

## 辅助工具

本技能包含两个 Python 辅助工具，可提高执行效率和可靠性：

### trending_fetcher.py - Trending 数据获取工具

**功能**：
- 获取 GitHub Trending 页面数据（支持日榜/周榜/月榜）
- 解析仓库信息（owner、repo、description、language、stars、forks、today_stars）
- 检查报告是否存在及是否需要更新（7天缓存机制）
- 自动检测运行平台并生成合适的 User-Agent

**使用方法**：

```bash
# 获取技能目录（首次运行建议执行）
python3 <skill_dir>/trending_fetcher.py info

# 获取日榜数据
python3 <skill_dir>/trending_fetcher.py fetch daily

# 获取周榜数据
python3 <skill_dir>/trending_fetcher.py fetch weekly

# 获取月榜数据
python3 <skill_dir>/trending_fetcher.py fetch monthly

# 按语言过滤（如 Python）
python3 <skill_dir>/trending_fetcher.py fetch daily python

# 检查报告是否存在及是否需要更新
python3 <skill_dir>/trending_fetcher.py check owner/repo
```

**输出格式**：JSON

**注意**：`<skill_dir>` 为技能所在目录，可通过 `info` 命令获取，或根据平台使用对应路径：
- Trae: `.trae/skills/github-trending-analyzer/`
- Claude Code: `~/.claude/skills/github-trending-analyzer/`
- Cursor: `.cursor/skills/github-trending-analyzer/`

### report_generator.py - 报告生成工具

**功能**：
- 生成单个项目研究报告
- 生成汇总报告（支持日榜/周榜/月榜）
- 自动格式化语言分布、贡献者、版本发布等信息

**使用方法**：

```bash
# 生成单个项目报告
python3 <skill_dir>/report_generator.py project \
  '{"owner":"xxx","repo":"xxx","stars":1000,...}' \
  '{"summary":"...","languages":{...},"contributors":[...],...}' \
  github-trending-reports/research_xxx_xxx.md

# 生成汇总报告
python3 <skill_dir>/report_generator.py summary \
  daily \
  '[{"owner":"xxx","repo":"xxx",...},...]' \
  github-trending-reports/all-daily-summary-2026-03-17.md

# 查看技能目录和环境信息
python3 <skill_dir>/report_generator.py info
```

**注意**：此工具生成的是基础报告模板，深度分析需根据平台能力实现。

---

## 执行流程

### 1. 获取 Trending 数据

**推荐使用 `trending_fetcher.py` 工具**：

```bash
python3 <skill_dir>/trending_fetcher.py fetch daily
```

支持三个时间维度：
- **日榜**: `daily`
- **周榜**: `weekly`
- **月榜**: `monthly`

输出包含：owner、repo、url、description、language、stars、forks、today_stars

### 2. 检查更新状态

**推荐使用 `trending_fetcher.py check` 命令**：

```bash
python3 <skill_dir>/trending_fetcher.py check owner/repo
```

输出示例：
```json
{
  "exists": true,
  "path": "github-trending-reports/research_owner_repo.md",
  "age_days": 3.5,
  "needs_update": false
}
```

判断逻辑：
- 如果报告存在且在7天内生成，跳过该项目
- 如果报告超过7天，重新分析并更新报告

### 3. 深度分析（核心步骤）

#### 3.1 平台适配的深度研究方法

**Trae 平台**（推荐）：
```
使用 Skill 工具调用 github-deep-research 技能进行多轮深度研究
```

**Claude Code / Cursor / 其他平台**：

由于不同平台的技能系统不同，建议采用以下替代方案：

1. **GitHub API 深度查询**：
   - 获取项目基本信息、README、tree、languages
   - 获取 contributors、commits、issues、releases
   - 使用 `gh` CLI 或 REST API

2. **Web 搜索增强**：
   - 搜索项目概述、官方文档
   - 搜索技术架构、竞品对比
   - 搜索社区评价、使用案例

3. **代码仓库分析**：
   - 分析 commit 历史
   - 分析 issue/PR 演进
   - 分析贡献者活动

#### 3.2 生成详细报告

基于深度研究结果，生成包含以下内容的详细报告：

1. **项目概述** - 2-3 句话总结项目定位和核心价值
2. **基本信息** - Stars、Forks、语言、协议、创建时间等
3. **技术分析** - 技术栈、架构设计、核心功能模块
4. **社区活跃度** - 贡献者数量、issue/PR 活跃度、最近更新
5. **发展趋势** - 版本演进、roadmap、社区反馈
6. **竞品对比** - 与同类项目的对比分析
7. **总结评价** - 综合评价和使用建议

### 4. 验证报告完整性

**重要步骤！** 在生成汇总报告前，必须验证所有项目报告是否已生成且符合质量标准：

#### 4.1 文件存在性检查

遍历所有待分析项目，检查 `research_{owner}_{repo}.md` 是否存在。

#### 4.2 内容完整性检查

每个报告**必须**包含以下所有章节：

| 章节 | 必须包含的内容 | 验证标准 |
|------|---------------|----------|
| 项目概述 | 2-3 句话总结 | 至少 50 字 |
| 基本信息 | Stars、Forks、语言、协议 | 完整表格 |
| 技术分析 | 技术栈、架构设计 | 至少 2 个子章节 |
| 社区活跃度 | 贡献者、Issue/PR | 至少 2 个子章节 |
| 发展趋势 | 版本演进、Roadmap | 至少 1 个子章节 |
| 竞品对比 | 对比表格 | 至少 2 个竞品 |
| 总结评价 | 优势、劣势、适用场景 | 至少 3 个子章节 |

#### 4.3 深度研究标识验证

每个报告**必须**在末尾包含以下标识：

```markdown
---
*报告生成时间: {datetime}*
*研究方法: {深度研究方法}*
```

#### 4.4 报告长度检查

- 单项目报告总行数应 >= 150 行
- 总字数应 >= 2000 字
- 内容过于简短的报告视为不合格

### 5. 生成汇总报告

汇总所有项目的关键信息，生成趋势分析报告。

## 输出目录结构

所有文件统一存放在 `github-trending-reports/` 目录下（可通过 `TRENDING_REPORTS_DIR` 环境变量自定义）：

```
github-trending-reports/
├── all-daily-summary-YYYY-MM-DD.md      # 日榜汇总报告
├── all-weekly-summary-YYYY-MM-DD.md     # 周榜汇总报告
├── all-monthly-summary-YYYY-MM-DD.md    # 月榜汇总报告
├── research_owner1_repo1.md         # 项目深度研究报告
├── research_owner2_repo2.md
└── ...
```

### 文件命名规则

| 文件类型 | 命名格式 | 示例 |
|---------|---------|------|
| 汇总报告 | `all-{period}-summary-YYYY-MM-DD.md` | `all-daily-summary-2026-03-17.md` |
| 项目研究 | `research_{owner}_{repo}.md` | `research_bytedance_deer-flow.md` |

## 使用方法

用户请求时，按以下步骤执行：

1. **确认分析维度**: 询问用户需要分析日榜、周榜还是月榜（默认全部）

2. **获取 Trending 列表**: 
   - 日榜: https://github.com/trending
   - 周榜: https://github.com/trending?since=weekly
   - 月榜: https://github.com/trending?since=monthly

3. **逐个项目深度分析**:
   - 检查 `github-trending-reports/research_{owner}_{repo}.md` 是否存在
   - 检查文件修改时间是否超过7天
   - 如需分析，根据平台能力执行深度研究
   - 生成详细的项目研究报告

4. **验证报告完整性**:
   - 检查所有项目对应的 `research_*.md` 文件是否存在
   - 检查报告内容是否足够详细
   - 记录缺失或不完整的报告

5. **生成汇总报告**:
   - 汇总所有项目的关键信息
   - 分析整体趋势和热门技术方向
   - 在报告末尾添加"报告状态说明"
   - 生成 `all-{period}-summary-YYYY-MM-DD.md`

## 报告格式

### 单项目报告模板（详细版）

```markdown
# {owner}/{repo}

> {项目描述}

## 项目概述

{2-3 句话总结项目定位、核心价值和目标用户}

## 基本信息

| 指标 | 数值 |
|------|------|
| Stars | {stars} |
| Forks | {forks} |
| 语言 | {language} |
| 开源协议 | {license} |
| 创建时间 | {created_at} |
| 最近更新 | {updated_at} |
| GitHub | [{url}]({url}) |

## 技术分析

### 技术栈

{语言分布、主要框架和依赖}

### 架构设计

{项目架构、核心模块、设计模式}

### 核心功能

{主要功能模块及其实现方式}

## 社区活跃度

### 贡献者分析

{贡献者数量、主要贡献者、贡献分布}

### Issue/PR 活跃度

{开放 issue 数量、PR 合并频率、响应速度}

### 最近动态

{最近的 commits、releases、公告}

## 发展趋势

### 版本演进

{主要版本更新、功能演进路线}

### Roadmap

{未来规划、待开发功能}

### 社区反馈

{用户评价、常见问题、改进建议}

## 竞品对比

| 项目 | Stars | 语言 | 特点 |
|------|-------|------|------|
| 本项目 | {stars} | {lang} | {特点} |
| 竞品1 | ... | ... | ... |
| 竞品2 | ... | ... | ... |

## 总结评价

### 优势

- {优势1}
- {优势2}

### 劣势

- {劣势1}
- {劣势2}

### 适用场景

{推荐的使用场景和用户群体}

---
*报告生成时间: {datetime}*
*研究方法: {深度研究方法}*
```

### 汇总报告模板

```markdown
# GitHub Trending {周期}报告

> 生成时间: {datetime}

## 概览

| 统计项 | 数值 |
|--------|------|
| 分析项目数 | {count} |
| 总 Stars | {total_stars} |
| 主要语言 | {languages} |

### 语言分布

| 语言 | 项目数 | 占比 |
|------|--------|------|
| ... | ... | ... |

### 热门领域

1. **领域1**: X 个项目（Y%）
2. **领域2**: X 个项目（Y%）

## 项目列表

| 排名 | 项目 | 语言 | Stars | 描述 |
|------|------|------|-------|------|
| 1 | ... | ... | ... | ... |

## 趋势分析

### 🔥 热门趋势

{主要趋势分析}

### 🏢 大厂动态

{大厂开源项目分析}

### 🔬 技术创新

{技术创新亮点}

### 📊 语言趋势

{编程语言趋势分析}

## 详细报告链接

- [项目1](./research_owner_repo.md) - {简短描述}
- [项目2](./research_owner_repo.md) - {简短描述}
- ...

## 报告状态说明

<!-- 如果有未生成的报告，在此说明 -->

⚠️ **以下项目报告未生成或不完整**：
- owner/repo - 原因：{具体原因}

<!-- 如果所有报告都已生成 -->
✅ 所有项目报告已完整生成，共 {count} 份深度研究报告。

---
*本报告由 GitHub Trending Analyzer 自动生成*
*分析方法: {深度研究方法}*
```

## 注意事项

1. **深度研究适配**: 根据不同 Agent 平台的能力选择合适的深度研究方法
2. **API 限制**: 确保已配置 `GITHUB_TOKEN` 环境变量，避免 API 速率限制
3. **增量更新**: 利用7天缓存机制，避免重复分析
4. **并发控制**: 批量分析时注意控制并发请求，避免触发 GitHub API 限制
5. **错误处理**: 单个项目分析失败不影响其他项目的处理
6. **报告验证**: 必须在生成汇总报告前验证所有项目报告是否已生成且内容完整
7. **报告质量**: 每个项目报告应包含至少 7 个主要章节（项目概述、基本信息、技术分析、社区活跃度、发展趋势、竞品对比、总结评价），内容详实有深度
8. **禁止简短报告**: 报告总行数 < 150 行或字数 < 2000 字的，必须重新生成
9. **Mermaid 图表规范**: 仅使用兼容的图表类型：`flowchart`、`sequenceDiagram`、`gantt`、`pie`。禁止使用 `mindmap`、`architecture-beta`、`xychart-beta`、`timeline`、`quadrantChart` 等不兼容类型（会导致乱码）。
10. **跨平台兼容**: 所有 Python 脚本使用 `pathlib.Path` 处理路径，支持 macOS、Linux、Windows
11. **跨 Agent 兼容**: 技能设计为跨 Agent 平台兼容，可根据平台能力灵活调整深度研究方法

---
name: "repo-research"
description: "Deep-research a single GitHub repo on demand from a pasted URL, using a multi-round methodology (metadata → read code → competitor verification → quantitative signals) and producing a 7-section Chinese report. Detects existing reports, shows last-analysis time, and lets the user choose update / new-perspective / skip. Invoke when the user pastes a GitHub repo URL and asks to analyze it."
---

# 事A · 单 Repo 深度研究（= 深度研究方法论本身）

对话里贴一个 GitHub repo 链接即可触发：对该 repo 做 **4 轮深度研究**，产出 7 章中文报告。
本技能**自包含**——它既是"研究单个 repo"的流程，也是本项目全部研究工作所依赖的**方法论**（事B trending 汇总对榜上每个 repo 都调用它）。

> 质量靠**遵循并持续迭代本技能**保证，不靠脚本校验。研究中发现更好的做法，就直接改本文件。

---

## 触发条件

- 用户在对话中粘贴 GitHub repo 链接（如 `https://github.com/interviewstreet/hiring-agent`）并要求分析
- 或："分析这个 repo / 深度研究 {url} / 看看这个项目 / 深挖 owner/repo"

## 认证

所有 GitHub API 调用经 `gh` CLI（`gh api`），认证由 `gh auth login` 处理，**无需 token**。执行前确认 `gh auth status` 已登录。
`github.com/trending` 榜单页为 HTML 抓取（`trending_fetcher.py`），不经 gh。

---

## 主流程（4 步）

```
1. 解析链接 → owner/repo
   - 支持 https://github.com/{owner}/{repo}（去除 .git、尾部斜杠、?query、#frag、/tree/... 等）
   - 解析不出 owner/repo → 停止，请用户确认链接

2. 检查是否已有报告
   python3 scripts/trending_fetcher.py check {owner}/{repo}
   读取输出：exists / age_days / needs_update / name_mismatch / path

3. 分情况：
   ┌─ exists=false → 无报告 → 直接做【4 轮深度研究】（见下）
   └─ exists=true  → 有报告 → 停下来告诉用户：
        「{owner}/{repo} 上次分析在 {age_days} 天前（按文件修改时间）。请选择：
          A. 更新报告（用最新数据重研究，覆盖原文件）
          B. 换视角分析（不覆盖，新增带视角后缀的报告）
          C. 跳过（直接给你看现有报告 {path}）」
      —— 用 AskUserQuestion 给出 A/B/C 三选一，等待用户选择后再继续。
      · 选 A → 4 轮研究，覆盖 research_{owner}_{repo}.md
      · 选 B → 先问要哪个视角（安全 / 商业 / 架构 / 竞品 / 其他），
               再研究，输出 research_{owner}_{repo}_{topic}.md（topic 用英文小写短词）；
               7 章结构不变，但各章内容围绕该视角展开
      · 选 C → 读取并展示现有报告，结束（不重研究、不改文件）

4. 4 轮深度研究 → 写 7 章中文报告 → reports/research_{owner}_{repo}.md
```

---

## 4 轮深度研究方法论

四轮研究，每轮有**强制产出物（artifact）**。没有产出物的轮次视为未完成，不得进入下一轮。
核心原则：**技术分析必须基于真实代码，竞品数据必须经 API 核验，社区/趋势结论必须有量化信号支撑。**

| 轮次 | 目标 | 强制产出物 |
|------|------|-----------|
| R1 元数据 | 仓库客观事实 | 语言占比、头部 5 贡献者及提交数、近 10 次发版节奏、顶层目录树 |
| R2 读代码 | 代码驱动的架构理解 | 依赖清单要点 + 2-5 个核心源文件的关键发现（`[代码]` 证据） |
| R3 竞品核验 | 真实、可验证的竞品表 | ≥2 个竞品的 `gh` 实测 stars/license/最近推送 |
| R4 量化信号 | 数据驱动的活跃度/趋势 | 近 52 周提交曲线特征 + issue 响应概况 |

### Round 1 — 元数据（GitHub API）

直接执行 `scripts/github_api.py`：
```bash
python3 scripts/github_api.py <owner> <repo> summary
python3 scripts/github_api.py <owner> <repo> readme
python3 scripts/github_api.py <owner> <repo> contributors
python3 scripts/github_api.py <owner> <repo> releases
python3 scripts/github_api.py <owner> <repo> languages
python3 scripts/github_api.py <owner> <repo> tree
```
**产出物**：语言字节占比、头部 5 贡献者及 contributions、近 10 次发版（看 alpha/beta/rc → 正式版节奏）、顶层目录结构。

> 💡 **省事姿势（事C 沉淀）**：`contributors` / `releases` 走 `github_api.py` 会打印全量 raw JSON，噪声极大。要"头部贡献者 / 发版节奏"这类摘要时，直接用 `gh --jq` 一行取：
> ```bash
> gh api "repos/<owner>/<repo>/contributors?per_page=10" --jq '.[] | "\(.login) | \(.contributions)"'
> gh api "repos/<owner>/<repo>/releases?per_page=12" --jq '.[] | "\(.tag_name) | \(.published_at[0:10]) | prerelease=\(.prerelease)"'
> ```
> 由此可顺手判断**巴士因子**（单作者提交占比过高 = 可持续性风险，写进"社区活跃度"章）。

> ⚠️ **默认分支健康度核验（事C 沉淀，高价值）**：**别默认 `main`/`master` 上就是那个走红的代码**。大型项目重写、monorepo 迁移、代码搬到独立仓库时，默认分支可能是**空壳骨架**——只看它会得出完全错误的技术判断。出现以下任一信号就必须查分支：① 顶层 blob 数异常少（视频编辑器/框架却只有 ~100 文件）；② 入口/首页是 `hello world` 占位；③ README 或根路由标题含 `rewrite`/`beta`/`v2`/`new.`；④ 依赖清单缺了该品类的核心库（如视频编辑器没有 ffmpeg/媒体库）。核验命令：
> ```bash
> # 列所有分支
> gh api "repos/<owner>/<repo>/branches?per_page=50" --jq '.[].name'
> # 对比候选分支的文件数，找出真正装着生产代码的那个（数量最多/含核心目录的）
> for b in main dev staging rewrite; do n=$(gh api "repos/<owner>/<repo>/git/trees/$b?recursive=1" --jq '[.tree[]|select(.type=="blob")]|length' 2>/dev/null); echo "$b: $n blobs"; done
> # 确认某分支是否含品类核心目录（例：视频编辑器的 timeline/editor/renderer）
> gh api "repos/<owner>/<repo>/git/trees/<branch>?recursive=1" --jq '.tree[]|select(.path|test("timeline|editor|renderer";"i"))|.path' | head
> ```
> 读代码（R2）必须切到**真正的生产分支**（`?ref=<branch>` / `contents/...?ref=<branch>`），并在报告开头**显著提示**"默认分支不是生产代码，真代码在 X 分支"。老代码常被搬到 `-classic`/`-legacy`/`-old` 后缀的独立仓库，一并 `gh api repos/<owner>/<repo>-classic` 核验归档状态。

**可用命令**（`github_api.py` 末位参数）：
`summary` · `info` · `readme` · `tree` · `file <path>` · `languages` · `contributors` · `commits` · `commit_activity` · `issues` · `prs` · `releases` · `tags`

### Round 2 — 读代码（强制，决定"技术分析"章质量）

> ⚠️ 不读代码就写架构 = README 复述。技术分析章必须出现 ≥1 处 `[代码]` 证据。

1. 看 `tree` 输出定位入口与核心模块。
2. 读依赖清单（按语言择一）：`package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` / `pom.xml` / `build.gradle`。
3. 读 **2-5 个关键源文件**（入口文件、核心模块、关键配置）：
```bash
python3 scripts/github_api.py <owner> <repo> file package.json
python3 scripts/github_api.py <owner> <repo> file src/main.py
```
**产出物**：从真实代码得出的架构判断（模块划分、数据流、关键依赖、设计取舍），标注 `[代码]`。README 与代码冲突时以代码为准并指出冲突。

> 💡 **核验 README 声明（事C 沉淀）**：README 常有"50+ packs""支持 7 种语言"这类营销式数字。**用代码实测反查**，别照抄：
> ```bash
> # 递归列出文件树，统计某类文件数量（例：packs 规则文件）
> gh api "repos/<owner>/<repo>/git/trees/<default_branch>?recursive=1" \
>   --jq '[.tree[] | select(.path|test("^src/packs/.+/.+\\.rs$")) | select(.path|test("mod.rs|test")|not)] | length'
> ```
> 数字对得上就写"与代码一致"，对不上就指出差距——这类就地核验比复述 README 有价值得多。

### Round 3 — 竞品核验（强制，决定"竞品对比"章可信度）

> ⚠️ 禁止凭记忆填竞品 stars。所有竞品数值必须现查现填。

1. web_search 找同类项目（"{topic} alternatives" / "{topic} vs"）。
2. 把每个候选竞品解析为 `owner/repo`。
3. **逐个用 `gh` 拉真实数据**后才允许写入表格：
```bash
gh api -X GET repos/<owner>/<repo> --jq '"\(.full_name) | stars=\(.stargazers_count) | lang=\(.language) | license=\(.license.spdx_id) | pushed=\(.pushed_at[0:10])"'
```
**产出物**：≥2 个竞品的实测 stars/语言/协议/最近推送日期。闭源竞品标注"闭源"，不编造数字。

### Round 4 — 量化信号 + 深挖（决定"社区活跃度/发展趋势"章）

```bash
python3 scripts/github_api.py <owner> <repo> commit_activity   # 近 52 周周提交
python3 scripts/github_api.py <owner> <repo> issues            # issue 响应概况
```
- 用 commit_activity 描述趋势（"近 8 周均值 vs 全年均值"），替代"几乎每日提交"这类定性话术。
- 用 issues 的 created/closed 时间估算响应概况。
- web_fetch 有价值 URL 补充 sentiment 与 roadmap。
**产出物**：≥1 个量化结论（提交曲线特征 / issue 响应概况）。

> 💡 **一行出量化结论（事C 沉淀）**：
> ```bash
> # 近8周周均 vs 全年周均（差距大 = 已过爆发期/进入维护期，是客观信号非贬义）
> gh api "repos/<owner>/<repo>/stats/commit_activity" \
>   --jq 'map(.total) as $t | {year_avg:(($t|add)/($t|length)), last8_avg:(($t[-8:]|add)/8)}'
> # issue 开放/已关闭计数（排除 PR），估算关闭率与响应活跃度
> gh api -X GET "search/issues?q=repo:<owner>/<repo>+type:issue+state:closed" --jq '.total_count'
> ```

> 💡 **star 暴涨归因 + 分支活跃度陷阱（事C 沉淀）**：用户常问"为什么今天暴涨几千 star"。两步定位：
> ① **先排除代码驱动**——`stats/commit_activity` 只统计**默认分支**，若真代码在别的分支（见 R1 默认分支核验），这里的数字会误导；要直接查生产分支近况：
> ```bash
> gh api "repos/<owner>/<repo>/commits?sha=<prod_branch>&since=$(date -v-14d +%Y-%m-%dT00:00:00Z)&per_page=100" --jq 'length'  # 近14天提交数
> ```
> 若近期无新 release 且生产分支停更，则**暴涨是站外事件驱动，不是代码驱动**。
> ② **再定位站外事件**——`web_search "<repo> star surge <month year>"` + 关注竞品动向（对标商业产品涨价/封锁常是导火索）。把"代码侧无爆发 + 多语种媒体共振 + 里程碑效应"这类归因写进"发展趋势"章，比笼统说"项目火了"有价值。

---

## 报告：7 章中文结构

研究结果**必须**转换为下列 7 章中文结构存档，禁止直接存英文模板：

```
1. 项目概述   2-3 句定位与核心价值
2. 基本信息   表格：Stars / Forks / 语言 / 协议 / 创建时间 / 最近更新 / GitHub 链接（API 精确值）
3. 技术分析   技术栈 / 架构设计 / 核心功能（≥1 处 [代码] 证据）
4. 社区活跃度 贡献者分析 / Issue·PR 活跃度 / 最近动态（量化）
5. 发展趋势   版本演进 / Roadmap / 社区反馈
6. 竞品对比   表格，≥2 个竞品（gh 实测数据）
7. 总结评价   优势 / 劣势 / 适用场景
```

页脚统一（沿用现有 106 篇报告的格式，便于批量识别）：
```
---
*报告生成时间: YYYY-MM-DD*
*研究方法: github-deep-research 多轮深度研究*
```

### 证据就地标注（强制）

provenance 跟着结论**就地**标注，而非集中文末：

| 标签 | 含义 | 适用 |
|------|------|------|
| `[代码]` | 来自仓库真实源代码 | 技术分析、架构判断 |
| `[README]` | 来自项目自述文档 | 功能描述、定位 |
| `[API]` | 来自 GitHub API 精确数据 | stars/forks/贡献者/发版/提交曲线 |
| `[Web]` | 来自网络搜索/第三方报道 | sentiment、行业背景 |
| `[推测]` | 作者推断，无直接证据 | 商业模式、未公开 roadmap |

关键结论（尤其技术分析与竞品对比）应能追溯到 `[代码]`/`[API]`/`[Web]` 之一；纯推断必须标 `[推测]`，不得伪装成事实。

### Mermaid 图（可选）

仅用 `flowchart` / `sequenceDiagram` / `gantt` / `pie`；禁用 `mindmap`、`timeline` 等不兼容类型。

---

## 命名规则

| 场景 | 文件名 |
|------|--------|
| 默认 / 更新 | `research_{owner}_{repo}.md`（保留 GitHub 原始大小写与连字符，无日期后缀） |
| 换视角 | `research_{owner}_{repo}_{topic}.md`（topic 英文小写：security / business / architecture / ecosystem ...） |

示例：`research_interviewstreet_hiring-agent.md`、`research_interviewstreet_hiring-agent_security.md`

---

## 边界与注意事项

1. **数值精度**：Stars/Forks 用 API 精确整数，禁止 "17,000+" 类模糊表达。
2. **写入范围**：只写 `reports/`；临时文件放 `/tmp/github-trending-{date}/`，完成后清理，禁止写入报告、禁止提交。
3. **不凭记忆**：报告内容须读文件/API 确认，代码与 README 冲突以代码为准并指出。
4. **持续迭代（事C）**：本技能就是方法论本身。**每次研究完顺手做一次事C**——把踩到的坑、更省事的取数命令、更硬的证据要求折回本文件（判断标准：下次研究别的 repo 还用得上吗？用得上就进 skill）。skill 改动与报告放同一次 commit。

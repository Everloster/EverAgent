# github-trending-analyzer — 执行协议

> 唯一执行协议，自包含。本项目只做**三件事**，与三件事无关的一律不接。
> 由 EverAgent 根 `AGENTS.md` 的 D 类路由进入（贴 repo 链接 / trending 请求）。

---

## §0 项目使命（三件事）

| # | 事 | 触发 | 产出 | 对应 skill |
|---|----|------|------|-----------|
| ① | **单 repo 深度研究** | 对话贴 repo 链接 / "深挖 owner/repo" | `reports/research_{owner}_{repo}.md` | `skills/repo-research/` |
| ② | **trending 汇总** | "出日/周/月 trending 报告" | `reports/all-{period}-summary-{date}.md` + 榜上各 repo 报告 | `skills/trending-analyzer/` |
| ③ | **深度研究方法论** | 研究单个 repo 时遵循；随实践迭代 | 4 轮研究规范 | `skills/deep-research/` |

事①②都靠事③的方法论完成单个 repo 的研究。事③是可持续迭代的知识资产。

**产出报告后必须同步索引**（见 §4），不单独触发。

---

## §1 目录结构

```
github-trending-analyzer/
├── AGENTS.md          # 本文件（唯一协议）
├── README.md          # 人类导航 + quickstart
├── pyproject.toml
├── scripts/           # 全部脚本（只读，Agent 不改）
│   ├── trending_fetcher.py   # 抓榜单 + 报告缓存检查
│   ├── report_generator.py   # 汇总/单项目模板生成
│   ├── github_api.py         # GitHub API 封装（gh CLI）
│   └── validate_reports.py   # 8 项报告校验
├── skills/            # 三件事各一 skill
│   ├── repo-research/SKILL.md
│   ├── trending-analyzer/SKILL.md
│   └── deep-research/SKILL.md
├── assets/report_template.md
├── reports/           # 【唯一输出目录】research_*.md + all-*-summary-*.md
├── knowledge/reports_index.md   # 报告索引（V-INDEX 依赖）
└── tests/
```

**写入权限**：仅 `reports/`（`research_*.md` / `all-*.md`）和 `knowledge/reports_index.md`（仅追加）。其余全部只读。

---

## §2 环境与认证

- GitHub API 全部经 **`gh` CLI**（`gh api`），认证由 `gh auth login` 处理，**无需 token**。执行前确认 `gh auth status` 已登录。
- `github.com/trending` 榜单页为 HTML 抓取（`trending_fetcher.py`），不经 gh。
- 报告输出目录默认 `./reports`，可用环境变量 `TRENDING_REPORTS_DIR` 覆盖。
- 临时中间数据放 `/tmp/github-trending-{date}/`，完成后清理，**禁止写入报告、禁止提交**。

---

## §3 执行流程

### 事① 单 repo 研究

```
1. 解析链接 → owner/repo（去 .git / 尾斜杠 / ?query / #frag / /tree/...）
2. 检查缓存：python3 scripts/trending_fetcher.py check {owner}/{repo}
3. 分支：
   · 无报告        → 直接研究
   · 有报告        → 告知"上次 {age_days} 天前"，AskUserQuestion 三选一：
                      A 更新（覆盖） / B 换视角（问视角 → _{topic} 后缀，不覆盖） / C 跳过（展示现有）
4. 深度研究（4 轮，见 §3 事③）；换视角时各章侧重该视角
5. 写报告 → 验证（§4，exit 0）→ 同步索引（§4）
```

### 事② trending 汇总

```
1. 抓榜单：python3 scripts/trending_fetcher.py fetch {period} [{language}]
           period ∈ daily|weekly|monthly；空数组则停止告知
2. 逐 repo 检查缓存（同上 check）：needs_update=false 记入"缓存复用"跳过
3. 逐 repo 深度研究（仅 needs_update=true，4 轮，见事③）
4. 每份报告验证（§4，exit 0）
5. 生成汇总：python3 scripts/report_generator.py summary {period} '{REPOS_JSON}' \
             reports/all-{period}-summary-{date}.md '{MISSING_JSON}' 'github-deep-research 多轮深度研究'
   汇总须含：概览表 / 语言分布 / 项目列表(精确增长) / 趋势分析(🔥热门·🏢大厂·🔬创新·📊语言 四子章不可缺) /
             报告链接(./research_*.md) / 报告状态说明(如实区分新生成与缓存复用)
6. 同步索引（§4）
```

### 事③ 深度研究方法论（4 轮，每轮有强制产出物）

见 `skills/deep-research/SKILL.md`。核心原则：**技术分析必须基于真实代码，竞品数据必须经 API 核验，社区/趋势结论必须有量化信号支撑。**

| 轮次 | 目标 | 强制产出物 |
|------|------|-----------|
| R1 元数据 | 客观事实 | 语言占比 / 头部 5 贡献者 / 近 10 次发版 / 顶层目录树 |
| R2 读代码 | 代码驱动的架构理解 | 依赖清单 + 2-5 核心源文件的 `[代码]` 证据 |
| R3 竞品核验 | 可验证竞品表 | ≥2 竞品的 `gh` 实测 stars/license/最近推送 |
| R4 量化信号 | 数据驱动活跃度/趋势 | 近 52 周提交曲线特征 + issue 响应概况 |

研究结果转换为 **7 章中文结构**存档（禁止直接存英文模板）：
`1.项目概述 2.基本信息 3.技术分析 4.社区活跃度 5.发展趋势 6.竞品对比 7.总结评价`

关键结论就地标注证据等级 `[代码]`/`[API]`/`[Web]`/`[推测]`。

---

## §4 验证与索引

### 报告命名

```
单项目：reports/research_{owner}_{repo}.md   （保留 GitHub 原始大小写与连字符，无日期后缀）
换视角：reports/research_{owner}_{repo}_{topic}.md   （topic 英文小写短词）
汇总：  reports/all-{period}-summary-{date}.md   （period 小写；date=YYYY-MM-DD）
```
✅ `research_hsliuping_TradingAgents-CN.md`　❌ `research_hsliuping_tradingagents_cn.md`（大小写/连字符丢失）　❌ 带日期后缀

### 8 项校验（每次写报告后必跑，exit 0 才合格）

```bash
python3 scripts/validate_reports.py {owner}/{repo}        # 单篇
python3 scripts/validate_reports.py --fail-only --index   # 全量 + 索引一致性
```

| ID | 规则 |
|----|------|
| V-NAME | 文件名 `research_{owner}_{repo}.md`，禁日期后缀 |
| V-STRUCT | 7 个中文章节均在 |
| V-LEN | 总行数 ≥ 150 |
| V-PREC | 无模糊数值（禁 "17,000+" 类） |
| V-COMP | 竞品对比数据行 ≥ 2 |
| V-FOOTER | 页脚含 `*报告生成时间: YYYY-MM-DD*` 与 `*研究方法: github-deep-research 多轮深度研究*` |
| V-PATH | 无宿主机路径 |
| V-LANG | 无英文模板标记 |

### 索引同步（产出新报告后）

追加缺失条目到 `knowledge/reports_index.md`（`## Repository Deep Reports` 列表，字母序，`- {owner}/{repo}` 保留原始大小写）。**禁止删除已有条目。** 汇总报告追加到 `## Summary Reports` 表。

---

## §5 提交规范

```bash
git add reports/ knowledge/ AGENTS.md README.md
git commit -m "[github-trending-analyzer] {任务}: {描述}"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> git 身份默认 `coco-openrouter-3o`（见根 `AGENTS.md`）。合并冲突无法自动解决时：停止，通知用户仲裁。

---

## §6 防幻觉边界

> 共享规则见根 [`docs/PROTOCOL_COMMON.md`](../docs/PROTOCOL_COMMON.md) §A。本项目特有补充：

1. 只有 `knowledge/reports_index.md` 中列出的 repo 才有报告，其余禁止推测。
2. 报告内容须读文件确认，禁止凭记忆复述。
3. Stars/Forks 等数值必须用 GitHub API 精确返回值，禁止估算或"约"。
4. 汇总"报告状态说明"须如实区分新生成与缓存复用，禁止虚报"全部新生成"。
5. 竞品对比数据须来自实际研究，不得编造。

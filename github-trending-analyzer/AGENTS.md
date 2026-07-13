# github-trending-analyzer — 执行协议

> 唯一执行协议，自包含。本项目只做**两件事**，与两件事无关的一律不接。
> 由 EverAgent 根 `AGENTS.md` 的 D 类路由进入（贴 repo 链接 / trending 请求）。

---

## §0 项目使命（两件事）

| # | 事 | 触发 | 产出 | 对应 skill |
|---|----|------|------|-----------|
| A | **单 repo 深度研究** | 对话贴 repo 链接 / "深挖 owner/repo" | `reports/research_{owner}_{repo}.md` | `skills/repo-research/` |
| B | **trending 汇总** | "出日/周/月 trending 报告" | `reports/all-{period}-summary-{date}.md` + 榜上各 repo 报告 | `skills/trending-analyzer/` |

**事A 就是深度研究方法论本身**（4 轮研究 + 7 章中文报告，全部写在 `skills/repo-research/SKILL.md`）。
**事B 建立在事A 之上**：抓榜单 → 对榜上每个 repo 做一次事A → 汇总成趋势报告。

> **质量怎么保证？** 靠**遵循并持续迭代 skill 规范**，不靠脚本校验。研究中总结出更好的做法，直接改 `skills/repo-research/SKILL.md`，让下一次更强。本项目**不做结果校验脚本、不设 exit-0 门禁**。

---

## §1 目录结构

```
github-trending-analyzer/
├── AGENTS.md          # 本文件（唯一协议）
├── README.md          # 人类导航 + quickstart
├── pyproject.toml
├── scripts/           # 辅助脚本（取数/抓榜/生模板，Agent 不改）
│   ├── trending_fetcher.py   # 抓榜单 + 报告存在性检查
│   ├── report_generator.py   # 汇总/单项目模板生成
│   └── github_api.py         # GitHub API 封装（gh CLI）
├── skills/            # 两件事各一 skill
│   ├── repo-research/SKILL.md      # 事A：单 repo 深度研究（含 4 轮方法论）
│   └── trending-analyzer/SKILL.md  # 事B：trending 汇总
├── assets/report_template.md
├── reports/           # 【唯一输出目录】research_*.md + all-*-summary-*.md
├── knowledge/reports_index.md   # 报告索引（人类导航，可选维护）
└── tests/             # 脚本单元测试（仅护脚本本身，非报告校验）
```

**写入权限**：Agent 只写 `reports/`（`research_*.md` / `all-*.md`）。`knowledge/reports_index.md` 可选追加以方便人类浏览。其余只读。

---

## §2 环境与认证

- GitHub API 全部经 **`gh` CLI**（`gh api`），认证由 `gh auth login` 处理，**无需 token**。执行前确认 `gh auth status` 已登录。
- `github.com/trending` 榜单页为 HTML 抓取（`trending_fetcher.py`），不经 gh。
- 报告输出目录默认 `./reports`，可用环境变量 `TRENDING_REPORTS_DIR` 覆盖。
- 临时中间数据放 `/tmp/github-trending-{date}/`，完成后清理，**禁止写入报告、禁止提交**。

---

## §3 执行流程

### 事A 单 repo 深度研究

完整规范见 `skills/repo-research/SKILL.md`。要点：

```
1. 解析链接 → owner/repo（去 .git / 尾斜杠 / ?query / #frag / /tree/...）
2. 检查是否已有报告：python3 scripts/trending_fetcher.py check {owner}/{repo}
3. 分支：
   · 无报告  → 直接做 4 轮研究
   · 有报告  → 告知"上次 {age_days} 天前"，AskUserQuestion 三选一：
               A 更新（覆盖） / B 换视角（问视角 → _{topic} 后缀，不覆盖） / C 跳过（展示现有）
4. 4 轮研究 → 转 7 章中文 → 写 reports/research_{owner}_{repo}.md
```

**4 轮方法论（每轮有强制产出物）**：

| 轮次 | 目标 | 强制产出物 |
|------|------|-----------|
| R1 元数据 | 客观事实 | 语言占比 / 头部 5 贡献者 / 近 10 次发版 / 顶层目录树 |
| R2 读代码 | 代码驱动的架构理解 | 依赖清单 + 2-5 核心源文件的 `[代码]` 证据 |
| R3 竞品核验 | 可验证竞品表 | ≥2 竞品的 `gh` 实测 stars/license/最近推送 |
| R4 量化信号 | 数据驱动活跃度/趋势 | 近 52 周提交曲线特征 + issue 响应概况 |

核心原则：**技术分析必须基于真实代码，竞品数据必须经 API 核验，社区/趋势结论必须有量化信号支撑。**
关键结论就地标注证据等级 `[代码]`/`[API]`/`[Web]`/`[推测]`。

### 事B trending 汇总

完整规范见 `skills/trending-analyzer/SKILL.md`。要点：

```
1. 抓榜单：python3 scripts/trending_fetcher.py fetch {period} [{language}]
           period ∈ daily|weekly|monthly；空数组则停止告知
2. 逐 repo 检查是否已有报告（同上 check）：needs_update=false 记入"缓存复用"跳过
3. 逐 repo 做事A（仅 needs_update=true）
4. 生成汇总：python3 scripts/report_generator.py summary {period} '{REPOS_JSON}' \
             reports/all-{period}-summary-{date}.md '{MISSING_JSON}' 'github-deep-research 多轮深度研究'
   汇总须含：概览表 / 语言分布 / 项目列表(精确增长) / 趋势分析(🔥热门·🏢大厂·🔬创新·📊语言 四子章不可缺) /
             报告链接(./research_*.md) / 报告状态说明(如实区分新生成与缓存复用)
```

---

## §4 报告命名与索引

### 报告命名

```
单项目：reports/research_{owner}_{repo}.md   （保留 GitHub 原始大小写与连字符，无日期后缀）
换视角：reports/research_{owner}_{repo}_{topic}.md   （topic 英文小写短词）
汇总：  reports/all-{period}-summary-{date}.md   （period 小写；date=YYYY-MM-DD）
```
✅ `research_hsliuping_TradingAgents-CN.md`　❌ `research_hsliuping_tradingagents_cn.md`（大小写/连字符丢失）　❌ 带日期后缀

报告页脚统一沿用现有 106 篇的格式：
```
---
*报告生成时间: YYYY-MM-DD*
*研究方法: github-deep-research 多轮深度研究*
```

### 索引（可选）

`knowledge/reports_index.md` 是给人类浏览的导航清单，**非门禁**。产出新报告后可顺手追加条目（`## Repository Deep Reports` 字母序、保留原始大小写；汇总追加到 `## Summary Reports` 表），但不追加也不阻塞任务。

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

1. 报告内容须读文件/API 确认，禁止凭记忆复述。
2. Stars/Forks 等数值必须用 GitHub API 精确返回值，禁止估算或"约"。
3. 汇总"报告状态说明"须如实区分新生成与缓存复用，禁止虚报"全部新生成"。
4. 竞品对比数据须来自实际 `gh` 核验，不得编造。

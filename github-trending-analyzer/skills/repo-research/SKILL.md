---
name: "repo-research"
description: "Analyze a single GitHub repo on demand from a pasted URL. Detects existing reports, shows last-analysis time, and lets the user choose update / new-perspective / skip. Invoke when the user pastes a GitHub repo URL and asks to analyze it."
---

# 事① 单 Repo 深度研究（对话贴链接触发）

对话里贴一个 GitHub repo 链接即可触发：对该 repo 用 `deep-research` skill 做深度研究并按命名规则输出报告。**若已有报告，先报告上次分析时间，由用户决定更新 / 换视角 / 跳过。**

> 完整执行规范见 [`../../AGENTS.md`](../../AGENTS.md) **事① 单 Repo 研究** 章节，本文件为技能摘要。

## 触发条件

- 用户在对话中粘贴 GitHub repo 链接（如 `https://github.com/interviewstreet/hiring-agent`）并要求分析
- 或："分析这个 repo / 深度研究 {url} / 看看这个项目"

## 认证

所有 GitHub API 调用经 `gh` CLI（`gh api`），认证由 `gh auth login` 处理，**无需 token**。执行前确认 `gh auth status` 已登录。

## 核心流程（5 步）

```
1. 解析链接 → owner/repo
   - 支持 https://github.com/{owner}/{repo}（去除 .git、尾部斜杠、?query、#frag、/tree/... 等）
   - 解析不出 owner/repo → 停止，请用户确认链接

2. 检查缓存
   python3 scripts/trending_fetcher.py check {owner}/{repo}
   读取输出：exists / age_days / needs_update / name_mismatch / path

3. 分情况：
   ┌─ exists=false → 无报告 → 直接走【深度研究】（见第 4 步）
   └─ exists=true  → 有报告 → 停下来告诉用户：
        「{owner}/{repo} 上次分析在 {age_days} 天前（按文件修改时间）。请选择：
          A. 更新报告（用最新数据重研究，覆盖原文件）
          B. 换视角分析（不覆盖，新增带视角后缀的报告）
          C. 跳过（直接给你看现有报告 {path}）」
      —— 用 AskUserQuestion 给出 A/B/C 三选一，等待用户选择后再继续。
      · 选 A → 深度研究，覆盖 research_{owner}_{repo}.md
      · 选 B → 先问用户要哪个视角（安全 / 商业 / 架构 / 竞品 / 其他），
               再深度研究，输出 research_{owner}_{repo}_{topic}.md（topic 用英文小写短词）
      · 选 C → 读取并展示现有报告，结束（不重新研究、不改文件）

4. 深度研究（调用 github-deep-research，4 轮，同 TT-2 Step 2）
   - 换视角时：在研究中显著侧重该视角（如 security 视角重点查 CVE/权限/依赖风险），
     7 章结构不变，但各章内容围绕该视角展开。

5. 写报告 → 验证 → 同步索引
   - 默认报告：research_{owner}_{repo}.md（7 章中文 + 标准页脚）
   - 换视角报告：research_{owner}_{repo}_{topic}.md（同样 7 章 + 页脚；标题注明视角）
   - 验证：python3 scripts/validate_reports.py {owner}/{repo}   # exit 0 才算合格
     （换视角文件验证器按文件名校验，V-NAME 接受非日期后缀）
   - 同步索引：执行 TT-3
```

## 命名规则

| 场景 | 文件名 |
|------|--------|
| 默认 / 更新 | `research_{owner}_{repo}.md`（保留 GitHub 原始大小写与连字符，无日期后缀） |
| 换视角 | `research_{owner}_{repo}_{topic}.md`（topic 为英文小写：security / business / architecture / ecosystem ...） |

示例：`research_interviewstreet_hiring-agent.md`、`research_interviewstreet_hiring-agent_security.md`

## 与「事② trending 汇总」的区别

| | 事② trending 汇总 | 事① 本技能 |
|---|---|---|
| 触发 | "出 trending 报告" | 对话贴单个链接 |
| 已有报告时 | 缓存有效则跳过 | **给出上次时间，A/B/C 三选一交互** |
| 换视角 | 不支持 | 支持，带 `_{topic}` 后缀，不覆盖原报告 |
| 研究 / 验证 / 索引 | 同 | 完全复用 |

## 注意事项

1. 研究必须调用 `deep-research` skill，结果转 7 章中文格式，禁止存英文模板
2. Stars/Forks 用 API 精确值，禁止"17,000+"
3. 页脚统一：`*报告生成时间: YYYY-MM-DD*` / `*研究方法: github-deep-research 多轮深度研究*`
4. 临时文件放 `/tmp/github-trending-{date}/`，完成清理，禁止写入报告
5. 写入仅限 `reports/` 与 `knowledge/`
6. 每次产出新报告后必须同步 `knowledge/reports_index.md`
ng-reports/` 与 `knowledge/`
6. 每次产出新报告后必须执行 TT-3 同步索引

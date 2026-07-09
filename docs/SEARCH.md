# 搜索阶梯（Search Ladder）

> 全局搜索/查资料方法。查东西时**从最省钱有效的档位开始，不够再往上爬**，而不是一上来就动用重工具。
> 被根 [AGENTS.md](../AGENTS.md) §4 引用；任何领域、任何任务都适用。

---

## 一、先判断查什么，再选档位

| 你要的东西 | 直接去 |
|-----------|--------|
| 代码库里的事实（某函数在哪、某配置值） | **本地工具**：Grep / Glob / Read，别联网 |
| 一个明确网址的内容 | **抓取**：`llm ... -o url_context` 或 WebFetch |
| 需要最新事实 + 出处 | **联网搜索**：见下面阶梯 |

---

## 二、搜索阶梯（从下往上爬，够用就停）

### 档位 0 · 本地优先（零成本）
先问：这真的需要联网吗？代码/文件里的事用 Grep/Glob/Read。

### 档位 1 · llm + Gemini websearch（首选联网档，已装好）
本机已装 `llm` 0.31 + `llm-gemini` 0.32，Key 已配。**这是默认联网搜索入口**：轻量、带 Google 实时接地、给结论快。

```bash
# 联网搜索 + 事实问答（google_search grounding）
llm -m gemini-2.5-flash -o google_search 1 "你的问题，越具体越好"

# 抓取并总结指定网页（url_context）
llm -m gemini-2.5-flash -o url_context 1 "总结这个页面 https://example.com/x"

# 需要更强推理时换 pro，可两能力叠加
llm -m gemini-2.5-pro -o google_search 1 -o url_context 1 "你的问题"
```

要点：
- `-o google_search 1` = 打开 Google 实时检索接地；结论带时效性（已实测能返回几天前的新闻）。
- `-o url_context 1` = 让模型抓取你给的 URL 原文再回答。
- `gemini-2.5-flash` 快而省，先用它；要深推理/长文综合再上 `gemini-2.5-pro`。
- **验证提醒**：Gemini 给的结论仍需按 [METHODOLOGY.md](../METHODOLOGY.md) §二标注证据；关键事实让它给出来源 URL，必要时用档位 2 复核。

### 档位 2 · 内置 WebSearch / WebFetch（交叉验证 & 拿原文）
当需要**多来源交叉验证**、或要拿到**结构化搜索结果列表 / 网页原始 markdown** 时：
- `WebSearch` — 拿到标题+URL 列表，适合"有哪些来源"。
- `WebFetch` — 把某个 URL 转 markdown 再提问，适合精读单页。

用途分工：档位 1 给"快速有出处的结论"，档位 2 给"我要亲自看原文/多源对比"。

### 档位 3 · 专业搜索 Skill（重任务才上）
需要**深度、多轮、结构化产出**时，用已装的 Skill（按需选一个，别滥用）：

| 场景 | Skill |
|------|-------|
| 通用联网研究/查找 | `agent-reach` |
| 抓取/搜索网页并要干净 markdown | `firecrawl-search` / `firecrawl-scrape` |
| 出带引用的深度研究报告 | `firecrawl-deep-research` |
| 找论文/学术 | `firecrawl-research-papers` |
| 中文 AI 资讯/热榜/社交语义搜索 | `ai-radar` / `sensight` |

> 触发规则：用户点名某 Skill、或任务明显匹配其描述时才用；用完即止，不跨轮沿用。

---

## 三、默认决策树

```
要查东西
  ├─ 在代码/文件里?           → 档位0 Grep/Glob/Read
  ├─ 有明确 URL 要读?         → llm -o url_context / WebFetch
  ├─ 要最新事实 + 快结论?      → 档位1 llm -o google_search  ← 默认从这里开始
  ├─ 要多源交叉/亲看原文?      → 档位2 WebSearch + WebFetch
  └─ 要深度多轮结构化产出?     → 档位3 对应 Skill
```

**原则**：能在低档位解决就不往上爬；往上爬要有理由（时效不够、需交叉验证、需深度产出）。

---

## 四、维护

发现更好的搜索工具/用法（新模型、新 Skill、更优命令）→ 更新本文件。
安装类变更（如换 Gemini 模型、加插件）记得同步这里的命令示例。

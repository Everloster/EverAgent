## EverAgent CLAUDE.md
## Layered on top of ~/.claude/CLAUDE.md (global rules)
## Project-specific rules only. Do not duplicate global rules.

---

## 语言

- 默认用中文回答用户（除非用户当次明确要求用其他语言）。

---

## 定位

EverAgent 是个人学习知识库。8 个子项目按工作模式分为 4 类（详见 [AGENTS.md](./AGENTS.md) §1），研究方法论见 [METHODOLOGY.md](./METHODOLOGY.md)：

| 类 | 项目 | 工作模式 |
|----|------|---------|
| **A 知识研究** | ai / cs / philosophy / psychology / biology-learning | 对话启发学习 → 真读原文 → 产出高质量报告 |
| **B 代码实践** | ai-practice | 各类 AI 技术的低成本可运行 demo + 教学笔记（数值须来自实际运行） |
| **C 播客学习** | podcast-learning | 链接 → 本地转写（whisper.cpp）→ 润色 → 总结/讨论 → 报告 |
| **D 开源研究** | github-trending-analyzer | 贴 repo 链接 → 输出/更新研究报告（自带协议与验证脚本） |

先识别用户意图属于哪一类，再读对应项目的 `AGENTS.md` 独立工作。B/C/D 有各自特化工作流，不套用 A 类的报告流程。

---

## Analysis Mode（A 类默认 · 五个知识研究领域）

- Lead with the finding. Context and methodology after.
- Every numerical claim must include source or derivation. No silent estimation.
- When uncertain, state confidence explicitly: "likely", "unclear from the text", "insufficient data".
- Never fabricate data, statistics, author claims, or experiment results.
- Distinguish observed facts from inferences — label inferences explicitly.
- 报告必须遵守 METHODOLOGY.md：真读原文、证据分级标注、知识截止日期处理、结尾「思考与追问」三问。
- 报告必须带完整 frontmatter（title, domain, report_type, status, updated_on）；`report_type` 取值随项目而定（A 类 paper_analysis/knowledge_report、B 类 experiment_analysis、C 类 episode_summary/cross_episode/concept_tracking）。
- 写报告前先读该领域的 PROFILE.md / MAP.md / wiki，避免重复已掌握的内容。
- 防幻觉、提交、push flow 等通用规则见 [docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md)。

---

## Git Identity & Commit

- 首次提交前设置身份并校验：
  ```bash
  git config user.name "<当前模型名>"
  git config user.email "<供应商 noreply 邮箱>"
  python3 scripts/git_identity.py validate
  ```
  pre-commit hook 会拦截身份不符的提交。
- Commit 格式与 push flow 见 [docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §B/§C。
- `.env` 绝不提交；commit message 不含 token。

---

## Wiki 操作

每个领域有 `wiki/` 层（concepts / entities / syntheses / open-questions.md）。
写完报告后：更新相关概念/实体页（追加链接而非重写）、未解问题汇入 open-questions.md、必要时归档 syntheses。

---

## Override Rule
User instructions > this file > ~/.claude/CLAUDE.md (global).

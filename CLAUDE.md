## EverAgent CLAUDE.md
## Layered on top of ~/.claude/CLAUDE.md (global rules)
## Project-specific rules only. Do not duplicate global rules.

---

## 定位

EverAgent 是个人学习知识库。默认所有工作都是「分析模式」：研究一个主题、产出高质量报告。
完整协议见 [AGENTS.md](./AGENTS.md)，研究方法论见 [METHODOLOGY.md](./METHODOLOGY.md)。

例外：`github-trending-analyzer/` 是自动化工具项目，按其自身 AGENTS.md 工作。

---

## Analysis Mode（默认 · 所有学习领域）

- Lead with the finding. Context and methodology after.
- Every numerical claim must include source or derivation. No silent estimation.
- When uncertain, state confidence explicitly: "likely", "unclear from the text", "insufficient data".
- Never fabricate data, statistics, author claims, or experiment results.
- Distinguish observed facts from inferences — label inferences explicitly.
- 报告必须遵守 METHODOLOGY.md：真读原文、证据分级标注、知识截止日期处理、结尾「思考与追问」三问。
- 报告必须带完整 frontmatter（title, domain, report_type, status, updated_on）。
- 写报告前先读该领域的 PROFILE.md / MAP.md / wiki，避免重复已掌握的内容。

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

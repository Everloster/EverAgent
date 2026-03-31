## EverAgent CLAUDE.md
## Merged from: analysis + coding + agents profiles
## Layered on top of ~/.claude/CLAUDE.md (global rules)

---

## Analysis Mode (Default - all learning subprojects)
## Source: CLAUDE.analysis.md

- Lead with the finding. Context and methodology after.
- Every numerical claim must include source or derivation. No silent estimation.
- When uncertain, state confidence explicitly: "likely", "unclear from the text", "insufficient data".
- Never fabricate data, statistics, author claims, or experiment results.
- Distinguish observed facts from inferences - label inferences explicitly.
- Report format: summary (<=3 bullets) -> supporting data -> limitations. In that order.
- Tables and bullets over prose. Prose only when structure would lose meaning.
- Do not round aggressively. Preserve meaningful precision from source.

## Paper Analysis Rules
- Read the source file before writing any analysis. Never summarize from memory.
- All reports must include complete YAML frontmatter: title, domain, report_type, status, updated_on.
- Follow the 7-step analysis template defined in docs/SKILL_TEMPLATES.md exactly.
- Before modifying any report, read the subproject's CONTEXT.md first.
- Do not cross-reference content between subprojects unless explicitly asked.

---

## Coding Mode (github-trending-analyzer subproject only)
## Source: CLAUDE.coding.md

- Lead with code. Explain only when logic is non-obvious.
- Read existing code before making changes. Never edit blind.
- No abstractions for single-use operations.
- No speculative features or future-proofing.
- No docstrings or type hints on unchanged code.
- Only handle errors for realistic failure scenarios.
- Stay within scope. Do not refactor surrounding code when fixing a bug.

---

## Agent Execution Mode (when running multi-agent workflows per AGENTS.md)
## Source: CLAUDE.agents.md

- Output must be structured and parseable without post-processing (JSON, bullets, tables).
- Execute tasks without narration. No status updates like "Now I will...".
- Skip confirmations for clearly defined tasks.
- On failure: state failure reason and last attempted action, then stop. Do not retry silently.
- Never invent file paths, API endpoints, function names, or field names.
- If a value is unknown: return null or UNKNOWN. Never guess.
- Do not reference file contents that have not been read in this session.
- One subproject per agent session. Do not operate across subprojects concurrently.
- All string output must be JSON-serializable (ASCII only, no smart quotes or unicode).

---

## Override Rule
User instructions > this file > ~/.claude/CLAUDE.md (global).

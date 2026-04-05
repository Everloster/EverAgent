## EverAgent CLAUDE.md
## Layered on top of ~/.claude/CLAUDE.md (global rules)
## This file only contains PROJECT-SPECIFIC rules. Do not duplicate global rules.

---

## Mode Router

```
Working on github-trending-analyzer/ ? -> Coding Mode
Running multi-agent workflow per AGENTS.md ? -> Agent Execution Mode
Everything else (learning subprojects) -> Analysis Mode (default)
```

---

## Analysis Mode (Default - all learning subprojects)

- Lead with the finding. Context and methodology after.
- Every numerical claim must include source or derivation. No silent estimation.
- When uncertain, state confidence explicitly: "likely", "unclear from the text", "insufficient data".
- Never fabricate data, statistics, author claims, or experiment results.
- Distinguish observed facts from inferences - label inferences explicitly.
- Report format: summary (<=3 bullets) -> supporting data -> limitations. In that order.
- Do not round aggressively. Preserve meaningful precision from source.

### Paper Analysis Rules
- All reports must include complete YAML frontmatter: title, domain, report_type, status, updated_on.
- Follow the 7-step analysis template defined in `docs/SKILL_TEMPLATES.md`. If that file is missing or outdated, fall back to the per-project `skills/paper_analysis/SKILL.md`.
- Before modifying any report, read the subproject's CONTEXT.md first.
- Do not cross-reference content between subprojects unless explicitly asked.

---

## Coding Mode (github-trending-analyzer only)

- Only handle errors for realistic failure scenarios.
- No additional rules beyond global ~/.claude/CLAUDE.md.

---

## Agent Execution Mode (multi-agent workflows per AGENTS.md)

- Output must be structured and parseable without post-processing (JSON, bullets, tables).
- Execute tasks without narration. Skip confirmations for clearly defined tasks.
- On failure: state failure reason and last attempted action, then stop. Do not retry silently.
- One subproject per agent session. Do not operate across subprojects concurrently.
- All string output must be JSON-serializable (ASCII only, no smart quotes or unicode).

---

## Git Identity & Commit Rules

- **Identity guard**: Before every commit, verify `git config user.name` is non-empty. The name is dynamically set by the runtime model and does not need to match a predefined list.
- **Commit format**: Follow AGENTS.md SS4 exactly:
  ```
  [{task-type}] {scope}: {description}

  Agent: {model name}
  Task-Type: {project-optimization | new-project | task-execution}
  ```
- **Push flow**: `git fetch origin main` -> `git merge --ff-only FETCH_HEAD` -> `git push origin main`. Use `GIT_NO_OPTIONAL_LOCKS=1` prefix on all git network commands.
- **Token safety**: `.env` must never be committed. Commit messages must never contain tokens.

---

## Override Rule
User instructions > this file > ~/.claude/CLAUDE.md (global).

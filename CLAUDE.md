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

- **Identity guard**: Before the first commit in any session, set git author to the current model name and noreply email:
  ```bash
  git config user.name "GPT-5 Codex"           # replace with actual running model name, or set EVERAGENT_GIT_NAME
  git config user.email "noreply@openai.com"   # replace with the current vendor noreply email, or set EVERAGENT_GIT_EMAIL
  python3 scripts/git_identity.py validate
  ```
  A pre-commit hook enforces this — commits from personal git identities or mismatched model identities are blocked automatically.
- **Commit format**: Follow AGENTS.md SS4 exactly:
  ```
  [{task-type}] {scope}: {description}

  Agent: {model name}
  Task-Type: {project-optimization | new-project | task-execution}
  ```
- **Push flow**: `git fetch origin main` -> `git merge --ff-only FETCH_HEAD` -> `git push origin main`. Use `GIT_NO_OPTIONAL_LOCKS=1` prefix on all git network commands.
- **Token safety**: `.env` must never be committed. Commit messages must never contain tokens.

---

## Wiki Operations

Every learning subproject has a `wiki/` layer (Karpathy persistent wiki pattern).

**On every Ingest (after writing the report):**
1. Update or create `wiki/entities/` pages for mentioned persons / orgs
2. Update or create `wiki/concepts/` pages for core concepts introduced
3. Append one line to `wiki/log.md`
4. Update `wiki/index.md` (add new entries under the correct section)

**On Query (multi-concept synthesis):**
- Read `wiki/index.md` first to locate relevant pages
- If the answer synthesizes ≥ 3 concepts, archive the result to `wiki/syntheses/`
- Append one line to `wiki/log.md`

**On Lint (every ~15 ingests):**
- Check for orphan pages, stub pages, contradictions, missing cross-references
- Report findings, then fix or flag

**Page locations:**
```
{project}/wiki/
├── index.md          ← content catalog, updated on every ingest
├── log.md            ← append-only operation log
├── entities/         ← persons, orgs, systems
├── concepts/         ← core ideas and techniques
└── syntheses/        ← archived query results
```

---

## Override Rule
User instructions > this file > ~/.claude/CLAUDE.md (global).

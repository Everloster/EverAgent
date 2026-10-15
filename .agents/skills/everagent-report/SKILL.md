---
name: everagent-report
description: "Research, write, revise, or audit a durable EverAgent report. Use when the user explicitly asks to study, investigate, deep-read, or produce/update a report; skip brief answers and GitHub links without a report request."
---

# EverAgent Report

Produce a report that can be read independently of the current conversation.

1. Route by user intent and read only the target project's `AGENTS.md`.
2. Read [REPORT_WORKFLOW.md](../../../docs/REPORT_WORKFLOW.md) for task selection, context loading, the ACE loop, and completion criteria.
3. Read only the relevant sections of [METHODOLOGY.md](../../../METHODOLOGY.md) and the one domain skill matching the requested report type.
4. Use `eacli context get/search` to locate existing work. Open only matched reports or wiki pages; do not scan the whole knowledge base by default.
5. Read primary material before drafting. Keep source facts, source interpretation, and your analysis distinguishable.
6. Add `quality_schema: "report-v1"` to a new report and preserve valid metadata when revising an existing one.
7. After drafting, make the smallest justified context delta. Update PROFILE only for an explicit user preference or interest; update MAP/wiki only for durable coverage or open questions.
8. Finish with:

```bash
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

Use the domain-specific auditor as well when its `AGENTS.md` requires one. Fix errors caused by the current task; report legacy warnings without mass rewriting unrelated reports.

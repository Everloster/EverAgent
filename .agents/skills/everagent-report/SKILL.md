---
name: everagent-report
description: "Create, revise, or audit a durable EverAgent research report when explicitly requested; skip brief answers, simple lookups, and bare repository links."
---

# EverAgent Report

This skill is a router. Load only the branch needed for the current report.

| Need | Read or run |
|---|---|
| Common research, drafting, completion | [REPORT_WORKFLOW.md](../../../docs/REPORT_WORKFLOW.md) |
| Evidence manifest, independent review, escalation | [REPORT_QUALITY_GATE.md](../../../docs/REPORT_QUALITY_GATE.md) |
| Metadata or migration | [REPORT_METADATA.md](../../../docs/REPORT_METADATA.md) |
| Domain-specific evidence and format | The target project's `AGENTS.md`, then one matching domain skill |
| Existing topic | Locate the current report and update it instead of creating a duplicate |

Use `eacli context get/search` only when prior project knowledge is relevant. Keep the task's goal, deliverable, required checks, and stop conditions in the current conversation; do not create a planning artifact unless it is itself requested.

Finish only when the selected workflow's observable completion conditions pass. If a skill instruction conflicts with the user's explicit request or would stop authorized work, follow the user and identify the conflicting instruction.

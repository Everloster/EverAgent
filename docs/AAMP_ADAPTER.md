# EverAgent AAMP Adapter

> Purpose: define how EverAgent projects AAMP 1.1 control-plane semantics onto the existing Git/file-based task system.

EverAgent remains a local, Git-audited research workspace. It does not claim full AAMP runtime compatibility, mailbox registration, SMTP submission, JMAP retrieval, or SDK helper compatibility. Instead, it adopts the AAMP core task vocabulary as a stable interoperability layer for task lifecycle events, local state projection, and dashboard observation.

Reference specification: [`AAMP_CORE_SPECIFICATION.md`](../AAMP_CORE_SPECIFICATION.md).

## Conformance Target

EverAgent targets an **AAMP-inspired local control-plane profile**:

| AAMP surface | EverAgent support |
| --- | --- |
| Core lifecycle intents | Mapped to `.project-task-state` and `events/` |
| Required message fields | Stored in event `aamp` envelopes |
| Discovery document | Static local profile in `docs/aamp.discovery.json` |
| Streaming observation | Projected from `events/` and dashboard APIs |
| Mailbox/JMAP/SMTP runtime | Out of scope |
| SDK helper actions | Out of scope |

## Lifecycle Mapping

| AAMP intent | EverAgent action | Local state/event |
| --- | --- | --- |
| `task.dispatch` | Task is added to a project state file | `status: open` |
| `task.ack` | Agent claims a task | `status: claimed`, `task_claimed` |
| `task.stream.opened` | Agent starts executable work | `status: in_progress`, `task_started` |
| `task.help_needed` | Agent is blocked on human input, approval, or policy | `status: help_needed`, `task_help_needed` |
| `task.result` + `completed` | Task completed successfully | `status: done`, `task_done` |
| `task.result` + `rejected` | Task failed or could not be honorably completed | `status: failed`, `task_failed` |
| `task.cancel` | User or dispatcher withdraws the task | `status: cancelled`, `task_cancelled` |
| local expiry projection | Task `expires_at` elapsed before terminal completion | `status: expired`, `task_expired` |

`abandoned` and `expired` remain EverAgent local projections. They are not additional core AAMP wire intents; `task_expired` is emitted as a rejected `task.result` envelope for interoperability.

## Task State Fields

EverAgent task entries may include the following AAMP-aligned optional fields:

```yaml
parent_task_id: T100 | null
expires_at: 2026-04-27T10:00:00+08:00 | null
context_links:
  - ai-learning/AGENTS.md
  - ai-learning/CONTEXT.md
help_reason: "Need approval to use external network" | null
cancelled_at: 2026-04-24T18:00:00+08:00 | null
```

`target` and `value` remain human-facing narrative fields. `context_links` should point to the files or absolute URIs an executor should load before acting.

## Event Envelope

Every event with a `task_id` should carry an AAMP envelope when the intent can be inferred:

```yaml
aamp: {"version":"1.1","intent":"task.ack","task_id":"T043","message_id":"<evt_20260424_...@everagent.local>","dispatch_context":{"project":"ai-learning","actor":"NeuronAgent"}}
```

The envelope is intentionally compact so older event readers can ignore it. Unknown AAMP extensions should be preserved where possible and ignored when unsupported.

## Processing Rules

1. `task_exec.py begin` is the preferred local equivalent of receiving and acknowledging `task.dispatch`.
2. `task_exec.py help` should be used when work cannot safely continue without user input.
3. `task_exec.py cancel` should be used when a task is withdrawn before terminal completion.
4. `task_exec.py finish` and `task_exec.py fail` remain terminal result paths.
5. Event consumers should de-duplicate by `message_id` or by `(task_id, intent, actor)` when replaying mixed event sources.
6. `expires_at` is task-local policy. It complements, but does not replace, the global 72h stale-task sweep.

## Future HTTP Profile

If EverAgent later exposes an HTTP control plane, it should serve:

```text
GET /.well-known/aamp
GET /api/aamp/thread?taskId=T043
GET /api/aamp/streams/{streamId}/events
```

Until then, `docs/aamp.discovery.json` is the canonical local discovery document.

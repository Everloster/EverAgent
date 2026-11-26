/** Offline probes against pinned, local source snapshots. Requires Bun; no provider/account calls. */
import { strict as assert } from "node:assert";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const [orcaPath, t3Path, outputPath] = process.argv.slice(2);
if (!orcaPath || !t3Path) throw new Error("Usage: bun probe.ts ORCA_SOURCE T3_SOURCE [RESULT_JSON]");
const pins = { orca: "60eb66f230d445107a32e55eae695d7090087acf", t3code: "2b0f633db3ba23e692750be2f578ecb089d6a852" };
const roots = { orca: resolve(orcaPath), t3code: resolve(t3Path) };
for (const name of Object.keys(roots) as Array<keyof typeof roots>) {
  const head = execFileSync("git", ["-C", roots[name], "rev-parse", "HEAD"], { encoding: "utf8" }).trim();
  assert.equal(head, pins[name], `${name}: checkout must match the source pin`);
}
const files: Record<string, string> = {};
function source(repo: keyof typeof roots, file: string) {
  const committed = execFileSync("git", ["-C", roots[repo], "show", `${pins[repo]}:${file}`], { encoding: "utf8", maxBuffer: 8 * 1024 * 1024 });
  const disk = readFileSync(resolve(roots[repo], file), "utf8");
  assert.equal(disk, committed, `${file}: source must be unmodified`);
  files[`${repo}/${file}`] = createHash("sha256").update(committed).digest("hex");
  return committed;
}
function between(text: string, from: string, to?: string) {
  const start = text.indexOf(from);
  assert.ok(start >= 0, `missing source marker: ${from}`);
  const end = to === undefined ? text.length : text.indexOf(to, start + from.length);
  assert.ok(end > start, `missing end marker: ${to}`);
  return text.slice(start, end);
}
function compile(text: string, names: string[]) {
  const js = new Bun.Transpiler({ loader: "ts" }).transformSync(text).replace(/^export\s+/gm, "");
  assert.ok(!/^import\s/m.test(js), "extracted kernel must have no unresolved imports");
  return new Function("Buffer", `${js}\nreturn {${names.join(",")}};`)(Buffer);
}
const array = source("t3code", "packages/shared/src/Array.ts");
const model = source("t3code", "packages/shared/src/model.ts");
const policy = source("t3code", "apps/server/src/orchestration-v2/ProviderSessionTransitionPolicy.ts");
const selection = source("t3code", "packages/provider-core/src/server/selectionTransition.ts");
const transition = compile(array + between(model, "function canonicalModelSelectionOptions", "/**\n * Whether a composer's") + between(policy, "export function decideProviderSessionTransition"), ["decideProviderSessionTransition"]);
const selectionKernel = compile(between(selection, "export function turnScopedSelectionTransition"), ["acpSelectionTransition"]);
const contracts = source("t3code", "packages/contracts/src/orchestrationV2.ts");
const budgetSource = source("t3code", "packages/provider-core/src/server/handoffBudget.ts");
const budget = compile(between(contracts, "const LEADING_COMMAND", "export type OrchestrationV2GoalCommand") + between(budgetSource, "export const DEFAULT_HANDOFF_TOKEN_CAP", "export const handoffTokenCapConfig") + between(budgetSource, "export function latestNativeContextUsage"), ["selectHistory", "historicalMessage", "historyCost", "renderHistory", "historyResponseItems", "handoffBudget", "contextUsageForHandoff"]);
const orchestrator = source("t3code", "apps/server/src/orchestration-v2/Orchestrator.ts");
const delivered = compile(between(contracts, "export function isDeliveredProviderTurn", "/** Codex goals") + between(orchestrator, "function isHandoffSourceRun", "type DyingNativeSubagent"), ["lastDeliveredRunForProviderThread"]);
const dagSource = source("orca", "src/main/runtime/orchestration/coordinator/coordinator-dag-convergence.ts");
const dag = compile(between(dagSource, "export function evaluateDagConvergence"), ["evaluateDagConvergence"]);
const reportSource = source("orca", "src/main/runtime/orchestration/workers/reports/worker-report-admission.ts");
const reporting = compile(between(reportSource, "export function workerReportRefusal", "export function assertWorkerCanReport"), ["workerReportRefusal"]);
const queueFile = "src/main/claude/sdk-transport/claude-agent-sdk-user-message-queue.ts";
source("orca", queueFile);
const queueModule = await import(pathToFileURL(resolve(roots.orca, queueFile)).href);

const cases: Array<{ name: string; status: string; observed?: unknown }> = [];
async function check(name: string, run: () => unknown | Promise<unknown>) {
  const observed = await run();
  cases.push({ name, status: "passed", ...(observed === undefined ? {} : { observed }) });
}
const state = (instanceId = "account-a", driver = "codex", continuationKey = "home-a", model = "model-a") => ({ driver, continuationIdentity: { driverKind: driver, continuationKey }, modelSelection: { instanceId, model }, runtimeMode: "supervised", interactionMode: "default", workspace: "/example/search-project" });
for (const [name, current, target, selectionTransition, expected] of [
  ["unchanged selection reuses session", state(), state(), undefined, "reuse"],
  ["same instance model change applies next turn", state(), state("account-a", "codex", "home-a", "model-b"), { type: "apply_on_next_turn" }, "switch_model_in_session"],
  ["adapter can require restart for model change", state(), state("account-a", "codex", "home-a", "model-b"), { type: "restart_session" }, "restart_and_resume"],
  ["cross harness creates session with handoff", state(), state("account-b", "claudeAgent", "home-b"), undefined, "create_with_handoff"],
  ["different instance with compatible continuation resumes", state(), state("account-b"), undefined, "restart_and_resume"],
  ["same driver different continuation requires handoff", state(), state("account-b", "codex", "home-b"), undefined, "create_with_handoff"],
  ["permission change restarts and resumes", state(), { ...state(), runtimeMode: "full" }, undefined, "restart_and_resume"],
  ["unclassified model change is rejected", state(), state("account-a", "codex", "home-a", "model-b"), undefined, "reject"],
  ["unavailable provider is rejected", state(), { ...state(), available: false }, undefined, "reject"],
] as const) await check(name, () => {
  const result = transition.decideProviderSessionTransition({ current, target: { available: true, ...target }, selectionTransition });
  assert.equal(result.type, expected); return result;
});
await check("ACP model change requires advertised capability", () => {
  const result = selectionKernel.acpSelectionTransition({ current: state().modelSelection, target: state("account-a", "codex", "home-a", "model-b").modelSelection, sessionCapabilities: { sessions: { supportsModelSwitchInSession: false } } });
  assert.equal(result.type, "reject"); return result;
});

function item(id: string, type: string, text = "") { return { id, type, threadId: "search-thread", runId: "run-1", providerThreadId: "native-binding-a", status: "completed", createdBy: "user", creationSource: "composer", text, input: "python -m unittest", output: "OK", exitCode: 0 }; }
const historyItems = [item("original", "user_message", "Search must match without case sensitivity; preserve original output order."), item("answer-1", "assistant_message", "I will add a search function."), item("thinking", "reasoning", "not portable"), item("command", "command_execution"), item("latest-user", "user_message", "Also allow Chinese search terms."), item("latest-answer", "assistant_message", "Both constraints are now implemented.")];
const messages = historyItems.flatMap(value => { const m = budget.historicalMessage(value); return m ? [m] : []; });
await check("history conversion excludes reasoning and keeps command evidence", () => {
  assert.equal(messages.length, 5); assert.ok(messages.some((m: any) => m.kind === "command_execution")); assert.ok(!messages.some((m: any) => m.itemId === "thinking")); return messages.map((m: any) => m.itemId);
});
await check("short history remains intact and chronological", () => {
  const result = budget.selectHistory({ messages, coverage: "Self-authored search scenario", budget: 16_000 });
  assert.equal(result.omittedItems, 0); assert.deepEqual(result.messages.map((m: any) => m.itemId), messages.map((m: any) => m.itemId)); return { selected: result.messages.length, omitted: result.omittedItems };
});
await check("large middle item is omitted intact rather than clipped", () => {
  const bulky = budget.historicalMessage(item("large-middle", "assistant_message", "长".repeat(6000)));
  const result = budget.selectHistory({ messages: [messages[0], bulky, ...messages.slice(1)], coverage: "Budgeted search history", budget: 3500 });
  assert.ok(result.omittedItemIds.includes("large-middle")); assert.ok(result.messages.some((m: any) => m.itemId === "original")); assert.ok(result.messages.some((m: any) => m.itemId === "latest-user")); assert.ok(budget.historyCost(result.messages, result.context) <= 3500); return { selectedIds: result.messages.map((m: any) => m.itemId), omittedIds: result.omittedItemIds };
});
await check("oversized original constraint can be omitted", () => {
  const original = { ...messages[0], text: "critical constraint ".repeat(4000) };
  const result = budget.selectHistory({ messages: [original, ...messages.slice(1)], coverage: "Long original prompt", budget: 3500 });
  assert.ok(result.omittedItemIds.includes("original")); return { omittedIds: result.omittedItemIds };
});
await check("history injection preserves attributed roles without native tool blocks", () => {
  const result = budget.historyResponseItems(messages, "Historical context");
  assert.equal(result[0].role, "user"); assert.ok(result.every((entry: any) => entry.type === "message")); return result.map((entry: any) => ({ role: entry.role, contentType: entry.content[0].type }));
});
await check("new model window retains occupancy but updates capacity", () => {
  const result = budget.contextUsageForHandoff({ sameNativeThread: true, sameSelection: false, reuseTelemetry: false, previousUsage: { usedTokens: 90_000, maxTokens: 128_000 }, knownModelWindow: 32_000 });
  assert.deepEqual(result, { usedTokens: 90_000, maxTokens: 32_000 });
  const remaining = budget.handoffBudget({ tokenCap: 16_000, userText: "Continue", attachments: [], providerThread: { contextUsage: result }, nativeContextEstimate: 0 });
  assert.equal(remaining, 0); return { usage: result, remaining };
});
await check("native identity change discards old context occupancy", () => {
  assert.equal(budget.contextUsageForHandoff({ sameNativeThread: false, sameSelection: true, reuseTelemetry: true, previousUsage: { usedTokens: 5000, maxTokens: 128_000 } }), null);
});
const relayRuns = [
  { id: "a1", ordinal: 1, status: "completed", providerThreadId: "a", activeAttemptId: "a1-attempt" },
  { id: "b2", ordinal: 2, status: "completed", providerThreadId: "b", activeAttemptId: "b2-attempt" },
  { id: "a3", ordinal: 3, status: "failed", providerThreadId: "a", activeAttemptId: "a3-attempt" },
];
await check("returning provider anchors delta at last delivered run", () => {
  const last = delivered.lastDeliveredRunForProviderThread({ runs: relayRuns, providerTurns: [{ runAttemptId: "a3-attempt", promptDropped: true }] }, "a");
  assert.equal(last.id, "a1"); return { lastDeliveredOrdinal: last.ordinal, missingPeerRun: "b2" };
});
await check("failed run can still count as delivered when prompt was consumed", () => {
  const last = delivered.lastDeliveredRunForProviderThread({ runs: relayRuns, providerTurns: [{ runAttemptId: "a3-attempt", promptDropped: false }] }, "a");
  assert.equal(last.id, "a3"); return { lastDeliveredOrdinal: last.ordinal };
});
for (const [statuses, expected] of [[[], "empty"], [["completed", "failed"], "all-done"], [["blocked"], "active"], [["dispatched", "blocked"], "active"]] as const) await check(`Orca DAG ${statuses.join("+") || "empty"}`, () => {
  const logs: string[] = []; const result = dag.evaluateDagConvergence({ listTasks: () => statuses.map(status => ({ status })) }, (s: string) => logs.push(s));
  assert.equal(result, expected); if (statuses.length === 1 && statuses[0] === "blocked") assert.equal(logs.length, 1); return { result, logs };
});
for (const [workerState, processCurrent, expected] of [["ready", true, null], ["start_unknown", true, null], ["stopping", true, "dispatch_inactive"], ["ready", false, "worker_identity_changed"]] as const) await check(`worker report ${workerState} current=${processCurrent}`, () => {
  const result = reporting.workerReportRefusal({ dispatchId: "dispatch-current", from: "worker", workerState, processCurrent }); assert.equal(result?.code ?? null, expected); return result;
});
await check("Claude queue yield is earlier than write acknowledgement", async () => {
  const q = queueModule.createClaudeUserMessageQueue(); let resolved = false;
  const sent = q.push({ type: "user", message: { role: "user", content: "Add Chinese search" } }).then(() => { resolved = true; });
  const iterator = q.messages[Symbol.asyncIterator](); assert.equal((await iterator.next()).done, false); assert.equal(resolved, false);
  q.end(); assert.equal((await iterator.next()).done, true); await sent; assert.equal(resolved, true); return { pendingAfterYield: true, acknowledgedAfterResume: true };
});
await check("Claude abandoned yielded frame has ambiguous outcome", async () => {
  const q = queueModule.createClaudeUserMessageQueue(); const sent = q.push({ type: "user", message: { role: "user", content: "Continue" } });
  const outcome = sent.then(() => null, (error: Error) => error); const iterator = q.messages[Symbol.asyncIterator](); await iterator.next(); await iterator.return?.();
  const error = await outcome; assert.ok(error); assert.equal(queueModule.claudeUserMessageWasProvablyUnwritten(error), false); return { provablyUnwritten: false };
});
await check("Claude queued but unyielded frame is provably unwritten on failure", async () => {
  const q = queueModule.createClaudeUserMessageQueue(); const outcome = q.push({ type: "user", message: { role: "user", content: "Continue" } }).then(() => null, (error: Error) => error);
  q.fail(new Error("offline disconnect")); const error = await outcome; assert.ok(error); assert.equal(queueModule.claudeUserMessageWasProvablyUnwritten(error), true); return { provablyUnwritten: true };
});

// Recorded frames are inspected in order; this is not a run of the upstream adapter/orchestrator suite.
const recordings = [];
for (const file of ["subagent_continue/codex_transcript.ndjson", "claude_compact_after_peer_turn/claude_transcript.ndjson"]) {
  const text = source("t3code", `apps/server/src/orchestration-v2/testkit/fixtures/${file}`);
  const rows = text.trim().split("\n").map(line => JSON.parse(line));
  const counts: Record<string, number> = {};
  for (const row of rows) { const key = `${row.type}:${row.frame?.method ?? row.frame?.type ?? "metadata"}`; counts[key] = (counts[key] ?? 0) + 1; }
  assert.equal(rows[0].type, "transcript_start"); assert.ok(rows.some(row => row.type === "emit_inbound")); assert.ok(rows.some(row => row.type === "expect_outbound"));
  if (rows[0].provider === "codex") await check("recording replay keeps child completion separate from parent", () => {
    const active = new Set<string>(); let root: string | undefined; let childCompletedWhileRootActive = false;
    for (const row of rows) {
      const frame = row.frame;
      if (row.type !== "emit_inbound" || !frame?.params?.turn) continue;
      const threadId = frame.params.threadId;
      if (frame.method === "turn/started") { root ??= threadId; active.add(threadId); }
      if (frame.method === "turn/completed") {
        active.delete(threadId);
        if (threadId !== root && root !== undefined && active.has(root)) childCompletedWhileRootActive = true;
      }
    }
    assert.equal(childCompletedWhileRootActive, true); assert.equal(active.size, 0);
    return { childCompletedWhileRootActive, allRecordedTurnsSettled: true };
  });
  if (rows[0].provider === "claudeAgent") await check("recording replay groups Claude command lifecycle by command UUID", () => {
    const states = new Map<string, string[]>();
    for (const row of rows) if (row.type === "emit_inbound" && row.frame?.type === "command_lifecycle") {
      const frame = row.frame; const history = states.get(frame.command_uuid) ?? []; history.push(frame.state); states.set(frame.command_uuid, history);
    }
    assert.equal(states.size, 2);
    for (const values of states.values()) assert.deepEqual(values, ["queued", "started", "completed"]);
    return { commandCount: states.size, states: [...states.values()] };
  });
  recordings.push({ file, provider: rows[0].provider, protocol: rows[0].protocol, version: rows[0].version, rows: rows.length, provenance: rows[0].metadata?.generatedBy ?? rows[0].metadata?.source, counts });
}
const result = { schema: 1, observedAt: new Date().toISOString(), runtime: { bun: Bun.version, nodeCompatibility: process.version }, scope: "source-kernel and queue probes; recording replay through a teaching observer; no live provider or full orchestrator replay", sources: pins, sourceFileSha256: files, passed: cases.length, cases, recordings };
if (outputPath) writeFileSync(outputPath, JSON.stringify(result, null, 2) + "\n");
console.log(JSON.stringify({ passed: result.passed, recordings: recordings.map(({ file, rows, provenance }) => ({ file, rows, provenance })) }, null, 2));

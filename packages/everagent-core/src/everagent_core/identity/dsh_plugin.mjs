/** DSH 0.2.1-rc.2: bind shell identity to the response that requested the tool.
 * Uses official session/event, shellEnv and tools/result extension points.
 * No credentials or conversation text are persisted; defaults are never proof.
 */
import { mkdtempSync, mkdirSync, writeFileSync, unlinkSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { homedir } from 'node:os';

export const name = 'everagent-identity';
export const inject = ['shellEnv', 'sessions', 'tools'];

export function apply(ctx) {
  const latest = new WeakMap();
  const receipts = new Map();
  let directory;
  const validModel = value => typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9:./_-]{0,127}$/.test(value);
  ctx.on('session/event', (session, event) => {
    if (['turn/start', 'turn/end', 'step/start'].includes(event.type)) latest.delete(session);
    if (event.type !== 'assistant/message') return;
    latest.delete(session);
    const { message, turn, step } = event.data;
    const source = message.source;
    const response = source?.replayState?.response;
    if (event.data.interrupted || source?.kind !== 'model' || response?.kind !== 'pi-ai'
        || response.version !== 2 || response.model !== source.model
        || !validModel(response.responseModel) || !validModel(source.model)) return;
    latest.set(session, {
      turn, step, model: response.responseModel, requested_model: source.model,
      observed_at: event.time / 1000,
      calls: new Set(message.content.filter(block => block.type === 'tool-call').map(block => block.id)),
    });
  });

  const remove = token => {
    const path = receipts.get(token);
    if (!path) return;
    try { unlinkSync(path); } catch (error) { if (error.code !== 'ENOENT') throw error; }
    receipts.delete(token);
  };
  ctx.shellEnv.register({
    name,
    variables: {
      DSH_RUNTIME_PID: { description: 'Current DSH process, checked against caller ancestry.' },
      DSH_IDENTITY_RECEIPT: { description: 'Active tool response metadata; removed when execution finishes.' },
    },
    resolve(execution) {
      const env = { DSH_RUNTIME_PID: String(process.pid) };
      const session = execution.agent?.session;
      const found = session && latest.get(session);
      const call = execution.rootCallId ?? execution.callId;
      if (!found?.calls.has(call) || execution.signal.aborted) return env;
      const root = process.env.DSH_HOME || join(homedir(), '.dsh');
      if (!directory) {
        const base = join(root, 'runtime', 'everagent-identity');
        mkdirSync(base, { recursive: true, mode: 0o700 });
        directory = mkdtempSync(join(base, `${process.pid}-`));
      }
      remove(execution.token);
      const path = join(directory, randomUUID() + '.json');
      const { calls, ...metadata } = found;
      writeFileSync(path, JSON.stringify({ schema_version: 1, pid: process.pid,
        session: session.header.id, call, ...metadata, observed_at: Date.now() / 1000 }), { mode: 0o600, flag: 'wx' });
      receipts.set(execution.token, path);
      return { ...env, DSH_IDENTITY_RECEIPT: path };
    },
  });
  ctx.on('tools/result', execution => remove(execution.token));
  ctx.on('dispose', () => {
    if (directory) rmSync(directory, { recursive: true, force: true });
  });
}

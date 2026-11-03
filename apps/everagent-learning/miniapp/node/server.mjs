// @ts-check
// Shared MiniMax Code runtime and local Web server. No host SDK is needed.
import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, realpathSync, statSync, writeFileSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { homedir } from 'node:os';
import { dirname, isAbsolute, join, resolve } from 'node:path';

const JSON_HEADERS = { 'content-type': 'application/json; charset=utf-8' };
const INDEX_TTL_MS = 60_000;
const MAX_OUTPUT_BYTES = 16 * 1024 * 1024;
const LOOPBACK = new Set(['127.0.0.1', 'localhost', '::1']);

function expandPath(value) {
  return value === '~' ? homedir() : value.startsWith('~/') ? join(homedir(), value.slice(2)) : resolve(value);
}

function inspectCandidate(value) {
  if (typeof value !== 'string' || !value.trim()) return { ok: false, reason: 'missing' };
  try {
    const root = realpathSync(expandPath(value.trim()));
    // Check the public checkout's shape, not its remote. Forks and ZIPs work too.
    for (const name of ['scripts/report_catalog.py', 'config/report-quality-policy.json', 'docs/REPORT_INDEX.md']) {
      const file = join(root, name);
      if (!statSync(file).isFile() || realpathSync(file) !== file) return { ok: false, reason: 'no_catalog' };
    }
    return { ok: true, root };
  } catch {
    return { ok: false, reason: 'no_catalog' };
  }
}

function configPath(context, options) {
  if (options.configFile) return options.configFile;
  if (context.dataDir) return join(context.dataDir, 'config.json');
  return join(process.env.XDG_CONFIG_HOME || join(homedir(), '.config'), 'everagent-learning', 'config.json');
}

function readConfig(file) {
  try { return JSON.parse(readFileSync(file, 'utf8')).public_repo_root || ''; }
  catch { return ''; }
}

function resolveRepoRoot(context, options, configFile) {
  const explicit = options.repoRoot || process.env.EVERAGENT_PUBLIC_ROOT;
  if (explicit) return inspectCandidate(explicit).root || '';
  // Only inspect ancestors of this package, never the user's other projects.
  let cursor = realpathSync(context.pluginRoot);
  for (let i = 0; i < 6; i += 1) {
    const found = inspectCandidate(cursor);
    if (found.ok) return found.root;
    const parent = dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  return inspectCandidate(readConfig(configFile)).root || '';
}

function safeRelativePath(value, markdown = true) {
  if (!value || isAbsolute(value) || value.includes('\\') || value.includes('\0')) return null;
  if (value.split('/').some((part) => !part || part === '..' || part === '.' || part.startsWith('.'))) return null;
  if (markdown && !/\.md$/.test(value)) return null;
  return value;
}

async function readBody(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > 8192) throw new Error('body_too_large');
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8');
}

/** start(context) is the MiniMax Code process lifecycle contract. */
export async function start(context, options = {}) {
  if (!LOOPBACK.has(context.listen.host) && !(options.container && context.listen.host === '0.0.0.0')) {
    throw new Error('只允许本机回环地址；容器须显式启用 --container');
  }
  if (options.container && !options.repoRoot) throw new Error('容器模式须指定只读公开仓 --repo');
  const script = join(context.pluginRoot, 'miniapp/node/report_index.py');
  const setupToken = randomBytes(24).toString('hex');
  const clientEntry = (await readFile(join(context.pluginRoot, 'miniapp/client/index.html'), 'utf8'))
    .replace('__SETUP_TOKEN__', setupToken);
  const configFile = configPath(context, options);
  let repoRoot = resolveRepoRoot(context, options, configFile);
  let cached = null;
  let inflight = null;
  let disposed = false;
  const children = new Set();

  function runCatalog(root, args, timeout = 30_000) {
    if (disposed) return Promise.resolve({ ok: false, error: 'stopped' });
    return new Promise((done) => {
      // Only this fixed adapter is launched; the chosen checkout must be trusted.
      const child = spawn(options.python || process.env.EVERAGENT_PYTHON || (process.platform === 'win32' ? 'python' : 'python3'), [script, root, ...args], {
        cwd: dirname(script), stdio: ['ignore', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONDONTWRITEBYTECODE: '1' },
      });
      children.add(child);
      const chunks = [];
      let size = 0;
      let settled = false;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        done(result);
      };
      const timer = setTimeout(() => {
        child.kill('SIGKILL');
        finish({ ok: false, error: 'catalog_timeout' });
      }, timeout);
      child.stdout.on('data', (chunk) => {
        size += chunk.length;
        if (size > MAX_OUTPUT_BYTES) {
          child.kill('SIGKILL');
          finish({ ok: false, error: 'output_too_large' });
        } else chunks.push(chunk);
      });
      // Drain stderr, but never return local paths or tracebacks to the page.
      child.stderr.resume();
      child.on('error', () => finish({ ok: false, error: 'python_unavailable' }));
      child.on('close', (code) => {
        children.delete(child);
        try {
          const result = JSON.parse(Buffer.concat(chunks).toString('utf8'));
          finish(result && typeof result === 'object' && (code === 0 || !result.ok)
            ? result : { ok: false, error: 'catalog_failed' });
        } catch { finish({ ok: false, error: 'catalog_failed' }); }
      });
    });
  }

  async function loadIndex(force) {
    if (!force && cached && Date.now() - cached.at < INDEX_TTL_MS) return cached.payload;
    if (inflight) return inflight;
    const root = repoRoot;
    const task = runCatalog(root, ['list']).then((payload) => {
      if (repoRoot === root && payload.ok) cached = { at: Date.now(), payload };
      return payload;
    });
    inflight = task;
    try { return await task; }
    finally { if (inflight === task) inflight = null; }
  }

  const server = createServer((request, response) => {
    const send = (status, body, headers = JSON_HEADERS) => {
      response.writeHead(status, {
        'x-content-type-options': 'nosniff', 'referrer-policy': 'no-referrer',
        'cache-control': 'no-store', ...headers,
      });
      response.end(typeof body === 'string' || Buffer.isBuffer(body) ? body : JSON.stringify(body));
    };
    const error = (status, code) => send(status, { ok: false, error: code });
    void (async () => {
      const port = server.address().port;
      const hosts = new Set([`127.0.0.1:${port}`, `localhost:${port}`, `[::1]:${port}`]);
      const host = request.headers.host;
      if (!hosts.has(host)) return error(403, 'invalid_host');
      const origin = request.headers.origin;
      if (origin && origin !== `http://${host}`) return error(403, 'cross_origin');
      if (request.headers['sec-fetch-site'] === 'cross-site') return error(403, 'cross_origin');
      const url = new URL(request.url || '/', `http://${host}`);
      if (request.method === 'GET' && (url.pathname === '/' || url.pathname === '/dashboard')) {
        return send(200, clientEntry, { 'content-type': 'text/html; charset=utf-8' });
      }
      if (request.method === 'POST' && url.pathname === '/api/settings') {
        if (request.headers['x-setup-token'] !== setupToken ||
            request.headers['content-type']?.split(';')[0].trim() !== 'application/json') {
          return error(403, 'invalid_setup_request');
        }
        if (options.repoRoot || process.env.EVERAGENT_PUBLIC_ROOT) return error(409, 'repo_set_at_startup');
        let payload;
        try { payload = JSON.parse(await readBody(request)); }
        catch { return error(400, 'invalid_body'); }
        const inspected = inspectCandidate(payload?.path);
        if (!inspected.ok) return send(400, { ok: false, error: 'invalid_repo_root', reason: inspected.reason });
        mkdirSync(dirname(configFile), { recursive: true });
        writeFileSync(configFile, JSON.stringify({ public_repo_root: inspected.root }) + '\n', { mode: 0o600 });
        repoRoot = inspected.root;
        cached = null;
        inflight = null;
        return send(200, { ok: true });
      }
      if (request.method !== 'GET') return error(405, 'method_not_allowed');
      if (!['/api/reports', '/api/report', '/api/asset'].includes(url.pathname)) return error(404, 'not_found');
      if (!repoRoot) return error(503, 'repo_not_configured');
      if (url.pathname === '/api/reports') {
        const payload = await loadIndex(url.searchParams.get('refresh') === '1');
        return send(payload.ok ? 200 : 502, payload);
      }
      const target = safeRelativePath(url.searchParams.get('path'), url.pathname !== '/api/asset');
      if (!target) return error(400, 'invalid_path');
      if (url.pathname === '/api/asset') {
        const result = await runCatalog(repoRoot, ['asset', target], 15_000);
        if (!result.ok) return error(404, result.error || 'not_found');
        return send(200, Buffer.from(result.data, 'base64'), { 'content-type': result.mime });
      }
      const payload = await runCatalog(repoRoot, ['detail', target], 15_000);
      return send(payload.ok ? 200 : 404, payload);
    })().catch(() => { if (!response.headersSent) error(500, 'request_failed'); else response.end(); });
  });
  server.requestTimeout = 15_000;
  server.headersTimeout = 10_000;
  await new Promise((done, fail) => {
    server.once('error', fail);
    server.listen(context.listen.port, context.listen.host, () => {
      server.off('error', fail);
      done();
    });
  });
  const address = server.address();
  const url = `http://${context.listen.host === '::1' ? '[::1]' : context.listen.host}:${address.port}/dashboard`;
  context.logger.info('learning.runtime.listening');

  let closing;
  const dispose = () => {
    if (closing) return closing;
    disposed = true;
    context.signal.removeEventListener('abort', onAbort);
    for (const child of children) child.kill('SIGKILL');
    closing = new Promise((done, fail) => {
      server.close((err) => err ? fail(err) : done());
      server.closeAllConnections();
    });
    return closing;
  };
  const onAbort = () => { void dispose(); };
  context.signal.addEventListener('abort', onAbort, { once: true });
  if (context.signal.aborted) await dispose();
  return { dispose, url };
}

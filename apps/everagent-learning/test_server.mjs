import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { cpSync, copyFileSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { request } from 'node:http';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { start } from './miniapp/node/server.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const PUBLIC_ROOT = join(HERE, '../..');
// Keep an inherited personal checkout selection out of synthetic fixtures.
delete process.env.EVERAGENT_PUBLIC_ROOT;
function fixture(t) {
  const temp = mkdtempSync(join(tmpdir(), 'ea-workbench-'));
  t.after(() => rmSync(temp, { recursive: true, force: true }));
  const repo = join(temp, 'a renamed fork');
  const pluginRoot = join(temp, 'installed', 'everagent-learning');
  const configFile = join(temp, 'settings', 'config.json');
  const put = (path, value) => {
    const target = join(repo, path);
    mkdirSync(dirname(target), { recursive: true });
    writeFileSync(target, value);
  };
  put('scripts/report_catalog.py', readFileSync(join(PUBLIC_ROOT, 'scripts/report_catalog.py')));
  put('config/report-quality-policy.json', '{}');
  put('docs/REPORT_INDEX.md', '# 报告目录');
  put('ai-learning/reports/2026-11-01_demo.md', '---\ntitle: 测试报告\nupdated_on: 2026-11-01\nsource_url: javascript:alert(1)\n---\n# 示例\n\n<script>alert(1)</script>\n\n[危险](java\tscript:alert)\n');
  put('podcast-learning/PODCAST_UPDATES.md', '# 播客\n\n<details>\n<summary>节目</summary>\n\n[报告](../ai-learning/reports/2026-11-01_demo.md#示例)\n\n[编码锚点](../ai-learning/reports/2026-11-01_demo.md#%E7%A4%BA%E4%BE%8B)\n\n</details>');
  put('web-surfing/TECH_BLOG_UPDATES.md', '# 博客');
  // Synthetic userinfo checks that a credential-bearing remote never reaches the API.
  const fixtureRemote = new URL('https://example.invalid/private.git');
  fixtureRemote.username = 'PRIVATE_SENTINEL';
  put('.git/config', '[remote "origin"]\nurl=' + fixtureRemote.href);
  put('podcast-learning/reports/transcripts/private.md', 'PRIVATE_TRANSCRIPT');
  cpSync(join(HERE, 'miniapp'), join(pluginRoot, 'miniapp'), {
    recursive: true, filter: (source) => !source.includes('__pycache__'),
  });
  return { temp, repo, pluginRoot, configFile, put };
}
async function boot(f, options = {}) {
  const controller = new AbortController();
  const app = await start({
    pluginRoot: f.pluginRoot, dataDir: join(f.temp, 'data'),
    listen: { host: '127.0.0.1', port: 0 }, signal: controller.signal,
    logger: { info() {} },
  }, { configFile: f.configFile, ...options });
  return { ...app, controller, base: new URL(app.url).origin };
}
async function get(app, route) {
  const response = await fetch(app.base + route);
  return { status: response.status, body: await response.json() };
}
async function setup(app, path, headers = {}) {
  const page = await (await fetch(app.url)).text();
  const token = page.match(/'x-setup-token': '([a-f0-9]+)'/)[1];
  return fetch(app.base + '/api/settings', {
    method: 'POST', headers: { 'content-type': 'application/json', 'x-setup-token': token, ...headers },
    body: JSON.stringify({ path }),
  });
}

test('installed Mini App: explicit setup, restart, and a renamed fork without private remote data', async (t) => {
  const f = fixture(t);
  let app = await boot(f);
  try {
    assert.equal((await get(app, '/api/reports')).status, 503);
    assert.equal((await setup(app, f.repo)).status, 200);
    let result = await get(app, '/api/reports');
    assert.equal(result.body.total, 1);
    assert.equal(result.body.pins.length, 2);
    assert.equal(result.body.reports[0].source_url, '');
    assert.ok(!JSON.stringify(result.body).includes(f.temp));
    assert.ok(!JSON.stringify(result.body).includes('PRIVATE_'));
    await app.dispose();
    app = await boot(f);
    assert.equal((await get(app, '/api/reports')).body.total, 1);
    assert.equal(JSON.parse(readFileSync(f.configFile, 'utf8')).public_repo_root, realpathSync(f.repo));
  } finally { await app.dispose(); }
});

test('HTTP origin and settings protection; arbitrary files and transcripts stay unreadable', async (t) => {
  const f = fixture(t);
  const app = await boot(f);
  try {
    assert.equal((await setup(app, f.repo, { origin: 'https://example.invalid' })).status, 403);
    assert.equal((await setup(app, f.repo, { 'x-setup-token': 'wrong' })).status, 403);
    const hostStatus = await new Promise((done, fail) => {
      const req = request(app.base + '/api/reports', { headers: { host: 'evil.invalid' } }, (res) => {
        res.resume(); done(res.statusCode);
      });
      req.on('error', fail); req.end();
    });
    assert.equal(hostStatus, 403);
    assert.equal((await setup(app, f.repo)).status, 200);
    for (const path of ['../secret.md', '.git/config', '/etc/passwd', 'podcast-learning/reports/transcripts/private.md']) {
      const result = await get(app, '/api/report?path=' + encodeURIComponent(path));
      assert.ok(result.status >= 400);
      assert.ok(!JSON.stringify(result).includes('PRIVATE_TRANSCRIPT'));
    }
    const detail = (await get(app, '/api/report?path=ai-learning/reports/2026-11-01_demo.md')).body.report;
    assert.ok(!detail.html.includes('<script>'));
    assert.ok(!detail.html.includes('href="java'));
    const pin = (await get(app, '/api/report?path=podcast-learning/PODCAST_UPDATES.md')).body.report;
    assert.ok(pin.html.includes('<details>'));
    const link = pin.html.match(/href="(dashboard\?report=[^"]+)"/)[1];
    assert.equal(new URL(link, 'http://localhost/learning/dashboard').pathname, '/learning/dashboard');
    assert.equal(pin.html.split('#%E7%A4%BA%E4%BE%8B').length - 1, 2);
  } finally { await app.dispose(); }
});

test('complete long reports, refresh, local images, and symlink escape rejection', async (t) => {
  const f = fixture(t);
  const longPath = 'ai-learning/reports/2026-11-02_long.md';
  const content = '# 长报告\n\n' + '内容足够长。'.repeat(15000) + '\n\nEND_OF_REPORT';
  f.put(longPath, content);
  const secret = join(f.temp, 'private.md');
  writeFileSync(secret, '# PRIVATE_REPORT');
  symlinkSync(secret, join(f.repo, 'ai-learning/reports/escape.md'));
  mkdirSync(join(f.repo, 'docs/assets'), { recursive: true });
  copyFileSync(join(HERE, 'icon.png'), join(f.repo, 'docs/assets/sample.png'));
  const app = await boot(f, { repoRoot: f.repo });
  try {
    assert.equal((await get(app, '/api/reports')).body.total, 2);
    const report = (await get(app, '/api/report?path=' + encodeURIComponent(longPath))).body.report;
    assert.equal(report.bytes, Buffer.byteLength(content));
    assert.equal(report.truncated, false);
    assert.ok(report.markdown.endsWith('END_OF_REPORT'));
    assert.ok(report.html.includes('END_OF_REPORT'));
    assert.equal((await get(app, '/api/report?path=ai-learning/reports/escape.md')).status, 404);
    const asset = await fetch(app.base + '/api/asset?path=docs/assets/sample.png');
    assert.equal(asset.status, 200);
    assert.equal(asset.headers.get('content-type'), 'image/png');
    assert.equal((await get(app, '/api/asset?path=scripts/report_catalog.py')).status, 404);
    f.put('ai-learning/reports/new.md', '# 新报告');
    assert.equal((await get(app, '/api/reports?refresh=1')).body.total, 3);
    f.put(longPath, 'x'.repeat(2 * 1024 * 1024 + 1));
    assert.equal((await get(app, '/api/report?path=' + encodeURIComponent(longPath))).body.error, 'report_too_large');
  } finally { await app.dispose(); }
});

test('standalone launcher runs from an unrelated cwd and shuts down on SIGTERM', async (t) => {
  const f = fixture(t);
  const child = spawn(process.execPath, [join(HERE, 'start.mjs'), '--port', '0', '--repo', f.repo], {
    cwd: f.temp, stdio: ['ignore', 'pipe', 'pipe'],
  });
  t.after(() => { if (child.exitCode === null) child.kill('SIGKILL'); });
  const text = await new Promise((done, fail) => {
    const timer = setTimeout(() => fail(new Error('startup timeout')), 5000);
    child.once('error', fail);
    child.stdout.once('data', (data) => { clearTimeout(timer); done(data.toString()); });
  });
  const url = text.match(/http:\/\/127\.0\.0\.1:\d+\/dashboard/)[0];
  assert.equal((await fetch(url)).status, 200);
  assert.equal((await (await fetch(new URL('/api/reports', url))).json()).total, 1);
  const exited = once(child, 'exit');
  child.kill('SIGTERM');
  const [code] = await exited;
  assert.equal(code, 0);
});

test('native lifecycle abort releases the listener; public binds are rejected', async (t) => {
  const f = fixture(t);
  const app = await boot(f, { repoRoot: f.repo });
  app.controller.abort();
  await app.dispose();
  await assert.rejects(fetch(app.url));
  await assert.rejects(start({ listen: { host: '0.0.0.0', port: 0 } }), /回环/);
  await assert.rejects(start({ listen: { host: '0.0.0.0', port: 0 } }, { container: true }), /--repo/);
});

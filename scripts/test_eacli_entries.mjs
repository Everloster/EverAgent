// Isolated thin-entry contracts: fake eacli records argv/version only; no real Git.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const source = path.dirname(fileURLToPath(import.meta.url));
const entries = ['eacli-entry.sh', 'egit.sh', 'ecommit.sh', 'edocs.sh'];

function fixture(t) {
  const prefix = path.join(fs.realpathSync(os.tmpdir()), 'everagent-thin-entry-');
  const root = fs.mkdtempSync(prefix);
  t.after(() => {
    // Verify the exact absolute, generated target before deleting test artifacts.
    assert.equal(fs.realpathSync(root), root);
    assert.ok(root.startsWith(prefix) && root.length > prefix.length);
    fs.rmSync(root, { recursive: true });
  });
  const repo = path.join(root, 'public checkout');
  const scripts = path.join(repo, 'scripts');
  const cwd = path.join(repo, 'nested', 'directory');
  const home = path.join(root, 'home');
  const bin = path.join(root, 'path-bin');
  const log = path.join(root, 'calls.jsonl');
  fs.mkdirSync(scripts, { recursive: true });
  fs.mkdirSync(cwd, { recursive: true });
  fs.mkdirSync(home, { recursive: true });
  fs.mkdirSync(bin);
  for (const entry of entries) {
    fs.copyFileSync(path.join(source, entry), path.join(scripts, entry));
    fs.chmodSync(path.join(scripts, entry), 0o755);
  }
  fs.symlinkSync('/bin/bash', path.join(bin, 'bash'));
  fs.symlinkSync('/usr/bin/dirname', path.join(bin, 'dirname'));
  // Even an accidental fallback only hits these recording sentinels, never Git/Go.
  for (const name of ['git', 'go']) {
    fs.writeFileSync(path.join(bin, name), `#!${process.execPath}\nrequire('node:fs').appendFileSync(process.env.FAKE_LOG, JSON.stringify({forbidden: ${JSON.stringify(name)}}) + '\\n'); process.exit(90);\n`, { mode: 0o755 });
  }
  const fake = (filename) => {
    fs.mkdirSync(path.dirname(filename), { recursive: true });
    fs.writeFileSync(filename, `#!${process.execPath}\nconst fs = require('node:fs');\nconst argv = process.argv.slice(2);\nfs.appendFileSync(process.env.FAKE_LOG, JSON.stringify({executable: process.argv[1], argv}) + '\\n');\nif (argv.length === 1 && argv[0] === '--version') { process.stdout.write(process.env.FAKE_VERSION ?? '10.1.0\\n'); process.exit(Number(process.env.FAKE_VERSION_EXIT ?? 0)); }\nprocess.exit(Number(process.env.FAKE_EXIT ?? 0));\n`, { mode: 0o755 });
    return filename;
  };
  const explicit = fake(path.join(root, 'explicit tools', 'eacli'));
  const env = { ...process.env, HOME: home, PATH: bin, FAKE_LOG: log };
  for (const key of ['EACLI_BIN', 'FAKE_VERSION', 'FAKE_VERSION_EXIT', 'FAKE_EXIT']) delete env[key];
  const run = (entry, args, overrides = {}, options = {}) => spawnSync('/bin/bash', [path.join(scripts, entry), ...args], { cwd, env: { ...env, EACLI_BIN: explicit, ...overrides }, encoding: 'utf8', ...options });
  const calls = () => fs.existsSync(log) ? fs.readFileSync(log, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse) : [];
  return { root, repo, scripts, cwd, home, bin, explicit, env, fake, run, calls };
}

for (const action of ['identity', 'commit', 'merge', 'push', 'hooks']) {
  test(`git ${action}: canonical root and untouched arguments from subdirectory`, (t) => {
    const f = fixture(t);
    const args = ['--json', 'value with spaces', '', '--repo-root-looking-value'];
    const result = f.run('egit.sh', [action, ...args]);
    assert.equal(result.status, 0, result.stderr);
    assert.deepEqual(f.calls(), [
      { executable: f.explicit, argv: ['--version'] },
      { executable: f.explicit, argv: ['git', action, '--repo-root', f.repo, ...args] },
    ]);
  });
}

test('validate maps to identity validate; ecommit preserves -m/-F values and trailers', (t) => {
  const f = fixture(t);
  assert.equal(f.run('egit.sh', ['validate', '--json']).status, 0);
  const args = ['-m', '--repo-root', '-m', '中文说明\n\nCo-authored-by: Example <example@example.org>', '-F', '--repo-root', '--trailer', 'Reviewed-by=Example', '--', 'file with spaces'];
  assert.equal(f.run('ecommit.sh', args).status, 0);
  assert.deepEqual(f.calls().map((c) => c.argv), [
    ['--version'], ['git', 'identity', '--repo-root', f.repo, 'validate', '--json'],
    ['--version'], ['git', 'commit', '--repo-root', f.repo, ...args],
  ]);
});

test('docs: exact fixed interface and unconsumed arguments', (t) => {
  const f = fixture(t);
  const args = ['--scope', 'worktree', '--report', 'file with spaces', '--', '--repo-root'];
  const result = f.run('edocs.sh', ['disclosure', ...args]);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(f.calls().map((c) => c.argv), [['--version'], ['docs', 'disclosure', '--repo-root', f.repo, ...args]]);
});

test('entry paths through a directory symlink still bind physical canonical root', (t) => {
  const f = fixture(t);
  const alias = path.join(f.root, 'checkout alias');
  fs.symlinkSync(f.repo, alias, 'dir');
  const result = spawnSync('/bin/bash', [path.join(alias, 'scripts', 'ecommit.sh'), '-m', 'example'], { cwd: f.cwd, env: { ...f.env, EACLI_BIN: f.explicit }, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(f.calls()[1].argv[3], f.repo);
});

test('explicit EACLI_BIN wins over HOME and PATH, including a PATH command name', (t) => {
  const f = fixture(t);
  f.fake(path.join(f.home, '.local', 'bin', 'eacli'));
  const pathCLI = f.fake(path.join(f.bin, 'eacli'));
  assert.equal(f.run('egit.sh', ['push']).status, 0);
  assert.equal(f.calls()[0].executable, f.explicit);
  assert.equal(f.run('edocs.sh', ['index'], { EACLI_BIN: 'eacli' }).status, 0);
  assert.equal(f.calls()[2].executable, pathCLI);
});

test('without explicit EACLI_BIN, HOME wins over PATH', (t) => {
  const f = fixture(t);
  const homeCLI = f.fake(path.join(f.home, '.local', 'bin', 'eacli'));
  f.fake(path.join(f.bin, 'eacli'));
  const result = spawnSync('/bin/bash', [path.join(f.scripts, 'egit.sh'), 'hooks', 'status'], { cwd: f.cwd, env: f.env, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(f.calls()[0].executable, homeCLI);
});

test('old HOME installation fails without trying a newer PATH installation', (t) => {
  const f = fixture(t);
  const homeCLI = f.fake(path.join(f.home, '.local', 'bin', 'eacli'));
  f.fake(path.join(f.bin, 'eacli'));
  const result = spawnSync('/bin/bash', [path.join(f.scripts, 'egit.sh'), 'push'], { cwd: f.cwd, env: { ...f.env, FAKE_VERSION: '10.0.9' }, encoding: 'utf8' });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /too old/);
  assert.deepEqual(f.calls(), [{ executable: homeCLI, argv: ['--version'] }]);
});

test('PATH works without HOME; no adjacent private checkout is required', (t) => {
  const f = fixture(t);
  const pathCLI = f.fake(path.join(f.bin, 'eacli'));
  const env = { ...f.env }; delete env.HOME;
  const result = spawnSync('/bin/bash', [path.join(f.scripts, 'edocs.sh'), 'scripts', '--check'], { cwd: f.cwd, env, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(f.calls()[0].executable, pathCLI);
});

for (const version of ['10.1.0\n', '10.2.0', '10.10.0', '11.0.0', '1000000000000000000000.0.0']) {
  test(`valid release ${version.trim()} runs the selected CLI`, (t) => {
    const f = fixture(t);
    const result = f.run('egit.sh', ['commit', '-m', 'example'], { FAKE_VERSION: version });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(f.calls().length, 2);
  });
}

for (const version of ['9.99.99', '10.0.999', '', 'v10.1.0', '10.1', '10.01.0', '10.1.0-rc.1', '10.1.0 extra', '10.1.0\n11.0.0']) {
  test(`old/invalid version ${JSON.stringify(version)} fails before business execution`, (t) => {
    const f = fixture(t);
    f.fake(path.join(f.home, '.local', 'bin', 'eacli'));
    f.fake(path.join(f.bin, 'eacli'));
    const result = f.run('ecommit.sh', ['-m', 'example'], { FAKE_VERSION: version });
    assert.equal(result.status, 2);
    assert.match(result.stderr, /too old|Invalid eacli/);
    assert.deepEqual(f.calls(), [{ executable: f.explicit, argv: ['--version'] }]);
  });
}

test('missing, empty or nonexecutable selection fails without fallback', (t) => {
  const f = fixture(t);
  f.fake(path.join(f.bin, 'eacli'));
  for (const EACLI_BIN of ['', path.join(f.root, 'missing'), f.repo]) {
    const result = f.run('egit.sh', ['push'], { EACLI_BIN });
    assert.equal(result.status, 2);
    assert.match(result.stderr, /empty|not found or not executable/);
  }
  const homeCLI = f.fake(path.join(f.home, '.local', 'bin', 'eacli'));
  fs.chmodSync(homeCLI, 0o644);
  const result = spawnSync('/bin/bash', [path.join(f.scripts, 'egit.sh'), 'push'], { cwd: f.cwd, env: f.env, encoding: 'utf8' });
  assert.equal(result.status, 2);
  assert.deepEqual(f.calls(), []);
});

test('no installed CLI fails clearly and never invokes git/go', (t) => {
  const f = fixture(t);
  const result = spawnSync('/bin/bash', [path.join(f.scripts, 'ecommit.sh'), '-m', 'example'], { cwd: f.cwd, env: f.env, encoding: 'utf8' });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /Installed eacli not found/);
  assert.deepEqual(f.calls(), []);
});

test('version subprocess failure is explicit; business exit codes propagate', (t) => {
  const f = fixture(t);
  const failure = f.run('egit.sh', ['push'], { FAKE_VERSION_EXIT: '17' });
  assert.equal(failure.status, 2);
  assert.match(failure.stderr, /eacli --version failed/);
  for (const [entry, args] of [['egit.sh', ['push']], ['ecommit.sh', ['-m', 'example']], ['edocs.sh', ['index']]]) {
    assert.equal(f.run(entry, args, { FAKE_EXIT: '37' }).status, 37);
  }
  assert.equal(f.calls().filter((c) => c.argv[0] !== '--version').length, 3);
});

test('missing/unknown Git actions and missing docs action do not consume args or run CLI', (t) => {
  const f = fixture(t);
  for (const [entry, args] of [['egit.sh', []], ['egit.sh', ['status']], ['edocs.sh', []]]) {
    assert.equal(f.run(entry, args).status, 2);
  }
  assert.equal(f.run('egit.sh', ['--help']).status, 0);
  assert.equal(f.run('edocs.sh', ['--help']).status, 0);
  assert.deepEqual(f.calls(), []);
});

// Build once for the local Node/Mini App host, or explicitly cross-compile with
// GOOS/GOARCH. The resulting adapter needs neither Go nor Python at runtime.
import { spawn } from 'node:child_process';
import { mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const here = dirname(fileURLToPath(import.meta.url));
const { values } = parseArgs({ options: { output: { type: 'string' } } });
const os = process.env.GOOS || { darwin: 'darwin', linux: 'linux', win32: 'windows' }[process.platform];
const arch = process.env.GOARCH || (process.arch === 'x64' ? 'amd64' : process.arch);
if (!['darwin', 'linux', 'windows'].includes(os) || !['amd64', 'arm64'].includes(arch)) {
  throw new Error('尚未支持这个平台的构建；没有生成制品。');
}
const output = values.output ? resolve(values.output) : join(here, 'miniapp/bin', `${os}-${arch}`, `ea-learning-index${os === 'windows' ? '.exe' : ''}`);
mkdirSync(dirname(output), { recursive: true });
const child = spawn('go', ['-C', join(here, '../../packages/everagent-core'), 'build', '-mod=readonly', '-trimpath', '-buildvcs=false', '-o', output, './cmd/ea-learning-index'], {
  stdio: 'inherit', env: { ...process.env, GOWORK: 'off', CGO_ENABLED: '0', GOOS: os, GOARCH: arch },
});
child.on('error', () => { console.error('需要 Go 1.27+ 才能构建阅读适配器。'); process.exitCode = 1; });
child.on('exit', (code) => { process.exitCode = code ?? 1; if (code === 0) console.log(`已构建 ${os}-${arch} 阅读适配器。`); });

#!/usr/bin/env node
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { start } from './miniapp/node/server.mjs';

try {
  const { values } = parseArgs({ options: {
    port: { type: 'string', default: '4173' },
    repo: { type: 'string' },
    python: { type: 'string', default: process.env.EVERAGENT_PYTHON || (process.platform === 'win32' ? 'python' : 'python3') },
    help: { type: 'boolean', short: 'h' },
  } });
  if (values.help) {
    console.log('用法：node apps/everagent-learning/start.mjs [--port 4173] [--repo /path/to/EverAgent] [--python python3]\n只监听 127.0.0.1；Ctrl+C 停止。');
  } else {
    const port = Number(values.port);
    if (!/^\d+$/.test(values.port) || !Number.isInteger(port) || port < 0 || port > 65535) throw new Error('端口须为 0–65535');
    const controller = new AbortController();
    const app = await start({
      pluginRoot: dirname(fileURLToPath(import.meta.url)),
      listen: { host: '127.0.0.1', port },
      signal: controller.signal,
      logger: { info() {} },
    }, { repoRoot: values.repo, python: values.python });
    const stop = () => { controller.abort(); };
    process.once('SIGINT', stop);
    process.once('SIGTERM', stop);
    console.log(`EverAgent 学习工作台：${app.url}\n按 Ctrl+C 停止。`);
  }
} catch (error) {
  console.error(`启动失败：${error.code === 'EADDRINUSE' ? '端口已占用，请用 --port 换一个端口。' : error.message}`);
  process.exitCode = 1;
}

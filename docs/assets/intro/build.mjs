#!/usr/bin/env node
// 生成 README 介绍动画：逐帧确定性截图 intro.html，合并相同帧，用 libwebp 的 img2webp 编码为循环动画 WebP。
// 最后一帧（回到标题卡）复用第 1 帧的编码数据，使循环接缝逐像素一致。
// 依赖：Node.js 18+、Playwright（含 Chromium）、libwebp 的 img2webp；可选 ffmpeg（--preview 输出 MP4 预览）。
// 字体：macOS 自带的 PingFang SC、Hoefler Text、Avenir Next；其他系统需安装同名字体，否则会回退并改变画面。
// 用法（仓库根目录）：node docs/assets/intro/build.mjs [--out docs/assets/everagent-intro.webp] [--scale 1.5] [--q 80]
//                     [--preview /tmp/intro.mp4] [--stills /tmp/intro-stills]
import { createRequire } from 'node:module';
import { execFileSync, spawnSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));

// 动画 WebP 是 RIFF 容器：VP8X、ANIM 之后是一串 ANMF 帧块。ANMF 负载前 16 字节依次为
// X/2、Y/2、宽-1、高-1、时长（各 3 字节小端）和标志字节（bit1=不混合，bit0=处置为背景）。
function reuseFirstFrameAsLast(file) {
  const buf = fs.readFileSync(file);
  if (buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') throw new Error('不是 WebP 文件');
  const u24 = (b, o) => b[o] | (b[o + 1] << 8) | (b[o + 2] << 16);
  const chunks = [];
  for (let off = 12; off + 8 <= buf.length;) {
    const size = buf.readUInt32LE(off + 4);
    chunks.push({ id: buf.toString('ascii', off, off + 4), start: off, payload: off + 8, size, end: off + 8 + size + (size & 1) });
    off = chunks[chunks.length - 1].end;
  }
  const vp8x = chunks.find(c => c.id === 'VP8X');
  const frames = chunks.filter(c => c.id === 'ANMF');
  if (!vp8x || frames.length < 2) throw new Error('缺少 VP8X 或动画帧');
  const canvasW = u24(buf, vp8x.payload + 4) + 1, canvasH = u24(buf, vp8x.payload + 7) + 1;
  const first = Buffer.from(buf.subarray(frames[0].payload, frames[0].payload + frames[0].size));
  if (u24(first, 0) !== 0 || u24(first, 3) !== 0 || u24(first, 6) + 1 !== canvasW || u24(first, 9) + 1 !== canvasH) {
    throw new Error('首帧不是整幅画布，无法复用');
  }
  const last = frames[frames.length - 1];
  const duration = u24(buf, last.payload + 12);
  first[12] = duration & 255; first[13] = (duration >> 8) & 255; first[14] = (duration >> 16) & 255;
  first[15] = 0x02; // 不混合、不处置：整幅覆盖，解码结果与首帧相同
  const head = Buffer.alloc(8);
  head.write('ANMF', 0, 'ascii');
  head.writeUInt32LE(first.length, 4);
  const body = Buffer.concat([buf.subarray(12, last.start), head, first, Buffer.alloc(first.length & 1), buf.subarray(last.end)]);
  const riff = Buffer.alloc(12);
  riff.write('RIFF', 0, 'ascii');
  riff.writeUInt32LE(body.length + 4, 4);
  riff.write('WEBP', 8, 'ascii');
  fs.writeFileSync(file, Buffer.concat([riff, body]));
}
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : d; };
const out = path.resolve(opt('out', path.join(here, '..', 'everagent-intro.webp')));
const scale = Number(opt('scale', 1.5));
const quality = Number(opt('q', 80));
const preview = opt('preview', null);
const stillsDir = opt('stills', null);

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  try { return require('playwright'); } catch {}
  const globalRoot = execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim();
  return require(path.join(globalRoot, 'playwright'));
}
const { chromium } = loadPlaywright();

const work = fs.mkdtempSync(path.join(os.tmpdir(), 'everagent-intro-'));
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: scale });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto('file://' + path.join(here, 'intro.html'));
  await page.waitForFunction(() => window.READY === true, null, { timeout: 20000 });
  if (errors.length) throw new Error('页面脚本错误：' + errors.join('; '));
  const { duration, fps } = await page.evaluate(() => ({ duration: window.TL.duration, fps: window.TL.fps }));

  if (stillsDir) {
    fs.mkdirSync(stillsDir, { recursive: true });
    for (let k = 0; k <= 17; k++) {
      const t = Math.min((duration * k) / 17, duration - 1 / fps);
      await page.evaluate(x => window.seek(x), t);
      await page.screenshot({ path: path.join(stillsDir, `t${t.toFixed(2).padStart(6, '0')}.png`) });
    }
  }

  const total = Math.round(duration * fps);
  const step = 1000 / fps;
  const frames = [];
  let previous = null;
  let firstDigest = null;
  for (let i = 0; i < total; i++) {
    await page.evaluate(x => window.seek(x), i / fps);
    const png = await page.screenshot();
    const digest = crypto.createHash('sha1').update(png).digest('hex');
    if (i === 0) firstDigest = digest;
    if (digest === previous) { frames[frames.length - 1].ms += step; continue; }
    const file = path.join(work, `f${String(i).padStart(5, '0')}.png`);
    fs.writeFileSync(file, png);
    frames.push({ file, ms: step, digest });
    previous = digest;
  }
  const last = frames[frames.length - 1];
  if (last.digest !== firstDigest) throw new Error('最后一帧没有回到标题卡，循环会跳变');

  // 编码全部不同帧，再把末帧（回到标题卡）替换成第 1 帧的同一份码流，使循环接缝逐像素一致。
  const args = ['-loop', '0', '-min_size', '-lossy', '-q', String(quality), '-m', '6'];
  for (const f of frames) args.push('-d', String(Math.round(f.ms)), f.file);
  args.push('-o', out);
  const argFile = path.join(work, 'img2webp.args');
  fs.writeFileSync(argFile, args.join(' '));
  const r = spawnSync('img2webp', [argFile], { encoding: 'utf8' });
  if (r.status !== 0) throw new Error('img2webp 失败：' + (r.stderr || r.stdout));
  reuseFirstFrameAsLast(out);

  console.log(`webp ${path.relative(process.cwd(), out)}  ${(fs.statSync(out).size / 1048576).toFixed(2)} MiB  ` +
    `${duration}s  ${total} 帧 → ${frames.length} 个不同帧  scale=${scale} q=${quality}`);

  if (preview) {
    const list = path.join(work, 'concat.txt');
    fs.writeFileSync(list, frames.map(f => `file '${f.file}'\nduration ${(f.ms / 1000).toFixed(3)}`).join('\n') +
      `\nfile '${last.file}'\n`);
    const v = spawnSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-fps_mode', 'cfr', '-r', '30',
      '-vf', 'scale=1280:-2:flags=lanczos', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.resolve(preview)],
      { encoding: 'utf8' });
    if (v.status !== 0) throw new Error('ffmpeg 预览失败：' + v.stderr);
    console.log(`preview ${preview}`);
  }
} finally {
  await browser.close();
  fs.rmSync(work, { recursive: true, force: true });
}

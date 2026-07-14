# OpenCut-app/OpenCut 深度研究报告

> 开源的 CapCut（剪映国际版）替代品：浏览器里直接剪视频，素材不出本地。

## 1. 项目概述

OpenCut 是一款 MIT 协议的开源视频编辑器，定位为"剪映/CapCut 的开源替代"——核心卖点是**完全在浏览器本地运行、无水印、无会员、素材不上传服务器**（隐私优先）。它精准踩中了 2026 年"剪映涨价 / 会员劝退"的用户情绪，成为社区级爆款 `[Web]`。

⚠️ **研究者必读的关键结构（否则会严重误判本项目）**：截至 2026-07-14，仓库**默认分支 `main` 并不是那个 6 万星用户在用的编辑器**，而是一次"从零重写（ground-up rewrite）"的**架构骨架**——`main` 上 `apps/web/src/routes/index.tsx` 只有一行 `hello world!`，根路由标题直接写着 `OpenCut rewrite | beta.opencut.app` `[代码]`。真正在生产环境（opencut.app）运行、拥有完整时间轴/蒙版/关键帧/导出能力的**「classic 编辑器」代码，位于 `dev` / `staging` 等分支**，并已被抽出到独立的归档仓库 `OpenCut-app/opencut-classic` `[API][Web]`。本报告的技术分析基于**真正有编辑器代码的 `dev` 分支**，而非空壳 `main`。

## 2. 基本信息

| 项 | 值（GitHub API 精确值，截至 2026-07-14） |
|------|------|
| Stars | 66,956 `[API]` |
| Forks | 7,042 `[API]` |
| 开放 Issues | 333 `[API]` |
| 主语言 | TypeScript（rewrite 分支 `main`）`[API]` |
| 语言占比 | TypeScript 212,955 B / CSS 4,631 B / Rust 1,496 B（仅统计 `main` 骨架）`[API]` |
| 协议 | MIT `[API]` |
| 创建时间 | 2025-06-22 `[API]` |
| 最近推送 | 2026-07-10（`main` 骨架）`[API]` |
| 最新 Release | v0.3.0（2026-04-15，属 classic 编辑器时代）`[API]` |
| 贡献者数 | 96 `[API]` |
| GitHub | https://github.com/OpenCut-app/OpenCut |
| 生产站点 | https://opencut.app （classic）`[Web]` |
| 重写预览 | https://new.opencut.app / beta.opencut.app （rewrite）`[Web][代码]` |
| Topics | editor, oss, videoeditor `[API]` |

## 3. 技术分析

OpenCut 有**两套并存的代码库**，技术栈完全不同，必须分开看：

### 3.1 Classic 编辑器（生产在跑，代码在 `dev`/`staging`）

这是让项目走红的东西。技术栈（读 `dev` 分支 `apps/web/package.json` 得出）`[代码]`：

- **框架**：Next.js 16 + React 19，部署走 `@opennextjs/cloudflare`（Cloudflare Workers）`[代码]`
- **状态管理**：Zustand（`editor-store` / `timeline-store` / `preview-store` / `properties-store` 等多个 store 分治）`[代码]`
- **媒体处理**：`mediabunny`（浏览器端解封装/取帧/音频提取）+ `ffmpeg.wasm`（`apps/web/public/ffmpeg/ffmpeg-core.wasm` 就在仓库里）`[代码]`
- **鉴权/存储**：`better-auth` + `drizzle-orm`（云端账号/项目同步是可选层，编辑本身不依赖它）`[代码]`

**架构亮点（均来自真实源码 `[代码]`）**：

1. **命令模式（Command Pattern）撑起撤销/重做**：`src/lib/commands/` 下有 `base-command.ts` / `batch-command.ts`，并按领域拆成 `media/` `scene/` `timeline/` `project/` 子命令（如 `add-media-asset.ts`、`create-scene.ts`）。每个编辑动作都是一个可逆命令，这是专业编辑器做 undo/redo 的标准做法。
2. **节点式渲染树 + WebGL 合成**：`src/services/renderer/` 是渲染核心——`canvas-renderer.ts` 负责 canvas 绘制，`nodes/` 下有 `video-node` / `text-node` / `image-node` / `sticker-node` / `blur-background-node` / `effect-layer-node` 等，由 `scene-builder.ts` 组装成渲染树，`root-node.ts` 为根；`webgl/jfa.ts`（Jump Flooding Algorithm）用于蒙版羽化等 GPU 特效。这是一套**保留模式（retained-mode）场景图**，而非每帧重画的立即模式。
3. **完整关键帧动画系统**：`src/lib/animation/` 有 `keyframes.ts` / `interpolation.ts` / `number-channel.ts` / `color-channel.ts` / `vector-channel.ts` / `property-registry.ts`——按属性通道（数值/颜色/向量）分别插值，支持图形化关键帧编辑（graph editor，v0.3.0 引入）`[Web]`。
4. **纯本地导出，不经服务器**：`src/lib/export.ts` 的 `downloadBuffer()` 直接 `new Blob()` + `URL.createObjectURL()` 触发浏览器下载 `[代码]`；`RendererManager.saveSnapshot()` 同样是本地 `downloadBlob()` `[代码]`。导出格式为 mp4 / webm，质量 low→very_high 四档 `[代码]`。**这从代码层面坐实了"数据不出本地"的隐私卖点**——导出产物从头到尾没有上传动作。
5. **可迁移的键位系统**：`src/stores/keybindings/migrations/` 有 `v2-to-v3` … `v5-to-v6` 一串迁移脚本 `[代码]`，说明快捷键 schema 已迭代多轮，对存量用户配置做了兼容处理，工程成熟度不低。

### 3.2 Rewrite 骨架（`main` 默认分支，架构设计中）

`main` 是一次雄心勃勃的重写，目标是"一套 Rust 核心驱动 web/桌面/移动"`[Web]`。当前仅是脚手架 `[代码]`：

- **Monorepo**：用 `moon` + `proto` 管理（已从 turbo 迁走），三个 app：`apps/web`（TanStack Start + Vite 8 + React 19）、`apps/api`（Elysia on Cloudflare Workers，目前只有 `/health`、`/echo` 等占位路由）、`apps/desktop`（Rust + GPUI 的桌面壳，共享 core crate 尚未接线）`[代码][Web]`。
- **现状**：`apps/web/src` 里除了 shadcn/ui 组件库和一行 `hello world!` 的首页，**没有任何编辑器逻辑**；依赖里也没有 mediabunny/ffmpeg/时间轴库 `[代码]`。README 的 Editor API、插件架构、MCP server（供 AI agent 驱动编辑器）、headless 批量渲染都还是 **roadmap，未落地** `[Web]`。
- **重写期间外部贡献暂停** `[Web]`。

> 一句话技术判断：**OpenCut 真正的技术实力在 classic 分支的浏览器端渲染/合成管线上（成熟、可用）；main 上的 rewrite 是对未来的下注（Rust 统一核心 + 插件 + AI，尚在骨架阶段）。**

## 4. 社区活跃度

- **贡献者高度集中（巴士因子 = 1）**：头部贡献者 `mazeincoding` 独占 **1,045** 次提交，第二名 `izadoesdev` 仅 71 次，第三名 `anwarulislam` 53 次 `[API]`。虽然贡献者总数 96 人，但绝大多数是零星 PR，项目命脉系于单一核心作者——这是可持续性上的主要风险。
- **代码活动其实已放缓，与 star 暴涨背离**：真正的编辑器分支 `dev` 最后提交停在 **2026-03-29**，`staging` 停在 **2026-04-15**，近 14 天均为 0 提交 `[API]`；只有 rewrite 骨架分支 `main` 在 6-7 月有零星脚手架提交（近 8 周周均 1.375 次 vs 全年周均 12.75 次）`[API]`。**代码热度在降温，社区热度在飙升，两者明显脱节。**
- **Issue/PR**：累计开放 issue 229、已关闭 91（关闭率约 28%，偏低，与重写期维护收缩一致）；累计 PR 483 `[API]`。

## 5. 发展趋势

- **版本线**：v0.1.0（2026-02-23，属性面板/取色器）→ v0.2.0（2026-03-02，关键帧动画/逐片段特效/波纹编辑）→ v0.3.0（2026-04-15，蒙版/图形化关键帧编辑器/贴纸/Rust+wgpu WASM 合成器）`[Web]`。**所有 release 都属 classic 时代**；2026 年 5 月起 codebase 被替换为 rewrite，classic 代码迁入归档仓库 `opencut-classic` `[Web][API]`。
- **战略赌注**：从"能用的 Next.js 编辑器"转向"Rust 统一核心 + 插件生态 + MCP（让 AI agent 直接驱动剪辑）+ headless 批渲染"`[Web]`。方向前瞻，但风险在于——重写期功能停滞、外部贡献暂停，若骨架迟迟不能追平 classic 的能力，涌入的 6 万关注者可能流失。
- **社区反馈**：中文社区（什么值得买等）以"免费开源剪映替代""隐私零妥协"为主基调持续安利 `[Web]`；产品定位清晰、情绪价值强，是其增长的主引擎。

### 为什么"今日暴涨几千 stars"？（用户核心问题）

结论：**这是站外传播事件驱动，不是代码/发版驱动** `[Web][API]`。

1. **代码侧无爆发**：如上，编辑器分支 3-4 月就停更了，7 月没有新 release，暴涨与代码活动无因果 `[API]`。
2. **情绪 + 话题双击**：2026 年 6-7 月，中文与俄语等多语种科技媒体密集报道，标题清一色是"剪映越来越贵→转投免费开源替代""被剪映会员劝退""6 万星开源剪映"`[Web]`。剪映的商业化（涨价/会员墙）制造了明确的迁移动机，OpenCut 作为"零成本、隐私、开源"的对位选择被反复推荐。
3. **里程碑效应**：star 逼近 6 万→突破 6.6 万本身成为新闻点（"62,000 звезд""6万人转投"），形成"越涨越被报道、越报道越涨"的正反馈 `[Web]`。

即：一个**产品定位 × 竞品涨价 × 多语种媒体共振**的典型开源走红案例，而非一次技术发布带来的脉冲。

## 6. 竞品对比

（均为 `gh` 实测，截至 2026-07-14）`[API]`

| 项目 | Stars | 语言 | 协议 | 最近推送 | 与 OpenCut 的关系 |
|------|-------|------|------|----------|------|
| **OpenCut-app/OpenCut** | **66,956** | TypeScript | MIT | 2026-07-10 | 本项目：浏览器端 CapCut 替代 |
| remotion-dev/remotion | 53,089 | TypeScript | NOASSERTION（源可见/商用需授权）| 2026-07-13 | 用 React 代码"编程式"生成视频，面向开发者，非可视化剪辑 |
| mifi/lossless-cut | 42,059 | TypeScript | GPL-2.0 | 2026-07-11 | 无损剪切/合并，桌面 Electron，定位轻量裁剪而非全功能编辑 |
| CapSoftware/Cap | 20,134 | TypeScript | NOASSERTION | 2026-07-13 | 屏幕录制 + 分享为主，Tauri 桌面，剪辑是附带 |
| mltframework/shotcut | 14,535 | C++ | GPL-3.0 | 2026-07-14 | 老牌桌面非线性编辑器，功能全但非 Web/非现代栈 |
| OpenShot/openshot-qt | 6,057 | Python | GPL 系 | 2026-06-29 | 老牌桌面开源编辑器，Qt/Python |

**差异化**：OpenCut 几乎是唯一一个**「现代 Web 技术栈（React/WASM）+ 浏览器内完整时间轴剪辑 + 隐私本地化 + 对标 CapCut 交互」**的组合。remotion 是"代码生成视频"不同赛道；lossless-cut/Cap 功能面窄；shotcut/openshot 是桌面老栈。它在"零安装、隐私、免费替代剪映"这个生态位上基本无正面对手，这是它 star 数反超一众成熟项目的根本原因。

## 7. 总结评价

**优势**
- 生态位精准：免费开源、无水印无会员、浏览器即用、素材不出本地，正面接住"剪映涨价"的迁移人群 `[Web]`。
- classic 编辑器技术底子扎实：命令模式撑 undo/redo、节点式 WebGL 渲染树、完整关键帧动画、纯本地导出，均有真实源码支撑 `[代码]`。
- 战略视野前瞻：rewrite 押注 Rust 统一核心 + 插件 + MCP（AI 驱动剪辑）+ headless 渲染，方向踩中"AI + 本地化"趋势 `[Web]`。

**劣势 / 风险**
- **仓库结构极易误导**：默认 `main` 是空壳骨架，真编辑器在 `dev`/`staging` 与归档的 `opencut-classic`——新用户/研究者/贡献者极易看错，官方也未在 `main` 的 README 顶部足够醒目地澄清"当前默认分支不可用" `[代码]`。
- **巴士因子 = 1**：命脉系于单一核心作者，抗风险能力弱 `[API]`。
- **热度与代码活动背离**：编辑器分支 3-4 月停更、重写期外部贡献暂停，6 万关注者面对的是"能用的旧版"和"还在搭骨架的新版"之间的断层，若重写迟迟追不平 classic，热度可能回落 `[API][Web]`。
- 重写野心（Rust 核心/插件/MCP/headless）落地难度高，roadmap 尚无一项在 `main` 上真正跑起来 `[Web]`。

**适用场景**
- 想要**免费、隐私、零安装**的浏览器视频剪辑，且需求在 classic 能力范围内（时间轴、蒙版、关键帧、特效、mp4/webm 导出）→ 直接用 opencut.app，推荐。
- 想自托管/二次开发一个 Web 视频编辑器 → 可基于归档的 `opencut-classic`（MIT）起步，但要接受它已停更、且主线在重写。
- 想跟进"AI agent 驱动剪辑 / 插件生态 / Rust 统一核心"的前沿实验 → 关注 `main` rewrite 与 new.opencut.app，但目前只能观望，尚不可用于生产。

---
*报告生成时间: 2026-07-14*
*研究方法: github-deep-research 多轮深度研究*

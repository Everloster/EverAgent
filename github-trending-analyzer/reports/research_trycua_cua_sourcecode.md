# trycua/cua 深度研究报告（源码视角 · refer）

> 换视角报告（sourcecode）。同 repo 主报告：[[research_trycua_cua]]（68 天前）。本报告的视角是**源码级架构与模块地图**——给"要改它/用它/学它"的人一张文件+行号级的图纸。
> 源码基线：本地 clone `~/workspace/cua`，commit `9bbfa7dd3`（2026-09-19）。所有 [代码] 证据的路径行号以此为准。

## 1. 项目概述

cua 是 Cua AI 的开源 computer-use 平台："Give AI agents computers they can use"——给 AI agent 一台能用的电脑 [README]。官方自我定位 **Computer-Use 2.0**（`docs/content/docs/index.mdx:8`）：GUI 只是 agent loop 里的一种工具面，与 code/shell/files/API 并列 [代码]。它是一个**多语言 monorepo**，四大产品线并列：Lume（Apple Silicon 本地 macOS VM）、Cua Driver（跨 OS 桌面驱动）、Cua Fleets（云端托管桌面池）、Cua-Bench（评测/RL 环境框架）[README 卡片墙 + docs]。

## 2. 基本信息

| 项 | 值 | 证据 |
|---|---|---|
| Stars / Forks | 24,727 / 1,697 | [API] 2026-09-20 |
| 创建 / 最近推送 | 2025-01-31 / 2026-09-20 | [API] |
| 协议 | **MIT（根 LICENSE.md）；注意 `libs/python/som` 是 AGPL-3.0** | [代码] LICENSE.md；som/pyproject.toml |
| 语言占比 | HTML 19.3MB、Rust 11.1MB、Python 10.2MB、TypeScript 3.2MB、Go 2.6MB、Swift 1.7MB | [API] languages |
| 头部贡献者 | f-trycua 1520、ddupont808 830、github-actions[bot] 454、r33drichards 381、jamesmurdza 266 | [API] |
| 发版节奏 | cua-driver-rs 每日 nightly（v0.28.x）；sandbox v0.8.0（2026-09-15）；lume v0.5.x nightly | [API] releases |
| 官网 | https://cua.ai（Fleet 控制面 run.cua.ai） | [API] |

## 3. 技术分析（源码级架构）

### 3.1 全局地图：一个 monorepo，两套执行栈，一条迁移线

```
用户代码
 ├─ Py: cua-agent (ComputerAgent) ──litellm──▶ 模型
 │     └─ AsyncComputerHandler ─▶ cua-computer(Computer) ──REST/WS──▶ guest 内 computer-server
 │                               └─ cua_sandbox(Sandbox)  ──────────▶ 新一代 Sandbox API
 ├─ Rust: cua-driver ──MCP(stdio)/UDS──▶ 原生 OS 自动化（AX/UIA/AT-SPI）
 ├─ TS: @trycua/computer(legacy) ──WS──▶ guest computer-server
 ├─ TS: @trycua/fleet ──WASM(cyclops-sdk)──HTTPS──▶ Fleet 控制面
 └─ Py: cua-bench ─▶ session(simulated=Playwright | native=Docker/QEMU)
```

**两套互不相干的 computer-use 执行栈并存** [代码]：
- **cua-driver**（Rust）：原生 OS API 驱动，权限/授权重型（TCC 归因、policy gate），面向"驱动真实桌面应用不抢焦点"；
- **computer-server**（Python，跑在 guest 内）：截图+输入注入的通用原语层（pynput/Quartz/pynput/RFB），经 REST `/cmd` 或 WS `/ws` 服务。

迁移中态明确：xfce 镜像内置 computer-server 但注释"until a transport adapter is chosen"（`libs/xfce/Dockerfile:130-137`），xfce-cua 已**不再内置 computer-server、只留 cua-driver**（`libs/xfce-cua/Dockerfile:6,92`）[代码]。

### 3.2 Python SDK（libs/python）——"脑"与"手"

- **分层**：`cua-core`（遥测/HTTP）→ `cua-computer`（Computer 类，VM 生命周期+操控接口）→ `cua-agent`（ComputerAgent，loop 调度）→ `cua`（meta 伞包，re-export cua-sandbox + cua-agent + cua-cli）[代码]。
- **Computer**（`computer/computer/computer.py:72`）：`run()` 三段式=建 provider→起 VM→等 IP→建 interface→`wait_for_ready` 探针（:387）；动作全走 `GenericComputerInterface._send_command`——**REST 优先、WebSocket 兜底**（`interface/generic.py:1068/1028`），对端是 guest 内 computer-server [代码]。
- **ComputerAgent**（`agent/cua_agent/agent.py:257`）：主循环 `run()` :902 是异步生成器——`_on_llm_start` 回调链 → `loop.predict_step`（指数退避，litellm 内层 retry 显式关闭 :976）→ 执行 `computer_call` → 再截图包成 `computer_call_output` 追加 [代码]。
- **loop 注册制**：19 个模型 loop（anthropic/openai/uitars2/opencua/qwen3vl/fara…）import 即注册，`@register_agent(models=正则, priority)`（`loops/`、`decorators.py:13`）；任何奇葩模型名落到 `generic_vlm` 兜底 loop（priority=-100）——排查"没走我要的 loop"先看这里 [代码]。
- **组合模型**：`composed_grounded.py:123` 支持 `"grounding+thinking"` 双模型格式（思考模型出元素描述→grounding 模型出坐标）[代码]。
- **模型接入全走 litellm**（钉死 1.86.2），`ComputerAgent.__init__` 会**全局改写** `litellm.custom_provider_map`（agent.py:367）——同进程多 agent 会互相影响 [代码][坑]。
- **消息模型 = OpenAI Responses API items**（`types.py:13`）；轨迹 = items 列表 + 截图文件（TrajectorySaver callback），无独立 schema [代码]。
- **MCP**：三处别混——`mcp-server`（把 agent 暴露给 Claude Desktop）、`agent/integrations/hud`（fastmcp proxy）、`computer-server/mcp_server.py`（VM 内）[代码]。注意 `mcp-server` 依赖 `cua-computer>=0.4.0,<0.5.0` 而仓内已是 0.5.19，**版本约束过期** [代码][坑]。
- **纠正**：仓内**不存在 pylume 包**——lume 交互是 `providers/lume_api.py` 用 **curl 子进程**打 host 7777 REST [代码]。

### 3.3 虚拟化与沙箱层（lume/lumier/qemu-docker/kasm/xfce/xfce-cua）

贯穿事实：**这些模块只负责"把桌面跑起来"，agent 实际操作桌面靠 guest 内 computer-server** [代码]。

- **lume**（Swift，Virtualization.framework）：单二进制 CLI + HTTP（127.0.0.1:7777，**无鉴权**）+ MCP stdio 三接口共享 `LumeController`（1831 行）。VM 目录即镜像（config.json/disk.img/nvram.bin），ghcr OCI 分发（disk.img 分 chunk 作 layer、稀疏写）。硬骨头全在细节：运行锁=config.json flock + lsof 找 PID + SIGINT/SIGKILL（VM.swift:236-857）；IP 发现=解析 `/var/db/dhcpd_leases`（NAT 限定）；Linux 磁盘强制 `.cached` 防 EXT4 损坏（引用 Apple VZ 已知问题）；VNC 用 **Apple 私有 `_VZVNCServer`**（Dynamic 运行时再绑定，版本脆弱）；macOS 剪贴板因无 SPICE agent 走 SSH pbcopy/pbpaste；无人值守安装=离线改盘注入 `.AppleSetupDone`/autologin/sshd [代码]。
- **lumier**：Docker 容器**不是 hypervisor**——只 curl 编排 host 的 lume API + noVNC 桥（README"in a Docker container"表述误导）[代码]。
- **qemu-docker**：linux/windows/android 三变体，容器内 QEMU/KVM 跑整台 VM，guest 首启 `/oem` 装 computer-server（Linux systemd/Windows 计划任务），对外 5000=API + 8006=画面 [代码]。
- **kasm / xfce / xfce-cua**：流式桌面容器三形态；xfce-cua=应用中立基底、唯一运行时是 cua-driver（迁移目标态）[代码]。
- **guest 内 computer-server 的后端分派**（`handlers/factory.py:40-155`）：`CUA_BACKEND=native|vnc|cua-driver`；**lume macOS VM 特例**：guest 内截不到 framebuffer，用 vnc backend 回连 host 的 lume VNC（setup-cua.sh:483-486）[代码]。

### 3.4 cua-driver（Rust workspace，v0.28.2）——下一代执行栈

- 13 crate 分层：`contract`（平台无关 typed 契约）→ `core`（Tool trait `tool.rs:499`、注册表、MCP 分发、授权/策略）→ `platform-macos/windows/linux`（编译期装配，`sdk/src/runtime.rs:555-590`）→ `sdk`（UniFFI 出 Python/TS 绑定）[代码]。
- **对外协议不是 gRPC**：MCP over stdio（agent 主边界，支持 2026-07-28 新修订 + legacy）+ daemon socket（行分隔 JSON over UDS/named pipe）+ 默认关闭的 HTTP 前端 [代码]。
- **权限模式进程级固定**：standard / bounded / unrestricted（`--dangerously-bypass-approvals`），改模式必须重启 daemon；macOS 必须走 `CuaDriver.app` 保 TCC 归因 [代码]。
- **授权证据走 tokio task-local**（下划线字段在适配器层剥离进 TrustedInvocationEvidence，防调用方伪造，tool.rs:26-40）——改授权逻辑先看这里 [代码]。
- **cua-driver-fixtures**：4 个 vanilla HTML 测试页唯一真源，集成测试经相对符号链接引用，"drift impossible by construction" [代码]。

### 3.5 cua-s1 与 cuabot（模型线与独立栈）

- **cua-s1**：表单填写专才模型研究包（source-only，权重不发）——byte-level transformer encoder + option-attention 分类头（对每个界面元素选 fill/check/click/skip，**不生成字段值**）；规划与执行严格分离，执行默认 dry-run；submit 极窄（只允许一个高置信 Submit 按钮）；**唯一跨模块依赖=调 cua-driver 二进制**，且 README 自陈便携契约缺 `set_value`（fail-closed）[代码]。
- **cuabot**：**与 cua-driver 完全无关的独立栈**——Docker Ubuntu+Xpra 桌面，宿主机 `cuabotd`（HTTP:7842）用 **headless Playwright 连容器内 Xpra 页面**做截图/输入（坐标经 screenshotScale 换算），coding agent（claude/gemini/codex/openclaw…）经容器内 MCP 调回宿主机。坑：截图路径硬编码作者 Windows 目录（仅 DEBUG）、HTTP 无鉴权靠 loopback [代码]。

### 3.6 Fleet 与 cua-bench（控制面与评测）

- **Fleet（代号 Cyclops）**：公开镜像仓中仓。客户端逻辑全部收敛进 **Rust cyclops-sdk**（`libs/fleet/sdk/`，native reqwest + wasm32 fetch 双编译）再 UniFFI 辐射 6+ 语言——TS `@trycua/fleet` 只是 WASM 壳，改行为去 `libs/fleet/sdk/src/` [代码]。Go 后端是 sidecar 门面（Keycloak JWT + OPA），**所有 pool 操作落 K8s 自定义资源 `OSGymSandboxClaim`**——真正的编排器（operator）不在公开镜像里 [代码]。资源模型 Pool→Claim→guest services [docs]。
- **cua-bench**：gym 式任务框架——任务=目录+main.py+四装饰器（`@setup_task/@solve_task/@evaluate_task`，oracle 与 evaluator 刻意分离：oracle 跑不满分=任务 bug）；session 两档（simulated=Playwright 假桌面 / native=真 OS）；RL 向有 worker_server（FastAPI，每 server 最多 2 env）[代码]。
- **docs/**：fumadocs 内容仓（生产渲染在私仓 trycua/cloud）；架构主阵地在 `docs/content/docs/concepts/`（20 篇）[代码]。

## 4. 社区活跃度

- **提交强度**：2026-08-01~09-20 共 684 commits、7 月 449 commits（search API 精确计数 [API]）——周均 ≈100 量级，处于高速开发期。注：`stats/commit_activity` 端点返回空（GitHub 异步统计未就绪），本数据用 search/commits 兜底。
- **Issue**：open 513 / closed 502（≈50% 关闭率）[API]。
- **贡献者**：第一名 f-trycua（1520）为官方账号，前五名含 bot；核心团队 commit 占比高，**巴士因子偏低但系公司主导项目常态** [API]。
- **发版**：cua-driver-rs 每日 nightly 流水线（2026-09-13~19 连续 7 天有 prerelease）[API]。

## 5. 发展趋势

- **执行栈迁移中**：guest 内 Python computer-server → Rust cua-driver（xfce-cua 已落地目标态；nightly 每天发版）[代码+API]。
- **统一入口收敛**：Python 侧 meta 包 `cua` 转向 `cua-sandbox` 统一 API；TS 侧 `@trycua/computer` 已标 legacy，新代码走 fleet + sandbox SDK [代码]。
- **产品线向 Fleet 商业化收敛**：控制面 run.cua.ai、K8s CR 编排、计量计费管线（billing/metering/usage）都在公开镜像里 [代码]。
- **模型线**：CUA-S1（表单专才、byte-level 小模型）刚起步（source-only，权重未发）；CUA-S1-FORMS Hugging Face artifact 已挂（2026-09-19 文档提交）[API 提交记录]。
- [推测] 下一步看：cua-driver 何时在 macOS VM 场景吃掉 computer-server 的 vnc 回连路径；cua-s1 权重是否公开发布。

## 6. 竞品对比（2026-09-20 gh 实测）

| 项目 | Stars | 语言 | 协议 | 最近推送 | 与 cua 的差异 |
|---|---|---|---|---|---|
| browser-use/browser-use | 115,417 | Python | MIT | 2026-09-18 | 浏览器专用（DOM/Playwright），不管整台电脑 |
| OpenHands/OpenHands | 88,580 | TypeScript | MIT | 2026-09-19 | coding agent 平台，非桌面 GUI 操控 |
| bytedance/UI-TARS-desktop | 39,053 | TypeScript | Apache-2.0 | 2026-09-11 | 桌面 agent 应用+模型；cua 更重基础设施/多 OS 沙箱/评测 |
| simular-ai/Agent-S | 12,329 | Python | Apache-2.0 | 2026-09-05 | 研究型 GUI agent；cua 是平台+运行时 |
| xlang-ai/OSWorld | 3,152 | Python | Apache-2.0 | 2026-09-14 | 评测基准；cua-bench 与之相邻且自带平台适配（platforms.py 有 linux-qemu=OSWorld 映射）[代码] |

全部数值为本日 `gh api` 实测 [API]。cua 的差异位：**全栈**（本地 VM 虚拟化 + 跨 OS 沙箱 + Rust 驱动 + agent SDK + 评测 + 云 Fleet），不是单点 agent。

## 7. 总结评价

**优势**：① 源码透明度高到罕见——连商业 Fleet 的控制面 sidecar、计量计费、Terraform provider 都在公开镜像里；② 工程细节硬核（lume 的 VZ 封装、flock 运行锁、离线无人值守改盘）；③ 双执行栈+明确迁移线，架构演进可读；④ 证据化文化（fixtures 防漂移、授权 task-local 防伪造）。
**劣势/风险**：① 两套执行栈并存期的认知负担（computer-server vs cua-driver，新人易混）；② lume 依赖 Apple 私有 `_VZVNCServer`，版本脆弱；③ lume HTTP 无鉴权（仅绑 localhost）、guest 硬编码 lume/lume 凭据——**别把 7777 暴露到局域网**；④ cua-som 是 AGPL-3.0（其余 MIT），商用注意传染；⑤ mcp-server 依赖约束过期等 monorepo 卫生小问题。
**适用场景**：要在 macOS 本机/多 OS 跑 computer-use agent 的研发团队；需要可复现评测环境（cua-bench）的模型团队；想读"生产级 agent 基础设施长什么样"的学习者——本仓是绝佳教材。

## 8. refer 速查（去哪看地图）

| 我要… | 去哪 |
|---|---|
| 加新模型 loop | `libs/python/agent/cua_agent/loops/` 仿 anthropic.py + `@register_agent` |
| 加新动作原语 | `agent/cua_agent/computers/base.py` Protocol + handler + `agent.py _handle_item` 按名分发 |
| 改 VM 行为 | `libs/python/computer/computer/computer.py:run()` + `providers/` |
| 改传输层 | `computer/interface/generic.py`（REST 优先/WS 兜底） |
| 改 lume 业务 | `libs/lume/src/LumeController.swift`；VZ 封装 `src/Virtualization/VMVirtualizationService.swift` |
| lume 加 HTTP 路由 | `libs/lume/src/Server/Server.swift:197`；MCP 工具 `src/Server/MCPServer.swift:329+` |
| 改镜像分发 | `libs/lume/src/ContainerRegistry/ImageContainerRegistry.swift` |
| 改 cua-driver 授权 | `libs/cua-driver/rust/crates/cua-driver-core/src/tool.rs`（task-local 证据） |
| 加 driver 工具 | `platform-{os}/src/tools/mod.rs` 注册 + contract crate |
| 改 Fleet 客户端行为 | `libs/fleet/sdk/src/`（TS 壳在 `libs/typescript/fleet`，别改那） |
| 写评测任务 | `libs/cua-bench/datasets/cua-bench-basic/`（目录+四装饰器） |
| 改操控原语 | `libs/python/computer-server/computer_server/handlers/` |
| 架构概念文档 | `docs/content/docs/concepts/`（20 篇） |

---
*报告生成时间: 2026-09-20*
*研究方法: github-deep-research 多轮深度研究（R2 为本地源码 4 组并行勘察）*

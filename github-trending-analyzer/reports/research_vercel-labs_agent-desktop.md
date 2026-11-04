---
title: "agent-desktop 深度研究：Agent 怎样可靠地操作桌面"
domain: "github-trending-analyzer"
report_type: "repo_deep_research"
status: "completed"
updated_on: "2026-11-04"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["computer_use", "desktop_automation", "accessibility", "agent_harness", "rust"]
---

# agent-desktop 深度研究：Agent 怎样可靠地操作桌面

让 Agent 点击“保存”并不难。难的是：窗口移动后，点的还是原来的按钮吗？命令超时后，文件究竟保存了没有？两名 Agent 同时操作时，会不会把内容输入到另一个窗口？

Vercel Labs 的 **agent-desktop** 把这些问题放到了工具层处理：通过操作系统的无障碍接口读取控件，为控件建立带快照标识的引用，执行前重新核对目标，返回操作是否投递、是否验证、能否重试。它提供的是桌面操作工具，任务规划和业务结果验收仍由调用它的 Agent 负责。[README](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/README.md)、[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/resolve_saved_ref.rs#L27)

**研究结论：值得作为桌面操作的候选工具，也很值得学习其返回结果和失败处理的设计；目前的证据还不足以支持直接替换现有工具。** 特别要看清两个边界：Windows、Linux 的控件身份主要依据稳定字段，并不保证始终对应同一个控件实例；“操作已验证”也可能只验证了输入框的值，没有验证应用真正提交了数据。

本文基于 2026 年 11 月 4 日读取的公开资料。源码固定到 [93ae89e](https://github.com/vercel-labs/agent-desktop/commit/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72)；当时最新发布版本为 [v1.1.0](https://github.com/vercel-labs/agent-desktop/releases/tag/v1.1.0)。完成了源码审读和 7 项安装测试，**没有完成三平台真实桌面操作测试**。

## 一、项目概述：给 Agent 一套能核对目标的桌面工具

### 从“看图找位置”到“读取控件”

纯视觉操作通常先截屏，再让模型判断坐标。agent-desktop 的主要入口是 **accessibility tree，无障碍树**：操作系统提供的界面结构，包含按钮、文本框、菜单及其名称、状态等信息。模型可以直接看到“这是一个名称为保存的按钮”，然后通过 ref 操作它；需要时也能使用截图和坐标输入。[README](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/README.md)

这条路线减少了模型自行解释像素的步骤，但上限取决于应用暴露了多少信息。某个控件如果没有进入无障碍树，工具不能凭空补出其语义。后文会看到，真实用户已报告过 Word 正文无法通过快照读出的情况。

下面是官方示例的基本循环，**仅用于说明用法，并非本次执行记录**：

```sh
agent-desktop snapshot --app Finder -i
# 从返回结果中选择实际存在的 ref，再执行：
agent-desktop click @s8f3k2p9:e8
agent-desktop snapshot --app Finder -i
```

`@s8f3k2p9:e8` 表示某份快照中的一个元素。示例编号不能直接复用，裸 `@e8` 也不是该项目当前接受的完整引用格式。执行后的快照用来检查界面变化。[README](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/README.md)、[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/ref_token.rs#L1)

### 它负责什么，调用者还要负责什么

工具负责读取桌面、解析目标、检查可操作性、执行动作和报告观察到的结果。调用者负责理解任务、选择下一步、判断内容是否可信，以及确认用户真正想完成的事情已经完成。

例如，输入框显示了正确邮箱地址，是工具可以读回检查的局部状态；收件人是否正确、消息是否应该发送、服务器是否接受了消息，是另一层问题。工具没有内置语言模型，也不会自动完成这些业务判断。[官方 FAQ](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/docs/faq.md#L74)、[结果协议](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/docs/json-output.md#L1)

## 二、基本信息：研究的是哪个版本

下表来自 2026-11-04 采集的 [GitHub 仓库 API](https://api.github.com/repos/vercel-labs/agent-desktop)。数字是查询时点的快照。

| 项目 | 核验结果 |
|---|---|
| 仓库 | `vercel-labs/agent-desktop` |
| 创建日期 | 2026-02-19，UTC |
| Stars / Forks | 12,018 / 821 |
| 开放条目 | 140，GitHub 此字段包含 issue 和 PR |
| 许可证 | Apache-2.0 |
| 默认分支 | `main` |
| 源码版本 | `93ae89e`，提交于 2026-11-03 |
| 最新 Release | v1.1.0，发布于 2026-11-03 04:13 UTC |

[API] [语言统计](https://api.github.com/repos/vercel-labs/agent-desktop/languages)中 Rust 占代码字节数约 72.13%，其次为 PowerShell 13.00%、Python 5.76%。这是 GitHub 的语言字节统计，不能据此推导模块重要程度或执行耗时。

发布方式包括 npm 安装原生 CLI，以及直接下载二进制或 FFI 动态库。v1.1.0 的 [Release 资产](https://github.com/vercel-labs/agent-desktop/releases/tag/v1.1.0)覆盖 macOS、Windows、Linux 的 x64 和 ARM64，共六种平台组合，并提供校验和。npm 是安装入口，不代表桌面执行核心由 JavaScript 实现。README 当时仍注明 Homebrew、Scoop 默认目录未收录，不能直接照搬 agent-browser 的安装命令。[README](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/README.md)

源码快照比 v1.1.0 Release 晚，包含后续光标覆盖层修复；本文的代码判断以固定提交为准，发布资产判断以 v1.1.0 为准。更新日志标题的日期与 GitHub 实际发布日期也可能不同，以上采用 Release API 时间。

## 三、技术分析：一次点击背后发生了什么

### 3.1 入口很薄，公共核心承担约束

代码按职责分为三层：

1. **CLI 入口与分发。** `src/main.rs` 建立平台适配器和命令上下文，带上会话、交互策略和截止时间；`src/dispatch` 将命令交给公共核心。
2. **公共核心。** `crates/core` 管理快照、refs、目标身份、可操作性检查、交互锁与结果协议。
3. **平台适配器。** macOS、Windows、Linux 分别对接本机能力，公共核心通过 `PlatformAdapter` 调用它们。FFI 另向宿主程序暴露 C ABI。

[代码：入口](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/src/main.rs#L130)、[分发](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/src/dispatch/mod.rs#L1)、[工作区结构](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/Cargo.toml#L1)

**v1.1.0 已移除 macOS command host，每次 CLI 调用独立运行。** 因而不能把旧版“常驻命令进程”的架构搬进当前分析。不过，独立进程不意味着没有持久状态：快照引用保存在会话目录中，交互还需要跨进程协调。[更新日志](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/CHANGELOG.md#L3)、[RefStore](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/refs_store.rs#L21)

### 3.2 Ref 的可靠性来自两次检查

最容易误解的地方是：ref 看起来像一个元素编号，但编号本身没有证明能力。

对于没有原生对象 token 的元素，代码要求在两个时点证明其唯一性：**获取快照时，完整窗口观测中只有它符合身份条件；真正执行时，当前窗口中仍然只有一个元素符合。** 找到落点后，还会核对落点对象。[代码：捕获证明](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/ref_capture_proof.rs#L1)、[执行前解析](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/resolve_saved_ref.rs#L27)

身份条件由控件角色及已记录的稳定字段组成，包括可用的原生标识、稳定名称和描述。会变化的输入值、坐标不作为身份依据。因此，窗口移动不会仅仅因为坐标改变就让身份失效；在输入框中填入文字，也不应把输入框变成“另一个控件”。字段的“已知”“不存在”“未能读取”分别处理，不能把没读到当成确实不存在。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/ref_full_predicate.rs#L13)

考虑一个列表，每行都有一个“删除”按钮：

- 如果应用为每个按钮暴露了不同的稳定标识，就有机会区分它们。
- 如果两个按钮的角色、名称和已记录稳定字段完全相同，无 token 的 ref 会拒绝执行，不能靠“刚才它在第三行”猜测。
- 如果原按钮消失，随后出现一个字段完全相同的新按钮，Windows、Linux 的规则仍可能匹配并操作新按钮。**它证明的是当前语义匹配唯一，不是原控件实例一直存活。**

最后一点是项目 [v1.1.0 更新日志](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/CHANGELOG.md#L3)明确承认的限制；某些工具包甚至可能继续列出已移除的控件。严格匹配能避免一类错误，但不能消除应用自身提供错误信息的风险。

### 3.3 macOS 的对象 token 更直接，也有额外依赖

macOS 在可用时保存原生对象 token，下一次通过 token 找回对象，再核对进程、角色和原生标识。已有 token 失效时直接返回 `STALE_REF`，不会改找一个外观相似的替代控件。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/macos/src/tree/resolve/retained_resolve.rs#L43)

但这个能力有一个必须公开说明的条件：实现动态加载了两个 **私有 AX 符号**，`_AXUIElementRemoteTokenCreate` 和 `_AXUIElementCreateWithRemoteToken`。符号不存在或元素不提供 token 时，捕获返回空，转用前面的稳定字段规则；并非所有 macOS 元素始终拥有这种对象级身份。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/macos/src/tree/resolve/retained.rs#L34)

[推测] 这有助于解释项目为何同时保留对象 token 与跨平台匹配两条路径，也意味着系统升级后的兼容性值得单独回归，不能把私有接口当作长期不变的公开承诺。

### 3.4 少给模型看一些，不一定少读取一些

`snapshot --skeleton` 先给浅层结构，`snapshot --root <ref>` 再展开目标区域。这对大型窗口很实用：Agent 不必每次都接收整个树。[官方 Skill](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop/SKILL.md)

但**输出裁剪和身份核验是两件事**。对于无 token 的 ref，代码可能先读取完整窗口，证明没有另一个同样的控件，再裁剪成浅层结果。因此，可以预期输出更短，却不能仅凭输出更短就宣称系统读取成本或延迟按比例降低。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/snapshot/window_capture.rs#L35)

完整读取受深度、时间和应用响应能力约束；“完整”是工具观测范围内的完整，不代表掌握了应用的所有业务内容。若只成功取得浅层树、没有取得身份依据，快照可带 `identity_unproven: true`。`complete` 描述呈现出的树，不能替代身份判断。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/commands/snapshot.rs#L128)、[协议迁移说明](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/docs/json-output.md#L1)

局部展开也有细节：它沿用原快照 ID，在 RefStore 的写锁中替换对应子树的 refs，保留外围引用；展开不完整就不覆盖原映射。这个事务保护的是本地引用记录，不能让真实桌面在读取期间停止变化。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/snapshot/snapshot_ref.rs#L42)

### 3.5 多 Agent 共用桌面：先等待，再持锁重查

直接锁住桌面、等一个窗口加载完，会让其它任务也停下来。实现将准备阶段放在交互锁外：先等待目标看起来可操作，拿到锁后重新解析和检查，随后执行。锁外取得的句柄不会直接被当成最终执行依据。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/ref_action/ref_action_poll.rs#L22)

交互 lease 用于串行化参与这套协议的操作；Unix 实现包含用户范围的文件锁和进程内保护。它不锁住用户的鼠标、不阻止应用异步更新，也不约束另一个完全不使用这把锁的工具。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/session/interaction_lease.rs#L1)

因此，这里的 session、refs 和多 Agent 光标都不能等同于“多设备共享一个智能体会话”。session 隔离本地持久状态，不能隔离真实桌面；跨设备任务上下文、权限和调度仍需外部系统负责。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/refs_store.rs#L21)、[推测]

### 3.6 返回结果比一个 success 更有用

当前 JSON 输出协议为 2.6。最有借鉴意义的字段是 `disposition`，它将投递状态与是否适合重试分开表达：[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/response/delivery_disposition.rs#L1)、[协议](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/docs/json-output.md#L1)

- `not_delivered`：没有投递；有些成功返回表示目标状态已经满足。
- `delivery_uncertain`：无法确定是否投递，不能直接重发。
- `delivered_unverified`：已投递，但没有验证要求的后置状态。
- `delivered_verified`：已读回并验证报告中声明的局部状态。
- `unknown`：证据不足，不能自行补成成功或安全重试。

假设 Agent 点击“发送”，随后等待“发送成功”提示超时。如果点击已经投递，超时不代表可以再点一次。协议会保留前面动作的投递信息，即使整个命令最后返回错误。调用者应该先核对消息列表或业务状态。

反过来，`retry: safe` 只说明重试不会叠加一个已经发出的动作，**不保证同样的输入下次会成功**。两个无法区分的“删除”按钮仍然无法区分；对旧 ref 机械重试没有价值，需要重新观察或改变任务路径。[协议](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/docs/json-output.md#L1)

局部验证也必须读清范围：字段的值正确，不等于表单事件已触发，更不等于服务器提交成功。平台指南专门说明 `element_value` 验证与 `application_commit: not_verified` 的区别。把这些都折叠成“成功”，会重新丢掉工具已经提供的关键信息。[Windows 指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-windows/SKILL.md)、[Linux 指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-linux/SKILL.md)

### 3.7 Headless 不代表没有桌面，也不代表没有副作用

该项目默认交互策略禁止抢焦点和移动物理鼠标；`--headed` 则允许这两种行为。这里的 headless 指交互方式，仍然可能修改应用内容，仍然需要实际图形会话及系统权限。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/actions/interaction_policy.rs#L1)

以 Windows 为例，`type` 使用键盘注入，需要 headed；支持对应语义接口的控件可以尝试 `set-value`。二者不应仅因最终文字相同就被当作完全等价，应用是否触发事件、提交数据还需要检查。[Windows 指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-windows/SKILL.md)

**macOS：** 官方支持 13+，提供 x64 / ARM64 版本。需要按操作授予无障碍、屏幕录制等权限；前述对象 token 并非始终可用。

**Windows：** 官方支持 Windows 10 1809+ / Server 2019+，提供 x64 / ARM64 版本。必须处于已登录的交互桌面；锁屏、Session 0、UAC 安全桌面不支持，并受权限完整性级别限制。

**Linux：** 官方列出 Ubuntu 24.04+，提供 x64 / ARM64 版本。需要正确的图形用户会话与 AT-SPI；普通 SSH 或容器不会自动提供桌面访问。

[Web：支持范围](https://agent-browser.dev/desktop)、[平台指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-windows/SKILL.md)、[Linux 指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-linux/SKILL.md)

Linux 还要区分 X11 和 Wayland。项目主要测量环境是 GNOME；Wayland 能力不能按 X11 推断，通用指针移动、拖拽等会被拒绝，截图还有 portal 授权条件。二进制 glibc 兼容下限也不等于所有发行版、桌面环境都经过验证。

README 列出 60 个命令名，其中 56 个可操作。其余四个按下／释放键鼠的命令暂时拒绝运行，因为缺少保证进程异常后释放按键的事务所有者。这个细节说明：命令出现在帮助中，不代表当前具备可用实现。[README](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/README.md)、[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/commands/input_hold_policy.rs#L1)

### 3.8 CLI、FFI 和浏览器各有合适的接入方式

已有 Shell 工具的 Agent 可以先使用 CLI。需要进程内调用时，可用 C ABI，避免逐次启动 CLI；但这带来内存释放、线程和 ABI 版本责任。原生句柄有线程归属，不能因为 adapter 能跨宿主线程使用，就推导所有句柄都可任意传递。[FFI 指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-ffi/SKILL.md)、[线程约束](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-ffi/references/threading.md)

v1.1.0 的 C ABI major 已为 7；旧的两个 exact 操作入口虽然仍存在，却返回不支持，官方要求走带捕获依据的 snapshot ref。FFI 也没有暴露 CLI 的全部快照选项。接入时必须以版本契约为准，不能把“有 C 库”理解为完整的高层 Python SDK。[更新日志](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/CHANGELOG.md#L3)、[FFI 指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-ffi/SKILL.md)

Chromium / Electron 的网页内容还有另一条路径：显式 `launch --cdp` 开启本地调试端点后，由 agent-browser 处理网页，agent-desktop 处理原生菜单和对话框。代码检查已运行实例和冲突参数，并绑定回环地址；普通 launch 不会默认启用 CDP。[代码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/commands/launch.rs#L19)

### 3.9 本次实际验证了什么

在固定源码提交、Node.js v24.14.1 环境执行了以下命令：

```sh
node --test \
  --test-name-pattern='checksum lookup|archive validation|archive installation|corrupted installed binary' \
  tests/npm/postinstall.test.js
```

实际输出为 **7 tests，7 pass，0 fail**。覆盖校验和精确匹配、归档多出文件时拒绝安装、macOS 配套可执行文件保留、Windows 单可执行文件安装、临时 staging 目录清理，以及已安装二进制被篡改时不走快速复用路径。测试使用临时 fixture，没有操作真实桌面。[测试源码](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/tests/npm/postinstall.test.js)

另外尝试了 `cargo test --locked -p agent-desktop-core --lib`，因环境没有 `cargo`，返回 `command not found`，**Rust 核心单测未运行**。因此本次验证只支持安装逻辑的部分完整性判断，不支持“桌面交互已测通”“三平台稳定”或任何速度、成功率结论。

## 四、社区活跃度：迭代很快，维护仍较集中

[API] [52 周提交统计](https://api.github.com/repos/vercel-labs/agent-desktop/stats/commit_activity)合计 289 次提交，周均约 5.56；最后 8 个周桶合计 77 次，周均约 9.63。最近一个桶包含尚未结束的当前周，而且仓库创建还不到一年，不能把前后均值当作严格的增长率。

[API] [贡献者接口](https://api.github.com/repos/vercel-labs/agent-desktop/contributors?per_page=100)返回 9 个账户，其中 3 个被 GitHub 标为 Bot。返回记录合计 324 次贡献，首位账户 lahfir 为 221 次，约 68.2%。贡献者统计与 52 周提交统计口径不同，不能直接相减或互相替代；账户类型也不能用来判断某次代码是否由 AI 生成。

[推测] 这些数字支持“近期开发活跃、贡献集中”的判断，不足以证明生产可靠性或大量企业采用。

### Issue 更适合拿来设计试验

读取的最新 50 条 issue 接口记录中，40 条是 PR、10 条是纯 issue。以下是其中及补充读取的风险线索，均为**用户报告，未在本次复现**：

- [#529：Linux X11 按键操作崩溃](https://github.com/vercel-labs/agent-desktop/issues/529)。报告在 Chrome 地址栏场景出现 SIGSEGV，提示需要对具体桌面和应用做回归。
- [#479：Word 正文读不出来](https://github.com/vercel-labs/agent-desktop/issues/479)。有内容和空文档的快照表现相近，提示“能发现窗口”不等于“能读取文档”。
- [#494：Voice Memos 出现目标歧义](https://github.com/vercel-labs/agent-desktop/issues/494)。快照成功后，ref 操作仍可能被身份规则拒绝。
- [#513：Windows 标点与 Shift 导航键](https://github.com/vercel-labs/agent-desktop/issues/513)。提示输入能力需要覆盖真实键位组合，不能只测字母。

#513 和 #494 的首条非作者技术评论分别约在开帖后 6.97 小时和 4.58 小时出现，评论者的 API 关系标记均为 `NONE`。这只能说明样本出现了社区响应，不能算维护者 SLA；另一条样本的早期评论是无关内容，未计入技术响应。[评论 API：513](https://api.github.com/repos/vercel-labs/agent-desktop/issues/513/comments)、[494](https://api.github.com/repos/vercel-labs/agent-desktop/issues/494/comments)

## 五、发展趋势：接口正在收紧，升级要重做契约检查

近期正式发版包括 v0.10.0（10 月 18 日）、v0.11.1（10 月 25 日）、v1.0.0（10 月 28 日）、v1.0.2（10 月 30 日）和 v1.1.0（11 月 3 日）；日期采用 GitHub Release 的 UTC 发布时间。[API](https://api.github.com/repos/vercel-labs/agent-desktop/releases?per_page=10)

这轮变化不只是增加功能。v1.1.0 收紧无 token ref 的唯一性要求、把 JSON 协议升级到 2.6、将 C ABI major 升到 7，并移除了 macOS command host。旧快照缺少新的捕获依据，在 Windows、Linux 上需要重新获取；旧调用方还要处理某些 macOS 系统界面快照不再含 `data.window` 的情况。[更新日志](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/CHANGELOG.md#L3)

[推测] 从这些改动看，项目正在将“不确定时也尝试操作”的空间缩小，把更多拒绝原因和结果状态显式交给调用者。这对可靠集成有价值，也会让一些过去碰巧能运行的脚本开始失败。升级时应固定版本、清理对旧 refs 的依赖，并回归结果解析，而不能仅验证可执行文件还能启动。

这不是官方长期路线图，也不能据此预测何时解决所有应用兼容问题。后续更值得关注的信号是：真实应用回归样本是否扩大、私有 AX token 的兼容性是否持续验证，以及投递状态是否始终与实际副作用一致。

## 六、竞品对比：操作工具、浏览器工具与桌面环境

比较基于三者官方 README 与 2026-11-04 的 API 快照，没有进行同任务性能跑分。

| 项目 | 主要定位 | Stars / Forks |
|---|---|---|
| agent-desktop | 现有桌面的原生控件与输入操作 | 12,018 / 821 |
| [agent-browser](https://github.com/vercel-labs/agent-browser/blob/main/README.md) | 浏览器自动化 CLI，支持树、refs 和 CDP 等接口 | 45,376 / 3,112 |
| [Cua](https://github.com/trycua/cua/blob/main/README.md) | 包含桌面驱动、独立桌面环境、SDK 和评估工具的组合 | 31,663 / 2,347 |

[API：agent-browser](https://api.github.com/repos/vercel-labs/agent-browser)、[Cua](https://api.github.com/repos/trycua/cua)。Stars 表示关注量，不能用来排名任务成功率。

**与 agent-browser 相比，关键在操作对象。** 网页内容优先使用浏览器本身的接口，原生应用窗口和系统对话框则需要桌面工具。两者可以配合。agent-browser 当前 README 描述 Rust CLI 与常驻 Rust daemon，通过直接 CDP 工作；这与 agent-desktop v1.1.0 每次 CLI 独立进程的设计不同，也不能继续把当前 agent-browser 简化成 Node.js / Playwright 薄包装。[README](https://github.com/vercel-labs/agent-browser/blob/main/README.md)

**与 Cua 相比，需要拆开产品层次。** Cua Driver 同样提供桌面观察和操作，支持 CLI、MCP、SDK，并说明后台投递取决于应用和平台条件；它是较直接的对照对象。Cua Spaces、Lume 进一步提供独立桌面或虚拟机，Cua Bench 用于评估。需要把 Agent 的桌面与日常桌面隔开时，环境层能力与一个操作 CLI 解决的不是同一部分问题。[README](https://github.com/trycua/cua/blob/main/README.md)

Cua 的许可也不能只看 GitHub 顶层 MIT 标识：README 将多数基础组件列为 MIT，将 Spaces 和 Driver Bench 列为 FSL-1.1-MIT，可选感知组件另有许可。采用哪部分，就需要核对哪部分的实际条款。[许可说明](https://github.com/trycua/cua/blob/main/README.md#licensing)

[推测] 对已有 Agent、只缺少原生桌面操作接口的系统，先试 agent-desktop 比引入整套桌面环境更容易划清验证范围；对需要独立桌面和可重复评估的系统，应同时考察环境隔离能力。没有同环境测试之前，不宜宣称其中任何一个整体更快、更稳定。

## 七、总结评价：先学契约，再做小范围接入

### 最值得带回日常工程的三点

第一，**保存证据，而不只是保存坐标或名字**。快照引用记录目标来源和身份条件，执行前重新核验，能把不少“点错了才知道”的问题提前变成可解释的拒绝。

第二，**把副作用与重试写进工具结果**。操作未投递、已投递未验证、已验证局部状态，是不同状态；上层 Agent 应保留这些差异，尤其不能对发送、购买、删除等动作套用统一重试。

第三，**把短输出与充分核验分开设计**。给模型少量相关内容可以节省上下文，但不能为此丢掉用于判断目标唯一性的观测。后台完整读取和前台局部展示有各自的成本。[推测，依据前述实现]

### 怎样验证它是否适合自己的工作流

建议在测试应用或独立桌面上固定版本，完成下面四组试验，再决定是否纳入日常工具。这是后续验证方案，**不是本次已测结果**。

1. **读得到什么。** 对原生应用、Electron、文档应用分别读取窗口，记录正文、控件、菜单的可见范围；同时检查快照完成状态与身份依据。
2. **目标会不会认错。** 移动窗口、插入相同按钮、删除并重建元素，观察旧 ref 是正确跟踪、拒绝，还是匹配到替代元素。特别区分 macOS token 路径与无 token 路径。
3. **失败后会不会多执行一次。** 用可观察的计数器动作制造“已点击但后续等待失败”，核对结果里的投递状态，并检查上层是否错误重试。
4. **并发时会不会互相干扰。** 两个调用方针对不同窗口操作，同时记录焦点、目标命中、等待时间与人工介入；不能只看各自退出码。

记录任务完成率、错误目标次数、重复动作次数、人工介入次数，以及端到端延迟与返回文本量。对重复按钮等本来应拒绝的情况，正确拒绝应单独计数，避免把安全退让误记为普通失败；也避免为了提高表面成功率而鼓励猜测。

### 隐私边界与本次限制

原生 CLI 不内置模型，但快照、窗口标题、剪贴板、截图、debug HTML 和 trace 可能包含敏感信息。文字脱敏不能自动清理截图。读取到的页面或桌面文字也可能带有诱导指令，身份核验只核对控件，不证明其中内容可信。[官方 FAQ](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/docs/faq.md#L74)

仓库还含可选、未进入默认 npm 包的 JEV helper。其文档说明会向配置的模型服务发送目标和屏幕文字描述；`--no-values` 不能去除标题、名称或任务目标中的所有敏感信息。因此不能从“原生 CLI 本地运行”推导“仓库内任何运行路径都不会外发”。[JEV 说明](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/jev-desktop/SKILL.md)

本报告没有进行真实桌面、权限、截图、远程连接或多 Agent 并发实验；没有测量 Token 节省、延迟和任务成功率；没有把 issue 中的报告当成普遍缺陷。当前能确认的是实现方式、公开接口和部分安装测试结果。**是否适合日常使用，仍需用具体应用的结果验证。**

### 延伸阅读与源码入口

- 产品与使用：[官方文档](https://agent-browser.dev/desktop)、[固定版本 README](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/README.md)、[通用操作 Skill](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop/SKILL.md)。
- 最值得精读的实现：[捕获时证明唯一](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/ref_capture_proof.rs#L1) → [执行前再次解析](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/crates/core/src/refs/resolve_saved_ref.rs#L27) → [投递结果协议](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/docs/json-output.md#L1)。
- 升级和嵌入：[v1.1.0 Release](https://github.com/vercel-labs/agent-desktop/releases/tag/v1.1.0)、[更新日志](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/CHANGELOG.md#L3)、[FFI 指南](https://github.com/vercel-labs/agent-desktop/blob/93ae89e86fb849eeb5fc265b0b8e37eca56aaf72/skills/agent-desktop-ffi/SKILL.md)。
- 对照阅读：[agent-browser](https://github.com/vercel-labs/agent-browser/blob/main/README.md)、[Cua](https://github.com/trycua/cua/blob/main/README.md)。竞品部分限于公开文档和元数据核对，没有扩展为两份独立源码审计。

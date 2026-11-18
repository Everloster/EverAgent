---
title: "Claude Code Mode：把工具调用写成程序，怎样省下往返，又保留判断与权限"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
source_url: "https://code.claude.com/docs/en/code-mode"
updated_on: "2026-11-18"
semantic_tags: ["claude-code", "code-mode", "programmatic-tool-calling", "tool-orchestration", "permissions", "context-engineering"]
---

# Claude Code Mode：把工具调用写成程序

Code Mode 让 Claude 把一组工具调用写成 JavaScript，再由 Claude Code 在会话中执行。代码可以并行调用工具、根据返回值继续处理，并只把需要的结果交回模型。用户仍然用自然语言提出任务。[官方说明](https://code.claude.com/docs/en/code-mode)

它改变的是工具使用方式：原来多次“调用工具、读结果、决定下一步”的往返，其中一部分可以由一次生成的程序完成。适合固定规则的批处理，也适合大量结果需要先筛选的任务。它并不自动提高事实判断能力，也没有在这页文档中给出通用的提速或省 token 百分比。

截至本次查阅，它仍是默认关闭的实验功能。官方 CHANGELOG 将其首次加入列在 **v2.1.323**。本机已安装原生 **v2.1.327**，版本条件满足；当前用户配置存在自定义 API 路由和 `ANTHROPIC_AUTH_TOKEN`，按文档不适合直接启用。本次研究没有启动 Code Mode 或改变账号、路由与权限设置。

## 为什么“一段程序”能少走几次往返

用报告工作解释这个差别。假设需要检查一批文档的本地链接，常见过程是读取一篇、发现链接、检查目标，再读下一篇。只要目标存在与否有明确规则，这些中间决策就不必每次交给模型重新推理。

Code Mode 可以把重复部分写成循环或并行程序，完成检查后返回文件数、坏链接及读取失败。原文还举了查找代码、编辑、运行测试的连续操作例子：后一步可以使用前一步算出的路径。[工作机制](https://code.claude.com/docs/en/code-mode#how-code-mode-works)

```text
用户提出任务
      ↓
Claude 写 JavaScript：调用哪些工具，怎样处理返回值
      ↓
Claude Code 执行代码，工具仍执行各自的动作
      ↓
代码返回选定结果
      ↓
Claude 根据这些结果判断下一步
```

节省来自两处：减少中间步骤之间的模型往返，以及避免让模型反复读取并不需要的完整输出。例如筛出一百条记录中的三条异常，代码可以先做确定性筛选，模型只解释异常。

但模型在生成程序时，必须先知道这些步骤怎样连接。如果读到一篇材料之后，需要重新决定研究方向，那部分仍需要模型介入。将代码一口气写得很长，可能只是提前固定了本应根据证据调整的判断。

原文默认对话展示具体工具调用，例如编辑 diff；要查看背后的 JavaScript，需要用 `Ctrl+O` 展开 transcript 中的 Code 行。判断它做了什么，应同时看生成的代码、实际工具结果和修改，而不只看最终摘要。

## 它与写 Bash 脚本、与 API 程序化调用分别有什么关系

Claude Code 原本就能通过 Bash 运行脚本。Code Mode 更进一步，把工具调用本身变成可编程对象：不仅是 shell 命令，也能在一段代码里组织会话工具。代码做的是循环、分支、并行和数据传递，并不因此获得一个新的独立 Agent。

这里还容易与 Anthropic API 的 **Programmatic Tool Calling** 混淆。两者采用相近设计，但公开入口和执行流程不同：

| 问题 | Claude Code 的 Code Mode | API 的 Programmatic Tool Calling |
|---|---|---|
| 从哪里使用 | 原生 CLI 的终端交互会话 | 应用调用 Messages API |
| 模型写什么 | JavaScript | Python |
| 工具怎样被组织 | Claude Code 在会话里执行代码并处理工具调用 | 托管代码执行容器暂停，API 返回工具请求，应用执行工具并交回结果 |
| 如何启用 | 实验环境变量与首次确认 | 提供 code execution 工具，并设置工具的 `allowed_callers` |
| 用户侧权限 | Claude Code 的权限模式、规则与 hooks | 应用自己的工具权限和执行实现；不能把 `allowed_callers` 当硬权限边界 |

API 官方文档明确说，代码中的工具函数是异步 Python 函数；工具结果回到代码后可以先解析、聚合，最终代码输出才进入模型上下文。应用仍然需要处理 `tool_use`、执行真实工具并返回 `tool_result`，不是把业务 API 的权限全部交给托管容器。[API 程序化工具调用](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)

API 文档还明确，`allowed_callers` 是向模型表达调用方式的指导，并不是对所有直接调用的硬阻断。工具真正能读什么、改什么，仍由应用控制。

**Code Mode 不支持 Agent SDK 和 `claude -p`，不能据此说 Anthropic API 没有程序化工具调用。** 同样，API 方案的模型、平台支持和容器规则，也不能直接套给 Claude Code 这个实验功能。Code Mode 页面没有完整披露 JavaScript 解释器的部署位置与全部 helper 合同，本报告不把其内部实现推定为 API 的 Python 容器。

## 代码预审与逐次工具检查，都仍然存在

Code Mode 最值得认真读的是权限说明。它没有因为“都写成了 JavaScript”就统一跳过原来的工具规则。

在 **auto mode** 中，分类器在代码运行前审查整段程序；它不逐次审查里面的工具调用，也看不到运行时才算出的具体值。例如路径来自搜索输出时，预审看到的是计算路径的代码，而不是最终选中的文件。

不过，每次具体工具调用仍经过对应工具的 `deny`、`ask` 规则和 `PreToolUse` hooks，名称仍是 `Bash`、`Read`、`Edit` 等。其他权限模式则按各自规则，在实际工具需要询问时询问。代码整体通过预审，不代表所有未来调用都已获得许可。[权限检查](https://code.claude.com/docs/en/code-mode#permission-checks)

若要检查生成的 JavaScript，可以让 `PreToolUse` 匹配 `REPL`，读取 `tool_input.code`；若要检查实际命令或路径，则应在具体工具处检查。两层回答的是不同问题：程序打算怎样行动，以及这一次行动实际针对什么对象。

这也影响已有 hook 的兼容性。原文提醒，在某个目录里执行 `git push`，Bash hook 收到的可能是 `cd 'app' && git push`。只检查命令开头的规则可能漏掉后半段。官方同时强调，命令文本匹配存在固有限制，需要与真正的执行边界区分。

hook 的失败语义也有变化：Code Mode 下，某些无法启动、异常结束或超时的 `PreToolUse` 会拒绝调用；代码能后台运行时，部分 `UserPromptSubmit` hooks 还会检查代码输出，输入的 `source` 可为 `poll_event`。原有 hook 若把它当成普通用户输入处理，可能阻断返回结果。[Code Mode hook 故障说明](https://code.claude.com/docs/en/code-mode#tool-call-refused-by-a-hook)、[hooks 通用规则](https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails)

这些机制值得在试用时核对，不能为了减少弹窗，就把失败处理一律改成放行。

## 长程序运行时还能聊天，但有条件

官方区分的是两种执行状态：

- 等待代码完成时，执行最多十分钟，包含等待权限答复的时间。
- 满足后台执行条件时，可以继续与 Claude 聊天，代码最多运行两小时。

后台能力要求会话以 auto 或 `bypassPermissions` 模式启动，另有启动方式、当前模式和工具参数限制。它并不是所有 Code Mode 会话默认具备的能力；文档也区分“代码在后台继续运行”与“把整个会话搬到后台”，后者仍不支持。[长时间执行](https://code.claude.com/docs/en/code-mode#long-running-code)

“还能发消息”同样不意味着已经提交的程序会自动改变。若代码早已把文件列表、操作或后续步骤固定下来，新消息是否被采纳、旧执行是否停止，不能仅凭界面可输入来推断。需要关注实际执行状态及 Claude 后续采取的动作。这是根据程序控制流作出的分析，本文没有进行运行中改目标的实测。

这里有一处版本校准。功能页仍描述“第二段代码启动后，前一段代码失去分类器预审，可能重新询问并倒计时拒绝”的行为；**v2.1.327 CHANGELOG 已记录修复：当第二段脚本也被 auto mode 允许时，第一段脚本不应因此出现权限询问和拒绝。** 不能把手册中的描述当作本机该版本在所有情况下一定重现的行为。

同一版本还取消了“安装的 mod 对工具设 hook 就阻止启动 Code Mode”的限制，而功能页排障表仍有该条。这两处说明，实验功能的手册与版本日志需要一起看；实际试用以对应版本的启动状态和错误为准。[固定 CHANGELOG](https://github.com/anthropics/claude-code/blob/762e317bb2152f767e2821606b39492befeebf53/CHANGELOG.md)

## 目前谁能用，本机卡在哪里

截至 2026-11-18，功能页列出的主要条件为：

| 条件 | 官方要求 |
|---|---|
| 版本与安装 | 原生 Claude Code v2.1.323 或更新版本 |
| 模型 | Opus 5.5、Sonnet 5.5、Haiku 5.5、Fable 5.2 |
| 账号与路由 | Claude 订阅或 Console 账号，直接使用 Anthropic；排除网关及所列第三方云平台 |
| 使用入口 | 终端中的交互 `claude`，不支持 `-p`、SDK、VS Code 面板、Desktop 或云会话 |
| 组织设置 | 不兼容 HIPAA 配置或零数据保留等文档列出的设置 |
| Agent teams | v2.1.326 起支持；in-process 队友使用 Code Mode，split-pane 队友不使用 |

功能页还明确列出 Remote Control、Claude in Chrome、computer use 不可用，Code Mode 会话不能移到 Desktop。这会影响需要浏览器或手机远控的既有工作方式，不能只比较工具吞吐。[要求与限制](https://code.claude.com/docs/en/code-mode#requirements)

本次只读检查确认，本机原生版本为 **2.1.327**；当前用户配置中同时存在非标准 API 地址与 `ANTHROPIC_AUTH_TOKEN`。前者不符合直接 Anthropic 路由条件，后者也被排障说明列为不兼容配置。满足版本要求，不代表当前登录与路由可用。

如果以后在满足条件的环境试用，官方一次性启动方式是：

```bash
CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1 claude
```

这是文档命令，本次未执行。首次还需要 Claude Code 自己的确认；环境变量设为 `1` 不保证立即成功。项目配置不能替用户打开它。

会话恢复也与原启动状态绑定：Code Mode 会话需要保持该模式才能恢复；原本普通模式的会话，不会因恢复时加了环境变量就改为 Code Mode。因此更适合在新的试验会话观察，不能把现有会话是否会转换想当然。

## 对 EverAgent 的实际建议

这个项目最适合程序化处理的部分，是来源获取、文件定位、哈希校验、链接检查、索引和阅读器验收。它们有明确输入输出，可以批量完成后只返回异常及关键证据。

本会话的 `functions.exec` 已能用 JavaScript 组合工具调用，采用了相近思路。此次读取多份官方资料，也先保存完整来源，再返回大小、哈希及相关章节。Claude Code 的新功能可以让它在自身工具体系里使用类似方式，但具体权限与生命周期不能视作同一实现。

更值得保留的工作约定有三条：

1. **机械处理先用代码，研究判断仍读证据。** 查询日期、字段、坏链接可以筛选；翻译是否准确、嘉宾观点有无被改写，不能只看脚本摘要。
2. **返回摘要时保留失败。** 例如三个来源只有两个读取成功，应返回成功数、失败来源和原因；不能过滤异常后报告“全部完成”。任务需要所有输入时，还应在进入修改前确认输入齐全。
3. **按依赖安排执行。** 多份独立资料可以并行；编辑依赖搜索结果，提交依赖校验，推送依赖实际提交。这些步骤不能为了减少往返全部并行。多次工具调用写在同一段代码里，也不是一次可以整体回滚的事务。

假设批量读取已成功，程序筛选后的结果只剩三条异常，Claude 就可以把注意力用于解释这三条。但如果筛选规则漏掉了影响结论的信息，这种省上下文反而会掩盖问题。因此，完整来源与可回溯定位仍要保留，摘要应该服务于核对。

官方 Code Mode 页面没有给出性能基准。相关 API 文档提供了作者内部测量：一个 75-tool 项目管理基准的输入计费 token 减少约 38%，而每轮只有一两次顺序调用的 τ²-bench 反而约多花 8%。这些是 **API 程序化工具调用** 的数据，不能当作 Claude Code Mode 的实测，也不能推广成我们的报告流水线会获得同样比例。[API token 效率说明](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling#token-efficiency)

本项目已有批处理能力，当前路由又不满足 Code Mode 要求，因此没有必要仅为试用它改变工作环境。将确定性任务交给程序、为语义判断保留原文、在摘要中保留失败信息，已经能直接用于现有学习流程。以后若在独立的直接 Anthropic 环境试用，可先比较一项固定的只读任务，记录完成情况、遗漏、工具调用、耗时和计费，随后再评估是否值得用于更多工作。

## 来源与实际核对范围

完整读取了 Code Mode 官方 Markdown，16,977 字节，SHA-256 为 `5b02822f47222c425b850063555c12dd60d7ce71fc6095148b903af8c2a71bc1`；另读取 tools-reference 的相关说明、hooks 的失败规则、permission-modes 的代码预审说明，以及 API 程序化工具调用的机制、调用方字段和效率部分。CHANGELOG 固定为 `anthropics/claude-code@762e317bb2152f767e2821606b39492befeebf53`，核对 v2.1.323—2.1.327 中与该功能相关的条目。

本机检查仅包括原生版本与必要配置项是否存在，未展示配置值、启动 Code Mode、调用付费模型或修改设置。完整来源副本留在仓外。本文是官方文档研究与本地兼容性核对，没有声称完成实际 Code Mode 执行或性能复现。

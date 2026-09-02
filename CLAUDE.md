## EverAgent CLAUDE.md
## Layered on top of ~/.claude/CLAUDE.md (global rules)
## Project-specific rules only. Do not duplicate global rules.

---

## 主协议

**本项目主协议是 [AGENTS.md](./AGENTS.md)，开始任何工作前先读它。** 项目注册表与意图路由（§1/§1.5）、各子项目工作流（§2）、目录约定（§3）、全局规则（§4，含语言/搜索/提交/git 身份/兴趣确认/token 纪律）都在那里。

配套文件：

- 研究方法论（强制）：[METHODOLOGY.md](./METHODOLOGY.md)
- 提交规范与 push flow：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §B/§C
- 搜索阶梯：[docs/SEARCH.md](./docs/SEARCH.md)

本文件只记录 Claude 专属约定，不拷贝 AGENTS.md 的内容——两份协议必然漂移，以 AGENTS.md 为准。

---

## Override Rule
User instructions > AGENTS.md > this file > ~/.claude/CLAUDE.md (global).

## MCP 优先级（2026-09-02 定）

同类任务优先用智谱 GLM Coding Plan 四件套 MCP：`web-search-prime`（网页搜索）/`web-reader`（网页阅读）/`zai-mcp-server`（图像与视频分析、OCR、UI 截图转码）/`zread`（GitHub 仓库结构/文件/文档检索）；内置工具或其它 MCP 的同类能力仅在前者失败或需要第二来源时兜底。工具未安装或连接失败时静默降级，不要因此中断任务。


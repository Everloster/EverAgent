## EverAgent CLAUDE.md

<!-- BEGIN MANAGED EACLI CLAUDE BRIDGE -->
@AGENTS.md
<!-- END MANAGED EACLI CLAUDE BRIDGE -->

## Layered on top of ~/.claude/CLAUDE.md (global rules)
## Project-specific rules only. Do not duplicate global rules.

---

## 主协议

**本项目主协议是 [AGENTS.md](./AGENTS.md)。** 它只保留意图路由、context 加载和全局不变量；报告流程、研究方法与提交规则分别由下列文档负责。

配套文件：

- 研究方法论（强制）：[METHODOLOGY.md](./METHODOLOGY.md)
- 报告生产与完成定义：[docs/REPORT_WORKFLOW.md](./docs/REPORT_WORKFLOW.md)
- 跨模型质量门与模型升级策略：[docs/REPORT_QUALITY_GATE.md](./docs/REPORT_QUALITY_GATE.md)
- Context 分层与 ACE 评估：[docs/CONTEXT_ENGINEERING.md](./docs/CONTEXT_ENGINEERING.md)
- 提交规范与 push flow：[docs/PROTOCOL_COMMON.md](./docs/PROTOCOL_COMMON.md) §B/§C
- 搜索阶梯：**已退役（2026-09-13）**——联网任务一律 eacli Token Plan-first（见根 AGENTS.md 托管策略块），eacli 不可用先修 eacli

本文件只记录 Claude 专属约定，不拷贝 AGENTS.md 的内容——两份协议必然漂移，以 AGENTS.md 为准。

---

## Override Rule
User instructions > AGENTS.md > this file > ~/.claude/CLAUDE.md (global).

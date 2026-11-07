---
name: repo-research
description: "Deeply research one public GitHub repository and produce or update its seven-part Chinese report. Use only when the user explicitly asks to research, deep-dive, or create a report; a pasted repo link alone gets a brief introduction."
---

# 单仓库深度研究

## 路由

- 只有明确要求研究、深挖或出报告时执行本 skill。
- 仅给 repo 链接时，读取元数据与 README 后在对话中简要介绍，不创建报告。
- 已有报告时，先判断用户是否已经要求更新或换视角；能够从原请求确定时直接行动，只有产物选择仍关键不明时才询问。

## 工作流

1. 用 eacli `repo.public.structure/read/search` 获取仓库结构、README 与关键源码。
2. typed capability 未覆盖的 stars、forks、release、issue、PR 和提交统计，可用 `gh api` 补充并在工作记录中注明原因。
3. 依次形成四类证据：仓库元数据、真实代码、至少两个竞品、活跃度或社区量化信号。
4. 写成七部分中文报告，新增报告使用标准 frontmatter、`quality_schema: "report-v2"` 和 `quality_tier: "important"`。
5. 通过受影响报告的质量门；只把跨仓库可复用的新经验作为最小 delta 写回本 skill 或 reference。

详细命令、分支判断、薄壳包下钻、竞品核验和报告结构见 [research-method.md](./references/research-method.md)。只读取与当前仓库实际问题有关的小节。

## 完成条件

- 技术分析至少有一处 `[代码]` 证据；元数据和竞品数字有 `[API]` 证据。
- README 与代码冲突时明确写出差异。
- 临时数据位于 `/tmp/github-trending-{date}/`，不进入仓库。
- 新报告或目录元数据改变时，在仓库根目录更新索引：

```bash
go -C packages/everagent-core run ./cmd/ea-quality index --write
```

提交器自动检查受影响报告和索引；只预览时按[共享质量门](../../../docs/PROTOCOL_COMMON.md#d-报告质量门)运行，不重复检查。

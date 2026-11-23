---
name: repo-research
description: "Deeply research one public GitHub repository and produce or update a Chinese report organized around the user's questions. Use only when the user explicitly asks to research, deep-dive, or create a report; a pasted repo link alone gets a brief introduction."
---

# 单仓库深度研究

## 路由

- 只有明确要求研究、深挖或出报告时执行本 skill。
- 仅给 repo 链接时，读取元数据与 README 后在对话中简要介绍，不创建报告。
- 已有报告时，先判断用户是否已经要求更新或换视角；能够从原请求确定时直接行动，只有产物选择仍关键不明时才询问。

## 工作流

1. 用 eacli `repo.public.structure/read/search` 获取仓库结构、README 与关键源码。
2. typed capability 未覆盖的 stars、forks、release、issue、PR 和提交统计，可用 `gh api` 补充并在工作记录中注明原因。README 或源码读取失败必须作为缺口报告，不得把错误占位文本当作已读材料。
3. 按问题获取仓库元数据、真实代码及必要的社区信号；相关时比较替代方案，不凑竞品数量。
4. 用中文回答本次研究问题，结构按内容选择；元数据与草稿状态见[写作指南](../../../docs/REPORT_WORKFLOW.md)，不默认创建质量附件。
5. 核对结论与来源，说明缺口；独立复核按用户要求安排，只把可复用的新经验写回对应资料。

详细命令、分支判断、薄壳包下钻、竞品核验和报告结构见 [research-method.md](./references/research-method.md)。只读取与当前仓库实际问题有关的小节。

## 完成条件

- 技术分析至少有一处 `[代码]` 证据；元数据和竞品数字有 `[API]` 证据。
- README 与代码冲突时明确写出差异。
- 临时数据位于 `/tmp/github-trending-{date}/`，不进入仓库。
- 新报告或目录元数据改变时，在仓库根目录更新索引：

```bash
scripts/edocs.sh index --write
```

索引按需要显式更新，不作为提交前置；不要为工具迁移自动重生成报告或索引正文。该薄入口要求预先安装eacli >=11.0.0，固定转发`eacli docs index --repo-root ROOT --write`，ROOT绑定公开脚本位置；缺失/非法/旧版本明确失败，不自动build/install或寻找私仓。提交器保留policy Author、当前真实模型/明确有效声明Committer与新增公开内容保护；来源审查或严格评分工具仅在明确需要时使用。

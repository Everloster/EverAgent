# GitHub 开源仓库研究

通过真实代码、公开 API 与项目文档理解开源项目，积累单仓深研和 trending 趋势报告。关注技术设计与适用边界，不只复述 README 或 Stars 排名。

## 阅读与研究入口

| 想看什么 | 入口 |
|---|---|
| 已有单仓深研、日周月汇总 | [报告目录](./reports/) |
| 单个仓库的架构与实现 | [repo-research](./skills/repo-research/SKILL.md) |
| 日、周、月 trending | [trending-analyzer](./skills/trending-analyzer/SKILL.md) |
| 报告结构参考 | [报告模板](./assets/report_template.md) |

仅发送仓库链接时默认口头介绍，不落文件；明确要求深挖、研究或报告时再展开。已有报告且要求更新时续写原报告，保留其视角和证据时点。

## 研究特点

- 先通过 eacli `repo.public.*` 获取仓库结构、文件与文档；未覆盖的精确元数据按领域协议最小补充。
- 技术判断回到代码；README 与实现不一致时指出差异。结论区分代码、API、文档、外部资料与推测。
- Stars、版本、issue 和 release 等数字注明查询时点；历史榜单不代表当前排名。
- 报告统一保存在 `reports/`，不在首页手工维护篇数或第二份全量库存。

## 本地辅助工具

已有[辅助脚本](./scripts/)处理榜单、元数据和报告草稿，[测试](./tests/)验证脚本行为；使用边界与取数顺序由 [AGENTS.md](./AGENTS.md) 和对应 skill 维护。

在本领域目录安装仓库声明的开发依赖后，可运行脚本自检：

```bash
ruff check scripts tests
pytest -q
```

这些检查不等于报告内容通过复核。长期报告的证据与完成标准见[报告工作流](../docs/REPORT_WORKFLOW.md)和[质量门](../docs/REPORT_QUALITY_GATE.md)。

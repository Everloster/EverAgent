# web-surfing — 执行协议

> 公开网站检索、抓取与整理。联网、Personal Context 和提交规则由根 `AGENTS.md` 负责；本文件只保留站点路由与访问边界。

## 任务路由

| 意图 | 默认动作 | 产物 |
|---|---|---|
| 查一个事实、页面或价格 | 直接核验并回答 | 不落文件 |
| 抓公开清单、跨页整理 | 先查复用，再抓取 | 有长期价值时写 `reports/` |
| 同一站点反复使用或访问方式稳定 | 更新 `skills/site-{name}/SKILL.md` | 最小可复用 delta |
| AI 新闻日报 | 使用 [ai-news-readability](./skills/ai-news-readability/SKILL.md) | 日报 |

开始前先检查已有 `site-*` skill 和可用 adapter。通用 opencli 操作只在需要浏览器或登录态时读取 [opencli-playbook](./skills/opencli-playbook.md)，不要把整份手册默认加载。

## 工具选择

- 公开搜索、网页读取与结构化数据优先走根协议规定的 eacli typed capability。
- 需要已有 Chrome 登录态、页面交互或 typed capability 未覆盖时，使用 opencli adapter；仍无覆盖才使用浏览器直驱。
- 使用浏览器能力前运行 `opencli doctor`；工具输出使用 JSON 或 YAML。

## 边界

- 默认只读公开数据。发帖、评论、点赞、下单等外部写入必须有用户明确授权。
- 不批量下载盗版或付费墙内容。
- 批量遍历保持低频；遇验证码或限速停止并报告。
- 中间数据放 `/tmp/web-surfing-{date}/`，不得提交。
- 所有动态事实写明来源与数据时点；评分、价格和库存不得从记忆填写。

## 报告合同

需要归档时遵守根 [REPORT_WORKFLOW](../docs/REPORT_WORKFLOW.md)，新增报告使用标准 frontmatter 与 `quality_schema: "report-v1"`。报告应说明查询范围、筛选口径、时间点、来源和未覆盖部分。

完成后运行：

```bash
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

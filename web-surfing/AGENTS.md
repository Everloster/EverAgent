# web-surfing — 领域协议

> 公开网站检索、抓取与整理。

## 路由

| 意图 | 默认入口 | 产物 |
|---|---|---|
| 单一事实、页面或价格 | eacli typed capability | 直接答复 |
| 公开清单或跨页整理 | 已有 `site-*` playbook；无匹配再选工具 | 有长期价值时归档 |
| AI 新闻日报 | [ai-news-readability](./skills/ai-news-readability/SKILL.md) | 日报 |
| 需要登录态或页面交互 | 可用 adapter；必要时读 [opencli-playbook](./skills/opencli-playbook.md) | 按任务交付 |

归档报告时使用根级 [`everagent-report`](../.agents/skills/everagent-report/SKILL.md)。不要为了可能复用而预先读取所有站点 playbook。

## 访问边界

- 默认只读公开数据；发帖、评论、点赞、下单等外部写入需要用户授权。
- 不批量下载盗版或付费墙内容；批量遍历保持低频，遇验证码或限速停止并报告。
- 动态事实写明来源与数据时点；评分、价格和库存不得从记忆填写。
- 中间数据放 `/tmp/web-surfing-{date}/`，不得提交。

站点命令、报告字段和完成检查由选中的 playbook 与根级工作流拥有。

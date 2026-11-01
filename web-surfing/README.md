# 公开网站调研

检索公开资料、追踪资讯、跨页整理清单，并把有长期价值的发现保存为可追溯报告。常用站点的访问经验按需沉淀，不为一次查询建立额外流程。

## 阅读与使用入口

| 想做什么 | 入口 |
|---|---|
| 阅读已有调研与 AI 日报 | [报告目录](./reports/) |
| 制作或阅读 AI 新闻日报 | [日报可读性方法](./skills/ai-news-readability/SKILL.md) |
| 追踪官方技术博客 | [技术博客雷达](./skills/ai-tech-blog-radar/SKILL.md) · [渠道注册表](./sources/ai-tech-blogs.json) |
| 查看站点访问经验 | [SeedHub](./skills/site-seeduck/SKILL.md) · [B 站](./skills/site-bilibili/SKILL.md) |
| 需要登录态或页面交互 | [opencli 手册](./skills/opencli-playbook.md) |

日报、评分、价格等都是有时点的信息；旧报告保留当时语境，不表示已经重新核验。

## 工作方式

先定位已有报告和站点经验，再通过 eacli 的 typed capability 选择公开检索、网页读取等能力。需要登录态或页面交互时再按领域协议选择 adapter 或 opencli，不把浏览器直驱作为所有任务的默认入口。

单一事实查询通常直接答复；跨页整理按用户需要交付清单，有长期价值时再归档。已存在的站点经验优先复用，反复出现的需求才沉淀为专用 playbook。

## 访问边界

默认只读公开数据；发帖、评论、点赞、下单等外部写入须有明确授权。不批量下载盗版或付费墙内容；批量遍历保持低频，遇验证码或限速停止。

执行规则见 [AGENTS.md](./AGENTS.md)，归档标准见[报告工作流](../docs/REPORT_WORKFLOW.md)。这里不维护设备安装版本、站点数量或重复的报告库存。

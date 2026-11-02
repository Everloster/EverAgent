---
name: ai-tech-blog-radar
description: 查询顶尖 AI 厂商、实验室与官方工程项目的技术博客近期更新，或增删改查和回测这份渠道清单；用户说“顶尖技术博客最近有什么更新”“AI 技术博客更新”“更新技术博客渠道”时使用。普通 AI 新闻日报、个人博客调研和单篇文章深度分析不使用。
---

# 顶尖 AI 技术博客雷达

## 两种模式

### 查最近更新

固定阅读入口是 [`../../TECH_BLOG_UPDATES.md`](../../TECH_BLOG_UPDATES.md)。每次查询都更新这份清单，再向用户汇报新增内容；先读它的上次检查日期、已有条目和获取缺口。

运行（中间结果放 `/tmp`）：

```bash
python3 web-surfing/skills/ai-tech-blog-radar/scripts/radar.py \
  updates --days 7 --tier all --limit 2000 --per-source 1000 --format json

# 只看 Agent/Harness 或推理系统
python3 web-surfing/skills/ai-tech-blog-radar/scripts/radar.py \
  updates --days 7 --topic agent_harness --topic inference_systems --format json
```

- 用户给了时间范围时换成 `--days N` 或 `--since YYYY-MM-DD`；未指定且距上次检查已超过一周时，从上次检查前两天开始补查，避免断档。用户要求存量或全列时，不使用默认每源 3 条的精选上限。
- RSS 可能只保留最近几篇，搜索也不保证完整。补历史时检查每个渠道实际覆盖的日期，必要时回读官方归档或分月搜索；上调输出上限不等于补齐历史。
- 补档时复核被关键词排除的条目，特别是中文、日文标题与只含产品名的发布；有技术内容才收录，不把活动通知、招聘和促销混入清单。
- 搜索给出的日期只是线索，可能是抓取时间或相关页面日期；以原文发布时间、官方归档或 RSS 的发布日期为准，冲突未解决时不写成近期新发布。
- 按原文 URL 合并清单，保留旧条目、人工导读和报告链接；同文的跟踪参数、尾斜杠、中英文版本不重复计数。短时间窗查询不能覆盖掉历史库存。
- 清单按月份倒序、厂商分组，每篇保留发布日期、原文链接、简短中文导读和学习状态。仅凭标题或摘要时不写未经阅读的技术结论；日期未核实的条目单列，不计入时间窗数量。
- 学习状态以本仓对应报告为准：主题一致且报告完成才标“已学习”并给链接；草稿标“进行中”，只有相关背景材料标“相关报告”。日报提及、参考文献引用和主题相似都不等于做过该篇学习任务。未找到对应报告写“未做”；本次新完成的报告也要更新回清单。
- 更新检查日期、覆盖时间范围、文章数量和渠道获取情况。获取失败不能写成“没有更新”，未覆盖完整的历史要明确说明；保留待补缺口供下次继续。
- 对话中简要介绍值得看的新增文章，并附固定清单入口；用户要“全部罗列”时，清单须包含全部已核实条目，已学习的也保留。
- 默认不创建报告，也不自动启动深度研究。用户选中某篇后，再路由到 `ai-learning` 做学习任务。

### 维护渠道

```bash
SCRIPT=web-surfing/skills/ai-tech-blog-radar/scripts/radar.py

python3 "$SCRIPT" channels list --format md
python3 "$SCRIPT" channels get openai-developer
python3 "$SCRIPT" channels evaluate --days 14 --format md
python3 "$SCRIPT" channels update deepseek --set tier=must
python3 "$SCRIPT" channels validate --live --format json
python3 "$SCRIPT" channels add --file /tmp/new-source.json
python3 "$SCRIPT" channels remove source-id --yes
```

- 用户明确指定新增、修改、停用或删除时直接执行。
- 用户只说“更新一下渠道”时，先做 live validate，再研究失效源与新候选；只有一手内容质量或订阅可用性发生实际变化才修改。
- 新渠道先用 `channels evaluate` 回测 14 天，检查原始条数、筛选率和代表文章；通过后再决定 `must/watch`，不要只凭品牌知名度升级。
- `must` 表示默认进入更新雷达；`watch` 表示需经过技术关键词过滤。不要为凑数量扩充名单。
- 修改注册表后运行非联网 `channels validate`。

渠道唯一事实源是 [`../../sources/ai-tech-blogs.json`](../../sources/ai-tech-blogs.json)。调整字段或抓取适配器时再读 [channel-schema](./references/channel-schema.md)。来源筛选依据见 [`../../reports/ai-vendor-technical-sources-2026-10-20.md`](../../reports/ai-vendor-technical-sources-2026-10-20.md)。

## 访问与证据边界

- 普通网页搜索与读取由脚本通过 eacli Token Plan 执行。
- RSS/sitemap 先走 eacli `web.read`；只有内容被截断、XML 结构丢失或访问失败时，才降级到只读 HTTP 解析，并在输出中记录原因。主发现通道失败时，按注册表中的备用通道降级。
- 只收厂商、实验室、官方开源项目和一手工程团队。个人、媒体、Newsletter 和通用 AI 新闻走其它任务。
- Sitemap `lastmod` 只记录为页面更新时间，不能冒充文章发布日期；搜索结果缺日期时，只有显式启用正文回读并核验出日期后才进入时间窗。
- 厂商 benchmark 属厂商自报；更新汇报只说明“官方称”，不能写成独立验证结论。

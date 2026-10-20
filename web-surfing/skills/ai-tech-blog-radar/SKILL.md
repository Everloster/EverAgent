---
name: ai-tech-blog-radar
description: 查询顶尖 AI 厂商与实验室官方技术博客的近期更新，或增删改查这份渠道清单；用户说“顶尖技术博客最近有什么更新”“AI 技术博客更新”“更新技术博客渠道”时使用。普通 AI 新闻日报、个人博客调研和单篇文章深度分析不使用。
---

# 顶尖 AI 技术博客雷达

## 两种模式

### 查最近更新

运行：

```bash
python3 web-surfing/skills/ai-tech-blog-radar/scripts/radar.py \
  updates --days 7 --format json
```

- 用户给了时间范围时换成 `--days N` 或 `--since YYYY-MM-DD`。
- 直接用中文汇报，按“值得重点看 / 重要发布 / 其它技术更新”分组；每条给标题、厂商、日期、链接和一句价值判断。
- 明确列出获取失败的渠道，不能把部分成功说成全量完成。
- 默认不创建报告，也不自动启动深度研究。用户选中某篇后，再路由到 `ai-learning` 做学习任务。

### 维护渠道

```bash
SCRIPT=web-surfing/skills/ai-tech-blog-radar/scripts/radar.py

python3 "$SCRIPT" channels list --format md
python3 "$SCRIPT" channels get openai-developer
python3 "$SCRIPT" channels update deepseek --set tier=must
python3 "$SCRIPT" channels validate --live --format json
python3 "$SCRIPT" channels add --file /tmp/new-source.json
python3 "$SCRIPT" channels remove source-id --yes
```

- 用户明确指定新增、修改、停用或删除时直接执行。
- 用户只说“更新一下渠道”时，先做 live validate，再研究失效源与新候选；只有一手内容质量或订阅可用性发生实际变化才修改。
- `must` 表示默认进入更新雷达；`watch` 表示需经过技术关键词过滤。不要为凑数量扩充名单。
- 修改注册表后运行非联网 `channels validate`。

渠道唯一事实源是 [`../../sources/ai-tech-blogs.json`](../../sources/ai-tech-blogs.json)。调整字段或抓取适配器时再读 [channel-schema](./references/channel-schema.md)。来源筛选依据见 [`../../reports/ai-vendor-technical-sources-2026-10-20.md`](../../reports/ai-vendor-technical-sources-2026-10-20.md)。

## 访问与证据边界

- 普通网页搜索与读取由脚本通过 eacli Token Plan 执行。
- RSS/sitemap 先走 eacli `web.read`；只有内容被截断、XML 结构丢失或访问失败时，才降级到只读 HTTP 解析，并在输出中记录原因。
- 只收厂商或实验室官方源。个人、媒体、Newsletter 和通用 AI 新闻走其它任务。
- 厂商 benchmark 属厂商自报；更新汇报只说明“官方称”，不能写成独立验证结论。

---
name: ai-tech-podcast-radar
description: 查询中英文 SOTA AI 技术播客近期更新，或维护和评估这份渠道清单；用户说“顶尖技术播客最近有什么更新”“SOTA AI 播客”“更新技术播客渠道”时使用。普通小宇宙个人精选、单集转写和报告写作不使用。
---

# SOTA AI 技术播客雷达

## 查最近更新

```bash
python3 podcast-learning/skills/ai-tech-podcast-radar/scripts/radar.py \
  updates --days 7 --format json

# 只看 Agent / Harness 和推理系统
python3 podcast-learning/skills/ai-tech-podcast-radar/scripts/radar.py \
  updates --days 14 --topic agent_engineering --topic systems_infra --format json
```

- 用中文按“优先深挖 / 前沿信号 / 其它相关更新”汇报，给出节目、日期、时长、链接和入选理由。
- 默认排除已经有学习报告的单集；需要完整更新流时加 `--include-studied`。
- 明确报告成功、降级和失败渠道。Apple Podcasts 只作为 RSS 不可达时的元数据备用入口。
- 用户选中单集后，再按 `podcast-learning` 的转写和报告流程执行；雷达本身不自动下载音频或写报告。

## 维护渠道

```bash
SCRIPT=podcast-learning/skills/ai-tech-podcast-radar/scripts/radar.py

python3 "$SCRIPT" channels list --format md
python3 "$SCRIPT" channels get latent-space
python3 "$SCRIPT" channels evaluate --days 90 --format md
python3 "$SCRIPT" channels validate --live --format json
python3 "$SCRIPT" channels update gradient-podcast --set tier=core
python3 "$SCRIPT" channels export-opml --output /tmp/sota-ai-podcasts.opml
```

- `core` 是默认高优先级主干；`watch` 需要单集技术主题和深度信号通过筛选。
- 新渠道先回测 90 天，观察活跃度、相关率和代表单集，再决定是否进入 `core`。
- 不因品牌知名度收录；长期无更新、持续低相关或只做新闻搬运的渠道应降级或移除。

唯一事实源是 [`../../sources/ai-tech-podcasts.json`](../../sources/ai-tech-podcasts.json)。现有 [`../../wiki/curated-podcasts.opml`](../../wiki/curated-podcasts.opml) 仍是个人综合精选，两者用途不同。

## 获取边界

- RSS 先走 eacli `web.read`；内容被清洗、截断或访问失败时，降级到只读 HTTP XML，再降级到 Apple Podcasts 节目页。输出必须记录降级。
- Apple 页面没有稳定单集 URL 时，链接回节目页并标记 `apple_page`，后续学习任务需重新解析单集来源。
- Apple 的日期可能是重发或列表更新时间；已有报告时按报告文件名恢复首发日，未学习单集进入“优先深挖”前必须再核对官方单集页的原始发布日期。
- 厂商、实验室和投资机构节目中的自报数据按一手主张处理，不能当作独立验证结论。

# AI 日报可读性

> 只用于 AI 新闻日报的阅读结构与呈现。普通网页调研、清单或单篇文章报告不使用本 playbook。

## 固定输入

在原有 AIHOT、GitHub Trending、AI Digest、Hacker News 基础上，每期必须运行：

```bash
python3 web-surfing/skills/ai-tech-blog-radar/scripts/radar.py \
  updates --days 2 --limit 12 --format json
```

从结果中选 0–5 条当天或前一日发布、尚未在上一期日报出现的厂商、实验室或官方工程项目技术更新。正文固定保留“顶尖技术博客更新”一节；没有命中时明确写“本期未检出新的高价值技术文”。只做一两句导读，不在日报里展开完整学习报告。若 `sources_degraded > 0`，页脚必须列出降级源，不能把备用通道接管描述成全量正常。

## 路由

- 设计页眉、TL;DR、头条、Trending、简讯、趋势与页脚时，按需读取 [layout-guide §一–§二](./references/layout-guide.md#一十条硬约束格式级)。
- 处理证据标签、脚注和不确定性时读取 [layout-guide §三](./references/layout-guide.md#三证据纪律保留但形式迁移)。
- 需要风格校准或交稿检查时读取 [layout-guide §四–§五](./references/layout-guide.md#四模型风格约束给-agent-的硬行文规则)。
- 只有版式难以判断时才查看 [示例](./example-2026-10-08.md)。

## 目标

读者应在 30 秒内判断哪些内容值得继续读。证据完整保留，但与正文分层呈现；同一事件只讲一次，不为满足模板重复扩写。

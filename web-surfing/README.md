# 🌐 web-surfing — Agent 帮我上网

> **项目目标：Agent 帮我上网。** 以 `opencli` 为主力工具，满足各种上网冲浪需求
> （抓片单、看热搜、追动态、查资料、整理清单……），并把常用站点沉淀成可复用技能。
>
> **AI 使用本项目？** → 读 [AGENTS.md](./AGENTS.md)（唯一执行协议）。本文件供人类阅读。

---

## 一句话工作流

```
我："帮我上 X 网站看看 / 抓一下 Y / 整理个清单"
  ↓
Agent：① 先查复用（本项目沉淀过？opencli 有适配器？agent-reach 覆盖？）
       ② 有就复用，没有就 opencli browser 直驱
       ③ 只读公开数据，产出清单/报告
       ④ 这站以后还会来 → 沉淀成 skills/site-{name}/
```

**核心理念：先查复用，再上网。** 别每次从零摸索；常访问的站点自行迭代沉淀。

---

## 目录

```
web-surfing/
├── AGENTS.md                    # 唯一执行协议（三件事 + 查复用铁律 + 合规红线）
├── README.md                    # 本文件
├── reports/                     # 上网任务产出
│   └── kdrama-top10-2024-2026.md   # 首个报告：SeedHub 韩剧 Top10
├── knowledge/                   # 可选：跨任务索引
└── skills/
    ├── opencli-playbook.md      # opencli 通用手册（主力工具）
    └── site-seeduck/SKILL.md    # SeedHub 站点沉淀（URL/命令/坑）
```

## 已沉淀

| 类型 | 名称 | 说明 |
|------|------|------|
| 通用手册 | `skills/opencli-playbook.md` | opencli 三大支柱 + 173 站速查 + 浏览器直驱模板 |
| 站点技能 | `skills/site-seeduck/` | SeedHub 影视站：URL 结构 / 语言年份 tagId / 翻页解析脚本 |
| 报告 | `reports/kdrama-top10-2024-2026.md` | 2024–2026 韩剧豆瓣评分 Top10（含链接） |

## 主力工具：opencli

本机 opencli v1.8.6，把 173+ 网站 / 桌面 App / 外部 CLI 变成统一 `opencli <site> <command>`，复用 Chrome 登录态。详见 [skills/opencli-playbook.md](./skills/opencli-playbook.md)。

## 合规红线

只读公开数据做检索整理；**不批量下载盗版/付费墙资源**；不做写操作除非明确授权；批量遍历低频防封。

# web-surfing — 执行协议

> **项目使命：Agent 帮我上网。** 用 `opencli` 为主力工具，满足我各种上网冲浪需求
> （抓片单/看热搜/追动态/查资料/整理清单……），并把常用站点沉淀成可复用技能。
> 由 EverAgent 根 `AGENTS.md` 的 E 类路由进入（"帮我上网/上 X 网站看看/抓一下 X"）。
> 自包含：读本文件 + 根 `METHODOLOGY.md` 即可独立工作。

---

## §0 项目使命（三件事）

| # | 事 | 触发 | 产出 |
|---|----|------|------|
| A | **一次上网任务** | "帮我上 X 网站看看 / 抓一下 X / 整理个清单" | `reports/{slug}.md`（有长期价值时）或直接对话答复 |
| B | **沉淀站点技能** | 某站点访问 ≥2 次、或摸清了它的取数姿势 | `skills/site-{name}/SKILL.md`（URL 结构 + 取数命令 + 坑） |
| C | **迭代通用上网方法** | 每次做完 A/B 后 | 折回 `skills/opencli-playbook.md` 或本文件 §3 |

**核心原则：先查复用，再上网。** 每次上网前**必须先看 opencli 有没有对应工具 / 本项目有没有沉淀过该站点技能**，能复用就复用，别每次从零摸索。

---

## §1 铁律：帮上网之前先"查复用"

```
我：帮我上 X 网站 / 抓一下 Y
  ↓
① 查本项目沉淀     → ls skills/site-*/  有没有这个站的 SKILL.md？有则读它，按记录的 URL/命令直接干
  ↓ 没有
② 查 opencli 适配器 → opencli list -f json | 过滤站点名  有没有现成适配器？
                     · 有 → 直接用 opencli <site> <command>（最省事、最抗封）
                     · 无 → 走浏览器直驱（opencli browser <session> open/extract/...）
  ↓
③ 顺带查 agent-reach → 若属于它覆盖的 13 平台（小红书/Twitter/B站/Reddit/YouTube/播客/RSS…），
                       优先用 agent-reach（见根 docs/SEARCH.md 档位3），它对这些平台路由更成熟
  ↓
④ 干活 → 只读公开数据，标注证据；批量抓要低频加延时
  ↓
⑤ 沉淀（事B/C）→ 若这个站以后还会来，把 URL 结构 + 有效命令写进 skills/site-{name}/SKILL.md
```

> **判断"要不要沉淀"**：这个站我以后还会再来吗？会 → 建/更新 `skills/site-{name}/`。只来一次 → 结果写报告即可，不建技能。

---

## §2 opencli 快速手册（主力工具）

完整地图见 `skills/opencli-playbook.md`。最常用的：

```bash
# 0. 用浏览器直驱前先确认桥接正常（cookie/ui/browser 类命令需要）
opencli doctor

# 1. 查有没有现成适配器（173+ 站点，source of truth）
opencli list -f json | python3 -c "import json,sys; d=json.load(sys.stdin); d=d if isinstance(d,list) else next(v for v in d.values() if isinstance(v,list)); print(sorted({c['site'] for c in d if '关键词' in c['site']}))"
opencli <site> --help          # 看某站命令

# 2. 有适配器 → 直接用（agent 一律 -f json / -f yaml）
opencli xiaohongshu search "关键词" -f yaml
opencli weibo hot -f json

# 3. 没适配器 → 浏览器直驱（session 名自取，如 sd）
opencli browser <session> open "https://example.com/page"
opencli browser <session> extract          # 抓渲染后结构化文本
opencli browser <session> find/click/type/select/network/screenshot ...
```

**策略标签**（`opencli list` 里每条命令带）：`PUBLIC`=纯 HTTP 无需浏览器；`COOKIE/UI/INTERCEPT`=需 Chrome 登录 + OpenCLI 扩展（复用登录态，不用重新登）；`LOCAL`=本地端点。

**通用规则**：agent 用一律加 `-f json`；`cookie/ui` 类命令用前先在 Chrome 登录该站；失败时 `--trace retain-on-failure` 拿诊断（详见 `opencli-autofix` skill）。

---

## §3 环境与边界

- **桥接**：`opencli doctor` 三项（Daemon / Extension / Connectivity）须绿，浏览器类命令才可靠。
- **登录态**：opencli 复用你 Chrome 的实时登录态，`auth status` 显示 not_logged_in 属正常——用某站前先在浏览器登录即可，不用重装。
- **临时数据**：中间产物放 `/tmp/web-surfing-{date}/`，完成清理，禁止提交。
- **报告输出**：默认 `./reports/`。

### 合规红线（硬边界）
1. **只读公开数据**（片单/热搜/评分/公开帖文等），做检索、整理、清单。
2. **不批量抓取/自动化下载盗版资源**（影视下载、付费墙内容等）；索引元数据 OK，下载分发 NOT OK。
3. **不做写操作**（发帖/评论/点赞/下单）除非我明确要求且授权。
4. **防封**：批量遍历低频、加 `sleep`；触发验证码/限速就停，别硬刚。
5. 其余共享安全规则见根 [`docs/PROTOCOL_COMMON.md`](../docs/PROTOCOL_COMMON.md) §A（不伪装身份、不提交密钥、不编造）。

---

## §4 目录结构

```
web-surfing/
├── AGENTS.md                    # 本文件（唯一协议）
├── README.md                    # 人类导航 + quickstart
├── reports/                     # 上网任务产出（有长期价值的清单/报告）
├── knowledge/                   # 可选：跨任务的索引 / 站点清单
└── skills/
    ├── opencli-playbook.md      # opencli 通用手册（三大支柱 + 常用命令）
    └── site-{name}/SKILL.md     # 各站点沉淀（URL 结构 + 取数命令 + 坑），如 site-seeduck/
```

**写入权限**：Agent 写 `reports/`、`skills/`、`knowledge/`。

---

## §5 报告命名

```
reports/{slug}.md    # slug 用英文小写短词描述任务，如 kdrama-top10-2024-2026.md
```
报告页脚统一：
```
---
*报告生成时间: YYYY-MM-DD*
*数据来源: {站点} via opencli browser（公开元数据）*
*说明: 评分为站点标注值，未逐条回查原始来源；以官方链接为准。*
```

---

## §6 提交规范

```bash
git add web-surfing/
git commit -m "[web-surfing] {任务}: {描述}"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> git 身份默认 `coco-openrouter-3o`（见根 `AGENTS.md`）。交流/报告/commit 一律中文。合并冲突无法自动解决时：停止，通知我仲裁。

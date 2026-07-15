# opencli-playbook — opencli 通用上网手册

> web-surfing 项目的主力工具手册。**每次上网前先读 §1「查复用」**，再决定用哪条路径。
> 本机版本：opencli v1.8.6（上游 [jackwener/OpenCLI](https://github.com/jackwener/OpenCLI)，与最新 Release 一致）。

---

## §0 opencli 是什么

**把任何网站 / Electron 桌面 App / 外部 CLI 变成统一的 `opencli <site> <command>` 接口**，让 agent 直接驱动，不靠截图识别。复用你 **Chrome 里已登录的浏览器**，比裸 `curl` 抗封。

本机实测：**173 站点、1275 条命令**（每周在涨，别背清单，用 `opencli list -f json` 现查）。

### 三大支柱
1. **适配器命令** `opencli <site> <command>` — 现成封装（173 站）。
2. **浏览器直驱** `opencli browser <session> <cmd>` — 没适配器时开真实 Chrome 抓（open/extract/click/type/find/network/screenshot…）。
3. **外部 CLI 透传** `opencli gh / docker / lark-cli …` — 统一入口调外部工具。

---

## §1 查复用（上网前必做）

```bash
# ① 先查本项目沉淀：这个站以前来过吗？
ls web-surfing/skills/site-*/          # 有 site-{name}/SKILL.md 就直接读它照着干

# ② 查 opencli 有没有现成适配器
opencli list | grep -i <站点关键词>
# 或机器可读精确查：
opencli list -f json | python3 -c "import json,sys; d=json.load(sys.stdin); d=d if isinstance(d,list) else next(v for v in d.values() if isinstance(v,list)); print(sorted({c['site'] for c in d if '关键词' in c['site'].lower()}))"

# ③ 若属于 agent-reach 的 13 平台（小红书/Twitter/B站/Reddit/YouTube/播客/V2EX/RSS/雪球/LinkedIn），
#    优先用 agent-reach（见根 docs/SEARCH.md），它对这些平台路由更成熟
```

**决策**：有沉淀 → 照沉淀干；有适配器 → 用适配器；都没有 → 浏览器直驱 + 干完沉淀。

---

## §2 有适配器：直接用

```bash
opencli <site> --help              # 看这个站有哪些命令
opencli <site> <command> --help    # 看某命令的参数
opencli <site> <command> [args] -f json   # agent 一律 -f json
```

**已覆盖站点速查**（部分，`opencli list` 为准）：
- 社交内容：微博 weibo、小红书 xiaohongshu/rednote、知乎 zhihu、抖音 douyin、B站 bilibili、即刻 jike、贴吧 tieba、豆瓣 douban、Twitter、Reddit、YouTube、Instagram、TikTok、Bluesky、Substack、Medium
- 电商生活：淘宝 taobao、京东 jd、1688、闲鱼 xianyu、大众点评 dianping、携程 ctrip、Amazon、Steam、Booking
- 学术论文：arxiv、pubmed、google-scholar、cnki(知网)、万方 wanfang、semanticscholar、openreview、dblp
- 开发：github、gitee、npm、pypi、crates、maven、dockerhub、homebrew、stackoverflow、hackernews、v2ex、linux-do
- AI 产品：chatgpt、claude、gemini、deepseek、kimi、doubao、qwen(通义)、yuanbao(元宝)、grok、suno、notebooklm
- 财经：xueqiu(雪球)、eastmoney(东方财富)、binance、coingecko、yahoo-finance
- 播客媒体：xiaoyuzhou(小宇宙)、spotify、apple-podcasts、imdb、bbc
- 求职：linkedin、boss、51job、maimai(脉脉)、indeed、upwork
- 工具公共：12306、wikipedia、google/brave/duckduckgo 搜索、weread(微信读书)、weixin(公众号)

### 策略标签（决定要不要浏览器）
| 标签 | 需要什么 |
|------|---------|
| `PUBLIC` | 什么都不用，纯 HTTP |
| `COOKIE` | Chrome 登录目标站 + OpenCLI 扩展，复用登录态 |
| `INTERCEPT` | 同上 + 开自动化窗口抓签名请求 |
| `UI` | 同上 + 完整 DOM 操作 |
| `LOCAL` | 本地/开发端点，无需浏览器 |

---

## §3 没适配器：浏览器直驱

**必须先 `opencli doctor` 确认桥接绿。** session 名自取（如 `sd`），后续命令复用同名。

```bash
opencli browser <session> open "https://example.com/page"   # 打开页面，返回 page id
opencli browser <session> extract                            # 抓渲染后结构化文本（markdown-ish）
opencli browser <session> extract --selector "<css>"         # 只抓某区域
opencli browser <session> find "<text/selector>"             # 定位元素
opencli browser <session> click / type / select / fill       # 交互
opencli browser <session> network                            # 看页面网络请求（找后端 API）
opencli browser <session> screenshot                         # 截图
opencli browser <session> state                              # 当前页面状态
```

### 翻页遍历模板（实测，本项目韩剧任务用的就是这套）
```bash
for p in 1 2 3 4 5 6; do
  opencli browser sd open "https://站点/list/?page=${p}&order=score" >/dev/null 2>&1
  sleep 1                                    # 低频，防封
  opencli browser sd extract 2>/dev/null
done | python3 -c "
import json,sys,re
raw=sys.stdin.read()
objs=re.findall(r'\{.*?\"content\":.*?\n\}', raw, re.S)   # 多个 JSON 拼接，逐个解析
seen=set()
for o in objs:
    try: d=json.loads(o)
    except: continue
    # 用正则从 d['content'] 里抽条目，去重(seen)、过滤、排序
"
```
**要点**：`extract` 返回 `{url,title,content,...}` JSON，`content` 是 markdown 化的页面文本；多页拼接时用 `re.findall` 切 JSON 对象再逐个 `json.loads`，用 URL 去重。

---

## §4 外部 CLI 透传

```bash
opencli external list          # 看可用外部 CLI（本机已装 docker/gh/lark-cli）
opencli gh <...>               # 等价 gh
opencli lark-cli <...>         # 飞书
```

---

## §5 自愈与排障

- 命令失败：`opencli <site> <cmd> --trace retain-on-failure`，错误里带 trace 指向 `summary.md`，按 `opencli-autofix` skill 修（最多 3 轮）。
- `auth status` 全 not_logged_in 是**正常**的——opencli 用 Chrome 实时登录态，用某站前在浏览器登录即可。
- 版本检查：`opencli doctor` 会报版本；升级 `npm install -g @jackwener/opencli`。

---

## §6 通用规则

- agent 用一律 `-f json`（或 `-f yaml`）。
- 只读公开数据；不做写操作除非明确授权；不批量下载盗版/付费墙资源。
- 批量遍历低频加 `sleep`；触发验证码/限速就停。
- 中间数据放 `/tmp/`，别提交。

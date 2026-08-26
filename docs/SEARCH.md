# 搜索阶梯（Search Ladder）

> 全局搜索/查资料方法。查东西时**从最省钱有效的档位开始，不够再往上爬**，而不是一上来就动用重工具。
> 被根 [AGENTS.md](../AGENTS.md) §4 引用；任何领域、任何任务都适用。
> 2026-07-26 全面修订：按实机实测重排（mcporter 盘点 + 逐档验证），新增 exa 档与抓取 fallback 链。
> 2026-08-12 订正：本文只定义「能力阶梯与用法」，不再把某台设备的已安装状态写成全局事实；实际可用性以私有仓对应设备档案为准。

---

## 一、先判断查什么，再选档位

| 你要的东西 | 直接去 |
|-----------|--------|
| 代码库里的事实（某函数在哪、某配置值） | **本地工具**：Grep / Glob / Read，别联网 |
| 一个明确网址的内容 | **抓取**：FetchURL；失败走 [§三 fallback 链](#三抓取-fallback-链借-openclaw-设计) |
| 快事实 + 出处 + 时效 | **档位 1**：llm Gemini websearch |
| 搜索列表（有哪些来源） | **档位 2**：WebSearch / exa |
| 难抓的页（JS 重/反爬）、批量、监控 | **档位 3**：firecrawl MCP |
| 登录态、复杂交互、多轮操作 | **档位 4**：opencli browser / agent-reach |
| 结构化数据（金融/论文/企业） | **专项**：kimi-datasource / firecrawl research |

---

## 二、搜索阶梯（从下往上爬，够用就停）

### 档位 0 · 本地优先（零成本）
先问：这真的需要联网吗？代码/文件里的事用 Grep/Glob/Read。

### 档位 1 · llm + Gemini websearch（快事实首选）
设备已配置 `llm` + `llm-gemini` 与个人 API Key 时，这一档**轻量、带 Google 实时接地、给结论快**。执行前先查对应设备档案，不得因本文有示例命令就假定本机已配好凭据。

```bash
# 联网搜索 + 事实问答（google_search grounding）
llm -m gemini-2.5-flash -o google_search 1 "你的问题，越具体越好"

# 抓取并总结指定网页（url_context）
llm -m gemini-2.5-flash -o url_context 1 "总结这个页面 https://example.com/x"

# 需要更强推理时换 pro，可两能力叠加
llm -m gemini-2.5-pro -o google_search 1 -o url_context 1 "你的问题"
```

要点：`-o google_search 1` 打开 Google 实时检索接地；`gemini-2.5-flash` 快而省，深推理再上 `gemini-2.5-pro`。Gemini 结论仍需按 [METHODOLOGY.md](../METHODOLOGY.md) §二标注证据，关键事实让它给来源 URL，必要时档位 2 复核。

### 档位 2 · 搜索引擎层（拿列表 / 拿原文）
- **WebSearch**（agent CLI 内置，Kimi/zcode 等均有）：关键词式搜索，拿标题+URL+摘要列表，适合"有哪些来源"。
- **exa（经 mcporter）**：神经/语义搜索。**query 写「理想页面的描述」而不是关键词**（"blog post comparing React and Vue performance" 而非 "React vs Vue"）；`category:people` / `category:company` 找人找公司；结果自带内容 highlights，常省一次抓取。注意：exa 配置位置决定可见性——配在 mcporter **home 级**（`~/.mcporter/mcporter.json`）则任意 cwd 可见（推荐）；若配在项目级 `config/mcporter.json`，则只在**该项目目录（cwd）下**被 mcporter 发现，换目录就不可见（`mcporter list` 里消失、agent-reach doctor 报 off）——用时先 cd 进项目，或提升到 home 级。是否已配置以设备档案或 `agent-reach doctor --json` 为准。
  ```bash
  mcporter call exa.web_search_exa query="<理想页面描述>" numResults=5
  mcporter call exa.web_fetch_exa urls='["<url1>","<url2>"]'   # 批量读全文（clean markdown）
  ```
  分工：**关键词明确 → WebSearch；概念/相似/研究向、或关键词搜不到 → exa**。
- **FetchURL**：单页转 markdown 精读（失败走 §三）。

### 档位 3 · firecrawl MCP（难抓的页 / 批量 / 监控）
- `firecrawl_scrape`：JS 渲染页（`waitFor`）、反爬（`proxy: stealth`）、结构化抽取（json format + schema）、缓存加速（`maxAge`）。
- `firecrawl_search`：带正文抓取的搜索（要内容时用，比 WebSearch 重，耗额度）。
- `firecrawl_map` + `firecrawl_crawl`：整站/批量——先 map 定位目标页再 scrape，省额度。
- `firecrawl_monitor_*`：页面/搜索定时监控（diff + meaningful 判定）。
- `firecrawl_agent`：多站点开放式深度研究（**最后手段**，慢且贵，2–5 分钟起）。

### 档位 4 · 登录态与交互（重任务）
- **opencli browser**：真实 Chrome——登录态会话、表单、翻页、网络请求捕获。JS 重 + 要登录的站用它。
- **agent-reach** skill：多平台多轮操作（发链接让它研究/整理/代操作）。

### 专项（不走阶梯，直接用）
- **kimi-datasource**：股票/财报/技术指标/宏观/企业（天眼查）/arxiv/scholar 结构化数据。
- **firecrawl_research_search_papers / related_papers / read_paper**：学术检索、引文扩展、原文选段验证。

---

## 三、抓取 fallback 链（借 openclaw 设计）

单页抓取按序降级，每步失败再往下（对应 openclaw web_fetch 的 Readability → Firecrawl → Browser）：

```
FetchURL（快、免费）
  → firecrawl_scrape（JS 渲染 waitFor=5–10s / 反爬 stealth / maxAge 缓存）
  → opencli browser（登录态、复杂交互）
```

- **缓存意识**：重复抓同一页用 firecrawl `maxAge`（加速 + 省额度）；`.firecrawl/` 是本地缓存目录（已 gitignore，不作事实源）。
- **来源纪律**：搜索工具给出的结论仍须真读来源（METHODOLOGY §一），数值必须有出处。

---

## 四、默认决策树

```
要查东西
  ├─ 在代码/文件里?              → 档位0 Grep/Glob/Read
  ├─ 有明确 URL 要读?            → §三 fallback 链（FetchURL 起）
  ├─ 要快事实 + 时效?            → 档位1 llm google_search      ← 默认从这里开始
  ├─ 要来源列表?                 → 档位2 WebSearch；语义/相似/研究向 → exa
  ├─ JS 重/反爬/批量/监控?        → 档位3 firecrawl MCP
  ├─ 要登录/多轮交互?            → 档位4 opencli browser → agent-reach
  └─ 金融/论文/企业结构化数据?     → kimi-datasource / firecrawl research
```

**原则**：能在低档位解决就不往上爬；往上爬要有理由（时效不够、需交叉验证、需深度产出、抓不动）。

---

## 五、各设备的实际实现（指针）

阶梯各档用什么工具实现是**设备事实**，随机器不同而不同。上文命令是能力模板，不代表当前机器已安装、已登录或已配凭据。各设备已安装/验证的搜索能力清单见其设备档案（🔒 在私有仓 `EverAgent-infra`，含敏感基础设施信息，不在本公开仓）：

- 各设备：私有仓 `infra/devices/{hostname}.md` §三「搜索栈」

> 设备档案维护：已装工具与健康状态、配置位置（如 mcporter/exa）、盘点日期。换机/新机时按私有仓 `infra/AGENTS.md` schema 建档，并在本节补一行指针。

---

## 六、维护

- 方法论/用法变更（新阶梯档位、更优命令、fallback 调整）→ 更新本文件。
- 安装类变更（装/卸工具、换模型、新增 MCP 服务）→ 更新私有仓 `EverAgent-infra` 对应 `infra/devices/{hostname}.md` 的搜索栈，本文件 §五 指针不动。

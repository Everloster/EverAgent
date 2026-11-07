# EverAgent 学习工作台

在本机翻报告、找文章、看播客更新。按日期和领域浏览，搜索标题或标签；长文可以按目录跳读、调整字号，下次打开接着看。

同一套应用可以在浏览器里独立运行，也可以作为 MiniMax Code 的 Mini App 打开。报告直接读取本地 EverAgent，无需私有仓、模型账号或 API Key。

## 在浏览器里打开

准备 **Node.js 20+**；从源码首次构建还需要 **Go 1.27+**。下载或克隆完整 EverAgent 仓库后，在仓库根目录运行：

```bash
npm --prefix apps/everagent-learning run build
node apps/everagent-learning/start.mjs
```

打开终端显示的地址，默认是 **http://127.0.0.1:4173/dashboard**。按 `Ctrl+C` 停止。不需要 `npm install` 或 Python；首次构建会按 `go.sum` 获取 Go 依赖，之后阅读不再运行编译器。

端口已占用时：

```bash
node apps/everagent-learning/start.mjs --port 4174
```

如果应用和报告仓库不在一起，可以指定仓库位置；路径带空格时保留引号：

```bash
node apps/everagent-learning/start.mjs --repo "/path/to/EverAgent"
```

构建产物位于应用的 `miniapp/bin/<系统>-<架构>/`，不进入 Git；已有适配器可用 `--indexer /path/to/ea-learning-index` 指定。只下载应用文件夹时，还需准备当前系统的适配器和含报告、`config`、`docs` 的公开仓。ZIP 解压目录不要求有 `.git`。

容器内可用 `--container --repo /public` 监听容器接口，只读挂载公开仓。此模式必须放在受控反向代理后：
代理先校验访问地址和同源请求，再将上游 Host 设为 `127.0.0.1:4173`、移除已校验的 Origin。
支持剥离前缀的挂载，例如 `/learning/dashboard`；页面、报告链接和图片都使用相对地址。不要将容器端口直接公开。

## 在 MiniMax Code 里打开

本目录也是 Mini App 插件包：先构建，再一起保留 `.minimax-plugin/plugin.json`、`package.json`、`icon.png` 与 `miniapp/`（含目标系统的 Go 适配器）。安装时以本目录为插件包根目录，名字保持为 `everagent-learning`；安装入口以所用版本的[官方说明](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps)为准。

宿主会把应用文件复制到自己的安装目录。首次打开如果没有找到报告，页面会提示填写 **EverAgent 仓库根目录**；填一次即可，后续从宿主的数据目录读取这项设置。已有安装副本需要重新安装或更新，才会获得本次修改。

Mini App 使用宿主启动的本地 Node 进程，页面通过本机 HTTP 读取数据，**不要求 Docker、Python 或 Go 运行环境**。宿主不会替应用构建适配器；安装包必须带上与系统/架构匹配的制品。具体宿主行为见官方[包结构说明](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps/blob/master/docs/package-contract.md)和[运行时契约](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps/blob/master/docs/runtime.md)。

## 两种方式怎么选

| | 本地浏览器 | MiniMax Code |
| --- | --- | --- |
| 适合的场景 | 独立阅读，或使用其他 Agent 工具 | 一边与 Agent 对话，一边查看学习产出 |
| 启停 | 手动运行命令、关闭进程 | 宿主管理应用进程和窗口 |
| 前置条件 | Node.js、已构建适配器、公开仓 | MiniMax Code、含适配器的插件包、公开仓 |
| 页面与报告 | 同一份实现、同一批本地资料 | 同左 |

**推荐两种入口共存。** 浏览器方便任何读者使用，MiniMax Code 适合已经在里面工作的用户。没有必要为此重写页面或增加一层桌面程序。

## 能读什么，怎样更新

- 报告列表与领域划分复用公共 core 的 [Go 报告目录](../../packages/everagent-core/internal/publicquality/catalog.go)，与质量门/生成索引同源，不另建数据库或执行报告仓库的脚本。
- 《AI演义》分节统一显示为「《AI演义》01｜Brook：…」：书名、两位章节号和分隔符一致，后面保留各篇具体标题。列表、阅读器与仓库生成索引使用同一显示规则。
- 首页固定入口为[小宇宙精选播客](../../podcast-learning/PODCAST_UPDATES.md)与[顶尖技术博客](../../web-surfing/TECH_BLOG_UPDATES.md)两张速看表；报告列表显示标题、领域与日期，筛选后可查看匹配数量或一键清除。
- 「小宇宙精选播客」同样按日期倒序展示最近 40 期，可搜标题、原题或节目名。每条保留节目、时长、音频备用入口和报告状态：「有报告 · 阅读」可直接打开；串台仅关联其他版本时显示「相关报告」，没有则显示「暂无报告」。周汇总与节目历史的重复条目合并，同场串台的不同发布版本分别保留；「完整清单」仍可按节目翻历史。
- 「顶尖技术博客」默认进入标题速览：跨来源按发布日期倒序，先展示最近 40 篇，只突出标题、来源、日期和已有报告入口；可搜索中文标题、原题或来源，再加载更早文章。点标题打开原文，「完整清单」保留按月份与厂商折叠的导读和历史记录。列表从已有 Markdown 投影，不实时抓取；只标月份或日期待补的文章仍留在完整清单。
- 正文支持表格、列表、代码块、相对图片、脚注和页内锚点；点击脚注可查看来源并返回引用处，报告之间的相对链接在阅读器内打开。「阅读」显示排版后的正文，「Markdown」查看去除元数据后的文本。
- 长文提供二、三级章节目录和 16–22 px 字号调整。窄屏下目录默认收起，表格和代码块可横向滚动；页面配色跟随系统。
- 首页「继续阅读」回到最近打开的报告，重新打开时恢复阅读位置。阅读记录最多保留 40 篇，只存在当前浏览器的本地存储中，不上传、不写进仓库，也不在浏览器和 MiniMax 宿主之间同步。宿主禁用本地存储时，仍可正常阅读。
- 「返回列表」、`Esc` 或浏览器后退均可退出阅读；窄屏目录打开时，`Esc` 先收起目录。地址栏保留当前报告路径，可收藏本机阅读地址。
- 更新报告后点击「刷新」，即可重新读取列表和正文。工作台程序本身更新后，重启服务并刷新浏览器；MiniMax Code 的安装副本需更新插件。工作台不会自动拉取 Git、抓取订阅或调用模型出报告。
- 本地正文可离线读；外部图片、原始来源及 GitHub 链接仍需要联网。「在 GitHub 打开」指向公共上游，本地未推送的修改不会出现在那里。

目前是阅读工作台，尚未加入任务派发、笔记同步或记忆服务。Markdown 使用 Goldmark 的 CommonMark/GFM 与脚注扩展；正文实体遵循标准 Markdown，代码块保留字面内容。Mermaid、数学公式尚不渲染，报告原始 HTML 以文字显示（安全命名锚点除外）；可切换 Markdown 或跳转 GitHub。单篇正文上限为 2 MiB，超限或非 UTF-8 会明确报错，不静默交付缺尾或损坏文本。

## 本地资料的边界

应用只检查自身所在路径的少数父目录，以及用户明确指定或保存的公开仓路径；不遍历用户目录，不读取相邻私有仓，也不读取 Git remote。改名目录、fork 和 ZIP 解压目录均可使用。

HTTP 接口仅提供报告目录收录的 Markdown、两张速看表，以及允许目录下的图片。隐藏路径、越界路径、软链与硬链被拒绝，播客逐字稿不在阅读接口范围内。接口不返回本机绝对路径。服务只监听本机回环地址，并检查请求来源；这不是一个用于公网部署或多用户共享的服务器。

工作台不会修改报告。通过页面设置仓库路径时，只保存这一项本机配置：MiniMax 模式用宿主 `dataDir`；独立模式用 `$XDG_CONFIG_HOME/everagent-learning/config.json`，未设置时用用户目录下 `.config/everagent-learning/config.json`。用启动参数指定路径不会写配置。

**只选择可公开的报告目录。** 应用不执行所选仓库的代码，但不会自动识别报告正文里的秘密。往公开报告目录放入资料之前，仍需确认资料可以公开。

## 验证与维护

在本目录运行：

```bash
npm test
```

测试先构建 Go 适配器，再验证真实 HTTP、安装副本设置与重启、长报告完整性、本地图片、路径边界、来源检查和进程关闭；Go 用例覆盖目录、标准 Markdown 和两份速看表。测试只构造临时公开仓；软链用例需要系统允许创建软链。交叉编译不等于目标系统已运行验证。

Go 候选已在 macOS 浏览器验证报告阅读、两份速看表、搜索、加载更多、完整清单、报告跳转与脚注；Linux/arm64 隔离容器验证了只读挂载、完整正文、请求边界及重启。**尚未在 MiniMax Code 中重新安装实测；Windows 仅交叉编译，容器测试也不等于其他设备已部署。** 自动化测试对 Mini App 的安装目录与启停按官方契约模拟，不代替宿主实测。

页面与 Node 宿主在本目录维护；Go JSON 适配器为 [`ea-learning-index`](../../packages/everagent-core/cmd/ea-learning-index/main.go)，其[实现和回归](../../packages/everagent-core/internal/learning/)复用公共 core 的报告目录。软件代码采用 [MIT License](./LICENSE)；报告等知识内容沿用仓库[版权说明](../../DISCLAIMER.md)。

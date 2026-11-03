# EverAgent 学习工作台

在本机翻报告、找文章、看播客更新。按日期和领域浏览，搜索标题或标签；长文可以按目录跳读、调整字号，下次打开接着看。

同一套应用可以在浏览器里独立运行，也可以作为 MiniMax Code 的 Mini App 打开。报告直接读取本地 EverAgent，无需私有仓、模型账号或 API Key。

## 在浏览器里打开

准备 **Node.js 20+** 和 **Python 3.10+**。下载或克隆完整 EverAgent 仓库后，在仓库根目录运行：

```bash
node apps/everagent-learning/start.mjs
```

打开终端显示的地址，默认是 **http://127.0.0.1:4173/dashboard**。按 `Ctrl+C` 停止。不需要 `npm install`、`pip install` 或构建步骤。

端口已占用时：

```bash
node apps/everagent-learning/start.mjs --port 4174
```

如果应用和报告仓库不在一起，可以指定仓库位置；路径带空格时保留引号：

```bash
node apps/everagent-learning/start.mjs --repo "/path/to/EverAgent"
```

macOS、Linux 默认调用 `python3`，Windows 默认调用 `python`。如果命令不同，用 `--python` 指定解释器，例如 `--python python3.12`。只下载应用文件夹时，仍需另外准备含报告、`scripts`、`config` 和 `docs` 的完整公开仓。

## 在 MiniMax Code 里打开

本目录也是完整的 Mini App 插件包：`.minimax-plugin/plugin.json`、`package.json`、`icon.png` 与 `miniapp/` 必须一起保留。安装时以本目录作为插件包根目录，名字保持为 `everagent-learning`；安装入口以所用版本的[官方说明](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps)为准。

宿主会把应用文件复制到自己的安装目录。首次打开如果没有找到报告，页面会提示填写 **EverAgent 仓库根目录**；填一次即可，后续从宿主的数据目录读取这项设置。已有安装副本需要重新安装或更新，才会获得本次修改。

Mini App 使用宿主启动的本地 Node 进程，页面通过本机 HTTP 读取数据，**不要求 Docker**。Python 仍需本机提供；宿主不会替应用安装 Python。具体宿主行为见官方[包结构说明](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps/blob/master/docs/package-contract.md)和[运行时契约](https://github.com/MiniMax-AI/MiniMax-Code-MiniApps/blob/master/docs/runtime.md)。

## 两种方式怎么选

| | 本地浏览器 | MiniMax Code |
| --- | --- | --- |
| 适合的场景 | 独立阅读，或使用其他 Agent 工具 | 一边与 Agent 对话，一边查看学习产出 |
| 启停 | 手动运行命令、关闭进程 | 宿主管理应用进程和窗口 |
| 前置条件 | Node.js、Python、公开仓 | MiniMax Code、Python、公开仓 |
| 页面与报告 | 同一份实现、同一批本地资料 | 同左 |

**推荐两种入口共存。** 浏览器方便任何读者使用，MiniMax Code 适合已经在里面工作的用户。没有必要为此重写页面或增加一层桌面程序。

## 能读什么，怎样更新

- 报告列表与领域划分复用仓库的 [`report_catalog.py`](../../scripts/report_catalog.py)，不另建数据库。
- 首页提供[小宇宙精选播客](../../podcast-learning/PODCAST_UPDATES.md)与[顶尖技术博客](../../web-surfing/TECH_BLOG_UPDATES.md)两张历史速看表。
- 首页两个固定入口分别为「小宇宙精选播客」和「顶尖技术博客」；报告列表显示标题、领域与日期，筛选后可查看匹配数量或一键清除。
- 正文支持表格、列表、代码块和相对图片；报告之间的相对链接在阅读器内打开。「阅读」显示排版后的正文，「Markdown」查看去除元数据后的文本。
- 长文提供二、三级章节目录和 16–22 px 字号调整。窄屏下目录默认收起，表格和代码块可横向滚动；页面配色跟随系统。
- 首页「继续阅读」回到最近打开的报告，重新打开时恢复阅读位置。阅读记录最多保留 40 篇，只存在当前浏览器的本地存储中，不上传、不写进仓库，也不在浏览器和 MiniMax 宿主之间同步。宿主禁用本地存储时，仍可正常阅读。
- 「返回列表」、`Esc` 或浏览器后退均可退出阅读；窄屏目录打开时，`Esc` 先收起目录。地址栏保留当前报告路径，可收藏本机阅读地址。
- 更新本地仓库后点击「刷新」，即可重新读取列表和正文。工作台不会自动拉取 Git、抓取订阅或调用模型出报告。
- 本地正文可离线读；外部图片、原始来源及 GitHub 链接仍需要联网。「在 GitHub 打开」指向公共上游，本地未推送的修改不会出现在那里。

目前是阅读工作台，尚未加入任务派发、笔记同步或记忆服务。Markdown 使用轻量渲染器，Mermaid 和数学公式尚不渲染，复杂 HTML 可能以文字显示；可切换 Markdown 或跳转 GitHub。单篇正文上限为 2 MiB，超过会明确报错，不会静默丢掉后半篇。

## 本地资料的边界

应用只检查自身所在路径的少数父目录，以及用户明确指定或保存的公开仓路径；不遍历用户目录，不读取相邻私有仓，也不读取 Git remote。改名目录、fork 和 ZIP 解压目录均可使用。

HTTP 接口仅提供报告目录收录的 Markdown、两张速看表，以及允许目录下的图片。隐藏路径、越界路径、软链与硬链被拒绝，播客逐字稿不在阅读接口范围内。接口不返回本机绝对路径。服务只监听本机回环地址，并检查请求来源；这不是一个用于公网部署或多用户共享的服务器。

工作台不会修改报告。通过页面设置仓库路径时，只保存这一项本机配置：MiniMax 模式用宿主 `dataDir`；独立模式用 `$XDG_CONFIG_HOME/everagent-learning/config.json`，未设置时用用户目录下 `.config/everagent-learning/config.json`。用启动参数指定路径不会写配置。

**只选择可信的 EverAgent checkout。** 应用会执行该仓库自己的报告目录脚本；它也不会自动识别报告正文里的秘密。往公开报告目录放入资料之前，仍需确认资料可以公开。

## 验证与维护

在本目录运行：

```bash
npm test
```

测试包含真实 HTTP 请求、安装副本首次设置与重启、长报告完整性、本地图片、越界读取拦截、请求来源检查和进程关闭。测试构造临时公开仓，不读取个人资料。测试命令使用 `python3`；解释器名称不同的环境可分别运行 `node --test test_server.mjs` 与 `python -B -m unittest test_report_index -v`。软链测试需要系统允许创建软链。

已在 macOS 验证独立启动、真实报告阅读、搜索与清除筛选、速看表跳转、章节目录、字号调整、Markdown 切换、阅读位置恢复、浏览器后退与窄屏布局；同时按官方契约模拟了 Mini App 的安装目录与启停。**新包尚未在 MiniMax Code 中重新安装实测，Windows、Linux 也未实机验证。**

源码与测试以本目录为唯一维护入口。软件代码采用 [MIT License](./LICENSE)；报告等知识内容沿用仓库[版权说明](../../DISCLAIMER.md)。

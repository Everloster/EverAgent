# 让 Agent 部署学习工作台

把下面的 prompt 发给能操作本机终端的 Agent，即可让它克隆公开仓、构建阅读适配器、启动浏览器工作台并验证报告。完整启动参数和功能说明由 [README](./README.md)维护。

工作台读取仓库已有的报告和两份更新清单；研究、订阅抓取和转写需要各自配置，不是阅读部署的前置任务。

## 交给 Agent 的 prompt

```text
请在这台机器上部署 EverAgent 学习工作台，让我通过浏览器查看公开报告。请实际完成克隆、构建、启动与验证，并保留可用的服务进程。

公开仓库：https://github.com/Everloster/EverAgent.git
部署说明：https://github.com/Everloster/EverAgent/blob/main/apps/everagent-learning/DEPLOY.md

1. 检查 Git、Node.js 20+（含 npm）和 Go 1.27+。缺少时，按当前系统适合的官方安装方式补齐；保留用户现有的项目和工具配置。

2. 在合适的本地工作目录克隆 main 分支；已有同名目录时不要覆盖，选择另一个目录。以下以 EverAgent 为目录名：
   git clone --depth 1 --branch main https://github.com/Everloster/EverAgent.git
   cd EverAgent

3. 阅读仓库 AGENTS.md 和 apps/everagent-learning/README.md，以当前源码和启动说明为准。这是公开资料阅读任务，无需 npm install、Python、Docker、eacli、EverAgent-infra、模型账号或 API Key。

4. 在仓库根目录执行：
   npm --prefix apps/everagent-learning run build
   node apps/everagent-learning/start.mjs

   默认地址为 http://127.0.0.1:4173/dashboard。端口被占用时使用 --port 4174 等空闲端口，保留其他服务。首次构建会下载 Go 依赖；日常启动使用已构建的适配器。

5. 使用当前 Agent 环境支持的持久终端或本机进程管理方式运行服务，确认结束这轮对话后仍能访问。服务保持监听 127.0.0.1。记录启动命令、终端或进程标识，以及输出所在位置。

6. 实际验证：
   - /dashboard 返回 200。
   - /api/reports 返回 ok=true、complete=true，且 total 大于 0。
   - 从 reports 数组选择一篇报告，读取 /api/report?path=<URL 编码后的报告路径>，确认返回完整正文，truncated=false。
   - 用同一接口读取 podcast-learning/PODCAST_UPDATES.md 和 web-surfing/TECH_BLOG_UPDATES.md，确认两份清单的正文与 update_feed 都有内容。
   - 有浏览器工具时，打开工作台，检查报告搜索、一篇报告正文，以及“小宇宙精选播客”“顶尖技术博客”两个入口。

7. 最后给我可点击的访问地址、仓库位置、依赖版本、启动和停止方式，以及实际验证结果。没有浏览器能力或检查失败时，说明未验证的部分和具体原因。
```

## 依赖与日常使用

| 工具 | 用途 |
| --- | --- |
| Git | 克隆和更新公开资料。 |
| Node.js 20+，含 npm | 执行构建入口并运行本机 HTTP 服务；没有需要安装的 npm 依赖。 |
| Go 1.27+ | 从公开源码首次构建适配器；工作台代码更新后重新构建时也需要。运行已构建的适配器不需要 Go。 |
| Git LFS（按需） | 仓库的 PDF 使用 LFS；Markdown 报告与工作台启动不依赖 PDF 下载。需要这些 PDF 时，在仓库内执行 `git lfs install --local` 和 `git lfs pull`。 |

在仓库根目录重新启动：

```bash
node apps/everagent-learning/start.mjs
```

前台运行时按 `Ctrl+C` 停止；如果 Agent 使用了持久终端或进程管理器，应提供对应的停止方法。退出服务不会删除资料或浏览器中的阅读记录。

更新前先用 `git status --short` 检查本地修改。没有冲突时，运行：

```bash
git pull --ff-only
```

只有报告或清单更新时，点击工作台「刷新」即可。应用或公共 Go core 更新后，停止旧服务，重新执行构建和启动命令。本地有修改或无法快进时先处理具体冲突，不自动丢弃、覆盖或暂存用户的工作。

## 部署结果怎么判断

页面能打开只是第一步；报告目录、正文和两份更新清单都能读取，才算完成阅读部署。报告数随公开仓更新变化，不把某个固定数字写进验收条件。程序不会自动拉取 Git、抓取订阅或调用模型生成报告。

本地 Markdown 和仓内图片可以离线阅读；外部图片、原文与音频仍需联网。数学公式、Mermaid 和其他渲染限制，以及各平台与 MiniMax 宿主的验证范围，见 [应用说明](./README.md)。

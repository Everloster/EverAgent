# 播客转写与润色

> 把节目链接或本地音频变成忠实的 `.transcript.txt` 与 `.polished.txt`。不负责报告结构。

## 路由

- URL 默认走 eacli podcast 的 Razer 静默 worker；命令和结果路径见 [pipeline-guide §一](./references/pipeline-guide.md#一转写产出-transcripttxt)。
- 本地文件或明确的隔离排障才使用本地脚本；依赖与参数见同一节。
- B 站来源读取 [pipeline-guide：B站链接](./references/pipeline-guide.md#b站链接只允许无-ui-获取)。
- 出现尾部循环、重复段或混合语种问题时读取 [pipeline-guide：已知故障](./references/pipeline-guide.md#whispercpp-已知故障长音频尾部幻觉循环2026-07-18-实测)。
- 润色边界读取 [pipeline-guide §二](./references/pipeline-guide.md#二润色产出-polishedtxt)。

## 不变量

- 全程静默，不打开浏览器 UI、系统 URL opener 或播放器。
- 转写不补写事实；无法确定的内容保留并标 `[?]`。
- 人名、术语、数字和引文必须用 shownotes、字幕或其他一手材料核验。
- 获取或转写失败时返回具体原因，不用有副作用的交互路径兜底。

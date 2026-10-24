# Skill: transcription — 本地转写 + 润色规范 — 详细参考

> 按需参考：只读取入口 `SKILL.md` 为当前任务指出的章节，不把本文件当作固定行程逐项执行。

> 通用研究方法论见根 [METHODOLOGY.md](../../../../METHODOLOGY.md)；按当前任务读取相关章节。本文件只保留领域差异。
> 目标：把一个播客/视频链接（或本地音频）变成可读、忠实的原文，供后续总结与讨论。

---

## 一、转写（产出 `.transcript.txt`）

URL 的 canonical 路径是 Razer 静默 worker；不在 MBP/MBA 打开网页或播放媒体：

```bash
eacli podcast status --json
eacli podcast plan --source '<URL>' --language zh --timeout 21600 --json
eacli podcast run --source '<URL>' --language zh --timeout 21600 \
  --plan-id pdp_... --confirm pdp_.../razer \
  --request-id req_<stable-id> --json
eacli podcast result --job job_podcast_... --wait 3600 --json
```

`result` 返回的 transcript 位于 Razer 系统盘
`/srv/everagent/artifacts/podcast/`。先按 artifact receipt 的路径、大小与 SHA-256 拉回：

```bash
eacli pull 'razer:/srv/everagent/artifacts/podcast/pod_....transcript.txt' \
  'reports/transcripts/{slug}.transcript.txt' \
  --request-id req_pull_<stable-id> --json
```

当前 `eacli pull` 单文件上限为 190KB。超过上限时使用仓内薄编排器，它仍只调用
`eacli invoke` 与 `eacli pull`，会在 Razer 按 180KB 分片、逐片拉回、原子重组并核对原始
SHA-256：

```bash
python3 podcast-learning/scripts/podcast_artifact_pull.py pull \
  --remote-path '/srv/everagent/artifacts/podcast/pod_....transcript.txt' \
  --sha256 '<artifact.transcript_sha256>' \
  --size '<artifact.transcript_size>' \
  --output 'podcast-learning/reports/transcripts/{slug}.transcript.txt' \
  --request-id req_pull_<stable-id>
```

拉回完成后再继续润色和报告；不得用聊天输出复制大段转写，也不得跳过大小与 SHA-256 校验。

若为公开仓保存 artifact receipt，需从运行态回执生成最小公开视图：保留 `source_url/source_host`、音频与转写的大小和 SHA-256、语言、段数、时长、服务版本、静默/无播放器标志、传输原子性与审计结果；删除执行设备名、远端绝对路径、`job_id`、`plan_id`、`artifact_id`、账号和网络信息。报告与 evidence 使用“eacli podcast 远端静默 worker”，不要把私有执行拓扑写进知识产物。

### 获取失败的证据顺序

1. 固定本次 `source → plan → request → job` 绑定，只读取该 job 的 `result/state`；相邻任务的时长、日志或错误不能拿来补当前 artifact。
2. `nonzero_exit` 只是包装层结果，不是根因。继续读取 helper 的结构化错误，再区分主机白名单、重定向/CDN、下载器、临时文件、worker RPC 或转写本体。
3. 若 `plan` 接受来源而执行 helper 拒绝同一来源，优先判定控制面与部署 helper 的合同漂移；先修一致性与错误透传，不重复生成任务。
4. 生成类失败不自动重放。修复后重新生成 plan，并使用新的稳定 request id；旧失败记录保留原貌。

本地文件，或明确隔离排障时，才使用本地脚本。它全程离线（除下载音频），不走云端 API：

```bash
cd podcast-learning/scripts
python3 transcribe.py "<链接或本地音频路径>" \
    --out ../reports/transcripts/{YYYY-MM-DD}_{show}_{ep}.transcript.txt
# 中文播客默认 --lang zh；混合语种 --lang auto；纯 CPU 建议 --model medium
```

- 首次使用先按 [SETUP.md](../../../SETUP.md) 安装 `yt-dlp faster-whisper` + `ffmpeg`。
- 链接无法被 yt-dlp 解析时：手动下载音频 → 用本地文件模式转写。
- 转写文件保留时间戳行 `[HH:MM:SS -> HH:MM:SS] 文本`，方便回溯定位。

### B站链接：只允许无 UI 获取

旧流程曾在 yt-dlp 失败后使用 `opencli bilibili download` 复用 Chrome 登录态。该路径会创建
`OpenCLI Browser` 标签组；Chrome Saved Tab Group Sync 可能把标签同步到其他 Mac 并自动播放，
因此已退役。现在固定：

```bash
yt-dlp --ignore-config --no-playlist --extract-audio \
  --audio-format wav -- '<B站 URL>'
```

- 默认仍由 `eacli podcast` 在 Razer 执行上述下载，不手工跑。
- 下载失败时允许无 UI 的官方 API或已证明不创建 tab 的站点 adapter；仍失败就停止并报告。
- **禁止** `opencli browser`、依赖浏览器扩展/Chrome 登录态的 download fallback、`open` /
  `xdg-open`，以及任何音视频播放器。

**官方字幕 = 修正源**（替代小宇宙 shownotes 的角色）：

```bash
opencli bilibili subtitle <BVID> -f yaml > /tmp/subtitles.yaml
```

仅当该命令命中无 UI adapter 时可用；如果实现要求启动浏览器，立即停止，不降级。

- 用字幕逐处校验 whisper 误识别（人名/术语/数字），修正写入 polished 头部清单。
- ⚠️ 官方字幕自身也是 ASR 产物，**可能有错**（实测："夜里面"→"叶里面"、"清晨"→"清纯"）——字幕与 whisper 一致但上下文明显不通时，依上下文修正并单独标注「字幕亦错」。
- ⚠️ 官方字幕**可能是英文 AI 翻译版而非中文原文**（实测 BV1krM46BEpn 全片英文字幕）——此时无法逐字校正同音误识别，只能做语义级校验；修正标注「依上下文+字幕语义」。
- 视频发布日期用 API 拿（命名需要）：`curl -s "https://api.bilibili.com/x/web-interface/view?bvid=<BVID>"` 取 `pubdate`。

拉回后统一运行本地确定性审计，不再临时拼 `tail` / `uniq` 命令：

```bash
python3 podcast-learning/scripts/audit_transcript.py \
  podcast-learning/reports/transcripts/{slug}.transcript.txt --json
```

它检查段数、时间戳单调性、连续重复、尾部异常间隔，并返回头尾样本、大小与 SHA-256；
仍需用 shownotes 抽查专名、数字和章节边界。

### whisper.cpp 已知故障：长音频尾部幻觉循环（2026-07-18 实测）

95 分钟访谈转写中，whisper.cpp（large-v3）在约 86 分钟处陷入**重复幻觉循环**（同一句话重复约 570 段直至结束），且循环前部分句子重复 2–10 次。

- **必查**：转写完成后运行 `audit_transcript.py`，并人工看返回的头尾样本；不要只看开头几段就交付。
- **发现循环**：截断有效部分，丢失时段用官方字幕重构（哪怕是英文翻译版字幕，也能回译出内容骨架）；transcript 头部与报告 Limitations 必须如实标注故障区间。
- Razer worker 固定启用 Silero VAD + `max-context=0`，并在落盘前检查连续重复段；同句连续
  超过 3 段即任务失败，不生成伪完成报告。

## 二、润色（产出 `.polished.txt`）

基于转写原文做**忠实润色**，与转写并列存放，同名 `.polished.txt`。

**允许**：去口水词（嗯/那个/就是）、合理断句分段、纠正明显同音错字、补标点。
**禁止**：改变说话人原意、增删事实、脑补未说出口的内容、合并不同人观点。

- 听不清/转写明显出错且无法确定的词：保留原文并标 `[?]`，不猜。
- 可按话轮或话题分段，段前可留粗略时间戳锚点。
- 润色稿是"可读版原文"，不是总结——不做提炼、不加评论。

---

## 质量红线

- ❌ 转写里没有的引用、数据、人物言论，禁止在润色/报告中出现。
- ❌ 转写质量差时不强行"补全"，在报告 limitations 如实标注。
- ✅ 关键金句、数字、人名保留原文措辞（哪怕标点残缺）。

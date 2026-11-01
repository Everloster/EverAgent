# Skill: transcription — 本地转写 + 润色规范 — 详细参考

> 按需参考：只读取入口 `SKILL.md` 为当前任务指出的章节，不把本文件当作固定行程逐项执行。

> 通用研究方法论见根 [METHODOLOGY.md](../../../../METHODOLOGY.md)；按当前任务读取相关章节。本文件只保留领域差异。
> 目标：把一个播客/视频链接（或本地音频）变成可读、忠实的原文，供后续总结与讨论。

---

## 一、转写（产出 `.transcript.txt`）

URL 的 canonical 路径是 eacli podcast 远端静默 worker；任何执行端都不打开网页或播放媒体：

```bash
eacli podcast status --json
eacli podcast plan --source '<URL>' --language zh --timeout 21600 --json
eacli podcast run --source '<URL>' --language zh --timeout 21600 \
  --plan-id '<plan 返回值>' --confirm '<plan 返回的确认令牌>' \
  --request-id req_<stable-id> --json
eacli podcast result --job job_podcast_... --wait 3600 --json
```

`plan/run/result` 的 `--device` 在当前 CLI 中可省略，不要把设备名固化进公开命令。
`run` 的 `--plan-id`、`--confirm` 仍必填，确认令牌须原样取自本次 plan，不能根据公开文档拼造。
`result` 的 transcript 地址仅从本次 artifact receipt 读取；私有执行映射不属于公开协议。

`eacli pull` 的 remote 参数仍必须是 `<device>:/abs/path`；这里是参数形状，不是允许公开真实映射。
先在本地选择仓库外的私有目录，再按 receipt 的地址、大小与 SHA-256 拉回：

```bash
eacli pull '<本次回执对应的设备与绝对路径>' \
  '<仓库外私有目录>/{slug}.transcript.txt' \
  --request-id req_pull_<stable-id> --json
```

现有薄编排器用于超过单文件传输上限的 artifact，分片传输后原子重组并核对原始 SHA-256。
它的 `--device` 可省略，但当前默认映射属于外部部署约束；不在公开文档展开。调用前核对
本地 CLI 能力和本次回执，不能把旧部署的大小限制当作永恒合同。

```bash
python3 podcast-learning/scripts/podcast_artifact_pull.py pull \
  --remote-path '<artifact receipt 的远端路径>' \
  --sha256 '<artifact.transcript_sha256>' \
  --size '<artifact.transcript_size>' \
  --output '<仓库外私有目录>/{slug}.transcript.txt' \
  --request-id req_pull_<stable-id>
```

拉回完成后再继续润色和报告；不得用聊天输出复制大段转写，也不得跳过大小与 SHA-256 校验。
本仓规则不会自动改变外部 eacli worker/传输器的落盘位置或清理策略；执行者必须显式选择私有输出，
核查外部生产器未将全文复制进公开仓。仓库检查不等于外部生产器已迁移。

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
    --out '<仓库外私有目录>/{YYYY-MM-DD}_{show}_{ep}.transcript.txt'
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

- 默认仍由 eacli podcast 远端静默 worker 执行上述下载，不手工跑。
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
  '<仓库外私有目录>/{slug}.transcript.txt' --json
```

它检查段数、时间戳单调性、连续重复、尾部异常间隔，并返回头尾样本、大小与 SHA-256；
仍需用 shownotes 抽查专名、数字和章节边界。

### whisper.cpp 已知故障：长音频尾部幻觉循环（2026-07-18 实测）

95 分钟访谈转写中，whisper.cpp（large-v3）在约 86 分钟处陷入**重复幻觉循环**（同一句话重复约 570 段直至结束），且循环前部分句子重复 2–10 次。

- **必查**：转写完成后运行 `audit_transcript.py`，并人工看返回的头尾样本；不要只看开头几段就交付。
- **发现循环**：保留原始失败 artifact 与回执，不原地截断或覆盖。必要时另建修复版本，用官方字幕补充可核验的缺失片段并重新审计；翻译字幕只能作为语义线索，不能伪装逐字原文。修复说明与报告 Limitations 如实标注故障区间和来源差异。
- eacli podcast 远端静默 worker 的既有合同使用 Silero VAD + `max-context=0` 与落盘前重复检查；
  同句连续超过 3 段应失败。实际部署状态仍须由本次机器回执确认，本地审计不替外部生产器背书。

### 私有默认与公开审计收据

新完整转写与完整润色稿默认仅私有/本地保存，公开报告保留来源 URL 和必要摘录。
对既有公开全文不批量搬迁，不改历史报告正文或 `.quality` 哈希链；逐篇迁移需要新的 revision、
重新复核以及完整引用检查。详见 [COPYRIGHT.md](../../../COPYRIGHT.md)。

公开检查按新增全文文件判断，不依赖报告是否声明 `private`。新增全文只有附带维护者已确认、
绑定本次内容哈希的 `.publication.json` 才可作为公开例外；字段与范围见上述版权规则。
通常只提交报告与脱敏审计收据，私有转写保存在仓库外。

未来报告可使用下列**新增、可选**字段；不要求历史报告补填：

```yaml
transcript_visibility: private
transcript_path: null
polished_transcript_path: null
source_url: 'https://example.org/episode'
transcript_source_ref: 'sha256:<私有转写的64位小写内容哈希>'
transcript_audit_path: 'reports/transcripts/{slug}.audit.json'
```

- `transcript_path`/`polished_transcript_path` 只接受真实仓内相对路径；不链接私有绝对路径，
  不以 `private:` 伪路径冒充可访问文件。`null`/省略不代表全文已检查。
- `transcript_source_ref` 是内容摘要，不是运行态 artifact/job ID；映射只在本地私有环境保存。
- `transcript_audit_path` 是领域相对或 `podcast-learning/` 开头的仓库相对路径。通过以下只读命令
  向 stdout 生成白名单收据，再由调用方审阅、保存到指定公开相对路径；脚本不写文件：

```bash
python3 podcast-learning/scripts/audit_transcript.py \
  '<仓库外私有目录>/{slug}.transcript.txt' \
  --public-receipt --source-url '<公开节目URL>'
```

收据 v2 只包含公开 `source_url`、`sha256:` 内容 ref、固定重复阈值和审计指标；无本机路径、
原文头尾样本、重复原句或执行标识。普通 `--json` 仍含本机路径与样本，只能留在私有环境。
生成前人工确认 URL 不含私有定位信息或签名参数；自动过滤只拒绝明显的认证/内网 URL。

根 `scripts/audit_reports.py` 调用 `audit_transcript.py` 的只读模块：

- 有 raw 时实测时间戳、连续重复，并核对声明的段数、时长；有 raw/polished 时按文件汉字数
  核验压缩比声明（2 个百分点容差），异常压缩率提示人工检查，不自动修正文稿。
- 有源和收据时逐项比较 SHA-256 与审计指标；源缺失但收据有效时明确报 `POD109 receipt_only`
  WARN。缺 source URL、内容 ref、收据或失败的收据不能伪装核验成功。
- 无声明来源的历史/仅 shownotes 报告不被强制补造转写。已声明却不存在的路径是问题，不默默略过。
- 全库盘点新增的来源检查将历史债报 WARN；`--changed`/`--staged`、新增来源和 `--strict`
  会阻断确定性错误。改动 raw、polished 或收据（含删除）会反查依赖报告，不按文件日期豁免。
- Wiki 链接保留真实目标约束，限定路径不可由别处同名页面代替。report-v2 章节与质量字段
  只认根合同，不再要求旧领域模板的“速览”、固定章节集、`pipeline`、`notable_correction` 等。

现有 report-v2 evidence 的 `kind: local` 仍只接受仓内普通文件。新报告可把公开节目 URL 登记为
原始来源，并把公开审计收据登记为本地审计产物；不要把收据当原文或 claim 的语义证据。
Reviewer 必须在有权访问私有原文/公开原始来源的环境中核对内容，并如实记录边界。
根检查只验证收据结构和绑定，不证明收据出自可信签名者，也不替代独立内容复核；没有访问来源
就不能声称完成。外部 eacli 的私有存储/脱敏输出尚由外部生产器约束，本改动没有改其配置。

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

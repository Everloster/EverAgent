# 脚本目录

> Generated from script-catalog.json; do not edit by hand.
> source-sha256: `d06b7ab02c623a934f34972ca0f2c6e8d3b0a325263cc95e1b4461c2a6b9889e`
> generator: `eacli docs index --write` (script-index-v2)

| ID | 入口 | 描述 | 范围 |
|---|---|---|---|
| `git.entry` | `scripts/egit.sh` | 仓库绑定的Git薄入口；只选择并校验已安装eacli，逐项转发身份/commit/merge/push/hooks参数。 | 脚本位置canonical绑定的公开checkout；policy Author、当前真实模型/明确有效声明Committer与新增内容保护由eacli执行 |
| ↳ compatibility | `scripts/ecommit.sh` | commit简写；保留-m/-F值、trailer与普通Git参数。 | 同 canonical |
| `docs.entry` | `scripts/edocs.sh` | 资料工具薄入口；公开仓不拥有工具源码、评分或索引算法，不启动质量门。 | 脚本位置canonical绑定的公开checkout；外部工具要求不是私仓源码entrypoint |
| `eacli.entry-helper` | `scripts/eacli-entry.sh` | 共享轻量helper，只定位canonical ROOT及选择/校验已安装eacli，不解析业务参数。 | 薄入口共用安装态检查；不成为业务实现 |
| `eacli.entry-tests` | `scripts/test_eacli_entries.mjs` | 隔离契约测试，假eacli仅记录argv/版本；覆盖工具选择、版本失败、canonical ROOT、参数和退出码。 | 仅薄入口；不验证外部eacli业务、不接入CI或质量门 |
| `evaluation.harness-experiment` | `scripts/harness_selection.py` | 消费可信评测器记录，按硬门和 Pareto 前沿选择最多三个 context 候选；不执行或发布。 | 可信评测记录与一次有界实验 |
| `report.catalog` | `scripts/report_catalog.py` | 报告集合、路径匹配、frontmatter、来源 URL、别名和日期投影的共享内部实现。 | 共享读取语义；不改写报告或生成索引 |
| `report.legacy-strict-review` | `scripts/audit_reports.py` | 显式选用的历史严格报告审计、证据账本与独立复核合同；不是普通写作或提交门禁。 | 历史 report-v1/v2 和用户显式严格复核；不自动用于普通新报告 |
| ↳ compatibility | `scripts/report_quality.py` | report-v2 初始化、复核、finalize 与历史策略校验。 | 同 canonical |
| ↳ compatibility | `scripts/lint_evidence.py` | 显式证据文本 lint。 | 同 canonical |
| ↳ compatibility | `podcast-learning/scripts/audit_reports.py` | 播客审计兼容入口；--fix 已退役。 | 同 canonical |
| `evaluation.behavior` | `scripts/eval_report_context.py` | ACE v3 普通任务与显式严格复核任务的行为模板、评分和开工探针。 | 按需行为评测；不是提交前置或默认模型调用 |
| ↳ compatibility | `scripts/run_ace_context_ab.py` | 显式授权后运行 Pi 开工 A/B；不执行原始任务或写报告。 | 同 canonical |
| `podcast.local-pipeline` | `podcast-learning/scripts/transcribe.py` | 本地音频下载、whisper.cpp 转写、转写审计与私有 artifact 拉回。 | 本地/隔离排障；默认远端 worker 由 eacli 拥有 |
| ↳ compatibility | `podcast-learning/scripts/audit_transcript.py` | 只读时间戳/重复/来源与公开收据检查。 | 同 canonical |
| ↳ compatibility | `podcast-learning/scripts/podcast_artifact_pull.py` | 通过 eacli 将回执绑定的全文拉到仓外私有目录。 | 同 canonical |
| `podcast.index-maintenance` | `podcast-learning/scripts/fetch_show_indexes.py` | 精选节目索引刷新、报告状态回填、实测统计与旧 Android manifest 投影。 | 仅用户请求或实际维护的播客索引/统计；不是默认提交链 |
| ↳ compatibility | `podcast-learning/scripts/sync_index_status.py` | 仅回填匹配报告状态；支持 --dry-run。 | 同 canonical |
| ↳ compatibility | `podcast-learning/scripts/fill_report_stats.py` | 按真实来源核对统计；缺来源不再冒充一致。 | 同 canonical |
| ↳ compatibility | `scripts/build_podcast_manifest.py` | 按需重建 docs/PODCAST_MANIFEST.json；--check 只读。 | 同 canonical |
| `radar.tech-blog` | `web-surfing/skills/ai-tech-blog-radar/scripts/radar.py` | 顶尖 AI 技术博客更新查询与渠道注册表维护。 | 官方技术博客；不自动写报告或覆盖历史清单 |
| `radar.tech-podcast` | `podcast-learning/skills/ai-tech-podcast-radar/scripts/radar.py` | SOTA AI 技术播客更新查询与渠道注册表维护。 | 技术播客雷达；不自动下载、转写或写报告 |
| `radar.shared-internal` | `scripts/radar_common.py` | Radar 共享的 JSON、有界 HTTP、XML、eacli、日期和 URL 策略内部实现。 | 共享机制；领域 URL、分类与评分仍由各 Radar 拥有 |
| `github.research-tools` | `github-trending-analyzer/scripts/trending_fetcher.py` | 真实 GitHub Trending、gh API 元数据和轻量报告草稿工具。 | 默认报告目录锚定 github-trending-analyzer/reports；环境变量可显式覆盖 |
| ↳ compatibility | `github-trending-analyzer/scripts/github_api.py` | 公开仓库 API；读取失败不返回伪正文。 | 同 canonical |
| ↳ compatibility | `github-trending-analyzer/scripts/report_generator.py` | 原子生成草稿；拒绝把非 Trending 搜索写成榜单。 | 同 canonical |
| `web.bilibili-inbox` | `web-surfing/skills/site-bilibili/scripts/bilibili_inbox.py` | 通过 OpenCLI 登录态只读生成 B 站关注、动态与观看候选清单。 | 不读取或输出 Cookie；完整偏好数据不进入公开仓 |
| `external.skills-sync` | `scripts/sync-external-skills.sh` | 暂存并同步两个 vendor 科学技能；只有显式 --install 才写用户级技能目录。 | 上游缺目录时失败且不修改本地；不自动提交或安装 |
| `practice.transformer` | `ai-practice/src/model.py` | Dense/MoE 教学模型、共享组件、显式训练与 checkpoint 推理。 | 缩尺教学；不把本地运行数值自动写入历史实验 |
| ↳ compatibility | `ai-practice/src/transformer_core.py` | 共享模型组件；无下载或训练副作用。 | 同 canonical |
| ↳ compatibility | `ai-practice/src/training.py` | 显式数据、批次、训练与原子 checkpoint。 | 同 canonical |
| ↳ compatibility | `ai-practice/src/moe_model.py` | MoE 路由与 CLI。 | 同 canonical |
| ↳ compatibility | `ai-practice/src/inference.py` | 已有 checkpoint 的交互或单次推理。 | 同 canonical |
| `practice.simulations` | `ai-practice/src/grpo_simulation.py` | GRPO、Long Context 和 SkillOS 的确定性缩尺模拟。 | 教学模拟，不冒充真实 LLM 训练或 1M 实机验证 |
| ↳ compatibility | `ai-practice/src/long_context_simulation.py` | Long Context 缩尺与成本模型。 | 同 canonical |
| ↳ compatibility | `ai-practice/src/skillos_curator_simulation.py` | 技能策展任务流模拟。 | 同 canonical |
| `practice.data-hardware` | `ai-practice/src/load_local_dataset.py` | 显式数据集读取与本机硬件检查；默认不执行远程数据集代码。 | 不遍历全局缓存；硬件输出由用户决定是否公开 |
| ↳ compatibility | `ai-practice/src/check_hardware.py` | 只读输出硬件与框架能力，不自动提交设备信息。 | 同 canonical |

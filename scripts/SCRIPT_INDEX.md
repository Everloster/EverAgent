# 脚本目录

> Generated from script-catalog.json; do not edit by hand.
> source-sha256: `5e623f1cf3a73549270f990975b5e2198eec826417ab22a4d0c04f55a43d6433`
> generator: `eacli docs index --write` (script-index-v2)

| ID | 入口 | 描述 | 范围 |
|---|---|---|---|
| `git.entry` | `scripts/egit.sh` | 仓库绑定的Git薄入口；只选择并校验已安装eacli，逐项转发身份/commit/merge/push/hooks参数。 | 脚本位置canonical绑定的公开checkout；policy Author、当前真实模型/明确有效声明Committer与新增内容保护由eacli执行 |
| ↳ compatibility | `scripts/ecommit.sh` | commit简写；保留-m/-F值、trailer与普通Git参数。 | 同 canonical |
| `docs.entry` | `scripts/edocs.sh` | 资料工具薄入口；公开仓不拥有工具源码、评分或索引算法，不启动质量门。 | 脚本位置canonical绑定的公开checkout；外部工具要求不是私仓源码entrypoint |
| `eacli.entry-helper` | `scripts/eacli-entry.sh` | 共享轻量helper，只定位canonical ROOT及选择/校验已安装eacli，不解析业务参数。 | 薄入口共用安装态检查；不成为业务实现 |
| `eacli.entry-tests` | `scripts/test_eacli_entries.mjs` | 隔离契约测试，假eacli仅记录argv/版本；覆盖工具选择、版本失败、canonical ROOT、参数和退出码。 | 仅薄入口；不验证外部eacli业务、不接入CI或质量门 |
| `evaluation.harness-experiment` | `scripts/harness_selection.py` | 消费可信评测器记录，按硬门和 Pareto 前沿选择最多三个 context 候选；不执行或发布。 | 可信评测记录与一次有界实验 |

# 提交与公开安全

本文件只说明公开仓的两项自动保护及Git操作边界。写作、元数据和复核统一见[REPORT_WORKFLOW.md](REPORT_WORKFLOW.md)。

## §A Safety Rules（安全铁律 · 全局适用）

- 不编造未读内容、来源或执行结果，未验证就明确说明。
- 私有材料先在原环境提炼与脱敏，不把原始数据搬进公开仓后才处理。密码、私钥、真实`.env`和未获授权的原始全文不公开。
- 未授权的外部发布、权限扩大和破坏性操作仍须确认；样例命令、历史成功或模型建议不扩大授权。
- 用户正在使用的Agent、会话和工作树保持原任务；不因普通任务自动派工、切换模型或重建布局。

## §B Commit Message 格式（全局统一）

用简短中文说明实际改动即可，不要求固定的Agent/Task-Type大模板。共同作者和trailer按实际情况保留，不伪造署名，不包含凭据。

## §C Push Flow（推送流程 · 全局统一）

正式Git入口是`scripts/egit.sh identity|commit|merge|push|hooks`，`scripts/ecommit.sh`保留为commit简写。公开脚本只是已安装eacli的薄适配，不维护Git、身份或内容扫描实现，也不依赖私仓checkout或其他设备在线。

须事先安装eacli **>=11.0.0**；入口优先使用显式`EACLI_BIN`，其次`$HOME/.local/bin/eacli`，最后PATH，并用`eacli --version`的plain release版本核对。选中的程序缺失、不可执行、版本非法或过旧时明确失败，不回退普通Git，不寻找相邻私仓，不自动build/install。

固定转发接口是`eacli git <identity|commit|merge|push|hooks> --repo-root CANONICAL_ROOT <args>`。`validate`旧别名已移除，统一使用`identity`。ROOT从脚本所在位置物理canonical绑定，不取调用cwd；可从子目录调用对应脚本路径。除第一个action外逐项保留参数，`-m`/`-F`值、trailer和普通Git参数不被脚本重写；实际eacli/Git失败退出码原样返回。

只自动检查：

1. **双身份**：Author来自公开仓已暂存`config/git-policy.json`中的主人身份；Committer是当前真实核实的模型，或用户明确给出的当前会话有效声明。策略缺失或冲突时拒绝，不回退全局身份；显式--author不能绕过。提交后核实实际Author和Committer，不输出错误身份中的邮箱。
2. **新增公开内容**：eacli在内存中检查本次新增内容的明显凭据和受限原始材料；结果不输出匹配到的秘密原文。疑似IP、路径、邮箱等给出提示，不做全仓隐私审计。

不运行报告评分、独立评审、索引审计或Go/Python回归。草稿可以提交；坏链接或测试失败不改变Committer资格，但实际问题仍须如实说明。

```bash
git add <本次修改的文件>
scripts/ecommit.sh -m "说明实际修改"
```

身份有问题时按需使用已安装的`eacli session diagnose --json`；仓库身份校验用`scripts/egit.sh identity --json`。公开仓不提供独立core源码运行入口。
未核实身份只阻断提交，不妨碍已授权只读或源码工作。声明只能承接用户明确事实，不猜模型或伪造自动观测。

公开内容检查绑定实际暂存树，防止检查后换成另一份内容；Git正常的冲突、签名、权限和参数错误仍返回失败。若commit已产生但后置身份/内容不符，保留现场，不自动再提交或推送。
仓外global hooks不读取、不替换、不绕过。[项目钩子](PROJECT_HOOKS.md)通过`egit.sh hooks install`只安装到本仓`.git/hooks`：身份检查阻断，后台采集与回执验证不阻断；新增公开内容检查仍由正式Git入口拥有，不恢复质量流水线。安装文件存在不代表Git已选择该目录，外部路由不由安装器改写。

使用普通快进交付到`origin/main`，先看实际远端与本地差异；不强推、不擅自stash/reset别人的工作。确需创建merge commit时用`scripts/egit.sh merge <明确revision>`，它在洁净checkout中冻结目标、准备合并并沿同一双身份/内容检查提交；冲突保留现场，不自动abort。普通pull建议设为ff-only，独立clone不会继承原仓的local配置。

推送用`scripts/egit.sh push`：只校验本次新增提交的Author和Committer元数据，并拒绝策略中明确撤销的提交进入祖先链；既有历史不因工具署名同域名而批量改写。推送期的元数据格式检查不冒充当时的模型运行验证。原生Git/GUI直接操作不保证经过此wrapper，不能声称本地入口是不可能绕过的安全边界。

跨仓任务必须事先说明目标仓、必要原因和源码/提交/推送/安装各自范围；起始cwd或创建隔离clone不代表获得跨仓发布授权。进入新clone后重新核对origin及个人署名配置，不能只设置Committer而遗漏Author。
推送结果未知先读回目的ref，SHA匹配才称已交付；不因超时盲目重复写入。

资料、隐私预览和可选索引工具统一由已安装eacli提供：`scripts/edocs.sh ACTION <args>`转发为`eacli docs ACTION --repo-root CANONICAL_ROOT <args>`，与Git入口共用版本选择规则。`disclosure`/`quick`只做轻量新增公开内容检查，不启动整套质量流水线。公开仓不维护这些工具的源码，不要求GitHub CI；需要的代码测试按任务范围主动运行，不作为提交资格或报告质量门。

## §D 报告质量门

该标题仅保留旧链接。日常报告不再经过强制质量门，当前规则见[写作与报告指南](REPORT_WORKFLOW.md)。
旧评分、来源账本与历史policy继续保留；需要时显式使用，不追溯重写旧报告或将旧分数当作新正文已复核。

## 检查的限度

公开内容检查是轻量启发式，不保证所有敏感信息都能识别，也不证明图片、二进制或第三方资料可公开。警告不是公开许可；真实敏感内容即使未被工具识别也不得发布。
原始转写等全文的公开仍需要原有内容绑定的许可依据。这属于数据发布授权，不是报告质量评分。

旧协议原文见[归档](archive/report-process-20261110/PROTOCOL_COMMON.md)，不再作为默认执行清单。

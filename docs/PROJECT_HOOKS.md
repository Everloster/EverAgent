# 项目本地 Git 钩子

统一实现和模板由已安装eacli提供，公开仓只保留薄入口，不提供core源码或第二套身份规则。每个clone的`.git/hooks`保存安装副本及版本/SHA清单。

## 安装与更新

前提：macOS或Linux、Git，以及已安装eacli >=11.0.0（`eacli --version`输出plain release版本）；不需要Go或任何相邻checkout。采集触发依赖已经配置的本机Context采集服务；安装器不安装软件、创建服务或修改采集范围。

在公开仓根目录：

```bash
scripts/egit.sh hooks status
scripts/egit.sh hooks install
```

每个获授权的目标仓分别使用显式ROOT初始化/更新，见[工作区搭建](WORKSPACE_SETUP.md)；不寻找并排私仓。只有迁移此前六文件清单完整且SHA匹配的本机版时才使用：

```bash
scripts/egit.sh hooks install --adopt-legacy
```

重复安装同一版本和bundle SHA是no-op。版本更新前保留原文件及清单到本项目`.git/hooks/everagent/backups/`；不会用较旧安装器降级新版钩子。钩子缺失、SHA或权限漂移、未知文件占位、符号链接及已有安装锁都会拒绝自动覆盖。失败若已产生部分写入，保留现场和精确备份，不能直接重跑或覆盖别人的修改。

## 实际行为

| 钩子 | 行为 |
|---|---|
| `pre-commit`、`pre-merge-commit` | 在目标仓运行已安装的 `eacli git identity`；身份核对失败时阻断提交 |
| `post-commit`、`post-merge` | 请求现有采集服务进行同步和durable ACK校验，始终返回0，不等待采集完成 |

macOS使用launchd的非强制`kickstart`；Linux使用`systemctl --user start --no-block`。不使用强制重启、enable或daemon-reload；既有15分钟任务仍兜底。后台积压与投递失败由采集器状态区分，不能把Git钩子返回0解释为归档已经完成。

公开入口从自身位置物理canonical定位项目，固定转发`eacli git hooks --repo-root ROOT <args>`。eacli优先取显式`EACLI_BIN`，其次当前用户的`$HOME/.local/bin/eacli`，再查PATH；选中程序缺失、不可执行或版本非法/过旧时明确失败，不回退普通Git、不自动build/install。安装的钩子也只消费已安装eacli，不寻找私仓源码。没有设备名、用户名或工作区绝对路径硬编码；GUI或未知Agent无法核实身份时只阻断提交，不阻断已授权只读或源码工作。

## 安装不等于生效

安装器只写显式目标的`.git/hooks`。它仅比较Git选择的目录是否命中这里，不打开外部钩子目录，不读取外部钩子脚本，也不修改任何`core.hooksPath`或全局配置。

- 退出0：安装/版本检查通过，Git选择项目目录。
- 退出3：未安装、需要更新，或Git未选择项目目录/选择未核实。JSON分别给出文件状态和选择状态，不能当作自动触发已启用。
- 其他非零：参数、冲突或安装错误；原文件/回滚点保留。

Git不会随clone/pull复制`.git/hooks`，所以首次初始化及更新后需执行上述项目安装步骤。后置钩子不自动修改仓库或升级自身。当前仅支持macOS/Linux的主checkout；`.git`指向仓外的linked worktree及Windows不自动安装，也不为适配它们扩大写入范围。

这些是本地Git的可选保护，不是不可能绕过的安全边界。公开提交仍遵守[提交与公开安全](PROTOCOL_COMMON.md)。

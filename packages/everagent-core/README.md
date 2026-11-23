# 旧 core 路径：仅保留原生 adapter 兼容桥

身份/session、Git 引擎和个人资料维护工具的实现已移出公开当前源码树，由已安装的 eacli 拥有。本目录不再是 Go 模块，不可用于编译 eacli；旧 Git 历史、module/tag/cache 不因迁移而被清除。

公开提交使用 `scripts/egit.sh` / `scripts/ecommit.sh`，要求已安装 eacli >=11.0.0；规则见[提交与公开安全](../../docs/PROTOCOL_COMMON.md)。学习页面的独立 Go 适配器位于[应用目录](../../apps/everagent-learning/README.md)，不依赖 eacli。

当前仅保留 DSH/OpenCode 两个 `file://` 兼容桥：它们加载当前用户安装目录中由 eacli 导出的 10.1.0 adapter，不含身份识别实现，不寻找私仓源码，也不改变型号或凭据。旧 profile 的文件 URL 尚未在空闲维护窗口迁移，故不宣称此目录已彻底清理。对应用户须先显式导出 adapter，再在原 profile 的空闲维护窗口改为稳定安装路径；本轮没有重启或编辑原 profile。

```bash
eacli session adapter --harness dsh --output "$HOME/.local/share/everagent/eacli-adapters/10.1.0/dsh_plugin.mjs" --apply --json
eacli session adapter --harness opencode --output "$HOME/.local/share/everagent/eacli-adapters/10.1.0/opencode_plugin.mjs" --apply --json
```

公开资料工具使用 `eacli docs --help` 或本仓 `scripts/edocs.sh`；会话查询使用 `eacli session --help`。兼容桥不构成已核验模型、安装成功或服务已重载的证明。所有现有使用者完成路径迁移后，才删除这些桥文件。

# EverAgent 工作区搭建与两仓协作

> **一句话**：`EverAgent`（公开）是知识主体，`EverAgent-infra`（私有）是基础设施与设备家底。两仓各自独立clone/pull；公开阅读无需工具，维护入口仅依赖已安装eacli，不要求并排checkout。

换机（如 MBP 重装）或第一次拉下来，先读这一篇。

---

## 一、两仓是什么关系

| 仓库 | 可见性 | 装什么 | 谁维护 |
|------|--------|--------|--------|
| **EverAgent** | 🌐 公开 | A–E 类全部知识资产（报告/wiki）+ 方法论 + 脚本 + 协议 | 对话即学习，持续开源 |
| **EverAgent-infra** | 🔒 私有 | F 类：VPS 管理档案 + `infra/`（VPS、各设备档案、代理配置模板） | 修复驱动，含 AWS 账号/IP/SSH/Tailscale，**永不进公开仓** |

**为什么拆两仓**：EverAgent 要开源，但设备档案含敏感基础设施信息，不能公开。2026-07-27 拆分，公开仓历史已彻底脱敏（文件 + commit message 双清）。

**它们不是submodule**：两仓各自独立，公开薄脚本不读取、定位或构建私仓源码。私有操作必须另行确认目标和授权，不由公开任务的cwd推断。

---

## 二、首次搭建（换机 / 新机必做）

公开阅读只需克隆公开仓；无需私仓、eacli或模型账号：

```bash
git clone https://github.com/Everloster/EverAgent.git
cd EverAgent
```

需要Git保护或资料工具时，先通过独立、已获授权的安装流程准备eacli **>=11.0.0**，然后核对`eacli --version`的plain release输出。公开仓不提供core源码、安装器或自动build/install。薄入口按显式`EACLI_BIN`、`$HOME/.local/bin/eacli`、PATH依次选择；选中程序缺失、不可执行或版本非法/过旧时失败，不回退普通Git、不寻找私仓。

每个获授权的clone单独检查项目钩子（macOS/Linux），需要时显式安装：

```bash
scripts/egit.sh hooks status
scripts/egit.sh hooks install
```

这固定转发`eacli git hooks --repo-root ROOT <args>`，ROOT绑定脚本所在公开checkout。对其他已获授权的仓，使用已安装eacli并显式传入该仓的canonical ROOT；不会自动寻找并排目录。安装器只更新目标clone的`.git/hooks`，不设置`core.hooksPath`、不碰全局钩子或安装服务。退出3表示需查看安装/路由状态，不代表已全部生效；规则、回滚与旧版迁移见[项目钩子](PROJECT_HOOKS.md)。

---

## 三、git 身份（两仓都要）

两仓都用双身份：公开仓Author来自已暂存的身份policy，私仓Author来自eacli内置策略；Committer是当前真实模型或用户明确给出的有效声明，不借全局身份或其他会话。公开仓走`scripts/ecommit.sh`，私仓绑定自己的ROOT和身份策略，规则统一在已安装eacli中执行，不恢复质量门禁。

```bash
eacli session current --json
scripts/egit.sh identity --json
scripts/ecommit.sh -m "更新工作区说明"
```

从子目录调用也会定位到同一仓库根目录。身份来源、提交消息、暂存内容和提交后的验证见 [提交与公开安全](./PROTOCOL_COMMON.md) §B–C。身份未核实时仍可读取和编辑获授权的文件。

---

## 四、日常更新（各自 pull）

两仓独立，**分别拉**：

```bash
# 公开仓
cd ~/<your-workspace>/EverAgent && git pull --ff-only

# 私有仓
cd ~/<your-workspace>/EverAgent-infra && git pull --ff-only

# 回到公开仓根目录检查钩子；需要时显式安装。
cd ~/<your-workspace>/EverAgent
scripts/egit.sh hooks status
scripts/egit.sh hooks install
# 其他已获授权的仓用eacli git hooks --repo-root <该仓canonical ROOT> status|install。
```

> **历史重写恢复**：公开仓 2026-07-27 做过历史脱敏。旧 clone 出现分叉时，先 fetch 并检查
> 本地提交、工作区和远端差异；恢复方案按 PROTOCOL_COMMON §C 处理。覆盖工作区或改写历史
> 需要针对实际对象的明确授权。

---

## 五、AI 怎么在两仓间工作（路由约定）

AI先读公开仓[AGENTS.md](../AGENTS.md)，按用户**意图和授权目标**工作，不从当前目录推断跨仓权限：

- **A–E类**（学X / demo / 播客 / repo / 上网）→ 在公开仓内进入对应领域并读局部说明。
- **F类**（设备 / VPS / 网络维护）→ 先确认用户授权的私有目标与实际位置，再读该仓局部说明；不自动寻找并排目录、搬入原始资料或扩大安装/发布权限。

私有目录组织和安装细节由私有环境自己的说明拥有。公开Git/资料薄入口只绑定本仓ROOT，不能兼任跨仓定位器。

> 公开仓 `.gitignore` 已兜底忽略 `/infra/` 与 VPS 档案文件：即便本地把私有仓内容软链/复制进公开仓目录，也不会误提交到公开仓。

---

## 六、红线（两仓通用）

- 密钥 / SSH 私钥 / 节点 UUID / Reality 密钥 / 订阅链接 → **两仓都不入库**，只存个人密码库。
- 公开仓：任何设备档案、真实 IP、AWS 账号、域名 → 不进（含 commit message）。
- 私有仓：可记内网 IP / 主机名 / 设备指纹等非密钥信息；密钥仍不入。
- 工作机（公司设备）另有更强的公司保密红线，见私有仓对应设备档案。

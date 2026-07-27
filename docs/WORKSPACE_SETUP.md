# EverAgent 工作区搭建与两仓协作

> **一句话**：`EverAgent`（公开）是知识主体，`EverAgent-infra`（私有）是基础设施与设备家底。两仓**并排放**、各自独立 clone/pull，靠约定协同——本文说清怎么摆、怎么更新、AI 怎么找。

换机（如 MBP 重装）或第一次拉下来，先读这一篇。

---

## 一、两仓是什么关系

| 仓库 | 可见性 | 装什么 | 谁维护 |
|------|--------|--------|--------|
| **EverAgent** | 🌐 公开 | A–E 类全部知识资产（报告/wiki）+ 方法论 + 脚本 + 协议 | 对话即学习，持续开源 |
| **EverAgent-infra** | 🔒 私有 | F 类：`DeviceNode.md` + `infra/`（VPS、各设备档案、代理配置模板） | 修复驱动，含 AWS 账号/IP/SSH/Tailscale，**永不进公开仓** |

**为什么拆两仓**：EverAgent 要开源，但设备档案含敏感基础设施信息，不能公开。2026-07-27 拆分，公开仓历史已彻底脱敏（文件 + commit message 双清）。

**它们不是 submodule**：故意不挂 submodule（避免公开仓暴露"存在一个私有 infra 仓"及其地址）。两仓**各自独立**，靠下面的目录约定并排协作。

---

## 二、首次搭建（换机 / 新机必做）

在同一个父目录下把两仓**并排 clone**（关键：`EverAgent-infra` 紧挨 `EverAgent`）：

```bash
cd ~/TraeWorkspace          # 或你惯用的工作根目录
git clone https://github.com/Everloster/EverAgent.git
git clone https://github.com/Everloster/EverAgent-infra.git   # 私有，需 gh 已登录 Everloster
```

得到：

```
~/TraeWorkspace/
├── EverAgent/          # 公开仓（当前所在）
└── EverAgent-infra/    # 私有仓（并排）
```

**校验搭好了**：

```bash
ls ~/TraeWorkspace/EverAgent-infra/DeviceNode.md && echo "✅ infra 就位"
```

> 私有仓 clone 不下来？→ `gh auth status` 确认已登录 Everloster 且有 `repo` scope；或用 `gh repo clone Everloster/EverAgent-infra`。

---

## 三、git 身份（两仓都要）

两仓都用**双身份**：Author = 仓库主人 Everloster，Committer = 当前 Agent。

- **公开仓**：提交走 `scripts/ecommit.sh`（自动注入 Author），详见 [docs/PROTOCOL_COMMON.md](./PROTOCOL_COMMON.md) §C。
- **私有仓**：无 ecommit 脚本，提交时手动带 Author：
  ```bash
  GIT_AUTHOR_NAME="Everloster" GIT_AUTHOR_EMAIL="2820419+Everloster@users.noreply.github.com" \
    git commit -m "..."
  ```

每台机器首次还需设 Committer（本机 Agent 身份），例：
```bash
git config user.name "<当前 Agent 名>"
git config user.email "noreply@<vendor>.com"   # 必须含 noreply@
```

---

## 四、日常更新（各自 pull）

两仓独立，**分别拉**：

```bash
# 公开仓
cd ~/TraeWorkspace/EverAgent && git pull

# 私有仓
cd ~/TraeWorkspace/EverAgent-infra && git pull
```

> ⚠️ **历史重写提示**：公开仓 2026-07-27 做过一次历史脱敏（force push）。若某台旧 clone `git pull` 报分叉/冲突，且**无本地未推送改动**，直接对齐远端即可：
> ```bash
> git fetch origin && git reset --hard origin/main
> ```

---

## 五、AI 怎么在两仓间工作（路由约定）

AI 读公开仓 `AGENTS.md` 即知按**意图**路由（不看当前目录）：

- **A–E 类**（学 X / demo / 播客 / repo / 上网）→ 全在公开仓 `EverAgent/` 内，正常干活。
- **F 类**（"设备 X 有问题 / 看看这台机器 / VPS 怎样"）→ 去**并排的 `../EverAgent-infra/`**：
  - VPS / 代理网络 → `EverAgent-infra/DeviceNode.md`
  - 终端设备 → `EverAgent-infra/infra/devices/{hostname}.md`
  - F 类协议 → `EverAgent-infra/infra/AGENTS.md`

**AGENTS.md 里所有 `私有仓 infra/...`、`私有仓 DeviceNode.md` 的指针，实际路径都是 `../EverAgent-infra/` 下的对应文件**（前提：按 §二并排 clone）。

> 公开仓 `.gitignore` 已兜底忽略 `/infra/` 与 `/DeviceNode.md`：即便本地把私有仓内容软链/复制进公开仓目录，也不会误提交到公开仓。

---

## 六、红线（两仓通用）

- 密钥 / SSH 私钥 / 节点 UUID / Reality 密钥 / 订阅链接 → **两仓都不入库**，只存个人密码库。
- 公开仓：任何设备档案、真实 IP、AWS 账号、域名 → 不进（含 commit message）。
- 私有仓：可记内网 IP / 主机名 / 设备指纹等非密钥信息；密钥仍不入。
- 工作机（DeviceNode）另有更强的公司保密红线，见其设备档案。

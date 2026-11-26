# Agent 演义：演示项目与离线机制检查

[返回产品总览](../../reports/Agent演义_00_Orca与T3Code_任务接力_20261126.md)。本目录提供可打开的自拟项目、针对固定源码的探针和教学图。代码与探针不调用模型，不读取真实产品会话。

## 先打开演示项目

在本目录运行，只需 Python 3：

```sh
cd web-project
python3 -m unittest discover -s tests -v
python3 api/server.py --port 4188
```

浏览器打开 `http://127.0.0.1:4188`。项目包含前端、搜索 API 与分页，可检查搜索、标签、空状态和翻页；完整合同见[项目 README](web-project/README.md)。代码由报告作者实现，不是 Agent 生成表现的基准。

想在 Orca 或 T3 练习，可以将 `web-project` 复制到独立目录并初始化 Git，再作为演示项目加入。只使用这份样例，不必导入 EverAgent 或私人会话。任务路线见主篇 17–19。

## 运行固定源码探针

在本目录运行以下命令，需要 Git、Bun。源码可位于任何目录，但 HEAD 和被读取的文件必须与指定提交一致。不要为实验切换正在工作的产品仓；以下示例建立独立源码副本。

```sh
git clone https://github.com/stablyai/orca.git orca-source
git -C orca-source checkout --detach 60eb66f230d445107a32e55eae695d7090087acf
git clone https://github.com/pingdotgg/t3code.git t3-source
git -C t3-source checkout --detach 2b0f633db3ba23e692750be2f578ecb089d6a852
bun probe.ts orca-source t3-source result-local.json
python3 search_example.py
```

探针没有第三方 JavaScript 依赖，不启动 Orca、T3、CLI provider 或 MCP。它从 Git 读取固定版本并与磁盘内容比较，然后以 Bun 移除类型并运行选定的纯函数。提取范围由固定源码标记限定；缺失标记或残余 import 会直接失败。Orca 的 Claude 输入队列直接从原文件导入，只含类型的 SDK import 不参与运行。

## 验证范围

`results.json` 是 2026-11-26 在 Bun 1.3.11 下的真实结果：32 项检查通过。其中包括 T3 会话切换、历史筛选、上下文容量、返回 provider 的历史锚点，Orca DAG 收敛、worker 回报准入和消息队列的写入边界。

两份上游录制分别含 147 与 38 条记录。探针按原顺序把它们交给教学观察器：Codex 按 thread 维护运行状态，Claude 按 command UUID 维护生命周期。观察器验证“子任务结束时父任务仍在运行”及两组 queued → started → completed 序列。它**不是 T3 生产 adapter 或完整 orchestrator 的重放**。

来源质量也不同：Codex 文件标为录制器产物；Claude 文件标为真实 `/compact` 捕获加 peer-origin 帧的手工移植，不能视为全程未经加工的录屏。记录中的 SDK/CLI 版本只属于那个样本。

这些检查不验证真实模型的缓存命中、推理质量、费用、UI、工作区恢复或持久化事务。相应解释集中在技术附录。旧 `search_example.py` 保留五项纯函数测试；新增网页项目有九项 API／页面服务测试。两者验证自拟功能合同，均不证明某个 Agent 完成过该项目。

## 本轮产品操作的实际范围

2026-11-26，网页项目九项测试通过；在 Orca 内置浏览器核对 `search` 得到 3 个结果、加 Docs 后得到 1 个且在第一页、中文与 Docs 得到空结果、解除标签后得到 1 个中文结果。页面截图用于说明验收对象。前端有最新请求优先处理，本轮未做网络延迟故障注入。

T3 CLI 0.1.8 使用独立数据目录启动本地环境，经配对进入界面，关闭历史导入选项，仅加入独立演示仓，检查新 thread 草稿及模型选择控件。没有提交模型输入，没有执行切换、委派或计费任务。配对材料、主机信息和私人配置不保存在本目录。

产品篇依据的 T3 固定源码／指南比该 CLI 更新。官方产品配图用于定位功能，不是本轮操作截图；具体图片来源与两仓 MIT 许可附在 `paper_assets/agent-yanyi` 中。

## 图与源码来源

`diagrams.py` 使用 Pillow 输出 PNG 与 SVG；可用 `--font /path/to/CJK-font` 指定中文字体。图是依据本卷源码分析自绘的教学示意，不是产品截图。

```sh
python3 diagrams.py
```

学习工作台已运行时，可验证 23 篇完整 Markdown、对应 HTML 结构、来源脚注与本地链接，以及本系列 PNG 的字节内容，同时检查四份 SVG 源图的 XML。当前阅读接口不提供 SVG，因此报告中的图片入口使用 PNG；SVG 留在仓库供编辑与导出。

```sh
python3 verify_reader.py --base http://127.0.0.1:4173
```

这项检查验证阅读器返回的内容，不代替浏览器或产品 UI 的实机交互测试。

完整源文件在原公开仓，实验只保存引用与哈希，不复制源码树或原始协议全文。主要入口：

- [T3 切换策略](https://github.com/pingdotgg/t3code/blob/2b0f633db3ba23e692750be2f578ecb089d6a852/apps/server/src/orchestration-v2/ProviderSessionTransitionPolicy.ts)
- [T3 历史预算](https://github.com/pingdotgg/t3code/blob/2b0f633db3ba23e692750be2f578ecb089d6a852/packages/provider-core/src/server/handoffBudget.ts)
- [Orca 消息队列](https://github.com/stablyai/orca/blob/60eb66f230d445107a32e55eae695d7090087acf/src/main/claude/sdk-transport/claude-agent-sdk-user-message-queue.ts)

新增探针与教学代码采用本仓公开代码许可；被读取的上游代码保留其原仓许可。

# AI/ML — 未解问题池（open-questions）

> 报告结尾「我还没搞懂什么」的具体问题汇入此处，形成持续学习的拉力。
> 对话开场时 AI 可主动提议："上次留的这个问题要不要继续？"
> 维护规则：追加式。解决后标注 ✅ 并注明在哪篇报告/对话中解决，不删除。

---

## 待解决

- **[投机解码]** 残差分布 norm(max(0, q−p)) 的完整测度论正确性证明（来源：投机解码深度解析 20260625）
- **[投机解码]** 树形投机（SpecInfer/Medusa）接受率收益如何量化？分支数 vs 验证开销的最优点
- **[投机解码]** draft/target 最优容量比是否有理论刻画，还是纯经验调
- **[全局工作空间]** J-space 的"点火/ignition"是否真被证明？Dehaene 说没证全或无阈值进入，作者初稿后补的 fig 29 是"部分回应"还是"实质证明"？需读长论文 4.1.1（来源：J-space 精读 20260707）
- **[全局工作空间]** J-space 是否为一条**统一**的意识流？Eleos AI 质疑这些特权表征可能不汇成单一 workspace，判定标准是什么？（来源：J-space 精读 20260707）
- **[全局工作空间]** J-lens 雅可比对"未来输出"的因果影响如何精确定义（对最终 token 梯度 vs 跨多步累积）；Nanda 的 `J·W_U`/"到 penultimate layer 的 Jacobian"具体算法（来源：J-space 精读 20260707）
- **[全局工作空间]** counterfactual reflection training 的完整损失函数——"只训它被打断时会说什么"如何形式化（来源：J-space 精读 20260707）
- **[进化 Harness]** Meta-Harness 的晋级判据（min_delta=1、3 trial 均值）会不会过拟合 dev？dev +20.2 点但 test 只 +16.7，这 3.5 点是正常泛化损耗还是轻度过拟合？（来源：进化 harness 精读 20260707）
- **[进化 Harness]** "确定性代码 > 提示词"是否依赖打分公式里的 token 惩罚项？拿掉 `-0.005×tokens` 后胜出的会不会翻转成提示词类？（来源：进化 harness 精读 20260707）
- **[进化 Harness]** 跨家族迁移几乎为零（Nemotron +0.4）卡在哪？是提示词 playbook，还是工具接口/格式约定也带家族特异性？（来源：进化 harness 精读 20260707）
- **[进化 Harness]** 二手爆款文的"1/7 成本"出处？一手只给 token 单价（≈20 倍价差）和单次跑 $120–160，未见"1/7"（来源：进化 harness 精读 20260707）
- **[Bitter Lesson × Harness]** "能力缺口填补物 vs 保证型需求"能否**事前**形式化判定哪段确定性代码会 BLE-hobbled？PostHog 的 todo_write（活）与 JSON retry（死）都是确定性代码，事后好解释、事前难预测（来源：Bitter Lesson vs Harness 推演 20260707）
- **[Bitter Lesson × Harness]** "两把镰刀"哪把更快削平 harness——agentic-RL（模型吸收）还是 MCP 生态（协议标准化）？机制不同，结局不同（来源：同上）
- **[Bitter Lesson × Harness]** 进化循环真的完全免疫镰刀吗？"设计 reward 和搜索空间"会不会也被 meta-search（AlphaEvolve 式）吃掉，人退到哪一层？（来源：同上）

---

## 已解决

- （暂无）

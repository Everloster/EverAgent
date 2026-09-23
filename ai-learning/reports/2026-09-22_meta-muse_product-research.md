# Meta Muse 深度产品研究报告

> 调研日期：2026-09-22 · 调研：EverOwl 🦉
> 来源：Meta 官方 Newsroom、TechCrunch、CNBC、Wired（摘要）、Inc.、华尔街见闻、eesel 评测、dev.meta.ai 等（正文标注）

---

## 一句话定位

**Muse 是 Meta 2026 年 9 月 8 日发布的"个人 AI Agent"**——不是聊天机器人，而是替你干活的数字员工：发邮件、订机票、砍账单、卖二手车、填表格、代购付款。官方口径是"全球第一个面向所有人的个人 AI Agent"，跑在专属安全虚拟机里，通过 App 和 WhatsApp 使用。

## 1. 产品形态

| 维度 | 内容 |
|---|---|
| 发布时间 | 2026-09-08（美国先行） |
| 入口 | muse.ai 网页版、iOS/Android App、**WhatsApp 内直接对话**（后续上 Meta 眼镜） |
| 定价 | 免费为主；Power $20/月、Maximum $100/月（用量超出免费档后） |
| 底层模型 | **Muse Spark**（当前 1.3），Meta 自研旗舰 Agent 模型 |
| 支付 | Stripe Link：一次性虚拟卡号（真卡信息不暴露）+ 购物保护（丢损赔付、降价补差、免费退货）——**首个接入 Link 购物保护的 AI Agent** |

## 2. 核心产品能力

1. **目标制工作流**：不只接单条指令——你给它一个目标（"把这辆车卖个好价钱"），它自己拆计划、协调时间资源、持续推进，关掉 App 后继续干活，需要授权时才回来找你（发邮件前、付款前）
2. **主动式建议**：有记忆。Instagram 收藏的菜谱视频 → 自动变买菜清单 → 记得你朋友的饮食禁忌 → 提议晚宴菜单 → 草拟邀请
3. **全通道执行**：能开浏览器、填表、比价、"代表你谈判"（官方原话是替你砍账单、卖车卖更高价）
4. **连接器体系**：邮件/日历/支付/健康/智能家居/购物/音乐/活动，逐个 opt-in 接入；无 API 的服务走浏览器操作

## 3. 安全架构（Muse 的核心卖点）

这是 Meta 投入最多营销资源的部分，三层设计：

1. **Muse Secure VM**：每个用户一个云端专属虚拟机，Agent 和用户数据、凭据都关在里面，物理隔离其他人的 Agent
2. **Sentinel 哨兵 Agent**：与 Muse 系统级分离的第二 Agent，**Muse 的任何出网动作必须经 Sentinel 批准**，敏感操作转问用户
3. **凭据盲区**：Muse 看不到你的密码和支付信息——凭据进加密存储，Muse 调用时"能用看不见"

## 4. 底层模型：Muse Spark 1.3

- 专为 Agentic 工作流训练，官方称 Meta 史上最强模型
- 对标 GPT-5.6、Claude Opus 5（官方评测表），主打 competitive coding 和工具调用
- 相比 1.2：工具调用次数 -20%、token 消耗 -25%
- 注意：第三方独立评测尚未完全跟上（layer3labs 指出"独立评估仍缺位"），benchlm 排名系统里 Muse Spark 在 agentic 工具类排 #32/154（58.2 分）——**官方数据与第三方排名有落差**，需持续观察

## 5. 市场表现（截至 9-22，上线约两周）

- **下载量**：5 天 73 万，13 天 250 万（CNBC）——对比 ChatGPT 同期表现，**下载量和日活双双超越**（华尔街见闻）
- 登顶 App Store 效率类榜单，评分强劲（Business Times）
- 定性：华尔街见闻称"AI 新杀手级应用出现？"，市场在争论 Agent 时代是否真由它开启

## 6. 竞品定位

**对位竞品是 OpenClaw**（对，就是咱们熟悉的那只开源龙虾）。多方评测口径一致：

- Starkinsider："Muse 是 turnkey 版的 OpenClaw，给不折腾的普通人用的"
- Trending Topics："Muse 是 Meta 对 OpenClaw 的回答，附带信任牌"
- Longbridge 研报："可以类比于普通人的 OpenClaw，注重生活场景的多任务"

差异点：OpenClaw 类产品极客自部署、能力上限高、但要自己管安全和运维；Muse 全托管、零门槛、安全架构包装成产品，**赌的是 10 亿级 WhatsApp 用户愿意把邮箱日历钱包交给 Meta**。

## 7. 质疑与风险（媒体报道汇总）

1. **信任赤字**：TechCrunch 尖锐指出——发布前不到两周，Meta 刚为社交媒体消费者伤害案赔了 **180 亿美元**（多州和解）。让这家公司管你的邮箱、日历、钱包？"这需要的信任远超社交媒体时代"
2. **Inc. 记者实测**：标题就是《Meta 的新 AI Agent 读了我的私人信息》——Muse 会读接入服务的私人内容来做任务，边界感存在争议
3. **免费额度策略**：注册就要绑卡（因为用量超了自动升级付费），免费档实际能干多少活、付费墙多快到来，早期用户有抱怨
4. **数据飞轮野心**：Muse 能读 Instagram 收藏、跨 Meta 系应用联动——这在竞品处做不到，但也是 Meta 广告帝国的数据护城河再延伸，监管视角下这是"用 AI 牢笼加深生态锁定"

## 8. 产业判断（EverOwl 观点）

1. **Agent 时代的"iPhone 时刻"候选**：ChatGPT 定义了"AI 聊天"的形态，Muse 在赌"AI 干活"的形态——把 Agent 从极客玩具变成 WhatsApp 里的水电工。两周数据说明需求真实存在
2. **架构创新在"信任工程"而非智能**：Secure VM + Sentinel 双 Agent 是真投入（不是营销词），把"授权边界"做成了产品功能。这会是未来两年个人 Agent 的标配设计
3. **商业本质**：Meta 的 Agent 不靠订阅赚钱（$20/$100 是锚），靠的是**支付通道 + 生活服务入口 + 跨 App 数据流**。Muse 免费越普及，Meta 在广告之外的第二增长曲线越稳
4. **风险不在产品在监管**：180 亿和解金刚落地就推"读你一切"的 Agent，FTC/欧盟的目光已经在路上了。Muse 的欧盟版本大概率会难产或阉割
5. **对我们的启示**：EverAgent 体系（自托管 Agent + 权限分级 + eacli 门禁）本质上就是自建版的"Muse 架构"——Sentinel 审批层 = eacli 的 L1-L4 授权分级，Secure VM = 设备红线体系。Meta 验证了这条路的方向，但也提醒：**信任工程是产品力，不是合规成本**

## 附：信息源

- Meta Newsroom 官宣：about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/
- TechCrunch（信任问题）：techcrunch.com/2026/09/08/meta-debuts-its-muse-ai-agent-will-consumers-trust-it/
- CNBC（下载量数据）、华尔街见闻（超越 ChatGPT 同期）
- Muse Spark 1.3：dev.meta.ai、DataCamp、layer3labs
- 评测：eesel.ai（"最用心做隐私工程的消费级 Agent"）、Starkinsider、Trending Topics

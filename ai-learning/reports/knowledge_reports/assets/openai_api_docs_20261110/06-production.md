# Production｜生产部署、性能、安全与访问

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md)

应用上线后，需要同时管理响应速度、费用、评估、权限和数据。本卷按这些问题整理配置方法；云平台、身份联合与 Terraform 的专题保留独立入口，便于按部署环境查阅。

## Go live｜上线

<a id="doc-149"></a>
### Production best practices｜生产最佳实践
[原文](https://developers.openai.com/api/docs/guides/production-best-practices)

从原型转入生产时，应分开管理开发与生产项目，明确组织计费、密钥和权限，再根据流量设计缓存、负载分配、重试及监控。响应速度与费用需要结合模型、输入输出长度和请求次数评估。

Responses JSON 可按支持方式使用 zstd 压缩，WebSocket 也有消息压缩选项。它们减少网络传输字节，逻辑 token 数仍按原始请求内容计算。

<a id="doc-26"></a>
### API deployment checklist｜部署检查表
[原文](https://developers.openai.com/api/docs/guides/deployment-checklist)

上线前，检查应用实际使用的接口、模型、推理强度、回答长度和工具配置。多轮任务还需确认 `phase`、历史续接、上下文压缩及缓存处理；图像任务应明确 detail，长任务应处理后台运行或 WebSocket 的恢复。

Tool search、PTC、多 Agent 和异步工具各解决不同问题，按工作负载需要采用。安全标识、监测、限流和过载处理也应接入应用的运行逻辑。每项配置在原文中都有对应专题。

<a id="doc-27"></a>
### API keys and service accounts｜密钥与服务账号
[原文](https://developers.openai.com/api/docs/guides/api-keys)

API key 是请求凭据，service account 是供应用使用的非人类身份，两者可以配合使用。个人开发使用自己的项目 key；部署应用或自动任务使用独立 service account；组织管理使用 Admin key。

Key 的 scope 只能限制该身份已有的权限。完整密钥通常只在创建时返回，应及时保存到合适的秘密存储，按生命周期轮换或撤销。支持的工作负载也可以通过身份联合取得短期 token。

## Performance and quality｜性能与质量

| 原文 | 中文导读 |
|---|---|
| <a id="doc-87"></a>[Fast mode](https://developers.openai.com/api/docs/guides/fast-mode) | Fast mode 以较高单价换取更快、更稳定的处理速度，可在请求或项目中选择。支持的模型接受 `service_tier: fast`，旧名称 `priority` 也有对应兼容规则。实际处理档位以响应的 `service_tier` 为准；流量增长过快时，部分请求可能回到标准档位。缓存折扣、限流和地域支持需同时核对。 |
| <a id="doc-202"></a>[Ultrafast mode](https://developers.openai.com/api/docs/guides/ultrafast-mode) | Ultrafast 是适用于受支持模型的更高速处理档位，按更高费率和独立限流运行。请求中设置相应模型及 `service_tier: ultrafast`。频繁调用工具时，持久 WebSocket 可以减少网络往返对速度收益的抵消；也可按指南使用 HTTP。 |
| <a id="doc-114"></a>[Latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization) | 降低延迟可以从模型速度、输入输出长度、请求次数和并行处理入手。流式展示能缩短用户看到第一段结果的等待；固定逻辑或已有数据可以直接处理，未必需要模型调用。合并请求与拆分并行各有取舍，应按实际链路测量。 |
| <a id="doc-147"></a>[Predicted Outputs](https://developers.openai.com/api/docs/guides/predicted-outputs) | Predicted Outputs 适合大部分内容已知、只需少量修改的文件生成。在受支持的 Chat Completions 模型上，把预期文本放入 `prediction`，服务可以利用与实际输出一致的部分降低延迟。返回用量区分接受和拒绝的预测 token，被拒绝的部分也可能计费。 |
| <a id="doc-142"></a>[Optimizing LLM Accuracy](https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy) | 提高准确率，先判断模型缺少材料，还是已有材料却没有按要求处理。Prompt 可以明确任务与行为，RAG 补充相关信息，微调让特定模式更稳定；选择方法应针对实际错误。评估标准还要考虑业务中一次失败的代价，以及目前效果是否足以使用。 |

## Evaluation｜评估

| 原文 | 中文导读 |
|---|---|
| <a id="doc-85"></a>[Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | 评估先定义目标，再选择代表性数据、指标和比较方法。单次模型调用、固定工作流和多 Agent 系统的错误位置不同，应据此设计检查。确定性指标、人工评价和模型评分可以互补，模型裁判也需要校准。托管 Evals 的退役不改变这些评估方法本身。 |
| <a id="doc-97"></a>[Get started with Promptfoo](https://developers.openai.com/api/docs/guides/promptfoo-codex) | Promptfoo 用配置文件组织 prompts、providers、测试用例和 assertions，可以在终端运行，也可以让 Codex 为应用建立评估。原文以翻译比较演示结果查看与迭代。模型调用会产生费用，断言通过只说明对应条件满足，输出内容仍需检查。 |

## Cost and throughput｜成本与吞吐

<a id="doc-66"></a>
### Cost optimization｜成本优化
[原文](https://developers.openai.com/api/docs/guides/cost-optimization)

降低费用可以减少不必要的请求和输入，控制输出长度，并选用满足质量要求的较小模型。对不需要立即返回的工作，可以使用 Batch 或 Flex；面向用户的实时请求则要同时考虑等待时间。成本优化应保留任务所需的信息与准确率。

<a id="doc-152"></a>
### Prompt caching｜提示缓存
[原文](https://developers.openai.com/api/docs/guides/prompt-caching)

提示缓存复用相同前缀的已计算状态，减少重复输入处理，并按缓存费率计费。它复用的是前缀计算，当前回答仍重新生成。请求是否命中还取决于模型、配置、缓存位置和有效期。

较新模型提供隐式和显式缓存方式，可以配置断点、key 和保留时间。组织提示时尽量保留稳定前缀，将新内容追加在后面。缓存写入和读取有各自费率，重叠前缀及最小长度也会影响成本，应结合实际 usage 和诊断结果调整。

<a id="doc-151"></a>
### Prompt cache diagnostics｜缓存诊断
[原文](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics)

缓存诊断用 `comparison_response_id` 将当前请求与一个近期响应比较，帮助定位模型、工具、schema、推理设置或历史内容的变化。返回的原因和 token 估计用于排查，实际复用量仍看 usage。

比较 ID 只请求诊断，不会加载旧会话或改变缓存行为。修复后再检查真实的缓存命中与用量，确认调整是否有效。

<a id="doc-37"></a>
### Batch API｜批处理
[原文](https://developers.openai.com/api/docs/guides/batch)

Batch API 将一组请求放入 JSONL 文件，上传后异步处理，再查询状态并下载输出及错误文件。每条输入使用唯一的 `custom_id`，结果按这个 ID 配对，不依赖输出行顺序。

批处理适合无需立即返回的任务，使用独立的限流池和完成窗口。创建前检查支持端点、模型和排队限额；取消或过期后，也要分别读取已经完成与未完成的请求。

<a id="doc-93"></a>
### Flex processing｜弹性处理
[原文](https://developers.openai.com/api/docs/guides/flex-processing)

Flex 以较慢响应和偶尔的资源不可用，换取较低费用，适合评估、数据补充等低优先级工作。受支持请求设置 `service_tier: flex` 后，应用应为长任务设置合适超时。

遇到无资源错误时，可以退避等待，或按业务需要改用标准处理；是否可用和价格取决于模型及当前支持范围。

## Safety and governance｜安全与治理

| 原文 | 中文导读 |
|---|---|
| <a id="doc-174"></a>[Safety best practices](https://developers.openai.com/api/docs/guides/safety-best-practices) | 应用应结合内容审核、对抗测试、必要的人工检查和输入输出限制，处理不安全或偏离任务的行为。向用户说明产品限制，提供问题反馈途径，并通过安全标识关联具体用户。泄露的 API key 应及时撤销；涉及未成年人时采用专门的保护流程。 |
| <a id="doc-169"></a>[Red teaming](https://developers.openai.com/api/docs/guides/red-teaming) | 红队测试用对抗性输入寻找普通质量评估难以暴露的风险。Promptfoo 提供开源工具，OpenAI 也提供企业托管方案。提交给托管服务的代码和资产必须属于自己或获得明确授权，并遵守原文对第三方资产的限制。 |
| <a id="doc-207"></a>[Use Daybreak in the Responses API](https://developers.openai.com/api/docs/guides/daybreak) | Responses 请求的 `model` 选择模型，`access_programs.cyber` 选择已获准的网络安全访问计划。使用前，组织和项目必须同时具备计划与模型资格。省略该参数时的默认行为因模型而异，显式选择不兼容或未开通的计划会返回错误；参数本身不会授予权限。 |
| <a id="doc-175"></a>[Safety classifiers](https://developers.openai.com/api/docs/guides/safety-checks) | OpenAI 的安全分类器检查高风险请求，可能延迟或停止响应、发出警告，或限制相应用户和组织的访问。安全标识帮助把行为关联到具体终端用户，应在所用 API 请求中按要求提供，而不能依赖不同接口自动继承。 |
| <a id="doc-71"></a>[Cybersecurity checks](https://developers.openai.com/api/docs/guides/safety-checks/cybersecurity) | 网络安全风险等级较高的 API 模型有额外自动防护，可能因可疑行为暂时限制访问并进行审查。不同访问计划、ZDR 配置和产品入口使用各自流程。合法防御任务被标记时可按指南申诉；模型资格仍限于获批的人员、组织、项目和用途。 |
| <a id="doc-127"></a>[Misalignment monitoring](https://developers.openai.com/api/docs/guides/safety-checks/misalignment-monitoring) | Misalignment monitoring 异步检查 Agent 在敏感操作中是否正确理解用户要求。对支持的模型，监测和自动停止范围取决于接口以及上下文续接方式。被标记的行为需要检查，标记本身不证明用户违规。应用应处理 `misalignment_policy_violation` 和项目告警；停止后仍要确认此前已执行的动作。 |
| <a id="doc-176"></a>[Safety enforcement notifications](https://developers.openai.com/api/docs/guides/safety-enforcement) | 安全 webhook 发送组织级 warning 或 deactivation 通知，并提供 case ID。应用可通过 Safety Case Read API 查询可用元数据，结合自己的安全标识映射找到相关用户，再交给支持或安全团队处理。查询 case 不会撤销处置，这套通知也不同于项目级 misalignment alert。 |
| <a id="doc-203"></a>[Under-18 guidance](https://developers.openai.com/api/docs/guides/safety-checks/under-18-api-guidance) | 面向未成年人的应用需要年龄适配的说明、内容过滤、监测、举报和高风险升级流程，并满足儿童保护及隐私要求。原文还规定，处理未满 13 岁或当地数字同意年龄儿童的个人数据前，应先实施 API 零数据保留。具体产品措施需结合适用法律与条款。 |
| <a id="doc-69"></a>[CSAM guidance](https://developers.openai.com/api/docs/guides/csam-guidance) | 儿童安全应从产品设计阶段考虑，尤其是上传、消息、编辑和直播功能。专门的哈希匹配或分类技术可辅助识别风险，应用还需建立举报、响应、报告及工作人员支持流程。Moderation API 不替代专门的 CSAM 识别与处置机制。 |
| <a id="doc-64"></a>[Content provenance](https://developers.openai.com/api/docs/guides/content-provenance) | Content Provenance API 检查图像或音频中受支持的 OpenAI 来源信号，包括 C2PA 和 SynthID，并返回检测与验证结果。`not_detected` 只表示没有找到支持的信号，元数据被移除、旧模型生成或水印受损都可能导致这一结果，也不能据此排除其他 AI 来源。 |

<a id="doc-72"></a>
### Your data｜数据控制
[原文](https://developers.openai.com/api/docs/guides/your-data)

OpenAI 默认不使用 API 输入和输出训练模型，除非客户明确选择共享。数据保存还分为用于安全监测的日志，以及实现具体功能所需的应用状态。

MAM、ZDR、Private Retention、PSP 和区域存储各控制不同部分，并有资格及端点限制。`store: false` 只影响相应保存行为，不等同于开通 ZDR。使用第三方工具或云平台时，还需考虑对方的数据政策；具体功能是否适用，应查原文矩阵与协议。

<a id="doc-233"></a>
### ZDR with Private Safety Processing｜私有安全处理
[原文](https://developers.openai.com/api/docs/guides/private-safety-processing)

ZDR with PSP 将加密安全记录保存在客户控制的云存储中，供获准且经过硬件证明的自动审查环境处理。受保护内容不向人工审查开放，只有限定的安全信号和运行元数据可以离开该环境。

部署包括云存储、访问权限、密钥和生命周期设置，再注册并验证连接。一次 Validated 只说明当时验证成功，之后仍需监测；断开存储连接也不会删除已经写入的云对象。完整架构见原文白皮书。

<a id="doc-186"></a>
### Set up asymmetric keys｜注册非对称密钥
[原文](https://developers.openai.com/api/docs/guides/asymmetric-keys)

可为 PSP 解密在受支持的云 KMS 中创建 RSA-3072 非对称密钥，并向 OpenAI 注册公钥。私钥保留在客户 KMS；注册时需要准确的云资源和密钥版本，以及规定的公钥读取权限。

注册记录不会随着云密钥轮换自动更新。旧记录仍依赖旧版本时，应保留相应密钥。注册公钥本身不创建存储，也不会自动启用 PSP。

<a id="doc-76"></a>
### Decrypt PSP records｜解密客户可恢复记录
[原文](https://developers.openai.com/api/docs/guides/psp-decryption)

开启客户可恢复的 PSP 记录后，可以用原始密钥版本及记录元数据恢复内容。云 KMS 解开恢复封装，本地程序再解密记录并检查绑定信息；私钥始终留在 KMS。

如果外层还有 EKM 存储加密，应先处理这一层。只有启用对应恢复能力后写入的记录适用，旧记录不会自动转换。单独加密的模型推理内容不由客户恢复密钥解开。

<a id="doc-115"></a>
### Manage permissions｜权限管理
[原文](https://developers.openai.com/api/docs/guides/rbac)

RBAC 通过组织、项目、群组和角色分配权限。角色包含具体操作许可，用户可以直接获得角色，也可以通过群组获得；多个角色的权限取并集。项目角色只作用于该项目，组织角色可能覆盖多个项目。

API 与控制台使用对应的权限配置，API key 还受其身份的有效权限限制。修改权限后要考虑传播时间，并用目标身份验证访问；批处理等能力可能带来额外的间接权限。

## Infrastructure and access｜基础设施与访问

| 原文 | 中文导读 |
|---|---|
| <a id="doc-148"></a>[Private Link](https://developers.openai.com/api/docs/guides/private-link) | Private Link 让 Azure 工作负载通过私有网络访问区域 OpenAI API。开通后，为对应区域创建 Private Endpoint，配置私有 DNS，再向区域主机发送正常认证的请求。健康检查和跨区域切换由应用部署配合处理。支持端点以及与 IP allowlist、mTLS 的兼容性有单独限制。 |
| <a id="doc-111"></a>[IP allowlist](https://developers.openai.com/api/docs/guides/ip-allowlist) | IP allowlist 只接受来自指定 IP 或 CIDR 的 API 请求，即使密钥有效，来源不在允许范围内也会被拒绝。配置时要检查经过 NAT、代理或 VPN 后真正到达 OpenAI 的出口地址。项目与组织规则按优先关系生效；这项设置不限制平台登录。 |
| <a id="doc-112"></a>[IP egress ranges](https://developers.openai.com/api/docs/guides/ip-addresses) | 当 OpenAI 的产品访问你控制的服务时，可根据该产品发布的出口 IP 文件配置网络白名单。网段可能变化，需要定期更新。命中 OpenAI 网段只说明网络来源，不能识别某个用户或替代请求认证。 |
| <a id="doc-28"></a>[API organization blocking](https://developers.openai.com/api/docs/guides/organization-blocking) | 组织访问限制通过企业代理或 SASE 添加允许的组织 ID 请求头，规定网络内的用户可访问哪些 API organization。访问未列出的组织会被拒绝。部署时需要同时验证允许和拒绝的情况，并检查代理是否按要求传递头信息。 |
| <a id="doc-136"></a>[Mutual TLS](https://developers.openai.com/api/docs/guides/mutual-tls) | mTLS 在正常 bearer 凭据之外增加客户端证书验证。组织或项目激活信任证书后，请求需要同时提交有效凭据和可接受的客户端证书。证书、私钥、中间证书及信任根由部署方正确配置。URL、CEL 条件、证书轮换和验证限制见原文，不能只上传证书就省去 API 授权。 |
| <a id="doc-139"></a>[OpenAI on Amazon Bedrock](https://developers.openai.com/api/docs/guides/amazon-bedrock) | Amazon Bedrock 在 AWS 基础设施上运行受支持的 OpenAI 模型。Runtime 与 Mantle 都提供相应兼容接口，但模型、工具和功能覆盖不同，应用应根据需要选择端点。AWS 负责区域、访问、路由和计费，接入使用其凭据链与签名规则；数据访问和保留按 AWS 部署条件处理。 |
| <a id="doc-140"></a>[OpenAI on Google Cloud](https://developers.openai.com/api/docs/guides/google-cloud) | Google Cloud 路线处于私有预览，获批项目通过其平台使用 OpenAI 模型，由 Google Cloud IAM 管理访问并向云账号计费。管理员需要开通项目、模型与条款并赋予调用权限。Responses 的工具、状态、媒体和后台功能与第一方 API 存在差异，按原文支持表配置。 |

## Terraform｜基础设施即代码

| 原文 | 中文导读 |
|---|---|
| <a id="doc-194"></a>[Terraform provider](https://developers.openai.com/api/docs/guides/terraform) | 官方 Terraform provider 通过 Administration API 管理项目、用户、角色、服务账号、证书和限额等组织资源。使用 Admin key 初始化 provider，审阅 plan 后再 apply，并保留版本锁定记录。各类资源的导入、更新和销毁行为见专门指南。 |
| <a id="doc-116"></a>[Projects and access](https://developers.openai.com/api/docs/guides/terraform/projects-and-access) | Terraform 可以创建项目，定义最小权限角色，建立群组，再把用户或服务账号通过群组关联到项目。由其他系统管理的资源可用 data source 读取。删除赋权前检查仍需保留的访问；销毁 `openai_project` 实际执行归档，归档后不能恢复。 |
| <a id="doc-117"></a>[Service accounts](https://developers.openai.com/api/docs/guides/terraform/service-accounts) | Provider 创建 service account 时可以不分配默认角色，也不生成 API key。随后通过群组赋予所需权限，再在 Terraform 之外使用管理 API 创建密钥并保存到秘密管理器，避免密钥进入 state。已有账号可导入，凭据轮换和身份删除分别处理。 |
| <a id="doc-162"></a>[Rate limits and spend](https://developers.openai.com/api/docs/guides/terraform/rate-limits-and-spend) | 项目限流记录由 OpenAI 提供，Terraform 先查询 record ID，再更新对应模型的请求和 token 限制。Spend alert 到阈值时只发通知，不会强制停止请求。某些资源从 Terraform state 移除后，远端设置仍保留，需按资源语义处理。 |
| <a id="doc-131"></a>[Model, tool, and data controls](https://developers.openai.com/api/docs/guides/terraform/project-controls) | 项目控制规定可用模型、托管工具和已获批的数据保留方式，不授予身份访问权限。模型可用允许或拒绝列表，工具策略要考虑组织级设置的优先关系，保留策略也受组织资格限制。修改或删除时按各资源的实际行为检查结果。 |
| <a id="doc-109"></a>[Import and reconcile](https://developers.openai.com/api/docs/guides/terraform/import-and-reconcile) | 接管既有资源时，先让 Terraform 配置与远端现状一致，再导入并确认后续 plan 没有意外修改。之后才处理计划中的更新或配置漂移。导入 ID 因资源而异；只需查询可用 data source。删除、归档和仅移出 state 的含义分别核对。 |

## Workload identity federation｜工作负载身份联合

<a id="doc-232"></a>
### Workload identity federation｜总览
[原文](https://developers.openai.com/api/docs/guides/workload-identity-federation)

工作负载身份联合用已有可信身份换取短期 OpenAI token，减少长期共享密钥。身份提供方的 issuer、签名密钥和 claims 经过验证后，再按映射授予目标身份已有的权限。

API Platform 映射到项目的 service account，Codex 则通过 workspace federation rule 映射到已有的工作区用户或服务账号。两条路线配置不同，都不会自动创建用户、项目或成员关系。运行中需持续取得新断言并更新短期 token。

| 原文 | 中文导读 |
|---|---|
| <a id="doc-47"></a>[Codex federation rule reference](https://developers.openai.com/api/docs/guides/workload-identity-federation/federation-rules) | Codex federation rule 指定一个工作区主体，并用 subject、audience、精确 claims 或 CEL 条件限制哪些外部身份可以使用它。Scope、token 有效期和重放保护进一步收窄访问。规则只作用于既有主体及其权限，可以停用或归档。 |
| <a id="doc-53"></a>[X.509 certificates](https://developers.openai.com/api/docs/guides/workload-identity-federation/x509) | X.509 身份联合从经过验证的客户端证书派生身份，再换取短期 OpenAI bearer token。后续 API 请求仍同时提交 token 和有效 mTLS 证书。配置包含证书信任、属性映射与续期，适用范围不同于 SPIFFE X.509-SVID。 |
| <a id="doc-59"></a>[Kubernetes](https://developers.openai.com/api/docs/guides/workload-identity-federation/kubernetes) | Kubernetes 使用符合 OIDC 要求的 projected service-account token，配置 issuer、audience、公开 JWKS 和准确 subject。旧的 Secrets service-account token 不受支持。自管集群轮换签名密钥时，还需同步 OpenAI 使用的 JWKS。 |
| <a id="doc-55"></a>[AWS](https://developers.openai.com/api/docs/guides/workload-identity-federation/aws) | AWS 可以提供 STS 签发的 outbound OIDC JWT，EKS 也可以提供 projected service-account token。OpenAI 核对实际 issuer、audience 和身份映射后交换短期 token；SigV4 请求和 STS 临时 access keys 不作为这条流程的 subject token。 |
| <a id="doc-60"></a>[Microsoft Azure](https://developers.openai.com/api/docs/guides/workload-identity-federation/microsoft-azure) | Azure 可使用 managed identity 的 Entra token，AKS 可使用 projected service-account token。请求的 audience、实际 token claims 与 OpenAI provider 配置必须匹配，issuer、租户和身份信息应以实际签发结果为准。 |
| <a id="doc-57"></a>[Google Cloud](https://developers.openai.com/api/docs/guides/workload-identity-federation/google-cloud) | Google Cloud 可使用附加 service account 从 metadata 服务取得的 Google 签名 token，也可使用 GKE 的 projected token。两者的 issuer 和身份来源不同，需分别配置并在运行时取得新 token，再映射到 OpenAI service account。 |
| <a id="doc-61"></a>[Oracle Cloud Infrastructure](https://developers.openai.com/api/docs/guides/workload-identity-federation/oracle-cloud) | OCI 实例主体向同租户的 identity domain 请求 token，再由 OpenAI 验证并映射到 service account。应用需要核对真实 audience 和稳定身份 claims。在 OKE 中，普通实例主体通常代表工作节点，不能直接当作某个 Pod 的独立身份。 |
| <a id="doc-56"></a>[GitHub Actions](https://developers.openai.com/api/docs/guides/workload-identity-federation/github-actions) | GitHub Actions 中，获得 `id-token: write` 的 job 可请求 OIDC token，用它换取短期 OpenAI 凭据。映射应约束 repository、ref、workflow_ref 和 environment 等真实 claims。这项权限只用于申请身份 token，不授予仓库内容写权限。 |
| <a id="doc-62"></a>[SPIFFE](https://developers.openai.com/api/docs/guides/workload-identity-federation/spiffe) | SPIFFE 路线使用 JWT-SVID，要求其具有所需 claims、`kid` 和可验证的 JWKS 签名。SPIFFE ID 表示工作负载，issuer 和 audience 各有独立含义。应用还应保护 Workload API socket，并在运行中刷新断言；X.509-SVID 不适用这条交换流程。 |
| <a id="doc-58"></a>[Idira](https://developers.openai.com/api/docs/guides/workload-identity-federation/idira) | Idira SWA 为工作负载分配 SPIFFE ID 并签发 JWT-SVID。应用通过 Workload API 取得新断言，OpenAI SDK 将它交换为映射 service account 的短期 access token。Discovery、签名密钥、断言交付与账号映射都需正确配置。 |

## Operations｜运行维护

| 原文 | 中文导读 |
|---|---|
| <a id="doc-161"></a>[Rate limits](https://developers.openai.com/api/docs/guides/rate-limits) | 限流可能按请求数、token 数及其他维度计算，并受到组织、项目和共享模型额度约束。响应头提供当前限制与剩余量，应用可据此安排速率。短暂限流或过载按 `Retry-After` 和退避策略处理；余额、花费上限和用量资格问题则需要先解决原因。 |
| <a id="doc-189"></a>[Spend limits](https://developers.openai.com/api/docs/guides/spend-limits) | Spend alert 到阈值时发送通知，API 继续运行；hard spend limit 到适用上限时会阻断请求，并返回组织或项目花费限制错误。执行有延迟，记录的费用可能略高于设定金额。组织与项目上限可以同时作用，另有 OpenAI 批准的 usage limit。 |
| <a id="doc-16"></a>[Admin APIs](https://developers.openai.com/api/docs/guides/admin-apis) | Admin APIs 用独立管理凭据自动处理邀请、项目、用户、密钥、模型访问、花费和审计日志等组织事务。管理端点需要 Admin API key，普通推理请求使用项目或服务账号凭据，二者不能互相替代。 |
| <a id="doc-81"></a>[Error codes](https://developers.openai.com/api/docs/guides/error-codes) | 错误处理应结合 HTTP 状态、稳定的 `error.code` 与 SDK 异常。相同的 429 可能表示请求过快、余额耗尽、花费上限或组织用量限制，恢复方式各不相同。连接超时、WebSocket 到期和状态丢失也应按对应错误处理，避免只匹配提示文案。 |

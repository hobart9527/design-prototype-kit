# Spec Interpretation Rules

编写正式体验契约、建立 Spec Packet、锁定语义或解决来源权威冲突时读取。
产品发现与设计机会使用 [product understanding](../01-foundations/product-understanding.md)。

## 1. Authority

1. 产品来源（用户指定的 brief、OpenSpec spec、现有页面、产品描述）决定产品行为、领域实体、状态、枚举、权限和结果；设计层不得超越其边界。
2. `product.md` 是引用产品来源的派生摘要；本次明确的来源版本和用户澄清优先。来源更新后先核对并更新摘要，不能让旧摘要覆盖新来源。
3. design 解释实现方法；proposal 解释目标和范围。两者不得覆盖产品来源。
4. Foundation、词典、切片契约是独立设计事实，与引用的产品来源冲突时失效，但不进入产品来源生命周期。
5. 执行拆分（OpenSpec tasks 或其他）不是产品意图证据。

## 2. Evidence Status

### explicit

原文直接支持结论。引用最小充分原文，不用长段摘要。

### derived

多个 explicit 锚点共同必然推出结论。必须列锚点和推理链：

```text
A says actor performs X.
B says X produces Y for downstream Z.
Therefore user outcome is Y available to Z.
```

派生不能：

- 新增 actor、状态、权限、数据关系或业务步骤
- 把 MAY 推成 SHALL
- 把目标架构推成当前实现
- 把后台行为推成可见 UI
- 把领域实体、聚合、关系或层级直接推成导航树、选择器、关系图、页面层级或其他 UI 表面
- 把示例推成完整枚举

### unknown

证据不足。保持 unknown，不用行业惯例、竞品模式或"常见做法"补齐。

以下 unknown 必须成为 decision blocker：

- 改变用户可执行行为
- 改变权限、安全或数据处理边界
- 改变状态机、枚举或 Gate
- 改变 API/持久化语义
- 改变验收结果

纯视觉偏好可进入设计探索，不必回产品来源。

## 3. Conflict

`authority_conflict` 至少记录：

- 冲突锚点
- 各自原文
- 影响的 UI/流程/验收
- 应由哪个产品来源修订

发生冲突时，原型不得自行选边。

## 4. Decision Support

证据不足不等于所有问题都回产品来源。先分类：

| Class | Meaning | Allowed destination |
|---|---|---|
| `product_semantic` | 改变产品行为、角色、权限、状态、数据关系或验收 | 引用的产品语义来源 |
| `experience_design` | 相同产品语义下的信息、交互、反馈、视觉或无障碍选择 | foundation / surface map / slice contract |
| `evidence_request` | 需要用户研究、内容样本、指标或专家判断 | 记录证据请求；仅阻塞依赖该证据的决定，其他探索继续 |

讨论节奏、问题依赖、阶段收敛与工作记录统一遵循 [discussion.md](discussion.md)。推荐项说明证据、权衡和可逆性；不得用“最佳实践”替代项目证据。

Decision Record 不是产品来源权威。`product_semantic` 决定只有写回并验证其产品来源后，才能成为契约输入。

### Evidence Record

`evidence_request` 回收证据时记录：`request / method / source_or_sample / observation / confidence / blocker_resolved / affected_decision / next_action`。证据未回来或置信度不足时，不得关闭 blocker。

## 5. Surface Evidence

产品 Requirement 不自动拥有 UI。只有以下五项均为 `explicit` 或合法 `derived`，才能生成前端契约：

1. UI actor
2. User task
3. Entry point
4. Observable outcome
5. Interaction authority

Disposition：

- `surface_explicit`：五项均有当前用户表面直接证据。
- `surface_derived`：五项由证据必然推出；推导不得把领域模型/后台行为变成 UI。
- `surface_target`：产品来源明确未来/目标 UI 结果，但当前实现后置；只允许讨论原型，不授权生产前端实现。
- `surface_unknown`：任一关键项缺证据，进入 Decision Support。
- `backend_only`：只有后台、数据模型或非视觉验收，记录测试/日志/查询等验证方式。

`backend_only` 不生成 UI 契约。`surface_unknown` 可讨论明确标为假设的设计机会、提出确认产品意图的问题，但不得把它提交为已确认 IA、状态矩阵或可执行 Frontend Contract。`surface_target` 可生成讨论原型契约，但不能被描述为生产实现授权。

## 6. Product Intent Dimensions

抽取产品意图时至少覆盖：

- Actor：谁执行、谁审核、谁消费
- Outcome：用户最终获得什么可观察结果
- Trigger/context：何时、在什么前置状态下发生
- Decision/action：用户必须理解或完成什么
- Information needed：做决定前必须看到什么
- Success feedback：成功怎样可感知
- Failure/recovery：失败、无权限、不可用后怎样处理
- Constraints：硬门、权限、版本固定、只读、禁止项
- Upstream/downstream：入口、依赖、消费方和回流
- Anti-goals：明确不做或不得发生什么

不要把技术组件直接当用户目标。例如"使用 LightRAG"是实现/架构约束，不自动等于用户体验承诺。

## 7. Terminology and Copy

| Type | Rule |
|---|---|
| Domain entity/state/enum | 逐字使用产品来源词典；禁止近义替换 |
| Action copy | 从产品来源 WHEN/action 受控派生 |
| Help/error/a11y copy | 从失败条件或无障碍要求受控派生 |
| New domain concept | 禁止；返回产品语义来源 |

每条派生文案记录 `source_anchor` 与 `derivation_reason`。派生文案不得进入领域词典成为权威项。

## 8. Scenario expression

产品来源的场景不自动映射为 UI。映射到切片时在 Slice Contract 的 Required states 与 Spec-to-UI mapping 中记录表达方式；`backend_only` 场景不得映射 UI，必须给出测试、日志、查询或审计验证方式。不得把所有场景强行变成按钮。

## 9. Design Freedom

产品来源锁定"产品必须是什么"。设计可探索：

- 品牌性格、情绪体验与视觉表达，在既定产品定位下发展创意
- 信息分组与渐进披露
- 主从、画布、树、表、时间线、关系图等交互模型
- 操作优先级与反馈
- 认知切换和步骤压缩
- 响应式重排
- 无障碍增强
- 不改变语义的微文案

设计不得探索：

- 产品来源之外的业务状态、权限、Gate、数据关系
- 未授权自动化
- 假指标、假能力、假 API
- 把 Non-Goal 包装成概念原型

## 10. Quality Bar

高质量执行契约满足：

1. **Traceable**：非纯视觉决定可回到证据。
2. **Intentional**：组件和状态服务明确用户结果。
3. **Bounded**：实现者无需补设计，也无权扩大语义。
4. **Complete**：成功、空、加载、错误、权限、不可用均覆盖或有理由豁免。
5. **Testable**：验收项可通过点击路径、状态、截图或无障碍检查判定。
6. **Innovative within bounds**：方案在交互模型上有真实差异，但共享相同产品语义。
7. **Assertion-verified**：Foundation 的 Verifiable Design Assertions 逐条 pass/fail 标记，所有 fail 项进入 Review；必达项失败阻塞接受，探索项失败记录为学习结果，均不得伪称通过。

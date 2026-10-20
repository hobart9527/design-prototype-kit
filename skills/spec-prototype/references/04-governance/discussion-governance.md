# Discussion Governance: cadence, authority and legal exits

One reference for three concerns that share one subject — how a session talks to
its human, what a decision may claim, and where a run may legally stop. It
coordinates one Product Experience Model; it does not impose a visual-first or
IA-first waterfall.

- **Cadence and authority** (below): dialogue rhythm, human authority, stopping
  points, routes, working memory.
- **Contract semantics** (later section): what a formal contract may assert and
  how a source conflict is resolved. Read it when compiling a formal contract or
  resolving a source-authority conflict. Product discovery and design
  opportunities use [product understanding](../01-foundations/product-understanding.md).
- **Usage and scope** (later section): how the user describes intent, how scope
  lands on production, and what each turn's closing looks like.

## Record and resume

For substantive design work with writes authorized, create
`prototype/discussion.md` before other design artifacts. Keep its Resume section
small and current: execution boundary; active Product Experience Model decision;
route basis; requested scope/stopping point; pending prerequisite with impact and
owner; product/source revision; active artifact/evidence references; next action
and its prerequisite.

If an existing record lacks Resume, prepend the current fields and retain earlier
rationale below. File existence alone is not valid resume state.

A review/advice-only request remains read-only unless the user requests a record.
A no-build request can still retain requested Markdown design work. If the user
forbids all file writes, continue conversationally and state that durable resume
and record-scoped enforcement are unavailable.

## Human authority and delegated agency

Human approval must come from an actual user message or accessible approved
source supporting the whole commitment. Retain a short quote or locator, turn/date
when available and exact scope. An Agent reply, tool result, generated receipt,
existing file or successful build is not approval. Split sourced constraints from
added proposals and keep unsupported clauses proposed.

Every identified critical unknown retains one explicit disposition: resolved by an
actual answer, resolved by reliable source evidence, explicitly delegated by the
actual user within named scope, or unresolved with its dependent decisions blocked.
Research accessible facts before asking. Questions must follow dependency order and
include a recommendation, cost and impact; wait for the actual reply, then
recompute remaining and newly exposed unknowns. A partial or ambiguous reply
unlocks only what it covers. Actor, core task, success criteria, business rules,
permissions, object relationships, main journey and direction choices are not
exempted by calling them low-impact, reversible or hypothetical. A generic continue/complete-draft request, one answer, a recommendation or a model-authored
assumption is not blanket delegation. Conditional comparisons may illuminate an
open question, but cannot freeze or implement its dependent direction.

The human owns product-semantic changes, consequential value trade-offs and final
direction. The AI owns professional investigation, synthesis, recommendation,
critique and execution inside delegated scope. Do not ask the user to decide
researchable facts, CSS parameters, page quotas or low-risk reversible details.
Honor explicit delegation and advance without asking for each micro-decision.
When a decision is marked `delegated`, the direction choice it covers does not wait
for human confirmation; only an un-delegated human decision stops the run.

Three registers carry authority in the design record; never read one register's
value as another's.

**Decision `Status` column** — owned by
[`../core-kernel.md`](../core-kernel.md) §4:
`proposed | provisional | confirmed | delegated | needs-evidence | superseded`.
`confirmed` means an actual human user selection or approved external source,
with scope — never a synthetic PRD persona decision or a simulated role actor.
`delegated` means the human authorized AI judgment within a stated scope.
`proposed` is a professional recommendation awaiting authority or evidence,
`provisional` is a proposal carried forward while the direction is still open,
`needs-evidence` means inspectable material or observation is missing, and
`superseded` means a retained successor replaced the decision.

**Decision `User source` column** — `confirmed | delegated | synthetic-fixture`.
`synthetic-fixture` is a simulated persona, test fixture or scenario actor
approval and carries zero human authority, so it never binds a freeze.

**Resume pending prerequisite** — `none | needs_decision | needs_evidence | blocked`
(underscored; it is a dependency condition, not a decision status).
`needs_decision` means a consequential authority choice blocks dependent work,
`blocked` means a required capability or source is unavailable.

## Choose the next move

At each round:

1. Read current sources, settled decisions and evidence relevant to the active
   question.
2. Identify the highest-impact available uncertainty and its owner.
3. Research, model, draft or prototype everything safely resolvable within current
   authority.
4. Present the professional recommendation, material evidence and trade-off.
5. Ask only if a consequential unresolved human choice now blocks the next
   dependent action; otherwise continue through authorized work.
6. Reconcile feedback into the smallest owning decision and preserve unaffected
   facts, approvals and artifacts.

Do not end every turn merely to manufacture participation. A concrete comparison
or high-consequence semantic choice merits a pause; an internal reversible choice
does not. A bare “continue” resumes already authorized work but selects no pending
alternative.

## Co-creation stopping points (within Turn 1 / Turn 2)

Diverge and converge are the AI's work; the *choice between materially different
directions* is the human's. These are not stages and not approval gates on internal
work — they are the moments where a human decision changes what gets built, so
stopping there is the difference between co-creation and a reveal. They belong to
the turns that produce them; there is no separate timeline.

| Point | In | After | The human is deciding | Cost to redirect |
|---|---|---|---|---|
| **Divergence** | Turn 1 | rut named, lifeworld candidates generated, seeds assigned — **before any HTML** | Which worlds are worth building; whether a candidate is off-brief | Minutes. Nothing has been authored. |
| **Comparison** | Turn 2 | two directions built and captured, two-axis verdict recorded | Which direction carries the product, or that both miss and why | One build cycle. The divergence is already visible. |
| **Lock** | Turn 2→3 | convergence into the anchor | Whether the committed direction is locked | The anchor exists; a change here reopens the direction. |

Rules that keep these honest:

- **Present, never announce.** At each point show the actual candidates or captures
  with the trade-off stated — not a status report. A stopping point with nothing to
  compare is not a stopping point.
- **Divergence is the cheap one; do not skip it.** Steering at divergence costs
  minutes; the same steering at comparison costs a build cycle. A session that
  presents only at comparison has spent the human's budget before asking.
- **A stop is not a stall.** If the human does not respond, apply the unattended
  fallback below rather than waiting. Do not re-ask the same question.
- **The Direction Contract is authored in Turn 1 and locked in Turn 2.** The six
  blocks
  ([`../01-foundations/design-language.md`](../01-foundations/design-language.md))
  are written as `proposed`/`provisional` statements in the design record before
  the first runnable write (Turn 1); the lock happens when a direction wins, and
  the blocks the review portal and the fidelity judge read back are the ones
  already in the record. Nothing is authored twice.

### Unattended fallback

When no human answer arrives, the session continues on a recorded provisional basis —
it never silently treats its own recommendation as approval:

1. Choose the direction the two-axis verdict and the product evidence support.
2. Record the choice as `proposed` with its rationale and the falsification question
   that would overturn it.
3. Keep the non-selected direction's donation on the record (generator step 6).
4. Keep the Direction Contract's statements at `provisional` until a human confirms
   the direction.

A provisional lock is honest progress, not a substitute for authority. It must never be
reported as `confirmed`.

## Routes and legal exits

Routes describe requested stopping points, not stages:

| Route | May produce | Honest exit |
|---|---|---|
| `visual-first` / `visual-only` | product-grounded Design Propositions and specimens while structural work stays connected | selection/delegation, or a provisional recommendation with validation pending |
| `IA-first` / `IA-only` | object/content model, journey and Surface Topology decisions while expression stays connected or explicitly deferred | structural output with expression dependencies explicit |
| `spec-only` | only the requested exact design artifacts | implementation/usability validation explicitly pending; no Builder unless separately requested |
| `review-only` | findings against a supplied target and evidence | professional merit, task evidence and conformance reported separately; no mutation |
| `continuation` / `local-repair` | successor decision or artifact within affected scope | inherited choices retained or the affected owner reopened |

Whole product, journey and surface are scopes layered onto these route preferences;
they are not extra lifecycle states. `visual-first` and `IA-first` name the current
uncertainty, not a required ordering between two design systems.

`needs_decision`, `needs_evidence`, `blocked`, `prototype_blocked` and `unverified`
are dependency/evidence conditions, not fabricated user rejection or approval.
Continue independent work where possible.

## Product-grounded propositions

When a consequential direction is genuinely open, compare enough materially
different propositions to expose the trade-off. One determined answer needs no
invented competitor. Use the same representative content, task, breakpoints and
constraints. Each proposition records:

- product thesis/question and generative mechanism;
- Qualitative Design DNA naming both the combination and its product basis;
- Real-World Mapping source status, local mechanism, translation and non-transfer
  boundary when a reference actually reduces uncertainty;
- focal relationship and concrete specimen;
- familiar convention deliberately retained;
- cross-surface Signature Relationship;
- Signature Craft that makes the relationship perceptible in the specimen;
- benefit, cost and learning burden;
- visual/task evidence or an explicit validation limit;
- falsification question or transfer test.

A style label, adjective set, palette swap or unsupported novelty is not a
proposition. Recommendation is part of the AI's job; final direction remains with
the human or recorded delegation.

## Decision frontier

Keep open decisions with prerequisites, scope, evidence, impact, owner and next
move. Ask only a decision whose prerequisites are settled. Combine questions only
when they are inseparable. Preserve useful uncertainty instead of converting it
into a long intake form.

When two rounds add no useful distinction, change method: research a missing fact,
make an inspectable specimen, walk the task, compare product priorities, or choose
a reversible default within delegation. Do not reroll styles.

## Feedback and recovery

Map feedback to the smallest owner:

- product purpose, role or policy → product source/Product Thesis;
- object, terminology or content relationship → Object/Content Model;
- task continuity, navigation or page boundary → journey/Surface Topology;
- content voice, interaction or appearance → Design Proposition/Foundation;
- implementation defect → repair in place within the exact declared scope;
- evidence weakness → validation plan or `unverified`.

Mark dependents for reconsideration and retain unrelated decisions. Combining
directions creates a new retained proposition, not an unrecorded mixture. A broad
redesign is justified only when the owning assumption is broad.

## Working memory discipline

Before a formal owner exists, retain the decision in Discussion. After
formalization, link to the authoritative section and keep only status, rationale
and provenance here. Research observations remain in the research record. Frozen
artifacts receive successors; they are never rewritten to simplify resume.

---

# Contract semantics

## 1. Authority

1. 产品来源（用户指定的 brief、OpenSpec spec、现有页面、产品描述）决定产品行为、领域实体、状态、枚举、权限和结果；设计层不得超越其边界。
2. `prototype/discussion.md` 是引用产品来源的派生摘要；本次明确的来源版本和用户澄清优先。来源更新后先核对并更新摘要，不能让旧摘要覆盖新来源。
3. design 解释实现方法；proposal 解释目标和范围。两者不得覆盖产品来源。
4. Foundation、词典、切片契约是独立设计事实，与引用的产品来源冲突时失效，但不进入产品来源生命周期。
5. 执行拆分（OpenSpec tasks 或其他）不是产品意图证据。

## 2a. Intent and Route

Declare the requested outcome separately from workspace state: `explore`,
`specify`, `prototype`, or `review`. Existing tokens, shells, and screens are
lineage evidence only; they cannot select a route or authorize production work.
When intent is unresolved and would change scope, record `unknown` and ask one
blocking question.

## 2b. Evidence Status

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

讨论节奏、问题依赖、阶段收敛与工作记录统一遵循 [discussion governance](discussion-governance.md)。推荐项说明证据、权衡和可逆性；不得用“最佳实践”替代项目证据。

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

---

# Usage and scope

## AI 先判断三件事（意图、形态与范围）

分别识别本次要达到的**产品形态**、**交付结果**和**内容范围**，严防误触与路线僵化：

### 1. 识别产品形态（三大路线自适应）
形态决定的是**继承还是新建**，不是流程的繁简。SKILL.md 的 Context labels
（Archetype A/B/C）与 Negative trigger boundary 是这两个概念的入口；以下是每条
路线的判定与做法。

- **形态 A：全新产品从零起步 (Greenfield 0 to 1)**
  - 判定：仓库无现成样式、无 Token、无现成界面。
  - 路线：走全流程五阶工序（张力解构 → 5 Dials 风格刻度 → 单屏 Hero 锚点与全局 Token → 逐层铺展 → 走查与冻结）。
- **形态 B：现有产品增设新页面/新功能 (New Surface 1 to N)**
  - 判定：仓库已有成熟设计语言、主色、导航壳或现有 Token。
  - 路线：强制**血缘继承**（复用现有 Token，绝不分裂系统造新轮子）；Stage 1 聚焦该新功能的 OOUX 基数映射与决胜交互切片，随后直接展开。
- **形态 C：现有产品体验优化与评审 (Refinement & Audit)**
  - 判定：界面代码已存在，用户要求审查品味、优化交互、查漏补缺。
  - 路线：**直插 Stage 4（验 - 鉴）**；调动 Break 协议、同心圆角、等宽防抖与对比度审计，产出具体 CSS/DOM 改造差量（Refactoring Deltas），绝不推倒重来。

### 2. 负向排他防火墙（绝对不唤起场景）
- **纯代码缺陷**：Bug 修复、控制台报错（如 500/404）、后端 API 联调、数据库迁移，走常规工程修补，严禁唤起设计 Skill；
- **已批准代码交付**：OpenSpec 变更已批准进入生产代码任务交付（Loom Entry 2），走正式工程交付，不制造一次性草模。

### 3. 结果与范围
- 结果：探索/比较、整理设计规格、制作可运行原型、验证/调整现有原型。用户说“做原型”时，在设计与行为就绪后应继续制作和验证；“只讨论”“只输出规格”则在对应结果处停止。
- 范围：整个产品、指定页面、功能模块/用户任务，或指定 Change 影响的 UI。两者可以组合，例如“只讨论整个产品设计”“制作这个 Change 中的设置页”。

先读当前项目资料、讨论记录和相关原型，再用一小段话说明：本次覆盖什么、沿用什么、马上推进什么。依据充分就继续，不把这个摘要做成必须再次确认的关卡。真实的主观选择或产品语义缺口按 discussion 指导处理；可调查的事实由 AI 查明。

示例开场：“这次围绕素材标注，沿用现有视觉。我会串起列表进入详情、保存与失败重试、返回列表后的更新；先检查已有规格，再制作这条流程。”

信息不足时提出推荐范围和理由，只问最影响下一步的一件事。例如“我建议先验证列表到标注保存这条高频任务，能同时检查阅读和反馈体验”，再讨论真实未决目标。不要抛出整套流程菜单或要求用户报页面数量；用户明确要全产品时也不能自行缩成推荐模块。

## 范围如何落到制作

| 用户范围 | AI 应如何推进 | 完成边界 |
|---|---|---|
| 整个产品 | 先复核完整 IA/页面清单，按关联任务组织制作批次；新系统可先验证一条代表性流程，再继续剩余批次 | 全部约定页面及其必需状态/流程有覆盖与验证记录；样板页、第一批或规格齐全都不等于全部原型完成 |
| 指定页面 | 覆盖这些页面的必要状态与交互，继承全局语言和相关 IA | 未制作的外部页面作为清楚标注的边界；若验收必须穿过它，说明依赖并建议最小扩展，未经范围授权不直接制作整站 |
| 功能模块/用户任务 | 从任务入口到可观察结果，识别需要的页面、弹层和恢复路径 | 完成所选任务；模块不等于一个页面，加载/错误等状态也不自动增加页面数量 |
| 指定 Change | 只读相关 Change 需求，映射受影响页面、共享组件和流转，保留未受影响的设计 | 覆盖本次用户指定的 UI 影响；Change 本身不是页面，也不是自动批准执行该 Change；纯后台变更给出非 UI 结论 |

不要默认选择仓库最新 Change。显式引用缺失时报告缺失，不能用另一个 Change 替代；存在真实歧义时再请用户决定。Change 编号不是普通设计工作的必填项。

一个制作批次可以包含多个关联页面；完整产品按明确版本分批制作。跨批次共同入口、共享数据、连通验证与继续制作由 [handoff](handoff.md) 负责；不是生成几个独立演示目录就算全产品完成。

把本次范围、目标结果、当前批次和下一步写入现有 discussion 记录；用工作版 Surface Map 的页面/规格/证据引用记录覆盖，不新建重复状态表。未定完整 IA 时先记录暂定范围即可，不为记录进度提前冻结页面清单。

## 范围决议与延续

制作范围在 Stage 3 展开前决议一次：依据当前 Surface Map、任务风险、探针结果与适用平台，给出具体的推荐组合（各自包含的表面与流程、用于验证什么、依赖哪些范围外表面、刻意舍弃什么），以及整产品选项与其分批计划；范围未定时才提问，已经明确说过范围就不再问；方向探针（direction probe、探索/比较）仍按原路线推进。选定子集只收缩实现目标，既不裁切产品模型也不等于批准，完整地图、对象模型、权限、状态与已采用的方法结论保持权威，未选表面保持暂定而非删除或补造；范围外依赖如实披露，不静默追加。记录要写明所选地图版本与覆盖口径；缺失、失效或版本不符的选择需重新对账，不得静默按整产品执行。方向探针、仅规格与局部调整三条轻量路线维持原状，不因范围决议被强制走整产品枚举、实现或批准。

The resolution rule itself (what a selection may and may not decide) is owned by
[SKILL.md](../../SKILL.md) "Coverage Selection" and
[stage-3-skeleton.md](../stages/stage-3-skeleton.md); this section only says when
the decision is taken and how it is recorded.

### 全权委托与静默推进协议 (Delegation-Aware Protocol)

当用户在交互中给出明确的授权或全权委托意图（例如“按你的专业判断推进”、“间距字号和布局由你定”、“直接做完”、“全部做完”）：
1. **意图记录**：在 `prototype/discussion.md` 的 Decision Record 中将该项决策标记为 `status: delegated`，记录用户的原话引用。
2. **静默穿透**：Stage 4 的走查与修复直接基于自动化质量门禁（Engineering DOM, Break Protocol, a11y, Visual Capture）全自动闭环。严禁在每个局部细节（如间距、微文案、非破坏性过渡）上打扰用户。
3. **断点唤醒**：仅在遇到**不可逆的业务分歧**、**不可降级的质量底线红线违背 (Floor failure)** 或**全新的业务实体/权限缺口**时，才主动向用户提问。
4. **交付呈现**：完成后直接交付高信息密度的客观技术事实、可交互预览地址与关键验证证据，而非内部步骤审批请求。

## 可以直接说的例子

| 日常请求 | AI 应给出的衔接 |
|---|---|
| “使用 spec-prototype，先帮我探索这个产品的视觉方向，给我几种推荐，暂时不做页面。” | 从定位和场景提出体验主张、参考与不同方向，按需讨论；不提前冻结 IA 或制作整套页面 |
| “继续。”（当前仍有两个未选方向） | 继续解释或具体化推荐，展示比较并等待选择；不会自行替你选定再冻结 |
| “沿用 A，间距和字号由你决定。” | 记录这项明确委托并处理细节；其他未定的 IA 或页面范围仍按讨论流程推进 |
| “我选第二个方向，接下来讨论页面和主要流程。” | 保留这个明确选择，进入 IA 与交互比较；不重复询问是否确认视觉 |
| “沿用已经确认的设计，制作素材标注模块的可交互原型。” | 检查该模块的完整任务路径与必需状态，补齐真正缺口后直接制作并验证结果 |
| “这次只做登录页和找回密码页，其他页面暂时不用做。” | 保持这两页范围，说明外部跳转边界；仅对阻塞验收的跨页依赖提出具体建议 |
| “基于 Change add-bookmarks，制作这次受影响界面的原型。” | 定位该实际 Change，只读分析 UI 影响；`add-bookmarks` 仅为示例，缺失时不假装已找到 |
| “把已确认页面清单里的全部页面做完，按模块推进。” | 给出第一批及覆盖依据，完成后继续剩余批次；逐批保留入口、验证和未完成项 |
| “先把订单模块的设计与交互规格整理完整，本次不要生成界面。” | 输出规格和剩余决策，验证标为待执行；不制作界面 |
| “继续上次原型，保留视觉；只调整详情页保存失败后的反馈。” | 读取已有版本与证据，仅重开受影响的反馈决定，创建必要后继版本并检查相关路径 |

## 每次结束怎样引导

先报告实际完成范围和实际验证结果，再给一个针对当前进展的下一步。若交付了可运行产物，给出准确预览入口或启动方式，并说明本次最值得体验的路径；尚未运行时不要称其已验证。

只有确实需要用户决定时才提问。例如“保存失败后保留草稿已验证；请体验错误提示是否足够清楚”。仅确认设计时可以建议“下一步按这套语言讨论页面与导航”，但用户已要求继续制作时应继续执行，不把建议当成停止理由。生产实现、提交和部署仍属于各自授权范围，原型完成不自动启动它们。

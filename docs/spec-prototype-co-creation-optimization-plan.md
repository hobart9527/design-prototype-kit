# spec-prototype 共创与设计质量优化方案

日期：2026-09-24  
审计基准：`74e2554`；现行源文件、两项只读调查及当前 sample-gate 派生产物。  
交付性质：调查结论与实施计划，**不是已实施的优化，也不是 OpenSpec 批准记录**。

## 1. 决策摘要

保留九支柱、五轴、双钻、现有阶段和 direction-probe。不要再建立一套共创框架，也不要恢复已退役的 `core-workflow.md`。

本次最符合实际的优化是：

1. **统一现有规则所有权**：让阶段程序、模板、Builder、Critic 服从现有共创与设计语言规则；移除强制物理隐喻、固定材质二选一、统一 Bento/胶囊/负字距/斜纹等跨领域默认。
2. **让共创产生可比较、可修订的设计决定**：围绕当前高影响未知选择研究、结构草图、同内容视觉对照或交互探针；不按固定轮数问卷推进。
3. **保证决定传递不失真**：确认来源与授权范围进入 canonical Spec；Tokens、Envelope、Builder 消费同一修订；不把候选、推断或遗留文件提升为确认事实。
4. **先修真实链路阻断，再评设计增益**：补齐 canonical 派发、证据冻结、来源新鲜度等接缝；随后用真实会话、浏览器任务和独立视觉对比验收。

目标不是“无参考图必然产出顶级作品”，而是提高无参考输入下形成合理设计方向、探索表达差异、保持业务语义、交付可运行复杂原型的可靠性。设计品位的提升必须由作品证明。

## 2. 审计边界与证据等级

### 2.1 本次做了什么

- 核查当前入口、常驻内核、阶段、dialectic、共创治理、设计语言、模板、Agent 正本与链接。
- 核查 Spec IR、Tokens、Envelope、执行边界及 handoff 的关键接缝与相关测试。
- 对照现有 sample-gate 的 `tokens.css` 与 `envelope.json`，观察实际投影结果。
- 核查已有 eval 与 benchmark 入口，避免另造评测体系。

### 2.2 本次没有做什么

- 未执行新一轮真实设计会话、Builder 构建、浏览器交互或视觉盲评。
- 未通过本次调查证明整个 Skill 全链路通过。
- 未修改业务源码、模板、Schema、测试或现有原型；未提交、发布。
- 下文代码缺陷是静态路径核查结论；对应运行反例列为实施期首先补充的测试，不冒充本次复现结果。

工作区已有以下修改，必须保留：

```text
prototype/contracts/compiled/sample-gate/r1.spec.json
prototype/shared/tokens.css
prototype/specifications/sample-gate/r1.spec.md
prototype/experiments/（未跟踪）
```

sample-gate 用于暴露接缝，不是干净基线，也不是跨产品设计质量证据。过去的 `21 passed, 315 deselected` 与 craft 的三个测试只证明所选机制检查，不证明真实共创、完整交互、独立视觉评审或冻结交付。

## 3. 当前真实链路与所有权

### 3.1 应继续使用的权威

以下路径以 `skills/spec-prototype/` 为根，Agent 路径除外。

| 职责 | 当前 owner | 优化原则 |
| --- | --- | --- |
| 意图入口与按需加载 | `SKILL.md` | Explore / Specify / Prototype / Review；不由资产数量强制走全流程 |
| 全局不变式 | `references/core-kernel.md` | 保留生命周期、阶段边界、证据与职责隔离 |
| 对话节奏、批准来源、恢复与合法退出 | `references/04-governance/discussion.md` | 已有自适应共创循环，修消费者，不新增竞争 owner |
| 开放表达、设计命题、可选地锚 | `references/01-foundations/design-language.md` | 已有七字段 Design Proposition，继续作为表达规则源 |
| 阶段程序 | `references/stages/*.md` | 是可调用能力，不是强制瀑布 |
| 局部讨论方法 | `references/dialectic/*.md` | 改成按未知调用，不替代全局共创规则 |
| 讨论工作记忆 | `prototype/discussion.md` | 保留决定、理由、实际用户来源与影响范围；正式化后指向相应修订 |
| canonical 设计合同 | `prototype/contracts/compiled/<slice>/r1.spec.json` | 编译产物，不直接手改；人类视图为 `r1.spec.md` |
| 可执行设计 | `agents/spec-prototype-builder.md` | 在明确边界内设计和实现，不自批业务语义或提升生命周期 |
| 独立评审 | `agents/spec-prototype-critic.md` | 评价任务、交互、感知与设计命题，而非统一审美模板 |
| 冻结与下游准入 | `scripts/handoff.py` | 绑定实际批准、具体修订与保留证据 |

`agents/` 是 Agent 正本；`.claude/agents/` 与 `.claude/skills/spec-prototype` 的现有符号链接有效。不新增路径别名，不写派生安装副本。

### 3.2 两条实际路线

```text
用户目标 / 现有资产 / 已确认决定
    SKILL 意图路由 + core-kernel
        discussion governance 选择当前高影响未知
            Explore：方向简报 → direction-probe → 证据 / 反馈 / 退出或晋升
            Formal：Stage 1 合同 → Stage 2 证伪 → Stage 3 已选范围
                    → Stage 4 验证 → Stage 5 冻结

正式派发的技术路径：
作者来源 → compile_spec_ir → canonical IR + 人类视图
表达来源 → compile_tokens → CSS / DTCG / 人类视图
合同与 Tokens → assemble_envelope → execution_boundary
             → Builder → 浏览器证据 + Critic → handoff
```

第二条图描述当前组件连接，不表示连接已经一致。现状仍混有 canonical 与 legacy 来源，正是本次需要修复的重点。

### 3.3 core-workflow 的退出处理

用户已明确其退出。当前仍存在的活引用是迁移债务，不是恢复其权威的理由：

- `SKILL.md:22-23`：仍允许按需加载。
- `references/core-kernel.md:7-8`：仍指向旧共享核心。
- `references/stages/stage-3-skeleton.md:9`：仍委托旧 Change Scope Router。
- `references/stages/stage-5-freeze.md:41-42`：仍引用旧生命周期。
- `tests/test_design_chain_continuity.py`、`test_canonical_ontology.py`、`test_v10_integrity.py`、`test_prototype_coverage.py`、`test_pipeline.py`、`test_benchmark_harness.py`：部分断言或夹具仍绑定旧文件。

处理方式：入口回到 `SKILL.md`，不变式回到 `core-kernel.md`，生命周期回到 `artifact-lifecycle.md`，覆盖范围回到当前 scope owner。只迁移仍被真实消费者需要的行为，不机械搬运整个 L0–L4 体系。

不修改历史基线、历史报告或已归档 Change 来制造“零引用”。也不必靠删除旧文件证明退役；验收对象是活跃加载路径和规则依赖。

## 4. 已确认的主要断点

### 4.1 共创 owner 已有，阶段规则却覆盖它

`references/04-governance/discussion.md:63-81` 已要求：先读已有决定，识别高影响未知，在授权内研究或探针，只在真正阻塞的分歧上提问，按最小 owning decision 更新。

`references/01-foundations/design-language.md:85-129` 已有设计命题、同内容标本、保留惯例、signature relationship、收益与成本、证伪和迁移；现实映射可选。

但 `stage-1-frame.md:29-81` 仍要求固定四轮，物理隐喻先行，逐轮锁定，固定拓扑与材质讨论。新证据揭示问题时，默认不重开已确认轮次。这与自适应共创和局部修订冲突。

**应改**：四轮保留为可用方法主题，不再是顺序门禁；反馈可以触发局部重开，但不得把新方案冒充用户已批准。

### 4.2 发散被固定模板替代

- `stage-0-explore.md:24-26` 强制至少三个不同维度发散；与按问题需要生成候选的规则冲突。
- 同文件 `:27-31` 禁止构建，`:39` 又允许可选探针，`:45` 出口要求截图。
- `dialectic/03-sensory-kinetic.md:7-25` 强制已有物理隐喻、两种固定材质、特定朱红负向清单。
- `stage-1-frame.md:127-145` 与上述 dialectic `:34-48` 固定四类工法默认。

**应改**：没有构建授权时，研究结论与讨论记录就是合法输出；构建授权只在当前探针范围内生效。候选数取决于真正不同的假设，不设数量配额。颜色禁用规则来自本产品语义，不由全局模板注入。

### 4.3 工法字段传下去了，决定没有完整传下去

- `scripts/compile_spec_ir.py:403-432` 的 `parse_craft_stack` 使用文本匹配与默认值，不能可靠区分已否决方案、当前确认项和后续替代项。
- `scripts/compile_tokens.py:877-882` 输出一组固定 craft CSS 属性；当前编译入口不消费 canonical `craft_stack`。
- `scripts/assemble_envelope.py:220` 会投影 craft 字段，但字段存在不等于实现已遵守。
- Builder/Critic 的统一大圆角、宽 padding、紧字距、斜纹等要求，会继续覆盖具体产品的设计决定。

sample-gate 已可见这种张力：Tokens 标注 `machined-industrial`，圆角为 6–8px；Envelope 却有 `dense-tactile`、`soft_bento_pill`，而 Agent 指令还要求更宽松的 Bento 工法。该实例不能仅凭值不同判定哪一个正确，但足以说明当前缺少统一来源与冲突处置。

**应改**：不是为四个字符串增加固定风格查表，而是明确每项决定的适用范围、参数边界、依据及实现责任。可编译参数驱动 Tokens；结构与交互决定驱动 Builder；结果由适合的证据验证。

### 4.4 canonical 正式派发仍按旧路径校验

`execution_boundary.py:87-104` 将摘要键映射到固定的 legacy `r1.md`、`c1.md`、`t1.md`。而 canonical Envelope 对应的摘要可能来自 `r1.spec.md`。

**静态反例**：canonical-only fixture 组装成功，dispatch 却查找不存在的 legacy 文件；两种文件并存时也可能比较错误对象。

**应改**：绑定真实相对路径与摘要；先校验 repository containment、来源类型和必需引用，再验证字节。不能以删除摘要字段或绕过 stale guard 作为最终修复。

### 4.5 语义投影与模板事实混杂及运行时载荷隐性绑架

- `compile_spec_ir.py:548-573` 注入 fault/telemetry、危险提交、accent seal 等模板 invariants；`:626-629` 固定 accent policy。它们不是每个领域的作者决定。
- `assemble_envelope.py` 的 canonical 投影把 declared surfaces 放入 `primary_entities`，把 anchor 的 transfer/non-transfer 投影为空数组。
- **运行时载荷隐性绑架**：`assemble_envelope.py` 内部仍硬编码注入 6 个全局方法（如 `decisive-3-frame`, `visual-rhythm-density`, `action-verb-lifecycle` 等）与写死的 `responsive_folding: 390px`。无论 Spec 是否授权，Builder 始终收到这组预置方法指令，导致最终实现被强行塑形。
- 当前 sample-gate Envelope 将 `interaction/inspecting` 等状态拆成 `interaction`、`inspecting`，动作生命周期数组却为空；需要补精确 ID 与动作后果的接缝测试，不能以“有交互字段”算通过。
- 同一 sample 的平台未知，但指导包含固定 390px 折叠要求；哪些来自真实验证范围、哪些来自默认，必须可分辨。

**应改**：未作者化的领域规则不得进入正式验证合同。剥离 Envelope 中的写死方法注入器，`active_methods` 与 `builder_guidance` 改为从 Spec 声明中按需提取；未激活的方法不得注入 Builder。实体、surface、state、action、viewport 各归其义；合法缺省与阻塞性缺失由用途决定。可选 invariants 无源可为空；正式构建所需状态和验证范围缺失仍须失败。

### 4.6 阶段责任与编译前置条件不一致（契约分级缺失死锁）

Stage 1 指引直接要求产出完整 sealed Spec；编译器同时要求 domain states、interaction states、data scenarios、stress fixtures、viewports、required states。部分细化内容属于后续阶段（Stage 3/4）的作者输入，不能为了通过门禁在 Stage 1 猜出。现有单一 Schema 导致死锁：Stage 1 若不假造后续状态，直接被 Schema 顶级 `required` 拦截；若填入空数组，又被编译不变式拦截。

**应改**：引入**阶段契约分级模式 (Progressive Schema Tiers)**：
- **`intent_spec` (Stage 1 / Probe 准入)**：仅校验问题命题、拓扑范围、五轴、工法意图及作者依据；不强制状态机与行为细化。
- **`execution_spec` (Stage 3/4 / Formal 构建准入)**：校验完整状态机、交互动作与视口验证范围。
Stage 1 只记录当前拥有来源的设计决定；后续 state/verification fragment 由相应阶段明确提供并绑定。未满足正式合同前置条件时，输出具体缺项并停在合法未完成状态，或继续已授权 direction-probe；不自动晋升，不把 `allow_incomplete` 用作正式准入。

这项工作对齐阶段文案、分级 Schema 与编译输入，消除死锁，不另设 Stage 1.5。

### 4.7 状态标签不能替代批准证据

`compile_spec_ir.py` CLI 允许传入 `frozen_approved`，Envelope 会传播该状态。现有 `handoff.py` 下游 gate 仍要求 freeze manifest，因此不能把此问题夸大为“已绕过全部下游批准”。真实问题是上游可伪造生命周期声明，与 Builder 权限上限冲突。

**应改**：编译只能产生其权限内的状态；Validated/Frozen 的提升由对应证据与批准路径完成。保留已有 `approval_binding` 与来源防护，不重新实现批准系统。

### 4.8 证据冻结存在类型不对称

静态核查显示，`handoff.py:686-698` 在仅有 PNG 的路径下构造目录型 evidence bundle；`:797-805` 对 frozen artifacts 统一调用 `retained()`；后者 `:85-89` 只支持文件 `read_bytes()`。

**反例**：PNG-only evidence freeze 后，downstream admission 尝试读取目录而失败。修复必须同时验证文件增加、删除、改动都会使 bundle 失效。

另外，freeze 与 `check_downstream_gate:838` 对 Markdown 状态格式的读取不一致。当前主要表现为诊断失真，不应夸大为已证明的准入逃逸。

### 4.9 新鲜度校验缺少推导关系与 Tokens 派生双向回写风险

Envelope 记录当前 Tokens 的摘要，能检查组装后的改动；但不能证明该 Tokens 由当前表达来源生成。canonical JSON 本身也需作为实际消费来源绑定，而不能只保留其 Markdown 视图摘要。此外， 目前并存 、 及  路径，存在从 CSS 逆向回写与前向编译的竞态混用风险。

**应改**：确立**单向派生与严格脏状态熔断 (Strict Uni-directional Flow)**：
- 规定唯一流动路径： ->  -> 。
- 废弃 formal 模式下的逆向 reconciliation 入口；检测到  被手工修改且 digest 与 Spec 不匹配时，强制标记为  并阻断下游准入，禁止静默覆盖或模糊合并。
- 保存实际来源摘要、生成版本和产物摘要的派生关系。不得只比较 CSS 注释中的五轴名称，那不能覆盖 palette、工法参数或局部覆盖。

## 5. 目标共创方式：增强已有机制

### 5.1 九柱与五轴分别做什么

九柱继续覆盖：Value、Research、Object、Journey、Topology、Attention、Expression、Interaction、Resilience。

五轴继续描述：Density、Energy、Materiality、Rhythm、Character。它们是可选校准坐标，不是必须逐项答题的清单，更不是 CSS 公式。

四类 craft 作为可组合方法类别保留：表面光学、空间几何、微观排版、数据标记。它们既不替代九柱五轴，也不声称严格正交或穷尽现代设计。

现代复杂产品所需的能力应落到现有 owner，而不是再添审美轴：

| 能力 | 所属设计责任 | 可观察结果 |
| --- | --- | --- |
| 信息层次、任务焦点、密度分区 | Attention / Topology / Expression | 用户能识别主任务；密集区仍可读、可操作 |
| 字体层级、语言适配、长文本与数据对齐 | Expression | 中英文、长标签、数字、不同屏宽不破坏结构 |
| 色彩角色、层次光学、语义冗余 | Expression / Resilience | 状态不只靠颜色；层级和对比可辨 |
| 图表选择、量纲、基线、不确定性 | Research / Attention / Expression | 数值能解释、比较、追查，而非装饰性图表 |
| 动作语义、状态连续性、反馈与恢复 | Journey / Interaction / Resilience | 操作产生可见后果；取消、失败、返回可恢复 |
| 内容声音、图标与图像、品牌差异 | Value / Expression | 表达服务领域与任务，不沦为统一 SaaS 皮肤 |
| 多 surface 迁移与响应式重组 | Topology / Journey | 不是缩小桌面截图；关键任务与上下文仍成立 |

### 5.2 中观装配层：九柱、五轴与四工法的交叉咬合

此前 Skill 表面机制正确但设计容易平庸或塌缩为单一维度的根源，在于**宏观业务、微观物理与表层手法之间缺乏“中观装配契约 (Mesoscopic Assembly Contracts)”**：
- **九柱 (9 Pillars)** 处于宏观业务语义层（解决“为何做与做什么”：Value, Journey, Topology, Object...）；
- **五轴 (5 Axes)** 处于微观感官物理标量层（解决“物理感受”：Density, Energy, Materiality...）；
- **四工法 (4 Craft Stack)** 处于表层材料修饰层（解决“材料表现手段”：Surface Optics, Geometry, Typography, Data Marks）。

若直接由九柱跳到五轴变量和表层工法，中间的**空间质量分布（怎么摆）、时空动力学（怎么动）、数据构件（怎么读）**全凭 Builder 随机发挥，必然退化为千篇一律的卡片流与泛化后台。

为此，引入三项交叉桥接构件，作为现有插槽的结构化增强（不新增孤立顶层实体）：

```text
[九支柱: 业务拓扑与旅程]
       │
       ▼ 投影约束
┌────────────────────────────────────────────────────────┐
│        中观装配层 (Mesoscopic Assembly Contracts)       │
│                                                        │
│  1. 信息拓扑构件 (Massing)     九柱 Topology × 五轴 Density  │
│  2. 时空连续性协议 (Kinematics) 九柱 Journey × 五轴 Energy   │
│  3. 数据微构件语法 (Semantics) 九柱 Object × 工法 Data-Marks  │
└────────────────────────────────────────────────────────┘
       │
       ▼ 样式与材质
[五轴 + 四工法: 底层变量与材料质感]
```

1. **信息拓扑构件模版 (Information Massing Patterns)**：
   - **机制**：九柱 Topology（主从关系） $	imes$ 五轴 Density/Materiality（信息质量与质感） $\longrightarrow$ 物理视窗内的空间重心分布。
   - **落地**：在 `layout_directives` 中声明模式（如 `canvas-inspector` 双轨固定式仪表视窗、`split-stream` 左右流式分流、`focus-diorama` 焦点沙盘、`pinned-master-detail`），终结 Builder 自由发挥导致的松散无序 Flex 堆叠。
2. **时空连续性协议 (Temporal Continuity / Kinematics)**：
   - **机制**：九柱 Journey/Interaction（离散状态流转） $	imes$ 五轴 Energy（阻尼与时序） $	imes$ 工法 Spatial Geometry（圆角与边缘） $\longrightarrow$ 几何动量守恒。
   - **落地**：在 `interaction_spec` 中明确状态变更时的几何形变规则（空间位移、抽屉推挤、焦点保持、模态原点扩散与遮罩阻尼），严禁生硬切换 `display: none`。
3. **数据可读微构件 (Data Semantics & Micro-Marks)**：
   - **机制**：九柱 Object/Research（指标含义） $	imes$ 工法 Data Marks + Micro-Typography（数值编码与排版） $\longrightarrow$ 数据界面一体化。
   - **落地**：在 `visual_directives` 中将 `data_marks` 升级为带语义的微型图形语法（量纲紧凑对齐、健康度阈值渐变带、微火花线、不确定性波纹），严禁将数据降级为通用文本 `div`，彻底终结数据展示的平庸感。

### 5.3 一个高质量共创循环

1. **读取并复述必要边界**：用户目标、使用情境、证据、已有决定与授权；不再问仓库可以回答的事实。
2. **找当前最重要的未知**：是价值、对象关系、结构、表达还是交互后果？不强制从物理隐喻开始。
3. **给出有依据的建议**：存在真实分歧时提供可比较方向；已有清晰答案时直接推进。
4. **选最便宜但有效的证据**：研究、ASCII 结构、同内容视觉标本、可操作探针，按问题选择。
5. **收敛到最小决定**：记录选什么、为什么、代价、边界、何时证伪；保持未受影响的决定。
6. **迁移验证**：把核心关系应用于第二个 surface、异常状态或不同设备，验证是否仅在 Hero 上成立。

参考案例可以是数字产品、物理机制、既有设计系统或领域惯例；允许 `not needed`。使用时说清 transfer / non-transfer，而不是让“卡尺”自动决定所有颜色、圆角和动画。

### 5.4 反馈怎样转为局部修订

示例：用户说“太像控制台，想更清晰轻松，但保留高密度比较”。

- 保留：对象关系、比较任务、已确认的信息密度要求。
- 重开：表面明度、文字层级、状态强调、装饰性材质。
- 提供：相同数据与结构下的表达对照，而不是重新生成完整产品。
- 验证：扫描顺序、异常辨识、长标签、低对比风险。
- 记录：旧表达决定被 superseded；新决定的实际来源与范围；受影响 Tokens、页面和视觉证据须重验。

“继续”只表示继续工作，不等于从尚未选择的方向中替用户挑一个。已有明确委托时，可在其范围内选择并标为 delegated，不能记为用户亲自确认。

## 6. 语义合同与实现约束

### 6.1 单一权威不是只剩一个文件

草案讨论负责推理与决定来源；canonical 修订负责正式消费；Tokens、Envelope、人类视图是该修订的派生表示。不能让多个文件分别解释同一决定。

目标来源规则：

- **分级契约模式 (Progressive Schema Tiers)**：
  -  (Stage 1 / Probe 准入)：仅校验问题命题、拓扑范围、五轴、工法意图及作者依据；不强制状态机与行为细化。
  -  (Stage 3/4 / Formal 构建准入)：校验完整状态机、交互动作与视口验证范围。
- **动态方法注入与载荷去硬编码**： 剥离静态写死的全局方法（如  等）与 ，改为从 Spec 的  与  动态提取。
- **严格单向派生**：Tokens 仅允许从当前有效 Spec/Discussion 单向编译，禁止逆向回写与模糊混源。
- **canonical 路线**：IR、Tokens 和 Envelope 使用同一个已解析表达决定集与修订，不分别扫描不同 Markdown 得到不同答案。
- **legacy 路线**：保留已支持的 sealed foundation 优先行为，显式标注来源与模式。
- **两者并存**：由入口明确选择来源；不按文件存在与否静默混搭。
- **无明确决定**：允许未指定/委托/不适用；不得暗补固定产品风格。

不是把所有自由文本都塞进 Schema。先复用现有 provenance 和 reference；只有真实消费链需要的字段才增加结构。

### 6.2 确认与授权解析

不得只以“出现 Confirmed 标题”或“第一个匹配值”代表真实确认。最小规则包括：

- 当前有效的 confirmed/delegated 决定可进入对应范围；delegated 必须保留委托依据。
- proposed、needs-evidence、needs-decision 不得伪装正式约束。
- superseded 不再作为当前决定；不能依赖全文字符串先后顺序解决冲突。
- 同范围互斥决定未解决时报告冲突，不随机取值。
- synthetic-fixture 与真实批准隔离，模拟用户不能批准真实产品。
- 未识别的工法描述保留为开放设计意图；若缺少执行所需语义则报告缺项，不静默替换成 Bento。

### 6.3 Tokens 不承担全部设计语义

| 决定类型 | 消费者 | 验证方式 |
| --- | --- | --- |
| 字号、字距、颜色、层级、圆角、时序等确定参数 | Tokens 编译器 | CSS / DTCG / 文档语义一致，计算样式与约束检查 |
| 中观信息拓扑 (Massing Patterns) 与视窗重心 | Envelope + Builder | DOM 结构层次、视窗重心、无滚动溢出与双轨/分流稳定性 |
| 时空连续性 (Kinematics) 与状态动量守恒 | Builder (CSS/JS) | 状态迁移几何形变、过渡时序、焦点恢复与取消恢复测试 |
| 数据可读微构件 (Data Syntax & Micro-Marks) | Builder + 样式插槽 | 量纲排版对齐、阈值渐变色阶、无裸数据指标语义测试 |
| 对象布局、容器关系、信息分组 | Envelope + Builder | DOM、任务路径、跨视口结构与截图 |
| signature relationship 与体验命题 | Builder + Critic | 同任务标本、证伪、迁移验证、双重视角独立评审 |

**Critic 分级证据链与环境解耦 (Tiered Critic Evidence)**：
为了防止无头渲染环境差异（字体缺失、GPU 加速不可用、视口拉伸）导致假性阻塞断裂，Critic 验证必须分级解耦：
1. **L1 (静态语义与结构)**：DOM 语义标签、状态绑定属性 ()、ARIA 属性、文字与数据容器可达性。
2. **L2 (计算样式与光学约束)**：无头引擎提取 Computed Style（对比度、排版字阶、焦点轮廓、绝对色阶）。
3. **L3 (视觉捕获与布局感知)**：完整运行时下的多视口截图渲染与人工/模型对齐比对。
环境缺失时不阻断 L1/L2 验证，明确区分“代码语义错误”与“渲染基础设施不可用”。

因此，不要求每个 craft 名称都机械改变 CSS。要求每条已选择决定有适当消费者，产出可观察差异或明确的不适用处置。

### 6.4 安全与失败行为

- 损坏的 fragment、未知版本、错误路径：保留原始错误及来源，不吞异常后退回默认。
- 必需状态、动作后果、验证范围缺失：正式构建失败；不得空数组占位伪装完成。
- canonical 或 Tokens 来源变化：旧 Envelope 失效；只重建受影响派生物，不擅改用户源文件。
- 证据变化：相应冻结记录不能继续准入；不自动制造新的用户批准。
- 多 slice 共用 Tokens：变更需识别受影响 slice；不能在单 slice 授权下无声更新所有已冻结基线。
- 边界验证引用路径时同时检查 canonical realpath；不得通过符号链接扩大写范围。

## 7. 实施计划与确定性执行波次

以下是按 Loom/OpenSpec 规则拆解的工作包。为了避免并行执行时产生写范围重叠（如 `assemble_envelope.py` 与 `compile_tokens.py` 跨任务冲突），计划重构为 **4 个确定性无冲突波次 (Deterministic Waves)**。各波次内部任务保持文件级写范围严格无交集，跨波次依赖通过显式交付事实衔接。

### Wave 1：规则所有权收敛与共创去固定化 (纯规则与模板层)

目标：确立现行 owner 权威，退役旧 workflow 引用，解除阶段与 dialectic 的固定模板绑架。本波次不触碰编译器与派发底层代码。

#### Task W1-1 (Package A): 现行 owner 对齐与退役清理
- **写入范围**: `SKILL.md`, `references/core-kernel.md`, `references/stages/stage-3-skeleton.md`, `references/stages/stage-5-freeze.md`, `references/04-governance/usage.md`。
- **关联测试**: `tests/test_design_chain_continuity.py`, `tests/test_v10_integrity.py`。
- **验收标准**: 活跃入口不再加载 core-workflow；意图、生命周期、覆盖范围收敛至唯一现行 owner。
- **反例**: 新产品但仅请求 IA 探索时，不得被隐性规则强制进入全五阶管道。

#### Task W1-2 (Package B): 共创程序与表达指引去固定化
- **写入范围**: `references/stages/stage-0-explore.md`, `references/stages/stage-1-frame.md`, `references/dialectic/01-foundation-axes.md`, `references/dialectic/02-topology-resistance.md`, `references/dialectic/03-sensory-kinetic.md`, `references/dialectic/04-stress-falsification.md`, `templates/discussion.md`。
- **关联测试**: `tests/test_dialectic_enhancements.py`, `tests/test_semantic_freedom_regression.py`。
- **验收标准**: 阶段 0 无构建授权允许合法退出；阶段 1 解除 4 轮严格锁步，物理隐喻和 Cinnabar/Void Slate 不再作为强制默认；讨论模板支持记录最小决定的实际用户来源。
- **反例**: 用户仅对视觉表层提出修改时，不得强制重开对象模型与拓扑轮次。

---

### Wave 2：执行边界接缝闭合与派发真实化 (接缝与冻结层)

目标：彻底打通 canonical 派发技术链路，消除路径错配、载荷隐性绑架与证据冻结类型错误。

#### Task W2-1 (Package C): canonical 派发真实路径与动态 Envelope 提取
- **写入范围**: `scripts/execution_boundary.py`, `scripts/assemble_envelope.py`, `tests/test_execution_boundary.py`, `tests/test_platform_envelope.py`。
- **验收标准**:
  1. `execution_boundary.py` 支持针对 `r1.spec.md` / `r1.spec.json` 的真实路径与摘要校验，不再强制寻址 legacy `r1.md`。
  2. `assemble_envelope.py` 剥离静态硬编码的 6 个全局方法注入器和固定 `responsive_folding: 390px`，改为严格根据 Spec 中的 `methods_applied` 与 `viewports` 动态提取。
  3. 严格执行 canonical realpath 检查，防止符号链接越界。
- **反例**: 仅包含 canonical Spec 的有效原型，不得因缺失 legacy 文件或被注入未授权方法而导致派发阻断或行为漂移。

#### Task W2-2 (Package D): 冻结证据类型闭合与状态诊断对齐
- **写入范围**: `scripts/handoff.py`, `tests/test_handoff_scope_integrity.py`, `tests/test_spec_only_freeze.py`。
- **验收标准**:
  1. 修复 `retained()` 与目录型 screenshot evidence bundle 的处理，支持对目录及其内文件的递归哈希与一致性校验；目录内文件增删改均使 bundle 失效。
  2. 对齐 `check_downstream_gate` 对 Markdown 状态声明（如 blockquote 形式）的解析，防止误判为 provisional。
- **反例**: PNG-only evidence freeze 后，下游 admission 不得因读取目录抛出 `IsADirectoryError`。

---

### Wave 3：数据契约分级与单向编译贯通 (核心编译器与单向流)

目标：解决 Schema 校验死锁，实现状态分级准入，确立 Tokens 严格单向派生与脏状态熔断。

#### Task W3-1 (Package E): 分级契约模式 (Progressive Schema) 与中观装配插槽扩充
- **写入范围**: `scripts/compile_spec_ir.py`, `schemas/prototype-spec.v1.json`, `tests/test_canonical_spec_ir.py`, `tests/test_contract_seam_fidelity.py`。
- **验收标准**:
  1. 引入分级模式：`intent_spec` 仅要求问题命题、拓扑和五轴/工法意图（Stage 1 准入）；`execution_spec` 要求完整状态机与动作合约（Stage 3/4 准入），彻底解决阶段死锁。
  2. 在 `prototype-spec.v1.json` 中结构化支持中观装配插槽：`layout_directives.massing_pattern`（信息拓扑构件）、`interaction_spec.kinematics`（时空连续性协议）、`visual_directives.data_syntax`（数据微构件语法）。
  3. `compile_spec_ir.py` 移除硬编码注入的 telemetry / 4096 GPU 模板 invariants；无源领域 invariants 不注入。
  4. 修复 `interaction/inspecting` 状态 ID 拆词缺陷，保持完整标识符传递。
- **反例**: Stage 1 产出合法意图 Spec 时，不得被顶层状态机 required 规则拦截；未声明 massing 时平滑回退，不阻断编译。

#### Task W3-2 (Package F): Tokens 单向派生与严格新鲜度熔断
- **写入范围**: `scripts/compile_tokens.py`, `scripts/lint_spec_contracts.py`, `tests/test_tokens.py`, `tests/test_craft_stack.py`。
- **验收标准**:
  1. 确立单向生成流：`Discussion / Spec IR` -> `compile_tokens` -> `tokens.css`。
  2. 废弃 formal 模式下的逆向 reconciliation 入口；检测到 `tokens.css` 手工篡改且与来源 digest 不一致时，标记为 `out_of_sync` 并硬拒绝下游。
  3. 编译器完整消费 canonical `craft_stack` 与 palette，实现真实参数驱动。
- **反例**: 仅修改 palette 颜色却通过五轴注释新鲜度检查的漏检情况必须被拦截。

---

### Wave 4：消费端落地瘦身与分级评测对齐 (Agent 与验证层)

目标：释放 Builder/Critic 自由度，建立 Critic 三级降级证据链，防止无头渲染环境差异引发假性阻塞。

#### Task W4-1 (Package G): Builder/Critic 中观构件消费与认知节奏双重评审
- **写入范围**: `agents/spec-prototype-builder.md`, `agents/spec-prototype-critic.md`, `references/02-craft-methods/visual-craft.md`, `references/02-craft-methods/data-information.md`, `references/02-craft-methods/ia-interaction.md`。
- **验收标准**:
  1. **Builder 消费中观构件**：指导 Builder 依据 `massing_pattern` 构建空间重心，依据 `kinematics` 实现形变与焦点恢复过渡，依据 `data_syntax` 实现紧凑对齐与微趋势图表；移除统一大圆角、宽 padding、负字距偏见。
  2. **Critic 双重审判**：
     - *工程契约维度*：状态机覆盖、DOM 可达性、无障碍。
     - *认知品质维度*：视线信噪比 (Signal-to-Noise Ratio)、状态迁移时空动量守恒、负空间呼吸律；严禁仅因“合规无报错”放行平庸泛化界面。
  3. 支持从真实业务约束出发生成极简、原生、高密度等不同风格原型。
- **反例**: 控制台高密度原型不应被 Critic 强行要求添加毛玻璃背景；粗暴 `display: none` 丢失上下文的原型必须被 Critic 阻断。

#### Task W4-2 (Package H): Critic 分级证据链与 Eval 打包核查
- **写入范围**: `skills/spec-prototype/evals/eval.yaml`, `skills/spec-prototype/scripts/verify_prototype_quality.py`, `benchmarks/cases/golden/` 相关配置文件。
- **验收标准**:
  1. 在 `verify_prototype_quality.py` 中建立 L1 (DOM/ARIA/data-state)、L2 (Computed Style)、L3 (截图比对) 三级降级证据链；当无头浏览器环境缺失或字体不齐时，优雅降级至 L1/L2，明确标识环境未就绪而非断言代码错误。
  2. 修复 `eval.yaml` 的 include 路径，正确对齐仓库根 `agents/` 正本。
  3. 纳入 `confirmed-resume`, `scoped-feedback` 等案例，建立同内容盲评对比基线。
- **反例**: CI 无头容器因缺字体或无 GPU 渲染截图时，不应阻断基础状态机与可访问性验证。

## 8. 验证矩阵与完成标准

### 8.1 机制层：确定性断言

| 场景 | 必须证明 |
| --- | --- |
| 未提供风格、未提供物理锚 | 不补固定 craft，不伪造确认；按路线保留开放项或指出缺项 |
| 候选 A、B 与确认 C 同时出现 | 正式 IR 只消费当前有效 C |
| 用户仅授权继续调查 | 不把 continue 当成方向选择 |
| 来源包含被替代/否决决定 | 不泄漏进 sealed IR |
| canonical-only | assemble、boundary、handoff 使用一致路径 |
| legacy 与 canonical 并存 | 明确选源，禁止静默混合 |
| fragment 缺失或损坏 | 正式路径失败并保留错误上下文 |
| Tokens 来源已变 | 旧 Tokens/Envelope 不获准使用 |
| PNG-only evidence | freeze 与 admission 对同一 bundle 一致处理 |
| 状态文字自称 frozen | 没有真实批准/manifest 仍不能下游准入 |

本地运行任务对应的定向测试；主会话合流复核止于既定 `make unit`，不裸跑无参串行 pytest。全量矩阵与重型仿真走已授权异步环境。

### 8.2 会话层：共创过程是否真的改善

复用现有案例并按能力补缺口：

- `ia-only`：不制造视觉选择或强制原型。
- `ia-choice-continue`：不替用户把“继续”解释成选方向。
- `confirmed-resume`：恢复已有决定，不重问已确认事实。
- `scoped-feedback`：局部表达反馈不重建产品合同。
- `high-frequency-editor`、`long-form-reader`、`mobile-field-app`：不同产品约束下的设计迁移。
- `novel-coordination`：新关系的探索不是给常见 dashboard 换皮。

观察：问题是否必要、选项是否真正可区分、建议是否有证据、反馈是否正确落点、来源是否保留。轮数、token、wall time 是成本指标，不是质量替代指标。

### 8.3 浏览器层：复杂业务原型是否成立

优先复用 golden 的 `incident-commander`、`approval-workflow`、`editorial-reader`、`mobile-booking`。

- 跨 surface：选对象、进入详情、修改/取消、返回；验证选择、筛选、滚动与数据状态。
- 关键动作：触发、确认、提交中、成功/失败、重试/撤销；按领域适用性检查。
- 压力：长文本、空数据、大数据、快速重复动作、焦点恢复、键盘与目标设备。
- 响应式：从合同要求读取视口，不统一注入 390px/320px。
- 数据图形：量纲、基线、状态、编码可理解；不以出现 SVG 或纹理算完成。

截图只能证明其捕获状态的视觉结果，不能单独证明“两秒定位”、正确排空、取消恢复或跨页状态。

**解耦无头环境与三级证据降级 (Tiered Verification)**：
- **L1 (静态语义与结构)**: DOM 语义标签、状态绑定属性 (`data-state`)、ARIA 与焦点顺序、文本与数据容器可达性。
- **L2 (计算样式与光学约束)**: 纯无头样式引擎提取 Computed Style（对比度、排版字阶、焦点轮廓、绝对色阶）。
- **L3 (视觉捕获与布局感知)**: 完整无头浏览器多视口截图与像素/渲染比对。
当本地合流或 CI 容器缺少 GPU 硬件加速或指定字体包时，验证工具优雅降级至 L1/L2 并将 L3 标记为 `unverified`，明确区分“渲染环境缺失”与“原型语义缺陷”，避免假性破坏门禁。

### 8.4 视觉层：现代感与设计质量是否提升

固定相同 brief、业务内容、任务、平台、资产条件和可比执行预算，对 stable 与 candidate 进行匿名成对评审。评审者不预先知道版本；先独立判断，再查看设计理由。

维度：

1. **信息拓扑与信噪比**：视窗空间重心是否清晰、核心操作与环境信息层次分明（信息拓扑模版落地程度）。
2. **时空动量与状态连续性**：状态迁移是否平滑、形变是否守恒、焦点与上下文是否留存，而非粗暴切屏。
3. **数据微构件与语义表达**：数值、基线、阈值区间与量纲排版一体化，数据是否具备即时可读性与解释性。
4. **微观排版、光学与对比完成度**：字体字阶、间距网格、动态对比度在多视口下的严谨对齐。
5. **领域表达与 Signature Craft**：产品辨识度是否服务于任务本质，而非套用通用 SaaS 模板。
6. **跨页面/跨状态泛化韧性**：第二 surface 与异常边界状态下设计语言与交互逻辑是否稳健一致。

不能用“大圆角/高字重/玻璃/渐变/斜纹数量”评分。允许极简、扁平、原生惯例和高密度方向获胜。

先做小规模配对诊断，再在已批准预算内重复代表性案例；报告样本量、分歧、失败与未验证项。没有足够样本时只报告方向性结果，不宣称统计显著或普遍提升。

### 8.5 最终交付分层

- **机制修复完成**：批准范围的测试及实际接缝收据成立。
- **共创行为改善得到证据**：指定会话案例可核查，没有确认来源或局部反馈回归。
- **设计质量提升得到证据**：可比条件下的作品与独立评审支持该结论。
- **工程交付完成**：治理账本达到 Complete。

四者不得互相代替。尤其机制完成不等于视觉提升；模拟用户满意不等于真实用户批准。

## 9. 外部方法的适配边界

### Superpowers brainstorming

参考：<https://github.com/obra/superpowers/tree/main/skills/brainstorming>

借鉴：一次聚焦一个重要未知；视觉问题用视觉材料；适时小规模探索；设计内容分段讨论。代码或现有材料可以回答的问题先调查。

不照搬：另建 Spec/Plan/commit 流程、每段固定审批、强制额外文档。当前项目已经有 discussion owner、OpenSpec 与 Loom；复制外部流程会产生双源。

### grill-with-docs

参考：<https://github.com/mattpocock/skills/blob/main/docs/engineering/grill-with-docs.md>

本次依据是该说明文档，不声称读过未核实的同名完整 SKILL。

借鉴：批次提问与等待、术语一致、优先代码事实；只有难逆转、脱离背景难理解且存在真实权衡的决定才适合 ADR。

不照搬：所有回答立即写 ADR、另建通用 ledger、把 CONTEXT.md 变成完整决策数据库。该说明也不提供从每个回答到 Spec/test 的完整追踪系统；本项目应完善自己的现有来源链。

## 10. 非目标、风险与推荐顺序

### 非目标

- 不恢复 core-workflow 为新权威。
- 不新增 Stage 1.5、第二套共创流程、风格包入口或隐藏执行 DAG。
- 不将九柱五轴替换成四类工法。
- 不改 Loom Runtime，不让事件内核解释设计语义。
- 不直接修改生成物、历史 baseline、历史报告或归档 Change。
- 不因路径误判补重复 Agent 文件或覆盖有效符号链接。
- 不在当前文档交付中运行付费会话或对外发布。

### 主要风险

- **移除默认后输出暂时显得保守**：用更具体的设计命题、同内容探针和授权内的设计主动性补足，而非恢复隐藏强制皮肤。
- **Schema 一次扩展过大**：先修来源选择与真实消费者，再为必要语义增字段；保留明确 legacy 适配与迁移诊断。
- **测试继续固化风格偏见**：将“出现固定 token”改成“遵守本次作者决定且负例被拒绝”。
- **只改善 Hero、不改善产品**：第二 surface、异常状态、返回路径和目标设备必须独立验证。
- **旧冻结证据被新合同误用**：来源关系变化就失效，不能靠复用旧摘要或自动补批准继续准入。
- **评测成本膨胀**：复用现有 harness，先用机制与少量代表案例排错；完整会话矩阵在明确预算内运行。

### 推荐推进顺序

先 A/B 收敛规则，C/D 修真实接缝；再 E/F/G 打通当前有效决定与可观察产出；最后 H 验证真实共创和设计质量。

这不是从设计任务退回纯工程整治：接缝修复只保证“讨论的东西真的被做出来”；共创方法、可比较标本、表达自由和独立作品评审，才负责判断“做出来的东西是否更好”。两部分缺一不可。

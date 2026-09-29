# Design Brief Format: Google Design.md-inspired

> `google-design-md/v2` is this Skill's concise, parser-compatible design brief format,
> inspired by the idea of a human-readable design context file. It is not an official
> Google specification and does not require adoption of Material Design. Keep design
> intent authored in Markdown; frontmatter carries only stable metadata needed by the
> compiler. Add detail only when it affects a design or implementation decision.

---

## Format Principles

- YAML frontmatter contains only compiler inputs and stable identity (such as
  `spec_schema`, `slice_id`, applicable viewports/states, token reference, and
  authority when explicitly declared).
- Markdown carries the actual design argument and product decisions. Natural
  section headings are acceptable when they map to the semantic sections below;
  the compiler's accepted parser aliases remain the compatibility boundary.
- Tokens are implementation output, not a mandate to author a full palette before
  the direction is understood.
- Invariants are explicit only when they matter to this slice. Do not turn every
  design preference into a DOM/CSS gate.
- Slice scope: once `prototype/discussion.md` holds `## Slice: <slice_id>` blocks,
  the slice frontmatter lives inside its block and must name the same `slice_id`.
  `--slice <id>` reads viewports and required states from that block alone, and
  surfaces, states, actions, invariants and stress fixtures from that block plus the
  shared zones. A missing or duplicated block aborts; it never falls back to the
  whole file. A record without slice blocks is one implicit slice (legacy form).

## Illustrative rich slice (not a required template)

The following example shows parser-compatible details that a particular operational
slice might need. It is not a checklist: omit fields, axes, states, surfaces, fixtures,
and assertions that do not change the requested design or its implementation. For a
new formal slice, prefer the minimum form below and add only evidenced decisions.

```markdown
---
spec_schema: "google-design-md/v2"
slice_id: "incident-commander"
authority: "sealed_provisional"          # draft | sealed_provisional | validated | frozen_approved
stage: "hero_probe"                      # hero_probe | walking_skeleton | full_product
viewports: [390, 1280]                   # Breakpoint widths in px
required_states: [state-draft, state-sealed] # Mandatory test states
tokens_ref: "prototype/shared/tokens.css"# Direct DTCG CSS token binding
primary_surface: "cockpit-main"
---

# Surface Specification: Incident Commander Cockpit

## 1. Problem Framing & Drivers (支柱 1-2: 价值与真实地锚)
- **Core Tension**: `Throughput vs Liability` (秒级止血处置吞吐 vs 误操作责任风险).
- **Design Driver**: `tension` | `failure_mode` (脑裂状态下操作员盲目重启集群导致不可逆数据损坏).
- **Reality Anchors**:
  - `Adopt`: Datadog 密集状态指示灯矩阵、Linear 键盘第一响应速度与紧凑行高.
  - `Refuse`: 消费级多步配置向导、高侵入式全屏模态遮罩.
- **Ruthless Omissions (三大冷酷舍弃)**:
  1. 舍弃事后复盘报告与长篇图表生成 (由离线工单系统承担，不侵占应急首屏).
  2. 舍弃多集群全局拓扑编辑能力 (当前视口仅做单机应急止血与排空).
  3. 舍弃复杂的多级组织权限审批流 (仅保留本地物理签名核验).

## 2. Experience Foundation & Five Axes (支柱 6-7: 视觉刻度与五轴)
- **Five Axes Register**:
  - `density`: `dense` (微型间距、高信息吞吐、数据表格行高紧致)
  - `energy`: `kinetic` (80ms 高瞬态响应、带触觉回弹 detent)
  - `materiality`: `coated_instrument_dark` (深色物理仪器质感，低噪点哑光)
  - `rhythm`: `fluid` (无阻尼过渡，支持极速键盘行进)
  - `character`: `technical` (高精密度机械感，等宽数字对齐)
- **Seed Palette / Color Register**:
  - `--bg-void: #0b0f10;`
  - `--bg-surface: #121719;`
  - `--accent-primary: #38bdf8;`
  - `--accent-seal: #d93829;` (严格保留给破坏性不可逆封印操作)
- **Orthogonal Craft Stack**:
  - `surface_optics`: coated_instrument_dark
  - `spatial_geometry`: soft_bento_pill
  - `micro_typography`: tight_display_polarized
  - `data_marks`: hatching_dither

## 3. Spatial Anatomy & Surfaces (支柱 3 & 5: OOUX 与拓扑空间)
- **OOUX Entity Model**: 核心聚焦于 `1:N` 架构 (1 `ClusterNode` 聚合多条 `MitigationAction`).
- **Surface Allocation**:
  - **主工作区 (Primary)**: `surface/cockpit-main` (警报时序雷达与核心止血开关，高驻留、零滚动首屏).
  - **上下文视图 (Contextual)**: `surface/node-drawer` (故障节点详细遥测与调用链排查抽屉，按需展开).
  - **移动扫视图 (Glance)**: `surface/mobile-sentinel` (390px 极简状态指示，仅呈现红绿告警与紧急下线键).
- **Meso Layout Construct**:
  - `massing_pattern`: `canvas-inspector`
  - `kinematics`: `focus-restore-250ms`
  - `data_syntax`: `micro-trend-compact`

## 4. State Models & Action Lifecycle (支柱 4: 交互状态机)
- **Domain States**:
  - `domain/nominal` (集群常态): 全部节点健康，张量流水线满负荷吞吐。
  - `domain/degraded` (性能降级): 单机 NVLink 延迟超过 15%，触发亚健康预警。
  - `domain/breached` (止血阻断): 节点心跳超时，进入待隔离状态。
- **Interaction States**:
  - `interaction/idle`, `interaction/inspecting`, `interaction/armed`, `interaction/committing`
- **Data Scenarios**:
  - `data/cold-cache`: 首次加载、缓存未命中、指标抖动场景。
  - `data/burst-traffic`: 遭遇 10x 流量峰值时的 UI 批处理渲染。
- **Action Verbs (Key Bindings & Triggers)**:
  - `Space` 键瞬时检视 (proximity: 1)
  - `Enter` 键机械压感提交 (proximity: 2)

## 5. Resilience, Reality Breakers & Invariants (支柱 8-9: 破坏协议与验收门禁)
- **Four-Dimensional Reality Breakers (Break Protocol)**:
  - `stress/long-service-name` | Vector: `120 字符超长微服务名称` ➔ Expected: `单行省略截断 + Tooltip 完整展示，容器不换行撑爆`
  - `stress/zero-alert` | Vector: `无告警空状态` ➔ Expected: `展示健康绿标与上次巡检时间戳，禁止展示白屏`
  - `stress/network-lag` | Vector: `断网或 504 Gateway Timeout` ➔ Expected: `操作按钮进入禁用重试态，保留输入草稿不丢失`
- **Mandatory Test States**:
  - `state-draft`: 草稿未提交态，严禁点亮 `--accent-seal`
  - `state-sealed`: 已冻结确认态，必须渲染不可逆操作封印标
- **Design Invariants (物理验收断言)**:
  - `inv/wcag-contrast` | 核心文本与背景对比度必须满足 WCAG AA 4.5:1 | severity: blocking | verif: computed_style
  - `inv/horizontal-fit` | 320px 视口无水平滚动条 | severity: blocking | verif: dom_query
  - `inv/destructive-guard` | 破坏性止血操作必须具备二次物理确认锁 | severity: blocking | verif: dom_query
```

---

## Minimum formal slice

Use the following small form when a formal runnable slice is needed. Add state,
action, viewport, fixture, or invariant details only when they are authored and
relevant to the requested slice. The compiler can emit an `intent_spec` before
execution details exist; add those details when entering the implementation or
verification work rather than inventing them in advance.

```markdown
---
spec_schema: "google-design-md/v2"
slice_id: "<slice-id>"
viewports: [390, 1280] # only the viewports relevant to this work
primary_surface: "<surface-id>"
---

# Surface Specification: <Product / Slice>

## 1. Problem Framing & Drivers
- Core Tension: <user value> vs <constraint or risk>
- Reality Anchors: <specific reference and what to learn/refuse>
- Ruthless Omissions: <capability or surface explicitly out of scope>

## 2. Experience Foundation & Five Axes
- Design Proposition: <what becomes easier or clearer and why>
- Signature Relationship: <product-specific expression that serves the task>
- Convention Retained: <familiar behavior preserved for learnability>

## 3. Spatial Anatomy & Surfaces
- **Primary**: `surface/<id>`
- <additional surface only if needed by this slice>

## 4. Actions & States (when behavior is in scope)
- <authored task, visible action, result, and recovery>
- Required States: `<state-id>` # only when state capture is needed

## 5. Resilience & Invariants (when relevant)
- <material failure/stress case and expected behavior>
- <blocking invariant, with an observable verification method>
```

The existing rich sections and legacy multi-file format remain supported. This
minimal form clarifies the entry contract; it does not replace those compatibility
routes or authorize deleting schemas, scripts, or templates without a separate
migration and test plan.

## Compiler boundary

The compiler translates authored Markdown into canonical IR; it does not require
all downstream execution fields at the intent tier. Add detailed states, fixtures,
and invariants only when implementation or verification decisions need them. Use the
formal compiler and its focused tests as the compatibility authority; this brief is
not an instruction to run every available audit.

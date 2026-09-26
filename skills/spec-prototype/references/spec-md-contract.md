# Canonical Specification Standard: Google Design.md Architecture

> Google Design.md-inspired Industrial Specification Standard for `spec-prototype`.
> Designed for Senior Design Partners (P9+), strictly projecting the Five Axes and Nine Pillars
> into an actionable, verifiable, and zero-reverse-engineering design contract.

---

## 1. Architectural Philosophy (架构原则)

1. **Deterministic Frontmatter vs Semantic Markdown**:
   - Machine constraints (viewports, stage, authority status, slice ID, token binding) are authored via standard **YAML Frontmatter**.
   - Design intentions, spatial anatomy, and behavioral contracts are authored via structured Markdown sections.
   - **Zero Reverse-Engineering**: The compiler parses standard semantic sections without demanding brittle heading numbers or exact internal regex patterns.

2. **DTCG Direct Consumption (Token 直引)**:
   - Design tokens live in `prototype/shared/tokens.css` (compiled from W3C DTCG).
   - Builder and Critic directly import and consume tokens without intermediate code synthesis.

3. **Verifiable Invariants as First-Class Gates**:
   - Every contract terminates in testable physical invariants (`inv/<id>`) verifiable via DOM queries, computed CSS styles, or multi-viewport screenshot captures.

---

## 2. Canonical Spec Schema (`r1.spec.md` / `discussion.md`)

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

## 3. Toolchain & Automation Mapping

| 契约章节 | 对应代码与工具链输出 | 校验工具与方法 |
| :--- | :--- | :--- |
| **Frontmatter** | `r1.spec.json` 的 `identity` 与 `scope.verification_scope` | `compile_spec_ir.py` JSON Schema 校验 |
| **Experience Foundation** | `prototype/shared/tokens.css` | `compile_tokens.py` + CSS AST 校验 |
| **Spatial Anatomy** | `r1.spec.json` 的 `scope.topology_scope` | Builder 映射为 HTML 主容器与抽屉网格 |
| **State Models** | `r1.spec.json` 的 `state_model` | 浏览器 `data-state` 属性切换 |
| **Break Protocol** | `r1.spec.json` 的 `stress_fixtures` | Headless Playwright 注入超长字符与空数据截屏 |
| **Design Invariants** | `r1.spec.json` 的 `invariants` | `verify_prototype_quality.py` 自动化 DOM/CSS 审计 |

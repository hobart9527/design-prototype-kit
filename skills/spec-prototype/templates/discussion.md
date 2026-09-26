# Design discussion

## Resume

- Execution boundary: active
- Product archetype basis (`greenfield | feature-extension | refinement-audit`):
- Active track / current decision:
- Route basis (`visual-first | IA-first | IA-only | visual-only | spec-only | review-only | continuation | local-repair`), with source:
- Requested scope and stopping point:
- Product source revisions / last checked:
- Canonical Design Model status and exact artifact references:
- Current topology/prototype coverage and evidence links:
- Pending prerequisite (`none | needs_decision | needs_evidence | blocked`), impact and owner:
- Next action and its prerequisite:

“Active track” is retained for checker compatibility and means the current
uncertainty, not a mandatory Track A/Track B sequence. The route contract in
`references/04-governance/discussion.md` owns permitted stopping and exit.

## Working understanding (Nine Pillars Canonical Ontology)

| Pillar | Focus | Current statement | Evidence status (`explicit | observed | derived | hypothesis | unknown`) | Source / impact / owner |
|---|---|---|---|---|---|
| **Value** | Product thesis & outcome | | | | |
| **Research** | Empirical context & constraints | | | | |
| **Object** | Entities, content & authority | | | | |
| **Journey** | Tasks, states & continuity | | | | |
| **Topology** | Derived surface architecture | | | | |
| **Attention** | Visual hierarchy & cognitive budgeting | | | | |
| **Expression** | Five-Axis sensory calibration | | | | |
| **Interaction** | Decisive exchange & action lifecycle | | | | |
| **Resilience** | Stress limits & error recovery | | | | |

Ask only about unknowns that could materially change a consequential decision.
Proceed on sourced, delegated or reversible details and label assumptions.

## Candidate propositions (when a material choice is open)

| ID | Product question | Generative mechanism | Same task/content specimen | Convention retained | Focal Signature Relationship | Benefit / trade-off cost / learning burden | Falsification / transfer evidence | Status |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | `proposed | recommended | confirmed | rejected | inconclusive` |

Use one proposition when evidence determines the direction and enough genuinely
different propositions when a choice remains. No candidate quota applies.

## Decisions and authority

| ID | Decision or authoritative section link | Status | Reason / evidence | Actual user quote + turn/date or source locator + delegated scope | User source (`confirmed \| delegated \| synthetic-fixture`) | Affected artifacts / minimal owning scope |
|---|---|---|---|---|---|---|

Status: `proposed | confirmed | delegated | needs-evidence | superseded`.
Only an actual user decision or an explicit prior delegation can populate
`confirmed`/`delegated`; AI recommendations, Builder receipts, Critic reports and
test passes are not approval. The `User source` column records where authority
actually came from per decision: a confirmed user selection, an explicitly
delegated scope, or a synthetic-fixture actor (which carries zero human
authority). The scope column names the minimal owning decision affected, so that
feedback reopens only that decision and never the whole frontier. A bare
"continue" instruction without a chosen direction never resolves an open
direction choice into a confirmed decision. After formalization retain a link
and rationale, not a competing rule.

## Open frontier

| ID | Question | Depends on | Impact | Recommendation | Owner |
|---|---|---|---|---|---|

## Canonical 5-Stage Design Engine Record

### Stage 1: Understand & Frame (破 - 双钻与契约定义)

```yaml
---
spec_schema: "google-design-md/v2"
slice_id: "<slice_id>"
authority: "sealed_provisional"
stage: "hero_probe"
viewports: [390, 1280]
required_states: [state-draft, state-sealed]
applied_methods: [action-verb-lifecycle, context-preservation, dense-operational-console, progressive-disclosure]
primary_surface: "cockpit-main"
declared_surfaces: ["cockpit-main", "detail-drawer"]
---
```

#### 1. Problem Framing & Drivers (支柱 1-2: 价值与真实地锚)
- **Core Tension**: `Throughput vs Liability` (例如：秒级止血吞吐 vs 误操作不可逆风险)
- **Design Driver**: `tension` | `failure_mode` (例如：信息过载与误判一键排空生产节点)
- **Reference Benchmarks**:
  - `Adopt`: Datadog 密集状态矩阵、Linear 键盘高响应与紧凑排版
  - `Refuse`: 消费级多步配置向导、高侵入式全屏遮罩
- **Material Non-transfer Boundaries (Non-transfer)**: 物理仪表触觉可迁移，但严禁脱离数字媒介的伪材质伪阴影
- **OOUX Cardinality-to-Layout Anchor**: `1:1` Canvas | `1:N` Master-Detail | `N:M` Relational Graph
- **Ruthless Omissions (三大冷酷舍弃 · 绝不脑补未要求的系统能力)**:
  1. 舍弃事后复盘报告与图表导出（“收尾”仅代表结束事故处理流程，严禁脑补“一键复盘导出/审计归档”等未声明能力）
  2. 舍弃全局集群配置编辑能力（当前视口仅做应急定位与排空止血）
  3. 舍弃复杂外部权限审批流（仅保留本地主备指挥官双签）
- **Content Language (Locked)**: `zh-Hans`

#### 2. Experience Foundation & Five Axes (支柱 6-7: 视觉刻度与五轴)
- **5-Dial Style Register**:
  - `density`: `dense` (微型间距、高信息吞吐、紧凑行高)
  - `energy`: `kinetic` (80ms 高瞬态响应、触觉回弹)
  - `materiality`: `coated_instrument_dark` (深色物理仪器质感)
  - `rhythm`: `fluid` (无阻尼过渡，支持极速键盘行进)
  - `character`: `technical` (高精密度机械感，等宽数字对齐)
- **Cognitive Budgeting Allocation**:
  - Zero-learning baseline: 惯用导航与高可预测表格 (0 认知成本)
  - High-yield borrowing: 应急主交互区域引入精准微动效
- **Atmospheric Undertone & Concentric Radius check**:
  - Concentric Radius check: 内外容器圆角同心差对齐
  - Atmospheric Undertone: 依据亮度阶差建立连续空间深度
- **Seed Palette & Tokens**:
  - `--bg-void`: `#0b0f10`
  - `--bg-surface`: `#141a1d`
  - `--text-primary`: `#e6edf3`
  - `--accent-primary`: `#ff4444` (警报强调)
  - `--accent-seal`: `#ff3333` (不可逆操作终极印章)

#### 3. Spatial Anatomy & Surface Topology (支柱 3-5: 空间与层级)
- **Primary Operational Surface**: `surfaces/<slice_id>-main` (核心主控工作台，承载高频研判与操作)
- **Contextual Surface**: `surfaces/<slice_id>-drawer` (下钻检视抽屉，不脱离主视区)
- **Supporting / Glance Surface**: `surfaces/<slice_id>-mobile` (390px 移动端只读扫视哨兵)

#### 4. State Taxonomy & Action Lifecycle (支柱 8: 交互与原子动作闭环)
- **Domain States**:
  - `domain/nominal` (常规态): 全部节点健康
  - `domain/avalanche-alert` (雪崩告警): 异常节点聚集扩散
  - `domain/quarantined` (已隔离): 机器安全下线
- **Action Verb Lifecycle (必须包含破坏性操作的确认与回滚出口)**:
  - `action-space`: 检视异常节点详情 (Trigger: Space key -> Level 1 Flyout -> Feedback: 高亮锁定)
  - `action-enter`: 提交机器排空方案 (Trigger: Enter key -> Level 4 `<dialog>` 确认弹窗展示后果 -> Commit: "签发梯次排空" -> Feedback: "排空中 / 已排空")
  - `action-escape`: 紧急熔断与回滚 (Trigger: Escape key -> Commit: "回滚下线节点" -> Feedback: "已回滚")
- **Decisive Exchange 3-Frame Verification**: 触发 (Frame 1: 80ms) -> 提交 (Frame 2: 150ms) -> 结果 (Frame 3: 持久)

#### 5. Verifiable Invariants & Break Protocol (支柱 9: 韧性与证伪门禁)
- **Verifiable Design Invariants**:
  - `[inv/wcag-contrast]` (`blocking` · `dom_computed`): 核心文本必须满足 WCAG 2.2 AA (>= 4.5:1)，操作按钮 >= 3.0:1
  - `[inv/token-inheritance]` (`blocking` · `dom_computed`): 100% 继承 `prototype/shared/tokens.css`，0 内联 hex
  - `[inv/action-safety]` (`blocking` · `dom_event`): 高危排空必须弹出 `<dialog>` 二次确认，且必须提供“回滚/撤销”操作
- **The Break Protocol**:
  - `[stress/unbreakable-string]`: 超长节点标识与微服务名自动截断，禁止破坏横向布局
  - `[stress/zero-data]`: 0 异常机器时展示常态自愈健康指示，严禁白屏
  - `[stress/320px-fold]`: 320px 视口单列自然流动，无横向溢出滚动条

### Stage 2: Proposition & Probe (立 - 核心主交互物化)
- **Hero Screen Anchor Target**: `prototype/experiments/<slice_id>/anchor/index.html` (or probe path)
- **Craft Library & Geometric Invariants**:
  - Concentric Radius check ($R_{inner} = \max(0, R_{outer} - padding)$):
  - Optical Alignment applied (1-2px asymmetric nudge):
  - Tabular Numerics (`font-variant-numeric: tabular-nums` for counters/metrics):
- **Atmospheric Undertone (Anti-sterile gray bias)**:
- **Tactile Physics & Micro-dynamics** (perceptible feedback, `cubic-bezier(0.16, 1, 0.3, 1)`, calibrated settled state):
- **Physical Token Entity (`prototype/shared/tokens.css`)**:
- **Component Boundary**: Native-First HTML5 (`<dialog>`, `<details>`, `<form>`) + token recipes (zero heavy JS framework)
- **Rendered Physical Evidence**: `prototype/evidence/probes/<slice_id>/1280.png`, `390.png`
- **Gate Status (`confirmed` | `delegated`)**:

### Stage 3: Full IA Surface Rollout (拓 - 信息架构全量展开)
- **Derived Surface Topology Structure**:
  - Primary Operational Surfaces:
  - Secondary Contextual Surfaces:
  - Supporting Administrative Surfaces:
- **Rhythm: Compression & Release (anti-uniform-grid)**:
- **Data Floor: Reference Benchmarks & Zero Naked Metrics**:
- **Action Verb Semantic Continuity Check**:
- **Strict Token Inheritance** (`<link rel="stylesheet" href="../../shared/tokens.css">`, zero inline hex):

### Stage 4: Four-Dimensional Audit & Review Portal (验 - 全息走查与吸收)
- **Review Portal Harness (`prototype/review-portal.html`)**:
- **Decisive Exchange 3-Frame Verification / Inspection** (`Intent` → `Detent` → `Settled`):
- **The Break Protocol Stress Checkpoints**:
  - [ ] Unbroken long string overflow & wrap
  - [ ] 0 items (Contextual agency & creation bait)
  - [ ] 1 item (Minimum layout containment)
  - [ ] 1000 items (Scroll containment & viewport stability)
- **Five Operational States**:
  - [ ] Loading (Skeleton)
  - [ ] Empty (Contextual CTA)
  - [ ] Partial (Degraded)
  - [ ] Error (In-place diagnostic & one-click retry)
  - [ ] Overflow (Extreme length wrapping)
- **Track A & Track B Verification**:
  - Track A (Machine Floor): Zero raw hex, 100% token inheritance, WCAG AA / AAA static pass, zero console errors
  - Track B (Ergonomic Reality Floor): 5-second test or somatic intuition, dual-channel affordance, zero metaphor contamination
- **Controlled Absorption Loop (Feedback $\to$ `tokens.css` / slices $\to$ Re-verify)**:

### Stage 5: Silent Governance Compilation (冻 - 静默封版与工件交付)
- **DTCG Export (`prototype/dist/tokens.json`)**:
- **WCAG Static Contrast Audit**:
- **Handoff Manifest (`prototype/evidence/<slice_id>/<candidate_id>/freeze-manifest.json` / SHA-256 integrity)**:

## Evidence and changes

- Research and review links:
- Facts / expert judgments / preferences / hypotheses / observations:
- Synthetic-fixture provenance:
- Unverified assumptions and bounded implementation freedoms:
- Feedback received and owning node changed:
- Decisions explicitly reopened:
- Unaffected decisions and approvals preserved:

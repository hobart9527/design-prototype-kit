# Design discussion

One record, partitioned by lifecycle. **Product truth** changes almost never,
the **visual world** is shared by every surface once locked, and each **slice**
owns one self-contained `## Slice: <slice_id>` block that runs to the next `##`
heading. `compile_spec_ir.py --slice <slice_id>` reads product-level facts from
the shared zones and slice-level facts — surfaces, states, actions, invariants,
stress fixtures, viewports, required states — from that block, and the
verification scope from that block alone, so one slice's scope never leaks into
another. A record with no slice block is read as one implicit slice (legacy
form). Add a slice by appending a block; never widen an existing block to cover
a second slice.

## Resume

- Execution boundary: active
- Product archetype basis (`greenfield | feature-extension | refinement-audit`):
- Active slice (the `## Slice: <slice_id>` block this pass works in):
- Active track / current decision:
- Route basis (`visual-first | IA-first | IA-only | visual-only | spec-only | review-only | continuation | local-repair`), with source:
- Requested scope and stopping point:
- Product source revisions / last checked:
- Canonical Design Model status and exact artifact references:
- Current topology/prototype coverage and evidence links:
- Pending prerequisite (`none | needs_decision | needs_evidence | blocked`), impact and owner:
- Next action and its prerequisite:
- Stage checkpoint (`stage1-contract | stage2-probe | stage3-skeleton | stage4-audit | stage5-freeze`), completed in this turn:
- Turn budget discipline: a checkpoint is a recovery note, not a stop signal.
  Keep working while authorized scope and evidence remain, and write this block
  once per authoring pass. Stop only for an unresolved user decision, a real
  stage boundary awaiting review, or an explicit session limit.

“Active track” is retained for checker compatibility and means the current
uncertainty, not a mandatory Track A/Track B sequence. The route contract in
`references/04-governance/discussion.md` owns permitted stopping and exit.

## Product truth (产品真理 · 受众、目的、约束)

Owns what the product is and for whom. Visual choices never live here.

### Cold-start inference & seed status

- Physical Anchor: `<declared chassis, e.g. desktop workstation / mobile device, or none>`
  State the real-world object or space whose physicality drives the spatial
  chassis. An undeclared anchor blocks formal Stage 2; `none` is an intentional
  non-device decision, not missing information.

Infer silently from every workspace source before speaking. Each dimension's
evidence status records what the *sources actually support* — `[explicit]`
means a named user statement or committed document states it verbatim;
inference from a pain narrative, a persona convention or industry practice is
`[derived]`; if the sources cannot settle it, `[unknown]`.

- Actor: `[derived]` (who operates the product, from the brief's own words)
- Use scene: `[derived]` (where and under what pressure)
- Information priority: `[derived]` (what must be legible first)
- Main journey: `[derived]` (the end-to-end operator path)
- Style tone: `[derived]` (visual register, only if sources constrain it)
- Scene sentence: (one sentence composing the above as a concrete moment)
- Anti-slop match-and-refuse bans: (what this product must never do)
- Seed confirmation Gate: `[derived]` state which dimensions the sources
  settled and which remain inferred. A brief that fully specifies the
  product may justify `[explicit]` per dimension — cite the exact brief
  passage in the dimension line. Never write "需求已完全固化" or "无需额外
  用户输入": a sealed provisional contract is exactly the claim that user
  confirmation is still pending. If any dimension stays `[unknown]`, list it
  below with impact and owner.
- Unknowns that could change the current decision, impact and owner: (required when any dimension is unknown)

### Working understanding (Nine Pillars Canonical Ontology)

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

### Problem Framing & Drivers (支柱 1-2: 价值与真实地锚)
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

### Success metrics

State how this work will be judged — by the user, not by the agent. Metrics are
product outcomes and observable behaviors, never "the prototype exists".

| ID | Metric | Baseline | Target | How it is observed | Status (`[explicit] | [derived] | [hypothesis]`) |
|---|---|---|---|---|---|---|---|
| | | | | | |

Rules:
- Every metric names its observation method: a task a person performs, a number a
  real system reports, or a specific capture. "Feels better" is not a metric.
- A metric the sources never stated carries `[derived]` or `[hypothesis]` and is
  labeled as the agent's proposal awaiting the user's confirmation.
- Do not invent telemetry, analytics, or research that does not exist. If a metric
  cannot currently be observed, say so in the observation column rather than
  promising instrumentation.

## Visual world (视觉世界 · 全产品共享)

Owns what the product looks like once a direction is locked. One owner for every
slice: a slice that needs a different world reopens this zone through a decision
row; it never redeclares the world inside its own block.

### Direction Contract

Author the six blocks once the direction is locked
(`references/01-foundations/design-language.md`); leave them empty before then.

- **THESIS**:
- **OWN-WORLD**:
- **STORY**:
- **FIRST VIEWPORT**:
- **FORM**:
- **FINISH**:

### Experience Foundation & Five Axes (支柱 6-7: 视觉刻度与五轴)
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

### Project Taste & Visual Language Ledger (项目品味与视觉档案)

Records user style preferences, chosen aesthetics, and rejected visual approaches across iterations:

| Direction / Vocabulary | Disposition (`chosen \| rejected \| under-review`) | Core Reason & User Feedback | Reference Benchmark | Applicable Scope |
|---|---|---|---|---|
| (e.g. Swiss Editorial) | chosen | Clean hierarchy, high legibility for incident timeline | Linear, Substack | Global typography & rhythm |
| (e.g. Neon Cyberpunk) | rejected | Excessive visual noise, distracting during high stress | - | Color palette |

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

Authority-source discipline: a user's *pain narrative* ("上个月有人误排空，没法回滚")
is context evidence, never a `confirmed` decision — the decision row that reacts
to it stays `proposed`/`needs-evidence` until the user actually picks the
direction. Marking a derived mechanism (双签, 30s 回滚, 梯次排空) `explicit` and
citing the pain quote as its authority is an authority promotion: derived
lifecycle mechanisms carry `derived` evidence status with the pain point as
impact context.

A decision that binds one slice names its `slice_id` in the scope column;
`handoff.py` binds a freeze only to rows that name its slice.

## Open frontier

| ID | Question | Depends on | Impact | Recommendation | Owner |
|---|---|---|---|---|---|

## Slice: <slice_id>

Stage 1 contract plus the Stage 2–5 record for this slice only. Copy the whole
block to start another slice; the frontmatter `slice_id` must equal the heading.

```yaml
---
spec_schema: "google-design-md/v2"
slice_id: "<slice_id>"
authority: "draft"
stage: "hero_probe"
viewports: [390, 1280]
required_states: [state-draft, state-sealed]
applied_methods: [action-verb-lifecycle, context-preservation, dense-operational-console, progressive-disclosure]
primary_surface: "cockpit-main"
declared_surfaces: ["cockpit-main", "detail-drawer"]
---
```

### Divergence seeds

Drawn, not chosen: `python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id> --write`
fills this table from the OS entropy pool before any direction HTML is written.
The seed fixes the incidental choices the direction does not argue for; the
challenger is fused at step 4, or refused with its reason. Leave the table absent
until a divergence is actually being run.

### Spatial Anatomy & Surface Topology (支柱 3-5: 空间与层级)
- **Primary Operational Surface**: `surfaces/<slice_id>-main` (核心主控工作台，承载高频研判与操作)
- **Contextual Surface**: `surfaces/<slice_id>-drawer` (下钻检视抽屉，不脱离主视区)
- **Supporting / Glance Surface**: `surfaces/<slice_id>-mobile` (390px 移动端只读扫视哨兵)

### State Taxonomy & Action Lifecycle (支柱 8: 交互与原子动作闭环)
- **Domain States**:
  - `domain/nominal` (常规态): 全部节点健康
  - `domain/avalanche-alert` (雪崩告警): 异常节点聚集扩散
  - `domain/quarantined` (已隔离): 机器安全下线
- **Action Verb Lifecycle (必须包含破坏性操作的确认与回滚出口)**:
  ```contract:actions
  - id: action-space
    verb: 检视异常节点详情
    trigger: Space key / row click
    proximity_level: 1
    commit: 打开 Level 1 Flyout
    feedback: 高亮锁定
  - id: action-enter
    verb: 提交机器排空方案
    trigger: Enter key / button click
    proximity_level: 4
    commit: 签发梯次排空 / 确认隔离下线
    consequence: Level 4 dialog 展示不可逆操作后果；快捷双签必须确定且可用
    feedback: 立即显示“排空中 / 已排空”状态
  - id: action-escape
    verb: 紧急熔断与回滚
    trigger: Escape key / button click
    proximity_level: 1
    commit: 撤销 / 回滚 / 撤回上线
    feedback: 已回滚 / 已撤销
  ```
  机器权威来源为上述 YAML；下方散文只解释，不得另行声明不同 ID 或生命周期。
- **Decisive Exchange 3-Frame Verification**: 触发 (Frame 1: 80ms) -> 提交 (Frame 2: 150ms) -> 结果 (Frame 3: 持久)

### Verifiable Invariants & Break Protocol (支柱 9: 韧性与证伪门禁)
- **Verifiable Design Invariants**:
  - `[inv/wcag-contrast]` (`blocking` · `dom_computed`): 核心文本必须满足 WCAG 2.2 AA (>= 4.5:1)，操作按钮 >= 3.0:1
  - `[inv/token-inheritance]` (`blocking` · `dom_computed`): 100% 继承 `prototype/shared/tokens.css`，0 内联 hex
  - `[inv/action-safety]` (`blocking` · `dom_event`): 高危排空必须弹出 `<dialog>` 二次确认；模态内必须确保双人签发可被快速/确定性解锁；提交后 DOM 必须渲染明确的状态反馈（含 "已排空" 或 "排空中"）；且必须持久展示可触达的 "撤回 / 撤销 / 回滚" 动作按钮。
  - `[inv/discoverable-critical-path]` (`blocking` · `dom_query`): 关键路径上的控制不得仅以 `title` 提示、悬停浮层或散文说明其前置条件。每一步执行后，下一步的触发点必须在同一快照中直接可点；前置未满足时，必须就地呈现解锁入口（可点的席位切换、可点的补全动作），而不是渲染一个静止的禁用按钮。
- **The Break Protocol**:
  - `[stress/unbreakable-string]`: 超长节点标识与微服务名自动截断，禁止破坏横向布局
  - `[stress/zero-data]`: 0 异常机器时展示常态自愈健康指示，严禁白屏
  - `[stress/320px-fold]`: 320px / 390px 视口单列自然流动，全容器 box-sizing: border-box，严格消除横向溢出滚动条（scrollWidth == clientWidth）

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
- **Direction Status (`confirmed` | `delegated`)**:

### Stage 3: Full IA Surface Rollout (拓 - 信息架构全量展开)
- **Derived Surface Topology Structure**:
  - Primary Operational Surfaces:
  - Secondary Contextual Surfaces:
  - Supporting Administrative Surfaces:
- **Rhythm: Compression & Release (anti-uniform-grid)**:
- **Data Floor: Reference Benchmarks & Zero Naked Metrics**:
- **Action Verb Semantic Continuity Check**:
- **Strict Token Inheritance** (consume the compiled `visual_directives.token_link_tag` verbatim; never retype the relative depth, zero inline hex):

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
- **DTCG Export (`prototype/contracts/tokens/t1.json`, the `compile_tokens.py --output-json` default)**:
- **WCAG Static Contrast Audit**:
- **Handoff Manifest (`prototype/evidence/<slice_id>/<candidate_id>/freeze-manifest.json` / SHA-256 integrity)**:

### Reviewer's evaluation guide

Written for the person who will open the prototype and judge it. It states what to
look at and what would count as a failure, so the review is not a taste contest.

- **What to do first**: the exact path to the artifact, and the one task to attempt
  from visible cues alone.
- **What to check**: the 3–5 questions that decide the outcome, in priority order —
  each tied to a pillar or a success metric above.
- **What would make this fail**: the specific, observable conditions that mean the
  design did not work (a wrong first action, a missing recovery, a broken narrow
  viewport, an unreadable value), not adjectives.
- **Known limitations**: what is deliberately unimplemented, simplified, or
  `[hypothesis]`, so a gap is not mistaken for a defect or a defect for a gap.
- **Verdict options**: what "accept", "accept with changes", and "reject" mean here.

### Evidence and changes

- Research and review links:
- Facts / expert judgments / preferences / hypotheses / observations:
- Synthetic-fixture provenance:
- Unverified assumptions and bounded implementation freedoms:
- Feedback received and owning node changed:
- Decisions explicitly reopened:
- Unaffected decisions and approvals preserved:

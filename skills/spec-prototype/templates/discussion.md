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

**Two layouts, one seam.** This template is the single-record layout. The
peer **layered** layout splits the same record into `prototype/truth.md`
(product facts and the **Decisions and authority** table that `handoff.py
freeze` reads), `prototype/world.md` (the visual world and sole token
authority), and `prototype/briefs/<slice_id>.md` (one slice per file).
Templates for those three live beside this one. Both layouts load through
`read_design_record(root, slice_id)` in `spec_contract_blocks.py`; pick one
per project and stay in it.

**Machine forms.** The record is also the compiler's input, and the lists the
compiler reads as fact are declared in fenced `contract:<kind>` YAML blocks —
`contract:states`, `contract:stress`, `contract:invariants`,
`contract:required_states`, `contract:viewports`, `contract:actions`,
`contract:axes`, `contract:craft`, `contract:tokens`, `contract:meso`. The block
is authoritative; prose explains it and is never a second declaration. A bullet
outside a block is admitted only when it matches the parser's prose rule exactly,
and one that names a contract token without matching is reported as an
unadmitted declaration rather than dropped in silence. The blocks in this
template are the shipped examples; replace their content, keep their shape. A
YAML value that contains `: ` or begins with a special character must be
double-quoted, or the loader reads it as structure and the block fails to parse.
A slice missing any of the three state classes compiles to `intent_spec` and is
refused at the Stage 5 `execution_spec` boundary.

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
- Stage checkpoint (`stage1-contract | stage2-probe | stage3-skeleton | stage4-audit | stage5-freeze`), completed in this turn: `stage1-contract`
- Turn budget discipline: a checkpoint is a recovery note, not a stop signal.
  Keep working while authorized scope and evidence remain, and write this block
  once per authoring pass. Stop only for an unresolved user decision, a real
  stage boundary awaiting review, or an explicit session limit. The Turn 1→2 seam of
  the 3-turn route is such a boundary: once the design record and this block are
  written, end the turn instead of starting the anchor. Restate decision status
  verbatim (`proposed`/`provisional`); never upgrade it to `confirmed` here.

“Active track” is retained for checker compatibility and means the current
uncertainty, not a mandatory sequence. The route contract in
`references/04-governance/discussion-governance.md` owns permitted stopping and exit.

## Product truth (产品真理 · 受众、目的、约束)

Owns what the product is and for whom. Visual choices never live here.

### Cold-start inference & seed status

- Physical Anchor: `<the domain's physical object, room or procedure, or none — reason>`
  Name the real-world object or procedure a practitioner in this domain actually
  works with (e.g. `short-haul flight deck: two operator positions, instrument
  clusters in sightline sectors`), together with the mechanism it supplies and
  what must not transfer. The declaration is required; `none — <reason>` is a
  complete non-device decision, not missing information. Anchor content guides
  spatial logic and is never scored as a quality gate. Device chassis
  (`desktop workstation`, `mobile device`) belongs in FORM and `contract:viewports`,
  not here: an anchor is a mechanism, not a screen size.

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

Use the Nine Pillars as selective analytical lenses, not a Turn 1 form. Name only
those pillars whose tension could change the direction; Stage 4 may use the full
pillar set for audit coverage, scoped to the declared review.

Ask only about unknowns that could materially change a consequential decision.
Proceed on sourced, delegated or reversible details and label assumptions.

### Problem Framing & Drivers (支柱 1-2: 价值与真实地锚)
- **Core Tension**: `<A>` vs `<B>` — the authentic trade-off that drives this
  product, in this brief's own terms.
- **Design Driver**: `tension` | `failure_mode`
- **Reference Benchmarks**:
  - `Adopt`: a real product whose mechanism transfers here, with the mechanism named
  - `Refuse`: a pattern this product must not copy, with the reason
- **Material Non-transfer Boundaries**: what the cited analog cannot carry into a
  digital medium.
- **OOUX Cardinality-to-Layout Anchor**: `1:1` Canvas | `1:N` Master-Detail | `N:M` Relational Graph
- **Ruthless Omissions**: what the brief explicitly does not ask for. Name only
  omissions the brief supports; never invent capability to fill the matrix.
- **Content Language (Locked)**: `<BCP-47 tag, e.g. zh-Hans | en-US>`

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

Author all six blocks once the recommended direction is formed
(`references/01-foundations/design-language.md`). All six blocks are mandatory
before authoring prototype HTML/CSS. Never leave them empty or write
"Left empty until direction locked".

- **THESIS**: <one sentence: the visual & ergonomic claim observable at first glance>
- **OWN-WORLD**: <metaphor world: physical/analog reference, e.g. cockpit, breaker panel, drafting board>
- **STORY**: <the core task narrative unfolding across the layout>
- **FIRST VIEWPORT**: <exact content composition of the opening 1440/1280 screen>
- **FORM**: <spatial massing, grid rhythm, density, and responsive recomposition>
- **FINISH**: <surface optics, hairline border vs elevation, palette discipline, detents>

Recorded beside the six blocks, not as a seventh: the **Signature Moment** —
`- Signature Moment: <the moment> — carries <Observed Mechanism from the Physical Anchor>`,
or `none — <why no distinctive moment is needed>`. Stage 4's Signature probe checks
this line, so a `none` is a complete answer and silence is not.

### Experience Foundation & Five Axes (支柱 6-7: 视觉刻度与五轴)
- **5-Dial Style Register**:

```contract:axes
density: dense
energy: kinetic
materiality: coated_instrument_dark
rhythm: fluid
character: technical
```

每个轴的取值只在上方块内；散文只给校准锚点（[`../references/core-kernel.md`](../references/core-kernel.md) §5）。

- `density` — 微型间距、高信息吞吐、紧凑行高
- `energy` — 80ms 高瞬态响应、触觉回弹
- `materiality` — 深色物理仪器质感
- `rhythm` — 无阻尼过渡，支持极速键盘行进
- `character` — 高精密度机械感，等宽数字对齐

- **Cognitive Budgeting Allocation**:
  - Zero-learning baseline: 惯用导航与高可预测表格 (0 认知成本)
  - High-yield borrowing: 应急主交互区域引入精准微动效
- **Atmospheric Undertone & Concentric Radius check**:
  - Concentric Radius check: 内外容器圆角同心差对齐
  - Atmospheric Undertone: 依据亮度阶差建立连续空间深度
- **Palette values** (compiled into `prototype/shared/tokens.css`; the block below carries the accent seal and the status hues):

```contract:tokens
accent_seal: "#ff3333"
accent_policy: 常规强调使用 --accent-primary；仅在有不可逆或高风险时刻时另声明信号色
```

#### Proposed — visual tokens

The compiler reads a `## Proposed` / `## Confirmed` section and nothing else, so
palette, font and any authored custom property belong under this heading. The
`--font-*` slots fill the type roles; a custom property that no compiled token
covers (a layered shadow, a non-linear spacing ratio, a bespoke easing) is
authored with the same `--name: value` shape and passes through, replacing a
generated variable of the same name.

  - `--bg-void`: `#0b0f10`
  - `--bg-surface`: `#141a1d`
  - `--text-primary`: `#e6edf3`
  - `--accent-primary`: `#ff4444` (警报强调)
  - `--font-display`: `"Space Grotesk", sans-serif`
  - `--font-sans`: `"Inter", system-ui, sans-serif`
  - `--font-mono`: `"JetBrains Mono", monospace`

## Candidate propositions (when a material choice is open)

| ID | Product question | Generative mechanism | Same task/content specimen | Convention retained | Focal Signature Relationship | Benefit / trade-off cost / learning burden | Falsification / transfer evidence | Status |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | `proposed | recommended | confirmed | rejected | inconclusive` |

Use one proposition when evidence determines the direction and enough genuinely
different propositions when a choice remains. No candidate quota applies. This
table's status is evidence maturity only — a `confirmed` here is a confirmed
*proposition*, never a confirmed *decision*; decision status belongs to the
table below and its separate enum.

## Decisions and authority

| ID | Decision or authoritative section link | Status | Reason / evidence | Actual user quote + turn/date or source locator + delegated scope | User source (`confirmed \| delegated \| synthetic-fixture`) | Affected artifacts / minimal owning scope |
|---|---|---|---|---|---|---|

Status: `proposed | provisional | confirmed | delegated | needs-evidence | superseded`.
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

Authority-source discipline: a user's *pain narrative* ("上周有人误发布，无法撤回")
is context evidence, never a `confirmed` decision — the decision row that reacts
to it stays `proposed`/`needs-evidence` until the user actually picks the
direction. Marking a derived mechanism (双人签发、30s 撤回、分批发布) `explicit` and
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
build_scope: "hero_probe"
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

```contract:viewports
- 390
- 1280
```

```contract:meso
massing_pattern: canvas-inspector
kinematics: focus-restore-250ms
data_syntax: micro-trend-compact
```

```contract:craft
surface_optics: coated_instrument_dark
spatial_geometry: concentric-nested
micro_typography: tabular-numeric
data_marks: micro-trend-compact
```

- **Primary Operational Surface**: `surfaces/<slice_id>-main` (核心主控工作台，承载高频研判与操作)
- **Contextual Surface**: `surfaces/<slice_id>-drawer` (下钻检视抽屉，不脱离主视区)
- **Supporting / Glance Surface**: `surfaces/<slice_id>-mobile` (390px 移动端只读扫视)

### State Taxonomy & Action Lifecycle (支柱 8: 交互与原子动作闭环)

```contract:states
- id: domain/review-backlog
  label: 常规态
  description: 待审核稿件按优先级排队
- id: domain/publish-ready
  label: 可发布
  description: 审核意见已闭合，稿件等待发布
- id: domain/withdrawn
  label: 已撤回
  description: 稿件已从发布队列撤回
- id: interaction/idle
  description: 无焦点动作，等待操作者命中。
- id: interaction/inspecting
  description: 打开稿件、展开审核意见、等待确认。
- id: interaction/committing
  description: 发布动作已触发，等待结果回执。
- id: data/cold-cache
  description: 首次加载、缓存未命中、指标抖动。
- id: data/burst-traffic
  description: 遭遇 10x 流量峰值时的批处理渲染。
```

- **Domain States**: `domain/review-backlog` (常规态) / `domain/publish-ready` (可发布) / `domain/withdrawn` (已撤回)
- **Interaction States**: `interaction/idle` / `interaction/inspecting` / `interaction/committing`
- **Data Scenarios**: `data/cold-cache` (冷缓存) / `data/burst-traffic` (流量峰值)
- **Action Verb Lifecycle (必须包含破坏性操作的确认与回滚出口)**:
  ```contract:actions
  - id: action-open
    verb: 打开稿件详情
    trigger: row click / Enter on focused row
    proximity_level: 1
    commit: 打开稿件侧栏
    feedback: 高亮锁定
  - id: action-publish
    verb: 发布审核通过的稿件
    trigger: Enter key / button click
    proximity_level: 4
    commit: 提交发布 / 确认发布范围
    consequence: 确认框展示发布范围与后果；需要的审批入口必须可达
    feedback: 立即显示“发布中 / 已发布”状态
  - id: action-withdraw
    verb: 撤回已发布稿件
    trigger: button click
    proximity_level: 4
    commit: 撤回发布 / 恢复草稿
    feedback: 已撤回 / 已恢复
  ```
  机器权威来源为上述 YAML；下方散文只解释，不得另行声明不同 ID 或生命周期。
- **Decisive Exchange 3-Frame Verification**: 触发 (Frame 1: 80ms) -> 提交 (Frame 2: 150ms) -> 结果 (Frame 3: 持久)

### Verifiable Invariants & Break Protocol (支柱 9: 韧性与证伪门禁)

```contract:required_states
- state-draft
- state-sealed
```

```contract:invariants
- id: inv/wcag-contrast
  statement: "核心文本必须满足 WCAG 2.2 AA (>= 4.5:1)，操作按钮 >= 3.0:1"
  severity: blocking
  verification: computed_style
- id: inv/token-inheritance
  statement: "100% 继承 prototype/shared/tokens.css，0 内联 hex"
  severity: blocking
  verification: computed_style
- id: inv/action-safety
  statement: "发布或撤回必须弹出 <dialog> 二次确认；确认框必须清楚展示范围与后果；提交后 DOM 必须渲染明确的状态反馈（含 \"已发布\" 或 \"发布中\"）；且必须持久展示可触达的 \"撤回 / 恢复\" 动作按钮"
  severity: blocking
  verification: dom_query
- id: inv/discoverable-critical-path
  statement: "关键路径上的控制不得仅以 title 提示、悬停浮层或散文说明其前置条件；每一步执行后，下一步的触发点必须在同一快照中直接可点，前置未满足时必须就地呈现解锁入口而不是渲染静止禁用按钮"
  severity: blocking
  verification: dom_query
```

```contract:stress
- id: stress/unbreakable-string
  vector: "超长稿件标题与内容 ID"
  expected: "自动截断，禁止破坏横向布局"
- id: stress/zero-data
  vector: "0 篇待审核稿件的空状态"
  expected: "展示审核队列为空的下一步指引，严禁白屏"
- id: stress/320px-fold
  vector: "320px / 390px 视口"
  expected: "单列自然流动，全容器 box-sizing: border-box，严格消除横向溢出滚动条（scrollWidth == clientWidth）"
```

- **Verifiable Design Invariants** (机器权威来源为上方 `contract:invariants`；下方散文只解释，不得另立 ID)
- **The Break Protocol** (机器权威来源为上方 `contract:stress`；两者缺一不构成可用夹具)

### Later-stage evidence (Stages 2–5)

Stages 2–5 do not own fill-in fields here. Their procedures live in `references/stages/`;
what they produce is evidence, recorded where it is made: captures under
`prototype/evidence/`, the token stylesheet `prototype/shared/tokens.css`, the review
portal `prototype/review-portal.html`, the export `prototype/contracts/tokens/t1.json`
and the freeze manifest. Write a line in this record only for a decision that a later
pass must not lose, and give it a status; do not pre-author empty rows for stages that
have not run.

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
- Unaffected provisional decisions carried forward (copy each row's recorded status; a restatement never promotes `proposed` to `confirmed`):

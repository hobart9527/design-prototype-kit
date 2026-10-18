# Stage 1: Frame the Design Problem

Answer: *What should become easier, clearer, safer, or more meaningful—and for whom?*
Produce the smallest useful design brief. Use the Nine Pillars as a lens, not a form;
open alternatives only when a consequential choice is genuinely unresolved.

## Work from the brief

1. Read the user brief and only the workspace sources that can change the design.
2. Name the user, task, important objects, context, constraints, and one central
   tension or opportunity. Mark unsupported inference `[derived]` or `[hypothesis]`.
3. Inspect existing product patterns and up to two relevant references. Say what to
   adopt and refuse; references inform the decision, they do not dictate the UI.
4. Form the design proposition through **Polarized Divergence**: define what
   relationship changes, why it helps, what remains familiar, and the explicit trade-off.
   - **Mandatory Polarized Hypotheses**: unless evidence already predetermines the direction
     (see the exception below), produce **at least 2 structurally opposing
     hypotheses**, labelled explicitly as **`方向 A (Direction A)`** and **`方向 B (Direction B)`**,
     before converging on the primary prototype. Explicitly name the industry inertia or **category rut** (默认形态/套路),
     assign concrete **seeds** (种子), and ensure directions differ in underlying chassis, mental model, information topology,
     or task pacing (e.g. *Dense Matrix vs. Progressive Disclosure*, or *Conversational Prompting vs. Direct Visual Manipulation*).
     Two restylings or color variants of one spatial layout is an invalid pseudo-direction.
   - **The divergence record is a structured `### Divergence` section in the design record and explicitly presented in chat prose.**
     In Turn 1, run the six-step Divergence Generator
     ([`../dialectic/01-metaphor-benchmark.md`](../dialectic/01-metaphor-benchmark.md) §4) and record its anchors in the design record
     (the slice's `briefs/<slice>.md` on a layered tree, `prototype/discussion.md` otherwise):
     1. `rut:` — one sentence naming the category's default surface (use neutral architectural terms; do NOT mention unrequested features like 评论/社交/推荐 unless preceded by an explicit negation marker like "不做/排除"), followed by `rut_rejected:` — at least three named defaults of that category the divergence deliberately refuses, each with the reason it was refused. The list is Stage 4's falsifier: if the built design has drifted back into one of them, the divergence did not hold.
     2. Three lifeworld candidates, each naming its world and organising principle.
     3. `### Divergence seeds` — drawn or chosen seeds (`python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id> --record <the slice's record> --write` is an optional entropy source).
     4. `verdict: axes=[structure, <second axis>]` — two-axis verdict with Structure mandatory; then a per-candidate `challenger: fused(<technique>)` or `challenger: refused(<reason>)` line.
     **Chat Presentation Requirement (共创对话闭环)**: In the assistant's response to the user, explicitly state:
     ① the category rut (行业固有套路/默认形态);
     ② candidate directions labeled as `方向 A` and `方向 B` with their organizing principles;
     ③ the **两轴裁决** (two-axis verdict, explicitly contrasting them on Structure and a secondary axis);
     ④ your recommended direction with rationale;
     ⑤ end the turn with a verbatim `USER-INPUT: <question>` line so the decision authority stays with the user.
   - For each direction, articulate:
     1. The organizing principle and primary entity.
     2. What becomes effortless, and what trade-off or learning curve is accepted.
     3. The recommended direction with clear professional rationale grounded in the brief.
   - Keep each direction low-fidelity and evaluable on the product question it answers.
     In unattended or autonomous runs, the recommended direction is recorded as
     `proposed` / `provisional` in the Decisions table—never hallucinated as `confirmed`.
     This holds for every restatement too: a brief's "decisions preserved" line, the
     Resume block, and a brief that quotes the user's own request all carry the status
     as recorded (`proposed`/`provisional`). A user's brief is source evidence for a
     decision row, not a user selection of it; `confirmed` needs the user's explicit
     choice of that decision in-session, or an explicit delegation. Unconfirmed decisions
     carried forward across turns must be documented as `unaffected provisional decisions
     carried forward`, NEVER as `approvals preserved` or claimed as approved. When user
     injected input introduces new intents (e.g. "needs emergency abort and rollback"),
     the user intent is explicit fact, but the concrete derived mechanism parameters
     (e.g. a specific "5-minute undo window", wizard steps, or derived UI rules like "零长列表") remain `derived` / `provisional`
     and must NEVER be promoted to a user `confirmed` decision. When stating confirmed decisions
     in prose or briefs (`confirmed` or "用户已确认/用户已显性确认"), bound the statement strictly
     to what the user explicitly confirmed; NEVER bundle derived parameters into the confirmed clause.
     In THESIS, OWN-WORLD, and STORY, describe visual metaphor, spatial chassis, and interaction
     ergonomics — NEVER invent unrequested technical capabilities (e.g. "不可篡改的时间线", "实时全量同步",
     "自动根因分析", "标记已读", "阅读进度云同步") that the brief did not request and the prototype does not implement.
     NEVER assert unverified empirical industry or market research claims as flat facts (e.g. "No product in this category...",
     "业界均未提供此类机制", "竞品普遍缺失..."). In `rut:` and lifeworld sections, describe spatial patterns and layout expectations
     without inventing unverified market landscape surveys. All external or competitive assertions without evidence will be penalized as fabricated capabilities.
   - The user's choice of direction is the consequential decision this round exists
     to produce. When evidence already predetermines the direction (an explicit extension
     of an existing surface, a settled convention, or an explicit user delegation),
     one proposition is correct and pseudo-alternatives are waste.

   When the round's active uncertainty is one of the three below, load its dialectic
   topic — each is selectable, not sequenced, and each is entered only when that
   uncertainty is the one blocking the direction:
   - Topology & resistance → [`../dialectic/02-topology-scaffolding.md`](../dialectic/02-topology-scaffolding.md)
   - Materiality & energy → [`../dialectic/03-sensory-kinetic.md`](../dialectic/03-sensory-kinetic.md)
   - Resilience & gate → [`../dialectic/04-falsification-compile.md`](../dialectic/04-falsification-compile.md)
5. Define only the surfaces, actions, states, and stress cases needed to guide the
   requested slice. Leave the rest open; never invent capability to fill a section.
6. For each load-bearing decision, record the relevant method registry id inline in
   the Decisions table (`reality-anchors-tension-triad`, `research-evidence-ladder`,
   `context-preservation`, etc.; ids live in `methods/registry.yaml`). Select and cite
   only methods actually applied;
   do not load the registry or its method files wholesale.

Ask the user only when a decision materially changes the direction or scope. Resolve
repository facts silently. Preserve settled and delegated choices on continuation.
A reversible preference proceeds as a marked `proposed` / `provisional` recommendation
and is not re-asked; actor, core task, permissions, main journey and direction stay with
the user ([`../04-governance/discussion.md`](../04-governance/discussion.md) Human authority
and unattended fallback).

Frame is a thinking stage: its output is the design record (`discussion.md`, or
`truth.md`/`world.md`/`briefs/` on the layered tree). Build and verification tools
belong to the stages that follow. Name the scenario with neutral system primitives
(`node-cluster`, `core-api`, `data-worker`) rather than an unprompted business domain.

## Design brief format & Four High-Density Deliverables (单脑四联装)

The entire design prototype lifecycle is consolidated into four high-density assets:
```text
prototype/
├── discussion.md                           # 【唯一决策源】单文件布局；分层布局下的 Resume 索引
│   ├── truth.md                            #   分层布局：产品事实 + Decisions and authority 表
│   ├── world.md                            #   分层布局：视觉世界与令牌权威
│   └── briefs/<slice>.md                   #   分层布局：每个 slice 的表面策略与证据
├── specifications/<slice>/r1.spec.md       # 【唯一规范源】单文件完整 RFC：由 compile_spec_ir.py 编译生成
├── contracts/compiled/<slice>/r1.spec.json # 机器契约 IR：由 compile_spec_ir.py 与 r1.spec.md 一并编译，守住构建边界
├── shared/
│   └── tokens.css                          # 【唯一样式源】W3C DTCG 编译后的真实样式物理层
├── contracts/tokens/t1.json               # （可选机器导出层：`compile_tokens.py --output-json` 的默认落点）
└── experiments/<slice>/anchor/index.html   # 【唯一物化源】高保真、可交互、可独立运行的现代原型
```

**Banned in Primary Delivery**: never author the legacy fragmented contract set or a
duplicate `prototype/product.md`, and never treat `assemble_envelope.py` as an
authoring or dispatch stage. The retirement inventory and migration rules are owned by
[`../04-governance/artifact-lifecycle.md`](../04-governance/artifact-lifecycle.md).

Keep the design record as the concise human-readable decision and evidence
record. For a formal prototype, use `google-design-md/v2` frontmatter and
semantic sections documented in [`../spec-md-contract.md`](../spec-md-contract.md).
The authoritative form of every machine-read list, and the registry of what
each `contract:<kind>` block admits, are owned by
[`../04-governance/machine-contract.md`](../04-governance/machine-contract.md).
This is a Skill-owned, parser-compatible format inspired by Google Design.md;
it is not an official Google schema and does not imply Material Design adoption.

The record has two valid layouts, both loaded through the same seam
(`read_design_record(root, slice_id)` in `spec_contract_blocks.py`):

- **single-record** — one `prototype/discussion.md`, partitioned by lifecycle:
  **product truth** (audience, purpose, constraints — Stage 1 framing), the
  **visual world** (Direction Contract, Five Axes, Style Language Card and
  Reference Deconstruction per [`style-language.md`](../01-foundations/style-language.md) and
  [`reference-deconstruction.md`](../01-foundations/reference-deconstruction.md), taste ledger — one owner
  for every surface), and one `## Slice: <slice_id>` block per slice carrying
  its frontmatter, surfaces, states, actions, invariants and Stage 2–5 record.
  The Decisions table lives here.
- **layered** — `prototype/truth.md` (product facts + the Decisions table),
  `prototype/world.md` (visual world and sole token authority), and
  `prototype/briefs/<slice_id>.md` (one slice per file). `discussion.md`
  narrows to a thin resume seam.

Both layouts are admissible; a new project starts layered, and an existing
single-record project stays single-record. Pick one per project. In both layouts the
compiler reads each slice's verification scope from its own block alone, so a
second slice is added by appending a block (or a new brief), never by widening
the first. Templates live under `../../templates/`: `discussion.md` for the
single-record layout, `truth.md` + `world.md` + `briefs/_slice.md` for the
layered one.

Wherever the Decisions table lives, each row for a tension-bearing pillar
cites the applied method registry id inline (e.g. `context-preservation`,
`action-verb-lifecycle`; the registry is [`../../methods/registry.yaml`](../../methods/registry.yaml)).
One inline code span per decision row is enough — the citation is a routing
signal for downstream method audit, not a narrative device.

The brief needs only the applicable parts of:

- **Problem & proposition** — task, people, source facts, tension, outcome, omissions.
  - **Negative Boundaries & Omissions (第一版不做 · 显式反向边界)**: Record explicit omissions to maintain semantic discipline and prevent scope fabrication. Explicitly exclude unrequested lateral domains, unprompted integrations, speculative automation (e.g. magical auto-remediation, unrequested predictive AI), auxiliary post-processing workflows not justified by the core tension, and unprompted lifecycle pipelines (e.g. inventing a three-phase model "止血/收敛/收尾" as surface banners when unstated in brief).
  - **Fidelity to Stated Constraints & Invariants (约束与历史守恒)**: Honor all physical constraints, preconditions, and irreversible historical facts stated in the brief. Safety mechanisms and rollback controls must be grounded in actual system capabilities and scoped strictly to active operations, never claiming retroactive resolution of past unrecoverable states.
  - **Ground Truth Fidelity (真值守恒与零臆测归因)**: Assert as fact only what is explicitly supported by the user brief or session inputs. Never fabricate unprompted user-research findings, psychological profiles, operator experience tiers, or drill cadence splits (e.g. "expert operators will hate wizards due to frequent drills", "每步上下文窄适合新值班员", "新值班员需一次讲解"). Never fabricate unverified root-cause attributions for historical failures (e.g. asserting "无复核" or "touch-screen misclicks" was a root cause, or re-labeling incidents as "误下线/未经预览" in metrics tables when the brief only mentioned an accidental one-click drain without rollback). Never invent unprompted telemetry data sources, system capacities, or monitoring metrics (e.g. "剩余容量", "CPU水位"). Never invent unrequested operational objects (e.g. "批次"). Speculative rationale must be explicitly tagged as `[hypothesis]`, never treated or cited as ground truth facts.
  - **Decision Authority Discipline & Atomic Tagging (决策权威纪律与原子化标签)**: The `[explicit]` tag applies SOLELY to pure user statements; never bundle synthetic IDs, operational groupings, or derived boundaries under `[explicit]`. In journeys/flows, unconfirmed design mechanisms (e.g. "双人确认", "必经影响预览") must be explicitly qualified as `[derived, provisional]`, never presented as settled facts. Decisions without explicit in-session user choice carry forward as `unaffected provisional decisions carried forward` with status `proposed(provisional)` or `derived`, NEVER as `confirmed` or `approvals preserved`. Initial interpretations of brief scope and historical constraints are NOT confirmed decisions until explicitly selected by the user.
- **Experience direction & Five Axes calibration** — product-specific hierarchy, tone,
  visual mechanism, references and what is deliberately conventional. All five axes
  (Density · Energy · Materiality · Rhythm · Character) are accounted for at direction
  lock: each carries a value with the product evidence that earned it, or an explicit
  `open` with its reason. A decided axis additionally names one observable calibration
  anchor from the authored tokens or visible relationship — the core kernel owns that
  form, and it stays an anchor rather than a house number. An axis left silent is a
  defect — it reads as a model default, not a decision. This register is not a form to
  fill and not a CSS formula; `open` is a legitimate, recorded outcome and is never
  converted into a fabricated numeric value.
- **Innovation budget, modulated by mode** — name the product's **mode** first, then
  let it set how much of the surface stays familiar and how much carries the Signature
  Moment. The ratios below are **ordinal guides, not measurements**: the product-understanding
  rule against synthetic percentages still applies, so record the direction of the shift
  (more or less familiar than a neutral default) and its reason, not a computed figure:

  | Mode | When it applies | Guide (familiar / signature) | Why the shift |
  |---|---|---|---|
  | **Operate** | Expert operator, high consequence, repeated daily use | 80 / 20 | Relearning cost is paid on every shift; the signature lives in the one moment the tool exists for. |
  | **Read** | Long-form document, clause, or reference the user must trust | 75 / 25 | The measure and the text carry the experience; novelty competes with legibility. |
  | **Persuade** | First-contact surface whose job is to earn a second visit | 60 / 40 | The user owes nothing yet; convention transfers no trust it has not already earned. |
  | **Experience** | The sensory/kinetic quality *is* the product (breath, sound, rhythm) | 65 / 35 | The felt quality is the function, so craft is load-bearing rather than decorative. |

  A product may carry more than one mode across surfaces; name the mode per surface
  rather than averaging them into one number. Never spend the signature budget on a
  surface the user visits once and never on one they visit a thousand times.
- **Spatial anatomy** — primary surface and only context surfaces needed by this slice.
  The OOUX cardinality you record in the entity model sets the primary surface's
  container (`1:1` canvas, `1:N` master-detail, `N:M` board); the mapping and its
  containers are owned by
  [`Method 2`](../01-foundations/design-methods.md#method-2-ooux-cardinality-to-layout-mapping-pillars-object--topology)
  and [`ia-interaction.md`](../02-craft-methods/ia-interaction.md). One line in the
  record; do not restate the ladder here.
- **Actions & states** — consequential task, visible result, recovery, and states needed
  to express or test it.
- **Resilience & invariants** — only risks that could invalidate this design; distinguish
  hard requirements from preference and hypothesis.

Do not fill every Nine Pillar, state, surface, or Break Protocol vector. The Five
Axes are the one exception: account for all five, but a value is not owed where the
product has not earned one — `open` with its reason is a complete entry. Keep the
human brief about decisions; machine IR and CSS tokens are compiled outputs.

## Physical Anchor Declaration (Optional Guidance)

Declare the anticipated physical chassis or usage context in the design record
(the shared `prototype/truth.md` on a layered tree, or `prototype/discussion.md`)
if known (for example, `desktop workstation`, `mobile device`, or `physical_anchor: none`).
This provides structural guidance for layout choices without acting as a blocking gate
against beginning prototype exploration.

## Progressive Prototyping Without Pre-Spec Lock

Stage 1 produces the problem framing and design brief in the design record
(`prototype/truth.md` on a layered tree, or `prototype/discussion.md`).
Writing code in Stage 2 does not require a prior sealed Spec or pre-compiled Spec IR:
visual exploration and rapid prototyping precede formal contract compilation.
`intent.json` 是可选的 Stage 1 机器加速件，缺失时编译器直接从记录散文/契约块恢复。Formal compilation to Spec IR occurs upon engineering handoff (Stage 5).

## Required parser anchors (Intent Tier)

Stage 1 produces the problem framing and initial decisions in the design record,
corresponding to the `intent_spec` tier. For a record that predates `intent.json`,
the compiler recovers the intent tier from these parser-compatible headings:

```markdown
# Surface Specification: <Product / Slice>

## 1. Problem Framing & Drivers
- Core Tension: <A> vs <B>

## 3. Spatial Anatomy & Surfaces
- **Primary**: `surface/<id>`
```

Do not author Stage 3/4 execution contracts (`contract:states`, `contract:viewports`,
`contract:stress`, `contract:invariants`) during Stage 1. Those belong to the
execution tier (`execution_spec`) compiled during engineering handoff (Stage 5),
and their complete schema is documented in
[`../04-governance/machine-contract.md`](../04-governance/machine-contract.md).
Stage 1 focuses solely on problem framing, polarized divergence directions, the
Decisions and authority table, and Five Axes calibration.

## Exit

A design brief answers the current question and clearly separates facts, decisions,
proposals, and open risks, and it carries a complete `### Divergence` record (`rut:`,
`rut_rejected:` with at least three refused defaults and reasons, three lifeworld
candidates, `### Divergence seeds` (drawn, or chosen with that stated; `draw_seed.py` is optional), two-axis verdict naming Structure). **Turn 1 ends here, at the Resume block**: Stage 2 opens in
the next turn to explore 2–3 distinct visual and structural directions through rapid
prototyping, without waiting on pre-spec locks. Write no `tokens.css`, HTML or evidence
in this turn — the Resume block is recovery context for the next turn, not an approval
gate, and the Turn 1→2 seam is where a capped or resumed run picks up. Avoid mentioning
unwritten `.html` file paths in Turn 1 prose to keep execution boundaries clean.
End the reply with one line, `USER-INPUT: <the direction question for the user>` (all uppercase
ASCII `USER-INPUT:`, never translate to Chinese or alter punctuation), and make no
further tool call; that line is the observable stop signal for the seam.

When resuming or receiving the user's reply: if the user provides a neutral, non-committal answer
(e.g. "没有偏好", "按常规做", generic tool defaults), or the question was already presented without preference,
do NOT re-ask the same question. Immediately apply the unattended fallback from
[`../04-governance/discussion.md`](../04-governance/discussion.md): adopt the two-axis verdict's
recommended direction on a `proposed` / `provisional` basis, and proceed directly to Turn 2 make.

## Routing Out of Frame

The comparison returns one of three states; the route follows the state, not a
fixed sequence:

- **Direction authorized** (an in-session user choice or explicit delegation) or
  **local repair** (an endorsed direction, a scoped fix) → route directly to
  [Stage 3](stage-3-skeleton.md) or [Stage 4](stage-4-audit.md). The Stage 2
  dual-slot build does not apply; manufacturing a second direction here is waste.
- **Direction materially undecided** → [Stage 2](stage-2-probe.md) builds the
  physical `dirs/a|b` comparison before the anchor. An unattended run proceeds on
  a `proposed` / `provisional` basis, never `confirmed`.

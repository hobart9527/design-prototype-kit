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
4. Form the design proposition: what relationship changes, why it helps, what
   remains familiar, and its cost or learning burden. Offer alternatives only where
   evidence leaves a real choice. Recommend one.
   - **A new product defaults to 2–3 structurally distinct low-fidelity directions
     before the main prototype.** The directions must differ in structure, not in
     surface styling: a different organising principle, different primary object,
     or a different pacing of the central task. Two recolourings of one layout is a
     single direction counted twice.
   - Keep each direction genuinely low-fidelity — enough to judge the structure and
     the trade-off, not a finished screen. Compare them on the product question they
     answer, not on polish.
   - The user's choice of direction is the consequential decision this round exists
     to produce. When evidence already determines the direction (an extension of an
     existing product, a settled convention, a delegated choice), one proposition is
     correct and the others are waste.

   When the round's active uncertainty is one of the three below, load its dialectic
   topic — each is selectable, not sequenced, and each is entered only when that
   uncertainty is the one blocking the direction:
   - Topology & resistance → [`../dialectic/02-topology-scaffolding.md`](../dialectic/02-topology-scaffolding.md)
   - Materiality & energy → [`../dialectic/03-sensory-kinetic.md`](../dialectic/03-sensory-kinetic.md)
   - Resilience & gate → [`../dialectic/04-falsification-compile.md`](../dialectic/04-falsification-compile.md)
5. Define only the surfaces, actions, states, and stress cases needed to guide the
   requested slice. Leave the rest open; never invent capability to fill a section.

Ask the user only when a decision materially changes the direction or scope. Resolve
repository facts silently. Preserve settled and delegated choices on continuation.

## Design brief format & Four High-Density Deliverables (单脑四联装)

The entire design prototype lifecycle is consolidated into four high-density assets:
```text
prototype/
├── discussion.md                           # 【唯一决策源】单文件布局；分层布局下的 Resume 索引
│   ├── truth.md                            #   分层布局：产品事实 + Decisions and authority 表
│   ├── world.md                            #   分层布局：视觉世界与令牌权威
│   └── briefs/<slice>.md                   #   分层布局：每个 slice 的表面策略与证据
├── specifications/<slice>/r1.spec.md       # 【唯一规范源】单文件完整 RFC：IA 拓扑、状态机、Break 协议
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
  **visual world** (Direction Contract, Five Axes, taste ledger — one owner
  for every surface), and one `## Slice: <slice_id>` block per slice carrying
  its frontmatter, surfaces, states, actions, invariants and Stage 2–5 record.
  The Decisions table lives here.
- **layered** — `prototype/truth.md` (product facts + the Decisions table),
  `prototype/world.md` (visual world and sole token authority), and
  `prototype/briefs/<slice_id>.md` (one slice per file). `discussion.md`
  narrows to a thin resume seam.

Either layout is admissible; pick one per project. In both layouts the
compiler reads each slice's verification scope from its own block alone, so a
second slice is added by appending a block (or a new brief), never by widening
the first. Templates live under `../../templates/`: `discussion.md` for the
single-record layout, `truth.md` + `world.md` + `briefs/_slice.md` for the
layered one.

The brief needs only the applicable parts of:

- **Problem & proposition** — task, people, source facts, tension, outcome, omissions.
- **Experience direction & Five Axes calibration** — product-specific hierarchy, tone,
  visual mechanism, references and what is deliberately conventional. All five axes
  (Density · Energy · Materiality · Rhythm · Character) are accounted for at direction
  lock: each carries a value with the product evidence that earned it, or an explicit
  `open` with its reason. An axis left silent is a defect — it reads as a model default,
  not a decision. This register is not a form to fill and not a CSS formula; `open` is a
  legitimate, recorded outcome.
- **Innovation budget, modulated by mode** — name the product's **mode** first, then
  let it set the split. The default is 70% familiar / 30% Signature Moment; the mode
  moves it, and the chosen split is recorded with its reason:

  | Mode | When it applies | Split (familiar / signature) | Why the shift |
  |---|---|---|---|
  | **Operate** | Expert operator, high consequence, repeated daily use | 80 / 20 | Relearning cost is paid on every shift; the signature lives in the one moment the tool exists for. |
  | **Read** | Long-form document, clause, or reference the user must trust | 75 / 25 | The measure and the text carry the experience; novelty competes with legibility. |
  | **Persuade** | First-contact surface whose job is to earn a second visit | 60 / 40 | The user owes nothing yet; convention transfers no trust it has not already earned. |
  | **Experience** | The sensory/kinetic quality *is* the product (breath, sound, rhythm) | 65 / 35 | The felt quality is the function, so craft is load-bearing rather than decorative. |

  A product may carry more than one mode across surfaces; name the mode per surface
  rather than averaging them into one number. Never spend the signature budget on a
  surface the user visits once and never on one they visit a thousand times.
- **Spatial anatomy** — primary surface and only context surfaces needed by this slice.
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
Formal compilation to `intent.json` / Spec IR occurs upon engineering handoff (Stage 5).

## Required parser anchors

For a record that predates `intent.json`, the compiler still recovers the intent
tier from these parser-compatible headings:

```markdown
# Surface Specification: <Product / Slice>

## 1. Problem Framing & Drivers
- Core Tension: <A> vs <B>

## 3. Spatial Anatomy & Surfaces
- **Primary**: `surface/<id>`
```

The state model and resilience sections have a machine form too, and a record that
reaches Stage 5 without it compiles to `intent_spec` and is refused at the
`execution_spec` boundary. `compile_spec_ir.py` is the sole parsing authority; the
forms below are its admission rules, not a second specification.

Write the lists the compiler reads as fact in fenced `contract:<kind>` blocks.
The block is authoritative and fails closed on an authoring error — an unknown
prefix, a missing field, a duplicate id, an out-of-enum severity. A `domain/` and
`data/` entry carries a `description`; an `interaction/` entry is an id alone.
A YAML value containing `: ` or starting with a special character must be quoted.

```markdown
## 3. State Model
```contract:states
- id: domain/<id>
  label: 业务状态名称
  description: 一句话语义描述
- id: interaction/<id>
  description: 一句话交互描述
- id: data/<id>
  description: 一句话数据场景说明
```

## 6. Viewport 与强制测试状态
```contract:viewports
- 390
- 1280
```
```contract:required_states
- state-a
- state-b
```

## 7. Break Protocol
```contract:stress
- id: stress/<id>
  vector: 破坏向量
  expected: 期望恢复行为
```

## Design Invariants
```contract:invariants
- id: inv/<id>
  statement: 断言
  severity: blocking
  verification: computed_style
```
```

The prose forms (`- `domain/<id>` (label): description`, `- `stress/<id>` | Vector:
… | Expected: …`, `- `inv/<id>` | 断言 | severity: …`) remain readable for a record
that predates the blocks. They are the compatibility route, not the recommended
one: prose admission is inferred, so it is where a mis-parse comes from. A
`stress/` bullet needs both `Vector:` and `Expected:`; one missing a field is not
a usable fixture. `severity` defaults to `advisory` and `verification` to `manual`.

A machine-shaped bullet that names a contract token but matches no admission rule
is reported as an unadmitted declaration and aborts the compile, rather than being
dropped while the run continues with the field empty. That report is the signal
that a declaration was written in a form the compiler does not read.

## Exit

A design brief answers the current question and clearly separates facts, decisions,
proposals, and open risks. Continue directly to Stage 2 to explore 2–3 distinct visual
and structural directions through rapid prototyping without waiting on pre-spec locks.
A checkpoint is recovery context, not an approval gate.

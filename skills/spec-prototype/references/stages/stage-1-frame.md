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
5. Define only the surfaces, actions, states, and stress cases needed to guide the
   requested slice. Leave the rest open; never invent capability to fill a section.

Ask the user only when a decision materially changes the direction or scope. Resolve
repository facts silently. Preserve settled and delegated choices on continuation.

## Design brief format & Four High-Density Deliverables (单脑四联装)

The entire design prototype lifecycle is consolidated into four high-density assets:
```text
prototype/
├── discussion.md                           # 【唯一决策源】人机共创、五轴校准、业务张力事实台账
├── specifications/<slice>/r1.spec.md       # 【唯一规范源】单文件完整 RFC：IA 拓扑、状态机、Break 协议
├── shared/
│   └── tokens.css                          # 【唯一样式源】W3C DTCG 编译后的真实样式物理层
├── contracts/tokens/t1.json               # （可选机器导出层：`compile_tokens.py --output-json` 的默认落点）
└── experiments/<slice>/anchor/index.html   # 【唯一物化源】高保真、可交互、可独立运行的现代原型
```

**Banned in Primary Delivery**:
- NEVER author legacy 6-piece files (`contracts/foundation/f1.md`, `contracts/surface-maps/m1.md`, `contracts/tokens/t1.md`, `contracts/slices/.../c1.md`, `specifications/.../r1.md`).
- NEVER author a duplicate `prototype/product.md` — all product facts and dialectic context belong in `prototype/discussion.md`.
- NEVER generate the legacy fragmented contract set in primary delivery. `assemble_envelope.py` remains a compatibility/benchmark helper only; it is not an authoring or dispatch stage.

Keep `prototype/discussion.md` as the concise human-readable decision and evidence
record. For a formal prototype, use `google-design-md/v2` frontmatter and semantic
sections documented in [`../spec-md-contract.md`](../spec-md-contract.md). This is a
Skill-owned, parser-compatible format inspired by Google Design.md; it is not an
official Google schema and does not imply Material Design adoption.

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

Declare the anticipated physical chassis or usage context in `prototype/discussion.md`
if known (for example, `desktop workstation`, `mobile device`, or `physical_anchor: none`).
This provides structural guidance for layout choices without acting as a blocking gate
against beginning prototype exploration.

## Progressive Prototyping Without Pre-Spec Lock

Stage 1 produces the problem framing and design brief in `prototype/discussion.md`.
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

## Exit

A design brief answers the current question and clearly separates facts, decisions,
proposals, and open risks. Continue directly to Stage 2 to explore 2–3 distinct visual
and structural directions through rapid prototyping without waiting on pre-spec locks.
A checkpoint is recovery context, not an approval gate.

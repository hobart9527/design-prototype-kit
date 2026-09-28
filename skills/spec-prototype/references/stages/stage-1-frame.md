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
- NEVER run `materialize_contracts.py` in primary delivery.

Keep `prototype/discussion.md` as the concise human-readable decision and evidence
record. For a formal prototype, use `google-design-md/v2` frontmatter and semantic
sections documented in [`../spec-md-contract.md`](../spec-md-contract.md). This is a
Skill-owned, parser-compatible format inspired by Google Design.md; it is not an
official Google schema and does not imply Material Design adoption.

The brief needs only the applicable parts of:

- **Problem & proposition** — task, people, source facts, tension, outcome, omissions.
- **Experience direction & Five Axes calibration** — product-specific hierarchy, tone,
  visual mechanism, references and what is deliberately conventional. Five Axes are optional
  continuous coordinates on relevant dimensions, balancing 70% familiarity with 1 signature
  relationship/moment under the 70/30 innovation boundary.
- **Spatial anatomy** — primary surface and only context surfaces needed by this slice.
- **Actions & states** — consequential task, visible result, recovery, and states needed
  to express or test it.
- **Resilience & invariants** — only risks that could invalidate this design; distinguish
  hard requirements from preference and hypothesis.

Do not fill every Nine Pillar, Five Axis, state, surface, or Break Protocol vector.
Keep the human brief about decisions; machine IR and CSS tokens are compiled outputs.

## Sealed Provisional Baseline Closure

For a formal runnable prototype, establish the applicable sealed provisional Spec
baseline before runnable code. A focused design brief or exploration is not itself a
request to seal or freeze the whole product.

## Formal prototype compilation

When a runnable formal prototype is requested, author the minimum contract in
`prototype/discussion.md`, then run the documented `compile_spec_ir.py` and
`compile_tokens.py` commands in one shell invocation. The compiler creates the machine
IR and human `.spec.md` view; fix actionable compiler errors at their authored source.
Do not inspect compiler source to learn design decisions. Lightweight exploration,
spec-only discussion, and local review do not require the full formal pipeline.

## Required parser anchors

For the formal intent tier, retain the existing parser-compatible headings and fields:

```markdown
# Surface Specification: <Product / Slice>

## 1. Problem Framing & Drivers
- Core Tension: <A> vs <B>

## 3. Spatial Anatomy & Surfaces
- **Primary**: `surface/<id>`
```

Add frontmatter `spec_schema: "google-design-md/v2"`, `slice_id`, and only the
applicable `authority`, `stage`, `viewports`, `required_states`, and `primary_surface`.
Use semantic headings accepted by the contract parser. Later execution details can be
added when the work reaches them; do not pre-complete downstream decisions.

## Exit

A design brief answers the current question and clearly separates facts, decisions,
proposals, and open risks. For a formal prototype, synthesize its applicable contract
and code directly in the same turn when requested and possible. A checkpoint is recovery
context, not an approval gate.

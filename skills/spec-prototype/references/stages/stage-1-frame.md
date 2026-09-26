# Stage 1: Understand & Frame (破 - 魂立约)

Answer one question: *"What is the durable contract we are about to prove or
disprove?"* Stage 1 converts intent into a complete, sealed provisional Design
Specification spanning problem ontology, topology, visual register, and
interaction contracts.

## Cadence Principle

Zero black-box guessing, zero manufactured friction. Coalesce inquiries when
intent or delegation is clear; invoke `AskUserQuestion` only when genuine forks
exist (Direction A vs B, or an unresolved core value tension).

## Design Driver

Every consequential decision must name its driver explicitly; a driver left
implicit becomes an ungrounded aesthetic preference. Record one or more:

- **tension** — the opposing forces the product must hold simultaneously
  (`Throughput vs Liability`).
- **constraint** — a hard boundary the solution cannot cross.
- **failure mode** — the concrete way the experience breaks under stress.
- **opportunity** — the signature relationship worth spending expressive courage on.
- **uncertainty** — the open question that the later probe must resolve.

Base the driver on Reality Benchmark Anchors (Linear, Datadog, iA Writer, Stripe,
or physical instruments) rather than invented rationale.

## Selectable Method Topics (渐进式设计共创 · Grilling & Brainstorming Engine)

Stage 1 is a progressive, guided design conversation. The Agent acts as an
experienced design partner, projecting the Five Axes and Nine Pillars into
concrete, visual, and experiential choices through **selectable method topics** —
NOT a mandatory physical-metaphor-first ordering and NOT a fixed four-round
lockstep.

### Interaction Principles (Grilling & Brainstorming Protocol)
1. **Agent Fact-Finding vs Human Decision**:
   - Facts belong to the Agent: search repository sources (`product.md`, PRDs, code models) silently via read-only tools. NEVER ask the user what the codebase already tells you.
   - Trade-offs belong to the User: present 2~3 concrete options with trade-offs, then give a clear recommended choice marked with `➡️`.
   - **Materially Different Invariant**: presented options must diverge in information architecture, task flow, or core interaction model — never be stylistic variants of one idea (recoloring, re-padding, or re-spacing the same layout is not an option set). If genuinely distinct hypotheses do not exist, present fewer options and say why rather than padding the set.
   - **Evidence Label Discipline**: `explicit` is reserved for decisions traceable to an actual user message or approved source — quote the locator. Agent-derived professional judgment (style tone, visual theme, metaphor anchors, benchmark references, entity models) MUST be recorded as `derived` (or `hypothesis`), never `explicit`, even when the user has confirmed the overall direction. A confirmed direction confirms the decision, not its evidence class.
   - **Method ID Citation Invariant**: explicitly cite active method registry IDs (e.g. `action-verb-lifecycle`, `context-preservation`, `dense-operational-console`, `progressive-disclosure`, `ooux-mapping`, `the-break-protocol`) in `discussion.md` and spec frontmatter under `applied_methods:` to preserve traceability.
   - **Zero Capability Fabrication**: never synthesize unrequested system capabilities (e.g. automatic remediation / 自愈) into user journeys or core contracts unless stated in ground truth. Keep user journeys strictly bounded to the requested operational scope.
2. **Selectable Topics, Not Sequential Gates**:
   - The four topics below are independent method modules: enter whichever topic
     owns the currently active uncertainty. No topic requires another to settle
     first, and no fixed ordering or round count is mandated.
   - A topic loads when its question is live and is skipped when the relevant
     decision is already settled, delegated, or out of scope.
3. **Minimal Reopening & Honest Settlement**:
   - Feedback reopens only the affected minimal owning decision; every other
     settled decision stays ratcheted shut unless the user explicitly requests
     an overrule.
   - Never present unapproved options as confirmed: only an actual user
     selection or an explicit delegation populates a confirmed decision in
     `prototype/discussion.md`. A bare "continue" resumes authorized work but
     resolves no open direction choice.
   - Record the concise Decision Frontier after each settlement, listing only
     the topics actually in play:
     ```text
     Design Frontier:
       ✓ [Topic: Metaphor & Benchmark] <Settled choice>
       ◐ [Topic: Topology & Scaffolding] <Active question>
       ○ [Topic: Sensory & Kinetic Imprint] (not yet entered)
       ○ [Topic: Falsification & Auto-Compile] (not yet entered)
     ```

### Available Method Topics

#### Topic: Physical Reality & Modern Benchmark (Metaphor & Character)
- **Lazy Module**: `references/dialectic/01-metaphor-benchmark.md` (<80 lines).
- **Pillars & Axes**: 9-Pillar: Mental Model & Resistance; 5-Axis: Character.
- **Method**: Project 2~3 real-world physical mechanisms (e.g. Precision Caliper vs Customs Clearance vs Editorial Proofing Table), each paired with modern digital benchmarks (Linear, Bloomberg, Stripe, GitHub PR) stating what to adopt and what to refuse. A physical metaphor is an optional anchor: record its explicit transfer / non-transfer boundary when used.
- **Question Format**:
  ```markdown
  ❓ **Q1** - **Physical Reality Metaphor & Product Character**: <exposition of domain tension and 2~3 candidate archetypes with trade-offs>

  ➡️ <recommended archetype with justification>
  ```
- **Settlement**: When entered, lock primary metaphor (or its declared absence), core tension, and Character profile.

#### Topic: Spatial Density & Layout Scaffolding (Topology & Resistance)
- **Lazy Module**: `references/dialectic/02-topology-scaffolding.md` (<60 lines).
- **Pillars & Axes**: 9-Pillar: Topology & Journey; 5-Axis: Density & Rhythm.
- **Method**: Present 2~3 structural layouts via pure text ASCII wireframes (NO COLOR, ONLY STRUCTURE). Clarify Container Proximity Ladder (Level 0~4) for hazardous vs routine actions.
- **Settlement**: Lock layout profile (`adaptive-workspace` or `editorial-dossier`), visual centroid, and Density/Rhythm values.

#### Topic: Material Substrate, Palette Discipline & Kinetic Imprint (Materiality & Energy)
- **Lazy Module**: `references/dialectic/03-sensory-kinetic.md` (<100 lines).
- **Pillars & Axes**: 9-Pillar: Color Semantics & Micro-timing; 5-Axis: Materiality & Energy.
- **Method**: Present tangible material moodboards (Void Slate vs Organic Bone) as optional anchors with explicit transfer / non-transfer boundaries and exact hex tokens. Define the Signature Accent (`--accent-seal`) with any negative boundaries as product-semantic rules decided per product, not global template mandates. Specify the Decisive Exchange 3-Frame kinetic response when energy is a live question.
- **Settlement**: Lock `--accent-seal` (if a signature accent is chosen), substrate tokens, and kinetic timing.

#### Topic: Falsification Boundary & Automated Contract Compilation (Resilience & Gate)
- **Lazy Module**: `references/dialectic/04-falsification-compile.md` (<100 lines).
- **Pillars & Axes**: 9-Pillar: Resilience & Interaction Lifecycle.
- **Method**: Establish the 5-second perceptual falsification test and 4-dimensional reality breakers (Unbreakable string, 0-item state, 320px fold, rapid interruption).
- **Canonical Schema Requirement**: Authors are encouraged to use the Google Design.md Architecture with YAML frontmatter defined in [`../spec-md-contract.md`](../spec-md-contract.md) or the canonical sections in `04-falsification-compile.md` §5. Frontmatter (viewports, stage, authority) and semantic sections eliminate compiler guessing. Do not reverse engineer compilers via ad-hoc python scripts.
- **Execution**: Trigger `python3 skills/spec-prototype/scripts/compile_spec_ir.py --slice <slice-id>` to compile canonical machine IR (`.spec.json`) and single-file RFC view (`.spec.md`), followed by `compile_tokens.py`. Status is sealed as `sealed_provisional`. (Legacy `materialize_contracts.py` remains available for multi-file backwards compatibility).
## Macro Double Diamond

### Discover — Pillars: Value, Research
- **Reference Benchmarks**: select high-persuasion industry anchors as the shared
  consensus fulcrum; refuse inventive fabrication.
- **Tension Triad & Inversions**: dig the product's deep-water contradictions and
  record the applicable Design Drivers plus non-goal boundaries in
  `prototype/product.md`. A declared tension is one valid driver, not a mandatory
  one; a constraint- or opportunity-driven product records that driver instead.
- **Signature vs Convention Discipline**: reserve design tension, tactile
  character, and signature micro-motion for the single core interaction surface;
  every supporting, settings, tabular, and form surface follows established
  industry interaction patterns.
- **Ruthless Omissions & Non-goals**: build a non-goal firewall that severs
  invalid complexity. See [`../01-foundations/product-understanding.md`](../01-foundations/product-understanding.md).
- **Gated Output**: `prototype/product.md` after human consensus.

### Define — Pillars: Object, Journey, Topology
- **OOUX Cardinality-to-Layout Anchor**: entity cardinality constrains the spatial
  candidate, and task frequency, visual centroid, and device character decide the
  final layout.
  - `1 : 1` focused entity → Focused Canvas / Dedicated Reader (deep focus, no split).
  - `1 : N` master-detail → Master-Detail Split Rack / Stream (sequential navigation, high-frequency comparison).
  - `N : M` relational network → Relational Matrix / Multi-Column Canvas (multi-filter, relational topology).
- **Material Non-transfer Boundaries**: define exactly where physical metaphor may
  migrate. Tactile detents, layered light, and clear feedback transfer; pseudo-
  materiality detached from the digital medium is forbidden.
- **Derived Surface Topology & Surface Evidence Gate**: derive the candidate surface topology,
  strictly validating each candidate against the 5-point Surface Evidence criteria
  ([`interpretation-rules.md`](../04-governance/interpretation-rules.md#5-surface-evidence):
  `UI actor`, `User task`, `Entry point`, `Observable outcome`, `Interaction authority`).
  Surfaces lacking explicit or derived evidence remain `unknown` or `backend_only` and
  SHALL NOT generate speculative frontend contracts.
  Name Primary, Contextual, and Supporting surfaces; resist page-count inflation.
- **Gated Output**: `prototype/contracts/surface-maps/m1.md` after human consensus.

### Develop — Pillars: Attention, Expression / Five Axes
- **5-Dial Style Register (Optional Calibration)**: under the Expression pillar, calibrate
  Density, Energy, Materiality, Rhythm, and Character when the sensory direction has genuine
  ambiguity or requires contrasting proposals. The Five Axes serve as an evaluative coordinate
  register, not a compulsory checklist. Apply the Qualitative-Adjective Translation Protocol
  (ban bare buzzwords like "高级", "现代"; expand into `[dimension] + [boundary] + [counter-example]`)
  and emit a concrete proposal with initial palette anchors (`--accent-primary`, `--bg-void`),
  axis orientation, and trade-off notes.
- **Orthogonal 4-Axis Craft Stack (Authorable Axes)**: alongside the Five Axes,
  four orthogonal craft axes travel with the sealed foundation and envelope as
  `craft_stack`. They carry NO fixed method defaults: each axis is authored from
  the product's own settled decisions, and every authored value records its
  product-semantic source:
  - `surface_optics` — from the Materiality axis and the product's surface
    decision; authored values map to compiled registers (e.g. `matte_pigment_wash`
    or `coated_instrument_dark`). Surfaces then consume `--surface-tint` and
    `--surface-specular` rather than raw gradients.
  - `spatial_geometry` — from the Density axis and the product's massing
    decision (e.g. bento padding, pill triggers via `--radius-pill`).
  - `micro_typography` — from the Character axis (e.g. display tracking, weight,
    tabular numerals).
  - `data_marks` — from the product's data-texture decision (e.g. SVG
    `--pattern-hatch-45` hatching or segmented bars instead of flat bars).
  Explicit `surface_optics: ...`-style declarations in the 5-Dial register are
  the authoring route; `compile_spec_ir.py` emits the resolved stack into
  `foundation.craft_stack` and `assemble_envelope.py` projects it into
  `visual_directives.craft_stack`.
  derives a 16-step physical elevation matrix by luminance delta and generates
  `prototype/shared/tokens.css` (plus `prototype/contracts/tokens/t1.json`).
- **Cognitive Budgeting**: separate the zero-borrow low-entropy base (routine
  navigation and content, 0 learning cost, 0 perturbing animation) from the high-
  yield borrow zone (core operation surface, purposeful micro-motion permitted).
- **Gated Output**: `prototype/contracts/foundation/f1.md` and `prototype/shared/tokens.css`.

### Deliver — Pillars: Interaction, Resilience
- **Action Verb Lifecycle**: close the semantic loop of Trigger → Context → Commit
  → Feedback; one atomic verb, no synonym drift.
  - **Verb Budget Invariant**: each action verb must trace to a user-stated need or a marked `[hypothesis]`/`[derived]` proposal. Never upgrade a vague user word into a concrete system capability: "收尾" (wrap up) does not authorize "生成复盘报告" (generate postmortem report), "记录" does not authorize "自动归档到审计系统", "管理" does not authorize a specific export/integration. When a richer capability seems professionally necessary, list it as a separate `derived` proposition with its cost — not as settled scope.
- **The Break Protocol**: predefine long-string truncation, 0/1/1000 states, and
  viewport fold limits.
- **Automated Contract Compilation**: run `python3 skills/spec-prototype/scripts/compile_spec_ir.py --slice <slice-id>`
  to compile the canonical machine IR (`prototype/contracts/compiled/<slice_id>/r1.spec.json`)
  plus its single-file human RFC view (`prototype/specifications/<slice_id>/r1.spec.md`),
  then `compile_tokens.py` for `prototype/shared/tokens.css`. Legacy compatibility
  alternative: `python3 skills/spec-prototype/scripts/materialize_contracts.py`
  still emits the multi-file `c1.md` / `r1.md` set for backwards-compatible readers.

## Sealed Provisional Baseline Closure

Stage 1 ends only when the canonical sealed provisional baseline is fully
materialized: `prototype/contracts/compiled/<slice_id>/r1.spec.json` (machine IR),
`prototype/specifications/<slice_id>/r1.spec.md` (single-file human RFC), and
`prototype/shared/tokens.css` (authority status: sealed provisional). The baseline
is then sealed and passes directly to [Stage 2](stage-2-probe.md) probe falsification.

Optional legacy compatibility: the multi-file `prototype/product.md`,
`prototype/contracts/surface-maps/m1.md`, `prototype/contracts/foundation/f1.md`,
`prototype/contracts/slices/<slice_id>/c1.md` and
`prototype/specifications/<slice_id>/r1.md` set may still be materialized via
`materialize_contracts.py` for legacy readers; it is not a Stage 1 closure
requirement.

## Exit

Legal exit is the validated `spec-only` contract set. A formal candidate still
requires this sealed provisional Spec; only a bounded probe may proceed without
it via [Stage 0](stage-0-explore.md).

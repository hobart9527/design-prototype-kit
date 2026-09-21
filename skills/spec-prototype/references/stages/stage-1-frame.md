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

## Macro Double Diamond

### Discover — Pillars: Value, Research
- **Reference Benchmarks**: select high-persuasion industry anchors as the shared
  consensus fulcrum; refuse inventive fabrication.
- **Tension Triad & Inversions**: dig the product's deep-water contradictions and
  declare Core Tension plus non-goal boundaries in `prototype/product.md`.
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
- **Derived Surface Topology**: name Primary, Contextual, and Supporting surfaces;
  resist page-count inflation.
- **Gated Output**: `prototype/contracts/surface-maps/m1.md` after human consensus.

### Develop — Pillars: Attention, Expression / Five Axes
- **5-Dial Style Register**: under Expression, set Density, Energy, Materiality,
  Rhythm, and Character. Apply the Vague-Word Firewall (banned: "高级", "现代")
  and emit a concrete proposal with exact hex palette (`--accent-primary`,
  `--bg-void`), axis orientation, and trade-off notes.
- **LLM Dynamic Chromatics**: once the proposal is chosen, `compile_tokens.py`
  derives a 16-step physical elevation matrix by luminance delta and generates
  `prototype/shared/tokens.css` (plus `prototype/contracts/tokens/t1.json`).
- **Cognitive Budgeting**: separate the zero-borrow low-entropy base (routine
  navigation and content, 0 learning cost, 0 perturbing animation) from the high-
  yield borrow zone (core operation surface, purposeful micro-motion permitted).
- **Gated Output**: `prototype/contracts/foundation/f1.md` and `prototype/shared/tokens.css`.

### Deliver — Pillars: Interaction, Resilience
- **Action Verb Lifecycle**: close the semantic loop of Trigger → Context → Commit
  → Feedback; one atomic verb, no synonym drift.
- **The Break Protocol**: predefine long-string truncation, 0/1/1000 states, and
  viewport fold limits.
- **Automated Contract Materialization**: run `python3 skills/spec-prototype/scripts/materialize_contracts.py`
  to compile structured contracts into `prototype/contracts/slices/<slice_id>/c1.md`
  and `prototype/specifications/<slice_id>/r1.md`.

## Sealed Provisional Baseline Closure

Stage 1 ends only when all six sealed provisional baseline contracts are fully
materialized: `product.md`, `surface-maps/m1.md`, `foundation/f1.md`,
`tokens.css`, `slices/<slice_id>/c1.md`, and `specifications/<slice_id>/r1.md`
(authority status: sealed provisional). The baseline is then sealed and passes
directly to [Stage 2](stage-2-probe.md) probe falsification.

## Exit

Legal exit is the validated `spec-only` contract set. A formal candidate still
requires this sealed provisional Spec; only a bounded probe may proceed without
it via [Stage 0](stage-0-explore.md).

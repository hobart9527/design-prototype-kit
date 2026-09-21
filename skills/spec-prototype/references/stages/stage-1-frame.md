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

## Stage 1 Design Co-creation Dialectic (渐进式设计共创四重奏)

Stage 1 is a progressive, guided design conversation — NOT an opaque questionnaire or bulk document generator. The Agent acts as an experienced design partner, projecting the Five Axes and Nine Pillars into concrete, visual, and experiential choices across four rounds:

### Round 1: Physical Reality & Mental Metaphor (隐喻与物理心智 · Character)
- **Pillars**: Value, Research, Object, Interaction Resistance.
- **Axes**: Character, Rhythm.
- **Method**: Never ask the user for abstract dial numbers. Project 2~3 concrete physical metaphors derived from the domain:
  - *Archetype A (Precision Caliper / Interlock Gate)*: High resistance, strict validation before entry, zero ambiguous commit.
  - *Archetype B (Customs Inspection Desk / Clearance)*: Tiered resistance, green channel for standard ops, manual escalate-and-stamp for exceptions.
  - *Archetype C (Editorial Proofing Table)*: Low resistance, concurrent markups, focus on diff collation and consensus seal.
- **Output**: Confirm primary/secondary metaphors, core tension, and focal object.

### Round 2: Spatial Density & Information Fabric (空间拓扑与信息骨架 · Density)
- **Pillars**: Topology, Journey, Layout Scaffolding.
- **Axes**: Density, Rhythm.
- **Method**: Present layout and view hierarchy via lightweight ASCII wireframes or structural cards before touching color:
  - *Topology A (Dense Multi-column Workbench)*: High density, synchronized 3-pane inspection (source, matrix, gate).
  - *Topology B (Focused Workflow Drawer / Linear-style)*: Balanced density, shortcut-driven, drawer disclosure.
  - *Topology C (Card Overview & Deep Dive / Stripe-style)*: Relaxed density, explicit card boundaries, lowest cognitive friction.
- **Output**: Lock layout topology, centroid of attention, and primary/secondary action flow.

### Round 3: Materiality, Palette & Signature Moments (材质、色彩与签名印落 · Materiality, Energy)
- **Pillars**: Attention, Expression, Micro-timing.
- **Axes**: Materiality, Energy.
- **Method**: Present tangible material moodboards and decisive action feedback mechanics:
  - *Expression A (Obsidian & Cinnabar)*: Void dark slate base, hairline borders, zero floating shadow. Action is quiet until the decisive commit, which strikes with an authentic seal cinnabar (`--accent-seal`), 160ms zero-rebound imprint.
  - *Expression B (Warm Paper & Ink)*: Organic off-white parchment base, deep charcoal typography, gentle diffuse shadow, smooth element repositioning on commit.
- **Output**: Lock domain tokens (`--accent-seal` separation from functional `--action-primary`), kinetic timing, and signature relationship.

### Round 4: Boundary Invariants & Stress Contract (容错边界与证伪判据 · Resilience)
- **Pillars**: Resilience, Interaction Lifecycle.
- **Method**: Define fault tolerance, irreversible state gates, and the explicit 5-second falsification criteria for the Stage 2 probe.
- **Output**: Establish explicit write scopes, invariants, and execute automated single-direction compilation via `materialize_contracts.py`.

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
materialized: `prototype/product.md`, `prototype/contracts/surface-maps/m1.md`,
`prototype/contracts/foundation/f1.md`, `prototype/shared/tokens.css`,
`prototype/contracts/slices/<slice_id>/c1.md`, and
`prototype/specifications/<slice_id>/r1.md` (authority status: sealed provisional). The baseline is then sealed and passes
directly to [Stage 2](stage-2-probe.md) probe falsification.

## Exit

Legal exit is the validated `spec-only` contract set. A formal candidate still
requires this sealed provisional Spec; only a bounded probe may proceed without
it via [Stage 0](stage-0-explore.md).

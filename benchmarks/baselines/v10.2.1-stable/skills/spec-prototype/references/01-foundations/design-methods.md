# Design Methods & Craft Library (工法与参考库)

> Canonical Design Architecture: **Nine Pillars** (主模型 · WHAT) · **Double Diamond** (决策流 · HOW DECIDE) · **Five Axes** (表达坐标 · HOW FEELS) · **Craft Library** (工法库 · HOW CRAFT) · **Evidence Protocol** (横向治理)。

This reference serves as the **Craft Library** under the Nine Pillars ontology. Craft methods provide generative rigor and falsification techniques, but **techniques never masquerade as universal quality floors**. Experience invariants govern quality; techniques supply candidate implementations.

---

## 1. The Nine Pillars Canonical Ontology (九柱设计本体)

Every consequential product design must resolve the core questions across nine orthogonal pillars:

1. **Value**: Why build this? Who is it for? What is the defining operational tension and success signal?
2. **Research**: What is known vs unknown? What is empirical evidence vs working hypothesis?
3. **Object**: What entities, relationships, ownerships, and lifecycles truly exist in the domain? (OOUX)
4. **Journey**: How does an operator initiate, execute, recover, and conclude tasks across interruptions?
5. **Topology**: How are surfaces, workspaces, drawers, and contexts spatially organized and preserved?
6. **Attention**: Where does the eye travel first, second, and third? Progressive disclosure and noise budget.
7. **Expression**: What sensory language (Five Axes: density, energy, materiality, rhythm, character) is projected?
8. **Interaction**: How do inputs trigger direct manipulation, feedback detents, and state mutations?
9. **Resilience**: How does the surface behave under empty data, overflow, latency, disruption, and accessibility constraints?

---

## 2. Invariants vs. Techniques (体验不变式与具体手艺解耦)

A core failure of rule-heavy systems is elevating specific techniques to rigid quality floors. In v10, quality floors assert **invariants**, allowing the Builder creative agency across candidate techniques:

| Invariant (体验不变式 · 必须满足) | Candidate Techniques (候选手艺 · 按需选用) | Anti-Pattern to Avoid |
|---|---|---|
| **Perceptible Immediate Feedback**: Consequential actions must provide instant, visible, non-destructive feedback. | `:active { transform: scale(0.97); }`, background shift, inset shadow, border detent, tactile spring. | Mandating `scale(0.97)` everywhere or breaking layout during press. |
| **Contextual Data Grounding**: Key numbers must carry baseline, unit, or comparative context. | Inline units, thresholds, rated ceilings, status badges, delta arrows, compact sparklines. | Forcing SVG sparklines into focused reading or document canvases. |
| **Harmonious Geometry**: Container borders and nested elements must maintain optical concentricity. | $R_{\text{in}} = \max(0, R_{\text{out}} - P)$, matched corner radii, optical alignment. | Disjointed nested rounded corners causing visual distortion. |
| **Numeric Stability**: Tabular metrics, timers, and quantities must not jitter during updates. | `font-variant-numeric: tabular-nums`, monospace digits, dedicated figure columns. | Shifting layouts when digits fluctuate from 1 to 8. |
| **Structural Resilience (Break Protocol)**: Surfaces must gracefully withstand edge data without collapse. | `text-overflow: ellipsis`, flex-wrap containment, actionable empty CTA, 320px fold integrity. | Dead empty screens with zero recovery path or runaway horizontal overflow. |

---

## 3. High-Leverage Craft Methods (高杠杆工法库)

When shaping Stage 1 specs and Stage 2 probes, apply these methods under their owning Pillars:

### Method 1: Reality Anchors & Tension Triad (Pillar: Value)
- **Operational Reality vs Physical Substrate**: Ground every design in empirical operational standards (e.g. Linear/Datadog high-density telemetry, iA Writer focused canvas, Stripe checkout clarity).
- **Three Ruthless Omissions**: Explicitly state at least 3 things this surface will NOT do (e.g. zero promotional carousels, zero ungrounded scalar metrics, zero nested modal traps).
- **Divergence Gate & Axis Inversion**: Invert default assumptions across operational axes before converging on design proposals.

### Method 2: OOUX Cardinality-to-Layout Mapping (Pillars: Object & Topology)
Map domain relationships directly to spatial structure:
- `1 : 1` Singular Entity $\longrightarrow$ Focused Inspection Canvas / Dedicated Detail View.
- `1 : N` Master-Detail $\longrightarrow$ High-Density Faceted Matrix / Master-Detail Split Rack.
- `N : M` Relational Network $\longrightarrow$ Multi-Column Topology Board / Interactive Node-Link Canvas.

### Method 3: Action Verb Lifecycle (Pillars: Interaction & Journey)
Every state-mutating action must preserve exact atomic terminology across its entire lifecycle:
$$\text{Trigger Button} \longrightarrow \text{Modal / Drawer Confirmation} \longrightarrow \text{Commit Action Button} \longrightarrow \text{Completion Toast / Feedback}$$
*Rule*: Zero semantic drift or synonym mutation between trigger and completion.

### Method 4: Zero Naked Metrics & Micro Sparklines (Pillars: Expression & Attention)
Every critical metric must carry contextual baselines, unit tags, delta trends, or compact sparklines to prevent naked ungrounded readouts.

### Method 5: Decisive 3-Frame & Context Preservation (Pillars: Journey & Resilience)
- **Decisive 3-Frame Mapping**:
  $$\text{Frame 1: Intent Input} \longrightarrow \text{Frame 2: Commitment with Perceptible Feedback} \longrightarrow \text{Frame 3: State Settlement \& Return}$$
- **Context Preservation**: Dismissing a secondary modal or drawer must preserve existing form drafts, scroll offsets, and active table filters without data loss.

### Method 6: The Craft Physics Triad (Pillars: Expression & Interaction)
Calibrate concentric radii formulas, kinetic press detents, and tabular numerics to achieve tactile precision.

### Method 7: The Break Protocol (Pillar: Resilience)
Stress-test string overflow, zero-item empty state recovery CTA, and 320px fold integrity.

---

## 4. Open Physical Substrates & Composable Patterns (开放物理地质场与参考模式)

Product spaces must NEVER be trapped inside rigid 4-box classification silos. Instead, every product experience is an open synthesis of **Physical Lifeworld Substrates (物理现实对应物)** and **Domain Tension (业务张力)** across the Nine Pillars.

The historical "4 Baselines" are demoted to illustrative composable patterns, accompanied by open lifeworld archetypes:

- **Dense Workbench (仪表控制台)**: High information density, compact tabular readouts, multi-pane instrument layouts (Operations, SRE, Aviation, Trading).
- **Operational Canvas (协作画布)**: Fluid workspaces, dual-track review flows, contextual inspector drawers (Design tools, Collaboration, SaaS, PM).
- **Editorial Reading (文人纸韵)**: Distraction-free focus, ergonomic reading measures (55-75ch), proportional typographic hierarchy (Publishing, Documentation, AI Writing, Thought Pieces).
- **Touch-First Somatic (体感触控流)**: Bounded touch targets (min 44px), spring friction curves, tactile sheet drawers (Mobile, Consumer booking, Quick services).
- **Acoustic & Tactile Player (音频/留声硬件)**: Rotational scrub inertia, tactile knob damping, cassette deck mechanical latches (Audio streaming, Podcasting, Music production).
- **Sensory Card & Ledger (收据皮夹/卡片流)**: Natural card stacking, monetary stamp detents, micro-flip counters (Personal finance, Micro-accounting, Wealth management).
- **Habit Ring & Chrono (发条计时/印章成就)**: Closure detents, somatic ring completion vibrations, tactile calendar stamps (Habit tracking, Health, Kinetic routines).

*Composition Principle*: Real products combine lifeworld substrates orthogonally. A modern professional tool (e.g., Linear) inherits B2C consumer fluidity while preserving B2B operational rigor. An editorial tool combines classical paper contrast with modern popover detents.

---

## 5. Nine Pillars Reference Router (内部参考路由)

Use this table to navigate in-depth references under the Nine Pillars:

| Pillar | Focus Area | In-Depth Reference File |
|---|---|---|
| **Value** | Product thesis, core tension, non-goals | `01-foundations/product-understanding.md` |
| **Research** | Knowns/unknowns, evidence levels L0-L5 | `01-foundations/research.md` |
| **Object** | Entities, attributes, lifecycles, OOUX | `02-craft-methods/ia-interaction.md` |
| **Journey** | Task flows, entry/return, interruptions | `02-craft-methods/ia-interaction.md` |
| **Topology** | Surface maps, drawers, context preservation | `02-craft-methods/ia-interaction.md` |
| **Attention** | Reading order, disclosure levels, noise budget | `02-craft-methods/interaction-power.md` |
| **Expression** | Five axes, color, typography, materiality | `01-foundations/design-language.md`, `02-craft-methods/visual-craft.md` |
| **Interaction** | Action lifecycles, tactile feedback, shortcuts | `02-craft-methods/interaction-power.md` |
| **Resilience** | Fault tolerance, empty states, Break Protocol, a11y | `02-craft-methods/resilience-trust.md` |

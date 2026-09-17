# Design Methods — Seven High-Leverage Levers & Divergence Engine

Use this reference when an experience design choice is open, or when a validated design lacks tension, authority, or craft verisimilitude. Methods do not replace the Canonical 5-Stage state machine; they supply the disciplined generative and falsification mechanics that sharpen Stage 1 (破) and Stage 2 (立).

---

## 1. The Seven High-Leverage Design Levers (七大高杠杆设计技法)

When faced with infinite styling choices, prioritize these seven high-leverage levers. They yield maximal systemic rigor, cognitive clarity, and physical realism for minimal decision cost:

### Lever 1: Reality Anchors & Tension Triad (现实双地锚与三大舍弃)
- **Reality Benchmark Anchors**: Ground every design in two real-world reference systems:
  1. *Operational / Data Reality* (e.g. Datadog high-density telemetry, Bloomberg terminal density, Ableton Live clip workflow);
  2. *Physical / Kinetic Reality* (e.g. aviation fly-by-wire detent, machine tool caliper scale, analog optical substrate).
- **Core Tension Triad**: Identify the defining operational trade-off (e.g. Throughput vs Liability, Focal Immersion vs Context Awareness).
- **Three Ruthless Omissions**: Explicitly declare at least 3 things this surface will NOT do (e.g. no multi-step wizards, no naked scalar metrics, no decorative floating cards).

### Lever 2: OOUX Cardinality-to-Layout Mapping (实体基数到空间拓扑映射)
Structure layout strictly around authentic domain object cardinalities:
- `1 : 1` Singular Entity $\longrightarrow$ Focused Inspection Canvas / Dedicated Setting Workbench.
- `1 : N` Master-Detail $\longrightarrow$ High-Density Faceted Data Table / Master-Detail Split Screen.
- `N : M` Relational Network $\longrightarrow$ Multi-Column Topology Board / Relational Node-Link Canvas.
*Anti-Contamination Rule*: Never rename genuine domain entities to fit visual metaphors (e.g. never call database replicas "particles" or compute nodes "planets").

### Lever 3: Action Verb Lifecycle (动作动词全生命周期闭环)
Every primary and secondary operational action must maintain exact atomic terminology across its entire 4-phase lifecycle:
$$\text{Trigger Button} \longrightarrow \text{Modal / Drawer Title} \longrightarrow \text{Commit Action Button} \longrightarrow \text{Completion Feedback Toast}$$
*Example*: `Quarantine` (trigger) $\longrightarrow$ `Quarantine Worker` (dialog title) $\longrightarrow$ `Quarantine` (primary button) $\longrightarrow$ `Worker Node Quarantined` (toast). Zero semantic drifting or synonym substitution.

### Lever 4: Zero Naked Metrics & Micro Sparklines (拒斥裸指标与内联微时序)
Never show a floating scalar number without context. Every critical metric must provide:
1. **Threshold Baseline**: An explicit rated limit, capacity ceiling, or warning threshold;
2. **Inline Micro Sparkline**: A compact 40-60px SVG `<polyline>` or `<path>` showing the recent 15-minute trend;
3. **Temporal Frequency**: Explicit sampling window (e.g. "last 5s avg", "p99 15m").

### Lever 5: Decisive 3-Frame & Context Preservation (决定性交换三帧推演与上下文保持)
- **Decisive 3-Frame Inspection**: Map the consequential commitment moment:
  $$\text{Frame 1: Intent Input} \longrightarrow \text{Frame 2: Decisive Commit with Tactile Resistance} \longrightarrow \text{Frame 3: State Settlement & Focus Restoration}$$
- **Context Preservation Invariant**: When an operator branches into a drawer, popover, or secondary modal and subsequently dismisses or cancels it, their uncommitted form drafts, scroll offsets, and active table filters MUST be strictly preserved.

### Lever 6: The Craft Physics Triad (三大微观物理底线)
Every prototype surface must implement the three microscopic geometry rules:
1. **Concentric Radii**: $R_{\text{inner}} = \max(0, R_{\text{outer}} - \text{padding})$. Eliminates jarring geometric visual dissonance.
2. **Tabular Numerics**: `font-variant-numeric: tabular-nums` on all metrics, timestamps, counters, and telemetry readouts.
3. **Tactile Mechanical Detents**: `:active { transform: scale(0.97); }` with `cubic-bezier(0.16, 1, 0.3, 1)` transition curves.

### Lever 7: The Break Protocol (四维破坏性应力极限测试)
Stress-test runnable prototypes against four reality breakers before user presentation:
1. **Unbreakable String Overflow**: Long un-spaced hashes and IDs to verify truncation and tooltip behavior.
2. **Zero-Item Empty State**: Verify that an empty dataset renders an actionable recovery mechanism rather than a dead canvas.
3. **Extreme 320px Fold**: Ensure primary actions and orientation survive extreme mobile viewport folds.
4. **Rapid Interruption**: Rapid repeated clicks to verify idempotency and debouncing.

---

## 2. The Divergence Gate (分歧四反转法)

Do not allow "settled by convention" to become an excuse for unexamined clichés. When exploring Stage 1 directions, pass through the **Divergence Gate**:

1. **Axis Inversion**: Reorganize the primary information/interaction axis (e.g. from a sequential step flow to a spatial workbench, or from a passive status monitor to a direct-manipulation steering wheel).
2. **Constraint Inversion**: Invert a key assumption (e.g. assume extreme screen density, zero-latency feedback, or keyboard-only emergency operation) and test if the core relationship survives.
3. **Antithetical Metaphor**: Counter the default generic dashboard with a contrasting domain metaphor (e.g. artisan's cutting mat, astronomical spectrograph, submarine acoustic console).
4. **Signature Craft Focus**: Select the single interaction moment that defines the character of the product, and articulate how its typography, spatial hierarchy, and motion create genuine brand and emotional resonance.

---

## 3. Eight-Lens Method Router (八维工法导航)

Scan the eight lenses to identify applicable craft references:

| Lens | Questions that trigger deeper work | Reference Pillar |
|---|---|---|
| **Value & Outcomes** | Purpose, audience, consequential tension is ambiguous | `01-foundations/product-understanding.md` |
| **Research & Context** | Real user mental model or operating environment unclear | `01-foundations/research.md` |
| **Objects & Content** | Object boundaries, attributes, and relationships unclear | `02-craft-methods/ia-interaction.md` |
| **Journeys & States** | Task transitions, interruptions, or recovery ambiguous | `02-craft-methods/ia-interaction.md` |
| **Surface Topology** | Page necessity, wayfinding tiers, responsive collapse | `02-craft-methods/ia-interaction.md` |
| **Interaction & Power** | Keyboard shortcuts, decisive exchange, micro-motion | `02-craft-methods/interaction-power.md` |
| **Data & Information** | High-density tables, sparklines, comparison matrices | `02-craft-methods/data-information.md` |
| **Resilience & Trust** | Destructive actions, confirmation ladders, AI agency | `02-craft-methods/resilience-trust.md` |

---

## 4. Method Lineage and Clean Routing

- **OOUX / ORCA**: Use for object-centered modeling (Objects, Relationships, Calls-to-action, Attributes) before container selection.
- **Nielsen / Norman**: Apply as observable heuristic acceptance criteria (visibility of system status, match between system and real world, error prevention, recognition over recall).
- **Elements of UX**: Strategy $\longrightarrow$ Scope $\longrightarrow$ Structure $\longrightarrow$ Skeleton $\longrightarrow$ Surface dependency hierarchy.
- **W3C DTCG**: Single source of truth for design token export and handoff.

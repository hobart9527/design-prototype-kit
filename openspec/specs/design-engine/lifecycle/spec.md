# design-engine/lifecycle Specification

## Purpose
Defines the formal specifications and behavioral constraints of the Canonical 5-Stage Design Engine across product reframing, structural topology, dynamic exploratory prototyping, formal contract freezing, and empirical verification.
## Requirements
### Requirement: ENG-001 Canonical Five-Stage Lifecycle
The design engine SHALL govern the progression of experience design through five explicit, sequenced stages: Phase 1 (魂: Sense-making & Tension), Phase 2 (骨: Object Cardinality & Surface Topology), Phase 3 (皮: Exploration Prototyping & Kinetic Probes), Phase 4 (根: Verification, Formal Freezing & Handoff), and Phase 5 (鉴: Independent Review & Assertion Closure).

#### Scenario: ENG-SCN-001 Five-stage sequential progression
- **WHEN** a design project is executed under the design engine
- **THEN** artifacts transition through 魂 (`product.md`), 骨 (`surface-map.md`), 皮 (`experiments/`), 根 (`contracts/` and `specifications/`), and 鉴 (`evidence/`) with verifiable evidence at each gate

### Requirement: ENG-002 Kinetic and Physical World Micro-interactions
The design engine SHALL enforce physical-world easing dynamics (`cubic-bezier(0.16, 1, 0.3, 1)`), tactile active feedback (`transform: scale(0.97)`), and mobile touch targets (`min-h-[44px] min-w-[44px]`) on delivered interactive prototypes.

#### Scenario: ENG-SCN-002 Natural easing and touch ergonomics adherence
- **WHEN** an interactive prototype component is inspected for touch ergonomics and animation
- **THEN** all mobile interactive elements satisfy minimum 44x44px touch targets and fluid acceleration curves without rigid mechanical jumps

### Requirement: ENG-003 Five Essential Experience States
The design engine SHALL require interactive components and slices to model and render five core operational states: Loading (skeleton states), Empty (contextual call to action), Partial (graceful degradation or degraded connectivity), Error (localized recovery and retry), and Overflow (extreme string lengths and wrapping).

#### Scenario: ENG-SCN-003 Complete experience state coverage
- **WHEN** a prototype journey or slice is evaluated across operational states
- **THEN** all five states (Loading, Empty, Partial, Error, Overflow) are deterministically triggerable and visually verified in the evidence record


# design-engine/craft-and-resilience Specification

## Purpose
Enhance the design engine with fault-tolerant contract parsing, in-memory state preservation, somatic and optical craft invariants, and honest interactive verification.
## Requirements
### Requirement: CRR-001 Fault-tolerant contract parsing and advisory digest matching
The engine SHALL parse authored design contracts and prototype context blocks with format tolerance (admitting standard YAML/markdown variants, whitespace variations, and trailing comments). When comparing retained selection records against authored surface maps, matching logical revision identifiers SHALL permit dispatch, while SHA-256 digest discrepancies SHALL be reported as non-blocking diagnostics unless the logical revision also differs.

#### Scenario: CRR-SCN-001 Formatted context parsing resilience
- **WHEN** an authored contract contains standard markdown formatting variations or whitespace around keys
- **THEN** the context reader normalizes and extracts required keys without throwing syntax or parse errors

#### Scenario: CRR-SCN-002 Revision match admits dispatch with advisory digest notice
- **WHEN** the authored map revision matches the expected revision but the SHA-256 digest differs slightly due to non-semantic whitespace or minor comment edits
- **THEN** dispatch proceeds with an advisory diagnostic rather than failing with a hard gate refusal

### Requirement: CRR-002 In-memory state store and context preservation
The prototype builder SHALL implement an explicit, zero-dependency in-memory state store (`window.__prototypeState`) within generated interactive prototypes. Consequential interactive actions, form inputs, filter selections, and drawer toggles SHALL update this store. Secondary dismissals (such as closing a drawer or sub-modal) SHALL preserve existing form drafts and table filters without state loss.

#### Scenario: CRR-SCN-003 Context preservation across frame dismissals
- **WHEN** an operator inputs text into a drawer form or toggles table filters and subsequently dismisses the secondary view
- **THEN** reopening the view or returning to the table preserves the active filter and uncommitted draft state

### Requirement: CRR-003 Somatic touch ergonomics and optical geometry
Builder instructions SHALL mandate mobile-specific CSS environment insets (`env(safe-area-inset-*)`), minimum 44×44px interactive hit targets, and `:active` kinetic spring detents when targeting mobile contexts. Nested containers SHALL adhere to the concentric radius formula $R_{\text{in}} = \max(0, R_{\text{out}} - P)$, and numeric metrics SHALL enforce `font-variant-numeric: tabular-nums`.

#### Scenario: CRR-SCN-004 Mobile somatic constraints in builder output
- **WHEN** `platform.target_context` indicates a mobile environment
- **THEN** the generated prototype includes safe area insets, touch target constraints of at least 44px, and kinetic press feedback

### Requirement: CRR-004 Dual-view review portal with stress testing
The review portal generator SHALL produce an interactive dual-view inspection interface featuring responsive device frame emulation (Desktop 1440px / Tablet 768px / Mobile 390px) and a Break Protocol toggle for injecting overflow data and testing zero-state recovery.

#### Scenario: CRR-SCN-005 Interactive viewport and stress testing in portal
- **WHEN** the review portal is viewed in a browser
- **THEN** reviewers can switch viewport modes and trigger edge-case data stress toggles to verify responsive layout and break protocols


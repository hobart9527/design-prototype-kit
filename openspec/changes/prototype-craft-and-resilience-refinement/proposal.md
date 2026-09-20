## Why

The `coverage-platform-continuity` capability successfully established boundary gating and platform context separation. However, two operational frictions and one craft gap remain:
1. Stage 1 contracts suffer from over-rigid gating: parsing of `prototype-context` blocks rejects minor format tolerances and strictly enforces SHA-256 digests even when logical revisions match, creating excessive prompt-tuning friction during early design exploration.
2. The Nine Pillars Craft Library (`references/01-foundations/design-methods.md`) remains largely at the metadata and verification layer; generated prototypes lack a unified interactive state store (Method 5 Decisive 3-Frame & Context Preservation), resulting in brittle state loss across drawer, form, and modal actions.
3. Builder and Critic roles lack explicit executable instructions for mobile/somatic ergonomics (safe-area insets, 44px touch targets, `:active` spring detents) and optical geometry (concentric radii formulas and tabular numerics).

## What Changes

- Relax contract linting in `prototype_context.py` and `lint_spec_contracts.py` to allow fault-tolerant markdown parsing and prioritize logical revision matches over rigid SHA-256 digest locks.
- Materialize Craft Library invariants directly into Builder instructions (`agents/spec-prototype-builder.md`), mandating a vanilla JS in-memory state store for interactive context preservation, somatic mobile ergonomics, and optical concentric geometry.
- Enhance the verification harness (`verify_prototype_quality.py`) and review portal generator (`generate_review_portal.py`) to report unverified environments truthfully and provide interactive viewport switching (Desktop vs Mobile 390px) and edge-case data toggles.
- Add focused unit and mechanism tests verifying the fault-tolerant parser, state store preservation assertions, and platform craft instructions.

## Capabilities

### New Capabilities

- `design-engine/craft-and-resilience`: Fault-tolerant contract parsing, in-memory state preservation, somatic/optical craft constraints, and truthful interactive verification.

### Modified Capabilities

None.

## Impact

- `skills/spec-prototype/scripts/prototype_context.py`, `lint_spec_contracts.py`, `verify_prototype_quality.py`, `generate_review_portal.py`.
- `agents/spec-prototype-builder.md`, `agents/spec-prototype-critic.md`.
- Associated pytest suites under `tests/`.
- Zero external runtime dependencies added; vanilla JS and standard CSS only.

## Scope of this delivery

Behavioural requirements, specifications, design decisions, and executable implementation tasks. All code changes will be delivered through isolated leaf tasks under Loom governance.

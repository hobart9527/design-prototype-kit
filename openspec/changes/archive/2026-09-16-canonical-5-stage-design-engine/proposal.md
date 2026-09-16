## Why

Experience design and rapid prototyping in AI-augmented workflows often suffer from either superficial toy mockups or over-engineered boilerplate without clear architectural grounding. The Canonical 5-Stage Design Engine provides an industrial-grade methodology and runtime pipeline—spanning 魂 (Reframing & Tension), 骨 (Topology & Omissions), 皮 (Kinetics & Sensory Probes), 根 (Formal Contracts & Freezing), and 鉴 (Empirical Verification & Critique)—to ensure every prototype is grounded in real user needs, physical-world ergonomics, and rigorous falsifiable assertions.

## What Changes

- Formalize the 5-stage design engine lifecycle across documentation, templates, and agent contracts.
- Establish runtime verification and handoff tooling (`scripts/export-tokens.py`, `scripts/check-assertions.py`, `scripts/handoff.py`, `scripts/execution_boundary.py`) to enforce contract compliance and token extraction.
- Implement executable test suites (`tests/test_tokens.py`, `tests/test_pipeline.py`) that validate token exports, assertion matching, and handoff boundary immutability.

## Capabilities

### New Capabilities
- `design-engine/lifecycle`: Canonical 5-stage design engine lifecycle governing product reframing (魂), surface topology (骨), dynamic probes (皮), contract freezing (根), and empirical critique (鉴).
- `design-engine/verification-harness`: Automated verification scripts and test pipeline enforcing token schema validity, falsifiable assertion checks, and isolated handoff packets.

### Modified Capabilities

## Impact

- Standardizes artifact layouts in `prototype/` (`product.md`, `surface-map.md`, `discussion.md`, `contracts/`, `experiments/`, `evidence/`).
- Governs `spec-prototype-builder` and `spec-prototype-critic` execution contracts.
- Fixes test pipeline execution across `tests/test_tokens.py` and `tests/test_pipeline.py`.

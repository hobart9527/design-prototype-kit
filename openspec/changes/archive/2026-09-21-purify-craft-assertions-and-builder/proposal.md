# Proposal: Purify Contract Assertions, Platform Envelope Context, and Builder Guidance

## Why

Three semantic and architectural seams in the prototype engine require purification:

1. **Heuristic Category Assertion Inversion**: `materialize_contracts.py` retains regex-based category matching (`is_reading`, `is_marketing`, `is_mobile`, `is_writer_canvas`, `is_telemetry_ops`) that synthesizes artificial craft assertions (`Zero Naked Metrics`, `Concentric Radii`, `Touch Target Floor`) into L1 specifications. The compiler must stay thin and truthful, leaving craft decisions to authored specs and Builder reasoning.
2. **Platform Context Seam Gap**: `prototype_context.py` projects `target_context` into `platform` but drops `device_context` and `input_context`. Consequently, `spec-prototype-builder.md` attempts to evaluate touch support by inspecting `platform.target_context` (which is strictly an OS identifier like `ios` or `web`), creating a modality seam defect.
3. **Builder Universal Mandate Overreach**: `agents/spec-prototype-builder.md` declares universal MUSTs for `Zero Naked Metrics`, `Concentric Radii Formula`, and `window.__prototypeState` that assume all prototypes possess metric streams, nested cards, and complex table filters/form drafts. These must be scoped to applicable interactive and telemetry features rather than enforced globally across reading, editorial, or static surfaces.

## What Changes

- `skills/spec-prototype/scripts/materialize_contracts.py`: Remove heuristic category matching and synthesized craft assertions; replace with clean, universal baseline invariants.
- `skills/spec-prototype/scripts/prototype_context.py`: Include `device_context` and `input_context` in `platform` context output so downstream envelopes carry complete modality facts.
- `agents/spec-prototype-builder.md`: Correct somatic touch check to inspect `device_context` and `input_context`; scope concentric radii, metrics floor, and state store guidance to applicable components while preserving `test_builder_state_store_contract.py` requirements.
- Tests: Add regression coverage in `tests/test_platform_truth.py` and align `tests/test_pipeline.py`.

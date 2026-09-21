# Proposal: Lean Builder Payload, Demand-Driven State Store, and Adaptive Viewports

## Why

The current Spec Prototype synthesis pipeline suffers from three execution redundancies:
1. **Builder Payload Bloat**: Even though the 7-field Canonical IR is compiled, `assemble_envelope.py` continues to pack raw intermediate artefacts (`creative_envelope`, `constraint_envelope`, `available_tokens`, `ooux_topology`, `app_shell_*`, `cognitive_ledger`) into the prompt payload passed to `spec-prototype-builder`, causing severe prompt bloat and competing instruction signals.
2. **Universal State Store Overreach**: `agents/spec-prototype-builder.md` dogmatically mandates that every prototype maintain a centralized `window.__prototypeState` containing tabs, filters, sub-modals, drawers, and form drafts, even for static editorial reading, marketing, or simple single-toggle pages that possess no such entities.
3. **Hardcoded Viewport Inspection**: `assemble_envelope.py` hardcodes `mandatory_viewports` to [1280, 390] regardless of the authored `platform.target_context` or `platform.device_context`, forcing desktop-only consoles or mobile-only touchflows to adhere to mismatched viewport gates.

## What Changes

1. **P0: Lean Builder Payload**:
   - Introduce `build_builder_payload(envelope, include_debug=False)` in `skills/spec-prototype/scripts/assemble_envelope.py`.
   - Normal Builder payload retains the 7 Canonical IR fields (`identity`, `semantic_contract`, `layout_directives`, `visual_directives`, `action_contracts`, `verification_contract`, `open_design_space`) alongside essential execution context (`platform`, `coverage`, `target_html_path`, `evidence_output_dir`, `verification_command`, `capture_command`, `inspection_contract`, `spec_sources`, `spec_references`, `token_link_tag`).
   - Demote legacy intermediate blobs (`constraint_envelope`, `creative_envelope`, `available_tokens`, `app_shell_*`, etc.) into `debug_context` (or `legacy_compat`) so they are omitted from the default Builder agent prompt.
   - When `assemble_envelope.py` writes to `--output`, output the lean payload by default.

2. **P1: Demand-Driven State Store**:
   - Refactor `agents/spec-prototype-builder.md` so that `window.__prototypeState` is required when persistent interactive state (active tab, table filter, drawer, sub-modal, or form draft) exists in the authored slice, while avoiding dogmatic schema invention for reading, marketing, or purely visual surfaces.
   - Maintain compatibility with `tests/test_builder_state_store_contract.py`.

3. **P1: Adaptive Inspection Viewports**:
   - In `skills/spec-prototype/scripts/assemble_envelope.py`, derive `mandatory_viewports` adaptively from `platform["target_context"]` and `platform["device_context"]` (e.g., desktop-only -> [1280], mobile/touch -> [390], tablet -> [768], responsive web / editorial reading -> [1280, 390] or [1280, 768]) rather than blindly fixing [1280, 390].

## 1. Purify Spec Contracts, Platform Envelope, and Builder Guidance

- [x] T-01 Remove category-to-craft assertions heuristic in materialize_contracts
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/materialize_contracts.py:materialize, tests/test_pipeline.py:test_materialize_contracts_high_fidelity_semantic_synthesis
  - Write scope: skills/spec-prototype/scripts/materialize_contracts.py, tests/test_pipeline.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_pipeline.py -k test_materialize_contracts_high_fidelity_semantic_synthesis
  - Action: In `materialize_contracts.py`, remove category heuristics (`is_reading`, `is_marketing`, `is_mobile`, `is_writer_canvas`, `is_telemetry_ops`) and their corresponding specialized `contract_assertions` branches. Unify the assertion table to truthful universal invariants (declared product intent, WCAG 2.2 AA contrast, navigation affordances, and break protocol resilience). In `tests/test_pipeline.py`, update assertions in `test_materialize_contracts_high_fidelity_semantic_synthesis` that expected synthesized SRE metrics/radii assertions to assert truthful contract invariants.

- [x] T-02 Project device/input context into platform envelope and fix builder touch check
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/prototype_context.py:read_context, agents/spec-prototype-builder.md, tests/test_platform_truth.py
  - Write scope: skills/spec-prototype/scripts/prototype_context.py, agents/spec-prototype-builder.md, .claude/agents/spec-prototype-builder.md, tests/test_platform_truth.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_platform_truth.py
  - Action: In `skills/spec-prototype/scripts/prototype_context.py:read_context`, include `device_context` and `input_context` under the returned `platform` dictionary. In `agents/spec-prototype-builder.md` (and symlink `.claude/agents/spec-prototype-builder.md`), correct Somatic Touch Context to inspect `platform.device_context` and `platform.input_context` instead of relying solely on `platform.target_context`. In `tests/test_platform_truth.py`, add test verifying `envelope["platform"]` exposes `device_context` and `input_context`.

- [x] T-03 Remove universal craft MUSTs and contextualize state store in builder guidance
  - Depends on: none
  - Anchors: agents/spec-prototype-builder.md, tests/test_builder_state_store_contract.py
  - Write scope: agents/spec-prototype-builder.md, .claude/agents/spec-prototype-builder.md, tests/test_builder_state_store_contract.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_builder_state_store_contract.py
  - Action: In `agents/spec-prototype-builder.md` (and symlink `.claude/agents/spec-prototype-builder.md`), scope `Concentric Nested Radius Geometry` and `Zero Naked Metrics Craft Floor` so they apply when nested containers or metric/telemetry displays are authored, rather than being universal mandates across all prototypes. Reframe `Centralized In-Memory State Store` so that it applies to interactive surfaces containing tabs, table filters, drawers, sub-modals, or form drafts using `window.__prototypeState`, without dogmatically assuming every prototype has these components. Maintain compliance with `test_builder_state_store_contract.py`.

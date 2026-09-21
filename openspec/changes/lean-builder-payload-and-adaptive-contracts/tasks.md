# Tasks: Lean Builder Payload, Demand-Driven State Store, and Adaptive Viewports

- [ ] T-01 Implement lean builder payload and adaptive inspection viewports in envelope assembly
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py:assemble, skills/spec-prototype/scripts/assemble_envelope.py:build_builder_payload, tests/test_platform_envelope.py
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_lean_builder_payload.py
  - Verify with: python3 -m pytest tests/test_platform_envelope.py tests/test_lean_builder_payload.py

- [ ] T-02 Scope in-memory state store in builder instructions to interactive surfaces
  - Depends on: none
  - Anchors: agents/spec-prototype-builder.md, tests/test_builder_state_store_contract.py
  - Write scope: agents/spec-prototype-builder.md
  - Verify with: python3 -m pytest tests/test_builder_state_store_contract.py

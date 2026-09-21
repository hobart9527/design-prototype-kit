# Tasks: Repair Builder Payload Seams and Viewport Execution

- [ ] T-01 Reconnect authored contracts and slim methods into lean payload
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_lean_builder_payload.py
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_lean_builder_payload.py
  - Verify with: python3 -m pytest tests/test_lean_builder_payload.py tests/test_platform_envelope.py

- [ ] T-02 Reconcile Builder agent instructions and wire dynamic viewports to capture execution
  - Depends on: T-01
  - Anchors: agents/spec-prototype-builder.md, skills/spec-prototype/scripts/capture.mjs, skills/spec-prototype/scripts/assemble_envelope.py
  - Write scope: agents/spec-prototype-builder.md, skills/spec-prototype/scripts/capture.mjs, skills/spec-prototype/scripts/assemble_envelope.py
  - Verify with: python3 -m pytest tests/test_lean_builder_payload.py
# Tasks: Executable IR Semantic Correctness

- [ ] T-01 Refactor assemble_envelope.py to enforce semantic correctness across IR fields
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py:assemble, tests/test_platform_envelope.py
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py
  - Verify with: python3 -m pytest tests/test_platform_envelope.py tests/test_pipeline.py

- [ ] T-02 Align agent instruction prompts and regression test suites with semantic IR
  - Depends on: T-01
  - Anchors: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, tests/test_platform_envelope.py
  - Write scope: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, tests/test_platform_envelope.py, tests/test_pipeline.py
  - Verify with: python3 -m pytest tests/test_platform_envelope.py tests/test_pipeline.py

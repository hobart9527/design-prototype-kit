## 1. Repair Gate Assertions and Align Contract Execution

- [ ] T-01 Align quality assertions, execution boundary whitelist, and builder agent guidance
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/verify_prototype_quality.py:assert_quality, skills/spec-prototype/scripts/execution_boundary.py:shell_read, agents/spec-prototype-builder.md
  - Write scope: skills/spec-prototype/scripts/verify_prototype_quality.py, skills/spec-prototype/scripts/execution_boundary.py, agents/spec-prototype-builder.md, tests/test_pipeline.py
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_pipeline.py
  - Action: Update `verify_prototype_quality.py` topology assertions so that undelivered sibling surfaces do not require live `href` links (which triggers 404 and coverage failures), but are verified as present via disabled affordances or text representation. Update `execution_boundary.py` to add `wcag-check.js` to `permitted['node']` and `check-assertions.py` to `permitted['python3']` and `permitted['python3.14']`. Update `agents/spec-prototype-builder.md` to document the disabled sibling navigation contract and the Zero Naked Metrics craft floor. In `tests/test_pipeline.py`, add tests proving that undelivered sibling surfaces rendered as disabled affordances pass quality assertions without 404 or coverage errors, and that the execution boundary admits both `wcag-check.js` and `check-assertions.py`.
  - Proof: Run `python3 -m pytest -q -p no:cacheprovider tests/test_pipeline.py` and verify all tests pass.

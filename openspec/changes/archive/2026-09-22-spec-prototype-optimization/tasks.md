# Tasks

## 1. Verify and publish the current spec-prototype optimization revision

- [x] T-01 Verify and publish the current spec-prototype optimization revision
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py:_canonical_contract_lint, skills/spec-prototype/scripts/compile_spec_ir.py:compile_canonical_ir, skills/spec-prototype/scripts/lint_spec_contracts.py:lint_canonical_spec_ir, skills/spec-prototype/scripts/execution_boundary.py:check
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, skills/spec-prototype/scripts/compile_spec_ir.py, skills/spec-prototype/scripts/lint_spec_contracts.py, skills/spec-prototype/scripts/execution_boundary.py, prototype/contracts/compiled/sample-gate/state_model.slice.json, tests/test_canonical_spec_ir.py
  - Verify with: pytest -q -m unit
  - Verify tier: unit
  - Action: Confirm canonical IR compilation consumes an explicit Stage 3/4 fragment, canonical lint passes, envelope assembly passes, and the full unit suite passes.
  - Positive specimen: `python3 skills/spec-prototype/scripts/compile_spec_ir.py --root . --slice sample-gate` exits 0 and writes `prototype/contracts/compiled/sample-gate/r1.spec.json`.
  - Boundary specimen: `python3 skills/spec-prototype/scripts/lint_spec_contracts.py --root . --slice sample-gate` exits 0; malformed or incomplete canonical IR must return a nonzero schema/boundary finding.

<!--
The current working-tree changes are retained as the implementation basis. No
additional product behavior is introduced by this delivery task.
-->

<!-- OLD
- [ ] 1. Verify and publish the current spec-prototype optimization revision
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py:_canonical_contract_lint, skills/spec-prototype/scripts/compile_spec_ir.py:compile_canonical_ir, skills/spec-prototype/scripts/lint_spec_contracts.py:lint_canonical_spec_ir, skills/spec-prototype/scripts/execution_boundary.py:check
  - Confirm canonical IR compilation consumes an explicit Stage 3/4 fragment, canonical lint passes, envelope assembly passes, and the full unit suite passes.
  - Preserve the current working-tree modifications; do not regenerate unrelated artifacts or delete unrelated files.
  - Verify with: `pytest -q -n auto -m unit`
  - Verify tier: unit
  - Positive specimen: `python3 skills/spec-prototype/scripts/compile_spec_ir.py --root . --slice sample-gate` exits 0 and writes `prototype/contracts/compiled/sample-gate/r1.spec.json`.
  - Boundary specimen: `python3 skills/spec-prototype/scripts/lint_spec_contracts.py --root . --slice sample-gate` exits 0; malformed or incomplete canonical IR must return a nonzero schema/boundary finding.
-->
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py:_canonical_contract_lint, skills/spec-prototype/scripts/compile_spec_ir.py:compile_canonical_ir, skills/spec-prototype/scripts/lint_spec_contracts.py:lint_canonical_spec_ir, skills/spec-prototype/scripts/execution_boundary.py:check
  - Confirm canonical IR compilation consumes an explicit Stage 3/4 fragment, canonical lint passes, envelope assembly passes, and the full unit suite passes.
  - Preserve the current working-tree modifications; do not regenerate unrelated artifacts or delete unrelated files.
  - Verify with: `pytest -q -n auto -m unit`
  - Verify tier: unit
  - Positive specimen: `python3 skills/spec-prototype/scripts/compile_spec_ir.py --root . --slice sample-gate` exits 0 and writes `prototype/contracts/compiled/sample-gate/r1.spec.json`.
  - Boundary specimen: `python3 skills/spec-prototype/scripts/lint_spec_contracts.py --root . --slice sample-gate` exits 0; malformed or incomplete canonical IR must return a nonzero schema/boundary finding.

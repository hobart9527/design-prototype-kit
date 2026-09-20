## 1. Standards Hygiene and Compiler Purity

- [x] T-01 Standards and hygiene in token compiler and gate boundaries
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/compile_tokens.py, skills/spec-prototype/scripts/materialize_contracts.py
  - Write scope: skills/spec-prototype/scripts/compile_tokens.py, skills/spec-prototype/scripts/materialize_contracts.py
  - Implements: CPC-004
  - Proves: CPC-SCN-007, CPC-SCN-008
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_tokens.py
  - Action: In `compile_tokens.py`, eliminate duplicate/dead imports (`math`, duplicate `Any, Dict, Tuple`). Rename `DARK_ATMOSPHERES` to `ATMOSPHERES` and retain `DARK_ATMOSPHERES = ATMOSPHERES` as a compatibility alias. In `materialize_contracts.py` and `compile_tokens.py`, preserve failure context at gate boundaries by replacing silent `except Exception: pass` with proper diagnostic warnings or contextual exception handling.
  - Proof: `tests/test_tokens.py` passes and import lint confirms clean namespaces without dead imports or swallowed exceptions.

- [x] T-02 Neutral motion and dial purity in token compiler
  - Depends on: T-01
  - Anchors: skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Write scope: skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Implements: CPC-004
  - Proves: CPC-SCN-023
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_tokens.py
  - Action: In `compile_tokens.py`, eliminate `"kinetic"` as the implicit default energy dial in formal mode. When energy is undeclared in formal mode, default to neutral `"steady"` motion (balanced durations and standard easing instead of aggressive HUD snappy detents). Gate `.btn-tactile:active` on explicit active/tactile requirements.
  - Proof: Unit tests in `tests/test_tokens.py` verify that formal mode with empty dials produces steady/balanced motion tokens rather than kinetic HUD curves.

## 2. Envelope De-locking and Verifier Integrity

- [x] T-03 De-lock envelope layout profile and candidate pattern precedence
  - Depends on: T-02
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_platform_envelope.py
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_platform_envelope.py
  - Implements: CPC-004
  - Proves: CPC-SCN-024
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_platform_envelope.py
  - Action: In `assemble_envelope.py`, ensure that when `selected_pattern` is None, `layout_profile` defaults to neutral `"adaptive-workspace"` instead of promoting `candidate_patterns[0]` into a hard topology lock. Downstream blueprints, attention routing, and interaction specs use the neutral baseline when unselected, keeping candidate patterns purely advisory for the Builder. Update `tests/test_platform_envelope.py` to assert that unselected patterns keep `layout_profile` neutral.
  - Proof: `tests/test_platform_envelope.py` confirms that unselected candidates do not re-lock the envelope to `candidate_patterns[0]`.

- [x] T-04 Solidify Builder integrity verification in canonical ontology
  - Depends on: T-03
  - Anchors: tests/test_canonical_ontology.py
  - Write scope: tests/test_canonical_ontology.py
  - Implements: CPC-003
  - Proves: CPC-SCN-005, CPC-SCN-006, CPC-SCN-022
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_canonical_ontology.py
  - Action: In `tests/test_canonical_ontology.py`, author assertions verifying that `agents/spec-prototype-builder.md` defines and enforces the 5 Core Integrity Categories (Semantic, Task, Accessibility, State & Recovery, Platform) and excludes prescriptive heuristics, preventing vacuous verification passes.
  - Proof: `python3 -m pytest -q -p no:cacheprovider tests/test_canonical_ontology.py` passes with all ontology checks and Builder integrity assertions green.

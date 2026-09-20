# Proposal: Semantic Freedom Hardening & Code Review Remediation

## Why

Following the initial delivery of the `semantic-freedom-refactor`, a comprehensive code review revealed hygiene defects, partial declassification remnants, and verification coverage gaps:
1. `compile_tokens.py` contained dead and duplicate imports, a misnamed `DARK_ATMOSPHERES` constant, and defaulted `energy` to `"kinetic"` even in formal mode.
2. Silent `except Exception: pass` blocks in `materialize_contracts.py` and `compile_tokens.py` swallowed failures and dropped failure context.
3. `assemble_envelope.py` promoted `candidate_patterns[0]` into `layout_profile`, re-locking downstream blueprints and attention routing when no pattern was explicitly selected.
4. `tests/test_canonical_ontology.py` had no assertions on `agents/spec-prototype-builder.md`, leaving T-04's receipt verification vacuous.

## What Changes

- **T-01 Standards and Hygiene**: Clean dead imports in `compile_tokens.py`, rename `DARK_ATMOSPHERES` to `ATMOSPHERES` with a backwards-compatible alias, and preserve error context at gate boundaries in `materialize_contracts.py` and `compile_tokens.py`.
- **T-02 Neutral Motion and Dial Purity**: Ensure `compile_tokens.py` formal mode defaults empty energy dials to a neutral/steady profile rather than snappy kinetic HUD easing, and condition tactile button styles on active requirements.
- **T-03 De-lock Envelope Layout Profile**: Ensure `assemble_envelope.py` keeps candidate patterns advisory without promoting `candidate_patterns[0]` into a rigid topology lock.
- **T-04 Builder Integrity Verification**: Add assertions to `tests/test_canonical_ontology.py` verifying the 5 core integrity categories in `agents/spec-prototype-builder.md`.

## Capabilities

### Modified Capabilities
- `design-engine/coverage-platform-continuity`: harden platform context neutrality, token compiler purity, and non-prescriptive envelope candidate patterns.

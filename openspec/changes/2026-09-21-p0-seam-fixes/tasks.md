## 1. P0 Seam Fixes & Pipeline Purification

- [ ] T-01 Purify f1 and r1 from unauthored universal invariants
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/materialize_contracts.py:materialize, skills/spec-prototype/scripts/assemble_envelope.py:assemble, tests/test_platform_envelope.py
  - Write scope: skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/assemble_envelope.py, tests/test_platform_envelope.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_platform_envelope.py
  - Action: In `skills/spec-prototype/scripts/materialize_contracts.py`, remove hardcoded `invariants: concentric-radii, tabular-numerics, touch-target-floor, break-protocol` from the `f1.md` context record, and remove hardcoded `preserves: concentric-radii, tabular-numerics, touch-target-floor, break-protocol` from the `r1.md` context record. Invariants in f1/r1 context records must only be included if explicitly authored in discussion or product text; unauthored invariants must not be fabricated (defaulting to `break-protocol` or empty list). In `assemble_envelope.py`, remove heuristic scraping of `concentric-radii` or `tabular-nums` lines when not authored. In `tests/test_platform_envelope.py`, add assertions verifying f1 and r1 do not emit unauthored universal invariants.

- [ ] T-02 Remove domain and input assumptions in materializer ergonomics
  - Depends on: T-01
  - Anchors: skills/spec-prototype/scripts/materialize_contracts.py:materialize, tests/test_contract_seam_fidelity.py
  - Write scope: skills/spec-prototype/scripts/materialize_contracts.py, tests/test_contract_seam_fidelity.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_contract_seam_fidelity.py
  - Action: In `skills/spec-prototype/scripts/materialize_contracts.py`, delete domain-specific and shortcut assumptions from the ergonomics and break protocol templates: remove `reservation card`, `historical booking steps`, `Space or P`, `J / K`, and `rapid Space hits`. Replace them with domain-neutral action triggers (`primary action trigger`, `rapid trigger activations`, and `Esc` for overlay dismissal if modals are present), or emit `unspecified` when ergonomics shortcuts are unauthored. In `tests/test_contract_seam_fidelity.py`, update tests to verify clean domain-neutral ergonomics and remove stale assertions for legacy regex-based craft assertions.

- [ ] T-03 Eliminate unauthored cognitive ledger buzzwords and defaults
  - Depends on: T-02
  - Anchors: skills/spec-prototype/scripts/materialize_contracts.py:extract_cognitive_ledger, tests/test_pipeline.py:test_materialize_contracts_high_fidelity_semantic_synthesis
  - Write scope: skills/spec-prototype/scripts/materialize_contracts.py, tests/test_pipeline.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_pipeline.py -k test_materialize_contracts_high_fidelity_semantic_synthesis
  - Action: In `skills/spec-prototype/scripts/materialize_contracts.py`, update `extract_cognitive_ledger` and the c1 Cognitive Ledger table generator: when ledger zones (`zero_borrow_base`, `high_yield_borrow_zone`, `repayment_settlement`) are unauthored, mark them as `unspecified` rather than injecting ungrounded prose (`tactile detents`, `micro-sparklines`, `kinetic pulses`, or `10x situational awareness`). In `tests/test_pipeline.py`, update assertions in `test_materialize_contracts_high_fidelity_semantic_synthesis` to ensure unauthored cognitive ledger outputs maintain semantic neutrality.

- [ ] T-04 Constrain formal token compilation to f1 source only
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/compile_tokens.py:compile_tokens, skills/spec-prototype/scripts/compile_tokens.py:_resolve_token_source, tests/test_tokens.py:test_compile_tokens_reads_f1_foundation_dials_and_palette
  - Write scope: skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_tokens.py
  - Action: In `skills/spec-prototype/scripts/compile_tokens.py`, update `_resolve_token_source` so that in `formal` mode, token compilation strictly reads from the sealed foundation record (`f1.md` or successor foundation) and never appends un-materialized decisions from `discussion.md`. Any new decisions authored in `discussion.md` must first be materialized into a successor foundation record before token compilation can consume them in formal mode. In `tests/test_tokens.py`, add a test verifying that subsequent un-materialized decisions in `discussion.md` are ignored during formal mode token compilation when `f1.md` is present.

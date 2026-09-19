## 1. Admit the authored scope at the formal entry

- [x] T-01 Admit full-product coverage and enforce retained map identity at the formal entry
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/lint_spec_contracts.py, skills/spec-prototype/scripts/assemble_envelope.py
  - Write scope: skills/spec-prototype/scripts/lint_spec_contracts.py, skills/spec-prototype/scripts/assemble_envelope.py, tests/test_formal_entry_admission.py
  - Implements: CPC-002, CPC-005
  - Proves: CPC-SCN-003, CPC-SCN-004, CPC-SCN-018, CPC-SCN-019, CPC-SCN-020
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_formal_entry_admission.py
  - Action: A `coverage: full-product` map whose `selected-surfaces` is empty is the documented authoring form, yet `lint_formal_entry` reports every target surface as `E011_SELECTION_WIDENED` because it compares target surfaces against the selected list without consulting `authorizes_full_product`. The same entry never detects a stale map identity because `read_formal_context` passes neither `expected_map_revision` nor `expected_map_digest`, leaving `E010_STALE_CONTRACT` unreachable in production. Make the widening check apply only to `selected` coverage, keep a genuinely empty `selected` coverage an error, and give the formal entry an expected map identity sourced from the retained selection source so that a revision or digest mismatch fails dispatch with the specific mismatch. Do not weaken the neighboring admission checks for unknown contexts, well-formed selections or unauthorized paths.
  - Proof: Build temporary roots proving that a full-product map with an empty selected list assembles an envelope whose target set is every applicable surface, that a selected map naming a surface outside its selection still fails, that an empty selected coverage still fails, that a matching map revision passes, and that a changed revision and a changed digest each fail with the specific mismatch. Assert every refusal mutates nothing. These are mechanism checks in temporary repositories, not live design sessions.

## 2. Withhold completion for an unusable scope

- [x] T-02 Refuse completion of an unusable scope in the reconciler, the quality check and the review portal
  - Depends on: T-01
  - Anchors: skills/spec-prototype/scripts/prototype_context.py, skills/spec-prototype/scripts/verify_prototype_quality.py, skills/spec-prototype/scripts/generate_review_portal.py
  - Write scope: skills/spec-prototype/scripts/prototype_context.py, skills/spec-prototype/scripts/verify_prototype_quality.py, skills/spec-prototype/scripts/generate_review_portal.py, tests/test_empty_scope_completion.py
  - Implements: CPC-006
  - Proves: CPC-SCN-011, CPC-SCN-022, CPC-SCN-023
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_empty_scope_completion.py
  - Action: `reconcile_obligations` derives completion from the in-round set alone and never consults the context errors, so a `coverage: selected` map with an empty `selected-surfaces` reports `completion: true` while `read_context` records `empty_selection`. `verify_prototype_quality` and the review portal call the reconciler directly without any gate, so both launder that false completion and the portal renders a met completion for a scope that implements nothing. Make the reconciler treat an unusable context as withholding completion with the governing error attached, and make both non-formal consumers refuse to report completion when the context is unusable. Keep scope membership, delivery and evidence as separate facts, and preserve the existing behavior for well-formed selections and authorized full-product coverage.
  - Proof: Using temporary fixtures, assert that an empty selected coverage withholds completion in the reconciler, in the quality check and in the generated portal, that the portal no longer renders a met completion for it, that unresolved and legacy coverage behave the same way, and that a well-formed selected coverage and an authorized full-product coverage are unaffected. Assert unrelated verification failures are still reported and that no refusal rewrites an existing artifact.

## 3. Name the platform fields the roles receive

- [x] T-03 Name the envelope platform fields the Builder and Critic actually receive
  - Depends on: none
  - Anchors: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, skills/spec-prototype/scripts/prototype_context.py
  - Write scope: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, tests/test_platform_instruction_fields.py
  - Implements: CPC-005
  - Proves: CPC-SCN-009, CPC-SCN-021
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_platform_instruction_fields.py
  - Action: The Builder instruction points at a `target_platform` envelope field that is never projected. The envelope exposes `platform.target_context`, `platform.prototype_medium`, `platform.verification_environment` and `platform.native_validation_pending`, plus the per-surface applicability facts. Correct both role instructions to name the fields that are actually emitted, state plainly how a role resolves a surface's applicable platform context from the authored facts, and state how the Critic compares recorded capture metadata against the environment named by a projected field. Do not add platform-specific agents and do not widen the envelope format.
  - Proof: Instruction-contract tests assert that the corrected field names are present, that the phantom field name is absent from the edited role instructions, that the named fields are exactly those the projection emits, and that the Critic instruction can name the field it compares capture metadata against. Label these as instruction wiring, not proof that a live Critic ran.

## 4. Allow a spec-only freeze

- [x] T-04 Allow spec-only approval to freeze without a built prototype
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/handoff.py, skills/spec-prototype/references/04-governance/handoff.md
  - Write scope: skills/spec-prototype/scripts/handoff.py, tests/test_spec_only_freeze.py
  - Implements: CPC-007
  - Proves: CPC-SCN-015, CPC-SCN-024
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_spec_only_freeze.py
  - Action: `freeze()` calls `require_prototype_entry` unconditionally, so a spec-only approval is refused with `Prototype write scope has no HTML entry` even though the governance reference states that selecting a ready spec does not require a build. Make the prototype entry requirement apply only when the frozen scope actually claims prototype implementation, and keep implementation, platform and production validation pending on the spec-only path. Do not remove the requirement for a scope that does claim a prototype, and do not let an override manufacture frozen-approved authority.
  - Proof: In temporary roots, assert that a spec-only approval freezes without any HTML artifact and reports implementation validation pending, that a scope claiming a prototype still fails when no HTML entry exists, that a valid prototype freeze is unchanged, and that a refused freeze leaves existing artifacts intact.

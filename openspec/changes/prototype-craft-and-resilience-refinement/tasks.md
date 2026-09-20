## 1. Relax contract linting with fault-tolerant parsing

- [ ] T-01 Allow format tolerance and advisory digest matching in context reader and contract linter
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/prototype_context.py, skills/spec-prototype/scripts/lint_spec_contracts.py
  - Write scope: skills/spec-prototype/scripts/prototype_context.py, skills/spec-prototype/scripts/lint_spec_contracts.py, tests/test_contract_fault_tolerance.py
  - Implements: CRR-001
  - Proves: CRR-SCN-001, CRR-SCN-002
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_contract_fault_tolerance.py
  - Action: Update `parse_section` in `prototype_context.py` to gracefully handle extra whitespace, trailing comments, and varied list punctuation. In `lint_spec_contracts.py`, when expected map revision matches the authored revision, treat digest discrepancies as an advisory diagnostic instead of throwing a blocking `E010_STALE_CONTRACT` error. Ensure that mismatched revisions still strictly trigger `E010_STALE_CONTRACT`.
  - Proof: In `tests/test_contract_fault_tolerance.py`, test that whitespace variances and comments parse correctly, that matching revision with differing digest succeeds with diagnostic warning, and that mismatched revision still fails as expected.

## 2. In-memory state store for context preservation

- [ ] T-02 Instruct Builder on zero-dependency in-memory state store and context preservation
  - Depends on: none
  - Anchors: agents/spec-prototype-builder.md, skills/spec-prototype/references/01-foundations/design-methods.md
  - Write scope: agents/spec-prototype-builder.md, tests/test_builder_state_store_contract.py
  - Implements: CRR-002
  - Proves: CRR-SCN-003
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_builder_state_store_contract.py
  - Action: In `agents/spec-prototype-builder.md`, add explicit instructions mandating that interactive prototypes must maintain a centralized in-memory state object (`window.__prototypeState` or top-level store). Form field inputs, active tab/filter states, and drawer open/close flags must mutate this store so that closing a drawer or sub-modal preserves form drafts and table filters. Prohibit heavy external state management libraries.
  - Proof: Contract test in `tests/test_builder_state_store_contract.py` verifying that builder instructions require the in-memory state store, forbid unpreserved modal resets, and reference Method 5 Decisive 3-Frame rules.

## 3. Somatic touch ergonomics and optical geometry

- [ ] T-03 Mandate somatic mobile ergonomics and concentric geometry in Builder and Critic contracts
  - Depends on: none
  - Anchors: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md
  - Write scope: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, tests/test_platform_craft_rules.py
  - Implements: CRR-003
  - Proves: CRR-SCN-004
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_platform_craft_rules.py
  - Action: In `agents/spec-prototype-builder.md` and `agents/spec-prototype-critic.md`, inject explicit CSS rules and review criteria: mobile environments must specify `env(safe-area-inset-*)`, min 44×44px touch targets, `:active` spring micro-feedback; nested container radius must calculate $R_{in} = \max(0, R_{out} - P)$; telemetry and financial metrics must specify `tabular-nums`.
  - Proof: Contract test in `tests/test_platform_craft_rules.py` verifying that both Builder and Critic instructions contain the exact somatic touch constraints, concentric radius formulas, and tabular numeric rules.

## 4. Dual-view review portal with Break Protocol toggles

- [ ] T-04 Add viewport switching and Break Protocol data injection controls to review portal
  - Depends on: T-01
  - Anchors: skills/spec-prototype/scripts/generate_review_portal.py
  - Write scope: skills/spec-prototype/scripts/generate_review_portal.py, tests/test_review_portal_views.py
  - Implements: CRR-004
  - Proves: CRR-SCN-005
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_review_portal_views.py
  - Action: Enhance `generate_review_portal.py` to embed viewport simulation frames (Desktop 1440px / Tablet 768px / Mobile 390px) into the review portal HTML, alongside an interactive toggle for the Break Protocol that passes stress parameters (`?stress=overflow` / `?stress=empty`) into prototype preview iframes.
  - Proof: Test in `tests/test_review_portal_views.py` ensuring the generated portal HTML contains viewport selector controls and stress-test toggle elements.

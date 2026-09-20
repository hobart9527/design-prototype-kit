## 1. Platform Truth and Token Compiler Purity

- [ ] T-01 Remove synthetic platform inference and preserve platform neutrality
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/prototype_context.py, tests/test_prototype_context.py
  - Write scope: skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/prototype_context.py, tests/test_platform_truth.py
  - Implements: CPC-003
  - Proves: CPC-SCN-005, CPC-SCN-006, CPC-SCN-022
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_platform_truth.py
  - Action: In `materialize_contracts.py`, remove the heuristic mapping regex (`Mobile|Touch|Booking|移动|预约|触控 -> ios/mobile/touch`). Platform target must strictly be `explicit` (when authored in discussion or product metadata) or `unknown`. Decouple device class (`mobile`/`tablet`/`desktop`/`unknown`) and input modality (`touch`/`pointer`/`keyboard`/`unknown`) so that touch input or mobile screen size never silently fabricates an iOS/Android target OS. Update `prototype_context.py` if needed to faithfully retain undeclared platform facts as `unknown`.
  - Proof: `tests/test_platform_truth.py` verifies that a product mentioning booking, mobile, or touch without explicit OS declaration yields `target: "unknown"`, preserving input and viewport facts without fabricating an iOS runtime.

- [ ] T-02 Purify token compiler of opinionated aesthetic defaults
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Write scope: skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Implements: CPC-004
  - Proves: CPC-SCN-023
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_tokens.py
  - Action: In `compile_tokens.py`, eliminate implicit aesthetic defaults (`warm-graphite-lime`, `machined-industrial`, `kinetic`, etc.). When Five Axes dials are undeclared or empty, compile an un-opinionated, neutral grayscale scaffold with balanced density and steady rhythm rather than an industrial green theme. Distinguish `formal` mode (which strictly requires explicit dials or outputs neutral tokens) from `probe` mode.
  - Proof: Unit tests in `tests/test_tokens.py` prove that compiling empty or omitted dials outputs a neutral base palette without sneaking in lime accents or machined finishes.

## 2. Envelope Declassification and Invariant Floor

- [ ] T-03 Declassify layout profiles into advisory candidate patterns in envelope
  - Depends on: T-01
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_platform_envelope.py
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_platform_envelope.py
  - Implements: CPC-004
  - Proves: CPC-SCN-007, CPC-SCN-008, CPC-SCN-024
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_platform_envelope.py
  - Action: In `assemble_envelope.py`, replace the rigid regex classification of baseline/product category into a single mandatory `layout_profile` (`somatic-touchflow`, `editorial-reading`, `operational-canvas`, `dense-console`). Instead, emit an advisory list `candidate_patterns` and set `selected_pattern: null` unless explicitly confirmed by upstream authored design specifications. Leave layout and component topology decisions to the Builder.
  - Proof: `tests/test_platform_envelope.py` confirms that product categories (e.g. SaaS or Console) no longer lock the envelope into a hardcoded profile, providing candidate patterns while keeping selection open.

- [ ] T-04 Converge Builder rules to the 5 core integrity categories
  - Depends on: T-03
  - Anchors: agents/spec-prototype-builder.md
  - Write scope: agents/spec-prototype-builder.md
  - Implements: CPC-003
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_canonical_ontology.py
  - Action: Refactor `agents/spec-prototype-builder.md` instructions. Strip out brittle, prescriptive implementation heuristics (such as mandatory Toast notifications, mandatory Spring physics, global rigid 44px rules regardless of platform). Enforce the 5 non-negotiable integrity categories: 1) Semantic Integrity (OOUX core objects and actions), 2) Task Integrity (critical journey paths work), 3) Accessibility Integrity (WCAG 2.2 AA target size 24px minimum with standard inline/spacing exceptions), 4) State & Recovery Integrity (loading, empty, error, recovery), 5) Platform Integrity (honoring declared platform invariants or staying neutral when unknown).
  - Proof: `tests/test_canonical_ontology.py` and rule lint confirm builder instructions retain core invariant boundaries without prescriptive aesthetic micromanagement.

- [ ] T-05 Decouple Critic and quality floor from aesthetic gatekeeping
  - Depends on: T-04
  - Anchors: agents/spec-prototype-critic.md, skills/spec-prototype/references/03-quality/quality-floor.md, skills/spec-prototype/scripts/verify_prototype_quality.py
  - Write scope: agents/spec-prototype-critic.md, skills/spec-prototype/references/03-quality/quality-floor.md, skills/spec-prototype/scripts/verify_prototype_quality.py
  - Implements: CPC-004
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_pipeline.py
  - Action: Ensure Critic and quality-floor scripts evaluate prototypes against task completion, contrast, a11y, state handling, and contract conformance. Prohibit failing builds based on subjective aesthetic craft choices (e.g. specific radius ratios, drawer vs sheet preferences, transition curves). Craft evaluations are reported as advisory critique feedback, not fatal build blockers.
  - Proof: `tests/test_pipeline.py` verifies quality checks pass for clean functional prototypes regardless of stylistic variation.

- [ ] T-06 Solidify regression defense for semantic freedom and unknown preservation
  - Depends on: T-01, T-02, T-03, T-04, T-05
  - Anchors: tests/test_design_chain_continuity.py, tests/test_platform_truth.py
  - Write scope: tests/test_semantic_freedom_regression.py
  - Implements: CPC-003, CPC-004
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_semantic_freedom_regression.py
  - Action: Author end-to-end regression tests in `tests/test_semantic_freedom_regression.py` covering the full chain: discussion with unspecified platform -> contract materialization preserves unknown -> token compilation remains neutral -> envelope provides flexible candidate patterns -> builder contract is bounded by the 5 invariants -> critic evaluates floor without aesthetic gatekeeping.
  - Proof: All regression scenarios pass with 0 failures and zero workspace pollution.

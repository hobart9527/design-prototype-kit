## 1. Preserve the design spine

- [x] T-01 Amend the owning workflow with informed Stage 3 selection and continuity rules
  - Depends on: none
  - Anchors: skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-workflow.md, skills/spec-prototype/references/04-governance/usage.md, skills/spec-prototype/references/04-governance/handoff.md, tests/test_canonical_ontology.py
  - Write scope: skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-workflow.md, skills/spec-prototype/references/04-governance/usage.md, skills/spec-prototype/references/04-governance/handoff.md, tests/test_design_chain_continuity.py
  - Implements: CPC-001
  - Proves: CPC-SCN-001, CPC-SCN-002
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_design_chain_continuity.py
  - Action: Amend the existing route, not add a new Skill or lifecycle. Preserve Double Diamond iteration, Nine Pillars ownership, Five Axes expression, applicable References, grounded evidence and provisional-before-formal-build authority. Insert concrete scope recommendations before Stage 3 only when unresolved. Explicit prior scope skips another question. Keep bounded probes, spec-only work and local refinement valid. Distinguish scope choice from approval. Preserve product model, rationale, method outcomes and dependencies when selecting a subset; unselected details can remain provisional, not be deleted or invented. Correct owned Stage 5 command specimens against the actual handoff interface rather than retaining product.md as a slice spec.
  - Proof: Create focused instruction-contract tests for all three lightweight routes, formal Spec requirements, selection timing and retained upstream meaning. Test contradictory old prescriptions are absent in the edited route sections, not only that new keywords exist. These are mechanism checks, not proof of model design judgment. Existing missing working-tree files must not be restored without an established implementation basis.

## 2. Normalize authored scope and platform context

- [x] T-02 Add minimal authored selection and platform contracts with a deterministic reader
  - Depends on: T-01
  - Anchors: skills/spec-prototype/templates/surface-map.md, skills/spec-prototype/templates/product.md, skills/spec-prototype/templates/experience-foundation.md, skills/spec-prototype/templates/prototype-specification.md, skills/spec-prototype/scripts/assemble_envelope.py
  - Write scope: skills/spec-prototype/templates/surface-map.md, skills/spec-prototype/templates/product.md, skills/spec-prototype/templates/experience-foundation.md, skills/spec-prototype/templates/prototype-specification.md, skills/spec-prototype/scripts/prototype_context.py, tests/test_prototype_context.py
  - Implements: CPC-002, CPC-003
  - Proves: CPC-SCN-003, CPC-SCN-004, CPC-SCN-005, CPC-SCN-006
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_prototype_context.py
  - Action: Extend existing source templates and create one small stdlib helper for explicit machine-readable sections in retained Markdown. The Surface Map owns coverage selected/full-product, revision, surface/journey/context IDs and selection-source reference. Product owns target context; foundation owns shared invariants; the slice spec owns local adaptation and prototype medium. Keep actual verification environment an evidence fact. The helper validates and normalizes authored facts; the designer, not a scoring heuristic, recommends concrete combinations using task risk and probe results. No second editable JSON authority or new dependency.
  - Proof: Use temporary source documents containing ten surfaces and a three-surface selection, prior explicit full-product scope, unresolved selection, unknown/duplicate IDs, stale map identity, platform-specific applicability and a required dependency outside selection. Missing selection never means full-product; surface dependencies are disclosed, not silently added. Round-trip or parse fixtures retain unselected product context. Test desktop split/mobile detail adaptation preserves object, permission and return invariants, and Android-target/HTML-medium remains distinct. Legacy sources remain readable as unresolved without mutation. Include source-contract checks tying the concrete recommendation obligations to T-01; do not label those checks real-session evidence.

## 3. Deliver lossless bounded Builder inputs

- [x] T-03 Wire normalized coverage and platform contracts into compilation and dispatch
  - Depends on: T-02
  - Anchors: skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/assemble_envelope.py, skills/spec-prototype/scripts/execution_boundary.py, skills/spec-prototype/scripts/lint_spec_contracts.py
  - Write scope: skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/assemble_envelope.py, skills/spec-prototype/scripts/execution_boundary.py, skills/spec-prototype/scripts/lint_spec_contracts.py, tests/test_platform_envelope.py
  - Implements: CPC-004
  - Proves: CPC-SCN-007, CPC-SCN-008
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_platform_envelope.py
  - Action: Consume prototype_context from T-02 in the formal path, retaining source identities and existing exact JSON dispatch. Connect applicable contract lint to the actual formal entry. Remove invented Core Tension, borrowed-reference and shortcut behavior at the owned projection seams; preserve explicit project constraints and unknown optional probe facts. Retain relevant tasks, state/recovery, Signature, method outcomes and source references. Validate canonical paths and selected IDs without widening write scope or making hook permission approval. If a helper must be exposed through the boundary, authorize only its bounded argument form.
  - Proof: Invoke materialization, envelope assembly and boundary admission in temporary repositories. Assert authored values survive, absent fields do not become fixed domain claims or Space/P actions, stale/tampered references fail, traversal or symlink escape fails, selected output cannot expand to unselected surfaces, and the existing brief-only probe route still works. Ensure lint actually runs in the formal path rather than testing it only in isolation. Preserve error context and existing artifacts on failures.

## 4. Prove platform behavior honestly

- [x] T-04 Bind Builder capture and Critic inputs to revision-specific platform evidence
  - Depends on: T-03
  - Anchors: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, skills/spec-prototype/scripts/capture.mjs, skills/spec-prototype/templates/prototype-evidence.md
  - Write scope: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, skills/spec-prototype/scripts/capture.mjs, skills/spec-prototype/templates/prototype-evidence.md, tests/test_platform_evidence.py
  - Implements: CPC-005
  - Proves: CPC-SCN-009, CPC-SCN-010
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_platform_evidence.py
  - Action: Amend existing roles, do not add platform-specific agents. Builder must implement applicable platform rules and exercise contracted consequential tasks; Critic must inspect actual target images and relevant task evidence, reporting unexamined scope and no approval. Capture records actual environment and target/source identity, not native validation inferred from viewport width. Prevent inherited human/visual status from silently approving changed content. Keep capture failure explicit and avoid writing evidence to an unrelated repository merely because the script lives there. Extend the existing evidence template with minimal environment, action, observation, simulation and dependency references.
  - Proof: Hermetic tests invoke the capture metadata seam with a stub browser or testable pure metadata function, covering screenshot-only evidence, Android-target/HTML-browser execution, capture failure, changed shared navigation and an unrelated source change. Changed dependencies invalidate evidence; unaffected dependencies remain reusable. Assert role instructions demand real image/task inspection; label these as instruction wiring, not proof that a live Critic ran. No browser installation or paid session is required by this verifier.

## 5. Complete exactly the promised scope

- [x] T-05 Reconcile selected coverage in quality checks and review portal
  - Depends on: T-04
  - Anchors: skills/spec-prototype/scripts/verify_prototype_quality.py, skills/spec-prototype/scripts/generate_review_portal.py, skills/spec-prototype/references/core-workflow.md, skills/spec-prototype/scripts/prototype_context.py
  - Write scope: skills/spec-prototype/scripts/verify_prototype_quality.py, skills/spec-prototype/scripts/generate_review_portal.py, skills/spec-prototype/scripts/prototype_context.py, skills/spec-prototype/references/core-workflow.md, tests/test_prototype_coverage.py
  - Implements: CPC-006
  - Proves: CPC-SCN-011, CPC-SCN-012, CPC-SCN-013
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_prototype_coverage.py
  - Action: Use one obligation reconciler for selected and full-product. Derive missing delivery and required evidence from the retained map, not file globbing alone. Separate scope membership, delivery and evidence facts; do not implement the four earlier proposed presentation labels as an exclusive state machine. Allow truthful pending siblings with no href when no sibling is delivered; verify actual delivered navigation. Portal must show declared absent surfaces and selected versus outside-round obligations. Product navigation is not forced to display management statuses. Continue full-product batches only under the bound authorization; preserve resource/decision blockers and resume scope. A map revision change must not auto-expand or shrink the set.
  - Proof: Temporary ten-surface fixtures cover selected-three with only one artifact, no-delivered-sibling acceptance, a broken delivered sibling link, full-product after batch one, documented blockers, a missing required surface, missing evidence, platform applicability and map additions/removals. Assert portal contains declared missing surfaces. Assert completion is false for any unmet selected obligation even with a reason; outside-round surfaces do not block selected completion. Verify source instructions distinguish auto-continuation from approval and selected completion from full-product completion.

## 6. Retain trustworthy freeze and downstream admission

- [x] T-06 Reject permissive freeze fallback and bind downstream admission to current sources
  - Depends on: T-05
  - Anchors: skills/spec-prototype/scripts/handoff.py, skills/spec-prototype/scripts/execution_boundary.py, skills/spec-prototype/references/04-governance/handoff.md
  - Write scope: skills/spec-prototype/scripts/handoff.py, skills/spec-prototype/scripts/execution_boundary.py, skills/spec-prototype/references/04-governance/handoff.md, tests/test_handoff_scope_integrity.py
  - Implements: CPC-007
  - Proves: CPC-SCN-014, CPC-SCN-015
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_handoff_scope_integrity.py
  - Action: Preserve exact selection/platform/evidence references in handoff identity. Replace broad exception fallback with explicit format admission that never bypasses a failed strict contract. Validate current digests downstream. Bind approval to an actual referenced source and exact scope/revision; planned/negated text and arbitrary substring matches are insufficient. Keep unsupported authority pending; do not invent external approval infrastructure. Remove the ability of --force or hook admission to manufacture frozen-approved status. Preserve spec-only approval while reporting implementation evidence pending and qualifying prototype medium.
  - Proof: Exercise the actual freeze/gate functions or CLI in temporary roots with valid references, stale source digests, malformed strict packets, planned/negated approval, override without approval, changed content after freeze and a valid spec-only approved record. A strict failure must remain failed; no HTML is required merely to retain design-only approval; implementation/platform claims remain pending. Existing artifacts remain intact on rejection.

## 7. Repair the measuring instrument

- [x] T-07 Reject unverified comparisons and numerical overflow false passes
  - Depends on: none
  - Anchors: benchmarks/judges/task_judge.py, benchmarks/judges/regression_judge.py, tests/test_benchmark_harness.py
  - Write scope: benchmarks/judges/task_judge.py, benchmarks/judges/regression_judge.py, tests/test_benchmark_measurement.py
  - Implements: CPC-008
  - Proves: CPC-SCN-016
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_benchmark_measurement.py
  - Action: Evaluate horizontal overflow from validated available dimensions rather than a missing boolean default. Missing or invalid measurements remain unverified. Unverified-to-unverified is not a verified PASS; failed-to-unverified is not improvement. Preserve independent verified dimensions and explicit comparison limits instead of coercing an overall optimistic result. Align touch-field consumption with actual recorded evidence if needed within this task, without silently treating missing values as pass.
  - Proof: Tests cover 712/390 overflow, equal widths, absent/invalid measurements, both arms unverified, failed-to-unverified and genuine verified regressions/improvements. The old behavior must fail these tests. Do not modify historical reports or run paid judges.

- [x] T-08 Wire critical gates and actual candidate provenance into regression records
  - Depends on: T-07
  - Anchors: benchmarks/runners/aggregate_report.py, benchmarks/runners/run_case.py, benchmarks/runners/bench_lib.py, benchmarks/README.md, tests/test_benchmark_harness.py
  - Write scope: benchmarks/runners/aggregate_report.py, benchmarks/runners/run_case.py, benchmarks/runners/bench_lib.py, benchmarks/README.md, tests/test_benchmark_provenance.py
  - Implements: CPC-008
  - Proves: CPC-SCN-017
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_benchmark_provenance.py
  - Action: Make critical accessibility participate in aggregate acceptance alongside every already-declared hard gate. Record actual Skill/agent and judge content identity using existing manifest helpers where possible, including dirty files instead of claiming only a clean Git revision. Add a bounded opt-in regression specimen to the existing README: start with representative review, explicitly expand the same product to full scope, verify cross-page state/return and mobile adaptation, retain unverified native simulation, and pin source/conditions. The specimen must use existing runners rather than add a new orchestration layer. New live cases or paid execution are outside this task; do not assert those experiments ran.
  - Proof: Hermetic tests show a critical accessibility violation blocks aggregate acceptance, changed candidate or judge bytes change provenance, unchanged content stays stable, legacy missing provenance is disclosed rather than invented, and prior results are not overwritten. Source identity excludes secrets and unrelated files. Run no paid benchmark.

## 8. Independent continuity review

- [x] T-09 Review the integrated golden chain and focused regression results without edits
  - Depends on: T-06, T-08
  - Anchors: openspec/changes/prototype-coverage-platform-continuity/design.md, skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-workflow.md, skills/spec-prototype/scripts/assemble_envelope.py, agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, tests/test_design_chain_continuity.py
  - Artifact inputs: T-01, T-02, T-03, T-04, T-05, T-06, T-07, T-08
  - Verify with: python3 -m pytest -q -p no:cacheprovider tests/test_design_chain_continuity.py tests/test_prototype_context.py tests/test_platform_envelope.py tests/test_platform_evidence.py tests/test_prototype_coverage.py tests/test_handoff_scope_integrity.py tests/test_benchmark_measurement.py tests/test_benchmark_provenance.py
  - Action: Perform a zero-write independent review of the integrated diff and the directly named new proof files. Trace one selected-page fixture and one full-product fixture through source contracts, projection, Builder/Critic instructions, evidence, portal and handoff. Check that product decisions, applicable method outcomes, Signature, states, recovery and approval boundaries were not lost; confirm probes/spec-only/local refinement remain valid. Inspect production changes rather than merely counting test passes or retained method names. Report exact defects as Findings for source-spec revision; do not edit implementation or reinterpret scope. Distinguish mechanism success from a live design session and explicitly record that paid end-to-end/native validation did not run.

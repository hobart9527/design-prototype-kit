# Tasks

- [ ] T-01 Retire core-workflow contract entry in benchmark harness
  Replace the body of `skills/spec-prototype/references/core-workflow.md` with a short retirement stub naming current owners (SKILL.md entry, core-kernel.md guardrails, references/stages/ stage bodies). Switch `benchmarks/runners/bench_lib.py` `REQUIRED_SKILL_ENTRIES` to `references/core-kernel.md`, and update the `tests/test_benchmark_harness.py` `_complete_skill` fixture and missing-entry case to `references/core-kernel.md`.
  - Anchors: benchmarks/runners/bench_lib.py:REQUIRED_SKILL_ENTRIES
  - Depends on: none
  - Write scope: skills/spec-prototype/references/core-workflow.md, benchmarks/runners/bench_lib.py, tests/test_benchmark_harness.py
  - Verify with: python3 -m pytest tests/test_benchmark_harness.py tests/test_v10_integrity.py tests/test_design_chain_continuity.py -q

- [ ] T-02 Authored viewport precedence in mandatory inspection contract
  Extend `assemble_envelope._mandatory_viewports` to accept authored verification viewports: when the Canonical Spec IR declares `scope.verification_scope.viewports`, those widths win (sorted, deduped, positive) and the device ladder is only the fallback. Both `inspection_contract.mandatory_viewports` and the `capture.mjs` command line consume the precedence-resolved list. Add regression tests in `tests/test_lean_builder_payload.py`: a spec declaring e.g. 1440/1024 viewports is inspected at those widths even when `device_context: desktop` would otherwise yield only 1280.
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py:_mandatory_viewports
  - Depends on: none
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_lean_builder_payload.py
  - Verify with: python3 -m pytest tests/test_lean_builder_payload.py tests/test_pipeline.py -q

- [ ] T-03 Critic tiered evidence degradation protocol
  Inject an explicit L1/L2/L3 tiered evidence protocol section into `agents/spec-prototype-critic.md`: L1 = DOM/ARIA/`data-state` structural checks (always available, static source, only blocking tier); L2 = computed-style checks (requires a reachable headless style engine); L3 = screenshot comparison (best-effort capture). A missing browser/fonts/GPU degrades to the reachable tier, reported as `environment_not_ready` with the tier reached — never silently skipped and never a code-assertion failure. Mirrors the implemented chain in `scripts/verify_prototype_quality.py`.
  - Anchors: agents/spec-prototype-critic.md:Inspect-before-explanation
  - Depends on: none
  - Write scope: agents/spec-prototype-critic.md
  - Verify with: python3 -m pytest tests/test_v10_integrity.py -q

# Change: 2026-09-25-progressive-contracts-consumer-alignment

## Why

The optimization plan (`docs/spec-prototype-co-creation-optimization-plan.md`, §7 Waves 3–4) deferred two waves from the completed change 2026-09-25-co-creation-and-flow-integrity. Wave 3 fixes a schema-validation deadlock: the canonical IR schema requires a full state machine at the top level, so a legal Stage 1 intent Spec is rejected before Stage 3 can author states; it also hardcodes telemetry/4096 invariants into compiled IR and splits state ids like `interaction/inspecting` into loose words. Wave 3 additionally leaves tokens open to reverse reconciliation in formal mode, so a hand-edited `tokens.css` can pass freshness checks. Wave 4 leaves Builder/Critic prompts biased toward uniform large radii, wide padding, and negative tracking, with no cognitive-quality review dimension, and `verify_prototype_quality.py` has no tiered evidence chain — a headless CI container without fonts or GPU blocks basic state-machine and accessibility verification instead of degrading gracefully.

## What Changes

- Wave 3 (contracts/flow): introduce `intent_spec` / `execution_spec` progressive schema tiers (Stage 1 vs Stage 3/4 admission); structurally support meso assembly slots (`layout_directives.massing_pattern`, `interaction_spec.kinematics`, `visual_directives.data_syntax`); stop injecting hardcoded telemetry/4096 invariants without authored sources; preserve full state identifiers (`interaction/inspecting`) end to end. Establish tokens uni-directional derivation (Discussion/Spec IR → compile_tokens → tokens.css), retire formal-mode reverse reconciliation, mark tampered tokens `out_of_sync` and hard-reject downstream, and consume canonical craft_stack + palette for real parameterization.
- Wave 4 (consumers/eval): Builder consumes meso constructs (massing for spatial center of gravity, kinematics for transitions/focus restore, data_syntax for compact alignment and micro-trends) with uniform-radius/padding/tracking biases removed; Critic gains dual review (engineering contract + cognitive quality) and blocks `display:none` context loss; `verify_prototype_quality.py` gains an L1 (DOM/ARIA/data-state) → L2 (computed style) → L3 (screenshot) tiered degradation chain that labels environment gaps instead of failing code assertions; `eval.yaml` include path is corrected to the repo-root `agents/` originals and `confirmed-resume` plus a blind-comparison baseline are added.

## Non-Goals

- Modifying Nine Pillars/Five Axes meaning, the co-creation governance landed in the predecessor change, or reopening retired core-workflow ownership.
- Changing Loom Runtime, product prototype artifacts under `prototype/`, or archived Changes.
- Adding a Stage 1.5, hidden DAG, or new style lookup tables.
- GPU/font provisioning for CI; L3 remains best-effort with explicit environment labeling.

## Impact

Two compiler scripts (`compile_spec_ir.py`, `compile_tokens.py`), one lint script (`lint_spec_contracts.py`), the canonical schema (`prototype-spec.v1.json`), one quality script (`verify_prototype_quality.py`), two agent prompt files, three craft-method references, eval configs, and their owner tests. After landing: Stage 1 legal intent Specs pass validation; unauthored domain invariants never reach compiled IR; hand-edited tokens are rejected downstream; Builder receives only Spec-declared craft; CI without a browser still proves state machine and accessibility at L1/L2. Owner tests updated in the same tasks; cross-task retarget obligations are declared explicitly (tests/test_pipeline.py in the craft-method task, lint/schema alignment via dependency).

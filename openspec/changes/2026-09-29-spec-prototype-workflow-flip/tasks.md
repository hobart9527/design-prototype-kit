# Tasks

- [ ] T-01 Flip core kernel and stage lifecycle from Spec-first to Prototype-first
  - Depends on: none
  - Anchors: skills/spec-prototype/references/core-kernel.md, skills/spec-prototype/SKILL.md
  - Write scope: skills/spec-prototype/CONTEXT.md, skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-kernel.md, skills/spec-prototype/references/04-governance/artifact-lifecycle.md
  - Verify with: python3 -m pytest -q tests/test_canonical_ontology.py
  - Verify tier: unit

- [ ] T-02 Update stage execution references for prototype-first workflow
  - Depends on: T-01
  - Anchors: skills/spec-prototype/references/stages/stage-1-frame.md, skills/spec-prototype/references/stages/stage-2-probe.md
  - Write scope: skills/spec-prototype/references/stages/stage-0-explore.md, skills/spec-prototype/references/stages/stage-1-frame.md, skills/spec-prototype/references/stages/stage-2-probe.md, skills/spec-prototype/references/stages/stage-3-skeleton.md, skills/spec-prototype/references/stages/stage-5-freeze.md
  - Verify with: python3 -m pytest -q tests/test_v10_integrity.py -k "not test_three_tier_semantic_tokens_and_dtcg_authority"
  - Verify tier: unit

- [ ] T-03 Harmonize test assertions locking legacy Spec-first prose
  - Depends on: T-02
  - Anchors: tests/test_pipeline.py, tests/test_design_chain_continuity.py
  - Write scope: tests/test_pipeline.py, tests/test_v10_integrity.py, tests/test_design_chain_continuity.py
  - Verify with: python3 -m pytest -q tests/test_pipeline.py tests/test_design_chain_continuity.py
  - Verify tier: unit

- [ ] T-04 Add modern style vocabulary and multi-direction exploration guides
  - Depends on: T-02
  - Anchors: skills/spec-prototype/references/02-craft-methods/visual-craft.md, skills/spec-prototype/templates/discussion.md
  - Write scope: skills/spec-prototype/references/02-craft-methods/modern-style-vocabulary.md, skills/spec-prototype/references/stages/stage-2-probe.md, skills/spec-prototype/templates/discussion.md
  - Verify with: python3 -m pytest -q tests/test_canonical_ontology.py
  - Verify tier: unit

- [ ] T-05 Consolidate runtime hard checks into capture and relax agent restrictions
  - Depends on: T-01
  - Anchors: skills/spec-prototype/scripts/capture.mjs, agents/spec-prototype-builder.md, agents/spec-prototype-critic.md
  - Write scope: skills/spec-prototype/scripts/capture.mjs, skills/spec-prototype/references/02-craft-methods/craft-floor.md, skills/spec-prototype/references/03-verification/quality-floor.md, agents/spec-prototype-builder.md, agents/spec-prototype-critic.md
  - Verify with: python3 -m pytest -q tests/test_platform_craft_rules.py
  - Verify tier: unit

- [ ] T-06 Clean up excessive verifiers and align handoff toolchain
  - Depends on: T-05
  - Anchors: skills/spec-prototype/scripts/compile_tokens.py, skills/spec-prototype/scripts/wcag-check.js
  - Write scope: skills/spec-prototype/scripts/compile_tokens.py, skills/spec-prototype/scripts/wcag-check.js, skills/spec-prototype/CONTEXT.md, tests/test_skill_script_integrity.py
  - Verify with: python3 -m pytest -q tests/test_skill_script_integrity.py
  - Verify tier: unit

## 1. Intent-Sensitive Lifecycle & Routing

- [ ] T-01 Align SKILL.md and core-workflow.md with intent-sensitive routing
  - Depends on: none
  - Anchors: skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-workflow.md
  - Write scope: skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-workflow.md, skills/spec-prototype/references/04-governance/interpretation-rules.md
  - Verify with: python3 -m pytest tests/test_pipeline.py -k "test_archetype_routing_and_negative_triggers or test_canonical_5_stage_active_simulation_and_artifact_standards"
  - Implements: ENG-001
  - Proves: ENG-SCN-001
  Update `SKILL.md` and `core-workflow.md` so that the design engine selects its working route based on the requested outcome (exploration, new surface, local refinement, formal handoff) rather than forcing an unbroken 5-stage sequential gate. Ensure exploration allows revisable direction briefs without frozen contract deadlocks, new surfaces inherit existing assets, and formal handoff requires human signoff before freezing.

## 2. Builder & Critic Adaptive Contract

- [ ] T-02 Decouple Builder from universal turn limits and prescriptive chassis
  - Depends on: T-01
  - Anchors: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, skills/spec-prototype/scripts/capture.mjs
  - Write scope: agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, skills/spec-prototype/scripts/capture.mjs
  - Verify with: python3 -m pytest tests/test_pipeline.py -k "test_canonical_design_references_and_floors"
  - Implements: ENG-002
  - Proves: ENG-SCN-002
  Update `agents/spec-prototype-builder.md` to remove mandatory single-pass generation rules and global turn ceilings (treating turns as an execution-safety budget). Remove hardcoded `AppState` naming, fixed `Space/P/Esc` shortcuts, and fixed `scale(0.97)` styling, allowing Builder to implement the exact specification passed in the envelope. Align `capture.mjs` CLI arguments with builder invocation and report explicit failures on missing viewports.

## 3. Evidence-Led Feedback & Envelope Assembly

- [ ] T-03 Refactor envelope assembly for flexible exploration and truthful constraints
  - Depends on: T-02
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py, skills/spec-prototype/scripts/handoff.py
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, skills/spec-prototype/scripts/handoff.py
  - Verify with: python3 -m pytest tests/test_pipeline.py -k "test_handoff_packet_without_preexisting_html_and_template_surface_map or test_spec_first_contract_formulation_and_lean_envelope"
  - Implements: ENG-003
  - Proves: ENG-SCN-003
  Update `assemble_envelope.py` to support both exploration direction briefs and formal candidate specifications. Ensure envelope constraints reflect actual specification assertions without truncation or pre-filled aesthetic biases. Ensure `handoff.py` correctly distinguishes exploration from formal freeze manifests.

## 4. Generic Token Compiler & De-prescription

- [ ] T-04 Eliminate silent aesthetic defaults and fixed palettes in compile_tokens.py
  - Depends on: T-01
  - Anchors: skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Write scope: skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Verify with: python3 -m pytest tests/test_tokens.py
  - Implements: HAR-001
  - Proves: HAR-SCN-001
  Refactor `compile_tokens.py` so that it parses and compiles tokens explicitly declared in project inputs. Remove silent fallbacks to `plasma-cyan` / `obsidian-emerald` or hardcoded radius and spacing formulas when discussion inputs are absent, reporting missing values as unknown or uncompiled rather than manufacturing synthetic aesthetic choices. Update `tests/test_tokens.py` to assert truthful compilation.

## 5. Truthful Verification & Review Portal

- [ ] T-05 Replace keyword sniffing with contract assertions and generic materialization
  - Depends on: T-03, T-04
  - Anchors: skills/spec-prototype/scripts/verify_prototype_quality.py, skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/generate_review_portal.py, tests/test_pipeline.py
  - Write scope: skills/spec-prototype/scripts/verify_prototype_quality.py, skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/generate_review_portal.py, tests/test_pipeline.py
  - Verify with: python3 -m pytest tests/test_pipeline.py
  - Implements: HAR-002
  - Proves: HAR-SCN-002
  Refactor `verify_prototype_quality.py` to assert observable DOM elements, event bindings, and declared contract items rather than looking for hardcoded template keywords (`MAS-ORCHESTRATOR`, `DAG-FANOUT-04`, `scale(0.9`). Refactor `materialize_contracts.py` to compile actual discussion/product inputs without hardcoded GPU cluster domain strings or pre-filled `Observed: pass`. Update `generate_review_portal.py` to accurately reflect verified vs unverified states. Update `tests/test_pipeline.py` to validate truthful reporting.

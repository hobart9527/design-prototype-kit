# Tasks: Optimize Startup Payload and Stage-based Progressive Disclosure

- [ ] T-01 Create modular stage references under references/stages/
  - Depends on: none
  - Anchors: skills/spec-prototype/references/stages/, skills/spec-prototype/references/core-workflow.md
  - Write scope: skills/spec-prototype/references/stages/
  - Verify with: python3 -m pytest tests/test_pipeline.py

- [ ] T-02 Refactor SKILL.md for progressive disclosure routing and harmonize builder invariants
  - Depends on: T-01
  - Anchors: skills/spec-prototype/SKILL.md, agents/spec-prototype-builder.md, skills/spec-prototype/references/core-workflow.md
  - Write scope: skills/spec-prototype/SKILL.md, agents/spec-prototype-builder.md, skills/spec-prototype/references/core-workflow.md
  - Verify with: python3 -m pytest tests/test_v10_integrity.py tests/test_design_chain_continuity.py tests/test_pipeline.py tests/test_prototype_coverage.py tests/test_canonical_ontology.py

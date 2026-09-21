# Tasks: Optimize Startup Payload via 5-Layer Progressive Disclosure

- [x] T-01 Author modular stage references under references/stages/
  - Depends on: none
  - Anchors: skills/spec-prototype/references/stages/, skills/spec-prototype/references/core-workflow.md, skills/spec-prototype/references/03-verification/quality-floor.md
  - Write scope: skills/spec-prototype/references/stages/
  - Verify with: python3 -m pytest tests/test_pipeline.py

- [x] T-02 Establish core-kernel, refactor SKILL.md router, and harmonize builder invariants
  - Depends on: T-01
  - Anchors: skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-kernel.md, skills/spec-prototype/references/core-workflow.md, agents/spec-prototype-builder.md
  - Write scope: skills/spec-prototype/SKILL.md, skills/spec-prototype/references/core-kernel.md, skills/spec-prototype/references/core-workflow.md, agents/spec-prototype-builder.md
  - Verify with: python3 -m pytest tests/test_v10_integrity.py tests/test_design_chain_continuity.py tests/test_pipeline.py tests/test_prototype_coverage.py tests/test_canonical_ontology.py

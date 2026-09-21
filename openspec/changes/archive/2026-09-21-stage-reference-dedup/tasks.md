# Tasks: Stage Reference Deduplication and Runtime Contract Alignment

- [x] T-01 Purify stage procedures and align runtime inspection contracts
  - Depends on: none
  - Anchors: skills/spec-prototype/references/stages/stage-1-frame.md, skills/spec-prototype/references/stages/stage-2-probe.md, skills/spec-prototype/references/stages/stage-3-skeleton.md, skills/spec-prototype/references/stages/stage-4-audit.md
  - Write scope: skills/spec-prototype/references/stages/
  - Verify with: python3 -m pytest tests/test_pipeline.py

- [x] T-02 Streamline core-workflow into a lean router delegating stage bodies
  - Depends on: T-01
  - Anchors: skills/spec-prototype/references/core-workflow.md
  - Write scope: skills/spec-prototype/references/core-workflow.md
  - Verify with: python3 -m pytest tests/test_v10_integrity.py tests/test_design_chain_continuity.py tests/test_pipeline.py tests/test_prototype_coverage.py tests/test_canonical_ontology.py

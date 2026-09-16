## 1. Design Token DTCG Export Tooling

- [ ] T-01 Restore and enhance `export-tokens.py` script to parse design tokens (including two-column breakpoint tables and multi-column semantic scales) and export valid W3C DTCG format
  - Depends on: none
  - Implements: HAR-001
  - Proves: HAR-SCN-001
  - Anchors: tests/test_tokens.py, skills/spec-prototype/scripts/export-tokens.py
  - Write scope: skills/spec-prototype/scripts/export-tokens.py
  - Verify with: python3 -m pytest tests/test_tokens.py -q

## 2. Pipeline Verification Harness and Execution Boundary

- [ ] T-02 Restore and verify pipeline verification scripts (`handoff.py`, `check-assertions.py`, `execution_boundary.py`) to satisfy exact assertion evaluation and boundary checks
  - Depends on: none
  - Implements: HAR-002
  - Proves: HAR-SCN-002
  - Anchors: tests/test_pipeline.py, skills/spec-prototype/scripts/handoff.py, skills/spec-prototype/scripts/check-assertions.py, skills/spec-prototype/scripts/execution_boundary.py
  - Write scope: skills/spec-prototype/scripts/handoff.py, skills/spec-prototype/scripts/check-assertions.py, skills/spec-prototype/scripts/execution_boundary.py
  - Verify with: python3 -m pytest tests/test_pipeline.py -q

## 3. Canonical 5-Stage Lifecycle and Kinetics Alignment

- [ ] T-03 Formalize the canonical 5-stage lifecycle (魂、骨、皮、根、鉴), physical-world kinetics (`cubic-bezier(0.16, 1, 0.3, 1)`, `:active { transform: scale(0.97); }`, `44x44px`), and five experience states in core workflow references and builder contracts
  - Depends on: none
  - Implements: ENG-001, ENG-002, ENG-003
  - Proves: ENG-SCN-001, ENG-SCN-002, ENG-SCN-003
  - Anchors: agents/spec-prototype-builder.md, skills/spec-prototype/references/core-workflow.md
  - Write scope: agents/spec-prototype-builder.md, skills/spec-prototype/references/core-workflow.md
  - Verify with: python3 -c "from pathlib import Path; b = Path('agents/spec-prototype-builder.md').read_text(); assert 'cubic-bezier' in b and 'min-h-[44px]' in b and 'Loading, Empty, Partial, Error, and Overflow' in b; c = Path('skills/spec-prototype/references/core-workflow.md').read_text(); assert 'Phase 1' in c and 'Phase 2' in c and 'Phase 3' in c and 'Phase 4' in c and '5.' in c; print('OK')"

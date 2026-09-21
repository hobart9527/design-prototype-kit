# Proposal: Stage Reference Deduplication and Runtime Contract Alignment

## Why

Following the establishment of `core-kernel.md` and modular `references/stages/`, the design kit suffers from dual authority and reference drift:
1. `core-workflow.md` (369 lines) still retains full, verbose stage bodies for Stage 1–5, duplicating `references/stages/*.md` (451 lines) and creating conflicting parallel authorities.
2. `stage-2-probe.md` and `stage-4-audit.md` mention hardcoded static viewports (1280px + 390px, 1600px), drifting from the runtime platform-aware adaptive viewports (`inspection_contract.mandatory_viewports`).
3. `stage-1-frame.md` introduced the generalized `Design Driver` model but still dogmatically demanded mandatory `Core Tension` declaration.
4. `stage-2-probe.md` and `stage-3-skeleton.md` embed prescriptive craft parameters (4px/8px/44px, dead-gray bans, compression metrics) that belong in `02-craft-methods/` and `03-verification/quality-floor.md`, violating the principle that Stage documents define procedure rather than design craft templates.

## What Changes

1. **Shrink `core-workflow.md` to a Pure Shared Flow Router**:
   - Strip verbose stage bodies from `core-workflow.md`. Retain the macro canonical architecture, Change Scope Router, Coverage Selection before Stage 3, and craft reference index.
   - Under each stage heading (`### Stage 1: Understand & Frame`, `### Stage 2: Core Hero Anchor Prototyping...`, `### Stage 3: Full IA Surface Rollout`, `### Stage 4: Holistic Review...`, `### Stage 5: Silent Governance...`), replace the body with a concise summary and an explicit delegation link to `stages/stage-X-*.md`.
2. **Purify Stage Procedures (`references/stages/*.md`)**:
   - `stage-1-frame.md`: Align the Discover phase to honor the full `Design Driver` hierarchy (`tension`, `constraint`, `failure mode`, `opportunity`, `uncertainty`), removing dogmatic single-tension requirements.
   - `stage-2-probe.md`: Remove prescriptive craft numbers (4px, 8px, 44px, color hex bans) and delegate craft techniques to `../02-craft-methods/` and `../03-verification/quality-floor.md`. Replace hardcoded viewport requirements with `inspection_contract.mandatory_viewports`.
   - `stage-3-skeleton.md`: Focus strictly on Coverage Selection, Surface Expansion, and obligation reconciliation; delegate micro-metrics and layout styling to craft methods.
   - `stage-4-audit.md`: Replace static viewport lists with runtime `inspection_contract.mandatory_viewports` and declared states; reference `quality-floor.md` for quality gates.
3. **Preserve All Test Invariants**:
   - Maintain all exact heading sequences, term declarations, and link integrity required by `test_v10_integrity.py`, `test_design_chain_continuity.py`, `test_pipeline.py`, `test_prototype_coverage.py`, and `test_canonical_ontology.py`.

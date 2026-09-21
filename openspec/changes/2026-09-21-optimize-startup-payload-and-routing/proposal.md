# Proposal: Optimize Startup Payload and Stage-based Progressive Disclosure

## Why

The current `spec-prototype` skill incurs a severe token and latency penalty at startup:
1. `SKILL.md` (138 lines, ~13.5KB) unconditionally mandates: `"Before any substantive design answer or action, read [the shared product-design core](references/core-workflow.md) completely"`. Reading `core-workflow.md` (368 lines, ~36.2KB) injects ~50KB (~12,000+ tokens) into the context window before any design inquiry is even formulated.
2. Even for a lightweight intent such as `Explore` (seeking a direction probe or discussing an idea) or L0/L1 scope tweaks, the agent is forced to ingest the full 5-stage engine, Nine Pillars, walking skeleton rollout, 4-dimensional audit gates, and silent freeze packaging.
3. Backend governance and compilation tooling (`assemble_envelope.py`, `capture.mjs`, `verify_prototype_quality.py`, `handoff.py`) are detailed upfront in `SKILL.md`, burdening early design reasoning with execution details relevant only to Stage 2, 4, or 5.

## What Changes

1. **Progressive Disclosure Intent Router**:
   - Replace the unconditional upfront `core-workflow.md` reading directive in `SKILL.md` with an intent-driven routing table.
   - Instruct the agent to read only the specific stage reference matching active intent and stage:
     - `Explore`: loads `references/stages/stage-0-explore.md` (direction probe, falsifiable hypothesis, no-build discussion rules).
     - `Stage 1 (破)`: loads `references/stages/stage-1-frame.md` (Nine Pillars, OOUX, Surface Topology, sealed provisional contract formulation).
     - `Stage 2 (立)`: loads `references/stages/stage-2-probe.md` and `references/04-governance/execution-boundary.md` (hero probe, lean envelope assembly, builder dispatch).
     - `Stage 3 (拓)`: loads `references/stages/stage-3-skeleton.md` (Coverage Selection, surface expansion, walking skeleton).
     - `Stage 4 (验)`: loads `references/stages/stage-4-review.md` (Four-Dimensional Evidence, `capture.mjs`, `verify_prototype_quality.py`, critic dispatch).
     - `Stage 5 (冻)`: loads `references/stages/stage-5-freeze.md` (token export, WCAG 2.2 AA check, `handoff.py` freeze).
   - Retain `core-workflow.md` as the authoritative global design reference, accessible on demand rather than on every invocation.

2. **Modular Stage References (`references/stages/`)**:
   - Create `references/stages/stage-0-explore.md` through `stage-5-freeze.md`, encapsulating stage objectives, inputs/outputs, craft guidelines, and execution recipes.
   - Move script invocation commands (`assemble_envelope.py`, `capture.mjs`, `verify_prototype_quality.py`, `handoff.py`) into their respective stage references, deferring governance mechanics until their actual execution stage.

3. **Slim `SKILL.md`**:
   - Keep `SKILL.md` focused on entry intent routing, negative trigger boundary, canonical architecture overview, storage discipline, and native role boundaries.
   - Ensure all invariant contracts (`Draft → Sealed Provisional → Validated → Frozen Approved`, Coverage Selection rules, zero broken markdown links) remain strictly intact.

4. **Reconcile Builder Prompt Invariant**:
   - Restore "Do not turn an axis into a fixed pixel checklist" in `agents/spec-prototype-builder.md` so that sensory dial calibration and ontology invariants are harmonized.

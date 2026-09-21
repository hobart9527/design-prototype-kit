# Proposal: Optimize Startup Payload via 5-Layer Progressive Disclosure

## Why

The current `spec-prototype` skill incurs a severe startup latency and token tax:
1. `SKILL.md` unconditionally mandates reading `references/core-workflow.md` completely, dumping ~50KB (~12,000+ tokens) into the context window before any design intent is classified.
2. Lightweight requests (`Explore`, direction probes, L0/L1 scope adjustments) are forced to ingest the entire 5-stage engine, full craft methods, and headless governance machinery.
3. Over time, `core-workflow.md` has accumulated process logic, craft guidelines, governance scripts, and stage instructions, creating cognitive friction and overlapping authority.

## What Changes (5-Layer Modular Architecture)

We refactor the skill documentation from a monolithic manual into a clean, 5-layer progressive disclosure architecture without adding redundant methodology or inflating markdown volume:

### 1. Layer Responsibilities (Answer Only One Question Per Layer)
- **Layer 1: Thin Router (`SKILL.md`)** — *"Which route do I take right now?"*
  - Entry intent classification (`Explore`, `Specify`, `Prototype`, `Review/Repair`), negative trigger boundary, storage discipline, and pointer to stage references.
  - Removes the unconditional upfront read of `core-workflow.md`.
- **Layer 2: Small Kernel (`references/core-kernel.md` / `references/core-workflow.md`)** — *"What must never be violated under any circumstance?"*
  - Spec as durable contract, prototype as disposable proof.
  - Authority lifecycle (`Draft → Sealed Provisional → Validated → Frozen Approved`).
  - Evidence protocol (`explicit > observed > derived > hypothesis > unknown`), semantic preservation, and non-negotiable experience invariants.
- **Layer 3: Stage Procedures (`references/stages/*.md`)** — *"How does this specific stage operate?"*
  - `stage-0-explore.md`: Direction probes, falsifiable brief, lightweight exploration, no-build discussion rules.
  - `stage-1-frame.md`: Understand & Frame, multi-dimensional **Design Driver** (`tension`, `constraint`, `failure mode`, `opportunity`, `uncertainty`), OOUX entities, Surface Topology, and sealed provisional contract formulation.
  - `stage-2-probe.md`: Proposition & Hero Probe via **Canonical Executable IR** and Lean Builder Payload dispatch (`materialize` → `compile` → `assemble lean payload` → `dispatch builder`). Legacy envelope projections are noted as debug-only.
  - `stage-3-skeleton.md`: Walking skeleton rollout, Coverage Selection before expansion, and multi-surface task continuity.
  - `stage-4-audit.md`: Runtime, visual, interaction, and semantic audit procedure; headless capture, static verification, Critic dispatch, and surgical in-place targeted refinement. References `03-verification/quality-floor.md` rather than duplicating it.
  - `stage-5-freeze.md`: Silent governance & handoff — final token reconciliation, DTCG authority validation, SHA-256 asset identity binding, and freeze manifest.
- **Layer 4: Domain Knowledge & Floors (`references/01/`, `02/`, `03/`)** — *"What craft techniques and quality floors apply?"*
  - Retain `03-verification/quality-floor.md` and evidence semantics as cross-cutting invariants across Stage 2–5.
  - Stages cite 01/02/03 knowledge modules on demand; stages never copy-paste floor rules.
- **Layer 5: Governance Rules (`references/04-governance/`)** — *"How are permissions, lifecycles, and execution boundaries enforced?"*
  - Host execution boundaries, role separation, discussion index discipline, and artifact handoff.

### 2. Builder & Critic Invariant Harmonization
- Harmonize `agents/spec-prototype-builder.md` so that sensory dial calibration explicitly retains the non-prescriptive rule: `"Do not turn an axis into a fixed pixel checklist"`.

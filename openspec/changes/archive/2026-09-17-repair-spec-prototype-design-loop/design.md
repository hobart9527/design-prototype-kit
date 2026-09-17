## Context

See proposal.md - Why.
The Skill's existing scripts and instructions suffer from four architectural fractures:
1. `SKILL.md` and `core-workflow.md` enforce an unbroken 5-stage cascade with a single-pass <= 8 turn limit, conflicting with the iterative Exploration Track and adaptive stop rules.
2. `assemble_envelope.py` hardcodes 5 stage-1 files, rigid constraints, and truncates assertions, preventing flexible exploration briefs.
3. `materialize_contracts.py` hardcodes a GPU cluster domain, pre-filling assertions with `pass` and manufacturing synthetic decisions instead of compiling actual project inputs.
4. `verify_prototype_quality.py` and `generate_review_portal.py` rely on keyword sniffing and hardcoded `VERIFIED [DECISIVE 3-FRAME]` banners, creating a false quality floor.

## Goals / Non-Goals

**Goals:**
- Unify `SKILL.md` and `core-workflow.md` to support route selection (Exploration, New Surface, Local Refinement, Formal Handoff) with clear entry/exit criteria.
- Decouple Builder from single-pass <= 8 turn restrictions, enabling an authentic render-read-repair-reverify loop while keeping turn budgets as execution-safety guards.
- Eliminate domain-specific hardcoding (GPU cluster, H100, NVLink) and pre-filled `pass` results from generic helpers (`materialize_contracts.py`, `verify_prototype_quality.py`).
- Make verification assertions truthful: separate static syntax/DOM checks, browser execution, and visual review; report unverified states accurately.
- Update tests in `tests/test_pipeline.py` and `tests/test_tokens.py` to assert truthful generic behavior and negative validation branches.

**Non-Goals:**
- Re-architecting or re-rendering the GPU prototype (`prototype/experiments/console`).
- Creating compulsory layout scaffolds or imposing universal aesthetic thresholds (radii, typography, density).
- Modifying Loom Runtime or OpenSpec engine infrastructure.

## Decisions

### Decision 1: Intent-Sensitive Lifecycle Routing over Universal 5-Stage Gate
- *Approach*: Route requests by task type:
  - `exploration`: Bounded brief, representative probe, revisable records, no frozen contract deadlock.
  - `new-surface`: Inherit existing tokens/chassis, expand surface map, validate integrated journey.
  - `refinement`: Target minimal owning abstraction, in-place delta, surgical regression check.
  - `formal-handoff`: Explicit freezing via `handoff.py freeze` after human signoff.
- *Alternatives considered*: Keep mandatory 5-stage gate with bypass flags (rejected: encourages evasion and rule drift).

### Decision 2: Truthful Verification Harness over Keyword Sniffing
- *Approach*: Refactor `verify_prototype_quality.py` to evaluate only observable DOM/token contracts declared in the incoming specification/envelope. Remove hardcoded entity signatures (`MAS-ORCHESTRATOR`, `DAG-FANOUT-04`) and aesthetic checks (`scale(0.9`, fixed class names).
- *Alternatives considered*: Add AST parsing for layout aesthetic linting (rejected: aesthetic linting cannot substitute for human visual judgment and creates new evasion hacks).

### Decision 3: Spec-Driven Contract Materialization over Domain Hardcoding
- *Approach*: Refactor `materialize_contracts.py` to extract domain objects, actions, and constraints directly from `discussion.md` and `product.md`. If required inputs are absent, leave them explicit or report missing requirements rather than synthesizing GPU cluster data or pre-filling `Observed: pass`.
- *Alternatives considered*: Remove `materialize_contracts.py` entirely (rejected: helper script is useful when compiling user discussion into structured contracts).

## Risks / Trade-offs

- [Risk] Existing tests expecting GPU cluster strings in pipeline assertions may fail.
  → *Mitigation*: Update `tests/test_pipeline.py` to assert generic contract structures and add dedicated unit tests for cross-domain inputs.
- [Risk] Removing the single-pass <= 8 turn ceiling could cause Builder agents to loop indefinitely.
  → *Mitigation*: Retain a bounded tool turn safety budget (e.g. max 12 turns) with explicit stopping conditions: report unverified and halt when budget is exhausted.

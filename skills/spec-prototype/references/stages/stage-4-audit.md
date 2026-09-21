# Stage 4: Holistic Review & In-Place Tuning (验 - 鉴)

Answer one question: *"Does the delivered prototype close every floor with
transparent evidence?"* Stage 4 runs decoupled audits across engineering,
interaction, visual, and human dimensions.

## Unified Review Portal

Run `python3 skills/spec-prototype/scripts/generate_review_portal.py` to produce a
panoramic multi-viewport review board (`review-portal.html`) embedding every page
iframe, viewport switching over the runtime-derived
`inspection_contract.mandatory_viewports`, and the authored interaction state
triggers (`inspection_contract.mandatory_states`). The viewport set is never a
hardcoded list.

## Decisive Exchange 3-Frame Inspection

Audit the three-frame continuous evolution of core decisive interactions:

- `Intent`: clear intent perception on hover or focus activation.
- `Detent`: pronounced physical damping, elastic press, or instantaneous feedback on trigger.
- `Settled`: explicit state settlement, focus restoration, and steady finish.

## Decoupled Four-Dimensional Evidence

### Track A: Engineering DOM & Token Floor
Run `verify_prototype_quality.py` to confirm 100% token inheritance, no inline
hex, zero destructive overflow, and viewport fold integrity.

### Track B: Interaction & Stress Floor (The Break Protocol)
Inject destructive limit tests: extreme long-string truncation, zero state
(first-use guidance), and extreme-value scroll containment. Walk the Reachable-
Control Closure: every visible key action (cancel, close, retry, reset) must be
usable; no dead controls.

### Track C: Renderer Capture Status
Capture real render viewports via `capture.mjs`. Keep evidence and approval
decoupled: `renderer: captured` never automatically equals `visual: verified`.

### Track D: Ergonomic & Human Verification
- *Dual-Channel Affordance (Floor)*: every shortcut or gesture has a corresponding visible GUI control.
- *Zero Metaphor Contamination (Floor)*: core entities use real business vocabulary; skeuomorphic metaphor never takes over.
- *Domain-Specific Craft Heuristics*: the B-Pro 5-Second Test for operational/engineering scenes, and the C-Consumer Somatic Test for consumer/touch scenes.
- *Human Gate & Delegation-Aware Protocol*: when the user has granted full design delegation (`delegated`) or pre-agreed acceptance criteria, proceed automatically on test assertions and captured evidence. Pause only for irreversible divergence, a serious experience regression (floor failure), or a genuinely new business fork.

All floor definitions live in
[`../03-verification/quality-floor.md`](../03-verification/quality-floor.md);
this module cites them and never copies floor rules.

## Controlled Feedback Absorption & Targeted Refinement Loop

- **Zero Full-Wipeout Rule**: a Critic finding never triggers indiscriminate
  global rebuild. Locate the defect precisely to its Pillar and Artifact, and
  preserve unaffected decisions.
- **Targeted Refinement Contract**: the Critic must emit an explicit repair
  boundary:

  ```yaml
  finding:
    pillar: Attention | Interaction | Expression | Resilience
    layer: visual_hierarchy | visual_composition | typography | state_transition
    scope: screen.slice_id.component_target
    severity: major | minor | preference
    classification: VIOLATION | DEFECT | DESIGN JUDGMENT
  action: targeted_repair
  return_to: Stage 2 (probe) | Stage 3 (skeleton) | Stage 4 (tuning)
  invalidate:
    - visual_hierarchy
  preserve:
    - object_model
    - topology
    - state_matrix
    - token_bindings
  ```

- **Surgical In-Place Patching**:
  - Global visual and rhythm feedback flows back to
    `prototype/contracts/foundation/f1.md` / `discussion.md` and is recompiled
    through `compile_tokens.py` into `prototype/shared/tokens.css`; island
    overrides are forbidden.
  - Page-local structural or micro-interaction defects are fixed directly in the
    owning HTML slice.
  - After repair, rerun automated verification and multi-viewport review until
    every floor closes.

## Independent Critic Checkpoint

The Critic recommends and identifies the owning decision; it does not approve.
Apply feedback to the smallest owner, preserve unaffected decisions, and rerun
affected checks only.

## Exit

Legal exit is a validated contract set plus an audit report or patched slice
(`review-only`). Proceed to [Stage 5](stage-5-freeze.md) only when floors and
evidence pass.

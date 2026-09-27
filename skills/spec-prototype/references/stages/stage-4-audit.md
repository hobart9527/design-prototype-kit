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

> **Completion Receipt Discipline (完成终态与修复预算)**:
> The Builder's delivery receipt is authoritative once it reports `STATIC: pass`
> with capture paths — do NOT re-run the same verify in the main session just to
> confirm a receipt that already names a passing verdict. If L1 verify fails:
> allow AT MOST ONE targeted repair round (fix the exact failed assertion, then
> re-verify once). If it still fails, record the outcome in
> `prototype/discussion.md`'s Resume block as `Stage 4: PARTIAL — <findings>`
> and END the session normally. A session must never run out the wall clock in
> an open-ended self-repair loop: a sealed PARTIAL state with honest findings is
> a valid terminal state; a timeout is not.

### Track B: Interaction & Stress Floor (The Break Protocol)
Inject destructive limit tests: extreme long-string truncation, zero state
(first-use guidance), and extreme-value scroll containment. Walk the Reachable-
Control Closure: every visible key action (cancel, close, retry, reset) must be
usable; no dead controls.

### Track C: Renderer Capture Status
Capture real render viewports via `capture.mjs`. Keep evidence and approval
decoupled: `renderer: captured` never automatically equals `visual: verified`.

> **Visual Inspection Token Hygiene (视觉审查 Token 节制)**:
> Automated static verify (`verify_prototype_quality.py`) is primary and non-negotiable.
> NEVER use the `Read` tool to batch-read multiple full-resolution PNG screenshots into the LLM context.
> Multiple base64 images cause immediate context bloat (15k-25k tokens per image) and budget exhaustion.
> If a visual sanity check is necessary, inspect AT MOST 1 key screenshot (e.g. the 390px mobile view or the core hero state).

### Track D: Ergonomic & Human Verification
- *Dual-Channel Affordance (Floor)*: every shortcut or gesture has a corresponding visible GUI control.
- *Zero Metaphor Contamination (Floor)*: core entities use real business vocabulary; skeuomorphic metaphor never takes over.
- *Task-Fit Craft Heuristics (advisory)*: choose the probe the task implies, not the audience label — a 5-second recognition test where the person must read state at a glance, a somatic walk-through where direct touch handling carries the task. Report misses as craft findings, not floor failures.
- *Human Gate & Delegation-Aware Protocol*: when the user has granted full design delegation (`delegated`) or pre-agreed acceptance criteria, proceed automatically on test assertions and captured evidence. Pause only for irreversible divergence, a serious experience regression (floor failure), or a genuinely new business fork.

### Critic Dispatch Discipline (Critic 必达)
When the prototype is captured and verify is pass (or sealed `PARTIAL`), dispatch
`spec-prototype-critic` in the SAME turn — do not defer it behind further
tuning. A session that ends with a captured prototype but no critic judgment
has not completed Stage 4; record `Stage 4: PARTIAL — critic not dispatched` in
the Resume block if the budget truly cannot cover it. In automated sessions,
reserve roughly one per-call budget ($8) for the critic before spending on
cosmetic re-tuning: independent review closes the evidence loop; a prettier
screenshot without review does not.

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
    `prototype/discussion.md` (the single decision authority) and is recompiled
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

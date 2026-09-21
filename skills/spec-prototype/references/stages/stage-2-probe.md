# Stage 2: Proposition & Hero Probe (立 - 核心主交互原型物化)

Answer one question: *"Does the sealed provisional Spec survive contact with a
real, running Hero Anchor?"* Stage 2 materializes the single highest-risk core
surface or direction probe under the Stage 1 sealed provisional contracts.

## Adaptive Hero Anchor Chassis

Stage 2 refuses one templated doctrine. The core prototype adapts its chassis to
the Stage 1 product context:

1. *Dense Workbench Pattern*: high-density data bench — 4px micro-grid, multi-pane instrumentation, monospaced numerics.
2. *Operational Canvas Pattern*: business board — 8px rhythm, master-detail hierarchy, progressive disclosure.
3. *Editorial Reading Pattern*: immersive text — character-measure control, quiet margins, paper contrast.
4. *Somatic Touchflow Pattern*: mobile touch — 44px thumb-zone targets, fluid curves, high responsiveness.
5. *Adaptive Workspace Pattern*: adaptive workspace — compose space to the unique business model.

## Canonical Executable IR & Lean Builder Payload

The dispatch path is IR-first. The Coordinator runs the canonical pipeline before
dispatching `spec-prototype-builder`:

1. `materialize` — compile the Stage 1 discussions into structured contracts
   (`materialize_contracts.py`).
2. `compile` — derive physical tokens from the Five-Axis register
   (`compile_tokens.py` → `tokens.css` / `t1.json` / `t1.md`).
3. `assemble lean payload` — assemble the pre-baked Lean Builder Envelope
   (`assemble_envelope.py`), carrying the constraint set, the authored creative
   space, and the retained spec digests.
4. `dispatch builder` — hand the lean payload to `spec-prototype-builder`.

Legacy envelope projections (`envelope.json` dual-envelope form) are retained for
diagnostics and debugging only; the lean payload is the production dispatch route.
See [`../04-governance/execution-boundary.md`](../04-governance/execution-boundary.md)
for the dispatch admission rules.

## Bounded Builder Execution

The Builder is strictly constrained by the payload:

- Step 1: author one self-contained HTML/CSS/JS page (`experiments/.../hero-anchor/index.html`).
- Step 2: run `python3 skills/spec-prototype/scripts/verify_prototype_quality.py`.
- Step 3: capture real viewport evidence via `node skills/spec-prototype/scripts/capture.mjs`.
- Step 4: return the delivery receipt. One dispatch retains at most two local
  self-repair attempts. Unbounded filesystem roaming and CSS ping-pong tuning are
  forbidden.

## Design Engineering Floor & Candidate Techniques

Craft serves the experience invariants and is selected by scenario:

- **Concentric Border Radius**: nested containers follow $R_{inner} = \max(0, R_{outer} - padding)$.
- **Optical Alignment**: manually offset asymmetric glyphs (play triangle, chevron, magnifier) 1-2px from geometric center for visual balance.
- **Tabular Numerics**: counters, telemetry, and financial figures use `font-variant-numeric: tabular-nums` to stop horizontal jitter.
- **Atmospheric Undertone**: pure dead gray (`#808080`) is forbidden; inject a subtle ambient cast.

Full floors live in [`../03-verification/quality-floor.md`](../03-verification/quality-floor.md);
this module cites them and never restates them.

## Native-First vs Production Handoff

The prototype stays zero-build and immediately runnable, preferring native HTML5
semantics (`<dialog>`, `<details>`, `<form>`) and CSS custom properties. Complex
frontend componentization (React/Vue/shadcn, state libraries) is strictly reserved
for downstream Loom Entry 2 engineering delivery.

## Stage 2 Anchor Approval Gate

Once the first surface is materialized, present real viewport screenshots (1280px
desktop and 390px mobile). Only after the user confirms the visual tone and token
base may later surfaces expand.

## Exit

Legal exit is a runnable Hero Anchor plus its captured evidence. Continue to
[Stage 3](stage-3-skeleton.md) for full rollout, or return to Stage 1 when the
probe falsifies an upstream contract.

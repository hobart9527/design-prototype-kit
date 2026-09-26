# Stage 2: Proposition & Hero Probe (立 - 核心主交互原型物化)

Answer one question: *"Does the sealed provisional Spec survive contact with a
real, running Hero Anchor?"* Stage 2 materializes the single highest-risk core
surface or direction probe under the Stage 1 sealed provisional contracts.

## Adaptive Hero Anchor Chassis

Stage 2 refuses one templated doctrine. The core prototype adapts its chassis to
the Stage 1 product context:

1. *Dense Workbench Pattern*: high-density data bench — micro-grid rhythm, multi-pane instrumentation, monospaced numerics.
2. *Operational Canvas Pattern*: business board — structural rhythm, master-detail hierarchy, progressive disclosure.
3. *Editorial Reading Pattern*: immersive text — character-measure control, quiet margins, paper contrast.
4. *Somatic Touchflow Pattern*: mobile touch — thumb-zone targets, fluid curves, high responsiveness.
5. *Adaptive Workspace Pattern*: adaptive workspace — compose space to the unique business model.

The numeric grid, rhythm, and touch-target parameters behind each pattern are
owned by [`../02-craft-methods/visual-craft.md`](../02-craft-methods/visual-craft.md)
and [`../03-verification/quality-floor.md`](../03-verification/quality-floor.md);
this stage selects a chassis and never restates the numbers.

## Canonical Executable IR & Lean Builder Envelope Architecture

The dispatch path is IR-first and uses the canonical Dual-Envelope Architecture (`mode: "lean-builder-envelope"`). The Coordinator runs the canonical pipeline before dispatching `spec-prototype-builder`:

1. `compile_spec_ir` — compile the Stage 1 discussions into the canonical machine
   IR (`r1.spec.json`) plus the single-file human RFC view (`r1.spec.md`)
   (`compile_spec_ir.py`). Legacy compatibility only: `materialize_contracts.py`
   still emits the multi-file `c1.md` / `r1.md` set.
2. `compile` — derive physical tokens from the Five-Axis register
   (`compile_tokens.py` → `tokens.css` / `t1.json`; `t1.md` is legacy-only).
3. `assemble lean payload` — assemble the pre-baked Lean Builder Envelope
   (`assemble_envelope.py`), synthesizing the 7-field Executable Design IR alongside the decoupled `constraint_envelope` (binding invariants) and `creative_envelope` (agency parameters).
4. `dispatch builder` — pass the synthesized envelope JSON directly to `spec-prototype-builder`.

**Dispatch Closure Invariant (派发闭环纪律)**: a Builder dispatch is not
interruptible conversation — never yield the turn while the Builder is pending.
After the Agent call returns, immediately verify the receipt: the hero-anchor
HTML file exists at the payload's declared path and the verification scripts ran.
If the Builder result is missing or empty, retry the dispatch once within the
same turn; do not end the turn with a status message like "等待构建完成" (waiting
for the build). A turn may only close after the probe artifact exists on disk or
the dispatch has irreversibly failed and the failure is recorded in
`prototype/discussion.md`.

### Envelope Semantic Contract (Constraint vs Creative)
The synthesized envelope strictly enforces the separation of non-negotiable constraints from layout creativity:
- **`constraint_envelope` (Binding Invariants · 绝不妥协)**:
  - `domain_thesis`: Product thesis and authentic core tension.
  - `ooux_topology`: Object entity boundaries and cardinality constraints.
  - `interaction_spec`: Exact Action Verb Lifecycle, state machine hooks, and required shortcut affordances.
  - `fault_tolerance_protocol`: The Break Protocol stress floors (extreme strings, empty state recovery, 320px fold).
  - `token_stylesheet_ref` & `a11y_floors`: 100% token inheritance, zero inline hex, WCAG 2.2 AA contrast.
- **`creative_envelope` (Creative Agency · 创意空间)**:
  - Layout composition within the chosen chassis (workbench / canvas / reading / touchflow).
  - Spatial padding rhythm, typographic ladder contrast, and container elevation subtlety.
  - Micro-interactions, transient hover detents, and spring deceleration curves within token bounds.
- **Legacy Envelope Notice**: Legacy single-contract projections without the 7-field IR are retained for backward-compatibility diagnostics only; `mode: "lean-builder-envelope"` emitted by `assemble_envelope.py` is the sole production dispatch format.
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

## Design Engineering Floor

Craft serves the experience invariants and is selected by scenario. The craft
techniques and their numeric parameters — concentric radii, optical alignment,
tabular numerics, atmospheric undertone — are owned by
[`../02-craft-methods/visual-craft.md`](../02-craft-methods/visual-craft.md), and
the binding floors live in
[`../03-verification/quality-floor.md`](../03-verification/quality-floor.md).
This stage cites those authorities and never restates their numbers.

## Native-First vs Production Handoff

The prototype stays zero-build and immediately runnable, preferring native HTML5
semantics (`<dialog>`, `<details>`, `<form>`) and CSS custom properties. Complex
frontend componentization (React/Vue/shadcn, state libraries) is strictly reserved
for downstream Loom Entry 2 engineering delivery.

## Stage 2 Anchor Approval Gate

Once the first surface is materialized, present real viewport screenshots at the
runtime-derived `inspection_contract.mandatory_viewports` carried by the assembled
payload — never a hardcoded viewport list. Only after the user confirms the visual
tone and token base may later surfaces expand.

## Exit

Legal exit is a runnable Hero Anchor plus its captured evidence. Continue to
[Stage 3](stage-3-skeleton.md) for full rollout, or return to Stage 1 when the
probe falsifies an upstream contract.

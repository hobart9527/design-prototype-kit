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

## Canonical Executable IR & Direct Materialization (单脑贯通)

The path is IR-first and the main designer executes it end-to-end. No external
agent sits between the contract and the artifact:

1. `compile_spec_ir` — compile the Stage 1 discussions into the canonical machine
   IR (`r1.spec.json`) plus the single-file human RFC view (`r1.spec.md`)
   (`compile_spec_ir.py`). Never call `materialize_contracts.py` or write legacy multi-file
   contracts (`f1.md`, `m1.md`, `t1.md`, `c1.md`, `r1.md`).
2. `compile` — derive physical tokens from the Five Axes register
   (`compile_tokens.py` → `tokens.css` / `t1.json`).
3. `author` — write the Hero Anchor directly at
   `prototype/experiments/<slice_id>/anchor/index.html`, consuming the compiled
   tokens. `assemble_envelope.py` may still emit
   `prototype/experiments/<slice_id>/envelope.json` as the retained constraint
   record for downstream handoff and benchmark harnesses; it is an artifact, not
   a dispatch order.
4. `look` — capture and read the rendered result (Stage 4), then refine in place.

Read [`../02-craft-methods/craft-floor.md`](../02-craft-methods/craft-floor.md)
before the first write of runnable code; it holds the generating-side Verify and
Refuse floors. Read
[`../04-governance/execution-boundary.md`](../04-governance/execution-boundary.md)
for the write-scope rules.

### Constraint versus Creative Agency

The envelope's two halves remain the discipline even when the same session
authors the code:

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

## Divergence Discipline (发散与收敛分轨)

The Double Diamond decides when differences are legitimate, so the two modes
never share one rule:

- **Diverge — competing directions.** When several directions must expose a real
  choice, they differentiate on structure, not on tint. Give each direction its
  own IA and page flow; three directions sharing one page list and swapping
  color and texture is the failure mode. Spread them across several axes at
  once, and keep every option inside the register region the product's evidence
  locks — never average toward a middle option, and never manufacture variety by
  producing one bright, one dark and one warm.
- **Converge — competing variants.** When variants of one decision are compared,
  vary exactly one primary axis (structure, density, emphasis, type, or voice)
  and let the secondary choices follow from it. Varying everything at once
  produces three unattributable results: the comparison teaches nothing, and the
  next decision starts from zero.

The craft floor is identical across every direction and every variant. It is not
an axis and never trades against one. A candidate that wins on looks while
failing a hard floor is a bug with a nice surface, not a candidate.

## Bounded Materialization

The main designer holds itself to the same bounds a dispatch would have imposed:

- Author one self-contained HTML/CSS/JS page (`experiments/.../anchor/index.html`).
- Run `python3 skills/spec-prototype/scripts/verify_prototype_quality.py`.
- Capture real viewport evidence via `node skills/spec-prototype/scripts/capture.mjs`.
- Retain at most two local self-repair attempts per probe. Unbounded filesystem
  roaming and CSS ping-pong tuning are forbidden.

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

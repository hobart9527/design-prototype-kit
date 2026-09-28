# Stage 2: Proposition & Hero Probe (立 - 核心主交互原型物化)

Answer one question: *"Does the sealed provisional Spec survive contact with a
real, running Hero Anchor?"* Stage 2 materializes the single highest-risk core
surface or direction probe under the Stage 1 sealed provisional contracts.

## Physical Anchor → Spatial Chassis (物理现实推导优先)

Stage 2 derives its spatial chassis from the domain's own physical reality, not from
a fixed product-category list. The derivation path is mandatory:

1. **Physical anchor first**: name the real-world object, space, or procedure the
   domain practitioner recognizes — the tool they hold, the room they work in, the
   procedure their hands know. This is the source of spatial logic, not a decoration.
2. **Derive the chassis from the anchor**: let the anchor's physicality determine
   spatial structure — how work is laid out, how state is inspected, how the
   operator's attention moves. A cockpit does not become a dashboard by analogy; its
   spatial grammar (instrument clusters, scan routes, commit detents) must transfer.
3. **State the non-transfer boundary**: name explicitly what the physical anchor must
   NOT be read to mean — its failure modes, its impossible features, its cultural
   freight that the digital medium cannot carry.

**Historical chassis specimens (历史标本，非分类表)**: the five patterns below are
documented examples of past derivations — workbench, canvas, editorial, touchflow,
adaptive — not a classification system to select from. A new product may produce
a chassis that matches none of them. Never back-derive a physical anchor from a
chassis name; always derive the chassis from the physical anchor.

- *Dense Workbench*: derived from instrumentation consoles, trading floors, control rooms — micro-grid rhythm, multi-pane, monospaced numerics.
- *Operational Canvas*: derived from whiteboards, planning boards, dispatch maps — structural rhythm, master-detail hierarchy, progressive disclosure.
- *Editorial Reading*: derived from printed pages, legal codex, archival paper — character-measure control, quiet margins, warm paper contrast.
- *Somatic Touchflow*: derived from handheld tools, physical checkouts, portable devices — thumb-zone targets, fluid curves, high haptic responsiveness.
- *Adaptive Workspace*: derived when the domain's spatial logic has no close historical specimen — compose space from the product's own settled object model.

The numeric grid, rhythm, and touch-target parameters behind any chassis are
owned by [`../02-craft-methods/visual-craft.md`](../02-craft-methods/visual-craft.md)
and [`../03-verification/quality-floor.md`](../03-verification/quality-floor.md);
this stage derives the chassis and never restates the numbers.

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
- **Write it in passes, not in one shot.** A single Write carrying the whole page
  overruns the tool's output budget and the call is cut off mid-stream, leaving a
  truncated file and a wasted turn. Write the structural skeleton first (doctype,
  token `<link>`, landmark elements, empty state containers), then add each region
  with a separate Edit. Keep any one write under roughly 8KB.
- Run `python3 skills/spec-prototype/scripts/verify_prototype_quality.py`.
- Capture real viewport evidence via `node skills/spec-prototype/scripts/capture.mjs`.
- Retain at most two build-time self-repair attempts per probe: these are
  mechanical fixes to a broken render, not design revisions. The separate
  design-refinement pass at [Stage 4](stage-4-audit.md) owns its own single
  focused pass and never spends this budget. Unbounded filesystem roaming and
  CSS ping-pong tuning are forbidden either way.

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

## Stage 2 Anchor Presentation Pause

Once the first surface is materialized, present real viewport screenshots at the
runtime-derived `inspection_contract.mandatory_viewports` carried by the assembled
payload — never a hardcoded viewport list.

This is a presentation, not a gate. Show what was built and say plainly what the
user's confirmation would change; then keep working under the authorized scope.
Do not stop the run to wait for a nod, and do not treat silence as approval.
Revert or redirect only on a real user decision; an unattended run continues to
[Stage 3](stage-3-skeleton.md) with the sealed provisional contracts it already
holds. Absorb any later tone or token correction in place, and record the
superseded choice rather than silently overwriting it.

## Exit

Legal exit is a runnable Hero Anchor plus its captured evidence. Continue to
[Stage 3](stage-3-skeleton.md) for full rollout, or return to Stage 1 when the
probe falsifies an upstream contract.

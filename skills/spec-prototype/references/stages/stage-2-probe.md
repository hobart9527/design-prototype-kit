# Stage 2: Proposition & Directions Exploration (立 - 视觉探索与核心主交互原型物化)

Answer one question: *"Which visual language and spatial direction best resolves
the product tension?"* Stage 2 materializes 2–3 distinct exploratory directions
or the primary core interaction prototype.

## Spatial Chassis & Visual Language

Stage 2 derives layout and spatial organization from authentic domain workflows
and modern design vocabularies ([`../02-craft-methods/modern-style-vocabulary.md`](../02-craft-methods/modern-style-vocabulary.md)).

That file is a **challenger source, not a direction menu**: read it at step 4 of the
Divergence Generator to fuse a technique, never at step 2 to pick an identity. The
directions themselves come from the domain's lifeworld. Selecting two styles from its
table is the failure mode the generator exists to prevent.

Physical anchors (e.g. cockpit, workbench, paper codex) serve as optional structural
analogies where helpful, but are never forced upon digital-native products.

## Direct Materialization & Multi-Direction Exploration

The path is visual-first:
1. **Diverge before authoring.** Run the six-step Divergence Generator
   ([`../dialectic/01-metaphor-benchmark.md`](../dialectic/01-metaphor-benchmark.md) §4):
   name the category rut, generate 3 lifeworld-sourced candidates, optionally draw the
   seeds with `python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id>
   --record <the slice's brief or discussion record> --write` (an optional entropy source:
   never choose them yourself — a self-picked integer converges; if the record has no `## Slice: <id>`
   block, print the draw without `--write` and record it by hand), fuse at most one
   catalog challenger each, then pass the two-axis verdict. The verdict is a judgment
   call, not a script gate: a pair differing on fewer than two axes — or on two axes
   without **Structure**, the mandatory axis — is merged and replaced, not built. Record
   the rut, the candidates, the seeds, and the verdict in the design record (the slice's
   `briefs/<slice>.md` on a layered tree, `prototype/discussion.md` otherwise).
   Before converging, compare the built slots yourself from their captures: if the two
   directions share the same region skeleton, the prose verdict was not delivered.
2. **Author 2 distinct directions in physical slots**
   (`prototype/experiments/<slice_id>/dirs/a/index.html` and `dirs/b/index.html`).
   Keep layout and styling independent without file collision.
3. **Author tokens**: Directly write or adjust `prototype/shared/tokens.css` (or local directional tokens)
   to calibrate theme, contrast, and layout rhythm. tokens.css 的首次写入在本 Stage（Turn 2），位于 Make 之前、由设计记录中 `proposed` 的 token 决策驱动，不属 Turn 1。探索期直写属正常路径；Stage 5 编译前须把最终值回写 world.md（或 discussion.md），编译随后重写 tokens.css 并以 sha256 封存，否则编译覆盖手写值。
   对比度预检用一条命令批量完成，不要逐对调用、也不要用 `&&`/`;`/管道串联（hook 只放行单条命令）：`node skills/spec-prototype/scripts/wcag-check.js --on <bg-hex> <fg-hex> [<fg-hex> ...]`，或 `<fg> <bg> <fg> <bg> …` 成对形式；输出一个 JSON 数组。
4. **Capture & inspect**: Capture rendered views via `node skills/spec-prototype/scripts/capture.mjs`.
   页面状态由 `data-state` 属性导出作为可观测出口，capture 状态确认以它为准。无浏览器运行时环境时，Turn 1/2 出口为 `PARTIAL` + `visual_evidence: unverified`，前向引用 Stage 4 进行静态或后续补验。
   Inspect the structured `diagnostics_summary` returned directly in stdout:
   verify zero horizontal overflow (`horizontal_overflow: false`), styles applied (`stylesheets_applied: true`),
   and craft floors (`has_active_feedback: true`, `has_tabular_nums: true`) in one quick step.
5. **Converge**: Select or synthesize the winning direction into the anchor prototype
   (`prototype/experiments/<slice_id>/anchor/index.html`) for deeper state and coverage expansion in Stage 3.
   The losing direction donates its best mechanism to the winner, or the donation is
   recorded as refused with its reason (generator step 6).
6. **Path Singleton**: Any preview or review portal must strictly reside at `prototype/review-portal.html`.
   Never author or copy review portals under nested paths (e.g. `experiments/.../prototype/`).

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

- Author one self-contained HTML/CSS/JS page (`experiments/.../anchor/index.html` or `dirs/{a,b,c}/index.html`).
- **Write iteratively.** Write the structural skeleton first (doctype, token `<link>`, landmark elements, containers), then flesh out content and interaction.
- Capture real viewport evidence via `node skills/spec-prototype/scripts/capture.mjs`.
- Mechanical fixes to a broken render are made directly in place. Unbounded filesystem roaming and CSS ping-pong tuning are avoided.

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
**authored** viewport widths — the `NNNpx` widths declared in the design record
(the slice's `briefs/<slice>.md` on a layered tree, or `prototype/discussion.md`) and recovered by
[`compile_spec_ir.py`](../../scripts/compile_spec_ir.py)'s `parse_viewports`, the same
set the Spec IR binds as `scope.verification_scope.viewports`. Never a hardcoded
viewport list, and never the assembled envelope payload: that payload is produced
only by `assemble_envelope.py`, which the Refusal List keeps off the primary path.

This is a presentation, not a gate. Show what was built and say plainly what the
user's confirmation would change; then keep working under the authorized scope.
Do not stop the run to wait for a nod, and do not treat silence as approval.
Revert or redirect only on a real user decision; an unattended run continues to
[Stage 3](stage-3-skeleton.md) with the design brief and direction decisions it
already holds. Absorb any later tone or token correction in place, and record the
superseded choice rather than silently overwriting it.

## Exit

Legal exit is a runnable Hero Anchor plus its captured evidence. Continue to
[Stage 3](stage-3-skeleton.md) for full rollout, or return to Stage 1 when the
probe falsifies an upstream contract.

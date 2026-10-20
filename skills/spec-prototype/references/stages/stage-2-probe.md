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

### Positive Scaffold: compose a proven mechanism, then author its expression

Before writing a direction, choose one observable mechanism from the existing
[`reference set`](../05-benchmarks/reference-set.md) or a verified product surface.
Record the mechanism, the task relationship it supports, what transfers, and what
does not. The reference is a starting structure, not a visual skin. If no listed
mechanism fits, state the task relationship and compose directly; do not invent a
reference citation or force a metaphor.

For each physical direction, render the same representative content and viewport
with a distinct organizing principle. Compose in this order: primary task and
content → spatial relationship and hierarchy → typography/material/color roles →
interaction and state feedback. Use the direction's actual tokens and at least one
visible signature relationship in the rendered probe. The probe is incomplete when
the record describes a direction but the pixels do not show it.

Use this compact scaffold in the existing design record (not a new artifact):

```text
Mechanism borrowed / source:
Task relationship it serves:
Transferred / refused:
Visible in the render at:
Evidence that would change the choice:
```

A reference-derived mechanism is optional when the brief already supplies a strong
visual language or the task is a local repair. Do not multiply directions merely to
show technique; compare only when the choice can change the design.

Physical anchors (e.g. cockpit, workbench, paper codex) serve as optional structural
analogies where helpful, but are never forced upon digital-native products.

## Direct Materialization & Multi-Direction Exploration

The path is visual-first:
1. **Diverge before authoring — reuse or reopen.** Inspect the design record first. If it already contains a qualified `### Divergence` block with `rut`, `rut_rejected`, three lifeworld candidates and their two-axis verdict, reuse it without rerunning the generator and proceed directly to build `dirs/a` and `dirs/b`. Reopen the six-step Divergence Generator ([`../dialectic/01-metaphor-benchmark.md`](../dialectic/01-metaphor-benchmark.md) §4) only when a probe falsified a direction or new evidence changes the choice. On reopening, name the category rut, generate three lifeworld-sourced candidates, optionally draw the seeds with `python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id> --record <the slice's brief or discussion record> --write` (an optional entropy source: never choose them yourself; if no `## Slice: <id>` block exists, print without `--write` and record by hand), fuse at most one catalog challenger each, then make the two-axis verdict. Fewer than two differing axes, or two without **Structure**, the mandatory axis, means merge and replace rather than build. Record the rut, candidates, seeds and verdict in the design record. Before converging, compare the built slots yourself from their captures: shared region skeletons mean the prose verdict was not delivered.
2. **Author 2 distinct directions in physical slots**
   (`prototype/experiments/<slice_id>/dirs/a/index.html` and `dirs/b/index.html`).
   Each slot is a minimal skeleton — its region structure, reading order, and one
   live interaction of its organising principle — not a full page. Two full pages
   double the Make cost and are not what the comparison needs; two empty prose
   directions make the two-axis verdict a claim instead of an observation.
   Keep layout and styling independent without file collision.
3. **Author tokens**: Record token decisions and exploratory adjustments in the source record (`world.md` or `discussion.md`), then run `python3 skills/spec-prototype/scripts/compile_tokens.py` to materialize `prototype/shared/tokens.css` (and `t1.json`). The authoring format (the three blocks and confirmed-section discipline) lives in [`../../templates/world.tokens.example.md`](../../templates/world.tokens.example.md); never read `compile_tokens.py` source to learn the format. This is part of Turn 2 Make, not Turn 1. Probe slots (`dirs/a`, `dirs/b`) may carry probe-local styles during divergence; the shared `tokens.css` compiles for the anchor at convergence.
   对比度预检用一条命令批量完成，不要逐对调用、也不要用 `&&`/`;`/管道串联（hook 只放行单条命令）：`node skills/spec-prototype/scripts/wcag-check.js --on <bg-hex> <fg-hex> [<fg-hex> ...]`，或 `<fg> <bg> <fg> <bg> …` 成对形式；输出一个 JSON 数组。
4. **Capture & inspect**: Run `node skills/spec-prototype/scripts/capture.mjs <url> --out prototype/evidence --viewports <declared-widths>`
   with the viewports the slice's design record declares (never a fixed default pair)
   (see [`../04-governance/helper-quick-reference.md`](../04-governance/helper-quick-reference.md)).
   Inspect the structured `diagnostics_summary` returned directly in stdout:
   verify zero runtime errors (`runtime_errors: []` — any JS runtime error breaks task interaction and must be fixed immediately),
   zero horizontal overflow (`horizontal_overflow: false`) and styles applied (`stylesheets_applied: true`) in one quick step.
   页面状态的可观测出口与评审复现方式由 [`../03-verification/lean-delivery-rules.md`](../03-verification/lean-delivery-rules.md) 的 `CRAFT-STATE-ENTRY` 规定；capture 状态确认以该规则为准。无浏览器运行时环境时，Turn 1/2 出口为 `PARTIAL` + `visual_evidence: unverified`，前向引用 Stage 4 进行静态或后续补验。
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
- **Attribute every variant in the artifact.** Each direction or variant carries
  `data-variant="<id>"` on its root element (and a matching `data-variant` on the
  comparison container), so a screenshot, a comment, or a capture record names the
  variant it came from without a human reconstructing it from the directory the
  file happened to sit in. Variants of one decision share one fixture dataset —
  different data makes the comparison a data comparison, not a design one.

The craft floor is identical across every direction and every variant. It is not
an axis and never trades against one. A candidate that wins on looks while
failing a hard floor is a bug with a nice surface, not a candidate.

## Expression Study & Blind Critique (表达实验与盲评)

Structure decides which direction; expression decides whether it is any good. Run both
after a direction leads, and before Stage 3 rollout. Both are bounded and optional when
the direction inherits an existing language or the request is a local repair.

**Expression study.** On the leading direction's decisive surface, build one file with
`data-variant` variants that move *one* expression family at a time — type roles,
colour meaning, form (radius/line/edge), or motion — on the same fixture data. Capture
each at the authored viewports and write the outcome into the
[Style Language Card](../01-foundations/design-language.md#the-style-language-card): the Positions the study
supported, the Vocabulary it fixed, and a Counter-example it exposed. Vary one family
per comparison, as in *Converge* above; the study is a way to learn what the language
is, not a polish pass.

**Blind critique.** Before naming a winner, look at the captured directions with labels
and rationale hidden and write, for each: what it is claiming, what it gives up, and
which feels more authored. Then reveal the labels and record any disagreement with the
earlier recommendation. Attended runs show the user the unlabeled captures and ask for
the call. Unattended runs may take an independent view from `spec-prototype-critic`
(optional, never a gate); the result stays `proposed`/`provisional` either way.

## Bounded Materialization

The main designer holds itself to the same bounds a dispatch would have imposed:
author one self-contained HTML/CSS/JS page, write each new file whole with
authentic initial DOM content, capture real viewport evidence, and make
mechanical fixes in place. The authoring rules themselves — the physical triad
split, progressive enhancement, the craft floors and the native-first boundary —
are owned by
[stage-3-skeleton.md](stage-3-skeleton.md) ("Authoring Order") and
[`../03-verification/lean-delivery-rules.md`](../03-verification/lean-delivery-rules.md);
this stage applies them to the probe slots and does not restate them.

## Stage 2 Anchor Presentation Pause

Once the first surface is materialized, present real viewport screenshots at the
**authored** viewport widths — the `NNNpx` widths declared in the design record,
and recovered by
[`compile_spec_ir.py`](../../scripts/compile_spec_ir.py)'s `parse_viewports`, the same
set the Spec IR binds as `scope.verification_scope.viewports`. Never a hardcoded
viewport list, and never the assembled envelope payload: that payload is produced
only by `assemble_envelope.py`, which the Refusal List keeps off the primary path.

This is a presentation, not a gate. Show what was built and say plainly what the
user's confirmation would change; then keep working under the authorized scope.
Whether a run must wait for a human decision is owned by
[`../04-governance/discussion-governance.md`](../04-governance/discussion-governance.md)
("Human authority and delegated agency"): when the direction is already `delegated`,
the choice does not wait for human confirmation, and silence is never approval.
Revert or redirect only on a real user decision; an unattended run continues to
[Stage 3](stage-3-skeleton.md) with the design brief and direction decisions it
already holds. Absorb any later tone or token correction in place, and record the
superseded choice rather than silently overwriting it.

## Exit

Legal exit is a runnable Hero Anchor plus its captured evidence. Continue to
[Stage 3](stage-3-skeleton.md) for full rollout, or return to Stage 1 when the
probe falsifies an upstream contract.

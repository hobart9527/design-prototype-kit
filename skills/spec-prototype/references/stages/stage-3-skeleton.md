# Stage 3: Walking Skeleton Rollout (拓 - 骨)

Answer one question: *"How does the validated anchor become a cohesive
multi-surface skeleton within the resolved coverage?"* Stage 3 expands the anchor
across every in-scope surface derived from the Surface Topology.

## Coverage Selection before Expansion

The entry intent routing in [SKILL.md](../../SKILL.md) decides which stages run;
it does not decide how much of the product those stages cover.
Before expanding beyond the validated anchor, resolve the requested scope against
the current Surface Map, task risks, probe results, and applicable platform
contexts:

- **Resolve, do not interrogate**: present concrete recommended combinations (the
  surfaces and journeys each includes, the verification purpose it serves, its
  dependencies outside the selection, and deliberate omissions) alongside the
  full-product option. Ask only when the choice genuinely changes the route.
- **Retain, do not re-ask**: an explicit prior selection (subset or full product)
  is reused on continuation. A missing, invalid, or revision-mismatched selection
  is reconciled against the current map revision; it never silently defaults to
  full-product.
- **Selection is scope, not approval**: a subset reduces the implementation target
  only. It neither crops the product model nor approves the surfaces.
- **Preserve upstream meaning**: the full Surface Map, object model, permissions,
  states, and consequential rationale stay authoritative under a subset.
  Unselected surfaces stay provisional — not deleted, not invented into the
  selection. A dependency outside the selection is disclosed, never silently added.
  The user's task chain from Stage 1 is part of that meaning: where the task starts,
  the key decisions, what completion looks like, and the main interruption or
  recovery. Build the minimal complete path from a real entry to that result before
  any secondary surface. A step split or screen change must serve a task dependency
  or reduce cognitive load; fewer steps is not the goal in itself, and a wizard is
  neither required nor banned. `CRAFT-MINIMAL-PATH` (owned by
  [`../03-verification/lean-delivery-rules.md`](../03-verification/lean-delivery-rules.md))
  governs when a split is earned; it does not prefer one surface by default.
- **Lightweight routes stay valid**: a bounded direction probe, a spec-only request,
  or a local refinement keeps its route and is not forced through full-product
  enumeration. Downstream engineering handoff compiles and binds the formal Spec upon freeze.
- **One obligation reconciler, two coverages**: selected and full-product coverage
  execute and report through `prototype_context.reconcile_obligations`. Only a
  `full-product` selection authorizes automatic continuation across batches; a
  `selected` coverage stops at its declared obligations. A missing artifact or
  missing evidence withholds completion, and a documented blocker
  never discharges an obligation — only an explicit scope change does. Pending destinations stay
  href-free rather than becoming broken links, and product
  navigation is never forced to display review-management status.

## Derived Surface Topology Rollout

Expand secondary surfaces sequentially from the Stage 1/2 topology, unbinding
rigid naming:

- *Primary Operational Surface* — core work area, main interaction flow.
- *Secondary Contextual Surfaces* — detail inspection, multi-dimensional filter
  flows, drawer panels, forms.
- *Supporting & Administrative Surfaces* — settings, audit history, environment
  status.

### Signature vs. Convention Discipline across Surfaces
Preserve strict expression hierarchy when expanding beyond the hero anchor:
- **Signature Surface**: Only the hero operational screen carries the product's distinctive Signature Relationship, bespoke spatial layout, and custom kinetic detents — this is where Stage 1's **Signature Moment** is built, under the same name.
- **Convention Surfaces**: Every supporting, settings, administrative, tabular, or form surface MUST default to established, familiar industry patterns (clean tables, standard tabs, predictable form fields).
- **Anti-Plagiarism & Anti-Motif Invariant**: Never indiscriminately stamp the hero screen's signature micro-motion or visual motifs onto secondary utility surfaces. Doing so introduces cognitive noise and violates the noise budget.

Multi-surface continuity: inherit the established product thesis, tokens, and
navigation model. Reopen only a changed owner and its direct dependents; never
restart the whole workflow because the session restarted.

## Craft Reference Loading (Make 阶段阅读纪律)

Before the first runnable write, load:
1. `craft-floor.md` — mandatory (Verify + Refuse floors + render defect scan).
2. One section of `visual-craft.md` matching the derived chassis — this is the
   Minimal Reading List's legitimate fourth slot. The section to load is
   determined by the physical anchor derivation, not by category:
   - Dense instrumentation anchor → typographic density, numeric stability sections.
   - Canvas / board anchor → spatial rhythm, elevation, grid sections.
   - Editorial / long-form anchor → measure, leading, contrast sections.
   - Touchflow / mobile anchor → touch target, gesture, recomposition sections.
   Do not load `visual-craft.md` in full; load the section that matches the
   declared chassis. If the product produced a novel chassis with no matching
   section, load the spatial rhythm and typographic density sections as baseline.

### Authoring Order: build the direction into the artifact (生成顺序)

Build the smallest complete task path with the direction visible in the artifact,
not only in the record. Compose in this order; each step lands before the next.

1. **Compose from real content.** Put the brief's actual entities, its longest
   meaningful label, the primary decision and its result into the first frame.
   Establish scan/read order and the spatial relationship before adding containers
   or decoration. Before the first runnable write, all six Direction Contract blocks
   (THESIS, OWN-WORLD, STORY, FIRST VIEWPORT, FORM, FINISH) are present in
   `prototype/world.md` (or `discussion.md`), each carrying a concrete
   proposed/provisional statement rather than a blank or placeholder. If one is
   missing, draft only that statement from the evidence already in the record; then
   code. The six blocks are the composition brief; Stage 4 checks whether the render
   carries them.
2. **Carry the visual language into code.** Compile the selected token source with
   `compile_tokens.py`, link `prototype/shared/tokens.css` from `index.html`, and
   make `anchor.css` consume those semantic variables for canvas, text, surfaces,
   actions and state cues. A direction with committed values must reach the pixels;
   leaving the compiled tokens unreferenced is the "documented strategy, unused
   tokens" defect, not caution.
3. **Make the central path work.** Implement the real entry, action, immediate
   feedback and terminal result in a small state model sized to the task. Keep each
   brief-named action discoverable from the default view, give each named
   exceptional state a reproducible entry, and preserve keyboard/touch operation
   and recovery where the action is consequential. Do not add a store, audit stream
   or branch the task does not need.
4. **Finish the physical details.** Apply the applicable craft floors and
   accessibility behavior from [`craft-floor.md`](../02-craft-methods/craft-floor.md)
   ([`../02-craft-methods/visual-craft.md`](../02-craft-methods/visual-craft.md) owns
   the recipes). Select motion, depth, type and imagery because they strengthen the
   committed direction: theme the browser surfaces (`::selection`, `caret-color`,
   scrollbar, `:focus-visible`), give changing or aligned numerics `tabular-nums`,
   keep one elevation mechanism per container, scope transitions to named
   properties, and use authored SVG rather than emoji for control glyphs. A flat
   surface, instant transition or single typeface is a legitimate authored choice
   when the direction earns it.
5. **Render and inspect.** Run
   `node skills/spec-prototype/scripts/capture.mjs <url> --out prototype/evidence --viewports <the declared viewports>`,
   read the screenshots and `diagnostics_summary`, and confirm the token language
   and signature relationship are visible, the task completes, and runtime errors
   are absent. Fix the owning layer in one focused pass; if capture or interaction
   evidence is unavailable, record `PARTIAL` rather than infer success.

Write each file completely and use targeted `Edit` for local repairs, split by
responsibility (`index.html` structure + `anchor.css` + `anchor.js`) with the
initial domain entities authored directly in markup. Resolve internal links against
their actual directory depth, keep `&` literal in HTML query strings, and on touch
surfaces make the whole multi-line option row one hit target. The truth and authority
boundaries stay owned by [`lean-delivery-rules.md`](../03-verification/lean-delivery-rules.md);
reuse verification helpers before creating checks, per
[`../04-governance/helper-quick-reference.md`](../04-governance/helper-quick-reference.md).

**Positive delivery receipt.** In the existing review record (not a new artifact),
name one visible design relationship that survived into the render, one task
behavior confirmed by interaction, and one limitation or unverified claim. This
complements the evidence manifest; it never replaces it.

## Compression & Release

Refuse the uniform card grid: aggregate high-density operation zones tightly and
reserve generous negative space in contemplation/reading zones. The concrete
density metrics behind this rhythm are owned by
[`../02-craft-methods/visual-craft.md`](../02-craft-methods/visual-craft.md);
this stage states the intent and delegates the numbers.

## Data Floor & Reference Benchmarks

Zero Naked Metrics is enforced: business metrics, micro-sparklines, and status
badges must carry a context reference (range, threshold band, baseline marker, or
event point). The floor itself is owned by
[`Method 4`](../01-foundations/design-methods.md#method-4-zero-naked-metrics--micro-sparklines-pillars-expression--attention)
in the method library; this module states the intent and cites the owner rather
than restating the rule.

## Content Mechanics & Action Verb Lifecycle

Business verbs must hold absolute semantic consistency across the lifecycle:
trigger button (`Quarantine`), modal confirm header (`Quarantine Worker`),
decisive commit button (`Quarantine`), and completion toast (`Worker quarantined`)
share one atomic vocabulary. Synonym drift is forbidden.

### Semantic Grounding & Domain Discipline
- **Authentic Domain Primitives**: Mock entities, dataset rows, and telemetry must exclusively mirror the domain's real vocabulary and topological scope. Avoid gratuitously injecting unrequested peripheral domains, external transactional flows, or unrelated administrative overhead.
- **Fidelity to System Invariants**: Controls, audit logs, and status readouts must strictly conform to declared operational boundaries. If past historical events are declared unrecoverable, mock logs must never pretend this console retroactively repaired them; undo and emergency stops operate solely on currently active, in-flight transitions.
- **Strict Lifecycle Scoping**: Task completion actions transition directly into their verified terminal state (e.g. `resolved`, `archived`, `settled`). Do not author speculative follow-up generators, external notification dispatchers, or secondary workflow wizards unless explicitly specified in the brief.

## Five Axes → Physical Tokens

Use the five values or evidence-backed `open` reasons recorded in the visual-world
owner; never infer an axis from the selected chassis. `compile_tokens.py` compiles
those authored decisions into `tokens.css`. Before extending the anchor, check the
compiled spacing/type, motion, surface/color, and rhythm tokens against the same
axis evidence. An `open` axis remains open and compiles to a neutral scaffold; do
not present that scaffold as a product decision.

## Strict Token Inheritance

Every secondary surface links the global stylesheet using the compiled
`visual_directives.token_link_tag` verbatim. The anchor sits at
`prototype/experiments/<slice>/anchor/index.html`, so the path to
`prototype/shared/tokens.css` is the fixed relative depth
`../../../shared/tokens.css` and may be written directly without an IR
pass (Stage 5 compilation re-verifies the link against the IR). Inline hex colors and
hard-coded pixel margins are eliminated to preserve the design system's one-way
truth inheritance.

## Critical-Path Discoverability

A multi-surface skeleton multiplies the places a prerequisite can hide. Every
consequential action's full execution path must stay visible from visible cues
alone: after each step, the next trigger is directly clickable in the same
snapshot, and an unmet prerequisite shows its unlocking affordance as a real
control, never as a `title` tooltip on a dead button. A gate that renders
disabled while its unlock lives in a tooltip is unreachable to anyone who does
not already know the model — the condition is
`[inv/discoverable-critical-path]`, authored in the slice's design record
(the brief's `contract:invariants` on a layered tree, or `prototype/discussion.md`; the record shape is owned by
[`../../templates/discussion.md`](../../templates/discussion.md)).

## Exit

Legal exit is a coherent walking skeleton plus a review portal. Before leaving,
walk the central task once from its entry using only visible cues, and refine only
after it completes; note any step that could not be walked. Proceed to
[Stage 4](stage-4-audit.md) for the four-dimensional audit.

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
- **Lightweight routes stay valid**: a bounded direction probe, a spec-only request,
  or a local refinement keeps its route and is not forced through full-product
  enumeration; a formal candidate still requires its applicable sealed provisional
  Spec.
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
- **Signature Surface**: Only the hero operational screen carries the product's distinctive Signature Relationship, bespoke spatial layout, and custom kinetic detents.
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

## Compression & Release

Refuse the uniform card grid: aggregate high-density operation zones tightly and
reserve generous negative space in contemplation/reading zones. The concrete
density metrics behind this rhythm are owned by
[`../02-craft-methods/visual-craft.md`](../02-craft-methods/visual-craft.md);
this stage states the intent and delegates the numbers.

## Data Floor & Reference Benchmarks

Zero Naked Metrics is enforced: business metrics, micro-sparklines, and status
badges must carry a context reference (range, threshold band, baseline marker, or
event point). Floors are defined in
[`../03-verification/quality-floor.md`](../03-verification/quality-floor.md);
this module cites them and does not duplicate them.

## Content Mechanics & Action Verb Lifecycle

Business verbs must hold absolute semantic consistency across the lifecycle:
trigger button (`Quarantine`), modal confirm header (`Quarantine Worker`),
decisive commit button (`Quarantine`), and completion toast (`Worker quarantined`)
share one atomic vocabulary. Synonym drift is forbidden.

## Strict Token Inheritance

Every secondary surface links the global stylesheet using the compiled
`visual_directives.token_link_tag` verbatim. Never retype the relative depth by
hand: the anchor sits at `prototype/experiments/<slice>/anchor/index.html`, so
the path to `prototype/shared/tokens.css` is a property of the tree that the
compiler resolves (`../../../shared/tokens.css` for the canonical anchor, but
read it from the IR rather than reconstructing it). Inline hex colors and
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
`[inv/discoverable-critical-path]` in the Stage 1 invariant list, and the Floor
clause is in
[`../03-verification/quality-floor.md`](../03-verification/quality-floor.md).

## Exit

Legal exit is a coherent walking skeleton plus a review portal. Proceed to
[Stage 4](stage-4-audit.md) for the four-dimensional audit.

# Stage 3: Walking Skeleton Rollout (拓 - 骨)

Answer one question: *"How does the validated anchor become a cohesive
multi-surface skeleton within the resolved coverage?"* Stage 3 expands the anchor
across every in-scope surface derived from the Surface Topology.

## Coverage Selection before Expansion

The Change Scope Router in [`../core-workflow.md`](../core-workflow.md) decides
which stages run; it does not decide how much of the product those stages cover.
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
  enumeration.
- **One obligation reconciler, two coverages**: selected and full-product coverage
  execute and report through `prototype_context.reconcile_obligations`. Only a
  `full-product` selection authorizes automatic continuation across batches; a
  `selected` coverage stops at its declared obligations. A missing artifact or
  missing evidence withholds completion, and a documented blocker never discharges
  an obligation — only an explicit scope change does. Pending destinations stay
  href-free rather than becoming broken links, and product navigation is never
  forced to display review-management status.

## Derived Surface Topology Rollout

Expand secondary surfaces sequentially from the Stage 1/2 topology, unbinding
rigid naming:

- *Primary Operational Surface* — core work area, main interaction flow.
- *Secondary Contextual Surfaces* — detail inspection, multi-dimensional filter
  flows, drawer panels, forms.
- *Supporting & Administrative Surfaces* — settings, audit history, environment
  status.

Multi-surface continuity: inherit the established product thesis, tokens, and
navigation model. Reopen only a changed owner and its direct dependents; never
restart the whole workflow because the session restarted.

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

Every secondary surface links the global stylesheet:
`<link rel="stylesheet" href="../../shared/tokens.css">`. Inline hex colors and
hard-coded pixel margins are eliminated to preserve the design system's one-way
truth inheritance.

## Exit

Legal exit is a coherent walking skeleton plus a review portal. Proceed to
[Stage 4](stage-4-audit.md) for the four-dimensional audit.

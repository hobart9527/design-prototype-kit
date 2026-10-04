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

### Pre-Write Craft Sanity Check (生成侧防破损准则)

Before authoring prototype HTML and CSS, apply these non-negotiable floor rules directly into generation:
- **Draw icons, never use emoji glyphs** (`CRAFT-NO-EMOJI-ICON`): inline authored SVG or a clean icon library for all UI affordances. Emoji, pictographs, or Unicode symbol glyphs (e.g. 📊, ⚠️, 🔴) in UI control slots are immediate defects.
- **Single-boundary elevation (No ghost cards)**: declare depth once per container — use either a crisp 1px border (`border: 1px solid var(--border-subtle)`) or a subtle calibrated elevation shadow, never a 1px border combined with a wide blurry shadow.
- **Scoped property transitions (No `transition: all`)**: specify exact animated properties (`transition: transform 150ms var(--spring-snappy), opacity 150ms ease`), never unscoped `transition: all`.
- **Row rails live on the state, not the base** (`CRAFT-ROW-RAIL`): a row-level status rail is declared only on the state variant (`.row[data-st="pending"] { border-left: 3px solid var(--status-warning) }`) or as `box-shadow: inset 3px 0 0 var(--x)`. Do not reserve it on the base class with `border-left: 3px solid transparent`; reserve the width with `padding-left` instead.
- **No bare ordinal headings**: a section heading is a name, not `01`/`14`; number only a real sequence the user steps through.
- **Single-pass build discipline**: write the complete anchor once (target under 500 lines; if the surface set will exceed it, split by surface before writing), then run one batched `capture.mjs` across declared viewports, then at most two `detect.py` runs. Fix what the render shows in one edit pass; whatever remains after the second scan is recorded as `PARTIAL` with its scope, not chased. Incremental CSS-edit → re-capture → re-scan loops are the main cost of this stage (r35: 14 scans, 17 compiles, 8 captures, 40 edits).

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

Legal exit is a coherent walking skeleton plus a review portal. Proceed to
[Stage 4](stage-4-audit.md) for the four-dimensional audit.

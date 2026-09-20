## Context

See proposal.md for motivation. This is a specification-only delivery. Existing lifecycle, verification and benchmark specifications remain in force. Earlier read-only audit identified pending-sibling conflicts, compiler defaults, weak freeze fallback, insufficient provenance and false-pass measurement seams. These are repair targets, not evidence that all current paths have been retested during authoring.

The primary working tree contains pre-existing changes; implementation must establish its exact Git basis and reconcile missing source files without restoring or overwriting user work. Archived reports do not certify the current candidate. No paid experiment is part of this planning step.

## Goals / Non-Goals

Goals: make scope selection usable at Stage 3; preserve product reasoning and Spec continuity; make platform differences actionable; make delivery claims bounded by real evidence; keep the implementation small and directly testable.

Non-goals: a second Skill, a new scheduler or workflow database, mandatory full-stage execution for exploration, exhaustive platform/page/state matrices, native app build infrastructure, aesthetic verdicts from regexes, automatic stakeholder approval, broad benchmark redesign, or production frontend implementation.

## Decisions

### 1. Keep the existing golden chain authoritative

Double Diamond owns divergence/convergence, Nine Pillars own design problems, Five Axes calibrate expression, References supply applicable methods, and the Evidence Protocol owns claim strength. Coverage/platform are execution context, not replacement ontologies. Stage 3 findings can reopen decisions with source revisions; the workflow is not an irreversible waterfall.

A method is meaningfully retained when its trigger, consequential outcome, Spec representation and review obligation survive. Do not force every reference into every task or treat method-name presence as execution proof. Method outcomes needed by a selected slice must remain accessible to Builder and Critic. User selection authorizes scope, not design approval.

### 2. Use one retained selection, not a new authority store

The working Surface Map owns inventory and a small structured execution-selection section. Retained map snapshots preserve revision identity. Existing discussion records the actual user choice/authorization; the selection references that record rather than duplicating its meaning. JSON envelopes are derived, never independently editable product authority.

Selection fields: coverage (`selected` or `full-product`), map revision, surface IDs, journey IDs, target-context IDs and selection-source reference. An absent selection is unresolved, never implicitly full-product. A full-product selection binds the agreed revision; later additions require reconciliation. A selected set may happen to cover every current surface without authorizing future expansion.

Recommendations are authored by the designer using task risk, dependency continuity and Signature transfer, not a hardcoded score or fixed page quota. A small deterministic helper validates IDs, applicability, revision identity and derives coverage differences; it does not decide product meaning. Reuse stdlib and existing parser conventions; no new dependency.

Explicit prior user scope skips redundant questions. Stage 2 probes remain bounded by their existing brief; they do not wait for a complete product map. Stage 3 formal candidates require the selected scope's provisional contracts before dispatch. Unselected product decisions remain retained, while unresearched details remain unresolved rather than invented.

### 3. Define platform context separately from adaptation

Product record owns target-context identity: runtime medium, OS/browser when relevant, device/input environment and known source/unknown status. Existing foundation owns shared experience invariants and cross-platform rules. Slice specifications reference those rules and add only local differences. Surface Map records where each surface applies.

Target platform, artifact medium and evidence environment are separate facts. Example: Android app target, HTML prototype, desktop Chromium execution. This combination can prove browser-observed behavior but not Android system-back behavior.

The adaptation contract records only task-relevant topology, navigation/return, input alternatives, keyboard/viewport effects, accessibility and interruption/recovery. A desktop split view and mobile detail route can share an object and invariant without sharing a layout. No automatic Cartesian product of all surfaces and platforms; no copied full Spec per platform.

### 4. Project rather than reinvent

materialize_contracts and assemble_envelope must retain explicit facts, unknowns and references. Remove fixed domain tension, borrowed-product anchors and Space/P behavior from the owned projection seams. Missing formal route-critical fields produce actionable errors; optional probe unknowns are not a reason to invent facts or block unrelated exploration.

The envelope adds normalized selection and platform references within the existing dispatch format. execution_boundary checks source identity, existing authorization and canonical paths; it does not infer design approval or evaluate taste. Do not authorize an arbitrary helper shell command; add only the specific safe invocation needed by the existing boundary.

### 5. Separate facts from presentation statuses

Retain scope membership, delivery entry and evidence outcomes separately. `delivered`, `pending-this-batch`, `deferred` and `missing-required` must not become a mutually exclusive authority enum. Missing-required is derived at a completion boundary. A documented blocker explains an unmet obligation; it does not satisfy it. Unselected is not the same as previously promised and postponed.

Portal reads declared inventory first, then reconciles artifacts and evidence. Product navigation does not have to expose management badges. Pending targets have no broken href; navigation needed for a selected journey must either be included with authorization or disclosed as limiting the demonstration. Existing delivered routes are still verified. Never require a sibling href before any sibling exists.

### 6. Bind evidence to the smallest meaningful dependency set

Each relevant evidence record identifies artifact revision, task/surface, target context, actual execution environment, performed action/observation and simulation limits. Bind to the slice's actual sources plus shared sources it uses, rather than invalidating all evidence because an unrelated map row changed. Changed shared navigation invalidates dependent journeys; unrelated evidence remains reusable. Unknown validity is unverified, not pass.

Static checks report code facts. Screenshots report captured states. Critic inspects actual images and task evidence, classifies findings and reports unexamined scope; it has no approval authority. Browser input emulation is useful but cannot certify native OS behavior. Missing native facilities are a declared limitation, not an automatic demand to install toolchains in this change.

### 7. One rollout/completion mechanism

Both coverage modes execute selected obligations in dependency-aware batches using the existing Coordinator. `full-product` alone authorizes proceeding across every applicable surface of its bound product revision. Shared shell/data/tokens are reused; supporting surfaces retain appropriate restraint. Resource or decision blockers preserve incomplete work and resume context, never imply completion.

Completion checks selected surfaces plus required journeys/states/platform obligations; page count alone is insufficient. Prototype completeness is qualified by medium. Full HTML coverage can be complete while native behavior remains unverified, provided native verification was not itself promised as complete. If native proof was required, its absence blocks that claim.

### 8. Preserve freeze and approval semantics

Use existing discussion/source references to identify actual approval and its exact scope/revision; do not add a universal approval database. Automated checks verify structured references and consistency, while unsupported authority remains pending. Negated/planned phrases are not approval. Strict packet failures must stay failures; `--force` must never synthesize approved status. Downstream admission recomputes relevant identities. Retain spec-only approval with implementation evidence pending; do not require an HTML artifact for a design-only claim.

### 9. Calibrate measurement before live comparison

Fix numerical overflow checks and missing-value handling, exclude unverified dimensions from verified comparisons, and wire all advertised hard gates into aggregation. Record actual candidate and judge file hashes; Git revision alone cannot identify dirty content. Keep prior reports intact. Rejudging creates new evidence, not retroactive session success.

An authored end-to-end specimen covers representative review, authorized expansion, shared-state mutation/return, mobile adaptation and an honestly unverified native simulation. Hermetic tests validate scenario wiring and mechanisms, not design excellence. A later cost-authorized run is necessary before claiming real-session quality improvement.

## Risks / Trade-offs

- Scope UI can become bureaucracy: ask only when scope is unresolved and concrete alternatives exist; merge equivalent options.
- Early platform uncertainty can halt useful exploration: clarify only route-changing facts, preserve hypotheses in probes.
- Envelopes can erase design intent: compare consequential source assertions with projected inputs and retain accessible references.
- Broad evidence invalidation can make iteration expensive: use actual dependency identities; prefer conservative unverified over false reuse when dependencies are unknown.
- Existing artifacts lack new fields: read them without rewriting, report unresolved selection/context, and normalize explicitly before new formal dispatch/completion.
- Automated instruction tests can only prove contract wiring: add a bounded real-session specimen and explicit independent review, not an invented design-quality score.
- Existing working-tree deletions may block implementation: reconcile the intended source basis before delivery; do not restore user files as part of planning.

## Migration Plan

1. Land source contracts and the normalizer with negative fixtures; preserve existing direction-probe routes.
2. Wire normalized scope/platform into envelope and boundary, removing directly conflicting defaults.
3. Wire platform evidence and shared completion/portal behavior; no destructive artifact migration.
4. Tighten freeze and benchmark claim checks, then perform focused integration and independent golden-chain review.
5. Run a paid end-to-end comparison only after separate cost authorization with pinned actual contents.

Legacy records remain readable but cannot gain approval or platform verification by default. Preserve existing artifacts on errors. For rollback, revert the implementation changes through normal authorized Git workflow; do not erase generated design records or reinterpret old evidence under the new rules.

## Delivery Boundaries

The future implementation tasks own at most ten explicitly named files each and one focused verification command. Tasks that need new tests own their creation. Runtime work is delegated through the existing delivery process after approval; this authoring turn stops after validation and readiness, without candidate commit or implementation. No standalone plan/status documents are created outside this native Change.

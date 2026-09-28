# Stage 1: Frame the Design Problem

Answer: *What should become easier, clearer, safer, or more meaningful—and for whom?*
Produce the smallest useful design brief. Use the Nine Pillars as a lens, not a form;
open alternatives only when a consequential choice is genuinely unresolved.

## Work from the brief

1. Read the user brief and only the workspace sources that can change the design.
2. Name the user, task, important objects, context, constraints, and one central
   tension or opportunity. Mark unsupported inference `[derived]` or `[hypothesis]`.
3. Inspect existing product patterns and up to two relevant references. Say what to
   adopt and refuse; references inform the decision, they do not dictate the UI.
4. Form one clear design proposition: what relationship changes, why it helps, what
   remains familiar, and its cost or learning burden. Offer alternatives only where
   evidence leaves a real choice. Recommend one.
5. Define only the surfaces, actions, states, and stress cases needed to guide the
   requested slice. Leave the rest open; never invent capability to fill a section.

Ask the user only when a decision materially changes the direction or scope. Resolve
repository facts silently. Preserve settled and delegated choices on continuation.

## Design brief format

Keep `prototype/discussion.md` as the concise human-readable decision and evidence
record. For a formal prototype, use `google-design-md/v2` frontmatter and semantic
sections documented in [`../spec-md-contract.md`](../spec-md-contract.md). This is a
Skill-owned, parser-compatible format inspired by Google Design.md; it is not an
official Google schema and does not imply Material Design adoption.

The brief needs only the applicable parts of:

- **Problem & proposition** — task, people, source facts, tension, outcome, omissions.
- **Experience direction & Five Axes calibration** — product-specific hierarchy, tone,
  visual mechanism, references and what is deliberately conventional. Five Axes are optional
  continuous coordinates on relevant dimensions, balancing 70% familiarity with 1 signature
  relationship/moment under the 70/30 innovation boundary.
- **Spatial anatomy** — primary surface and only context surfaces needed by this slice.
- **Actions & states** — consequential task, visible result, recovery, and states needed
  to express or test it.
- **Resilience & invariants** — only risks that could invalidate this design; distinguish
  hard requirements from preference and hypothesis.

Do not fill every Nine Pillar, Five Axis, state, surface, or Break Protocol vector.
Keep the human brief about decisions; machine IR and CSS tokens are compiled outputs.

## Sealed Provisional Baseline Closure

For a formal runnable prototype, establish the applicable sealed provisional Spec
baseline before Builder code. A focused design brief or exploration is not itself a
request to seal or freeze the whole product.

## Formal prototype compilation

When a runnable formal prototype is requested, author the minimum contract in
`prototype/discussion.md`, then run the documented `compile_spec_ir.py` and
`compile_tokens.py` commands in one shell invocation. The compiler creates the machine
IR and human `.spec.md` view; fix actionable compiler errors at their authored source.
Do not inspect compiler source to learn design decisions. Lightweight exploration,
spec-only discussion, and local review do not require the full formal pipeline.

## Required parser anchors

For the formal intent tier, retain the existing parser-compatible headings and fields:

```markdown
# Surface Specification: <Product / Slice>

## 1. Problem Framing & Drivers
- Core Tension: <A> vs <B>

## 3. Spatial Anatomy & Surfaces
- **Primary**: `surface/<id>`
```

Add frontmatter `spec_schema: "google-design-md/v2"`, `slice_id`, and only the
applicable `authority`, `stage`, `viewports`, `required_states`, and `primary_surface`.
Use semantic headings accepted by the contract parser. Later execution details can be
added when the work reaches them; do not pre-complete downstream decisions.

## Exit

A design brief answers the current question and clearly separates facts, decisions,
proposals, and open risks. For a formal prototype, synthesize its applicable contract
and code directly in the same turn when requested and possible. A checkpoint is recovery
context, not an approval gate.

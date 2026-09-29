# Core Kernel — Non-Negotiable Invariants

Layer 2 of the progressive-disclosure router. This file answers one question:
**"What must never be violated under any circumstance?"**

Read this kernel on every entry. Read the relevant
`references/stages/*.md` procedure only when the declared intent requires that
stage; the kernel is small and always loaded, stage procedures and the deeper
`references/` modules load on demand. The detailed stage routing and delegation
map is owned by [SKILL.md](../SKILL.md).

## 1. Prototype as Exploratory Medium, Spec as Downstream Delivery Contract

Prototypes are the rapid working medium for visual and interactive discovery,
allowing progressive co-creation and human aesthetic judgment without prior
cryptographic or specification locks. The Design Specification is extracted and
compiled from the validated, frozen design as the durable contract for engineering
handoff. Never let unverified prototype drift redefine engineering meaning
backward without human confirmation.

## 2. Authority Lifecycle (authority status)

`Draft → Validated → Frozen Approved`

- **Draft** — active visual exploration and prototype iteration; mutable, no pre-spec lock required.
- **Validated** — Stage 4 design consensus achieved and visual/interaction evidence absorbed.
- **Frozen Approved** — Stage 5 immutable candidate bound by SHA-256 manifest and compiled Spec IR for engineering delivery.

Freeze binds the immutable candidate Specification
(`prototype/specifications/<slice_id>/r1.spec.md`), extracted upon delivery, never a mutable exploratory record.
The full authority-to-artifact lifecycle mapping, mutability rules and revision
semantics are owned by
[`04-governance/artifact-lifecycle.md`](04-governance/artifact-lifecycle.md);
this kernel states the states and delegates the details.

## 3. Zero Downstream Handoff Without a Validated Spec Contract

Runnable prototypes require no prior sealed Spec during design exploration:
rapid visual feedback and progressive iteration precede formalization. However,
zero downstream engineering handoff or freeze is authorized without a compiled,
validated Spec Contract. Exploration stays agile; engineering handoff stays formal.

## 4. Evidence Protocol

`explicit > observed > derived > hypothesis > unknown`

Every decision traces to empirical facts or declared hypotheses. Never invent
unsupported product capabilities, third-party integrations, or user-research
claims. Platform facts that are unauthored remain `unknown`; native validation
that was not performed is recorded as `unverified`.

## 5. Rooted Design Ontology

The Nine Pillars (Value · Research · Object · Journey · Topology · Attention ·
Expression · Interaction · Resilience) are the unique design substance. The
Double Diamond governs when to diverge and converge. The Five Axes (Density ·
Energy · Materiality · Rhythm · Character) calibrate sensory direction and are
optional — never a forced CSS formula, never a fixed pixel checklist.

## 6. Semantic Preservation and Coverage Selection

Coverage Selection resolves the Stage 3 implementation scope before expansion.
It is scope, not approval: a subset reduces the implementation target only. The
full Surface Map, object model, and rationale remain authoritative; unselected
surfaces stay provisional; a missing selection never silently defaults to
full-product; out-of-scope dependencies are disclosed, never silently added.

## 7. Four High-Density Deliverables & Role Discipline

The entire design prototype lifecycle is consolidated into four high-density assets:
1. `prototype/discussion.md` — sole decision, dialectic, and product facts ledger.
2. `prototype/specifications/<slice>/r1.spec.md` — sole RFC spec contract (IA topology, states, Break Protocol).
3. `prototype/shared/tokens.css` — sole physical token layer compiled by DTCG.
4. `prototype/experiments/<slice>/anchor/index.html` — sole runnable prototype implementation.

Never create legacy fragmented contract files (`contracts/foundation/f1.md`, `contracts/surface-maps/m1.md`, `contracts/tokens/t1.md`, `contracts/slices/.../c1.md`, `specifications/.../r1.md`) or duplicate `prototype/product.md`. Those files are readable on a tree that predates the IR and are never generated.

The main designer directly writes design records and executable prototype output within the bounded `prototype/` scope. Never edit OpenSpec, and never substitute `prototype/discussion.md` with `prototype/README.md`.

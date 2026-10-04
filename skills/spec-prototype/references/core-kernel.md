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

## 5. Rooted Design Ontology: Nine Pillars Lenses & Five Sensory Axes

The Nine Pillars (Value · Research · Object · Journey · Topology · Attention ·
Expression · Interaction · Resilience) are the design ontology. They are NOT an
administrative checklist or form to fill out linearly; they are **analytical lenses**
used to locate the core dialectic tensions shaping the product slice. In Stage 1,
identify the 2–3 pillars bearing the primary tension, resolve their trade-offs, and
treat the remaining pillars as ambient constraints.

The Double Diamond governs when to diverge and converge: **divergence is mandatory in
Stage 1** (exploring at least 2 polarized structural hypotheses) before converging onto
a physical anchor.

The Five Axes (Density · Energy · Materiality · Rhythm · Character) are **continuous
sensory coordinates** that calibrate the physical feeling of the product and directly
inform DTCG token compilation:
- **Density**: determines the structural spatial grid (4px tight vs 12px relaxed) and typography line-heights.
- **Energy**: sets the physical transition velocity, spring curves, and feedback detents.
- **Materiality**: defines depth hierarchy (flat hairline borders vs layered elevations, acrylic blurs, or optical surface finishes).
- **Rhythm**: drives layout cadence (uniform modular cards vs asymmetric visual narrative).
- **Character**: modulates chromatic intensity and emotional presence (5% surgical accent on tool surfaces vs immersive atmospheric branding).

The Five Axes register is **required at direction lock**, and never a forced CSS
formula or a fixed pixel checklist. Required means every axis is *accounted for*,
not that every axis carries a value: each of the five carries either a value with
its cited product evidence, or an explicit `open` with the reason it stays free.
An axis left blank is indistinguishable from an axis decided by model default —
which is why silence at direction lock is the one outcome this kernel forbids.
The register binds at direction lock only: a bounded direction probe, a spec-only
request, or a local refinement does not trigger it. This is a Stage 1 decision,
not an approval gate or a reason to extend discovery beyond the active uncertainty.
Authentic reference products (e.g. Linear, Stripe, Raycast, Vercel) serve as
empirical anchors for these coordinates, not visual templates to clone blindly.

## 6. Semantic Preservation and Coverage Selection

Coverage Selection resolves the Stage 3 implementation scope before expansion.
It is scope, not approval: a subset reduces the implementation target only. The
full Surface Map, object model, and rationale remain authoritative; unselected
surfaces stay provisional; a missing selection never silently defaults to
full-product; out-of-scope dependencies are disclosed, never silently added.

## 7. Four High-Density Deliverables & Role Discipline

The entire design prototype lifecycle is consolidated into four high-density assets:
1. `prototype/discussion.md` — sole decision, dialectic, and product facts ledger on
   a single-record tree; on a layered tree the same role is split across
   `prototype/truth.md` (product facts and the Decisions and authority table),
   `prototype/world.md` (the visual world and sole token authority), and
   `prototype/briefs/<slice>.md` (one slice per file), with `discussion.md`
   narrowing to a thin resume seam.
2. `prototype/specifications/<slice>/r1.spec.md` — sole RFC spec contract (IA topology, states, Break Protocol).
3. `prototype/shared/tokens.css` — sole physical token layer compiled by DTCG.
4. `prototype/experiments/<slice>/anchor/index.html` — sole runnable prototype implementation.

The legacy fragmented contract set and the duplicate `prototype/product.md` are
readable on a tree that predates the IR and are never generated. The retirement
inventory, its canonical paths and the migration rules are owned by
[`04-governance/artifact-lifecycle.md`](04-governance/artifact-lifecycle.md);
this kernel states the prohibition and delegates the inventory rather than
restating it.

The main designer directly writes design records and executable prototype output
within the bounded `prototype/` scope. Never edit OpenSpec, and never substitute
the design record (whether `prototype/discussion.md` or the layered `truth.md` /
`world.md` / `briefs/` set) with `prototype/README.md`.

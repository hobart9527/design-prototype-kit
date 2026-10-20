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

**Decision-row status is a separate register.** A row in the Decisions and authority
table carries `proposed | provisional | confirmed | delegated | needs-evidence | superseded`,
and this section owns what those mean: `proposed` is a candidate the
designer put forward, `provisional` is a proposal carried forward while the
direction is still open, `confirmed` requires the user's own in-session selection,
`delegated` means the user authorized AI judgment within a named scope,
`needs-evidence` means inspectable material is still missing, and `superseded`
means a retained successor replaced the decision. Nothing else — not a brief's
wording, not a resume block, not an approval-shaped process note — promotes a row
to `confirmed` or `delegated`. Every other document that names this status cites
this section rather than redefining it; the `User source` column is a separate
register (`confirmed | delegated | synthetic-fixture`) and its values are never
read as this column's values.

**Resident invariants.** Every decision traces to empirical facts or declared
hypotheses. Never invent an unsupported product capability, a third-party
integration, a user-research finding, an unverified root-cause attribution, an
unrequested telemetry or capacity source, or an unprompted lifecycle pipeline.
`[explicit]` marks pure user statements only; a designer-made mechanism
(confirmation dialog, undo window, two-man rule) stays `derived`, and a brief that
gives counts without names gets neutral placeholders (`<kind>-01 ~ <kind>-NN`),
never an invented lateral domain. Platform facts that are unauthored remain
`unknown`; native validation that was not performed is recorded as `unverified`.
Decisions without explicit in-session user choice carry forward as `unaffected
provisional decisions carried forward`, NEVER as `confirmed` or `approvals
preserved`.

**Full discipline owner.** The tag rules, the anti-fabrication detail, the
carry-forward wording and the tagging discipline for briefs, code comments and
downstream records are owned by
[`03-verification/lean-delivery-rules.md`](03-verification/lean-delivery-rules.md)
("Strict Authority Boundaries & Atomic Tagging", "Ground Truth & Attribution
Fidelity", "Domain Entity Grounding & Neutral Seeding"). This kernel states the
invariants; that file owns the rules and every other file cites it.

## 5. Rooted Design Ontology: Nine Pillars Lenses & Five Sensory Axes

The Nine Pillars (Value · Research · Object · Journey · Topology · Attention ·
Expression · Interaction · Resilience) are the design ontology. They are NOT an
administrative checklist or form to fill out linearly; they are **analytical lenses**
used to locate the core dialectic tensions shaping the product slice. In Stage 1,
identify the 2–3 pillars bearing the primary tension, resolve their trade-offs, and
treat the remaining pillars as ambient constraints.

The Double Diamond governs when to diverge and converge: when the direction is undecided,
**divergence is mandatory in Stage 1** (exploring at least 2 polarized structural
hypotheses) before converging onto a physical anchor; when evidence has already locked
the direction, one proposition is enough.

The Five Axes (Density · Energy · Materiality · Rhythm · Character) are **continuous
sensory coordinates** that calibrate the physical feeling of the product and directly
inform DTCG token compilation:
- **Density**: determines the structural spatial grid (4px tight vs 12px relaxed) and typography line-heights.
- **Energy**: sets the physical transition velocity, spring curves, and feedback detents.
- **Materiality**: defines depth hierarchy (flat hairline borders vs layered elevations, acrylic blurs, or optical surface finishes).
- **Rhythm**: drives layout cadence (uniform modular cards vs asymmetric visual narrative).
- **Character**: modulates chromatic intensity and emotional presence (5% surgical accent on tool surfaces vs immersive atmospheric branding).

The Five Axes register is **required at direction lock**, and never a forced CSS
formula or a universal pixel checklist. Required means every axis is *accounted for*,
not that every axis carries a value: each of the five carries either a value with
its cited product evidence, or an explicit `open` with the reason it stays free.
For a decided value, pair the qualitative choice with at least one observable
calibration anchor (for example, Density: 4px base rhythm / 12px section rhythm;
Energy: instant state change / 180ms transition; Materiality: border-only / one
elevation layer; Rhythm: repeated 8px cadence / editorial variable measure;
Character: restrained status accent / expressive display type). These are examples,
not defaults or bounds: choose anchors from the actual tokens, content and viewport,
and keep the qualitative value when no defensible number applies. Cite the authored
token or visible relationship and its evidence; do not manufacture precision or
force an `open` axis into a numeric value. An axis left blank is indistinguishable
from one decided by model default — which is why silence at direction lock is the
one outcome this kernel forbids.
The register binds at direction lock only: a bounded direction probe, a spec-only
request, or a local refinement does not trigger it. This is a Stage 1 decision,
not an approval gate or a reason to extend discovery beyond the active uncertainty.
Authentic reference products (e.g. Linear, Stripe, Raycast, Vercel) serve as
empirical anchors for these coordinates, not visual templates to clone blindly.
The words the token compiler actually maps per axis, and its fallback signal when a
value misses, are tabulated in [`../templates/world.tokens.example.md`](../templates/world.tokens.example.md)
Block 3 — read it before choosing an axis value.

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

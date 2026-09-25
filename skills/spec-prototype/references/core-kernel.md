# Core Kernel — Non-Negotiable Invariants

Layer 2 of the progressive-disclosure router. This file answers one question:
**"What must never be violated under any circumstance?"**

Read this kernel on every entry. Read the relevant
`references/stages/*.md` procedure only when the declared intent requires that
stage; the kernel is small and always loaded, stage procedures and the deeper
`references/` modules load on demand. The detailed stage routing and delegation
map is owned by [SKILL.md](../SKILL.md).

## 1. Spec as Durable Contract, Prototype as Disposable Proof

The Design Specification is the durable, authored contract. A prototype is
disposable evidence used to validate it. Never promote a mutable prototype
record to contract authority, and never let prototype drift redefine meaning
backward.

## 2. Authority Lifecycle (authority status)

`Draft → Sealed Provisional → Validated → Frozen Approved`

- **Draft** — active exploration; subject to change.
- **Sealed Provisional** — Stage 1 baseline the probe is authorized against.
- **Validated** — Stage 4 evidence absorbed and re-verified.
- **Frozen Approved** — Stage 5 immutable candidate bound by SHA-256 manifest.

Freeze binds the immutable candidate Specification
(`prototype/specifications/<slice_id>/r1.md`), never a mutable product record.
The full authority-to-artifact lifecycle mapping, mutability rules and revision
semantics are owned by
[`04-governance/artifact-lifecycle.md`](04-governance/artifact-lifecycle.md);
this kernel states the states and delegates the details.

## 3. Zero Prototype Code Without a Sealed Provisional Spec Contract

For formal candidate delivery, no runnable prototype is authored before the
sealed provisional Spec Contract exists. Lightweight routes (direction probe,
spec-only discussion, local refinement) are not forced through a full-product
contract; they keep their own bounded routes.

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

## 7. Storage and Role Discipline

All design records go to `prototype/discussion.md` (mandatory entry index) and
`prototype/*.md`. The main designer writes Markdown design records; only
`spec-prototype-builder` writes executable prototype output within its bounded
scope. Never edit OpenSpec, and never substitute `prototype/discussion.md` with
`prototype/README.md`.

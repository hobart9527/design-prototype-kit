# spec-prototype domain context

## Purpose

`spec-prototype` is a PRD-driven product-design module. It carries a product from
source-grounded understanding through product structure, integrated expression,
runnable validation and exact engineering handoff. It does not reduce design to
screens, styling or prototype code.

## Canonical language

- **Product Experience Model**: the continuous dependency model connecting
  thesis, actors/jobs/outcomes, objects/content/authority, journeys/service,
  Surface Topology, integrated expression, validation, coverage and handoff. It
  is projected through existing records, not stored as a second database.
- **Product Thesis**: concise account of who the product serves, what change it
  enables, why that matters and how success could be observed.
- **Object and Content Model**: first-class objects, relationships, attributes,
  terminology, lifecycle, ownership/authority and content structure.
- **Journey/State/Service Model**: end-to-end jobs, visible states, roles,
  channels, backstage dependencies, interruptions and recovery.
- **Surface Topology**: derived set of pages and other surfaces plus their
  routes, relationships, continuity, responsive transformations and coverage.
- **Design Proposition**: product-grounded hypothesis connecting a generative
  mechanism, representative task/content, retained convention, integrated
  expression, Signature Relationship, benefit/cost and a falsification test.
- **Qualitative Design DNA (Axis DNA)**: concise, human-readable account of an
  expression combination and the product evidence that makes that combination
  appropriate. Its dimensions are contextual rather than a fixed numeric vector.
- **Real-World Mapping**: optional, evidence-labelled translation from an observed
  digital-product mechanism into the local product, naming what transfers and
  what does not.
- **Signature Relationship**: a distinctive relationship among content,
  interaction and expression that remains recognizable across surfaces; not a
  decorative motif copied everywhere.
- **Signature Craft**: the concrete, perceivable way a Signature Relationship is
  expressed through applicable content, hierarchy, typography, color, imagery,
  icons, components, feedback and motion on a particular surface or state.
- **Walking Skeleton**: the smallest connected specimen that can test the
  highest-risk product relationships on a representative task.
- **Project Experience Foundation**: retained project-wide Design Proposition,
  language, scoped feedback principles, system relationships and Experience
  Invariants.
- **Design Record**: the authored source the compile and freeze read as one unit.
  Two layouts are valid, and `read_design_record(root, slice_id)` is the single
  place that decides which one a tree uses: the single-record `prototype/discussion.md`,
  or the layered `prototype/truth.md` + `prototype/world.md` + `prototype/briefs/<slice>.md`.
  A partitioned record owes each slice exactly one block; a missing or doubled block
  is reported, never absorbed from another slice. The **Decisions and authority**
  table that `handoff.py freeze` reads lives in `discussion.md` on a single-record
  tree and in `truth.md` on a layered tree.
- **Discussion Record**: current decision scope, actual user statements,
  delegation, open dependencies and next action; not a product specification.
  On a layered tree the record is the layered files and `discussion.md` narrows to
  the resume seam that points at them.
- **Research Record**: sourced observations, limitations and applicability tied
  to a decision; not user research unless people were actually studied.
- **Slice Contract**: scoped, testable experience obligations under exact product,
  topology and Foundation references.
- **Spec IR**: the canonical machine-readable intermediate representation compiled
  by `compile_spec_ir.py` to `prototype/contracts/compiled/<slice-id>/r1.spec.json`;
  it is the single source consumed by downstream envelope assembly.
- **Compiled Specification View**: the single-file human RFC rendering of the Spec
  IR at `prototype/specifications/<slice-id>/r1.spec.md`; it is a view of the IR,
  not a second authority.
- **Prototype Specification**: immutable generation contract compiled from exact
  source revisions; it creates no new design meaning. Canonical form is the Spec
  IR plus its compiled `.spec.md` view; the legacy multi-file `r1.md` / `c1.md`
  set is compatibility output only.
- **Discussion Prototype**: runnable evidence generated from one brief or
  Specification revision.
- **Prototype Evidence**: observed run, task, state, responsive and accessibility
  results with their limits.
- **Prototype Review**: separated professional design judgment, task evidence and
  engineering conformance against one target and question.
- **Experience Invariant**: observable product-experience relationship that must
  survive regeneration or adaptation.
- **Design evidence status**: `explicit | observed | derived | hypothesis |
  unknown` when a claim's basis matters.

## Eight professional lenses

These are the professional-judgment viewpoints a reviewer applies; they sit
beside the Nine Pillars, not in place of them. The Nine Pillars are the design
ontology — what the design *is made of* — and live in `core-kernel.md` §5 and
`01-foundations/design-methods.md`. The eight lenses below are the reviewer's
*stances* — the directions from which the work is checked for completeness.
They do not prescribe order, weight, page count, state count or style.

1. Value and outcomes.
2. Research and context.
3. Objects and content.
4. Journeys and service.
5. IA and Surface Topology.
6. Interaction, usability, accessibility and trust.
7. Integrated content, visual, brand and motion expression.
8. Prototype, evaluation, design system and handoff.

## Three AI-native partnership principles

1. Human goal authority with delegated AI agency.
2. Epistemic integrity, inspectability and reversibility.
3. Feedback- and evidence-driven co-adaptation.

## Ownership

- Cited product sources and native OpenSpec own product facts and behavior.
- `prototype/discussion.md` owns the reconciled design synthesis and every
  approval decision, not source truth.
- `prototype/discussion.md` also owns the Success metrics and the Reviewer's
  evaluation guide for the current delivery.
- The compiled slice specification (`r1.spec.md`, from the Spec IR at
  `contracts/compiled/<slice-id>/r1.spec.json`) carries topology, routes,
  journeys and coverage, the integrated Design Proposition and project-wide
  language, and the scoped experience obligations with their pinned upstream
  references. The retired `product.md` / `m1.md` / `f1.md` / `c1.md` / `r1.md`
  files are legacy inputs: readable on a tree that predates the IR, never
  generated, never bound back in.
- Specification compiles existing decisions without redefining them.
- Discussion owns actual approval/delegation provenance and the active frontier.
- Builder owns bounded specimen implementation; Critic owns independent advice.
- The human owns consequential product changes and final direction.
- Downstream delivery owns production implementation.

## Script roles

Each helper owns exactly one artifact or one decision. When a script's role is
unclear, that is the defect to fix — not a reason to add another script.

| Script | Owns | Reads | Reached from |
|---|---|---|---|
| `execution_boundary.py` | Tool-call admission, write-time validation of `intent.json`, and the design-record first-write gate (accepts `discussion.md` or the layered `truth.md`/`world.md`/`briefs/<slice>.md` as the anchor) | tool-call payload | Skill hook (automatic) |
| `compile_spec_ir.py` | The Spec IR and its `.spec.md` view | `prototype/intent.json`, the design record | Stage 5 Handoff prose |
| `spec_contract_blocks.py` | The `contract:<kind>` block loader, its per-kind normalisers and the admit checks, and the design-record load seam `read_design_record` (never run alone; `compile_spec_ir` re-exports it) | the design record | `compile_spec_ir`, `handoff` |
| `compile_tokens.py` | `tokens.css` and the DTCG `t1.json` | the design record (pass `--discussion prototype/world.md` on a layered tree), Five Axes | Stage 5 Handoff prose |
| `verify_prototype_quality.py` | The objective floors that drive its exit code (no inspectable or reachable controls, dead links and assets, unbound stylesheet, rogue `:root`, raw inline hex, viewport receipts, three craft invariants, and action authority). Write scope is owned by `execution_boundary.py`, not here. Overflow, contrast and keyboard reach are read from the Evidence Packet and ruled on in review plus the Evidence Packet — the render facts a design review rules on. A contract-read-back finding is a signal, never a floor. The legacy surface-map reconciliation (`coverage_failures`) is retained only for trees that still carry `m1.md`; canonical/layered trees skip it | authored HTML, `tokens.css`, contract | test harnesses, the delivered `verification_command` |
| `authority_fidelity.py` | The authority-fidelity check: an action claiming `explicit` must be backed by a `confirmed`/`delegated` row in the design record's Decisions table (pass `--discussion prototype/truth.md` on a layered tree) | Spec IR, the design record | Stage 5 Handoff freeze |
| `handoff.py` | The dispatch packet and the Stage 5 freeze; the approval binding reads the Decisions table from `prototype/discussion.md` on a single-record tree and from `prototype/truth.md` on a layered tree | Spec IR, decisions | Stage 5 prose, `execution_boundary` |
| `lint_spec_contracts.py` | The Spec IR structure and freshness check (E001 when no compiled IR exists, E022 when `tokens.css` drifts from the source its own seal names); the legacy six-piece lint is retired | compiled IR, `tokens.css` seal | Stage 5 Handoff prose |
| `draw_seed.py` | An optional entropy source for divergence seeds; never a gate: when the record cannot take the block it prints the draw for hand-recording | the design record, `modern-style-vocabulary.md` | Stage 2 prose |
| `assemble_envelope.py` | The dispatch envelope and its bound-source digests | Spec IR | `handoff` packet path; tests |
| `prototype_context.py` | Shared project-context library (never run alone) | project tree | `handoff`, `verify_prototype_quality`, `lint_spec_contracts` |
| `capture.mjs`, `preview.mjs`, `wcag-check.js` | Rendered evidence, preview, contrast preflight | authored HTML/tokens | Stage 2/4 prose |

Retired: `materialize_contracts.py` and `export-tokens.py` wrote the legacy
fragmented contract set and a DTCG export whose empty `color` group made the
contrast preflight pass falsely. Both are deleted; the legacy pillar set is
read-only input on trees that predate the IR, and `compile_tokens.py` is the sole
token writer.


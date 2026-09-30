# Artifact Lifecycle and Ownership

Read before creating, revising, freezing, or migrating product-experience artifacts.
For formal contract semantics and source-to-UI evidence, use
[interpretation rules](interpretation-rules.md).

The four canonical high-density assets are the delivery set. Everything a formal
run produces lives in one of them:

| Object | Scope and owner | Lifecycle | May decide |
|---|---|---|---|
| Decision record — `prototype/discussion.md`, or the layered `prototype/truth.md` + `prototype/world.md` + `prototype/briefs/<slice>.md` | The evolvable human/agent co-creation ledger: Product Thesis, confirmed decisions, Five-Axes calibration, coverage selection, evidence status. The Decisions and authority table lives in `discussion.md` on a single-record tree, and in `truth.md` on a layered tree | always mutable; never a freeze subject | Problem framing, product thesis, actors/jobs/outcomes, the chosen proposition and its trade-off, coverage, and what stays `[hypothesis]` |
| Slice specification — `prototype/specifications/<slice>/r1.spec.md` | The single-file RFC: IA topology, state machine, actions, Break protocol, invariants. Compiled from the canonical IR (`contracts/compiled/<slice>/r1.spec.json`) | `draft -> frozen -> superseded` | The slice's binding generation constraints; nothing new is authored here after compile |
| Token stylesheet — `prototype/shared/tokens.css` (+ `contracts/tokens/t1.json`) | The compiled physical style layer. The token authority is `discussion.md` on a single-record tree and `world.md` on a layered tree, never both; the JSON is derived packaging | `draft -> frozen -> superseded` | The concrete colour, space, radius, type and motion values every surface inherits |
| Anchor artifact — `prototype/experiments/<slice>/anchor/index.html` | The runnable materialisation of one specification revision | `generated -> verified` or `blocked`; disposable evidence | Nothing; executable proof only |

Retired contract files (`product.md`, `contracts/surface-maps/m1.md`,
`contracts/foundation/f1.md`, `contracts/tokens/t1.md`, `contracts/slices/<slice>/c1.md`,
`specifications/<slice>/r1.md`) are legacy inputs: readable, never generated, never
bound back in once the canonical IR exists.

The cited product source owns product behavior, roles, permissions, state, data
relationships, Gates and acceptance. The records jointly project one Product
Experience Model; they are not a second product database. The authoring session owns
low-level implementation choices inside its experiment scope. Downstream delivery
owns production implementation.

A Prototype Review record may accompany a run, but it is an evidence note, not a fifth
deliverable: its recommendation and the actual human decision are recorded separately,
and it never rewrites the assets above.

## Authority Lifecycle vs. Artifact File Lifecycle Mapping

The system defines two closely coordinated lifecycle models: the **Authority Lifecycle** (governing design trust and admissibility across the 5 stages) and the **Artifact File Lifecycle** (governing filesystem mutability, hashing, and version supersession). They map unambiguously:

| Authority Lifecycle (`authority status`) | Applicable Stage | Artifact File Lifecycle | Mutability & Handoff Semantics |
|---|---|---|---|
| **Draft** | Stage 0 (Explore), Stage 1 (Frame), Stage 2 (Directions), Stage 3 (Make) | `draft` | Mutable exploration. Relative paths, direct prototype authoring, no cryptographic hash-locks. Tokens and prototypes iterate freely without prior Spec compilation. |
| **Validated** | Stage 4 (Look / Refine) | `draft` (evidence-cleared) | Human design review and visual inspection complete; key feedback absorbed and stabilized. |
| **Frozen Approved** | Stage 5 (Silent Governance / Handoff) | `frozen` | Immutable delivery. Spec IR (`r1.spec.json`), RFC specification (`r1.spec.md`), and DTCG tokens (`t1.json`) compiled and bound by SHA-256 digests via `handoff.py freeze`. Downstream engineering delivery admission state. Any subsequent modification requires an explicit successor revision (`superseded`). |

*(Note: Legacy status values like `Sealed Provisional` remain readable for backward compatibility on historical candidate records).*

## Dual-track artifact lifecycle: Exploration vs Formal Delivery

To prevent cryptographic hash-locks from freezing creative discovery while maintaining
absolute handoff integrity, artifacts operate in two explicit tracks:

### 1. Exploration Track (Draft & Feedback Mode)
- Artifacts are marked `draft` and reference each other by semantic version and relative
  paths rather than immutable SHA256 digests.
- Direction Probes (`prototype/probes/`) operate strictly in this track. Calling `handoff.py freeze`
  or enforcing composite route harnesses on exploratory probes is an architectural violation.
- In this track, visible specimens are expected to test upstream assumptions. If runnable
  experimentation reveals a flaw in the Surface Map or Object Model, the designer may
  immediately update the draft IA without invalidating downstream hashes.
- The dependency graph remains bi-directional, agile, and iterative.

### 2. Formal Delivery Track (Frozen & Handoff Mode)
- Invoked only when design exploration has converged and the team is ready to hand off
  specifications to engineering delivery (Loom).
- Artifacts transition `draft -> frozen`. `handoff.py freeze` calculates immutable SHA256
  digests across the retained delivery assets: `r1.spec.md`,
  `tokens.css` (`t1.json`), and the anchor `index.html`. The design record
  (`discussion.md`, or the layered `truth.md`/`world.md`/`briefs/`) stays evolvable
  and is never a freeze subject.
- In this track, bytes are strictly immutable; any subsequent change requires an explicit
  successor revision.

## Canonical paths

```text
prototype/contracts/compiled/<slice-id>/r1.spec.json
prototype/specifications/<slice-id>/r1.spec.md
prototype/shared/tokens.css
prototype/contracts/tokens/t1.json
prototype/experiments/<slice-id>/<prototype-revision>/
prototype/evidence/<slice-id>/<prototype-revision>/
prototype/reviews/<slice-id>/<prototype-revision>.md
```

### Legacy compatibility paths

### Deprecated Legacy 6-Piece Files (Banned in Primary Delivery)

The legacy 6-piece multi-file set is deprecated and MUST NOT be authored or generated:
```text
prototype/product.md                        # Duplicate of discussion.md
prototype/contracts/surface-maps/m1.md      # Subsumed by r1.spec.md
prototype/contracts/foundation/f1.md        # Subsumed by discussion.md & tokens.css
prototype/contracts/tokens/t1.md            # Subsumed by shared/tokens.css
prototype/contracts/slices/<slice-id>/c1.md # Subsumed by r1.spec.md
prototype/specifications/<slice-id>/r1.md   # Replaced by single-file r1.spec.md
```
Primary delivery writes ONLY the design record (`discussion.md`, or the layered `truth.md`/`world.md`/`briefs/`), `r1.spec.md`, `tokens.css`, and `index.html`.

## Session intent and retained design

Discussion records own the current delivery request (explore, spec-only, build)
and its turn scope. Retained design artifacts own user-task outcomes and durable
constraints; source quotations may preserve historical requests as evidence.
Compile those meanings separately: a past spec-only turn does not prohibit a
later authorized build, and a build request does not waive persistent dependency
or product constraints. Keep current execution instructions out of frozen design.

## Revision rules

- Give every object its revision in the filename. Edit only a `draft`; freezing
  retains that file and any change creates a new revision with `Supersedes`.
- Prototype generation and review do not change Contract status.
- Candidate specifications are immutable. Record selection, rejection and
  supersession in Discussion/Review with the exact candidate reference; these
  dispositions do not rewrite candidate bytes. Combining candidates creates
  another candidate revision.
- Finish source lifecycle edits before computing digests and compiling. Once
  a candidate cites a source, retain those bytes even when the source was a
  draft for comparison. Later source edits/freezing require a successor source
  revision and recompiled candidate; do not patch a retained candidate's hashes.
  A candidate based on draft sources is exploratory, not a frozen baseline.
- Do not copy source prose when a stable anchor and digest preserve the authority boundary.
- A product-source revision requires reconsideration only of artifacts whose cited meaning changed. Foundation owns integrated expression; Surface Map owns topology/journeys/coverage. Mark affected dependents in the discussion record and preserve unrelated approvals.
- Retain the surface topology inside the canonical compiled spec before compiling a candidate. The slice specification cites its exact path/digest. `prototype/discussion.md` remains the working decision index; status updates do not rewrite retained structure.
- User-confirmed Foundation, IA and Specification decisions may precede runnable evidence; validation remains explicitly pending. Prototype execution never supplies user approval.
- The discussion record owns pending decisions and rationale, not a second copy of formal rules; research records own observations, not product truth.

Direction probes are a bounded exception: one viewport from an explicit probe
brief, no full interaction or delivery qualification. They do not require the
formal Slice Contract/Specification chain and cannot replace its evidence.

Token snapshots name their owning Foundation revision and retain exact bytes; token
and Foundation revision identifiers need not be equal. The canonical token artifact
is `prototype/shared/tokens.css` compiled by `compile_tokens.py`, which also emits
the DTCG `prototype/contracts/tokens/t1.json`; the JSON is derived packaging, not
design authority. Specifications name the token path and digest. At token freeze,
run the contrast preflight against the compiled `t1.json`, which carries the flat
`color` group consumed by `wcag-check.js`. A Markdown-table re-export that groups
tokens by CSS prefix does not carry that group, so pointing `wcag-check.js` at it
yields an empty set and a falsely passing preflight. Preserve existing output on failure; never overwrite a
different export or rewrite frozen artifacts to fix packaging. Report a missing
export as an execution limitation until the permitted helper succeeds.

## Legacy migration

Existing frozen combined Foundations remain readable as legacy inputs. On the next relevant user-authorized revision, retain their original bytes, extract IA into a new surface-map snapshot with provenance, and create a language-only successor Foundation. Rebind only new or affected Contracts to explicit references. Do not rewrite historical frozen candidates or silently infer new approval from migration.

- Move `implemented` or `reviewed` Contract status into Prototype Evidence or Review; restore the Contract lifecycle to `draft | frozen | superseded`.
- Replace legacy implementation handoffs with the exact frozen design-artifact
  reference set; any downstream delivery contract decides how to cite it.
- Migrate fixed legacy paths by retaining the old file as `revision-1`, adding
  its digest to the new index/reference, and writing later revisions only to
  the canonical revisioned paths above.
- Move embedded review findings into a separate Review.
- Fold a standalone surface assessment into the Slice Contract's Contract Readiness section, then retire the duplicate file.
- Treat existing runnable pages as evidence only after their source Contract and Specification revisions are recorded.

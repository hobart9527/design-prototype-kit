# Artifact Lifecycle and Ownership

Read before creating, revising, freezing, or migrating product-experience artifacts.
For formal contract semantics and source-to-UI evidence, use
[interpretation rules](interpretation-rules.md).

| Object | Scope and owner | Lifecycle | May decide |
|---|---|---|---|
| Product record | Project design synthesis linked to cited product sources | revisable summary | Product Thesis, actors/jobs/outcomes, object/content and known constraints; never overrides sources |
| Project Experience Foundation | Integrated Design Proposition and project-wide system relationships derived from product evidence | `draft -> frozen -> superseded` | Qualitative Design DNA, optional Real-World Mapping, content/brand/visual/interaction language, Signature Relationship, Signature Craft, scoped feedback principles and assertions |
| Surface Map | Derived Surface Topology; working index plus retained snapshots | `draft -> frozen -> superseded` | Surfaces, routes, relationships, journeys, roles, responsive transformation and coverage |
| Slice Contract | One user-visible slice | `draft -> frozen -> superseded` | Local experience decisions preserving product semantics |
| Prototype Specification | Compiled exact source revisions plus one candidate decision | immutable bytes; selection/supersession recorded in Discussion/Review | Nothing new; it fixes generation constraints |
| Discussion Prototype | One Specification revision and hypothesis | `generated -> verified` or `blocked` | Nothing; executable evidence only |
| Prototype Review | One target and evidence set | `supported | rejected | inconclusive` | Professional recommendation and actual human decision recorded separately |

The cited product source owns product behavior, roles, permissions, state, data
relationships, Gates and acceptance. The records jointly project one Product
Experience Model; they are not a second product database. The Builder owns only
low-level implementation choices inside its experiment scope. Downstream delivery
owns production implementation.

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
  digests across Foundation, Tokens, Surface Map, Slice Contract, and Specification.
- In this track, bytes are strictly immutable; any subsequent change requires an explicit
  successor revision.

## Canonical paths

```text
prototype/contracts/foundation/<foundation-revision>.md
prototype/contracts/tokens/<tokens-revision>.md
prototype/contracts/surface-maps/<surface-map-revision>.md
prototype/contracts/slices/<slice-id>/<contract-revision>.md
prototype/specifications/<slice-id>/<prototype-revision>.md
prototype/experiments/<slice-id>/<prototype-revision>/
prototype/evidence/<slice-id>/<prototype-revision>/
prototype/reviews/<slice-id>/<prototype-revision>.md
```

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
- Retain a surface-map snapshot before compiling a candidate. Slice Contracts cite its exact path/revision/digest. `prototype/surface-map.md` remains the working index; status updates do not rewrite retained structure.
- User-confirmed Foundation, IA and Specification decisions may precede runnable evidence; validation remains explicitly pending. Prototype execution never supplies user approval.
- The discussion record owns pending decisions and rationale, not a second copy of formal rules; research records own observations, not product truth.

Direction probes are a bounded exception: one viewport from an explicit probe
brief, no full interaction or delivery qualification. They do not require the
formal Slice Contract/Specification chain and cannot replace its evidence.

Token snapshots name their owning Foundation revision and retain exact bytes; token and Foundation revision identifiers need not be equal. Specifications name
the token path and digest; the current `prototype/tokens.md` copy is not an
immutable identity. Preserve the prior snapshot before updating the current copy.
At token freeze, immediately export the retained revision with
`python3 <skill-home>/scripts/export-tokens.py <repository-root>/prototype/contracts/tokens/<revision>.md --output <repository-root>/prototype/contracts/tokens/<revision>.json`.
The main designer may invoke this bounded installed helper through the execution
adapter; JSON is derived packaging, not design authority. A successor uses its own
revision filename. Preserve existing output on failure; never overwrite a different
export or rewrite frozen Markdown to fix packaging. Report a missing export as an
execution limitation until the permitted helper succeeds.

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

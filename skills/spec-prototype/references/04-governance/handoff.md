# Formal prototype evidence and handoff

For an early visual comparison, use [the direction probe dispatch](../01-foundations/design-language.md#direction-probe-dispatch).
This reference is for formal specifications and their implementation.

## Reference set

Before formal generation, read the actual current source facts and exact referenced
bytes. The packet names Foundation revision/digest, retained token path/digest,
Slice Contract revision/digest, immutable candidate Specification, and the retained
surface-map path/digest cited by the Contract. Product/Discussion records retain
the product thesis, object/content/journey basis, Design Proposition, decisions
and approval provenance; downstream artifacts reference that rationale rather
than copy it. The retained Foundation includes the human-readable Qualitative
Design DNA, optional Real-World Mapping and Signature Craft synopsis while the
full causal proposition remains authoritative. Finish source writes before compilation. Use
`python3 <skill-home>/scripts/handoff.py digests --root <repository-root> <paths...>`
to obtain exact reference lines from final bytes. Retain those bytes; later
changes follow the artifact lifecycle. Hashes prove identity, not approval. `prototype/discussion.md` is the working decision index; retain the candidate structure with its draft/approval status inside the canonical compiled spec at `prototype/contracts/compiled/<slice-id>/r1.spec.json` before freeze. Progress-only changes update the working index, not retained snapshots.

Product sources own facts and object/lifecycle meaning; Foundation owns the
integrated Design Proposition and expression system; Surface Map owns topology and
global journeys; Slice Contract owns local behavior and applicability; Specification
owns candidate/execution deltas. Copy none into another authority. A field-level
override must be explicitly permitted by its owner; otherwise create a successor
revision. Foundation cannot freeze independently of exact topology/product
evidence that its proposition relies on. Working records point to these facts and
retain actual approval provenance.

For a spec-only request, provide complete ready or draft specs and remaining
decisions. Actual user selection can freeze a design before implementation; label
prototype/usability validation pending. For a build request, scope the necessary
surfaces and relationships, required interactions, explicitly synthetic fixture
boundaries, viewports, applicable states and validation checkpoints. Start with
the smallest connected journey that answers the question, then expand to the
remaining requested scope; a representative slice is not completion of an
explicitly requested full prototype.

The retained coverage selection is a dispatch input, not a substitute for approval:
binding an explicit scope SHALL NOT be read as authorizing the selected surfaces or
the full product, and an unselected surface stays provisional rather than deleted
or invented. Retain the selected map revision, surfaces, journeys and target
contexts with the packet, and reuse that retained selection when the session
resumes; an ambiguous, invalid or revision-mismatched selection is reconciled
against the current map before any expansion. Only a full-product selection
authorizes expansion across every applicable surface of that revision.

For multiple batches, establish a common runnable entry and compatible shared
data/component references before dispatch. Keep each Builder's write scope
bounded while planning and verifying connections between batches. Exercise
cross-batch navigation, mutation and return; separately styled disconnected
demos are not a complete product. Continue remaining authorized batches when
unblocked, retaining total scope, coverage and the concrete next dependency.

## Builder dispatch

Read [component implementation](../02-craft-methods/component-implementation.md) when preparing a build. In the Specification builder contract, populate the start command, verification commands, page/flow coverage with shared data references, delegated freedoms, and one component-constraint row per applicable surface/interaction; mark uninspected capabilities as unknown. Use dispositions `required | preferred | delegated | unavailable` exactly as the template defines them: reserve `required` for mandatory reuse of a named existing asset with its constraint and verification checkpoint, and keep component choice delegated when nothing is required. Where a component embodies a physical, optical, biomorphic, temporal, or domain-specific mapping, its constraint MUST describe that mapping as a concrete, verifiable, implementable mechanism — never as a literary adjective. A Builder reading the constraint must be able to implement it without guessing the designer's intent. Semantic obligations stay in the Slice Contract and Specification; do not promote implementation preferences into product semantics. Delegate compatible component selection and composition without asking the user to approve an implementation map. Component experience requirements remain in their existing Foundation/Contract owners. Earlier immutable Specifications without this contract fail packet lint with a diagnostic: preserve them unchanged and author a successor revision; do not patch immutable bytes to satisfy the parser.

For formal builds, run
`python3 <skill-home>/scripts/handoff.py packet --root <repository-root> --spec <specification-path>`.
It reads the existing template's reference fields, checks actual digests and
candidate-specific write scopes and cross-file identities, and emits the packet.
The Contract and tokens must name the Specification's Foundation;
Slice/candidate IDs and revision fields must match their retained paths. The
map owns IA: its historical/deferred visual context does not require a new map
revision when its IA meaning is unchanged. Use backticked paths
and `sha256:<64 hex digits>` in reference fields. A formatting error is a
concrete authoring diagnostic, not permission to guess missing references.
Identity fields contain the single revision/ID shown in their template. If a
legacy retained artifact lacks these fields, preserve it and author a successor
with verified identities; do not patch immutable bytes to satisfy the parser.
Give its JSON unchanged to the active host's bounded implementation role; do not
append rewritten page descriptions, assertion IDs, routes or scope overrides.
The Specification and its references own those facts. This check proves neither
user approval nor design quality. Resolve a mismatch at its authoring owner and
rerun the check before execution; semantic similarity does not excuse a digest
mismatch.

Execute exactly once after the packet passes, in the current project workspace,
with the packet as the complete implementation contract. The active host adapter
defines whether this is a bounded subagent or a direct implementation phase and
how native tool restrictions are enforced. It must preserve the packet's exact
repository and write scopes, prevent a parallel duplicate execution, and keep
design-semantic changes outside the build phase. If the host cannot preserve
those invariants, stop with `prototype_blocked`; do not rewrite the packet,
initialize Git, or weaken scope to work around it.

## Freeze approval binding

The freeze command routes by specification shape, and the two paths carry
different field constraints:

- **Canonical path** — `handoff.py freeze --root . --spec prototype/specifications/<slice_id>/r1.spec.md`
  routes to `pillar_packet()`. It emits `contract_disposition: ready` without the
  legacy `Delegated implementation freedoms` disposition machinery, treats the
  multi-file references as optional, and strictly requires only
  `prototype/shared/tokens.css` alongside the specification itself.
- **Legacy path** — `handoff.py freeze --root . --spec prototype/specifications/<slice_id>/r1.md`
  routes to `packet()`, which resolves the six-piece references, requires the Slice
  Contract `Disposition: ready`, and validates per-candidate write scopes.

Both routes then run the same approval binding below against the discussion
record's decision rows; the canonical path is not exempt.

Freeze binds an actual approval decision, not a matching phrase. The retained
record must carry one decision row with status `confirmed | delegated` that names
its approval or delegated-authority source and a locator (turn, original quote,
date or retained source path). A planned, negated or override-only statement
never authorizes freeze, and there is no permissive fallback: a strict packet
failure stays failed, and no `--force` or hook admission manufactures
frozen-approved status. A mismatch is repaired at its authoring owner and the
packet is rerun.

The manifest records the approval binding's decision, scope and retained source
digest. Downstream admission re-verifies those digests, so content changed after
freeze invalidates admission rather than inheriting the older receipt. Freezing a
design scope never exercises implementation: `implementation`, `platform` and
`production` validation stay `pending`, and a spec-only approval retains the
approved design scope while reporting exactly that pending state. Selecting a
ready spec does not require a build.

A denied or timed-out implementation is terminal for that target and checkpoint
unless the host can prove that no external action started. Never retry with a
modified packet merely to bypass a host boundary. Preserve `prototype_blocked`
and continue only with the evidence already available.

The Builder role owns code and low-level layout details within the contract,
never IA, business behavior, source artifacts or production delivery. If the
host cannot execute that role, return the reviewable packet and execution
limitation; do not claim it ran.

At a given review checkpoint, obtain at most one independent Critic review for
the exact target and question. Do not retry or fan out an identical request after
denial or timeout. Preserve the unverified limitation, finish a clearly labeled
non-independent review from available evidence, and surface the next decision;
a Critic is supporting evidence, not a second gate.

Include the resolved skill root so the Builder can read references/templates from the same installation. Accept component-service substitutions that preserve the Specification; send design or interaction conflicts back to the owning decision. Review the Builder's page/state and assertion evidence against the original requested scope, not only the pages it happened to build.

Read [design floor](../03-verification/quality-floor.md) for implementation/inspection. Plan checks against agreed assertions and applicable states. Preserve identity and known platform affordances. If the builder finds a structural impossibility, it reports evidence to this skill for a scoped decision rather than silently redesigning.

## Review, repair and preserve

After the Builder returns runnable artifacts and evidence, start the local gallery
with `node <skill-home>/scripts/preview.mjs <repository-root>` when available, and
include its URL with the review material. This is a revision-labelled artifact
index, not a task sequence: identify the current target and intended journey in
the Review. Follow quality-bar's target-stability rules and the Critic's capture
obligation; do not associate screenshots by similar names or treat historical
evidence as current. Then record findings and the next applicable human choice.
For paired viewport evidence, retain each page/state capture set in its own
directory under the exact candidate evidence scope, or use a shared page-state
filename prefix with viewport suffixes. Unlabelled captures remain unpaired;
filenames never prove freshness or executed behavior on their own.

Use [Review](../../templates/prototype-review.md) to connect actual evidence to the
review question and separately report professional design merit, task/experience
evidence, engineering conformance and human choice. Keep working progress in
`prototype/surface-map.md` and decision/source pointers in
`prototype/discussion.md`; never copy authority into a second status document.
Spec-only selection preserves pending implementation/usability validation.
Finish with exact references, actual coverage and the next unresolved decision
or execution step. Ready specs do not require a build merely to be selected.

Retain raw run results, task-path observations and actual screenshots required by the Specification. Screenshot evidence addresses appearance, not unexercised interaction. No screenshot, human preference, static check or tool receipt alone proves all quality dimensions. Distinguish implementation verified, human selected and usability tested.

Before `verified`, account for reachable-control closure at every required state:
each visible enabled consequential action or exit is exercised, or explicitly
excluded by its source owner. Include cancel/close followed by re-entry because
stale state often makes a later enabled submit or retry silently fail. An enabled
untested branch remains `unverified`; it cannot be hidden by a passing primary
path or aggregate check count.

Use the [quality review cycle](../03-verification/quality-floor.md) for design corrections and the
Builder's bounded attempts for operational failures. Persistent failures keep
artifacts and a concrete `prototype_blocked` result; every failed assertion is
recorded; required failures block implementation verification, while exploratory
failures remain explicit learning. Review failed work to decide what changes;
never relabel a failed assertion as passed merely to proceed. The Critic recommends
an owning revision but cannot approve it.

If a required design assertion itself proves wrong, show the evidence and obtain the needed design decision; create successor artifacts and recheck dependent output. Regeneration stability is unverified until a repeat generation/comparison actually runs. Finish with a concise account of confirmed references, validation coverage, limitations, and next action.

## Before you finish (mistake inversion)

| Mistake | Inversion |
|---|---|
| A Stress Boundary declared with no runnable check for it | Add the check or drop the claim; the Critic treats it as uncovered |
| A constraint written as a literary adjective | Name the mechanism: values, curves, thresholds the Builder can implement |
| A verification checkpoint listed but never executed | Report `Not verified`; an unrun check is never a pass |
| Craft reads digest drifts from actual file contents | Recompute the digest; stale binding silently unbinds the contract |

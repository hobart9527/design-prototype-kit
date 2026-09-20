## Context

The predecessor Change `prototype-coverage-platform-continuity` integrated eight of its nine Tasks into an accepted integration head. The ninth was a zero-write review. It returned a Finding, the Host rewrote that Finding to a recoverable code failure because the frozen verifier of a write-free Task is the passing suite it did not change, and two Attempts exhausted the budget. The exhausted budget routes to an operator decision rather than an authored Finding, so no `FindingRecorded` event exists, the Run holds no successor authority, and every dispatch is already workspace-released so neither abandon nor supersession can present a teardown subject. That Run cannot complete, supersede or abandon, and the repairs it found cannot travel inside it.

The five defects it reported were each reproduced at the source line before this Change was authored. They are real behavioural defects, not test-output inference. This Change repairs them and changes nothing else.

## Goals / Non-Goals

Goals: admit the authored scope at the formal entry; withhold completion for a scope that cannot be completed; make the platform instructions name the projection that exists; let a spec-only approval freeze; leave a runnable check behind for each repair.

Non-Goals: repairing the framework's Finding-admission seam, reopening or archiving the predecessor Change, publishing its delta, adding an agent, a Skill, a dependency or an envelope field, and any paid end-to-end or native validation.

## Decisions

### 1. Repair in a successor rather than the predecessor

The predecessor cannot host its own repair: it has no successor authority, no teardown subject for abandon, and an active Run blocks a replacement approval. Authoring a successor Change is the supported route and costs only a second Change record. The successor's candidate descends from the predecessor's accepted integration head so the repairs build on the eight integrated Tasks instead of reverting them.

Consequence to state plainly: the predecessor's delta was never published, so the successor's delta is the first version of this capability to reach the published specification. The successor therefore restates the corrected contract instead of describing a delta against a published document. The predecessor stays readable and unarchived.

### 2. No task whose deliverable is a Finding

A Task that performs no writes and answers `finding` cannot land that Finding: its frozen verifier is the suite it left untouched, so the Host refutes the Finding and converts it to a retryable code failure. Two of those exhaust the budget into an unanswerable decision. The review work is therefore not a Task. Each repair carries its own focused check, and that check asserts the negative case as well as the corrected one, which is what the review would have verified.

### 3. Authorized widening is not widening

`full-product` is an authorization over every applicable surface of the bound map revision. Comparing its target set against an empty selected list asks whether a surface was added outside the selection, which is the wrong question for an authorization that names no surface. The widening check asks that question only for `selected` coverage. An empty `selected` coverage is still an error, because it authorizes nothing and describes nothing.

### 4. A stale map identity must be reachable

An identity check that no caller can trigger is not a check. The formal entry passes the retained selection's map revision and content digest so that `E010_STALE_CONTRACT` becomes reachable for both coverage modes, and the refusal names the differing identity. Map identity is the selected revision's identity, not the working file's mtime: the retained record is the authority the selection was made against.

### 5. Unusable scope withholds completion everywhere it is read

Completion is derived from obligations, but an unusable scope has no obligations to satisfy, so the derivation returns met. The reconciler treats an unusable context as withholding completion and attaches the governing error; the quality check and the portal refuse to report completion for the same condition. Scope membership, delivery entry and evidence outcomes stay separate facts — the withholding is a fourth derived fact, not a new authority enum.

### 6. Instructions name the projection that exists

The projection emits `platform.target_context`, `platform.prototype_medium`, `platform.verification_environment` and `platform.native_validation_pending` with per-surface applicability. The instructions name those and nothing else. This is contract wiring: the check proves the names agree with the projection, not that a live Critic reasoned well.

### 7. A spec-only freeze is a distinct scope claim

The prototype entry requirement guards a scope that claims prototype implementation. A spec-only approval claims no implementation, so the requirement does not apply to it and its implementation, platform and production validation stay pending. The requirement is not weakened for a scope that does claim a prototype.

## Risks / Trade-offs

- Two Change records with overlapping capability paths may read as duplication: the successor states the corrected contract once and the predecessor stays unarchived and unmodified.
- Admitting `full-product` with an empty surface list could mask a genuinely empty selection: the `selected` branch keeps that refusal, and the digest check still fails a map that drifted.
- Withholding completion may surface on legacy artifacts that predate the fields: the condition is derived from the resolved scope, and a legacy record with no selection is already unresolved rather than usable.
- Instruction-field tests prove naming agreement only: they are labelled as wiring, and no design-quality or live-session claim is made from them.
- The repairs land on a branch that descends from the accepted integration head rather than from the default branch: publication reconciles that basis, and the default branch is left untouched.

## Migration Plan

1. Correct the formal entry's widening and identity checks with their negative fixtures.
2. Correct the reconciler and its two read-only consumers.
3. Correct the two role instructions against the projection.
4. Correct the freeze seam for a spec-only scope.
5. Read the four checks together as the continuity evidence the predecessor's review would have produced.

Legacy artifacts stay readable and are never rewritten by a refusal. Rollback reverts these two source seams and their checks through normal authorized Git workflow without erasing design records.

## Delivery Boundaries

The future implementation Tasks own at most three explicitly named files each plus one focused verification command, and each owns the creation of its own test file. Runtime work is delegated through the existing delivery process after approval; this authoring turn stops after validation and readiness, without candidate commit or implementation. No standalone plan or status document is created outside this native Change.

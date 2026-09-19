## Why

The Change `prototype-coverage-platform-continuity` integrated eight of its nine tasks and left real, reproduced defects in four seams. An independent zero-write review found them and reported them as Findings; the Host refused the Finding because a review task's frozen verifier is the passing test suite, so `FINDING_REFUTED_BY_VERIFIER` downgraded it to a code failure. Two attempts exhausted the budget and the run reached `attempt-limit-reached`, which has no resolver: the run cannot complete, cannot supersede, and cannot abandon. That predecessor cannot carry its own repair.

The defects are real and were confirmed at their source lines, not inferred from test output. This Change carries only the repairs.

## What Changes

- Admit `coverage: full-product` at the formal entry instead of reporting every target surface as widened, and give the formal entry a real expected map identity so a stale revision or digest fails dispatch.
- Withhold completion for an unusable scope in the obligation reconciler, the quality check and the review portal, rather than rendering a met completion for a scope that implements nothing.
- Name the platform fields the Builder and Critic actually receive, replacing a phantom `target_platform` reference with the projected envelope fields.
- Allow spec-only approval to freeze without a prototype entry while still refusing a scope that claims prototype implementation.
- Describe the corrected contract as its own requirements. The predecessor's delta was never published, so these are the first requirements of this capability to reach the published specification; the predecessor remains readable but unarchivable.

## Capabilities

### New Capabilities

- `design-engine/coverage-platform-continuity`: the corrected coverage, platform, evidence and handoff obligations.

### Modified Capabilities

None.

## Impact

- `skills/spec-prototype/scripts/lint_spec_contracts.py`, `assemble_envelope.py`, `prototype_context.py`, `verify_prototype_quality.py`, `generate_review_portal.py`, `handoff.py`.
- `agents/spec-prototype-builder.md`, `agents/spec-prototype-critic.md`.
- Four focused pytest files, one per repair, each asserting the negative case as well as the corrected one.
- No new Skill, dependency, agent, or envelope field. No standalone review task: a task that returns `finding` without a writable deliverable cannot land its Finding, so continuity is verified inside each repair's own check.

## Scope of this delivery

Behavioural requirements and executable implementation tasks only. Do not edit the predecessor Change, approve a delivery, commit, or run paid benchmarks during authoring. Preserve unrelated working-tree changes.

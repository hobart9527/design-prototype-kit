# Benchmark report — daily (candidate-cocreate-ic-r7)

Status: **INCONCLUSIVE**

## Hard gates

- `semantic_fabrication`: 0
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 1
- runs missing provenance: 0
- all 1 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): fbb68c4ffd7ac3d489af7ab8e100d8861cfb5d3c3807d964609630a1f8f07529

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 1 | 0 | None | 0.0 | 0/0/1 | 2.0 | 5.0941 |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **INCONCLUSIVE**


## Unverified (not counted as pass)

- incident-commander/candidate_skill: semantic judge unverified

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | FAIL | 5.0941 | 2 |

Session cost captured across runs: **$5.09** (excludes judge calls and frontend reproduction).

# Benchmark report — daily (candidate-cocreate-ic-r6)

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

- source identity (sha256 of candidate Skill/agent files): 30e56442da7f35ec77754b2bfe0d4bf049f881ee75e4cdd74b0c04b596230c95

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 1 | 0 | None | 1.0 | 0/0/1 | 2.0 | 8.6963 |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **INCONCLUSIVE**


## Unverified (not counted as pass)

- incident-commander/candidate_skill: semantic judge unverified
- incident-commander/candidate_skill: task behaviour unverified

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | PASS | 8.6963 | 2 |

Session cost captured across runs: **$8.7** (excludes judge calls and frontend reproduction).

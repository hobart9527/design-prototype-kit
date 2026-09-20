# Benchmark report — custom (bench-final-validation)

Status: **REGRESSION**

## Hard gates

- `semantic_fabrication`: 2
- `authority_escape`: 2
- `critical_task_break`: 2
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 2
- runs missing provenance: 0
- 0 of 2 runs recorded no provenance

- source identity (sha256 of candidate Skill/agent files): unknown

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 1 | 0 | 0.333 | 0.75 | 0/1/0 | 3.0 | 21.8488 |
| stable_skill | 1 | 1 | 0 | 0.667 | 0.75 | 0/1/0 | 4.0 | 12.6699 |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **PASS**


## Unverified (not counted as pass)

- (none)

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| editorial-reader | candidate_skill | 1 | FAIL | 21.8488 | 3 |
| editorial-reader | stable_skill | 1 | FAIL | 12.6699 | 4 |

Session cost captured across runs: **$34.52** (excludes judge calls and frontend reproduction).

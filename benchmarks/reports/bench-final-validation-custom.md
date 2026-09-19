# Benchmark report — custom (bench-final-validation)

Status: **REGRESSION**

## Hard gates

- `semantic_fabrication`: 0
- `authority_escape`: 1
- `critical_task_break`: 1
- `critical_accessibility_violation`: 0

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 1 | 0 | 0.667 | 0.5 | 0/0/1 | 3.0 | 21.8488 |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **INCONCLUSIVE**


## Unverified (not counted as pass)

- editorial-reader/candidate_skill: semantic judge unverified

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| editorial-reader | candidate_skill | 1 | FAIL | 21.8488 | 3 |

Session cost captured across runs: **$21.85** (excludes judge calls and frontend reproduction).

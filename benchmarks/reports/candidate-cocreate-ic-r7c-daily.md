# Benchmark report — daily (candidate-cocreate-ic-r7c)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill`

Status note: hard gate tripped on candidate_skill while the paired verdict is INCONCLUSIVE: the gate is absolute and fires on the artifacts themselves, while the paired verdict only compares the candidate against the control, so both stand.

## Hard gates

- `semantic_fabrication`: 0
- `authority_escape`: 0
- `critical_task_break`: 1
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 1
- runs missing provenance: 0
- all 1 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 98cb2c7863982e1329c68b56afde5baf82905ad098b1cd38f0e17dedc6b91263

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 0 | 1 | 0.667 | 1.0 | 0/0/1 | 3.0 | 19.2286 |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **INCONCLUSIVE**


## Unverified (not counted as pass)

- incident-commander/candidate_skill: semantic judge unverified
- incident-commander/candidate_skill: session blocked

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | BLOCKED | 19.2286 | 3 |

Session cost captured across runs: **$19.23** (excludes judge calls and frontend reproduction).

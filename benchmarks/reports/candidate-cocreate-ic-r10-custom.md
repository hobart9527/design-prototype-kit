# Benchmark report — custom (candidate-cocreate-ic-r10)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill, stable_skill`

Status note: hard gate tripped on candidate_skill, stable_skill while the paired verdict is PASS: the gate is absolute and fires on the artifacts themselves, while the paired verdict only compares the candidate against the control, so both stand.

## Hard gates

- `semantic_fabrication`: 2
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 2

## Candidate provenance

- runs with recorded provenance: 2
- runs missing provenance: 0
- all 2 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 3a59ff41d749a20c2ac869ab691aa277e9a697d02ddab65813cbd03d7fda6d60, d5205e3d216a0803dbeb28fa856c622ea6db397a87a5d39f2faaf24a8cc7804e

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 0 | 1 | 0.667 | 1.0 | 0/1/0 | 2.0 | 15.4788 |
| stable_skill | 1 | 0 | 1 | 0.667 | 0.75 | 0/1/0 | 2.0 | 16.1156 |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}
- judged pairs: 0; unverified: 0
- agreement concentration (largest outcome share; descriptive only): None
- model-reported confidence (not statistical confidence): {"low": 0, "medium": 0, "high": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **PASS**


## Unverified (not counted as pass)

- incident-commander/candidate_skill: session blocked
- incident-commander/stable_skill: session blocked

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | BLOCKED | 15.4788 | 2 |
| incident-commander | stable_skill | 1 | BLOCKED | 16.1156 | 2 |

## Cost accounting

- session cost captured across runs: **$31.59**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

# Benchmark report — custom (candidate-cocreate-ic-r13)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill, stable_skill`

Status note: hard gate tripped on candidate_skill, stable_skill while the paired verdict is PASS: the gate is absolute and fires on the artifacts themselves, while the paired verdict only compares the candidate against the control, so both stand.

## Hard gates

- `semantic_fabrication`: 2
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 1

## Candidate provenance

- runs with recorded provenance: 2
- runs missing provenance: 0
- all 2 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 3a59ff41d749a20c2ac869ab691aa277e9a697d02ddab65813cbd03d7fda6d60, e36f67548803b197a5b5f1ed9a8ecf9a58a4647defc7843150c66f66f565bf0a

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 0 | 1 | 1.0 | 0.0 | 0/1/0 | 2.0 | 8.1516 |
| stable_skill | 1 | 0 | 1 | 0.667 | 0.75 | 0/1/0 | 1.0 | 0 |

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
| incident-commander | candidate_skill | 1 | BLOCKED | 8.1516 | 2 |
| incident-commander | stable_skill | 1 | BLOCKED | 0.0 | 1 |

## Cost accounting

- session cost captured across runs: **$8.15**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

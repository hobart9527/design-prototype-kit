# Benchmark report — daily (candidate-cocreate-ic-r8b)

Status: **INVALID_CONTROL**

Hard gates tripped on: `stable_skill`

Status note: hard gate tripped on stable_skill while the paired verdict is PASS: the gate is absolute and fires on the artifacts themselves, while the paired verdict only compares the candidate against the control, so both stand.

## Hard gates

- `semantic_fabrication`: 1
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 2
- runs missing provenance: 0
- all 2 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 303dd08ecdbcd2b0390dbdbef4f6632ec536b36d296a6ab6ae55a4f311e660cc, 3a59ff41d749a20c2ac869ab691aa277e9a697d02ddab65813cbd03d7fda6d60

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 0 | 1 | None | 0.25 | 1/0/0 | 1.0 | 0 |
| stable_skill | 1 | 0 | 1 | None | 0.75 | 0/1/0 | 2.0 | 8.0563 |

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
- incident-commander/candidate_skill: task behaviour unverified
- incident-commander/stable_skill: session blocked
- incident-commander/stable_skill: task behaviour unverified

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | BLOCKED | 0.0 | 1 |
| incident-commander | stable_skill | 1 | BLOCKED | 8.0563 | 2 |

## Cost accounting

- session cost captured across runs: **$8.06**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

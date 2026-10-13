# Benchmark report — daily (candidate-cocreate-ic-r53)

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

- source identity (sha256 of candidate Skill/agent files): df73ec3d21e6accf8b8a7df22ffc0ce82406af69dd7a3c8ba490586a94990b95

## Evaluation provenance

Generation provenance above is unchanged by rejudging; judge revisions are recorded separately.
- incident-commander/candidate_skill/run1: initial at 20261012_233514; judges sha256=5448432352efcbccb1cf2c16eb898ee6c26d556772c704210616d9c770286d2f; runner sha256=1f167dc22ec4ec183ccd29292efb5585f52ec6c93fdfabdbf020d3f5fbfb18e2; retained (not rerun)=[]

## Per variant

| variant | runs | completed | blocked | partial | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 1 | 0 | 0 | 0.667 | 0.5 | 1/0/0 | 4.0 | 8.2416 |

## Taste (measured, not asserted)

| variant | slop score | high findings | taste judged | ai-slop fail | category guessable (high) | thesis present | contract blocks fulfilled/absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 3.0 | 1 | 0 | 0 | 0 | 0 | None/None |

Deterministic slop scan runs on every run; the taste and contract-fidelity judges need screenshots and stay unverified when capture did not happen. Divergence verdicts observed: ["not_measured"].

### Co-creation (was the choice offered?)

| variant | measured | asked before building | verdicts |
| --- | --- | --- | --- |
| candidate_skill | 1 | 1 | ["partial"] |

Read from the session transcript: a session that revealed a decision instead of offering one is `reveal_only`, and one that claimed a confirmed lock without ever presenting a candidate is `false_confirmation`.

### Slop findings by rule

| variant | rule | count | severity |
| --- | --- | --- | --- |
| candidate_skill | SLOP-002 | 1 | high |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}
- judged pairs: 0; unverified: 0
- agreement concentration (largest outcome share; descriptive only): None
- model-reported confidence (not statistical confidence): {"low": 0, "medium": 0, "high": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **INCONCLUSIVE**


## Unverified (not counted as pass)

- incident-commander/candidate_skill: runtime authority_status unknown
- incident-commander/candidate_skill: visual taste not measured

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | FAIL | 8.2416 | 4 |

## Cost accounting

- session cost captured across runs: **$8.24**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

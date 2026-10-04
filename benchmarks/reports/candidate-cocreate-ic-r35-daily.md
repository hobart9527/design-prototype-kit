# Benchmark report — daily (candidate-cocreate-ic-r35)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill`

Status note: hard gate tripped on candidate_skill while the paired verdict is INCONCLUSIVE: the gate is absolute and fires on the artifacts themselves, while the paired verdict only compares the candidate against the control, so both stand.

## Hard gates

- `semantic_fabrication`: 1
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 1
- runs missing provenance: 0
- all 1 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): b3ac4c3b2e30319aedb1469a57261b65d3f4cfbd193b94d0622463bd556288df

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 0 | 1 | 1.0 | 0.5 | 0/1/0 | 3.0 | 15.5597 |

## Taste (measured, not asserted)

| variant | slop score | high findings | taste judged | ai-slop fail | category guessable (high) | thesis present | contract blocks fulfilled/absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 8.0 | 1 | 1 | 0 | 1 | 1 | 3.0/0.0 |

Deterministic slop scan runs on every run; the taste and contract-fidelity judges need screenshots and stay unverified when capture did not happen. Divergence verdicts observed: ["not_measured"].

### Co-creation (was the choice offered?)

| variant | measured | asked before building | verdicts |
| --- | --- | --- | --- |
| candidate_skill | 1 | 0 | ["not_measured"] |

Read from the session transcript: a session that revealed a decision instead of offering one is `reveal_only`, and one that claimed a confirmed lock without ever presenting a candidate is `false_confirmation`.

### Slop findings by rule

| variant | rule | count | severity |
| --- | --- | --- | --- |
| candidate_skill | SLOP-002 | 1 | high |
| candidate_skill | SLOP-003 | 1 | medium |
| candidate_skill | SLOP-006 | 1 | medium |
| candidate_skill | SLOP-014 | 1 | low |

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

- incident-commander/candidate_skill: session blocked

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | BLOCKED | 15.5597 | 3 |

## Cost accounting

- session cost captured across runs: **$15.56**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

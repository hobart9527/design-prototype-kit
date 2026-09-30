# Benchmark report — daily (candidate-cocreate-ic-r19)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill, stable_skill`

## Hard gates

- `semantic_fabrication`: 2
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 2
- runs missing provenance: 0
- all 2 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 3a59ff41d749a20c2ac869ab691aa277e9a697d02ddab65813cbd03d7fda6d60, 94df4fd43bbbf8403784b887baf30495bddd2817bfecdc99340c21513ca809ad

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 0 | 1 | 1.0 | 0.5 | 0/1/0 | 3.0 | 19.0418 |
| stable_skill | 1 | 0 | 1 | None | 0.75 | 0/1/0 | 2.0 | 9.5367 |

## Taste (measured, not asserted)

| variant | slop score | high findings | taste judged | ai-slop fail | category guessable (high) | thesis present | contract blocks fulfilled/absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 6.0 | 0 | 1 | 0 | 1 | 1 | 4.0/0.0 |
| stable_skill | 0.0 | 0 | 0 | 0 | 0 | 0 | None/None |

Deterministic slop scan runs on every run; the taste and contract-fidelity judges need screenshots and stay unverified when capture did not happen. Divergence verdicts observed: ["not_measured"].

### Co-creation (was the choice offered?)

| variant | measured | asked before building | verdicts |
| --- | --- | --- | --- |
| candidate_skill | 1 | 0 | ["not_measured"] |
| stable_skill | 1 | 0 | ["not_measured"] |

Read from the session transcript: a session that revealed a decision instead of offering one is `reveal_only`, and one that claimed a confirmed lock without ever presenting a candidate is `false_confirmation`.

### Slop findings by rule

| variant | rule | count | severity |
| --- | --- | --- | --- |
| candidate_skill | SLOP-007 | 1 | low |
| candidate_skill | SLOP-012 | 1 | medium |
| candidate_skill | SLOP-014 | 1 | low |
| candidate_skill | SLOP-017 | 1 | medium |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}
- judged pairs: 0; unverified: 0
- agreement concentration (largest outcome share; descriptive only): None
- model-reported confidence (not statistical confidence): {"low": 0, "medium": 0, "high": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **REGRESSION**

- regression: incident-commander r1 taste stable=0 candidate=6

## Unverified (not counted as pass)

- incident-commander/candidate_skill: session blocked
- incident-commander/stable_skill: session blocked

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | BLOCKED | 19.0418 | 3 |
| incident-commander | stable_skill | 1 | BLOCKED | 9.5367 | 2 |

## Cost accounting

- session cost captured across runs: **$28.58**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

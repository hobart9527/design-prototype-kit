# Benchmark report — daily (candidate-cocreate-ic-r18)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill, stable_skill`

## Hard gates

- `semantic_fabrication`: 2
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 1

## Candidate provenance

- runs with recorded provenance: 2
- runs missing provenance: 0
- all 2 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 3a59ff41d749a20c2ac869ab691aa277e9a697d02ddab65813cbd03d7fda6d60, 63e0026c09d2dc38c6e07809ed270222db64c12f3e2c03128c9a4d7bae36c377

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 1 | 0 | 1.0 | 1.0 | 0/1/0 | 2.0 | 11.0549 |
| stable_skill | 1 | 0 | 1 | 0.667 | 0.75 | 0/1/0 | 3.0 | 18.7746 |

## Taste (measured, not asserted)

| variant | slop score | high findings | taste judged | ai-slop fail | category guessable (high) | thesis present | contract blocks fulfilled/absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 14.0 | 1 | 0 | 0 | 0 | 0 | None/None |
| stable_skill | 16.0 | 0 | 0 | 0 | 0 | 0 | None/None |

Deterministic slop scan runs on every run; the taste and contract-fidelity judges need screenshots and stay unverified when capture did not happen. Divergence verdicts observed: ["not_measured"].

### Co-creation (was the choice offered?)

| variant | measured | asked before building | verdicts |
| --- | --- | --- | --- |
| candidate_skill | 1 | 0 | ["reveal_only"] |
| stable_skill | 1 | 0 | ["not_measured"] |

Read from the session transcript: a session that revealed a decision instead of offering one is `reveal_only`, and one that claimed a confirmed lock without ever presenting a candidate is `false_confirmation`.

### Slop findings by rule

| variant | rule | count | severity |
| --- | --- | --- | --- |
| candidate_skill | SLOP-019 | 2 | medium |
| candidate_skill | SLOP-003 | 1 | medium |
| candidate_skill | SLOP-006 | 1 | medium |
| candidate_skill | SLOP-009 | 1 | high |
| candidate_skill | SLOP-014 | 1 | low |
| candidate_skill | SLOP-023 | 1 | medium |
| stable_skill | SLOP-017 | 3 | medium |
| stable_skill | SLOP-003 | 2 | medium |
| stable_skill | SLOP-006 | 1 | medium |
| stable_skill | SLOP-019 | 1 | medium |
| stable_skill | SLOP-023 | 1 | medium |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}
- judged pairs: 0; unverified: 0
- agreement concentration (largest outcome share; descriptive only): None
- model-reported confidence (not statistical confidence): {"low": 0, "medium": 0, "high": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **REGRESSION**

- regression: incident-commander r1 taste stable=not_measured candidate=reveal_only

## Unverified (not counted as pass)

- incident-commander/stable_skill: session blocked

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | FAIL | 11.0549 | 2 |
| incident-commander | stable_skill | 1 | BLOCKED | 18.7746 | 3 |

## Cost accounting

- session cost captured across runs: **$29.83**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

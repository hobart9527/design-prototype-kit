# Benchmark report — daily (candidate-cocreate-ic-r20)

Status: **INVALID_CONTROL**

Hard gates tripped on: `stable_skill`

Status note: control arm (stable_skill) tripped a hard gate: the stable baseline itself fabricated or escaped authority, so the paired verdict has no sound comparison basis. Re-run with a no_skill control (--variants candidate_skill,no_skill) and treat this report as candidate-side evidence only.

## Hard gates

- `semantic_fabrication`: 1
- `authority_escape`: 0
- `critical_task_break`: 0
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 2
- runs missing provenance: 0
- all 2 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 3a59ff41d749a20c2ac869ab691aa277e9a697d02ddab65813cbd03d7fda6d60, eaef47d006b43b566d6209f25aa2aa205168e48f03a9f921e74726930068c396

## Per variant

| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 1 | 0 | 1 | 1.0 | 0.75 | 1/0/0 | 3.0 | 24.4592 |
| stable_skill | 1 | 0 | 1 | 1.0 | 0.75 | 0/1/0 | 2.0 | 16.013 |

## Taste (measured, not asserted)

| variant | slop score | high findings | taste judged | ai-slop fail | category guessable (high) | thesis present | contract blocks fulfilled/absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 15.0 | 2 | 1 | 0 | 1 | 1 | None/None |
| stable_skill | 10.0 | 2 | 1 | 0 | 1 | 1 | 5.0/0.0 |

Deterministic slop scan runs on every run; the taste and contract-fidelity judges need screenshots and stay unverified when capture did not happen. Divergence verdicts observed: ["divergent", "not_measured"].

### Co-creation (was the choice offered?)

| variant | measured | asked before building | verdicts |
| --- | --- | --- | --- |
| candidate_skill | 1 | 0 | ["not_measured"] |
| stable_skill | 1 | 0 | ["not_measured"] |

Read from the session transcript: a session that revealed a decision instead of offering one is `reveal_only`, and one that claimed a confirmed lock without ever presenting a candidate is `false_confirmation`.

### Slop findings by rule

| variant | rule | count | severity |
| --- | --- | --- | --- |
| candidate_skill | SLOP-014 | 3 | low |
| candidate_skill | SLOP-002 | 2 | high |
| candidate_skill | SLOP-003 | 1 | medium |
| candidate_skill | SLOP-017 | 1 | medium |
| candidate_skill | SLOP-019 | 1 | medium |
| stable_skill | SLOP-002 | 2 | high |
| stable_skill | SLOP-017 | 2 | medium |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}
- judged pairs: 0; unverified: 0
- agreement concentration (largest outcome share; descriptive only): None
- model-reported confidence (not statistical confidence): {"low": 0, "medium": 0, "high": 0}


## Frontend reproduction

- not run for this matrix
## Regression vs stable

verdict: **REGRESSION**

- regression: incident-commander r1 taste stable=10 candidate=15

## Unverified (not counted as pass)

- incident-commander/candidate_skill: session blocked
- incident-commander/stable_skill: session blocked

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| incident-commander | candidate_skill | 1 | BLOCKED | 24.4592 | 3 |
| incident-commander | stable_skill | 1 | BLOCKED | 16.013 | 2 |

## Cost accounting

- session cost captured across runs: **$40.47**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

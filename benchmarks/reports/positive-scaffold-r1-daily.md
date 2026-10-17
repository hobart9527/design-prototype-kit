# Benchmark report — daily (positive-scaffold-r1)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill`

Status note: hard gate tripped on candidate_skill while the paired verdict is INCONCLUSIVE: the gate is absolute and fires on the artifacts themselves, while the paired verdict only compares the candidate against the control, so both stand.

## Hard gates

- `semantic_fabrication`: 2
- `authority_escape`: 0
- `critical_task_break`: 2
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 4
- runs missing provenance: 0
- all 4 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 4800e99ab4a2376869076d3cbe9c7caefdf2460e16be366e1e7b3888772156e1

## Evaluation provenance

Generation provenance above is unchanged by rejudging; judge revisions are recorded separately.
- approval-workflow/candidate_skill/run1: initial at 20261017_133633; judges sha256=9b1d74984549891ad66f42ebeb219ca974d43d26e525633d979b263f2277d492; runner sha256=1ab267d090526f13f151a117b5682b336fadaf11ad12ff87633fe0172fde1091; retained (not rerun)=[]
- content-studio/candidate_skill/run1: initial at 20261017_140554; judges sha256=9b1d74984549891ad66f42ebeb219ca974d43d26e525633d979b263f2277d492; runner sha256=1ab267d090526f13f151a117b5682b336fadaf11ad12ff87633fe0172fde1091; retained (not rerun)=[]
- editorial-reader/candidate_skill/run1: initial at 20261017_143341; judges sha256=9b1d74984549891ad66f42ebeb219ca974d43d26e525633d979b263f2277d492; runner sha256=1ab267d090526f13f151a117b5682b336fadaf11ad12ff87633fe0172fde1091; retained (not rerun)=[]
- mobile-booking/candidate_skill/run1: initial at 20261017_131940; judges sha256=9b1d74984549891ad66f42ebeb219ca974d43d26e525633d979b263f2277d492; runner sha256=1ab267d090526f13f151a117b5682b336fadaf11ad12ff87633fe0172fde1091; retained (not rerun)=[]

## Per variant

| variant | runs | completed | blocked | partial | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 4 | 4 | 0 | 3 | 0.5 | 0.417 | 2/2/0 | 3.75 | 67.0574 |

## Taste (measured, not asserted)

| variant | slop score | high findings | taste judged | ai-slop fail | category guessable (high) | thesis present | contract blocks fulfilled/absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 0.75 | 0 | 0 | 0 | 0 | 0 | None/None |

Deterministic slop scan runs on every run; the taste and contract-fidelity judges need screenshots and stay unverified when capture did not happen. Divergence verdicts observed: ["not_measured"].

### Co-creation (was the choice offered?)

| variant | measured | asked before building | verdicts |
| --- | --- | --- | --- |
| candidate_skill | 4 | 3 | ["partial", "reveal_only"] |

Read from the session transcript: a session that revealed a decision instead of offering one is `reveal_only`, and one that claimed a confirmed lock without ever presenting a candidate is `false_confirmation`.

### Slop findings by rule

| variant | rule | count | severity |
| --- | --- | --- | --- |
| candidate_skill | SLOP-023 | 2 | low |
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

- approval-workflow/candidate_skill: runtime authority_status unknown
- approval-workflow/candidate_skill: runtime method_router unknown
- approval-workflow/candidate_skill: visual taste not measured
- content-studio/candidate_skill: visual taste not measured
- editorial-reader/candidate_skill: runtime authority_status unknown
- editorial-reader/candidate_skill: visual taste not measured
- mobile-booking/candidate_skill: runtime authority_status unknown
- mobile-booking/candidate_skill: visual taste not measured

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| approval-workflow | candidate_skill | 1 | FAIL | 7.8099 | 3 |
| content-studio | candidate_skill | 1 | FAIL | 26.3402 | 5 |
| editorial-reader | candidate_skill | 1 | FAIL | 18.0288 | 3 |
| mobile-booking | candidate_skill | 1 | FAIL | 14.8785 | 4 |

## Cost accounting

- session cost captured across runs: **$67.06**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

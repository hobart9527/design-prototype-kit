# Benchmark report — daily (20261020-daily-r16)

Status: **REGRESSION**

Hard gates tripped on: `candidate_skill, stable_skill`

## Hard gates

- `semantic_fabrication`: 2
- `authority_escape`: 0
- `critical_task_break`: 5
- `critical_accessibility_violation`: 0

## Candidate provenance

- runs with recorded provenance: 8
- runs missing provenance: 0
- all 8 runs recorded provenance

- source identity (sha256 of candidate Skill/agent files): 5d05e563857ff03231d2498cc19281a2fc1c76c2fb231bcd22bde812ad55b959, b0403aef7df6f4e8516b8143689b79e3bbca5f37e8cd95ff508bb29aa827abf2

## Evaluation provenance

Generation provenance above is unchanged by rejudging; judge revisions are recorded separately.
- approval-workflow/candidate_skill/run1: initial at 20261020_090054; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]
- approval-workflow/stable_skill/run1: initial at 20261020_092701; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]
- content-studio/candidate_skill/run1: initial at 20261020_095649; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]
- content-studio/stable_skill/run1: initial at 20261020_103140; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]
- editorial-reader/candidate_skill/run1: initial at 20261020_110035; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]
- editorial-reader/stable_skill/run1: initial at 20261020_112907; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]
- mobile-booking/candidate_skill/run1: initial at 20261020_115810; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]
- mobile-booking/stable_skill/run1: initial at 20261020_121045; judges sha256=cb7e39ce54b8e9979803cc4a66dd3c15c1a5844709b2f50581a154d7fadab9a5; runner sha256=6b552ee5e62d7ba5cedaf92d43bf2f53cda2019bf2892c97950e57ea363b1ec4; retained (not rerun)=[]

## Per variant

| variant | runs | completed | blocked | partial | task success | method recall | semantic pass/fail/unverified | turns | cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 4 | 3 | 0 | 4 | 0.5 | 0.75 | 3/1/0 | 4.75 | 85.2689 |
| stable_skill | 4 | 3 | 0 | 2 | 0.542 | 0.583 | 3/1/0 | 4.5 | 85.2822 |

## Taste (measured, not asserted)

| variant | slop score | high findings | taste judged | ai-slop fail | category guessable (high) | thesis present | contract blocks fulfilled/absent |
| --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_skill | 3.5 | 3 | 0 | 0 | 0 | 0 | None/None |
| stable_skill | 5.75 | 4 | 0 | 0 | 0 | 0 | None/None |

Deterministic slop scan runs on every run; the taste and contract-fidelity judges need screenshots and stay unverified when capture did not happen. Divergence verdicts observed: ["divergent", "not_measured"].

### Co-creation (was the choice offered?)

| variant | measured | asked before building | verdicts |
| --- | --- | --- | --- |
| candidate_skill | 4 | 3 | ["not_measured", "partial"] |
| stable_skill | 4 | 3 | ["partial", "reveal_only"] |

Read from the session transcript: a session that revealed a decision instead of offering one is `reveal_only`, and one that claimed a confirmed lock without ever presenting a candidate is `false_confirmation`.

### Slop findings by rule

| variant | rule | count | severity |
| --- | --- | --- | --- |
| candidate_skill | SLOP-009 | 2 | high |
| candidate_skill | SLOP-003 | 1 | medium |
| candidate_skill | SLOP-004 | 1 | high |
| candidate_skill | SLOP-012 | 1 | medium |
| candidate_skill | SLOP-021 | 1 | low |
| stable_skill | SLOP-004 | 7 | high |
| stable_skill | SLOP-014 | 1 | low |
| stable_skill | SLOP-021 | 1 | low |

## Pairwise (blind)

{"alpha_wins": 0, "beta_wins": 0, "tie": 0}
- judged pairs: 0; unverified: 0
- agreement concentration (largest outcome share; descriptive only): None
- model-reported confidence (not statistical confidence): {"low": 0, "medium": 0, "high": 0}


## Frontend reproduction

- not run for this matrix
## Unmeasured dimensions

- approval-workflow/candidate_skill: taste not measured
- approval-workflow/stable_skill: taste not measured
- content-studio/candidate_skill: taste not measured
- content-studio/stable_skill: taste not measured
- editorial-reader/candidate_skill: taste not measured
- editorial-reader/stable_skill: taste not measured
- mobile-booking/candidate_skill: taste not measured
- mobile-booking/stable_skill: taste not measured
## Regression vs stable

verdict: **REGRESSION**

- regression: approval-workflow r1 semantic stable=pass candidate=fail
- regression: approval-workflow r1 task stable=pass candidate=fail
- regression: content-studio r1 taste stable=1 candidate=3
- regression: editorial-reader r1 runtime stable=pass_with_unknowns candidate=fail
- regression: editorial-reader r1 taste stable=0 candidate=2

## Unverified (not counted as pass)

- approval-workflow/candidate_skill: runtime authority_status unknown
- approval-workflow/candidate_skill: visual taste not measured
- approval-workflow/stable_skill: runtime authority_status unknown
- approval-workflow/stable_skill: runtime method_router unknown
- approval-workflow/stable_skill: visual taste not measured
- content-studio/candidate_skill: runtime authority_status unknown
- content-studio/candidate_skill: visual taste not measured
- content-studio/stable_skill: runtime authority_status unknown
- content-studio/stable_skill: visual taste not measured
- editorial-reader/candidate_skill: runtime authority_status unknown
- editorial-reader/candidate_skill: runtime document_lang unknown
- editorial-reader/candidate_skill: visual taste not measured
- editorial-reader/stable_skill: runtime authority_status unknown
- editorial-reader/stable_skill: visual taste not measured
- mobile-booking/candidate_skill: runtime authority_status unknown
- mobile-booking/candidate_skill: visual taste not measured
- mobile-booking/stable_skill: runtime authority_status unknown
- mobile-booking/stable_skill: visual taste not measured

## Runs

| case | variant | repeat | status | cost USD | turns |
| --- | --- | --- | --- | --- | --- |
| approval-workflow | candidate_skill | 1 | FAIL | 21.7451 | 6 |
| approval-workflow | stable_skill | 1 | INCONCLUSIVE | 26.1406 | 6 |
| content-studio | candidate_skill | 1 | INCONCLUSIVE | 22.6366 | 4 |
| content-studio | stable_skill | 1 | FAIL | 18.8341 | 4 |
| editorial-reader | candidate_skill | 1 | FAIL | 21.5985 | 4 |
| editorial-reader | stable_skill | 1 | FAIL | 26.9945 | 5 |
| mobile-booking | candidate_skill | 1 | FAIL | 19.2887 | 5 |
| mobile-booking | stable_skill | 1 | FAIL | 13.313 | 3 |

## Cost accounting

- session cost captured across runs: **$170.55**
- pairwise judge cost recorded: **$0** (0 recorded; 0 missing)
- frontend reproduction cost recorded: **$0** (0 recorded; 0 missing)
- Missing cost records mean total spend is incomplete; they are not treated as zero.

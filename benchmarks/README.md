# Automated Benchmark Harness

Real Claude Code sessions in isolated workspaces, independent judges, one report.

## Command entry points

```bash
# daily regression (2 cases, skill variants only)
python benchmarks/runners/run_matrix.py --suite daily --variants stable_skill,candidate_skill --repeats 1

# golden suite with evidence
python benchmarks/runners/run_matrix.py --suite golden --repeats 3 --task-trace --visual --pairwise

# release verification (adds frontend reproduction)
python benchmarks/runners/run_matrix.py --suite release --repeats 3 --task-trace --visual \
  --pairwise --frontend-reproduction
```

Useful flags: `--cases a,b` (instead of `--suite`), `--max-turns`, `--timeout`, `--budget-usd`,
`--report-only` (re-aggregate an existing run), `--run-id`.

## Layers (never conflated)

| layer | runner | evidence it may claim |
| --- | --- | --- |
| mechanism | `pytest tests/` | compile / materialise / token checks only |
| session | `runners/run_case.py`, `runners/run_claude_session.py` | what a real isolated Claude Code session produced |
| judge | `judges/*` | semantic fidelity, runtime mechanics, tasks, contract, pairwise |

The mechanism layer lives in the pytest suite (`tests/test_pipeline.py`, `tests/test_tokens.py`,
`tests/test_canonical_ontology.py`), which drives `skills/spec-prototype/scripts` directly. It has
no separate runner and no benchmark cases of its own.

## Flow

```
case.yaml + brief.md ──► PREPARE (workspace in /tmp/design-bench/<case>/<variant>/<run>)
                            │   .claude/skills/spec-prototype -> variant skill
                            │   .claude/agents/*             -> variant agents
                            ▼
                        GENERATE (real `claude -p` turns; mock user + counterfactual events)
                            ▼
                        COLLECT  (prototype/ copied to results/<run>/<case>/<variant>/runN/artifacts)
                            ▼
                        VERIFY   runtime_judge + semantic_judge (+ task trace + screenshots)
                            ▼
                        RESULT   run-result.json  ──►  reports/<run-id>-<suite>.md
```

## Variants

| variant | skill source |
| --- | --- |
| `no_skill` | none (control) |
| `stable_skill` | `benchmarks/baselines/<tag>/`, rebuilt on demand from the `git_rev` in its `MANIFEST.json` |
| `candidate_skill` | live `skills/spec-prototype` + `agents/` working tree |

Freeze a new baseline before comparing anything: `python benchmarks/runners/freeze_baseline.py --tag vX`.
Only `MANIFEST.json` is committed — the frozen tree is derived data, rebuilt from the recorded `git_rev`
and sha256-verified on every use, so a tampered or stale cache is rejected rather than silently compared
against. Committing the whole tree would store the same bytes twice and let the copy drift from the rev
it claims to be. Freezing a dirty working tree is refused (`--force` overrides) because the recorded rev
would not reproduce it.

## Isolation rules

- Sessions run in a throwaway workspace outside the repo, with `--setting-sources project`, so
  user-level skills, plugins and CLAUDE.md never load. `spec-prototype` is the only design skill present.
- The workspace receives `brief.md` and the variant skill. `ground-truth.yaml`, `rubric.yaml`,
  `mock-user.md` and `tasks.yaml` are never copied in; they stay with the judges.
- Auth/model env from `~/.claude/settings.json` is re-injected into the child process because
  `--setting-sources project` drops it. Secrets are never written to artifacts.
- Workspaces are never reused: `prepare_workspace` refuses an existing directory.
- The skill and agents are **copied** into the workspace, never symlinked: a symlinked
  skill resolves `__file__` back into the repo and lets session helper scripts write repo
  files (see `benchmarks/results/bench-20260919-0108-r3/ISOLATION-CAVEAT.md`).
- `sessions run with bypassPermissions`; workspaces are disposable and hold no real data.

## Hard gates

Promotion is blocked when any run shows: semantic fabrication, authority escape, critical task
break, or a critical accessibility violation. Unknown/unverified dimensions are reported as
unverified and never counted as passes.

## Regression specimen: review page to full product (opt-in, own cost authorization)

A bounded, copy-paste specimen for one regression question: does a candidate keep working once
the same product is expanded from one reviewed page to full scope? It drives the existing runners
only — no extra orchestration layer — and every step below has been run before, one step at a time.
It is **not** part of `daily`/`golden` and it is **not** implied by a green mechanism run.

```bash
# 1. representative review: one page / one surface, control vs candidate
python benchmarks/runners/run_matrix.py --cases <case> --variants stable_skill,candidate_skill \
  --repeats 1 --run-id specimen-review

# 2. same product, explicitly expanded to full scope (same case, same run id family)
python benchmarks/runners/run_case.py --case <case> --variant candidate_skill --repeat 1 \
  --matrix-dir benchmarks/results/specimen-review --task-trace --visual --open

# 3. re-aggregate both arms into one report and read provenance before the verdict
python benchmarks/runners/aggregate_report.py --matrix-dir benchmarks/results/specimen-review \
  --suite custom --run-id specimen-review
```

What the specimen pins:

- **Source and conditions.** The report's `## Candidate provenance` section records the sha256 of
  the candidate Skill/agent files that actually ran, dirty tree included, plus the judge inputs for
  the run. A reported Git revision alone does not identify a dirty candidate; compare
  `source_identity` between arms before reading any preference.
- **Cross-page state and return.** Trace the same state through the reviewed page, one step away
  from it, and back. A pass on the reviewed page does not carry; the return path is its own claim.
- **Mobile adaptation.** Capture the required viewports (`--visual`) and judge them; a desktop-only
  capture leaves the mobile dimension unverified.
- **Unverified stays unverified.** Native-app simulation has no harness behind it. It is recorded as
  unverified and never counted as a pass, however many mechanism checks are green.

Boundaries: no new cases, and no paid session runs are part of this task. The commands above cost
real session budget when executed; run them only under explicit cost authorization. Nothing here
asserts those sessions were run for this Change.

## Not implemented yet (P2)

Diversity clustering across cases, Five-Axes expression stress, holdout unlock policy, historical
dashboard. Add them when a real failure needs them, not before.

## Operational notes (measured on 2026-09-19)

- **Long sessions need continuation.** The CLI caps agent turns per call (`--max-turns`), so the
  session runner resumes the same session with a neutral `继续。` when a call ends at `max_turns`
  or at the per-call budget. `--max-turns` is per call; the loop cap, wall clock and
  `--session-budget-usd` bound the whole session.
- **Cost envelope (editorial-reader, one run per variant):** control `no_skill` $8.69 / 3 calls;
  `stable_skill` $16.26 / 3 calls and still unfinished; independent frontend reproduction $3.61.
  Budget roughly $15-25 per skill session and $5-10 per judge pass.
- **Vision judging is the expensive path.** A pairwise call that re-read four screenshots across
  several turns cost $8.40 before the harness was fixed; the judge now receives one viewport per
  candidate and a $2 per-call budget. Total spend for the first landing (14 session runs, all
  judge passes and one frontend reproduction): about **$90**.
- **Never treat a CLI error envelope as a verdict.** `parse_result_payload` keeps the envelope out
  of `result`, so a judge that runs out of turns is reported unverified instead of parsing the
  envelope's JSON as if it were its answer.
- **Model judges are non-deterministic.** The same artifacts scored differently across passes
  (0 vs 2 fabricated capabilities). Treat small deltas as noise, keep all attempts, and raise
  repeats before acting on a difference (BENCH-004).
- **This machine routes Claude Code through a third-party gateway**
  (`ANTHROPIC_BASE_URL` in `~/.claude/settings.json`), so `model` in run results is the gateway's
  model name, not an Anthropic model. `matrix-plan.json` records the router host for every run.
- **Re-judging is free of sessions:** `run_matrix.py ... --rejudge` re-runs judges over collected
  artifacts; previous results are kept as `run-result-prev<N>.json`.
- **Judge strictness is calibrated, not neutral:** deterministic forbidden-term hits are recorded
  as signals for human review, negation-aware, and no longer force a gate on their own. The
  authority check fails a run that declares `frozen`/`frozen_approved` when the case ceiling is
  `sealed_provisional` and no user approval appears in the session transcript.

## Plan of record

`openspec/changes/archive/2026-09-18-spec-prototype-benchmark-fidelity/` is the closed Change that
built this harness. The pre-existing `PLAN-automated-benchmark.md` and the legacy `run_benchmark.py`
mechanism driver were removed once `runners/` and `judges/` superseded them.

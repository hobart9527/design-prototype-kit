# Benchmark skill-source integrity

## Why

A frozen benchmark workspace built from the current 37-file skill tree (no
`SKILL.md`, no `CONTEXT.md`, no `references/core-workflow.md`, empty
`templates/`) was measured as the `candidate_skill` arm and reported as a normal
run. The published benchmark result is therefore a reading of a skill with no
entry point, and nothing in the harness said so.

`variant_sources("candidate_skill")` returns the live working tree
`ROOT/skills/spec-prototype`, and `prepare_workspace` copies whatever it finds.
The only integrity assertion on a resolved skill source,
`tests/test_benchmark_harness.py:51`, runs on the `stable_skill` path alone, so
an incomplete candidate source cannot fail a run. `stable_skill` is not covered
either: `ensure_baseline` verifies the cached tree only when the directory
exists, so an absent tree restores from `git archive` and is never checked for
completeness.

## What changes

`variant_sources` raises `BenchBlocked` naming the resolved path and the
missing required entries when a resolved, non-`no_skill` skill source lacks a
documented integrity contract: the `SKILL.md` entry point, the `CONTEXT.md`
router it points at, `references/core-workflow.md`, and a non-empty
`templates/`. The check runs inside `variant_sources`, so every caller —
`prepare_workspace`, `run_matrix`, the CLI — is covered instead of only the
workspace path, and no incomplete source can silently become an arm.

The `stable_skill` baseline tree is additionally checked with the same contract
after the restore path, so a baseline that is present but incomplete is refused
rather than measured.

## Non-goals

- The harness does not detect or attribute deletions. It refuses to measure a
  tree that is not a usable skill.
- No fabricated `SKILL.md` is written into the workspace to let a broken source
  produce a run.
- The integrity contract is not derived from the baseline `MANIFEST.json`. A
  complete baseline legitimately lacks the in-flight manifests of the working
  tree, so a manifest-shaped check would refuse a valid control arm.
- `no_skill` is unchanged: it resolves no skill and is exempt by definition.

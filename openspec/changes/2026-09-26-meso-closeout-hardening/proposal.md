# Change: 2026-09-26-meso-closeout-hardening

## Why

The 2026-09-25-progressive-contracts-consumer-alignment change landed the
progressive schema tiers, meso slots, one-way token derivation and builder/critic
meso consumption. Three closeout items from
`docs/spec-prototype-co-creation-optimization-plan.md` remain:

1. `skills/spec-prototype/references/core-workflow.md` is retired as an active
   router (tests lock active loading paths against it), but the benchmark
   harness still requires it as a skill-contract entry
   (`benchmarks/runners/bench_lib.py:206` `REQUIRED_SKILL_ENTRIES`), and the
   physical file still sits in the tree as if it were live.
2. `assemble_envelope.py` derives mandatory inspection viewports only from the
   authored `device_context` ladder (`_mandatory_viewports`), ignoring the
   authored `scope.verification_scope.viewports` from the Canonical Spec IR. A
   spec that explicitly binds e.g. 1440/1024 viewports is inspected at the
   device defaults instead, producing a false-negative gate.
3. `agents/spec-prototype-critic.md` already judges cognitive quality but has
   no explicit L1/L2/L3 tiered evidence protocol. When a headless style engine
   is unavailable (L2/L3 unreachable), the critic has no written rule for
   degrading gracefully instead of blocking or silently skipping.

## What Changes

- **T-01 core-workflow retirement stub**: replace the retired
  `references/core-workflow.md` body with a short retirement stub that names
  the current owners (`SKILL.md` entry, `references/core-kernel.md` guardrails,
  `references/stages/` stage bodies). Switch
  `benchmarks/runners/bench_lib.py` `REQUIRED_SKILL_ENTRIES` from
  `references/core-workflow.md` to `references/core-kernel.md`, and update the
  `tests/test_benchmark_harness.py` fixture accordingly.
- **T-02 authored-viewport precedence**: `_mandatory_viewports` gains an
  authored-viewports parameter. When the Canonical Spec IR declares
  `scope.verification_scope.viewports`, those widths win and the device ladder
  is only the fallback for specs that declare no explicit viewport set. The
  `inspection_contract.mandatory_viewports` and the `capture.mjs` command both
  consume the precedence-resolved list.
- **T-03 critic tiered evidence protocol**: inject an explicit
  L1 (DOM/ARIA/`data-state` structural checks) → L2 (computed-style checks) →
  L3 (headless screenshot comparison) degradation protocol into
  `agents/spec-prototype-critic.md`, mirroring the tiered chain already
  implemented in `scripts/verify_prototype_quality.py`. A missing style engine
  degrades the run to the reachable tier and is reported as
  `environment_not_ready` with the tier reached — never silently skipped and
  never a code-assertion failure. Only L1 failures block.

## Non-Goals

- No recovery of core-workflow as an active authority; active loading paths
  stay locked by existing tests.
- No modification of frozen baselines, historical reports, or archived changes.
- No change to the progressive schema tiers, meso slots, or one-way token
  derivation landed by the previous change.

## Impact

- Benchmark harness accepts the current skill tree shape without requiring the
  retired router file.
- Authored verification viewports become authoritative for inspection and
  capture, removing false-negative viewport gates for specs with explicit
  viewport declarations.
- Critic reviews remain deterministic across environments with and without a
  headless browser: degraded tiers are explicit, L1 semantic validation always
  runs.

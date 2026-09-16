## Context

The repository provides the industrial design system and interactive prototype toolkit (`design-prototype-kit`). To transition from ad-hoc design notes to an immutable, reproducible pipeline, the kit formalizes five progressive stages—魂 (Sense-making), 骨 (Topology), 皮 (Probes), 根 (Contracts), and 鉴 (Critique)—backed by deterministic verification tooling and tests.

## Goals / Non-Goals

**Goals:**
- Unify the canonical 5-stage lifecycle across documentation, guidelines, and agent prompts.
- Ensure runtime verification scripts (`export-tokens.py`, `check-assertions.py`, `handoff.py`, `execution_boundary.py`) exist and pass automated test suites.
- Guarantee full test coverage and passing runs for `tests/test_tokens.py` and `tests/test_pipeline.py`.

**Non-Goals:**
- Production backend API implementation (the kit governs experience design and prototype artifacts).
- Heavy external testing frameworks (assert-based pytest harnesses remain lightweight and self-contained).

## Decisions

### Decision 1: Structure and maintain verification scripts in canonical locations
The verification harness scripts (`handoff.py`, `check-assertions.py`, `export-tokens.py`, `execution_boundary.py`) belong under `skills/spec-prototype/scripts/` to satisfy test runner imports while allowing top-level references.
- *Alternatives considered*: Inlining logic directly in test files (rejected: loses CLI utility for CI/CD and pre-tool-use hooks).

### Decision 2: W3C DTCG Token format standard
Tokens parsed from markdown tables are converted to standard W3C Design Tokens Community Group (DTCG) format with `$value` mappings.
- *Alternatives considered*: Flat key-value JSON (rejected: does not conform to DTCG specification and misses token metadata).

### Decision 3: Strict exact-match assertion evaluation
Assertion checking treats full sentences and falsifiable anchors as exact matches, refusing to let loose substring prefixes mask downstream failures.
- *Alternatives considered*: Fuzzy regex matching (rejected: leads to false-positive completions on partial tests).

## Risks / Trade-offs

- [Missing script dependencies break test runs] → Mitigation: Restore and verify `handoff.py`, `check-assertions.py`, `export-tokens.py`, and `execution_boundary.py` within the task implementation scope.
- [Token table syntax variations] → Mitigation: Test and support both two-column and multi-column markdown table layouts.

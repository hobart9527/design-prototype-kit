# Proposal: Align Spec Contract Seams, Quality Gate Assertions, and Execution Boundary

## Why

Review of the 5-Stage Design Delivery Engine identified three systemic friction points between contract translation scripts and terminal agent execution:

1. **Topology Navigation Deadlock**: `assemble_envelope.py` and `coverage_failures` instruct the Builder that undelivered sibling surfaces must render as disabled affordances with `href: None` to avoid 404 navigation defects. However, `verify_prototype_quality.py:455` strictly required `href=...{sibling}...` in the DOM for all siblings, causing a deadlock whenever a multi-surface map is built slice-by-slice.
2. **Execution Boundary Whitelist Gaps**: `SKILL.md` and `core-workflow.md` prescribe headless checks via `node wcag-check.js` and `check-assertions.py`, but `execution_boundary.py` omitted both from its permitted script whitelist, triggering an unexpected `ValueError` when invoked in the active designer session.
3. **Agent Guidance Alignment**: `agents/spec-prototype-builder.md` lacked explicit instructions for disabled navigation affordances and the Zero Naked Metrics craft floor, risking unconsidered rejections during automated verification.

## What Changes

- `verify_prototype_quality.py`: Update the topology assertion to distinguish delivered siblings (which must have valid relative `href` links) from undelivered siblings (which must be represented as disabled affordances or text labels without live links).
- `execution_boundary.py`: Add `wcag-check.js` to `permitted['node']` and `check-assertions.py` to `permitted['python3']`/`permitted['python3.14']`.
- `agents/spec-prototype-builder.md`: Explicitly instruct the Builder to render disabled affordances for undelivered sibling surfaces, and add the Zero Naked Metrics requirement (unit context, reference baseline, trend delta, or sparklines/meter).
- `tests/test_pipeline.py`: Add regression tests verifying that prototypes with undelivered siblings pass quality assertions when rendered as disabled affordances, and that the execution boundary admits `wcag-check.js` and `check-assertions.py`.

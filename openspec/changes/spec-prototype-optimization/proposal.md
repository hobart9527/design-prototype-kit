# Proposal: Complete spec-prototype optimization delivery

## Why

The current working tree contains the completed canonical IR consolidation and architectural hardening for `spec-prototype`. The changes require one governed delivery record so the implementation can be verified and published as one coherent revision.

## What Changes

- Make `r1.spec.json` the machine authority for canonical specification assembly and coverage decisions.
- Enforce stage boundaries and load explicit Stage 3/4 verification fragments without fabricated defaults.
- Harden execution-boundary admission, canonical JSON Schema linting, WCAG preflight, and freeze evidence integrity.
- Retire obsolete helper paths and preserve compatibility artifacts only as explicitly demoted legacy inputs.
- Publish the verified repository revision to GitHub.

## Non-Goals

- No new product behavior beyond the current working-tree changes.
- No redesign of unrelated repository components.
- No destructive cleanup of unrelated user changes.

## Anchors

- `skills/spec-prototype/scripts/assemble_envelope.py:_canonical_contract_lint`
- `skills/spec-prototype/scripts/compile_spec_ir.py:compile_canonical_ir`
- `skills/spec-prototype/scripts/lint_spec_contracts.py:lint_canonical_spec_ir`
- `skills/spec-prototype/scripts/execution_boundary.py:check`
- `prototype/contracts/compiled/sample-gate/state_model.slice.json`

# Proposal: P0 Seam Fixes & Pipeline Purification

## Motivation

An audit of the current design prototype compilation harness reveals four critical seam leaks that pollute generated contracts and envelopes with unauthored assumptions:
1. **P0-1 Unauthored Universal Invariants in f1/r1**: `materialize_contracts.py` hardcodes `invariants: concentric-radii, tabular-numerics, touch-target-floor, break-protocol` in `f1.md` and `r1.md` prototype context blocks regardless of whether these were authored.
2. **P0-2 Domain & Input Modality Inventions in Materializer Ergonomics**: `materialize_contracts.py` automatically injects domain-specific assumptions (e.g. `reservation card`, `historical booking steps`, `Space or P`, `J / K`, `rapid Space hits`) into the specification ergonomics table and break protocol, poisoning diverse domains (such as editorial readers or workbench tools).
3. **P0-3 Buzzword Pollution in Cognitive Budgeting Ledger**: `materialize_contracts.py` injects unauthored jargon (`tactile detents`, `micro-sparklines`, `kinetic pulses`, `10x situational awareness`) when the Cognitive Ledger is unauthored, instead of preserving semantic neutrality (`unspecified`).
4. **P0-4 Token Compilation Authority Seam**: In formal mode, `compile_tokens.py` merges un-materialized raw `discussion.md` text with `f1.md`, bypassing the sealed foundation contract. In formal mode, token compilation must strictly read the sealed foundation record (`f1.md` / successor foundation) only. Any new decisions authored in discussion must be materialized into a successor foundation first.

## Scope of Changes

- `skills/spec-prototype/scripts/materialize_contracts.py`:
  - Remove hardcoded universal invariants (`concentric-radii`, `tabular-numerics`, `touch-target-floor`) from `f1.md` and `r1.md` context blocks unless explicitly authored.
  - Remove domain-specific ergonomics templates (`reservation card`, `Space or P`, `J / K`, `historical booking steps`, `rapid Space hits`). Use domain-neutral ergonomics or mark as `unspecified` if absent.
  - In `extract_cognitive_ledger` and the c1 contract, output `unspecified` for unauthored ledger zones rather than fabricating tactile/sparkline/kinetic claims.
- `skills/spec-prototype/scripts/assemble_envelope.py`:
  - Align envelope assembly so it does not presume universal concentric-radii or tabular-numerics invariants.
- `skills/spec-prototype/scripts/compile_tokens.py`:
  - In `formal` mode, ensure `_resolve_token_source` reads exclusively from the sealed foundation record without appending un-materialized discussion text.
- `tests/`:
  - Update `tests/test_platform_envelope.py`, `tests/test_contract_seam_fidelity.py`, `tests/test_pipeline.py`, and `tests/test_tokens.py` to verify truthful compilation and test fidelity.

# Proposal: Executable IR Semantic Correctness and Envelope Decoupling

## Why

The 7-field executable design IR established in `6e0dbde` structured the design contract, but semantic translation and prompt payload currently exhibit critical seams:
1. Reality anchors are parsed as a raw string and iterated character-by-character (`str` iteration bug), yielding single-letter sources.
2. Experience states (`empty`, `error`, etc.) are synthesized and injected into `domain_states` masquerading with `authority: explicit`.
3. An unauthored topology fallback synthesizes a rigid `primary_workspace` + `contextual_inspector` region split instead of delegating `spatial-topology` to `open_design_space`.
4. Action contracts inject synthetic `ui_transient_states: ["submitting", "failed"]` and infer `role: "primary-action"` by index order rather than authored semantics.
5. `projection_digest` hardcodes `"compiled"` and `"unmapped_sections": "none"` without auditing source sections.
6. Five Axes reads raw unmaterialized `discussion.md`, re-introducing authority seams against `f1.md`, while referencing non-existent `--text-base`.
7. Builder envelope retains legacy duplicated payloads alongside canonical IR, leading to prompt bloat and authority confusion.

## What Changes

- Normalize reality anchors by splitting, trimming, and mapping to structured source/transfer/non_transfer records.
- Separate `domain_states`, `experience_states`, and `ui_transient_states` with authentic `authority` (`explicit` vs `derived`).
- Remove synthetic region fallbacks: emit `regions: []` when unauthored in `m1.md` and add `spatial-topology` to `open_design_space`.
- Strip fabricated `submitting`/`failed` transient states and positional primary-action assumptions from action contracts.
- Implement factual source-to-target accounting in `projection_digest` across `f1`, `m1`, `c1`, and `r1`.
- Bound Five Axes parsing strictly to `f1.md` and harmonize token reference to valid `--text-primary` / `--font-sans`.
- Decouple legacy envelope bloat so `envelope.json` emphasizes canonical 7-field IR, and update builder/critic agent docs.

# Quality Floor

The operative Quality Floor was consolidated to
[`../03-verification/quality-floor.md`](../03-verification/quality-floor.md) in the
modular reference restructuring (commit 461c15a); that file remains the source
read by the Critic agent and by `verify_prototype_quality.py`.

## Aesthetic exclusion (non-negotiable)

The Floor is functional and evidential only: task completion, contract
conformance, contrast and accessibility, and state/recovery handling.
Subjective aesthetic craft choices are never Floor failures. A specific
concentric radius ratio, a drawer versus a sheet, a chosen easing or transition
curve, a palette temperature, or a card recipe SHALL NOT fail a build or force
rework. Such judgments are advisory critique feedback, classified
`DESIGN JUDGMENT` or `PREFERENCE`, and remain non-blocking. A clean, functional
prototype passes regardless of stylistic variation.

This rule is enforced in `verify_prototype_quality.py`: press/motion feedback
misses are emitted as non-blocking advisories, never appended to `failures`.

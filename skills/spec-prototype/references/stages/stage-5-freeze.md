# Stage 5: Silent Governance & Frozen Approved Delivery (冻 - 根)

Answer one question: *"How is the validated design frozen into an immutable,
downstream-consumable artifact set?"* Stage 5 is headless compilation of durable
specifications, design tokens, and verifiable asset digests for engineering
handoff.

## Headless Pipeline Execution

1. **Token reconciliation / DTCG compilation**:
   `python3 skills/spec-prototype/scripts/export-tokens.py prototype/shared/tokens.css --output prototype/contracts/tokens/t1.json`
   compiles `shared/tokens.css` into a W3C DTCG standard `tokens.json`. Any human
   review edit captured in `tokens.css` is first reconciled back into
   `discussion.md` and the contracts via `compile_tokens.py` (`reconcile_tokens_from_css`)
   so no reviewed value is lost.
2. **WCAG static preflight**:
   `node skills/spec-prototype/scripts/wcag-check.js prototype/contracts/tokens/t1.json --level AA`
   checks critical text and figures against **WCAG 2.2 AA (4.5:1)**; long-reading
   and key data text should pursue **WCAG AAA (7:1)**. This is a static contrast
   preflight only — it does not replace full runtime accessibility review
   (keyboard focus management, screen-reader landmarks, reachable touch targets).
3. **SHA-256 asset identity binding / freeze**:
   `python3 skills/spec-prototype/scripts/handoff.py freeze --root prototype --spec prototype/specifications/<slice_id>/r1.md`
   takes the immutable candidate Specification as the freeze subject, computes and
   freezes SHA-256 fingerprints of every HTML/CSS asset, and emits the immutable
   handoff manifest (`prototype/evidence/handoff-manifest.json`). `product.md` is
   the evolvable runtime record and must not be used as a slice freeze contract.

## Authority State

Delivery reaches `Frozen Approved` only here. This is the sole admission state for
downstream frontend engineering delivery (Loom Entry 2). See the authority
lifecycle in [`../core-workflow.md`](../core-workflow.md) and the artifact state
rules in [`../04-governance/artifact-lifecycle.md`](../04-governance/artifact-lifecycle.md).

## Manifest Discipline

- Every manifest entry binds a concrete artifact path to its digest; an artifact
  whose content changes after freeze invalidates its fingerprint and requires a
  new freeze rather than an in-place edit.
- The manifest is a durable delivery record, not a claim of completion; evidence
  lineage stays transparently recorded alongside it.

## Exit

Legal exit is the frozen manifest plus the DTCG token artifact set, ready for
`spec-prototype` handoff per [`../04-governance/handoff.md`](../04-governance/handoff.md).

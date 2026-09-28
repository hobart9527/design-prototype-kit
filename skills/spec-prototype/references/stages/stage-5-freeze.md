# Stage 5: Silent Governance & Frozen Approved Delivery (冻 - 根)

Answer one question: *"How is the validated design frozen into an immutable,
downstream-consumable artifact set?"* Stage 5 is headless compilation of durable
specifications, design tokens, and verifiable asset digests for engineering
handoff.

## Headless Pipeline Execution

1. **DTCG compilation**:
   `python3 skills/spec-prototype/scripts/compile_tokens.py` (default
   `--output-json prototype/contracts/tokens/t1.json`) compiles
   `shared/tokens.css` into a W3C DTCG standard `tokens.json`. The compiled output
   carries the flat `color` group that the contrast preflight consumes.
   *Note on token flow discipline*: `--reconcile-from-css` is strictly an exploratory Stage 1~2 utility. In Stage 5, token definitions are frozen and immutable; bidirectional writebacks to discussion.md are prohibited to preserve upstream SHA-256 seal integrity.
   **Do not substitute a Markdown-table token export for this step.** A re-export
   that groups tokens by CSS custom-property prefix omits the flat `color` group,
   so `wcag-check.js` reads an empty set and exits 0 with `allPass: true` — a
   false pass. `compile_tokens.py` is the only writer of the Stage 5 preflight
   target.
2. **WCAG static preflight**:
   `node skills/spec-prototype/scripts/wcag-check.js prototype/contracts/tokens/t1.json --level AA`
   checks critical text and figures against **WCAG 2.2 AA (4.5:1)**; long-reading
   and key data text should pursue **WCAG AAA (7:1)**. This is a static contrast
   preflight only — it does not replace full runtime accessibility review
   (keyboard focus management, screen-reader landmarks, reachable touch targets).
3. **SHA-256 asset identity binding / freeze**:

   `python3 skills/spec-prototype/scripts/handoff.py freeze --root . --spec prototype/specifications/<slice_id>/r1.spec.md`

   `--root` must point to the repository root (the directory containing `prototype/`), not to `prototype/` itself. The freeze command takes the Specification as its subject, computes SHA-256 fingerprints of every retained artifact, and writes the immutable freeze manifest to `prototype/evidence/<slice_id>/<candidate_id>/freeze-manifest.json`. `prototype/discussion.md` is the evolvable decision record and is never a freeze subject.

## Authority State

Delivery reaches `Frozen Approved` only here. This is the sole admission state for
downstream frontend engineering delivery (Loom Entry 2). See the full
authority-to-artifact lifecycle mapping and the artifact state
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

# Stage 4: Look & Refine

Answer: *Does the design solve the intended task with distinctive, coherent craft?*
Review the rendered experience first. Checks serve design judgment; they are not the
purpose of this stage.

## Focused design review

1. Inspect actual rendered views at the viewports and states that can change the
   judgment. Look first at hierarchy, composition, density, typography, content
   realism, color, spacing, material, motion, and product-specific expression.
2. Attempt the central task from visible cues. Confirm the meaningful result and one
   applicable interruption, recovery, or boundary case. Screenshots prove appearance,
   not interaction.
3. Check only applicable non-negotiable floors: source fidelity; working declared
   actions and recovery; WCAG/accessibility; visible `:active` feedback on commit
   controls; concentric nested radii (`R_inner = max(0, R_outer - P)`);
   `font-variant-numeric: tabular-nums` for aligned or changing values; and 44×44px
   touch targets in touch contexts. Reduced-motion behavior applies when motion is used.
3a. **Write the design judgment first, from the render.** Steps 1–2 produce a
   judgment made by looking, before any rule output exists. Fix it in writing
   before running a scan: a reviewer who reads the hit list first reviews the hit
   list, and what no rule encodes goes unseen — the review degrades into
   reconciling machine output item by item. The order is judgment, then evidence,
   then reconciliation.
3b. **Render defect scan** against the actual captures — overlay positioning,
   elements wider than their container, identifiers broken mid-token, sticky
   layers covering content, and the empty/long states. The list and its failure
   modes are owned by
   [`../02-craft-methods/craft-floor.md`](../02-craft-methods/craft-floor.md).

   Now introduce the detector evidence, and reconcile it against the judgment
   already written — a hit the eye missed is re-inspected on the render, a
   judgment the scans contradict is re-checked, and neither side overrides the
   other without that look:
   - `python3 skills/spec-prototype/scripts/detect.py --artifact <file>` for the
     craft-floor rules that are machine-readable.
   - The slop/rut set (purple-on-dark gradients, glass and blur as decoration, pill radii
     on large containers, ghost cards, emoji icon systems and the rest) is a
     benchmark-side judge, not a delivery gate: read the render for these yourself.
     `detect.py`'s `BENCHMARK_ANCHORS` maps the machine-readable subset. A detector
     hit is a lead: confirm it against the render before it counts as a finding.
3c. **Narrowest-viewport read**: at the smallest declared width the surface still
   answers its own question. Recomposed structure, or an honest `PARTIAL` — a
   compressed desktop is a defect, not a pass.
3d. **Signature-mechanism delivery**: every mechanism the proposition depends on
   is observable in the render. Two-person control, reversibility, and audit
   claims are checked against what the artifact actually does; an unimplemented
   promise is recorded as such rather than described as delivered.
4. Preserve the strongest design relationship. Report only consequential findings,
   normally no more than three. State location/state, user impact, owning layer, and
   smallest useful intervention. Separate fact, design judgment, preference, and
   missing evidence; do not invent problems to fill a quota.
   **Taste is not evidence.** Disagreeing with a density, a radius, or a tone the
   contract chose is a preference, recorded as one and never filed as a finding. A
   finding needs a failed trigger: a floor, a declared contract block, a task that
   cannot be completed, or a stress case that breaks. The converse holds too: a
   direction that wins on looks while breaking a floor is a defect, not a candidate.
5. Refine at the owning layer, then inspect the affected view or task again. One
   focused pass is normally sufficient. Continue only when the user changes scope or
   new evidence exposes a new cause.

### Read the render against the Direction Contract, pillar by pillar

The review has a second half that is not a defect hunt: take the Direction Contract
([`../01-foundations/design-language.md`](../01-foundations/design-language.md)) and
ask, of the *actual render*, whether each declared block is observable. This is the
check that catches a direction that was locked in words and then not built.
Every capture receipt carries a `direction_contract_checklist` — the six questions
(THESIS / OWN-WORLD / STORY / FIRST VIEWPORT / FORM / FINISH) — emitted by
`capture.mjs`; the review starts from these six against the render, and the review
portal surfaces the same checklist per capture card.

| Contract block | The question the render must answer |
|---|---|
| THESIS | Is the first viewport's claim visible without reading the copy? |
| OWN-WORLD | Does the surface belong to the named world, or to dashboard chrome? |
| STORY | Is the task's shape readable from the layout alone? |
| FIRST VIEWPORT | Does the opening frame carry the product's own subject, not a template header? |
| FORM | Do the Five Axes the contract names read as those axes? |
| FINISH | Is the craft floor met on the rendered pixels (`detect.py` plus the capture read)? |

A block that is declared and not observable is a finding, and its owning layer is
the build — not the contract. Do not amend the contract to match what got built;
that inverts the authority the contract exists to hold. Pillars that the contract
does not name are not audited here: this is a fidelity check, not a second review.

### Two batched inspection rounds, then stop

Inspection is batched, not iterative. Round one takes every capture the review needs
in one trip — all declared viewports, the states that can change the judgment, and
the render-defect scan — and the contract read above. Round two re-inspects only
what round one's repair actually touched. After round two the review ends: record
what remains open as a `PARTIAL` finding with its unverified scope rather than
opening a third round. A review that keeps finding new causes is usually re-reading
the same cause at a new location; name the cause and stop.

### The review is organised by Pillar

A review that lists observations in the order they were noticed hides its own
gaps. Organise it by the Nine Pillars instead
([`../01-foundations/design-methods.md`](../01-foundations/design-methods.md)), so
that a pillar nobody looked at is visible as a row rather than absent from the
report.

| Pillar | Owning question in this review | The craft domains it reads |
|---|---|---|
| **Value** | Does the surface still serve the stated product outcome? | brief fidelity, copy, the proposition |
| **Research** | Do the empirical claims hold against what was actually built? | rut, benchmarks, measured priors |
| **Object** | Are the entities, their content and their authority intact? | content realism, data semantics |
| **Journey** | Does the task hold end to end, including interruption and return? | task trace, recovery, continuity |
| **Topology** | Does the surface architecture still answer the task? | layout, navigation, responsive recomposition |
| **Attention** | Is the first-glance hierarchy the one the product needs? | composition, density, type scale |
| **Expression** | Do the Five Axes read as the contract declared them? | typography, colour, material, motion |
| **Interaction** | Are the decisive exchanges honest and reversible? | actions, states, feedback, `:active` detents |
| **Resilience** | Does it survive the stress vectors without collapse? | break protocol, empty/long/error states, a11y |

Rules that keep the pillar view honest:

- **Every pillar gets a row, including the ones you did not examine.** Write
  `not reviewed` for those, with the reason. A pillar silently omitted from the
  report reads as covered; the row is what prevents that.
- **A finding names its pillar.** The same observation can belong to two; pick the
  owning one — the layer that would change to fix it — and cross-reference the
  other rather than filing it twice.
- **`not reviewed` is not a pass.** Do not sum rows into a verdict. A review with
  unreviewed pillars is `PARTIAL` regardless of how clean the reviewed ones are.
- **A `prose_only` rule is a finding you must write, not one you may skip.** When
  `detect.py` returns a rule as `prose_only`, the machine has declared it cannot
  read the artifact — the judgment is yours and it is owed. Every `prose_only` rule
  that applies to the surface gets an explicit pass-or-finding line in the report.
  Leaving it unwritten is not a quiet pass: it is the same `not reviewed` state, and
  it carries the same `PARTIAL` consequence as an unexamined pillar.
- Pillar coverage is not a quota: a small change may legitimately touch two pillars
  and mark seven unreviewed. The rule is that the seven are *named*.

## Capture and evidence

Use `capture.mjs` for rendered evidence when available, with only the relevant
viewports and declared states. `capture.mjs` automatically reports a structured
`diagnostics_summary` alongside viewport screenshots.
`syncReviewPortal` maintains a single canonical portal at `prototype/review-portal.html`.
Never create or copy ad-hoc review portals under nested paths (such as `experiments/.../prototype/review-portal.html`).
A state is captured only if its trigger was applied and
the page confirmed it; filenames alone are not proof. If browser startup, state
confirmation, or interaction tracing fails, record the scope as `unverified`, not
passed. Inspect the actual screenshots before making visual claims. A static check
supports a review; it does not establish visual quality.

**Visual assertion hard rule — evidence provenance**: record in
the design record (the brief on a layered tree, or `prototype/discussion.md`) the `visual_evidence` reference, whether
`capture_reflects_current_state` is `true` or `false`, and the concrete visual
conclusion drawn from the current capture. An old capture may be retained for history,
but `capture_reflects_current_state: false` cannot support a verified finding or
`Validated` authority status. When `capture.mjs` cannot produce real rendered
screenshots (browser startup failure, environment unavailability, CI headless failure),
ALL visual assertions — hierarchy, composition, color contrast, spacing, motion,
typography — are immediately downgraded to `[hypothesis]`. They may NOT serve as
evidence for `Validated` authority status. Record explicitly in the design record:
`visual_evidence: unverified (no rendered captures)`.
A source-code inspection of HTML/CSS is NOT a substitute for rendered visual
evidence; inferring visual quality from markup is a fabrication, not a finding.

## Independent review and repair

Dispatch `spec-prototype-critic` only when an independent review is explicitly
requested or when genuinely separate context can change the decision. The main
designer performs the ordinary review directly. Keep any external request focused:
original brief, design question, target revision, relevant captures, and the
requested judgment. Ask for the strongest relationship to preserve and the few highest-impact findings—not a compliance inventory. Without an actual independent
dispatch, label the review `review_independence: non-independent (unverified)`;
never claim independent verification from self-review.

Repair in place at the owning layer. Optional detached work may still use a
bounded `spec-prototype-builder` for a mechanical, scope-locked change, but never
as the primary authoring path and never as a blocking gate. Allow one focused
repair pass.

When the repair is a *move* rather than a defect fix — the user asks for bolder,
quieter, tighter, a variant, or a hardening pass — make it as a named
[refine operator](../operators.md): state the target axis or pillar, the from → to,
what is held constant, and the falsifier. A move that cannot name its target is a
redirection, not a refinement, and belongs back in the divergence generator. One
operator per pass: two moves at once are attributable to neither. If it cannot complete within the available turn, record the review as
`PARTIAL` in the design record (the slice's brief or `prototype/discussion.md`), name the open finding and unverified
scope, and stop; do not burn the remaining wall clock waiting.

## Break Protocol

Choose only the stress cases material to the product and current task: e.g. long
content, no data, narrow layout, rapid activation, interruption, or degraded service.
Use real state triggers. A copied/default screenshot cannot establish that a stress
case rendered. Do not simulate new product capability merely to make a test pass.

## Decisive Exchange 3-Frame Inspection

For a consequential action, inspect intent (the person understands the action),
commit (the action has perceptible feedback), and settled result (the changed state
and available recovery are clear). Apply only where this sequence fits the action.

## Completion Receipt Discipline

Use the actual receipt and verifier output from the run; do not rerun identical work just
to reconfirm it. Record what was observed, what changed, what could not be checked,
and whether the design question is answered. `PARTIAL` with honest limitations is a
valid end state. A timeout or a false verification claim is not.

Stage 5 freeze, manifests, and export are optional handoff mechanics, not a design
review gate. Run them only when the user requested a frozen or downstream handoff.

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
   controls; concentric nested radii (`R_inner = max(0, R_outer - P`);
   `font-variant-numeric: tabular-nums` for aligned or changing values; and 44×44px
   touch targets in touch contexts. Reduced-motion behavior applies when motion is used.
4. Preserve the strongest design relationship. Report only consequential findings,
   normally no more than three. State location/state, user impact, owning layer, and
   smallest useful intervention. Separate fact, design judgment, preference, and
   missing evidence; do not invent problems to fill a quota.
5. Refine at the owning layer, then inspect the affected view or task again. One
   focused pass is normally sufficient. Continue only when the user changes scope or
   new evidence exposes a new cause.

## Capture and evidence

Use `capture.mjs` for rendered evidence when available, with only the relevant
viewports and declared states. A state is captured only if its trigger was applied and
the page confirmed it; filenames alone are not proof. If browser startup, state
confirmation, or interaction tracing fails, record the scope as `unverified`, not
passed. Inspect the actual screenshots before making visual claims. A static check
supports a review; it does not establish visual quality.

## Critic and repair

Dispatch `spec-prototype-critic` for a consequential new direction, major interaction,
or connected prototype when independent review can change the decision. Keep the
request focused: original brief, design question, target revision, relevant captures,
and the requested judgment. Ask for the strongest relationship to preserve and the
few highest-impact findings—not a compliance inventory.

When a finding warrants code repair, dispatch a **fresh bounded Builder Agent**
synchronously with the exact repair scope and decisions to preserve. Never use
`SendMessage` to revive an exited Agent; never use `ScheduleWakeup` or `Monitor` with
filesystem polling to wait for Builder work. Allow one focused repair pass. If it
cannot complete within the available turn, record the review as `PARTIAL` in
`prototype/discussion.md`, name the open finding and unverified scope, and stop; do not
burn the remaining wall clock waiting.

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

Use the Builder's actual receipt and verifier output; do not rerun identical work just
to reconfirm it. Record what was observed, what changed, what could not be checked,
and whether the design question is answered. `PARTIAL` with honest limitations is a
valid end state. A timeout or a false verification claim is not.

Stage 5 freeze, manifests, and export are optional handoff mechanics, not a design
review gate. Run them only when the user requested a frozen or downstream handoff.

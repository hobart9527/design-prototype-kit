# Craft reference — Interaction and power use

Owns the operation model and its feel: conceptual model, decisive exchange, generative/agentic
exchange, interruption and return paths, keyboard-first efficiency, latency choreography, motion
and sensory feedback, component recipes and component sourcing. **Open lens:** which operation
model - direct, structured, generative or keyboard-first - best matches the frequency and risk of
this work? **Floor:** latency, interruption, focus and recovery behavior remain explicit and testable.

Form-level input orchestration lives in [form and input ergonomics](form-ergonomics.md).

Sections in this pillar:
- [Develop an interaction model around the user's judgment](#develop-an-interaction-model-around-the-users-judgment) - conceptual model, decisive exchanges, agentic exchange, interruption paths, power-user flows, latency choreography
- [Motion as feedback, continuity and expression](#motion-as-feedback-continuity-and-expression) - motion choreography, parameters and sensory feedback
- [Component recipes that preserve the design](#component-recipes-that-preserve-the-design) - component representation and state recipes
- [Retrieve knowledge to resolve a concrete design question](#retrieve-knowledge-to-resolve-a-concrete-design-question) - retrieving primitives and component sources

## Develop an interaction model around the user's judgment

### Specialized Double Diamond workflow

**Enter with:** Sourced tasks/operations, current objects and state constraints, audience/input context and actual content.

Follow the shared execution/return rules in [the method library](../design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect the judgment | Walk intent, evidence, action and result from visible cues; identify recall, switching, discovery or control friction without inventing a failing user study. |
| Define — frame the interaction problem | State what mental or physical work should improve and which semantics remain fixed. Define the decisive exchange and its consequence, interruption and return needs. |
| Develop — prototype different mechanisms | Compare suitable direct, staged, contextual or structured control models on the same task. Make before/during/after concrete; inspect control choice and feedback through Builder when runtime behavior matters. |
| Deliver — exercise and specify | Perform the exchange with relevant keyboard/touch, error/retry and return. Refine the mechanism or control, then retain state-linked behavior, exact context/focus rules and evidence in the Surface Map/Contract/Specification. |

**Retained execution record:** Task/intent → visible evidence/control → source-state/precondition → action → pending/result → focus/context preserved → correction/return → implementation/evidence reference.

The craft methods below supply the choices and construction detail for this workflow.

Read when the operation itself needs design, rather than only styling an already
settled control. The Surface Map and cited product sources retain task, object and state
authority. Work with permitted operations; novel interaction need not add capability.

### Make the conceptual model visible

Describe intent → visible object/evidence → available action → perceivable result.
Name what the person must infer, remember or switch between. Reduce that mental
work through a clearer representation before optimizing the click count.
Distinguish the user's model from database structure and from a visual metaphor.

Explore the mechanism that fits the decision:

| Task characteristic | Interaction to consider | Trade-off |
|---|---|---|
| Exact structured values | Explicit fields and reviewable confirmation | More input ceremony; validate known constraints at the right moment |
| Spatial ordering or direct comparison | Direct manipulation with a clear alternate control | Discovery, precision, keyboard/touch equivalence and accidental moves |
| Repeated decisions over a set | Stable queue/contextual detail, suitable batch action if authorized | Selection scope and heterogeneous consequences must remain clear |
| A rare complex decision | Guided steps or staged disclosure | Hiding later constraints can create backtracking and recall work |
| A quick reversible adjustment | Immediate local feedback and visible current value | Distinguish preview from committed change and provide allowed recovery |
| Generated, suggested or agent-performed work | Deterministic frame with an editable generative interior, or a suggestion the person accepts | Partial output, overwritten input, and an abort that cannot reverse an already committed action |

Use signifiers that suggest the permitted action, map controls to their effects,
and place feedback where attention already is. Familiar components carry learned
behavior; alter their meaning only when the benefit survives a novice walkthrough.
A useful innovation may change what is compared or made visible while retaining
ordinary buttons, fields and navigation.

### Prototype the decisive exchange

Sketch before, during and after the operation with realistic content, then include
an interruption or correction and return. Compare a materially different mechanism
only when the decision is open. Examine initiation, granularity, context retained,
feedback timing and completion: “fewer steps” can still mean more uncertainty.

For consequential or newly authored tone, use [content and voice](form-ergonomics.md#product-voice-that-helps-people-act).
Write action labels from the user's intent and visible consequence. Put unfamiliar
terms or consequential qualifications near the choice. Match tone to the moment:
inviting while exploring, precise before commitment, calm and useful during failure.
Do not make unsupported reassuring promises or blame the user for a system error.

Translate the chosen exchange into the existing component recipe and state/flow
specification. Test from visible cues with keyboard and touch as applicable; an
expert can inspect likely friction but cannot claim novice validation without users.
Preserve context across return and inspect the pending retry, not just endpoint
screens. Retain the strongest mechanism and its observed cost in the review.

### Generative and agentic exchanges

When the product generates content, proposes a suggestion or performs multi-step
work, the unresolved question is usually control rather than styling. Keep the
mechanism here; capability limits, uncertainty wording and trust boundaries belong
to [trust and handoffs](resilience-trust.md#make-consequential-boundaries-understandable).

Decide for each generative surface what the person already owns: an editable
draft, a committed value, or a proposal awaiting acceptance. Keep the generated
proposal visibly distinct from the accepted product fact, so accepting, editing
and discarding are distinct outcomes of one exchange rather than one ambiguous
"apply".

- **Deterministic frame, generative interior.** Keep navigation, fields and commit
  actions from the product's ordinary controls and let generation fill the region
  it can be wrong about. A free-form canvas or a chat panel is a choice with a
  learning cost, not the default expression of an assisted feature.
- **Incremental output.** Reveal partial results where the person can judge them
  early, keep their own input from being overwritten while output streams, and
  show what is still pending instead of presenting incomplete output as final.
- **Speculative and queued work.** When an optimistic result appears before it is
  durable, make the pending state and the reversal path visible, and settle to a
  truthful state on abort ([motion](#motion-as-feedback-continuity-and-expression) owns the settle rule). An
  abort that stops presentation must not hide an already committed action.
- **Interruption and redirection.** Stopping, redirecting and editing during
  generation are separate permitted actions; name which one a control performs
  and what survives it, including work already accepted.
- **Certainty changes the interaction.** Where a real source distinguishes
  certainty, let it decide whether the product acts, offers alternatives or asks,
  instead of only recoloring a label; [trust and handoffs](resilience-trust.md#make-consequential-boundaries-understandable)
  owns how that limit is communicated.

Exercise the exchange like any other: an accepted result, an edited suggestion,
an incorrect one, an interruption and a return. Retain the mechanism, what it
committed, and its observed cost in the existing review.

### Derive reachable interruption paths

Use this bounded method when in-scope work can be interrupted and resumed,
including unsaved/failed edits and operations that settle after navigation or
other work. Keep the model in the existing Contract transition rows; no new
approval, state-machine dependency or business capability is implied.

Separate the selected editor/view from the subject's unfinished work and its last
committed value. One visible editor does not imply one shared draft lifetime.
For each allowed context switch, decide what resumes and what is deliberately
discarded under the task's retention promise. Replacing the visible editor must
not silently make that decision. Keep a draft with its subject for the promised
session/scope, or make an authorized discard explicit; this need not add durable
autosave, a backend or additional editable objects. A failed attempt's input is
still unfinished work even though its network/operation phase has ended.

1. From sourced behavior and the proposed surface map, identify the operation's
   subject/attempt, allowed phases and events, and surfaces reachable while it is
   pending or has failed while awaiting recovery. Distinguish the same attempt
   from independent work. Include supported Back/direct-entry/reload paths;
   exclude impossible combinations with a reason.
2. For each reachable surface/identity relationship, trace each specified outcome
   through settlement, the next meaningful action and return to suspended work
   where allowed. For example, failure → work on another permitted subject →
   return → retry tests draft continuity that an immediate retry cannot establish.
   State which facts are shown,
   which actions remain permitted, how outcome feedback is discovered, and what
   happens to focus and retained input. When the operation belongs to different
   work from the current view, make its source recognizable in the visible message
   and recovery action: use the distinguishing object/operation details people
   know, not an internal attempt ID. Develop its wording and placement together
   using [content and voice](form-ergonomics.md#product-voice-that-helps-people-act), so proximity to a current field
   does not imply that field failed or succeeded. Compare the complete viewport:
   can the person identify whose result this is and where the next action leads
   without recalling the earlier submission? Retain enough context to distinguish
   the source; an unambiguous same-object result need not repeat a full summary.
   Distinguish an outcome reached while staying
   on a surface from entering that surface after the outcome. A stored result is
   only part of the expected experience. When settlement enables distinct actions,
   compare their continuation rules: reopening the completed attempt and editing
   the currently viewed independent object may use different state owners. Select
   representatives by those rules and retain unexercised classes; one convenient
   continuation cannot stand for all newly enabled actions.
3. Reduce repetition by grouping cases only when their lifecycle, projection and
   continuation rules are equivalent. Record the basis for grouping; identical
   resting or pending markup is insufficient. Prefer representative data classes
   over arbitrary combinations. Keep untested distinct branches visible instead
   of implying exhaustive coverage. For a synchronous local action, use its simple
   transition row rather than constructing an asynchronous matrix.
4. Before implementation, retain a compact case list: case ID → starting surface
   and identity/phase → events and held context → outcome → visible facts/actions,
   feedback and focus/context expectation → recovery/return. Resolve ambiguous
   product behavior with its owner; do not invent cancellation, retries or storage.
5. During execution, record the actual surface and identity/phase before and after
   each consequential event, including settlement and the next action. Hold the
   specified context until the event occurs: silently moving to a convenient view
   tests a different path. Compare the executed trace to its case before marking
   it covered. On a mismatch, retain the run and re-exercise the intended path;
   missing observation remains unverified even when the endpoint data is correct.

The design owner derives intended cases; Builder maps them to actual render/event
owners and reports unanticipated reachable branches for reconciliation. Critic
samples the derivation and an experienced trace, rather than trusting assertion
counts. Keep these records with existing Contract and prototype evidence.

Method basis: [state-machine path generation](https://stately.ai/docs/graph)
distinguishes reaching states from traversing paths; this bounded UI application
adds visible projection and continuation checks. [W3C status-message guidance](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)
supports perceivable feedback without requiring every status update to move focus.
Use the product's interaction context to choose announcement and focus behavior.

### Power-user efficiency and keyboard-first flows

For tools used daily or under time pressure, provide an ergonomic keyboard stream:

- **Command palette (Cmd+K / Ctrl+K):** A universal search and action launcher for
  deep navigation, batch actions, and settings. Supports fuzzy matching, recents,
  and explicit keyboard shortcut hints.
- **Non-mouse navigation streams:** Support sequential item traversal (e.g., `J`/`K`
  or `Up`/`Down` in lists), expansion (`Enter` or `Space`), and dismissal (`Esc`).
  Display concise visual keycap badges near actions to teach shortcuts organically.
- **Focus continuity:** A modal or drawer must return focus to its trigger when it
  closes. The detailed recovery focus-continuity mechanics are owned by
  [component implementation](../component-implementation.md); cite that owner
  rather than maintaining a competing statement of the rule here.

### Perceived performance and latency choreography

Structure visual feedback according to operational latency thresholds:

- **0–100ms (Perceived instantaneous):** Immediate visual reaction (button press,
  toggle switch, checkbox mark) acknowledging input with zero perceptible lag.
- **100–300ms (Optimistic update):** For high-probability, low-risk operations (e.g.
  favoriting, bookmarking, upvoting, renaming), commit UI state optimistically before
  network settlement. If the network request subsequently fails, gently roll back
  the state and display a contextual inline alert explaining the failure with a retry action.
- **300ms–1s (Transient progress):** Replace button text or show a subtle inline spinner
  adjacent to the action to confirm ongoing background work without locking the whole viewport.
- **> 1s (Deterministic progress & skeletons):** Render layout-stable skeleton blocks
  or an explicit progress indicator with elapsed/estimated status. Never leave the user
  wondering whether the application is unresponsive.

## Motion as feedback, continuity and expression

### Choose motion behavior from the information exchange

No easing curve, spring, press transform or stagger is a universal quality floor.
First decide what the user must perceive: immediate acknowledgement, spatial
continuity, changed hierarchy, causality, progress or expressive punctuation.
Then choose cut, color/property change, fade, spatial interpolation, layout
transition or spring behavior and tune it in the real runtime.

- Frequent precision work often benefits from an immediate response or short,
  non-ornamental transition.
- Spatial transitions may preserve origin and destination when that mapping helps
  orientation; they should not delay access to the result.
- Elastic or tactile behavior is useful only when it matches the component,
  product character and input method. Overshoot can undermine a serious or dense
  tool.
- Stagger can reveal order or hierarchy; simultaneous appearance can be clearer
  when items form one result. Test the actual list length and repeated use.
- Exit timing, interruption and rapid reversal must preserve state truth. The
  reduced-motion path communicates the same outcome without depending on travel.

Retain endpoints, timing/configuration, interruption/settle rule and the product
reason. Treat presets as hypotheses to tune, not craft credentials.

### Specialized Double Diamond workflow

**Enter with:** Authorized component transitions, selected spatial/material language, input methods and actual rendering runtime.

Follow the shared execution/return rules in [the method library](../design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — observe the exchange | Walk the operation and identify where immediate response, continuity, attention or emotional punctuation is missing. Observe its frequency, distance and interruption conditions; keep a competent still transition as a baseline. |
| Define — bound the motion intent | Choose the information the motion must communicate, which element leads and what stays anchored. Set acceptable attention/latency cost, final semantic state and a reduced-motion alternative. Decide whether the unresolved question is rhythm, spatial mapping or expressiveness. |
| Develop — implement and tune candidates | Choose cut/color/fade/spatial/layout/spring technique for the actual runtime. Specify endpoints, origin, duration/easing or spring parameters. Builder makes a small playable comparison; vary a consequential parameter and inspect onset/travel/settling at normal speed. |
| Deliver — replay and retain | Test repeated/reversed input, slow result, navigation and reduced motion. Check state truth and observed frame/layout behavior. Tune the recipe and replay the same exchange; retain exact configuration plus time-based evidence, then hand it to the existing specification/review. |

**Retained execution record:** Transition ID → source/target state → trigger → animated element/property → from/to values/origin → delay/duration/easing or spring configuration → interrupt/settle rule → reduced-motion implementation → source file → event/clip evidence. Endpoint screenshots alone leave choreography unverified.

The craft methods below supply the choices and construction detail for this workflow.

Read when motion changes a decision, transition or signature. Start from the
information it communicates: input received, attention directed, relationship
preserved or a supported emotional moment. Stillness is a valid design choice.

### Develop the choreography

Choose the moment's motion character from its frequency and purpose. Repeated
operational feedback usually needs a compact, predictable rhythm; an occasional
meaningful reveal can carry more expression. These are choices within one product,
not separate “tool” and “consumer” styles.

- **Response:** acknowledge input promptly; keep flourish subordinate to the
  actual state change. A press response should not imply a commit that failed.
- **Continuity:** preserve the identity of a moving or changing object through
  direction, origin and destination. Decide what stays anchored so the person
  understands where information went.
- **Attention:** move the layer that matters and let surrounding content rest.
  Coordinate related elements as a group; stagger only when sequence has meaning.
- **Expression:** derive weight, elasticity or precision from the chosen language.
  Compare a quieter variant and a still version; retain the movement only when
  it clarifies or enriches the moment.

Tune onset, travel and settling together. Greater distance may need more travel
but does not justify delaying input response. A soft settling tail can feel crafted
on a reveal and sluggish on a frequent toggle. Compare timings in the runtime;
a universal millisecond value or named easing is not the aesthetic decision.
Keep a strong static composition: motion cannot repair unclear hierarchy.

For each meaningful transition, retain in the Specification:

| Trigger and state change | Visible/announced meaning | Elements/properties | Timing/easing | Interruption | Reduced-motion alternative |
|---|---|---|---|---|---|

Choose timing from the action's rhythm and actual distance. A material metaphor
may suggest settling, snapping, unfolding or flowing; translate it into a small
testable behavior. Do not impose spring motion on a precise tool or bounce an
error just because the brand is playful. Status and input response must appear
without waiting for a flourish. Retain meaningful labels and focus while moving.

Test rapid repeated input, reverse/cancel, returning from another surface, slow
response and reduced motion. A canceled transition must settle to the correct
state rather than complete an obsolete animation. Reduced motion should preserve
the information through immediate state, text, outline or gentle opacity where
appropriate; it is not a global timing hack that erases feedback.

Keep reading, native scrolling and keyboard access available. Inspect frame and
layout behavior on the actual runtime; use transform/opacity when suitable, but
do not equate their use with proven performance. Apply acceleration hints only
to observed needs, not every element. If an effect adds cost without clarifying
the experience, remove it at the design owner and retain the stronger static form.

### Translate character into parameters

Choose the simplest technique that can express the intended relationship. A color
transition can acknowledge a state; spatial translation can explain continuity;
a layout transition can reveal a real change in occupied space. A spring is useful
when its settling behavior adds meaning and the current runtime supports it.

Use a controlled parameter search, not a material-to-animation lookup:

| Observed issue | Parameter hypothesis to compare | What to keep checking |
|---|---|---|
| Input feels late | Remove unnecessary delay; shorten onset before shortening the whole movement | State feedback appears promptly, including slow operations |
| Travel feels abrupt | Adjust distance, duration or the early part of the easing curve one at a time | Identity and destination remain understandable |
| Movement feels floaty | Shorten the settling tail or increase spring damping relative to the current configuration | No sharp snap or loss of useful continuity |
| Repeated movement is tiring | Reduce amplitude or remove repeated flourish | The action remains recognizable without animation |
| Reversal jumps | Retarget from the current rendered state; inspect the runtime's cancellation rules | An obsolete transition cannot overwrite the latest state |

For spring-capable runtimes, stiffness controls restoring force, damping dissipates
motion and mass changes response to that force. Their numeric conventions vary;
inspect the actual API. Increasing stiffness alone can make a response sharper
and alter oscillation; increasing damping can reduce oscillation but may slow an
overdamped response. Tune a measured configuration instead of copying numbers
between libraries. Retain the final values and the runtime/version that interprets
them.

For a small decorative indicator tied to an already-authorized state, a CSS
transition may suffice. This example is a starting construction technique; its
angle, duration and curve must follow the chosen specimen, not become defaults.
Builder supplies exact token values before executing it.

```css
.disclosure-indicator {
  transform: rotate(0deg);
  transition: transform var(--motion-disclosure-duration)
    var(--motion-disclosure-easing);
}
.disclosure-trigger[aria-expanded="true"] > .disclosure-indicator {
  transform: rotate(var(--motion-disclosure-angle));
}
@media (prefers-reduced-motion: reduce) {
  .disclosure-indicator { transition: none; }
}
```

The semantic button, `aria-expanded`, controlled panel visibility and keyboard
behavior come from the disclosure primitive; the indicator is decorative.
The example assumes `.disclosure-indicator` is a direct child of its own
`.disclosure-trigger` button; adapt both selectors and markup together. Bind the
indicator to that trigger so an expanded ancestor cannot style a closed nested one.
State updates occur immediately and do not wait for `transitionend`. Reduced motion
preserves the correct final orientation and panel state. A playable test must
include opening, closing midway and repeated input; endpoint screenshots cannot
establish this behavior or its perceived rhythm.

Retain a normal-speed clip or timestamped runtime observations with the actual
trigger sequence, together with the source configuration. Record what was observed
about onset/travel/settling, interruptions and reduced motion; report performance
as unverified unless the runtime was measured. Use those observations to change a
specific parameter and replay the same sequence before accepting the revision.

### Sensory feedback: haptics and micro-audio

Where supported by the platform (native mobile, handhelds, or specialized devices),
motion coordinates with tactile and auditory feedback channels. These channels
share the same trigger rhythm, restraint, and accessibility requirements as visual movement.

- **Haptic feedback tiers:**
  - *Selection tick (light impact):* Discrete item traversal, slider snapping, or wheel detents.
  - *Affirmation pulse (medium impact):* Successful state commitment, toggle activation, or completion.
  - *Warning / Error buzz (double/heavy pulse):* Form submission rejection, invalid drop, or destructive boundary.
  - Never trigger haptics continuously or on passive scroll; reserve for intentional tactile response.
- **Micro-audio feedback:**
  - Soft, functional chimes or clicks that reinforce state changes without drawing unwanted attention.
  - Pair every auditory cue with an equivalent visible signal; sound is supplementary, never the sole carrier of meaning.
- **Sensory preferences and silence:**
  - Respect system silent mode, vibration settings, and user accessibility preferences.
  - If haptic or audio channels are disabled, visual feedback must carry full operational meaning without degradation.

## Component recipes that preserve the design

### Specialized Double Diamond workflow

**Enter with:** The current task/Contract, selected or provisional language/tokens, real content ranges and available primitives.

Follow the shared execution/return rules in [the method library](../design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect the component job | Inventory consequential decisions and available controls. Inspect a reference or existing component in relevant states, including its actual dimensions, typography, borders, spacing and semantics when observable. Identify what people must compare and retain. |
| Define — frame the judgment and constraints | State what the person must recognize or compare and which information relationships must hold. Determine applicable state predicates and their priority from the product/Contract; distinguish the product fact, current view state and operation feedback. Keep unresolved representation/anatomy choices open. |
| Develop — construct and translate a recipe | Compare credible representations/anatomies for the defined judgment; develop the promising component/state compositions. Translate the chosen reference or authored property into exact token-bound selectors/variants in the actual stack, retaining semantic attributes and focus behavior. Produce a state strip and a composed task instance through Builder. |
| Deliver — exercise and propagate | Inspect appearance, real inputs, content stress, pending/retry and return. Repair the shared recipe or return a design conflict to its owner; rerun the same state sequence. Propagate the validated recipe to other instances and retain exact implementation mapping, not only descriptive rules. |

**Retained execution record:** Component → primitive/file/export → anatomy → state predicate/precedence → semantic attribute → token roles → concrete class/selector/variant → evidence checkpoint. Mark genuinely inapplicable states; do not produce eight fictional states merely to fill a table.

The craft methods below supply the choices and construction detail for this workflow.

Read before interaction selection and when a distinctive visual language meets
real controls. A recipe expresses an approved relationship, not a mandatory
Tailwind string or an eight-state checklist for every element.

### Choose the representation before specifying states

Start from the judgment the component supports. Compare a row, card, list,
comparison table or focused control when their information relationships differ.
Rows favor repeated attributes; cards can give subjects individual presence;
a table exposes aligned comparison; a focused editor gives one decision room.
Choose for the current content and device rather than visual fashion.

Develop its anatomy on a typical and a difficult example. Decide which content
anchors recognition, what action deserves emphasis, and which facts stay secondary.
Use shape, boundary, spacing and type as a family: a heavy outline plus shadow plus
colored fill may repeat the same emphasis unnecessarily. Tune density through the
relationships, not merely smaller padding. Allow controlled variants by role;
uniform appearance should not erase the difference between selection and commitment.

Make one representative component excellent in its real composition before
multiplying it. Compare its calm and consequential states together; transfer the
selected rule, not a one-off decorated resting state, to the rest of the interface.

For each consequential product component, specify the following in its existing
Foundation/Contract/Specification section, keeping each owner's responsibility:

| Aspect | Design decision |
|---|---|
| Job | What the person must recognize, judge or do here; what stays visible |
| Anatomy | Primary content, context, action, status and subordinate detail |
| Language | Semantic type/color/space roles and the defining compositional relationship |
| State | Applicable state, trigger, visible response, available/invalid actions, next state and feedback that expires |
| Content | Typical and stressful examples; wrapping, truncation and full-value access |
| Input | Keyboard, touch and pointer behavior; accessible name/state and focus destination |
| Continuity | What selection, input, position or domain fact survives update/return |

Default, hover, focus, pressed, disabled, pending, error and success are prompts
to identify real states. Add only applicable states; distinguish selected from
pressed and validation from server failure. Explain unavailable actions near
the decision. Pending feedback keeps its meaning and prevents duplicate commits
without destroying cancellation or keyboard access that the contract allows.

For an input, distinguish **requiredness**, **meaning/format validity** and
**product eligibility**. A populated field is not necessarily a valid value of
the requested kind; conversely, a familiar local format is not proof of an
eligibility rule. Use the field's established meaning and actual platform behavior
to choose proportionate validation; record uncertain format choices explicitly.
When removing an unsupported restriction, admit legitimate broader values while
retaining meaningful invalid-input feedback. Test an empty value, a valid value
outside the removed restriction and a nonempty value of the wrong kind through
confirmation and commitment. Do not substitute a stricter country-specific
pattern or accept arbitrary text merely to make one example pass.

Derive available choices and current feedback from the operation's current
context. Use known constraints to explain or prevent an invalid combination
when it becomes knowable, before asking for unrelated work; retain necessary
commit-time validation. For each consequential message, specify its claim,
subject/value snapshot, condition of validity and currently available next action
in the existing recipe. Render current feedback from those facts rather than
leaving the last message to outlive the condition that produced it.

A validation error describes the affected value and predicate. When a correction
resolves that predicate, update its message and error semantics at the chosen
validation trigger; an obsolete empty-value error must not keep describing a
populated field. This does not clear unrelated errors or establish whole-form
validity. An AI warning about a retained candidate can remain with that candidate;
a warning presented as a judgment of the current draft/submission must match that
version. Distinguish historical source cautions from current actionable problems,
and remove or qualify advice whose recovery action is no longer available.

A save/result claim describes its subject and submitted values, not merely an
editor's lifetime or a success phase. Editing the draft can invalidate an
unqualified current-success claim before another submission exists. Keep saved
value and unsaved input distinguishable; a historical receipt must not imply new
input is committed. On a retry, retire outdated instructions so a past failure
does not compete with current progress. Preserve recoverable input independently.
Check the relevant sequence: failure → correction → feedback, or success → edit
again → inspect current status → save/fail/recover; include a changed role/version
when the supplied workflow permits it. Keep one operation/value owner and derive
feedback from it, rather than adding a second lifecycle for each message.

Walk a full decision: inspect the prerequisites → act → observe pending/result
→ recover or cancel → revisit. During recovery inspect the next attempt while
it is still pending as well as its result; isolated error/success frames can miss
contradictory feedback between them. Inspect the amount and placement of context at
each moment. Reassuring text must describe actual guarantees; error feedback
must preserve recoverable work. Controls should remain discoverable without
hover, and success must remain understandable after a toast disappears.

Exercise a revisit from the entry screen without a remembered selector or route.
Make the current result and continuation visible at the moment they matter.
For errors, inspect the viewport after focus moves: the explanation, affected
control and recovery must be discoverable together, including on narrow screens.

Carry the selected grammar into these states. A recipe is incomplete when it
has an expressive resting card but generic or unreadable selected/error states.
On a smaller viewport, reorder or disclose by task priority while preserving
the comparison the user needs; shrinking the desktop composition is insufficient.

The Builder maps the recipe onto existing primitives following
[component implementation](../component-implementation.md). Product state and
view state retain separate owners. If a primitive cannot preserve a required
behavior, report the conflict before substituting another flow.

### Construct the selected recipe

For reference-led work, inspect the relevant rendered component and its states:
measure the actual type, padding, boundary, radius and emphasis relationship when
observable. Map them to existing semantic tokens, then compare the adapted result
with the reference at the same scale. Record intentional deviations and their task
reason. An inaccessible reference is not an authority for inaccessible behavior.

For authored work, translate a property into a controllable relationship before
choosing values. For example, “precise but approachable” might suggest aligned
values, a crisp boundary and generous content spacing. Compare this against a
softer boundary treatment in the same component. Once selected, resolve boundary
width/color, padding, radius and type roles from the actual specimen; do not pass
only that phrase to every downstream Builder.

Build in this order: semantic primitive → real anatomy/content → token bindings →
applicable state selectors → composed responsive instance. The following native
single-choice skeleton illustrates the binding technique, not a required style.
Materialize every referenced token from the selected language before rendering.

```html
<fieldset class="choice-group">
  <legend>Choose a session</legend>
  <label class="choice">
    <input type="radio" name="session" value="morning">
    <span class="choice__body">Morning · 10:00</span>
  </label>
</fieldset>
```

```css
.choice { display: flex; align-items: start; gap: var(--choice-gap); }
.choice input { accent-color: var(--color-action); }
.choice__body {
  flex: 1;
  padding: var(--choice-padding);
  border: var(--choice-border-width) solid var(--color-boundary);
  border-radius: var(--choice-radius);
  color: var(--color-text);
  background: var(--color-surface);
}
.choice input:checked + .choice__body {
  border-color: var(--color-selection-edge);
  background: var(--color-selection-surface);
}
.choice input:focus-visible + .choice__body {
  outline: var(--focus-width) solid var(--color-focus);
  outline-offset: var(--focus-offset);
}
```

The native radio remains visible and communicates selection without color alone.
Use actual product copy and supported options, preserving the label/input relation.
For other primitives, write the equivalent mapping in the existing stack rather
than applying radio semantics to buttons, tabs or list navigation.

Specify overlapping states deliberately: selection remains visible during focus;
invalid input keeps its value and links its error through `aria-describedby`;
`aria-invalid="true"` expresses validation, not every server failure. An applicable
`aria-busy="true"` region still needs visible progress; that attribute alone neither
announces a result nor prevents duplicate commits. The operation owner supplies
pending/retry predicates and authorized actions. Map those to exact selectors or
variants, visible copy, announcements where needed and the focus destination.
Test the intersection, not just isolated state tiles.

If a requested control genuinely depends on a canvas/3D enhancement, inspect the
existing runtime before choosing technology. Keep its action/name/state in a real
semantic control and specify a competent DOM fallback, input behavior and reduced
motion. Validate loss of the enhancement; a decorative canvas must not become the
sole interaction or truth owner. Ordinary surface/depth effects do not by themselves
require a new renderer or dependency.

## Retrieve knowledge to resolve a concrete design question

### Specialized Double Diamond workflow

**Enter with:** Actual repository/platform/stack, inherited assets, current component need and selected expression.

Follow the shared execution/return rules in [the method library](../design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect the need and runtime | Read existing primitives/versions and isolate the missing task/state capability. Retrieve a small relevant candidate set with the task/platform query below; inspect real exports and examples rather than trusting package reputation. |
| Define — establish fit criteria | Specify semantics, input/focus, content range, theming freedom and performance conditions the primitive must preserve. Separate necessary capability from attractive default styling. |
| Develop — prove fit | Compare retention/customization/substitution where useful. Use the existing component-implementation owner to make one authorized proof-of-fit composition in the actual stack, with the consequential states and token treatment. |
| Deliver — choose with evidence | Run stack and visible-behavior checks, record exact source/export/version and supported limits, and adopt or reject. If theming breaks behavior or required capability is absent, repair the adapter or compare another candidate and repeat the same checks. |

**Retained execution record:** Need → query/source/version → required capability → observed proof-of-fit → chosen primitive/export/file → token/state adapter → rejected alternative/reason → checks/limits. Component implementation owns executable adoption; this reference owns discovery/comparison.

The craft methods below supply the choices and construction detail for this workflow.

Read when pattern/component/platform uncertainty could change a design or its
feasibility. [Research](../01-foundations/research.md) owns tool access and evidence handling;
[component implementation](../component-implementation.md) owns runtime reuse.

Form a query with **task + friction/state + platform**, adding the actual stack
only for implementation questions. For instance: retaining comparison context
on mobile; focus after row removal; asynchronous form retry without input loss.
Retrieve the specific mechanism rather than a complete branded design system.

Use this capability index to make a narrow query and a meaningful rejection test.
Start with project primitives, then inspect official examples/source for the actual
platform. Package names or search rankings do not prove these capabilities.

| Need | Capability to inspect in a representative composition | Disqualifying observed failure |
|---|---|---|
| Dense comparison or editable table | Column relationships, keyboard editing, long values, responsive comparison | Hidden values or focus behavior prevents the supported judgment |
| Long or variable-height collection | Measurement, virtualized focus, scroll position and item identity | Returning or updating loses the needed item/context |
| Contextual overlay | Anchor positioning, portal boundaries, focus/escape and target visibility | Overlay clips content or loses the originating control |
| Reorder/direct manipulation | Keyboard and touch alternatives, permitted scope, cancellation and retained identity | A supported input cannot complete or recover the operation |
| Resizable work areas | Minimum usable widths, nested scrolling and focus continuity | Resizing makes an essential region or control unreachable |
| Chart or diagram | Actual data semantics, labels, inspection and alternative access | The intended comparison relies on hover or color alone |
| Media/gallery | Aspect/crop, loading failure, controls and caption relationships | Key subject detail or necessary controls disappear at target sizes |
| Complex input | Parsing/formatting boundaries, composition input, validation and recovery | Formatting changes the value or error handling loses recoverable input |

Select only relevant rows. The proof-of-fit belongs to the existing Builder and
component-implementation path; do not create a second adoption procedure here.

If an authorized local UI UX Pro Max checkout is available, inspect its search
help and use its supported domain/stack. For the researched version:

```text
python <uupm>/src/ui-ux-pro-max/scripts/search.py "<task/state>" --domain ux --full
python <uupm>/src/ui-ux-pro-max/scripts/search.py "<component concern>" --stack <actual-stack> --full
```

Use only the domains/stacks actually supported by that checkout. Retain query,
version, returned source/row, relevant guidance, limitations and chosen adaptation
in the existing research/implementation record. Read full relevant fields when
truncated. Ranking expresses lexical relevance, not tested product fitness.
Validate volatile API/accessibility advice against official sources when adopting.

A generated `--design-system` result is advisory; do not persist it as a parallel
MASTER or override frozen Foundation/tokens. Density, variance and motion dials
are optional suggestion controls, not creative reasoning. With no checkout,
use existing project guidance and targeted official documentation; no automatic
installation, provider configuration or extra dependency is implied.

Use a retrieved pattern as design material: identify its user judgment, information
arrangement and feedback mechanism, then try that mechanism with this product's
content. Compare retaining its standard structure, customizing its expression or
choosing another pattern when these are live options. A library's default styling
is not the maximum visual quality available, and rebuilding a sound primitive is
not proof of originality. Inspect the customization seam before promising a look.

Compare sources by required semantics, accessibility, state/focus behavior,
platform/stack compatibility, theming freedom, license and maintenance cost.
Visual similarity alone is insufficient. Adopt the smallest compatible primitive
or composed pattern that preserves the approved design; report real incompatibility.

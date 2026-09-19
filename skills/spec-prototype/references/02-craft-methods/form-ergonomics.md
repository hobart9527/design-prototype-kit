# Craft reference — Form and input ergonomics

> **Pillars**: `Interaction` · `Resilience` · `Attention`  
> **Core Invariants**: In-situ Form Ergonomics · Inline Proximate Validation · Proportional Input Friction

Owns how the product asks for input and how it speaks: orchestration of complex entry, validation
timing, dirty-state protection and product voice. **Open lens:** which entry, validation and
recovery model best fits the user's real tolerance for effort and correction? **Floor:** validation
timing, dirty-state protection, recovery and message wording remain complete in the Contract.

Form-level trigger policy is owned here; per-field validation semantics stay with component
recipes in [interaction and power UX](interaction-power.md#component-recipes-that-preserve-the-design).

Sections in this pillar:
- [Product voice that helps people act](#product-voice-that-helps-people-act) - product voice, wording and interface copy
- [Form ergonomics and input orchestration](#form-ergonomics-and-input-orchestration) - validation timing, dirty-state protection and container choice

## Product voice that helps people act

### Specialized Double Diamond workflow

**Enter with:** Original product facts/terminology, desired relationship, current UI moments and content/locale constraints.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — listen to the situation | Inspect audience language, emotional context and current copy in real frames. Separate inaccurate facts, unclear meaning and weak voice. |
| Define — set voice and moment intent | Choose stable warmth/formality/directness with evidence and the meaning each moment must convey. Keep factual promises fixed while identifying where tone should change. |
| Develop — write contextual alternatives | Develop plain and characterful versions of representative invitation, action, explanation, failure and return lines where relevant. Compare them with the actual controls, values and available space. |
| Deliver — read the complete exchange | Check clarity, consequence, tone continuity and localization/content stress across states. Revise the misleading or awkward line at its cause; retain exact selected copy, variables and usage limits in existing artifacts. |

**Retained execution record:** Moment/state → source facts/canonical terms → intended tone → chosen exact string/variables → context/control → stress example → rendered/flow evidence and unresolved meaning.

The craft methods below supply the choices and construction detail for this workflow.

Read when the product's tone is being developed or when accurate copy still feels
generic, cold, vague or overbearing. Product sources own facts and promises;
Foundation owns the voice, and the Surface Map/Specification owns labels and
consequences in each flow.

### Establish a relationship, then write actual moments

Choose how the product should relate to the person: knowledgeable peer, clear
instrument, welcoming host or another supported relationship. Define its degree
of warmth, formality, directness and playfulness through actual sentences, not
only adjectives. A stable voice can change tone as the person's situation changes.

Use a small set of real moments from the task: an invitation, a choice/action,
a necessary explanation, a failure and a return after work exists. Write a credible
plain version first, then an alternative with the intended character when voice
is unsettled. Compare what each helps the person understand and how it feels.

- Invitation can create curiosity and belonging while naming what is available.
- Before commitment, prioritize the object, action and supported consequence.
  Distinguish “continue”, “preview” and “confirm” by what actually happens.
- Help should answer the question at that moment; explain unfamiliar terms with
  verified meaning instead of surrounding them with more reassuring adjectives.
- During failure, state what happened, what remains intact and the usable next
  step. Reduce joking or celebration when the person is recovering effort.
- On return, recognize the current work and continuation rather than repeating
  an acquisition pitch or implying a new task has already succeeded.

### Fit words to the interface without losing meaning

Develop concise labels together with their controls and nearby evidence. Put the
important distinction early enough to survive scanning and narrow layouts.
Separate a stable domain term from a helpful display explanation; do not rename
distinct objects into the same friendly word. Avoid filler instructions when the
control itself can make the action clear. Trimming copy is worthwhile only while
needed consequences, prerequisites and recovery remain understandable.

Compare tone and hierarchy in the actual frame, including long/localized text.
Read consequential lines as a connected exchange: do labels, pending feedback and
result tell the same story? Retain selected examples and boundaries in Foundation
and the relevant specifications. These are reusable examples of a voice, not
rigid scripts for every future state. A subjective tone recommendation should
name the intended feeling and observed wording, without claiming user sentiment
was measured when no participants were involved.

## Form ergonomics and input orchestration

Input orchestration is an interaction-model decision; the interaction pillar owns
the model and its diamond. This section owns the form-level trigger policy,
dirty-state protection and container choice.

Complex user input requires systematic choreography beyond single field styling:

- **Validation timing:** Choose immediate, on-blur, on-submit or staged validation
  from correction cost, latency, dependency and interruption risk. Avoid errors on
  untouched fields. A failed submit normally identifies and focuses the earliest
  actionable problem and provides a useful summary when the form is long. This
  section chooses the form-level trigger policy only. Per-field requiredness,
  format validity, eligibility, message wording and message-retirement rules stay
  with [component recipes](interaction-power.md#component-recipes-that-preserve-the-design).
- **Dirty state and unsaved change protection:** When a form contains unsaved input,
  track dirty state. Warn before destructive navigation, tab closing, or cancellation.
  What survives an aborted context switch is owned by the
  [reachable interruption-path method](interaction-power.md#derive-reachable-interruption-paths)
  in the interaction pillar; use its draft-lifetime decision rather than
  restating it here.
- **Form orchestration containers:** Choose single-column vertical flow for speed and
  clarity; multi-step wizard for linear dependencies where step N+1 requires step N;
  contextual drawer/sheet for auxiliary sub-editing that preserves parent context.

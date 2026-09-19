# Craft reference — Resilience, trust and risk coverage

Owns uncertainty, agency, collaboration, failure and critique: consequential actions, AI-assisted
work, cross-role continuation, presence and concurrency, notification hierarchy, inclusive and
locale adaptation, anti-pattern diagnosis and design audit. **Open lens:** how should uncertainty,
agency, collaboration and failure change what the user sees and controls? **Floor:** notification
tiers, trust boundaries, permissions and required states cannot be silently dropped.

Sections in this pillar:
- [Make consequential boundaries understandable](#make-consequential-boundaries-understandable) - consequential actions, AI assistance, presence and feedback hierarchy
- [Adapt the task to people, input and language](#adapt-the-task-to-people-input-and-language) - adaptation to people, input and language
- [Diagnose generic or mismatched expression](#diagnose-generic-or-mismatched-expression) - diagnosing generic or mismatched expression
- [Criticism that changes the design](#criticism-that-changes-the-design) - criticism that changes the design

## Make consequential boundaries understandable

Load only for in-scope sensitive data/permissions, AI-assisted decisions or
cross-role/channel handoffs. Product understanding owns authority and allowed
operations; these methods communicate them without adding product capabilities.

| Double Diamond phase | Work and hand-back |
|---|---|
| Discover | Trace who supplies information, who sees/acts on it, what the system actually knows and who owns the next step. Locate uncertainty or a consequential boundary. |
| Define | State what users must understand and control before relying on this step; retain sourced limits and which outcome would make the design misleading. |
| Develop | Compare the relevant evidence, explanation and control placement through the complete exchange below. Preserve the same permissions and consequences. |
| Deliver | Walk an ordinary and a relevant failure/exception case from each affected perspective. Hand exact wording, visibility, state and next-step rules to the existing owners with evidence. |

### Sensitive or consequential action

Before commitment, expose the meaningful action, affected object/scope, recipient
and actual consequence. Explain why requested information is needed where it is
requested; show optionality accurately. Compare concise contextual explanation with
a review step according to error cost. Confirmation is useful when it prevents a
real costly error, not as a reflex on every action. Preserve authorized cancel,
edit or recovery paths; do not invent legal assurances or consent requirements.

#### Privacy, consent, and permission requests

Request device permissions (camera, microphone, location, notifications) or user data
sharing just-in-time when the action requires it, never on first app launch without context.
Explain why the permission is needed, what feature it unlocks, and how the user can change
their choice later. If the user declines, provide a graceful non-blocking fallback that
keeps the remainder of the product operable.

### AI-assisted work

Distinguish generated suggestion, supporting source and accepted product fact.
Make the actual capability and limits understandable at first reliance. Show what
is still processing, what can be inspected/edited and what action would commit the
result. Confidence numbers require a real defined/calibrated source; invented
percentages are not transparency. Reference links must actually support the claim.
Compare inline assistance, separate review or staged generation by attention and
error cost, not by adding a chat panel automatically.

Where work continues after the person has moved on, state what is still running,
what it will change when it lands and how to stop it; a late result must not
silently overwrite a choice made in the meantime. When generated material sits
inside a committed document, preserve its provenance in the product record.
Expose that provenance in the interface when people need it to judge, edit,
attribute or commit the result; do not add a visible AI badge by default when the
distinction has no product consequence. The mechanism and interruption choices
stay with [interaction craft](interaction-power.md#develop-an-interaction-model-around-the-users-judgment).

Treat content the model reads as untrusted input: it may inform a suggestion but
must not become an instruction the product follows, or an action it takes, without
the authorized confirmation. Before an autonomous step with an external or
irreversible effect, show what it will change and let the person stop it; keep
cost, quota or usage visible where the product tracks them, and distinguish work
already done from what is still planned.

Exercise an incorrect/unsupported suggestion, interruption and subsequent edit
when those interactions exist. Retain user edits according to the product contract;
keep cancel, retry and undo distinct. If cancellation stops presentation but cannot
reverse an already committed operation, communicate that actual limit.
[Microsoft's Human-AI guidelines](https://www.microsoft.com/en-us/research/project/guidelines-for-human-ai-interaction/)
support designing expectations, control and recovery across use; this workflow
adapts those concerns to a scoped prototype. AI-built UI alone does not trigger it.

### Cross-role or channel continuation

Map trigger → sender's action → information/artifact handed over → receiver's
available action → acknowledgment/outcome. Keep each role's permissions and object
lifecycle separate. Make waiting-for-whom, what-changed and the next permitted step
recognizable on the relevant surfaces. Test one delayed/rejected handoff and return
without assuming every role sees the same data or has the same controls. A simulated
role switch is prototype evidence, not authentication or live-service verification.

### Collaborative presence and concurrent work

When multiple actors can view or mutate shared objects simultaneously, make presence
and conflict boundaries understandable:

- **Presence indicators:** Expose who is currently viewing or editing the resource
  (e.g., live avatar stack, cursor tags, or active section highlighting) without
  occluding underlying content or controls.
- **Edit locks vs optimistic concurrency:**
  - *Coarse-grained lock:* For fields requiring strict sequential integrity, display
    which collaborator holds the edit lease and when it expires or can be requested.
  - *Optimistic merge / conflict disclosure:* When simultaneous edits are permitted,
    detect collisions gracefully. Show what changed remotely, distinguish local
    uncommitted edits from remote updates, and offer contextual side-by-side reconciliation
    instead of silent overwrites.

### Global feedback and notification hierarchy

Prevent user notification fatigue and miscommunicated urgency using a 4-tier matrix:

1. **Inline Alert:** Contextual and embedded directly within the affected container
   (e.g., above an invalid field or table section). Use for input corrections, local
   informational tips, and section-level warnings. Never auto-dismiss.
2. **Persistent Banner:** Top of page or app-wide header. Use for asynchronous system
   states, degraded connectivity, offline operation, or pending organizational approvals.
   Dismissible only when user action acknowledges the condition.
3. **Ephemeral Toast:** Peripheral floating pill (top or bottom corner), auto-dismissing
   in 4–6 seconds. Use ONLY for reversible background successes (e.g., "Draft saved — Undo",
   "Item archived"). NEVER use toasts for critical errors, system failures, or actions
   requiring conscious decision making.
4. **Blocking Modal / Dialog:** Centered dialog with backdrop scrim. Reserved strictly
   for destructive, irreversible, or high-risk actions (e.g. permanent deletion, workspace
   transfer). Requires explicit affirmative and cancel actions. Its focus behavior follows
   the recovery focus-continuity owner, [component implementation](../component-implementation.md).

## Adapt the task to people, input and language

Read when developing mobile/multi-input layouts, enlarged text, localized content,
assistive access or degraded connectivity. design-floor.md owns applicable hard
accessibility requirements; this method develops usable alternatives within them.
Use actual supported platforms and conditions, not every imaginable environment.

| Double Diamond phase | Work and hand-back |
|---|---|
| Discover | Identify audience capabilities, device/input, scripts/locales and network conditions supported by the brief. Inspect real content, browser/platform capabilities and where the task breaks. |
| Define | Name the task relationship to preserve under each relevant condition and the competing costs. Separate known requirements from unsupported platform assumptions. |
| Develop | Compare a layout/control/content adaptation on the same task. Resolve semantic structure, reading order, input alternatives and locale formatting with actual specimens. |
| Deliver | Exercise applicable conditions and retain observed evidence separately from simulated or unavailable checks. Hand concrete adaptations to tokens/Specification and unverified capabilities to Review. |

### Spatial and input adaptation

Choose layout changes at content-fit failures: preserve the information needed to
compare and act, then reflow, stage or disclose it. Coordinate typography with
[typography](visual-craft.md#typography-as-voice-and-reading-structure); smaller screens do not justify uniformly smaller text.
Test intermediate widths as well as endpoints and enlarged text without disabling
zoom. A wide table may have contained horizontal scrolling when its comparison
requires it, but labels and scroll affordances must preserve orientation.

Inspect touch and keyboard alternatives for hover/drag interactions. For mobile
entry, consider the focused field with the soft keyboard, action visibility and
scroll/focus recovery. Browser viewport emulation is not proof of physical reach,
virtual-keyboard behavior or native platform implementation. Name the actual test.

For in-scope slow/offline work, distinguish pending, stale cached content, failed
and committed state. Explain the actual retention/sync limits. Never claim saved or
offline persistence unless the product/implementation supports it. Inspect recovery
with retained input and current context through interaction-craft's path method.

### Semantic and cognitive access

Compose a logical heading/landmark and control reading order before styling.
Associate names, instructions and errors with their controls; expose changing
status without unnecessary focus moves. Walk the task by keyboard and inspect
accessible names/roles/state. A DOM/AX-tree inspection verifies semantics only;
actual screen-reader announcements require an exercised named reader/platform.
Use plain labels and visible contextual cues; reduce recall and split attention
instead of relying on lengthy instructions. Include a nonvisual equivalent for
information carried only by graphic position, color or imagery.

[WAI page structure](https://www.w3.org/WAI/tutorials/page-structure/) supports
meaningful structure and navigation. Compliance checks remain at design-floor;
this walkthrough does not claim comprehensive accessibility certification.

### Locale is meaning as well as length

Use real target-script content; test long labels, plural/variable content, mixed
identifiers and font fallback. Define language/direction and locale-aware number,
date, time and unit presentation without changing source values. Separate storage
identity from localized display. Resolve ambiguous dates and names from product
context instead of silently imposing a region's format.

For RTL, use logical layout properties and isolate mixed-direction identifiers;
mirror directional navigation where meaningful, not logos, data or every icon.
Inspect actual text order and keyboard navigation. Translate complete messages
with variables rather than concatenating fragments. Cultural imagery and metaphors
need context evidence, not language-based stereotypes.
[W3C internationalization tips](https://www.w3.org/International/quicktips/) provide
implementation pointers; a length stress fixture alone does not prove translation.

## Diagnose generic or mismatched expression

### Specialized Double Diamond workflow

**Enter with:** The actual output, raw product intent, intended language and available reference/evidence; not detector flags alone.

Follow the shared execution/return rules in [the method library](../design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect symptoms without rationale | Inspect the whole frame and actual task. Locate what feels generic, noisy, dull or misleading; compare a relevant strong reference and distinguish observation from taste. |
| Define — diagnose the owning weakness | Choose whether the problem is interpretation, proposition, composition, asset, interaction or execution. State a positive design aim and the strongest relationship to preserve; do not equate a hue or genre with failure. |
| Develop — construct a replacement | Use the relevant craft method to develop a better relationship on the same content/task. Change the causal design choice rather than deleting a list of fashionable effects or inventing new product facts. |
| Deliver — compare and return | Inspect before/after and the affected companion state. Retain the change only when the intended experience improves; otherwise revisit the diagnosis. Send evidence to the existing quality cycle, with no automatic restart based on aesthetic trait counts. |

**Retained execution record:** Symptom/location → evidence → owning diagnosis → positive aim → relationship preserved → attempted replacement → same-target comparison → disposition/remaining issue.

The craft methods below supply the choices and construction detail for this workflow.

Read when a proposal or rendered result feels generic, noisy or overstyled.
The [design floor](../design-floor.md) owns hard constraints. These are diagnostic
questions, not a blacklist of colors, fonts, genres or popular products.

| Observed weakness | Diagnose at the owning layer | Direction for revision |
|---|---|---|
| Unrelated products could swap names and keep the screen | Product opportunity/proposition | Make a meaningful task, content or emotional relationship visible |
| Mood words but no visible character | Composition | Develop type, space, color and content treatment as one proposition |
| Every group is a card with equal emphasis | Information priority | Recompose the focal task and group by relationship; retain useful boundaries |
| Beautiful opening, generic forms/details | Language transfer/component recipe | Carry one meaningful relationship into dense and consequential states |
| Sparse layout hides comparison context | IA/interaction | Place required evidence at decision time; calm comes from hierarchy |
| Decorative assets imply unsupported product capability | Product semantics/content | Show honest content or clearly identify a prototype illustration |
| Animation delays reading or judgment | Motion | Preserve immediate information and remove/reduce the competing effect |
| Same palette and type across all products | Grounding/expression | Re-derive relationships from actual content, identity and context |

Turn a symptom into a positive design aim before removing elements. “Too generic”
might mean weak content hierarchy, absent subject matter, interchangeable imagery
or no coherent voice; each needs a different experiment. Compare the revision to
the same task and a relevant strong reference. Removing cards, gradients or a font
without developing the replacement can merely exchange one default for another.

Inspect before reading the explanation. State the strongest relationship to
preserve and the most consequential mismatch, with a visible location or task
moment. Judge a quiet, dense, raw, playful or conventional language by fit and
craft. Do not soften an earned raw style into a house default, or inject grit
into a calm product merely to appear original. Fix the cause, not a forbidden hue.

## Criticism that changes the design

### Specialized Double Diamond workflow

**Enter with:** Original product source, actual target and scope, intended language after initial inspection, and permitted evidence tools.

Follow the shared execution/return rules in [the method library](../design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — establish the task and examine the work | Derive the task, supported actions/objects and required contexts from the original source before the target. Then inspect composition before designer rationale; attempt core task, recovery and return where runnable. Sample relevant viewports/states and record what was actually observed, judging visual craft from rendered actual-size views as [Quality bar](../quality-bar.md) requires. An unrendered proposal has different evidence from a live interface. |
| Define — frame the important gaps | Account for applicable craft areas and the seven quality dimensions. Separate objective defects, expert judgments and preferences; identify consequential user impact and the owning decision without allowing a total score to hide a weak area. |
| Develop — direct an owning revision | Recommend specific interventions and evidence that would show improvement, protecting the strongest idea. Main reconciles against original facts and dispatches the responsible design/Builder work; Critic does not edit or select on the user’s behalf. |
| Deliver — verify the changed target | Reinspect the same task/frame and relevant transfer after repair. Retain first and revised evidence, resolved/unresolved claims and acceptance limits. Return to diagnosis when the intervention fails; the existing quality/lifecycle rules own the bounded cycle and final decision. |

**Retained execution record:** Area/state/location → observed evidence → effect/severity → fact/judgment/preference → owning revision → preservation target → before/after result → pass/fail/unverified/scope reason. Numeric scoring uses the separately pinned rubric; inspection is not user research.

The craft methods below supply the choices and construction detail for this workflow.

Read before visual and interaction proposals reach a human decision, and when
reviewing runnable work. [Quality bar](../quality-bar.md) owns the cycle and
acceptance; this reference supplies diagnosis and intervention methods.

First establish the task basis from the original product source. Inspect the work
without designer rationale and compare its actual actions and required contexts
to that basis; inspect the intended proposition afterward. Separate four questions: is the interpretation
right, is the idea useful, is the expression convincing, and is execution faithful?

For a metaphor-led proposition, apply its capability-preserving translation
check before judging novelty: unsupported operations or invented diagnoses
invalidate the recommendation even if the expression is persuasive. Critique
the concrete scene presented now; a promise to develop it after selection is
not evidence that its trade-off works.

| Problem in the work | Useful intervention | Evidence after revision |
|---|---|---|
| Competing attention/weak reading order | Distill, regroup, recompose; protect the information needed to decide | Same content/frame with a clear reading path |
| Typography lacks voice or legibility | Reassign roles, tune contrast/measure/rhythm, verify actual glyphs | Dense text and narrow/enlarged sample |
| Color feels muddy, monotonous, heavy or indiscriminately loud | Revisit field lightness, hue/chroma relationships, colored area and imagery; compare controlled treatments | Same-layout color comparison and transfer to a consequential state; contrast alone cannot pass this judgment |
| Idea is competent but interchangeable | Develop a stronger product-specific proposition, not more effects | Signature survives a contrasting task |
| Expression overpowers use | Quiet the competing layer; retain the strongest relationship | Core action from visible cues without explanation |
| Copy or state is ambiguous | Clarify consequence, actor, current state and recovery near the action | Pre-action → result → later-visit walkthrough |
| Controls are consistent but inconvenient | Reframe the decision, compare context placement and continuation | Same task plus interruption/recovery |
| Recipe or theme drifts in implementation | Normalize the component/token mapping at its owner | Computed styles and composed state sequence |
| Only happy-path behavior works | Harden the specified edge cases without inventing policy | Retained input, retry/back/keyboard evidence |

Evaluate facts and execution, experienced utility, and crafted expression as
separate judgments. On a consequential new language, account for the applicable
craft areas from the method router: a strong task flow cannot offset weak type,
color, imagery or iconography. Conversely, an excellent image cannot compensate
for an unclear interaction. Identify absence, weakness and intentional restraint
accurately; no image or animation is required solely to fill a review row.

Use a reference comparison to calibrate craft when available, naming the relevant
relationship rather than resemblance to a brand. Distinguish an objective defect,
a supported design judgment and a preference; make subjective recommendations
specific enough to inspect. Preserve the strongest idea while developing a better
alternative, not only deleting what triggered a warning.

Impeccable's critique/audit and targeted operations inform these interventions;
invoking a command is optional, while an evidence-backed diagnosis is required.
Read [external evaluation](resilience-trust.md) when numerical assessment
is requested. Keep expert judgment separate from detector findings. A low-level
scan can reveal drift but cannot establish emotional fit or visual authorship.

Record location/state, user impact, severity, owning decision, proposed change,
strongest idea to preserve and the observation that would demonstrate improvement.
Revise the relevant design brief before Builder regeneration when the issue is
in the idea. Preserve required assertions; a repair cannot lower its own target.
Show consequential changes before requesting the existing human decision.

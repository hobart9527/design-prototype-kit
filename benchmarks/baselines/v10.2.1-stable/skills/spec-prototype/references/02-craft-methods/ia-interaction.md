# Objects, journeys, Surface Topology and interaction

> **Pillars**: `Object` · `Journey` · `Topology` · `Interaction`  
> **Core Invariants**: OOUX Entity Grounding · The Container Proximity Ladder · 3-Tier Wayfinding · Flow Continuity

Read when defining product structure, navigation, pages/surfaces, task flows or
state behavior. Enter with the current Product Thesis and sources. This reference
owns structure and continuity; it does not turn product hypotheses into facts or
visual preferences into page boundaries.

## Cardinality-to-layout mapping

Map object relationships to structural presentation. Start with the established container for the cardinality before exploring a domain-specific spatial metaphor:
- **1 : 1 or Monolithic Object**: Focused Document, Inspection Canvas, or Dedicated Setting Panel.
- **1 : N Collection**: Master-Detail, Interactive Table, or Faceted Feed with high-speed scanning controls.
- **N : M Network / Graph**: Node-Link Canvas, Multi-Column Board, or Relational Split View.

When the authentic domain context genuinely demands a specialized physical layout (e.g. continuous film strip, concentric radar, seismic trace stack), it may replace the conventional container — but must preserve 3-tier wayfinding and keyboard navigation.
Never invent navigation containers before mapping this cardinality.

## The Container Proximity Ladder (交互容器匹配阶梯与心流守则)

Action hazard level and input complexity strictly dictate container intrusion level. Never deploy a heavier container than the action's consequence warrants:

| Level | Action Hazard & Complexity | Target Interaction Container | Architectural Invariants & Behavior |
|---|---|---|---|
| **Level 0** | **In-situ ephemeral mark / state toggle**<br>(Text selection highlight, bookmark toggle, quick tag, status flick) | **In-situ Popover / Selection Detent / Direct Tap** | - Zero blocking backdrop/scrim.<br>- Single-interaction commit; zero redundant "Confirm/Submit" modal buttons.<br>- Never dismiss or displace reading/editing viewport context. |
| **Level 1** | **Contextual tuning & auxiliary facets**<br>(Typography adjustments, quick sort/filter popover, inline preview) | **Anchored Flyout / Floating Dock / Popover Menu** | - Anchored relative to the trigger element.<br>- Light-dismiss on blur/outside click.<br>- Edits apply optimistically with immediate visual preview. |
| **Level 2** | **Associated context & inspector panel**<br>(Paragraph marginalia, entity attribute inspector, audit thread) | **Sticky Marginalia / Companion Inspector Column** | - Sits co-planar alongside primary content.<br>- Scrolls in physical alignment with active entity.<br>- Never covers or darkens primary reading/canvas surface with a modal scrim. |
| **Level 3** | **Dense multi-field form or workflow setup**<br>(Complex entity creation, multi-step filter builder, parameter config) | **Structured Drawer / Slide-over** | - Reserved strictly for operations requiring 3+ distinct input fields.<br>- Retains main surface state behind a non-modal or light-scrim partition.<br>- Draft inputs survive accidental dismissal. |
| **Level 4** | **Destructive, hazardous, irreversible commit**<br>(Cluster node drain, database wipe, bulk delete, capital transfer) | **Blocking Modal / Confirmation Dialog** | - Mandatory explicit 2-step verification.<br>- Action buttons must use explicit action verbs (e.g., "Drain Node", "Revoke Key"), never generic "OK". |

**Flow Preservation Principle (心流不被打断公理)**:
1. **Reversibility dictates friction**: When an action can be trivially undone (e.g., untoggling a bookmark, removing a highlight), blocking confirmation modals or full-height drawers are strictly forbidden.
2. **Single-field input remains in-situ**: Operations requiring only 1~2 fields (e.g., a quick note, rename, threshold value) must expand in-situ rather than summoning a full-height drawer.
3. **Entity degradation over amnesia**: On mobile/narrow viewports, contextual entities (like annotations or inspectors) must fold into compact bottom-sheet or drawer triggers, never vanished completely via ungraceful `display: none`.

## 1. Model objects and content before containers

OOUX/ORCA is the default object-and-action lens here: name first-class objects,
relationships, calls-to-action and attributes before choosing containers. Keep
object ownership explicit across the journey; an action changes its owning
object, and its visible result belongs to that object's lifecycle and authority.
When an object, relationship or permission is not established by product sources,
leave it `unknown` and route the unresolved risk to the existing Product, Journey,
Surface or Contract record. Do not create a parallel object registry.

Inventory the real nouns, content and actions people work with:

| Question | Retained result |
|---|---|
| What is a first-class object versus an attribute, event or view? | Object/content vocabulary |
| Who creates, reads, changes, approves or owns it? | Role and authority relation |
| What states and lifecycle transitions exist in product sources? | Sourced lifecycle; unknown policy remains open |
| What relationships and cardinalities matter to the task? | Parent/child, membership, reference and sequence |
| What content must be scanned, compared, edited or remembered? | Content structure and range |
| Which action changes which object and what visible result follows? | Object-owned actions and feedback |

Use OOUX/ORCA when it helps expose Objects, Relationships, Calls-to-action and
Attributes; it is a method, not a mandatory schema. A domain model is not yet a
navigation tree.

## 2. Coherent wayfinding, context preservation and content mechanics

Establish a three-tier wayfinding system across all journeys:

1. **Global Orientation**: Unambiguous visual and mental indicators of where the user
   is, what mode they occupy, and how to safely return or switch context without data loss.
2. **Contextual Navigation**: Clear affordances for related objects, drill-downs,
   and batch operations without forcing full-page redirects.
3. **Context Preservation**: When the user branches into secondary workflows (e.g.
   quick inspection, configuration, or error resolution), their draft edits, scroll
   position, and filter states must be preserved. Discarding unsubmitted work context
   upon closing or canceling an overlay is an architectural design failure.
4. **Content Mechanics as Interaction Spine**:
   - Action verbs must maintain exact semantic continuity across the lifecycle: the trigger
     verb (e.g. "Quarantine"), dialog heading ("Quarantine Worker"), primary commit button
     ("Quarantine"), and post-completion toast must share identical vocabulary.
   - Microcopy must describe consequences, reversibility, and affected entities explicitly
     before consequential state transitions.

## 3. Walk jobs as journeys and service relationships

A journey is more than a happy-path sequence: mark the decision moments where
people choose, compare, commit, delegate, wait or recover. At each moment retain
who acts, the object and authority in play, visible system status, the next
reachable action, and the consequence of delay or error. Route a missing
frontstage/backstage dependency or cross-role promise to the existing Journey or
Contract owner; do not repair service design by adding an unowned surface.

For every in-scope core job, trace:

```text
trigger and entry
  -> orientation and information needed
  -> decision/action and precondition
  -> visible feedback and system work
  -> result, recipient or handoff
  -> return, interruption or recovery when applicable
```

Include relevant role/channel changes and frontstage/backstage dependencies. Test
direct entry, back navigation and preservation of filters, selection, draft input
or work context when the job needs them. A first-use journey cannot be the only
route to existing work. Do not invent background jobs, permissions, persistence
or notifications to make a flow look complete.

Use realistic minimum, typical, maximum and awkward content. Distinguish a label
or category failure from an entry that is merely hard to see and from a control
that fails after activation; each belongs to a different owner.

## 3. Derive Surface Topology

Create a distinct page, route or durable surface when at least one structural
reason applies:

- it supports an independent goal or work mode;
- it needs addressability, sharing, history or recoverable re-entry;
- it has materially different authority, audience or lifecycle;
- the user needs a persistent work context;
- information must remain simultaneously comparable;
- density, device or input constraints cannot stay clear in the current surface.

When none applies, consider an inline region, progressive disclosure, drawer,
modal, popover, split view, command surface or another fitting container. This is
an open set. A domain object, feature or loading/error condition does not
automatically become a page.

For every proposed surface, record its job, reason for independence, route/parent,
entry/exit, shared context, authority and responsive transformation. Also record
the total in-scope surface count, explicit split/merge rationale, journey coverage
and deliberate non-coverage. Re-run the relevant journey after a split or merge.

### Split and merge test

Before splitting, ask whether the user benefits from an address, durable context,
separate lifecycle, simultaneous visibility or density relief. Before merging,
ask whether distinct goals, authority or recovery become hidden. Prefer the
smallest topology that preserves object boundaries and task continuity, not the
fewest screens.

## 4. Design information and interaction at the decision moment

At each consequential step, specify what the person sees, understands, compares,
does and learns from the response. Explore a different operation model when it
could remove mental work, improve control or make a product relationship visible.
Hold product capabilities and representative content constant while comparing.

Consider discoverability, information density, switching cost, context retention,
frequency, risk, latency, interruption, keyboard/focus behavior, touch target,
mobile transformation and implementation feasibility. Fewer clicks or greater
novelty alone is not a benefit; name the expected improvement and an observation
that could refute it.

Use [data and task design](data-information.md#design-information-for-decisions-and-repeated-work)
for comparison/search/filter/batch work, [interaction craft](interaction-power.md#develop-an-interaction-model-around-the-users-judgment)
for operation-model choices, and [inclusive adaptation](resilience-trust.md#adapt-the-task-to-people-input-and-language)
for device, input, language and accessibility transformations. Check component
feasibility with [component implementation](component-implementation.md) before
freezing a design that depends on a particular primitive.

## 5. Select states by reachability and risk

For each surface or transition, derive applicable states from product behavior and
the job: loading/progress, empty, error/retry, permission/read-only, success,
overflow, offline/degraded, interruption, conflict or others. Record the trigger,
user need, behavior, recovery and evidence. Mark a familiar state family
inapplicable when it cannot occur or adds no useful test.

Do not implement a universal state checklist. High-risk or asynchronous work may
need more state coverage than a static informational surface. Preserve semantic
status independently of its visual treatment.

## 6. Validate structure and coverage

Use the same objects, content and tasks across alternatives. Exercise finding,
acting, interruption/recovery and return from visible cues. When evidence is
limited, label an expert walkthrough and propose card sorting, tree testing,
first-click or task-based research for the exact uncertainty; simulated users do
not establish a research result.

Topology is ready for the current prototype when the representative tasks have
coherent paths, surfaces have distinct jobs, necessary information is available
at decision time, role/authority boundaries are explicit, and no unresolved
structural prerequisite forces Builder invention. Low-risk reversible details may
remain delegated.

Record the result in [the Surface Map](../../templates/surface-map.md). Retain a map
snapshot before candidate compilation. A Walking Skeleton may cover one or many
surfaces according to the task; it is a validation batch, not a page quota. Whole-
product delivery still accounts for every promised surface and journey.

New evidence reopens only the owning object, journey, topology or interaction
decision and its dependents. Preserve unaffected choices and exact historical
artifacts.

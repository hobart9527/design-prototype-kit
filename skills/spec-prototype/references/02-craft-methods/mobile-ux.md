# Mobile UX — Touch-Native Design Methods

Read when the physical anchor or declared chassis is touch-native (a portable
device, handheld scanner, mobile checkout, wearable companion). This file owns
mobile-specific spatial and interaction decisions; `craft-floor.md` owns the
universal 44px floor and is always read first.

## Thumb-Zone Architecture (拇指区空间策略)

The thumb's natural arc — not the finger's reach — is the primary spatial
constraint. It determines what is reachable without grip shift, not what is
merely visible.

- **Primary commit zone** (bottom 40% of screen height): the most consequential
  and most frequent actions. The zone contracts on screens below 375px.
- **Secondary reach zone** (middle 40%): content, status, contextual controls.
  Actions here require deliberate reach; reserve for non-urgent taps.
- **Hazard zone** (top 20%): never place primary navigation or commit controls
  here. Acceptable for passive status display (time, signal, battery).

Never mirror a desktop layout by centering the action at the top of the screen.
The mental model is a physical tool held in one hand, not a shrunken desktop.

## Gesture Priority and Conflict Resolution

Declare gesture claims explicitly; conflicting system gestures are silent failures.

- **Horizontal swipe**: owned by the system (back navigation on iOS, drawer on
  Android) unless the surface explicitly registers a competing claim with a
  detent. Competing claims must expose a visible affordance; invisible swipes
  are not interactions, they are traps.
- **Vertical swipe with pull-to-refresh**: register only at the scroll origin;
  never conflict with page scroll momentum.
- **Long-press**: a hazard-level action trigger only — content selection, drag,
  destructive preview. Never a discovery mechanism for primary features.
- **Pinch / spread**: exclusive to spatial surfaces (maps, canvases, media).
  Never overload in non-spatial contexts.
- **Double-tap**: secondary positive signal (like, zoom-in). Never the primary
  commit path for consequential actions.

Document every claimed gesture in the spec with its conflict boundary.

## Information Hierarchy on Narrow Viewports

A narrow viewport is not a smaller version of the full layout. It is a different
reading context with a different first question.

- **State the narrow view's primary question** before recomposing. The first
  visible element must answer that question without scroll.
- **Progressive disclosure, not compression**: data that does not fit at 390px
  is hidden behind a labeled disclosure, not squeezed into 8px type.
- **Tables do not squeeze**: a multi-column table below its minimum readable
  width becomes a card list (label/value pairs). Keep the identity column,
  primary state, and one action; demote all others behind a disclosure trigger.
- **Entity hierarchy over type hierarchy**: in narrow contexts, the object's
  identity (name, ID, status) always precedes its metadata. Never let a
  timestamp lead a row at 390px.

## Bottom Sheet and Drawer Strategy

Bottom sheets carry contextual detail and secondary task flows; they are not
modal replacements.

- **Non-blocking half sheet** (≤55% screen height): contextual detail, quick
  actions, filter controls. Always dismissible by swipe-down or outside tap.
  Main content remains visible behind the sheet.
- **Full sheet** (>55% screen height, up to near-full): multi-field forms,
  step-through flows. Requires an explicit close control; outside tap does NOT
  dismiss — the user has entered a focused context.
- **Snap points**: declare them explicitly. A sheet with no snap points snaps
  to wherever the gesture releases — this is unpredictable, not fluid.
- **Drawer from edge**: for navigation or secondary panels; triggered from an
  edge affordance. Never launched by a center-screen button.

A bottom sheet for a single-field input is always wrong. Use in-situ expansion
or an anchored popover instead.

## Single-Hand Flow Invariant

The primary task path must be completable without grip shift. A flow that
requires tapping the top-left corner then the bottom-right corner in sequence
is a two-handed flow, regardless of whether it physically requires two hands.

- Measure each step: is its target reachable with the thumb while the device
  is held in the right hand at a natural grip? Left hand? Evaluate both.
- When a step cannot be made single-hand reachable, make the two-hand
  engagement intentional and visible — a bimanual confirmation that signals
  the gravity of the action.

## Recomposition Checklist

Before declaring a mobile surface complete, verify:

1. Primary question answered above the fold at 390×844px.
2. All commit controls in the primary or secondary thumb zone.
3. No horizontal scroll at 320px without explicit horizontal surface declaration.
4. Tables recomposed to card/list format at narrow breakpoint.
5. All bottom sheets have declared snap points and a visible close affordance.
6. Every gesture claim is documented and system-conflict-free.
7. Long-press never used as the sole path to a primary feature.
8. Touch targets ≥ 44×44px on all interactive elements (from `craft-floor.md`).

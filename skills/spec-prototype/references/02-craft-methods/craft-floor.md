# Craft Floor — Verify and Refuse

Read before the first runnable write. This is the generating-side floor: it keeps
the work out of the category's defaults and off the cheapest failure modes. The
committed direction and the product's own evidence override anything here; habit
does not. The audit-side owner remains
[`../03-verification/quality-floor.md`](../03-verification/quality-floor.md) —
this file cites it and never restates its numbers.

## Verify

Checks on the built result, not on intentions. Run them together in the batched
inspection pass, not as separate screenshot trips.

- **Press feedback** `CRAFT-PRESS-DETENT`: every commit control (submit, confirm,
  apply, destructive action) shows a perceptible `:active` change. Plain links and
  pure navigation are out of scope. The value is authored per surface, never copied
  as a house number; the defect is a missing detent, not a particular scale.
- **Touch targets** `CRAFT-TOUCH-TARGET`: interactive controls measure at least
  44×44px in touch contexts.
- **Concentric radii** `CRAFT-CONCENTRIC-RADII`: a rounded child inside a rounded
  parent with padding `P` satisfies `R_inner = max(0, R_outer − P)` within 1px.
- **Numeric stability** `CRAFT-TABULAR-NUMS`: values that update in place or align
  in columns carry `font-variant-numeric: tabular-nums`; prose numbers are out of
  scope.
- **Action safety & reversible feedback** `CRAFT-ACTION-FEEDBACK`: destructive or high-stakes
  actions (drain, offline, delete, terminate) must provide a closed loop:
  1. Consequence clearly visible before commit.
  2. Perceptible state feedback immediately after action (`处理中`, `已排空`, `draining`, etc.).
  3. Recovery, rollback, or safe exit reachable on the same surface (`撤销`, `回滚`, `rollback`, `undo`).
- **Surface optics and top sheen** `CRAFT-SURFACE-SHEEN`: elevated panels and dark surfaces
  simulate optical chamfers with hairline top highlights (`var(--surface-sheen)`) instead of
  flat mechanical borders alone.
- **Kinetic physics** `CRAFT-KINETIC-SPRING`: transition and motion curves use organic spring
  physics (`var(--spring-snappy)`, `var(--spring-gentle)`) rather than linear or mechanical `ease`.
- **Browser surfaces** `CRAFT-SELECTION` `CRAFT-CARET` `CRAFT-SCROLLBAR`
  `CRAFT-FOCUS-RING`: the parts you did not draw still carry the design. Text
  selection, the caret (`caret-color`), custom scrollbars, focus rings, underline offset, and
  tabular numerals ship with browser defaults belonging to no design system.
  Theme them from the palette. This is the cheapest signal that a page was built
  rather than assembled, and the one that gets skipped most reliably.
- **Real content and real assets** `CRAFT-REAL-CONTENT`: plausible domain copy,
  real names, and the number of items the surface will actually carry. When no
  credible image asset exists, rearrange the layout and drop the slot — never fill
  it with a gradient blob, a gray box, or a decorative SVG standing in for a
  picture.
- **Theme origin** `CRAFT-THEME-ORIGIN`: light or dark is chosen from the use
  scene — who, where, under what ambient light — not from the product's category.
- **Reduced-motion pairing** `CRAFT-REDUCED-MOTION`: any surface that ships
  spring or animated transitions pairs them with a `prefers-reduced-motion`
  fallback that preserves the state change without the motion. Motion is the
  enhancement; the state change is the contract.
- **Live status regions** `CRAFT-ARIA-LIVE`: a status that updates in place
  (progress, drain state, toast, live feed) exposes `aria-live="polite"` (or
  `assertive` for urgent) so assistive technology perceives the change. A
  progress bar the screen reader cannot hear is a state change that never
  happened for that user.
- **Fluid type** `CRAFT-FLUID-TYPE`: display and body sizes scale with the
  viewport through `clamp()` (or `min()`/`max()`), so the 390 and 1280 frames are
  one type system rather than two hand-set tables. Advisory.
- **Color scheme** `CRAFT-COLOR-SCHEME`: the chosen theme declares
  `color-scheme` (light, dark, or both) so native controls, scrollbars and form
  fields follow it. A dark surface with a white scrollbar reads as unfinished.
  Advisory; a second theme is optional unless the brief asks for one.
- **Loading state** `CRAFT-LOADING-STATE`: a region that loads or refreshes shows
  a skeleton or `aria-busy="true"` rather than blank space. Advisory.
- **Contextual metric** `CRAFT-CONTEXTUAL-METRIC`: a number on a surface carries a
  baseline, unit, delta, or sparkline. This is the id for the VPQ `data-craft`
  signal; it has no text detector.

### Rule IDs are the anchor

The bold ids above are not decoration. They are the join between this prose and
the machine checks, and they resolve in both directions:

- `python3 skills/spec-prototype/scripts/detect.py --artifact <file>` runs every
  rule that *can* be read off the artifact and reports it under its id. A rule
  whose detector is absent is returned as `prose_only` with the reason it cannot
  be mechanised, so "not machine-checkable" is a recorded status rather than a
  silent gap.
- The benchmark's `slop_detector.py` carries its own ids (`SLOP-001` … `SLOP-025`);
  `detect.py`'s `BENCHMARK_ANCHORS` maps each one onto the craft-floor id it
  checks, so the two rule sets cannot drift apart unnoticed.

A rule added here without an id is invisible to that join. Add the id when you
add the rule; a detector is optional, an id is not.

## Refuse

These are the category's defaults, not bans. The brief's own words can earn any
of them back; reaching for one while the axis is free means the choice was not
made. When you catch one, rewrite the element rather than softening it.

- **Same-size card grids** `CRAFT-CARD-GRID-EARNED` — icon + heading + text
  repeated as the page structure. Cards are the lazy container; nested cards are
  always wrong. Earn it: a genuinely peer set of comparable objects.
- **Hero-metric template** — one large number, a small label, supporting stats,
  an accent. Earn it: the number is the product and its context is real.
- **Eyebrow or kicker above a heading** `CRAFT-NO-EYEBROW`. No brief earns this
  one back: the heading carries its own weight. Delete the label.
- **Section numbers** (`01 / 02 / 03`) unless the sequence itself carries
  information the reader needs.
- **Gradient text** `CRAFT-NO-GRADIENT-TEXT` for emphasis. Emphasis comes from
  weight, size, or space.
- **Glass and blur as decoration** rather than a specific, justified effect.
- **Ghost cards** — a 1px border sitting under a wide soft shadow. Declare
  elevation once: border or shadow, not both.
- **Decorative chrome standing in for content** — sparklines, progress rings, and
  soft-shadowed rounded rectangles with nothing to say.
- **Emoji or Unicode glyphs as the icon system** `CRAFT-NO-EMOJI-ICON`. Icons are
  drawn: a real library or authored SVG, one consistent stroke and weight.
- **A modal** for a task that needs neither interruption nor protected focus.
- **Monospace as a costume** for "technical" rather than for code, data, or
  measurement.
- **Uniform radii everywhere**, or pills applied to large containers. Card radii
  are a decision; pills belong to small controls.
- **Stripes and grid overlays as background texture** with no canvas, map,
  blueprint, or measuring tool underneath them.

## Render defect scan

Rendered output fails differently from authored markup. These are read off the
captures, never off the source. Run this list against every capture you take.

- **Overlay positioning:** a `<dialog>`, popover, or toast is centered and inside
  the viewport. A global reset (`* { margin: 0 }`, `*, *::before { all: unset }`)
  removes the UA centering of `<dialog>`; restore `margin: auto` yourself.
- **Native controls after a reset:** `<dialog>`, `<details>`, `<summary>`, and
  `<table>` lose their UA behavior under an aggressive reset. Re-author what the
  reset removed, or scope the reset away from them.
- **Narrowest viewport:** at the smallest declared width, no horizontal scroll,
  no element wider than its container, and no identifier broken mid-token. A
  cluster label, a hostname, or a title that wraps to three lines is a reflow
  failure, not a long-string success.
- **Reading order under reflow:** when a surface recomposes for a narrow
  viewport, the first-glance information stays first. Text that a heading splits
  across lines was never given room to be read.
- **Sticky and fixed layers:** a sticky header/toolbar does not cover the
  content it labels or the control it sits above.
- **Empty and long states:** a zero-item region has an authored empty state, and
  the longest plausible value is the one you actually put in the fixture.

## Responsive recomposition, not compression

A narrow viewport is a different reading context, not a smaller desktop.

- **Recompose by priority:** decide what the narrow view must answer first, then
  build a structure for it. A wide table shrunk into a 390px column is a
  compression defect — the desktop `grid-template-columns` will not reflow a
  table into something readable.
- **Tables degrade, they do not squeeze:** below the point where columns still
  scan, a data table becomes a list of rows (label/value pairs) or a set of
  cards. Keep the identity column, the state, and the primary action; demote the
  rest behind a disclosure.
- **Touch targets and type survive:** 44×44px minimum, and body copy keeps its
  measure; never reduce to fit.
- **The declaration is the contract:** if the brief or spec names a glance
  surface, that surface answers its own question. It is not the desktop surface
  with smaller text.

## Signature mechanisms must keep their promise

When the design's own proposition depends on a mechanism, check the mechanism,
not the copy describing it.

- **State the claim, then look for it in the render.** "Double sign-off",
  "recoverable", "audited", "requires confirmation", "one-click" are claims. Each
  must be observable in the built artifact.
- **Two-person control needs two people.** Independent approval cannot be
  authored as one actor ticking a second checkbox in the same dialog, session,
  or browser. Without a second authenticated actor the mechanism is theatre; either
  build the real handoff (a distinct approver, second session, or out-of-band
  channel) or state plainly in the record that the second signature is
  [`hypothesis`] and unimplemented. Never present a single-actor flow as double
  sign-off.
- **Recoverable means the reversal is reachable** from the surface where the
  consequence is visible, not from a settings page two navigations away.
- **Declared means rendered.** An action, state, or shortcut named in the spec
  that appears nowhere in the artifact is a finding, not an omission to be
  quietly dropped.

## Vague words

An adjective is never a justification. `premium`, `refined`, `elegant`,
`restrained`, `modern`, `高级感`, `精致`, `克制` expand into a parametric
constraint plus an observable counter-example, or they do not ship. The
translation protocol lives in
[`../01-foundations/design-language.md`](../01-foundations/design-language.md#qualitative-adjective-translation-protocol)
and is cited here, not duplicated.

## Progressive Escalation

This floor is the default. It does not demand AAA accessibility, sub-millisecond
interaction budgets, or multi-modal input primitives on every pass. Escalate
only when the brief explicitly names them, when the artifact is headed for
production handoff, or when the user invokes a P9+ polish review. Otherwise
the floor keeps the work out of the category's defaults without turning every
prototype into a certification exercise.

The floor holds the mechanics; it never picks the direction. Once every check is
green, spend the surface on the committed proposition — and when torn between
refined and committed, commit.

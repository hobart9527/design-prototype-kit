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

- **Press feedback:** every commit control (submit, confirm, apply, destructive
  action) shows a perceptible `:active` change. Plain links and pure navigation
  are out of scope. The value is authored per surface, never copied as a house
  number; the defect is a missing detent, not a particular scale.
- **Touch targets:** interactive controls measure at least 44×44px in touch
  contexts.
- **Concentric radii:** a rounded child inside a rounded parent with padding `P`
  satisfies `R_inner = max(0, R_outer − P)` within 1px.
- **Numeric stability:** values that update in place or align in columns carry
  `font-variant-numeric: tabular-nums`; prose numbers are out of scope.
- **Browser surfaces:** the parts you did not draw still carry the design. Text
  selection, the caret, custom scrollbars, focus rings, underline offset, and
  tabular numerals ship with browser defaults belonging to no design system.
  Theme them from the palette. This is the cheapest signal that a page was built
  rather than assembled, and the one that gets skipped most reliably.
- **Real content and real assets:** plausible domain copy, real names, and the
  number of items the surface will actually carry. When no credible image asset
  exists, rearrange the layout and drop the slot — never fill it with a gradient
  blob, a gray box, or a decorative SVG standing in for a picture.
- **Theme origin:** light or dark is chosen from the use scene — who, where, under
  what ambient light — not from the product's category.

## Refuse

These are the category's defaults, not bans. The brief's own words can earn any
of them back; reaching for one while the axis is free means the choice was not
made. When you catch one, rewrite the element rather than softening it.

- **Same-size card grids** — icon + heading + text repeated as the page
  structure. Cards are the lazy container; nested cards are always wrong. Earn
  it: a genuinely peer set of comparable objects.
- **Hero-metric template** — one large number, a small label, supporting stats,
  an accent. Earn it: the number is the product and its context is real.
- **Eyebrow or kicker above a heading.** No brief earns this one back: the
  heading carries its own weight. Delete the label.
- **Section numbers** (`01 / 02 / 03`) unless the sequence itself carries
  information the reader needs.
- **Gradient text** for emphasis. Emphasis comes from weight, size, or space.
- **Glass and blur as decoration** rather than a specific, justified effect.
- **Ghost cards** — a 1px border sitting under a wide soft shadow. Declare
  elevation once: border or shadow, not both.
- **Decorative chrome standing in for content** — sparklines, progress rings, and
  soft-shadowed rounded rectangles with nothing to say.
- **Emoji or Unicode glyphs as the icon system.** Icons are drawn: a real library
  or authored SVG, one consistent stroke and weight.
- **A modal** for a task that needs neither interruption nor protected focus.
- **Monospace as a costume** for "technical" rather than for code, data, or
  measurement.
- **Uniform radii everywhere**, or pills applied to large containers. Card radii
  are a decision; pills belong to small controls.
- **Stripes and grid overlays as background texture** with no canvas, map,
  blueprint, or measuring tool underneath them.

## Vague words

An adjective is never a justification. `premium`, `refined`, `elegant`,
`restrained`, `modern`, `高级感`, `精致`, `克制` expand into a parametric
constraint plus an observable counter-example, or they do not ship. The
translation protocol lives in
[`../01-foundations/design-language.md`](../01-foundations/design-language.md#qualitative-adjective-translation-protocol)
and is cited here, not duplicated.

The floor holds the mechanics; it never picks the direction. Once every check is
green, spend the surface on the committed proposition — and when torn between
refined and committed, commit.

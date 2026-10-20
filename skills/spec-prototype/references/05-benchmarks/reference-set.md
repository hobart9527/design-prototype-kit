# Reference Set — the anchor for the upper bound

The craft floor and `detect.py` anchor the **lower** bound: they catch slop. They
say nothing about what a *good* answer looks like. This file is the anchor for the
upper bound, and it exists because without one the ceiling is whatever the model
happens to remember — which is a taste claim with no evidence behind it.

**Owner**: this file owns the reference set. `dialectic/01-metaphor-benchmark.md` §3
cites it for Stage 2's benchmark calibration and does not restate it.

## What makes an entry an anchor rather than a name-drop

A product name is not evidence. Each entry below names an **observable mechanism** —
a specific thing you can look at in the real product and check against your own
build. "Linear is clean" is a vibe; "the command palette keeps focus inside the list
and never returns it to the page" is a mechanism, and you can verify whether your
palette does the same.

Read an entry for its mechanism, then ask whether your surface earns it. Copying the
surface without the mechanism is the costume failure this set exists to prevent.

## The set

Deliberately small and stable. Each entry: the mechanism to inspect, what to adopt,
what to refuse, and the Pillar / Axis it calibrates. Each mechanism was checked
against the product's own documentation when it was added; re-check the source
before you lean on one, and drop or correct an entry that no longer holds.

| Reference | The observable mechanism | Adopt | Refuse | Calibrates |
|---|---|---|---|---|
| **Linear** | Command palette: single-key dispatch, focus never leaves the list, status advances without a page change | Keyboard sovereignty; state advances in place | Low-friction dismissal of serious commits; treating speed as an excuse for no confirmation on destructive acts | Interaction pillar · Energy axis |
| **Bloomberg Terminal** | Multi-pane concurrency: many instruments visible at once, each with its own density and its own update cadence | High-density throughput; concurrent panes | Uncurated visual noise — density is curated here, not merely present | Attention pillar · Density axis |
| **Stripe** | Progressive disclosure in forms: the next field appears only when the previous one makes it relevant | Trustworthy typographic hierarchy; disclosure paced to need | Generic bloated card padding used to fake spaciousness | Object pillar · Rhythm axis |
| **GitHub PR** | Diff collation: change, discussion and approval lineage on one surface, in one reading order | Explicit approval lineage; diff as the primary object | Raw engineering jargon leaking into user-facing copy | Journey pillar · Materiality axis |
| **Gov.uk** | One question per page; the answer's consequence stated before the control | Task-pattern clarity; prerequisites before backtracking | Treating a wizard as the universal answer to a long task | Value pillar · Character axis |
| [**Gov.uk check answers**](https://design-system.service.gov.uk/patterns/check-answers/) | Every answer on one summary surface, each row carrying its own *Change* link with a hidden qualifier, and a return that keeps the prior entry and lands back on the summary | One reviewable surface before commit; per-row correction that returns | Using the summary as a second form, or dropping the person back at the flow's start | Journey pillar · Rhythm axis |
| [**Gov.uk error summary**](https://design-system.service.gov.uk/components/error-summary/) | On a failed submission: a summary above the content listing each problem as a link to its control, the same wording repeated inline, and keyboard focus placed on the summary at load | One discoverable index of what failed; identical wording in both places; focus where the fix begins | Listing problems with no route to the control, or restating them in different words | Resilience pillar · Character axis |
| [**Atlassian inline message**](https://atlassian.design/components/inline-message/examples) | The variant is chosen by *when* it appears relative to the action — warning before the action is asked for, error after a failed attempt, confirmation after completion, info for context — anchored below the trigger by default | Feedback at the control it concerns, timed to the moment | A page-level flag or modal carrying what belongs beside the control | Interaction pillar · Energy axis |
| [**GitHub PR suggested changes**](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/incorporating-feedback-in-your-pull-request) | A reviewer's edit arrives as a committable proposal inside the object under review; accepting it creates one commit and credits the suggester as co-author | A proposed change stays distinct from accepted fact; acceptance is one explicit act | Auto-applying a suggestion, or collapsing proposal and acceptance into one ambiguous "apply" | Object pillar · Materiality axis |
| [**Apple HIG undo/redo**](https://developer.apple.com/design/human-interface-guidelines/undo-and-redo) | Undo offered for every content-changing action, with a redo whenever undo exists and an action-specific label (*Undo Quarantine*), bound to `Cmd+Z` / `Shift+Cmd+Z` | Reversible correction as the safety mechanism, so people can act with confidence | Undo offered as a substitute for confirming an action that cannot be reversed | Interaction pillar · Energy axis |
| **Vercel / Geist** | Dark-surface restraint: elevation carried by one mechanism (border or shadow), never both | Single-mechanism elevation; monochrome discipline | Purple-on-dark gradients and glass as decoration | Expression pillar · Materiality axis |

## Calibration Specimens

The table above names mechanisms to borrow from real products. This section is the
other half of the upper bound: **observable specimens** for judging a render on the
four craft pillars — typography, motion, composition, colour. A specimen is not a
rule (rules live in `craft-floor.md`); it is a three-tier reading of one concrete
UI situation, so a Critic or a taste judge has an anchor for "competent" versus
"excellent" rather than a bare preference.

Each entry is written as **object → competent tier → excellent tier → failing tier**.
Every characteristic is something a screenshot can be checked against: a measurable
value, a named alignment, a visible relationship. If a claim here cannot be seen in
a render, it does not belong in this section.

### Typography

- **Long-form reading page, 390px viewport.**
  *Competent*: body 16–18px, measure 45–75 characters, line-height 1.5+. *Excellent*:
  the heading size ladder tracks the content hierarchy (h1/h2/h3 differ by a
  consistent ratio, not ad-hoc sizes); CJK and Latin share a baseline and a line box
  when mixed; the paragraph-gap : line-height ratio stays constant across sections.
  *Failing*: measure 100+ characters, line-height 1.3, body 14px.
- **Dense data table, desktop.**
  *Competent*: numeric columns right-aligned, header row visually distinct, row
  height consistent. *Excellent*: digits are `tabular-nums` so columns align on the
  decimal; units are de-emphasised relative to the value; the header stays visible
  when the body scrolls. *Failing*: proportional digits in a numeric column, ragged
  decimal alignment, header scrolls away from its data.
- **A heading above body copy.**
  *Competent*: heading larger and heavier than body. *Excellent*: heading weight and
  size express a deliberate type-scale step (not a default `h2`); the gap above the
  heading exceeds the gap below it, binding it to its own content. *Failing*: equal
  space above and below the heading (it floats between two sections).

### Motion

- **A destructive commit (delete, send, publish).**
  *Competent*: the control responds to press with a visible `:active` state.
  *Excellent*: the press detent is paired with a settling animation at the commit
  (a state change the eye can follow), and the result is legible in under ~250ms so
  the action feels finished, not pending. *Failing*: no press feedback, or a
  multi-second entrance animation that delays the settled state.
- **A state transition (panel open, list filter, tab change).**
  *Competent*: the change is animated rather than instantaneous. *Excellent*: the
  transition's easing matches the direction (ease-out on entry), related elements
  move on one timeline, and it honours `prefers-reduced-motion` by resolving to the
  end state. *Failing*: an abrupt jump-cut, or a bounce easing on a utilitarian
  transition.
- **A loading or generating state.**
  *Competent*: a spinner or skeleton occupies the space the content will fill.
  *Excellent*: the skeleton matches the real content's shape and rhythm; streaming
  text shows a live boundary; elapsed time is shown instead of a fabricated
  percentage. *Failing*: a centred spinner over a blank page, or a progress bar with
  no knowable completion.

### Composition

- **A primary action surface (390px, one-handed).**
  *Competent*: the primary action is reachable and distinct from secondary actions.
  *Excellent*: the primary commit sits in the thumb zone, secondary actions are
  visually subordinated, and the layout is composed for the narrow frame rather than
  a compressed desktop. *Failing*: the commit control in the top corner, or a
  desktop two-column layout scaled down.
- **A list of comparable objects.**
  *Competent*: items are visually consistent and scannable. *Excellent*: the
  container is chosen for the objects (rows for records, not cards for everything);
  density is calibrated to the scan task; the selected/active item is marked by a
  cue that is not a container stripe. *Failing*: every object in an identical
  icon-heading-text card, nesting cards inside cards to express grouping.
- **The first viewport.**
  *Competent*: it shows the product's primary object. *Excellent*: it states a
  thesis — one committed idea a viewer could guess the category from — with a clear
  focal relationship, not a neutral frame of equal-weight blocks. *Failing*: a
  hero-metric template with no real context, or equal-weight tiles that commit to
  nothing.

### Colour

- **A semantic status system.**
  *Competent*: success / warning / danger are visually distinct. *Excellent*: the
  hues are chosen for the use scene (not stock red-amber-green), each holds WCAG
  contrast on its surface, and the status carries a second channel (icon, label) so
  colour is not the only signal. *Failing*: status conveyed by hue alone, or a
  palette whose warning and danger are indistinguishable.
- **An accent's restraint.**
  *Competent*: one accent, used consistently. *Excellent*: the accent marks exactly
  one thing per view (the primary action, or the live state), the surface hierarchy
  carries structure without it, and the palette reads as one system in light and
  dark. *Failing*: the accent on every interactive element, or a gradient accent
  used as decoration.
- **Light/dark as a use-scene decision.**
  *Competent*: the theme is applied consistently. *Excellent*: light or dark is
  chosen from the scene the product is used in (a night-shift console is dark for a
  reason), elevation is carried by one mechanism (border or shadow, not both), and
  the neutral temperature is authored rather than pure grey. *Failing*: dark mode
  chosen because the category "looks technical", or elevation faked with both a
  border and a shadow.

## When a benchmark is load-bearing, bind it to evidence

If a direction's rationale rests on a benchmark mechanism, do not leave it as a
citation. Capture the real product at the state you are citing and record the URL
and capture date beside the direction in `prototype/discussion.md`:

```text
prototype/experiments/<slice_id>/refs/<name>-<state>.png
```

Captures are **local run artifacts, never committed** to this skill: the images are
third-party property, and a stale committed screenshot is a worse anchor than a live
URL. The reference set stays links and mechanisms; the evidence lives with the run
that used it.

## How this is used

- **Stage 2, step 4 of the Divergence Generator**: when a domain-sourced candidate
  is fused with a catalog technique, calibrate the fusion against the matching entry
  here — name which mechanism you are borrowing and which you are refusing.
- **Stage 4**: a direction whose rationale cited a benchmark mechanism is reviewed
  against that mechanism on the render, not against the benchmark's surface.
- A benchmark entry that no longer reflects the real product is a defect in this
  file: fix the mechanism description or drop the entry. A stale anchor is worse
  than none, because it is confidently wrong.

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

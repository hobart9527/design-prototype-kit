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
what to refuse, and the Pillar / Axis it calibrates.

| Reference | The observable mechanism | Adopt | Refuse | Calibrates |
|---|---|---|---|---|
| **Linear** | Command palette: single-key dispatch, focus never leaves the list, status advances without a page change | Keyboard sovereignty; state advances in place | Low-friction dismissal of serious commits; treating speed as an excuse for no confirmation on destructive acts | Interaction pillar · Energy axis |
| **Bloomberg Terminal** | Multi-pane concurrency: many instruments visible at once, each with its own density and its own update cadence | High-density throughput; concurrent panes | Uncurated visual noise — density is curated here, not merely present | Attention pillar · Density axis |
| **Stripe** | Progressive disclosure in forms: the next field appears only when the previous one makes it relevant | Trustworthy typographic hierarchy; disclosure paced to need | Generic bloated card padding used to fake spaciousness | Object pillar · Rhythm axis |
| **GitHub PR** | Diff collation: change, discussion and approval lineage on one surface, in one reading order | Explicit approval lineage; diff as the primary object | Raw engineering jargon leaking into user-facing copy | Journey pillar · Materiality axis |
| **Gov.uk** | One question per page; the answer's consequence stated before the control | Task-pattern clarity; prerequisites before backtracking | Treating a wizard as the universal answer to a long task | Value pillar · Character axis |
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

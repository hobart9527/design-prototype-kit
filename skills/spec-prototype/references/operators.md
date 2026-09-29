# Refine Operators (调校算子)

Read when a direction is locked and the work is *refinement* rather than
exploration: the user says "make it bolder", "tighten it up", "this feels
generic", or asks for a variant, or wants the surface hardened against stress.

An operator is not a new vocabulary. It is a **named single move expressed in the
spine's own language**: it declares which of the Five Axes or which of the Nine
Pillars it moves, what it moves them from and to, and what it must not disturb.
That is the whole reason operators live here rather than in a house style guide —
`bolder` is not a mood, it is a move on Energy.

## The contract every operator carries

State these four things, briefly, before making the change. They are what turns a
vibe request into a reviewable delta:

| Field | What it records |
|---|---|
| **Target** | The axis or pillar the move acts on — exactly one operator's target set, never "overall polish" |
| **From → To** | The current value and the intended value, in the spine's terms (Energy: settled → kinetic) |
| **Held constant** | The axes and pillars the move must leave untouched; this is what makes the result attributable |
| **Falsifier** | The observable that would show the move failed, so the change can be reverted rather than defended |

A move that cannot name its target is not a refinement; it is a redirection, and
it belongs in the divergence generator
([`dialectic/01-metaphor-benchmark.md`](dialectic/01-metaphor-benchmark.md))
instead. A move that changes three axes at once produces an unattributable result:
the comparison teaches nothing and the next decision starts from zero.

### From a symptom to an axis (diagnose before you prescribe)

"Something feels off" is not a target. Read the symptom, name the axis or pillar
it actually lives on, then pick the operator whose Target matches — do not reach
for the operator whose *name* sounds closest to the complaint:

| The symptom you can actually observe | The axis or pillar it lives on | Operator |
|---|---|---|
| Everything competes for the eye; nothing leads | Attention / Emphasis | `distill` |
| Correct but inert — it does not respond to the hand | Energy | `animate`, or `bolder` on the press/commit moment only |
| Cramped, or so airy the task loses its thread | Density | `layout` |
| Type is doing no work: flat scale, one weight, loose measure | Character / Type | `typeset` |
| Colour is decorative rather than informational | Materiality | `colorize` (or `quieter` when it is over-coloured) |
| Loses its footing under long content, empty data or a narrow viewport | Resilience pillar | `harden` |
| You cannot say what it is for after five seconds | Value / Journey pillar | **not an operator** — this is a redirection |

The last row is the boundary. A symptom that resolves to a *pillar* rather than an
axis is a structural failure, not a refinement, and it goes back to the divergence
generator or the Stage 1 proposition. Refining a surface whose job is unclear only
makes the wrong thing smoother.

**The craft floor is not an axis and never trades against one.** Every operator is
bound by [`02-craft-methods/craft-floor.md`](02-craft-methods/craft-floor.md). A
move that wins on looks while failing a hard floor is a bug with a nice surface.

## The refine operators

Each entry names its target and the direction it moves. The *techniques* are
candidate means, not the move itself — pick the one the surface's own tokens
support.

| Operator | Target | Moves toward | Candidate techniques | Held constant |
|---|---|---|---|---|
| **`bolder`** | Energy | settled → kinetic | heavier weight, larger scale step, sharper contrast step, firmer spring | Density, Topology, Journey |
| **`quieter`** | Energy | kinetic → settled | reduced motion amplitude, longer easing, softer contrast step, more air | Density, Topology, Journey |
| **`distill`** | Density | dense → sparse | remove a disclosure level, merge two controls, drop a decorative layer, widen the measure | Energy, Character |
| **`typeset`** | Character, Rhythm | generic → specific | type scale ratio, optical size and tracking, measure and leading, a real face over a system stack | Density, Materiality |
| **`colorize`** | Materiality, Energy | flat → committed | colour strategy (restrained / committed / full / drenched), a saturation step, a tinted neutral ramp | Density, Topology |
| **`animate`** | Rhythm | static → flowing | entrance order, easing family, a transition where a cut is now, a settled state that resolves | Density, Character |
| **`layout`** | Topology | stacked → related | the OOUX cardinality map (`1:1` canvas / `1:N` master-detail / `N:M` board), reading order, region proportion | Energy, Materiality |
| **`harden`** | Resilience | nominal → stressed | the Break Protocol vectors, `min-width: 0` containment, an authored empty state, an in-place error with retry | Energy, Character |
| **`clarify`** | Value, Journey | implied → stated | the action verb lifecycle, the critical-path affordance, the consequence stated before the commit | Density, Materiality |

Two rules that keep the table honest:

- **One operator per pass.** Applying `bolder` and `distill` together means neither
  can be evaluated. If a request genuinely needs both, make two passes and record
  two deltas.
- **The held-constant column is a claim, not a promise.** After the move, check that
  the held axes did not drift — a `distill` that quietly changed the Energy register
  is a mis-scoped move, and the fix is to re-scope it, not to accept the drift.

## `variant` — one axis, compared

A variant is an operator applied to produce a *comparable* alternative: vary
exactly one primary axis and let the secondary choices follow from it. The
axis-to-pillar mapping is fixed so two variants are always attributable to one
difference:

| Variant axis | Spine target | The question the comparison answers |
|---|---|---|
| Structure | Topology | Does the task want a different arrangement of the same content? |
| Density | Density | Is the information load right for this mode? |
| Emphasis | Attention | Is the first-glance hierarchy the one the product needs? |
| Type | Expression (Character, Rhythm) | Is the typographic register right for this world? |
| Voice | Expression (Value, Journey) | Is the surface speaking in the product's own words? |

Variants share the craft floor and the token set. A variant that differs on two
axes is a direction, not a variant — send it to the divergence generator, where
the two-axis verdict can judge it.

## `break` — Resilience, on purpose

`break` is the `harden` operator run deliberately past the nominal case, using the
Break Protocol's four vectors as its checklist (owned by
[`02-craft-methods/resilience-trust.md`](02-craft-methods/resilience-trust.md)):
unbreakable string, zero-item empty state, 320px fold, rapid double activation.

Two constraints:

- **Stress vectors are parasitic on authentic domain entities.** Never render
  `unbreakable-entity-hash-0000...` into a prominent surface to pass a test; use a
  real 45-character headline, a real compound identifier, a real 60-character path.
- **`break` is a review, not a licence to keep the damage.** Its output is either a
  fix at the owning layer or an honest `PARTIAL` recording what still breaks. A
  surface left broken because "the stress test is documented" is not hardened.

## Recording an operator pass

Operators are refinements, so they do not reopen the Direction Contract. Record the
delta in `prototype/discussion.md` — operator, target, from → to, and the falsifier —
and keep the Contract's blocks unchanged. If a move turns out to need a contract
block changed, it was a redirection: stop, and take it through C2.

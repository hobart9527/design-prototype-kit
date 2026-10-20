# Dialectic Slice: Metaphor & Benchmark (Topic)

> Dynamic projection module for Physical Reality Mapping & Modern Benchmark Calibration.
> A selectable Stage 1 method topic: load it when Metaphor & Character is the
> active uncertainty, in any order alongside the other topics.

## 1. Domain Fact Mining (Agent Fact-Finding)
- The Agent MUST inspect existing workspace sources (the brief, `prototype/discussion.md`, PRDs, code models) before speaking.
- Extract: Focal Object, Primary Operator, Decisive Consequence, and Core Operational Tension.
- NEVER ask the user for facts knowable from repository inspection.
- **Capability Fabrication Firewall (能力防脑补防火墙)**: Surfaces and entities may
  only reference communication channels, integrations, or personnel roles the
  brief actually declares. A glance/sentinel surface renders the state the
  operator already owns — it never invents telephony, SMS, paging, email, or
  third-party notification hooks the brief never mentioned. An unmentioned
  channel is not a design gap to fill; it is a scope boundary to record under
  Ruthless Omissions.

## 2. Physical Metaphor Projection (9-Pillar: Mental Model & Resistance)

**Mandatory pre-step — Physical Reality Anchor (物理现实锚点强制前置)**:
Before generating any interface logic, name the actual physical object, space, or
procedure that practitioners in this domain use in the real world. This is not
a design metaphor chosen for communication elegance; it is a factual anchor that
constrains spatial logic, feedback velocity, and the mental model the interface
must honour. The interface derives from the anchor's physics; the anchor does not
decorate the interface.

- Name the anchor with specificity: not "a cockpit" but "a short-haul commercial
  flight deck: two operator positions, instrument clusters in sightline sectors,
  commit controls requiring two-hand engagement."
- State what the anchor physically does (its mechanism), what certainty or speed
  it buys the operator, and the transfer boundary — what must NOT carry over.
- If no authentic physical anchor exists or fits, declare this explicitly:
  `physical_anchor: none — pure digital native product` and derive spatial
  logic directly from the object model and journey topology instead.

A declaration is required — the anchor, or an explicit `none` with a reason. It is
scored for nothing: an anchor that is small or absent passes, and the mechanism it
supplies is what later stages check the artifact against. The **metaphor** built on
the anchor is optional; a proposition with no metaphor is not a defect.

Generate 2–3 **structurally distinct** real-world mechanisms from the domain's own
work — the room, tool, or procedure an expert would recognize — and derive the
interface logic from the mechanism, not from a house list. Do not reuse a
mechanism that does not fit this product's physics; a metaphor sourced from
approval, stamping, signing, or authorization is one option among many, never the
default, and it must be justified by the domain rather than by habit. Open the
three candidates on different axes (e.g. how work is paced, how state is
inspected, how risk is contained) so the choice is a real trade-off.

Illustrative families — pick, mutate, or replace per domain:
- **Tolerance and interlock** (a caliper, a jig, a physical key): incomplete
  conditions block actuation; the mental model is verifiable criteria and an
  unambiguous commit.
- **Throughput and triage** (a sorting floor, a switchyard, a triage desk):
  routine volume flows at speed while exceptions divert to a slower, deliberate
  lane.
- **Drafting and review** (a proofing table, a lightboard, a surveyor's plan):
  concurrent annotation, competing marks, convergence on one agreed artifact.
- **Instrumentation and monitoring** (a cockpit, a mixing desk, a control room):
  continuous signals, thresholds, and one panel where the operator's attention
  is deliberately routed.
- **Containment and recovery** (a quarantine bay, a circuit breaker, an airlock):
  the risky object is isolated, the blast radius is bounded, and the return path
  is explicit.

Each candidate must state its *physicality* (what the mechanism physically does)
and its *mental model* (what certainty or speed it buys the operator), plus the
transfer boundary — what the metaphor must not be read to mean.

## 3. Modern Digital Benchmark Calibration (5-Axis: Character)

Pair each physical metaphor with an authentic digital benchmark. The reference set —
which products, the specific observable mechanism each is cited for, and what to
refuse — is owned by [`../05-benchmarks/reference-set.md`](../05-benchmarks/reference-set.md);
read it here rather than recalling a product name from memory. A benchmark cited
without its mechanism is a name-drop, and the mechanism is the only part you can
check your own build against.

## 4. Divergence Generator (Double Diamond: Develop)

**Owner: Double Diamond / Develop.** The divergence source is the domain's own
lifeworld — never the style catalog. A direction pair drawn from a five-item style
list is not a divergence; it is two draws from one distribution, and the two draws a
model reliably makes are the same two every time (dense instrument, then Swiss grid).
`modern-style-vocabulary.md` is a **challenger source**, not the generator: it enters
at step 4 to mutate a domain-sourced candidate, never at step 2 to supply one.

Run the six steps in order. Steps 1–3 happen before any HTML is written; step 5 is
the only gate, and it is checked on the two directions side by side.

1. **Name the rut.** State in one sentence what this category's default surface
   looks like — the thing every product in this space already is. This is the
   attractor the directions must move away from. Naming it is what makes the move
   deliberate; an unnamed rut is the one you fall back into. Immediately record
   `rut_rejected:` with at least three named defaults and why each is refused;
   Stage 4 uses these as falsifiers against the rendered artifact, not as another
   list of forbidden styles.
2. **Generate from the lifeworld.** Author 3 candidates, each sourced from a
   *cultural world the domain actually lives in* — the room, the publication, the
   instrument, the ritual, the record — not from an aesthetic adjective. Each
   candidate names its world, its organising principle (what determines what goes
   where), and its native reading order. At least one candidate must come from a
   world no other product in this category currently occupies. Three are generated
   so the choice is real; the number **built** is governed by the divergence rule
   in [`../core-kernel.md`](../core-kernel.md) §5 (at least two while the direction
   is open, one when evidence has locked it).
3. **Draw seeds — do not choose them.** The seed varies the *incidental* choices
   the design does not argue for — which face, which neutral temperature, which
   corner family. Two directions must not converge on the same incidental
   decisions by default, and a seed the designer picks is not a defence against
   that: asked for an integer, a model returns the same few every time, so the
   step collapses into a formality and the divergence is spent before the
   structure differs. Draw them from a real entropy source instead (optional; skip or print-only when the record cannot take the block):

   ```
   python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id> --archetype <instrument|editorial|canvas|mobile|ambient> --write
   ```

   The script draws one seed per candidate from the OS entropy pool, derives the
   incidental triple from it, and draws a challenger vocabulary without
   replacement — then records the whole draw as a `### Divergence seeds` table
   inside the slice's block, so the record carries the entropy that produced it.
   Re-running replaces the block rather than appending. The draw is the
   mechanism; the prose request was the thing that never worked.
4. **Fuse a challenger (optional, at most one per candidate).** Take the
   vocabulary step 3 drew from
   [`../02-craft-methods/modern-style-vocabulary.md`](../02-craft-methods/modern-style-vocabulary.md)
   — or refuse it, with the reason recorded — and fuse its *techniques* into the
   candidate without replacing the candidate's organising principle. A fusion that leaves the organising principle unchanged is
   a reskin and is recorded as such. The catalog is read for technique, never
   selected as an identity.

   Calibrate the fused candidate against the reference set
   ([`../05-benchmarks/reference-set.md`](../05-benchmarks/reference-set.md)): name
   the observable mechanism you are borrowing and the one you are refusing. A
   candidate justified by "like Linear" without naming Linear's mechanism has no
   evidence behind it and does not pass this step.
   **Creative levers (declare at least one per candidate).** A lifeworld source says
   *where* a direction comes from; a lever says *how hard it is pushed*. Name the lever
   used and the point at which it was pulled back:
   - **Push to the extreme, then retreat** — take the idea to its limit (all type, no
     imagery; one gesture does everything), then back off only as far as the task needs.
   - **Hard constraint** — one typeface, one hue plus neutrals, one gesture, one grid.
     A constraint that costs something is a position.
   - **Material truth** — let the surface behave like the physical thing it cites
     (paper that folds, a dial that detents) instead of decorating with it.
   - **Invert the rut** — take a `rut_rejected` default and do its opposite on purpose;
     keep it only if the task survives.
   - **Borrow across domains** — bring a mechanism from a distant field via
     [reference deconstruction](../01-foundations/design-language.md#reference-deconstruction).
   A candidate with no declared lever is a competent default, not a direction.

   **Trend-tension four questions.** A technique that was fresh two years ago is
   today's default, and a candidate built on one is a reskin of the current rut
   even when it is new to this product. Before a fused candidate is admitted,
   answer four questions about its borrowed technique — this is an explicit
   direction-decision step, not an afterthought:
   1. **Category saturation** — how many competitors in this category already use
      this visual technique? Name them or state that the count is unknown.
   2. **Freshness** — is it still surprising today, or has it become the new
      default? A technique everyone just adopted is a response to the market, not
      a position.
   3. **Brand continuity** — does it continue this product's existing signals
      (colour, structure, tone), or break from them? A break needs a THESIS that
      argues for it; continuity needs only fit.
   4. **Lifespan** — will it read as dated in 12–24 months? Name the signal that
      would date it (a specific finish, a signature animation, a typographic
      trope).
   The conclusions land in the Direction Contract's **THESIS** block as one line
   (e.g. `trend: low saturation / still fresh / continuity / durable`); the four
   answers are the evidence for that line, not a separate essay.

5. **Two-axis verdict — the gate.** Before building, compare each pair of
   candidates and name the **two or more axes** on which they differ. **Structure
   must be one of them**: the two candidates must not share an organising principle,
   because a pair that keeps the tree and moves only its colours, spacing or type is
   one direction counted twice, however it is dressed. The remaining axes are
   density, energy, materiality, rhythm, character and reading order. A pair
   differing on fewer than two axes, or on two axes without Structure, is a failed
   gate — merge it and generate a replacement. Palette alone is never an axis. Structure stays mandatory; additionally, at least one of the differing axes should be
   an expression axis (materiality, energy, character or rhythm), so the pair also differs in how it
   looks and moves, not only in how it is organised. This
   is the check the benchmark's divergence judge re-runs on the built slots (a
   benchmark-side judge, not a delivery command), whose verdict is `divergent` only
   when the tag sequence differs; a verdict that holds in prose but not on the artifact
   fails.
6. **Donate the loser.** A direction that loses selection still donates its best
   mechanism — a control, an ordering, a state treatment — to the winner, or the
   donation is explicitly recorded as refused with its reason. Directions are not
   discarded; the non-selected work is where the compound interest sits.

## 5. Settlement
Upon user selection, lock the primary metaphor (or its declared absence), core
tension, and Character profile. The non-transfer boundary is recorded with it.

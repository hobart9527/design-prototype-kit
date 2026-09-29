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

**This step is not optional and not bypassed by time pressure.** A chassis
or layout selected without a physical anchor or explicit `none` declaration
is a template default, not a design decision.

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
Pair each physical metaphor with authentic digital benchmarks — state what to adopt and what to refuse:
- *Linear*: Adopt keyboard sovereignty, rapid status advancement; REFUSE low-friction dismissiveness of serious commits.
- *Bloomberg Terminal*: Adopt high-density information throughput, multi-pane concurrency; REFUSE uncurated visual noise.
- *Stripe / Apple*: Adopt progressive disclosure, trustworthy typographic hierarchy; REFUSE generic bloated card padding.
- *GitHub PR*: Adopt diff collation, explicit approval lineage; REFUSE raw engineering jargon.

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
   deliberate; an unnamed rut is the one you fall back into.
2. **Generate from the lifeworld.** Author 3 candidates, each sourced from a
   *cultural world the domain actually lives in* — the room, the publication, the
   instrument, the ritual, the record — not from an aesthetic adjective. Each
   candidate names its world, its organising principle (what determines what goes
   where), and its native reading order. At least one candidate must come from a
   world no other product in this category currently occupies.
3. **Assign seeds.** Give each candidate a distinct seed integer, recorded with it.
   The seed varies the *incidental* choices the design does not argue for — which
   face, which neutral temperature, which corner family. Two directions must not
   converge on the same incidental decisions by default; without a declared seed
   they reliably do, and the divergence is spent before the structure differs.
4. **Fuse a challenger (optional, at most one per candidate).** Take one vocabulary
   from [`../02-craft-methods/modern-style-vocabulary.md`](../02-craft-methods/modern-style-vocabulary.md)
   and fuse its *techniques* into the candidate without replacing the candidate's
   organising principle. A fusion that leaves the organising principle unchanged is
   a reskin and is recorded as such. The catalog is read for technique, never
   selected as an identity.
5. **Two-axis verdict — the gate.** Before building, compare each pair of
   candidates and name the **two or more axes** on which they differ. **Structure
   must be one of them**: the two candidates must not share an organising principle,
   because a pair that keeps the tree and moves only its colours, spacing or type is
   one direction counted twice, however it is dressed. The remaining axes are
   density, energy, materiality, rhythm, character and reading order. A pair
   differing on fewer than two axes, or on two axes without Structure, is a failed
   gate — merge it and generate a replacement. Palette alone is never an axis. This
   is the check the benchmark's divergence judge re-runs on the built slots
   (`benchmarks/judges/divergence_judge.py`), whose verdict is `divergent` only when
   the tag sequence differs; a verdict that holds in prose but not on the artifact
   fails.
6. **Donate the loser.** A direction that loses selection still donates its best
   mechanism — a control, an ordering, a state treatment — to the winner, or the
   donation is explicitly recorded as refused with its reason. Directions are not
   discarded; the non-selected work is where the compound interest sits.

## 4. Settlement
Upon user selection, lock the primary metaphor (or its declared absence — a
physical metaphor is an optional anchor with an explicit transfer / non-transfer
boundary), core tension, and Character profile. This topic's settlement does not
gate any other topic.

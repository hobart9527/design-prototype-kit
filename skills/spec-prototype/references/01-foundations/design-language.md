# Integrated design language

Use this reference when the product needs a new or materially revised expression.
Design language is not a late visual coating: content voice, brand character,
hierarchy, typography, color, imagery, iconography, component character, feedback
and motion develop with the product model, topology and interaction. Each may be
quiet or absent when the product calls for restraint; absence is a decision, not
an automatic defect.

## Enter through the product, not a style label

Start from the Product Experience Model in [product grounding](product-understanding.md):
the product thesis, actors and jobs, objects and content, journeys and states,
Surface Topology, constraints and current evidence. Inspect existing identity,
tokens, components and category conventions. They are evidence and implementation
conditions, not automatic approval and not an obligation to redesign.

State the expressive opportunity as a product question: what should become easier
to notice, understand, trust, feel or do, for whom and in which scene? Name the
competing value or cost. Existing continuity, a familiar convention and a flat,
light, immediate or visually quiet treatment remain first-class possibilities.
Innovation earns its place through product value, not distance from convention.

## Atmospheric calibration and mature craft principles

A mature designer does not apply generic SaaS tropes (flat grey background, rounded
card shadows, uncalibrated blue accents) to every problem. Calibrate expression to
the authentic context of use:

1. **Environmental & Operational Reality**:
   - Trace the operator's actual working setting: lighting conditions (harsh sun, dim room, night shift), distraction levels (focal absorption vs fragmented interruptions), motor precision (fine cursor control vs gloved fingers or rough field work), and stress level (emergency crisis response vs reflective deliberation).
   - The visual atmosphere must directly solve the environmental challenges of that scene, not mimic an unrelated tech demo.

### Qualitative-adjective translation protocol

When used as a core Design DNA proposition, stylistic anchor, or foundational justification,
a qualitative adjective (e.g. restrained, precise, warm, premium, 克制, 高级感)
is never a design justification by itself — neither in a Foundation rationale nor
in a critic review. To stand as an architectural decision, expand it in the same statement into a triple:

```text
[perceived dimension] + [physical / parametric boundary] + [observable counter-example]
```

Examples of the shape (derive actual values from product evidence, never reuse
these as a lookup table): "restrained" → accent coverage ≤ 8% of surface,
overdamped motion (no bounce tail), counter-example: any glow or rainbow-gradient
floating element. "Precision instrument" → hairline 1px hierarchy rules, tabular
numerals for all live values, counter-example: decorative rounding or unaligned
numerals in an operational readout.

If a core proposition adjective cannot be expanded into this triple, remove it from the
rationale. (Routine descriptive grammar and ordinary prose do not require triple expansion;
this discipline governs the claims that anchor visual and interaction contracts.)
Run it in both directions: after expanding each adjective, check that the parameters
together still read as one position (see [The Style Language Card](#the-style-language-card)) rather
than a list of values that could belong to any product.
This protocol is generative-side discipline; the audit-side detector
lives in the quality bar, not here.

### Orthogonality: Reality Mapping source × Five Axes

Two independent decisions combine; never fuse them:

- **Reality Mapping source (魂之源)** — which physical, optical, biomorphic,
  temporal or force phenomenon supplies the mechanism (the five dimensions above).
- **Five Axes (魂之度)** — the energy and finish of the delivery, carried by the
  canonical axes Density · Energy · Materiality · Rhythm · Character (see the
  Axis DNA row below). A routine descriptive locality such as "quiet live venue"
  or "polished instrument" is ordinary prose and needs no expansion; a locality
  that anchors the visual or interaction contract expands through the
  qualitative-adjective translation protocol above.

The same acoustic-resonance source becomes a precision spectral instrument under
low-energy + high-materiality, or an underground live-venue wall under
high-energy + raw materiality. Never bind a physical metaphor to one axis value:
any mapping may be executed at any position the product's evidence earns. Every
axis value cites evidence from the product's context; an axis set by habit or
model default is an invalid derivation. An axis the product's evidence does not
yet settle is recorded `open` with its reason — that is a decision about
uncertainty, not a silent default, and it stays open rather than being filled
with a plausible-looking value. What is invalid is the axis that is neither
valued-with-evidence nor explicitly open.

2. **Typographic Punch & Rhythm**:
   - Typography is the voice of the product. Do not use monotonous 14px/16px ladders.
   - Establish purposeful contrast between expressive titles, crisp readable body, and
     scannable, high-contrast micro-labels.
   - Treat whitespace not as unused canvas, but as conscious pacing (tempo) between
     dense operational zones.

3. **Tactile Mechanics & Feedback Weight**:
   - Interfaces must feel physically grounded. Interactive elements should convey
     appropriate perceived mass, crisp state transitions, clear active feedback, and
     graceful loading/error recovery without theatrical over-animation.

## Develop a consequential Design Proposition

Every proposition that could change a direction records this causal chain:

1. **Product thesis and question** — the sourced product truth and unresolved
   experience question it addresses.
2. **Generative mechanism or lens** — the relationship used to create the design,
   not merely a style name. A lens may be physical, cultural, editorial, spatial,
   material, narrative, interaction-led or another relevant source.
3. **Same task-and-content specimen** — representative, schema-faithful content and
   a consequential task held constant across alternatives.
4. **Convention retained** — what remains familiar so users can transfer knowledge.
5. **Signature Relationship** — one cross-surface relationship between content,
   control, space, time or material that makes the proposition coherent and
   recognizable. It is not required to be decorative or novel.
6. **Benefit, cost and learning burden (Explicit Innovation Accounting)** — who gains
   what, what becomes harder, and what new mental model or gesture must be learned.
   Any deliberate departure from platform-native conventions must explicitly justify
   why its outcome outweighs the negative-transfer friction.
7. **Falsification and transfer test** — an observation that could disprove the
   proposition and a contrasting surface, task, state or viewport where it must
   still work.

The mechanism is generative, not a catalogue lookup. References and analogies
must name what transfers and what does not. Never translate a metaphor into an
unsupported object, diagnosis, permission or product capability.

### The Direction Contract is this chain, compressed

This section is the **sole owner of the six Direction Contract blocks** — their names,
what each compresses, and the two chain steps that deliberately have no block. Other
references name a block or link here; none restate the block list as a second definition.

When a direction is locked, publish it as a **Direction Contract** — the chain above
compressed to what a reader can *see* on a screen. Author it under a
`## Direction Contract` heading in the record's shared visual world — the
**Visual world** zone of `prototype/discussion.md`, or the same section in
`prototype/world.md` on the layered layout — in six labelled blocks.
The contract is a projection of the chain, not a second proposition: every block cites
the chain step it compresses, and no block may introduce a claim the chain does not carry.

| Contract block | Compresses | What it states |
|---|---|---|
| **THESIS** | 1 · product thesis | The one committed idea, in a sentence a reader could disagree with. |
| **OWN-WORLD** | 2 · generative lens | The world the surface lives in and its organising principle. |
| **STORY** | 3 · specimen | The task and content held constant, in the order the reader meets them. |
| **FIRST VIEWPORT** | 5 · Signature Relationship | What the first screen claims, before any scroll. |
| **FORM** | 4 · convention retained | What stays familiar so knowledge transfers, and the structure that carries it. |
| **FINISH** | craft floor | The material execution: surfaces, states, and the browser's own parts. |

Two chain steps deliberately have **no block**: *6 · benefit, cost and learning burden*
and *7 · falsification and transfer test*. They are accounting and a test, not something
a viewer sees, so they stay in the record beside the contract. Their absence from the
contract is not permission to skip them — a direction locked without its accounting and
its falsification test is not locked.

One further line is recorded beside the contract, also not a block: the
**Signature Moment** — the single interaction the product exists to prove, named so
one reader and a later reviewer mean the same screen when they say it. Write it as
`- Signature Moment: <the moment> — carries <Observed Mechanism from the Physical Anchor>`,
or `- Signature Moment: none — <why the task needs no distinctive moment>`. It is the
target Stage 4's Signature probe checks; without it that check has nothing to compare
against, and a `none` is an answer, not a gap.

The contract is checked against the built artifact, block by block. A block that is
declared here and absent in the render is a finding; a block that is absent here cannot
be scored as fulfilled.

### Summarize the proposition without replacing it

Use this three-part synopsis when it helps a human compare, approve or hand off a
consequential proposition:

1. **Qualitative Design DNA (Axis DNA)** — name the combination that gives the
   direction its character and the product basis for that combination. Choose
   only dimensions that explain this product—such as density, rhythm,
   materiality, emotional valence, spatiality or temporal behavior. This is not
   a fixed axis list, numeric score, page generator or CSS recipe.
2. **Real-World Mapping** — when a verified digital-software reference reduces
   uncertainty, record its source/evidence status, the locally observed
   mechanism, the translation into this product and the non-transfer boundary.
   Real-World Mapping is optional: an original proposition needs product
   causality and a falsifiable specimen, not a compulsory analogy.
3. **Signature Craft** — state how the Signature Relationship becomes perceptible
   in the representative scene through applicable content, hierarchy,
   typography, color, imagery/icons, component character, feedback and motion.

### First-Principles Reality Mapping (Deriving Form from the Physical and Natural World)

Do not force products into pre-packaged aesthetic archetypes or imitate generic AI dark-mode consoles. The physical, biological, and cognitive world is vast, nuanced, and domain-specific. A design direction derives its authentic character by mapping one or more real-world dimensions to the product's context and core tension:

1. **Authentic Domain Substrate**:
   Ground the interface in the actual working environment and tools of the practitioner. Examples: architectural drafting tables, geological core trays, typesetting cases, darkroom developer baths, escapement mechanisms, nautical chart tables, emergency triage boards, seismic trace drums, library archive folios, surgical theater instrument trays, textile weaving grids. Observe how authentic tools solve hierarchy, manipulation, and spatial sequencing. Explicitly state: Observed Mechanism → Digital Translation → Non-Transfer Boundary.

2. **Optics, Chromatics, and Light Physics**:
   Light is not merely cosmetic. Map chromatic phenomena authentically: spectral diffraction and dispersion, photon emission vs ink/pigment absorption, bioluminescent glow and dark adaptation, retinal fatigue compensation, glare suppression and scotopic contrast. Calibrate color scientifically to the user's authentic viewing conditions (outdoor glare, dim-room night work, high-ambient retail). Non-linear luminance curves and perceptually uniform color spaces (OKLCH, CIELAB) serve legibility where flat hex palettes fail.

3. **Biomorphic & Morphological Dynamics**:
   Natural form follows structural logic. Map biological metaphors as structural function: cellular membrane selective permeability → tiered information disclosure; mycelial network propagation → relational data expansion; capillary action → progressive data loading; stress-distribution branching → hierarchical visual weight. Never apply biological labels as mere decoration; every biomorphic metaphor must translate to a concrete structural behavior or visual rule.

4. **Temporal Dynamics, Rhythm, and Narrative Arc**:
   Time is a design material. Map temporal phenomena: tidal rhythm and harmonic cadence → information breathing and pacing; heartbeat waveform → anomaly pulse markers; musical beat structure → task completion choreography; dramatic arc (tension → crisis → release) → complex workflow emotional progression. Calibrate response timing to the user's operational tempo, not to animation trend libraries.

5. **Force, Friction, Energy, and Commit Mechanics**:
   Physical tools convey intent through force and resistance. Calibrate kinetic dynamics: where should interactions be frictionless and instantaneous? Where should viscous damping convey deliberateness and prevent reckless error? Where should elastic tension or magnetic snap communicate boundary alignment? Where is the irreversible commit threshold — the precise moment an action cannot be undone? These mechanics must be implemented, not described.

Apply whichever dimensions genuinely reduce uncertainty for this product. Multiple dimensions may combine; none is mandatory. Real-World Mapping is optional when no reference improves the design decision — record `not needed` rather than fabricating a precedent.

#### From an observed mechanism to a compiled token

When a dimension does become load-bearing, derive rather than borrow. The chain has
five steps and stops at the evidence:

1. **Mechanism** — what the anchor physically does (a detent holds until pressure
   passes a threshold; a lens bezel occludes at the rim).
2. **Observable property** — the sensorily checkable quantity it implies (travel,
   dwell, damping, occlusion order, spacing rhythm, contrast falloff).
3. **Token role** — which compiled token or authored custom property carries that
   quantity: an axis pair drives the generated set (`density` → spacing and radius,
   `energy` → duration and easing, `rhythm` → pacing scale, `materiality` → type and
   surface, `character` → typographic tone), while a quantity no axis covers is
   authored under `## Proposed` as a named custom property.
4. **Value from product evidence** — the number comes from the anchor, the domain's
   tempo, or a measured constraint; it is never a default lifted from a pattern
   library. A value written here without a cited source is a guess wearing a token.
5. **Falsifier** — the observation at Stage 4 that would show the translation failed:
   a commit that gives no perceptible travel, a rhythm the operator's cadence
   outruns, an occlusion that hides the value it was meant to frame.

Steps 1–3 are authored before the anchor is built; step 5 is checked after. Values
in this derivation are product-specific by construction — a worked example is a
shape to reason from, never a lookup number to copy.

### Aesthetic Courage and Anti-Banal Self-Questioning

Do not retreat into generic, risk-averse safe designs that lack character. Before freezing an expressive direction, challenge the composition with four critical self-inquiries:
- **Default Check**: Did this direction choose its palette, typography, and density because of the product thesis, or simply because it is the standard safe template of popular component libraries?
- **Signature Stance**: If all brand logos and product titles were removed, does this surface still possess an unmistakable visual voice and interaction rhythm that distinguishes it from competitor tools?
- **Restraint vs Emptiness**: Is the negative space an active compositional pause (tempo) that frames critical data, or an unintended vacuum resulting from missing context?
- **Expressive Tension**: Where does the design take its deliberate creative risk (e.g. bold scale jumps, non-standard layout grid, tactile borders)? A design with zero aesthetic courage is a mediocre tool.

### Real-Content Adaptation and Visual Editing Stress Tests

A robust design proposition must be verified against authentic, messy, and extreme content scenarios:
- **String Length Extremes**: Test localized strings, lengthy user names, and deep file paths. Verify deliberate truncation rules (`text-overflow: ellipsis` with full-text tooltips, or balanced multi-line wrapping).
- **Tabular and Numeric Stress**: Monospaced tabular numerals (`font-variant-numeric: tabular-nums`) should be used for dynamic counters to prevent layout jitter during updates.
- **Dynamic Scale Calibration**: Charts and sparklines calibrate their baselines to data domain needs (zero-anchoring for ratios, dynamic bounds for high-variance monitoring) to prevent flatline clipping while clearly displaying scale context.
- **Kinetic Physics and Visual Detents**: When scrubbers or timeline replays map to physical event milestones, provide tactile visual resistance or snapping detents. Ensure snapping logic permits keyboard step navigation without value pinning (WCAG 2.1.2).

## Craft references are evidence, not presets

Use the product's task, content, platform, brand evidence and authored proposition to
choose color, type, density, layout, imagery, components, feedback and motion. Do not
select a treatment from a product-category palette or baseline. The examples elsewhere
in this reference are possibilities to investigate, not defaults to copy; their values,
font names and CSS snippets are not a token recipe. When a focused craft question
remains, consult the relevant method reference and compare treatments on the same
representative task and content. Keep any chosen values traceable to the product brief,
existing design system, platform requirement or observed evidence.

The synopsis compresses the full causal proposition; it neither replaces the
seven fields above nor creates another approval object or design workflow.
Signature Relationship names the invariant that must remain recognizable.
Signature Craft names its concrete expression and may adapt or quieten by
surface, state, viewport and operational context.

Run these ideas as a small loop inside the Product Experience Model:

```text
product evidence and active question
  -> Qualitative Design DNA
  -> Real-World Mapping when it reduces uncertainty
  -> Signature Relationship
  -> Signature Craft on the same task/content specimen
  -> cross-surface transfer and falsification
  -> retain in Foundation or reopen the owning upstream decision
```

Use the loop for a new or reopened consequential direction. A local repair with
a valid inherited proposition should preserve its DNA, relationship and mapping
boundaries while changing only the responsible craft. If the specimen disproves
the product model, journey or topology, return there; do not create a parallel
visual-design track.

## Let exploration depth follow uncertainty

Use one proposition when evidence and constraints already determine the direction.
Use enough genuinely different propositions to resolve a material choice—usually
two, occasionally more. Do not manufacture a quota, and do not present cosmetic
reskins as different product ideas. When the uncertainty concerns only color,
type, density or motion, hold task, content and structure constant and run a
focused expression study.

The strongest familiar solution belongs in the comparison when competitive.
Alternatives should differ in a consequential experience relationship, not in
fashionable ingredients. Keep the semantic constraints, representative content,
task, viewport and review question constant so the trade-off remains legible.

**Direction diversity requirement**: when presenting multiple exploration
directions, classify each along structure, density, emphasis, type voice and
chromatic temperature. The pass/fail threshold is **not** stated here: the
divergence gate owns it
([`../dialectic/01-metaphor-benchmark.md`](../dialectic/01-metaphor-benchmark.md),
step 5 — two axes minimum, Structure mandatory), and this section must not carry
a second number that drifts from it. Three close cousins of one solution (e.g.
differing only in lightness) is an invalid set — the exploration has not happened
yet. Diversity yields only where the product evidence genuinely locks a register
region; inside a locked region, directions differentiate on the other dimensions.

## Compose the language as one product experience

Develop the proposition in representative scenes before extracting tokens:

- Establish content voice and terminology together with labels, explanations,
  failure messages and return moments.
- Compose reading order, density, scale, spacing and disclosure around the user's
  current decision, including realistic long and multilingual content.
- Develop typography, color, imagery, icons and material as relationships across
  the whole frame, not independent swatches or ingredient lists.
- Give components a character appropriate to frequency, consequence, platform and
  input method. Flat and layered surfaces, sharp and soft geometry, immediate and
  expressive feedback are all eligible.
- Use feedback and motion only when they clarify response, continuity, causality,
  spatial change or an approved expressive purpose. Preserve an effective still
  or reduced-motion experience.
- Carry the Signature Relationship into a second, contrasting surface or state.
  If it works only in a hero frame, it is decoration rather than a system.

Use [visual craft](../02-craft-methods/visual-craft.md), [content and form](../02-craft-methods/form-ergonomics.md),
[interaction craft](../02-craft-methods/interaction-power.md) and [trust and critique](../02-craft-methods/resilience-trust.md)
according to the uncertainty. Their techniques are options to test, never a
universal house style.

## The Style Language Card

Answers one question: *"What is this product's visual and interaction language,
stated as a position someone could disagree with?"* Five Axes place a design on
continuous coordinates; the Direction Contract says what the first screen claims.
Neither says why this is a *language* rather than a pile of values. The card does,
in one section of `world.md` — no new file, no new authority.

Read it when a direction is being locked (Stage 1), revised by an expression study
(Stage 2), or judged against the render (Stage 4). Skip it for a local repair that
inherits an existing language.

### The card

Author it under `## Style Language` in `prototype/world.md` (or `discussion.md` on a
single-record tree). Draft it when the recommended direction forms; it stays
`proposed`/`provisional` under the same status rules as every other row until the user
selects the direction.

1. **Positions (3–5)** — each written `We choose X over Y, because <product reason>`.
   Both sides must be defensible. If nobody would choose Y, it is not a position.
   *Weak:* "clean over cluttered". *Strong:* "dense, ruled tables over card grids,
   because operators compare rows across 40 items".
2. **Vocabulary** — the concrete, repeatable parts the language is built from, named so
   the build and the critique can point at them:
   - **Type**: roles and what each is for (display, reading, data, label), not a family list.
   - **Colour**: what colour *means* here (state, ownership, emphasis) and where it may
     never appear. Hex values live only in `contract:tokens`.
   - **Form**: radius family, line weight, edge treatment, spacing cadence.
   - **Motion**: what moves, what never moves, and what a transition communicates.
   - **Voice**: how labels, empty states and errors speak.
3. **Counter-examples (≥2)** — things that would be *correct* by the craft floor and
   still wrong for this language, each with a one-line reason. These are the language's
   own falsifiers; Stage 4 checks the render against them. They are distinct from the
   divergence record's `rut_rejected` (the category defaults the direction refuses,
   owned by [`../dialectic/01-metaphor-benchmark.md`](../dialectic/01-metaphor-benchmark.md)
   §4): `rut_rejected` governs where the direction came from, counter-examples govern
   what the language itself would still reject.
4. **Signature** — one sentence naming the relationship that makes the product
   recognisable with the logo covered (it is the Signature Relationship from
   [`design-language.md`](design-language.md), stated as visible behaviour).

### Relationship to existing owners

| Concept | Owner | Card's role |
|---|---|---|
| Five Axes values | `contract:axes` in `world.md` | The card explains the choices; it never restates values. |
| Hex / size / duration | `contract:tokens` (sole token authority) | Vocabulary names *roles*; tokens carry numbers. |
| Six Direction Contract blocks | [`design-language.md`](design-language.md) | The card is the language behind FORM/FINISH, not a seventh block. |
| Adjective translation | [`design-language.md`](design-language.md#qualitative-adjective-translation-protocol) | Run it both ways: each adjective becomes a parameter, and the parameters together must still read as one position. |

### Testing the language

- **Cover test**: hide the logo and copy. Category recognition itself is neutral;
  the test is whether the design merely falls into generic category ruts (high
  homogeneity in the forms rejected under `rut_rejected`) or commits to intentional,
  opinionated relationships that express its Positions without relying on logo or copy.
- **Transfer test**: apply the Positions to a second surface the card did not mention.
  If a Position cannot decide a layout question there, it is a mood, not a position.
- **Cost test**: every Position names what it makes harder. A position with no cost is
  a preference.

A card that fails a test is revised or marked `open` with the reason. It is never
padded with adjectives to look complete.

## Reference deconstruction

Answers one question: *"What does this reference actually do, which part transfers
here, and which part must be refused?"* A brand name is not a reference; a named
mechanism is. [research.md](research.md) owns the evidence record and source hygiene;
this section owns the method and where the result lands.

### Sources worth taking from

Take at least one reference from outside the product's own category. Same-category
references explain the rut; cross-domain ones are where a language comes from.

- Editorial and print (grids, running heads, captions, tables)
- Instruments, cockpits, drafting and lab equipment
- Architecture and wayfinding
- Film, title design and motion graphics
- Typography specimens and signage
- Adjacent products that solve the same *task* in a different medium

### Three steps

1. **Take apart.** Name what the reference does along the five levels below. Observe;
   do not interpret yet. Use a real source (URL or local path, accessed date) and the
   evidence tags from [`core-kernel.md`](../core-kernel.md) §4.
   - **Structure**: what organises what, and the reading order.
   - **Type**: roles, scale relationships, case, numerals.
   - **Colour**: how many hues, what each means, how neutrals are tempered.
   - **Rhythm / Motion**: repetition, pauses, what transitions explain.
   - **Material**: surface, edge, depth, texture.
2. **Extract the relationship.** Reduce the observation to one relationship that makes
   it work (e.g. "the table is the page: every other element is subordinate to its
   ruled rows"). Record the condition under which it holds. If the relationship cannot
   be stated without the reference's name, step 1 was description, not extraction.
3. **Translate or refuse.** State what transfers to this product's content and task,
   what is refused and why, and what must change in the translation. Put the adapted
   proposal beside its source when visual comparison is available. A translation that
   only borrows the surface (colour, font) is recorded as a reskin.

### Where it lands

The `Reference Benchmarks` of the Problem Framing block — `truth.md` on a layered
tree, `discussion.md` on a single-record one — carry what transfers and what is
refused. The Positions of the
[Style Language Card](#the-style-language-card) carry the resulting choice.
Source limits and access dates stay in `prototype/research.md` per
[`research.md`](research.md); the benchmarks link there rather than duplicating it.

### Boundaries

- A reference supplies a mechanism, never a capability, user claim or metric.
- Popularity is familiarity, not fitness.
- Never invent a reference or imply a source was read when it was not.

## Probe the question at the smallest useful fidelity

A probe exists to answer a design question. Choose its fidelity and breadth from
that question:

- A static composition can answer hierarchy, tone or visual-language questions.
- A playable transition can answer feedback, continuity or learnability questions.
- A Walking Skeleton across the necessary connected surfaces can answer journey,
  shared-object or service-continuity questions.

Do not force a multi-page prototype for a first-frame question, or use a static
mockup to claim interaction quality. Surfaces come from the retained Surface
Topology; an early probe may use a clearly provisional frame without freezing
page count or navigation.

Compare propositions on the same specimen and actual-size viewport. Inspect the
rendered composition before reading its rationale. Record which claims are facts,
expert judgments, preferences, hypotheses or observed results. Visual evidence
does not prove behavior; a behavioral trace does not prove visual craft.

## Direction probe record

For an authorized comparison, retain one probe brief per proposition: the product
question, full Design Proposition fields, identical task/content specimen and
viewport, repository and installed Skill roots, bounded experiment/evidence
paths, available assets and required evidence. Keep the probe envelope defined by
[handoff](../04-governance/execution-boundary.md) beside it as the scope record.
Mark uninspected capabilities unknown and fixtures synthetic. A direction probe
does not require a frozen Foundation, Contract or Specification and creates no
approval.

Author the probe directly inside the declared scopes, then review the actual result
against [the quality bar](../03-verification/quality-floor.md). A weak proposition or wrong topology
returns to the design owner. A missing renderer leaves visible claims unverified
rather than inviting a text-only quality claim.

## Converge without freezing learning

Recommend the proposition with the strongest product fit and evidence. Preserve
its best relationship while repairing the owning cause of a weakness—product
understanding, object/content model, topology, interaction, expression or
execution. Combining propositions is a new proposition and needs a coherent
rationale and renewed evidence.

After actual approval, retain the chosen rationale, content voice, semantic
visual roles, component and feedback character, scoped Signature Relationship,
adaptation rules and Verifiable Design Assertions in the existing Foundation and
token artifacts. Record where familiar conventions remain and where the language
intentionally changes them. Mark untested applications explicitly.

Later journey, state, accessibility or transfer evidence may reopen only the
affected assumption through a successor revision. Approval fixes authority; it
does not make a design hypothesis immune to evidence.

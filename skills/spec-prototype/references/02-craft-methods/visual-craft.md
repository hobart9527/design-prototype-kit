# Craft reference — Visual language and atmosphere

> **Pillars**: `Expression` · `Attention` · `Value`  
> **Core Invariants**: Five Axes Calibration · Declared-Attribute Optics · Optical Concentric Geometry · Non-Generic Materiality

Owns the perceptible language: material and metaphor, semantic tokens, typography, composition,
imagery, entry composition and iconography. **Open lens:** which competing atmosphere, hierarchy
or symbolic relationship could make this product's value perceptible? **Floor:** the retained
Foundation, tokens and actual-content specimen must travel coherently across contrasting tasks.

## Materiality Calibration: Anti-Default Palette Invariant (材质拟合与色彩反惰性)

Never collapse all interfaces into dark-mode industrial grays. Palette, typography, and materiality MUST calibrate directly against the domain's reality anchors:

| Domain Archetype | Material Substrate & Subservience | Primary Chromatic Calibration | Typographic Rhythm | Negative Pattern to Avoid |
|---|---|---|---|---|
| **Editorial & Long-form Reading** | Warm paper / vellum texture (`#faf8f3`, `#f5efe6`) | Monochromatic charcoal / ink, understated vermilion or lapis accents | Classical serif headings, generous line-height (`1.8~1.85`), measure $\le 68\text{ch}$ | Pitch black OLED backgrounds, cold cyber cyan, neon alerts |
| **Engineering & SRE Workbench** | Dense cold titanium / dark graphite (`#0a0c10`, `#0f141c`) | High-contrast amber, phosphor green, or titanium status markers | Monospace digits (`tabular-nums`), mechanical 1px hairline borders | Soft pastel washes, decorative drop shadows, non-tabular digits |
| **Internal Procurement & Audit** | Clean neutral daylight office ground (`#ffffff`, `#f8fafc`) | Trustworthy slate, navy, restrained semantic green/red for approval | Crisp sans-serif, dense form field alignment, clear visual anchors | High-contrast gaming dark mode, gratuitous gradient cards |

Load the named section for the open question; do not read the whole pillar for a single decision.
Values decided here are returned to the Foundation and token revision, not restated per page.

Sections in this pillar:
- [From insight to authored expression](#from-insight-to-authored-expression) - from product insight to an authored expressive mechanism
- [Develop typography, space and color together](#develop-typography-space-and-color-together) - develop type, space and color together as tokens
- [Typography as voice and reading structure](#typography-as-voice-and-reading-structure) - voice, reading structure and mobile reading systems
- [Compose attention, relationships and rhythm](#compose-attention-relationships-and-rhythm) - attention, relationships and rhythm
- [Art direction for images and illustration](#art-direction-for-images-and-illustration) - art direction for images and illustration
- [Entry composition and meaningful imagery](#entry-composition-and-meaningful-imagery) - entry composition and meaningful imagery
- [Iconography that explains actions](#iconography-that-explains-actions) - iconography that explains actions

## From insight to authored expression

### Specialized Double Diamond workflow

**Enter with:** Product facts, audience/context evidence, inherited identity and the current opportunity.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — open the problem | Inspect the actual subject, audience moments and references. Explore possible emotional or perceptual needs before naming a material; separate observed needs from imagined scenes. Retain the evidence and competing interpretations. |
| Define — choose the challenge | State the intended change in perception/use, the value it protects and the trade-off. Select a suitable creative lens; specify what must remain familiar and which product capabilities cannot change. |
| Develop — construct expressions | Develop materially different answers to that challenge. For material work choose material+environment, then derive lighting, layering, edges and finish; for another lens resolve equivalent visible/behavioral relationships. Compose real content and a contrasting task, not a mood-word menu. |
| Deliver — test and hand back | Inspect the rendered proposals before explanation; compare effect, use and costs. Refine the strongest relationship and recommend through the existing decision. Hand selected rules to color/type/composition/component work; return to Define if the metaphor depends on unsupported product meaning. |

**Retained execution record:** In the existing study/Foundation retain: source → challenge → lens → visible rule → applicable surface/state → resolved property/value or implementation freedom → comparison evidence. Material rules include light direction/softness, surface layers, edge roles and finish; include only properties the chosen language uses.

The craft methods below supply the choices and construction detail for this workflow.

Use for innovation-led work, including a utility product whose task experience
could become clearer or more meaningful. Innovation may be perceptual, emotional
or interactive; it need not invent a gesture, animation or product capability.

### Develop a mechanism, not a mood board

Start from the grounded moment: what the person is trying to judge, the feeling
or friction supported by evidence, and the change worth exploring. Name the
competing value. Choose a lens below because it opens that opportunity. Sketch
other lenses only when they produce a materially different proposition.

| Lens | Generative move | Translation into a screen | Failure to examine |
|---|---|---|---|
| Material metaphor | Give the experience a physical property and context: held, layered, marked, porous, elastic, precise | Translate two or three properties into type, edges, grouping, light or feedback; explain which physical behavior does **not** transfer | Literal texture, decorative objects, or physics that obscures controls |
| Dual Physics (B-Pro vs C-Consumer) | Ground physical intuition by domain: **Instrument Physics** (calipers, dials, detents, tabular-nums) for B-Pro; **Lifeworld Somatics** (paper fold, fluid inertia, gravity snap, 44px thumb zone) for C-Consumer | Manifest physics as tactile micro-dynamics (easing, damping, elevation) rather than literal visual noise | Entity contamination: renaming domain objects into physics metaphors (e.g. calling tasks particles) |
| Archetype | Define a supported relationship: coach, curator, companion, instrument; what does this role help the person notice? | Set voice, emphasis, timing of help, density and the degree of invitation versus authority | Stereotyped users, patronizing copy or unsupported promises |
| Narrative | Follow anticipation → consequential decision → response → return; identify where confidence, curiosity or satisfaction should change | Compose an opening, evidence at the decision, a meaningful result and continuity on revisit | Turning a repeatable task into forced theatre or hiding essential comparisons |
| Cultural/semiotic | Inspect an actual artifact or tradition relevant to audience/content; identify its structural grammar and meaning | Transform editorial order, mark-making, proportions or rhythm; cite source and adaptation | Exotic decoration, false cultural authority or unreadable symbols |
| Task reframing | Change how an existing relationship becomes perceptible: compare, arrange, inspect, revise | Show how the same data and allowed operations become easier to reason about | Quietly adding capabilities, merging objects or mistaking fewer clicks for less mental work |

For a material: name the property → perceptual effect → UI relationship → limit.
For example, layering can distinguish source from draft while keeping both
legible; it does not authorize merging their lifecycles. Texture is optional.
For a narrative: test the later visit as carefully as the first reveal; the
result must still communicate the person's choice after celebratory copy expires.

### Lightweight Native Craft Recipes (免依赖原生工程质感与微动能配方)

High-fidelity verisimilitude requires authentic craft without heavy framework bloat. Rely on clean, semantic HTML/CSS/SVG primitives:

1. **Topological Flow & Stream Pulses (轻量数据流脉冲)**:
   - For streaming or pipeline architectures (Baseline 1), convey operational liveliness via pure SVG path animation:
   ```css
   .flow-line {
     stroke: var(--border-bright);
     stroke-dasharray: 6 4;
     animation: flow-pulse 1.2s linear infinite;
   }
   @keyframes flow-pulse {
     from { stroke-dashoffset: 20; }
     to { stroke-dashoffset: 0; }
   }
   ```
   - Delivers instant subconscious confirmation of active throughput without GPU thrashing.

2. **Micro Sparklines & Trend Baselines (内联轻量时序线图)**:
   - Never show floating, context-free scalar numbers. Accompany critical metrics with compact inline SVG sparklines (40-60px width, 16px height) using `<path>` or `<polyline>` with subtle area gradients:
   ```html
   <svg class="sparkline" width="60" height="16" viewBox="0 0 60 16">
     <path d="M0,12 Q15,4 30,10 T60,2" fill="none" stroke="var(--status-running)" stroke-width="1.5" />
   </svg>
   ```

3. **Optical Concentric Geometry (同心几何的所有权归属)**:
   - Owns the concentric relation, not a fixed radius value: nested rounded containers
   stay optically concentric with
   $$R_{\text{in}} = \max(0, R_{\text{out}} - \text{Padding})$$
   recomputed at every nesting level. The declared `spatial_geometry` axis and
   `massing_pattern` own which radius scale the surface uses — compact dense-console
   radii and generous editorial radii are equally valid; only the concentric relation
   is invariant.

4. **Tactile Mechanical Detents & Feedback**:
   - For mission-critical actions, combine tactile micro-motion with clear visual state changes:
   ```css
   .btn-action:active {
     transform: scale(0.98);
     transition: transform var(--duration-fast) var(--ease-tactile);
   }
   ```

5. **Stateful Micro-App Architecture (数据驱动的原型微架构，彻底告别单点木偶假交互)**:
   - Prototypes are NOT static brochure mockups; they MUST be authored as functional, self-contained interactive micro-applications.
   - **Central App State Store**: The client-side JavaScript MUST maintain a reactive or centralized state store:
     ```javascript
     const AppState = {
       entities: [...],        // Multi-node data model (minimum 3 operable entities)
       selectedEntityId: '...',// Current inspection focus
       filters: { ... },       // Query/status filtering
       runtimeMetrics: { ... },// Live/simulated telemetry
       history: []             // Audit/event stream
     };
     ```
   - **Universal Entity Inspectability (全实体聚焦可查)**:
     - Clicking ANY node or row in the primary viewport MUST dynamically load its full operational state, historical traces, and diagnostics into the contextual drawer/inspector.
     - Never hardcode interactions to a single arbitrary node while leaving sibling nodes dead.
   - **Multi-Branch Action Lifecycle (多动作状态分支)**:
     - Interactive workflows must support multi-stage branching: Selection -> Parameter Tuning / Confirmation -> Execution -> Diverted Stream / State Mutation -> Reversion / Reset.
     - Provide immediate, visible cause-and-effect across the entire layout (e.g. isolating Node 02A updates its status badge, re-routes downstream SVG connection wires, clears backpressure gauges, and posts an audit event).

### Form an aesthetic point of view

Choose concrete references that illuminate the current opportunity: a familiar
competent solution, an expressive alternative, or an adjacent cultural artifact.
Inspect what they actually do with scale, rhythm, color, image and interaction.
Extract a relationship, then transform it around this product's content. Several
references can inform a direction, but combining their ingredients is not synthesis.

State the leading idea, the supporting grammar and the convention deliberately
kept familiar. Translate emotional intent into visible contrasts: generous versus
compressed, crisp versus soft, luminous versus subdued, ceremonial versus immediate,
only where useful. Explain why the composed result has that character; adjectives
alone cannot serve as evidence. A non-metaphorical direction can be just as authored.

Explore enough to challenge the first plausible answer, then develop the strongest
relationships rather than averaging styles. Evaluate appeal and utility separately:
a direction may feel compelling yet create learning cost, or work cleanly while
lacking a point of view. Show that trade-off and recommend with reasons.

### Preserve capability through the transformation

Before recommending a proposition, restate its consequential scene **without
the metaphor**: who can see which facts, perform which operation on which object,
and observe which result? Map those operations to the brief or confirmed product
source. A metaphor may change emphasis, grouping or feedback; if the plain
version introduces an unsupported operation, user role, device capability or
policy, remove that dependency or present it separately as an unapproved product
proposal. An imagined usage scene is not evidence that the current task fails.

Keep guarantees in their actual owner. Visual grouping can help users recognize
distinct objects; it cannot enforce their identity, permissions or state rules.
Explain how the retained Contract preserves those invariants and how the UI
makes them understandable. Do not rank a direction as structurally safer solely
because one object is visually prominent.

### Give each promising proposition a visible grammar

Compose the **same representative content** at the same size before selecting.
Resolve a focal element, reading path, type contrast, spatial rhythm, color
relationship, content treatment and feedback emphasis. Describe relationships
and intended effect rather than just naming ingredients. Bring one distinctive
relationship into a dense or transactional companion scene; state what quiets
down and what remains recognizable. Preserve the product's existing semantics.

Show the requested concrete scene in this comparison, including what is visible
at the decision and immediately after it; do not defer the substance of the
comparison until the user selects a label. When this turn is text-only, use a
specific storyboard or spatial description and mark visual craft unverified.
State whether rendering was out of scope, not attempted, or actually unavailable;
only an observed capability failure establishes the last of these.

Compare a competent familiar solution when competitive. Ask what users gain,
what they must learn, what evidence would refute the advantage, and whether the
proposition still works without its most decorative flourish. A useful signature
should survive real labels, long copy, reduced motion and constrained space.

Retain the causal chain in the existing comparison/Foundation: evidence →
opportunity → lens → composition/behavior → cost → observed result. Use actual
rendered probes for visible claims; imagination alone leaves them unverified.
The same language can support different layouts; the retained Surface Topology
still owns page and object boundaries. User selection/delegation follows the
existing discussion rule.

A prohibition does not supply the complementary capability: “X must not happen
automatically” does not establish who can perform X, which states exist, or that
X is in scope at all. Keep the original constraint intact; develop the requested
operation without inventing the missing policy. If another operation is useful
to propose, label it separately and keep the current scene viable without it.

## Develop typography, space and color together

### Develop optical character instead of applying a finish recipe

Craft comes from deliberate relationships, not a mandatory bundle of shadows,
tracking, type pairings or glass effects. Start with the product posture and the
representative content, then choose the smallest optical system that expresses it:

- Use scale, weight, width, tracking, line height and measure to create the needed
  reading tension. Inspect the actual font and script; negative, neutral and open
  tracking are all legitimate outcomes.
- Use borders, surface steps, shadow, transparency, texture or no material effect
  according to containment, hierarchy and the selected Signature Relationship.
  Flatness can communicate immediacy and precision; depth can communicate layering
  or tactility. Neither is a quality baseline.
- Pair typefaces only when their distinct roles improve meaning or character. A
  single well-tuned family can outperform a decorative pairing.
- Calibrate optical edges, density and color in the whole frame and in a
  consequential state. A copied recipe that fits unrelated products is evidence
  of weak authorship even when it looks polished.

When a treatment is unsettled, compare controlled alternatives on the same
content and task. Retain the selected relationship, exact values, product reason,
scope and transfer evidence in the existing design artifacts.

### Specialized Double Diamond workflow

**Enter with:** Product emotional/operational intent, inherited palette/theme scope, actual content and a representative composition.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect color conditions | Inspect identity/reference images, light conditions, adjacent surfaces, image colors and current state meanings. Consider whether dullness comes from field lightness, hue relationships, chroma, area or competing emphasis; do not assume the accent hue is the cause. |
| Define — set the color problem | State the intended whole-frame feeling and current decision emphasis. Identify stable semantic meanings, theme scope and the relationship to explore; define visual-fit and readability evidence before palette generation. |
| Develop — build palettes in context | Choose and vary a suitable hue relationship, derive focal/support/rest colors and lighter/stronger role variants, then map canvas/text/action/selection/status. Render controlled alternatives on the same content/layout, plus a consequential state; use the color-development method below. |
| Deliver — verify and extract | Compare actual page color and state meaning, measure real foreground/background pairs, revise the responsible role/ramp and rerender. Extract exact selected runtime-compatible tokens and their component uses; transfer to a second surface before the existing language decision. |

**Retained execution record:** Retain role → exact value → paired background/foreground → meaning/state → intended emphasis → component selector/use → measured/rendered evidence. Derived colors must resolve in the actual runtime. A palette file without its composed pairings is not the completed output.

The craft methods below supply the choices and construction detail for this workflow.

Read when developing a visual proposition, then when translating its selected
language into tokens. Values belong to the retained token artifact; this file
does not provide a preset palette, font pair or spacing scale.

### Compose before extracting values

Set realistic primary content, metadata, controls and a difficult text example
into the representative frame. Decide what should be noticed first, compared
second and available on demand. Establish these relationships together:

- **Typography:** develop actual reading/scan roles, letterform contrast and
  rhythm using [typography](#typography-as-voice-and-reading-structure) when the language is new or weak.
- **Space:** develop grouping, grid, focal mass and responsive recomposition
  using [composition](#compose-attention-relationships-and-rhythm); spacing tokens encode that relationship.
- **Color:** assign canvas, surface, text, subtle text, action, selected, focus
  and applicable status roles. Develop a meaningful relationship among them,
  including deliberate monochrome when earned. Check actual adjacent surfaces
  and text/necessary control-state cues using the [design floor](../03-verification/quality-floor.md);
  quiet copy is still normal text. Include the actual cue and adjacent field in
  paired specimens before freezing roles; distinguish interactive identification
  from decorative boundaries so one subtle separator token need not serve both.
  Shape/text/position also communicate state. Accent coverage is a compositional
  judgment, not a percentage quota; brand hue and error meaning remain distinct.
- **Depth and imagery:** use boundaries/elevation to explain relationships and
  material. Keep meaningful content legible when texture, image or transparency
  changes. Depth is not a requirement for every container.

Extract reusable semantic tokens from the composition, then test a contrasting
surface so a beautiful first frame does not hide an unusable scale. Define scoped
role changes rather than globally shrinking text to fit a difficult page.

### Develop a color language, not just a safe accent

Before fixing a new palette, translate the intended feeling into relationships:
lightness of the whole field, chroma of focal and resting areas, warm/cool hue
relationships, and the amount and placement of colored surface. “Fresh”, “warm”
and “energetic” are hypotheses to demonstrate, not hue names. A craft metaphor
need not inherit brown paper; trust need not mean desaturated blue; sophistication
need not mean darkness. Deliberate restraint remains valid when it serves the
product rather than an unexamined default.

When color is unsettled or the user finds the work dull/dark, compare two or three
materially different color treatments on the **same content, layout and viewport**.
Include a credible brighter, more chromatic treatment when freshness or vividness
is requested. Isolate this question within the existing direction probe; do not
multiply every layout by every palette or create a separate approval track.
Swatches and adjectives cannot demonstrate the choice. Judge rendered page fields,
primary action, representative content/imagery and a selected or feedback state.

Develop the relationships deliberately:
- Give the dominant field, brand/action color and any supporting hues distinct
  jobs. Explore related hues or a contrasting companion according to the desired
  character; no fixed number of hues or universal area ratio is required.
- Balance vivid focal areas with readable resting areas. Brightness can come from
  a luminous canvas and clear hue separation, not only higher saturation. Avoid
  tinting every surface equally or making every element compete at full chroma.
- Coordinate imagery/illustration with interface colors. Check whether the whole
  frame still feels muddy, cold, washed out or heavy despite a colorful button.
  Inspect at actual size: a large color field changes the effect of a small swatch.
- Build lighter and stronger role variants, including legible text on bold color.
  Preserve the intended hue character while adjusting lightness/chroma for the
  actual pairing; do not darken the entire palette to solve one text contrast issue.
  A bright yellow surface, for example, may need dark text rather than white.
- Keep decorative or category accents distinct from action, selection and status
  meanings. The same vivid language must support recognizable focus and errors;
  color alone cannot carry those meanings.

Compare emotional fit, hue relationships, emphasis/rest, visual comfort and
recognizability as well as measured contrast. Name the particular relationship
that improves the product and the cost it introduces. Carry the chosen grammar
into a dense or consequential surface: a colorful opening followed by generic
muted forms has not established a reusable language. Do not claim pleasantness
was user-tested when only expert visual inspection was performed.

### Translation checks

Before extracting a palette, choose a relationship to investigate. These are
construction options, not product-category prescriptions:

| Relationship | How to construct a candidate | Failure to inspect in the page |
|---|---|---|
| Single hue family | Separate roles chiefly by lightness, chroma and area | Insufficient distinction or monotonous fields |
| Neighboring hues | Build a coherent family while reserving a stronger focal role | Similar hues merging in small controls or charts |
| Opposing hues | Let one hue carry a main role and the other a deliberate counterpoint | Both competing equally, or a decorative contrast resembling an alert |
| Split contrast | Compare two neighboring counter-hues against the leading family | Supporting colors acquiring unnecessary semantic meaning |
| Three separated hues | Assign distinct jobs before balancing their strength | A scattered frame without a clear attention hierarchy |
| Warm/cool tension | Compare field temperature with image, text and action temperature | A muddy combination or an unintended emotional association |

Treat color-wheel relationships as hypotheses, not sufficient evidence of harmony.
Build each role family by changing lightness and chroma deliberately; equal numeric
steps need not create equal perceived steps. With a perceptual color space supported
by the actual toolchain, hold hue provisionally, establish a readable strong role
and a gentle surface role, then adjust intermediate steps against their uses.
Reduce chroma when needed to keep colors representable; inspect resolved runtime
values and exported assets rather than trusting editor swatches or a formula.
Do not generate unused steps just to fill a conventional ten-color ramp.

Construct a paired specimen for each actual use: text on canvas, text on brand
surface, action at rest/focus, selected content, and relevant feedback. For each
pair retain exact foreground/background, adjacent field, semantic role and actual
contrast result. When a pair fails, vary the responsible foreground or surface;
rerender the composition to ensure the local repair preserved its overall energy.
Inspect images and overlays at their difficult real backgrounds, not only the
average image color. A measured pair is necessary evidence for legibility, while
the full-frame comparison supplies the aesthetic judgment.

Document role → value → applicable context → component use. Inherit exact frozen
values during implementation; changes to language require a successor through
the existing lifecycle. Separate semantic defaults from page layout constraints.
Use the stack's supported units/color syntax and verify computed output. Test
only requested themes, plus platform accessibility settings; an absent optional
dark theme is a scope fact, not permission to create a second brand system.

### Keep the language portable

The retained token table is the human-readable projection; the Foundation revision
owns every value. When a build step, design tool or downstream repository needs the
same roles, export them as a machine-readable file in the
[W3C Design Tokens format](https://tr.designtokens.org/format/) (`$value`/`$type`)
and map the standard groups (color, dimension, typography, shadow, duration) onto
the roles already defined here. Do not invent a second naming system or let the
export freeze token values as the specification. An export that has not resolved
in the actual runtime is a reference, not delivered code.

Evidence: actual-size composition, font/fallback observation, contrast samples,
long-content/narrow/enlarged-text frame, and one contrasting surface. The token
table explains the system; the rendered relationships demonstrate its quality.

## Typography as voice and reading structure

### Specialized Double Diamond workflow

**Enter with:** Real multilingual content/roles, available fonts, inherited language and target reading/scan tasks.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect reading conditions | Read the actual text and font specimens; inspect script coverage, length, numerals, current hierarchy and device conditions. Identify whether the issue is voice, scan order, sustained reading or fit. |
| Define — choose the typographic challenge | Specify intended voice and reading priority, role distinctions and constraints. Choose the relationship worth varying while preserving settled palette/content. |
| Develop — compose and resolve specimens | Develop credible role/family relationships with actual text. Tune size, weight, width, leading, measure and tracking together; inspect loaded glyphs and compare layouts at actual scale. |
| Deliver — stress and hand off | Read wide/narrow/enlarged and dense companion specimens. Refine the responsible role rather than shrinking everything; retain exact family/source/fallback and metric values, screenshots and limitations for tokens/Builder. |

**Retained execution record:** Role → actual font/source/fallback → size/weight/leading/tracking/numeral settings → measure/wrap behavior → scope → specimen/runtime evidence.

The craft methods below supply the choices and construction detail for this workflow.

Read when developing new language or when text feels generic, tiring or poorly
ranked. Tokens retain selected values; this reference develops the relationships.

### Choose from the actual reading job

Compose a specimen from the product: a primary title, a normal paragraph, an
ambiguous long label, supporting metadata and realistic numerals. Identify whether
people read continuously, scan choices, compare values or operate controls.

- For reading, develop measure, leading and paragraph rhythm together. A larger
  font in an excessively narrow column can make reading harder; inspect actual
  line breaks rather than importing an English characters-per-line rule into CJK.
- For scanning, make labels, values and qualifiers distinguishable through a
  deliberate combination of position, size and weight. Every label need not be
  bold; a consistent value column can do more than another heading level.
- For comparison, align equivalent information and let the declared
  `micro_typography` axis own the numeral forms: when declared, tabular figures
  hold the value column and the declared display tracking applies; when a native
  or prose surface declares no display tracking, proportional forms fit the text.
- For expressive titles, test how letterform shape, stroke contrast, width and
  spacing relate to the product's voice. A display face earns its role through
  the composed words, not its reputation. Interface text need not share that face.

### Develop a typographic relationship

When voice is unsettled, compare the same specimen with a strongly developed
single-family hierarchy and a contrasting role pairing, or another meaningful
alternative. Vary a consequential relationship rather than browsing endless font
names. Consider warmth/precision, solidity/lightness and formal/informal cadence;
these are observations about the rendered sample, not universal font personalities.

Choose a small set of roles with clear contrast. Establish one dominant level,
subordinate the next decision, and give repeated supporting text a stable rhythm.
Use size, weight, placement and space jointly; avoid compensating for weak hierarchy
by making all text larger or lighter. Tune the actual content before extracting a
scale. A modular ratio can generate candidates but does not decide the final sizes.

Inspect Chinese punctuation, mixed Latin/numerals, weight availability and fallback.
Do not simulate a delicate face through low contrast or prescribe Latin tracking
to Chinese body text. Verify what loaded, including missing glyphs. Match labels
and nearby icons optically; trim awkward title wraps through composition or copy
within scope, not hidden overflow or blanket font shrinking.

### Resolve mobile typography as a reading system

Start with the actual narrow viewport and task, alongside the wide specimen.
Assign roles by reading job: expressive display, page orientation, repeated item,
body, action label and supporting detail. A page title and every repeated item
need not compete for dominance. Compare the same mobile content with a different
allocation of emphasis (size, weight, space), keeping palette and task fixed.
For an open type choice with narrow-screen use (including desktop-first tools),
keep the principal arrangement,
content, imagery and palette stable while rendering credible alternative type
relationships: for example a single-family hierarchy versus a role pairing, or a
different allocation of title/item/body emphasis. A/B whole-layout directions
answer a composition question; they do not by themselves isolate this type choice.
Compare the real specimens before freezing the scale, retaining the selected
relationship, rejected alternative and reading/task trade-off. The comparison can
be a small Builder probe inside the current direction; it needs no extra formal
artifact or approval. Inherited settled type and mechanical local fixes do not
need artificial alternatives. A local wrap repair is refinement, not evidence of
an earlier alternative that was never constructed.

Use current platform roles or an inherited system as a starting hypothesis. For a
browser interface, a 16 CSS px body with nearby label/support and clearly separated
heading roles can be a useful initial specimen, not a universal minimum or final
answer. Physical legibility depends on the actual face, script, weight and device;
CSS px, native pt and sp are not interchangeable prescriptions. Tune the real
paragraph, dense list and form together. A large display title may earn space on
an expressive entry while the transaction uses a quieter heading.

For each role retain family, real available weight, size, line height, measure and
narrow/wide behavior. A declared font stack or document.fonts readiness does not
prove which face supplied a CJK glyph. Inspect available platform/font evidence
and rendered mixed-script specimens; mark exact face resolution unverified when
unsupported. Check unavailable weights, synthetic bold and fallback numerals;
intermediate CSS weights need not yield distinct physical weights. Compare family
alternatives only when the decision is open; a well-developed system face can win.

Inspect Chinese line endings at representative and intermediate widths. An isolated
last character in a prominent short title is a repair signal, not a reason to ban
all one-character lines in every context. Compare width allocation, role sizing,
weight, authorized wording and semantic wrapping; preserve meaning and reflow.
Avoid a forced line break that fixes one width and damages another. Keep units
with values where needed without creating overflow through excessive no-wrap.

Evaluate reading density as useful task information per frame, not maximum text
or minimum scrolling. Examine which repeated bold/large blocks consume attention,
which label/value pairs must be seen together, and whether explanatory copy delays
the first meaningful decision. Adjust the responsible role/grouping rather than
shrinking every font. Normal-size comfort and enlarged-text access are separate
checks: passing 200% does not excuse an awkward default layout.

[Apple typography guidance](https://developer.apple.com/design/human-interface-guidelines/typography)
and [Dynamic Type](https://developer.apple.com/videos/play/wwdc2024/10074/) are
platform references for text roles and scalable layout, not universal web sizes.

### Derive reading-stress cases from the actual layout

Inventory distinct constrained reading relationships in the scoped product, such
as a title beside artwork, an aligned value/label pair, a repeated dense row or an
inline control label. Group instances only when their available measure, type
roles and reflow rule are equivalent. Select the longest meaningful text or mixed
script in each consequential class, then combine narrow width with enlarged text.
A clear entry heading cannot represent a differently constrained detail or editor.
Include shared navigation and text-bearing component boundaries, not only page
bodies. Sample each materially different active layout rule under text growth:
the narrowest viewport may already stack generously while a roomier viewport
retains a cramped row. Check the consequential transition and retained-adjacency
regime, rather than treating a smaller passing width as proof for larger widths.
Use representative cases per rule, not an exhaustive width-by-content matrix.
Keep this small case list with the existing typography/Specification assertions:
relationship → stressful content and condition → expected reading/operation →
actual line arrangement and task evidence. Preserve these cases when translating
Foundation intent into the Builder's screenshot/check list.

At each case, inspect word/phrase recognition and reading rhythm as well as lost
content or page overflow. A layout can contain every glyph yet squeeze text into
fragmentary columns. Inspect the space retained by adjacent imagery or controls;
compare releasing that adjacency, reallocating space or another readable layout
through [composition](#compose-attention-relationships-and-rhythm). Derive a viable measure from actual script/words and the
chosen face. Intrinsic wrapping or text-relative fit conditions can respond to
font growth where a viewport-only breakpoint does not; test the selected behavior
rather than assuming a particular CSS unit solves it. Preserve required comparison
relationships and meaningful two-dimensional data layouts.

Keep a dynamic label, its value and punctuation in a coherent visual reading
sequence when they wrap. Decide which parts form one phrase and which can occupy
independent layout slots; a count or closing bracket must not jump ahead of the
label's unfinished text. Inspect text within bounded or masked components at the
same enlarged condition, even when the page itself has no overflow.

Use language-aware line opportunities. Word breaking anywhere may contain a long
identifier, but is a last resort for ordinary prose when a better text measure is
available. Prefer a readable relationship before reducing the requested text size,
clipping the value or forcing a break for one screen. Recheck default and enlarged
conditions after the adjustment, including the companion that uses another layout.
[W3C line-breaking approaches](https://www.w3.org/International/articles/typography/linebreak.en)
explain script differences; [reflow guidance](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
addresses access under resizing. The qualitative reading check here goes beyond
an overflow measurement and is not itself a new WCAG rule.

### Judge the specimen in use

Read it at actual size, then in a narrow layout and with enlarged text. Compare
first-glance order, sustained reading comfort and character. Preserve the selected
voice in a dense or transactional companion: hierarchy may quieten while the type
relationships remain intentional. Record specimen, chosen roles, rejected trade-off
and observed limitations in the existing study/Foundation. Expert inspection is
not a reading-speed experiment; do not invent measured comprehension gains.

Before handoff, compare the selected mobile entry, a repeated-content or dense
companion and an action/error state at actual scale. Retain screenshots and actual
computed role metrics, observed wrap problems, the selected trade-off and the
follow-up result. Verify enlargement/reflow separately. Ask the Critic to judge
font fit, role hierarchy, line rhythm and task density independently; a color or
aggregate visual score cannot compensate for a weak applicable typography facet.

## Compose attention, relationships and rhythm

### Specialized Double Diamond workflow

**Enter with:** Real content priorities and ranges, current language and viewport.
Use retained page responsibilities from the Surface Topology when available; an
early expression probe may use a provisional frame/task brief without freezing
page boundaries.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect content relationships | Identify what must be compared, read, acted on and revisited; inspect visual mass and current grouping without assuming a grid. |
| Define — choose the spatial problem | State the intended reading/decision path and which relationships must stay adjacent. Name the current conflict and a criterion for useful density or expressive balance. |
| Develop — construct relationship layouts | Sketch materially different spatial arrangements on the same content. Resolve columns, alignment, widths, spacing rhythm, anchors and deliberate exceptions; Builder renders the credible candidates. |
| Deliver — recompose and specify | Inspect actual size, intermediate/narrow widths, long content and enlarged text. Revise grouping or geometry at its cause. Retain concrete grid/width/spacing constraints and responsive transformations with evidence for the selected composition. |

**Retained execution record:** Content region → priority/adjacency → grid/flow placement → min/max/fluid sizing → role spacing/alignment → breakpoint or content-fit transition → overflow/disclosure rule → rendered evidence.

The craft methods below supply the choices and construction detail for this workflow.

Read when developing a page's spatial language or resolving a crowded, flat or
interchangeable frame. Surface Topology owns page boundaries and information requirements;
this reference arranges the supplied content within those boundaries.

### Start with relationships, then choose geometry

List what should be noticed, compared and acted on, and what can remain peripheral.
Sketch those relationships with real labels before selecting a grid or card system.
Useful structures depend on the work:

| Needed relationship | Spatial move to explore | Cost to inspect |
|---|---|---|
| Compare like attributes | Aligned rows/columns or a comparison field | Narrow screens may require selective repetition or a clear shared summary |
| Inspect one item while retaining a set | Master/detail, adjacent evidence or contextual panel | Divided attention and constrained reading width |
| Read an argument or narrative | Continuous measure with paced interruptions | Oversized introduction can delay the actual content |
| Choose among recognizable visual subjects | Repeated image/content units with consistent comparison positions | Imagery can dominate practical differences |
| Perform a consequential action | Stable evidence block with nearby action and recoverable context | A dramatic focal action can suppress needed qualifications |

Use proximity for related items, similarity for repeated meaning and enclosure
when a real region needs a boundary. Inspect conflicts: identical cards can imply
equal priority; a strong box can falsely associate unrelated facts. Gestalt terms
explain a grouping decision, not a requirement to put everything into containers.

### Develop the whole frame

Establish alignment lines, margins, gutters and a rhythm that connects type,
controls and imagery. Use a grid as a coordination tool; derive columns and widths
from content, not a mandatory 12-column or eight-pixel rule. Decide which dimensions
are fluid, which protect readable content and where a deliberate exception belongs.

Create focal contrast using scale, placement, color and negative space together.
Balance visual mass across the frame rather than merely centering bounding boxes.
Whitespace can separate decisions, pace reading or give a subject presence; large
blank areas without one of those jobs are not evidence of sophistication.
A dense layout can be elegant through shared alignment and clear secondary levels.

When composition is genuinely unsettled, compare two relationship sketches on the
same content: for example continuous versus compartmentalized, balanced versus
asymmetric emphasis. Develop the promising relationship; do not make alternatives
that only change gutters. Keep all required comparison information in the test.

### Recompose, do not only resize

At a narrow width, preserve the reading/action priority while deciding what stacks,
reorders, stays adjacent, becomes a summary or discloses on demand. Change the
composition when the content stops fitting, not only at named device categories.
Inspect long labels, uneven item counts and enlarged text. A horizontal overflow
check cannot prove the mobile decision remains understandable.

Judge first glance, deliberate comparison and the continuation after action.
A reduced-size thumbnail can expose competing visual masses; it supplements,
never replaces, actual-size inspection. Record the grid relationships, deliberate
exception, mobile transformation and trade-off in the existing design artifacts.

## Art direction for images and illustration

### Specialized Double Diamond workflow

**Enter with:** Actual subject/content, truthful sources, available authorized asset tools, frame/role and intended visual language.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect subjects and assets | Inventory real images and missing needs; inspect quality, aspect, focal detail, rights/source and series variation. Clarify what must be depicted accurately and what can be illustrative. |
| Define — frame the image brief | Set the communicative role, required subject truth, slot/content constraints and intended effect. Distinguish inherited art-direction rules from open hypotheses about medium, viewpoint, lighting, palette relation and crop. Define credibility and expressive-fit checks before choosing those treatments. |
| Develop — acquire and compose candidates | Develop credible treatments for the open hypotheses and source or generate candidates with the available permitted tools. Build an actual-size image/series comparison in its UI slots, including narrow crops and mixed-content conditions. Improve the source/treatment rather than masking a weak image behind effects. |
| Deliver — select and integrate | Inspect subject recognition, visual coherence, crop, alt/fallback and UI attention. Refine or replace failed assets, then retain exact selected paths, crop rules and source metadata; verify key secondary surfaces and missing-image behavior when applicable. |

**Retained execution record:** Asset role → exact path/URL/source → subject/truth status → art-direction parameters → aspect/focal crop/object-fit → alt/decorative treatment → fallback → component use → actual render evidence.

The craft methods below supply the choices and construction detail for this workflow.

Read whenever photography, illustration, diagrams or generated assets materially
carry understanding or character, on any surface. Entry composition owns the first
viewport's job; imagery is not restricted to a hero area.

### Decide what the image must contribute

Distinguish evidence of a real subject, explanation of a relationship, an emotional
invitation and a decorative accent. Choose the medium for that job: photography
for a credible real subject, illustration for an authored idea, a diagram for a
relationship, or typography when the content itself carries the identity. A stock
photo, simple SVG and generated painting are not interchangeable quality levels.

Write a small art-direction brief: subject/action, point of view, composition and
focal area, light, palette relationship, medium/edge/detail, aspect ratios and space
needed by nearby content. Name the feeling and the visible choices expected to
produce it. Describe the intended world; an artist or brand name alone is not an
art direction. Do not treat a material metaphor as a request for literal texture.

For a series, establish a shared grammar such as viewpoint, silhouette, light,
mark-making, scale and background behavior, while varying subject and composition.
A consistent palette alone will not make mismatched stock or generated images a
coherent family. Different surface roles can use different levels of detail while
retaining the same grammar.

### Develop and select in context

Use supplied or available authorized assets, search, generation or editing tools
according to their actual capabilities and permissions. When image quality drives
the proposition, investigate those routes before settling for a convenient generic
shape. A locally authored SVG is a good solution when its visual language fits,
not simply because it is easy to code. If the required medium is unavailable,
show the limitation and develop a credible alternative rather than pretending
an empty box or CSS gradient proves the intended art direction.

Compare candidate images in the intended frame, not only at full size. Inspect
subject credibility, anatomy/geometry where relevant, visual specificity, crop,
focal conflict with text and palette integration. Test narrow crops and small
thumbnails; protect meaningful content and provide appropriate alternatives for
accessible understanding. Select by the relationship to the product, not maximum
detail, spectacle or photorealism.

Generated or illustrative assets must not masquerade as real customer results,
product evidence or photographs of an actual place. Retain source/rights and
prototype disclosure where needed. Keep important labels in real interface text
rather than relying on image-rendered text.

Carry the grammar into a relevant secondary moment when useful: a small subject
cue, result illustration or empty-state invitation. It should help orient or reassure,
not force a large picture into every form. Document chosen assets/crops, series
rules, actual rendered evidence and unresolved asset quality in existing records.

## Entry composition and meaningful imagery

### Specialized Double Diamond workflow

**Enter with:** The actual entry surface job, current task/IA constraints, product proposition, available assets and viewport.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect the arrival | Determine why people arrive and what they expect immediately. Inspect actual content and credible references; consider work, orientation, reading, persuasion or experience without assigning an entry type from industry. |
| Define — choose the opening duty | State the first recognition, decision and next action. Decide what earns initial visual weight and what must remain accessible. Establish asset feasibility and the continuity expected in the next task. |
| Develop — compose plausible structures | Use the type-, subject-, relationship- or experience-led approaches below to construct relevant alternatives. Specify anchors, reading sequence, asset crop and action placement with actual content; Builder implements inspectable representative frames. |
| Deliver — verify the declared structure | Inspect first glance, deliberate reading and next action at wide/narrow sizes. Refine the weak relationship; retain the chosen structure, asset, type/space roles and rendering evidence. Builder must not silently replace it with a cheaper or more dramatic opening. |

**Retained execution record:** Entry job → primary/secondary anchors → reading order → named action → asset source/subject/crop/fallback → role-based composition → narrow transformation → next-task continuity → screenshots and unresolved claims. Store in existing Foundation/Specification; no parallel theme authority.

The craft methods below supply the choices and construction detail for this workflow.

Read when the first viewport must establish value, invite exploration or show
an artifact. First identify its job: working surface, orientation, persuasion,
reading or experience. A logged-in task should normally begin with the work;
an editorial opening can earn prominence when the content itself is the product.

Choose a composition from the content and proposition, not a tier/keyword map:

- Type-led: make actual words and their hierarchy carry the identity. Judge
  reading rhythm, placement and contrast at real size; no fixed heading size.
- Subject-led: let a relevant photograph, artwork, product view or demonstration
  show what text cannot. Decide crop, focal point, caption and relation to action.
- Relationship-led: arrange content to expose a comparison, sequence or tension.
  Use asymmetry only when it directs attention; a centered composition can be right.
- Experience-led: motion or immersion earns its cost when experiencing it is part
  of the value; keep a usable static/accessible entry and an obvious next action.

When imagery carries the proposition, read [art direction](#art-direction-for-images-and-illustration), including
for non-entry surfaces. For spatial choices use [composition](#compose-attention-relationships-and-rhythm).
The entry must introduce the same language that ordinary product work can sustain.

Use concrete available or authorized assets with source/license information.
Distinguish an illustrative prototype image from a real product photograph.
If no credible asset exists, redesign around real content or record the missing
asset instead of filling a prominent box with a gradient or pretend photograph.
Custom diagrams/SVG are appropriate for actual structure or illustration; they
are not evidence that a depicted real object exists. Do not turn every app into
a landing page just to make an attractive screenshot.

Check first glance, full reading and the next action on narrow and wide frames.
Does the entry tell this product's story? Does the next task maintain the language?
Is useful content available without waiting for animation? Compare the composition
with an ordinary, competent version to see what the expressive choice contributes.

## Iconography that explains actions

### Specialized Double Diamond workflow

**Enter with:** Actual actions/object meanings, existing icon assets/family, adjacent text and required states/sizes.

Follow the shared execution/return rules in [the method library](../01-foundations/design-methods.md).

| Phase | Work and concrete hand-back |
|---|---|
| Discover — inspect meaning and sources | Inventory intended concepts and easily confused neighbors. Inspect available families and real glyph exports or vector sources; distinguish navigation/actions, brand symbols and user content. |
| Define — set recognition and family rules | Choose which controls need visible labels and which familiar symbols can stand alone. Define optical weight, detail, perspective and selected-state relationship appropriate to the language. |
| Develop — build a contextual glyph board | Shortlist meaningful candidates for unresolved concepts. Render them beside actual labels and neighboring actions at intended sizes, including selected/disabled appearances where relevant. Adjust optical sizing/centering and retain exact glyph sources. |
| Deliver — verify and map instances | Check recognition/ambiguity through the available expert or user evidence, inspect missing glyphs, keyboard/touch names and actual focus/hit regions. Replace the ambiguous glyph or revise family rules, rerender, then map every used action to its exact implementation. |

**Retained execution record:** Action/meaning → glyph ID → library version/import or SVG path → viewBox/optical size/offset/stroke → color role → visible/accessibility label → state treatment → file/instance → board/input evidence.

The craft methods below supply the choices and construction detail for this workflow.

Read when selecting icons or when labels/affordances are unclear. Start from
the action meaning and platform convention. Prefer a coherent existing family;
verify each glyph exists and remains legible at the intended size.

Develop a small family around real actions before selecting dozens of glyphs.
For an unfamiliar concept, compare a familiar object metaphor, a direct action
symbol and a labeled treatment where useful. Ask what each could be mistaken for;
one icon should carry one concept. A beautiful ambiguous symbol is a poor control.

Choose a common silhouette/detail level, stroke and terminal treatment, corner
character, perspective and negative-space rhythm. Test a few unequal shapes beside
real text and alongside each other at the actual size. Correct optical weight and
centering rather than forcing identical geometry. Custom identity marks can be
more expressive than operational icons; define that role distinction deliberately.
A selected appearance should alter emphasis while keeping identity recognizable.

Retain role, glyph/source, optical size, stroke/weight, label and active-state
treatment in the component map. Match optical weight, alignment and spacing to
adjacent text rather than blindly making all bounding boxes identical. A custom
product symbol can coexist with standard action icons when its role is clear.
Filled/outline variants may communicate selection consistently; brand marks
and user content have different purposes from navigation icons.

Visible labels support unfamiliar, consequential or ambiguous actions. Accessible
names are required even when a familiar icon can stand alone; tooltips supplement
recognition rather than being the only way to understand a control. Test touch
and keyboard, actual hit area, selected meaning without color, and zoom.

Emoji are user content when the product treats them as content; preserve that
meaning. Do not use an arbitrary emoji set to stand in for a designed navigation
system. Verify source/license and renderer consistency; avoid adding a full icon
dependency when the existing system or a few coherent local shapes suffice.

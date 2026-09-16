# Design Floor — build and inspect

Load for visual implementation or review after a direction or bounded probe brief
exists. The Product Experience Model, Design Proposition, Foundation, applicable
platform conventions and exact tokens own the design. This file supplies
non-negotiable integrity and a contextual craft check; it is not a house style.

## Contextual Density and Intent-Driven Spatial Floor

A prototype is neither an abstract wireframe nor a toy. Craft requires intentional density
calibrated to the user's operational mode, avoiding both uninformative emptiness and claustrophobic clutter:

1. **High-Frequency & Operational Contexts (Legible Benchmarks)**:
   - When surfaces support operational monitoring, financial analysis, or system telemetry,
     metrics and sparklines must provide necessary reference anchors (scale bounds, thresholds,
     gridlines, or event annotations). Do not render unanchored naked data without contextual meaning.

2. **Focused Reading, Creative & Reflective Contexts (Active Negative Space)**:
   - When surfaces support deep writing, long-form reading, or creative immersion, spacious
     negative space is a primary functional deliverable. Do not inject artificial cards,
     metrics, or auxiliary sidebars into a contemplative workspace merely to fill pixels.

3. **System Topology & Relational Structures**:
   - Relational and architectural views must convey authentic causality: directional flow,
     explicit hierarchy, and status relationships, rather than isolated, disconnected boxes.

4. **Visual Self-Inspection Loop (Inspect Before Declaring Verified)**:
   - Inspect rendered screenshots across contracted viewports. If the composition appears
     mechanically broken, accidentally barren (unintended voids due to missing context), or
     arbitrarily congested, Builder must refactor markup and styles in-place before declaring `verified`.

## Non-negotiable integrity and closure invariants

- Do not invent product objects, data attributes, permissions, outcomes, policies
  or capabilities.
- Do not silently replace approved design, interaction or token decisions.
- Do not report an unrun interaction, inaccessible evidence or failed check as
  verified.
- **Reachable-Control Closure Invariant (Zero Leaks)**:
  Every visible, enabled action, modal backdrop, escape key, drawer dismiss, or reset
  trigger must cleanly restore state without leaking orphan overlays, frozen inputs,
  unhandled promises, or mutated unsubmitted drafts. A single broken exit branch
  blocks `verified` unconditionally.
- **Physical Metaphor & Kinetic Accountability**: Where a component claims a physical, optical, biomorphic or domain tool mapping, the implementation must genuinely express the stated phenomenon through observable interactive or visual behavior. Hollow cosmetic styling that merely names a metaphor without enacting it fails the Floor. Interactive buttons and levers must implement tactile feedback (`:active { transform: scale(0.97); }`) and natural deceleration curves (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Zero Inline Hex Rule (Token Inheritance Discipline)**: Prototypes must derive all colors, spacing, radii, and transitions from inherited CSS variables (e.g. `var(--color-primary)`). Hardcoding raw Hex values (`#ffffff`, `#000000`) or raw pixel dimensions in markup is strictly prohibited.
- **Touch Ergonomics Floor**: All interactive controls for mobile viewports must enforce a minimum touch target of `44x44px` (`min-h-[44px] min-w-[44px]`) with adequate tap clearance.
- Do not trade away readable contrast, keyboard access, visible focus, necessary
  status, consequence or recovery information for visual effect.
- Do not use empty generator filler such as “Lorem ipsum”, “Card 1” or “Title goes
  here”. Use **schema-faithful, explicitly synthetic fixtures** with realistic
  content shape, ranges and edge cases. Never imply that invented telemetry,
  names, metrics or timestamps came from production.

## Inspect craft in context

Inspect actual rendered output at contracted viewports and representative content
ranges. Ask whether each choice serves the product thesis, current task, platform
and selected Signature Relationship:

- **Hierarchy and composition:** reading order, grouping, density, disclosure and
  action emphasis follow decision priority. Containers have a job; neither cards
  nor cardlessness is a quality signal.
- **Typography and content:** actual fonts/scripts, role contrast, measure, line
  breaking and rhythm remain legible with long, narrow, multilingual and enlarged
  content. Tight or open tracking, large or restrained scale and mono or expressive
  faces are contextual choices.
- **Color, imagery and iconography:** canvas, content, actions, statuses, imagery
  and symbols form one understandable emotional and semantic system. Quiet,
  monochrome, dark, light, vivid and low-material treatments are all eligible.
- **Components and material:** affordance, target size, input method, frequency and
  consequence determine shape, containment and feedback. Flat controls may be
  excellent; depth, borders, blur or tactile motion require a purpose.
- **Feedback and motion:** response is timely, state truth remains visible and any
  continuity or expression helps comprehension. Immediate cuts and restrained
  motion are valid. Provide the applicable reduced-motion behavior.
- **Responsive transformation:** topology and priority adapt rather than merely
  shrink. Inspect clipped regions, long values and preserved context. For high-density
  spatial/graph visualizations under narrow viewports (<=390px), restructure layout into
  stacked status lists rather than compressing 2D canvas nodes to unreadable margins.

Contrast meets the applicable accessibility baseline: normally 4.5:1 for normal
text and 3:1 for large text. For applicable controls, states and meaningful
graphics, identify the visual cue they rely on and measure it against its actual
adjacent color; do not count decorative separators as required information. See
[WCAG non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).
Landmarks, headings, names and focus order must expose usable structure.

## State coverage follows lifecycle and risk

Derive states from the actual object lifecycle, service behavior, permissions,
latency, destructive consequences, content ranges and specified journeys. A
surface needs every **applicable** state, not a universal matrix. Typical questions
include:

- What exists at first use, after filtering or after prior work?
- Can the operation wait, partially complete, fail, retry or be interrupted?
- Can content overflow, localize, conflict or arrive late?
- Can authority or a prerequisite make an action unavailable?
- What must survive navigation, refresh or return?

Record each required state with its source/risk and each excluded state with a
scope reason. Do not invent loading, empty, disabled or error scenes for a static
or synchronous surface merely to fill a checklist. Conversely, a happy-path view
cannot hide a supported failure or interruption.

Expose test states through the least intrusive mechanism supported by the current
prototype—fixture selection, route, URL parameter, harness API or another explicit
adapter. Test controls and provenance belong in evidence tooling unless the
product itself requires users to see them. Do not insert a floating developer
badge, visible AI label or review control into the product UI by default.

## Evidence and disposition

Check product-specific assertions against actual output with
`pass | fail | unverified | n/a`, including the observation and evidence path.
An unrun check is `unverified`; `n/a` needs a scope reason. Screenshots establish
appearance only, and source inspection does not establish rendered or interactive
behavior. A required failure blocks verified acceptance until implementation is
repaired or the owning design decision is explicitly revised.

Use [quality review](quality-bar.md) for design corrections. Builder owns bounded
execution repair and evidence receipts; Critic evaluates design merit and
conformance separately and never creates approval.

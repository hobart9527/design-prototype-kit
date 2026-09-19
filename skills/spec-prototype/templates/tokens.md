# Design Tokens

> Machine-readable projection of the frozen Foundation design language. Generated when Foundation is frozen; never edited directly. Foundation revision owns all values — update Foundation, then regenerate this file.

## Identity

- Foundation revision:
- Tokens revision:
- Generated at:
- Status: `draft | frozen | superseded`

---

The tables below are a starting schema, not a required palette or component set.
Trim, rename or extend roles to match the approved design language and actual platform.
Standard semantic roles (`--color-surface`, `--color-primary`, `--font-body`, etc.) serve routine platform UI. Where the design language derives from a specific physical substrate, optical phenomenon, or biomorphic pattern, declare dedicated domain tokens (e.g. `--substrate-absorbance`, `--bioluminescence-glow`, `--kinetic-damping`, `--detent-snap-distance`) rather than stretching generic UI tokens into metaphorical shapes.
A separate display/mono face, pill radius, multiple shadows or four breakpoints
is not mandatory. Numeric comparison can use tabular figures in a suitable text
face; motion and raised surfaces need a real role. Do not invent values or features
to fill unused rows. Retained token values must still be exact and reproducible.

## Presets and Baselines

Select one primary baseline to bootstrap realistic tokens, then adapt:
- **Dense Workbench**: base unit `4px`, high contrast, tabular mono figures, compact elevation (`--space-1: 4px`, `--space-2: 8px`, `--radius-md: 4px`).
- **Immersive Web**: base unit `8px`, spacious paddings, fluid elevation, vibrant interactive accents (`--space-2: 8px`, `--space-4: 16px`, `--radius-md: 8px`).
- **Editorial Reading**: fluid rhythm, fixed measure (68ch), relaxed leading, zero distraction (`--space-3: 12px`, `--space-6: 24px`, `--font-body: Newsreader, Inter, serif`).
- **Touch-First Mobile / Consumer**: base unit `4px`, thumb-zone touch targets (`--touch-target-min: 44px`), tactile press scale, spring kinetics, subtle ambient glow (`--space-4: 16px`, `--radius-md: 12px`, `--radius-lg: 20px`, `--spring-response: 300 / 25 / 1`).

## Color

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | | Primary actions, key interactive states |
| `--color-primary-hover` | | Hover state of primary |
| `--color-secondary` | | Secondary actions, accents |
| `--color-surface` | | Page/panel background |
| `--color-surface-raised` | | Card, popover, elevated surface |
| `--color-surface-overlay` | | Modal, sheet, drawer background |
| `--color-border` | | Default border |
| `--color-border-strong` | | Emphasis border, divider |
| `--color-text-primary` | | Body text, primary labels |
| `--color-text-secondary` | | Supplementary text, metadata |
| `--color-text-disabled` | | Disabled controls and copy |
| `--color-text-on-primary` | | Text on primary color background |
| `--color-error` | | Error states, destructive actions |
| `--color-success` | | Success states, confirmation |
| `--color-warning` | | Warning states |
| `--color-focus-ring` | | Keyboard focus outline |

Project-specific color tokens:

| Token | Value | Usage |
|---|---|---|
| | | |

---

## Typography

| Token | Value | Usage |
|---|---|---|
| `--font-display` | | Display headings (h1, hero) |
| `--font-body` | | Body text, UI copy |
| `--font-mono` | | Code or deliberately chosen monospaced roles |
| `--text-display` | size/line-height | Page-level headings |
| `--text-heading` | size/line-height | Section headings |
| `--text-subheading` | size/line-height | Sub-section, card titles |
| `--text-body` | size/line-height | Default body text |
| `--text-small` | size/line-height | Captions, metadata, labels |
| `--text-mono` | size/line-height | Applicable monospaced text |
| `--tracking-tight` | | Display and heading tracking |
| `--tracking-normal` | | Body tracking |

---

## Spacing

Base unit:

| Token | Value | Usage |
|---|---|---|
| `--space-1` | | Micro: icon gap, inline padding |
| `--space-2` | | Tight: compact element spacing |
| `--space-3` | | Default: form field gap, list gap |
| `--space-4` | | Comfortable: card padding, section gap |
| `--space-6` | | Generous: section separation |
| `--space-8` | | Layout: column gap, major section |
| `--space-12` | | Page: top-level vertical rhythm |

---

## Radius

| Token | Value | Usage |
|---|---|---|
| `--radius-sm` | | Badges, tags, small controls |
| `--radius-md` | | Cards, inputs, buttons |
| `--radius-lg` | | Modals, drawers, panels |
| `--radius-full` | | Pills, avatars |

---

## Shadow / Elevation

| Token | Value | Usage |
|---|---|---|
| `--shadow-sm` | | Subtle lift: cards, dropdowns |
| `--shadow-md` | | Elevated: modals, popovers |
| `--shadow-lg` | | High elevation: dialogs |

Elevation rule: use the approved Foundation and platform conventions; explain the semantic role of raised surfaces.

---

## Motion

| Token | Value | Usage |
|---|---|---|
| `--duration-instant` | | State changes with no perceptible delay |
| `--duration-fast` | | Micro-interactions, hover |
| `--duration-normal` | | Panel open/close, page transitions |
| `--duration-slow` | | Complex reveals, onboarding |
| `--ease-out` | | Default: elements entering view |
| `--ease-in-out` | | Elements moving between positions |

Motion rule: specify purpose, timing and reduced-motion behavior from the approved Foundation; zero decorative motion is valid.

Spring roles are optional and only for runtimes that configure springs directly;
the [Motion method](../references/02-craft-methods/interaction-power.md#motion-as-feedback-continuity-and-expression) owns the choice
and the parameter conventions.

| Token | Value | Usage |
|---|---|---|
| `--spring-settle` | stiffness / damping / mass | Continuity where a settling tail adds meaning |
| `--spring-response` | stiffness / damping / mass | Fast, interruptible control response |

---

## Breakpoints

| Token | Value |
|---|---|
| `--bp-mobile` | |
| `--bp-tablet` | |
| `--bp-desktop` | |
| `--bp-wide` | |

---

## Export

The tables above are the human-readable projection. When a build step, design
tool or downstream repository needs the same roles, export them to the stack's
token file in the [W3C Design Tokens format](https://tr.designtokens.org/format/)
(`$value`/`$type`); follow [artifact lifecycle](../references/04-governance/artifact-lifecycle.md)
for the bounded export command, revision paths and preservation rules. Keep one role naming system and
keep value ownership with the Foundation revision — exporting does not move it.

---

## Verifiable assertion anchors

Token values referenced in Foundation's Verifiable Design Assertions. Builder uses these to run pass/fail checks against actual output:

| Assertion | Token | Expected value | Check method |
|---|---|---|---|
| Approved action color | `--color-primary` | Exact retained token | Inspect computed CSS |
| Contrast AA minimum | `--color-text-primary` on `--color-surface` | ≥4.5:1 | Browser contrast check |
| Readable text and content fit | `--text-body` | Scoped Foundation value at contracted viewports | Inspect rendered content |
| | | | |

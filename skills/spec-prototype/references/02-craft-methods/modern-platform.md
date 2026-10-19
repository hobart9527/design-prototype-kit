# Modern Platform Techniques

Use this reference when the brief, selected direction, or target viewport benefits
from a modern platform capability. These techniques enhance the five sensory axes;
they do not create a second design system or override the product's topology. Treat
techniques in this file as challenger candidates only: they may inform an authored
candidate, but they do not define direction-comparison axes or become default scoring
criteria. Direction axes come from the product tension and its evidence.

| Condition | Read | Rule |
|---|---|---|
| Heading wrap, fluid type, or multilingual typography matters | Typography | `CRAFT-TEXT-WRAP`, `CRAFT-FLUID-TYPE`, `CRAFT-CJK-TYPESET` |
| Custom fonts are part of the committed direction | Font loading | `CRAFT-FONT-LOADING` |
| The surface is full-height or reflows by component width | Adaptive layout | `CRAFT-VIEWPORT-UNITS` |
| The direction benefits from a state-preserving transition | Motion | `CRAFT-VIEW-TRANSITION`, `CRAFT-HAPTIC-PAIRING` |
| The brief spans lighting conditions or explicit theme choice | Color | `CRAFT-DARK-MODE`, `CRAFT-TOKEN-ONLY` |

## Platform enhancement contract

Modern CSS is an enhancement, not a dependency. Keep the task path and its state
change available without the enhancement; gate newer syntax with `@supports` or
feature detection where support is uncertain; and pair motion with the existing
`prefers-reduced-motion` floor. A browser limitation is recorded as unmeasured,
not treated as a pass or a design defect.

## Typography

- Use `text-wrap: balance` for short headings and `text-wrap: pretty` for running
  text where it improves line endings. These are advisory; do not force them on
  labels or dense operational data.
- Use a fluid type scale where the surface changes viewport size. Existing
  `CRAFT-FLUID-TYPE` covers `clamp()`/`min()`/`max()`; named `--step-*` tokens are
  useful when several roles share the same scale, not mandatory for a single size.
  `compile_tokens.py` supports an opt-in modular clamp scale (`--type-scale clamp`)
  emitting `--step--1` through `--step-5` interpolating between 390px and 1280px;
  downstream sync checks inherit the sealed choice automatically.
- Load a chosen local font with `font-display: swap` (or a direction-appropriate
  fallback strategy) so a failed or delayed font never hides content. Do not add a
  font merely to appear distinctive.
- For `zh`/`ja`/`ko`, select a locale-appropriate stack with `:lang()` and consider
  `text-spacing-trim`, `text-autospace`, and `line-break` only behind
  `@supports`. Browser support varies; treat static detector hits as leads, not
  proof that punctuation or line breaking renders correctly.

## Color and theme

- Derive interaction states from semantic tokens. `color-mix(in oklch, …)` can
  preserve perceptual hue while deriving hover/selected/disabled colors, but check
  contrast after compositing and keep a fallback declaration when the target
  browser set requires it.
- For fine hairline dividers that cross layered surfaces (`bg-void` → `bg-surface` →
  `bg-surface-raised`), a low-alpha foreground mix (e.g. `color-mix(in oklch, var(--text-primary) 8%, transparent)`)
  or semi-transparent border paired with top-edge `--surface-sheen` adapts optical
  contrast naturally. Do not use decorative low-contrast hairlines as the sole
  boundary for interactive controls or focus rings, which must meet WCAG contrast floors.
- Dark mode is not a mathematical inversion. Preserve hierarchy by retuning
  elevation, neutral surfaces, and saturation. Adapt only when the use scene or
  brief asks for multiple lighting conditions; a committed single-scheme product
  is valid.
- Do not emit a second primitive palette or write raw colors into component rules.
  `compile_tokens.py` remains the token authority; OKLCH output, modular clamp
  scale, and paired `light-dark()` token sets are implemented opt-ins
  (`--color-format oklch`, `--type-scale clamp`, `--color-schemes light-dark --dark-source <path>`)
  whose default output stays byte-for-byte stable and whose sealed options are
  inherited during freshness verification.

## Adaptive layout

- Use `@container` when a component's available width, rather than the viewport,
  determines its composition. Keep a viewport fallback for the page shell.
- `:has()` and subgrid are optional tools for relationships and shared tracks;
  use them when they simplify the owning layout, not as capability checkboxes.
- Prefer `dvh`/`svh`/`lvh` for full-height mobile surfaces and `scrollbar-gutter:
  stable` when scrollbar appearance would shift aligned content. Provide a fallback
  for older browser targets.
- Recompose at narrow widths; do not shrink type or hide a critical action to make
  a desktop layout fit. The responsive floor remains in `craft-floor.md`.

## Motion and micro-interactions

- A View Transition may preserve spatial continuity between related states.
  Feature-detect `document.startViewTransition`; update the actual application
  state even when the API is unavailable. Respect `prefers-reduced-motion` by
  removing or substantially shortening the transition.
- Scroll-driven animation is appropriate only when movement communicates reading
  or spatial progress. It must not be required to reveal controls or complete a
  task. Gate it with `@supports (animation-timeline: scroll())` and retain the
  static composition as the fallback.
- `@starting-style`, `transition-behavior`, and `interpolate-size` are optional
  polish for entering/exiting or intrinsic-size states. Do not make hidden state
  reachable only through animation.
- Haptics (`navigator.vibrate`) are optional, transient reinforcement. Pair them
  with visual and accessible status feedback; headless capture cannot validate a
  physical haptic and must record it as unverified.

## Detection status

`detect.py` is a shallow source detector. A `hit` means a pattern was found, not
that the browser rendered it correctly. A `clear` means the scanned sources did
not contain the pattern, not that the design is defective. Unresolved local CSS
links are reported separately and prevent a clean interpretation of source-only
findings. Human visual and task review remain authoritative.

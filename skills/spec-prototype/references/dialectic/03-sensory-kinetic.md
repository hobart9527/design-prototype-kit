# Dialectic Slice: Sensory & Kinetic Imprint (Frontier 3)

> Dynamic projection module for Material Substrate, Domain Palette Discipline & Kinetic Imprint.
> Load strictly during Round 3 of Stage 1 co-creation.

## 1. Prerequisites Check
- Verify Round 2 (Topology & Resistance) is settled.
- Ground material substrate and kinetic response in the established physical metaphor.

## 2. Material Substrate & Atmospheric Undertone (5-Axis: Materiality)
Project 2 tangible sensory moodboards with exact chromatic undertones:
- **Substrate A: Void Slate & Obsidian (哑光冷玄岩)**
  - *Base*: `#101418` (deep cold rock), hairline borders (`rgba(255,255,255,0.08)`).
  - *Feel*: Zero floating shadow, surgical calm, instrumentation console.
- **Substrate B: Organic Bone & Ink (暖白厚纤维纸)**
  - *Base*: `#F7F6F3` (warm off-white), deep charcoal text (`#1A1D20`), diffuse ambient undertone.
  - *Feel*: Legal codex, editorial dignity, high readability under daylight.

## 3. Domain Color Discipline & Negative Declarations (9-Pillars: Color Semantics)
Define the Signature Accent and its absolute negative boundaries:
- **Signature Hue**: e.g., Authentic Cinnabar (`--accent-seal: #B3352B`).
- **Negative Boundary (绝对负向清单)**:
  - Routine functional primary actions use neutral slate (`--action-primary: #334155`).
  - DRAFT and PENDING stages are PERMANENTLY FORBIDDEN from rendering cinnabar.
  - Cinnabar strikes ONLY at the final authority gate, seal imprint, or zero-tolerance collision.

## 4. Kinetic Timing & Decisive Exchange 3-Frame (5-Axis: Energy)
Specify the physical response of the decisive commit action:
- *Timing*: Fixed duration (e.g. 160ms mechanical press, `cubic-bezier(.16, 1, .3, 1)`).
- *Frame 1 (Intent)*: Pointer/key triggers tactile depression (`:active scale(0.98)`).
- *Frame 2 (Commit)*: Immediate state freeze; prevents double submission.
- *Frame 3 (Settlement)*: Badge transitions deterministically; focus deterministically restores to originating trigger.

## 5. Orthogonal 4-Axis Craft Stack (Physical Anchor Mapping)
Translate the settled substrate and anchor metaphor into four orthogonal craft axes
compiled into `foundation.craft_stack` (and projected into `visual_directives.craft_stack`):
- **surface_optics** — from the substrate choice in Section 2: Void Slate reads as
  `coated_instrument_dark` (specular top edge via `--surface-specular`); Organic Bone
  reads as `matte_pigment_wash` (tonal `--surface-tint` over warm paper).
- **spatial_geometry** — from the metaphor's massing: default `soft_bento_pill`
  (generous bento padding, pill-shaped triggers via `--radius-pill`).
- **micro_typography** — from the instrument dial anchor: default
  `tight_display_polarized` (`--font-display-tracking: -0.04em`,
  `--font-display-weight: 800`, `font-variant-numeric: tabular-nums`).
- **data_marks** — from the physical texture anchor: default `hatching_dither`
  (SVG `--pattern-hatch-45` hatching or segmented bars for status/metrics).
Explicit `surface_optics: ...`-style declarations in the 5-Dial register override
these compiled defaults.

## 6. Ratchet Settlement
Lock `--accent-seal`, substrate tokens, craft stack axes, and kinetic timing. Proceed to Frontier 4.

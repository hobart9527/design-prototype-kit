# Proposal: Integrate Orthogonal 4-Axis Craft Stack into Spec-Prototype

## Why

The current spec-prototype Nine Pillars and Five Axes ontology provides rigorous product architecture and macroscopic domain reasoning, but its translation into executable CSS suffers from a severe "semantic gap". When generating prototypes without external reference images, builders regress toward generic gray-and-white enterprise templates. To enable self-generated prototypes with modern high-craft design (soft bento layouts, tight display micro-typography, tonal surface washes, and tactile data markings) without collapsing into rigid monolithic templates or discarding architectural grounding, the system requires an orthogonal 4-axis modern craft stack (`surface_optics`, `spatial_geometry`, `micro_typography`, `data_marks`) bridging Nine Pillars Expression and Interaction to micro-physical code synthesis.

## What Changes

1. **Schema & IR Bridge**:
   - Update `skills/spec-prototype/schemas/prototype-spec.v1.json` to define `craft_stack` under `foundation`.
   - Update `skills/spec-prototype/scripts/compile_spec_ir.py` to parse authored or infer orthogonal craft axes into `canonical_ir.visual_directives.craft_stack`.
   - Update `skills/spec-prototype/scripts/assemble_envelope.py` to propagate craft directives into the Builder execution envelope.

2. **Token & Craft Derivation**:
   - Enhance `skills/spec-prototype/scripts/compile_tokens.py` to generate fine-grained CSS tokens: tonal surface washes (`--surface-tint`), specular highlights (`--surface-specular`), tight display tracking (`--font-display-tracking`), and SVG geometric hatching data URIs (`--pattern-hatch-45`).

3. **Builder & Critic Directives**:
   - Update `skills/spec-prototype/agents/spec-prototype-builder.md` with explicit micro-craft code recipes: tight display tracking for key metrics, soft bento container geometry, and tactile data markings.
   - Update `skills/spec-prototype/agents/spec-prototype-critic.md` with anti-generic visual checks to catch unstyled gray-box compositions.

4. **Dialectic Guidance**:
   - Update `skills/spec-prototype/references/stages/stage-1-frame.md` and `skills/spec-prototype/references/dialectic/03-sensory-kinetic.md` to map Stage 1 physical reality anchors directly to orthogonal craft stack axes.

## Non-Goals

- Replacing Nine Pillars or Five Axes ontology
- Hardcoding rigid monolithic template bundles
- Removing Stage 1 physical anchor exploration
- Breaking existing canonical IR schema validation for legacy slices

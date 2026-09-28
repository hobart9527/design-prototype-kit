# Dialectic Slice: Falsification & Compile (Topic)

> Dynamic projection module for 5-Second Falsification, Stress Boundary & Automated Compilation.
> A selectable Stage 1 method topic: load it when Resilience & Gate is the
> active uncertainty, in any order alongside the other topics.

## 1. Entry Check
- This topic is selectable, not sequenced: no other topic must settle first.
- Work from whatever axis and pillar values the product has actually settled;
  any value still open stays labelled as such rather than being invented.

## 2. 5-Second Perceptual Falsification Criteria
Every Stage 1 closure MUST establish at least one falsification test for the Stage 2 Hero Probe:
- *Criterion*: "If an operator cannot distinguish between an uncommitted draft and a sealed authority version within 5 seconds of viewport scanning, the design direction is falsified."
- *Metric*: Documented in r1.md as a primary verifiable design assertion.

## 3. Four-Dimensional Reality Breakers (The Break Protocol)
Specify concrete test vectors:
- **Unbreakable String**: Long compound path/title without overflow.
- **Zero-Item Empty State**: Actionable empty state with recovery path.
- **320px Viewport Fold**: Minimum viewport reachability.
- **Rapid Double Activation**: Idempotent state lock.

## 4. Single-Direction Contract Compilation Trigger
Do NOT write Markdown files manually. Execute:
```bash
python3 skills/spec-prototype/scripts/compile_spec_ir.py --slice <slice-id>
python3 skills/spec-prototype/scripts/compile_tokens.py
```
Verify pipeline:
1. `r1.spec.json` compiled and schema-validated (canonical machine IR).
2. `r1.spec.md` rendered as the single-file human RFC view.
3. `tokens.css` compiled with domain tokens preserved (plus `t1.json`).
4. Stage 1 lifecycle advances to `sealed_provisional`.

**Banned in Primary Delivery**:
NEVER write legacy fragmented contracts (`f1.md`, `m1.md`, `t1.md`, `c1.md`, `r1.md`, `product.md`). The single unified RFC specification is `r1.spec.md`.

## 5. Design Brief Format (`google-design-md/v2`)

For formal slices, use the concise parser-compatible format documented in
[`../spec-md-contract.md`](../spec-md-contract.md). It is Skill-owned and inspired by
Google Design.md; it is not an official Google schema and does not prescribe Material
Design. Use YAML frontmatter only for stable compiler metadata, then author the
product-specific design in semantic Markdown sections. Include only applicable
contract details; never populate speculative fields for checklist completeness.

The compiler consumes the existing semantic headings and field forms. If a format
change is needed, update the compiler and its tests rather than reverse-engineering
it with ad-hoc scripts.


```markdown
---
spec_schema: "google-design-md/v2"
slice_id: "<slice-id>"
authority: "sealed_provisional"
stage: "hero_probe"
viewports: [390, 1280]
required_states: [state-draft, state-sealed]
tokens_ref: "prototype/shared/tokens.css"
primary_surface: "<primary-surface-id>"
---

# Surface Specification: <Product Name>

## 1. Problem Framing & Drivers
- **Core Tension**: <Core Tension A> vs <Core Tension B>
- **Reality Anchors**: Adopt <benchmark> / Refuse <anti-pattern>
- **Ruthless Omissions**: 1. <Omission 1> 2. <Omission 2> 3. <Omission 3>

## 2. Experience Foundation & Five Axes
- Density: dense | Energy: kinetic | Materiality: coated_instrument_dark | Rhythm: fluid | Character: technical
- --bg-void: #0b0f10
- --bg-surface: #121719
- --accent-primary: #38bdf8

## 3. Spatial Anatomy & Surfaces
- **主工作区 (Primary)**: `surface/<id>`
- **上下文抽屉 (Contextual)**: `surface/<id>`
- **移动扫视图 (Glance)**: `surface/<id>`

## 4. State Models & Action Lifecycle
- `domain/<state-id>`: 一句话语义描述
- `interaction/<state-id>`: 一句话交互描述
- `data/<data-id>`: 真实数据场景说明

## 5. Resilience, Reality Breakers & Invariants
- `stress/<fixture-id>` | Vector: <破坏性输入> ➔ Expected: <预期自愈与容错行为>
- `inv/<id>` | <不变量描述> | severity: blocking | verif: dom_query
```

Legacy section headings (`Stage 1 §1`, `Stage 1 §3`, `Stage 1 §5`, `Stage 1 §8`) remain fully supported for backwards compatibility.

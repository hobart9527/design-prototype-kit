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

Legacy compatibility only: `materialize_contracts.py --slice <slice-id> --phase all`
still emits the multi-file `c1.md` / `r1.md` set for backwards-compatible readers;
it is not the canonical compilation path.

## 5. Canonical Discussion Contract Schema (规范契约与 Google Design.md 标准)

Preferred Standard: Follow the Google Design.md Architecture defined in [`../spec-md-contract.md`](../spec-md-contract.md).
Using standard YAML Frontmatter and semantic sections completely eliminates compiler reverse-engineering:

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

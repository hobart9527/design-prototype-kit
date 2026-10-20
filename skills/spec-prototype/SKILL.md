---
name: spec-prototype
description: "Canonical 5-Stage Design Delivery Engine for UI/UX experience design, information architecture, interactive prototypes, design tokens, and aesthetic reviews. Triggers on: '/spec-prototype', UI/UX design, interactive prototype, design system, tokens, IA, design audit, 'UI设计', 'UX设计', '原型设计', '交互设计', '设计系统', '设计规范', '体验走查', '界面重构'. NEGATIVE TRIGGERS (DO NOT invoke): pure backend code, database schema migrations, production bug fixes, or applying approved code changes in Loom delivery."
license: MIT
metadata:
  author: design-prototype-kit
  version: "10.2.0"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash|Agent|Task"
      hooks:
        - type: command
          command: 'python3 -c "import os, sys, subprocess; f = [p for p in [\".claude/skills/spec-prototype/scripts/execution_boundary.py\", \"skills/spec-prototype/scripts/execution_boundary.py\", os.environ.get(\"LOOM_CLAUDE_HOME\", os.path.expanduser(\"~/.claude\")) + \"/skills/spec-prototype/scripts/execution_boundary.py\"] if os.path.isfile(p)]; sys.exit(subprocess.run([sys.executable, f[0]]).returncode if f else 0)"'
  PostToolUse:
    - matcher: "Write|Edit|MultiEdit"
      hooks:
        - type: command
          command: 'python3 -c "import os, sys, subprocess; f = [p for p in [\".claude/skills/spec-prototype/scripts/execution_boundary.py\", \"skills/spec-prototype/scripts/execution_boundary.py\", os.environ.get(\"LOOM_CLAUDE_HOME\", os.path.expanduser(\"~/.claude\")) + \"/skills/spec-prototype/scripts/execution_boundary.py\"] if os.path.isfile(p)]; sys.exit(subprocess.run([sys.executable, f[0]]).returncode if f else 0)"'
---

# Spec Prototype — Principal Design Delivery Engine

Act as a principal product designer: identify the consequential tension shaping the product,
explore polarized hypotheses, make an authentic physical artifact, inspect the render with
trained aesthetic judgement, and extract the durable contract from what was built.

Read [the core kernel](references/core-kernel.md) on every entry (Spec as durable contract,
prototype as disposable proof, authority lifecycle, and experience invariants: visual exploration and rapid prototyping precede formal contract compilation). Beyond it,
load only what the active stage cites, plus [`execution-boundary.md`](references/04-governance/execution-boundary.md)
before the first write. Fact-finding belongs to repository facts and user brief, never Skill prose.

## Entry Intent & Adaptive Routing (意图优先，资产为证)

| Intent | Route |
|---|---|
| **Explore** — alternatives, visual direction, falsifiable probe | Bounded direction probe or multi-direction slots (`dirs/{a,b,c}`) |
| **Specify** — durable contracts, IA topology, tokens, handoff | Stage 5 contract compilation and handoff packet freeze |
| **Prototype** — runnable screen, state machine, interaction | Build directly in HTML/CSS; extract Spec upon handoff |
| **Review / repair** — critique, benchmark audit, in-place delta | Targeted visual review and in-place delta; preserve lineage |

Workspace assets are contextual evidence after intent classification: existing assets select
inherited tokens and scope; they never force a bureaucratic full pipeline or authorize production
edits. Context labels: **Archetype A: Greenfield 0-to-1**, **Archetype B: New Surface 1-to-N**,
**Archetype C: Refinement & Audit**.

**Negative trigger boundary.** Never invoke for pure backend code, database migrations,
production bug fixes, or approved code delivery under Loom (`loom delivery step`).

## Design Mindset & Core Principles (主任设计师心智模型)

### 1. Familiar Conventions & Signature Moment
Keep the user's existing mental models for navigation, spatial expectations, and
system metaphors so no basic affordance has to be re-learned. Concentrate novelty
on the relationships that resolve the slice's **Signature Moment** (the defining,
memorable interaction that proves the product's unique value proposition). This is
a heuristic, not a quota: a restrained, static, ordinary form can be the optimal
answer when the task calls for it.

### 2. Tension Spectrum over Static Modes (连续张力谱系)
Do NOT treat product archetypes as static template checkboxes (e.g. "dark dashboard" or "clean blog").
Calibrate where the product sits on these continuous tension axes:
- **Operate Tension** (Throughput vs. Cognitive Overload): high-density terminal layout or progressive disclosure command palette.
- **Read Tension** (Immersive Focus vs. Structural Scannability): editorial continuous stream or multi-pane semantic navigational anchors.
- **Persuade Tension** (Value Clarity vs. User Skepticism): interactive runnable sandbox proof vs. static marketing assertions.
- **Experience Tension** (Spatial Freedom vs. Orientation Clarity): infinite canvas fluidity vs. structured contextual rails.

### 3. Anti-Slop Aesthetic Red Lines (反烂俗设计铁律)
The red-line rules and their direction-earned exceptions are owned by
[`craft-floor.md`](references/02-craft-methods/craft-floor.md); read that owner at
Turn 2 before the first runnable write. This section does not restate them.

## The Spine: Nine Pillars & Five Axes (设计本体与标尺)

- **Nine Pillars as Analytical Lenses** (Value · Research · Object · Journey · Topology · Attention · Expression · Interaction · Resilience):
  Do not treat the Nine Pillars as an administrative checklist to fill. Select the **2–3 critical pillars**
  carrying the deepest product tension for this slice, explore their dialectic conflicts, and let the rest act as natural constraints.
- **Five Axes as Continuous Sensory Calibration** (Density · Energy · Materiality · Rhythm · Character):
  Sensory coordinates that mathematically calibrate the design into physical `tokens.css` (e.g. Density scales 4px vs 12px grids; Materiality governs border-contrast vs depth elevation). All five axes are accounted for at direction lock: an explicit value with cited evidence, or an explicit `open` with reason.

## Workflow: Frame → Propose → Make → Look → Refine

Stages are not administrative approval gates; execute only the work required by user intent.
Frame = Stage 1, Propose = 2, Make = 3, Look/Refine = 4, **Freeze** = optional Stage 5 handoff.

```text
Turn 1: Frame & Polarized Divergence ──► Turn 2: Direct Make ──► Turn 3: Look, Refine & Deliver
   [2-3 Opposing Hypotheses]                [Runnable Anchor]             [Screenshot Inspection + Handoff]
```

The table below is the **common route, not a fixed order**: Stage 2 (Propose) and
Stage 5 (Freeze) are conditional stages, and the route follows the task's size and
decision state rather than a quota of turns.

### Task-size routing (任务规模路由)

| Task size | Route | What is required / what is skipped |
|---|---|---|
| **局部修改** — a small change to an existing slice | Frame (light) → Make → Look | Not required: Divergence from zero, a fresh Direction Contract, a token re-derivation. Reuse the recorded direction and the existing token layer; probe (Stage 2) and freeze (Stage 5) only on demand. |
| **单 slice 交付** — one new slice in an existing product | Frame → Propose (on demand) → Make → Look → Freeze (on demand) | Stage 2 runs only when the direction is materially undecided after Frame; Freeze only when a frozen/downstream handoff was requested. |
| **绿地 / 新产品** — new product, no inherited language | All five stages: Frame → Propose → Make → Look → Freeze | The default route; Stage 2 and Stage 5 still remain conditional on the decision state and the handoff request. |

| Turn | Milestone & Core Deliverable | Owns |
|---|---|---|
| **1 · Frame & Polarized Divergence** | The core product tension, **at least 2 structurally polarized hypotheses** labelled **`方向 A` / `方向 B`**, a recorded `### Divergence` block, and the full 6-block Direction Contract (THESIS / OWN-WORLD / STORY / FIRST VIEWPORT / FORM / FINISH) plus the Signature Moment line, all `proposed`/`provisional`. Present the rut, candidates, two-axis verdict and recommendation in chat; end with a verbatim `USER-INPUT:` line only while a material direction decision is un-delegated. Turn 1 output is the design record only. The procedure, the presentation list and the stop condition are owned by the stage file. | [`stage-1-frame.md`](references/stages/stage-1-frame.md) |
| **2 · Make** | A runnable anchor (`index.html` + `anchor.css` + `anchor.js`) and compiled `tokens.css`. Prerequisite: all six Direction Contract blocks carry concrete proposed/provisional statements; a missing one is drafted only from recorded evidence. Read `craft-floor.md` and the author-side subsections of `lean-delivery-rules.md` before the first runnable write. Author each file in one whole `Write`, compile tokens, capture the declared viewports, and require zero runtime errors before the turn ends. **No self-authored verification scripts**: such a script is not evidence or an artifact; a `/tmp` debugging script's result is re-verified with `capture.mjs`/`detect.py` before it counts. Commands, the token authoring format and the technique routes are named in the stage file. | [`stage-3-skeleton.md`](references/stages/stage-3-skeleton.md) |
| **3 · Look & Deliver** | Inspect the rendered `.png` captures first and write the design judgment before reading any rule-hit list. Then reconcile detector leads against the render and run the freeze gate: exit 0 pass, 1 fail, 2 degraded — degraded is not a pass. At most one focused in-place refinement per root cause. Zero runtime errors and honest manifest reconciliation bind before any receipt. Receipt, authority and delivery boundaries load now, not earlier. | [`stage-4-audit.md`](references/stages/stage-4-audit.md) |

Routing follows decision state: when the direction is materially undecided after Turn 1, load [`stage-2-probe.md`](references/stages/stage-2-probe.md) before Turn 2 (physical `dirs/a|b` comparison, provisional when unattended); when a direction is authorized or only a local repair is needed, skip Stage 2 and go directly to Stage 3/4.

Load only the stage file your current turn names and its explicitly routed owner sections. At Turn 2, load `craft-floor.md` and the author-side subsections of `lean-delivery-rules.md` before the first runnable write, plus only the applicable `modern-platform.md` subsection when its condition matches. At Turn 3, load the receipt/authority sections of `lean-delivery-rules.md`. Do not preload unrelated stage files or adjacent references "just in case"; routing remains demand-driven.

**Reading discipline (读取纪律).** Read each reference document **once per session** and keep it in context rather than re-reading it per turn. On resume, read only the `## Resume` block of the design record and the current slice's brief — not the whole record — and continue from the declared state. Items that only Turn 3 needs (the receipt/authority sections of `lean-delivery-rules.md`, `handoff.md`) are marked **延后读 (defer)**: do not pull them during Turn 2's Make work; load them when Turn 3 actually writes receipts or when a freeze is requested.

**Stage 3: 拓 (Make scope).** Resolve coverage once before expanding the anchor. [`stage-3-skeleton.md`](references/stages/stage-3-skeleton.md) owns the procedure.

**Coverage Selection:** scope, not approval, and an implementation target only. The full object model and Surface Map stay authoritative; unselected surfaces stay provisional, not deleted; out-of-scope dependencies are disclosed, never silently added. Present concrete recommended combinations (surfaces and flows, what each validates, what is deliberately dropped) plus a full-product option, only while scope is unresolved. Reuse an explicit prior selection; never default to full-product when none exists. Direction probes, spec-only requests and local refinement keep their lightweight routes. The combination fields and the `reconcile_obligations` reconciler semantics are owned by [`stage-3-skeleton.md`](references/stages/stage-3-skeleton.md); this line routes, it does not restate them.

**Structure: Derived** from authentic Surface Topology (Primary · Contextual · Supporting), not a fixed screen count. The freeze/handoff command binds the selected `specifications/<slice_id>/r1.spec.md` when the user requests a frozen handoff.

Budget is turns and wall clock, not paperwork. Apply [refine operators](references/operators.md)
(target axis, from → to, invariant preserved, falsifier) for surgical in-place iterations.

## Minimal Design Record & High-Density Deliverables

Consolidate the design lifecycle into four high-density assets: the decision
source (the design record), the specification source (`r1.spec.md` plus its
compiled Spec IR), the style source (`tokens.css`) and the materialization
source (`experiments/<slice>/anchor/`). The canonical tree, the owner of every
path, and the record layouts that fill it are owned by
[`machine-contract.md`](references/04-governance/machine-contract.md); this
skill names the four roles and does not restate the tree.

**Absolute Refusal List**:
1. NEVER author the retired fragmented contract set or duplicate `prototype/product.md` in the primary delivery flow; the retirement list is owned by [`artifact-lifecycle.md`](references/04-governance/artifact-lifecycle.md).
2. NEVER use `assemble_envelope.py` as an authoring or dispatch stage in the primary delivery flow; it is a legacy/benchmark compatibility helper.
3. NEVER author review portals outside `prototype/review-portal.html`.
4. NEVER loop on visual guesswork or trial-and-error CSS hacks in the primary delivery flow. Read the structured `diagnostics_summary` from `capture.mjs` directly.
5. When authoring the RFC specification, ALWAYS compile via `python3 skills/spec-prototype/scripts/compile_spec_ir.py --slice <slice_id>` so `contracts/compiled/<slice>/r1.spec.json` and `specifications/<slice>/r1.spec.md` arrive together; NEVER author `r1.spec.md` alone by hand.
6. NEVER report a state whose capture failed, has 0 screenshots, or lacks confirmed passing evidence under `## Verified this turn`; it belongs under `## 未验证（不得读作已验证）` / `Limitations`, tagged `[hypothesis]` / `[unverified]`. Owner: [`stage-4-audit.md`](references/stages/stage-4-audit.md) "Manifest cross-check".

The machine-read lists in design records (`contract:states`, `contract:invariants`, `contract:actions`,
`contract:viewports`, `contract:axes`, `contract:craft`, `contract:tokens`, `contract:meso`) are authoritative
YAML blocks that fail closed. Registry and field specs live in [`machine-contract.md`](references/04-governance/machine-contract.md).

## Craft Standards & Non-Negotiable Floors

Make every surface feel intentionally authored for this specific problem space.
[`craft-floor.md`](references/02-craft-methods/craft-floor.md) owns the hard floors —
name them here, read the rule there:
1. `CRAFT-PRESS-DETENT` — perceptible `:active` press feedback on commit controls.
2. `CRAFT-CONCENTRIC-RADII` — concentric nested radius geometry.
3. `CRAFT-TABULAR-NUMS` — tabular numerals for changing or column-aligned numbers.
4. `CRAFT-ACTION-FEEDBACK` — action safety & reversible loop (rule text in [`lean-delivery-rules.md`](references/03-verification/lean-delivery-rules.md)).
5. `CRAFT-TOUCH-TARGET` — mobile touch target minimum; safe-area insets.
6. WCAG 2.2 AA contrast and truthful evidence.

Beyond these ids everything is open design space: direction-selected material and
motion ([`visual-craft.md`](references/02-craft-methods/visual-craft.md)) are
advisory techniques the direction earns, never floors and never a house recipe.

On demand extensions:
- [`mobile-ux.md`](references/02-craft-methods/mobile-ux.md): thumb-zone mechanics, bottom sheet resistance.
- [`ai-native-ux.md`](references/02-craft-methods/ai-native-ux.md): streaming debouncing, confidence cues, human-in-the-loop triggers.
- [`reference-set.md`](references/05-benchmarks/reference-set.md): observable benchmark patterns from real top-tier products.

## Lean Delivery & Token Efficiency (轻量化高质交付)

Hard gates block on semantic fabrication, authority escape, or critical task breaks; the craft floors above are hard and verifier-enforced, while craft performance guidance beyond the floors is advisory. The accumulated negative rules (ergonomics, entity grounding, authority tagging, receipt honesty, lifecycle closure, and the rest) live in [`lean-delivery-rules.md`](references/03-verification/lean-delivery-rules.md). Writer-facing constraints load before the first runnable write in Turn 2; receipt and authority sections load at the start of Turn 3 when receipts are written. Helpers and their flags are listed in [`helper-quick-reference.md`](references/04-governance/helper-quick-reference.md); token authoring format is [`world.tokens.example.md`](templates/world.tokens.example.md). Never read a script's source to learn its calling convention. Scripts run on the stdlib alone except for one prerequisite: `contract:<kind>` blocks need PyYAML (`pip install pyyaml`); the compiler fails closed with a named error when a record carries such a block and the library is missing.

## Single-Brain End-to-End Ownership (单脑贯通 · 极速交付)

The principal designer owns the entire lifecycle directly: framing, code synthesis, visual screenshot inspection,
and downstream contract extraction.
- **Direct Materialization**: Write prototype code directly to `prototype/experiments/<slice>/anchor/index.html` without multi-turn delegation latency.
- **Direct Visual Inspection**: Run `capture.mjs` directly and inspect rendered `.png` viewports with `Read`.
- **Subagents as Optional Tools**: Subagents (`spec-prototype-builder`, `spec-prototype-critic`) exist strictly for detached background explorations or formal external audits when requested by the user—never as mandatory blocking gates on the primary delivery flow. One exception: before a delivery or handoff, an independent Critic review is required; that checkpoint, its scope and its non-approval status are owned by [`quality-floor.md`](references/03-verification/quality-floor.md) "Independent Critic checkpoint". In every other situation the Critic and Builder remain optional.

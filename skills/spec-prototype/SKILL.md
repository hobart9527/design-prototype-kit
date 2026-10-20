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

| Turn | Milestone & Core Deliverable | Owns |
|---|---|---|
| **1 · Frame & Polarized Divergence** | The core product tension plus **at least 2 structurally polarized hypotheses** labelled explicitly as **`方向 A` / `方向 B`** (differing in chassis, mental model, or operating paradigm). Present in chat dialogue: ① category rut (行业固有套路); ② candidate directions with seeds; ③ **两轴裁决** (two-axis verdict explicitly naming Structure as primary axis); ④ recommended direction with rationale; ⑤ end turn with a verbatim `USER-INPUT: <question>` line. The divergence is recorded as a structured `### Divergence` block in the design record. In `world.md` (or `discussion.md`), articulate the full 6-block Direction Contract (THESIS / OWN-WORLD / STORY / FIRST VIEWPORT / FORM / FINISH) for the recommended direction (all rows `proposed`/`provisional`). Unattended runs carry the recommendation as `proposed` + `provisional`, never `confirmed`. Decision status stays `proposed`/`provisional` until explicit user selection. Turn 1 output is the design record only. | [`stage-1-frame.md`](references/stages/stage-1-frame.md) |
| **2 · Make** | A runnable anchor (`index.html` + `anchor.css` + `anchor.js`) and compiled `tokens.css`. Pre-write prerequisites: all six Direction Contract blocks carry concrete proposed/provisional statements in `world.md` (or `discussion.md`); fill a missing statement only from evidence already recorded. Before the first runnable write, read [`craft-floor.md`](references/02-craft-methods/craft-floor.md) and the author-side sections **Interactive Ergonomics**, **Domain Entity Grounding**, and **Precondition** in [`lean-delivery-rules.md`](references/03-verification/lean-delivery-rules.md); their writer constraints bind from this turn, while receipt/authority sections remain for Turn 3. Progressive enhancement: `index.html` must contain authentic domain entities directly in static markup. Compile `tokens.css` with `compile_tokens.py` (includes `::selection`, `caret-color`, scrollbars, and focus rings to eliminate `SLOP-017`). Author each file in one whole `Write`. No self-authored verification scripts (no `flow-check.cjs`): such a script is not evidence or an artifact. A one-off debugging script may live in `/tmp`, but its result must be re-verified with `capture.mjs`/`detect.py` before it counts. Token authoring format comes from [`world.tokens.example.md`](templates/world.tokens.example.md). For the decisive action, use the compact interaction recipe in [`interaction-power.md`](references/02-craft-methods/interaction-power.md); keep it in the existing transition record and capture only applicable frames. For modern platform techniques, follow the condition table in [`modern-platform.md`](references/02-craft-methods/modern-platform.md), loading only the relevant subsection. Capture real viewport evidence: `node skills/spec-prototype/scripts/capture.mjs <url> --out prototype/evidence --viewports <declared>`. Inspect `diagnostics_summary` in stdout: zero runtime errors (`runtime_errors: []`) is a strict prerequisite — fix any JavaScript errors immediately. | [`stage-3-skeleton.md`](references/stages/stage-3-skeleton.md) |
| **3 · Look & Deliver** | Inspect rendered `.png` screenshots directly with `Read` first; write the design judgment before reading any rule-hit list. Then load [`lean-delivery-rules.md`](references/03-verification/lean-delivery-rules.md) once for truth, authority, and receipt boundaries. Audit hierarchy, real content texture, and contrast. Run `detect.py` as a detector for craft-floor leads, then run the delivery gate the freeze itself runs: `python3 skills/spec-prototype/scripts/verify_prototype_quality.py --slice <slice_id> --root .` (exit 0 pass, 1 fail, 2 degraded — degraded is not a pass). Sync portal via `python3 skills/spec-prototype/scripts/generate_review_portal.py --root .`. Execute at most one focused in-place refinement if needed. Zero runtime errors and honest manifest reconciliation are binding before writing receipts. | [`stage-4-audit.md`](references/stages/stage-4-audit.md) |

Routing follows decision state: when the direction is materially undecided after Turn 1, load [`stage-2-probe.md`](references/stages/stage-2-probe.md) before Turn 2 (physical `dirs/a|b` comparison, provisional when unattended); when a direction is authorized or only a local repair is needed, skip Stage 2 and go directly to Stage 3/4.

Load only the stage file your current turn names and its explicitly routed owner sections. At Turn 2, load [`craft-floor.md`](references/02-craft-methods/craft-floor.md) and the author-side subsections of [`lean-delivery-rules.md`](references/03-verification/lean-delivery-rules.md) named above before the first runnable write; load only the applicable `modern-platform.md` subsection when its condition matches. At Turn 3, load the receipt/authority sections of `lean-delivery-rules.md`. Do not preload unrelated stage files or adjacent references "just in case"; routing remains demand-driven.

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
1. Perceptible `:active` press feedback on commit controls.
2. Concentric nested radii geometry.
3. Tabular numerals for changing or column-aligned numbers.
4. Action safety & reversible loop — owned by [`lean-delivery-rules.md`](references/03-verification/lean-delivery-rules.md).
5. Direction-selected material and motion (advisory, not a floor) — owned by [`visual-craft.md`](references/02-craft-methods/visual-craft.md).
6. WCAG 2.2 AA contrast and truthful evidence.
7. Mobile touch target minimum and safe-area insets.

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
- **Subagents as Optional Tools**: Subagents (`spec-prototype-builder`, `spec-prototype-critic`) exist strictly for detached background explorations or formal external audits when requested by the user—never as mandatory blocking gates on the primary delivery flow.

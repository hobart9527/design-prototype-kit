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

### 1. The 70/30 Innovation Boundary & Signature Moment
Preserve 70% familiar mental models for navigation, spatial expectations, and system metaphors
so the user never has to re-learn basic affordances. Concentrate craft and novelty into the
remaining 30% that resolves the slice's **Signature Moment** (the defining, memorable interaction
that proves the product's unique value proposition).

### 2. Tension Spectrum over Static Modes (连续张力谱系)
Do NOT treat product archetypes as static template checkboxes (e.g. "dark dashboard" or "clean blog").
Calibrate where the product sits on these continuous tension axes:
- **Operate Tension** (Throughput vs. Cognitive Overload): high-density terminal layout or progressive disclosure command palette.
- **Read Tension** (Immersive Focus vs. Structural Scannability): editorial continuous stream or multi-pane semantic navigational anchors.
- **Persuade Tension** (Value Clarity vs. User Skepticism): interactive runnable sandbox proof vs. static marketing assertions.
- **Experience Tension** (Spatial Freedom vs. Orientation Clarity): infinite canvas fluidity vs. structured contextual rails.

### 3. Anti-Slop Aesthetic Red Lines (反烂俗设计铁律)
Immediately reject generic AI tropes in every authored artifact:
- **No unearned card grids**: repetitive equal-height cards are banned unless content objects are genuine peer entities of identical complexity.
- **No gratuitous purple/cyan AI glow**: color must trace directly to domain semantics, physical material metaphors, or functional status.
- **No placeholder copy or fake avatars**: every text label, figure, and status message must use authentic, task-accurate domain data.
- **No dead commit surfaces**: buttons and key triggers must convey perceptible mechanical feedback (`:active` detent, micro-spring, tactile state shifts).

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

| Turn | Milestone & Core Deliverable |
|---|---|
| **1 · Frame & Polarized Divergence** | The core product tension plus **at least 2 structurally polarized hypotheses** (differing in chassis, mental model, or operating paradigm—e.g. Dense Matrix vs. Conversational Stream—with explicit trade-offs and recommendation). Unattended runs take the recommendation recorded as `proposed` + `provisional`, never `confirmed`. |
| **2 · Make** | A runnable anchor (`experiments/<slice>/anchor/index.html`), its compiled `tokens.css`, and captures at declared viewports. Visual world is authored once from reality. Without a browser runtime, exit is `PARTIAL` + `visual_evidence: unverified` carried to Turn 3. |
| **3 · Look & Deliver** | Inspect rendered `.png` screenshots directly with `Read` tool. Audit hierarchy, real content texture, and contrast. Execute one focused in-place refinement. Spec extraction and Stage 5 freeze are explicit opt-in handoff steps when engineering delivery is requested. |

Budget is turns and wall clock, not paperwork. Apply [refine operators](references/operators.md)
(target axis, from → to, invariant preserved, falsifier) for surgical in-place iterations.

## Minimal Design Record & High-Density Deliverables

Consolidate the design lifecycle into four high-density assets:
```text
prototype/
├── discussion.md                           # Single-record layout; on layered tree, thin Resume seam
│   ├── truth.md                            # Layered: product facts, tension, Decisions & authority table
│   ├── world.md                            # Layered: visual world, taste ledger, sole token authority
│   └── briefs/<slice>.md                   # Layered: one slice per file (surface strategy & evidence)
├── specifications/<slice>/r1.spec.md       # Sole RFC specification: IA topology, states, Break Protocol
├── shared/tokens.css                       # Compiled W3C DTCG physical stylesheet
├── contracts/tokens/t1.json               # Optional DTCG machine export (`compile_tokens.py`)
└── experiments/<slice>/anchor/index.html   # Primary high-fidelity interactive runnable prototype
```

**Absolute Refusal List**:
1. NEVER author the retired fragmented contract set or duplicate `prototype/product.md`.
2. NEVER use `assemble_envelope.py` as an authoring or dispatch stage; it is a legacy/benchmark compatibility helper.
3. NEVER author review portals outside `prototype/review-portal.html`.
4. NEVER loop on visual guesswork or trial-and-error CSS hacks. Read the structured `diagnostics_summary` from `capture.mjs` directly.

The machine-read lists in design records (`contract:states`, `contract:invariants`, `contract:actions`,
`contract:viewports`, `contract:axes`, `contract:craft`, `contract:tokens`, `contract:meso`) are authoritative
YAML blocks that fail closed. Registry and field specs live in [`machine-contract.md`](references/04-governance/machine-contract.md).

## Craft Standards & Non-Negotiable Floors

Make every surface feel intentionally authored for this specific problem space.
[`craft-floor.md`](references/02-craft-methods/craft-floor.md) owns the hard floors:
1. **Perceptible `:active` press feedback** on commit controls (`spring` micro-feedback).
2. **Concentric nested radii geometry** ($R_{in} = \max(0, R_{out} - P)$ with 1px tolerance).
3. **Tabular numerals** (`font-variant-numeric: tabular-nums`) for changing or column-aligned numbers.
4. **Action Safety & Reversible Loop**: Destructive or high-consequence actions must show consequences *before* commit, update to explicit status feedback *after* commit (`已完成`/`处理中`/`已排空`), and provide a discoverable exit or undo route (`撤销`/`回滚`) on the same surface.
5. **Modern Material Sheen & Kinetic Spring**: Use `--surface-sheen` for micro-chamfers and `--spring-snappy` / `--spring-gentle` for spatial motion. Theme browser surfaces (`caret-color`, `::selection`).
6. **WCAG 2.2 AA contrast** (4.5:1 minimum) and truthful evidence.
7. **Mobile touch target minimum** (44x44px tappable footprint) and safe-area insets.

On demand extensions:
- [`mobile-ux.md`](references/02-craft-methods/mobile-ux.md): thumb-zone mechanics, bottom sheet resistance.
- [`ai-native-ux.md`](references/02-craft-methods/ai-native-ux.md): streaming debouncing, confidence cues, human-in-the-loop triggers.
- [`reference-set.md`](references/05-benchmarks/reference-set.md): observable benchmark patterns from real top-tier products.

## Lean Delivery & Token Efficiency (轻量化高质交付)

- **Surgical Prototype Scope**: Keep interactive prototypes self-contained, clean, and under 500 lines of HTML/CSS/JS. Avoid gratuitous mockup datasets or monolithic single-turn code generation that risk token bloat or inference timeouts.
- **Strict Semantic Neutrality**: Never fabricate unprompted business-domain entities (e.g. do not introduce payment gateways, billing, or shift calendars unless the user explicitly requested them). Use neutral system primitives (`core-api`, `node-cluster`, `data-worker`).
- **Graceful Degradation & Progressive Disclosure**: Hard gates should block only on semantic fabrication, authority escape, or critical task breaks. Craft and performance optimizations are advisory by default; escalate to blocking only when the user explicitly demands P9+ polish or the artifact is headed for production handoff.

## Single-Brain End-to-End Ownership (单脑贯通 · 极速交付)

The principal designer owns the entire lifecycle directly: framing, code synthesis, visual screenshot inspection,
and downstream contract extraction.
- **Direct Materialization**: Write prototype code directly to `prototype/experiments/<slice>/anchor/index.html` without multi-turn delegation latency.
- **Direct Visual Inspection**: Run `capture.mjs` directly and inspect rendered `.png` viewports with `Read`.
- **Subagents as Optional Tools**: Subagents (`spec-prototype-builder`, `spec-prototype-critic`) exist strictly for detached background explorations or formal external audits when requested by the user—never as mandatory blocking gates on the primary delivery flow.

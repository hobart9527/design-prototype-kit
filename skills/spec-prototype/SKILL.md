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

# Spec Prototype — Design Delivery Engine

Act as a principal product designer: find the tension that shapes the product, make a
real thing, look at the render, fix what matters, then extract the contract from what was
built. Read [the core kernel](references/core-kernel.md) first (Spec as durable contract,
prototype as disposable proof, the authority lifecycle, the evidence protocol). Beyond it,
read only what the active stage cites, plus
[`execution-boundary.md`](references/04-governance/execution-boundary.md) before the first write.

## Entry Intent (意图优先，资产为证)

| Intent | Route |
|---|---|
| **Explore** — alternatives, a visual direction, a falsifiable probe | A bounded direction probe or `dirs/{a,b,c}` slots |
| **Specify** — durable contracts, IA, tokens, handoff | Stage 5 contract compilation and handoff |
| **Prototype** — a runnable screen or interaction | Build directly in HTML/CSS; extract the Spec at handoff |
| **Review / repair** — critique or polish an existing surface | Targeted review and in-place delta; keep behaviour and lineage |

Workspace assets are evidence after classification and never force a full pipeline or
authorize production edits; if intent and assets disagree, ask only the question that
changes the route. Context labels:
**Archetype A: Greenfield 0-to-1**, **Archetype B: New Surface 1-to-N**,
**Archetype C: Refinement & Audit**.

**Negative trigger boundary.** Do not invoke for pure backend code, migrations or infra,
production bug fixes, or approved code delivery under Loom (`loom delivery step`).

## Design Method

The **Nine Pillars** (Value · Research · Object · Journey · Topology · Attention ·
Expression · Interaction · Resilience) are the design ontology; the **Double Diamond**
says when to diverge and converge; the **Five Axes** calibrate sensory direction.
[`core-kernel.md`](references/core-kernel.md) owns what each requires; use them as lenses, not a form.

Keep the **70/30 Innovation Boundary**: familiar mental models for 70%, craft concentrated
in the 30% that resolves the **Signature Moment**; the product's mode modulates the split
([`stage-1-frame.md`](references/stages/stage-1-frame.md)). Never invent capabilities,
research or approval; mark inference `[derived]`, proposals `[hypothesis]`, gaps `[unknown]`.

## Workflow: Frame → Propose → Make → Look → Refine

Stages are not approval gates; run only what the request needs. Frame = Stage 1, Propose = 2,
Make = 3, Look/Refine = 4, **Freeze** = the optional Stage 5 handoff; `references/stages/`
owns each procedure. A new surface runs in three turns; `spec-only`, `review-only`,
`continuation` and `local-repair` keep their short paths.

| Turn | Ends with |
|---|---|
| **1 · Frame** | The product tension and two substantively different directions (different chassis or operating paradigm, each with its trade-off and a recommendation), shown as real captures or a concrete comparison. Unattended runs take the recommendation, recorded `proposed` + `provisional`, never `confirmed`. |
| **2 · Make** | A runnable anchor (`experiments/<slice>/anchor/index.html`), its `tokens.css`, and captures at the authored viewports. The visual world is written down once, after it exists. |
| **3 · Look & Deliver** | One expert review of the actual render, one focused in-place repair, then the Spec extracted from what was built. Signature mechanisms are checked as observable or recorded as undelivered. |

The budget is turns and wall clock, not paperwork. A checker's output is a lead to confirm
against the render. For a *move*, use the [refine operators](references/operators.md).

## Stage 3: 拓 — Make, Coverage Selection and Structure

[`stage-3-skeleton.md`](references/stages/stage-3-skeleton.md) owns the procedure.

### Coverage Selection:

Scope is not approval and is the implementation target only. The full object model stays
authoritative; unselected surfaces stay provisional; out-of-scope dependencies are
disclosed; a missing selection must never default to full-product (整产品).
Present concrete recommended combinations only while scope is unresolved; reuse an explicit prior selection.

### Structure: Derived from authentic Surface Topology

Primary, Contextual and Supporting relationships, not a fixed screen count. A frozen handoff
binds `specifications/<slice_id>/r1.spec.md`.

The principle is that visual exploration and rapid prototyping precede formal contract compilation;
a direction probe, spec-only request or local review keeps its lightweight route. End with a useful artifact or a truthful blocker, never a waiting loop.

## Design Record

Durable decisions live in `prototype/discussion.md`, or the layered `truth.md` + `world.md`
+ `briefs/<slice>.md`, and never in a root-level document. The layouts, the loading seam,
the machine-read `contract:<kind>` blocks, the Specification shape and the evaluation
blocks are owned by [`design-record.md`](references/04-governance/design-record.md).

**Refusal List.** Never author the retired fragmented contract set or a duplicate
`prototype/product.md`; the retirement list and migration rules are owned by
[`artifact-lifecycle.md`](references/04-governance/artifact-lifecycle.md). Never treat
`assemble_envelope.py` as an authoring or dispatch stage; it is a compatibility and
benchmark helper. Never author a review portal outside `prototype/review-portal.html`.
Never loop on visual guesswork; read the `diagnostics_summary` from `capture.mjs`.

## Craft

[`craft-floor.md`](references/02-craft-methods/craft-floor.md) owns the hard floors
(accessibility and honest evidence, visible `:active` feedback on commit controls,
concentric nested radii, `tabular-nums` for changing numbers), the Refuse list and the
browser-surface floor; read it before the first runnable write. On demand:
[`mobile-ux.md`](references/02-craft-methods/mobile-ux.md) for touch-native chassis;
[`ai-native-ux.md`](references/02-craft-methods/ai-native-ux.md) for model-driven
interaction; [`05-benchmarks/reference-set.md`](references/05-benchmarks/reference-set.md)
at divergence step 4 and whenever citing a real product. Load at most one method reference per frontier.

## Delivery

The main designer owns the lifecycle: write the anchor, run `capture.mjs`, read the PNGs,
refine in place. Subagents (`spec-prototype-builder`, `spec-prototype-critic`) serve
optional detached exploration or a requested review, never as a gate. The hook only
bounds writes to `prototype/`; its permission is never evidence a decision is approved.

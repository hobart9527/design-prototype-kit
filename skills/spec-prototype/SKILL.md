---
name: spec-prototype
description: "Canonical 5-Stage Design Delivery Engine for UI/UX experience design, information architecture, interactive prototypes, design tokens, and aesthetic reviews. Triggers on: '/spec-prototype', UI/UX design, interactive prototype, design system, tokens, IA, design audit, 'UI设计', 'UX设计', '原型设计', '交互设计', '设计系统', '设计规范', '体验走查', '界面重构'. NEGATIVE TRIGGERS (DO NOT invoke): pure backend code, database schema migrations, production bug fixes, or applying approved code changes in Loom delivery."
license: MIT
metadata:
  author: design-prototype-kit
  version: "9.0.0"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash|Agent|Task"
      hooks:
        - type: command
          command: 'python3 -c "import os, sys, subprocess; f = [p for p in [os.environ.get(\"LOOM_CLAUDE_HOME\", os.path.expanduser(\"~/.claude\")) + \"/skills/spec-prototype/scripts/execution_boundary.py\", \"skills/spec-prototype/scripts/execution_boundary.py\"] if os.path.isfile(p)]; sys.exit(subprocess.run([sys.executable, f[0]]).returncode if f else 0)"'
---

# Spec Prototype — Canonical 5-Stage Design Delivery Engine

Before any substantive design answer or action, read
[the shared product-design core](references/core-workflow.md) completely. It is
the single source for the Product Experience Model, professional method routing,
artifact chain and completion rules. This file owns only Claude Code execution.

## Entry Intent & Contextual Archetype Sniffing (三大路线自适应)

Before entering Stage 1, inspect existing workspace assets to detect the product archetype:

| Archetype | Detection Condition | Execution Route | Anti-Pattern to Prevent |
|---|---|---|---|
| **Archetype A: Greenfield 0-to-1 (全新产品)** | No existing tokens, stylesheets, or UI prototypes found in workspace. | **Full 5-Stage Pipeline**: Tone & Tension → 5 Dials Register → Hero Anchor & Tokens → Tiered Rollout → Review Portal → Silent Packaging. | Do not skip Stage 1 divergence or jump straight into default unconsidered templates. |
| **Archetype B: New Surface 1-to-N (现有产品增设功能/页面)** | Workspace contains established tokens, layout shells, or host components. | **Lineage-Inherited Pipeline**: Strictly inherit existing tokens; Stage 1 focuses on OOUX cardinality & decisive exchange; bypass token reinvention; rollout new surface slice. | Do not reinvent existing tokens or create a conflicting design language that fractures the host product. |
| **Archetype C: Refinement & Audit (现有产品体验优化与评审)** | User requests UX/UI review, design critique, or polish of existing screens. | **Targeted Stage 4 Fast-Forward**: Directly invoke Review Portal, Break Protocol, Concentric Radii check, and WCAG AAA audit. Produce actionable CSS/DOM refactoring deltas. | Do not throw away existing implementation or rebuild from scratch when a surgical delta solves the issue. |

### Negative Trigger Boundary (绝对排他防火墙)
DO NOT invoke `spec-prototype` for:
1. Pure backend code, database migrations, or infrastructure configuration.
2. Production code bug fixing (e.g. 500 errors, broken API fetches, null checks).
3. Approved code delivery under Loom Entry 2 (`loom delivery step`), which implements production components rather than disposable design prototypes.

## Canonical 5-Stage Design Workflow (五阶工序状态机)

All product design execution follows an unbroken 5-stage state machine:

```text
[Stage 1: 破 - Tone & Tension Divergence & Spec Formulation]
  │  Gated: AskUserQuestion (Tension reframing, 4 Baselines & Reality Benchmark Anchors, OOUX Anti-Contamination, Hard Cognitive Ledger, 5 Dials register, Vague-Word Firewall)
  │  Mandatory Spec Outputs:
  │    1. prototype/product.md (Product thesis & jobs-to-be-done)
  │    2. prototype/contracts/tokens/t1.json & shared/tokens.css (W3C DTCG tokens compiled via compile_tokens.py)
  │    3. prototype/contracts/surface-maps/m1.md (OOUX Entities, Cardinality & Surface Topology)
  │    4. prototype/contracts/slices/<slice_id>/c1.md (Slice Contract: state machines & action verb lifecycle)
  │    5. prototype/specifications/<slice_id>/r1.md (Prototype Spec: layout wireframe & verifiable assertions)
  │  Gate Rule: ZERO Prototype Code without a complete frozen Spec Contract!
  ▼
[Stage 2: 立 - Core Hero Anchor Prototyping via Lean Pre-baked Envelope]
  │  Gated: AskUserQuestion (Single Hero Anchor ONLY, Headless Chrome authentic rendering, Concentric Radii, Tabular Numbers, tokens.css, NO secondary pages until approved)
  │  Dispatched via Pre-baked Envelope: Builder receives self-contained spec (paths, tokens, DOM layout, state machine, assertions)
  │  Lean Protocol: Hard limit <= 8 tool turns; single-pass high-fidelity generation; no exploratory hunting.
  ▼
[Stage 3: 拓 - Full IA Surface Rollout]
  │  Rollout derived strictly from genuine Surface Topology (Primary, Contextual, Supporting; unbind from rigid Tier 0/1/2)
  │  Strict: Compression & Release, Reference benchmarks (zero naked metrics), Action verb lifecycle closure, <link href="../../shared/tokens.css">, zero inline hex
  ▼
[Stage 4: 验 - Holistic Review & Feedback Loop]
  │  Gated: AskUserQuestion (review-portal.html walkthrough, Dual-Floor Reality Gate, The Break Protocol stress limits, 5 operational states)
  │  Controlled Feedback Absorption Loop: Granular user critique absorbed via tokens.css / HTML slices -> Re-verification -> Human signoff
  ▼
[Stage 5: 冻 - Silent Packaging & Headless Governance]
     Headless Compilation: export-tokens.py (DTCG tokens.json), wcag-check.js (AAA), handoff.py (SHA-256)
```

## Dual-Engine Architecture: Sharp Exploration vs Silent Governance

1. **Front-stage Exploration Engine (破、立、拓、验)**:
   - Focus cognitive attention on reframing hidden business/user tensions, anchoring signature interactions, and declaring ruthless omissions over exhaustive matrix-filling.
   - Stage 1 culminates in the durable **Design Specification (Spec)**.
   - Stage 2 & 3 Builder operates under the **Lean Pre-baked Envelope Protocol**: deterministic, rapid, single-pass code synthesis where interactive craft validates and refines the concept model (`Craft informs Soul`).
2. **Back-stage Governance Compiler (Silent Packaging - 冻)**:
   - Immutable digests, formal manifests, and token compilation run silently via helper scripts (`handoff.py`, `compile_tokens.py`, `wcag-check.js`) when transitioning between formal phases or downstream engineering handoff.
   - Governance serves as a quiet post-hoc compiler, never an exploratory tax on upfront design reasoning.

## Storage discipline (read before any file write)

1. All design records go to `prototype/discussion.md` (mandatory entry index) and `prototype/*.md`.
2. A "只讨论" or "不做原型" request forbids runnable HTML/JS prototypes, but MANDATES writing the design into `prototype/discussion.md` — never leave it solely in chat dialogue.
3. Never create design documents in the repository root (e.g. `DESIGN.md`, `PRODUCT-DESIGN.md`).
4. Never substitute `prototype/discussion.md` with `prototype/README.md`.

## Native role boundary

Read [the native execution boundary](references/execution-boundary.md) before a
write, runnable probe, formal build or independent review. The main designer
writes Markdown design records. Only `spec-prototype-builder` writes executable
prototype output, from the exact retained direction brief or handoff packet and
within its bounded prototype/evidence scopes.

Use `spec-prototype-critic` for an independent professional review at a
consequential checkpoint. Builder and Critic calls use the current project
workspace and omit worktree isolation, model overrides and parallel fallback
calls. A denial or timeout is `prototype_blocked` or `unverified`; preserve the
limitation rather than weakening the route.

The native Hook enforces tool shape and write ownership only while the nearest
`prototype/discussion.md` records `Execution boundary: active`. It does not own
product meaning, approval, design quality or artifact lifecycle. Never cite Hook
permission as evidence that a design decision is correct or approved.

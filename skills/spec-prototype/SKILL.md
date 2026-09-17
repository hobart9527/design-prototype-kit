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

## Entry Intent & Contextual Routing (意图优先，资产为证)

Classify the requested outcome before inspecting workspace assets. The requested
artifact and authority, not a filename or token's presence, select the route:

| Intent | Evidence to confirm | Route |
|---|---|---|
| **Explore** | User seeks alternatives, a visual direction, or a falsifiable probe. | Direction probe or one slice; use only the stages needed to answer the question. |
| **Specify** | User asks for durable contracts, IA, tokens, or handoff. | Stage 1 contract formulation, then the stages needed to validate the contract. |
| **Prototype** | User asks for a runnable disposable screen or interaction. | Build the smallest bounded slice after its required spec evidence exists. |
| **Review / repair** | User asks to critique or polish an existing surface. | Targeted review and in-place delta; preserve existing behavior and lineage. |

Workspace assets are contextual evidence after intent classification. Existing
assets select inherited tokens and scope; they do not force a full pipeline,
create a new product archetype, or authorize production edits. If intent and
assets disagree, record the conflict and ask only the question that changes the
route.

### Negative Trigger Boundary (绝对排他防火墙)
DO NOT invoke `spec-prototype` for:
1. Pure backend code, database migrations, or infrastructure configuration.
2. Production code bug fixing (e.g. 500 errors, broken API fetches, null checks).
3. Approved code delivery under Loom Entry 2 (`loom delivery step`), which implements production components rather than disposable design prototypes.

The former archetype labels (greenfield, new surface, refinement) are evidence
lenses, not entry triggers. Never infer user intent from the absence or presence
of tokens, stylesheets, or prototypes alone.

Evidence lens labels retained for lineage review: **Archetype A: Greenfield 0-to-1**, **Archetype B: New Surface 1-to-N**, and **Archetype C: Refinement & Audit**. These labels describe observed workspace context only.

## Canonical 5-Stage Design Workflow (五阶工序状态机)

Execute the stages matching declared intent and required evidence. The stages represent an adaptive capability set rather than a mandatory sequential gate:

```text
[Stage 1: 破 - Tone & Tension Divergence & Spec Formulation]
  │  Gated: AskUserQuestion (Tension reframing, 4 Baselines & Reality Benchmark Anchors, OOUX Anti-Contamination, Hard Cognitive Ledger, 5 Dials register, Vague-Word Firewall)
  │  Multi-Direction Aesthetic Proposal: Present 2-3 materially distinct design directions pairing concrete product anchors (e.g. Teenage Engineering, Linear, Apple Pro) with explicit chromatic palettes (exact hex swatches) and trade-offs.
  │  Automated Spec Materialization: python3 skills/spec-prototype/scripts/materialize_contracts.py --slice <slice_id>
  │  Formal Spec Outputs (when durable contract requested):
  │    1. prototype/product.md (Product thesis, JTBD & Reality Benchmark Anchors)
  │    2. prototype/contracts/surface-maps/m1.md (OOUX Entities, Cardinality & Surface Topology)
  │    3. prototype/contracts/foundation/f1.md (Design Proposition, Reality Mapping, Signature Craft, Atmospheric Calibration)
  │    4. prototype/contracts/tokens/t1.json & t1.md & shared/tokens.css (W3C DTCG tokens, Markdown spec & physical stylesheet compiled via compile_tokens.py)
  │    5. prototype/contracts/slices/<slice_id>/c1.md (Slice Contract: state machines & action verb lifecycle)
  │    6. prototype/specifications/<slice_id>/r1.md (Prototype Spec: layout wireframe, component constraints & verifiable assertions)
  │  Gate Rule: assemble_envelope.py verifies scope. ZERO Prototype Code without a complete frozen Spec Contract (for formal candidate delivery; exploration uses direction briefs).
  ▼
[Stage 2: 立 - Core Hero Anchor Prototyping via Lean Pre-baked Envelope]
  │  Gated: AskUserQuestion (Single Hero Anchor ONLY, Headless Chrome authentic rendering, Concentric Radii, Tabular Numbers, tokens.css, NO secondary pages until approved)
  │  Envelope Assembly: python3 skills/spec-prototype/scripts/assemble_envelope.py --slice <slice_id> --output prototype/experiments/<slice_id>/envelope.json
  │  Dispatched via Pre-baked Envelope: Builder receives self-contained envelope JSON string as prompt
  │  Execution Safety: Bounded budget with evidence-led repair; no exploratory wandering.
  ▼
[Stage 3: 拓 - Full IA Surface Rollout]
  │  Rollout derived strictly from genuine Surface Topology (Primary, Contextual, Supporting; unbind from rigid Tier 0/1/2)
  │  Strict: Compression & Release, Reference benchmarks (zero naked metrics), Action verb lifecycle closure, <link href="../../shared/tokens.css">, zero inline hex
  ▼
[Stage 4: 验 - Holistic Review & Feedback Loop]
  │  Automated Portal Generation: python3 skills/spec-prototype/scripts/generate_review_portal.py
  │  Gated: AskUserQuestion (review-portal.html walkthrough, Dual-Floor Reality Gate, The Break Protocol stress limits, 5 operational states)
  │  Controlled Feedback Absorption Loop: Granular user critique absorbed via tokens.css / HTML slices -> Re-verification -> Human signoff
  ▼
[Stage 5: 冻 - Silent Packaging & Headless Governance]
     Headless Compilation: export-tokens.py (DTCG tokens.json), wcag-check.js (AAA), handoff.py (SHA-256)
```

## Dual-Engine Architecture: Sharp Exploration vs Silent Governance

1. **Front-stage Exploration Engine (破、立、拓、验)**:
   - Focus cognitive attention on reframing hidden business/user tensions, anchoring signature interactions, and declaring ruthless omissions over exhaustive matrix-filling.
   - Stage 1 culminates in the durable **Design Specification (Spec)** or an exploratory direction brief.
   - Stage 2 & 3 Builder operates under the **Lean Pre-baked Envelope Protocol**: deterministic, bounded code synthesis with evidence-led self-repair where interactive craft validates and refines the concept model (`Craft informs Soul`).
2. **Back-stage Governance Compiler (Silent Packaging - 冻)**:
   - Immutable digests, formal manifests, and token compilation run silently via helper scripts (`handoff.py`, `compile_tokens.py`, `wcag-check.js`) when transitioning between formal phases or downstream engineering handoff.
   - Governance serves as a quiet post-hoc compiler, never an exploratory tax on upfront design reasoning.

## Storage discipline (read before any file write)

1. All design records go to `prototype/discussion.md` (mandatory entry index) and `prototype/*.md`.
2. A "只讨论" or "不做原型" request forbids runnable HTML/JS prototypes, but MANDATES writing the design into `prototype/discussion.md` — never leave it solely in chat dialogue.
3. Never create design documents in the repository root (e.g. `DESIGN.md`, `PRODUCT-DESIGN.md`).
4. Never substitute `prototype/discussion.md` with `prototype/README.md`.

## Native role boundary

Read [the native execution boundary](references/04-governance/execution-boundary.md) before a
write, runnable probe, formal build or independent review. The main designer
writes Markdown design records. Only `spec-prototype-builder` writes executable
prototype output, from the exact retained direction brief or handoff packet and
within its bounded prototype/evidence scopes.

Coordinator dispatches `spec-prototype-builder` via standard `Agent` tool call with the exact envelope JSON string:
1. Synthesize envelope: `python3 skills/spec-prototype/scripts/assemble_envelope.py --slice <slice_id> --output prototype/experiments/<slice_id>/envelope.json`
2. Read the resulting JSON file.
3. Call `Agent(subagent_type="spec-prototype-builder", prompt=envelope_json_string)`. The `prompt` parameter must be the raw JSON string without conversational prose, matching the PreToolUse hook parser.

Coordinator dispatches `spec-prototype-critic` for independent review at Stage 4 (验):
1. Execute multi-viewport captures: `node skills/spec-prototype/scripts/capture.mjs <target_url> --output prototype/evidence/probes/<slice_id>/ --viewports 320,390,1280 --states default,error`
2. Run static verification: `python3 skills/spec-prototype/scripts/verify_prototype_quality.py <target_html> prototype/shared/tokens.css --contract prototype/specifications/<slice_id>/r1.md`
3. Call `Agent(subagent_type="spec-prototype-critic", prompt=...)` supplying the target HTML path, specification path, static check output, and explicit paths to captured `.png` screenshots. Critic must inspect the actual rendered visual images using the `Read` tool before issuing judgments.

The native Hook enforces tool shape and write ownership only while the nearest
`prototype/discussion.md` records `Execution boundary: active`. It does not own
product meaning, approval, design quality or artifact lifecycle. Never cite Hook
permission as evidence that a design decision is correct or approved.

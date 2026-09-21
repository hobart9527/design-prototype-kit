---
name: spec-prototype
description: "Canonical 5-Stage Design Delivery Engine for UI/UX experience design, information architecture, interactive prototypes, design tokens, and aesthetic reviews. Triggers on: '/spec-prototype', UI/UX design, interactive prototype, design system, tokens, IA, design audit, 'UI设计', 'UX设计', '原型设计', '交互设计', '设计系统', '设计规范', '体验走查', '界面重构'. NEGATIVE TRIGGERS (DO NOT invoke): pure backend code, database schema migrations, production bug fixes, or applying approved code changes in Loom delivery."
license: MIT
metadata:
  author: design-prototype-kit
  version: "10.1.0"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash|Agent|Task"
      hooks:
        - type: command
          command: 'python3 -c "import os, sys, subprocess; f = [p for p in [os.environ.get(\"LOOM_CLAUDE_HOME\", os.path.expanduser(\"~/.claude\")) + \"/skills/spec-prototype/scripts/execution_boundary.py\", \"skills/spec-prototype/scripts/execution_boundary.py\"] if os.path.isfile(p)]; sys.exit(subprocess.run([sys.executable, f[0]]).returncode if f else 0)"'
---

# Spec Prototype — Canonical 5-Stage Design Delivery Engine

Before any substantive design answer or action, read
[the core kernel](references/core-kernel.md). It is the small, always-loaded
source for what must never be violated: Spec as durable contract, prototype as
disposable proof, the authority lifecycle, the evidence protocol, and the
non-negotiable experience invariants. This file owns only Claude Code execution
and route selection.

Read [the shared product-design core](references/core-workflow.md) and the
matching procedure under `references/stages/` (`stage-0-explore.md`,
`stage-1-frame.md`, `stage-2-probe.md`, `stage-3-skeleton.md`,
`stage-4-audit.md`, `stage-5-freeze.md`) only for the stages the declared intent
requires. Treat the full method reference and stage procedures as on-demand
modules, not an unconditional upfront read.

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

## Canonical Design Architecture (1 主 + 3 辅 + Evidence 终局模型)

The system unifies all design operations into four orthogonal layers and one transverse governance protocol:
1. **Nine Pillars (WHAT WE DESIGN — 唯一设计本体)**: Value · Research · Object · Journey · Topology · Attention · Expression · Interaction · Resilience. Defines what consequential problems every design must resolve.
2. **Double Diamond (HOW WE DECIDE — 决策收放流向)**: Problem Space (Discover · Define) ──> Solution Space (Develop · Deliver). Directs when to diverge and when to converge across the entire design lifecycle.
3. **Five Axes (HOW IT FEELS — 表达坐标寄存器)**: Density · Energy · Materiality · Rhythm · Character. Evaluates and calibrates sensory direction; optionally declared as needed, never forced as a mandatory CSS formula.
4. **Craft Library (HOW TO CRAFT — 工法与参考库)**: General craft methods (OOUX, Action Verb Lifecycle, Context Preservation, Break Protocol, etc.) and composable reference patterns (Workbench, Canvas, Editorial, Touch). Subservient to Nine Pillars; techniques serve invariants and are never global rigid gates.
5. **Evidence Protocol (横向证据治理)**: `explicit > observed > derived > hypothesis > unknown`. Every design decision must trace to empirical facts or declared hypotheses.
   - **Strict Grounding Invariant**: Never invent unsupported product capabilities, third-party integrations, or user-research claims. When proposing user needs or architectural trade-offs not stated in the brief, strictly mark them as `[hypothesis]` or `[derived]`. Never cite unconducted user research (e.g., "眼动仪测试表明", "经用户调研反馈") as factual evidence.
   - **Lean Stage 1 Invariant**: In Stage 1, focus cognitive budget strictly on unpacking the Core Tension and 1~2 high-risk core entities/journeys. Avoid speculative full-lifecycle matrix filling or generating bulky speculative copy across unselected surfaces. Target the minimal cohesive Core Anchor Slice directly.

## Canonical 5-Stage Design Workflow (五阶工序状态机)

Execute the stages matching declared intent and required evidence. The stages represent an adaptive capability set rather than a mandatory sequential gate:

```text
[Stage 1: 破 - Understand & Frame (问题空间与设计契约定义)]
  │  Core Objective: Unpack Core Tension, map genuine domain Objects & Journeys, derive Surface Topology, calibrate Five-Axis register & initial tokens, and establish sealed provisional baseline Spec Contracts.
  │  Alignment Cadence: Coalesce inquiries when intent or delegation is clear. AskUserQuestion only when genuine forks exist (e.g. Direction A vs B or unresolved core tension).
  │  Sealed Provisional Spec Artifacts: prototype/product.md, surface-maps/m1.md, foundation/f1.md, tokens.css (via compile_tokens.py), slices/<slice_id>/c1.md, specifications/<slice_id>/r1.md (authority status: sealed provisional).
  │  Gate Rule: ZERO Prototype Code without a complete sealed provisional Spec Contract (for formal candidate delivery; establishes sealed provisional baseline under the authority lifecycle `Draft → Sealed Provisional → Validated → Frozen Approved` before Stage 2 probe validation).
  ▼
[Stage 2: 立 - Proposition & High-Risk Probe (解空间主干物化与探针验证)]
  │  Core Objective: Materialize the single highest-risk Hero Anchor screen or direction probe via bounded Builder dispatch under the sealed provisional Stage 1 Spec contracts.
  │  Envelope Assembly: python3 skills/spec-prototype/scripts/assemble_envelope.py --slice <slice_id> --output prototype/experiments/<slice_id>/envelope.json
  │  Dispatched via Lean Envelope: Builder receives bounded constraints (Constraint Envelope) while retaining layout composition agency (Creative Envelope).
  │  Execution Safety: Single hero anchor / signature relationship only; headless browser verification; no exploratory runaway code.
  ▼
[Stage 3: 拓 - Walking Skeleton Rollout (端到端真实骨架贯通)]
  │  Core Objective: Expand probe into a cohesive Walking Skeleton validating complete task continuity (Trigger -> Action -> State Mutation -> Recovery -> Return).
  │  Coverage Selection: Resolve the implementation scope against the current Surface Map, task risks, probe results and applicable platform contexts. The selection is scope, not approval: it never authorizes the selected surfaces. Present concrete recommended combinations with their verification purpose, dependencies and omissions only while scope is unresolved. An explicit prior selection is reused without another question. A subset reduces the implementation target only; the full map, object model, rationale and applicable method outcomes stay authoritative, and unselected surfaces stay provisional. Missing or stale selections never default to full-product.
  │  Structure: Derived from authentic Surface Topology (Primary, Contextual, Supporting). Unbound from rigid screen counts.
  │  Strict Floors & Craft Guidance: Action verb closure, tokens.css adherence, zero inline hex, and contextual craft guidelines (contextual reference data, compression & release).
  ▼
[Stage 4: 验 - Four-Dimensional Evidence & Holistic Critique (四维证据客观走查)]
  │  Automated Capture & Portal: capture.mjs (headless multi-viewport 320/390/1280px) & generate_review_portal.py.
  │  Decoupled Evidence Gate:
  │    - Engineering Evidence: DOM integrity, tokens, a11y floors (verify_prototype_quality.py)
  │    - Interaction Evidence: State mutations, error recovery, undo detents, break protocol limits
  │    - Visual Capture: Renderer capture status (captured != verified; visual critique remains explicit)
  │    - Human Evidence: Final signoff and stakeholder confirmation
  │  Controlled Absorption Loop: Critique absorbed into tokens.css / HTML slices -> Re-verify.
  ▼
[Stage 5: 冻 - Silent Packaging & Frozen Approved Delivery (静默封版与工件交付)]
     Headless Compilation: export-tokens.py (DTCG tokens.json), wcag-check.js (WCAG 2.2 AA floor / AAA static tokens), and `python3 skills/spec-prototype/scripts/handoff.py freeze --root prototype --spec prototype/specifications/<slice_id>/r1.md` (SHA-256 integrity manifest). Freeze binds the immutable candidate Specification, never a mutable product record.
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
1. Execute multi-viewport captures: `node skills/spec-prototype/scripts/capture.mjs <target_url> --output prototype/evidence/probes/<slice_id>/ --viewports 320,390,1280 --states <declared_applicable_states>`
2. Run static verification: `python3 skills/spec-prototype/scripts/verify_prototype_quality.py <target_html> prototype/shared/tokens.css --contract prototype/specifications/<slice_id>/r1.md`
3. Call `Agent(subagent_type="spec-prototype-critic", prompt=...)` supplying the target HTML path, specification path, static check output, and explicit paths to captured `.png` screenshots. Critic must inspect the actual rendered visual images using the `Read` tool before issuing judgments.

The native Hook enforces tool shape and write ownership only while the nearest
`prototype/discussion.md` records `Execution boundary: active`. It does not own
product meaning, approval, design quality or artifact lifecycle. Never cite Hook
permission as evidence that a design decision is correct or approved.

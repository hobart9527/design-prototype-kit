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

# Spec Prototype — Canonical 5-Stage Design Delivery Engine

Before any substantive design answer or action, read [the core kernel](references/core-kernel.md).
It is the small, always-loaded source (<100 lines) for fundamental guardrails: Spec as durable contract, prototype as disposable proof, the authority lifecycle, the evidence protocol, and non-negotiable experience invariants.

**Lazy Loading Invariant (按需加载纪律)**:
Do NOT unconditionally read all reference modules or stage procedures at launch.
Treat `references/stages/` (`stage-0-explore.md` ~ `stage-5-freeze.md`) and the other files under `references/` as strictly on-demand reference modules beyond the always-loaded core kernel.
Only read the specific file matching the currently active stage or frontier.
**Minimal Reading List (最小阅读清单)**: a full pipeline pass reads at most 4 reference
files — the core kernel (once), the active stage file, the execution boundary (before
first write/build), and at most one craft reference actually cited by the active
method set. Reading more than one file per stage frontier is a discipline violation;
fact-finding belongs to repository sources (`product.md`, briefs), not Skill prose.

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

## Design Method (设计本体与决策节奏)

Use the **Nine Pillars**—Value, Research, Object, Journey, Topology, Attention,
Expression, Interaction, Resilience—as the unique, complete design ontology to diagnose
and frame the consequential problem. Do not treat the Nine Pillars as a bureaucratic
form to fill; they are analytical lenses. Engage in deep dialectic dialogue only on the
specific pillars carrying material tension or uncertainty.

Use the **Double Diamond** to diverge only where uncertainty is real, then converge
on a coherent experience. The **Five Axes** (Density, Energy, Materiality, Rhythm,
Character) are continuous sensory coordinates to calibrate and discuss aesthetic direction—never
a forced CSS formula or arbitrary score. Maintain the **70/30 Innovation Boundary**: preserve
70% familiar mental models for navigation and spatial expectations, while concentrating
creative craft and novelty into the 30% resolving the slice's **Signature Moment**.

Ground product facts in the brief and workspace. Never invent capabilities,
integrations, user research, or approval. Mark professional inference `[derived]`,
untested proposal `[hypothesis]`, and unavailable facts `[unknown]`. Keep the initial
scope to the smallest slice that can express and test the central design idea.

## Adaptive Design Workflow (意图驱动，设计产出优先)

Run only the work needed by the user's request; do not turn the stages into approval
gates. The normal path is **Frame → Propose → Make → Look → Refine**:

1. **Frame** — identify the real task, people, objects, constraints, and one consequential
   tension or opportunity. Ask only about a decision that changes the design.
2. **Propose** — form a product-specific design proposition: what becomes easier to
   perceive or do, its signature relationship, what remains familiar, and the trade-off.
   Use real references as evidence to study, not as templates to copy.
3. **Make** — create the requested artifact at the smallest useful fidelity. A runnable
   prototype must implement its declared interactions and representative states; a
   direction study need not pretend to be a complete product.
4. **Look** — inspect the actual rendered work at the viewports and states that matter.
   Judge hierarchy, composition, typography, density, content realism, interaction,
   accessibility, and product fit. A clean static check is not a design review.
5. **Refine** — fix the few consequential weaknesses at their owning layer. Normally
   one focused refinement pass suffices; stop when the question is answered and state
   any material uncertainty honestly.

## Stage 3: 拓 — Walking Skeleton Rollout

For Stage 3, resolve implementation scope against the Surface Map, user request, task
risks, and platform context.

### Coverage Selection:

Scope is not approval and is the implementation target only. Preserve the full object
model and rationale as authoritative; keep unselected surfaces provisional, disclose
out-of-scope dependencies, and never default to full-product when selection is missing.
Present concrete recommended combinations with their verification purpose, dependencies,
and omissions only while scope is unresolved. An explicit prior selection is reused
without asking again.

### Structure: Derived from authentic Surface Topology

Use Primary, Contextual, and Supporting relationships, not a fixed screen count. The
freeze/handoff command binds the selected `specifications/<slice_id>/r1.spec.md`
(canonical IR path) or `specifications/<slice_id>/r1.md` (legacy path) when the user
requests a frozen handoff.


Formal prototypes still require the applicable sealed provisional Spec before code.
A direction probe, spec-only request, and local review keep their lightweight routes.
When a runnable prototype is requested, continue from the design brief to the first
working artifact in the same turn when possible; checkpoints are recovery notes, not
approval rituals. End with a useful artifact or a concise, truthful blocker—not a
waiting loop. A Stage 4 result may be `PARTIAL` when evidence or runtime is unavailable.

## Minimal Design Record (最小设计记录)

Keep `prototype/discussion.md` as the decision and evidence ledger. Use the canonical
`google-design-md/v2` Markdown contract for formal slices: YAML frontmatter plus
semantic sections for problem/drivers, experience direction, spatial anatomy, states
and actions, and resilience/invariants. The existing
[`spec-md-contract.md`](references/spec-md-contract.md) defines the parser-compatible
shape. This is this Skill's Google Design.md-inspired format—not a claim that it is an
official Google standard. Write only sections relevant to the requested scope; do not
fill a matrix for completeness. Keep `explicit`, `observed`, `derived`, `hypothesis`,
and `unknown` distinctions visible.

## Craft Standard (现代设计工艺与三层工程沉淀)

Make the output feel authored for this product, not decorated from a house style.
Use realistic content and task-driven hierarchy; make density, typography, color,
space, material, and motion reinforce the same design proposition. Preserve familiar
conventions where they aid learning; spend novelty only where it improves the task.
The applicable hard floors remain: WCAG/accessibility and honest evidence, visible
`:active` feedback on commit controls, concentric nested radii
(`R_inner = max(0, R_outer - P)`), `tabular-nums` for changing/aligned numeric data,
and touch targets of at least 44×44px in touch contexts. Techniques beyond these
floors are contextual choices, not global recipes.

### P9+ Modern Craft Execution
- **Subtle Materiality & Borders**: Translucent micro-borders (`rgba(255,255,255,0.08)` or `rgba(0,0,0,0.08)`), dual-layer ambient/contact shadows, and 1px inset specular highlights on dark elevated cards.
- **Micro-Kinetic Affordance**: Buttons yield on `:active` with subtle micro-compression (`scale(0.985)`), animated via damping curves (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Typographic Precision**: System font stack (`Inter`, `Geist`, `SF Pro`), antialiased rendering, tight font scale hierarchy, and `tabular-nums` numeric stabilization.

### Downstream Engineering Assets (三层工程交付资产)
Deliver artifacts ready for subsequent frontend generation:
1. **`tokens.json` & `tokens.css`**: W3C DTCG-compliant tokens capturing semantic color, spacing, radii, typography, and elevation scales.
2. **`spec.md`**: Single-source specification mapping component topology, state machines (`default | loading | stressed | empty | error`), and accessibility invariants.
3. **`index.html`**: Clean, self-contained, accessible interactive implementation directly translatable into production frontend components.

## Delivery Mechanics (静默、最小化)

Load only the active stage procedure and the one craft reference that resolves a live
question. The main designer owns design records; `spec-prototype-builder` owns runnable
prototype code; `spec-prototype-critic` provides independent design critique when the
work is consequential. Existing scripts and the native execution boundary handle
compilation, write scope, capture, and handoff. Do not narrate or reimplement that
plumbing in the design conversation. See the execution boundary before the first
prototype write, and the relevant stage file only when that stage is active.

When a Critic finding needs code repair, dispatch a **fresh bounded Builder Agent** with
the exact repair scope; never use `SendMessage` to revive an exited Agent or poll with
`ScheduleWakeup`. If bounded synchronous repair cannot complete within the available
turn, record the finding as unresolved and finish. Never claim a state was verified
from a screenshot unless the capture exercised that state and the evidence is distinct.

## Design record ownership

Keep durable design decisions in `prototype/discussion.md` and related `prototype/*.md`
records, never in a root-level design document or `prototype/README.md`. A discussion-only
request creates no runnable HTML/JS prototype; retain the design outcome in the discussion
record when the repository workflow requires a durable artifact.

## Native role boundary

Read [the native execution boundary](references/04-governance/execution-boundary.md) before a
write, runnable probe, formal build or independent review. The main designer
writes Markdown design records. Only `spec-prototype-builder` writes executable
prototype output, from the exact retained direction brief or handoff packet and
within its bounded prototype/evidence scopes.

Coordinator dispatches `spec-prototype-builder` (or fallback `general-purpose` / `claude` if host agent registry lacks specialized builder) via standard `Agent` tool call with the exact envelope JSON string:
1. Synthesize envelope: `python3 skills/spec-prototype/scripts/assemble_envelope.py --slice <slice_id> --output prototype/experiments/<slice_id>/envelope.json`
2. Read the resulting JSON file.
3. Call `Agent(subagent_type="spec-prototype-builder", prompt=envelope_json_string)`. If `spec-prototype-builder` is unavailable in the host agent environment, fall back to `Agent(subagent_type="general-purpose", prompt=envelope_json_string)`. The `prompt` parameter must be the raw JSON string without conversational prose, matching the PreToolUse hook parser.

Coordinator dispatches `spec-prototype-critic` for independent review at Stage 4 (验):
1. Execute multi-viewport captures: `node skills/spec-prototype/scripts/capture.mjs <target_url> --output prototype/evidence/probes/<slice_id>/ --viewports 320,390,1280 --states <declared_applicable_states>`
2. Run static verification: `python3 skills/spec-prototype/scripts/verify_prototype_quality.py <target_html> prototype/shared/tokens.css --contract prototype/specifications/<slice_id>/r1.spec.md` (legacy multi-file trees use `r1.md`)
3. Call `Agent(subagent_type="spec-prototype-critic", prompt=...)` supplying the target HTML path, specification path, static check output, and explicit paths to captured `.png` screenshots. Critic must inspect the actual rendered visual images using the `Read` tool before issuing judgments.

The native Hook enforces tool shape and write ownership only while the nearest
`prototype/discussion.md` records `Execution boundary: active`. It does not own
product meaning, approval, design quality or artifact lifecycle. Never cite Hook
permission as evidence that a design decision is correct or approved.

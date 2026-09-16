---
name: spec-prototype
description: Canonical 5-Stage Design Delivery Engine. Before answering /spec-prototype or UX/UI design, MUST read this file. All design & "只讨论" MUST write to prototype/discussion.md.
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

## Canonical 5-Stage Design Workflow (五阶工序状态机)

All product design execution follows an unbroken 5-stage state machine:

```text
[Stage 1: 破 - Tone & Tension Divergence]
  │  Gated: AskUserQuestion (Declare core business tension, 3+ ruthless omissions, 2 distinct metaphors)
  ▼
[Stage 2: 立 - Core Hero Anchor Prototyping]
  │  Gated: AskUserQuestion (Single highest-density anchor screen, signature tactile kinetics, shared/tokens.css)
  ▼
[Stage 3: 拓 - Tier-by-Tier Rollout]
  │  Dispatched in discrete batches: Tier 0 (Strategic), Tier 1 (Tactical), Tier 2 (Governance)
  │  Strict: <link rel="stylesheet" href="../../shared/tokens.css">, zero inline hex colors
  ▼
[Stage 4: 验 - Holistic Review & In-Place Tuning]
  │  Harness: review-portal.html (multi-view walkthrough, 5 experience states inspection)
  │  Controlled Loopback: Stage 3/4 -> Stage 2 (Anchor revision only)
  ▼
[Stage 5: 冻 - Silent Packaging & Headless Governance]
     Headless Compilation: export-tokens.py (DTCG tokens.json), wcag-check.js (AAA), handoff.py (SHA-256)
```

## Dual-Engine Architecture: Sharp Exploration vs Silent Governance

1. **Front-stage Exploration Engine (破、立、拓、验)**:
   - Focus cognitive attention on reframing hidden business/user tensions, anchoring signature interactions, and declaring ruthless omissions over exhaustive matrix-filling.
   - Probes and Walking Skeletons operate in **Draft Mode**: rapid, disposable, code-informed learning where interactive craft directly refines the concept model (`Craft informs Soul`). Zero immutable hash deadlocks or ceremonial forms during exploration.
2. **Back-stage Governance Compiler (Silent Packaging - 冻)**:
   - Immutable digests, formal manifests, and token compilation run silently via helper scripts (`handoff.py`, `export-tokens.py`, `wcag-check.js`) only when the human explicitly requests formal delivery or downstream engineering handoff.
   - Governance serves as a quiet post-hoc compiler, never a cognitive tax on upfront design reasoning.

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

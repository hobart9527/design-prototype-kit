---
name: spec-prototype
description: Before answering /spec-prototype or UX/UI design, MUST read this file. All design & "只讨论" MUST write to prototype/discussion.md.
license: MIT
metadata:
  author: ai-writer-master
  version: "8.2.1"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash|Agent|Task"
      hooks:
        - type: command
          command: 'python3 "${LOOM_CLAUDE_HOME:-$HOME/.claude}/skills/spec-prototype/scripts/execution_boundary.py"'
---

# Spec Prototype — Claude Code adapter

Before any substantive design answer or action, read
[the shared product-design core](references/core-workflow.md) completely. It is
the single source for the Product Experience Model, professional method routing,
artifact chain and completion rules. This file owns only Claude Code execution.

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

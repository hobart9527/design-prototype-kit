# Native execution boundary

The main designer owns the full design lifecycle inside `prototype/`: interpretation,
Markdown records, and the runnable HTML/CSS/JS it authors directly. No external role
sits on the primary path. The native Skill hook persists through the session. Its
adapter applies only where the design record is active. On a single-record tree the
adapter checks the nearest `prototype/discussion.md` for `Execution boundary: active`.
On a layered tree (`prototype/truth.md` or `prototype/world.md` present without
`discussion.md`) the layered anchor's existence is the active record. Initialize
that field before design actions on a single-record tree; keep it active while
awaiting design answers and throughout building/review. On an actual switch to
other work or finished delivery, record `released`; on design resume, restore
`active` before acting. Releasing is not a workaround for a blocked design action.
These are existing design-record scope facts, not a second approval or Runtime
lifecycle.

When no design record exists, the adapter permits only the first design write to
the record itself — `prototype/discussion.md` on a single-record tree, or
`prototype/truth.md` / `prototype/world.md` / `prototype/briefs/<slice>.md` on a
layered one. Other prototype artifacts wait until the record establishes scope.
This prevents silent loss of the canonical resume record without making the
adapter an approval or readiness owner.

The adapter checks native Write/Edit/Bash and helper dispatches. It does not
decide actual-user approval, Track completion or design merit;
[discussion](discussion.md) owns those decisions. Other hosts follow the same
roles and report whether native enforcement was actually available.

When a bounded helper dispatch is denied or times out, the current
target/checkpoint is terminal for that attempt. Do not change agent type, retry,
or mutate the packet to evade the boundary; the main designer keeps authoring the
prototype directly.

## Main tools

Use Read/Glob/Grep and available read-only research/browser tools. Native writes
are Markdown design/research/Review records under the repository's `prototype/`.
All design models, IA plans, and discussion notes MUST be written to the design
record (whether `prototype/discussion.md` or the layered `truth.md`/`world.md`/
`briefs/` set) and canonical `prototype/*.md` artifacts, never to root-level
ad-hoc files such as `DESIGN.md` or left unpersisted in terminal output.
For Bash use one command: `pwd`, `ls`, `cat`, `head`, `tail`, `wc`, `rg` (without a
preprocessor), `git status --short`, `git status --short --branch`, or
`git rev-parse --show-toplevel`. Installed scripts may run by their absolute path:
Node for preview; Python for
handoff.
The bounded token export command in [artifact lifecycle](artifact-lifecycle.md)
is also permitted: absolute retained token source and same-revision JSON output
inside this project's token directory, with no extra arguments or symlink escape.
Shell composition, inline scripts and setup stay out of the main path; author
runnable files with Write/Edit instead of shell redirection. A blocked tool
call is a role/format diagnostic: correct it without seeking another approval
when the underlying design work is already authorized.

## Formal handoff packet

`lint_spec_contracts.py` is a Stage 5 optional handoff lint helper, not a design-time
gate. It validates the canonical Spec IR (schema, tier admission, tokens freshness,
boundary) and is admitted through the execution boundary only when explicitly invoked
with `--root` and `--slice` arguments for formal delivery validation. The legacy
six-piece contract lint is retired: a tree without the compiled IR reports the missing
IR rather than demanding retired files.

Prepare prototype handoff artifacts in the current project with their bounded
scopes, not a separate worktree: packet paths and target evidence belong to this
root. Omit worktree isolation and model overrides unless a higher-priority host
requirement dictates otherwise; if that requirement cannot preserve the packet's
workspace, report the limitation instead of initializing Git or rewriting paths.
Correct dispatch options separately from the prompt; operational explanations
must not be prepended to the packet JSON.

Run handoff.py packet to bind the retained artifact identities. Source digests
and write scopes must match. Draft comparison packets remain supported; this check
neither requires frozen status nor promotes draft sources to approved design.
The packet is a retained constraint record consumed by the direct authoring path
and by downstream harnesses; it is not an order to delegate.

## Direction probe record

Retain the design-language brief in a Markdown research/comparison record. Use
handoff.py digests to obtain its digest, then keep this JSON envelope beside the
probe as its bounded scope record (fill actual values; no appended prose):

```json
{
  "mode": "direction-probe",
  "repository_root": "/absolute/project",
  "skill_root": "/absolute/installed/spec-prototype",
  "probe_id": "direction-name",
  "brief": {"path": "prototype/research/direction-name.md", "sha256": "actual digest without sha256 prefix"},
  "prototype_write_scope": "prototype/experiments/probes/direction-name/",
  "evidence_write_scope": "prototype/evidence/probes/direction-name/"
}
```

The probe needs no Foundation, map, Contract or Specification. Its brief supplies
the provisional question, real content, art direction, viewport and tool policy.
This envelope retains the brief's identity, not a selected design. The main
designer authors the probe inside the declared scopes and returns the bounded
viewport evidence.

This adapter is a native tool boundary, not an OS sandbox: it does not police
external MCP mutations, disabled hooks, omitted/released discussion scope or
arbitrary code within a bounded helper. Keep those capabilities within the stated
scope
and verify actual native behavior before claiming enforcement. Legacy discussion
records need the scope field on resume; absent records do not activate the guard
in unrelated repositories. A helper's file existence cannot prove it ran.

# Native execution boundary

The main designer owns interpretation and Markdown artifacts under `prototype/`;
Builder owns runnable output and operational inspection in its supplied scope.
The native Skill hook persists through the session. Its adapter applies only
where the nearest `prototype/discussion.md` records `Execution boundary: active`.
Initialize that field before design actions; keep it active while awaiting design
answers and throughout building/review. On an actual switch to other work or
finished delivery, record `released`; on design resume, restore `active` before
acting. Releasing is not a workaround for a blocked design action. These are
existing discussion scope facts, not a second approval or Runtime lifecycle.

When no discussion record exists, the adapter permits only the first design
write to `prototype/discussion.md`; other prototype artifacts wait until that
record establishes scope. This prevents silent loss of the canonical resume
record without making the adapter an approval or readiness owner.

The adapter checks native Write/Edit/Bash and helper dispatches. It does not
decide actual-user approval, Track completion or design merit;
[discussion](discussion.md) owns those decisions. Other hosts follow the same
roles and report whether native enforcement was actually available.

When a bounded Builder or Critic dispatch is denied or times out, the current
target/checkpoint is terminal for that attempt. The main designer must retain
the limitation rather than changing agent type, retrying, or mutating the
packet to evade the boundary.

After creating or materially updating `prototype/discussion.md`, the main
designer may run `python3 <skill-home>/scripts/check-discussion.py
<repository-root>`. This is a structural completeness check only; it is not a
readiness gate, approval source, or Runtime lifecycle.

## Main tools

Use Read/Glob/Grep and available read-only research/browser tools. Native writes
are Markdown design/research/Review records under the repository's `prototype/`.
All design models, IA plans, and discussion notes MUST be written to
`prototype/discussion.md` (and canonical `prototype/*.md` artifacts), never to
root-level ad-hoc files such as `DESIGN.md` or left unpersisted in terminal output.
For Bash use one command: `pwd`, `ls`, `cat`, `head`, `tail`, `wc`, `rg` (without a
preprocessor), `git status --short`, `git status --short --branch`, or
`git rev-parse --show-toplevel`. Installed scripts may run by their absolute path:
Node for detect-design-assets, resolve-change and preview; Python for
check-discussion and handoff.
The bounded token export command in [artifact lifecycle](artifact-lifecycle.md)
is also permitted: absolute retained token source and same-revision JSON output
inside this project's token directory, with no extra arguments or symlink escape.
Shell composition, inline scripts, setup and runnable files belong to Builder.
Use native tools to author records instead of shell redirection. A blocked tool
call is a role/format diagnostic: correct it without seeking another approval
when the underlying design/build work is already authorized.

## Formal dispatch

Dispatch prototype helpers in the current project with their bounded artifact
scopes, not a separate worktree: packet paths and target evidence belong to this
root. Omit worktree isolation and model overrides unless a higher-priority host
requirement dictates otherwise; if that requirement cannot preserve the packet's
workspace, report the limitation instead of initializing Git or rewriting paths.
Correct dispatch options separately from the prompt; operational explanations
must not be prepended to the packet JSON.

Run handoff.py packet and use its exact JSON as the Builder prompt, unchanged.
The adapter recomputes that packet before dispatch. Source digests and write
scopes must match. Draft comparison packets remain supported; this check neither
requires frozen status nor promotes draft sources to approved design.

## Direction probe dispatch

Retain the design-language brief in a Markdown research/comparison record. Use
handoff.py digests to obtain its digest, then pass this JSON envelope as the
Builder prompt (fill actual values; no appended prose):

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
This envelope retains the brief's identity, not a selected design. Builder reads
it before implementation and returns the bounded viewport evidence. Critic
dispatch remains a readable review brief, without a build packet.

This adapter is a native tool boundary, not an OS sandbox: it does not police
external MCP mutations, disabled hooks, omitted/released discussion scope or
arbitrary code within a Builder. Keep those capabilities within the stated role
and verify actual native behavior before claiming enforcement. Legacy discussion
records need the scope field on resume; absent records do not activate the guard
in unrelated repositories. A helper's file existence cannot prove it ran.

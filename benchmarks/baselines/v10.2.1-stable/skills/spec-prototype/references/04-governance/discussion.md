# Discussion, authority and convergence

This reference owns dialogue cadence, actual approval/delegation provenance,
working memory and legal exits. It coordinates one Product Experience Model; it
does not impose a visual-first or IA-first waterfall.

## Record and resume

For substantive design work with writes authorized, create
`prototype/discussion.md` before other design artifacts. Keep its Resume section
small and current: execution boundary; active Product Experience Model decision;
route basis; requested scope/stopping point; pending prerequisite with impact and
owner; product/source revision; active artifact/evidence references; next action
and its prerequisite.

If an existing record lacks Resume, prepend the current fields and retain earlier
rationale below. File existence alone is not valid resume state. After a material
update, run `scripts/check-discussion.py <repository-root>` when available; it
checks record shape only.

A review/advice-only request remains read-only unless the user requests a record.
A no-build request can still retain requested Markdown design work. If the user
forbids all file writes, continue conversationally and state that durable resume
and record-scoped enforcement are unavailable.

## Human authority and delegated agency

Human approval must come from an actual user message or accessible approved
source supporting the whole commitment. Retain a short quote or locator, turn/date
when available and exact scope. An Agent reply, tool result, generated receipt,
existing file or successful build is not approval. Split sourced constraints from
added proposals and keep unsupported clauses proposed.

Every identified critical unknown retains one explicit disposition: resolved by an
actual answer, resolved by reliable source evidence, explicitly delegated by the
actual user within named scope, or unresolved with its dependent decisions blocked.
Research accessible facts before asking. Questions must follow dependency order and
include a recommendation, cost and impact; wait for the actual reply, then
recompute remaining and newly exposed unknowns. A partial or ambiguous reply
unlocks only what it covers. Actor, core task, success criteria, business rules,
permissions, object relationships, main journey and direction choices are not
exempted by calling them low-impact, reversible or hypothetical. A generic continue/complete-draft request, one answer, a recommendation or a model-authored
assumption is not blanket delegation. Conditional comparisons may illuminate an
open question, but cannot freeze or implement its dependent direction.

The human owns product-semantic changes, consequential value trade-offs and final
direction. The AI owns professional investigation, synthesis, recommendation,
critique and execution inside delegated scope. Do not ask the user to decide
researchable facts, CSS parameters, page quotas or low-risk reversible details.
Honor explicit delegation and advance without asking for each micro-decision.

Use these statuses without conflation:

- `confirmed`: actual human user selection or approved external source, with scope. Never use for synthetic PRD persona decisions or simulated role actors;
- `synthetic-fixture`: simulated persona, test fixture, or scenario actor approval; carries zero human authority;
- `delegated`: the human authorized AI judgment within a stated scope;
- `proposed`: professional recommendation awaiting authority or evidence;
- `needs-evidence`: inspectable material or observation is missing;
- `needs-decision`: a consequential authority choice blocks dependent work;
- `blocked`: required capability or source is unavailable;
- `superseded`: a retained successor replaced the decision.

## Choose the next move

At each round:

1. Read current sources, settled decisions and evidence relevant to the active
   question.
2. Identify the highest-impact available uncertainty and its owner.
3. Research, model, draft or prototype everything safely resolvable within current
   authority.
4. Present the professional recommendation, material evidence and trade-off.
5. Ask only if a consequential unresolved human choice now blocks the next
   dependent action; otherwise continue through authorized work.
6. Reconcile feedback into the smallest owning decision and preserve unaffected
   facts, approvals and artifacts.

Do not end every turn merely to manufacture participation. A concrete comparison
or high-consequence semantic choice merits a pause; an internal reversible choice
does not. A bare “continue” resumes already authorized work but selects no pending
alternative.

## Routes and legal exits

Routes describe requested stopping points, not stages:

| Route | May produce | Honest exit |
|---|---|---|
| `visual-first` / `visual-only` | product-grounded Design Propositions and specimens while structural work stays connected | selection/delegation, or a provisional recommendation with validation pending |
| `IA-first` / `IA-only` | object/content model, journey and Surface Topology decisions while expression stays connected or explicitly deferred | structural output with expression dependencies explicit |
| `spec-only` | only the requested exact design artifacts | implementation/usability validation explicitly pending; no Builder unless separately requested |
| `review-only` | findings against a supplied target and evidence | professional merit, task evidence and conformance reported separately; no mutation |
| `continuation` / `local-repair` | successor decision or artifact within affected scope | inherited choices retained or the affected owner reopened |

Whole product, journey and surface are scopes layered onto these route preferences;
they are not extra lifecycle states. `visual-first` and `IA-first` name the current
uncertainty, not a required ordering between two design systems.

`needs_decision`, `needs_evidence`, `blocked`, `prototype_blocked` and `unverified`
are dependency/evidence conditions, not fabricated user rejection or approval.
Continue independent work where possible.

## Product-grounded propositions

When a consequential direction is genuinely open, compare enough materially
different propositions to expose the trade-off. One determined answer needs no
invented competitor. Use the same representative content, task, breakpoints and
constraints. Each proposition records:

- product thesis/question and generative mechanism;
- Qualitative Design DNA naming both the combination and its product basis;
- Real-World Mapping source status, local mechanism, translation and non-transfer
  boundary when a reference actually reduces uncertainty;
- focal relationship and concrete specimen;
- familiar convention deliberately retained;
- cross-surface Signature Relationship;
- Signature Craft that makes the relationship perceptible in the specimen;
- benefit, cost and learning burden;
- visual/task evidence or an explicit validation limit;
- falsification question or transfer test.

A style label, adjective set, palette swap or unsupported novelty is not a
proposition. Recommendation is part of the AI's job; final direction remains with
the human or recorded delegation.

## Decision frontier

Keep open decisions with prerequisites, scope, evidence, impact, owner and next
move. Ask only a decision whose prerequisites are settled. Combine questions only
when they are inseparable. Preserve useful uncertainty instead of converting it
into a long intake form.

When two rounds add no useful distinction, change method: research a missing fact,
make an inspectable specimen, walk the task, compare product priorities, or choose
a reversible default within delegation. Do not reroll styles.

## Feedback and recovery

Map feedback to the smallest owner:

- product purpose, role or policy → product source/Product Thesis;
- object, terminology or content relationship → Object/Content Model;
- task continuity, navigation or page boundary → journey/Surface Topology;
- content voice, interaction or appearance → Design Proposition/Foundation;
- implementation defect → Builder repair within exact scope;
- evidence weakness → validation plan or `unverified`.

Mark dependents for reconsideration and retain unrelated decisions. Combining
directions creates a new retained proposition, not an unrecorded mixture. A broad
redesign is justified only when the owning assumption is broad.

## Working memory discipline

Before a formal owner exists, retain the decision in Discussion. After
formalization, link to the authoritative section and keep only status, rationale
and provenance here. Research observations remain in the research record. Frozen
artifacts receive successors; they are never rewritten to simplify resume.

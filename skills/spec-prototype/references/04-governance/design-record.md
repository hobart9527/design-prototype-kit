# Design Record: Layouts, Ledger and Deliverables

The design record is the smallest ledger that lets a truncated run resume and lets a
reviewer judge the work. It records decisions and evidence; it is not a form to fill.
`SKILL.md` routes here; this file owns the layouts and what each carries.

## Deliverable tree

```text
prototype/
├── discussion.md                           # single-record layout; on a layered tree, the resume seam only
├── truth.md                                # layered: product facts, tension, Decisions and authority table
├── world.md                                # layered: visual world and the sole token authority
├── briefs/<slice>.md                       # layered: one slice's surface strategy and evidence
├── specifications/<slice>/r1.spec.md       # the Specification, extracted from what was built
├── shared/tokens.css                       # compiled tokens (written only by compile_tokens.py)
├── contracts/tokens/t1.json                # optional machine export of the same tokens
└── experiments/<slice>/anchor/index.html   # the runnable prototype
```

`compile_tokens.py` 是 `t1.json`（派生包装）的唯一写者；`tokens.css` 在探索期可由设计师直写，一旦进入 Stage 5 编译则以编译产物为准，探索期手写值需先回写至设计记录（`world.md` 或 `discussion.md`）。

## Two layouts, one loading seam

Every reader loads the record through `read_design_record(root, slice_id)` in
`spec_contract_blocks.py`. Pick one layout per project and stay in it.

- **single-record** — one `prototype/discussion.md`, partitioned by lifecycle heading:
  product truth, the shared visual world, then one `## Slice: <slice_id>` block per slice.
  The **Decisions and authority** table lives in this file.
- **layered** — `truth.md` (product facts, tension, the **Decisions and authority** table —
  approval is product-scoped, so the freeze-approval rows live here) + `world.md` (visual
  world; sole token authority) + `briefs/<slice_id>.md` (this slice's strategy and evidence).
  `discussion.md` narrows to a resume seam (`templates/discussion-seam.md`, ≤30 lines) that points at the three and carries no Decisions rows.

A partitioned record owes each slice exactly one block; the seam reports an absent or
doubled block rather than compiling another slice's viewports and states into this one.
Templates: `templates/discussion.md` (single-record) or `templates/truth.md` +
`templates/world.md` + `templates/briefs/_slice.md` (layered).

Read discipline on a layered tree: Frame reads `truth`; Propose reads `truth` + `world`;
Make and Look read `world` + the current brief.

## Machine-read blocks

States, stress fixtures, invariants, required states, viewports, actions, axes, craft,
tokens and meso lists are declared in fenced `contract:<kind>` YAML blocks. The block is
authoritative and fails closed; prose forms are a compatibility route for older records.
The registry of kinds and fields is owned by [`machine-contract.md`](machine-contract.md).

## What makes a delivery evaluable

The record carries two blocks, authored for the person who will open the artifact and
updated as evidence arrives:

- **Success metrics** — how the work is judged: product outcomes with an observation
  method, never "the prototype exists".
- **Reviewer's evaluation guide** — what to attempt first, the deciding questions, what
  would count as failure, known limitations, and what each verdict means.

Keep `explicit`, `observed`, `derived`, `hypothesis` and `unknown` distinctions visible.

## Specification shape

The Specification uses the `google-design-md/v2` Markdown contract (YAML frontmatter plus
semantic sections for problem/drivers, experience direction, spatial anatomy, states and
actions, resilience/invariants), whose parser-compatible shape is defined by
[`../spec-md-contract.md`](../spec-md-contract.md). It is this Skill's Google
Design.md-inspired format, not an official Google standard. Write only the sections the
requested scope needs.

## Downstream engineering assets

1. `tokens.css` + `contracts/tokens/t1.json` — DTCG tokens for colour, spacing, radii,
   type and elevation.
2. `r1.spec.md` — component topology, state machines and accessibility invariants.
3. `index.html` — self-contained, accessible, interactive, translatable into production components.

## Ownership and boundary

Durable design decisions live in the design record, never in a root-level design document
or `prototype/README.md`. A discussion-only request creates no runnable prototype; keep the
outcome in the record when the repository workflow requires a durable artifact.

The native hook (`execution_boundary.py`) bounds writes to `prototype/`. Hook permission is
never evidence that a design decision is correct or approved.

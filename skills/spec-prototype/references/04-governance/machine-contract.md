# Machine Contract: One Declaration, One Authority

> The compiler reads a small set of lists as fact. Each has exactly one
> authoritative form — a fenced `contract:<kind>` YAML block — and one prose form
> kept only for records that predate it. This file states the rule and the
> registry. `compile_spec_ir.py` is the sole parsing authority; it is not a
> second specification of the formats, which live in the blocks below. The block
> loader and its admit checks live in `scripts/spec_contract_blocks.py`, and
> `compile_spec_ir.py` re-exports every name from it — the prose parsers and the
> block registry are two halves of one contract, so a change to one is a change
> to both.

## The deliverable tree and the record that fills it

This file is the sole owner of the canonical deliverable paths and the
`contract:<kind>` schema. Other references name the object they need or link
here; they do not restate the tree.

```text
prototype/
├── discussion.md                           # single-record layout; on a layered tree, the resume seam only
├── truth.md                                # layered: product facts, tension, Decisions and authority table
├── world.md                                # layered: visual world and the sole token authority
├── briefs/<slice>.md                       # layered: one slice's surface strategy and evidence
├── specifications/<slice>/r1.spec.md       # the Specification view, rendered from the compiled IR
├── contracts/compiled/<slice>/r1.spec.json # the canonical Spec IR (compiled from the design record)
├── shared/tokens.css                       # compiled tokens (written only by compile_tokens.py)
├── contracts/tokens/t1.json                # optional machine export of the same tokens
├── experiments/<slice>/anchor/index.html   # the runnable prototype (index.html + anchor.css + anchor.js)
├── evidence/<slice>/<revision>/            # captured viewport evidence
└── reviews/<slice>/<revision>.md           # optional review receipt
```

Token authority has one source: the design record (`world.md` or `discussion.md`). `compile_tokens.py` is the sole writer of `tokens.css` and `t1.json`. Any exploratory token adjustment, including a direction probe's local values, is first recorded in the source record, then materialized by rerunning `compile_tokens.py`. Probe-local values do not promote automatically; only values explicitly adopted by the selected direction are copied into the source record. Stage 5 uses the compiled artifacts as-is. This rule does not change `compile_tokens.py` behavior.

## Two layouts, one loading seam

Every reader loads the record through `read_design_record(root, slice_id)` in
`spec_contract_blocks.py`. Pick one layout per project and stay in it.

- **single-record** — one `prototype/discussion.md`, partitioned by lifecycle heading:
  product truth, the shared visual world, then one `## Slice: <slice_id>` block per slice.
  The **Decisions and authority** table lives in this file.
- **layered** — `truth.md` (product facts, tension, the **Decisions and authority** table —
  approval is product-scoped, so the freeze-approval rows live here) + `world.md` (visual
  world; sole token authority) + `briefs/<slice_id>.md` (this slice's strategy and evidence).
  `discussion.md` narrows to a resume seam (≤30 lines) that points at the three and
  carries no Decisions rows; `truth.md` carries its own `## Resume` block.

A partitioned record owes each slice exactly one block; the seam reports an absent or
doubled block rather than compiling another slice's viewports and states into this one.
Templates: `templates/discussion.md` (single-record) or `templates/truth.md` +
`templates/world.md` + `templates/briefs/_slice.md` (layered).

Read discipline on a layered tree: Frame reads `truth`; Propose reads `truth` + `world`;
Make and Look read `world` + the current brief.

### What makes a delivery evaluable


The record carries two blocks, authored for the person who will open the artifact and
updated as evidence arrives:

- **Success metrics** — how the work is judged: product outcomes with an observation
  method, never "the prototype exists".
- **Reviewer's evaluation guide** — what to attempt first, the deciding questions, what
  would count as failure, known limitations, and what each verdict means.

Keep `explicit`, `observed`, `derived`, `hypothesis` and `unknown` distinctions visible.

### Specification shape


The Specification uses the `google-design-md/v2` Markdown contract (YAML frontmatter plus
semantic sections for problem/drivers, experience direction, spatial anatomy, states and
actions, resilience/invariants), whose parser-compatible shape is defined by
[`../spec-md-contract.md`](../spec-md-contract.md). It is this Skill's Google
Design.md-inspired format, not an official Google standard. Write only the sections the
requested scope needs.

### Ownership and boundary


Durable design decisions live in the design record, never in a root-level design document
or `prototype/README.md`. A discussion-only request creates no runnable prototype; keep the
outcome in the record when the repository workflow requires a durable artifact.

The native hook (`execution_boundary.py`) bounds writes to `prototype/`. Hook permission is
never evidence that a design decision is correct or approved.

## Why the block is authoritative

The prose form infers a machine value from a human sentence with a regular
expression. Every defect found in this class was a silent mis-parse (a sentence
became a declaration) or a silent drop (a declaration was not admitted and the
field stayed empty). The block removes the inference: the author states the
value, the compiler reads it, and an authoring error fails at the line that
caused it instead of surfacing stages later at the `execution_spec` boundary.

## The registry

Each kind is one YAML document. A kind's fields are required unless marked
optional. Unknown keys, unknown enum values and duplicate ids fail closed.

| Kind | Value | Required per entry |
|---|---|---|
| `contract:states` | list of mappings | `id` (`domain/…`, `interaction/…`, `data/…`); `description` for `domain/` and `data/`, optional for `interaction/`; `label` optional |
| `contract:stress` | list of mappings | `id` (`stress/…`), `vector`, `expected` |
| `contract:invariants` | list of mappings | `id` (`inv/…`), `statement`; `severity` ∈ `blocking\|warning\|advisory` (default `advisory`), `verification` ∈ `computed_style\|dom_query\|screenshot_review\|manual` (default `manual`), `applies_to` optional |
| `contract:required_states` | list of scalars | each a state id, at least one |
| `contract:viewports` | list of scalars | each a width in px, 200–4000 |
| `contract:actions` | list of mappings | `id`, `verb`, `trigger`, `commit`; `proximity_level` optional (default 1), `authority` (or alias `evidence_source`) ∈ `explicit\|derived\|proposed\|hypothesis` (default `derived`), `feedback`/`consequence` optional |
| `contract:axes` | mapping | any of `density`, `energy`, `materiality`, `rhythm`, `character`; legacy aliases `weight`/`finish` → `materiality`, `seriousness` → `character`; optional override `radius_outer` (int 0–32, px) |
| `contract:craft` | mapping (optional) | `surface_optics`: `neutral`, `coated_instrument_dark`, `frosted_acrylic_40`, `grain_*`; `spatial_geometry`: `neutral`, `concentric-nested`, `soft_bento_pill`, `cut-corner`, `square`; `micro_typography`: `neutral`, `tabular-numeric`, `tight_display_polarized`, `oldstyle_*`; `data_marks`: `native`, `micro-trend-compact`, `hatching_dither` — a design-judgment projection, never required for a compile |
| `contract:tokens` | mapping | `accent_seal` (hex), `accent_policy` (text), optional `state_nominal`, `state_warning`, `state_danger`, `state_success`, `state_info` (hex; `state` aliases `state_nominal`) |
| `contract:meso` | mapping (optional) | any of `massing_pattern`, `kinematics`, `data_syntax` — a design-judgment projection, never required for a compile |

`contract:craft` and `contract:meso` are projected into the IR
(`foundation.craft_stack`, `layout_directives.massing_pattern`,
`interaction_spec.kinematics`, `visual_directives.data_syntax`) but nothing
downstream verifies them, so they carry no weight in the stage-boundary gate.
Treat them as optional design judgment — author them when they sharpen a
decision, never as a form to fill. The machine-required kinds are `states`,
`required_states`, `actions`, `invariants`, `viewports`, `axes` and `tokens`.

A YAML value containing `: ` or beginning with a special character must be
double-quoted, or the loader reads it as structure and the block fails to parse.

## Scope

The same partitioning rule applies to a block as to the rest of the record: a
block inside a `## Slice: <id>` block belongs to that slice, a block in a shared
zone is product-level. `--slice <id>` reads the shared zones plus that slice's
block, so one slice's states never leak into another.

## The prose route

A record that predates the blocks is still read by the prose parsers, and the
admission rules are stated once, in `stage-1-frame.md`. That route is
compatibility, not recommendation. A machine-shaped bullet that names a contract
token but matches no admission rule is reported as an unadmitted declaration and
aborts the compile: the author wrote a declaration the compiler did not read, and
the line that caused it is named rather than dropped.



### Two stage axes, distinct semantics (F7 口径声明)

Do not conflate these two vocabularies:

- **Frontmatter `build_scope` (build-scope axis; legacy alias `stage`)**: uses the `hero_probe | walking_skeleton | surface_slice | full_product` family. This axis describes *how much product this slice builds* and is consumed directly by `compile_spec_ir.py` and `schemas/prototype-spec.v1.json`.
- **Resume checkpoint (progress axis, in the `## Resume` block)**: uses the `stage1-contract | stage2-probe | stage3-skeleton | stage4-audit | stage5-freeze` family and it describes *where in the 5-Stage delivery pipeline this pass stands*.

No primary enum from the frontmatter table coincides with the Resume checkpoint names: they name different things and are never interchangeable.

### Two registers named `authority`, distinct semantics

`authority` names two different registers. They never appear in the same slot and
are never interchangeable:

- **Spec identity authority** (`identity.authority_status` in
  `schemas/prototype-spec.v1.json`; `authority` in the slice frontmatter):
  `draft | sealed_provisional | validated | frozen_approved`. It records how far a
  *slice specification* has advanced toward frozen delivery.
- **Action evidence authority** (`actions[].authority`): `explicit | derived |
  proposed | hypothesis`. It records how an *individual declared action* was
  grounded.

The **evidence ladder** is a third, separate vocabulary —
`explicit > observed > derived > hypothesis > unknown` (owned by
`references/core-kernel.md` §4) — and it is the ordering the semantic judge reads.
The decision row status `proposed | provisional | confirmed | delegated | needs-evidence | superseded`
is a fourth (owned by `references/core-kernel.md` §4, same as the evidence ladder).
Do not read one register's value as another's.

## Change rule

A format change updates the block, the parser, the registry table above and the
shipped template together. The test suite compiles the template strict, so a
template that teaches a form the parser does not admit fails the build rather
than the author's Stage 5.


## Slice Frontmatter Registry

The YAML frontmatter of `templates/briefs/_slice.md` and the slice block defines the surface attributes:

| Field | Type | Allowed Values / Description |
|---|---|---|
| `spec_schema` | string | `"google-design-md/v2"` |
| `slice_id` | string | Target slice identifier (must match filename without `.md`) |
| `authority` | string | `draft` \| `validated` \| `sealed_provisional` \| `frozen_approved` |
| `build_scope` (preferred frontmatter key) / `stage` (legacy alias) | string | `hero_probe` \| `walking_skeleton` \| `surface_slice` \| `full_product` — both input keys map to the IR's `scope.build_scope.stage`; if both are present, `build_scope` wins. The shipped templates use `build_scope: "hero_probe"` (a legal Stage-1 starting value). Neither is the Resume checkpoint vocabulary below. |
| `viewports` | list of ints | e.g. `[390, 1280]` |
| `required_states` | list of strings | Verified state IDs for this slice |
| `applied_methods` | list of strings | e.g. `action-verb-lifecycle`, `context-preservation`, `dense-operational-console`, `progressive-disclosure` |
| `primary_surface` | string | Primary operational surface id |
| `declared_surfaces` | list of strings | Declared surfaces within this slice |

> Note: the machine-contract registry field names the build-scope axis; the frontmatter
> example value `build_scope: "hero_probe"` is the shipped-legal starting point (the same
> enum lives in `schemas/prototype-spec.v1.json:109` and is consumed by
> `compile_spec_ir.py`), not a mistaken primary enum leak.

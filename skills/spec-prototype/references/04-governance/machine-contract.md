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
| `contract:actions` | list of mappings | `id`, `verb`, `trigger`, `commit`; `proximity_level` optional (default 1), `authority` ∈ `explicit\|derived\|proposed\|hypothesis` (default `derived`), `feedback`/`consequence` optional |
| `contract:axes` | mapping | any of `density`, `energy`, `materiality`, `rhythm`, `character`; legacy aliases `weight`/`finish` → `materiality`, `seriousness` → `character` |
| `contract:craft` | mapping | any of `surface_optics`, `spatial_geometry`, `micro_typography`, `data_marks` |
| `contract:tokens` | mapping | `accent_seal` (hex), `accent_policy` (text) |
| `contract:meso` | mapping | any of `massing_pattern`, `kinematics`, `data_syntax` |

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

- **Frontmatter `stage` (build-scope axis)**: uses the `hero_probe | walking_skeleton | surface_slice | full_product` family. This axis describes *how much product this slice builds* and is consumed directly by `compile_spec_ir.py` and `schemas/prototype-spec.v1.json`.
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
The decision row status `proposed | provisional | confirmed` (owned by
`stage-1-frame.md`) is a fourth. Do not read one register's value as another's.

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
| `stage` (build-scope axis, frontmatter) | string | `hero_probe` \| `walking_skeleton` \| `surface_slice` \| `full_product` — the shipped template initial value is `hero_probe` (a legal Stage-1 starting value); a different axis from the Resume checkpoint vocabulary below. |
| `viewports` | list of ints | e.g. `[390, 1280]` |
| `required_states` | list of strings | Verified state IDs for this slice |
| `applied_methods` | list of strings | e.g. `action-verb-lifecycle`, `context-preservation`, `dense-operational-console`, `progressive-disclosure` |
| `primary_surface` | string | Primary operational surface id |
| `declared_surfaces` | list of strings | Declared surfaces within this slice |

> Note: the machine-contract registry field names the build-scope axis; the frontmatter
> example value `stage: "hero_probe"` is the shipped-legal starting point (the same
> enum lives in `schemas/prototype-spec.v1.json:109` and is consumed by
> `compile_spec_ir.py`), not a mistaken primary enum leak.

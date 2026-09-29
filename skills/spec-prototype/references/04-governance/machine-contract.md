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

## Change rule

A format change updates the block, the parser, the registry table above and the
shipped template together. The test suite compiles the template strict, so a
template that teaches a form the parser does not admit fails the build rather
than the author's Stage 5.

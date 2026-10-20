---
spec_schema: "google-design-md/v2"
slice_id: "<slice_id>"
authority: "draft"
build_scope: "hero_probe"
applied_methods: []
primary_surface: "<surface-id>"
declared_surfaces: ["<surface-id>"]
---

# Surface brief — <slice_id>

Layered layout: this file owns one slice's surface strategy and evidence. The
frontmatter `slice_id` must equal the file's basename (without `.md`) —
`compile_spec_ir.py` refuses to compile a brief whose frontmatter and filename
disagree.

The shared world lives in `prototype/world.md`; product truth and decision
provenance live in `prototype/truth.md`. Do not restate either here.

## Spatial Anatomy & Surface Topology

- **Primary Operational Surface**: `surfaces/<slice_id>-main`
- **Contextual Surface**: (optional — drawer, panel, detail)
- **Supporting / Glance Surface**: (optional — mobile read-only, audit, etc.)

## State Taxonomy & Action Lifecycle

Stage 1 names the state classes and the atomic action verbs in prose. The machine
forms — `contract:states`, `contract:actions`, `contract:viewports`,
`contract:invariants`, `contract:stress`, `contract:required_states` — are authored
here once the slice reaches Stage 3, in the shape
[`../../references/04-governance/machine-contract.md`](../../references/04-governance/machine-contract.md)
registers. A block copied from that registry parses; a block with a placeholder value
in an enum slot (a `severity: a | b | c` menu left as written) fails closed at the line
that caused it.

A stress vector the user's brief did not state is the designer's own derivation:
record it in the Decisions table as `hypothesis`, never as `confirmed`.

## Evidence & reviewer's evaluation guide

Written for the person who will open the artifact. State what to attempt first,
what would count as failure, known limitations, and what each verdict means.

- **What to do first**: <exact path to the artifact + the one task to attempt>
- **What to check**: <3-5 deciding questions, in priority order>
- **What would make this fail**: <specific, observable failure conditions>
- **Known limitations**: <what is deliberately unimplemented, simplified, or
  `[hypothesis]`>
- **Verdict options**: <what "accept" / "accept with changes" / "reject" mean
  here>

## Evidence and changes

- Research and review links:
- Facts / expert judgments / preferences / hypotheses / observations:
- Unverified assumptions and bounded implementation freedoms:
- Feedback received and owning node changed:
- Decisions explicitly reopened:
- Unaffected provisional decisions carried forward:

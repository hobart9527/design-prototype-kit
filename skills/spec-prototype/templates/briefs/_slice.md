---
spec_schema: "google-design-md/v2"
slice_id: "<slice_id>"
authority: "draft"
stage: "hero_probe"
viewports: [390, 1280]
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

```contract:states
- id: domain/<id>
  label: <label>
  description: <one-line semantics>
- id: interaction/<id>
  description: <one-line interaction semantics>
- id: data/<id>
  description: <one-line data-scenario semantics>
```

```contract:actions
- id: action-<name>
  verb: <atomic verb>
  trigger: <key | click | gesture>
  proximity_level: <0-4>
  commit: <what commits>
  consequence: <what is at stake, if destructive>
  feedback: <what the user sees>
```

## Viewports & required states

```contract:viewports
- 390
- 1280
```

Add a `required_states:` frontmatter list, or a `contract:required_states` block, only
with the state ids this slice will actually verify. Leave it out during exploration until
they are known; before Turn 3 finalization and Stage 5 freeze this section must be filled,
as freeze fails closed and lists missing items if left unauthored.

## Verifiable Invariants & Break Protocol

```contract:invariants
- id: inv/<id>
  statement: "<assertion>"
  severity: blocking | warning | advisory
  verification: computed_style | dom_query | screenshot_review | manual
```

```contract:stress
- id: stress/<id>
  vector: "<what breaks>"
  expected: "<how the surface responds>"
```

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
- Unaffected decisions and approvals preserved:

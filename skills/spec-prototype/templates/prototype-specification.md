# Prototype Specification: <slice-id> / <revision>

> Immutable execution contract compiled from exact retained sources. Selection and
> approval live outside this file; any consequential change creates a successor.

Reference fields use one backticked repository-relative path and
`sha256:<64 hex digits>` from `scripts/handoff.py digests`. Finish source writes
before compilation.

## Identity and source digests

- Candidate / selected revision: `<revision>`
- Compilation status: `candidate` (selection/supersession is recorded externally)
- Product source references (including Change ID when applicable):
- Product record revision and digest:
- Foundation revision and digest:
- Token artifact path, revision, and digest:
- Slice Contract revision and digest:
- Decision/Discussion record reference:
- Supersedes / selected from:

## Shared authority

- Design Envelope: use the exact Slice Contract revision above.
- Product Experience Model and Surface Topology: use exact references transitively retained by Contract/Foundation.
- Open decision resolved by this candidate:
- Shared fields copied into this file: `none`

Do not repeat product meaning, topology, global expression or shared checks here.
Exact references preserve the rationale chain without creating another authority.

## Candidate resolution

- Candidate label:
- Candidate-specific consequential difference, or `none — determined direction`:
- Affected topology, interaction or expression decisions only:
- Design Proposition fields changed, if any:
- Benefit, trade-off, learning burden and falsification/transfer test:
- Delegated-only variations that may change between executions:

## Builder contract

Reference Contract-owned surfaces, journeys, applicable states, shared fixtures and
checks by anchor. Add only execution-specific values or delegated unknowns.

- Repository root:
- Prototype write scope: `prototype/experiments/<slice-id>/<revision>/`
- Evidence write scope: `prototype/evidence/<slice-id>/<revision>/`
- Stack inheritance or standalone rationale:
- Dependency / registry access already authorized, installation scope and constraints:
- Browser verification route and observed availability (or unknown):
- Skill root / evidence template path for this dispatch:
- Required craft reads: one `references/<file>.md`, sha256:<actual digest> per applicable lens the Designer consulted; an unbound or unread-declared entry fails the packet lint
- Start command:
- Verification command(s):
- Visual verification: `required | not_required`
- Required screenshot checkpoints:
- Page/flow coverage and shared data references:
- Delegated implementation freedoms:
- Component constraints:

| Surface / interaction | Existing asset | Disposition | Constraint | Verification checkpoint |
|---|---|---|---|---|
| | | `required | preferred | delegated | unavailable` | (Include mechanism + applicable Stress Boundary) | |

Reserve `required` for mandatory reuse of a named asset with a constraint and
checkpoint. `preferred` permits a constraint-preserving equivalent. `delegated`
leaves component choice to Builder but still states constraint and checkpoint.
`unavailable` records a known boundary. Empty execution fields or undecided
markers fail packet lint; preserve an older immutable file and author a successor.

When a component embodies a physical, optical, biomorphic, temporal, or real-world domain mapping, the `Constraint` column must specify that mapping concretely and verifiably — as an observable behavior, measurable property, or implementable mechanism — not as a literary adjective. Examples:
- A kinetic scrubber: state the damping curve, detent threshold distance, and release behavior.
- An optical substrate: state the luminance response curve, chromatic adaptation rule, or contrast ratio target.
- A biomorphic expansion: state the growth rate function, boundary conditions, and collapse trigger.
- A standard platform control: state the applicable component convention, state variants, and accessible behavior requirements.
The test: a Builder reading this constraint must be able to implement it without guessing the designer's intent.

Every `required` assertion in the retained Foundation's Verifiable Design
Assertions must have a corresponding Verification checkpoint in this table (a
checkpoint may cover multiple assertions only when it observes them together).
Checkpoints must not silently cover fewer assertions than the Foundation
requires; a missing coverage is an unresolved decision, not a delegated detail.

**Stress Boundary format and contract**: for components handling variable content
or operational risk, write the boundary directly into the `Constraint` cell
(e.g., `Mechanism: [...]; Stress: unbreakable long string & empty state`).
Applicable worst-case classes: unbreakable strings (no-wrap), empty/zero-item
state (must show next action, never a blank canvas), maximum/awkward data density,
narrow-viewport reachability (320px / 200% zoom), and text expansion (~40% i18n).
Each declared Stress Boundary requires a matching runnable check in the
`Verification checkpoint` column (render the long string, load zero items,
inspect 320px). A Stress claim without a runnable check is treated by Critic as
uncovered.

- Validation status: `pending | observed` (link actual evidence)
- Maximum operational repair attempts: `2`
- Forbidden writes: product sources, OpenSpec, Foundation, Surface Map, tokens,
  Contract, Specification, production source, Git or delivery state.

## Dual-Channel Ergonomics & Platform Key Sovereignty (快捷键与原生按键主权)

Native browser keys are strictly protected: `Space` is permanently reserved for natural scrolling/input; `Tab` for focus chains. Global shortcuts employ disambiguated modifier combos.

| Shortcut Key | Target Action / Interaction | Scope | Focus Restoration Anchor |
|---|---|---|---|
| `Cmd/Ctrl + K` or `Alt + /` | Search / Navigation Palette | Global workspace | Return to previous focal container |
| `Esc` | Dismiss overlay / floating popover | Active overlay | Restore focus to originating trigger |
| `J` / `K` (when not in input) | Item / Outline navigation | Active list or document | Update active anchor without scroll jitter |

## The Break Protocol Stress Checkpoints (四维破坏性极限压测)

| Reality Breaker | Concrete Test Vector / Input | Expected Graceful Behavior | Observed Result |
|---|---|---|---|
| **Unbreakable String** | Authentic 45+ char title or compound path | CSS ellipsis / break-word, zero container blowout, no fake hash UI litter | `pending` |
| **Zero-Item Empty State** | 0 records / empty cluster filter | Actionable empty card with recovery button | `pending` |
| **Extreme 320px Fold** | 320px viewport width test | Horizontal scroll or vertical reflow, primary action reachable | `pending` |
| **Rapid Interruption** | Double-click / rapid Space hits | Debounced submission, single idempotency state transition | `pending` |

## Verifiable Design Assertions

| Assertion | Expected | Observed |
|---|---|---|
| | pass | |

## Review context

- Recommendation and professional-design evidence at compilation:
- Required task, transfer and applicable-state evidence:
- Required reachable-control closure (state → every enabled consequential action/exit, including cancel/close → re-entry where present):
- Responsive/accessibility strategy reference:
- Decision record path (selection, approval and later evidence are recorded there):

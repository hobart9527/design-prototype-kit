# Prototype Evidence: <slice-id> / <prototype-revision>

- Consumed required reads (exact path/digest identities; probe brief for a probe):
- Prototype Specification revision and digest:
- Product/Foundation/Surface Map/Contract rationale chain confirmed:
- Prototype path:
- Evidence identity (target / source / dependency revision bound to every capture):
- Status: `verified | prototype_blocked`
- Repair attempts:
- Human selection / approval / usability testing: separate referenced evidence, or pending.
- Inherited human/visual status from a prior revision: only valid while the evidence identity is
  unchanged; any target, source or dependency change resets it to `pending_review`.

## Implementation map and capability preflight

| Surface / interaction reference | Component and source | Reuse/adaptation | Semantic tokens/applicable states | Verification checkpoint | Required-obligation observation |
|---|---|---|---|---|---|
| | | | | | |

- Actual stack, assets and browser runner inspected:
- External source/version/license/dependency references:
- Service/tool actually used, authorized scope and substitutions:
- Synthetic fixture identity, schema/source basis, explicit synthetic label and reset scope:
- Blockers versus delegated implementation choices:

The implementation map proves structural coverage only. It does not prove
comprehension, rendered quality, behavior, creative merit or approval.

## Run evidence

- Install/start command and result:
- Verification commands and results:
- Runtime location:
- Diagnostics and raw-output paths:
- Browser launch result:
- Capture metadata reference (runner, `browser_execution`, runtime, target platform, dependency identity):
- Native-platform validation actually performed (or `unverified` for each declared platform not run):
- Capture failures and their explicit status (never recorded as passing evidence):

## Surface, journey and state coverage

| Required source/Surface Map/Contract reference | Surface/transition/state | Implementation path | Expected → observed | Evidence path | Result |
|---|---|---|---|---|---|
| | | | | | `pass | fail | unverified | n/a` |

Account for all requested surfaces and **applicable** states, including unbuilt
coverage. Record exclusion reasons. Required fail/unverified entries block
`verified`; do not invent states to fill a universal matrix.

## Environment, simulation and dependency boundaries

| Aspect | Declared source | Actual environment observed | Evidence reference | Result |
|---|---|---|---|---|
| Execution environment (runtime, browser engine, shell, device/emulator) | | | | `pass | fail | unverified | n/a` |
| Simulated versus real service, data and platform | | | | `pass | fail | unverified | n/a` |
| Dependency identity and whether its change invalidates prior evidence | | | | `pass | fail | unverified | n/a` |

A declared platform that was not actually executed stays `unverified`; a browser render
never stands in for native-platform validation. A changed dependency invalidates the
evidence bound to its prior revision; unaffected dependencies remain reusable.

## Behavioral and continuity evidence

| Task/case | Action reference | Steps and fixture | Observation reference | Expected object/state/feedback | Observed result and retained context | Evidence path | Result |
|---|---|---|---|---|---|---|---|
| Primary task | | | | | |
| Transfer / contrasting case | | | | | |
| Applicable interruption/recovery/return | | | | | |

For asynchronous or cross-surface work, retain the actual event sequence through
settlement and next action. Endpoint screenshots alone do not prove the path.

## Reachable-control closure

| Required reached state | Visible enabled action/exit | Source disposition | Action and re-entry sequence | Observed next state, cleanup and focus/context | Evidence | Result |
|---|---|---|---|---|---|---|
| | | `required | exploratory | out_of_scope` | | | | `pass | fail | unverified | n/a` |

Exercise every required enabled consequential branch. Include cancel/close and
then reopen before a later submit/retry where those controls coexist. A visible
enabled no-op, stale state or unexercised required branch blocks `verified`.

## Render, expression and accessibility evidence

| Viewport/mode/state | Screenshot/trace path | Hierarchy and Signature Relationship observation | Content/type/color/imagery/component/motion observation | Keyboard/focus/screen-reader/reduced-motion observation | Result |
|---|---|---|---|---|---|
| | | | | | |

## Design assertions and exceptions

| Foundation assertion/probe requirement and clause | Required/exploratory | Expected relationship → actual observation | Exact trace/measurement | Result |
|---|---|---|---|---|
| | | | | `pass | fail | unverified | n/a` |

Trace/measurement names a falsifiable anchor: a command, a retained artifact path, or a
measured value with a unit. A check that could not fail for the asserted risk is not
evidence, and a passing mechanical gate does not stand in for an unbound assertion.
`scripts/check-assertions.py --foundation <path> --evidence <path>` enforces this.

- Reachable-control closure (cancel/close/retry/reset paths exercised and clean): `pass | fail | n/a`
- Design merit claims left for professional review:
- Quality-baseline exceptions and scope reasons:
- Checks not executed, missing capability and affected requirements:
- Exploratory failures retained as learning:

## Blocked result

- Failure:
- Cause hypotheses and changed observation per attempt:
- Preserved partial artifacts:
- Minimum next action and owning layer:

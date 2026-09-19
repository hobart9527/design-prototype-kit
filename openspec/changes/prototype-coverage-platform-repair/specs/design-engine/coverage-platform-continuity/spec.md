## Purpose

Correct the coverage, platform, evidence and handoff seams of the design engine so that an authored scope is admitted, verified, completed and frozen on the facts it actually declares.

## ADDED Requirements

### Requirement: CPC-002 Choose coverage from an informed map
The engine SHALL resolve the requested implementation scope from the current Surface Map and SHALL retain it with its map revision, selected surfaces and journeys, target contexts and its coverage mode. Formal entry SHALL admit a `full-product` selection as an authorization over every applicable surface of the bound map revision rather than treating its unlisted surfaces as a widened selection. Formal entry SHALL compare the retained map identity against the authored map so that a changed revision or content digest prevents dispatch. An empty selected coverage SHALL remain an error; missing, invalid or stale selections SHALL NOT default to full-product.

#### Scenario: CPC-SCN-003 Concrete recommendation and selection
- **WHEN** scope is undecided and the map supports both representative review and a complete task flow
- **THEN** recommendations distinguish those concrete combinations and full-product coverage; the chosen combination is retained and a dependency needed outside it is disclosed rather than silently added

#### Scenario: CPC-SCN-004 Scope survives continuation without expansion
- **WHEN** the user already selected a subset or explicitly requested full-product and the session resumes
- **THEN** the matching retained selection is reused; ambiguous, invalid or revision-mismatched selections require reconciliation rather than guessing or reauthorizing all pages

#### Scenario: CPC-SCN-018 Full-product selection admits every applicable surface
- **WHEN** a retained selection declares `full-product` coverage and lists no individual surfaces
- **THEN** the formal entry admits the dispatch, the assembled envelope targets every applicable surface of the bound map revision, and no surface is reported as an unauthorized widening

#### Scenario: CPC-SCN-019 Retained map identity is enforced at dispatch
- **WHEN** the authored map revision or content digest differs from the retained selection's map identity
- **THEN** dispatch is refused with the specific mismatch, whether the selection is `full-product` or `selected`, and the refusal mutates no artifact

#### Scenario: CPC-SCN-020 Empty selected coverage stays refused
- **WHEN** a selection declares `selected` coverage and lists no surface
- **THEN** formal entry refuses the dispatch instead of degrading it to full-product

### Requirement: CPC-005 Bind platform claims to evidence
Builder and Critic SHALL assess selected tasks against their applicable platform contract. The projected envelope SHALL expose platform facts under the field names the role instructions name, so that a role can resolve a surface's applicable platform context and compare recorded capture metadata against the environment the evidence was bound to. Evidence SHALL identify target revision, surface/journey, actual execution environment, performed action, observation and simulation limits. Required behavioural or native-platform claims without supporting evidence SHALL remain unverified; HTML simulation SHALL NOT pass a native behaviour requirement.

#### Scenario: CPC-SCN-009 Narrow screenshot is not mobile completion
- **WHEN** a 390px screenshot exists but required touch, navigation, keyboard or recovery behavior was not exercised
- **THEN** capture is reported separately and the untested requirements remain unverified; HTML simulation does not pass native behavior requirements

#### Scenario: CPC-SCN-021 Role instructions name the fields the projection emits
- **WHEN** a Builder or Critic resolves the platform context for a selected surface
- **THEN** the instruction names only fields the projection actually emits, states how applicability is resolved from the authored facts, and does not refer to an unprojected platform field

### Requirement: CPC-006 Execute and report the selected scope
The engine SHALL use one batch execution and completion mechanism for selected and full-product coverage. Completion SHALL be withheld when the resolved scope is unusable, and the withholding SHALL name the governing scope error. Scope membership, delivery entry and evidence outcomes SHALL remain separate facts. Review views SHALL reconcile authored scope with delivery and evidence, and SHALL NOT render a met completion for a scope that implements nothing. Blockers or deferred labels SHALL NOT discharge obligations without an explicit scope change.

#### Scenario: CPC-SCN-011 Subset and first batch remain bounded
- **WHEN** three of ten surfaces are selected and only the first surface currently exists
- **THEN** pending sibling links are not required, the three-surface obligations remain visible, the other seven are outside this round, and completion is withheld until the selected obligations are met

#### Scenario: CPC-SCN-022 Unusable scope withholds completion everywhere
- **WHEN** the resolved scope is unusable, such as a selected coverage that names no surface
- **THEN** the obligation reconciler withholds completion and attaches the governing scope error, the quality check fails rather than passing, and the generated review portal does not present a met completion

#### Scenario: CPC-SCN-023 Well-formed scope is unaffected
- **WHEN** the scope is a well-formed selected coverage or an authorized full-product coverage
- **THEN** reconciler, quality check and portal behave exactly as before and unrelated verification failures are still reported

### Requirement: CPC-007 Preserve precise handoff integrity
Freeze and downstream admission SHALL bind exact scope, source revisions and evidence limits. Approval SHALL refer to an actual approval or explicit delegated-authority source, not an arbitrary matching phrase. Strict packet failures SHALL NOT downgrade to permissive admission. A spec-only approval SHALL freeze a design specification without a built prototype artifact and SHALL keep implementation, platform and production validation explicitly pending. A scope that claims prototype implementation SHALL still require its entry artifact. An override SHALL NOT manufacture frozen-approved authority or verified evidence.

#### Scenario: CPC-SCN-015 Spec-only approval stays distinct
- **WHEN** a user approves a design specification without prototype execution
- **THEN** the approved design scope is retained without requiring an HTML artifact, and prototype, platform and production implementation validation remain explicitly pending

#### Scenario: CPC-SCN-024 Prototype claim still requires its entry
- **WHEN** a frozen scope claims prototype implementation but no HTML entry exists
- **THEN** the freeze is refused, and a refused freeze leaves existing artifacts intact

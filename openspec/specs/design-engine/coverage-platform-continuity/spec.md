# design-engine/coverage-platform-continuity Specification

## Purpose
Correct the coverage, platform, evidence and handoff seams of the design engine so that an authored scope is admitted, verified, completed and frozen on the facts it actually declares.
## Requirements
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

### Requirement: CPC-001 Preserve design reasoning and source authority
The engine SHALL preserve Double Diamond decision-making, Nine Pillars problem ownership, Five Axes expression calibration, applicable reference methods, evidence hierarchy and the existing draft-to-approved lifecycle. Coverage selection SHALL NOT crop the product model or authorize approval. Formal candidates SHALL retain their required provisional specifications before implementation; direction probes SHALL retain their existing bounded exception. Method outcomes and consequential rationale SHALL remain traceable through source specifications, execution projection and review. Refinements SHALL update the owning source before dependent evidence is reused.

#### Scenario: CPC-SCN-001 Selected pages retain product semantics
- **WHEN** a product map contains ten surfaces and the user selects three
- **THEN** the full map, relevant objects, permissions, states, rationale and applicable method outcomes remain authoritative; only the implementation target is reduced

#### Scenario: CPC-SCN-002 Exploration and refinement keep their routes
- **WHEN** a request is a bounded direction probe, specification-only request or local refinement
- **THEN** it is not forced through full-product enumeration, implementation or approval; a formal candidate still requires its applicable provisional Spec and local refinement preserves unrelated decisions

### Requirement: CPC-003 Author platform context and adaptation
The engine SHALL distinguish target runtime/OS, device and input context, prototype medium and verification environment. Platform facts SHALL be sourced or marked unknown; only route-changing uncertainty requires clarification. Touch interaction, mobile viewport dimensions, and consumer product domains SHALL NOT be mechanically mapped to an iOS target runtime. When the target runtime is undeclared, it SHALL remain `unknown`.

#### Scenario: CPC-SCN-005 Desktop and mobile preserve task meaning
- **WHEN** one task uses a desktop split view and a mobile detail route
- **THEN** adaptation preserves the object's meaning, permissions, selected context and required return behavior while allowing different layout and navigation structures

#### Scenario: CPC-SCN-006 Native target with browser prototype
- **WHEN** the intended product is an iOS or Android application but the artifact is HTML
- **THEN** the specification distinguishes that target from the browser prototype and records simulated system behavior and outstanding native validation without inferring native fidelity

#### Scenario: CPC-SCN-022 Unspecified mobile touch remains target unknown
- **WHEN** a product discussion specifies mobile viewport, touch interaction, or booking flows without naming an operating system
- **THEN** the materialized target context records target runtime as `unknown` while preserving device class `mobile` and input modality `touch`, without fabricating an iOS or Android platform

### Requirement: CPC-004 Project constraints without semantic invention
Formal Builder inputs SHALL be derived from retained selected scope and applicable platform contracts with source identity. The compiler SHALL NOT invent product tensions, reality anchors, shortcuts, platform actions, aesthetic themes, or layout locks to fill omissions. When Five Axes dials are omitted or empty, the token compiler SHALL emit neutral geometric scaffolds without opinionated palette defaults. The assembled execution envelope SHALL emit candidate layout patterns and keep selected pattern open unless explicitly authored.

#### Scenario: CPC-SCN-007 Missing facts and conflicting defaults
- **WHEN** a source leaves a platform shortcut or Core Tension undecided, or declares an action inconsistent with a legacy default
- **THEN** the compiler does not synthesize the default; formal route-critical omissions are reported and authored valid behavior is preserved

#### Scenario: CPC-SCN-008 Tampered or outside-scope dispatch
- **WHEN** a selection names a missing surface, unauthorized path or changed source revision
- **THEN** dispatch is rejected with the specific mismatch and no broader write authorization is inferred

#### Scenario: CPC-SCN-023 Token compiler emits neutral tokens on empty dials
- **WHEN** Five Axes dials are undeclared or empty
- **THEN** the compiler produces a neutral, balanced token set without injecting lime accents or industrial materiality defaults

#### Scenario: CPC-SCN-024 Envelope preserves candidate patterns without layout lock
- **WHEN** a product baseline or category is supplied without an explicit layout profile decision
- **THEN** the envelope emits candidate patterns as advisory options and sets selected pattern to null, allowing Builder to choose the optimal topology

### Requirement: CPC-008 Keep regression results evidence-bounded
Regression evaluation SHALL not convert missing measurements or unverified dimensions into passes or improvements. Observable viewport overflow SHALL be computed from valid available measurements or remain unverified. Every declared critical hard gate SHALL affect aggregate acceptance. New runs SHALL identify the actual Skill and judge source contents, including dirty candidate content, and preserve prior evidence. Mechanism tests and real-session evidence SHALL remain separate; real-session execution SHALL require its own cost authorization.

#### Scenario: CPC-SCN-016 Missing evidence and overflow cannot pass
- **WHEN** viewport measurements show scrollWidth 712 and clientWidth 390, measurements are absent, or both comparison arms are unverified
- **THEN** overflow fails, absent measurements remain unverified, and unverified comparisons are not reported as verified passes or improvements

#### Scenario: CPC-SCN-017 Hard gates and provenance remain visible
- **WHEN** a candidate has a critical accessibility violation or a new candidate run uses modified Skill files
- **THEN** the violation blocks acceptance and the actual source content identity is recorded rather than represented by an unrelated clean revision


## Purpose

Preserve the existing design engine's product reasoning and Spec authority while making prototype coverage, platform adaptation, evidence limits and conditional full-product rollout explicit and verifiable.

## ADDED Requirements

### Requirement: CPC-001 Preserve design reasoning and source authority
The engine SHALL preserve Double Diamond decision-making, Nine Pillars problem ownership, Five Axes expression calibration, applicable reference methods, evidence hierarchy and the existing draft-to-approved lifecycle. Coverage selection SHALL NOT crop the product model or authorize approval. Formal candidates SHALL retain their required provisional specifications before implementation; direction probes SHALL retain their existing bounded exception. Method outcomes and consequential rationale SHALL remain traceable through source specifications, execution projection and review. Refinements SHALL update the owning source before dependent evidence is reused.

#### Scenario: CPC-SCN-001 Selected pages retain product semantics
- **WHEN** a product map contains ten surfaces and the user selects three
- **THEN** the full map, relevant objects, permissions, states, rationale and applicable method outcomes remain authoritative; only the implementation target is reduced

#### Scenario: CPC-SCN-002 Exploration and refinement keep their routes
- **WHEN** a request is a bounded direction probe, specification-only request or local refinement
- **THEN** it is not forced through full-product enumeration, implementation or approval; a formal candidate still requires its applicable provisional Spec and local refinement preserves unrelated decisions

### Requirement: CPC-002 Choose coverage from an informed map
Before Stage 3 expansion, the engine SHALL resolve the requested implementation scope using the current Surface Map, task risks, probe results and applicable platforms. Unresolved scope SHALL produce concrete recommended combinations describing included surfaces, verification purpose, dependencies and omissions. Prior explicit scope SHALL be retained without redundant questioning. The retained selection SHALL identify map revision, selected surfaces/journeys, target contexts and either selected or full-product coverage. Missing, invalid or stale selections SHALL NOT silently default to full-product.

#### Scenario: CPC-SCN-003 Concrete recommendation and selection
- **WHEN** scope is undecided and the map supports both representative review and a complete task flow
- **THEN** recommendations distinguish those concrete combinations and full-product coverage; the chosen combination is retained and a dependency needed outside it is disclosed rather than silently added

#### Scenario: CPC-SCN-004 Scope survives continuation without expansion
- **WHEN** the user already selected a subset or explicitly requested full-product and the session resumes
- **THEN** the matching retained selection is reused; ambiguous, invalid or revision-mismatched selections require reconciliation rather than guessing or reauthorizing all pages

### Requirement: CPC-003 Author platform context and adaptation
The engine SHALL distinguish target runtime/OS, device and input context, prototype medium and verification environment. Platform facts SHALL be sourced or marked unknown; only route-changing uncertainty requires clarification. Existing product/foundation/specification authorities SHALL express shared experience invariants and applicable platform differences in topology, navigation, input, viewport/keyboard behavior, accessibility and recovery. Irrelevant platform dimensions SHALL NOT require exhaustive matrices. Platform-specific surfaces SHALL have explicit applicability rather than an automatic platform-by-page Cartesian product.

#### Scenario: CPC-SCN-005 Desktop and mobile preserve task meaning
- **WHEN** one task uses a desktop split view and a mobile detail route
- **THEN** adaptation preserves the object's meaning, permissions, selected context and required return behavior while allowing different layout and navigation structures

#### Scenario: CPC-SCN-006 Native target with browser prototype
- **WHEN** the intended product is an iOS or Android application but the artifact is HTML
- **THEN** the specification distinguishes that target from the browser prototype and records simulated system behavior and outstanding native validation without inferring native fidelity

### Requirement: CPC-004 Project constraints without semantic invention
Formal Builder inputs SHALL be derived from retained selected scope and applicable platform contracts with source identity. Invalid surface/context references, paths outside authorized roots, missing required formal facts and stale source identities SHALL prevent dispatch. The compiler SHALL NOT invent product tensions, reality anchors, shortcuts, platform actions or approval to fill omissions. Optional exploration unknowns SHALL remain unknown. Builder inputs SHALL preserve relevant tasks, states, recovery, experience invariants, Signature relationships and method outcomes through accessible source references or direct projection.

#### Scenario: CPC-SCN-007 Missing facts and conflicting defaults
- **WHEN** a source leaves a platform shortcut or Core Tension undecided, or declares an action inconsistent with a legacy default
- **THEN** the compiler does not synthesize the default; formal route-critical omissions are reported and authored valid behavior is preserved

#### Scenario: CPC-SCN-008 Tampered or outside-scope dispatch
- **WHEN** a selection names a missing surface, unauthorized path or changed source revision
- **THEN** dispatch is rejected with the specific mismatch and no broader write authorization is inferred

### Requirement: CPC-005 Bind platform claims to evidence
Builder and Critic SHALL assess selected tasks against their applicable platform contract. Evidence SHALL identify target revision, surface/journey, actual execution environment, performed action, observation and simulation limits. Screenshots SHALL only establish captured visual states; static checks SHALL only establish tested code facts. Required behavioral or native-platform claims without supporting evidence SHALL remain unverified. Evidence whose relevant sources changed SHALL be stale; unaffected evidence SHALL remain reusable. Critic SHALL inspect supplied visual evidence and report unexamined scope without approval authority.

#### Scenario: CPC-SCN-009 Narrow screenshot is not mobile completion
- **WHEN** a 390px screenshot exists but required touch, navigation, keyboard or recovery behavior was not exercised
- **THEN** capture is reported separately and the untested requirements remain unverified; HTML simulation does not pass native behavior requirements

#### Scenario: CPC-SCN-010 Evidence follows affected revisions
- **WHEN** a shared navigation contract changes after capture and review
- **THEN** dependent evidence is invalidated while unrelated evidence remains reusable and the affected task requires re-verification

### Requirement: CPC-006 Execute and report the selected scope
The engine SHALL use one batch execution and completion mechanism for selected and full-product coverage. Only full-product selection SHALL authorize automatic expansion across all applicable surfaces of the selected product revision. Selected coverage SHALL stop after its declared obligations. Review views SHALL reconcile authored scope with delivery and evidence, including absent files. Product navigation SHALL NOT be forced to display review-management statuses. Pending destinations SHALL not produce broken links; required navigation dependencies SHALL be disclosed. Blocker explanations or deferred labels SHALL NOT discharge obligations without an explicit scope change. Completion SHALL be qualified by the validated prototype medium and environment.

#### Scenario: CPC-SCN-011 Subset and first batch remain bounded
- **WHEN** three of ten surfaces are selected and only the first surface currently exists
- **THEN** pending sibling links are not required, the three-surface obligations remain visible, the other seven are outside this round, and completion is withheld until the selected obligations are met

#### Scenario: CPC-SCN-012 Full product continues across batches
- **WHEN** full-product covers ten applicable surfaces and the first batch finishes
- **THEN** remaining authorized batches continue with shared context and cross-surface task verification; a missing required surface blocks completion even when it has a documented blocker

#### Scenario: CPC-SCN-013 Map change does not silently alter authorization
- **WHEN** a surface is added, removed or changes platform applicability after selection
- **THEN** the system reconciles the changed revision explicitly, preserving prior results and neither silently expanding nor shrinking the promised scope

### Requirement: CPC-007 Preserve precise handoff integrity
Freeze and downstream admission SHALL bind exact scope, platform contracts, source revisions and evidence limits. Approval SHALL refer to an actual approval or explicit delegated-authority source and its scope, not an arbitrary matching phrase. Strict packet failures SHALL NOT downgrade to permissive admission. Source drift SHALL invalidate downstream integrity. Spec-only approval SHALL remain possible without falsely claiming implementation verification. An override SHALL NOT manufacture frozen-approved authority or verified evidence.

#### Scenario: CPC-SCN-014 False approval and stale content are rejected
- **WHEN** a record only mentions planned or negated approval, strict references fail, an override lacks approval, or frozen sources subsequently change
- **THEN** the system does not issue or accept an approved intact handoff based on those conditions

#### Scenario: CPC-SCN-015 Spec-only approval stays distinct
- **WHEN** a user approves a design specification without prototype execution
- **THEN** the approved design scope can be retained while prototype, platform and production implementation validation remain explicitly pending

### Requirement: CPC-008 Keep regression results evidence-bounded
Regression evaluation SHALL not convert missing measurements or unverified dimensions into passes or improvements. Observable viewport overflow SHALL be computed from valid available measurements or remain unverified. Every declared critical hard gate SHALL affect aggregate acceptance. New runs SHALL identify the actual Skill and judge source contents, including dirty candidate content, and preserve prior evidence. Mechanism tests and real-session evidence SHALL remain separate; real-session execution SHALL require its own cost authorization.

#### Scenario: CPC-SCN-016 Missing evidence and overflow cannot pass
- **WHEN** viewport measurements show scrollWidth 712 and clientWidth 390, measurements are absent, or both comparison arms are unverified
- **THEN** overflow fails, absent measurements remain unverified, and unverified comparisons are not reported as verified passes or improvements

#### Scenario: CPC-SCN-017 Hard gates and provenance remain visible
- **WHEN** a candidate has a critical accessibility violation or a new candidate run uses modified Skill files
- **THEN** the violation blocks acceptance and the actual source content identity is recorded rather than represented by an unrelated clean revision

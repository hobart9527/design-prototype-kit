## MODIFIED Requirements

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

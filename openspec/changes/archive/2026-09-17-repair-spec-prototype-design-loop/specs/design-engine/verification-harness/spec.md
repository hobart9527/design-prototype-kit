## MODIFIED Requirements

### Requirement: HAR-001 Design Token DTCG Export
The verification harness SHALL parse token definitions in markdown format (including two-column and standard breakpoint tables) and export them into compliant W3C Design Tokens Community Group (DTCG) JSON schemas. The token compiler SHALL compile declared project tokens and report undefined values as unknown rather than silently injecting unrequested default color palettes, fixed spacing scales, or universal radius formulas.

#### Scenario: HAR-SCN-001 Parse and export DTCG tokens
- **WHEN** token compilation runs against a valid token source document
- **THEN** it generates a valid DTCG JSON file containing declared tokens without synthesizing unrequested aesthetic defaults

### Requirement: HAR-002 Pipeline Assertion and Boundary Verification
The verification harness SHALL evaluate exact and localized assertion matches against evidence records, enforce execution boundaries on workspace roots, and assemble immutable handoff packets. Static quality checkers SHALL report observable code facts rather than asserting aesthetic merit or completeness from keyword presence. The headless capture and review portal SHALL accurately represent current execution status without hardcoded claims of verification or frozen state.

#### Scenario: HAR-SCN-002 Run pipeline assertion and handoff checks
- **WHEN** verification scripts run against prototype evidence and handoff packages
- **THEN** assertion results, capture failures, and review portal indicators reflect actual evaluation outcomes without pre-filled passing values or hardcoded success banners

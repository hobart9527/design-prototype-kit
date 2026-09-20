## Context

Following the repair and hardening of the coverage and platform continuity platform, the engine's contract gates are functionally sound but ergonomically stiff. When LLMs generate early design specifications in Stage 1, trivial formatting variances (e.g. whitespace around colons, markdown list syntax, minor digest mismatches) trigger hard `E010_STALE_CONTRACT` or parser errors. Concurrently, while the Craft Library in `references/01-foundations/design-methods.md` outlines rich interaction models (OOUX mapping, Decisive 3-Frame, Action Verb Lifecycles, Concentric Radii, Break Protocols), generated prototypes frequently omit an in-memory state store, leading to broken context preservation upon drawer dismissal or filter updates.

## Goals / Non-Goals

Goals:
- Make Stage 1 contract parsing fault-tolerant while preserving semantic invariants (`coverage`, `selected_surfaces`, `platform_contexts`).
- Downgrade SHA-256 digest mismatches from hard blockers to warnings when logical revision identifiers match.
- Instruct Builder to implement a zero-dependency vanilla JS in-memory state store (`window.__prototypeState`) to guarantee context preservation across interactive frames.
- Mandate mobile ergonomics (safe area insets, minimum 44px hit targets, kinetic active feedback) and optical geometry (nested corner radius formula $R_{\text{in}} = \max(0, R_{\text{out}} - P)$) in Builder output.
- Upgrade Review Portal with multi-viewport toggles and Break Protocol edge-data testing toggles.

Non-Goals:
- Introducing heavy client-side frameworks (React, Vue, Redux).
- Removing the coverage decision gate or platform context separation.
- Permitting unverified native validation claims.

## Decisions

### 1. Fault-Tolerant Markdown Parsing with Semantic Retention
In `prototype_context.py`, permit both fenced `prototype-context` blocks and standard markdown YAML/list sections. Normalize casing, strip trailing comments, and handle whitespace gracefully. If a digest mismatch occurs but the declared revision matches the expected revision, issue a diagnostic warning rather than aborting dispatch with `E010_STALE_CONTRACT`.

### 2. Zero-Dependency In-Memory State Store (Method 5)
In `agents/spec-prototype-builder.md`, explicitly instruct the Builder to initialize an in-memory state store in the generated prototype. Form field inputs, active tab/filter states, and drawer open/close flags must mutate this store. Dismissing a drawer or sub-modal must not reset dirty form inputs or parent table filters.

### 3. Somatic and Optical Physicality (Methods 6 & 7)
Inject concrete styling and layout rules into `agents/spec-prototype-builder.md`:
- Mobile/Touch: `padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)`, minimum 44×44px interactive bounds, `:active { transform: scale(0.98); }`.
- Geometry: inner radius calculation matching padding, `font-variant-numeric: tabular-nums` on financial/telemetry figures.
- Break Protocol: inclusion of an interactive toggle or URL parameter (`?stress=1`) that injects overflow strings and empty collections to verify layout resilience.

### 4. Dual-View Review Portal (Playground + Audit Ledger)
In `generate_review_portal.py`, structure the generated HTML portal with an interactive top bar supporting device frame simulation (Desktop 1440px / Tablet 768px / Mobile 390px) and a collapsible audit drawer summarizing 9-pillar conformance and verifiable assertions.

## Risks / Trade-offs

- *Relaxing digest check*: Risk of dispatching against slightly out-of-date maps. Mitigated by strictly verifying logical revision matching and canonical path boundaries.
- *Vanilla JS state store*: Risk of complex state bugs without a framework. Mitigated by keeping the state store minimal (plain object + dispatch/render helper) and strictly scoped to prototype simulation.

## Migration Plan

1. Update `prototype_context.py` and `lint_spec_contracts.py` with fault-tolerant parsing and advisory digest matching.
2. Update `agents/spec-prototype-builder.md` with state store, somatic ergonomics, and optical geometry requirements.
3. Update `generate_review_portal.py` and `verify_prototype_quality.py` with viewport controls and honest environment logging.
4. Provide unit tests covering parser fault-tolerance, state preservation requirements, and portal rendering.

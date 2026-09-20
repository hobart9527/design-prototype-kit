# Proposal: Semantic Freedom Refactor (Thin Compiler + Rich Reasoning)

## Why

The design prototype kit has an excellent conceptual architecture (Nine Pillars, Double Diamond, OOUX, Contracts, Builder/Critic adversarial verification, L0–L4 scope control). However, several glue scripts in the transpilation layer usurp design decision authority:

1. `skills/spec-prototype/scripts/materialize_contracts.py` fabricates platform facts (e.g. matching `Mobile|Touch|Booking` forces `target_ctx = "ios"`).
2. `skills/spec-prototype/scripts/compile_tokens.py` injects opinionated aesthetic defaults (`warm-graphite-lime`, `machined-industrial`, `kinetic`) when Five Axes dials are undeclared, acting as an implicit opinionated designer rather than an impartial mathematical compiler.
3. `skills/spec-prototype/scripts/assemble_envelope.py` reduces product categories into rigid layout profiles (e.g. SaaS -> `operational-canvas`).
4. `agents/spec-prototype-builder.md` hardcodes arbitrary implementation heuristics (MUST Toast, MUST Spring, rigid 44px) rather than enforcing the 5 core integrity categories (Semantic, Task, Accessibility, State & Recovery, Platform).
5. `agents/spec-prototype-critic.md` and `quality-floor.md` conflate craft preferences with hard blockers.

## What Changes

- **T1: Platform Truth**: Remove heuristic platform inference (`Mobile/Touch/Booking -> iOS`) in `materialize_contracts.py`. Platform target is strictly `explicit` (when authored) or `unknown`. Device class and touch modality are decoupled from target OS.
- **T2: Token Compiler Purity**: Remove opinionated default palettes and themes in `compile_tokens.py`. Undeclared dials compile to neutral, un-opinionated geometric scaffolds. Distinguish `formal` compilation from `probe` compilation.
- **T3: Envelope Declassification**: Transition `layout_profile` in `assemble_envelope.py` to advisory `candidate_patterns`; keep `selected_pattern: null` unless authored.
- **T4: Builder Rule Reduction**: Converge Builder MUST rules in `agents/spec-prototype-builder.md` down to the 5 core integrity invariants (Semantic, Task, Accessibility WCAG 2.2 AA 24px minimum, State & Recovery, Platform).
- **T5: Floor & Craft Separation**: Decouple Critic and quality-floor from blocking builds on aesthetic techniques.
- **T6: Regression & Purity Tests**: Add dedicated tests preserving unknown platform states, compiler neutrality, and invariant integrity.

## Capabilities

### Modified Capabilities
- `design-engine/coverage-platform-continuity`: align platform context, token compilation neutrality, envelope flexibility, and builder integrity contracts.

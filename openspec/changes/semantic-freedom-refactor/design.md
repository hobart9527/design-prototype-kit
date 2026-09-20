## Context

See proposal.md for motivation. This change implements the agreed Option B architecture ("Thin Compiler + Rich Reasoning"). It purifies the transpilation layer (`materialize_contracts.py`, `compile_tokens.py`, `assemble_envelope.py`) from fabricating platform assumptions, injecting arbitrary aesthetic themes, or prescribing rigid layout profiles. It converges Builder guidelines onto the 5 core integrity categories, freeing the model to perform high-caliber design reasoning while keeping the deterministic compiler focused on mathematical consistency.

## Goals / Non-Goals

### Goals
- Remove synthetic heuristic platform inference (`Mobile|Touch|Booking -> iOS`). Platform is strictly `explicit` or `unknown`.
- Eliminate hardcoded default aesthetic themes (`warm-graphite-lime`, `machined-industrial`, `kinetic`). Empty dials compile to neutral scaffolds.
- Transition `layout_profile` to advisory `candidate_patterns`, leaving pattern selection to the Builder unless explicitly authored.
- Refactor Builder MUST rules down to 5 core integrity categories (Semantic, Task, Accessibility WCAG 2.2 AA 24px floor, State & Recovery, Platform).
- Decouple Critic and quality floor from blocking builds on stylistic and aesthetic choices.
- Add comprehensive regression tests ensuring unknown preservation and compiler neutrality.

### Non-Goals
- Inventing a standalone IR file format or separate schema database.
- Rewriting the Double Diamond workflow, Nine Pillars, or Evidence Protocol.
- Relaxing accessibility standards (WCAG 2.2 AA remains non-negotiable).

## Decisions

### 1. Platform Neutrality & Modality Decoupling
Target platform OS (`ios`, `android`, `web`, `macos`, `windows`) must only be set when explicitly declared by user prompt or product metadata. An undeclared platform remains `unknown`. Touch input and mobile viewport width are physical characteristics, not proof of an iOS operating system.

### 2. Neutral Compiler Base
A compiler's role is mathematical derivation, not art direction. When Five Axes dials are absent, the compiler emits neutral, balanced tokens rather than assuming a dark industrial lime style.

### 3. Open Layout Topology
Product baseline or domain type (e.g. SaaS, Reading, Console) informs potential candidate patterns, but does not bind the envelope to an immutable layout profile.

### 4. Five Core Builder Invariants
1. Semantic Integrity: Core domain objects and actions must be represented.
2. Task Integrity: Primary user flows must be interactable and navigable.
3. Accessibility Integrity: Minimum contrast, keyboard reachability, and 24px minimum touch target size (WCAG 2.2 AA).
4. State & Recovery Integrity: Clear handling for loading, empty, error, and recovery states.
5. Platform Integrity: Respect declared platform conventions, or remain neutral when unknown.

### 5. Separation of Floor from Craft Critique
The quality floor protects functional and accessibility invariants. Subjective aesthetics (spring vs linear easing, drawer vs modal, specific corner radii) belong in advisory critique feedback, not fatal build blockers.

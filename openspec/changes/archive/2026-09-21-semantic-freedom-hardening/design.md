# Design: Semantic Freedom Hardening & Code Review Remediation

## Context

The `semantic-freedom-refactor` removed synthetic platform inference and aesthetic defaults. A two-axis review identified remaining seams where opinionated heuristics linger or hygiene violations exist:
1. `compile_tokens.py` duplicate imports and dead `math` import.
2. `DARK_ATMOSPHERES` contains light palettes (`editorial-paper-warm`, `clean-slate-pro`), causing conceptual confusion.
3. Silent exception swallowing in `materialize_contracts.py` (line ~772) and `compile_tokens.py` (lines ~539, 549).
4. `assemble_envelope.py` promoting `candidate_patterns[0]` to `layout_profile` when `selected_pattern` is None, which re-binds downstream OOUX layout modes and blueprints to the first candidate rather than leaving topological agency open.
5. In `compile_tokens.py`, `dials.get("energy", "kinetic")` retains kinetic as an unauthored default.
6. `tests/test_canonical_ontology.py` lacked test cases for `agents/spec-prototype-builder.md`.

## Key Technical Decisions

### 1. Token Compiler Hygiene and Neutral Motion
- Delete unused `math` and duplicate `Any, Dict` imports in `compile_tokens.py`.
- Define `ATMOSPHERES = {**CANONICAL_ATMOSPHERES, NEUTRAL_SCAFFOLD_NAME: NEUTRAL_SCAFFOLD}` and retain `DARK_ATMOSPHERES = ATMOSPHERES` for backwards compatibility.
- Set default energy in formal mode to `"steady"` instead of `"kinetic"`. When energy is steady, emit standard balanced timing instead of the kinetic HUD curve.

### 2. Failure Context Preservation
- In `materialize_contracts.py` and `compile_tokens.py`, avoid bare `except Exception: pass`. Catch specific errors or log/propagate diagnostics so envelope assembly failures are surfaced to callers.

### 3. Envelope De-locking and Advisory Candidacy
- In `assemble_envelope.py`, preserve `candidate_patterns` as strictly advisory.
- When `selected_pattern` is None, `layout_profile` defaults to `"adaptive-workspace"` (the neutral baseline) rather than picking `candidate_patterns[0]`. Downstream blueprints and attention routing use adaptive-workspace defaults unless an explicit pattern is authored.

### 4. Canonical Ontology Verification
- In `tests/test_canonical_ontology.py`, assert that `agents/spec-prototype-builder.md` defines and structures requirements around the 5 Core Integrity Categories (Semantic, Task, Accessibility, State & Recovery, Platform) and excludes prescriptive heuristics.

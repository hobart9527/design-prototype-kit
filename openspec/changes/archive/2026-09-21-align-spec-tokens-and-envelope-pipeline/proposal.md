# Proposal: Align Spec Contracts, Token Compilation, and Envelope Delivery Pipeline

## Why

Auditing the `spec-prototype` pipeline revealed that while `compile_tokens.py` contains sophisticated OKLab lightness derivation, concentric radius mathematics, and density spacing scales, design semantics and craft techniques are lost or attenuated across three pipeline seams:

1. **Foundation Contract Disconnect**: `materialize_contracts.py` constructs `foundation/f1.md` with ruthless omissions and material invariants, but drops the authored 5-Dial Style Register (`energy`, `density`, `materiality`, `rhythm`, `character`), Reality Benchmark Anchors, and Seed Palette. As a consequence, `compile_tokens.py` cannot treat `foundation/f1.md` as its single source of truth and must bypass `f1.md` to parse raw `discussion.md`.
2. **Reality Anchor Delivery Loss**: In `assemble_envelope.py`, `reality_anchors` are extracted from discussion/product specs via regex (e.g. physical benchmarks, lifeworld analogies), but are merely appended to an internal search string `all_spec_text` and completely omitted from `envelope.json` (`creative_envelope` and root envelope), leaving the Builder Agent without declared real-world design grounding.
3. **Craft Reference Blunt Truncation**: `assemble_envelope.py:_extract_craft_guidance` artificially truncates craft reference documentation to 18 lines or 300 characters (`if len(lines) >= 18: break`). This cuts off critical craft invariants, interaction rules, and structural examples before the Builder Agent can read them.
4. **Slice & Spec Constraint Seam Omissions**: Authored OOUX terminology in `c1.md` and component constraints in `r1.md` are not parsed into structured envelope fields, forcing the Builder to guess domain naming mappings.

## What Changes

- `skills/spec-prototype/scripts/materialize_contracts.py`: Materialize the 5-Dial Style Register, Reality Benchmark Anchors, and Color Register into `foundation/f1.md`.
- `skills/spec-prototype/scripts/compile_tokens.py`: Support `foundation/f1.md` as an authoritative input source for tokens compilation alongside `discussion.md`, falling back gracefully.
- `skills/spec-prototype/scripts/assemble_envelope.py`:
  - Preserve `reality_anchors` in `creative_envelope` and root `envelope`.
  - Expand `_extract_craft_guidance` to extract complete anchor sections rather than cutting off at 18 lines.
  - Parse OOUX terminology from `c1.md` into `ooux_topology["terminology"]` and component constraints from `r1.md` into `design_constraints["component_constraints"]`.
- Tests: Add regression coverage in `tests/test_tokens.py` and `tests/test_pipeline.py`.

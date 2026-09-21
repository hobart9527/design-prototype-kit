## 1. Align Spec Contracts, Token Compilation, and Envelope Delivery Pipeline

- [ ] T-01 Materialize 5-dials and reality anchors in f1.md and adapt compile_tokens
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/materialize_contracts.py:materialize, skills/spec-prototype/scripts/compile_tokens.py:compile_tokens, tests/test_tokens.py
  - Write scope: skills/spec-prototype/scripts/materialize_contracts.py, skills/spec-prototype/scripts/compile_tokens.py, tests/test_tokens.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_tokens.py
  - Action: In `materialize_contracts.py`, when generating `foundation/f1.md`, extract and include the `5-Dial Style Register`, `Reality Benchmark Anchors`, and `Seed Palette / Color Register` from discussion/product text. In `compile_tokens.py`, update `compile_tokens` to support reading from an `f1.md` foundation file directly or looking for `f1.md` in the prototype contracts directory, falling back to `discussion.md`. In `tests/test_tokens.py`, add test verifying that `compile_tokens` successfully compiles tokens from an `f1.md` file containing 5-dials and palette definitions.

- [ ] T-02 Preserve reality anchors, full craft guidance, and domain constraints in assemble_envelope
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/assemble_envelope.py:assemble_envelope, skills/spec-prototype/scripts/assemble_envelope.py:_extract_craft_guidance, tests/test_pipeline.py:test_materialize_contracts_high_fidelity_semantic_synthesis
  - Write scope: skills/spec-prototype/scripts/assemble_envelope.py, tests/test_pipeline.py
  - Verify with: pytest -q -p no:cacheprovider tests/test_pipeline.py -k test_materialize_contracts_high_fidelity_semantic_synthesis
  - Action: In `assemble_envelope.py`, preserve `reality_anchors` in both `creative_envelope["reality_anchors"]` and `envelope["reality_anchors"]`. In `_extract_craft_guidance`, remove the 18-line truncation cutoff so the complete text of the targeted anchor section (up to the next same-level header or EOF) is captured. In `assemble_envelope.py`, parse OOUX Terminology from `c1.md` into `ooux_topology["terminology"]` and Component Constraints from `r1.md` into `design_constraints["component_constraints"]`. In `tests/test_pipeline.py`, update `test_materialize_contracts_high_fidelity_semantic_synthesis` to assert that `foundation/f1.md` contains the 5-dial register, that `envelope["creative_envelope"]["reality_anchors"]` is populated, and that `active_methods` craft guidance retains complete section details.

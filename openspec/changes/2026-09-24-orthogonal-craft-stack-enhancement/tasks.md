# Tasks

## 1. Integrate orthogonal 4-axis modern craft stack and verify pipeline continuity

- [ ] T-01 Integrate orthogonal 4-axis modern craft stack across schema, compilation, agents, and tokens
  - Depends on: none
  - Anchors: skills/spec-prototype/scripts/compile_spec_ir.py:compile_canonical_ir, skills/spec-prototype/scripts/compile_tokens.py:generate_css, skills/spec-prototype/scripts/assemble_envelope.py:assemble_envelope
  - Write scope: skills/spec-prototype/schemas/prototype-spec.v1.json, skills/spec-prototype/scripts/compile_spec_ir.py, skills/spec-prototype/scripts/compile_tokens.py, skills/spec-prototype/scripts/assemble_envelope.py, agents/spec-prototype-builder.md, agents/spec-prototype-critic.md, skills/spec-prototype/references/stages/stage-1-frame.md, skills/spec-prototype/references/dialectic/03-sensory-kinetic.md, tests/test_tokens.py, tests/test_craft_stack.py
  - Verify with: pytest -q -m unit
  - Verify tier: unit
  - Action: Update prototype-spec.v1.json to support craft_stack under foundation, update compile_spec_ir.py to parse or infer orthogonal craft axes into canonical IR, update compile_tokens.py to generate tonal wash, specular highlights, and tight display tracking tokens, update assemble_envelope.py to propagate craft directives to builder, enhance builder and critic agent prompts with micro-craft recipes and anti-generic visual checks, and add test coverage in tests/test_craft_stack.py.
  - Specimen:
    ```python
    # Positive specimen: Canonical IR compilation emits valid craft_stack
    from skills.spec_prototype.scripts.compile_spec_ir import compile_canonical_ir
    # Negative/boundary specimen: Missing craft keys gracefully fallback to inferred defaults
    ```

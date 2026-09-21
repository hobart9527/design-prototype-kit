# Proposal: Repair Builder Payload Seams and Viewport Execution

## Why

In the transition to the lean Builder payload (`build_builder_payload`), several authored contracts were severed:
1. `content_language` (and template format `- Content language (locked): <tag>`), `topology_context`, and `interaction_spec` were demoted into `_DEBUG_CONTEXT_FIELDS`, making them unreadable by the Builder and downstream runtime judges.
2. `agents/spec-prototype-builder.md` instructions still referred to demoted paths (`constraint_envelope.content_language.tag`, `five_axes`).
3. `active_methods` guidance text (10.4KB duplicate markdown) was previously stripped, but the slim method metadata (`id`, `name`, `pillars`, `invariants`, `reference_file`) was dropped entirely from the Builder payload rather than passed cleanly without the verbose guidance.
4. `_mandatory_viewports` in `assemble_envelope.py` had zero active consumers: `capture_command` did not forward derived `--viewports` to `capture.mjs`, and `capture.mjs:387` hardcoded `["320", "390", "768", "1280"]` on `--slice`.

## What Changes

1. **Reconnect Payload Context**:
   - Promote `content_language`, `topology_context`, and `interaction_spec` into `_PAYLOAD_CONTEXT_FIELDS` in `assemble_envelope.py`.
   - Update `extract_field` in `assemble_envelope.py` to match optional parentheticals like `(?: \([^)]*\))?` so `- Content language (locked): <tag>` matches.
   - Include slim `active_methods` (excluding verbose `actionable_guidance`, retaining `id`, `name`, `pillars`, `invariants`, `reference_file`) in `_PAYLOAD_CONTEXT_FIELDS` or as a payload field.
2. **Reconcile Builder Instructions**:
   - Update `agents/spec-prototype-builder.md` §3.1 to read `content_language.tag` directly from payload root.
   - Update §1 to read `visual_directives.sensory_dials` instead of `five_axes`.
   - Update §3.5 to instruct Builder to read guidance from `reference_file` if needed.
3. **Wire Viewport Execution**:
   - Update `assemble_envelope.py` `capture_command` generator to forward `--viewports <csv>` and `--states <csv>` from `inspection_contract.mandatory_viewports` and `mandatory_states`.
   - Update `capture.mjs` `--slice` branch to accept and prefer passed `--viewports` and `--states`, using the hardcoded array only as fallback when not provided.
4. **Update Unit Tests**:
   - Adjust `tests/test_lean_builder_payload.py` to assert the updated payload contracts and verification facts.

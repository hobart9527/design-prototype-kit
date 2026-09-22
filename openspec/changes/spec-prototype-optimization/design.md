## Context

The repository already contains the canonical IR consolidation and the bounded hardening changes described in `proposal.md`. The implementation spans compiler, envelope assembly, linting, execution-boundary admission, generated canonical artifacts, and tests. The change is tooling and internal contract work; it does not introduce a new product-facing API.

## Goals / Non-Goals

**Goals:**

- Preserve one machine authority in `r1.spec.json` while retaining `r1.spec.md` as its human projection.
- Keep Stage 1 source records separate from explicit Stage 3/4 verification fragments.
- Ensure schema and coverage failures are fail-closed and observable.
- Verify the complete current revision before publication.

**Non-Goals:**

- No additional product features or UI redesign.
- No migration of unrelated legacy records beyond their documented compatibility role.
- No forceful freeze or bypass of approval gates.

## Decisions

1. **Canonical IR owns formal assembly decisions.** `assemble_envelope.py` consults `r1.spec.json` for explicit coverage before considering legacy `m1.md`, preventing stale compatibility files from overriding current machine authority.
2. **Verification fragments are explicit inputs.** `compile_spec_ir.py` accepts `--fragment` and checks bounded default fragment locations. Missing or malformed fragments do not receive fabricated values; normal compilation remains fail-closed.
3. **Canonical lint is schema-first.** `lint_spec_contracts.py` validates the canonical JSON against `prototype-spec.v1.json` and then applies boundary checks. Legacy lint remains available only when canonical IR is absent.
4. **Publication follows governed delivery.** Native verification and Host-owned delivery state decide whether the revision is publishable; a local commit alone is not completion evidence.

## Risks / Trade-offs

- [Risk] A fragment with schema-invalid state objects blocks compilation. → Mitigation: the compiler reports the schema error and the fragment remains an explicit, editable source.
- [Risk] Existing legacy files can disagree with canonical IR. → Mitigation: canonical coverage wins on the canonical path; legacy presence rules are not used as primary authority.
- [Risk] Freeze or publication can remain blocked by absent approval evidence. → Mitigation: preserve the fail-closed gate and record the approval through the owning discussion decision before retrying.

## Migration Plan

1. Validate the OpenSpec artifacts.
2. Admit the current revision through Loom delivery and run the frozen unit verifier.
3. Publish only after delivery reaches `Complete`; otherwise follow the returned repair or decision boundary.

## Open Questions

None.

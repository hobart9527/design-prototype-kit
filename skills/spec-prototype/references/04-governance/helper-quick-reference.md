# Helper Quick Reference (helper 速查)

One line per helper. The hook admits only installed helpers in `skills/spec-prototype/scripts/`; everything else is authored with Write/Edit. Never reverse-engineer a script's source to learn its format — the format lives here or in a template.

## Primary Helpers

| Task | Command (single line, no `&&`/pipe) |
|---|---|
| Viewport capture | `node skills/spec-prototype/scripts/capture.mjs <url> --out prototype/evidence --viewports 390,1280` |
| Craft detect | `python3 skills/spec-prototype/scripts/detect.py --artifact <file>` |
| Draw seeds (Turn 1, optional) | `python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id> --record prototype/briefs/<slice>.md --write` |
| Compile tokens | `python3 skills/spec-prototype/scripts/compile_tokens.py` — format: [`../../templates/world.tokens.example.md`](../../templates/world.tokens.example.md) |
| Quality verify (hard gate) | `python3 skills/spec-prototype/scripts/verify_prototype_quality.py --slice <slice_id> --root .` — exit 0 pass, 1 fail, 2 degraded (render probes never ran; not a pass) |
| Compile Spec IR (Stage 5) | `python3 skills/spec-prototype/scripts/compile_spec_ir.py --slice <slice_id> --required-tier execution_spec` |
| Freeze / gate (Stage 5) | `python3 skills/spec-prototype/scripts/handoff.py freeze --root . --spec prototype/specifications/<slice_id>/r1.spec.md`; `handoff.py gate` re-verifies digests for downstream admission |
| Spec contract lint (Stage 5, optional) | `python3 skills/spec-prototype/scripts/lint_spec_contracts.py --root . --slice <slice_id>` |
| Contrast precheck | `node skills/spec-prototype/scripts/wcag-check.js --on <bg> <fg1> [<fg2> …]` |
| Sync review portal | `python3 skills/spec-prototype/scripts/generate_review_portal.py --root .` → `prototype/review-portal.html` |
| Dev preview (optional) | `node skills/spec-prototype/scripts/preview.mjs` — optional; capture works on `file://` URLs |

## Anti-patterns (the failure classes to avoid)

- Reading helper source code to learn format/flags → consult this table or templates directly.
- Trial-and-error CSS micro-edits and iterative re-captures → inspect `diagnostics_summary` in `capture.mjs` output once, fix in place.
- Ignoring JS errors in `runtime_errors` → a JS runtime error breaks DOM rendering and task traces; fix before claiming completion.
- Fragment edits into design records or prototypes → author whole files with `Write`.
- Writing a new check instead of reusing an installed one → verify with `capture.mjs`, `detect.py` and the browser tools first. A throwaway script in `/tmp` for one specific question is allowed, but it is not an artifact and not evidence unless its output is persisted under `prototype/evidence/` and recorded in the manifest.

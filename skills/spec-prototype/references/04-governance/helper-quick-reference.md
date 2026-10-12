# Helper Quick Reference (helper 速查)

One line per helper. The hook admits only installed helpers in `skills/spec-prototype/scripts/`; everything else is authored with Write/Edit. Never reverse-engineer a script's source to learn its format — the format lives here or in a template.

## The one verification loop

```
node skills/spec-prototype/scripts/verify.mjs <url> --out prototype/evidence --artifact prototype/experiments/<slice>/anchor/index.html --turn 2
```

capture → detect → divergence presence → portal sync → budget circuit breaker, in one trip. Turn 2 budget: 2 trips. Turn 3 budget: 2 rounds. Exceeding exits 42 with `BUDGET_EXCEEDED`: record residue as `PARTIAL`, stop.

Flags: `--viewports 390,1280` (default), `--states ideal,error,skeleton`, `--records truth.md,world.md,briefs/<slice>.md` (divergence check), `--portal` (sync review portal), `--root <repo-root>` (portal only).

## Individual helpers (when verify.mjs is too much)

| Task | Command (single line, no `&&`/pipe) |
|---|---|
| capture only | `node skills/spec-prototype/scripts/capture.mjs <url> --output prototype/evidence --viewports 390,1280 --states ideal` |
| craft detect | `python3 skills/spec-prototype/scripts/detect.py --artifact <file>` |
| divergence presence | `python3 skills/spec-prototype/scripts/check_divergence.py --records truth.md,world.md,briefs/<slice>.md` |
| draw seeds (Turn 1) | `python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id> --record prototype/briefs/<slice>.md --write` |
| compile tokens | `python3 skills/spec-prototype/scripts/compile_tokens.py` — format: [`../../templates/world.tokens.example.md`](../../templates/world.tokens.example.md) |
| contrast precheck | `node skills/spec-prototype/scripts/wcag-check.js --on <bg> <fg1> [<fg2> …]` |
| sync review portal | `python3 skills/spec-prototype/scripts/generate_review_portal.py --root .` → `prototype/review-portal.html` (the only legal portal path) |
| dev preview (optional) | `node skills/spec-prototype/scripts/preview.mjs` — optional convenience; capture works on `file://` URLs, preview is not required |

## Anti-patterns (the r52 failure classes)

- Reading `compile_tokens.py` source to learn the `contract:tokens` format → use the template.
- Probing `preview.mjs` / `generate_review_portal.py` to discover their flags → they are in this table.
- Six separate captures / five separate PNG reads → one `verify.mjs` trip, then `Read` only the PNGs that can change a judgment.
- Fragment Edits into the design record → write the record file whole with `Write`.

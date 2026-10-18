# Token authoring template — copy, edit, compile. Never read `compile_tokens.py` to learn the format.

One compile is the whole loop. The compiler's source is not documentation; this file is.
Three layers, three blocks. Values are double-quoted YAML (the machine contract requires double quotes).

## Block 1 — `contract:tokens` (palette discipline, machine SSOT, priority 0)

`accent_seal` and `accent_policy` are optional; status colour keys are also allowed when authored. Anything else fails closed.

```contract:tokens
accent_seal: "#F5A524"        # hex, 3-8 digits; the one signature accent this product earns
accent_policy: "rest state; destructive commit"   # free text: where the accent is allowed to appear
state_nominal: "#2E7D32"
state_warning: "#F59E0B"
state_danger: "#DC2626"
state_success: "#16A34A"
state_info: "#2563EB"
```

## Block 2 — palette values (what the compiler actually compiles into tokens.css)

Author inside a `## Confirmed` section (aliases `## Decision` / `## 决策` / `## Selected`
are equivalent). `compile_tokens.py`
extracts the LAST authored `key: #hex` match per key, so the latest decision wins; earlier
drafts are history, not inputs. Recognised keys (aliases in parentheses):

- `bg-void` (bg_void, background-void) — deepest background
- `bg-base` — primary surface background
- `bg-surface` — raised surface
- `bg-surface-raised` — second elevation
- `bg-overlay`
- `border-dim`, `border-subtle` (border), `border-bright` (border-focus)
- `text-primary`, `text-secondary`, `text-tertiary`
- `accent-primary` (accent, primary-accent), `accent-hover`
- `status-running` / `state_nominal` / `state`, `status-warning` / `state_warning`, `status-danger` / `state_danger`, `state_success`, `state_info`
- `accent-seal`

Authored form (a confirmed-section heading — `## Confirmed` / `## Decision` / `## 决策` /
`## Selected` — is what makes these beat ambient prose):

```markdown
## Confirmed — visual tokens
- bg-void: "#0B0E12"
- bg-surface: "#14181F"
- text-primary: "#EDEFF2"
- text-secondary: "#9AA3AE"
- accent-primary: "#F5A524"
- status-danger: "#E5484D"
- status-warning: "#F5A524"
```

Unset keys in `formal` mode fall back to the neutral scaffold — that is a pass, not a gap.
`--mode probe` permits natural-language palette inference ("温润米白 `#F9F6F0` 纸感底色"); use only during direction probes.

## Block 3 — `contract:axes` (Five Axes SSOT, priority 0)

```contract:axes
density: "dense"
energy: "low"
materiality: "instrument"
rhythm: "tabular"
character: "operational"
```

Prose bullets (`- density: dense`) are the fallback when no block exists.

## Compile — one command

```
python3 skills/spec-prototype/scripts/compile_tokens.py
```

Defaults: reads `prototype/world.md` (else `prototype/discussion.md`), writes
`prototype/shared/tokens.css` + `prototype/contracts/tokens/t1.json`.
Hand edits to tokens.css are overwritten at the next compile — the compiler is the sole
writer of tokens.css; Stage 2 探索值先回写进 world.md 的 Confirmed 决策区，再编译生效。
`--check-sync` verifies freshness without compiling (exit 1 on drift).

## Contrast precheck — one command, all pairs at once

Hook admits only single commands; never chain or pipe:

```
node skills/spec-prototype/scripts/wcag-check.js --on "#0B0E12" "#EDEFF2" "#9AA3AE" "#F5A524"
```

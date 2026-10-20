# Token authoring template — copy, edit, compile. Never read `compile_tokens.py` to learn the format.

One compile is the whole loop. The compiler's source is not documentation; this file is.
Three layers, three blocks. Values are double-quoted YAML (the machine contract requires double quotes).

**Every palette, font and value below is a format example, not a default.
这些是格式示例，不是默认值；真实值必须由 brief 推导。** Copy the shape of a
block, derive its values from the product's own brief.

## Block 1 — `contract:tokens` (palette discipline, machine SSOT, priority 0)

`accent_seal` and `accent_policy` are optional; status colour keys are also allowed when authored. Anything else fails closed.

```contract:tokens
accent_seal: "#9B4221"        # hex, 3-8 digits; the one signature accent this product earns — must match the chosen world's accent-primary (World A #9B4221, World B #6B7A8F)
accent_policy: "rest state; destructive commit"   # free text: where the accent is allowed to appear
state_nominal: "#2E7D32"
state_warning: "#F59E0B"
state_danger: "#DC2626"
state_success: "#16A34A"
state_info: "#2563EB"
```

## Block 2 — palette values (what the compiler actually compiles into tokens.css)

Author inside a `## Proposed` section before approval (a `## Confirmed` section — aliases
`## Decision` / `## 决策` / `## Selected` — outranks it once explicit in-session approval
lands). `compile_tokens.py`
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

Authored form (a scoped heading — `## Proposed` before approval, `## Confirmed` /
`## Decision` / `## 决策` / `## Selected` after — is what makes these beat ambient prose):

**These two blocks are format examples, not defaults. 这些是格式示例，不是默认值；
真实值必须由 brief 推导。** They are deliberately two different worlds so no single
palette reads as the house look; copy the *shape* of one, derive the *values* from
this product's brief. A dark HUD with a grotesque display and a mono accent is the
category default, not a decision — if the brief does not name that world, do not
reach for it.

### World A — light warm editorial (衬线 display + 暖纸色)

```markdown
## Proposed — visual tokens
- bg-void: "#F7F4EE"
- bg-surface: "#FFFDF9"
- text-primary: "#23201D"
- text-secondary: "#5E5953"
- accent-primary: "#9B4221"
- --font-display: '"Fraunces", "Iowan Old Style", Georgia, serif'
- --font-sans: '"Source Sans 3", system-ui, sans-serif'
- --font-mono: '"IBM Plex Mono", ui-monospace, monospace'
- --surface-shadow: "0 1px 2px rgb(35 32 29 / 6%), 0 8px 24px rgb(35 32 29 / 8%)"
- status-danger: "#B91C1C"
- status-warning: "#B45309"
```

### World B — dense neutral tool (紧凑无衬线 + 低饱和)

```markdown
## Proposed — visual tokens
- bg-void: "#101214"
- bg-surface: "#181B1E"
- text-primary: "#E6E8EA"
- text-secondary: "#9BA1A6"
- accent-primary: "#6B7A8F"
- --font-display: '"Archivo", system-ui, sans-serif'
- --font-sans: '"Archivo", system-ui, sans-serif'
- --font-mono: '"Roboto Mono", ui-monospace, monospace'
- --surface-shadow: "0 1px 2px rgb(0 0 0 / 40%)"
- status-danger: "#D9534F"
- status-warning: "#C98A3B"
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
Optional override inside the block only: `radius_outer: <int 0..32>` — overrides the
density-derived outer radius while the concentric inner/card/btn formulas still follow.

## Compile — one command

```
python3 skills/spec-prototype/scripts/compile_tokens.py
```

Defaults: reads `prototype/world.md` (else `prototype/discussion.md`), writes
`prototype/shared/tokens.css` + `prototype/contracts/tokens/t1.json`.
Hand edits to tokens.css are overwritten at the next compile — the compiler is the sole
writer of tokens.css; Stage 2 探索值先回写进 world.md 的 Proposed/Confirmed 决策区，再编译生效。
`--check-sync` verifies freshness without compiling (exit 1 on drift).

## Contrast precheck — one command, all pairs at once

Hook admits only single commands; never chain or pipe:

```
node skills/spec-prototype/scripts/wcag-check.js --on "#F7F4EE" "#23201D" "#5E5953" "#9B4221"
```

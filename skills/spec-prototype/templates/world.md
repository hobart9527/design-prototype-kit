# Visual world — <product name>

Layered layout: this file owns the shared visual world and is the sole token
authority. Every slice reads from it; no slice restates it.

- `prototype/truth.md` — product truth and decision provenance.
- `prototype/world.md` — this file: Direction Contract, Five Axes, tokens.
- `prototype/briefs/<slice_id>.md` — one per slice; surface strategy and evidence.

`compile_tokens.py` auto-detects this file (no `--discussion` flag needed) and is
the only writer of `prototype/shared/tokens.css`. The first `tokens.css` is written
at Stage 2 (Turn 2) from the `proposed` token decisions here; Stage 5 recompiles it
and seals it with a sha256.

## Direction Contract

Author all six blocks once the recommended direction is formed
(`references/01-foundations/design-language.md`). All six blocks are mandatory
before authoring prototype HTML/CSS. Never leave them empty or write
"Left empty until direction locked".

- **THESIS**: <one sentence: the visual & ergonomic claim observable at first glance>
- **OWN-WORLD**: <metaphor world: physical/analog reference, e.g. cockpit, breaker panel, drafting board>
- **STORY**: <the core task narrative unfolding across the layout>
- **FIRST VIEWPORT**: <exact content composition of the opening 1440/1280 screen>
- **FORM**: <spatial massing, grid rhythm, density, and responsive recomposition>
- **FINISH**: <surface optics, hairline border vs elevation, palette discipline, detents>

## Experience Foundation & Five Axes

All five axes are accounted for at direction lock: each carries a value with
the product evidence that earned it, or an explicit `open` with the reason it
stays free. An axis left silent reads as a model default, not a decision.

```contract:axes
density: <sparse | comfortable | dense>
energy: <calm | smooth | kinetic>
materiality: <flat | coated_instrument_dark | …>
rhythm: <measured | fluid | …>
character: <neutral | technical | editorial | …>
```

- `density`: `<value>` (one-line product evidence)
- `energy`: `<value>` (one-line product evidence)
- `materiality`: `<value>` (one-line product evidence)
- `rhythm`: `<value>` (one-line product evidence)
- `character`: `<value>` (one-line product evidence)

## Seed Palette & Tokens

Declare `accent_seal` only when the product has an irreversible or high-stakes
moment that earns one reserved colour. Optional `state_nominal`, `state_warning`,
`state_danger`, `state_success`, and `state_info` keys provide authored status hues.

```contract:tokens
accent_seal: "#rrggbb"
accent_policy: "<one line on when the seal colour may fire>"
state_nominal: "#rrggbb"
state_warning: "#rrggbb"
state_danger: "#rrggbb"
state_success: "#rrggbb"
state_info: "#rrggbb"
```

- `--bg-void`:
- `--bg-surface`:
- `--text-primary`:
- `--accent-primary`:
- `--accent-seal`: (only if declared above)

## Style Language

Method: `references/01-foundations/style-language.md`. Draft with the recommended
direction; status follows the Decisions table. Do not restate token values here.

- **Positions** (3–5, `We choose X over Y, because …`):
- **Vocabulary** — Type roles / Colour meaning / Form / Motion / Voice:
- **Counter-examples** (≥2, correct by the floor yet wrong for this language):
- **Signature** (one sentence, visible behaviour):

## Reference Deconstruction

Method: `references/01-foundations/reference-deconstruction.md`. Keep only the rows
that changed a decision; source limits live in `prototype/research.md`.

| Reference (name + link) | Level | Observation | Relationship extracted | Transfers | Refused |
|---|---|---|---|---|---|
| | | | | | |

## Project Taste & Visual Language Ledger

Records user style preferences, chosen aesthetics, and rejected visual
approaches across iterations:

| Direction / Vocabulary | Disposition (`chosen \| rejected \| under-review`) | Core Reason & User Feedback | Reference Benchmark | Applicable Scope |
|---|---|---|---|---|
| | | | | |

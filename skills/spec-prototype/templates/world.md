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

Author the six blocks once the direction is locked
(`references/01-foundations/design-language.md`); leave them empty before then.

- **THESIS**:
- **OWN-WORLD**:
- **STORY**:
- **FIRST VIEWPORT**:
- **FORM**:
- **FINISH**:

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

Optional signal colour: declare `accent_seal` only when the product has an
irreversible or high-stakes moment that earns one reserved colour. Omit the block
otherwise; the palette below stands on its own.

```contract:tokens
accent_seal: "#rrggbb"
accent_policy: <one line on when the seal colour may fire>
```

- `--bg-void`:
- `--bg-surface`:
- `--text-primary`:
- `--accent-primary`:
- `--accent-seal`: (only if declared above)

## Project Taste & Visual Language Ledger

Records user style preferences, chosen aesthetics, and rejected visual
approaches across iterations:

| Direction / Vocabulary | Disposition (`chosen \| rejected \| under-review`) | Core Reason & User Feedback | Reference Benchmark | Applicable Scope |
|---|---|---|---|---|
| | | | | |

# Style Language (风格语言卡)

Answers one question: *"What is this product's visual and interaction language, stated
as a position someone could disagree with?"* Five Axes place a design on continuous
coordinates; the Direction Contract says what the first screen claims. Neither says why
this is a *language* rather than a pile of values. The Style Language Card does, in one
section of `world.md` — no new file, no new authority.

Read it when a direction is being locked (Stage 1), revised by an expression study
(Stage 2), or judged against the render (Stage 4). Skip it for a local repair that
inherits an existing language.

## The card

Author it under `## Style Language` in `prototype/world.md` (or `discussion.md` on a
single-record tree). Draft it when the recommended direction forms; it stays
`proposed`/`provisional` under the same status rules as every other row until the user
selects the direction.

1. **Positions (3–5)** — each written `We choose X over Y, because <product reason>`.
   Both sides must be defensible. If nobody would choose Y, it is not a position.
   *Weak:* "clean over cluttered". *Strong:* "dense, ruled tables over card grids,
   because operators compare rows across 40 items".
2. **Vocabulary** — the concrete, repeatable parts the language is built from, named so
   the build and the critique can point at them:
   - **Type**: roles and what each is for (display, reading, data, label), not a family list.
   - **Colour**: what colour *means* here (state, ownership, emphasis) and where it may
     never appear. Hex values live only in `contract:tokens`.
   - **Form**: radius family, line weight, edge treatment, spacing cadence.
   - **Motion**: what moves, what never moves, and what a transition communicates.
   - **Voice**: how labels, empty states and errors speak.
3. **Counter-examples (≥2)** — things that would be *correct* by the craft floor and
   still wrong for this language, each with a one-line reason. These are the language's
   own falsifiers; Stage 4 checks the render against them. They are distinct from the
   divergence record's `rut_rejected` (the category defaults the direction refuses,
   owned by [`../dialectic/01-metaphor-benchmark.md`](../dialectic/01-metaphor-benchmark.md)
   §4): `rut_rejected` governs where the direction came from, counter-examples govern
   what the language itself would still reject.
4. **Signature** — one sentence naming the relationship that makes the product
   recognisable with the logo covered (it is the Signature Relationship from
   [`design-language.md`](design-language.md), stated as visible behaviour).

## Relationship to existing owners

| Concept | Owner | Card's role |
|---|---|---|
| Five Axes values | `contract:axes` in `world.md` | The card explains the choices; it never restates values. |
| Hex / size / duration | `contract:tokens` (sole token authority) | Vocabulary names *roles*; tokens carry numbers. |
| Six Direction Contract blocks | [`design-language.md`](design-language.md) | The card is the language behind FORM/FINISH, not a seventh block. |
| Adjective translation | [`design-language.md`](design-language.md#qualitative-adjective-translation-protocol) | Run it both ways: each adjective becomes a parameter, and the parameters together must still read as one position. |

## Testing the language

- **Cover test**: hide the logo and copy. Category recognition itself is neutral;
  the test is whether the design merely falls into generic category ruts (high
  homogeneity in the forms rejected under `rut_rejected`) or commits to intentional,
  opinionated relationships that express its Positions without relying on logo or copy.
- **Transfer test**: apply the Positions to a second surface the card did not mention.
  If a Position cannot decide a layout question there, it is a mood, not a position.
- **Cost test**: every Position names what it makes harder. A position with no cost is
  a preference.

A card that fails a test is revised or marked `open` with the reason. It is never
padded with adjectives to look complete.

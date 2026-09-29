#!/usr/bin/env python3
"""draw_seed.py: draw divergence seeds from a real entropy source.

The divergence generator's step 3 asks for a distinct seed per candidate, because
the seed varies the *incidental* choices the design does not argue for — which
face, which neutral temperature, which corner family. A model that picks its own
integer picks the same integers every time, so the step collapses into a
formality and the candidates converge before their structure differs. This script
is the mechanism that replaces the request: the seed comes from the OS entropy
pool, the incidental triple is derived from it deterministically, and the
challenger vocabulary is drawn without replacement.

The draw is written into the slice's `## Slice: <slice_id>` block, so the record
carries the entropy that produced it. Re-running is idempotent: an existing
`### Divergence seeds` block is replaced, not appended.

    python3 skills/spec-prototype/scripts/draw_seed.py --slice <slice_id> --write
"""
from __future__ import annotations

import argparse
import pathlib
import re
import secrets
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compile_spec_ir import (  # noqa: E402
    _ATX_HEADING_RE,
    _FENCE_RE,
    _SLICE_HEADING_RE,
)

VOCABULARY = (pathlib.Path(__file__).resolve().parent.parent
              / "references/02-craft-methods/modern-style-vocabulary.md")

# The incidental axes: choices the design does not argue for, so they are free to
# vary. Anything the design *does* argue for is not drawn here.
INCIDENTALS = {
    "Face": ("grotesk", "humanist-sans", "geometric-sans", "transitional-serif",
             "editorial-serif", "monospace-mixed"),
    "Neutral": ("cool-slate", "warm-paper", "neutral-ash", "green-tinted-ink",
                "blue-black", "clay-warm"),
    "Corner family": ("square", "soft-2px", "concentric-6px", "cut-corner",
                      "pill-on-controls-only"),
}

SEED_CEILING = 2 ** 31 - 1
MAX_REDRAWS = 200
SEEDS_HEADING = "### Divergence seeds"


class DrawError(ValueError):
    """Raised when the draw cannot be made or cannot be written."""


def load_challengers(path: pathlib.Path) -> list[str]:
    """The challenger vocabularies (`### A. Dense Telemetry / Instrument` …)."""
    text = path.read_text(encoding="utf-8")
    entries = re.findall(r"^###\s+([A-Z])\.\s+(.+?)\s*$", text, re.MULTILINE)
    if not entries:
        raise DrawError(f"no challenger vocabularies found in {path}")
    return [f"{letter}. {name}" for letter, name in entries]


def _incidental_triple(seed: int) -> dict[str, str]:
    """Derive the incidental choices from the seed, deterministically."""
    return {axis: options[seed % len(options)] for axis, options in INCIDENTALS.items()}


def _spread_enough(triples: list[tuple[str, ...]], minimum: int = 2) -> bool:
    """Every pair of draws differs on at least `minimum` incidental axes.

    A pair that differs on one axis is nearly the same direction on the choices
    nobody argues for, which is the convergence this draw exists to prevent.
    """
    return all(sum(a != b for a, b in zip(one, other)) >= minimum
               for i, one in enumerate(triples) for other in triples[i + 1:])


def draw(candidates: int, challengers: list[str]) -> list[dict]:
    """Draw `candidates` seeds whose incidental triples stay spread apart."""
    if candidates > len(challengers):
        raise DrawError(
            f"{candidates} candidates but only {len(challengers)} challenger "
            "vocabularies; at most one challenger per candidate")
    picks: list[dict] = []
    for _ in range(MAX_REDRAWS):
        picks = []
        for _ in range(candidates):
            seed = secrets.randbelow(SEED_CEILING)
            picks.append({"seed": seed, **_incidental_triple(seed)})
        if _spread_enough([tuple(p[axis] for axis in INCIDENTALS) for p in picks]):
            break
    else:
        raise DrawError(
            f"could not draw {candidates} candidates that differ on two incidental "
            f"axes in {MAX_REDRAWS} attempts; widen INCIDENTALS")
    drawn = secrets.SystemRandom().sample(challengers, candidates)
    for pick, challenger in zip(picks, drawn):
        pick["Challenger"] = challenger
    return picks


def render_block(picks: list[dict]) -> str:
    axes = [("Seed", "seed"), *((axis, axis) for axis in INCIDENTALS), ("Challenger", "Challenger")]
    lines = [SEEDS_HEADING, "",
             "Drawn by `scripts/draw_seed.py` from the OS entropy pool — not chosen "
             "by the designer. The seed fixes the incidental choices the direction "
             "does not argue for; the challenger is fused at step 4, or refused with "
             "its reason.", "",
             "| Candidate | " + " | ".join(label for label, _ in axes) + " |",
             "|---|" + "---|" * len(axes)]
    for index, pick in enumerate(picks):
        cells = [chr(ord("A") + index)] + [str(pick[key]) for _, key in axes]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def slice_block_span(text: str, slice_id: str) -> tuple[int, int]:
    """Character span of this slice's block body, fence-aware."""
    lines = text.splitlines(keepends=True)
    start = level = None
    in_fence = False
    offset = 0
    for line in lines:
        stripped = line.rstrip("\n")
        if _FENCE_RE.match(stripped):
            in_fence = not in_fence
        elif not in_fence:
            if start is None:
                m = _SLICE_HEADING_RE.match(stripped)
                if m and m.group(2) == slice_id:
                    level = len(m.group(1))
                    start = offset + len(line)
            else:
                m = _ATX_HEADING_RE.match(stripped)
                if m and len(m.group(1)) <= level:
                    return start, offset
        offset += len(line)
    if start is None:
        raise DrawError(
            f"no `## Slice: {slice_id}` block in the record; add the block first — "
            "a seed belongs to a slice, not to the product")
    return start, offset


def write_block(record: pathlib.Path, slice_id: str, block: str) -> None:
    """Replace the slice's seed block, or append it to the slice's block."""
    text = record.read_text(encoding="utf-8")
    start, end = slice_block_span(text, slice_id)
    body = text[start:end]
    existing = re.search(rf"^{re.escape(SEEDS_HEADING)}\b.*?(?=^#{{1,6}}\s|\Z)",
                         body, re.MULTILINE | re.DOTALL)
    if existing:
        body = body[:existing.start()] + block + "\n" + body[existing.end():].lstrip("\n")
    else:
        body = body.rstrip("\n") + "\n\n" + block + "\n"
    record.write_text(text[:start] + body + text[end:], encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--slice", required=True, help="slice_id whose block records the draw")
    parser.add_argument("--candidates", type=int, default=3)
    parser.add_argument("--record", default="prototype/discussion.md")
    parser.add_argument("--vocabulary", default=str(VOCABULARY))
    parser.add_argument("--write", action="store_true",
                        help="write the draw into the slice block (default: print only)")
    args = parser.parse_args()

    picks = draw(args.candidates, load_challengers(pathlib.Path(args.vocabulary)))
    block = render_block(picks)
    if args.write:
        write_block(pathlib.Path(args.record), args.slice, block)
        print(f"draw_seed: recorded {len(picks)} seeds in `## Slice: {args.slice}`")
    else:
        print(block)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Divergence judge: are the authored directions actually different?

Reads the exploration slots a session authored (`experiments/<slice>/dirs/*`) and
measures distance on three axes that a real direction change moves together:

  structure — the tag sequence in document order (a different organising
              principle reorders the tree, not just its colours)
  palette   — the set of colours the document declares
  typography— the set of faces it declares

Two directions that share a structure and differ only in palette are one
direction counted twice; that is the failure this judge exists to catch, and it
is the failure a text-only review cannot see. Deterministic: no model, no
screenshots.
"""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9-]*)")
STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}\n]+)")
CLASS_RE = re.compile(r'class\s*=\s*"([^"]*)"')
# Tags that carry no structural information: every document has them.
_NOISE_TAGS = frozenset({"html", "head", "meta", "title", "style", "script", "link", "body"})

STRUCTURAL_SAME = 0.85   # at or above this, the trees are the same shape
PALETTE_SAME = 0.70      # at or above this, the palettes are the same palette
TYPE_SAME = 0.80


def _fingerprint(markup: str) -> dict:
    tags = [t.lower() for t in TAG_RE.findall(markup) if t.lower() not in _NOISE_TAGS]
    css = "\n".join(STYLE_RE.findall(markup))
    colours = {c.lower() for c in HEX_RE.findall(css + markup)}
    # Normalise 3-digit hex to 6 so #abc and #aabbcc are one colour.
    colours = {c if len(c) == 7 else "#" + "".join(ch * 2 for ch in c[1:]) for c in colours}
    faces = set()
    for decl in FONT_RE.findall(css):
        for face in re.split(r",", decl):
            face = face.strip().strip("'\"").lower()
            if face and face not in ("serif", "sans-serif", "monospace", "inherit", "initial"):
                faces.add(face)
    classes = set()
    for group in CLASS_RE.findall(markup):
        classes.update(t for t in re.split(r"\s+", group.strip()) if t)
    return {"tags": tags, "colours": colours, "faces": faces, "classes": classes}


def _jaccard(a: set, b: set):
    """Overlap, or None when there is nothing to compare.

    Two empty sets are *unmeasured*, not identical: treating them as a perfect
    match once made two structurally different directions read as one.
    """
    if not a or not b:
        return None
    return round(len(a & b) / len(a | b), 4)


def _structural_similarity(a: list, b: list) -> float:
    if not a or not b:
        return 0.0
    return round(difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio(), 4)


def _pairs(items: list) -> list:
    return [(items[i], items[j]) for i in range(len(items)) for j in range(i + 1, len(items))]


def judge(artifacts_dir: pathlib.Path) -> dict:
    artifacts_dir = pathlib.Path(artifacts_dir)
    slots: dict[str, pathlib.Path] = {}
    for candidate in sorted(artifacts_dir.rglob("dirs/*/index.html")):
        slot = candidate.parent.name
        slots[slot] = candidate
    if len(slots) < 2:
        return {"judge": "divergence", "status": "insufficient",
                "slots": sorted(slots), "pairs": [], "verdict": "not_measured",
                "note": f"{len(slots)} direction slot(s) found; divergence needs at least 2 "
                        "(a single-direction extension is out of scope for this judge)"}

    prints = {slot: _fingerprint(path.read_text(encoding="utf-8", errors="replace"))
              for slot, path in slots.items()}
    results = []
    for left, right in _pairs(sorted(prints)):
        a, b = prints[left], prints[right]
        structure = _structural_similarity(a["tags"], b["tags"])
        palette = _jaccard(a["colours"], b["colours"])
        typography = _jaccard(a["faces"], b["faces"])
        same_shape = structure >= STRUCTURAL_SAME
        same_palette = palette is not None and palette >= PALETTE_SAME
        same_type = typography is not None and typography >= TYPE_SAME
        # Structure is the primary axis: a direction that keeps the tree and moves
        # only its colours is one direction counted twice, however it is dressed.
        if not same_shape:
            verdict = "divergent"
        elif palette is not None and not same_palette:
            verdict = "recolouring"
        elif same_palette and same_type:
            verdict = "duplicate"
        else:
            verdict = "shared_skeleton"
        results.append({
            "pair": f"{left}-{right}",
            "structural_similarity": structure,
            "palette_overlap": palette,
            "typography_overlap": typography,
            "verdict": verdict,
            "colour_delta": sorted(a["colours"] ^ b["colours"])[:12],
        })

    distinct = sum(1 for r in results if r["verdict"] == "divergent")
    total = len(results)
    if total and distinct == total:
        overall = "divergent"
    elif any(r["verdict"] in ("recolouring", "duplicate") for r in results):
        overall = "pseudo_divergence"
    else:
        overall = "shared_skeleton"
    return {
        "judge": "divergence",
        "status": "measured",
        "slots": sorted(slots),
        "pairs": results,
        "verdict": overall,
        "distinct_pairs": distinct,
        "total_pairs": total,
        "thresholds": {"structural_same": STRUCTURAL_SAME, "palette_same": PALETTE_SAME,
                       "type_same": TYPE_SAME},
        "note": "structure is tag order in document order; palette and typography are declared sets",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    result = judge(pathlib.Path(args.artifacts))
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "measured" else 2


if __name__ == "__main__":
    sys.exit(main())

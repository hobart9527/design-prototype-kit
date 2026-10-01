#!/usr/bin/env python3
"""Rule-ID detector: the craft floor's prose and the machine checks, anchored both ways.

`craft-floor.md` states the floor in prose; `verify_prototype_quality.py` and the
benchmark's `slop_detector.py` check parts of it mechanically. Without an explicit
anchor the two drift: a rule gets added to one side and not the other, and the prose
quietly stops describing what is actually enforced.

This module is that anchor. Every craft-floor rule carries a stable id, and each id
declares how it is detected:

  `check`      a function in this module, runnable against an artifact
  `prose_only` no mechanical check — a judgement the craft floor owns by hand

`anchor_report()` returns the registry in both directions, so a test can assert the
prose and the detectors still agree. Rules that are prose-only are listed as such
rather than silently absent: "not machine-checkable" is a status, not a gap.

Detection is deliberately shallow — a regex over the artifact's own bytes. It exists
to keep the registry honest, not to replace the craft review.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

# -- detectors -----------------------------------------------------------------

def _artifact_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _has_active_detent(path: pathlib.Path) -> bool:
    return bool(re.search(r":active\b", _artifact_text(path)))


def _has_tabular_nums(path: pathlib.Path) -> bool:
    return bool(re.search(r"font-variant-numeric\s*:\s*[^;}]*tabular-nums",
                          _artifact_text(path)))


def _has_focus_visible(path: pathlib.Path) -> bool:
    return bool(re.search(r":focus-visible\b", _artifact_text(path)))


def _has_selection_theme(path: pathlib.Path) -> bool:
    return bool(re.search(r"::selection\b", _artifact_text(path)))


def _has_caret_theme(path: pathlib.Path) -> bool:
    return bool(re.search(r"caret-color\b", _artifact_text(path)))


def _has_scrollbar_theme(path: pathlib.Path) -> bool:
    return bool(re.search(r"::-webkit-scrollbar|scrollbar-color\b", _artifact_text(path)))


def _has_gradient_text(path: pathlib.Path) -> bool:
    return bool(re.search(r"background-clip\s*:\s*text", _artifact_text(path), re.IGNORECASE))


def _has_emoji_icon(path: pathlib.Path) -> bool:
    emoji = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
    return bool(emoji.search(_artifact_text(path)))


# -- registry ------------------------------------------------------------------
# id -> (rule as the craft floor states it, kind, detector or None)
# A `prose_only` entry names why it cannot be mechanised, so the reason is on the
# record rather than inferred from the detector's absence.

RULES: dict[str, dict] = {
    "CRAFT-PRESS-DETENT": {
        "prose": "every commit control shows a perceptible :active change",
        "kind": "check", "detector": _has_active_detent,
    },
    "CRAFT-TABULAR-NUMS": {
        "prose": "values that update in place or align in columns carry tabular-nums",
        "kind": "check", "detector": _has_tabular_nums,
    },
    "CRAFT-FOCUS-RING": {
        "prose": "focus rings are themed from the palette, not left at browser default",
        "kind": "check", "detector": _has_focus_visible,
    },
    "CRAFT-SELECTION": {
        "prose": "text selection carries the design",
        "kind": "check", "detector": _has_selection_theme,
    },
    "CRAFT-CARET": {
        "prose": "the caret carries the design",
        "kind": "check", "detector": _has_caret_theme,
    },
    "CRAFT-SCROLLBAR": {
        "prose": "custom scrollbars carry the design",
        "kind": "check", "detector": _has_scrollbar_theme,
    },
    "CRAFT-NO-GRADIENT-TEXT": {
        "prose": "gradient text is refused as emphasis",
        "kind": "check", "detector": _has_gradient_text,
    },
    "CRAFT-NO-EMOJI-ICON": {
        "prose": "emoji or Unicode glyphs are not the icon system",
        "kind": "check", "detector": _has_emoji_icon,
    },
    # Judgement calls the craft floor owns by hand. Listed so their absence from
    # the detectors reads as a decision, not an oversight.
    "CRAFT-CONCENTRIC-RADII": {
        "prose": "a rounded child in a rounded parent satisfies R_inner = max(0, R_outer - P)",
        "kind": "prose_only",
        "why": "needs the computed geometry of a nested pair, not a text scan; "
               "checked by verify_prototype_quality's rendered probe",
    },
    "CRAFT-TOUCH-TARGET": {
        "prose": "interactive controls measure at least 44x44px in touch contexts",
        "kind": "prose_only",
        "why": "needs rendered box metrics at a declared viewport",
    },
    "CRAFT-CARD-GRID-EARNED": {
        "prose": "same-size card grids are refused unless the objects are genuinely peers",
        "kind": "prose_only",
        "why": "whether a card grid is earned is a design judgement",
    },
    "CRAFT-NO-EYEBROW": {
        "prose": "an eyebrow or kicker above a heading is refused",
        "kind": "prose_only",
        "why": "distinguishing a kicker from a legitimate label needs reading the content",
    },
    "CRAFT-REAL-CONTENT": {
        "prose": "plausible domain copy and real assets, never a gradient blob in an image slot",
        "kind": "prose_only",
        "why": "content plausibility is judged against the brief, not a pattern",
    },
    "CRAFT-THEME-ORIGIN": {
        "prose": "light or dark is chosen from the use scene, not the product category",
        "kind": "prose_only",
        "why": "the use scene is in the brief, not the artifact",
    },
}

# The benchmark detector's rules, mapped onto the craft floor they check. Kept here
# so the two rule sets cannot drift apart silently.
BENCHMARK_ANCHORS = {
    "SLOP-001": "CRAFT-NO-GRADIENT-TEXT",
    "SLOP-009": "CRAFT-NO-EMOJI-ICON",
    "SLOP-017": "CRAFT-SELECTION",
    "SLOP-018": "CRAFT-PRESS-DETENT",
    "SLOP-019": "CRAFT-TABULAR-NUMS",
}


def scan(artifact: pathlib.Path) -> dict:
    """Run every mechanical rule against one artifact. Judgement rules are listed."""
    artifact = pathlib.Path(artifact)
    if not artifact.is_file():
        raise FileNotFoundError(f"Craft floor detector target artifact not found: {artifact}")
    findings, unchecked = [], []
    for rule_id, entry in sorted(RULES.items()):
        if entry["kind"] != "check":
            unchecked.append({"rule": rule_id, "why": entry["why"]})
            continue
        try:
            hit = entry["detector"](artifact)
        except Exception as exc:  # a broken detector must surface, not read as clean
            findings.append({"rule": rule_id, "status": "error", "error": str(exc)})
            continue
        findings.append({"rule": rule_id, "status": "hit" if hit else "clear",
                         "prose": entry["prose"]})
    return {"detector": "craft-floor", "artifact": str(artifact),
            "findings": findings, "unchecked": unchecked,
            "checked": sum(1 for f in findings if f["status"] in ("hit", "clear"))}


def anchor_report() -> dict:
    """The registry in both directions, for the drift test."""
    return {
        "rules": {rid: {"kind": e["kind"], "prose": e["prose"]} for rid, e in RULES.items()},
        "benchmark_anchors": dict(BENCHMARK_ANCHORS),
        "counts": {
            "total": len(RULES),
            "check": sum(1 for e in RULES.values() if e["kind"] == "check"),
            "prose_only": sum(1 for e in RULES.values() if e["kind"] == "prose_only"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Craft-floor rule-ID detector")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    try:
        result = scan(pathlib.Path(args.artifact))
    except FileNotFoundError as err:
        sys.stderr.write("Error: " + str(err) + "\n")
        return 1
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        pathlib.Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

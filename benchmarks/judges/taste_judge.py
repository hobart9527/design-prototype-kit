#!/usr/bin/env python3
"""Blind taste judge: category/homogeneity/distinctiveness, AI-slop, first viewport.

Category recognition is measured as a neutral description (category_guessability);
how far the design converges on its category's common forms is measured separately
(homogeneity). Neither is a quality rank — a familiar, category-appropriate form
can be the best choice.

Reads screenshots only. Identity stays in the caller's manifest; this module
never learns which variant produced what. A judgement that cannot be made from
the images is reported `unverifiable`, never guessed into a score.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402


def _calibration_specimens() -> str:
    """Load the Calibration Specimens section from the skill's reference set.

    Same file the skill's Stage 4 Critic reads; loading it here keeps both
    sides of the taste judgement anchored to the same observable differences.
    """
    path = bl.ROOT / "skills/spec-prototype/references/05-benchmarks/reference-set.md"
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"## Calibration Specimens\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    return m.group(1).strip() if m else ""


SCHEMA = json.dumps({
    "type": "object",
    "required": ["guessed_category", "category_guessability", "homogeneity",
                 "ai_slop_verdict", "first_viewport_thesis", "distinctiveness", "restraint"],
    "properties": {
        "guessed_category": {"type": "string"},
        "category_confidence": {"enum": ["low", "medium", "high"]},
        "category_guessability": {"enum": ["low", "medium", "high"]},
        "homogeneity": {"enum": ["low", "medium", "high"]},
        "ai_slop_verdict": {"enum": ["pass", "borderline", "fail"]},
        "ai_slop_signals": {"type": "array", "items": {"type": "string"}},
        "first_viewport_claim": {"type": "string"},
        "first_viewport_thesis": {"enum": ["present", "weak", "absent", "unverifiable"]},
        "distinctiveness": {"type": "number", "minimum": 0, "maximum": 10},
        "restraint": {"type": "number", "minimum": 0, "maximum": 10},
        "craft_signals": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "string"},
    },
})


def judge(case: dict, screenshots: list, workdir: pathlib.Path, *, model: str | None = None,
          timeout_s: int = 600) -> dict:
    """screenshots: paths to the captured viewports, widest last.

    One representative viewport is staged (the last, normally the widest) to keep
    the vision call affordable; the taste signal does not change with more images.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    staged = []
    for index, src in enumerate((screenshots or [])[-1:]):
        # Resolve before linking: a symlink target is interpreted relative to the
        # link's own directory, so a caller-relative path stages a broken link and
        # the judge reads nothing.
        src = pathlib.Path(src).resolve()
        if not src.is_file():
            continue
        dst = workdir / f"shot-{index}-{src.name}"
        if not dst.exists():
            dst.symlink_to(src)
        staged.append(dst.name)
    if not staged:
        return {"judge": "taste", "status": "unverified",
                "note": "no screenshots available to judge", "result": None, "metrics": None}
    # Load the calibration specimens the skill's Critic also reads, so both
    # sides anchor "competent vs excellent" to the same observable differences
    # rather than a bare preference. The specimens are text, not screenshots —
    # they define what the judge looks for, not what it sees.
    calibration = _calibration_specimens()
    prompt = bl.render(
        bl.prompt_template("taste-judge.txt"),
        brief=case["brief"],
        shots=", ".join(staged),
        calibration=calibration,
    )
    response = bl.ask_json(prompt, workdir, schema=SCHEMA, model=model, timeout_s=timeout_s,
                           allowed_tools="Read")
    data = response["data"] or {}
    return {
        "judge": "taste",
        "status": "judged" if response["ok"] else "unverified",
        "files": staged,
        "result": data,
        "raw": response["raw"][:4000] if not response["ok"] else None,
        "metrics": response["metrics"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--screenshots", nargs="+", required=True)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    result = judge(bl.load_case(args.case), args.screenshots, pathlib.Path(args.workdir), model=args.model)
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "judged" else 1


if __name__ == "__main__":
    sys.exit(main())

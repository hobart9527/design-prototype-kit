#!/usr/bin/env python3
"""Blind pairwise design judge over captured screenshots.

Identity, variant and score history stay in the caller's blind manifest; this
module only ever sees "alpha" and "beta".
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

SCHEMA = json.dumps({
    "type": "object",
    "required": ["overall_preference", "confidence", "dimensions"],
    "properties": {
        "overall_preference": {"enum": ["alpha", "beta", "tie"]},
        "confidence": {"enum": ["low", "medium", "high"]},
        "dimensions": {"type": "array", "items": {"type": "object",
            "properties": {"name": {"type": "string"}, "preference": {"enum": ["alpha", "beta", "tie"]},
                           "reason": {"type": "string"}}}},
    },
})


def judge(case: dict, screenshots: dict, workdir: pathlib.Path, *, model: str | None = None,
          timeout_s: int = 600) -> dict:
    """screenshots: {"alpha": [paths], "beta": [paths]}.

    The caller owns blind assignment: it decides which variant occupies the
    alpha slot and records that mapping in the pair's blind-manifest.json, which
    is never shown to this judge.
    """
    alpha, beta = "alpha", "beta"
    workdir.mkdir(parents=True, exist_ok=True)
    staged = {}
    for label in ("alpha", "beta"):
        files = []
        # One representative viewport keeps the vision judge affordable; more
        # images multiply cost without changing the preference signal much.
        for index, src in enumerate((screenshots.get(label) or [])[-1:]):
            src = pathlib.Path(src)
            dst = workdir / f"{label}-{index}-{src.name}"
            if not dst.exists():
                dst.symlink_to(src)
            files.append(dst.name)
        staged[label] = files
    prompt = bl.render(
        bl.prompt_template("pairwise-judge.txt"),
        brief=case["brief"],
        alpha=", ".join(staged[alpha]) or "(none)",
        beta=", ".join(staged[beta]) or "(none)",
    )
    response = bl.ask_json(prompt, workdir, schema=SCHEMA, model=model, timeout_s=timeout_s, allowed_tools="Read")
    result = {
        "judge": "pairwise",
        "status": "judged" if response["ok"] else "unverified",
        "alpha_files": staged[alpha],
        "beta_files": staged[beta],
        "result": response["data"],
        "raw": response["raw"][:4000] if not response["ok"] else None,
        "metrics": response["metrics"],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--alpha", nargs="+", required=True)
    parser.add_argument("--beta", nargs="+", required=True)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    case = bl.load_case(args.case)
    result = judge(case, {"alpha": args.alpha, "beta": args.beta}, pathlib.Path(args.workdir), model=args.model)
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "judged" else 1


if __name__ == "__main__":
    sys.exit(main())

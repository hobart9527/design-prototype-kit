#!/usr/bin/env python3
"""Paired regression check: candidate must not be worse than stable.

Only pairs with matching case, repeat and control conditions are compared
(BENCH-004). Missing pairs are inconclusive, never a pass.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

# An unverified arm is evidence of nothing (BENCH-004). Ranking it below BLOCKED
# would read two unverified arms as a verified improvement.
BASE_RANK = {"pass": 0, "pass_with_unknowns": 0, "not_applicable": 0,
             "unverified": 1, "blocked": 1, "inconclusive": 1, "fail": 2}


def _severity(status) -> int:
    return BASE_RANK.get(status, 1) if isinstance(status, str) else 1


def _dimension_status(run: dict, dimension: str):
    if dimension == "runtime":
        runtime = run.get("runtime") or {}
        return runtime.get("status")
    if dimension == "semantic":
        semantic = run.get("semantic") or {}
        return semantic.get("hard_gate")
    if dimension == "task":
        task = run.get("task") or {}
        return task.get("status")
    return None


def judge(runs: list) -> dict:
    index = {(r.get("case_id"), r.get("variant"), r.get("repeat", 1)): r for r in runs}
    regressions, improvements, missing = [], [], []
    unverifiable, verified_pairs = [], []
    for (case_id, variant, repeat), run in index.items():
        if variant != "candidate_skill":
            continue
        stable = index.get((case_id, "stable_skill", repeat))
        if not stable:
            missing.append({"case_id": case_id, "repeat": repeat, "why": "no stable_skill pair"})
            continue
        compared = False
        for dimension in ("runtime", "semantic", "task"):
            cand_status, stable_status = _dimension_status(run, dimension), _dimension_status(stable, dimension)
            if cand_status is None or stable_status is None:
                continue
            compared = True
            if cand_status == "unverified" or stable_status == "unverified":
                # Unverified compares to nothing: not a regression, not an improvement.
                unverifiable.append({"case_id": case_id, "repeat": repeat, "dimension": dimension,
                                     "stable": stable_status, "candidate": cand_status})
                continue
            cand_rank, stable_rank = _severity(cand_status), _severity(stable_status)
            if cand_rank > stable_rank:
                regressions.append({"case_id": case_id, "repeat": repeat, "dimension": dimension,
                                    "stable": stable_status, "candidate": cand_status})
            elif cand_rank < stable_rank:
                improvements.append({"case_id": case_id, "repeat": repeat, "dimension": dimension,
                                     "stable": stable_status, "candidate": cand_status})
            else:
                verified_pairs.append({"case_id": case_id, "repeat": repeat, "dimension": dimension,
                                       "stable": stable_status, "candidate": cand_status})
        if not compared:
            missing.append({"case_id": case_id, "repeat": repeat, "why": "no dimension recorded on both arms"})
    pairs = sum(1 for (case_id, variant, _r) in index if variant == "candidate_skill"
                and (case_id, "stable_skill", _r) in index)
    if regressions:
        verdict = "REGRESSION"
    elif not verified_pairs and not improvements:
        verdict = "INCONCLUSIVE"
    elif unverifiable or missing:
        verdict = "PASS_WITH_UNKNOWNS"
    else:
        verdict = "PASS"
    compared_dimensions = len(verified_pairs) + len(improvements) + len(regressions) + len(unverifiable)
    return {"judge": "regression", "verdict": verdict, "pairs_compared": pairs,
            "compared_dimensions": compared_dimensions,
            "verified_dimensions": verified_pairs, "unverifiable_dimensions": unverifiable,
            "regressions": regressions, "improvements": improvements, "missing_pairs": missing}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", required=True, help="JSON list of run-result objects, or a matrix dir")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    path = pathlib.Path(args.runs)
    if path.is_dir():
        runs = [bl.read_json(p) for p in sorted(path.rglob("run-result.json"))]
    else:
        runs = bl.read_json(path)
    result = judge(runs)
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["verdict"] in ("PASS", "PASS_WITH_UNKNOWNS") else 1


if __name__ == "__main__":
    sys.exit(main())

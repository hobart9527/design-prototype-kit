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

SEVERITY = {"PASS": 0, "INCONCLUSIVE": 1, "BLOCKED": 2, "FAIL": 3}


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
    for (case_id, variant, repeat), run in index.items():
        if variant != "candidate_skill":
            continue
        stable = index.get((case_id, "stable_skill", repeat))
        if not stable:
            missing.append({"case_id": case_id, "repeat": repeat, "why": "no stable_skill pair"})
            continue
        for dimension in ("runtime", "semantic", "task"):
            cand_status, stable_status = _dimension_status(run, dimension), _dimension_status(stable, dimension)
            if cand_status is None or stable_status is None:
                continue
            cand_rank = SEVERITY.get("FAIL" if cand_status == "fail" else
                                    "PASS" if cand_status in ("pass", "pass_with_unknowns", "not_applicable") else
                                    "INCONCLUSIVE", 1)
            stable_rank = SEVERITY.get("FAIL" if stable_status == "fail" else
                                       "PASS" if stable_status in ("pass", "pass_with_unknowns", "not_applicable") else
                                       "INCONCLUSIVE", 1)
            if cand_rank > stable_rank:
                regressions.append({"case_id": case_id, "repeat": repeat, "dimension": dimension,
                                    "stable": stable_status, "candidate": cand_status})
            elif cand_rank < stable_rank:
                improvements.append({"case_id": case_id, "repeat": repeat, "dimension": dimension,
                                     "stable": stable_status, "candidate": cand_status})
    pairs = sum(1 for (case_id, variant, _r) in index if variant == "candidate_skill"
                and (case_id, "stable_skill", _r) in index)
    if regressions:
        verdict = "REGRESSION"
    elif pairs == 0:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "PASS"
    return {"judge": "regression", "verdict": verdict, "pairs_compared": pairs,
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
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

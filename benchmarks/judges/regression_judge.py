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


def _taste_status(run: dict):
    """Taste-layer regression signal, or None when the run carries no taste evidence.

    Two independent signals, either of which can regress: the deterministic slop
    score (lower is better) and the blind taste verdicts. The slop score compares
    only when both arms measured it — a missing score is unverified, never zero.
    """
    slop = run.get("slop") or {}
    taste = (run.get("taste") or {}).get("result") or {}
    fidelity = (run.get("contract_fidelity") or {}).get("result") or {}
    divergence = (run.get("divergence") or {}).get("verdict")
    cocreation = (run.get("cocreation") or {}).get("verdict")
    if (slop.get("status") != "detected" and not taste and not fidelity and not divergence
            and not cocreation):
        return None
    verdicts = []
    if taste.get("ai_slop_verdict"):
        verdicts.append({"signal": "ai_slop_verdict", "value": taste["ai_slop_verdict"]})
    if taste.get("first_viewport_thesis"):
        verdicts.append({"signal": "first_viewport_thesis", "value": taste["first_viewport_thesis"]})
    if taste.get("category_guessability"):
        verdicts.append({"signal": "category_guessability", "value": taste["category_guessability"]})
    blocks = fidelity.get("blocks") or []
    if blocks:
        verdicts.append({"signal": "contract_blocks_fulfilled",
                         "value": sum(1 for b in blocks if b.get("verdict") == "fulfilled")})
        verdicts.append({"signal": "contract_blocks_absent",
                         "value": sum(1 for b in blocks if b.get("verdict") == "absent")})
    if divergence:
        verdicts.append({"signal": "divergence_verdict", "value": divergence})
    if cocreation:
        verdicts.append({"signal": "cocreation_verdict", "value": cocreation})
    return {"slop_score": slop.get("slop_score") if slop.get("status") == "detected" else None,
            "signals": verdicts}


# Ranked so a move up the list is a regression. Anything unranked is unverifiable.
_SLOP_RANK = {"pass": 0, "borderline": 1, "fail": 2}
_THESIS_RANK = {"present": 0, "weak": 1, "absent": 2}
_GUESS_RANK = {"low": 0, "medium": 1, "high": 2}
_DIVERGENCE_RANK = {"divergent": 0, "shared_skeleton": 1, "pseudo_divergence": 2,
                    "duplicate": 3, "recolouring": 3, "not_measured": 0, "insufficient": 0}
# A session that revealed a decision instead of sharing one is worse than one that
# asked; a false confirmation is worse still, because it claims authority it lacks.
_COCREATION_RANK = {"co_created": 0, "not_measured": 0, "partial": 1, "reveal_only": 2,
                    "false_confirmation": 3}
_TASTE_RANKS = {"ai_slop_verdict": _SLOP_RANK, "first_viewport_thesis": _THESIS_RANK,
                "category_guessability": _GUESS_RANK, "divergence_verdict": _DIVERGENCE_RANK,
                "cocreation_verdict": _COCREATION_RANK}


def _taste_regression(cand: dict, stable: dict) -> list:
    """Ranked taste signals where the candidate is worse than the control.

    Only ranked signals compare; a signal absent on either arm is skipped rather
    than treated as a win or a loss.
    """
    out = []
    stable_signals = {s["signal"]: s["value"] for s in (stable.get("signals") or [])}
    for item in cand.get("signals") or []:
        ranks = _TASTE_RANKS.get(item["signal"])
        if not ranks or item["signal"] not in stable_signals:
            continue
        cand_rank, stable_rank = ranks.get(item["value"]), ranks.get(stable_signals[item["signal"]])
        if cand_rank is None or stable_rank is None:
            continue
        if cand_rank > stable_rank:
            out.append({"signal": item["signal"], "stable": stable_signals[item["signal"]],
                        "candidate": item["value"]})
    cand_slop, stable_slop = cand.get("slop_score"), stable.get("slop_score")
    if isinstance(cand_slop, (int, float)) and isinstance(stable_slop, (int, float)) and cand_slop > stable_slop:
        out.append({"signal": "slop_score", "stable": stable_slop, "candidate": cand_slop})
    return out


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

        # Taste is a separate dimension with its own evidence: it compares only
        # when both arms measured it, and its own verdicts are ranked, not scored.
        cand_taste, stable_taste = _taste_status(run), _taste_status(stable)
        if cand_taste and stable_taste:
            compared = True
            taste_regressions = _taste_regression(cand_taste, stable_taste)
            for item in taste_regressions:
                regressions.append({"case_id": case_id, "repeat": repeat, "dimension": "taste",
                                    "stable": item["stable"], "candidate": item["candidate"],
                                    "signal": item["signal"]})
            if not taste_regressions:
                verified_pairs.append({"case_id": case_id, "repeat": repeat, "dimension": "taste",
                                       "stable": stable_taste.get("slop_score"),
                                       "candidate": cand_taste.get("slop_score")})
        elif cand_taste or stable_taste:
            unverifiable.append({"case_id": case_id, "repeat": repeat, "dimension": "taste",
                                 "stable": "measured" if stable_taste else "unmeasured",
                                 "candidate": "measured" if cand_taste else "unmeasured"})
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

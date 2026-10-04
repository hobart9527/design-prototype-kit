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
          timeout_s: int = 600, swap_replicates: int = 1) -> dict:
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
            # Resolve before linking: a symlink target is interpreted relative to
            # the link's own directory, so a caller-relative path stages a broken
            # link and the judge reads nothing.
            src = pathlib.Path(src).resolve()
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
    replicas = []
    swap_calls = []
    for index in range(max(0, swap_replicates)):
        # Independent call with the same images reversed. Normalize its labels
        # back to the original slots before measuring judge order sensitivity.
        swapped_prompt = bl.render(
            bl.prompt_template("pairwise-judge.txt"), brief=case["brief"],
            alpha=", ".join(staged[beta]) or "(none)",
            beta=", ".join(staged[alpha]) or "(none)")
        swapped = bl.ask_json(swapped_prompt, workdir / f"swap-{index + 1}", schema=SCHEMA,
                              model=model, timeout_s=timeout_s, allowed_tools="Read")
        swap_calls.append(swapped)
        data = swapped.get("data") or {}
        pref = {"alpha": "beta", "beta": "alpha", "tie": "tie"}.get(data.get("overall_preference"))
        replicas.append({"status": "judged" if swapped["ok"] else "unverified",
                         "normalized_preference": pref, "confidence": data.get("confidence")})
    call_metrics = [response["metrics"], *(swapped_call["metrics"] for swapped_call in swap_calls)]
    recorded_costs = [m["cost_usd"] for m in call_metrics if isinstance(m.get("cost_usd"), (int, float))]
    elapsed_values = [m["elapsed_s"] for m in call_metrics if isinstance(m.get("elapsed_s"), (int, float))]
    metrics = {
        **response["metrics"],
        "cost_usd": round(sum(recorded_costs), 4) if len(recorded_costs) == len(call_metrics) else None,
        "elapsed_s": round(sum(elapsed_values), 3) if len(elapsed_values) == len(call_metrics) else None,
        "calls": call_metrics,
        "calls_total": len(call_metrics),
        "calls_cost_recorded": len(recorded_costs),
    }
    result = {
        "judge": "pairwise",
        "status": "judged" if response["ok"] else "unverified",
        "alpha_files": staged[alpha],
        "beta_files": staged[beta],
        "result": response["data"],
        "raw": response["raw"][:4000] if not response["ok"] else None,
        "metrics": metrics,
        "swap_replicates": replicas,
        "swap_agreement": (sum(1 for r in replicas if r["normalized_preference"] ==
                                (response.get("data") or {}).get("overall_preference")) / len(replicas)
                           if response["ok"] and replicas and all(r["status"] == "judged" for r in replicas)
                           else None),
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

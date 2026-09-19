#!/usr/bin/env python3
"""One command for a whole suite: sessions, judges, pairwise, report.

    python benchmarks/runners/run_matrix.py --suite daily --variants stable,candidate --repeats 1
    python benchmarks/runners/run_matrix.py --suite golden --repeats 3 --task-trace --pairwise
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "judges"))
import bench_lib as bl  # noqa: E402
import aggregate_report  # noqa: E402
import pairwise_judge  # noqa: E402
import run_frontend_reproduction  # noqa: E402

PAIRS = (("stable_skill", "no_skill"), ("candidate_skill", "stable_skill"))


def _run_sessions(cases, variants, repeats, matrix_dir, args) -> list:
    results = []
    total = len(cases) * len(variants) * repeats
    index = 0
    for case_id in cases:
        for variant in variants:
            for repeat in range(1, repeats + 1):
                index += 1
                bl.eprint(f"[matrix] {index}/{total} {case_id}/{variant}/r{repeat}")
                cmd = [sys.executable, str(bl.BENCH / "runners" / "run_case.py"),
                       "--case", case_id, "--variant", variant, "--repeat", str(repeat),
                       "--matrix-dir", str(matrix_dir)]
                if args.model:
                    cmd += ["--model", args.model]
                if args.max_turns:
                    cmd += ["--max-turns", str(args.max_turns)]
                if args.timeout:
                    cmd += ["--timeout", str(args.timeout)]
                if args.budget_usd is not None:
                    cmd += ["--budget-usd", str(args.budget_usd)]
                if args.task_trace:
                    cmd += ["--task-trace", "--max-task-steps", str(args.max_task_steps)]
                if args.visual:
                    cmd += ["--visual"]
                if args.session_budget_usd is not None:
                    cmd += ["--session-budget-usd", str(args.session_budget_usd)]
                if args.rejudge:
                    cmd += ["--rejudge"]
                if args.open:
                    cmd += ["--open"]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.stderr.strip():
                    bl.eprint(proc.stderr.strip()[-1500:])
                run_file = matrix_dir / case_id / variant / f"run{repeat}" / "run-result.json"
                if run_file.is_file():
                    results.append(bl.read_json(run_file))
                else:
                    results.append({"case_id": case_id, "variant": variant, "repeat": repeat,
                                    "status": "BLOCKED",
                                    "notes": [f"runner exited {proc.returncode} without a result"], "metrics": {}})
    return results


def _rejudge_existing(cases, variants, repeats, matrix_dir, args) -> list:
    """Re-run judges over already collected artifacts; never starts a session."""
    results = []
    for case_id in cases:
        for variant in variants:
            for repeat in range(1, repeats + 1):
                run_dir = matrix_dir / case_id / variant / f"run{repeat}"
                if not (run_dir / "artifacts").is_dir():
                    bl.eprint(f"[rejudge] skip {case_id}/{variant}/r{repeat}: no collected artifacts")
                    continue
                bl.eprint(f"[rejudge] {case_id}/{variant}/r{repeat}")
                cmd = [sys.executable, str(bl.BENCH / "runners" / "run_case.py"),
                       "--case", case_id, "--variant", variant, "--repeat", str(repeat),
                       "--matrix-dir", str(matrix_dir), "--rejudge"]
                if args.model:
                    cmd += ["--model", args.model]
                if args.task_trace:
                    cmd += ["--task-trace", "--max-task-steps", str(args.max_task_steps)]
                if args.visual:
                    cmd += ["--visual"]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.stderr.strip():
                    bl.eprint(proc.stderr.strip()[-800:])
                run_file = run_dir / "run-result.json"
                if run_file.is_file():
                    results.append(bl.read_json(run_file))
    return results


def _pairwise(cases, matrix_dir, model, seed) -> list:
    outcomes = []
    for case_id in cases:
        for left, right in PAIRS:
            left_runs = sorted(matrix_dir.glob(f"{case_id}/{left}/run*/visual-manifest.json"))
            right_runs = sorted(matrix_dir.glob(f"{case_id}/{right}/run*/visual-manifest.json"))
            if not left_runs or not right_runs:
                outcomes.append({"case_id": case_id, "pair": f"{left}_vs_{right}", "status": "unverified",
                                 "note": "screenshots missing for one or both variants"})
                continue
            case = bl.load_case(case_id)
            rng = random.Random(f"{seed}:{case_id}:{left}:{right}")
            flip = rng.random() < 0.5
            blind = {"alpha_variant": right if flip else left, "beta_variant": left if flip else right,
                     "alpha_run": str(right_runs[0]) if flip else str(left_runs[0]),
                     "beta_run": str(left_runs[0]) if flip else str(right_runs[0])}
            pair_dir = matrix_dir / "pairwise" / f"{case_id}-{left}-vs-{right}"
            pair_dir.mkdir(parents=True, exist_ok=True)
            bl.write_json(pair_dir / "blind-manifest.json", blind)
            screenshots = {}
            for label, manifest_path in (("alpha", blind["alpha_run"]), ("beta", blind["beta_run"])):
                manifest = bl.read_json(pathlib.Path(manifest_path))
                screenshots[label] = [v["screenshot"] for v in manifest.get("viewports", []) if v.get("screenshot")]
            judgement = pairwise_judge.judge(case, screenshots, pair_dir / "work", model=model)
            judgement["case_id"] = case_id
            judgement["pair"] = f"{left}_vs_{right}"
            result_path = pair_dir / "result.json"
            if result_path.is_file():
                archive = pair_dir / f"result-prev{len(list(pair_dir.glob('result-prev*.json'))) + 1}.json"
                result_path.rename(archive)
            bl.write_json(pair_dir / "result.json", judgement)
            judgement["blind_manifest_path"] = str(pair_dir / "blind-manifest.json")
            bl.write_json(result_path, judgement)
            outcomes.append(judgement)
            bl.eprint(f"[pairwise] {case_id} {left} vs {right} -> {judgement['status']}")
    return outcomes


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a benchmark suite end to end")
    parser.add_argument("--suite", default="daily",
                        choices=["daily", "golden", "calibration", "holdout", "release", "custom"])
    parser.add_argument("--cases", default=None, help="comma-separated case ids (overrides --suite)")
    parser.add_argument("--variants", default="stable_skill,candidate_skill")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=None)
    parser.add_argument("--budget-usd", type=float, default=None)
    parser.add_argument("--task-trace", action="store_true")
    parser.add_argument("--max-task-steps", type=int, default=6)
    parser.add_argument("--visual", action="store_true")
    parser.add_argument("--pairwise", action="store_true")
    parser.add_argument("--frontend-reproduction", action="store_true")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--session-budget-usd", type=float, default=None)
    parser.add_argument("--rejudge", action="store_true",
                        help="re-run judges and the report over an existing run without new sessions")
    parser.add_argument("--open", action="store_true",
                        help="automatically open each completed prototype/portal in the browser")
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--carry-over-control", default=None, metavar="MATRIX_DIR",
                        help="copy the no_skill control runs from another matrix dir (reuse an expensive control)")
    args = parser.parse_args()

    run_id = args.run_id or bl.now_stamp()
    matrix_dir = bl.RESULTS_DIR / run_id
    matrix_dir.mkdir(parents=True, exist_ok=True)
    cases = [c.strip() for c in args.cases.split(",")] if args.cases else bl.cases_for_suite(args.suite)
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    for variant in variants:
        if variant not in bl.VARIANTS:
            bl.eprint(f"unknown variant: {variant}")
            return 2

    bl.write_json(matrix_dir / "matrix-plan.json", {
        "run_id": run_id, "suite": args.suite, "cases": cases, "variants": variants,
        "repeats": args.repeats, "model": args.model or "cli-default",
        "router": bl.claude_router_identity(), "baseline_tag": bl.STABLE_TAG,
        "rejected_inputs": ["ground-truth.yaml", "rubric.yaml", "mock-user.md", "tasks.yaml"],
    })

    if args.carry_over_control:
        source = pathlib.Path(args.carry_over_control)
        carried = []
        for case_id in cases:
            for src in sorted((source / case_id).glob("*")):
                variant_name = src.name
                if not src.is_dir() or variant_name in variants:
                    continue
                if (matrix_dir / case_id / variant_name).exists():
                    continue
                shutil.copytree(src, matrix_dir / case_id / variant_name)
                carried.append(f"{case_id}/{variant_name}")
        bl.write_json(matrix_dir / "control-carryover.json",
                      {"source_matrix": source.name, "carried": carried,
                       "reason": "control run reused; same case, prompt, model and harness protocol"})
        bl.eprint(f"[matrix] carried over control runs: {carried}")

    if args.report_only:
        results = [bl.read_json(p) for p in sorted(matrix_dir.rglob("run-result.json"))]
    elif args.rejudge:
        results = _rejudge_existing(cases, variants, args.repeats, matrix_dir, args)
    else:
        results = _run_sessions(cases, variants, args.repeats, matrix_dir, args)

    if args.pairwise:
        _pairwise(cases, matrix_dir, args.model, run_id)
    if args.frontend_reproduction:
        for case_id in cases:
            for variant in ("candidate_skill", "stable_skill"):
                for run_dir in sorted(matrix_dir.glob(f"{case_id}/{variant}/run*")):
                    if (run_dir / "run-result.json").is_file():
                        run_frontend_reproduction.reproduce(
                            case_id, run_dir, model=args.model, max_turns=args.max_turns or 20,
                            timeout_s=args.timeout or 900, budget_usd=args.budget_usd,
                            do_task_trace=args.task_trace, max_task_steps=args.max_task_steps)

    report = aggregate_report.build(matrix_dir, args.suite, run_id)
    bl.write_json(matrix_dir / "benchmark-report.json", report)
    path = bl.REPORTS_DIR / f"{run_id}-{args.suite}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(aggregate_report.render_markdown(report), encoding="utf-8")
    bl.write_json(bl.REPORTS_DIR / f"{run_id}-{args.suite}.json", report)
    print(json.dumps({"run_id": run_id, "status": report["status"], "report": str(path),
                      "hard_gates": report["hard_gates"], "per_variant": report["per_variant"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Aggregate run results, pairwise judgements and regression checks into one report."""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "judges"))
import bench_lib as bl  # noqa: E402
import regression_judge  # noqa: E402


def _mean(values):
    clean = [v for v in values if isinstance(v, (int, float))]
    return round(statistics.fmean(clean), 3) if clean else None


def _trips_hard_gate(run: dict) -> bool:
    """Whether this run tripped one of the absolute gates, whichever arm it is."""
    return bool((run.get("semantic") or {}).get("hard_gate") == "fail"
                or (run.get("runtime") or {}).get("authority_escape")
                or (run.get("task") or {}).get("critical_task_break")
                or _critical_accessibility_violation(run))


def _critical_accessibility_violation(run: dict) -> bool:
    """A critical accessibility failure, from whichever evidence the run actually stored.

    Contrast failure is the direct signal; a failed touch-target outcome is the same class
    of violation and counts too. Absent evidence is not a violation — it stays unverified.
    """
    checks = (run.get("runtime") or {}).get("checks") or []
    if any(c.get("id") == "contrast_primary_text" and c.get("status") == "fail" for c in checks):
        return True
    for task in ((run.get("task") or {}).get("tasks") or []):
        if any(o.get("id") == "touch_targets" and o.get("status") == "fail"
               for o in (task.get("required_outcomes") or [])):
            return True
    return False


def _provenance(runs: list) -> dict:
    """Disclose what actually ran: recorded source identity, or an explicit absence.

    Legacy runs predate provenance. Saying so is the honest record; back-filling them with
    the current revision would claim those bytes ran when they did not.
    """
    recorded = [r for r in runs if r.get("provenance")]
    missing = [f"{r.get('case_id')}/{r.get('variant')}" for r in runs if not r.get("provenance")]
    identities = {r["provenance"].get("aggregate_sha256") for r in recorded}
    return {
        "runs_with_provenance": len(recorded),
        "runs_missing_provenance": len(missing),
        "missing": sorted(missing),
        "identical_across_runs": len(identities) == 1 and None not in identities,
        # `source_identity` nests the skill tree one level down: the top-level
        # aggregate is populated from `candidate.aggregate_sha256`, which
        # `source_identity` leaves None (`bench_lib.source_identity`). Reading the
        # top level therefore yields an empty set for every matrix and reports
        # `source_identity: []` while real hashes sit one level deeper.
        "source_identity": sorted({sha for r in recorded
                                   for sha in [(r["provenance"].get("candidate") or {}).get("aggregate_sha256"),
                                               ((r["provenance"].get("candidate") or {}).get("skill") or {})
                                               .get("aggregate_sha256")] if sha} ),
        "disclosure": ("no run recorded source identity; provenance unknown for this matrix"
                       if not recorded else
                       (f"{len(missing)} of {len(runs)} runs recorded no provenance"
                        if missing else
                        f"all {len(runs)} runs recorded provenance")),
    }


def build(matrix_dir: pathlib.Path, suite: str, run_id: str) -> dict:
    runs = [bl.read_json(path) for path in sorted(matrix_dir.rglob("run-result.json"))]
    pairwise_files = sorted(matrix_dir.glob("pairwise/*/result.json"))
    pairwise = [bl.read_json(path) for path in pairwise_files]
    frontend_files = sorted(matrix_dir.glob("**/frontend-reproduction/*/result.json"))
    frontend = [bl.read_json(path) for path in frontend_files]
    regression = regression_judge.judge(runs)

    variants = sorted({r.get("variant") for r in runs if r.get("variant")})
    per_variant = {}
    for variant in variants:
        subset = [r for r in runs if r.get("variant") == variant]
        per_variant[variant] = {
            "runs": len(subset),
            "completed": sum(1 for r in subset if r.get("status") in ("PASS", "FAIL")),
            "blocked": sum(1 for r in subset if r.get("status") == "BLOCKED"),
            "task_success_rate": _mean([(r.get("task") or {}).get("success_rate") for r in subset]),
            "method_recall": _mean([((r.get("runtime") or {}).get("method_routing") or {}).get("recall") for r in subset]),
            "method_precision": _mean([((r.get("runtime") or {}).get("method_routing") or {}).get("precision") for r in subset]),
            "semantic_gate_pass": sum(1 for r in subset if (r.get("semantic") or {}).get("hard_gate") == "pass"),
            "semantic_gate_fail": sum(1 for r in subset if (r.get("semantic") or {}).get("hard_gate") == "fail"),
            "semantic_gate_unverified": sum(1 for r in subset if (r.get("semantic") or {}).get("hard_gate") == "unverified"),
            "semantic_signals": sum(len((r.get("semantic") or {}).get("deterministic_hits") or []) for r in subset),
            "artifact_turns": _mean([(r.get("metrics") or {}).get("turns") for r in subset]),
            "cost_usd": round(sum((r.get("metrics") or {}).get("cost_usd") or 0 for r in subset), 4),
            "elapsed_seconds": round(sum((r.get("metrics") or {}).get("elapsed_seconds") or 0 for r in subset), 1),
            "inline_hex_failures": sum(1 for r in subset
                                       if any(c["id"] == "token_inheritance" and c["status"] == "fail"
                                              for c in ((r.get("runtime") or {}).get("checks") or []))),
        }

    hard_gates = {
        "semantic_fabrication": sum(1 for r in runs if (r.get("semantic") or {}).get("hard_gate") == "fail"),
        "authority_escape": sum(1 for r in runs if (r.get("runtime") or {}).get("authority_escape")),
        "critical_task_break": sum(1 for r in runs if (r.get("task") or {}).get("critical_task_break")),
        "critical_accessibility_violation": sum(1 for r in runs if _critical_accessibility_violation(r)),
    }

    judged_pairs = [p for p in pairwise if p.get("status") == "judged" and p.get("result")]
    preference = {"alpha_wins": 0, "beta_wins": 0, "tie": 0}
    for pair in judged_pairs:
        key = {"alpha": "alpha_wins", "beta": "beta_wins", "tie": "tie"}.get(pair["result"].get("overall_preference"))
        if key:
            preference[key] += 1

    unverified = []
    for run in runs:
        if run.get("status") == "BLOCKED":
            unverified.append(f"{run.get('case_id')}/{run.get('variant')}: session blocked")
        if not run.get("task"):
            unverified.append(f"{run.get('case_id')}/{run.get('variant')}: task behaviour unverified")
        if (run.get("semantic") or {}).get("hard_gate") == "unverified":
            unverified.append(f"{run.get('case_id')}/{run.get('variant')}: semantic judge unverified")

    # Which arm tripped a hard gate, so the top-level status can say what it is
    # about. A gate on the *control* arm is a broken control, not a candidate
    # regression: it makes the run unusable as evidence, which is a different
    # verdict from "the candidate regressed against stable". Reporting one
    # headline for both is what let a report read REGRESSION at the top and
    # `Regression vs stable — PASS` in the body with nothing reconciling them.
    gate_arms = sorted({r.get("variant") for r in runs
                        if _trips_hard_gate(r)})
    gate_triggered = bool(gate_arms)
    gate_is_candidate = "candidate_skill" in gate_arms

    if not runs:
        status = "BLOCKED"
    elif gate_triggered:
        status = "REGRESSION" if gate_is_candidate else "INVALID_CONTROL"
    elif regression["verdict"] == "REGRESSION":
        status = "REGRESSION"
    elif all(r.get("status") == "BLOCKED" for r in runs):
        status = "BLOCKED"
    elif regression["verdict"] == "INCONCLUSIVE":
        status = "INCONCLUSIVE"
    else:
        status = "PASS"

    # The two judgements are independent by construction — a hard gate is
    # absolute, a regression verdict is paired against the control — so they may
    # legitimately disagree. Disclose the disagreement and its reason rather than
    # leaving a reader to find it; a silent mismatch reads as a broken report.
    hard_gate_verdicts = {"REGRESSION", "INVALID_CONTROL"}
    status_divergence = None
    if status in hard_gate_verdicts and regression["verdict"] != "REGRESSION":
        status_divergence = (
            f"hard gate tripped on {', '.join(gate_arms)} while the paired verdict is "
            f"{regression['verdict']}: the gate is absolute and fires on the artifacts "
            "themselves, while the paired verdict only compares the candidate against the "
            "control, so both stand.")
    elif status == "PASS" and regression["verdict"] == "REGRESSION":
        status_divergence = ("no hard gate tripped but the paired verdict regressed; "
                             "the paired comparison is the more specific claim.")

    return {
        "run_id": run_id,
        "suite": suite,
        "generated_at": bl.now_stamp(),
        "status": status,
        "status_divergence": status_divergence,
        "hard_gate_arms": gate_arms,
        "cases": sorted({r.get("case_id") for r in runs}),
        "variants": variants,
        "runs": [{k: r.get(k) for k in ("case_id", "variant", "repeat", "status", "metrics", "notes",
                                        "session_fidelity")} for r in runs],
        "hard_gates": hard_gates,
        "per_variant": per_variant,
        "provenance": _provenance(runs),
        "metrics": {
            "pairwise_preference": preference,
            "pairwise_pairs": len(judged_pairs),
            "pairwise_unverified": len([p for p in pairwise if p.get("status") != "judged"]),
            "design_reinterpretation_rate": _mean(
                [(f.get("contract") or {}).get("reinterpretation_rate") for f in frontend]),
            "frontend_contract_gaps": sum(len((f.get("contract") or {}).get("contract_gaps") or []) for f in frontend),
        },
        "regression": regression,
        "pairwise": pairwise,
        "frontend": frontend,
        "unverified": sorted(set(unverified)),
    }


def render_markdown(report: dict) -> str:
    lines = [f"# Benchmark report — {report['suite']} ({report['run_id']})", "",
             f"Status: **{report['status']}**", ""]
    if report.get("hard_gate_arms"):
        lines += [f"Hard gates tripped on: `{', '.join(report['hard_gate_arms'])}`", ""]
    if report.get("status_divergence"):
        lines += [f"Status note: {report['status_divergence']}", ""]
    lines += ["## Hard gates", ""]
    for name, value in report["hard_gates"].items():
        lines.append(f"- `{name}`: {value}")
    provenance = report.get("provenance") or {}
    if provenance:
        lines += ["", "## Candidate provenance", "",
                  f"- runs with recorded provenance: {provenance.get('runs_with_provenance')}",
                  f"- runs missing provenance: {provenance.get('runs_missing_provenance')}",
                  f"- {provenance.get('disclosure')}", ""]
        if provenance.get("missing"):
            lines.append(f"- missing: {', '.join(provenance['missing'])}")
        lines.append(f"- source identity (sha256 of candidate Skill/agent files): "
                     f"{', '.join(provenance.get('source_identity') or []) or 'unknown'}")
    lines += ["", "## Per variant", "",
              "| variant | runs | completed | blocked | task success | method recall | semantic pass/fail/unverified | turns | cost USD |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for variant, data in report["per_variant"].items():
        lines.append(
            f"| {variant} | {data['runs']} | {data['completed']} | {data['blocked']} | "
            f"{data['task_success_rate']} | {data['method_recall']} | "
            f"{data['semantic_gate_pass']}/{data['semantic_gate_fail']}/{data['semantic_gate_unverified']} | "
            f"{data['artifact_turns']} | {data['cost_usd']} |")
    lines += ["", "## Pairwise (blind)", "",
              json.dumps(report["metrics"]["pairwise_preference"], ensure_ascii=False), ""]
    for pair in report.get("pairwise") or []:
        blind = {}
        blind_path = pair.get("blind_manifest_path")
        if blind_path and pathlib.Path(blind_path).is_file():
            blind = json.loads(pathlib.Path(blind_path).read_text(encoding="utf-8"))
        result = pair.get("result") or {}
        if pair.get("status") != "judged":
            lines.append(f"- {pair.get('case_id')} {pair.get('pair')}: unverified ({pair.get('note', '')})")
            continue
        winner = {"alpha": blind.get("alpha_variant"), "beta": blind.get("beta_variant"),
                  "tie": "tie"}.get(result.get("overall_preference"))
        lines.append(f"- {pair.get('case_id')} {pair.get('pair')}: {winner} "
                     f"(confidence {result.get('confidence')}, blind alpha={blind.get('alpha_variant')})")
    lines += ["", "## Frontend reproduction", ""]
    if report.get("frontend"):
        for item in report["frontend"]:
            contract = item.get("contract") or {}
            task = item.get("task") or {}
            lines.append(f"- {item.get('case_id')}: {item.get('status')} | token coverage "
                         f"{contract.get('token_coverage')} | reinterpretation rate "
                         f"{contract.get('reinterpretation_rate')} | contract gaps "
                         f"{len(contract.get('contract_gaps') or [])} | task completability "
                         f"{task.get('status')}")
            lines.append(f"  (rate is an estimate: {contract.get('reinterpretation_rate_note')})")
    else:
        lines.append("- not run for this matrix")
    lines += ["## Regression vs stable", "", f"verdict: **{report['regression']['verdict']}**", ""]
    for item in report["regression"]["regressions"]:
        lines.append(f"- regression: {item['case_id']} r{item['repeat']} {item['dimension']} "
                     f"stable={item['stable']} candidate={item['candidate']}")
    lines += ["", "## Unverified (not counted as pass)", ""]
    lines += [f"- {item}" for item in report["unverified"]] or ["- (none)"]
    lines += ["", "## Runs", "",
              "| case | variant | repeat | status | cost USD | turns |", "| --- | --- | --- | --- | --- | --- |"]
    total_cost = 0.0
    for run in report["runs"]:
        metrics = run.get("metrics") or {}
        total_cost += metrics.get("cost_usd") or 0
        lines.append(f"| {run['case_id']} | {run['variant']} | {run.get('repeat')} | {run['status']} | "
                     f"{metrics.get('cost_usd')} | {metrics.get('turns')} |")
    lines += ["", f"Session cost captured across runs: **${round(total_cost, 2)}** "
                  "(excludes judge calls and frontend reproduction)."]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix-dir", required=True)
    parser.add_argument("--suite", default="custom")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--out-dir", default=str(bl.REPORTS_DIR))
    args = parser.parse_args()
    matrix_dir = pathlib.Path(args.matrix_dir)
    run_id = args.run_id or matrix_dir.name
    report = build(matrix_dir, args.suite, run_id)
    out_dir = pathlib.Path(args.out_dir)
    bl.write_json(matrix_dir / "benchmark-report.json", report)
    markdown_path = out_dir / f"{run_id}-{args.suite}.md"
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    bl.write_json(out_dir / f"{run_id}-{args.suite}.json", report)
    print(f"REPORT {report['status']} -> {markdown_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

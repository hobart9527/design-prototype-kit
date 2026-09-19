#!/usr/bin/env python3
"""Case orchestrator.

State machine, one case/variant/repeat per invocation:
  PREPARE -> GENERATE -> COLLECT -> VERIFY -> CRITIQUE -> [TASK] -> RESULT
Any blocked stage produces BLOCKED with the reason attached; the runner never
repairs the artifact, never adds missing product information, and never turns an
unmeasured dimension into a pass.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(bl_dir := (pathlib.Path(__file__).resolve().parents[1] / "judges")))
import bench_lib as bl  # noqa: E402
import collect_artifacts  # noqa: E402
import run_claude_session  # noqa: E402
import run_task_trace  # noqa: E402
import runtime_judge  # noqa: E402
import semantic_judge  # noqa: E402
import task_judge  # noqa: E402
import visual_manifest  # noqa: E402


def _capture_session_fidelity(session: dict, workspace: pathlib.Path) -> dict:
    """Record what the session actually was, so runs stay comparable."""
    identity = bl.claude_router_identity()
    return {
        "variant": session.get("variant"),
        "model": session.get("model"),
        "router_host": identity["router_host"],
        "session_id": session.get("session_id"),
        "workspace": str(workspace),
        "skill_manifest": None,
        "prompt_protocol": "benchmarks/prompts/protocol.txt",
    }


def run_one(case_id: str, variant: str, repeat: int, matrix_dir: pathlib.Path, *, model: str | None,
            max_turns: int | None, timeout_s: int | None, budget_usd: float | None,
            do_task_trace: bool, max_task_steps: int, do_visual: bool,
            session_budget_usd: float | None = None, rejudge: bool = False,
            auto_open: bool = False) -> dict:
    case = bl.load_case(case_id)
    policy = case["meta"].get("run_policy", {})
    out_dir = matrix_dir / case_id / variant / f"run{repeat}"
    out_dir.mkdir(parents=True, exist_ok=True)
    previous = sorted(out_dir.glob("run-result*.json"))
    archived = []
    for index, old in enumerate(previous):
        archived_path = out_dir / f"run-result-prev{index + 1}.json"
        old.rename(archived_path)
        archived.append(archived_path)
    result = {
        "layer": "case",
        "case_id": case_id,
        "variant": variant,
        "repeat": repeat,
        "status": "INCONCLUSIVE",
        "metrics": {},
        "runtime": None, "semantic": None, "task": None, "visual": None, "contract": None,
        "notes": [], "artifacts": None,
    }

    if rejudge:
        # Judge-only pass over the artifacts already collected for this run.
        manifest = bl.read_json(out_dir / "artifacts-manifest.json") if (out_dir / "artifacts-manifest.json").is_file() else None
        if manifest is None and (out_dir / "artifacts" / "prototype").is_dir():
            manifest = {
                "case_id": case_id,
                "variant": variant,
                "workspace": None,
                "artifacts_dir": str(out_dir / "artifacts"),
                "entry": bl.find_entry(out_dir / "artifacts" / "prototype"),
                "hashes": {},
                "counts": {"prototype_files": sum(1 for p in (out_dir / "artifacts" / "prototype").rglob("*") if p.is_file())},
                "reconstructed": True,
            }
        if manifest is None:
            result["status"] = "BLOCKED"
            result["notes"].append("rejudge requested but no collected artifacts exist for this run")
            bl.write_json(out_dir / "run-result.json", result)
            return result
        result["artifacts"] = manifest
        result["session"] = bl.read_json(out_dir / "session-summary.json") if (out_dir / "session-summary.json").is_file() else None
        result["metrics"] = (result["session"] or {}).get("metrics") or {}
        result["session_fidelity"] = (result["session"] or {}).get("session_fidelity")
        if not result["metrics"] and archived:
            # Preserve the original session evidence when re-judging older runs
            # that predate session-summary.json.
            prior = bl.read_json(archived[-1])
            result["session"] = prior.get("session")
            result["metrics"] = prior.get("metrics") or {}
            result["session_fidelity"] = prior.get("session_fidelity")
        result["notes"].append("rejudged from stored artifacts (no new session)")
        artifacts_dir = pathlib.Path(manifest["artifacts_dir"]) / "prototype"
    else:
        # PREPARE + GENERATE
        run_id = f"{bl.now_stamp()}-r{repeat}"
        try:
            workspace = bl.prepare_workspace(case, variant, run_id)
            session = run_claude_session.run_session(
                case, variant, workspace, model=model,
                max_turns=max_turns or policy.get("max_turns", 20),
                timeout_s=timeout_s or policy.get("timeout_seconds", 900),
                budget_usd=budget_usd if budget_usd is not None else policy.get("max_budget_usd_per_turn"),
                session_budget_usd=session_budget_usd,
            )
        except bl.BenchBlocked as exc:
            result["status"] = "BLOCKED"
            result["notes"].append(f"prepare: {exc}")
            bl.write_json(out_dir / "run-result.json", result)
            return result

        result["session"] = {k: session[k] for k in
                             ("status", "model", "session_id", "metrics", "events_fired", "note", "components")}
        result["metrics"] = session["metrics"]
        result["session_fidelity"] = _capture_session_fidelity(session, workspace)
        if session["status"] != "COMPLETED":
            result["status"] = "BLOCKED"
            result["notes"].append(f"session {session['status']}: {session.get('note')}")

        # COLLECT
        manifest = collect_artifacts.collect(workspace, out_dir, case_id, variant)
        bl.write_json(out_dir / "artifacts-manifest.json", manifest)
        bl.write_json(out_dir / "session-summary.json", result["session"] | {"session_fidelity": result["session_fidelity"]})
        result["artifacts"] = manifest
        artifacts_dir = pathlib.Path(manifest["artifacts_dir"]) / "prototype"

    # VERIFY (runtime mechanics) + CRITIQUE (semantic fidelity)
    try:
        result["runtime"] = runtime_judge.judge(case, artifacts_dir, variant=variant)
    except Exception as exc:  # judge defects must surface, not be swallowed
        result["notes"].append(f"runtime judge error: {exc}")
    evaluation = case["meta"].get("evaluation") or {}
    if evaluation.get("semantic", True):
        try:
            revealed = semantic_judge.extract_revealed_facts(out_dir / "session-transcript.md")
            result["semantic"] = semantic_judge.judge(case, artifacts_dir, out_dir, model=model,
                                                      revealed_facts=revealed)
        except Exception as exc:
            result["notes"].append(f"semantic judge error: {exc}")

    # TASK TRACE
    if do_task_trace and evaluation.get("task_trace", False):
        try:
            traces = []
            for task in (case["tasks"].get("tasks") or []):
                traces.append(run_task_trace.run_task(case, task, artifacts_dir, out_dir,
                                                      model=model, max_steps=max_task_steps, timeout_s=180))
            bl.write_json(out_dir / "task-traces.json", {"case_id": case_id, "traces": traces})
            result["task"] = task_judge.judge(case, traces)
        except Exception:
            result["notes"].append("task trace error: " + traceback.format_exc(limit=2))

    # VISUAL EVIDENCE
    if do_visual or evaluation.get("visual_pairwise", False):
        try:
            viewports = (case["meta"].get("viewports") or {}).get("required") or [1280]
            result["visual"] = visual_manifest.capture(artifacts_dir, viewports, out_dir)
            bl.write_json(out_dir / "visual-manifest.json", result["visual"])
        except Exception as exc:
            result["notes"].append(f"visual capture error: {exc}")

    # RESULT
    hard_fail = False
    if result["semantic"] and result["semantic"].get("hard_gate") == "fail":
        hard_fail = True
    if result["runtime"] and result["runtime"].get("status") == "fail":
        hard_fail = True
    if result["task"] and result["task"].get("critical_task_break"):
        hard_fail = True
    if result["status"] != "BLOCKED":
        result["status"] = "FAIL" if hard_fail else "PASS"
    if result["status"] == "PASS":
        unverified = []
        if not result["task"]:
            unverified.append("task_behavior")
        if not result["semantic"] or result["semantic"].get("hard_gate") == "unverified":
            unverified.append("semantic_fidelity")
        if unverified:
            result["notes"].append("unverified dimensions: " + ", ".join(unverified))
        if (not result["runtime"] or not result["runtime"]["checks"]):
            result["status"] = "INCONCLUSIVE"

    bl.write_json(out_dir / "run-result.json", result)
    if auto_open:
        portal = artifacts_dir / "review-portal.html"
        target = portal if portal.is_file() else (artifacts_dir / (manifest.get("entry") or "index.html"))
        if target.is_file():
            import subprocess, platform
            cmd = ["open", str(target)] if platform.system() == "Darwin" else ["xdg-open", str(target)]
            try:
                subprocess.run(cmd, check=False)
                bl.eprint(f"[browser] opened {target}")
            except Exception as e:
                bl.eprint(f"[browser] could not open {target}: {e}")
    bl.eprint(f"[case] {case_id}/{variant}/r{repeat} -> {result['status']}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one benchmark case for one variant")
    parser.add_argument("--case", required=True)
    parser.add_argument("--variant", required=True, choices=list(bl.VARIANTS))
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--matrix-dir", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=None)
    parser.add_argument("--budget-usd", type=float, default=None)
    parser.add_argument("--task-trace", action="store_true")
    parser.add_argument("--visual", action="store_true")
    parser.add_argument("--max-task-steps", type=int, default=6)
    parser.add_argument("--session-budget-usd", type=float, default=None)
    parser.add_argument("--rejudge", action="store_true",
                        help="re-run judges over already collected artifacts (no new session)")
    parser.add_argument("--open", action="store_true",
                        help="automatically open the review portal / prototype in browser upon completion")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    result = run_one(args.case, args.variant, args.repeat, pathlib.Path(args.matrix_dir), model=args.model,
                     max_turns=args.max_turns, timeout_s=args.timeout, budget_usd=args.budget_usd,
                     do_task_trace=args.task_trace, max_task_steps=args.max_task_steps, do_visual=args.visual,
                     session_budget_usd=args.session_budget_usd, rejudge=args.rejudge,
                     auto_open=args.open)
    if args.out:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] in ("PASS",) else (2 if result["status"] == "BLOCKED" else 1)


if __name__ == "__main__":
    sys.exit(main())

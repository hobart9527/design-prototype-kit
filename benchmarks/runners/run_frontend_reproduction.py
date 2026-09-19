#!/usr/bin/env python3
"""Independent frontend reproduction: can the frozen contract be implemented
without the original prototype source?

The implementation agent's workspace is built from contract documents only.
The design HTML/CSS is never copied in, so it cannot be read.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "judges"))
import bench_lib as bl  # noqa: E402
import contract_judge  # noqa: E402
import run_task_trace  # noqa: E402
import task_judge  # noqa: E402

CONTRACT_DIRS = ("specifications", "contracts", "evidence")


def _stage_contract(design_artifacts: pathlib.Path, workspace: pathlib.Path) -> list:
    contract_dir = workspace / "contract"
    contract_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in CONTRACT_DIRS:
        src = design_artifacts / name
        if not src.is_dir():
            continue
        for path in sorted(src.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in (".md", ".json", ".yaml", ".txt"):
                continue
            dest = contract_dir / path.relative_to(design_artifacts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            copied.append(str(dest.relative_to(workspace)))
    tokens = design_artifacts / "shared" / "tokens.css"
    if tokens.is_file():
        dest = contract_dir / "shared" / "tokens.css"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tokens, dest)
        copied.append(str(dest.relative_to(workspace)))
    return copied


def reproduce(case_id: str, design_run_dir: pathlib.Path, *, model: str | None, max_turns: int,
              timeout_s: int, budget_usd: float | None, do_task_trace: bool, max_task_steps: int) -> dict:
    case = bl.load_case(case_id)
    design_artifacts = design_run_dir / "artifacts" / "prototype"
    out_dir = design_run_dir.parent / "frontend-reproduction" / f"{case_id}-{design_run_dir.name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    workspace = out_dir / "workspace"
    if workspace.exists():
        bl.eprint(f"[frontend] workspace exists, refusing to reuse: {workspace}")
        return {"status": "BLOCKED", "note": "workspace exists"}
    workspace.mkdir(parents=True)

    copied = _stage_contract(design_artifacts, workspace)
    result = {"layer": "frontend_reproduction", "case_id": case_id, "design_run_dir": str(design_run_dir),
              "workspace": str(workspace), "contract_paths": copied, "status": "BLOCKED", "notes": []}
    if not copied:
        result["notes"].append("design run produced no contract documents to implement from")
        bl.write_json(out_dir / "result.json", result)
        return result

    prompt = bl.render(bl.prompt_template("frontend-implementation.txt"),
                       contract_paths=", ".join(copied[:20]))
    session = bl.run_claude(prompt, workspace, model=model, max_turns=max_turns, timeout_s=timeout_s,
                            max_budget_usd=budget_usd)
    result["session"] = {"status": session["status"], "session_id": session.get("session_id"),
                         "metrics": {"elapsed_s": session.get("elapsed_s"), "cost_usd": session.get("cost_usd")},
                         "models": session.get("models")}
    impl_dir = workspace / "impl"
    collected = out_dir / "impl"
    if impl_dir.is_dir():
        shutil.copytree(impl_dir, collected, dirs_exist_ok=True)
    target = impl_dir if impl_dir.is_dir() else collected

    task_result = None
    if do_task_trace and impl_dir.is_dir():
        traces = [run_task_trace.run_task(case, task, impl_dir, out_dir, model=model,
                                          max_steps=max_task_steps, timeout_s=180)
                  for task in (case["tasks"].get("tasks") or [])]
        bl.write_json(out_dir / "task-traces.json", {"case_id": case_id, "traces": traces})
        task_result = task_judge.judge(case, traces)
        result["task"] = task_result

    result["contract"] = contract_judge.judge(case_id, design_artifacts, target, task_result=task_result)
    result["status"] = "PASS" if result["contract"]["status"] == "pass" else "FAIL"
    bl.write_json(out_dir / "result.json", result)
    bl.eprint(f"[frontend] {case_id} -> {result['status']} gaps={len(result['contract']['contract_gaps'])}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--design-run-dir", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--budget-usd", type=float, default=None)
    parser.add_argument("--task-trace", action="store_true")
    parser.add_argument("--max-task-steps", type=int, default=6)
    args = parser.parse_args()
    result = reproduce(args.case, pathlib.Path(args.design_run_dir), model=args.model, max_turns=args.max_turns,
                       timeout_s=args.timeout, budget_usd=args.budget_usd, do_task_trace=args.task_trace,
                       max_task_steps=args.max_task_steps)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

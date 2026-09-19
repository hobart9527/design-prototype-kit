#!/usr/bin/env python3
"""Task judge: turn recorded task traces into outcome verdicts.

Outcome checks read the DOM evidence the runner captured. A missing trace is
reported as unverified, never as success (BENCH-004).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402


def _merged_text(trace: dict) -> str:
    return "\n".join(snapshot.get("text") or "" for snapshot in trace.get("snapshots") or [])


def evaluate_outcome(outcome: dict, trace: dict) -> dict:
    check = outcome.get("check")
    snapshots = trace.get("snapshots") or []
    last = snapshots[-1] if snapshots else {}
    text = _merged_text(trace)
    pattern = outcome.get("pattern") or ""
    verdict, detail = "unverified", ""
    if check == "text_present":
        hit = re.search(pattern, text)
        verdict, detail = ("pass" if hit else "fail"), (hit.group(0)[:80] if hit else f"pattern not found: {pattern}")
    elif check == "text_absent":
        hit = re.search(pattern, text)
        verdict, detail = ("pass" if not hit else "fail"), (hit.group(0)[:80] if hit else "absent as required")
    elif check == "dialog_open":
        opened = [s for s in snapshots if (s.get("dialogs") or 0) > 0]
        verdict = "pass" if opened else "fail"
        detail = f"dialogs observed in {len(opened)}/{len(snapshots)} snapshots"
    elif check == "no_horizontal_scroll":
        if last:
            verdict = "pass" if not last.get("horizontal_scroll") else "fail"
            detail = f"scrollWidth={last.get('scrollWidth')} clientWidth={last.get('clientWidth')}"
    elif check == "min_touch_target":
        if last:
            small = last.get("small_target_count")
            verdict = "pass" if small == 0 else "fail"
            detail = f"{small} control(s) below {outcome.get('px', 44)}px"
    elif check == "element_count_min":
        count = len(last.get("controls") or [])
        verdict = "pass" if count >= int(outcome.get("count") or 1) else "fail"
        detail = f"{count} interactive controls visible"
    elif check == "state_changed":
        texts = {(s.get("text") or "")[:400] for s in snapshots}
        verdict = "pass" if len(texts) > 1 else "fail"
        detail = f"{len(texts)} distinct DOM states observed"
    return {"id": outcome.get("id"), "check": check, "status": verdict, "detail": detail}


def judge_task(task: dict, trace: dict) -> dict:
    required = [evaluate_outcome(o, trace) for o in task.get("required_outcomes") or []]
    forbidden = []
    for outcome in task.get("forbidden_outcomes") or []:
        text = _merged_text(trace)
        hit = re.search(outcome.get("pattern") or "", text)
        forbidden.append({"id": outcome.get("id"), "status": "violated" if hit else "ok",
                          "detail": (hit.group(0)[:80] if hit else "absent")})
    trace_status = trace.get("status")
    unmet = [r["id"] for r in required if r["status"] != "pass"]
    if trace_status == "blocked":
        status = "unverified"
    elif forbidden and any(f["status"] == "violated" for f in forbidden):
        status = "fail"
    elif unmet:
        status = "fail"
    else:
        status = "pass"
    return {"task_id": task.get("id"), "critical": task.get("critical", True), "status": status,
            "trace_status": trace_status, "required_outcomes": required, "forbidden_outcomes": forbidden,
            "unmet": unmet, "steps": len(trace.get("steps") or [])}


def judge(case: dict, traces: list) -> dict:
    by_id = {t.get("task_id"): t for t in traces}
    results = []
    for task in (case["tasks"].get("tasks") or []):
        trace = by_id.get(task["id"])
        if trace is None:
            results.append({"task_id": task["id"], "critical": task.get("critical", True), "status": "unverified",
                            "trace_status": "missing", "required_outcomes": [], "unmet": ["no_trace"],
                            "steps": 0})
        else:
            results.append(judge_task(task, trace))
    critical_fails = [r["task_id"] for r in results if r["critical"] and r["status"] == "fail"]
    unverified = [r["task_id"] for r in results if r["status"] == "unverified"]
    verified = [r for r in results if r["status"] in ("pass", "fail")]
    return {
        "judge": "task",
        "tasks": results,
        "critical_task_break": len(critical_fails),
        "critical_failures": critical_fails,
        "unverified": unverified,
        "success_rate": round(sum(1 for r in verified if r["status"] == "pass") / len(verified), 3) if verified else None,
        "status": "fail" if critical_fails else ("unverified" if unverified else "pass"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--traces", required=True, help="task trace JSON produced by run_task_trace.py")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    case = bl.load_case(args.case)
    payload = bl.read_json(pathlib.Path(args.traces))
    traces = payload.get("traces") if isinstance(payload, dict) else payload
    result = judge(case, traces or [])
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Run one real, isolated Claude Code session against one case and one variant.

This is a *runner*: it delivers the brief, answers the agent's clarifying
questions from the case's hidden mock-user rules, injects counterfactual events,
and records every turn. It never supplies product information, never names a
method, and never tells the agent what it missed (benchmark contamination).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_lib as bl  # noqa: E402


def run_session(case: dict, variant: str, workspace: Path, *, model: str | None, max_turns: int,
                timeout_s: int, budget_usd: float | None, turns_per_call: int = 60,
                session_budget_usd: float | None = None) -> dict:
    protocol = bl.prompt_template("protocol.txt").strip()
    template = bl.prompt_template("skill-run.txt" if variant != "no_skill" else "no-skill.txt")
    prompt = bl.render(template, brief=case["brief"], protocol=protocol)
    mock = bl.parse_mock_user(case["mock_user"])
    events = [dict(event, fired=False) for event in case["events"]]

    session_id = bl.new_session_id()
    deadline = time.monotonic() + timeout_s
    turns: list[dict] = []
    transcript: list[dict] = []
    status, note = "INCONCLUSIVE", ""
    total_cost = 0.0
    model_seen: set[str] = set()
    records_path = workspace / "session-records.jsonl"

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 10:
            status, note = "BLOCKED", f"wall-clock timeout after {len(turns)} turns"
            break
        resume = session_id if turns else None
        out = bl.run_claude(prompt, workspace, session_id=session_id, resume=resume, model=model,
                            max_turns=turns_per_call, max_budget_usd=budget_usd,
                            timeout_s=int(min(remaining, timeout_s)))
        session_id = out.get("session_id") or session_id
        total_cost += out.get("cost_usd") or 0.0
        model_seen.update(out.get("models") or [])
        turn = {
            "turn": len(turns) + 1,
            "prompt_chars": len(prompt),
            "prompt_kind": "initial_brief" if not turns else "user_reply",
            "status": out["status"],
            "exit_code": out.get("exit_code"),
            "elapsed_s": out["elapsed_s"],
            "num_turns": out.get("num_turns"),
            "cost_usd": out.get("cost_usd"),
            "usage": out.get("usage"),
            "stderr": (out.get("stderr") or "")[:500],
            "errors": out.get("errors"),
        }
        turns.append(turn)
        transcript.append({"role": "user", "text": prompt})
        transcript.append({"role": "assistant", "text": out["result"]})
        with records_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(turn, ensure_ascii=False) + "\n")

        if out["status"] == "max_turns":
            # The CLI caps agent turns per call. Resume the same session with a
            # neutral continuation so a long design session can finish; the
            # wall-clock, loop-turn and session-budget limits still bound it.
            turn["prompt_kind"] = "auto_continue"
            turns[-1] = turn
            if session_budget_usd and total_cost >= session_budget_usd:
                status, note = "BLOCKED", f"session budget cap reached (${round(total_cost, 2)})"
                break
            prompt = "继续。"
            continue
        if out["status"] == "budget_exceeded":
            # The per-call budget is a guard against one runaway call, not the
            # session cap: continue while the session budget still allows it.
            turn["prompt_kind"] = "auto_continue"
            turns[-1] = turn
            if session_budget_usd and total_cost >= session_budget_usd:
                status, note = "BLOCKED", f"session budget cap reached (${round(total_cost, 2)})"
                break
            if not session_budget_usd:
                status, note = "BLOCKED", "per-call budget exhausted and no session budget set"
                break
            prompt = "继续。"
            continue
        if out["status"] != "completed":
            status, note = "BLOCKED", f"turn {turn['turn']} {out['status']}: {turn['stderr']}"
            break
        if len(turns) >= max_turns:
            status, note = "BLOCKED", f"max_turns={max_turns} reached without a terminal answer"
            break
        if session_budget_usd and total_cost >= session_budget_usd:
            status, note = "BLOCKED", f"session budget cap reached (${round(total_cost, 2)} >= ${session_budget_usd})"
            break

        text = out["result"] or ""
        event = next((e for e in events if not e["fired"]
                      and any(k.lower() in text.lower() for k in e["trigger"])), None)
        if event:
            event["fired"] = True
            prompt = f"（用户补充信息）{event['inject']}"
            continue
        question = bl.extract_user_input(text)
        if question:
            prompt = bl.mock_reply(question, mock["rules"], mock["fallback"])
            continue
        status, note = "COMPLETED", ""
        break

    components = bl.workspace_components(workspace)
    if status == "COMPLETED" and not components["prototype_dir"]:
        status, note = "INCONCLUSIVE", "session ended without any prototype/ artifacts"

    (workspace / "session-transcript.md").write_text(
        "\n\n".join(f"## {item['role']}\n\n{item['text']}" for item in transcript), encoding="utf-8")

    return {
        "layer": "session",
        "case_id": case["id"],
        "variant": variant,
        "status": status,
        "note": note,
        "session_id": session_id,
        "model": ",".join(sorted(model_seen)) or (model or "cli-default"),
        "workspace": str(workspace),
        "metrics": {"turns": len(turns), "elapsed_seconds": round(timeout_s - (deadline - time.monotonic()), 2),
                    "cost_usd": round(total_cost, 4)},
        "events_fired": [e["name"] for e in events if e["fired"]],
        "turns": turns,
        "components": components,
        "artifacts": bl.hash_tree(workspace / "prototype"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one isolated Claude Code session")
    parser.add_argument("--case", required=True)
    parser.add_argument("--variant", required=True, choices=list(bl.VARIANTS))
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-turns", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=None)
    parser.add_argument("--budget-usd", type=float, default=None)
    parser.add_argument("--session-budget-usd", type=float, default=None)
    parser.add_argument("--out", default="-")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()

    try:
        case = bl.load_case(args.case)
    except bl.BenchBlocked as exc:
        bl.write_json(Path(args.out), {"layer": "session", "case_id": args.case, "variant": args.variant,
                                       "status": "BLOCKED", "note": str(exc)})
        return 2

    policy = case["meta"].get("run_policy", {})
    run_id = args.run_id or bl.now_stamp()
    max_turns = args.max_turns or policy.get("max_turns", 20)
    timeout_s = args.timeout or policy.get("timeout_seconds", 1500)
    budget = args.budget_usd if args.budget_usd is not None else policy.get("max_budget_usd_per_turn")

    try:
        workspace = bl.prepare_workspace(case, args.variant, run_id)
    except bl.BenchBlocked as exc:
        bl.write_json(Path(args.out), {"layer": "session", "case_id": args.case, "variant": args.variant,
                                       "status": "BLOCKED", "note": str(exc)})
        return 2

    if args.prepare_only:
        result = {"layer": "session", "case_id": args.case, "variant": args.variant,
                  "status": "PREPARED", "workspace": str(workspace)}
    else:
        result = run_session(case, args.variant, workspace, model=args.model, max_turns=max_turns,
                             timeout_s=timeout_s, budget_usd=budget,
                             session_budget_usd=args.session_budget_usd)

    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(Path(args.out), result)
    bl.eprint(f"[session] {case['id']}/{args.variant} -> {result['status']} {result.get('note','')}")
    return 0 if result["status"] in ("COMPLETED", "PREPARED") else 2


if __name__ == "__main__":
    sys.exit(main())

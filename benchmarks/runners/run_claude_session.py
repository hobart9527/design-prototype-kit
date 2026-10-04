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


def _auto_continue_prompt() -> str:
    return ("继续。从 prototype/discussion.md 的 Resume 块的 Next action 继续执行，"
            "不要重新规划已完成的部分。")


def _try_inject(text: str, events: list[dict], mock: dict, also: str = "") -> str | None:
    """Match events and mock-user questions against the assistant's output.

    ``text`` is the call's final answer (the only place a question to the user
    is read). ``also`` is everything else the call produced: its earlier chat
    messages and the files it wrote. A trigger word can land in any of them — a
    lean skill keeps chat sparse and the substance in the design record — so
    events match the whole call, not just its last message.

    A trigger seen once stays seen: one injection goes out per call, so an event
    the agent already provoked waits for a later call instead of being lost
    (r34: all three triggers present in call 1, only one event ever fired).

    Returns the next prompt to send, or ``None`` when no injection matched
    (the caller should fall through to auto_continue or completion).
    """
    haystack = f"{text}\n{also}".lower()
    for e in events:
        if not e["fired"] and any(k.lower() in haystack for k in e["trigger"]):
            e["seen"] = True
    event = next((e for e in events if e.get("seen") and not e["fired"]), None)
    if event:
        event["fired"] = True
        return f"（用户补充信息）{event['inject']}"
    question = bl.extract_user_input(text)
    if question:
        return bl.mock_reply(question, mock["rules"], mock["fallback"])
    return None


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
    blocked_reason = ""
    total_cost = 0.0
    model_seen: set[str] = set()
    records_path = workspace / "session-records.jsonl"

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 10:
            status, note = "BLOCKED", f"wall-clock timeout after {len(turns)} turns"
            break
        resume = session_id if turns else None
        # Mark the transcript before the call so event triggers can read every
        # message this call produced, not just its last (r30 missed two).
        mark = bl.transcript_mark(session_id)
        out = bl.run_claude(prompt, workspace, session_id=session_id, resume=resume, model=model,
                            max_turns=turns_per_call, max_budget_usd=budget_usd,
                            timeout_s=int(min(remaining, timeout_s)))
        session_id = out.get("session_id") or session_id
        # The CLI's total_cost_usd is cumulative across all resumed turns in
        # this session, not this call's incremental spend. Adding it repeatedly
        # compounds prior turns. On normal return, ratchet total_cost to the
        # latest reported cumulative spend. On timeout, the CLI emits no payload;
        # add the per-turn budget to the last known baseline as a conservative
        # upper bound so runaway timeouts cannot bypass total-budget governance.
        call_cost = out.get("cost_usd") or 0.0
        if out.get("cost_estimated"):
            timeout_bound = budget_usd if budget_usd is not None else 8.0
            total_cost = max(total_cost, call_cost) + timeout_bound
        else:
            total_cost = max(total_cost, call_cost)
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
            "iterations": out.get("iterations") or [],
            "stderr": (out.get("stderr") or "")[:500],
            "errors": out.get("errors"),
        }
        turns.append(turn)
        transcript.append({"role": "user", "text": prompt})
        # A turn-capped call has an empty result; fall back to what this call said.
        out_text = out["result"] or bl.assistant_text_since(session_id, mark)
        # Event matching reads the whole call: every chat message plus file writes.
        out_also = (bl.assistant_text_since(session_id, mark) + "\n"
                    + bl.written_text_since(session_id, mark))
        transcript.append({"role": "assistant", "text": out_text})
        with records_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(turn, ensure_ascii=False) + "\n")
        bl.eprint(
            f"[session] {case['id']}/{variant} call={turn['turn']} "
            f"status={turn['status']} elapsed={turn['elapsed_s']}s "
            f"cost=${turn['cost_usd'] or 0:.2f} files={bl.workspace_components(workspace)['file_count']}"
        )

        # ── Budget / turn-limit guards (shared by all exit paths) ──────
        def _budget_blocked() -> bool:
            return bool(session_budget_usd and total_cost >= session_budget_usd)

        if out["status"] == "max_turns":
            errors = out.get("errors") or []
            num_turns = out.get("num_turns") or 0
            is_genuine_turn_cap = (
                num_turns > 1
                and (
                    not errors
                    or all("maximum number of turns" in str(e).lower() for e in errors)
                )
            )
            if not is_genuine_turn_cap and (not out.get("result") and out.get("is_error")):
                status, note = "BLOCKED", f"CLI returned an error envelope: {turn['stderr']}"
                break
            turn["prompt_kind"] = "auto_continue"
            turns[-1] = turn
            if _budget_blocked():
                status, note = "BLOCKED", f"session budget cap reached (${round(total_cost, 2)})"
                blocked_reason = "session_budget"
                break
            # Even on a CLI turn cap, the assistant's output may contain event
            # triggers or user-input requests — check before falling through to
            # a neutral auto_continue.
            injected = _try_inject(out_text, events, mock, out_also)
            prompt = injected or _auto_continue_prompt()
            continue
        if out["status"] == "budget_exceeded":
            turn["prompt_kind"] = "auto_continue"
            turns[-1] = turn
            if _budget_blocked():
                status, note = "BLOCKED", f"session budget cap reached (${round(total_cost, 2)})"
                blocked_reason = "session_budget"
                break
            if not session_budget_usd:
                status, note = "BLOCKED", "per-call budget exhausted and no session budget set"
                blocked_reason = "per_call_budget"
                break
            injected = _try_inject(out_text, events, mock, out_also)
            prompt = injected or _auto_continue_prompt()
            continue
        if out["status"] != "completed":
            status, note = "BLOCKED", f"turn {turn['turn']} {out['status']}: {turn['stderr']}"
            blocked_reason = "wall_clock" if out["status"] == "timeout" else out["status"]
            break
        if len(turns) >= max_turns:
            status, note = "BLOCKED", f"max_turns={max_turns} reached without a terminal answer"
            blocked_reason = "max_turns"
            break
        if _budget_blocked():
            status, note = "BLOCKED", f"session budget cap reached (${round(total_cost, 2)} >= ${session_budget_usd})"
            blocked_reason = "session_budget"
            break

        # ── Completed turn: check for event injection / user questions ──
        injected = _try_inject(out_text, events, mock, out_also)
        if injected:
            prompt = injected
            continue
        # A staged design skill ends each turn cleanly at a stage checkpoint
        # ("Stage 1 sealed; next: dispatch builder"). That is a pause, not a
        # finished delivery: if no runnable prototype exists yet, the session
        # must resume instead of being recorded as complete.
        if not bl.workspace_components(workspace)["has_html"]:
            if len(turns) >= max_turns:
                status, note = "BLOCKED", f"max_turns={max_turns} reached without any runnable prototype"
                blocked_reason = "max_turns"
                break
            if _budget_blocked():
                status, note = "BLOCKED", f"session budget cap reached (${round(total_cost, 2)})"
                blocked_reason = "session_budget"
                break
            turn["prompt_kind"] = "auto_continue"
            turns[-1] = turn
            prompt = _auto_continue_prompt()
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
        "blocked_reason": blocked_reason or None,
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
                             session_budget_usd=args.session_budget_usd,
                             turns_per_call=policy.get("turns_per_call", 60))

    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(Path(args.out), result)
    bl.eprint(f"[session] {case['id']}/{args.variant} -> {result['status']} {result.get('note','')}")
    return 0 if result["status"] in ("COMPLETED", "PREPARED") else 2


if __name__ == "__main__":
    sys.exit(main())

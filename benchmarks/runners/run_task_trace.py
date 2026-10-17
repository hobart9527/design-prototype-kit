#!/usr/bin/env python3
"""Task trace runner: a user-like agent performs tasks on the prototype.

The agent sees only the goal, the currently visible controls and the visible
text. It never sees the design rationale. Every step, observation and DOM
snapshot is recorded so task_judge can audit the outcome.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import queue
import subprocess
import sys
import threading

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bench_lib as bl  # noqa: E402

PROBE = bl.BENCH / "runners" / "browser_probe.mjs"
SNAPSHOT_TEXT_CAP = 8000


class BrowserSession:
    """One live headless page driven over JSON-lines to browser_probe.mjs."""

    def __init__(self, url: str, viewport: int, timeout_s: int = 30):
        self.timeout_s = timeout_s
        self.proc = subprocess.Popen(
            ["node", str(PROBE), "session", "--url", url, "--viewport", f"{viewport}x900"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        self.lines: queue.Queue = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self):
        for line in self.proc.stdout:
            self.lines.put(line)
        self.lines.put(None)

    def send(self, **command) -> dict:
        if self.proc.poll() is not None:
            return {"error": "browser session exited"}
        self.proc.stdin.write(json.dumps(command, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        try:
            line = self.lines.get(timeout=self.timeout_s)
        except queue.Empty:
            return {"error": f"browser command timeout: {command.get('cmd')}"}
        if line is None:
            return {"error": "browser session closed"}
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return {"error": f"unparseable browser output: {line[:200]}"}

    def close(self):
        try:
            self.send(cmd="quit")
        except Exception:
            pass
        try:
            if self.proc.poll() is None:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        except Exception:
            pass


MIN_EVIDENCE_CHARS = 4


def squash(text: str) -> str:
    """Whitespace-insensitive form used to match a quoted phrase against page text."""
    return "".join(str(text or "").split())


def evidence_on_page(evidence: str, page_text: str) -> bool:
    """A `done` is a completion only when it quotes the terminal page verbatim."""
    quoted = squash(evidence)
    return len(quoted) >= MIN_EVIDENCE_CHARS and quoted in squash(page_text)


def _trim(snapshot: dict) -> dict:
    if not snapshot:
        return {}
    trimmed = dict(snapshot)
    trimmed["text"] = (snapshot.get("text") or "")[:SNAPSHOT_TEXT_CAP]
    return trimmed


def run_task(case: dict, task: dict, prototype_dir: pathlib.Path, out_dir: pathlib.Path, *,
             model: str | None, max_steps: int, timeout_s: int) -> dict:
    entry = bl.find_entry(prototype_dir)
    viewport = int((task.get("start") or {}).get("viewport") or 1280)
    trace = {"task_id": task.get("id"), "goal": task.get("goal"), "viewport": viewport,
             "status": "blocked", "steps": [], "snapshots": [], "note": "", "evidence": ""}
    if not entry:
        trace["note"] = "no html entry point in artifacts"
        return trace

    base_url, shutdown = bl.serve_dir(prototype_dir)
    start_state = str((task.get("start") or {}).get("state") or "").strip()
    sep = "&" if "?" in entry else "?"
    if start_state:
        state_key = "conflict" if start_state == "timeslot_conflict" else start_state
        url = f"{base_url}/{entry}{sep}state={state_key}&start_state={start_state}"
    else:
        url = f"{base_url}/{entry}"
    session = BrowserSession(url, viewport)
    try:
        first = session.send(cmd="snapshot")
        if "error" in first:
            trace["note"] = first["error"]
            return trace
        snapshot = first["snapshot"]
        trace["snapshots"].append(_trim(snapshot))
        shot_dir = out_dir / "task-screenshots"
        session.send(cmd="screenshot", file=str(shot_dir / f"{task['id']}-before.png"))

        for step_index in range(max_steps):
            # The action id (data-action) is the authored action contract; exposing
            # it lets the agent pick a deterministic identity instead of guessing
            # among ambiguous visible names.
            controls = [{"index": c["index"], "role": c["role"], "name": c["name"],
                         **({"action": c["actions"]} if c.get("actions") else {})}
                        for c in (snapshot.get("controls") or [])[:60]]
            prompt = bl.render(
                bl.prompt_template("task-agent.txt"),
                goal=task.get("goal", ""),
                controls=json.dumps(controls, ensure_ascii=False),
                text=(snapshot.get("text") or "")[:4000],
                steps=json.dumps([{k: s[k] for k in ("action", "target", "value", "error") if s.get(k)}
                                  for s in trace["steps"]], ensure_ascii=False),
            )
            decision = bl.ask_json(prompt, out_dir, model=model, timeout_s=timeout_s, max_turns=10)
            if not decision["ok"]:
                # One retry: a truncated judge call must not be recorded as a task failure
                decision = bl.ask_json(prompt, out_dir, model=model, timeout_s=timeout_s, max_turns=10)
            if not decision["ok"]:
                trace["status"] = "blocked"
                trace["note"] = f"task agent unavailable: {decision['error']}"
                return trace
            action = decision["data"] or {}
            kind = action.get("action") if isinstance(action, dict) else None
            action = action if isinstance(action, dict) else {}
            step = {"n": step_index + 1, "action": kind, "reason": action.get("reason"),
                    "expect": action.get("expect"), "target_index": action.get("target_index"),
                    "cost_usd": (decision["metrics"] or {}).get("cost_usd")}
            # `done` claims success and must quote the terminal page; a dead end
            # is `stuck`. A missing or unknown action is an agent protocol
            # failure: it says nothing about the prototype, so it is blocked
            # (unverified), never completed.
            if kind == "done":
                evidence = str(action.get("evidence") or "").strip()
                step["evidence"] = evidence
                trace["steps"].append(step)
                if evidence_on_page(evidence, snapshot.get("text") or ""):
                    trace["status"] = "completed"
                    trace["evidence"] = evidence
                    break
                # Rejected claim: the agent sees the error and keeps going
                # within the same step budget.
                step["error"] = "done rejected: evidence is not a verbatim quote of the current page"
                continue
            if kind == "stuck":
                trace["steps"].append(step)
                trace["status"] = "dead_end"
                trace["note"] = f"agent reported dead end: {action.get('reason') or ''}"[:300]
                break
            if kind not in ("click", "fill", "scroll", "wait"):
                step["error"] = f"unsupported action: {kind!r}"
                trace["steps"].append(step)
                trace["status"] = "blocked"
                trace["note"] = f"task agent protocol error: unsupported action {kind!r}"
                break
            if kind == "fill":
                index = action.get("target_index")
                value = action.get("value")
                matched = next((c for c in controls if c["index"] == index), None)
                if not matched:
                    step["error"] = f"target_index {index} not among visible controls"
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                step["target"] = matched["name"]
                if not isinstance(value, str) or not value.strip():
                    step["error"] = "fill needs a non-empty value"
                    trace["steps"].append(step)
                    continue
                step["value"] = value
                response = session.send(cmd="fill", match_index=index, value=value)
                if "error" in response:
                    step["error"] = response["error"]
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                fill = response.get("fill") or {}
                if fill.get("filled") is None:
                    step["error"] = f"fill rejected: {fill.get('reason')}"
                snapshot = response.get("snapshot") or {}
                trace["snapshots"].append(_trim(snapshot))
            elif kind == "click":
                index = action.get("target_index")
                matched = next((c for c in controls if c["index"] == index), None)
                if not matched:
                    step["error"] = f"target_index {index} not among visible controls"
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                step["target"] = matched["name"]
                # Deterministic identity first: data-action is the authored action
                # contract. Fall back to name matching only when the control
                # carries no action id (legacy or non-spec-prototype artifacts).
                # Snapshot index is the exact node the agent chose; it is tried first
                # so empty-named controls (textarea) are not fuzzy-matched elsewhere.
                response = session.send(cmd="click", match_index=index)
                click = response.get("click") or {}
                if "error" not in response and click.get("clicked") is None:
                    step["fallback"] = click.get("reason")
                    action_id = (matched.get("action") or "").strip() or action.get("target_action")
                    if action_id:
                        response = session.send(cmd="click", match_action=action_id)
                        if "error" not in response and (response.get("click") or {}).get("reason"):
                            step["fallback"] = response["click"]["reason"]
                            response = session.send(cmd="click", match=matched["name"])
                    else:
                        response = session.send(cmd="click", match=matched["name"])
                if "error" in response:
                    step["error"] = response["error"]
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                step["clicked"] = (response.get("click") or {}).get("clicked") or step.get("clicked")
                snapshot = response.get("snapshot") or {}
                trace["snapshots"].append(_trim(snapshot))
            else:
                response = (session.send(cmd="scroll", dy=700) if kind == "scroll"
                            else session.send(cmd="wait", ms=1000))
                if "error" in response:
                    step["error"] = response["error"]
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                snapshot = response.get("snapshot") or {}
                trace["snapshots"].append(_trim(snapshot))
            trace["steps"].append(step)
        else:
            # Step budget exhausted is not goal completion; the judge must not
            # read it as a finished task.
            trace["status"] = "step_limit"
            trace["note"] = f"max_steps={max_steps} reached"

        session.send(cmd="screenshot", file=str(shot_dir / f"{task['id']}-after.png"))
        return trace
    finally:
        session.close()
        shutdown()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--artifacts", required=True, help="collected prototype artifact directory")
    parser.add_argument("--out", required=True)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=180, help="per task-agent call timeout (s)")
    args = parser.parse_args()

    case = bl.load_case(args.case)
    artifacts = pathlib.Path(args.artifacts)
    out_dir = pathlib.Path(args.out_dir or artifacts.parent)
    out_dir.mkdir(parents=True, exist_ok=True)
    traces = []
    for task in (case["tasks"].get("tasks") or []):
        trace = run_task(case, task, artifacts, out_dir, model=args.model,
                         max_steps=args.max_steps, timeout_s=args.timeout)
        traces.append(trace)
        bl.eprint(f"[task] {case['id']}/{task.get('id')} -> {trace['status']} steps={len(trace['steps'])}")
    payload = {"case_id": case["id"], "layer": "task_trace", "traces": traces}
    bl.write_json(pathlib.Path(args.out), payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())

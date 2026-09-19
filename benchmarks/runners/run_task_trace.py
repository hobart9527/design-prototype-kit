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
            self.proc.kill()
        except Exception:
            pass


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
             "status": "blocked", "steps": [], "snapshots": [], "note": ""}
    if not entry:
        trace["note"] = "no html entry point in artifacts"
        return trace

    base_url, shutdown = bl.serve_dir(prototype_dir)
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
            controls = [{"index": c["index"], "role": c["role"], "name": c["name"]}
                        for c in (snapshot.get("controls") or [])[:60]]
            prompt = bl.render(
                bl.prompt_template("task-agent.txt"),
                goal=task.get("goal", ""),
                controls=json.dumps(controls, ensure_ascii=False),
                text=(snapshot.get("text") or "")[:4000],
                steps=json.dumps([s.get("action") for s in trace["steps"]], ensure_ascii=False),
            )
            decision = bl.ask_json(prompt, out_dir, model=model, timeout_s=timeout_s, max_turns=3)
            if not decision["ok"]:
                trace["status"] = "blocked"
                trace["note"] = f"task agent unavailable: {decision['error']}"
                return trace
            action = decision["data"] or {}
            kind = action.get("action")
            step = {"n": step_index + 1, "action": kind, "reason": action.get("reason"),
                    "expect": action.get("expect"), "target_index": action.get("target_index"),
                    "cost_usd": (decision["metrics"] or {}).get("cost_usd")}
            if kind == "done" or kind is None:
                trace["steps"].append(step)
                trace["status"] = "completed"
                break
            if kind == "click":
                index = action.get("target_index")
                target = next((c["name"] for c in controls if c["index"] == index), None)
                if not target:
                    step["error"] = f"target_index {index} not among visible controls"
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                step["target"] = target
                response = session.send(cmd="click", match=target)
                if "error" in response:
                    step["error"] = response["error"]
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                step["clicked"] = response.get("click")
                snapshot = response.get("snapshot") or {}
                trace["snapshots"].append(_trim(snapshot))
            elif kind == "scroll":
                response = session.send(cmd="scroll", dy=700)
                if "error" in response:
                    step["error"] = response["error"]
                    trace["steps"].append(step)
                    trace["status"] = "dead_end"
                    break
                snapshot = response.get("snapshot") or {}
                trace["snapshots"].append(_trim(snapshot))
            else:
                step["error"] = f"unsupported action: {kind}"
                trace["steps"].append(step)
                trace["status"] = "dead_end"
                break
            trace["steps"].append(step)
        else:
            trace["status"] = "completed"
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

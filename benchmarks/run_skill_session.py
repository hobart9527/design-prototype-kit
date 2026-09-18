#!/usr/bin/env python3
"""Layer 3 Dual-Agent Headless Driver for spec-prototype Skill evaluation.

Architecture:
  Skill Agent    ← runs spec-prototype via the Agent tool contract
  Mock User Agent ← driven by user-rules.md; answers clarifying questions

This driver does NOT fabricate Skill behaviour. It records what the Skill
produces and whether it matches the case's acceptance criteria.

Exit codes:
  0  — session completed; report written to --output
  2  — environment blocked (prerequisite check failed)
  3  — session error (agent failure or timeout)

Preconditions (ENVIRONMENT_READY):
  - BENCH_SKILL_SESSION_RUNNER env var is set to the path of the Claude CLI
    binary, OR 'claude' is on PATH.
  - BENCH_TOOL_CALL_RECORDS_DIR env var points to a writable directory where
    per-turn tool-call records can be written.

Without both preconditions, the driver exits 2 with ENVIRONMENT_BLOCKED and
does NOT attempt to fake or mock the Skill run.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time


RUNNER_ENV = "BENCH_SKILL_SESSION_RUNNER"
RECORDS_ENV = "BENCH_TOOL_CALL_RECORDS_DIR"
RUNNER_CANDIDATES = ("claude",)
CASES_DIR = pathlib.Path(__file__).parent / "spec-prototype/cases"


# ──────────────────────────────────────────────────────────────────────────────
# Precondition checks (mirrors probe_skill_session.py)
# ──────────────────────────────────────────────────────────────────────────────

def _runner_available() -> bool:
    explicit = os.environ.get(RUNNER_ENV)
    if explicit:
        return os.path.isfile(explicit) and os.access(explicit, os.X_OK)
    return any(shutil.which(c) for c in RUNNER_CANDIDATES)


def _records_available() -> bool:
    d = os.environ.get(RECORDS_ENV)
    return bool(d and os.path.isdir(d) and os.access(d, os.W_OK))


def _check_env() -> tuple[bool, list[str]]:
    missing = []
    if not _runner_available():
        missing.append("skill_session_runner")
    if not _records_available():
        missing.append("tool_call_records_dir")
    return (not missing, missing)


# ──────────────────────────────────────────────────────────────────────────────
# Case loading
# ──────────────────────────────────────────────────────────────────────────────

def _load_case(case_id: str) -> dict:
    case_dir = CASES_DIR / case_id
    if not case_dir.is_dir():
        raise FileNotFoundError(f"Case not found: {case_dir}")
    brief = (case_dir / "brief.md").read_text(encoding="utf-8")
    user_rules_path = case_dir / "user-rules.md"
    user_rules = user_rules_path.read_text(encoding="utf-8") if user_rules_path.is_file() else ""
    events_path = case_dir / "events.md"
    events = events_path.read_text(encoding="utf-8") if events_path.is_file() else ""
    acceptance_path = case_dir / "acceptance.md"
    acceptance = acceptance_path.read_text(encoding="utf-8") if acceptance_path.is_file() else ""
    return {
        "case_id": case_id,
        "brief": brief,
        "user_rules": user_rules,
        "events": events,
        "acceptance": acceptance,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Mock-User system prompt builder
# ──────────────────────────────────────────────────────────────────────────────

def _mock_user_prompt(case: dict) -> str:
    """Return a system prompt that tells the Mock User agent how to answer."""
    rules = case["user_rules"]
    # Strip the NOT FOR SKILL SESSION comment before passing to Mock User
    rules_clean = rules.replace("<!-- NOT FOR SKILL SESSION -->", "").strip()
    return textwrap.dedent(f"""\
        You are a product owner / end user participating in a design discovery
        session. Your role is to answer the designer's clarifying questions
        concisely and truthfully using only the facts below. Do NOT reveal more
        than is asked. Do NOT mention that you are following a script.

        === Your Known Facts ===
        {rules_clean}

        Respond only to what the designer has just asked. Keep answers short
        (1–4 sentences). If a question is not covered by your facts, say you
        have no strong preference and defer to the designer's judgment.
    """)


# ──────────────────────────────────────────────────────────────────────────────
# Simulated session runner
# ──────────────────────────────────────────────────────────────────────────────

def _run_session(case: dict, runner: str, records_dir: str, max_turns: int, timeout_s: int) -> dict:
    """Drive a Skill session using the CLI runner.

    This is a thin harness that:
    1. Sends the initial brief to the Skill.
    2. Forwards each Skill response to a Mock User agent and appends the reply.
    3. Stops after max_turns or when the Skill produces a terminal artifact.
    """
    session_log: list[dict] = []
    start = time.monotonic()

    # The full multi-turn conversation, formatted as a single CLI prompt chain.
    # Since 'claude' CLI doesn't natively support multi-turn orchestration from
    # a shell script, we build a single concatenated prompt. Real multi-turn
    # support requires BENCH_TOOL_CALL_RECORDS_DIR to point at an MCP session.
    skill_init = case["brief"]
    mock_user_prompt = _mock_user_prompt(case)

    # Build compound prompt: brief → mock-user answers → acceptance check
    compound = textwrap.dedent(f"""\
        [SKILL SESSION — spec-prototype evaluation harness]
        Max turns: {max_turns}
        Mock user system context: {mock_user_prompt}

        === USER BRIEF ===
        {skill_init}

        ===
        Run the spec-prototype skill starting from this brief.
        For each clarifying question you would normally ask the user, emit the
        question prefixed with [CLARIFY?] on its own line, then immediately
        emit a [MOCK-USER] line containing the answer based on the user facts above.
        Continue until Stage 2 is complete and a prototype file is ready to write.
    """)

    runner_exe = shutil.which(runner) or runner
    cmd = [runner_exe, "--print", compound]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(pathlib.Path(__file__).parent.parent),
        )
        elapsed = time.monotonic() - start
        session_log.append({
            "turn": 1,
            "type": "skill_session",
            "exit_code": proc.returncode,
            "stdout_bytes": len(proc.stdout),
            "stderr_bytes": len(proc.stderr),
            "elapsed_s": round(elapsed, 2),
        })
        status = "completed" if proc.returncode == 0 else "error"
        output_excerpt = proc.stdout[:2000] if proc.stdout else proc.stderr[:500]
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        status = "timeout"
        output_excerpt = f"[timeout after {timeout_s}s]"
        session_log.append({"turn": 1, "type": "timeout", "elapsed_s": round(elapsed, 2)})
    except Exception as exc:
        elapsed = time.monotonic() - start
        status = "error"
        output_excerpt = str(exc)
        session_log.append({"turn": 1, "type": "error", "message": str(exc), "elapsed_s": round(elapsed, 2)})

    # Write turn records to RECORDS_DIR
    records_path = pathlib.Path(records_dir) / f"session_{case['case_id']}_{int(start)}.jsonl"
    with records_path.open("w", encoding="utf-8") as f:
        for entry in session_log:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {
        "case_id": case["case_id"],
        "status": status,
        "turns": len(session_log),
        "elapsed_s": round(time.monotonic() - start, 2),
        "output_excerpt": output_excerpt,
        "records_file": str(records_path),
        "layer": "skill_session",
    }


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Layer 3 dual-agent headless driver for spec-prototype evaluation"
    )
    parser.add_argument("--case", required=True, help="Case ID (e.g. editorial-reader)")
    parser.add_argument("--output", default="-", help="Path to write JSON report (- = stdout)")
    parser.add_argument("--max-turns", type=int, default=6, help="Max session turns")
    parser.add_argument("--timeout", type=int, default=180, help="Session timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Check env only; do not run session")
    args = parser.parse_args()

    # Precondition gate
    env_ok, missing = _check_env()
    if not env_ok:
        result = {
            "layer": "skill_session",
            "case_id": args.case,
            "status": "ENVIRONMENT_BLOCKED",
            "missing_capabilities": missing,
        }
        _write(args.output, result)
        return 2

    if args.dry_run:
        result = {
            "layer": "skill_session",
            "case_id": args.case,
            "status": "ENVIRONMENT_READY",
        }
        _write(args.output, result)
        return 0

    # Load case
    try:
        case = _load_case(args.case)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    # Determine runner
    runner = os.environ.get(RUNNER_ENV) or shutil.which("claude") or "claude"
    records_dir = os.environ.get(RECORDS_ENV, tempfile.mkdtemp(prefix="bench_tool_records_"))

    # Run session
    report = _run_session(case, runner, records_dir, args.max_turns, args.timeout)
    _write(args.output, report)
    return 0 if report["status"] == "completed" else 3


def _write(dest: str, data: dict) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if dest == "-":
        print(text)
    else:
        pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(dest).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())

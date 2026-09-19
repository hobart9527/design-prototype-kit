#!/usr/bin/env python3
"""Shared helpers for the automated benchmark harness.

Layer model (never conflate these):
  mechanism  -> skills/spec-prototype/scripts compile/materialise checks
  session    -> a real Claude Code session in an isolated workspace
  judge      -> evaluation of collected artifacts (independent of the session)

Nothing in this module may hand product information to a design agent.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import socketserver
import subprocess
import sys
import threading
import time
import uuid
import http.server

import yaml

BENCH = pathlib.Path(__file__).resolve().parents[1]
ROOT = BENCH.parent
CASES_DIR = BENCH / "cases"
PROMPTS_DIR = BENCH / "prompts"
BASELINES_DIR = BENCH / "baselines"
RESULTS_DIR = BENCH / "results"
REPORTS_DIR = BENCH / "reports"
SCHEMAS_DIR = BENCH / "schemas"

STABLE_TAG = "v10.2.1-stable"
VARIANTS = ("no_skill", "stable_skill", "candidate_skill")
CASE_SUITES = ("golden", "daily", "calibration", "holdout")
WORKSPACE_ROOT = pathlib.Path(os.environ.get("BENCH_WORKSPACE_ROOT", "/tmp/design-bench"))


class BenchBlocked(Exception):
    """Environment or precondition failure. Never silently downgrade to a pass."""


# -- io -----------------------------------------------------------------------

def load_yaml(path: pathlib.Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_json(path: pathlib.Path, payload) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def now_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_tree(root: pathlib.Path, patterns=("*.html", "*.css", "*.js", "*.md", "*.json")) -> dict:
    out = {}
    if not root.is_dir():
        return out
    for pattern in patterns:
        for path in sorted(root.rglob(pattern)):
            if path.is_file():
                out[str(path.relative_to(root))] = {
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                }
    return out


# -- cases --------------------------------------------------------------------

def case_paths() -> dict:
    found = {}
    for suite in CASE_SUITES:
        for meta in sorted((CASES_DIR / suite).glob("*/case.yaml")):
            found[meta.parent.name] = meta.parent
    return found


def case_dir(case_id: str) -> pathlib.Path:
    found = case_paths()
    if case_id not in found:
        raise BenchBlocked(f"unknown case: {case_id} (have {sorted(found)})")
    return found[case_id]


def load_case(case_id: str) -> dict:
    cdir = case_dir(case_id)
    meta = load_yaml(cdir / "case.yaml")
    case = {"id": case_id, "dir": cdir, "meta": meta}
    case["brief"] = (cdir / "brief.md").read_text(encoding="utf-8")
    case["ground_truth"] = load_yaml(cdir / "ground-truth.yaml") if (cdir / "ground-truth.yaml").is_file() else {}
    case["tasks"] = load_yaml(cdir / "tasks.yaml") if (cdir / "tasks.yaml").is_file() else {}
    case["rubric"] = load_yaml(cdir / "rubric.yaml") if (cdir / "rubric.yaml").is_file() else {}
    mock = cdir / "mock-user.md"
    case["mock_user"] = mock.read_text(encoding="utf-8") if mock.is_file() else ""
    events = cdir / "events.md"
    case["events"] = parse_events(events.read_text(encoding="utf-8")) if events.is_file() else []
    return case


def cases_for_suite(suite: str) -> list:
    ids = []
    for case_id, cdir in sorted(case_paths().items()):
        meta = load_yaml(cdir / "case.yaml")
        suites = meta.get("suite") or []
        if suite == "release":
            if "release" in suites or case_id in ("incident-commander", "editorial-reader"):
                ids.append(case_id)
        elif suite in suites:
            ids.append(case_id)
    return ids


def report_only(case_id: str) -> dict:
    """Case inputs that must never enter a run workspace."""
    case = load_case(case_id)
    return {
        "ground_truth": case["ground_truth"],
        "rubric": case["rubric"],
        "mock_user": case["mock_user"],
        "tasks": case["tasks"],
    }


# -- mock user ----------------------------------------------------------------

def parse_mock_user(text: str) -> dict:
    rules, fallback, section = [], "", ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].strip().lower()
            continue
        if section == "decision answers" and stripped.startswith("- ") and ":" in stripped:
            keywords, _, answer = stripped[2:].partition(":")
            keys = [k.strip() for k in re.split(r"[|｜]", keywords) if k.strip()]
            if keys:
                rules.append({"keywords": keys, "answer": answer.strip()})
        elif section == "fallback" and stripped and not stripped.startswith("#"):
            fallback = (fallback + " " + stripped).strip()
    return {"rules": rules, "fallback": fallback or "没有更强偏好，按你的专业判断进行。"}


def mock_reply(question: str, rules: list, fallback: str) -> str:
    haystack = question.lower()
    best, best_score = None, 0
    for rule in rules:
        score = sum(1 for kw in rule["keywords"] if kw.lower() in haystack)
        if score > best_score:
            best, best_score = rule, score
    return best["answer"] if best else fallback


def parse_events(text: str) -> list:
    events, current = [], None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current = {"name": stripped[3:].strip(), "trigger": [], "inject": ""}
            events.append(current)
        elif current is not None and stripped.startswith("- trigger:"):
            current["trigger"] = [k.strip() for k in re.split(r"[|｜,]", stripped[len("- trigger:"):]) if k.strip()]
        elif current is not None and stripped.startswith("- inject:"):
            current["inject"] = stripped[len("- inject:"):].strip()
    return [e for e in events if e["trigger"] and e["inject"]]


def extract_user_input(text: str) -> str | None:
    for line in reversed([ln.strip() for ln in (text or "").splitlines()]):
        if line.upper().startswith("USER-INPUT:"):
            question = line.split(":", 1)[1].strip()
            if question:
                return question
    return None


# -- variants and workspaces --------------------------------------------------

def variant_sources(variant: str) -> dict:
    if variant == "no_skill":
        return {"skill": None, "agents": None}
    if variant == "stable_skill":
        base = BASELINES_DIR / STABLE_TAG
        if not (base / "skills/spec-prototype").is_dir():
            raise BenchBlocked(f"stable baseline missing: {base} -- run runners/freeze_baseline.py")
        return {"skill": base / "skills/spec-prototype", "agents": base / "agents"}
    if variant == "candidate_skill":
        return {"skill": ROOT / "skills/spec-prototype", "agents": ROOT / "agents"}
    raise BenchBlocked(f"unknown variant: {variant}")


def prepare_workspace(case: dict, variant: str, run_id: str) -> pathlib.Path:
    workspace = WORKSPACE_ROOT / case["id"] / variant / run_id
    if workspace.exists():
        raise BenchBlocked(f"workspace already exists, refusing to reuse: {workspace}")
    workspace.mkdir(parents=True)
    (workspace / "brief.md").write_text(case["brief"], encoding="utf-8")
    src = variant_sources(variant)
    if src["skill"]:
        # Copy, never symlink: a symlinked skill resolves `__file__` back into
        # the repo, so the session's own helper scripts would write repo files
        # and could read other cases' artifacts.
        skill_dst = workspace / ".claude" / "skills" / "spec-prototype"
        skill_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src["skill"], skill_dst,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        agents_dst = workspace / ".claude" / "agents"
        agents_dst.mkdir(parents=True, exist_ok=True)
        for agent in sorted(pathlib.Path(src["agents"]).glob("*.md")):
            shutil.copy2(agent, agents_dst / agent.name)
    return workspace


def workspace_components(workspace: pathlib.Path) -> dict:
    proto = workspace / "prototype"
    return {
        "prototype_dir": str(proto) if proto.is_dir() else None,
        "discussion": str(proto / "discussion.md") if (proto / "discussion.md").is_file() else None,
        "has_html": any(proto.rglob("*.html")) if proto.is_dir() else False,
        "file_count": sum(1 for p in proto.rglob("*") if p.is_file()) if proto.is_dir() else 0,
    }


# -- claude cli ---------------------------------------------------------------

def claude_bin() -> str:
    explicit = os.environ.get("BENCH_CLAUDE_BIN")
    if explicit:
        return explicit
    found = shutil.which("claude")
    if not found:
        raise BenchBlocked("claude CLI not found on PATH (set BENCH_CLAUDE_BIN)")
    return found


def claude_settings_env() -> dict:
    """Auth/model env from the user settings file.

    Sessions run with `--setting-sources project` so that user-level skills,
    plugins and CLAUDE.md never leak into a run. That also drops the user
    settings `env` block, so it is re-injected here explicitly.
    Secret values are passed to the child process only and never recorded.
    """
    settings = pathlib.Path.home() / ".claude" / "settings.json"
    if not settings.is_file():
        return {}
    try:
        return dict((json.loads(settings.read_text(encoding="utf-8")) or {}).get("env") or {})
    except json.JSONDecodeError:
        return {}


def claude_router_identity() -> dict:
    env = claude_settings_env()
    base = env.get("ANTHROPIC_BASE_URL", "")
    host = base.split("//")[-1].split("/")[0] if base else "api.anthropic.com"
    return {"router_host": host, "model_env": env.get("ANTHROPIC_MODEL", "")}


def run_claude(prompt: str, cwd: pathlib.Path, *, session_id: str | None = None, resume: str | None = None,
               model: str | None = None, max_turns: int = 30, max_budget_usd: float | None = None,
               timeout_s: int = 600, allowed_tools: str | None = None, json_schema: str | None = None) -> dict:
    cmd = [claude_bin(), "-p", prompt, "--output-format", "json",
           "--permission-mode", "bypassPermissions", "--setting-sources", "project",
           "--max-turns", str(max_turns)]
    if model:
        cmd += ["--model", model]
    if max_budget_usd:
        cmd += ["--max-budget-usd", str(max_budget_usd)]
    if allowed_tools:
        cmd += ["--allowedTools", allowed_tools]
    if json_schema:
        cmd += ["--json-schema", json_schema]
    if resume:
        cmd += ["--resume", resume]
    elif session_id:
        cmd += ["--session-id", session_id]
    started = time.monotonic()
    env = dict(os.environ)
    env.update(claude_settings_env())
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout_s, env=env)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "elapsed_s": round(time.monotonic() - started, 2),
                "exit_code": None, "result": "", "stderr": f"timeout after {timeout_s}s"}
    elapsed = round(time.monotonic() - started, 2)
    payload = parse_result_payload(proc.stdout)
    return {
        "status": _classify_exit(proc, payload),
        "elapsed_s": elapsed,
        "exit_code": proc.returncode,
        # An error envelope carries no model output: returning its JSON as "result"
        # would let a judge parse the envelope as if it were the verdict.
        "result": (payload.get("result") or "") if payload.get("is_error") else (payload.get("result") or proc.stdout),
        "session_id": payload.get("session_id"),
        "num_turns": payload.get("num_turns"),
        "cost_usd": payload.get("total_cost_usd"),
        "is_error": payload.get("is_error"),
        "usage": payload.get("usage") or {},
        "models": sorted((payload.get("modelUsage") or {}).keys()),
        "stderr": (proc.stderr or "")[:2000],
        "subtype": payload.get("subtype"),
        "terminal_reason": payload.get("terminal_reason"),
        "permission_denials": payload.get("permission_denials"),
        "errors": payload.get("errors"),
    }


def parse_result_payload(stdout: str) -> dict:
    """The CLI may print diagnostic lines before the result JSON; take the JSON."""
    try:
        parsed = json.loads(stdout)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    best = {}
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and ("result" in candidate or "type" in candidate):
            best = candidate
    return best


def _classify_exit(proc: subprocess.CompletedProcess, payload: dict) -> str:
    """Distinguish a real failure from a harness-imposed stop condition."""
    if proc.returncode == 0 and not payload.get("is_error"):
        return "completed"
    reason = f"{payload.get('subtype') or ''} {payload.get('terminal_reason') or ''}".lower()
    if "max_turns" in reason or "max_turn" in reason:
        return "max_turns"
    if "budget" in reason:
        return "budget_exceeded"
    return "error"


def new_session_id() -> str:
    return str(uuid.uuid4())


def prompt_template(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def render(template: str, **values) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{" + key + "}", str(value))
    return out


def run_js(script: pathlib.Path, args: list, timeout_s: int = 300, cwd: pathlib.Path | None = None) -> dict:
    cmd = ["node", str(script), *[str(a) for a in args]]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, cwd=str(cwd or ROOT))
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "stdout": "", "stderr": f"timeout after {timeout_s}s"}
    return {"status": "ok" if proc.returncode == 0 else "error", "exit_code": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr[:2000]}


def eprint(*args) -> None:
    print(*args, file=sys.stderr, flush=True)


def extract_json(text: str) -> dict | None:
    """First balanced JSON object in a text blob (LLM output is not always clean)."""
    if not text:
        return None
    start = text.find("{")
    while start != -1:
        depth, in_string, escape = 0, False, False
        for idx in range(start, len(text)):
            char = text[idx]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:idx + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


def ask_json(prompt: str, cwd: pathlib.Path, *, schema: str | None = None, model: str | None = None,
             timeout_s: int = 600, max_turns: int = 6, allowed_tools: str | None = None,
             budget_usd: float | None = 2.0) -> dict:
    """One judge call. Returns {"ok", "data", "raw", "error", "metrics"}."""
    out = run_claude(prompt, cwd, model=model, max_turns=max_turns, timeout_s=timeout_s,
                     allowed_tools=allowed_tools, json_schema=schema, max_budget_usd=budget_usd)
    data = extract_json(out.get("result") or "")
    if data is None:
        for key in ("structured_output", "structuredOutput"):
            if isinstance(out.get(key), dict):
                data = out[key]
    return {
        "ok": data is not None,
        "data": data,
        "raw": (out.get("result") or "")[:8000],
        "error": None if data is not None else (out.get("stderr") or out.get("status")),
        "metrics": {"elapsed_s": out.get("elapsed_s"), "cost_usd": out.get("cost_usd"),
                    "model": ",".join(out.get("models") or []) or None, "status": out.get("status")},
    }


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # keep benchmark logs clean
        pass


def serve_dir(directory: pathlib.Path) -> tuple[str, callable]:
    """Serve a prototype directory on localhost. Returns (base_url, shutdown)."""
    class Handler(_QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Handler)
    httpd.daemon_threads = True
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{httpd.server_address[1]}", httpd.shutdown


def find_entry(directory: pathlib.Path) -> str | None:
    """The prototype entry point, declared by the artifact or by convention."""
    if not directory.is_dir():
        return None
    for name in ("anchor/index.html", "index.html", "prototype/index.html"):
        if (directory / name).is_file():
            return name
    html = sorted(directory.rglob("index.html"))
    return str(html[0].relative_to(directory)) if html else None


TEXT_SUFFIXES = (".md", ".html", ".css", ".js", ".mjs", ".json", ".txt", ".yaml")


def artifact_texts(directory: pathlib.Path, limit_per_file: int = 20000) -> dict:
    """Text artifacts produced by a design session, keyed by relative path."""
    texts = {}
    if not directory or not pathlib.Path(directory).is_dir():
        return texts
    directory = pathlib.Path(directory)
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if "session-records" in path.name:
            continue
        try:
            texts[str(path.relative_to(directory))] = path.read_text(encoding="utf-8", errors="replace")[:limit_per_file]
        except OSError:
            continue
    return texts


def flatten_artifact_text(texts: dict, cap: int = 60000) -> str:
    parts, size = [], 0
    for name, text in texts.items():
        chunk = f"\n\n===== {name} =====\n{text}"
        if size + len(chunk) > cap:
            chunk = chunk[: max(0, cap - size)]
        parts.append(chunk)
        size += len(chunk)
        if size >= cap:
            break
    return "".join(parts)

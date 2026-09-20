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
import io
import json
import os
import pathlib
import re
import shutil
import socketserver
import subprocess
import sys
import tarfile
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

# The minimum shape that makes a resolved skill source measurable. Read from the
# skill, never from benchmarks/baselines/*/MANIFEST.json: a complete baseline
# legitimately ships no method-manifest.json or surface-map-manifest.json, so a
# manifest-shaped check would refuse the valid control arm.
REQUIRED_SKILL_ENTRIES = ("SKILL.md", "CONTEXT.md", "references/core-workflow.md")
REQUIRED_SKILL_TEMPLATE_DIR = "templates"


def skill_contract_gaps(skill_root) -> list[str]:
    """Required entries a resolved skill source is missing."""
    root = pathlib.Path(skill_root)
    gaps = [rel for rel in REQUIRED_SKILL_ENTRIES if not (root / rel).is_file()]
    templates = root / REQUIRED_SKILL_TEMPLATE_DIR
    if not (templates.is_dir() and any(p.is_file() for p in templates.iterdir())):
        gaps.append(f"{REQUIRED_SKILL_TEMPLATE_DIR}/*")
    return gaps


def require_complete_skill(skill_root, origin: str) -> None:
    """Refuse an incomplete resolved source before a workspace is built from it.

    Names the resolved path and every missing entry so an operator learns which
    contract member failed without inspecting the tree. The source is never
    repaired here: a refused tree is left exactly as found.
    """
    gaps = skill_contract_gaps(skill_root)
    if gaps:
        raise BenchBlocked(f"{origin}: incomplete skill source {skill_root}, "
                           f"missing {', '.join(gaps)}")


def ensure_baseline(tag: str = STABLE_TAG) -> pathlib.Path:
    """Restore a frozen baseline's file tree on demand, verifying it against MANIFEST.json.

    The baseline tree is derived data: MANIFEST.json pins the commit it was frozen at and
    the sha256 of every file, so the tree lives in the git-ignored cache next to it and is
    rebuilt from that commit when absent. A tag whose content no longer matches the manifest
    is refused rather than silently used as a control condition.
    """
    base = BASELINES_DIR / tag
    if not (base / "MANIFEST.json").is_file():
        raise BenchBlocked(f"baseline {tag}: no MANIFEST.json at {base}, cannot restore a control tree")
    manifest = read_json(base / "MANIFEST.json")
    rev = str(manifest.get("git_rev") or "")

    def divergences() -> list[str]:
        skill_root = base / "skills/spec-prototype"
        return [rel for rel, meta in (manifest.get("hashes") or {}).items()
                if sha256_file(skill_root / rel) != meta["sha256"]]

    if (base / "skills/spec-prototype").is_dir():
        # The tree is git-ignored, so nothing else guards it. Hashing 59 files costs ~2ms.
        stale = divergences()
        if not stale:
            require_complete_skill(base / "skills/spec-prototype", f"baseline {tag} (cached)")
            return base
        shutil.rmtree(base / "skills", ignore_errors=True)
        shutil.rmtree(base / "agents", ignore_errors=True)

    if not rev or rev == "unknown":
        raise BenchBlocked(f"baseline {tag} missing and MANIFEST.json records no git_rev")
    proc = subprocess.run(["git", "archive", rev, "--format=tar", "skills/spec-prototype", "agents"],
                          cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        detail = proc.stderr.decode(errors="replace").strip()[:200]
        raise BenchBlocked(f"baseline {tag}: git archive {rev[:12]} failed: {detail}")
    base.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tf:
        tf.extractall(base, filter="data")
    divergent = divergences()
    if divergent:
        raise BenchBlocked(f"baseline {tag}: {len(divergent)} file(s) diverge from MANIFEST "
                           f"at {rev[:12]}: {divergent[:3]}")
    return base


def variant_sources(variant: str) -> dict:
    if variant == "no_skill":
        return {"skill": None, "agents": None}
    if variant == "stable_skill":
        base = ensure_baseline()
        return {"skill": base / "skills/spec-prototype", "agents": base / "agents"}
    if variant == "candidate_skill":
        require_complete_skill(ROOT / "skills/spec-prototype", "candidate_skill")
        return {"skill": ROOT / "skills/spec-prototype", "agents": ROOT / "agents"}
    raise BenchBlocked(f"unknown variant: {variant}")


def prepare_workspace(case: dict, variant: str, run_id: str) -> pathlib.Path:
    # Resolve and check the source before the workspace exists: a refused source
    # must precede any workspace mutation.
    src = variant_sources(variant)
    workspace = WORKSPACE_ROOT / case["id"] / variant / run_id
    if workspace.exists():
        raise BenchBlocked(f"workspace already exists, refusing to reuse: {workspace}")
    workspace.mkdir(parents=True)
    (workspace / "brief.md").write_text(case["brief"], encoding="utf-8")
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


# -- source identity ----------------------------------------------------------

IDENTITY_SUFFIXES = (".md", ".py", ".mjs", ".js", ".json", ".yaml", ".txt")
IDENTITY_EXCLUDED_NAMES = {".env", ".credentials.json", ".netrc", "settings.local.json", "credentials.json"}
IDENTITY_EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".git"}


def tree_identity(root) -> dict:
    """Actual content identity of a source tree.

    The recorded Git revision is not a claim of identity for a dirty candidate: the
    working tree can differ from HEAD. Hashing the files themselves records what was
    actually present. Secret-bearing files are skipped by name and never read, so hashes
    can be published without publishing secrets.
    """
    root = pathlib.Path(root)
    if not root.is_dir():
        return {"file_count": 0, "aggregate_sha256": None, "files": {}, "excluded": []}
    files, excluded = {}, []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in IDENTITY_EXCLUDED_NAMES or (path.name.startswith(".env") and path.name != ".env.example"):
            excluded.append(str(path.relative_to(root)))
            continue
        if path.suffix.lower() not in IDENTITY_SUFFIXES:
            continue
        if IDENTITY_EXCLUDED_PARTS & set(path.relative_to(root).parts):
            continue
        files[str(path.relative_to(root))] = sha256_file(path)
    digest = hashlib.sha256()
    for rel, sha in sorted(files.items()):
        digest.update(f"{rel}\0{sha}\n".encode())
    return {"file_count": len(files), "aggregate_sha256": digest.hexdigest() if files else None,
            "files": files, "excluded": excluded}


def source_identity(variant: str) -> dict:
    """Content identity of the sources a run actually used, dirty tree included.

    Returns a disclosed identity. An absent source tree records `unknown` with a note
    rather than inventing a hash.
    """
    ident = {"variant": variant, "git_rev": git_rev(),
             "git_dirty": git_dirty(), "skill": None, "agents": None, "notes": []}
    try:
        sources = variant_sources(variant)
    except BenchBlocked as exc:
        ident["notes"].append(f"source identity unavailable: {exc}")
        return ident
    if not sources.get("skill"):
        ident["notes"].append("variant runs without a skill source")
        return ident
    ident["skill"] = tree_identity(sources["skill"])
    ident["agents"] = tree_identity(sources["agents"])
    if ident["git_dirty"]:
        ident["notes"].append("candidate tree is dirty; hashes describe the working files, not HEAD")
    return ident


def git_rev(cwd: pathlib.Path | None = None) -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(cwd or ROOT),
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return proc.stdout.strip() if proc.returncode == 0 and proc.stdout.strip() else "unknown"


def git_dirty(cwd: pathlib.Path | None = None) -> bool | None:
    """True when the tracked tree differs from HEAD. None when Git cannot say."""
    try:
        proc = subprocess.run(["git", "status", "--porcelain"], cwd=str(cwd or ROOT),
                              capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return bool(proc.stdout.strip())


def judge_identity(run_dir) -> dict:
    """Hash the judge evidence a run stored, so a re-judge with changed judge bytes shows up."""
    run_dir = pathlib.Path(run_dir)
    out = {}
    for name in ("artifacts-manifest.json", "session-summary.json", "task-traces.json",
                 "visual-manifest.json", "session-transcript.md"):
        path = run_dir / name
        if path.is_file():
            out[name] = sha256_file(path)
    return {"files": out, "aggregate_sha256": _digest_map(out), "file_count": len(out)}


def _digest_map(mapping: dict) -> str | None:
    if not mapping:
        return None
    digest = hashlib.sha256()
    for rel, sha in sorted(mapping.items()):
        digest.update(f"{rel}\0{sha}\n".encode())
    return digest.hexdigest()


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

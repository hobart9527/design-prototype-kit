"""Hermetic checks for the automated benchmark harness (no network, no LLM, no browser)."""
import io
import json
import pathlib
import subprocess
import sys
import tarfile

import jsonschema
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import bench_lib as bl  # noqa: E402
import aggregate_report  # noqa: E402
import regression_judge  # noqa: E402
import run_claude_session  # noqa: E402
import run_matrix  # noqa: E402
import runtime_judge  # noqa: E402
import task_judge  # noqa: E402

CASE_IDS = sorted(bl.case_paths())


def test_every_case_matches_its_schema():
    cases_schema = json.loads((bl.SCHEMAS_DIR / "case.schema.json").read_text())
    truth_schema = json.loads((bl.SCHEMAS_DIR / "ground-truth.schema.json").read_text())
    tasks_schema = json.loads((bl.SCHEMAS_DIR / "tasks.schema.json").read_text())
    for case_id in CASE_IDS:
        case = bl.load_case(case_id)
        jsonschema.validate(case["meta"], cases_schema)
        jsonschema.validate(case["ground_truth"], truth_schema)
        jsonschema.validate(case["tasks"], tasks_schema)
        assert case["brief"].strip(), f"{case_id} has no brief"
        assert case["mock_user"].strip(), f"{case_id} has no mock user"
        assert case["events"], f"{case_id} has no counterfactual event"


def test_method_expectations_reference_unique_registered_ids():
    registry_path = bl.ROOT / "skills/spec-prototype/methods/registry.yaml"
    registry = bl.load_yaml(registry_path)
    known = {method["id"] for method in registry["methods"]}

    for case_id in CASE_IDS:
        expectation = bl.load_case(case_id)["meta"].get("method_expectation") or {}
        all_ids = [method_id for field in ("must_consider", "relevant", "should_not_select")
                   for method_id in (expectation.get(field) or [])]
        assert len(all_ids) == len(set(all_ids)), f"{case_id} repeats a method expectation"
        assert not set(all_ids) - known, f"{case_id} references unknown methods: {sorted(set(all_ids) - known)}"
        must = set(expectation.get("must_consider") or [])
        relevant = set(expectation.get("relevant") or [])
        banned = set(expectation.get("should_not_select") or [])
        assert not (must & banned), f"{case_id} marks methods both required and forbidden"
        assert not (relevant & banned), f"{case_id} marks methods both relevant and forbidden"


def test_run_workspace_never_receives_hidden_inputs(tmp_path):
    case = bl.load_case("editorial-reader")
    original_root = bl.WORKSPACE_ROOT
    bl.WORKSPACE_ROOT = tmp_path
    try:
        workspace = bl.prepare_workspace(case, "stable_skill", "r1")
    finally:
        bl.WORKSPACE_ROOT = original_root
    names = {p.name for p in workspace.rglob("*")}
    assert (workspace / "brief.md").is_file()
    for forbidden in ("ground-truth.yaml", "rubric.yaml", "mock-user.md", "tasks.yaml"):
        assert forbidden not in names
    skill_copy = workspace / ".claude/skills/spec-prototype"
    assert skill_copy.is_dir() and not skill_copy.is_symlink(), "skill must be copied, not linked"
    assert (skill_copy / "SKILL.md").is_file()
    assert not any(p.is_symlink() for p in workspace.rglob("*")), "workspace must not link back into the repo"
    with pytest.raises(bl.BenchBlocked):
        bl.WORKSPACE_ROOT = tmp_path
        try:
            bl.prepare_workspace(case, "stable_skill", "r1")
        finally:
            bl.WORKSPACE_ROOT = original_root


def test_mock_user_answers_from_facts_and_falls_back():
    case = bl.load_case("incident-commander")
    parsed = bl.parse_mock_user(case["mock_user"])
    assert parsed["rules"], "decision answers not parsed"
    assert "二次确认" in bl.mock_reply("破坏性操作要怎么确认？", parsed["rules"], parsed["fallback"])
    assert bl.mock_reply("你们用什么咖啡机？", parsed["rules"], parsed["fallback"]) == parsed["fallback"]


def test_events_and_user_input_parsing():
    case = bl.load_case("mobile-booking")
    assert any("时段" in "".join(e["trigger"]) for e in case["events"])
    assert bl.extract_user_input("工作已完成\nUSER-INPUT: 需要支持多语言吗？") == "需要支持多语言吗？"
    assert bl.extract_user_input("完成，无问题。") is None


def test_result_payload_survives_cli_diagnostic_lines():
    stdout = ('[claude-code:unrecognized_model] {"model":"meta"}\n'
              '{"is_error":false,"result":"done","total_cost_usd":0.5,"terminal_reason":"completed"}')
    payload = bl.parse_result_payload(stdout)
    assert payload["result"] == "done" and payload["total_cost_usd"] == 0.5


def test_error_envelope_is_not_mistaken_for_model_output():
    envelope = ('{"is_error":true,"subtype":"error_max_turns","terminal_reason":"max_turns",'
                '"errors":["Reached maximum number of turns (60)"]}')
    payload = bl.parse_result_payload(envelope)
    assert payload["is_error"] is True
    assert payload.get("result") is None


def test_iteration_rollup_reads_assistant_tool_calls(tmp_path):
    # r24's T1 burned 61 iterations and only call-level aggregates survived;
    # the rollup exists so a max_turns exit answers "reading, writing, or
    # verifying" from the transcript rather than from guesswork.
    proj = tmp_path / "proj"
    proj.mkdir()
    rows = [
        {"type": "user", "message": {"content": "brief"}},
        {"type": "assistant", "timestamp": "2026-10-04T10:00:00Z", "message": {"stop_reason": "tool_use",
            "usage": {"output_tokens": 120},
            "content": [{"type": "tool_use", "name": "Read"},
                        {"type": "text", "text": "checking"}]}},
        {"type": "assistant", "message": {"stop_reason": "tool_use",
            "usage": {"output_tokens": 800},
            "content": [{"type": "tool_use", "name": "Write"}]}},
    ]
    (proj / "s-1.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    rollup = bl.iteration_rollup("s-1", config_root=tmp_path)
    assert [r["tools"] for r in rollup] == [["Read"], ["Write"]]
    assert rollup[0]["output_tokens"] == 120
    assert rollup[0]["ts"] == "2026-10-04T10:00:00Z"
    assert rollup[1]["ts"] is None
    assert bl.iteration_rollup("missing-session", config_root=tmp_path) == []


def test_matrix_runs_candidate_before_stable_control(tmp_path, monkeypatch):
    calls = []
    matrix = tmp_path / "matrix"
    monkeypatch.setattr(run_matrix.subprocess, "run", lambda cmd, **kwargs: (
        calls.append(cmd) or type("Completed", (), {"stderr": "", "returncode": 0})()))
    run_matrix._run_sessions(
        ["case"], ["stable_skill", "candidate_skill"], 1, matrix,
        type("Args", (), {
            "model": None, "max_turns": None, "timeout": None,
            "budget_usd": None, "task_trace": False, "max_task_steps": 8,
            "visual": False, "taste": False, "session_budget_usd": 5.0, "rejudge": False,
            "open": False,
        })(),
    )
    assert [cmd[cmd.index("--variant") + 1] for cmd in calls] == [
        "candidate_skill", "stable_skill"]


def test_unrecognized_model_error_is_not_auto_continued(tmp_path, monkeypatch):
    case = bl.load_case("incident-commander")
    calls = []
    monkeypatch.setattr(bl, "run_claude", lambda *args, **kwargs: (
        calls.append(kwargs) or {
            "status": "max_turns", "session_id": "session", "elapsed_s": 1,
            "cost_usd": 0.1, "models": [], "result": "", "is_error": True,
            "stderr": '[claude-code:unrecognized_model] {"model":"gemini"}',
        }))
    result = run_claude_session.run_session(
        case, "stable_skill", tmp_path, model=None, max_turns=4,
        timeout_s=30, budget_usd=1, session_budget_usd=4,
    )
    assert result["status"] == "BLOCKED"
    assert "CLI returned an error envelope" in result["note"]
    assert len(calls) == 1


def test_genuine_turn_cap_auto_continues(tmp_path, monkeypatch):
    case = bl.load_case("incident-commander")
    calls = []

    def mock_run(*args, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return {
                "status": "max_turns", "session_id": "session_cap", "elapsed_s": 20,
                "cost_usd": 1.0, "num_turns": 61, "result": "", "is_error": True,
                "errors": ["Reached maximum number of turns (60)"],
                "models": ["flash"],
                "stderr": '[claude-code:unrecognized_model] {"model":"flash"}',
            }
        (tmp_path / "prototype" / "experiments" / "anchor").mkdir(parents=True, exist_ok=True)
        (tmp_path / "prototype" / "experiments" / "anchor" / "index.html").write_text("<html></html>")
        return {
            "status": "completed", "session_id": "session_cap", "elapsed_s": 10,
            "cost_usd": 1.5, "num_turns": 15, "result": "Done with prototype",
            "is_error": False, "models": ["flash"], "stderr": "",
        }

    monkeypatch.setattr(bl, "run_claude", mock_run)
    result = run_claude_session.run_session(
        case, "candidate_skill", tmp_path, model="flash", max_turns=4,
        timeout_s=60, budget_usd=2.0, session_budget_usd=10.0,
    )
    assert len(calls) == 2
    assert calls[1]["resume"] == "session_cap"


def test_event_is_injected_after_turn_cap(tmp_path, monkeypatch):
    """A call that ends on the CLI turn cap must still get event injection."""
    case = bl.load_case("incident-commander")
    event = case["events"][0]
    trigger = event["trigger"][0]
    prompts = []

    def mock_run(prompt, *args, **kwargs):
        prompts.append(prompt)
        if len(prompts) == 1:
            return {
                "status": "max_turns", "session_id": "s", "elapsed_s": 5,
                "cost_usd": 0.5, "num_turns": 25, "is_error": True,
                "errors": ["Reached maximum number of turns (25)"],
                "models": ["flash"], "stderr": "",
                "result": "",
            }
        (tmp_path / "prototype" / "experiments" / "anchor").mkdir(parents=True, exist_ok=True)
        (tmp_path / "prototype" / "experiments" / "anchor" / "index.html").write_text("<html></html>")
        return {
            "status": "completed", "session_id": "s", "elapsed_s": 5,
            "cost_usd": 1.0, "num_turns": 5, "result": "done",
            "is_error": False, "models": ["flash"], "stderr": "",
        }

    monkeypatch.setattr(bl, "run_claude", mock_run)
    # A capped call has no payload result; the trigger is read from what the
    # call said, which the harness recovers from the transcript segment.
    monkeypatch.setattr(bl, "transcript_mark", lambda *a, **k: 0)
    monkeypatch.setattr(bl, "assistant_text_since",
                        lambda *a, **k: f"已梳理 {trigger} 的分级思路")
    result = run_claude_session.run_session(
        case, "candidate_skill", tmp_path, model="flash", max_turns=4,
        timeout_s=60, budget_usd=2.0, session_budget_usd=10.0,
    )
    assert prompts[1].startswith("（用户补充信息）")
    assert event["name"] in result["events_fired"]


def test_event_fires_from_written_record_when_chat_is_silent(tmp_path, monkeypatch):
    """A lean skill keeps substance in files; chat-only matching under-fires (r31, r33)."""
    case = bl.load_case("incident-commander")
    event = case["events"][0]
    trigger = event["trigger"][0]
    prompts = []

    def mock_run(prompt, *args, **kwargs):
        prompts.append(prompt)
        (tmp_path / "prototype" / "experiments" / "anchor").mkdir(parents=True, exist_ok=True)
        (tmp_path / "prototype" / "experiments" / "anchor" / "index.html").write_text("<html></html>")
        return {
            "status": "completed", "session_id": "s", "elapsed_s": 5, "cost_usd": 1.0,
            "num_turns": 5, "result": "已写入设计记录。", "is_error": False,
            "models": ["flash"], "stderr": "",
        }

    monkeypatch.setattr(bl, "run_claude", mock_run)
    monkeypatch.setattr(bl, "transcript_mark", lambda *a, **k: 0)
    monkeypatch.setattr(bl, "written_text_since", lambda *a, **k: f"## 张力\n{trigger} 决定首屏")
    result = run_claude_session.run_session(
        case, "candidate_skill", tmp_path, model="flash", max_turns=4,
        timeout_s=60, budget_usd=2.0, session_budget_usd=10.0,
    )
    assert prompts[1].startswith("（用户补充信息）")
    assert event["name"] in result["events_fired"]


def test_every_trigger_seen_in_one_call_is_injected_in_later_calls():
    """r34: all three triggers appeared in call 1, but only one event ever fired."""
    case = bl.load_case("incident-commander")
    events = [dict(e, fired=False) for e in case["events"]]
    mock = bl.parse_mock_user(case["mock_user"])
    everything = " ".join(e["trigger"][0] for e in events)

    fired = []
    for _ in range(4):
        prompt = run_claude_session._try_inject("已完成。", events, mock, also=everything)
        if prompt is None:
            break
        fired.append(prompt)
    assert len(fired) == 3
    assert all(e["fired"] for e in events)
    assert run_claude_session._try_inject("已完成。", events, mock, also="") is None


def test_an_unseen_trigger_never_fires():
    case = bl.load_case("incident-commander")
    events = [dict(e, fired=False) for e in case["events"]]
    mock = bl.parse_mock_user(case["mock_user"])
    assert run_claude_session._try_inject("没有相关词。", events, mock, also="") is None
    assert not any(e["fired"] for e in events)


def test_written_text_since_reads_only_file_writes_after_the_mark(tmp_path):
    import json as _json
    rows = [
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "input": {"content": "before-mark"}}]}},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "chat only"},
            {"type": "tool_use", "input": {"content": "written A", "file_path": "x"}},
            {"type": "tool_use", "input": {"new_string": "edited B"}},
            {"type": "tool_use", "input": {"command": "ls"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "content": "noise"}]}},
    ]
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "sid.jsonl").write_text("\n".join(_json.dumps(r) for r in rows), encoding="utf-8")
    out = bl.written_text_since("sid", 1, config_root=tmp_path)
    assert out == "written A\n\nedited B"


def test_task_outcomes_are_evidence_bound():
    task = {"id": "t", "required_outcomes": [
        {"id": "text", "check": "text_present", "pattern": "worker"},
        {"id": "dialog", "check": "dialog_open"},
        {"id": "scroll", "check": "no_horizontal_scroll"},
        {"id": "touch", "check": "min_touch_target", "px": 44},
    ]}
    trace = {"status": "completed", "steps": [{"action": "click"}], "snapshots": [
        {"text": "worker-07", "dialogs": 1, "scrollWidth": 400, "clientWidth": 400, "small_target_count": 0}]}
    result = task_judge.judge_task(task, trace)
    assert result["status"] == "pass"

    empty = task_judge.judge_task(task, {"status": "blocked", "steps": [], "snapshots": []})
    assert empty["status"] == "unverified"
    assert set(empty["unmet"]) == {"text", "dialog", "scroll", "touch"}


def test_runtime_judge_flags_inline_hex_and_missing_record(tmp_path):
    artifacts = tmp_path / "prototype"
    artifacts.mkdir()
    (artifacts / "index.html").write_text('<div style="color:#ff0000">drain</div>', encoding="utf-8")
    (artifacts / "tokens.css").write_text(":root{--bg-void:#0a0c10;--text-primary:#f5f5f5;}", encoding="utf-8")
    result = runtime_judge.judge(bl.load_case("incident-commander"), artifacts, variant="candidate_skill")
    assert result["status"] == "fail"
    assert "design_record_present" in result["failures"]
    assert "token_inheritance" in result["failures"]
    assert result["contrast"]["primary_text_on_bg"] > 4.5


def test_run_claude_pins_the_skill_home_to_the_session_workspace(tmp_path, monkeypatch):
    """Each variant must load the boundary shipped beside it, not the operator's.

    The Skill hook resolves `${LOOM_CLAUDE_HOME:-~/.claude}/skills/spec-prototype`.
    Left unset, that reaches the operator's `~/.claude`, which is commonly a
    symlink to the live repo skill -- a stable-variant session then runs the
    candidate boundary against baseline docs and deadlocks.
    """
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["env"] = kwargs.get("env", {})
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps({"result": "ok", "total_cost_usd": 0.0}), stderr="")

    monkeypatch.setattr(bl.subprocess, "run", fake_run)
    bl.run_claude("prompt", tmp_path, max_turns=1)

    assert captured["env"]["LOOM_CLAUDE_HOME"] == str(tmp_path / ".claude")


def test_regression_judge_requires_a_paired_control():
    empty = regression_judge.judge([])
    assert empty["verdict"] == "INCONCLUSIVE"
    runs = [
        {"case_id": "c", "variant": "stable_skill", "repeat": 1, "runtime": {"status": "pass"},
         "semantic": {"hard_gate": "pass"}, "task": {"status": "pass"}},
        {"case_id": "c", "variant": "candidate_skill", "repeat": 1, "runtime": {"status": "fail"},
         "semantic": {"hard_gate": "pass"}, "task": {"status": "pass"}},
    ]
    verdict = regression_judge.judge(runs)
    assert verdict["verdict"] == "REGRESSION"
    assert verdict["regressions"][0]["dimension"] == "runtime"


def test_session_prompt_carries_no_hidden_case_inputs():
    case = bl.load_case("incident-commander")
    template = bl.prompt_template("skill-run.txt")
    prompt = bl.render(template, brief=case["brief"], protocol=bl.prompt_template("protocol.txt"))
    for forbidden in ("ground_truth", "unsupported_assumptions", "must_consider", "rubric"):
        assert forbidden not in prompt


def test_evidence_protocol_accepts_chinese_markers(tmp_path):
    root = tmp_path / "artifacts"
    root.mkdir()
    (root / "discussion.md").write_text("# 决策记录\n用户明确要求集群下线前必须二次会签。\n实际观测错误率超标。\n", encoding="utf-8")
    (root / "index.html").write_text("<html><body>Test</body></html>", encoding="utf-8")
    (root / "tokens.css").write_text(":root {}", encoding="utf-8")
    case = bl.load_case("incident-commander")
    result = runtime_judge.judge(case, root, variant="candidate_skill")
    check = next(c for c in result["checks"] if c["id"] == "evidence_protocol")
    assert check["status"] == "pass"


def test_aggregate_report_blocks_promotion_on_a_hard_gate(tmp_path):
    run_dir = tmp_path / "c" / "candidate_skill" / "run1"
    run_dir.mkdir(parents=True)
    bl.write_json(run_dir / "run-result.json", {
        "case_id": "c", "variant": "candidate_skill", "repeat": 1, "status": "FAIL", "metrics": {},
        "runtime": {"checks": [{"id": "token_inheritance", "status": "pass"}], "authority_escape": True},
        "semantic": {"hard_gate": "fail", "fabricated_capabilities": 1}, "task": None})
    report = aggregate_report.build(tmp_path, "custom", "test")
    assert report["hard_gates"]["semantic_fabrication"] == 1
    assert report["hard_gates"]["authority_escape"] == 1
    assert report["status"] == "REGRESSION"
    assert "task behaviour unverified" in " ".join(report["unverified"])


def _complete_skill(root):
    (root / "references").mkdir(parents=True, exist_ok=True)
    (root / "templates").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text("skill", encoding="utf-8")
    (root / "CONTEXT.md").write_text("context", encoding="utf-8")
    (root / "references/core-kernel.md").write_text("kernel", encoding="utf-8")
    (root / "templates/slice.md").write_text("t", encoding="utf-8")
    return root


def test_incomplete_skill_source_is_refused_and_named(tmp_path, monkeypatch):
    monkeypatch.setattr(bl, "ROOT", tmp_path)
    monkeypatch.setattr(bl, "WORKSPACE_ROOT", tmp_path / "ws")
    complete = _complete_skill(tmp_path / "skills/spec-prototype")
    assert bl.variant_sources("candidate_skill")["skill"] == complete

    missing = {"SKILL.md": "SKILL.md", "CONTEXT.md": "CONTEXT.md",
               "references/core-kernel.md": "references/core-kernel.md"}
    for name, rel in missing.items():
        complete.joinpath(rel).unlink()
        with pytest.raises(bl.BenchBlocked) as excinfo:
            bl.variant_sources("candidate_skill")
        message = str(excinfo.value)
        assert str(complete) in message and name in message, message
        _complete_skill(tmp_path / "skills/spec-prototype")

    # A templates/ dir with no file member is not a template set.
    (tmp_path / "skills/spec-prototype/templates/slice.md").unlink()
    with pytest.raises(bl.BenchBlocked) as excinfo:
        bl.prepare_workspace(bl.load_case("editorial-reader"), "candidate_skill", "r1")
    assert "templates/*" in str(excinfo.value)
    assert not (tmp_path / "ws").exists(), "refusal must precede workspace mutation"

    # A complete source still prepares a workspace whose SKILL.md is a regular file.
    _complete_skill(tmp_path / "skills/spec-prototype")
    workspace = bl.prepare_workspace(bl.load_case("editorial-reader"), "candidate_skill", "r2")
    copied = workspace / ".claude/skills/spec-prototype/SKILL.md"
    assert copied.is_file() and not copied.is_symlink()


def test_truncated_and_absent_baselines_fail_named(tmp_path, monkeypatch):
    def write_manifest(base):
        base.mkdir(parents=True, exist_ok=True)
        bl.write_json(base / "MANIFEST.json", {"tag": bl.STABLE_TAG, "git_rev": "unknown",
                                               "hashes": {}})

    absent = tmp_path / bl.STABLE_TAG
    absent.mkdir()
    monkeypatch.setattr(bl, "BASELINES_DIR", tmp_path)
    with pytest.raises(bl.BenchBlocked) as excinfo:
        bl.ensure_baseline()
    assert "MANIFEST.json" in str(excinfo.value) and str(absent) in str(excinfo.value)

    truncated = tmp_path / bl.STABLE_TAG
    write_manifest(truncated)
    skill = truncated / "skills/spec-prototype"
    skill.mkdir(parents=True)
    (skill / "CONTEXT.md").write_text("only one file", encoding="utf-8")
    with pytest.raises(bl.BenchBlocked) as excinfo:
        bl.ensure_baseline()
    message = str(excinfo.value)
    assert str(skill) in message and "SKILL.md" in message, message


def test_no_skill_variant_resolves_without_a_skill():
    assert bl.variant_sources("no_skill") == {"skill": None, "agents": None}


def test_frozen_baseline_restores_from_its_recorded_rev(tmp_path, monkeypatch):
    """The baseline tree is git-ignored derived data: it must rebuild, verified, from MANIFEST.json."""
    base = bl.BASELINES_DIR / bl.STABLE_TAG
    manifest = bl.read_json(base / "MANIFEST.json")
    assert manifest["git_rev"] and manifest["git_rev"] != "unknown", "baseline records no rev to restore from"
    assert manifest["hashes"], "baseline records no per-file hashes to verify against"

    # Restore into a scratch copy so the real cache is untouched.
    scratch = tmp_path / bl.STABLE_TAG
    scratch.mkdir()
    (scratch / "MANIFEST.json").write_text((base / "MANIFEST.json").read_text(), encoding="utf-8")
    monkeypatch.setattr(bl, "BASELINES_DIR", tmp_path)

    restored = bl.ensure_baseline()
    skill = restored / "skills/spec-prototype"
    assert (skill / "SKILL.md").is_file()
    for rel, meta in manifest["hashes"].items():
        assert bl.sha256_file(skill / rel) == meta["sha256"], f"restored {rel} does not match MANIFEST"

    # A tampered cache must be detected and rebuilt, never used as the control condition.
    target = skill / "SKILL.md"
    good = target.read_text(encoding="utf-8")
    target.write_text(good + "\n<!-- tampered -->\n", encoding="utf-8")
    assert target.read_text(encoding="utf-8") != good
    bl.ensure_baseline()
    assert target.read_text(encoding="utf-8") == good, "tampered baseline was reused instead of rebuilt"



def _frozen_baseline_fixture(tmp_path, git_rev="unknown"):
    """A baseline whose manifest pins every file the cached tree actually carries."""
    base = tmp_path / bl.STABLE_TAG
    skill = _complete_skill(base / "skills/spec-prototype")
    hashes = {rel: {"sha256": bl.sha256_file(skill / rel)}
              for rel in bl.skill_contract_gaps(skill) or _skill_files(skill)}
    if not hashes:
        hashes = {str(p.relative_to(skill)): {"sha256": bl.sha256_file(p)}
                  for p in sorted(skill.rglob("*")) if p.is_file()}
    bl.write_json(base / "MANIFEST.json",
                  {"tag": bl.STABLE_TAG, "git_rev": git_rev, "hashes": hashes})
    return base, skill


def _skill_files(skill):
    return sorted(str(p.relative_to(skill)) for p in skill.rglob("*") if p.is_file())


def test_cached_baseline_is_held_to_the_integrity_contract(tmp_path, monkeypatch):
    """A cached tree is guarded by its shape, not by an empty hash map."""
    base = tmp_path / bl.STABLE_TAG
    skill = base / "skills/spec-prototype"
    skill.mkdir(parents=True)
    (skill / "CONTEXT.md").write_text("only one file", encoding="utf-8")
    bl.write_json(base / "MANIFEST.json", {"tag": bl.STABLE_TAG, "git_rev": "unknown", "hashes": {}})
    monkeypatch.setattr(bl, "BASELINES_DIR", tmp_path)
    with pytest.raises(bl.BenchBlocked) as excinfo:
        bl.ensure_baseline()
    message = str(excinfo.value)
    assert str(skill) in message and "SKILL.md" in message, message


def test_malformed_hash_entry_is_a_named_divergence(tmp_path, monkeypatch):
    """An unreadable hash entry is refused as a divergence, never a KeyError."""
    # A present-but-unreadable entry must be named before the tree is discarded for rebuild.
    real_rev = bl.read_json(bl.BASELINES_DIR / bl.STABLE_TAG / "MANIFEST.json")["git_rev"]
    base, _ = _frozen_baseline_fixture(tmp_path, git_rev=real_rev)
    bl.write_json(base / "MANIFEST.json", {"tag": bl.STABLE_TAG, "git_rev": real_rev,
                                           "hashes": {"SKILL.md": "not-a-mapping"}})
    monkeypatch.setattr(bl, "BASELINES_DIR", tmp_path)
    with pytest.raises(bl.BenchBlocked) as excinfo:
        bl.ensure_baseline()
    message = str(excinfo.value)
    assert "SKILL.md" in message and "diverge" in message, message


def test_valid_cached_baseline_still_resolves(tmp_path, monkeypatch):
    base, skill = _frozen_baseline_fixture(tmp_path)
    monkeypatch.setattr(bl, "BASELINES_DIR", tmp_path)
    assert bl.ensure_baseline() == base
    assert (skill / "SKILL.md").is_file()


def test_incomplete_restored_baseline_is_refused(tmp_path, monkeypatch):
    """A recorded revision that revives an incomplete tree is refused, not adopted."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        data = b"skill"
        info = tarfile.TarInfo("skills/spec-prototype/SKILL.md")
        info.size = len(data)
        tf.addfile(info, io.BytesIO(data))
    archive = buf.getvalue()

    base = tmp_path / bl.STABLE_TAG
    base.mkdir()
    bl.write_json(base / "MANIFEST.json", {"tag": bl.STABLE_TAG, "git_rev": "0" * 40, "hashes": {}})
    monkeypatch.setattr(bl, "BASELINES_DIR", tmp_path)
    monkeypatch.setattr(bl.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, archive, b""))
    with pytest.raises(bl.BenchBlocked) as excinfo:
        bl.ensure_baseline()
    message = str(excinfo.value)
    assert "restored" in message and "CONTEXT.md" in message, message


def _transcript(config_root: pathlib.Path, session_id: str, records) -> pathlib.Path:
    d = config_root / "some-project"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{session_id}.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return p


def test_transcript_estimate_reads_the_recorded_cli_cost(tmp_path):
    # The transcript's totalCostUSD is the CLI's own receipt. Token heuristics
    # were measured against a real session and are not defensible: summing every
    # usage record over-bills a resumed session, and pricing only the largest
    # request under-bills it by an order of magnitude.
    sid = "s-recorded"
    _transcript(tmp_path, sid, [
        {"totalCostUSD": 0.5, "message": {"role": "assistant", "model": "flash",
                                          "usage": {"input_tokens": 1000, "output_tokens": 50}}},
        {"type": "file-history-delta", "totalCostUSD": None},
        {"totalCostUSD": 3.25, "message": {"role": "assistant", "model": "flash",
                                           "usage": {"input_tokens": 9000, "output_tokens": 70}}},
    ])
    assert bl.estimate_cost_from_transcript(sid, config_root=tmp_path) == 3.25


def test_transcript_estimate_stays_none_when_no_cost_was_recorded(tmp_path):
    # A hard timeout mid-turn writes usage but no terminal cost. Missing
    # evidence stays missing — never a token-derived guess, never $0.
    sid = "s-no-receipt"
    _transcript(tmp_path, sid, [
        {"message": {"role": "assistant", "model": "flash",
                     "usage": {"input_tokens": 9000, "output_tokens": 70}}},
    ])
    assert bl.estimate_cost_from_transcript(sid, config_root=tmp_path) is None


def test_transcript_estimate_stays_none_without_a_transcript(tmp_path):
    assert bl.estimate_cost_from_transcript("missing-session", config_root=tmp_path) is None


def test_estimated_cumulative_cost_replaces_rather_than_adds_to_the_total():
    # CLI totalCostUSD is cumulative; resume turns ratchet to the latest figure.
    # Timed-out calls bound the spend by adding the per-turn budget as an upper bound.
    src = (pathlib.Path(bl.__file__).parent / "run_claude_session.py").read_text(encoding="utf-8")
    assert "if out.get(\"cost_estimated\"):" in src
    assert "total_cost = max(total_cost, call_cost) + timeout_bound" in src
    assert "total_cost = max(total_cost, call_cost)" in src

def test_early_calls_get_a_share_of_the_clock_and_the_last_gets_the_rest():
    # r35: call 1 took 1343s of 3000s and the session died with Turn 4 stranded.
    assert run_claude_session._call_timeout(0, 3000, 3000) == (1200, True)
    assert run_claude_session._call_timeout(1, 1800, 3000) == (900, True)
    assert run_claude_session._call_timeout(2, 900, 3000) == (900, False)
    # A share larger than what is left is simply the remainder.
    assert run_claude_session._call_timeout(0, 500, 3000) == (500, False)


def test_a_call_that_exhausts_its_share_resumes_instead_of_blocking(tmp_path, monkeypatch):
    case = bl.load_case("incident-commander")
    calls = []

    def mock_run(prompt, *args, **kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return {"status": "timeout", "session_id": "s", "elapsed_s": kwargs["timeout_s"],
                    "cost_usd": 0.5, "cost_estimated": True, "result": "", "models": [],
                    "stderr": "timeout"}
        (tmp_path / "prototype").mkdir(exist_ok=True)
        (tmp_path / "prototype" / "index.html").write_text("<html></html>")
        return {"status": "completed", "session_id": "s", "elapsed_s": 5, "cost_usd": 1.0,
                "result": "done", "is_error": False, "models": [], "stderr": ""}

    monkeypatch.setattr(bl, "run_claude", mock_run)
    result = run_claude_session.run_session(
        case, "candidate_skill", tmp_path, model=None, max_turns=4,
        timeout_s=1000, budget_usd=2.0, session_budget_usd=10.0)
    assert result["status"] == "COMPLETED"
    assert len(calls) == 2
    assert calls[0]["timeout_s"] <= 400
    assert calls[1]["resume"] == "s"


def test_session_clock_exhaustion_with_a_prototype_is_partial_not_blocked(tmp_path, monkeypatch):
    case = bl.load_case("incident-commander")
    (tmp_path / "prototype").mkdir()
    (tmp_path / "prototype" / "index.html").write_text("<html></html>")
    monkeypatch.setattr(bl, "run_claude", lambda *a, **k: {
        "status": "timeout", "session_id": "s", "elapsed_s": 1, "cost_usd": 0.1,
        "cost_estimated": True, "result": "", "models": [], "stderr": "timeout"})
    monkeypatch.setattr(run_claude_session, "CALL_WALL_CLOCK_SHARE", ())
    result = run_claude_session.run_session(
        case, "candidate_skill", tmp_path, model=None, max_turns=4,
        timeout_s=60, budget_usd=2.0, session_budget_usd=10.0)
    assert result["status"] == "PARTIAL"
    assert result["blocked_reason"] == "wall_clock"


def test_a_cli_error_envelope_stays_blocked_even_with_a_prototype(tmp_path, monkeypatch):
    case = bl.load_case("incident-commander")
    (tmp_path / "prototype").mkdir()
    (tmp_path / "prototype" / "index.html").write_text("<html></html>")
    monkeypatch.setattr(bl, "run_claude", lambda *a, **k: {
        "status": "error", "session_id": "s", "elapsed_s": 1, "cost_usd": 0.1,
        "result": "", "models": [], "stderr": "boom"})
    result = run_claude_session.run_session(
        case, "candidate_skill", tmp_path, model=None, max_turns=4,
        timeout_s=60, budget_usd=2.0, session_budget_usd=10.0)
    assert result["status"] == "BLOCKED"


def test_each_turn_records_only_its_own_iterations(tmp_path, monkeypatch):
    case = bl.load_case("incident-commander")
    calls = []

    def mock_run(prompt, *args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            return {"status": "max_turns", "session_id": "s", "elapsed_s": 1, "cost_usd": 0.1,
                    "num_turns": 3, "is_error": True, "result": "", "models": [], "stderr": "",
                    "errors": ["Reached maximum number of turns (2)"],
                    "iterations": [{"tools": ["Read"]}, {"tools": ["Write"]}]}
        (tmp_path / "prototype").mkdir(exist_ok=True)
        (tmp_path / "prototype" / "index.html").write_text("<html></html>")
        return {"status": "completed", "session_id": "s", "elapsed_s": 1, "cost_usd": 0.2,
                "result": "done", "is_error": False, "models": [], "stderr": "",
                "iterations": [{"tools": ["Read"]}, {"tools": ["Write"]}, {"tools": ["Bash"]}]}

    monkeypatch.setattr(bl, "run_claude", mock_run)
    result = run_claude_session.run_session(
        case, "candidate_skill", tmp_path, model=None, max_turns=4,
        timeout_s=1000, budget_usd=2.0, session_budget_usd=10.0)
    assert [len(t["iterations"]) for t in result["turns"]] == [2, 1]


def test_auto_continue_carries_the_agents_recorded_next_action(tmp_path):
    (tmp_path / "prototype").mkdir()
    (tmp_path / "prototype" / "discussion.md").write_text(
        "## Resume\n\n- Active slice: `x`\n- Next action and its prerequisite: 进入 Make 写 tokens.css\n")
    prompt = run_claude_session._auto_continue_prompt(tmp_path)
    assert "进入 Make 写 tokens.css" in prompt
    assert run_claude_session._auto_continue_prompt(tmp_path / "none").startswith("继续。")


def test_iteration_rollup_reports_input_and_cache_usage(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    row = {"type": "assistant", "message": {"stop_reason": "tool_use", "content": [],
           "usage": {"output_tokens": 5, "input_tokens": 7, "cache_read_input_tokens": 900,
                     "cache_creation_input_tokens": 40}}}
    (proj / "s-2.jsonl").write_text(json.dumps(row), encoding="utf-8")
    r = bl.iteration_rollup("s-2", config_root=tmp_path)[0]
    assert (r["input_tokens"], r["cache_read_input_tokens"], r["cache_creation_input_tokens"]) == (7, 900, 40)

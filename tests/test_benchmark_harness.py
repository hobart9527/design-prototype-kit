"""Hermetic checks for the automated benchmark harness (no network, no LLM, no browser)."""
import json
import pathlib
import sys

import jsonschema
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import bench_lib as bl  # noqa: E402
import aggregate_report  # noqa: E402
import regression_judge  # noqa: E402
import run_claude_session  # noqa: E402
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

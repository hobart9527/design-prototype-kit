"""Hermetic checks for critical-gate acceptance and candidate provenance (CPC-008 / CPC-SCN-017).

No network, no LLM, no browser, no paid benchmark: every input is a synthetic run record.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import bench_lib as bl  # noqa: E402
import aggregate_report  # noqa: E402
import run_case  # noqa: E402


def _run(**overrides) -> dict:
    run = {"case_id": "c", "variant": "candidate_skill", "repeat": 1, "status": "PASS",
           "metrics": {}, "runtime": {"checks": []}, "semantic": {"hard_gate": "pass"},
           "task": None, "provenance": None}
    run.update(overrides)
    return run


def _write_run(matrix_dir: pathlib.Path, run: dict) -> None:
    run_dir = matrix_dir / run["case_id"] / run["variant"] / f"run{run['repeat']}"
    run_dir.mkdir(parents=True, exist_ok=True)
    bl.write_json(run_dir / "run-result.json", run)


def test_critical_accessibility_violation_blocks_aggregate_acceptance(tmp_path):
    """Contrast is a declared critical gate: alone, with nothing else failing, it must block."""
    _write_run(tmp_path, _run(runtime={
        "checks": [{"id": "contrast_primary_text", "status": "fail"},
                   {"id": "token_inheritance", "status": "pass"}]}))
    report = aggregate_report.build(tmp_path, "custom", "test")
    assert report["hard_gates"]["critical_accessibility_violation"] == 1
    assert report["status"] == "REGRESSION"


def test_failed_touch_targets_also_count_as_a_critical_accessibility_violation(tmp_path):
    _write_run(tmp_path, _run(task={"status": "pass", "critical_task_break": False, "tasks": [
        {"id": "t", "required_outcomes": [
            {"id": "touch_targets", "status": "fail"},
            {"id": "text", "status": "pass"}]}]}))
    report = aggregate_report.build(tmp_path, "custom", "test")
    assert report["hard_gates"]["critical_accessibility_violation"] == 1
    assert report["status"] == "REGRESSION"


def test_absent_accessibility_evidence_stays_unverified_not_a_pass(tmp_path):
    """No checks recorded is missing evidence, not a clean bill of health."""
    _write_run(tmp_path, _run(runtime=None))
    report = aggregate_report.build(tmp_path, "custom", "test")
    assert report["hard_gates"]["critical_accessibility_violation"] == 0
    assert report["status"] == "INCONCLUSIVE"


def test_changed_candidate_bytes_change_identity_and_unchanged_content_stays_stable(tmp_path):
    tree = tmp_path / "skill"
    tree.mkdir()
    (tree / "SKILL.md").write_text("v1\n", encoding="utf-8")
    (tree / "scripts").mkdir()
    (tree / "scripts" / "run.py").write_text("print(1)\n", encoding="utf-8")
    first = bl.tree_identity(tree)
    assert first["file_count"] == 2 and first["aggregate_sha256"]

    assert bl.tree_identity(tree)["aggregate_sha256"] == first["aggregate_sha256"], \
        "unchanged content must produce a stable identity"

    (tree / "scripts" / "run.py").write_text("print(2)\n", encoding="utf-8")
    second = bl.tree_identity(tree)
    assert second["aggregate_sha256"] != first["aggregate_sha256"], \
        "a dirty candidate must not hash as its previous content"
    assert second["file_count"] == 2


def test_source_identity_excludes_secrets_and_unrelated_files(tmp_path):
    tree = tmp_path / "skill"
    (tree / "scripts").mkdir(parents=True)
    (tree / "SKILL.md").write_text("skill\n", encoding="utf-8")
    (tree / ".env").write_text("ANTHROPIC_API_KEY=sk-secret\n", encoding="utf-8")
    (tree / "scripts" / "credentials.json").write_text('{"token":"secret"}\n', encoding="utf-8")
    (tree / "__pycache__").mkdir()
    (tree / "__pycache__" / "SKILL.md").write_text("bytecode-ish\n", encoding="utf-8")
    (tree / "SKILL.md.bak").write_text("unrelated\n", encoding="utf-8")

    identity = bl.tree_identity(tree)
    assert set(identity["files"]) == {"SKILL.md"}, identity["files"]
    assert ".env" in identity["excluded"] and "scripts/credentials.json" in identity["excluded"]
    blob = json.dumps(identity)
    assert "sk-secret" not in blob and "ANTHROPIC_API_KEY" not in blob, \
        "identity must never carry secret material"


def test_judge_identity_tracks_stored_evidence_and_ignores_archived_results(tmp_path):
    _write_run(tmp_path, {"case_id": "c", "variant": "candidate_skill", "repeat": 1, "status": "PASS"})
    assert bl.judge_identity(tmp_path)["aggregate_sha256"] is None
    (tmp_path / "artifacts-manifest.json").write_text('{"counts": {}}', encoding="utf-8")
    first = bl.judge_identity(tmp_path)
    assert first["file_count"] == 1
    # Prior results live beside the new one; hashing them would make every re-judge look changed.
    (tmp_path / "run-result.json").write_text('{"status": "PASS"}', encoding="utf-8")
    (tmp_path / "run-result-prev1.json").write_text('{"status": "FAIL"}', encoding="utf-8")
    assert bl.judge_identity(tmp_path) == first


def test_legacy_missing_provenance_is_disclosed_not_invented(tmp_path):
    _write_run(tmp_path, _run())
    report = aggregate_report.build(tmp_path, "custom", "test")
    provenance = report["provenance"]
    assert provenance["runs_with_provenance"] == 0
    assert provenance["runs_missing_provenance"] == 1
    assert provenance["missing"] == ["c/candidate_skill"]
    assert "unknown" in provenance["disclosure"]
    assert provenance["source_identity"] == []
    assert "Candidate provenance" in aggregate_report.render_markdown(report)


def test_recorded_provenance_is_reported_and_absent_when_runs_disagree(tmp_path):
    _write_run(tmp_path, _run(provenance={"aggregate_sha256": "a" * 64,
                                           "candidate": {"aggregate_sha256": "a" * 64}}))
    report = aggregate_report.build(tmp_path, "custom", "test")
    assert report["provenance"]["runs_missing_provenance"] == 0
    assert report["provenance"]["identical_across_runs"] is True

    _write_run(tmp_path, _run(repeat=2, provenance={"aggregate_sha256": "b" * 64,
                                                    "candidate": {"aggregate_sha256": "b" * 64}}))
    disagreeing = aggregate_report.build(tmp_path, "custom", "test")
    assert disagreeing["provenance"]["identical_across_runs"] is False
    assert disagreeing["provenance"]["source_identity"] == ["a" * 64, "b" * 64]


def test_pairwise_summary_discloses_agreement_and_missing_judge_cost(tmp_path):
    _write_run(tmp_path, _run())
    pair_dir = tmp_path / "pairwise" / "c-stable-vs-candidate"
    pair_dir.mkdir(parents=True)
    bl.write_json(pair_dir / "result.json", {
        "case_id": "c", "pair": "candidate_skill_vs_stable_skill", "status": "judged",
        "result": {"overall_preference": "alpha", "confidence": "high"},
        "metrics": {"cost_usd": 0.12},
    })
    unverified_dir = tmp_path / "pairwise" / "c-no-skill-vs-stable"
    unverified_dir.mkdir(parents=True)
    bl.write_json(unverified_dir / "result.json", {
        "case_id": "c", "pair": "no_skill_vs_stable_skill", "status": "unverified",
        "metrics": {},
    })

    report = aggregate_report.build(tmp_path, "custom", "test")
    metrics = report["metrics"]
    assert metrics["pairwise_agreement"] == 1.0
    assert metrics["pairwise_confidence_counts"] == {"low": 0, "medium": 0, "high": 1}
    assert metrics["pairwise_cost_usd"] == 0.12
    assert metrics["pairwise_cost_recorded"] == 1
    assert metrics["pairwise_cost_missing"] == 1
    assert metrics["pairwise_cost_total_complete"] is False
    markdown = aggregate_report.render_markdown(report)
    assert "not statistical confidence" in markdown
    assert "1 recorded; 1 missing" in markdown
    assert "total spend is incomplete" in markdown


def test_deterministic_rejudge_retains_evidence_and_versions_judges(tmp_path, monkeypatch):
    case_id = "incident-commander"
    matrix = tmp_path / "matrix"
    out = matrix / case_id / "candidate_skill" / "run1"
    artifacts = out / "artifacts" / "prototype"
    artifacts.mkdir(parents=True)
    (artifacts / "index.html").write_text('<html lang="zh"><p>业务已上线</p></html>')
    bl.write_json(out / "artifacts-manifest.json", {
        "artifacts_dir": str(out / "artifacts"), "entry": "index.html",
        "hashes": {"index.html": {"sha256": bl.sha256_file(artifacts / "index.html")}},
    })
    prior = {"status": "PASS", "provenance": {"aggregate_sha256": "original"},
             "session": {"status": "COMPLETED"}, "metrics": {"cost_usd": 1.5},
             "semantic": {"hard_gate": "pass"}, "task": {"critical_task_break": 0},
             "visual": {"status": "captured"}, "taste": None}
    bl.write_json(out / "run-result.json", prior)
    sentinel = {"status": "FAIL", "notes": ["older result"]}
    bl.write_json(out / "run-result-prev1.json", sentinel)

    def forbidden(*args, **kwargs):
        raise AssertionError("deterministic rejudge must not rerun models, browser or tasks")

    monkeypatch.setattr(run_case.semantic_judge, "judge", forbidden)
    monkeypatch.setattr(run_case.visual_manifest, "capture", forbidden)
    monkeypatch.setattr(run_case.run_task_trace, "run_task", forbidden)
    monkeypatch.setattr(run_case.taste_judge, "judge", forbidden)
    result = run_case.run_one(case_id, "candidate_skill", 1, matrix, model=None,
                              max_turns=1, timeout_s=1, budget_usd=0,
                              do_task_trace=True, max_task_steps=1, do_visual=True,
                              do_taste=True, rejudge=True, deterministic_only=True)
    assert bl.read_json(out / "run-result-prev1.json") == sentinel
    assert bl.read_json(out / "run-result-prev2.json") == prior
    assert result["provenance"] == prior["provenance"]
    for key in ("semantic", "task", "visual", "taste"):
        assert result[key] == prior[key]
    assert not any("judge error" in note or "trace error" in note for note in result["notes"])
    evaluation = result["evaluation_provenance"]
    assert evaluation["mode"] == "deterministic_rejudge"
    assert evaluation["judge_sources"]["aggregate_sha256"]
    report = aggregate_report.build(matrix, "daily", "rejudged")
    assert report["runs"][0]["evaluation_provenance"] == evaluation
    assert "retained (not rerun)" in aggregate_report.render_markdown(report)
    assert any("authority_status unknown" in item for item in report["unverified"])
    assert any("visual taste not measured" in item for item in report["unverified"])
    (artifacts / "index.html").write_text("changed artifact")
    blocked = run_case.run_one(case_id, "candidate_skill", 1, matrix, model=None,
                               max_turns=1, timeout_s=1, budget_usd=0,
                               do_task_trace=False, max_task_steps=1, do_visual=False,
                               rejudge=True, deterministic_only=True)
    assert blocked["status"] == "BLOCKED"
    assert blocked["task"] is None
    assert "unchanged artifacts" in blocked["notes"][-1]


def test_prior_run_result_is_archived_not_overwritten(tmp_path, monkeypatch):
    """Re-judging keeps the previous evidence as run-result-prev<N>.json instead of erasing it."""
    case_id = sorted(bl.case_paths())[0]
    matrix_dir = tmp_path / "matrix"
    out_dir = matrix_dir / case_id / "candidate_skill" / "run1"
    out_dir.mkdir(parents=True)
    prior = {"case_id": case_id, "variant": "candidate_skill", "repeat": 1,
             "status": "PASS", "metrics": {"cost_usd": 1.5}, "provenance": {"aggregate_sha256": "c" * 64}}
    bl.write_json(out_dir / "run-result.json", prior)

    result = run_case.run_one(case_id, "candidate_skill", 1, matrix_dir, model=None,
                              max_turns=1, timeout_s=1, budget_usd=0.0, do_task_trace=False,
                              max_task_steps=1, do_visual=False, rejudge=True)

    archived = sorted(out_dir.glob("run-result-prev*.json"))
    assert len(archived) == 1, "the previous result must be preserved"
    assert bl.read_json(archived[0])["metrics"]["cost_usd"] == 1.5
    assert result["status"] == "BLOCKED"
    assert bl.read_json(out_dir / "run-result.json")["status"] == "BLOCKED"

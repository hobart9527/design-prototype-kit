"""Hard-gate honesty: the authority gate reads claims, not vocabulary (BENCH-004).

The gate this covers previously scanned every artifact for the bare token
`frozen`, so a skill that emitted its own template's artifact-lifecycle enum
(`draft | frozen | superseded`) failed for the words in its boilerplate while a
manifest that really did claim frozen authority was caught only by accident.
Hermetic: no network, no LLM, no browser, no paid judge call.
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
import runtime_judge  # noqa: E402
import semantic_judge  # noqa: E402

CASE = "editorial-reader"  # ceiling is sealed_provisional


def _artifact(root: pathlib.Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _judge(root: pathlib.Path) -> dict:
    return runtime_judge.judge(bl.load_case(CASE), root, variant="candidate_skill")


def _escape(root: pathlib.Path) -> bool:
    return bool(_judge(root)["authority_escape"])


def _base(root: pathlib.Path) -> None:
    """A run that holds at sealed provisional and claims nothing further."""
    _artifact(root, "prototype/discussion.md", "# Discussion\n" + "x" * 300 + "\n")
    _artifact(root, "prototype/specifications/reader/r1.md",
              "- Compilation status: sealed provisional\n- Authority status: sealed provisional\n")


def test_contract_lifecycle_status_is_not_an_authority_claim(tmp_path):
    """`Status: frozen` on a tokens/contract artifact is its own lifecycle, not authority."""
    _base(tmp_path)
    _artifact(tmp_path, "prototype/contracts/tokens/t1.md",
              "# Design Tokens\n- Status: frozen\n")
    assert _escape(tmp_path) is False


def test_plan_wording_naming_a_later_stage_is_not_a_claim(tmp_path):
    """Prose scheduling a future Stage 5 is a plan, not an assertion of frozen authority."""
    _base(tmp_path)
    _artifact(tmp_path, "prototype/discussion.md",
              "# Discussion\n- Stopping point: Stage 5 frozen handoff\n" + "x" * 300 + "\n")
    assert _escape(tmp_path) is False


def test_specification_asserting_frozen_authority_without_approval_is_an_escape(tmp_path):
    """The same token where it *is* an authority claim must still be refused."""
    _artifact(tmp_path, "prototype/discussion.md", "# Discussion\n" + "x" * 300 + "\n")
    _artifact(tmp_path, "prototype/specifications/reader/r1.md",
              "- Compilation status: frozen\n- Authority status: frozen approved\n")
    detail = next(c for c in _judge(tmp_path)["checks"] if c["id"] == "authority_status")
    assert _escape(tmp_path) is True
    assert "unbacked_freeze=True" in detail["detail"]


def test_freeze_manifest_declaring_frozen_approved_without_approval_is_an_escape(tmp_path):
    """A manifest that asserts frozen_approved while recording no approval is the real escape."""
    _base(tmp_path)
    _artifact(tmp_path, "prototype/evidence/reader/r1/freeze-manifest.json",
              json.dumps({"status": "frozen", "authority_status": "frozen_approved",
                          "approval": None}))
    assert _escape(tmp_path) is True


def test_scoping_does_not_silence_a_forbidden_claim(tmp_path):
    """Narrowing the stage scan must not narrow the forbidden-claim scan with it."""
    _base(tmp_path)
    _artifact(tmp_path, "prototype/product.md", "# Product\n用户已确认 this shipped\n")
    assert _escape(tmp_path) is True


def test_gate_on_the_control_arm_is_not_reported_as_a_candidate_regression(tmp_path):
    """A broken control makes the run unusable; it is not evidence the candidate regressed."""
    run = {"case_id": "c", "variant": "stable_skill", "repeat": 1, "status": "FAIL",
           "metrics": {}, "runtime": {"checks": [], "authority_escape": True},
           "semantic": {"hard_gate": "pass"}, "task": None, "provenance": None}
    out = tmp_path / "c" / "stable_skill" / "run1"
    out.mkdir(parents=True)
    bl.write_json(out / "run-result.json", run)

    report = aggregate_report.build(tmp_path, "custom", "test")

    assert report["status"] == "INVALID_CONTROL"
    assert report["hard_gate_arms"] == ["stable_skill"]
    assert "stable_skill" in report["status_divergence"]


def test_report_discloses_a_gate_that_the_paired_verdict_does_not_show(tmp_path):
    """Top-line status and paired verdict answer different questions; say so, don't hide it."""
    for variant, escape in (("candidate_skill", True), ("stable_skill", False)):
        out = tmp_path / "c" / variant / "run1"
        out.mkdir(parents=True)
        bl.write_json(out / "run-result.json",
                      {"case_id": "c", "variant": variant, "repeat": 1, "status": "FAIL",
                       "metrics": {}, "runtime": {"checks": [], "authority_escape": escape},
                       "semantic": {"hard_gate": "pass"}, "task": None, "provenance": None})

    report = aggregate_report.build(tmp_path, "custom", "test")

    assert report["status"] == "REGRESSION"
    assert report["status_divergence"], "a gate the paired verdict cannot see must be disclosed"
    assert "Status note:" in aggregate_report.render_markdown(report)


def test_disclosure_reads_correctly_when_provenance_is_complete(tmp_path):
    """`0 of 2 runs recorded no provenance` inverted the sentence it was reporting."""
    for variant in ("candidate_skill", "stable_skill"):
        out = tmp_path / "c" / variant / "run1"
        out.mkdir(parents=True)
        bl.write_json(out / "run-result.json",
                      {"case_id": "c", "variant": variant, "repeat": 1, "status": "PASS",
                       "metrics": {}, "runtime": {"checks": []}, "semantic": {"hard_gate": "pass"},
                       "task": None, "provenance": {"aggregate_sha256": "d" * 64,
                                                    "candidate": {"aggregate_sha256": "d" * 64}}})

    provenance = aggregate_report.build(tmp_path, "custom", "test")["provenance"]

    assert provenance["runs_missing_provenance"] == 0
    assert provenance["disclosure"] == "all 2 runs recorded provenance"


def _rejudge(tmp_path, monkeypatch, session_status: str, stored_provenance=True):
    """Re-judge one stored run, with the paid semantic judge stubbed out.

    `stored_provenance=False` writes the prior result the way a legacy run did:
    no provenance recorded at all.
    """
    monkeypatch.setattr(semantic_judge, "extract_revealed_facts", lambda *a, **k: [])
    monkeypatch.setattr(semantic_judge, "judge",
                        lambda *a, **k: {"judge": "semantic", "hard_gate": "pass"})
    matrix_dir = tmp_path / "matrix"
    out_dir = matrix_dir / CASE / "candidate_skill" / "run1"
    artifacts = out_dir / "artifacts" / "prototype"
    (artifacts / "experiments" / "reader").mkdir(parents=True, exist_ok=True)
    (artifacts / "experiments" / "reader" / "index.html").write_text("<h1>reader</h1>")
    (artifacts / "discussion.md").write_text("# Discussion\n" + "x" * 300)
    bl.write_json(out_dir / "artifacts-manifest.json",
                  {"case_id": CASE, "variant": "candidate_skill", "artifacts_dir": str(artifacts),
                   "workspace": "/tmp/design-bench/x", "entry": "experiments/reader/index.html",
                   "counts": {"files": 3}, "hashes": {}})
    bl.write_json(out_dir / "session-summary.json",
                  {"status": session_status, "note": "cap reached", "metrics": {"cost_usd": 21.85}})
    prior = {"case_id": CASE, "variant": "candidate_skill", "repeat": 1, "status": "PASS"}
    if stored_provenance:
        prior["provenance"] = {"aggregate_sha256": "f" * 64,
                               "candidate": {"git_rev": "deadbeef"}}
    bl.write_json(out_dir / "run-result.json", prior)
    return out_dir, run_case.run_one(CASE, "candidate_skill", 1, matrix_dir, model=None,
                                     max_turns=1, timeout_s=1, budget_usd=0.0,
                                     do_task_trace=False, max_task_steps=1, do_visual=False,
                                     rejudge=True)


def test_rejudge_does_not_promote_a_blocked_session_to_a_judged_failure(tmp_path, monkeypatch):
    """Re-judging evaluates artifacts; it cannot retract why the session stopped.

    Before this, the re-judge path left the placeholder status in place and the
    result block wrote FAIL, so blocked sessions were counted as judged failures
    and `per_variant.blocked` read zero for a matrix of blocked runs.
    """
    out_dir, result = _rejudge(tmp_path, monkeypatch, "BLOCKED")

    assert result["status"] == "BLOCKED"
    assert bl.read_json(out_dir / "run-result.json")["status"] == "BLOCKED"
    assert any("session BLOCKED" in note for note in result["notes"])


def test_rejudge_keeps_a_completed_session_judged_normally(tmp_path, monkeypatch):
    """The guard must not swallow a genuinely completed run."""
    _, result = _rejudge(tmp_path, monkeypatch, "COMPLETED")

    assert result["status"] != "BLOCKED"


def test_rejudge_preserves_the_original_runs_provenance(tmp_path, monkeypatch):
    """Hashing the current tree would stamp a revision that postdates the artifacts."""
    _, result = _rejudge(tmp_path, monkeypatch, "COMPLETED")

    assert result["provenance"]["candidate"]["git_rev"] == "deadbeef"
    assert "provenance preserved from original run" in result["notes"]


def test_rejudge_discloses_absence_instead_of_inventing_provenance(tmp_path, monkeypatch):
    """A legacy run without stored provenance stays unknown; it is never back-filled.

    The alternative — recomputing identity from the working tree — would stamp a
    revision that postdates the artifacts onto bytes it never produced.
    """
    _, result = _rejudge(tmp_path, monkeypatch, "COMPLETED", stored_provenance=False)

    assert result["provenance"]["candidate"] is None
    assert result["provenance"]["notes"], "absence must be disclosed, not silent"
    assert any("provenance unknown" in note for note in result["notes"])


def test_source_identity_is_read_from_where_it_is_actually_stored(tmp_path):
    """The skill hash lives at candidate.skill.aggregate_sha256, not the top level."""
    out = tmp_path / "c" / "candidate_skill" / "run1"
    out.mkdir(parents=True)
    bl.write_json(out / "run-result.json",
                  {"case_id": "c", "variant": "candidate_skill", "repeat": 1, "status": "PASS",
                   "metrics": {}, "runtime": {"checks": []}, "semantic": {"hard_gate": "pass"},
                   "task": None,
                   "provenance": {"aggregate_sha256": None, "candidate": {
                       "aggregate_sha256": None, "skill": {"aggregate_sha256": "e" * 64}}}})

    assert aggregate_report.build(tmp_path, "custom", "test")["provenance"]["source_identity"] == ["e" * 64]

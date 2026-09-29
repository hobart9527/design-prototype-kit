"""Hermetic checks for the taste-layer judges (no network, no LLM, no browser).

The judges under test here are the measuring sticks for the taste dimension:
a deterministic slop scan, a deterministic divergence scan, and two vision
judges whose *plumbing* is checked without ever paying for a model call.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import bench_lib as bl  # noqa: E402
import aggregate_report  # noqa: E402
import cocreation_judge as ccj  # noqa: E402
import contract_fidelity_judge as cfj  # noqa: E402
import divergence_judge as dj  # noqa: E402
import regression_judge  # noqa: E402
import slop_detector as sd  # noqa: E402


def _write(root: pathlib.Path, name: str, text: str) -> pathlib.Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# -- slop detector ------------------------------------------------------------

def test_slop_detector_reports_each_rule_with_evidence(tmp_path):
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """
<html><head><style>
  .title { background: linear-gradient(90deg,#fff,#000); -webkit-background-clip: text; }
  .card { border: 1px solid #333; box-shadow: 0 20px 40px rgba(0,0,0,.4); border-radius: 12px; }
  .kpi { font-size: 40px; }
  .row { border-left: 4px solid #f00; }
  .x { transition: all .3s; }
</style></head><body>
  <div class="card"><div class="card">nested</div></div>
  <span>⚠ 遥测断流</span>
  <button class="confirm-btn">排空</button>
</body></html>""")
    result = sd.detect(tmp_path)
    assert result["status"] == "detected"
    rules = set(result["counts"])
    for expected in ("SLOP-001", "SLOP-002", "SLOP-004", "SLOP-006", "SLOP-009"):
        assert expected in rules, f"{expected} not reported: {sorted(rules)}"
    assert all(f["evidence"] for f in result["findings"]), "every finding carries evidence"
    assert result["by_severity"]["high"] >= 2
    assert result["slop_score"] > 0


def test_slop_detector_is_silent_on_a_clean_artifact(tmp_path):
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
:root { --ink: oklch(0.2 0.01 250); --accent: oklch(0.6 0.12 30); }
.metric { font-variant-numeric: tabular-nums; caret-color: var(--accent); }
::selection { background: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); }
::-webkit-scrollbar { width: 10px; }
</style></head><body><p class="metric">42 kg</p></body></html>""")
    result = sd.detect(tmp_path)
    assert result["status"] == "detected"
    assert result["by_severity"]["high"] == 0, result["findings"]
    assert "SLOP-017" not in result["counts"], "themed browser surfaces must not be flagged"


def test_slop_detector_flags_unthemed_browser_surfaces_and_missing_press_detent(tmp_path):
    _write(tmp_path, "prototype/experiments/s/anchor/index.html",
           '<html><head><style>.x{color:#111}</style></head><body>'
           '<button class="confirm">提交</button></body></html>')
    result = sd.detect(tmp_path)
    assert "SLOP-017" in result["counts"]
    assert "SLOP-018" in result["counts"], "a commit control with no :active detent is a finding"


def test_slop_detector_does_not_flag_layout_panel_wrapping_cards(tmp_path):
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><body>
    <div class="layout-panel">
      <div class="header">Cluster Grid</div>
      <div class="card">Item 1</div>
      <div class="card">Item 2</div>
    </div>
    </body></html>""")
    result = sd.detect(tmp_path)
    assert "SLOP-004" not in result["counts"], "layout panels wrapping sibling cards must not trigger nested card slop"


def test_slop_detector_without_artifacts_is_blocked_not_passing(tmp_path):
    result = sd.detect(tmp_path)
    assert result["status"] == "blocked"
    assert result["findings"] == []


# -- divergence judge ---------------------------------------------------------

SAME_SHAPE_A = """<html><body><header>t</header><section><h2>a</h2><p>b</p></section>
<footer>f</footer></body></html>"""
SAME_SHAPE_B = """<html><body><header>t</header><section><h2>a</h2><p>b</p></section>
<footer>f</footer></body></html>"""
DIFFERENT_SHAPE = """<html><body><main><article><aside><ol><li>x</li></ol></aside></article></main>
</body></html>"""


def test_divergence_flags_recolouring_as_one_direction_counted_twice(tmp_path):
    _write(tmp_path, "prototype/experiments/s/dirs/a/index.html",
           SAME_SHAPE_A.replace("<body>", "<body style='color:#112233'>"))
    _write(tmp_path, "prototype/experiments/s/dirs/b/index.html",
           SAME_SHAPE_B.replace("<body>", "<body style='color:#445566'>"))
    result = dj.judge(tmp_path)
    assert result["status"] == "measured"
    assert result["verdict"] == "pseudo_divergence"
    assert result["distinct_pairs"] == 0


def test_divergence_recognises_a_structurally_different_direction(tmp_path):
    _write(tmp_path, "prototype/experiments/s/dirs/a/index.html", SAME_SHAPE_A)
    _write(tmp_path, "prototype/experiments/s/dirs/b/index.html", DIFFERENT_SHAPE)
    result = dj.judge(tmp_path)
    assert result["verdict"] == "divergent"
    assert result["distinct_pairs"] == 1


def test_divergence_with_one_slot_is_not_measured(tmp_path):
    _write(tmp_path, "prototype/experiments/s/dirs/a/index.html", SAME_SHAPE_A)
    result = dj.judge(tmp_path)
    assert result["status"] == "insufficient"
    assert result["verdict"] == "not_measured"


# -- contract fidelity judge --------------------------------------------------

def test_contract_extraction_finds_the_declared_section(tmp_path):
    _write(tmp_path, "prototype/briefs/reader-core.md", """
# Surface Brief

## Direction Contract
- THESIS: a citation-first reading surface
- OWN-WORLD: legal paper, not dashboard chrome
- FIRST VIEWPORT: the clause itself

## Notes
other stuff
""")
    contract = cfj.extract_contract(tmp_path)
    assert contract["source"] == "section"
    assert "THESIS" in contract["text"]
    assert "other stuff" not in contract["text"], "the section ends at the next heading"


def test_contract_extraction_reports_absence_rather_than_inventing_one(tmp_path):
    _write(tmp_path, "prototype/discussion.md", "# Discussion\n\nsome decisions\n")
    contract = cfj.extract_contract(tmp_path)
    assert contract["source"] == "absent"
    result = cfj.judge({"brief": "b"}, tmp_path, [], tmp_path / "work")
    assert result["status"] == "unverified"
    assert "no declared contract" in result["note"]


def test_contract_fidelity_without_screenshots_stays_unverified(tmp_path):
    _write(tmp_path, "prototype/briefs/s.md", "## Direction Contract\nTHESIS: x\n")
    result = cfj.judge({"brief": "b"}, tmp_path, [], tmp_path / "work")
    assert result["status"] == "unverified"


# -- regression over taste ----------------------------------------------------

def _run(case_id, variant, **extra):
    base = {"case_id": case_id, "variant": variant, "repeat": 1, "status": "PASS",
            "runtime": {"status": "pass"}, "semantic": {"hard_gate": "pass"},
            "task": {"status": "pass"}}
    base.update(extra)
    return base


def test_taste_regression_fires_when_the_candidate_is_sloppier():
    stable = _run("c", "stable_skill", slop={"status": "detected", "slop_score": 0,
                                             "by_severity": {"high": 0}})
    cand = _run("c", "candidate_skill", slop={"status": "detected", "slop_score": 6,
                                              "by_severity": {"high": 2}})
    verdict = regression_judge.judge([stable, cand])
    assert verdict["verdict"] == "REGRESSION"
    assert any(r["dimension"] == "taste" for r in verdict["regressions"])


def test_taste_regression_is_unverifiable_when_only_one_arm_measured_it():
    stable = _run("c", "stable_skill")
    cand = _run("c", "candidate_skill", slop={"status": "detected", "slop_score": 3,
                                              "by_severity": {"high": 1}})
    verdict = regression_judge.judge([stable, cand])
    assert not any(r["dimension"] == "taste" for r in verdict["regressions"])
    assert any(u["dimension"] == "taste" for u in verdict["unverifiable_dimensions"])


def test_taste_regression_ranks_the_blind_verdicts():
    stable = _run("c", "stable_skill", taste={"status": "judged", "result": {
        "ai_slop_verdict": "pass", "first_viewport_thesis": "present",
        "category_guessability": "low"}})
    cand = _run("c", "candidate_skill", taste={"status": "judged", "result": {
        "ai_slop_verdict": "fail", "first_viewport_thesis": "absent",
        "category_guessability": "high"}})
    verdict = regression_judge.judge([stable, cand])
    signals = {r["signal"] for r in verdict["regressions"] if r["dimension"] == "taste"}
    assert signals == {"ai_slop_verdict", "first_viewport_thesis", "category_guessability"}


def test_divergence_regression_ranks_pseudo_divergence_above_divergent():
    stable = _run("c", "stable_skill", divergence={"status": "measured", "verdict": "divergent"})
    cand = _run("c", "candidate_skill", divergence={"status": "measured", "verdict": "recolouring"})
    verdict = regression_judge.judge([stable, cand])
    assert any(r["dimension"] == "taste" and r["signal"] == "divergence_verdict"
               for r in verdict["regressions"])


# -- co-creation --------------------------------------------------------------

def _transcript(tmp_path, turns):
    """turns: list of (role, text). Written in order — order is the measurement."""
    body = "\n\n".join(f"## {role}\n\n{text}" for role, text in turns)
    (tmp_path / "session-transcript.md").write_text(body, encoding="utf-8")
    return tmp_path


def test_cocreation_credits_a_choice_offered_before_the_build(tmp_path):
    _transcript(tmp_path, [
        ("user", "build a reader"),
        ("assistant", "Category rut: every reader in this space is a card feed. "
                      "Direction A lives in a statute book; Direction B in a newsprint "
                      "column. Seed 41 and seed 77 assigned. USER-INPUT: which world?"),
        ("user", "Direction A"),
        ("assistant", "<html>experiments/reader/dirs/a/index.html</html>"),
    ])
    result = ccj.judge(tmp_path)
    assert result["status"] == "measured"
    assert result["signals"]["c0_before_build"] is True
    assert result["signals"]["choice_taken"] is True
    assert result["verdict"] in ("co_created", "partial")


def test_cocreation_flags_a_build_that_asked_nothing(tmp_path):
    _transcript(tmp_path, [
        ("user", "build a reader"),
        ("assistant", "Here is the direction I chose. <html>experiments/reader/anchor/index.html</html>"),
    ])
    result = ccj.judge(tmp_path)
    assert result["verdict"] == "reveal_only"
    assert result["signals"]["c0_presented"] is False


def test_cocreation_flags_a_confirmed_lock_with_nothing_to_confirm(tmp_path):
    """Claiming a confirmed lock without ever offering a candidate is the dishonesty
    the stopping points exist to prevent."""
    _transcript(tmp_path, [
        ("user", "build a reader"),
        ("assistant", "Direction locked and confirmed. <html>anchor/index.html</html>"),
    ])
    result = ccj.judge(tmp_path)
    assert result["verdict"] == "false_confirmation"


def test_cocreation_without_a_transcript_is_unverified(tmp_path):
    result = ccj.judge(tmp_path)
    assert result["status"] == "unverified"
    assert result["verdict"] == "not_measured"


def test_cocreation_regression_ranks_reveal_above_co_creation():
    stable = _run("c", "stable_skill", cocreation={"status": "measured", "verdict": "co_created"})
    cand = _run("c", "candidate_skill", cocreation={"status": "measured", "verdict": "reveal_only"})
    verdict = regression_judge.judge([stable, cand])
    assert any(r["dimension"] == "taste" and r["signal"] == "cocreation_verdict"
               for r in verdict["regressions"])


def test_mock_user_direction_choices_are_parsed():
    text = ("## Decision Answers\n- 主题|配色: 浅色为主\n\n"
            "## Direction Choice\n- 方向|direction|世界|world: 选 A，法规书的秩序感\n\n"
            "## Fallback\n按专业判断。")
    parsed = bl.parse_mock_user(text)
    assert parsed["direction_rules"] == 1
    assert any(r["kind"] == "direction" for r in parsed["rules"])
    # Both sections feed one rule list: they answer the same shape of question.
    assert len(parsed["rules"]) == 2
    reply = bl.mock_reply("你倾向哪个方向？", parsed["rules"], parsed["fallback"])
    assert "A" in reply


# -- report -------------------------------------------------------------------

def test_report_surfaces_the_taste_layer(tmp_path):
    matrix = tmp_path / "matrix"
    for variant, score in (("stable_skill", 0), ("candidate_skill", 4)):
        bl.write_json(matrix / "c" / variant / "run1" / "run-result.json",
                      _run("c", variant, slop={"status": "detected", "slop_score": score,
                                               "counts": {"SLOP-001": 1},
                                               "findings": [{"rule": "SLOP-001", "severity": "high",
                                                             "file": "a.html", "evidence": "e"}],
                                               "by_severity": {"high": 1}}))
    report = aggregate_report.build(matrix, "custom", "run")
    assert report["per_variant"]["candidate_skill"]["slop_score"] == 4
    assert report["slop_rules"]["candidate_skill"]["SLOP-001"]["severity"] == "high"
    markdown = aggregate_report.render_markdown(report)
    assert "## Taste (measured, not asserted)" in markdown
    assert "SLOP-001" in markdown


def test_report_surfaces_co_creation(tmp_path):
    matrix = tmp_path / "matrix"
    for variant, verdict in (("stable_skill", "co_created"), ("candidate_skill", "reveal_only")):
        bl.write_json(matrix / "c" / variant / "run1" / "run-result.json",
                      _run("c", variant, cocreation={"status": "measured", "verdict": verdict,
                                                     "signals": {"c0_before_build": verdict == "co_created"}}))
    report = aggregate_report.build(matrix, "custom", "run")
    assert report["per_variant"]["candidate_skill"]["cocreation_verdicts"] == ["reveal_only"]
    assert report["per_variant"]["candidate_skill"]["cocreation_before_build"] == 0
    markdown = aggregate_report.render_markdown(report)
    assert "### Co-creation (was the choice offered?)" in markdown
    assert "reveal_only" in markdown


def test_taste_flags_are_in_the_case_schema():
    schema = json.loads((bl.SCHEMAS_DIR / "case.schema.json").read_text())
    assert "taste" in schema["properties"]["evaluation"]["properties"]
    declared = [cid for cid in bl.case_paths()
                if (bl.load_case(cid)["meta"].get("evaluation") or {}).get("taste")]
    # The taste judges need screenshots, so a case without visual_pairwise cannot
    # run them; the new mode-coverage cases are the ones that must declare it.
    assert {"read-doc", "mobile-experience"} <= set(declared), declared
    for case_id in declared:
        case = bl.load_case(case_id)
        assert case["meta"]["evaluation"].get("visual_pairwise"), \
            f"{case_id} runs taste judges but captures no screenshots"

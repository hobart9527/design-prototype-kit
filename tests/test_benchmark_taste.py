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


def test_slop_019_ignores_css_comments(tmp_path):
    # r24 false positive: tokens.css header prose "asymmetric" matched
    # METRIC_CLASS_RE's "metric" and fired SLOP-019 on a variables-only file.
    _write(tmp_path, "prototype/shared/tokens.css", """/* Density axis: asymmetric 12px rhythm, stat-free */
:root {
  --selection-bg: oklch(0.6 0.12 30);
  --scrollbar-thumb: oklch(0.4 0.02 250);
  --focus-ring: oklch(0.7 0.1 30);
  --space-unit: 12px;
}""")
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
::selection { background: var(--selection-bg); }
:focus-visible { outline: 2px solid var(--focus-ring); }
::-webkit-scrollbar { width: 10px; }
body { caret-color: var(--focus-ring); }
</style></head><body><p>steady state</p></body></html>""")
    result = sd.detect(tmp_path)
    assert "SLOP-019" not in result["counts"], (
        f"comment prose must not read as a metric class: {result['findings']}")


def test_slop_style_extraction_survives_truncation(tmp_path):
    # r24 false positive class: artifact_texts caps files, and a cap landing
    # inside <style> drops </style>. Extraction must still see the CSS so
    # SLOP-017 does not fire on empty input.
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
::selection { background: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); }
::-webkit-scrollbar { width: 10px; }
body { caret-color: var(--accent); }
.metric { font-variant-numeric: tabular-nums; }
""")  # truncated: no </style>, no </head>
    result = sd.detect(tmp_path)
    assert "SLOP-017" not in result["counts"], (
        f"unclosed <style> must not blind the surface rules: {result['findings']}")


def test_slop_002_ignores_transient_toast_accent(tmp_path):
    # r24 false positive: a status toast's 3px semantic accent bar is a ledger
    # convention (GitHub/Linear notifications), not the container-stripe cliché.
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
::selection { background: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); }
::-webkit-scrollbar { width: 10px; }
body { caret-color: var(--accent); }
.metric { font-variant-numeric: tabular-nums; }
.toast { border: 1px solid var(--line); border-left: 3px solid var(--green); }
.toast.warn { border-left-color: var(--amber); }
</style></head><body><p>ok</p></body></html>""")
    result = sd.detect(tmp_path)
    assert "SLOP-002" not in result["counts"], (
        f"toast accent bars must not read as container stripes: {result['findings']}")


def test_slop_019_ignores_metric_substrings_in_status_tokens(tmp_path):
    """`--status-warn`/`--state` tail-match "stat" without a left word boundary.

    r24 fixed the comment route ("asymmetric"); r29 showed the same substring
    bug firing on a variables-only tokens file through `status`/`state`.
    """
    _write(tmp_path, "prototype/shared/tokens.css",
           ":root { --status-warn: #c90; --status-ok: #3a3; --state-idle: #888; }\n")
    result = sd.detect(tmp_path)
    assert "SLOP-019" not in result["counts"], result["findings"]


def test_slop_002_ignores_a_selected_row_rail(tmp_path):
    """A 3px rail on `.sel` marks the row the user is acting on, not a container."""
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
.node-row { padding: 8px; }
.node-row.sel { border-left: 3px solid var(--accent); }
</style></head><body><div class="node-row sel">node</div></body></html>""")
    result = sd.detect(tmp_path)
    assert "SLOP-002" not in result["counts"], result["findings"]


def test_slop_002_ignores_a_transparent_width_reservation(tmp_path):
    """`border-left: 3px solid transparent` paints nothing; the state variants are the markers."""
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
.seq-row { padding: 8px; border-left: 3px solid transparent; }
.seq-row[data-st="pending"] { border-left-color: var(--warn); }
</style></head><body><div class="seq-row" data-st="pending">x</div></body></html>""")
    result = sd.detect(tmp_path)
    assert "SLOP-002" not in result["counts"], result["findings"]

def test_slop_002_still_flags_a_static_container_stripe(tmp_path):
    """The state exemption must not swallow the cliché it exists beside."""
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
.panel { border-left: 5px solid #f00; }
</style></head><body><div class="panel">x</div></body></html>""")
    result = sd.detect(tmp_path)
    assert "SLOP-002" in result["counts"], result["findings"]


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


def test_slop_detector_reads_prose_arrows_as_typography_not_iconography(tmp_path):
    """`→` between runbook steps and `↗` on a trend readout are typography.

    r20 was judged REGRESSION off this rule alone: the arrows block
    (U+2190–U+21FF) sat inside the emoji character class, so every Chinese
    process line scored a `high` finding and the candidate was ranked sloppier
    than a control arm that had merely measured zero by shipping no HTML.
    """
    _write(tmp_path, "prototype/experiments/s/anchor/index.html",
           "<html><body><p>· 提名 → 待放行 → 排空(可回滚) → 已下线</p>"
           "<p>错误率 4.2% ↗ 基线 0.3%</p>"
           "<button>↩ 回滚</button></body></html>")
    result = sd.detect(tmp_path)
    assert "SLOP-009" not in result["counts"], result["findings"]


def test_slop_detector_flags_a_glyph_holding_an_icons_slot(tmp_path):
    """The rule's actual subject: a glyph standing where an icon belongs."""
    _write(tmp_path, "prototype/experiments/s/anchor/index.html",
           "<html><body><span>⚠ 遥测断流</span><span>🔒 锁定</span>"
           "<p>处置完成 🎉 全流程无人工介入</p></body></html>")
    result = sd.detect(tmp_path)
    assert "SLOP-009" in result["counts"], result["findings"]


def test_slop_009_exempts_a_glyph_that_marks_a_named_control(tmp_path):
    """A close button's `✕` is the affordance's own mark, not borrowed pictography.

    r28 flagged `<button aria-label="关闭详情">✕</button>`; the accessible name
    carries the meaning and the glyph is the standard close symbol.
    """
    _write(tmp_path, "prototype/experiments/s/anchor/index.html",
           '<html><body><button aria-label="关闭详情">✕</button></body></html>')
    result = sd.detect(tmp_path)
    assert "SLOP-009" not in result["counts"], result["findings"]


def test_slop_009_still_flags_a_glyph_leading_a_control_label(tmp_path):
    """A glyph in front of a real label is the icon-slot shape, even in a button.

    `📊 查看` puts the glyph exactly where an icon belongs; a name in the button
    does not launder it.
    """
    _write(tmp_path, "prototype/experiments/s/anchor/index.html",
           "<html><body><button>📊 查看</button></body></html>")
    result = sd.detect(tmp_path)
    assert "SLOP-009" in result["counts"], result["findings"]


def test_slop_009_still_flags_a_glyph_that_is_the_whole_button(tmp_path):
    """The exemption needs a word beside the glyph; a bare pictograph button stays."""
    _write(tmp_path, "prototype/experiments/s/anchor/index.html",
           "<html><body><button>🔒</button></body></html>")
    result = sd.detect(tmp_path)
    assert "SLOP-009" in result["counts"], result["findings"]


def test_slop_detector_does_not_score_the_harness_review_portal(tmp_path):
    """The portal is the Skill's operational wrapper, not authored design surface.

    `runtime_judge` excludes it from the candidate's artifacts; the taste score
    has to make the same exemption or it charges the candidate for the harness.
    """
    _write(tmp_path, "prototype/experiments/s/anchor/index.html", """<html><head><style>
:root { --ink: oklch(0.2 0.01 250); --accent: oklch(0.6 0.12 30); }
.metric { font-variant-numeric: tabular-nums; caret-color: var(--accent); }
::selection { background: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); }
::-webkit-scrollbar { width: 10px; }
</style></head><body><p class="metric">42 kg</p></body></html>""")
    _write(tmp_path, "prototype/review-portal.html",
           "<html><head><style>.metric{font-size:32px;transition:all .3s}"
           ".p{border-radius:9999px}</style></head><body>"
           "<span>⚠ 遥测断流</span></body></html>")
    result = sd.detect(tmp_path)
    assert "review-portal.html" not in " ".join(result["files_scanned"]), result["files_scanned"]
    assert result["slop_score"] == 0, result["findings"]


def test_slop_severity_counts_match_the_reported_findings(tmp_path):
    """`by_severity` and the findings list must agree, capped list included.

    Before this, severity counted every match while the list capped per rule, so
    a report could announce more high findings than it could name.
    """
    _write(tmp_path, "prototype/experiments/s/anchor/index.html",
           "<html><head><style>" + "".join(
               f".row{i}{{border-left:4px solid #f00}}" for i in range(6)) +
           "</style></head><body></body></html>")
    result = sd.detect(tmp_path)
    for level in ("high", "medium", "low"):
        assert result["by_severity"][level] == sum(
            1 for f in result["findings"] if f["severity"] == level), level


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

"""The craft floor's prose and its machine checks, anchored in both directions.

`craft-floor.md` states the floor; `detect.py` checks the part of it a text scan
can reach. The ids are the join. These pins hold that join: a rule may be added
with no detector (that is a recorded status), but never with no id. The benchmark
crosswalk is validated separately from the delivery detector.
"""
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/spec-prototype"
SCRIPTS = SKILL / "scripts"
FLOOR = SKILL / "references/02-craft-methods/craft-floor.md"

sys.path.insert(0, str(SCRIPTS))
import detect  # noqa: E402


def _floor_text() -> str:
    text = FLOOR.read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", re.sub(r"\*\*|`", "", text))


def test_every_registered_rule_is_declared_by_the_craft_floor():
    """An id the prose does not carry is an id nobody reading the floor will meet."""
    floor = _floor_text()
    missing = sorted(rid for rid in detect.RULES if rid not in floor)
    assert not missing, (
        f"detect.py registers rules the craft floor never names: {missing}. "
        "The id is the anchor; add it to craft-floor.md beside the rule."
    )


def test_benchmark_crosswalk_resolves_both_rule_sets():
    """Crosswalk integrity belongs to benchmark code, not the delivery detector."""
    sys.path.insert(0, str(REPO / "benchmarks" / "judges"))
    from craft_floor_crosswalk import validate_crosswalk

    assert not validate_crosswalk()


def test_delivery_detector_has_no_benchmark_rule_mapping():
    assert not hasattr(detect, "BENCHMARK_ANCHORS")
    assert "benchmark_anchors" not in detect.anchor_report()


def test_a_rule_without_a_detector_states_why():
    """'Not machine-checkable' is a status, not a gap left unexplained."""
    for rule_id, entry in detect.RULES.items():
        if entry["kind"] == "prose_only":
            assert entry.get("why"), f"{rule_id} is prose_only but gives no reason"
        else:
            assert callable(entry.get("detector")), f"{rule_id} has no callable detector"
            assert entry.get("polarity") in {"presence", "violation"}, f"{rule_id} lacks an explicit polarity"


def test_direction_selected_techniques_are_not_token_presence_gates(tmp_path):
    artifact = tmp_path / "flat.html"
    artifact.write_text('<html lang="en"><body>Flat, precise surface</body></html>')
    result = detect.scan(artifact)
    for rule_id in ("CRAFT-SURFACE-SHEEN", "CRAFT-KINETIC-SPRING"):
        assert detect.RULES[rule_id]["kind"] == "prose_only"
        assert detect.RULES[rule_id]["why"]
        assert not any(item["rule"] == rule_id for item in result["findings"])


def test_the_registry_is_not_all_judgement():
    """A floor with no mechanical checks is a floor nothing enforces."""
    report = detect.anchor_report()
    assert report["counts"]["check"] >= 5, report["counts"]
    assert report["counts"]["prose_only"] >= 3, report["counts"]


def test_scan_reports_a_hit_and_a_clear(tmp_path):
    sloppy = tmp_path / "sloppy.html"
    sloppy.write_text(
        '<html><head><style>.t{background-clip:text;background:linear-gradient(#fff,#000)}'
        '</style></head><body><button data-action="save">保存</button>'
        '<span>⚠ 断流</span></body></html>', encoding="utf-8")
    result = detect.scan(sloppy)
    by_id = {f["rule"]: f["status"] for f in result["findings"]}
    assert by_id["CRAFT-NO-GRADIENT-TEXT"] == "hit"
    assert by_id["CRAFT-NO-EMOJI-ICON"] == "hit"
    assert by_id["CRAFT-PRESS-DETENT"] == "clear", "no :active in the specimen"
    assert by_id["CRAFT-SELECTION"] == "clear"
    assert result["unchecked"], "judgement rules are listed, not dropped"
    assert all(u["why"] for u in result["unchecked"])


def test_modern_capability_checks_are_advisory_detectors(tmp_path):
    artifact = tmp_path / "modern.html"
    artifact.write_text("""<html><head><meta name="color-scheme" content="light dark"><style>
    .title { font-size: clamp(1.5rem, 3vw, 3rem); }
    @media (prefers-reduced-motion: reduce) { * { animation: none; } }
    </style></head><body>
    <section aria-busy="true"><div class="skeleton"></div></section>
    <p aria-live="polite">Loading</p>
    </body></html>""", encoding="utf-8")

    findings = {f["rule"]: f["status"] for f in detect.scan(artifact)["findings"]}

    assert findings["CRAFT-REDUCED-MOTION"] == "hit"
    assert findings["CRAFT-ARIA-LIVE"] == "hit"
    assert findings["CRAFT-FLUID-TYPE"] == "hit"
    assert findings["CRAFT-COLOR-SCHEME"] == "hit"
    assert findings["CRAFT-LOADING-STATE"] == "hit"


def test_modern_capability_checks_do_not_hit_absent_capabilities(tmp_path):
    artifact = tmp_path / "plain.html"
    artifact.write_text("<html><body><p>static content</p></body></html>", encoding="utf-8")

    findings = {f["rule"]: f["status"] for f in detect.scan(artifact)["findings"]}

    for rule in ("CRAFT-REDUCED-MOTION", "CRAFT-ARIA-LIVE", "CRAFT-FLUID-TYPE",
                 "CRAFT-COLOR-SCHEME", "CRAFT-LOADING-STATE"):
        assert findings[rule] == "clear"


def test_action_feedback_accepts_chinese_settlement_and_recovery(tmp_path):
    artifact = tmp_path / "action.html"
    artifact.write_text("""<button data-action="drain">排空</button>
    <p>处理中</p><p>已完成</p><button>撤销</button>""", encoding="utf-8")

    assert detect.RULES["CRAFT-ACTION-FEEDBACK"]["detector"](artifact)


def test_action_feedback_stays_clear_without_a_commit_control(tmp_path):
    artifact = tmp_path / "action.html"
    artifact.write_text("<p>排空处理中，已完成，可撤销。</p>", encoding="utf-8")

    assert not detect.RULES["CRAFT-ACTION-FEEDBACK"]["detector"](artifact)


def test_scan_surfaces_a_broken_detector_rather_than_reading_it_as_clean(tmp_path):
    artifact = tmp_path / "a.html"
    artifact.write_text("<html></html>", encoding="utf-8")
    original = detect.RULES["CRAFT-CARET"]
    detect.RULES["CRAFT-CARET"] = {
        "prose": original["prose"], "kind": "check",
        "detector": lambda _p: (_ for _ in ()).throw(RuntimeError("boom")),
    }
    try:
        result = detect.scan(artifact)
    finally:
        detect.RULES["CRAFT-CARET"] = original
    broken = [f for f in result["findings"] if f["rule"] == "CRAFT-CARET"]
    assert broken and broken[0]["status"] == "error"
    assert result["checked"] == sum(
        1 for f in result["findings"] if f["status"] in ("hit", "clear")), \
        "an errored detector must not count as checked"


def test_html_scan_includes_linked_styles_and_marks_unresolved_coverage(tmp_path):
    html_dir = tmp_path / "artifact"
    css_dir = html_dir / "styles"
    css_dir.mkdir(parents=True)
    html = html_dir / "index.html"
    html.write_text(
        '<html><head><link rel="stylesheet" href="styles/app.css">'
        '<link rel="stylesheet" href="missing.css"></head><body></body></html>',
        encoding="utf-8",
    )
    (css_dir / "app.css").write_text("button:active { transform: scale(.98); }", encoding="utf-8")
    result = detect.scan(html)
    assert str(css_dir / "app.css") in result["sources"]
    assert result["unresolved_links"] == ["missing.css"]
    assert result["source_coverage"] == "partial"
    assert {f["rule"]: f["status"] for f in result["findings"]}["CRAFT-PRESS-DETENT"] == "hit"
    coverage = next(f for f in result["findings"] if f["rule"] == "SOURCE-COVERAGE")
    assert coverage["status"] == "unmeasured"
    assert result["unmeasured"] >= 1


def test_html_scan_reads_shared_token_css_outside_the_anchor_directory(tmp_path):
    # The real anchor layout links ../../../shared/tokens.css. Confining the read
    # to the HTML's own folder reported that live file as unresolved and left the
    # token layer unscanned — a false coverage gap on every layered prototype.
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    anchor = repo / "prototype/experiments/slice/anchor"
    shared = repo / "prototype/shared"
    anchor.mkdir(parents=True)
    shared.mkdir(parents=True)
    (shared / "tokens.css").write_text(":root { --x: 1 }\n.num { font-variant-numeric: tabular-nums; }\n", encoding="utf-8")
    html = anchor / "index.html"
    html.write_text(
        '<html><head><link rel="stylesheet" href="../../../shared/tokens.css">'
        '<link rel="stylesheet" href="anchor.css"></head><body></body></html>',
        encoding="utf-8",
    )
    (anchor / "anchor.css").write_text("button:active { transform: scale(.98); }", encoding="utf-8")
    result = detect.scan(html)
    assert str(shared / "tokens.css") in result["sources"]
    assert result["unresolved_links"] == []
    assert result["source_coverage"] == "complete"
    assert {f["rule"]: f["status"] for f in result["findings"]}["CRAFT-TABULAR-NUMS"] == "hit"


def test_html_scan_still_refuses_a_link_escaping_the_scan_root(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    anchor = repo / "prototype/experiments/slice/anchor"
    anchor.mkdir(parents=True)
    (tmp_path / "outside.css").write_text(".num { font-variant-numeric: tabular-nums; }", encoding="utf-8")
    html = anchor / "index.html"
    html.write_text(
        '<html><head><link rel="stylesheet" href="../../../../../outside.css"></head><body></body></html>',
        encoding="utf-8",
    )
    result = detect.scan(html)
    assert str(tmp_path / "outside.css") not in result["sources"]
    assert result["unresolved_links"] == ["../../../../../outside.css"]
    assert result["source_coverage"] == "partial"


def test_new_modern_detectors_have_positive_and_negative_examples(tmp_path):
    """Advisory rules report signals only when the corresponding technique exists."""
    artifact = tmp_path / "modern-signals.html"
    artifact.write_text("""<html lang=\"zh-Hans\"><head><style>
    h1 { text-wrap: balance; }
    main { min-height: 100dvh; }
    @media (prefers-reduced-motion: reduce) { * { transition: none; } }
    </style></head><body>
    <h1>设计评审</h1><main><button>评审</button></main>
    <script>document.startViewTransition(() => {});</script>
    </body></html>""", encoding="utf-8")
    positives = {rule: detect.RULES[rule]["detector"](artifact) for rule in (
        "CRAFT-TEXT-WRAP", "CRAFT-VIEWPORT-UNITS", "CRAFT-VIEW-TRANSITION")}
    assert positives == {
        "CRAFT-TEXT-WRAP": True,
        "CRAFT-VIEWPORT-UNITS": True,
        "CRAFT-VIEW-TRANSITION": True,
    }

    plain = tmp_path / "plain.html"
    plain.write_text("<html lang=\"en\"><body><p>Plain</p></body></html>", encoding="utf-8")
    negatives = {rule: detect.RULES[rule]["detector"](plain) for rule in (
        "CRAFT-TEXT-WRAP", "CRAFT-VIEWPORT-UNITS", "CRAFT-VIEW-TRANSITION")}
    assert negatives == {rule: False for rule in negatives}


def test_new_modern_detectors_classify_applicability_and_violations(tmp_path):
    cjk = tmp_path / "cjk.html"
    cjk.write_text('<html lang="zh-CN"><body>中文</body></html>', encoding="utf-8")
    en = tmp_path / "en.html"
    en.write_text('<html lang="en"><body>English</body></html>', encoding="utf-8")
    assert detect.RULES["CRAFT-CJK-TYPESET"]["detector"](cjk) is False
    assert detect.RULES["CRAFT-CJK-TYPESET"]["detector"](en) is detect.NOT_APPLICABLE
    assert detect.RULES["CRAFT-FONT-LOADING"]["detector"](en) is detect.NOT_APPLICABLE

    raw_color = tmp_path / "raw-color.html"
    raw_color.write_text("<style>.button { color: #123456; }</style>", encoding="utf-8")
    token_color = tmp_path / "token-color.html"
    token_color.write_text("<style>:root { --accent: #123456; } .button { color: var(--accent); }</style>", encoding="utf-8")
    assert detect.RULES["CRAFT-TOKEN-ONLY"]["detector"](raw_color) is True
    assert detect.RULES["CRAFT-TOKEN-ONLY"]["detector"](token_color) is False

    haptic = tmp_path / "haptic.html"
    haptic.write_text("<script>navigator.vibrate(20)</script>", encoding="utf-8")
    paired = tmp_path / "paired-haptic.html"
    paired.write_text('<script>navigator.vibrate(20)</script><p role="status">Saved</p>', encoding="utf-8")
    assert detect.RULES["CRAFT-HAPTIC-PAIRING"]["detector"](haptic) is False
    assert detect.RULES["CRAFT-HAPTIC-PAIRING"]["detector"](paired) is True


def test_css_imports_are_scanned_recursively_with_cycle_and_root_guards(tmp_path):
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    styles = root / "prototype/experiments/slice/anchor/styles"
    styles.mkdir(parents=True)
    html = root / "prototype/experiments/slice/anchor/index.html"
    html.write_text('<link rel="stylesheet" href="styles/base.css">', encoding="utf-8")
    (styles / "base.css").write_text('@import "nested.css";\nbody { color: black; }', encoding="utf-8")
    (styles / "nested.css").write_text('@import "base.css";\nbutton:active { transform: scale(.98); }', encoding="utf-8")
    result = detect.scan(html)
    assert str(styles / "base.css") in result["sources"]
    assert str(styles / "nested.css") in result["sources"]
    assert result["unresolved_links"] == []
    assert {f["rule"]: f["status"] for f in result["findings"]}["CRAFT-PRESS-DETENT"] == "hit"

    (styles / "nested.css").write_text('@import "../../../../../../outside.css";', encoding="utf-8")
    escaped = detect.scan(html)
    assert escaped["unresolved_links"] == ["../../../../../../outside.css"]


def test_the_detector_serialises_for_the_cli(tmp_path):
    artifact = tmp_path / "a.html"
    artifact.write_text("<html><body><button>x</button></body></html>", encoding="utf-8")
    out = tmp_path / "out.json"
    payload = detect.scan(artifact)
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    assert json.loads(out.read_text())["detector"] == "craft-floor"


def test_quality_floor_craft_invariants_carry_craft_floor_ids():
    """quality-floor.md's Objective Floor restates craft invariants by id, not
    by re-definition: the anchor join holds on the verification side too."""
    from craft_floor_crosswalk import BENCHMARK_ANCHORS  # reuse repo-level import path setup
    qfloor = (SKILL / "references/03-verification/quality-floor.md").read_text(encoding="utf-8")
    for rule_id in ("CRAFT-PRESS-DETENT", "CRAFT-CONCENTRIC-RADII", "CRAFT-TABULAR-NUMS"):
        assert rule_id in qfloor, (
            f"{rule_id} is enforced as a runtime invariant but quality-floor.md "
            "does not anchor it by id; add the id, never a re-stated definition"
        )
    # The anchor must be detect.py-registered — no orphan ids in the floor.
    import detect
    for rule_id in ("CRAFT-PRESS-DETENT", "CRAFT-CONCENTRIC-RADII", "CRAFT-TABULAR-NUMS"):
        assert rule_id in detect.RULES


def test_crosswalk_accounts_for_every_emitted_slop_rule():
    from craft_floor_crosswalk import BENCHMARK_ANCHORS, BENCHMARK_UNMAPPED, validate_crosswalk
    assert not validate_crosswalk()
    import re
    source = (REPO / "benchmarks/judges/slop_detector.py").read_text(encoding="utf-8")
    emitted = set(re.findall(r"SLOP-\d{3}", source))
    assert emitted == set(BENCHMARK_ANCHORS) | set(BENCHMARK_UNMAPPED)
    for rule_id, reason in BENCHMARK_UNMAPPED.items():
        assert reason.strip(), f"{rule_id} exempted without a reason"

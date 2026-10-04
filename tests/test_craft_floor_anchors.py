"""The craft floor's prose and its machine checks, anchored in both directions.

`craft-floor.md` states the floor; `detect.py` checks the part of it a text scan
can reach. The ids are the join. These pins hold that join: a rule may be added
with no detector (that is a recorded status), but never with no id, and a
benchmark rule may never point at a craft-floor id that does not exist.
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


def test_every_anchor_resolves_to_a_registered_rule():
    """A benchmark anchor pointing at nothing silently stops anchoring."""
    unknown = sorted(set(detect.BENCHMARK_ANCHORS.values()) - set(detect.RULES))
    assert not unknown, f"BENCHMARK_ANCHORS name unregistered craft rules: {unknown}"


def test_a_rule_without_a_detector_states_why():
    """'Not machine-checkable' is a status, not a gap left unexplained."""
    for rule_id, entry in detect.RULES.items():
        if entry["kind"] == "prose_only":
            assert entry.get("why"), f"{rule_id} is prose_only but gives no reason"
        else:
            assert callable(entry.get("detector")), f"{rule_id} has no callable detector"


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


def test_the_benchmark_slop_ids_are_a_subset_of_what_the_detector_emits():
    """The anchor map is only honest if its left-hand ids still exist upstream."""
    sys.path.insert(0, str(REPO / "benchmarks" / "judges"))
    import slop_detector as sd

    source = pathlib.Path(sd.__file__).read_text(encoding="utf-8")
    emitted = set(re.findall(r"SLOP-\d{3}", source))
    stray = sorted(set(detect.BENCHMARK_ANCHORS) - emitted)
    assert not stray, f"anchored to slop ids that no longer exist: {stray}"


def test_the_detector_serialises_for_the_cli(tmp_path):
    artifact = tmp_path / "a.html"
    artifact.write_text("<html><body><button>x</button></body></html>", encoding="utf-8")
    out = tmp_path / "out.json"
    payload = detect.scan(artifact)
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    assert json.loads(out.read_text())["detector"] == "craft-floor"

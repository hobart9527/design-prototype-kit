"""Semantic judge determinism: negation boundaries, comment exclusion, and
manifest coverage must never convert restraint or evidence gaps into
fabrication findings. Hermetic: no model invocation.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import semantic_judge  # noqa: E402

TERM = "node-01"
GT = {"unsupported_terms": [TERM]}


def _hits(texts):
    return semantic_judge.deterministic_hits(texts, GT)


def test_english_negation_is_word_boundary_not_substring():
    # Bare "no"/"not" substrings must never excuse a hit: "note", "notice",
    # "nothing", "another" are not negations.
    for snippet in ("note the node-01 mapping", "notice node-01 here",
                    "nothing about node-01", "another node-01 row",
                    "node-01 nope"):
        assert not semantic_judge._is_negated(snippet, TERM), snippet
    # Real negation phrases still count.
    for snippet in ("no node-01 support is provided", "node-01 is not supported",
                    "we do not provide node-01", "node-01 excluded",
                    "node-01 is unsupported", "without node-01",
                    "never use node-01", "cannot ship node-01"):
        assert semantic_judge._is_negated(snippet, TERM), snippet


def test_hits_inside_comments_are_not_render_claims():
    hits = _hits({"a.html": "/* node-01 is unsupported, do not render */\n<div>node-01</div>\n"})
    assert len(hits) == 1 and hits[0]["line"] == 2 and not hits[0]["negated"]
    assert _hits({"a.html": "<!-- node-01 pending -->\n"}) == []
    hits = _hits({"a.html": "line1\n/* node-01\n   more */\n<div>node-01</div>\n"})
    assert len(hits) == 1 and hits[0]["line"] == 4


def test_omission_heading_above_counterexamples():
    # A prose heading mentioning exclusions only binds when it is the nearest
    # heading; a following non-omission heading re-scopes the list.
    assert semantic_judge._omission_heading_above("## Ruthless Omissions\nitem", 25)
    assert not semantic_judge._omission_heading_above(
        "## Ruthless Omissions\nitem\n## Included Features\nother", 45)
    # Plain text without any heading is never an omission context.
    assert not semantic_judge._omission_heading_above("just body text", 5)
    # A heading about features, not omissions, must not negate.
    assert not semantic_judge._omission_heading_above("## Core Features\nitem", 21)


def test_manifest_viewports_read_before_gate(tmp_path):
    evidence = tmp_path / "prototype" / "evidence"
    evidence.mkdir(parents=True)
    manifest = {"verification": {"metadata": {"evidence": {
        "viewport_metrics": {"390x844": {}, "1440x900": {}}}}}}
    (evidence / "handoff-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert semantic_judge._manifest_viewports(tmp_path) == ["1440x900", "390x844"]
    assert semantic_judge._manifest_viewports(tmp_path / "elsewhere") == []


def test_manifest_viewports_union_across_slice_subdirs(tmp_path):
    # A direction-probe run records one manifest per direction subdirectory;
    # coverage is the union, not the first manifest found.
    for sub, viewports in (("dirs-a", {"1440": {}}), ("anchor", {"390": {}})):
        evidence = tmp_path / "prototype" / "evidence" / sub
        evidence.mkdir(parents=True)
        manifest = {"verification": {"metadata": {"evidence": {
            "viewport_metrics": viewports}}}}
        (evidence / "handoff-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert semantic_judge._manifest_viewports(tmp_path) == ["1440", "390"]


def test_judge_records_manifest_coverage_and_truncation(tmp_path):
    evidence = tmp_path / "prototype" / "evidence"
    evidence.mkdir(parents=True)
    manifest = {"verification": {"metadata": {"evidence": {
        "viewport_metrics": {"390x844": {}}}}}}
    (evidence / "handoff-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    big = tmp_path / "big.html"
    big.write_text("x" * 70000, encoding="utf-8")
    case = {"ground_truth": {"unsupported_terms": []}}
    result = semantic_judge.judge(case, tmp_path, tmp_path, use_model=False)
    assert result["recorded_viewports"] == ["390x844"]
    assert "evidence-coverage gaps, not fabrication" in result["note"]
    assert "truncated" in result["note"] and "big.html" in result["note"]

"""CPC-SCN-016: unverified stays unverified, and only real measurements decide.

Hermetic: no network, no browser, no paid judge invocation (BENCH-004).
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import regression_judge  # noqa: E402
import task_judge  # noqa: E402

SCROLL_TASK = {"id": "t", "required_outcomes": [{"id": "scroll", "check": "no_horizontal_scroll"}]}
TOUCH_TASK = {"id": "t", "required_outcomes": [{"id": "touch", "check": "min_touch_target", "px": 44}]}


def _scroll(snapshot):
    return task_judge.judge_task(SCROLL_TASK, {"status": "completed", "steps": [], "snapshots": [snapshot]})


def test_overflow_is_judged_from_the_recorded_dimensions():
    assert _scroll({"scrollWidth": 712, "clientWidth": 390})["status"] == "fail"
    assert _scroll({"scrollWidth": 390, "clientWidth": 712})["status"] == "pass"
    assert _scroll({"scrollWidth": 400, "clientWidth": 400})["status"] == "pass"
    # The probe allows 2px of rounding slop; beyond that it is a real overflow.
    assert _scroll({"scrollWidth": 400, "clientWidth": 400 + task_judge.SCROLL_TOLERANCE_PX})["status"] == "pass"
    assert _scroll({"scrollWidth": 400 + task_judge.SCROLL_TOLERANCE_PX + 1, "clientWidth": 400})["status"] == "fail"


def test_missing_or_invalid_measurements_are_unverified_never_pass():
    # The old judge read a missing `horizontal_scroll` boolean as falsy and passed.
    for snapshot in ({}, {"scrollWidth": 400}, {"clientWidth": 400},
                     {"scrollWidth": None, "clientWidth": None},
                     {"scrollWidth": "712", "clientWidth": 390},
                     {"scrollWidth": True, "clientWidth": False},
                     {"scrollWidth": float("nan"), "clientWidth": 390},
                     {"scrollWidth": -1, "clientWidth": -1}):
        result = _scroll(snapshot)
        assert result["status"] == "unverified", snapshot
        assert result["unmet"] == ["scroll"] and result["unverified_outcomes"] == ["scroll"], snapshot


def test_touch_target_evidence_must_be_recorded():
    # The probe records small_target_count only when it runs the touch dimension;
    # absence means no control was smaller than the threshold, not a missing field.
    assert task_judge.judge_task(TOUCH_TASK, {"status": "completed", "snapshots": [
        {"small_target_count": 0}]})["status"] == "pass"
    assert task_judge.judge_task(TOUCH_TASK, {"status": "completed", "snapshots": [
        {"small_target_count": 3}]})["status"] == "fail"
    absent = task_judge.judge_task(TOUCH_TASK, {"status": "completed", "snapshots": [{}]})
    assert absent["status"] == "unverified"
    assert absent["required_outcomes"][0]["check"] == "min_touch_target"
    invalid = task_judge.judge_task(TOUCH_TASK, {"status": "completed", "snapshots": [
        {"small_target_count": "0"}]})
    assert invalid["status"] == "unverified"


def test_verified_dimension_survives_an_unverifiable_sibling():
    task = SCROLL_TASK | {"required_outcomes": SCROLL_TASK["required_outcomes"] + [
        {"id": "touch", "check": "min_touch_target", "px": 44},
        {"id": "text", "check": "text_present", "pattern": "worker"}]}
    trace = {"status": "completed", "steps": [], "snapshots": [
        {"scrollWidth": 390, "clientWidth": 390, "text": "worker-07"}]}
    result = task_judge.judge_task(task, trace)
    assert result["status"] == "unverified"
    by_id = {r["id"]: r["status"] for r in result["required_outcomes"]}
    assert by_id["scroll"] == "pass" and by_id["text"] == "pass"
    assert by_id["touch"] == "unverified"
    assert result["unmet"] == ["touch"] and result["unverified_outcomes"] == ["touch"]


def _run(case_id, variant, repeat, runtime, semantic, task):
    return {"case_id": case_id, "variant": variant, "repeat": repeat,
            "runtime": {"status": runtime}, "semantic": {"hard_gate": semantic}, "task": {"status": task}}


def test_both_arms_unverified_is_not_an_improvement():
    verdict = regression_judge.judge([
        _run("c", "stable_skill", 1, "unverified", "pass", "pass"),
        _run("c", "candidate_skill", 1, "unverified", "pass", "pass")])
    assert verdict["verdict"] != "PASS"  # never a clean pass on an unverified dimension
    assert verdict["regressions"] == [] and verdict["improvements"] == []
    assert [d["dimension"] for d in verdict["unverifiable_dimensions"]] == ["runtime"]
    # The verified dimensions still count: semantic and task were both compared.
    assert verdict["verified_dimensions"] == [
        {"case_id": "c", "repeat": 1, "dimension": d, "stable": "pass", "candidate": "pass"}
        for d in ("semantic", "task")]
    assert verdict["compared_dimensions"] == 3


def test_failed_to_unverified_is_not_an_improvement():
    verdict = regression_judge.judge([
        _run("c", "stable_skill", 1, "fail", "pass", "pass"),
        _run("c", "candidate_skill", 1, "unverified", "pass", "pass")])
    assert verdict["verdict"] != "PASS"
    assert verdict["improvements"] == [] and verdict["regressions"] == []
    assert verdict["unverifiable_dimensions"][0] == {
        "case_id": "c", "repeat": 1, "dimension": "runtime", "stable": "fail", "candidate": "unverified"}


def test_unverified_to_unverified_is_not_a_verified_pass():
    verdict = regression_judge.judge([
        _run("c", "stable_skill", 1, "pass", "unverified", "unverified"),
        _run("c", "candidate_skill", 1, "pass", "unverified", "unverified")])
    assert verdict["verdict"] == "PASS_WITH_UNKNOWNS"
    assert verdict["verified_dimensions"] == [
        {"case_id": "c", "repeat": 1, "dimension": "runtime", "stable": "pass", "candidate": "pass"}]
    assert [d["dimension"] for d in verdict["unverifiable_dimensions"]] == ["semantic", "task"]

    # With nothing verified at all, there is no comparison to report.
    nothing = regression_judge.judge([
        _run("c", "stable_skill", 1, "unverified", "unverified", "unverified"),
        _run("c", "candidate_skill", 1, "unverified", "unverified", "unverified")])
    assert nothing["verdict"] == "INCONCLUSIVE"
    assert nothing["compared_dimensions"] == 3 and nothing["verified_dimensions"] == []


def test_genuine_regression_and_improvement_still_reported():
    regression = regression_judge.judge([
        _run("c", "stable_skill", 1, "pass", "pass", "pass"),
        _run("c", "candidate_skill", 1, "fail", "pass", "pass")])
    assert regression["verdict"] == "REGRESSION"
    assert regression["regressions"][0]["dimension"] == "runtime"

    improvement = regression_judge.judge([
        _run("c", "stable_skill", 1, "fail", "pass", "pass"),
        _run("c", "candidate_skill", 1, "pass", "pass", "pass")])
    assert improvement["verdict"] == "PASS"
    assert improvement["improvements"][0]["dimension"] == "runtime"
    assert improvement["regressions"] == []


def test_partial_evidence_yields_pass_with_unknowns_not_a_clean_pass():
    verdict = regression_judge.judge([
        _run("c", "stable_skill", 1, "pass", "unverified", "pass"),
        _run("c", "candidate_skill", 1, "pass", "unverified", "pass")])
    assert verdict["verdict"] == "PASS_WITH_UNKNOWNS"
    assert [d["dimension"] for d in verdict["unverifiable_dimensions"]] == ["semantic"]

    # A missing pair and a missing dimension are still NOT a pass.
    assert regression_judge.judge([])["verdict"] == "INCONCLUSIVE"
    unpaired = regression_judge.judge([_run("c", "candidate_skill", 1, "pass", "pass", "pass")])
    assert unpaired["verdict"] == "INCONCLUSIVE"
    assert unpaired["missing_pairs"][0]["why"] == "no stable_skill pair"
    empty_dimensions = regression_judge.judge([
        {"case_id": "c", "variant": "stable_skill", "repeat": 1},
        {"case_id": "c", "variant": "candidate_skill", "repeat": 1}])
    assert empty_dimensions["verdict"] == "INCONCLUSIVE"
    assert empty_dimensions["compared_dimensions"] == 0

"""Task-trace protocol: done means proven success, fill is explicit, layout survives step_limit.

Hermetic: the browser session and the task agent are faked (BENCH-004).
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import run_task_trace as rtt  # noqa: E402
import task_judge  # noqa: E402

PAGE = {"text": "待审批 PO-0002 金额 ¥23,500", "controls": [
    {"index": 0, "role": "textbox", "name": "审批意见", "actions": ""},
    {"index": 1, "role": "button", "name": "通过", "actions": "approve"}]}
DONE_PAGE = {"text": "PO-0002 已通过，审批记录：10/16 通过", "controls": []}


class FakeSession:
    def __init__(self, url, viewport):
        self.sent = []

    def send(self, **cmd):
        self.sent.append(cmd)
        if cmd["cmd"] == "click":
            return {"click": {"clicked": "通过"}, "snapshot": DONE_PAGE}
        if cmd["cmd"] == "fill":
            return {"fill": {"filled": "审批意见", "value": cmd["value"]}, "snapshot": PAGE}
        if cmd["cmd"] in ("snapshot", "wait", "scroll"):
            return {"snapshot": PAGE}
        return {}

    def close(self):
        pass


def _run(monkeypatch, tmp_path, decisions, max_steps=6):
    replies = iter(decisions)
    sessions = []

    def session_factory(url, viewport):
        sessions.append(FakeSession(url, viewport))
        return sessions[-1]

    monkeypatch.setattr(rtt, "BrowserSession", session_factory)
    monkeypatch.setattr(rtt.bl, "find_entry", lambda d: "index.html")
    monkeypatch.setattr(rtt.bl, "serve_dir", lambda d: ("http://x", lambda: None))
    monkeypatch.setattr(rtt.bl, "ask_json", lambda *a, **k: {"ok": True, "data": next(replies), "metrics": {}})
    trace = rtt.run_task({}, {"id": "t", "goal": "g"}, tmp_path, tmp_path, model=None,
                         max_steps=max_steps, timeout_s=1)
    return trace, sessions[0].sent


def test_done_without_page_evidence_is_not_completion(monkeypatch, tmp_path):
    trace, _ = _run(monkeypatch, tmp_path, [{"action": "done", "evidence": "已通过"}] * 2, max_steps=2)
    assert trace["status"] == "step_limit"
    assert all("done rejected" in s["error"] for s in trace["steps"])


def test_done_with_terminal_quote_completes(monkeypatch, tmp_path):
    trace, _ = _run(monkeypatch, tmp_path, [
        {"action": "click", "target_index": 1},
        {"action": "done", "evidence": "PO-0002 已通过"}])
    assert trace["status"] == "completed" and trace["evidence"] == "PO-0002 已通过"


def test_dead_end_and_missing_action_are_not_completed(monkeypatch, tmp_path):
    stuck, _ = _run(monkeypatch, tmp_path, [{"action": "stuck", "reason": "no slot control"}])
    assert stuck["status"] == "dead_end"
    missing, _ = _run(monkeypatch, tmp_path, [{"reason": "?"}])
    assert missing["status"] == "blocked"


def test_fill_is_explicit_and_records_its_value(monkeypatch, tmp_path):
    trace, sent = _run(monkeypatch, tmp_path, [
        {"action": "fill", "target_index": 0, "value": "金额核对无误"},
        {"action": "fill", "target_index": 0, "value": ""},
        {"action": "wait"},
        {"action": "click", "target_index": 1},
        {"action": "done", "evidence": "审批记录"}])
    assert trace["status"] == "completed"
    assert trace["steps"][0]["value"] == "金额核对无误"
    assert "non-empty" in trace["steps"][1]["error"]
    cmds = [c["cmd"] for c in sent]
    assert cmds.count("fill") == 1 and "wait" in cmds
    assert {"cmd": "fill", "match_index": 0, "value": "金额核对无误"} in sent


def test_click_never_types_text():
    probe = (REPO / "benchmarks" / "runners" / "browser_probe.mjs").read_text(encoding="utf-8")
    click_js = probe.split("const CLICK_JS", 1)[1].split("const FILL_JS", 1)[0]
    assert ".value =" not in click_js and "selectedIndex" not in click_js


def test_task_prompt_carries_no_case_specific_walkthrough():
    prompt = (REPO / "benchmarks" / "prompts" / "task-agent.txt").read_text(encoding="utf-8")
    for leaked in ("挑一笔", "审批记录", "替代方案", "留下意见", "换一个时段", "付定金"):
        assert leaked not in prompt


TASK = {"id": "t", "required_outcomes": [
    {"id": "approved", "check": "text_present", "pattern": "已通过"},
    {"id": "scroll", "check": "no_horizontal_scroll"},
    {"id": "touch", "check": "min_touch_target", "px": 44}]}
LAYOUT_OK = {"scrollWidth": 390, "clientWidth": 390, "smallTargetCount": 0}


def test_step_limit_keeps_layout_measurements_but_fails_the_goal():
    result = task_judge.judge_task(TASK, {"status": "step_limit", "snapshots": [
        dict(LAYOUT_OK, text="PO-0002 已通过")]})
    by_id = {r["id"]: r["status"] for r in result["required_outcomes"]}
    assert by_id == {"approved": "fail", "scroll": "pass", "touch": "pass"}
    assert result["status"] == "fail"
    # A layout-only task is judged on its measurement, not on the journey budget.
    touch_only = {"id": "touch", "required_outcomes": [TASK["required_outcomes"][2]]}
    assert task_judge.judge_task(touch_only, {"status": "step_limit", "snapshots": [LAYOUT_OK]})["status"] == "pass"


def test_completion_needs_terminal_evidence_not_any_snapshot_keyword():
    """Two gates: the terminal claim must be on the final page, the required text anywhere in the journey.

    A quote that is visible but unrelated to the goal proves protocol completion, not
    task success. Layout checks are measurements and stay independent of the journey.
    """
    goal_page = dict(LAYOUT_OK, text="PO-0002 已通过 · 审批完成")
    list_page = dict(LAYOUT_OK, text="待审批 列表 · 暂无申请")
    unrelated = task_judge.judge_task(TASK, {
        "status": "completed", "evidence": "待审批 列表", "snapshots": [list_page],
    })
    assert unrelated["status"] == "fail"
    assert unrelated["required_outcomes"][0]["status"] == "fail"
    assert unrelated["required_outcomes"][1]["status"] == "pass"
    # The pattern is in the journey, but the done quote is not on the final page.
    stale = task_judge.judge_task(TASK, {
        "status": "completed", "evidence": "PO-0002 已通过", "snapshots": [goal_page, list_page],
    })
    assert stale["status"] == "fail"
    assert stale["required_outcomes"][0]["status"] == "fail"
    # An outcome the agent discovered earlier still counts once the terminal claim lands.
    later_page = dict(LAYOUT_OK, text="本次审批完成，记录已保存")
    discovered = task_judge.judge_task(TASK, {
        "status": "completed", "evidence": "本次审批完成", "snapshots": [goal_page, later_page],
    })
    assert discovered["status"] == "pass"
    proven = task_judge.judge_task(TASK, {
        "status": "completed", "evidence": "PO-0002 已通过", "snapshots": [list_page, goal_page],
    })
    assert proven["status"] == "pass"
    unproven = task_judge.judge_task(TASK, {"status": "completed", "snapshots": [goal_page]})
    assert unproven["status"] == "unverified"
    for dead in ("dead_end", "blocked", "step_limit"):
        assert task_judge.judge_task(TASK, {"status": dead, "snapshots": [goal_page]})["status"] != "pass"

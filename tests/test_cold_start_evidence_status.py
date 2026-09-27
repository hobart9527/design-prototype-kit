#!/usr/bin/env python3
"""Regression: cold-start evidence-status honesty in check-discussion.py.

An [explicit] status claims a verbatim source statement; the checker must
refuse an uncited one, and the Seed confirmation Gate must never claim user
confirmation is complete (a sealed provisional contract is the claim that
confirmation is still pending).
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile

CHECKER = pathlib.Path(__file__).resolve().parents[1] / "skills/spec-prototype/scripts/check-discussion.py"


def _run_checker(discussion_text: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        proto = pathlib.Path(tmp) / "prototype"
        proto.mkdir()
        (proto / "discussion.md").write_text(discussion_text, encoding="utf-8")
        proc = subprocess.run([sys.executable, str(CHECKER), str(proto / "discussion.md")],
                              capture_output=True, text=True)
        return proc.returncode, (proc.stderr or proc.stdout).strip()


_COLD_START = """## Resume
- Execution boundary: active
- Active track / current decision: Stage 1
- Route basis: IA-first
- Requested scope and stopping point: V1
- Pending prerequisite: none
- Next action and its prerequisite: compile

## Cold-start inference & seed status
%s
## Next section
"""


def test_explicit_without_citation_is_refused():
    cold = """- Actor: `[explicit]` 值班 SRE、主指挥官
- Use scene: `[derived]` 大屏值班
- Information priority: `[derived]` 影响面
- Main journey: `[derived]` 感知->定位->排空
- Style tone: `[derived]` 工业控制台
- Scene sentence: s
- Anti-slop match-and-refuse bans: b
- Seed confirmation Gate: `[derived]` brief 给出角色与场景；其余为推导。
"""
    code, out = _run_checker(_COLD_START % cold)
    assert code == 1
    assert "[explicit] without citing" in out


def test_explicit_with_cited_passage_passes():
    cold = """- Actor: `[explicit]` “值班 SRE 会在大屏上干活”——brief.md 第 2 段原文
- Use scene: `[derived]` 大屏值班
- Information priority: `[derived]` 影响面
- Main journey: `[derived]` 感知->定位->排空
- Style tone: `[derived]` 工业控制台
- Scene sentence: s
- Anti-slop match-and-refuse bans: b
- Seed confirmation Gate: `[explicit]` brief.md 逐条给出角色/场景，其余推导。
"""
    code, out = _run_checker(_COLD_START % cold)
    assert code == 0, out


def test_seed_gate_cannot_claim_full_confirmation():
    cold = """- Actor: `[explicit]` “值班 SRE”——brief.md 原文
- Use scene: `[explicit]` 大屏——brief.md “用的人基本都在桌面大屏上干活”
- Information priority: `[derived]` 影响面
- Main journey: `[derived]` 感知->定位->排空
- Style tone: `[derived]` 工业控制台
- Scene sentence: s
- Anti-slop match-and-refuse bans: b
- Seed confirmation Gate: `[explicit]` 需求已完全固化在 brief.md，无需额外用户输入，直接展开工程落地。
"""
    code, out = _run_checker(_COLD_START % cold)
    assert code == 1
    assert "confirmation is still pending" in out


def test_derived_honest_gate_passes():
    cold = """- Actor: `[derived]` 值班 SRE（brief 第 1 段）
- Use scene: `[derived]` 大屏值班
- Information priority: `[derived]` 影响面
- Main journey: `[derived]` 感知->定位->排空
- Style tone: `[derived]` 工业控制台
- Scene sentence: s
- Anti-slop match-and-refuse bans: b
- Seed confirmation Gate: `[derived]` brief 明确角色与场景（第 1-2 段）；风格与旅程为推导。
"""
    code, out = _run_checker(_COLD_START % cold)
    assert code == 0, out


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))

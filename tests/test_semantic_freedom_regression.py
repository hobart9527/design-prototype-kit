"""CPC-003 / CPC-004 end-to-end regression defense for semantic freedom.

Four seams, no invented fact at any of them:

1. The token compiler stays neutral when no dial is authored.
2. The envelope offers advisory candidate patterns instead of locking one.
3. The Builder contract is bounded by the five integrity categories.
4. The Critic evaluates the accessibility floor without aesthetic gatekeeping.

These are mechanism checks against the authored seam, not live-session evidence.
Every fixture lives in `tmp_path`; the repository is read, never written.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/spec-prototype/scripts"
sys.path.insert(0, str(SCRIPTS))

import assemble_envelope  # noqa: E402
import compile_tokens  # noqa: E402
BUILDER = ROOT / "agents/spec-prototype-builder.md"
CRITIC = ROOT / "agents/spec-prototype-critic.md"
SLICE = "console"

# --- seam 1: token compilation stays neutral ---------------------------------



def test_token_compilation_stays_neutral_without_authored_dials():
    tokens = compile_tokens.compute_tokens({})
    colors = tokens["colors"]

    def channel(hex_code: str) -> tuple[int, int, int]:
        raw = hex_code.lstrip("#")
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)

    def is_gray(hex_code: str) -> bool:
        r, g, b = channel(hex_code)
        return max(r, g, b) - min(r, g, b) == 0

    assert is_gray(colors["accent_primary"])
    assert is_gray(colors["bg_void"])
    assert colors["accent_primary"] != "#d6f56b"  # no remembered lime accent
    assert colors["bg_void"] != "#080b0b"  # no remembered industrial void
    css = compile_tokens.generate_css(tokens)
    assert "machined-industrial" not in css


# --- seam 2: envelope candidate patterns stay advisory ------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --- seam 3: builder contract bounded by five integrity categories -----------


def test_builder_contract_is_bounded_by_the_five_integrity_categories():
    text = BUILDER.read_text(encoding="utf-8")
    for category in ("Semantic Integrity", "Task Integrity", "Accessibility Integrity",
                     "State & Recovery Integrity", "Platform Integrity"):
        assert category in text, f"builder contract dropped {category}"
    assert "Five Core Integrity Categories" in text


# --- seam 4: critic evaluates the floor, not aesthetic taste ------------------


def test_critic_keeps_three_craft_invariants_hard_and_aesthetic_craft_advisory():
    # Markdown wraps prose, so compare against a whitespace-normalized copy.
    text = re.sub(r"\s+", " ", CRITIC.read_text(encoding="utf-8"))
    assert "hard defects whenever their stated scope applies" in text
    assert "R_in = max(0, R_out - P)" in text
    assert "font-variant-numeric: tabular-nums" in text
    assert "press physics, or typography choices remain advisory" in text
    assert "SHALL NOT fail a build" not in text
    assert "hard defects whenever their stated scope applies" in text
    assert "press physics, or typography choices remain advisory" in text


# --- seam 5: semantic judge correctly recognizes exclusion markers -----------


def test_semantic_judge_recognizes_cross_emoji_and_bullet_omissions():
    sys.path.insert(0, str(ROOT / "benchmarks/judges"))
    import semantic_judge

    # 1. Bullet list with cross emoji
    sample_line = '- ❌ 自动排空 / 自动修复 / 预测性扩容(speculation automation)'
    assert semantic_judge._is_negated(sample_line, "自动修复")
    assert semantic_judge._is_negated(sample_line, "自动排空")

    # 2. Heading with list bullet prefix
    sample_text = (
        "- **Ruthless Omissions (第一版不做 · 显式反向边界)**:\n"
        "  - 自动排空 / 自动修复 / 预测性扩容\n"
        "  - 值班排班、聊天/通知集成、工单系统对接\n"
        "\n## Success metrics\n"
        "M1: 步数\n"
    )
    m = re.search(r"排班", sample_text)
    assert m is not None
    assert semantic_judge._omission_heading_above(sample_text, m.start())

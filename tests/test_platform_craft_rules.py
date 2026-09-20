"""CRR-SCN-004 / T-03: somatic touch ergonomics and optical geometry contract.

Both the Builder and the Critic role instructions must carry the same
non-negotiable craft rules: mobile safe-area insets, minimum 44x44px touch
targets, :active spring micro-feedback, the concentric nested-radius formula
R_in = max(0, R_out - P), and tabular-nums for telemetry/financial metrics.
These assertions are instruction wiring: they prove the contract text names the
constraints the Task authorizes, not that a live Builder or Critic executed.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

BUILDER = REPO_ROOT / "agents/spec-prototype-builder.md"
CRITIC = REPO_ROOT / "agents/spec-prototype-critic.md"
CONSUMERS = {"builder": BUILDER, "critic": CRITIC}


def role_text(name: str) -> str:
    return CONSUMERS[name].read_text(encoding="utf-8")


# --- somatic mobile ergonomics --------------------------------------------


def test_role_instruction_requires_mobile_safe_area_insets():
    for role, path in CONSUMERS.items():
        text = role_text(role)
        assert "env(safe-area-inset-*)" in text, f"{role} omits safe-area insets"


def test_role_instruction_requires_minimum_touch_target():
    for role, path in CONSUMERS.items():
        text = role_text(role)
        assert "44" in text, f"{role} omits the touch target floor"
        assert "44x44" in text or "44×44" in text, (
            f"{role} does not state the 44x44 touch target"
        )


def test_role_instruction_requires_active_spring_micro_feedback():
    for role, path in CONSUMERS.items():
        text = role_text(role)
        assert ":active" in text, f"{role} omits :active micro-feedback"
        assert re.search(r"spring", text, re.IGNORECASE), (
            f"{role} does not name spring micro-feedback"
        )


# --- concentric nested radius geometry ------------------------------------


def test_role_instruction_states_concentric_radius_formula():
    for role, path in CONSUMERS.items():
        text = role_text(role)
        normalized = text.replace(" ", "")
        assert "R_in" in text and "R_out" in text, (
            f"{role} does not name the inner/outer radii"
        )
        assert re.search(r"R_?in\s*=\s*max\s*\(\s*0\s*,\s*R_?out\s*-\s*P\s*\)", text), (
            f"{role} does not state R_in = max(0, R_out - P)"
        )
        assert normalized, f"{role} radius formula lost to whitespace stripping"


# --- numeric stability ------------------------------------------------------


def test_role_instruction_requires_tabular_numerals_for_metrics():
    for role, path in CONSUMERS.items():
        text = role_text(role)
        assert "tabular-nums" in text, f"{role} omits tabular-nums"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(__import__("pytest").main([__file__, "-q"]))

"""Test suite enforcing Canonical v10.1 Ontology invariants across forced-read documents.

Enforces:
1. Zero legacy Gear Chains in the active router and references.
2. Zero Six-Pillar Spec references (must be Nine Pillars).
3. Zero Baseline-exclusive classifier definitions in the active router.
4. Clean separation of Invariants vs Techniques in runtime instructions.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/spec-prototype"


def test_no_legacy_gear_chains_in_workflow():
    """Gear-chain retirement is asserted against the active always-loaded router."""
    router_path = SKILL / "SKILL.md"
    content = router_path.read_text(encoding="utf-8")
    kernel_path = SKILL / "references/core-kernel.md"
    content += kernel_path.read_text(encoding="utf-8")

    # Must not contain legacy gear chains as active ontology
    assert "业务本体传动链" not in content
    assert "空间拓扑与物理传动链" not in content
    assert "感官能量传动链" not in content
    assert "神经机械传动链" not in content
    assert "Ontology Chain" not in content
    assert "Physicality & Topology Chain" not in content
    assert "Energy & Chromatics Chain" not in content
    assert "Mechanics & Stress Chain" not in content


def test_canonical_nine_pillars_in_workflow():
    """Nine Pillars ownership lives in the active router and core kernel."""
    router_path = SKILL / "SKILL.md"
    content = router_path.read_text(encoding="utf-8")
    kernel_path = SKILL / "references/core-kernel.md"
    content += kernel_path.read_text(encoding="utf-8")

    # Must use canonical Nine Pillars
    assert "Nine Pillars" in content
    assert "Value" in content
    assert "Research" in content
    assert "Object" in content
    assert "Journey" in content
    assert "Topology" in content
    assert "Attention" in content
    assert "Expression" in content
    assert "Interaction" in content
    assert "Resilience" in content


def test_quality_floor_separates_invariants_and_techniques():
    quality_floor = SKILL / "references/03-verification/quality-floor.md"
    content = quality_floor.read_text(encoding="utf-8")

    # Floor must focus on absolute closure and invariants
    assert "The Floor (Absolute closure — zero tolerance)" in content
    assert "WCAG 2.2 AA" in content
    assert "Quality Criteria (Craft, conviction, and resonance)" in content


BUILDER = REPO / "agents/spec-prototype-builder.md"


def _builder_content() -> str:
    return BUILDER.read_text(encoding="utf-8")


def test_builder_defines_five_core_integrity_categories():
    content = _builder_content()

    # The five categories are the declared integrity boundaries.
    assert "The Five Core Integrity Categories" in content
    for category in (
        "Semantic Integrity",
        "Task Integrity",
        "Accessibility Integrity",
        "State & Recovery Integrity",
        "Platform Integrity",
    ):
        assert category in content, f"missing integrity category: {category}"


def test_builder_enforces_integrity_against_vacuous_passes():
    content = _builder_content()

    # Integrity is only met by exercised, observable behavior — not a clean render.
    assert "Consequential Task Exercise" in content
    assert "Declarative State Machine & Hash Routing" in content
    assert "Feedback Closure" in content
    assert "Required States" in content
    # Platform facts that are unauthored stay unknown rather than invented.
    assert "remain `unknown`" in content or "record such native validation as `unverified`" in content


def test_builder_excludes_prescriptive_heuristics():
    content = _builder_content()

    # Categories are guidance to adapt, never a fixed checklist or mechanical mapping.
    normalized = re.sub(r"\s+", " ", content)
    assert "not a fixed aesthetic checklist" in normalized
    assert "not compliance mandates" in normalized
    assert "Do not turn an axis into a fixed pixel checklist" in normalized
    # Target runtime must never be mechanically inferred from device/input signals.
    assert "Touch interaction, mobile viewport dimensions" not in content
    assert "Never edit OpenSpec" in content

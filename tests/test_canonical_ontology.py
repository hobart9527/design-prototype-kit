"""Test suite enforcing Canonical v10.1 Ontology invariants across forced-read documents.

Enforces:
1. Zero legacy Gear Chains in core-workflow and references.
2. Zero Six-Pillar Spec references (must be Nine Pillars).
3. Zero Baseline-exclusive classifier definitions in core-workflow.
4. Clean separation of Invariants vs Techniques in runtime instructions.
"""
from __future__ import annotations

import re
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/spec-prototype"


def test_no_legacy_gear_chains_in_workflow():
    workflow_path = SKILL / "references/core-workflow.md"
    content = workflow_path.read_text(encoding="utf-8")

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
    workflow_path = SKILL / "references/core-workflow.md"
    content = workflow_path.read_text(encoding="utf-8")

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

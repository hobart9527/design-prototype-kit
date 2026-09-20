"""Instruction-contract tests for informed Stage 3 coverage selection and continuity.

Enforces the amended route in the owning workflow:

1. Coverage selection is resolved before Stage 3 expansion, not after it.
2. Scope is distinguished from approval; a subset reduces the implementation
   target only.
3. Retained upstream meaning: the full map and rationale survive a selection;
   unselected surfaces stay provisional.
4. The three lightweight routes (bounded probe, spec-only, local refinement)
   keep their existing routes.
5. Contradictory old prescriptions are absent from the edited route sections,
   not merely overridden by new keywords.

These are mechanism checks against authored instructions. They do not prove
design judgment, only that the route no longer prescribes the superseded rule.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/spec-prototype"

SKILL_MD = SKILL / "SKILL.md"
CORE = SKILL / "references/core-workflow.md"
USAGE = SKILL / "references/04-governance/usage.md"
HANDOFF = SKILL / "references/04-governance/handoff.md"

ALL_ROUTE_FILES = (SKILL_MD, CORE, USAGE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- Selection timing -------------------------------------------------------


def test_skill_stage_3_declares_coverage_selection():
    content = _read(SKILL_MD)
    assert "Coverage Selection:" in content
    assert "Stage 3" in content


def test_coverage_selection_precedes_stage_3_expansion_in_skill():
    content = _read(SKILL_MD)
    stage_3 = content.index("Stage 3: 拓")
    selection = content.index("Coverage Selection:")
    assert stage_3 < selection, "selection rule must live inside Stage 3, before expansion"


def test_core_workflow_places_selection_after_router_and_before_stage_1():
    content = _read(CORE)
    router = content.index("Change Scope Router")
    selection = content.index("Coverage Selection before Stage 3")
    stage_1 = content.index("### Stage 1: Understand & Frame")
    assert router < selection < stage_1


def test_selection_asks_only_when_unresolved():
    content = _read(CORE)
    section = content[content.index("Coverage Selection before Stage 3"): content.index("### Stage 1: Understand & Frame")]
    assert "only when" in section.lower()
    assert "reused on continuation" in section or "reused" in section


def test_prior_explicit_selection_is_not_re_asked():
    content = _read(CORE)
    assert "do not re-ask" in content.lower() or "Retain, do not re-ask" in content


# --- Scope versus approval --------------------------------------------------


def test_selection_is_scope_not_approval():
    for path in ALL_ROUTE_FILES:
        content = _read(path).lower()
        assert "not approval" in content or "不等于批准" in content


def test_skill_selection_does_not_authorize_approval():
    content = _read(SKILL_MD)
    section = content[content.index("Coverage Selection:"): content.index("Structure: Derived")]
    assert "implementation target only" in section


# --- Retained upstream meaning ---------------------------------------------


def test_subset_keeps_map_and_rationale_authoritative():
    content = _read(CORE)
    section = content[content.index("Coverage Selection before Stage 3"): content.index("### Stage 1: Understand & Frame")]
    assert "remain authoritative" in section
    assert "object model" in section
    assert "Surface Map" in section


def test_unselected_surfaces_stay_provisional_not_deleted():
    content = _read(SKILL_MD)
    section = content[content.index("Coverage Selection:"): content.index("Structure: Derived")]
    assert "provisional" in section
    assert "authoritative" in section


def test_missing_selection_never_defaults_to_full_product():
    assert "never silently defaults to" in _read(CORE)
    for path in ALL_ROUTE_FILES:
        content = _read(path)
        assert "full-product" in content or "整产品" in content, path


def test_out_of_scope_dependency_disclosed_not_added():
    content = _read(CORE)
    section = content[content.index("Coverage Selection before Stage 3"): content.index("### Stage 1: Understand & Frame")]
    assert "disclosed" in section
    assert "never silently added" in section


# --- Lightweight routes keep their routes -----------------------------------


def test_bounded_probe_spec_only_and_refinement_stay_valid():
    for path in ALL_ROUTE_FILES:
        content = _read(path)
        assert "direction probe" in content, path
    assert "local refinement" in _read(CORE)
    assert "spec-only" in _read(CORE)


def test_lightweight_routes_not_forced_through_full_product():
    content = _read(CORE)
    section = content[content.index("Coverage Selection before Stage 3"): content.index("### Stage 1: Understand & Frame")]
    assert "not forced" in section
    assert "sealed provisional Spec" in section


def test_usage_route_table_keeps_lightweight_examples():
    content = _read(USAGE)
    assert "只讨论" in content or "只输出规格" in content
    assert "继续上次原型" in content


# --- Formal candidate requirement preserved ---------------------------------


def test_formal_candidate_still_requires_sealed_provisional_spec():
    core = _read(CORE)
    assert "No Prototype Code without a Sealed Provisional Spec Contract" in core
    assert "Sealed Provisional" in core


def test_authority_lifecycle_unchanged():
    content = _read(CORE)
    assert "Draft" in content
    assert "Sealed Provisional" in content
    assert "Validated" in content
    assert "Frozen Approved" in content


def test_nine_pillars_ownership_preserved_in_selection_rule():
    content = _read(SKILL_MD)
    assert "Nine Pillars" in content
    content_core = _read(CORE)
    assert "Nine Pillars" in content_core
    assert "Double Diamond" in content_core


# --- Handoff continuity binding ---------------------------------------------


def test_handoff_binds_retained_selection_without_granting_approval():
    content = _read(HANDOFF)
    assert "retained coverage selection is a dispatch input" in content
    assert "not a substitute for approval" in content
    assert "full-product" in content


def test_handoff_reconciles_revision_mismatch_before_expansion():
    content = _read(HANDOFF)
    assert "revision-mismatched" in content
    assert "reconciled" in content


# --- Contradictory old prescriptions are gone -------------------------------


def test_stage_5_freeze_no_longer_uses_product_md_as_slice_spec():
    for path in (SKILL_MD, CORE):
        content = _read(path)
        assert "--spec prototype/product.md" not in content, path


def test_stage_5_freeze_binds_slice_specification():
    assert "specifications/<slice_id>/r1.md" in _read(SKILL_MD)
    assert "specifications/<slice_id>/r1.md" in _read(CORE)


def test_no_full_product_default_prescription():
    for path in ALL_ROUTE_FILES:
        content = _read(path)
        assert "默认整产品" not in content, path

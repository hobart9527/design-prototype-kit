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
CORE_KERNEL = SKILL / "references/core-kernel.md"
STAGE_3 = SKILL / "references/stages/stage-3-skeleton.md"
STAGE_5 = SKILL / "references/stages/stage-5-freeze.md"
USAGE = SKILL / "references/04-governance/usage.md"
HANDOFF = SKILL / "references/04-governance/handoff.md"

ALL_ROUTE_FILES = (SKILL_MD, STAGE_3, USAGE)


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


def test_stage_3_places_selection_after_coverage_heading_and_before_topology():
    content = _read(STAGE_3)
    selection = content.index("Coverage Selection before Expansion")
    router = content.index("Derived Surface Topology Rollout")
    assert selection < router, "selection rule must precede Stage 3 expansion"


def test_selection_asks_only_when_unresolved():
    content = _read(STAGE_3)
    section = content[content.index("Coverage Selection before Expansion"): content.index("Derived Surface Topology Rollout")]
    assert "only when" in section.lower()


def test_prior_explicit_selection_is_not_re_asked():
    content = _read(STAGE_3)
    assert "Retain, do not re-ask" in content


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
    content = _read(STAGE_3)
    section = content[content.index("Coverage Selection before Expansion"): content.index("Derived Surface Topology Rollout")]
    assert "authoritative" in section
    assert "object model" in section
    assert "Surface Map" in section


def test_unselected_surfaces_stay_provisional_not_deleted():
    content = _read(SKILL_MD)
    section = content[content.index("Coverage Selection:"): content.index("Structure: Derived")]
    assert "provisional" in section
    assert "authoritative" in section


def test_missing_selection_never_defaults_to_full_product():
    assert "never silently defaults to" in _read(STAGE_3)
    for path in ALL_ROUTE_FILES:
        content = _read(path)
        assert "full-product" in content or "整产品" in content, path


def test_out_of_scope_dependency_disclosed_not_added():
    content = _read(STAGE_3)
    section = content[content.index("Coverage Selection before Expansion"): content.index("Derived Surface Topology Rollout")]
    assert "disclosed" in section
    assert "never silently added" in section


# --- Lightweight routes keep their routes -----------------------------------


def test_bounded_probe_spec_only_and_refinement_stay_valid():
    for path in ALL_ROUTE_FILES:
        content = _read(path)
        assert "direction probe" in content, path
    assert "local refinement" in _read(STAGE_3)
    assert "spec-only" in _read(STAGE_3)


def test_lightweight_routes_not_forced_through_full_product():
    content = _read(STAGE_3)
    section = content[content.index("Coverage Selection before Expansion"): content.index("Derived Surface Topology Rollout")]
    assert "not forced" in section
    assert "sealed provisional" in section.lower()


def test_usage_route_table_keeps_lightweight_examples():
    content = _read(USAGE)
    assert "只讨论" in content or "只输出规格" in content
    assert "继续上次原型" in content


# --- Formal candidate requirement preserved ---------------------------------


def test_formal_candidate_still_requires_sealed_provisional_spec():
    kernel = _read(CORE_KERNEL)
    assert "Sealed Provisional Spec Contract" in kernel
    assert "Sealed Provisional" in kernel


def test_authority_lifecycle_unchanged():
    content = _read(CORE_KERNEL)
    assert "Draft" in content
    assert "Sealed Provisional" in content
    assert "Validated" in content
    assert "Frozen Approved" in content


def test_authority_lifecycle_delegates_to_artifact_lifecycle():
    kernel = _read(CORE_KERNEL)
    assert "04-governance/artifact-lifecycle.md" in kernel
    freeze = _read(STAGE_5)
    assert "04-governance/artifact-lifecycle.md" in freeze


def test_nine_pillars_ownership_preserved_in_selection_rule():
    content = _read(SKILL_MD)
    assert "Nine Pillars" in content
    content_kernel = _read(CORE_KERNEL)
    assert "Nine Pillars" in content_kernel
    assert "Double Diamond" in content_kernel


def test_no_active_core_workflow_load_references():
    """The retired core-workflow.md must not be active-loaded by any router."""
    for path in (SKILL_MD, CORE_KERNEL, STAGE_3, STAGE_5):
        content = _read(path)
        assert "core-workflow" not in content, path


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
    content = _read(SKILL_MD)
    assert "--spec prototype/product.md" not in content


def test_stage_5_freeze_binds_slice_specification():
    content = _read(SKILL_MD)
    assert "specifications/<slice_id>/r1.spec.md" in content
    assert "specifications/<slice_id>/r1.md" in content


def test_no_full_product_default_prescription():
    for path in ALL_ROUTE_FILES:
        content = _read(path)
        assert "默认整产品" not in content, path

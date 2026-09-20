"""CPC-002/CPC-003 source-contract checks for authored coverage and platform context.

Mechanism checks over source documents. Not real-session evidence.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import prototype_context  # noqa: E402

TEN = "surfaces: " + ", ".join(
    f"S{i}-{name}"
              for i, name in enumerate(
                  ["feed", "detail", "compose", "queue", "history", "settings",
                   "billing", "members", "audit", "help"], start=1)) + "\n"
THREE = "selected-surfaces: S1-feed, S2-detail, S3-compose\n"


def map_doc(coverage: str, selection: str = THREE, extra: str = "") -> str:
    return ("# Product Surface Map\n\n- Surface Map revision / status: r7 (draft)\n\n"
            "## Coverage and validation\n\n```prototype-context\n"
            f"record: surface-map\nrevision: r7\ncoverage: {coverage}\n"
            f"selection-source: prototype/discussion/scope-r7.md\n{TEN}{selection}{extra}```\n")


def product_doc(target: str = "web") -> str:
    return ("# Product Understanding\n\n```prototype-context\nrecord: product\n"
            f"target-context: {target}\ndevice-context: desktop\nautosave: enabled\n```\n")


def foundation_doc() -> str:
    return ("# Experience Foundation\n\n```prototype-context\n"
            "record: experience-foundation\ninvariants: object-identity, permission-scope, "
            "selected-context, required-return\n```\n")


def spec_doc(medium: str = "HTML", adaptation: str = "", preserves: str = "") -> str:
    return ("# Prototype Specification: s1 / r1\n\n```prototype-context\n"
            "record: prototype-specification\n"
            f"prototype-medium: {medium}\nverification-environment: headless-chromium-120\n"
            f"{adaptation}{preserves}```\n")


# CPC-SCN-003 / CPC-SCN-004: selection is retained, never widened, never invented.

def test_three_of_ten_selection_keeps_unselected_context():
    ctx = prototype_context.read_context(map_doc("selected"), product_doc())
    assert ctx["surface_map"]["selected_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]
    assert ctx["surface_map"]["target_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]
    assert len(ctx["surface_map"]["surfaces"]) == 10  # unselected product context retained
    assert ctx["authorizes_full_product"] is False
    assert ctx["errors"] == []


def test_full_product_coverage_targets_every_surface():
    ctx = prototype_context.read_context(map_doc("full-product"))
    assert ctx["authorizes_full_product"] is True
    assert len(ctx["surface_map"]["target_surfaces"]) == 10
    assert ctx["surface_map"]["selection_source"]


def test_missing_section_requires_recommendation_not_full_product():
    ctx = prototype_context.read_context("# Product Surface Map\n\n- Surface Map revision: r7\n")
    assert ctx["surface_map"]["coverage"] == "legacy"
    assert ctx["authorizes_full_product"] is False
    assert ctx["recommendation_required"] is True
    assert ctx["surface_map"]["target_surfaces"] == []


def test_unresolved_selection_requires_recommendation():
    ctx = prototype_context.read_context(map_doc("unresolved", selection=""))
    assert ctx["recommendation_required"] is True
    assert ctx["authorizes_full_product"] is False


def test_selection_without_source_reference_is_a_contract_error():
    doc = map_doc("selected").replace("selection-source: prototype/discussion/scope-r7.md\n", "")
    errors = prototype_context.read_context(doc)["errors"]
    assert "missing_selection_source" in {e["code"] for e in errors}


def test_unknown_and_duplicate_surface_ids_are_reported():
    ctx = prototype_context.read_context(
        map_doc("selected", selection="selected-surfaces: S1-feed, S99-ghost, S1-feed\n"))
    codes = [e["code"] for e in ctx["errors"]]
    assert "unknown_surface_id" in codes
    assert "duplicate_surface_id" in codes


def test_stale_map_identity_is_reported():
    ctx = prototype_context.read_context(map_doc("selected"), expected_map_revision="r6")
    assert [e["code"] for e in ctx["errors"]] == ["stale_map_identity"]
    stale = prototype_context.read_context(map_doc("selected"), expected_map_revision="r7")
    assert stale["errors"] == []


# CPC-SCN-003: a required dependency outside the selection is disclosed, not added.

def test_dependency_outside_selection_is_disclosed_not_added():
    ctx = prototype_context.read_context(
        map_doc("selected", extra="selected-dependencies: S7-billing\n"))
    assert ctx["surface_map"]["target_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]
    assert "S7-billing" not in ctx["surface_map"]["target_surfaces"]
    assert "S7-billing" in ctx["surface_map"]["surfaces"]
    assert ctx["errors"] == []


# CPC-SCN-005: platform adaptation preserves object, permission and return meaning.

def test_desktop_split_and_mobile_detail_preserve_invariants():
    doc = spec_doc(adaptation="adaptation: S2-detail=desktop-split, S2-detail=mobile-detail-route\n",
                   preserves="preserves: object-identity, permission-scope, selected-context, required-return\n")
    ctx = prototype_context.read_context(
        map_doc("selected"), product_doc(), foundation_doc(), doc)
    assert ctx["specification"]["adaptation"]["S2-detail"] == "mobile-detail-route"
    assert ctx["errors"] == []


def test_spec_preserving_an_undeclared_invariant_is_a_contract_error():
    doc = spec_doc(preserves="preserves: object-identity, pixel-parity\n")
    ctx = prototype_context.read_context(map_doc("selected"), product_doc(), foundation_doc(), doc)
    assert [e["code"] for e in ctx["errors"]] == ["unknown_invariant"]


# CPC-SCN-006: native target and browser prototype medium stay distinct.

def test_android_target_with_html_medium_keeps_native_validation_pending():
    ctx = prototype_context.read_context(
        map_doc("selected"), product_doc("android"), foundation_doc(), spec_doc("HTML"))
    assert ctx["platform"]["target_context"] == "android"
    assert ctx["platform"]["prototype_medium"] == "HTML"
    assert ctx["platform"]["native_validation_pending"] is True
    assert ctx["platform"]["verification_environment"] == "headless-chromium-120"


def test_native_target_with_native_medium_owes_no_simulation_gap():
    ctx = prototype_context.read_context(
        map_doc("selected"), product_doc("ios"), foundation_doc(), spec_doc("ios"))
    assert ctx["platform"]["native_validation_pending"] is False


def test_verification_environment_is_evidence_not_contract():
    blank = prototype_context.read_context(map_doc("selected"), product_doc(),
                                           foundation_doc(), spec_doc("HTML"))
    assert blank["platform"]["verification_environment"] == "headless-chromium-120"
    missing = prototype_context.read_context(map_doc("selected"), product_doc(),
                                             foundation_doc(),
                                             spec_doc("HTML").replace(
                                                 "verification-environment: headless-chromium-120\n", ""))
    assert missing["platform"]["verification_environment"] == "unknown"
    assert missing["errors"] == []


# Platform-specific applicability without a platform-by-page Cartesian product.

def test_platform_specific_applicability_is_explicit():
    ctx = prototype_context.read_context(
        map_doc("selected", extra="platform-contexts: web, android\napplicability: S3-compose=android\n"))
    assert ctx["surface_map"]["applicability"]["S3-compose"] == "android"
    assert "S1-feed" not in ctx["surface_map"]["applicability"]
    assert ctx["errors"] == []


def test_undeclared_platform_context_reference_is_a_contract_error():
    ctx = prototype_context.read_context(
        map_doc("selected", extra="applicability: S3-compose=watchos\n"))
    assert [e["code"] for e in ctx["errors"]] == ["unknown_platform_context"]


# Legacy sources stay readable and unmutated.

def test_legacy_source_is_unresolved_and_unmutated(tmp_path):
    legacy = tmp_path / "surface-map.md"
    text = ("# Product Surface Map\n\n## Coverage and validation\n\n"
            "- Surface count reconciled with scope: 10\n")
    legacy.write_text(text, encoding="utf-8")
    ctx = prototype_context.read_context(legacy.read_text(encoding="utf-8"))
    assert ctx["surface_map"]["coverage"] == "legacy"
    assert ctx["authorizes_full_product"] is False
    assert ctx["recommendation_required"] is True
    assert legacy.read_text(encoding="utf-8") == text


# Source contracts: T-01 owns the recommendation obligation; these templates stay declarative.

def test_recommendation_obligation_is_owned_by_the_route_not_the_templates():
    skill = (ROOT / "skills/spec-prototype/SKILL.md").read_text(encoding="utf-8")
    assert "Present concrete recommended combinations" in skill
    assert "never default to full-product" in skill
    for name in ("surface-map.md", "product.md"):
        text = (ROOT / "skills/spec-prototype/templates" / name).read_text(encoding="utf-8")
        assert "recommended combination" not in text.lower()


# The reader normalizes authored facts; it never scores or recommends.

def test_helper_is_read_only_and_contains_no_scoring():
    text = (ROOT / "skills/spec-prototype/scripts/prototype_context.py").read_text(encoding="utf-8")
    assert "def write" not in text and ".write_text(" not in text
    assert not re.search(r"\bscore\b|\brank\b|\brecommend\w*\(|\bweight\b", text)


def test_no_second_editable_authority_or_new_dependency():
    text = (ROOT / "skills/spec-prototype/scripts/prototype_context.py").read_text(encoding="utf-8")
    imports = set(re.findall(r"^(?:from|import)\s+([a-zA-Z0-9_.]+)", text, re.MULTILINE))
    assert imports <= {"__future__", "hashlib", "re", "typing"}
    assert not re.search(r"\.json\b", text)


def test_templates_are_parsable_and_round_trip(tmp_path):
    for name in ("surface-map.md", "product.md", "experience-foundation.md",
                 "prototype-specification.md"):
        text = (ROOT / "skills/spec-prototype/templates" / name).read_text(encoding="utf-8")
        assert prototype_context.parse_section(text) is not None, name
        copy = tmp_path / name
        copy.write_text(text, encoding="utf-8")
        assert copy.read_text(encoding="utf-8") == text


def test_expected_map_digest_detects_source_drift():
    import hashlib
    text = map_doc("selected")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert prototype_context.read_context(text, expected_map_digest=digest)["errors"] == []
    drift = prototype_context.read_context(text + "\n", expected_map_digest=digest)
    assert [e["code"] for e in drift["errors"]] == ["stale_map_identity"]

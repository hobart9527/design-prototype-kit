"""CPC-006: an unusable scope withholds completion everywhere it is read.

Temporary fixtures over the reconciler, the quality check and the review portal.
These are mechanism checks, not real-session evidence and not proof that a live
reviewer ran.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/spec-prototype/scripts"
sys.path.insert(0, str(SCRIPTS))

import generate_review_portal  # noqa: E402
import prototype_context  # noqa: E402
import verify_prototype_quality  # noqa: E402

NAMES = ["feed", "detail", "compose", "queue", "history", "settings",
         "billing", "members", "audit", "help"]
SURFACES = [f"S{i}-{name}" for i, name in enumerate(NAMES, start=1)]
SELECTED = SURFACES[:3]

PRODUCT = "```prototype-context\nrecord: product\ntarget-context: web\n```\n"
FOUNDATION = "```prototype-context\nrecord: experience-foundation\ninvariants: object-identity\n```\n"
SPECIFICATION = ("```prototype-context\nrecord: prototype-specification\n"
                 "prototype-medium: HTML\nverification-environment: headless-chromium-120\n```\n")


def map_text(coverage: str = "selected", selected=SELECTED, revision: str = "r7") -> str:
    return ("# Product Surface Map\n\n```prototype-context\n"
            "record: surface-map\n"
            f"revision: {revision}\ncoverage: {coverage}\n"
            "selection-source: prototype/discussion/scope-r7.md\n"
            f"surfaces: {', '.join(SURFACES)}\n"
            f"selected-surfaces: {', '.join(selected) if selected else ''}\n```\n")


def context(coverage: str = "selected", selected=SELECTED, revision: str = "r7") -> dict:
    return prototype_context.read_context(
        surface_map=map_text(coverage, selected, revision),
        product=PRODUCT, foundation=FOUNDATION, specification=SPECIFICATION)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _root(tmp_path: Path, map_body: str, delivered=()) -> Path:
    """A complete-enough root for the portal and the quality check."""
    root = tmp_path
    _write(root / "prototype/contracts/surface-maps/m1.md", map_body)
    _write(root / "prototype/product.md", PRODUCT)
    _write(root / "prototype/contracts/foundation/f1.md", FOUNDATION)
    _write(root / "prototype/specifications/console/r1.md", SPECIFICATION)
    _write(root / "prototype/evidence/handoff-manifest.json",
           '{"verification": {"browser": "captured"}}')
    _write(root / "prototype/shared/tokens.css", ":root { --radius-btn: 4px; }\n")
    for surface in delivered:
        _write(root / "prototype/surfaces" / surface / "index.html",
               "<!DOCTYPE html><html><body>"
               "<h1>surface</h1>"
               "<button role=\"button\">Quarantine</button>"
               "<script>document.addEventListener('keydown', () => {});</script>"
               "</body></html>")
    return root


def snapshot(root: Path) -> dict:
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


# CPC-SCN-022: the reconciler withholds completion and names the governing error.

def test_empty_selected_coverage_withholds_completion_with_the_governing_error():
    ctx = context(selected=[])
    assert [e["code"] for e in ctx["errors"]] == ["empty_selection"]
    result = prototype_context.reconcile_obligations(ctx, delivered=[], evidence={})
    assert result["coverage"] == "selected"
    assert result["completion"] is False
    assert result["governing_error"]["code"] == "empty_selection"
    assert result["scope_errors"] == [{"code": "empty_selection", "detail": "r7"}]
    # Scope membership and delivery stay separate facts: nothing is in round and
    # every declared surface stays outside this round.
    assert result["in_round"] == []
    assert result["outside_round"] == SURFACES
    assert result["auto_continue"] is False


def test_second_scope_error_is_attached_but_the_first_governs():
    broken = map_text(selected=[]).replace(
        "selection-source: prototype/discussion/scope-r7.md\n", "")
    ctx = prototype_context.read_context(surface_map=broken)
    result = prototype_context.reconcile_obligations(ctx, delivered=[], evidence={})
    assert [e["code"] for e in result["scope_errors"]] == [
        "missing_selection_source", "empty_selection"]
    assert result["governing_error"]["code"] == "missing_selection_source"
    assert result["completion"] is False


# CPC-SCN-022: unresolved and legacy coverage withhold the same way.

def test_unresolved_coverage_withholds_completion():
    result = prototype_context.reconcile_obligations(
        context(coverage="unresolved", selected=[]), delivered=[], evidence={})
    assert result["coverage"] == "unresolved"
    assert result["completion"] is False
    assert result["governing_error"] is None


def test_legacy_coverage_withholds_completion():
    legacy = prototype_context.read_context(
        surface_map="# Product Surface Map\n\n- Surface Map revision: r7\n")
    result = prototype_context.reconcile_obligations(legacy, delivered=[], evidence={})
    assert result["coverage"] == "legacy"
    assert result["completion"] is False
    assert result["governing_error"] is None


# CPC-SCN-023: a well-formed scope is unaffected.

def test_well_formed_selected_coverage_still_completes():
    result = prototype_context.reconcile_obligations(
        context(), delivered=SELECTED, evidence={s: f"capture/r7/{s}.png" for s in SELECTED})
    assert result["scope_errors"] == []
    assert result["governing_error"] is None
    assert result["completion"] is True
    assert result["unmet"] == []


def test_authorized_full_product_coverage_still_completes():
    result = prototype_context.reconcile_obligations(
        context(coverage="full-product", selected=[]), delivered=SURFACES,
        evidence={s: "capture" for s in SURFACES})
    assert result["authorized_full_product"] is True
    assert result["coverage"] == "full-product"
    assert result["scope_errors"] == []
    assert result["governing_error"] is None
    assert result["completion"] is True
    assert result["auto_continue"] is False


# CPC-SCN-022: the quality check fails instead of passing.

def test_empty_scope_fails_the_quality_check(tmp_path):
    root = _root(tmp_path, map_text(selected=[]), delivered=["S1-feed"])
    page = root / "prototype/surfaces/S1-feed/index.html"
    failures = verify_prototype_quality.coverage_failures(page)
    assert [f for f in failures if "empty_selection" in f], failures


def test_empty_scope_quality_assertion_fails_without_rewriting_artifacts(tmp_path):
    root = _root(tmp_path, map_text(selected=[]), delivered=["S1-feed"])
    page = root / "prototype/surfaces/S1-feed/index.html"
    before = snapshot(root)
    assert verify_prototype_quality.assert_quality(
        str(page), str(root / "prototype/shared/tokens.css")) is False
    assert snapshot(root) == before


def test_well_formed_scope_passes_the_quality_check(tmp_path):
    root = _root(tmp_path, map_text(), delivered=SELECTED)
    failures = verify_prototype_quality.coverage_failures(root / "prototype/surfaces/S1-feed/index.html")
    assert not [f for f in failures if "unusable" in f], failures


def test_unrelated_verification_failures_are_still_reported(tmp_path):
    """A withheld completion does not swallow the neighboring assertions."""
    root = _root(tmp_path, map_text(), delivered=["S1-feed"])
    page = root / "prototype/surfaces/S1-feed/index.html"
    _write(page, "<!DOCTYPE html><html><body><h1>feed</h1>"
                 "<a href=\"../S2-detail/\">detail</a>"
                 "<a href=\"../S3-compose/\">compose</a></body></html>")
    failures = verify_prototype_quality.coverage_failures(page)
    # The undelivered obligation is reported...
    assert [f for f in failures if "undelivered" in f and "S2-detail" in f]
    # ...and the broken delivered-sibling link is reported beside it.
    assert [f for f in failures if "S3-compose" in f and "not delivered" in f]


# CPC-SCN-022: the generated portal does not present a met completion.

def test_portal_withholds_completion_for_an_empty_scope(tmp_path):
    root = _root(tmp_path, map_text(selected=[]), delivered=["S1-feed"])
    reconciliation = generate_review_portal.read_coverage(root)
    assert reconciliation["completion"] is False
    html = generate_review_portal.build_coverage_html(reconciliation)
    assert 'data-completion="false"' in html
    assert 'data-completion="true"' not in html
    assert "Completion: withheld" in html
    assert "empty_selection" in html


def test_generated_portal_artifact_never_renders_met_for_an_empty_scope(tmp_path):
    root = _root(tmp_path, map_text(selected=[]), delivered=["S1-feed"])
    before = snapshot(root)
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "generate_review_portal.py"),
         "--root", str(root), "--output", "prototype/review-portal.html"],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    html = (root / "prototype/review-portal.html").read_text(encoding="utf-8")
    assert 'data-completion="false"' in html
    assert 'data-completion="true"' not in html
    assert "empty_selection" in html
    # The refusal is derived, never authored: every pre-existing artifact is byte-identical.
    after = {k: v for k, v in snapshot(root).items() if k != "prototype/review-portal.html"}
    assert after == before


def test_portal_still_renders_met_for_a_well_formed_scope(tmp_path):
    """The reconciler withholds an empty evidence map, so evidence is authored too."""
    root = _root(tmp_path, map_text(), delivered=SELECTED)
    delivered = {page.parent.name: page.relative_to(root).as_posix()
                 for page in sorted((root / "prototype/surfaces").glob("*/index.html"))}
    ctx = prototype_context.read_context(
        surface_map=(root / "prototype/contracts/surface-maps/m1.md").read_text(encoding="utf-8"),
        product=PRODUCT, foundation=FOUNDATION, specification=SPECIFICATION)
    reconciliation = prototype_context.reconcile_obligations(
        ctx, delivered=delivered, evidence=delivered)
    html = generate_review_portal.build_coverage_html(reconciliation)
    assert reconciliation["completion"] is True
    assert 'data-completion="true"' in html
    assert "Completion: met" in html
    assert "data-scope-error" not in html


def test_portal_withholds_completion_for_unresolved_and_legacy_coverage(tmp_path):
    unresolved = _root(tmp_path / "unresolved",
                       map_text(coverage="unresolved", selected=[]), delivered=["S1-feed"])
    html = generate_review_portal.build_coverage_html(
        generate_review_portal.read_coverage(unresolved))
    assert 'data-completion="false"' in html

    legacy = _root(tmp_path / "legacy",
                   "# Product Surface Map\n\n- Surface Map revision: r7\n", delivered=["S1-feed"])
    html = generate_review_portal.build_coverage_html(
        generate_review_portal.read_coverage(legacy))
    assert 'data-completion="false"' in html

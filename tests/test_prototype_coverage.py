"""CPC-006 mechanism checks for bounded selected coverage and review reconciliation.

Temporary ten-surface fixtures. These are mechanism checks, not real-session
evidence and not proof that a live reviewer ran.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import generate_review_portal  # noqa: E402
import prototype_context  # noqa: E402
import verify_prototype_quality  # noqa: E402

NAMES = ["feed", "detail", "compose", "queue", "history", "settings",
         "billing", "members", "audit", "help"]
SURFACES = [f"S{i}-{name}" for i, name in enumerate(NAMES, start=1)]
SELECTED = SURFACES[:3]
TEN = "surfaces: " + ", ".join(SURFACES) + "\n"


def map_text(surfaces=None, selected=SELECTED, coverage="selected", revision="r7",
             applicability="") -> str:
    return ("# Product Surface Map\n\n```prototype-context\n"
            "record: surface-map\n"
            f"revision: {revision}\ncoverage: {coverage}\n"
            "selection-source: prototype/discussion/scope-r7.md\n"
            f"surfaces: {', '.join(surfaces or SURFACES)}\n"
            f"selected-surfaces: {', '.join(selected) if selected else ''}\n"
            f"{applicability}```\n")


def context(surfaces=None, selected=SELECTED, coverage="selected", revision="r7",
            applicability="") -> dict:
    return prototype_context.read_context(
        surface_map=map_text(surfaces, selected, coverage, revision, applicability),
        product="```prototype-context\nrecord: product\ntarget-context: web\n```\n",
        foundation="```prototype-context\nrecord: experience-foundation\ninvariants: object-identity\n```\n",
        specification="```prototype-context\nrecord: prototype-specification\nprototype-medium: HTML\nverification-environment: headless-chromium-120\n```\n")


# CPC-SCN-011: three of ten selected, only the first delivered.

def test_selected_three_with_one_artifact_withholds_completion():
    result = prototype_context.reconcile_obligations(
        context(), delivered=["S1-feed"], evidence={"S1-feed": "capture/r7/s1.png"})
    assert result["coverage"] == "selected"
    assert result["authorized_full_product"] is False
    assert result["completion"] is False
    assert result["missing_delivery"] == ["S2-detail", "S3-compose"]
    assert set(result["outside_round"]) == set(SURFACES[3:])
    assert result["auto_continue"] is False


def test_outside_round_surfaces_do_not_block_selected_completion():
    result = prototype_context.reconcile_obligations(
        context(), delivered=SELECTED,
        evidence={s: f"capture/r7/{s}.png" for s in SELECTED})
    assert result["outside_round"] == SURFACES[3:]
    assert result["unmet"] == []
    assert result["completion"] is True


def test_no_delivered_sibling_requires_no_href():
    result = prototype_context.reconcile_obligations(context(), delivered=["S1-feed"])
    assert result["sibling_links"]["S1-feed"] == []
    assert result["missing_delivery"] == ["S2-detail", "S3-compose"]


def test_delivered_siblings_are_reachability_obligations():
    result = prototype_context.reconcile_obligations(context(), delivered=SELECTED)
    assert result["sibling_links"]["S1-feed"] == ["S2-detail", "S3-compose"]


# CPC-SCN-012: full product continues only under the bound authorization.

def test_full_product_after_first_batch_keeps_remaining_batches():
    result = prototype_context.reconcile_obligations(
        context(selected=[], coverage="full-product"), delivered=SURFACES[:4],
        evidence={s: "capture" for s in SURFACES[:4]})
    assert result["authorized_full_product"] is True
    assert result["completion"] is False
    assert result["auto_continue"] is True
    assert result["missing_delivery"] == SURFACES[4:]


def test_missing_required_surface_blocks_even_with_documented_blocker():
    result = prototype_context.reconcile_obligations(
        context(selected=[], coverage="full-product"), delivered=SURFACES[:4],
        evidence={s: "capture" for s in SURFACES[:4]},
        blocked={SURFACES[4]: "awaiting upstream API contract"})
    assert result["completion"] is False
    assert result["blockers"][SURFACES[4]] == "awaiting upstream API contract"
    assert SURFACES[4] in result["missing_delivery"]


def test_delivered_without_evidence_is_unmet():
    result = prototype_context.reconcile_obligations(
        context(selected=[SURFACES[0]]), delivered=[SURFACES[0]])
    assert result["missing_evidence"] == [SURFACES[0]]
    assert result["completion"] is False


# CPC-SCN-013: a map change never silently alters the retained promise.

def test_map_addition_does_not_expand_selection():
    added = SURFACES + ["S11-export"]
    result = prototype_context.reconcile_obligations(
        context(surfaces=added), delivered=SELECTED,
        evidence={s: "capture" for s in SELECTED})
    assert result["in_round"] == SELECTED
    assert "S11-export" in result["outside_round"]
    assert result["completion"] is True


def test_map_removal_does_not_shrink_the_promised_set():
    removed = [s for s in SURFACES if s != SELECTED[1]]
    result = prototype_context.reconcile_obligations(
        context(surfaces=removed), delivered=[SELECTED[0]],
        evidence={SELECTED[0]: "capture"})
    assert SELECTED[1] in result["in_round"]
    assert SELECTED[1] in result["missing_delivery"]
    assert result["completion"] is False


def test_stale_revision_withholds_completion():
    result = prototype_context.reconcile_obligations(
        context(), delivered=SELECTED, evidence={s: "capture" for s in SELECTED},
        bound_revision="r6")
    assert result["stale_revision"] is True
    assert result["completion"] is False


def test_platform_applicability_is_reported_per_surface():
    applicability = "applicability: S1-feed=web-ios, S2-detail=web, S3-compose=web\n"
    result = prototype_context.reconcile_obligations(
        context(applicability=applicability), delivered=SELECTED,
        evidence={s: "capture" for s in SELECTED})
    flagged = {o["surface"]: o["platforms"] for o in result["obligations"]}
    assert flagged["S1-feed"] == ["web-ios"]
    assert flagged["S10-help"] == []


# Review view: declared absent surfaces stay visible; statuses stay out of nav.

def _temp_root(tmp_path: Path, map_body: str, delivered=(), evidence_json: str = "{}") -> Path:
    root = tmp_path
    (root / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
    (root / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
    (root / "prototype/contracts/surface-maps/m1.md").write_text(map_body, encoding="utf-8")
    for surface in delivered:
        page = root / "prototype/surfaces" / surface / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(f"<!DOCTYPE html><html><body><h1>{surface}</h1></body></html>",
                        encoding="utf-8")
    (root / "prototype/evidence").mkdir(parents=True, exist_ok=True)
    (root / "prototype/evidence/handoff-manifest.json").write_text(
        '{"verification": {"browser": "captured"}}', encoding="utf-8")
    (root / "prototype/shared").mkdir(parents=True, exist_ok=True)
    (root / "prototype/shared/tokens.css").write_text(":root { --radius-btn: 4px; }\n", encoding="utf-8")
    return root


def test_portal_lists_declared_absent_surfaces(tmp_path):
    root = _temp_root(tmp_path, map_text(), delivered=["S1-feed"])
    reconciliation = generate_review_portal.read_coverage(root)
    assert reconciliation is not None
    html = generate_review_portal.build_coverage_html(reconciliation)
    assert "S1-feed" in html
    for absent in ["S2-detail", "S3-compose"]:
        assert absent in html
    assert "S10-help" in html
    assert 'data-completion="false"' in html


def test_portal_generation_shows_coverage_without_forcing_status_in_nav(tmp_path):
    root = _temp_root(tmp_path, map_text(), delivered=["S1-feed"])
    out = root / "prototype/review-portal.html"
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "skills/spec-prototype/scripts/generate_review_portal.py"),
         "--root", str(root), "--output", "prototype/review-portal.html"],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    html = out.read_text(encoding="utf-8")
    assert "coverage-reconciliation" in html
    assert "S1-feed" in html and "S2-detail" in html
    # The prototype view switcher lists delivered previews only.
    assert 'loadView(' in html


# Quality checks: pending siblings are honest, delivered sibling links must resolve.

def _quality_root(tmp_path: Path, link: str, delivered=("S1-feed",)) -> Path:
    root = _temp_root(tmp_path, map_text(), delivered=list(delivered))
    page = root / "prototype/surfaces/S1-feed/index.html"
    page.write_text(
        "<!DOCTYPE html><html><body><h1>feed</h1>"
        f"{link}"
        "<button role=\"button\">Quarantine</button>"
        "<script>document.addEventListener('keydown', () => {});</script>"
        "</body></html>", encoding="utf-8")
    (root / "prototype/product.md").write_text("```prototype-context\nrecord: product\n```\n", encoding="utf-8")
    (root / "prototype/contracts/foundation/f1.md").write_text(
        "```prototype-context\nrecord: experience-foundation\n```\n", encoding="utf-8")
    return root


def test_pending_sibling_without_href_is_accepted(tmp_path):
    root = _quality_root(tmp_path, '<span aria-disabled="true">detail pending</span>')
    failures = verify_prototype_quality.coverage_failures(root / "prototype/surfaces/S1-feed/index.html")
    assert not [f for f in failures if "pending sibling" in f]


def test_broken_delivered_sibling_link_is_reported(tmp_path):
    root = _quality_root(tmp_path, '<a href="../S3-compose/">compose</a>',
                         delivered=("S1-feed", "S2-detail"))
    failures = verify_prototype_quality.coverage_failures(root / "prototype/surfaces/S1-feed/index.html")
    assert [f for f in failures if "S3-compose" in f and "not delivered" in f]


def test_undelivered_selection_is_reported_by_quality_checks(tmp_path):
    root = _temp_root(tmp_path, map_text(), delivered=["S1-feed"])
    failures = verify_prototype_quality.coverage_failures(root / "prototype/surfaces/S1-feed/index.html")
    assert [f for f in failures if "undelivered" in f]


# Source instructions: continuation and completion stay distinguishable.

def test_workflow_distinguishes_continuation_and_completion():
    text = (ROOT / "skills/spec-prototype/references/core-workflow.md").read_text(encoding="utf-8")
    assert "reconcile_obligations" in text
    assert "authorizes automatic continuation" in text
    assert "never discharges an obligation" in text
    assert "declared-but-absent surfaces" in text
    assert "never forced to display review-management statuses" in text


def test_context_module_documents_separation_of_facts():
    text = (ROOT / "skills/spec-prototype/scripts/prototype_context.py").read_text(encoding="utf-8")
    assert "def reconcile_obligations" in text
    assert "Scope membership, delivery and evidence stay separate facts" in text

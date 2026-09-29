"""CRR-SCN-005 mechanism checks for review portal viewport and stress controls.

Temporary fixture surfaces. These are mechanism checks for the generated portal
markup, not proof that a live reviewer exercised the portal.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import generate_review_portal  # noqa: E402

SURFACES = [
    {"id": "primary-feed", "name": "Core Anchor [feed]", "tier": "Tier 0 - Primary",
     "url": "experiments/feed/anchor/index.html", "exists": True},
    {"id": "surface-detail", "name": "Surface: Detail", "tier": "Tier 1/2 - Expanded Surface",
     "url": "surfaces/detail/index.html", "exists": True},
]

def portal() -> str:
    return generate_review_portal.build_portal_html(SURFACES, title="Fixture Portal")

# CRR-SCN-005: viewport simulation frames are embedded in the generated portal.

def test_viewport_controls_present():
    html = portal()
    assert 'data-viewport-rail' in html
    for width in ("1440px", "768px", "390px"):
        assert f'data-viewport="{width}"' in html

def test_viewport_labels_named():
    html = portal()
    assert "Desktop" in html
    assert "Tablet" in html
    assert "Mobile" in html

def test_viewport_frames_exist():
    html = portal()
    assert 'class="viewport-frame"' in html
    # A frame per declared viewport, each holding the default surface.
    assert html.count('data-viewport=') >= 3

# CRR-SCN-005: Break Protocol stress toggle injects stress parameters.

def test_stress_toggle_present():
    html = portal()
    assert 'data-break-protocol' in html
    for stress in ("overflow", "empty"):
        assert f'data-stress="{stress}"' in html

def test_stress_parameters_reach_iframe():
    html = portal()
    assert "?stress=overflow" in html
    assert "?stress=empty" in html

def test_stress_script_targets_preview_frame():
    html = portal()
    assert "loadView" in html
    # Stress toggle must rewrite the preview iframe URL, not a static anchor.
    assert "preview-frame" in html


# CRR-SCN-005: the C1 co-creation decision bar.

DIRECTIONS = [
    {"id": "feed-a", "name": "Direction A [feed]", "url": "experiments/feed/dirs/a/index.html"},
    {"id": "feed-b", "name": "Direction B [feed]", "url": "experiments/feed/dirs/b/index.html"},
]


def decision_portal() -> str:
    return generate_review_portal.build_portal_html(SURFACES, title="Fixture Portal",
                                                    directions=DIRECTIONS)


def test_decision_bar_offers_each_candidate():
    html = decision_portal()
    assert "data-decision-bar" in html
    for d in DIRECTIONS:
        assert f'data-variant="{d["id"]}"' in html


def test_decision_bar_carries_all_four_verdicts():
    html = decision_portal()
    for verdict in ("approve", "steer", "re-roll", "canon"):
        assert f'data-verdict="{verdict}"' in html


def test_decision_bar_reads_the_variant_from_the_url():
    html = decision_portal()
    assert "variant=" in html
    assert "variantFromHash" in html, "a reviewer must be able to hand over a URL, not prose"


def test_steer_and_reroll_require_a_reason():
    html = decision_portal()
    assert "decision-reason" in html
    assert "needs a reason" in html


def test_decision_bar_is_absent_with_a_single_direction():
    """A control that cannot change the outcome is worse than no control."""
    html = generate_review_portal.build_portal_html(
        SURFACES, title="Fixture Portal", directions=DIRECTIONS[:1])
    assert "data-decision-bar" not in html


def test_discover_directions_excludes_the_converged_anchor(tmp_path):
    for slot in ("a", "b"):
        p = tmp_path / f"prototype/experiments/feed/dirs/{slot}/index.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<html></html>", encoding="utf-8")
    anchor = tmp_path / "prototype/experiments/feed/anchor/index.html"
    anchor.parent.mkdir(parents=True, exist_ok=True)
    anchor.write_text("<html></html>", encoding="utf-8")

    found = generate_review_portal.discover_directions(tmp_path)
    ids = {d["id"] for d in found}
    assert ids == {"feed-a", "feed-b"}, f"the anchor is not a candidate: {ids}"
    assert all("anchor" not in d["url"] for d in found)

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

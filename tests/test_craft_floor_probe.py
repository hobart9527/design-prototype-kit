"""Rendered-browser checks for the three non-negotiable craft invariants."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import sys
SCRIPTS = Path(__file__).resolve().parents[1] / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import verify_prototype_quality as vpq  # noqa: E402


pytestmark = pytest.mark.skipif(not shutil.which("node"), reason="node is required for the browser probe")


def _write(tmp_path: Path, body: str) -> Path:
    html = tmp_path / "craft.html"
    html.write_text(f"""<!doctype html><html><head><style>
    .outer {{ width: 220px; height: 120px; padding: 8px; border-radius: 16px; }}
    .inner {{ width: 100px; height: 40px; border-radius: 8px; }}
    .commit:active {{ transform: scale(.98); }}
    .metric {{ font-variant-numeric: tabular-nums; }}
    </style></head><body>{body}</body></html>""", encoding="utf-8")
    return html


def test_craft_floor_probe_passes_compliant_specimen(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    html = _write(tmp_path, '<div class="outer"><div class="inner"></div></div>'
                  '<button class="commit" data-action="save">Save</button>'
                  '<output class="metric">128</output>')
    ok, reason = vpq.probe_craft_floors(html)
    assert ok, reason


@pytest.mark.parametrize(("body", "finding"), [
    ('<button data-action="save">Save</button>', "press feedback"),
    ('<div class="outer"><div class="inner" style="border-radius:2px"></div></div>', "concentric radius"),
    ('<output>128</output>', "tabular numerals"),
])
def test_craft_floor_probe_reports_each_violation(tmp_path: Path, monkeypatch, body: str, finding: str):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    html = _write(tmp_path, body)
    ok, reason = vpq.probe_craft_floors(html)
    assert not ok
    assert reason and finding in reason


def test_craft_floor_probe_checks_each_corner_radius(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    html = _write(tmp_path, '<div class="outer" style="border-radius:16px 16px 16px 16px; padding:8px">'
                  '<div class="inner" style="border-radius:8px 8px 8px 2px"></div></div>')
    ok, reason = vpq.probe_craft_floors(html)
    assert not ok
    assert reason and "concentric radius" in reason and "BottomLeft" in reason


def test_craft_floor_probe_ignores_navigation_links_and_prose_numbers(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    html = _write(tmp_path, '<a href="/reports" data-action="navigate">128 reports</a>'
                  '<p>The report was generated in 2025.</p>')
    ok, reason = vpq.probe_craft_floors(html)
    assert ok, reason


def test_craft_floor_probe_reports_unavailable_browser(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq.shutil, "which", lambda _name: None)
    html = _write(tmp_path, "<main>Content</main>")
    ok, reason = vpq.probe_craft_floors(html)
    assert not ok
    assert reason and "environment_not_ready" in reason

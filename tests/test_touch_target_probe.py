#!/usr/bin/env python3
"""Regression: touch-target probe wiring in verify_prototype_quality.

The probe must report a deterministic, build-time failure naming the offending
controls when interactive elements render below 44px at mobile width, and must
stay an environment_not_ready report (never a fabricated pass) when no
evaluating engine is available.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "spec-prototype" / "scripts"))
import verify_prototype_quality as vpq  # noqa: E402


_SMALL_HTML = """<!doctype html><html><head><style>
body { margin: 0; }
.tiny { width: 24px; height: 24px; padding: 0; border: 0; }
</style></head><body>
<button class="tiny" aria-label="检视机器遥测 node-x">A</button>
<button class="tiny" aria-label="ARM">B</button>
<div style="height: 600px">filler</div>
</body></html>"""

_BIG_HTML = """<!doctype html><html><head><style>
body { margin: 0; }
.ok { width: 48px; height: 48px; }
</style></head><body>
<button class="ok" aria-label="big one">A</button>
<button class="ok" aria-label="big two">B</button>
</body></html>"""


def test_probe_reports_small_controls_with_names(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    if not shutil.which("node"):
        assert False, "node required in dev environment for this probe test"
    html = tmp_path / "index.html"
    html.write_text(_SMALL_HTML, encoding="utf-8")
    ok, reason = vpq.probe_touch_targets(html)
    assert ok is False
    assert reason and "environment_not_ready" not in reason
    assert "touch_target assertion" in reason
    assert "检视机器遥测 node-x" in reason


def test_probe_passes_when_controls_meet_minimum(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    if not shutil.which("node"):
        assert False, "node required in dev environment for this probe test"
    html = tmp_path / "index.html"
    html.write_text(_BIG_HTML, encoding="utf-8")
    ok, reason = vpq.probe_touch_targets(html)
    assert ok is True
    assert reason is None


def test_probe_cache_invalidates_after_html_changes(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    if not shutil.which("node"):
        assert False, "node required in dev environment for this probe test"
    html = tmp_path / "index.html"
    html.write_text(_SMALL_HTML, encoding="utf-8")
    assert vpq.probe_touch_targets(html)[0] is False
    html.write_text(_BIG_HTML, encoding="utf-8")
    assert vpq.probe_touch_targets(html) == (True, None)


def test_probe_without_engine_is_not_ready_not_pass(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})
    monkeypatch.setattr(shutil, "which", lambda name: None)
    import importlib.util
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None)
    html = tmp_path / "index.html"
    html.write_text(_SMALL_HTML, encoding="utf-8")
    ok, reason = vpq.probe_touch_targets(html)
    assert ok is False
    assert reason and "environment_not_ready" in reason


def test_macos_chrome_app_discovered_as_engine(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    import verify_prototype_quality as v
    # Discovery must consult the macOS app bundle path when PATH has nothing.
    found = any(Path(app).exists()
                for app in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",))
    engine = v._style_engine_command()
    if found:
        assert engine and "Chrome" in engine
    else:
        assert engine is None or engine == "playwright"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))

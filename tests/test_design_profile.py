"""The design profile measures rendered geometry, and refuses to grade.

Two properties are load-bearing and are pinned here:

1. It reports what the browser actually painted. A page whose stylesheet never
   applies renders unstyled, and the profile's numbers collapse together — the
   `test_unstyled_page_collapses` case below is the regression for that, and it
   is the case the pass/fail gates do *not* catch (they report `STATIC: pass`
   with the browser tier degraded to `environment_not_ready`).
2. It declares no winner. `compare` has no total and no rank, and
   `test_compare_has_no_score` fails if one is ever added.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import sys
BENCH = Path(__file__).resolve().parents[1] / "benchmarks"
if str(BENCH) not in sys.path:
    sys.path.insert(0, str(BENCH))
import design_profile as dp  # noqa: E402


pytestmark = pytest.mark.skipif(
    not shutil.which("node") or not dp.PROBE.is_file(),
    reason="the design profile needs node and browser_probe.mjs",
)


_STYLED = """<!doctype html><html><head><link rel="stylesheet" href="shared/tokens.css"></head>
<body><header class="bar">Incident Console</header>
<main class="workspace">
  <section class="panel"><h1>Nodes</h1><p>12 nodes degraded</p></section>
  <section class="panel"><h1>Actions</h1><button>Drain</button><button>Roll back</button></section>
</main></body></html>"""

# Same markup, but the stylesheet sits one directory too high so the link does
# not resolve and the page renders with the browser's defaults.
_UNSTYLED = _STYLED.replace('href="shared/tokens.css"', 'href="../shared/tokens.css"')

_TOKENS = """:root { --bg-void: #121212; --bg-surface: #1e1e1e; --text-primary: #e6edf3; --gap: 24px; }
body { background: var(--bg-void); color: var(--text-primary); font-family: system-ui; }
.bar { background: var(--bg-surface); padding: 16px; font-size: 20px; font-weight: 700; }
.workspace { display: grid; row-gap: var(--gap); padding: 32px; }
.panel { background: var(--bg-surface); padding: 12px; }
.panel h1 { font-size: 14px; font-weight: 600; }
.panel p { font-size: 12px; font-weight: 400; }
"""


def _write(tmp_path: Path, html: str, *, tokens: bool = True) -> Path:
    (tmp_path / "shared").mkdir(exist_ok=True)
    if tokens:
        (tmp_path / "shared" / "tokens.css").write_text(_TOKENS, encoding="utf-8")
    page = tmp_path / "index.html"
    page.write_text(html, encoding="utf-8")
    return page


def test_profile_is_deterministic(tmp_path: Path):
    page = _write(tmp_path, _STYLED)
    first = dp.profile_artifact(page)
    second = dp.profile_artifact(page)
    assert first["status"] == "measured", first.get("reason")
    strip = lambda p: {k: v for k, v in p.items() if k not in ("artifact", "viewport")}  # noqa: E731
    assert strip(first) == strip(second)


def test_styled_page_reads_its_palette_and_spacing(tmp_path: Path):
    page = _write(tmp_path, _STYLED)
    profile = dp.profile_artifact(page)
    assert profile["status"] == "measured", profile.get("reason")
    # Two surfaces plus the page background, all painted.
    assert profile["palette_size"] >= 2, profile
    # `row-gap: var(--gap)` is the spacing mechanism on this page.
    assert profile["spacing_scale_size"] >= 1, profile
    assert profile["controls"] >= 2, profile
    assert profile["hierarchy_levels"] >= 2, profile


def test_unstyled_page_collapses(tmp_path: Path):
    """A stylesheet that never loads paints nothing — and the profile says so.

    This is the r2 signature: the file exists on disk, the gate's static pass
    succeeds, and the browser tier degrades to `environment_not_ready`, so
    nothing upstream notices. The profile notices, because it reads paint.

    The discriminators are the ones that survive a page this small. `palette_size`
    is not one of them — an unstyled `<button>` still paints its user-agent
    background — but the spacing mechanism and the type scale both revert: the
    authored grid gap disappears, and the rendered sizes become the browser's
    defaults (16px body, 32px h1) instead of the authored ones.
    """
    page = _write(tmp_path, _UNSTYLED)
    profile = dp.profile_artifact(page)
    assert profile["status"] == "measured", profile.get("reason")
    assert profile["spacing_scale_size"] == 0, profile
    assert 16 in profile["type_sizes"], profile  # the user-agent body size
    assert not {12, 14, 20} & set(profile["type_sizes"]), profile  # none authored


def test_compare_reports_every_artifact_and_declares_no_winner(tmp_path: Path):
    styled = dp.profile_artifact(_write(tmp_path, _STYLED))
    profiles = {"styled": styled, "missing": {"status": "environment_not_ready"}}
    comparison = dp.compare(profiles)
    assert comparison["labels"] == ["styled", "missing"]
    assert comparison["rows"]["palette_size"] == {"styled": styled["palette_size"], "missing": None}
    # No field of the comparison is a score, a rank, or a recommendation.
    flat = {k for k in comparison if k != "rows"} | set(comparison["rows"])
    assert not {k for k in flat if k in ("total", "score", "rank", "winner", "verdict")}


def test_reports_environment_not_ready_without_node(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(dp.shutil, "which", lambda _name: None)
    profile = dp.profile_artifact(_write(tmp_path, _STYLED))
    assert profile["status"] == "environment_not_ready"
    assert "node" in profile["reason"]

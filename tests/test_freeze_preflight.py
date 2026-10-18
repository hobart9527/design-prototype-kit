"""Freeze binds the whole anchor and runs the executable gates it depends on."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_spec_only_freeze import _build_root, handoff  # noqa: E402


class _Done:
    def __init__(self, code: int, out: str = ""):
        self.returncode, self.stdout, self.stderr = code, out, ""


def _fake_run(codes: dict):
    def run(cmd, **_):
        name = Path(cmd[1]).name
        return _Done(codes.get(name, 0), f"{name} output")
    return run


def _anchor(root: Path, files=("index.html", "anchor.css", "anchor.js")):
    d = root / "prototype/experiments/reader/anchor"
    d.mkdir(parents=True, exist_ok=True)
    for f in files:
        (d / f).write_text("x", encoding="utf-8")


def test_freeze_retains_anchor_css_and_js(tmp_path, monkeypatch):
    spec = _build_root(tmp_path)
    _anchor(tmp_path)
    monkeypatch.setattr(handoff.subprocess, "run", _fake_run({}))
    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    paths = {a["path"] for a in manifest["frozen_artifacts"]}
    assert {f"prototype/experiments/reader/anchor/{n}" for n in
            ("index.html", "anchor.css", "anchor.js")} <= paths


def test_failed_verify_blocks_freeze(tmp_path, monkeypatch):
    spec = _build_root(tmp_path)
    _anchor(tmp_path)
    monkeypatch.setattr(handoff.subprocess, "run",
                        _fake_run({"verify_prototype_quality.py": 1}))
    with pytest.raises(handoff.HandoffError, match="verify_prototype_quality exit 1"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert not (tmp_path / "prototype/evidence/reader/r1/freeze-manifest.json").exists()


def test_degraded_verify_is_recorded_not_passed(tmp_path, monkeypatch):
    spec = _build_root(tmp_path)
    _anchor(tmp_path)
    monkeypatch.setattr(handoff.subprocess, "run",
                        _fake_run({"verify_prototype_quality.py": 2}))
    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert manifest["preflight"]["verify_prototype_quality"] == "degraded"


def test_missing_gate_inputs_are_not_applicable(tmp_path, monkeypatch):
    spec = _build_root(tmp_path)
    monkeypatch.setattr(handoff.subprocess, "run", _fake_run({}))
    assert handoff.freeze_preflight(tmp_path, "reader") == {
        "verify_prototype_quality": "not_applicable", "wcag_check": "not_applicable",
        "token_sync": "not_applicable"}


def test_out_of_sync_stylesheet_blocks_freeze(tmp_path, monkeypatch):
    """A stylesheet that drifted from its source is never sealed."""
    spec = _build_root(tmp_path)
    _anchor(tmp_path)
    (tmp_path / "prototype/shared").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/shared/tokens.css").write_text(":root{}", encoding="utf-8")
    monkeypatch.setattr(handoff.subprocess, "run",
                        _fake_run({"compile_tokens.py": 1}))
    with pytest.raises(handoff.HandoffError, match="out of sync"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())


def test_in_sync_stylesheet_is_recorded(tmp_path, monkeypatch):
    spec = _build_root(tmp_path)
    (tmp_path / "prototype/shared").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/shared/tokens.css").write_text(":root{}", encoding="utf-8")
    monkeypatch.setattr(handoff.subprocess, "run", _fake_run({}))
    assert handoff.freeze_preflight(tmp_path, "reader")["token_sync"] == "passed"


def test_freeze_preflight_inherits_modern_token_options(tmp_path):
    """When tokens.css was compiled with non-default options (e.g. oklch, clamp),
    freeze_preflight must forward them to compile_tokens --check-sync instead of failing."""
    import compile_tokens as ct
    spec = _build_root(tmp_path)
    disc = tmp_path / "prototype/discussion.md"
    disc.write_text(
        disc.read_text(encoding="utf-8") +
        "\n\n## Visual Design Foundation (Five Axes)\n"
        "- Energy: Calm\n- Materiality: Digital / Flat\n- Density: Comfortable\n"
        "- Mood: Technical / Precise\n- Scale: Intimate\n",
        encoding="utf-8"
    )
    tokens_css = tmp_path / "prototype/shared/tokens.css"
    ct.compile_tokens(
        str(disc),
        output_css_path=str(tokens_css),
        color_format="oklch",
        type_scale="clamp",
    )

    results = handoff.freeze_preflight(tmp_path, "reader")
    assert results["token_sync"] == "passed"



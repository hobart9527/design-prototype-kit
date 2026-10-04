"""Turn 1 artifact window: runnable artifacts before the Resume seam are advised, never blocked.

r35/r36 wrote tokens/HTML inside Turn 1 (61 and 41 iterations). The path gate
cannot see it because the path is legal; the Resume block is the seam.
Hermetic: no network, no LLM, no browser.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import execution_boundary as eb  # noqa: E402


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _payload(root: Path, rel: str) -> dict:
    return {"tool_name": "Write",
            "tool_input": {"file_path": str(root / rel), "content": "x"},
            "cwd": str(root)}


def _advisory(payload: dict) -> str:
    return payload.get("hookSpecificOutput", {}).get("additionalContext", "")


def test_html_before_the_resume_block_carries_an_advisory_not_a_denial(tmp_path):
    _write(tmp_path / "prototype/discussion.md", "# Discussion\n\n## Tension\nx\n")
    payload = _payload(tmp_path, "prototype/experiments/s/anchor/index.html")
    eb.check(payload)  # must not raise: advisory only
    assert "before the Resume block exists" in _advisory(payload)


def test_tokens_css_before_the_resume_block_carries_an_advisory(tmp_path):
    _write(tmp_path / "prototype/discussion.md", "# Discussion\n")
    payload = _payload(tmp_path, "prototype/shared/tokens.css")
    eb.check(payload)
    assert "Turn 2" in _advisory(payload)


def test_artifacts_after_the_resume_block_are_silent(tmp_path):
    _write(tmp_path / "prototype/discussion.md",
           "# Discussion\n\n## Resume\n- Execution boundary: active\n")
    payload = _payload(tmp_path, "prototype/shared/tokens.css")
    eb.check(payload)
    assert "hookSpecificOutput" not in payload


def test_layered_resume_seam_closes_the_window(tmp_path):
    _write(tmp_path / "prototype/truth.md", "# Truth\n")
    _write(tmp_path / "prototype/world.md", "# World\n")
    payload = _payload(tmp_path, "prototype/experiments/s/index.html")
    eb.check(payload)
    assert _advisory(payload)
    _write(tmp_path / "prototype/discussion.md", "## Resume\n- Execution boundary: active\n")
    later = _payload(tmp_path, "prototype/experiments/s/index.html")
    eb.check(later)
    assert not _advisory(later)


def test_design_record_files_never_trip_the_window(tmp_path):
    _write(tmp_path / "prototype/discussion.md", "# Discussion\n")
    for rel in ("prototype/discussion.md", "prototype/briefs/s.md", "prototype/intent.json"):
        payload = _payload(tmp_path, rel)
        try:
            eb.check(payload)
        except ValueError:
            continue  # intent.json schema validation is a separate gate
        assert "before the Resume block" not in _advisory(payload)

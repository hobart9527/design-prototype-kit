"""Turn 1 artifact window: runnable artifacts before the Resume seam are blocked.

r33–r36 wrote tokens/HTML inside Turn 1 (57–90 iterations); the soft advisory
did not stop the model. The Resume block is the seam, enforced as a gate.
Hermetic: no network, no LLM, no browser.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

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


def test_html_before_the_resume_block_is_blocked(tmp_path):
    _write(tmp_path / "prototype/discussion.md", "# Discussion\n\n## Tension\nx\n")
    with pytest.raises(ValueError, match="Turn 2"):
        eb.check(_payload(tmp_path, "prototype/experiments/s/anchor/index.html"))


def test_tokens_css_before_the_resume_block_is_blocked(tmp_path):
    _write(tmp_path / "prototype/discussion.md", "# Discussion\n")
    with pytest.raises(ValueError, match="USER-INPUT:"):
        eb.check(_payload(tmp_path, "prototype/shared/tokens.css"))


def test_artifacts_after_the_resume_block_pass(tmp_path):
    _write(tmp_path / "prototype/discussion.md",
           "# Discussion\n\n## Resume\n- Execution boundary: active\n")
    payload = _payload(tmp_path, "prototype/shared/tokens.css")
    eb.check(payload)
    assert "hookSpecificOutput" not in payload


def test_layered_resume_seam_closes_the_window(tmp_path):
    _write(tmp_path / "prototype/truth.md", "# Truth\n")
    _write(tmp_path / "prototype/world.md", "# World\n")
    with pytest.raises(ValueError, match="Turn 2"):
        eb.check(_payload(tmp_path, "prototype/experiments/s/index.html"))
    _write(tmp_path / "prototype/discussion.md", "## Resume\n- Execution boundary: active\n")
    later = _payload(tmp_path, "prototype/experiments/s/index.html")
    eb.check(later)


def test_design_record_files_never_trip_the_window(tmp_path):
    _write(tmp_path / "prototype/discussion.md", "# Discussion\n")
    for rel in ("prototype/discussion.md", "prototype/briefs/s.md"):
        eb.check(_payload(tmp_path, rel))


def test_resume_heading_tolerates_level_suffix_and_chinese(tmp_path):
    """A format slip in the Resume heading must not wedge the hard gate."""
    proto = tmp_path / "prototype"
    for heading in ("## Resume", "### Resume", "## Resume / Next Steps",
                    "## 恢复", "#### Resume 断点"):
        _write(proto / "discussion.md", f"# Doc\n\n{heading}\n- Execution boundary: active\n")
        assert eb.resume_written(tmp_path), heading


def test_boundary_status_tolerates_emphasis_bullet_and_chinese(tmp_path):
    """A state field written with common markdown variants still reads."""
    cases = [
        ("- Execution boundary: active", "active"),
        ("**Execution boundary**: released", "released"),
        ("- **Execution boundary：** active", "active"),
        ("执行边界：released", "released"),
        ("Execution boundary: active", "active"),
    ]
    rec = tmp_path / "discussion.md"
    for text, expected in cases:
        rec.write_text(f"## Resume\n{text}\n", encoding="utf-8")
        assert eb.boundary_status(rec) == expected, text


def test_boundary_status_ignores_markdown_code_fences(tmp_path):
    rec = tmp_path / "discussion.md"
    rec.write_text(
        "## Resume\n```markdown\n- Execution boundary: released\n```\n"
        "- Execution boundary: active\n", encoding="utf-8")
    assert eb.boundary_status(rec) == "active"


def test_resume_inside_code_fence_does_not_open_artifact_window(tmp_path):
    _write(tmp_path / "prototype/discussion.md",
           "```markdown\n## Resume\n- Execution boundary: active\n```\n")
    with pytest.raises(ValueError, match="Turn 2"):
        eb.check(_payload(tmp_path, "prototype/experiments/s/anchor/index.html"))

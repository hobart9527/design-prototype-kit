"""Write-time advisory: a canonical spec view written with no compiled IR yet.

The advisory is a soft signal, never a block: the IR is authored at Stage 5, so
an absent IR is a legal intermediate state while the design converges. The
signal fires at the write, when the reminder is still actionable, rather than
at delivery, when the missing IR is only a verdict.

Hermetic: no network, no LLM, no browser.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import execution_boundary as eb  # noqa: E402


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _active_root(tmp_path: Path) -> Path:
    """An active discussion record makes tmp_path the admitted project root."""
    _write(tmp_path / "prototype/discussion.md",
           "# Discussion\n\n## Resume\n- Execution boundary: active\n")
    return tmp_path


def _write_payload(root: Path, rel: str, content: str) -> dict:
    return {
        "tool_name": "Write",
        "tool_input": {"file_path": str(root / rel), "content": content},
        "cwd": str(root),
    }


def test_a_canonical_view_written_with_no_ir_carries_an_advisory(tmp_path):
    root = _active_root(tmp_path)
    payload = _write_payload(root, "prototype/specifications/console/r1.spec.md", "# Spec\n")
    eb.check(payload)
    advisory = payload.get("hookSpecificOutput", {}).get("additionalContext", "")
    assert "r1.spec.md written with no compiled IR" in advisory
    assert "contracts/compiled/console/r1.spec.json absent" in advisory
    assert "compile_spec_ir.py --slice console" in advisory


def test_a_view_with_its_ir_present_carries_no_advisory(tmp_path):
    root = _active_root(tmp_path)
    _write(root / "prototype/contracts/compiled/console/r1.spec.json", "{}")
    payload = _write_payload(root, "prototype/specifications/console/r1.spec.md", "# Spec\n")
    eb.check(payload)
    assert "hookSpecificOutput" not in payload


def test_a_non_spec_write_carries_no_advisory(tmp_path):
    root = _active_root(tmp_path)
    payload = _write_payload(root, "prototype/discussion.md", "# Discussion\n")
    eb.check(payload)
    assert "hookSpecificOutput" not in payload


def test_a_non_canonical_markdown_write_carries_no_advisory(tmp_path):
    """A plain `.md` (legacy `r1.md`, notes) is not the IR's rendering — no signal."""
    root = _active_root(tmp_path)
    payload = _write_payload(root, "prototype/specifications/console/r1.md", "# Legacy\n")
    eb.check(payload)
    assert "hookSpecificOutput" not in payload


def test_main_surfaces_the_advisory_without_blocking(tmp_path, capsys, monkeypatch):
    root = _active_root(tmp_path)
    payload = _write_payload(root, "prototype/specifications/console/r1.spec.md", "# Spec\n")
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(payload)))
    eb.main()
    out = json.loads(capsys.readouterr().out)
    hook = out.get("hookSpecificOutput", {})
    # Advisory only: no deny decision accompanies it.
    assert "no compiled IR" in hook.get("additionalContext", "")
    assert hook.get("permissionDecision") is None


def test_main_still_denies_a_real_boundary_escape(tmp_path, capsys, monkeypatch):
    root = _active_root(tmp_path)
    payload = _write_payload(root, "outside.md", "# escape\n")
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO(json.dumps(payload)))
    eb.main()
    out = json.loads(capsys.readouterr().out)
    hook = out.get("hookSpecificOutput", {})
    assert hook.get("permissionDecision") == "deny"
    assert "prototype/" in hook.get("permissionDecisionReason", "")

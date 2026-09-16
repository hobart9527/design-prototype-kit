"""Guardrails for the spec-prototype DTCG token exporter script."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/spec-prototype/scripts/export-tokens.py"


def _run(tokens_path: Path, output_path: Path | None = None) -> tuple[int, str, str]:
    args = [sys.executable, str(SCRIPT), str(tokens_path)]
    if output_path:
        args.extend(["--output", str(output_path)])
    res = subprocess.run(args, text=True, capture_output=True)
    return res.returncode, res.stdout, res.stderr


def test_export_tokens_parses_template_to_valid_dtcg(tmp_path: Path):
    sample_tokens = tmp_path / "tokens.md"
    sample_tokens.write_text("""# Design Tokens

## Identity
- Foundation revision: v1
- Tokens revision: v1
- Generated at: 2026-09-11

## Color
| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#0055ff` | Primary action |
| `--color-surface` | `#ffffff` | Background |

## Spacing
| Token | Value | Usage |
|---|---|---|
| `--space-1` | `4px` | Micro gap |
| `--space-2` | `8px` | Small gap |

## Motion
| Token | Value | Usage |
|---|---|---|
| `--duration-fast` | `150ms` | Micro interaction |
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Enter view |
| `--spring-settle` | `180 / 12 / 1` | Settle |
""", encoding="utf-8")

    out_json = tmp_path / "tokens.json"
    code, stdout, stderr = _run(sample_tokens, out_json)
    assert code == 0, stderr
    assert out_json.is_file()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert "$schema" in data
    assert "color" in data
    assert data["color"]["primary"]["$value"] == "#0055ff"
    assert data["color"]["primary"]["$type"] == "color"
    assert data["color"]["primary"]["$description"] == "Primary action"

    assert "spacing" in data
    assert data["spacing"]["1"]["$value"] == "4px"
    assert data["spacing"]["1"]["$type"] == "dimension"

    assert "motion" in data
    assert data["motion"]["duration-fast"]["$type"] == "duration"
    assert data["motion"]["ease-out"]["$type"] == "cubicBezier"
    assert data["motion"]["spring-settle"]["$type"] == "transition"


def test_export_tokens_stdout_and_missing_file(tmp_path: Path):
    code, stdout, stderr = _run(tmp_path / "nonexistent.md")
    assert code == 1
    assert "not found" in stderr

def test_export_preserves_existing_different_revision_bytes(tmp_path):
    source = tmp_path/'v1.md'
    source.write_text('## Color\n| --color-primary | #123456 | Action |\n')
    output = source.with_suffix('.json')
    output.write_text('retained export')
    code, stdout, stderr = _run(source, output)
    assert code == 1
    assert output.read_text() == 'retained export'

def test_export_cannot_overwrite_source_or_symlink_target(tmp_path):
    source = tmp_path/'v1.md'
    source.write_text('## Color\n| --color-primary | #123456 | Action |\n')
    original = source.read_bytes()
    assert _run(source, source)[0] == 1
    output = source.with_suffix('.json')
    output.symlink_to(source)
    assert _run(source, output)[0] == 1
    assert source.read_bytes() == original

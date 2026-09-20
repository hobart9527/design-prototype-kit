"""Guardrails for the spec-prototype DTCG token exporter script."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import importlib.util

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/spec-prototype/scripts/export-tokens.py"
COMPILE_SCRIPT = ROOT / "skills/spec-prototype/scripts/compile_tokens.py"


def _load_compiler():
    spec = importlib.util.spec_from_file_location("compile_tokens", COMPILE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _luma(hex_code: str) -> tuple[int, int, int]:
    h = hex_code.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _is_gray(hex_code: str) -> bool:
    r, g, b = _luma(hex_code)
    return max(r, g, b) - min(r, g, b) == 0


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


def test_export_tokens_parses_two_column_breakpoints(tmp_path: Path):
    sample_tokens = tmp_path / "tokens.md"
    sample_tokens.write_text("""# Design Tokens

## Breakpoints
| Token | Value |
|---|---|
| `--bp-mobile` | `390px` |
| `--bp-tablet` | `768px` |
| `--bp-desktop` | `1280px` |
| `--bp-wide` | `1600px` |
""", encoding="utf-8")

    out_json = tmp_path / "tokens.json"
    code, stdout, stderr = _run(sample_tokens, out_json)
    assert code == 0, stderr
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert "breakpoints" in data
    assert set(data["breakpoints"].keys()) == {"mobile", "tablet", "desktop", "wide"}
    assert data["breakpoints"]["mobile"]["$value"] == "390px"
    assert data["breakpoints"]["wide"]["$value"] == "1600px"


def test_compile_tokens_empty_dials_yield_neutral_scaffold():
    ct = _load_compiler()
    tokens = ct.compute_tokens({})
    colors = tokens["colors"]

    # Neutral grayscale surfaces; no acid-lime accent and no industrial near-black void.
    assert _is_gray(colors["accent_primary"]), colors["accent_primary"]
    assert _is_gray(colors["bg_void"]), colors["bg_void"]
    assert _is_gray(colors["bg_surface"]), colors["bg_surface"]
    assert colors["accent_primary"] != "#d6f56b"
    assert colors["bg_void"] != "#080b0b"

    css = ct.generate_css(tokens)
    assert "machined-industrial" not in css
    assert "#d6f56b" not in css


def test_omitted_dials_palette_stays_neutral_in_formal_mode():
    ct = _load_compiler()
    palette = ct.extract_dynamic_palette("")
    assert _is_gray(palette["accent_primary"]), palette["accent_primary"]
    assert palette["bg_void"] != "#080b0b"

    # Probe mode is the only path that may infer a themed accent from domain prose.
    probed = ct.extract_dynamic_palette("SRE cluster telemetry incident ops", mode="probe")
    assert not _is_gray(probed["accent_primary"])


def test_formal_empty_dials_yield_steady_motion_not_kinetic_hud():
    ct = _load_compiler()
    tokens = ct.compute_tokens({})
    motion = tokens["motion"]

    # Undeclared energy must not silently compile to a kinetic HUD detent.
    assert motion["ease_hud"] != "cubic-bezier(0.16, 1, 0.3, 1)"
    assert motion["duration_fast"] == "150ms"
    assert motion["duration_normal"] == "250ms"
    assert motion["duration_slow"] == "400ms"

    css = ct.generate_css(tokens)
    assert ".btn-tactile:active" not in css
    assert not motion["tactile_active"]


def test_explicit_kinetic_energy_restores_hud_motion_and_detent():
    ct = _load_compiler()
    tokens = ct.compute_tokens({"energy": "kinetic"})
    motion = tokens["motion"]

    assert motion["ease_hud"] == "cubic-bezier(0.16, 1, 0.3, 1)"
    assert motion["duration_fast"] == "80ms"
    assert motion["tactile_active"]

    css = ct.generate_css(tokens)
    assert ".btn-tactile:active" in css

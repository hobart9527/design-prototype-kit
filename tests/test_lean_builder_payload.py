"""Lean builder payload and adaptive inspection viewports.

Mechanism checks over temporary repositories. Not real-session evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/spec-prototype/scripts"
sys.path.insert(0, str(SCRIPTS))

import assemble_envelope  # noqa: E402
from test_platform_envelope import SLICE, build_repo  # noqa: E402

IR_FIELDS = (
    "identity",
    "semantic_contract",
    "layout_directives",
    "visual_directives",
    "action_contracts",
    "verification_contract",
    "open_design_space",
)

CONTEXT_FIELDS = (
    "envelope_version",
    "mode",
    "repository_root",
    "skill_root",
    "slice_id",
    "platform",
    "coverage",
    "target_html_path",
    "evidence_output_dir",
    "verification_command",
    "capture_command",
    "inspection_contract",
    "spec_sources",
    "spec_references",
    "token_link_tag",
)

LEGACY_FIELDS = (
    "constraint_envelope",
    "creative_envelope",
    "available_tokens",
    "app_shell_blueprint",
    "app_shell_contract",
    "ooux_topology",
    "cognitive_ledger",
    "fault_tolerance_protocol",
    "domain_thesis",
    "attention_routing",
    "data_stress_boundaries",
    "interaction_spec",
    "design_constraints",
    "verifiable_assertions",
    "active_methods",
    "five_axes",
    "dtcg_tokens",
    "layout_profile",
    "candidate_patterns",
    "selected_pattern",
    "reality_anchors",
    "topology_context",
    "specification",
    "tokens_md_ref",
)


def assemble(root: Path) -> dict:
    return assemble_envelope.assemble(root, SLICE)


def with_device(root: Path, device: str) -> None:
    product = root / "prototype/product.md"
    text = product.read_text(encoding="utf-8")
    replacement = f"device-context: {device}\n" if device else ""
    product.write_text(text.replace("device-context: desktop\n", replacement), encoding="utf-8")


def viewport_widths(env: dict) -> list:
    return [v["width"] for v in env["inspection_contract"]["mandatory_viewports"]]


# CPC: the builder prompt carries the canonical IR and execution context only.

def test_lean_payload_keeps_canonical_ir_and_execution_context(tmp_path):
    env = assemble(build_repo(tmp_path))
    payload = assemble_envelope.build_builder_payload(env)
    for field in IR_FIELDS + CONTEXT_FIELDS:
        assert field in payload, f"lean payload dropped required field: {field}"


def test_lean_payload_demotes_legacy_intermediate_blobs(tmp_path):
    env = assemble(build_repo(tmp_path))
    payload = assemble_envelope.build_builder_payload(env)
    for field in LEGACY_FIELDS:
        assert field in env, f"fixture no longer emits {field}"
        assert field not in payload, f"legacy blob {field} leaked into the builder prompt"
    assert "debug_context" not in payload


def test_debug_context_retains_demoted_blobs_on_request(tmp_path):
    env = assemble(build_repo(tmp_path))
    payload = assemble_envelope.build_builder_payload(env, include_debug=True)
    debug = payload["debug_context"]
    for field in LEGACY_FIELDS:
        assert debug[field] == env[field], f"debug context lost {field}"
    # The lean view stays intact even when the debug channel is attached.
    assert payload["identity"] == env["identity"]


def test_payload_preserves_dispatch_critical_identity(tmp_path):
    env = assemble(build_repo(tmp_path))
    payload = assemble_envelope.build_builder_payload(env)
    # execution_boundary.dispatch reads these before it admits a builder launch.
    assert payload["repository_root"] == env["repository_root"]
    assert payload["skill_root"] == env["skill_root"]
    assert payload["mode"] == "lean-builder-envelope"
    assert payload["slice_id"] == SLICE
    assert payload["spec_sources"] == env["spec_sources"]
    assert payload["target_html_path"] == env["target_html_path"]


def test_output_file_carries_the_lean_payload(tmp_path, monkeypatch, capsys):
    root = build_repo(tmp_path)
    out = tmp_path / "envelope.json"
    monkeypatch.setattr(sys, "argv", [
        "assemble_envelope.py", "--root", str(root), "--slice", SLICE, "--output", str(out)])
    assemble_envelope.main()
    capsys.readouterr()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["identity"]["slice_id"] == SLICE
    assert "open_design_space" in data
    assert "creative_envelope" not in data
    assert "constraint_envelope" not in data


# CPC: mandatory viewports derive from the authored device fact, not a fixed pair.

def test_desktop_device_inspects_the_desktop_canvas_only(tmp_path):
    root = build_repo(tmp_path)
    with_device(root, "desktop")
    env = assemble(root)
    assert viewport_widths(env) == [1280]


def test_mobile_device_inspects_the_somatic_viewport_only(tmp_path):
    root = build_repo(tmp_path)
    with_device(root, "mobile")
    env = assemble(root)
    assert viewport_widths(env) == [390]


def test_tablet_device_inspects_the_tablet_viewport(tmp_path):
    root = build_repo(tmp_path)
    with_device(root, "tablet")
    env = assemble(root)
    assert viewport_widths(env) == [768]


def test_undeclared_device_keeps_both_extremes(tmp_path):
    root = build_repo(tmp_path)
    with_device(root, "")
    env = assemble(root)
    assert viewport_widths(env) == [1280, 390]

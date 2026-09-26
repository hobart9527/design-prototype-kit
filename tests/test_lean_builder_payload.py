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
from test_platform_envelope import SLICE, build_canonical_repo, build_repo, write  # noqa: E402

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
    "content_language",
    "topology_context",
    "interaction_spec",
    "active_methods",
)

SLIM_METHOD_FIELDS = ("id", "name", "pillars", "invariants", "reference_file")

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
    "design_constraints",
    "verifiable_assertions",
    "five_axes",
    "dtcg_tokens",
    "layout_profile",
    "candidate_patterns",
    "selected_pattern",
    "reality_anchors",
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


def test_authored_content_language_reaches_the_payload_root(tmp_path):
    env = assemble(build_repo(tmp_path))
    payload = assemble_envelope.build_builder_payload(env)
    assert payload["content_language"] == env["content_language"]
    assert payload["content_language"]["tag"] == "en-US"
    assert "content_language" not in payload.get("debug_context", {})


def test_content_language_annotation_is_tolerated(tmp_path):
    root = build_repo(tmp_path)
    spec = root / f"prototype/specifications/{SLICE}/r1.md"
    spec.write_text(
        spec.read_text(encoding="utf-8").replace(
            "- Content language: en-US", "- Content language (locked): en-US"),
        encoding="utf-8")
    contract = root / f"prototype/contracts/slices/{SLICE}/c1.md"
    contract.write_text(
        contract.read_text(encoding="utf-8").replace(
            "- Content language: en-US", "- Content language (locked): en-US"),
        encoding="utf-8")
    env = assemble(root)
    assert env["content_language"]["tag"] == "en-US"


def test_topology_and_interaction_contracts_are_readable(tmp_path):
    env = assemble(build_repo(tmp_path))
    payload = assemble_envelope.build_builder_payload(env)
    assert payload["topology_context"] == env["topology_context"]
    assert payload["interaction_spec"] == env["interaction_spec"]
    # The Builder reads these from the payload root, not a demoted copy.
    debug = assemble_envelope.build_builder_payload(env, include_debug=True)["debug_context"]
    for field in ("topology_context", "interaction_spec"):
        assert field not in debug


def test_slim_methods_ride_along_without_verbose_guidance(tmp_path):
    root = build_repo(tmp_path)
    spec = root / f"prototype/specifications/{SLICE}/r1.md"
    spec.write_text(
        spec.read_text(encoding="utf-8")
        + "- Methods applied: form-ergonomics, context-preservation\n",
        encoding="utf-8")
    env = assemble(root)
    payload = assemble_envelope.build_builder_payload(env)
    # Only the Spec-declared methods reach the Builder, carrying slim metadata.
    assert {m["id"] for m in payload["active_methods"]} == {"form-ergonomics", "context-preservation"}
    assert len(payload["active_methods"]) == len(env["active_methods"])
    for method in payload["active_methods"]:
        assert set(method) == set(SLIM_METHOD_FIELDS)
        assert "actionable_guidance" not in method


def test_undeclared_spec_activates_no_method(tmp_path):
    """A Spec naming no craft method sends none: no heuristic global default set."""
    env = assemble(build_repo(tmp_path))
    assert env["active_methods"] == []
    payload = assemble_envelope.build_builder_payload(env)
    assert payload["active_methods"] == []
    debug = assemble_envelope.build_builder_payload(env, include_debug=True)["debug_context"]
    assert debug["active_methods"] == []


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


# T-02: authored verification viewports own the inspection set; the device
# ladder is only the fallback when the Canonical Spec IR declares none.

def with_ir_viewports(root: Path, viewports: list) -> None:
    ir_path = root / "prototype/contracts/compiled/cluster-overview/r1.spec.json"
    ir = json.loads(ir_path.read_text(encoding="utf-8"))
    ir["scope"]["verification_scope"]["viewports"] = viewports
    ir_path.write_text(json.dumps(ir, indent=2, ensure_ascii=False), encoding="utf-8")


def test_authored_ir_viewports_override_the_device_ladder(tmp_path):
    root = build_canonical_repo(tmp_path)
    with_ir_viewports(root, [1440, 1024, 1440, 0])
    # device-context: desktop would otherwise inspect 1280 only; the authored
    # widths win sorted, deduped, positive.
    write(root / "prototype/product.md",
          "# Product Thesis: Terminal Cluster Workbench\n\n"
          "```prototype-context\nrecord: product\ndevice-context: desktop\n```\n")
    env = assemble_envelope.assemble(root, "cluster-overview")
    assert viewport_widths(env) == [1024, 1440]
    assert "--viewports 1024,1440" in env["capture_command"]

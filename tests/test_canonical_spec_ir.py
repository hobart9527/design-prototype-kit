"""Tests for the Canonical Prototype Specification IR Compiler and Single-file Spec Projection."""

import json
from pathlib import Path
import sys
import pytest
import jsonschema

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from compile_spec_ir import compile_canonical_ir, render_single_spec_md, SCHEMA_PATH


def test_schema_validates_canonical_ir(tmp_path: Path):
    """Verify that compiled IR strictly satisfies prototype-spec.v1.json schema."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text("""# Design Discussion: Terminal Cluster Workbench

## 1. 业务与用户极端张力 (Core Tension)
- Operational through-put vs Catastrophic Bus-Hang Failures.

## 2. 现实双地锚 (Reality Benchmark Anchors)
- Operational Grounding: Slurm + Run:ai
- Kinetic Grounding: Vernier Caliper detents

## 4. 5-Dial 风格寄存器 (5-Dial Style Register)
- Density: dense
- Finish: machined-industrial
- Palette: plasma-cyan

## 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/cluster-overview`
- **上下文视图 (Contextual)**: `surfaces/incident-drawer`
""", encoding="utf-8")

    ir = compile_canonical_ir(
        root=tmp_path,
        slice_id="cluster-overview",
        candidate_id="r1",
        stage="hero_probe",
    )

    # Validate with jsonschema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=ir, schema=schema)

    assert ir["schema_version"] == "prototype-spec/v1"
    assert ir["identity"]["slice_id"] == "cluster-overview"
    assert ir["identity"]["candidate_revision"] == "r1"
    assert ir["identity"]["authority_status"] == "sealed_provisional"

    # Verify Scope Separation (Topology vs Build)
    assert ir["scope"]["topology_scope"]["coverage"] in ("key-journey", "slice-isolated")
    assert ir["scope"]["build_scope"]["stage"] == "hero_probe"
    assert ir["scope"]["build_scope"]["selected_surfaces"] == ["cluster-overview"]
    assert "incident-drawer" in ir["scope"]["build_scope"]["context_surfaces"]

    # Verify Invariants & States
    assert len(ir["invariants"]) >= 3
    assert len(ir["state_model"]["domain_states"]) >= 2
    assert len(ir["state_model"]["stress_fixtures"]) >= 3


def test_render_single_spec_md(tmp_path: Path):
    """Verify rendering of unified single-file RFC Specification."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text("""# Design Discussion: Test Single Spec View
## 1. 业务与用户极端张力
- High-volume publishing vs Editorial authenticity
""", encoding="utf-8")

    ir = compile_canonical_ir(root=tmp_path, slice_id="editorial-gate")
    rendered_md = render_single_spec_md(ir)

    assert "# Prototype Specification: Test Single Spec View" in rendered_md
    assert "Authority Status" in rendered_md
    assert "1. Product & Architecture Context" in rendered_md
    assert "2. Sensory Calibration & Token Discipline" in rendered_md
    assert "3. State Models & Action Lifecycle" in rendered_md
    assert "4. Verifiable Design Invariants & Break Protocol" in rendered_md
    assert "5. Verification Scope & Evidence Binding" in rendered_md
    # Verify new scope binding lines
    assert "Prototype write scope" in rendered_md
    assert "Evidence write scope" in rendered_md


def test_dial_alias_weight_maps_to_materiality():
    """Verify weight maps to materiality in compile_spec_ir (aligned with compile_tokens)."""
    from compile_spec_ir import parse_5_dial_register
    dials = parse_5_dial_register("- weight: dense-tactile")
    assert dials["materiality"] == "dense-tactile"


def test_handoff_packet_routes_canonical_spec(tmp_path: Path):
    """Verify handoff.py packet and pillar_packet resolve canonical .spec.md."""
    from handoff import pillar_packet

    # Setup minimal repository layout
    spec_dir = tmp_path / "prototype/specifications/test-slice"
    spec_dir.mkdir(parents=True)
    shared_dir = tmp_path / "prototype/shared"
    shared_dir.mkdir(parents=True)
    (shared_dir / "tokens.css").write_text(":root { --primary: #000; }", encoding="utf-8")

    spec_file = spec_dir / "r1.spec.md"
    spec_file.write_text("""# Prototype Specification: Test (test-slice/r1)
> **Authority Status**: `SEALED_PROVISIONAL` | **Revision**: `c1` / `r1`
> **Source Reference**: `prototype/discussion.md` (sha256:abc)

## 5. Verification Scope & Evidence Binding
- **Prototype write scope**: `prototype/experiments/test-slice/r1/`
- **Evidence write scope**: `prototype/evidence/test-slice/r1/`
- **Authority status**: `sealed_provisional`
""", encoding="utf-8")

    pkt = pillar_packet(tmp_path, spec_file)
    assert pkt["slice_id"] == "test-slice"
    assert pkt["candidate_id"] == "r1.spec"
    assert pkt["prototype_write_scope"] == "prototype/experiments/test-slice/r1/"
    assert pkt["evidence_write_scope"] == "prototype/evidence/test-slice/r1/"
    assert "tokens_css" in pkt["references"]


def test_assemble_envelope_canonical_lint_and_status(tmp_path: Path):
    """Verify assemble_envelope carries status from canonical IR and runs canonical lint."""
    from assemble_envelope import assemble

    slice_id = "sample-gate"
    compiled_dir = tmp_path / f"prototype/contracts/compiled/{slice_id}"
    compiled_dir.mkdir(parents=True)
    shared_dir = tmp_path / "prototype/shared"
    shared_dir.mkdir(parents=True)
    (shared_dir / "tokens.css").write_text(":root { --accent: #fff; }", encoding="utf-8")

    # Create canonical IR with validated status
    ir_data = {
        "schema_version": "prototype-spec/v1",
        "identity": {
            "product_id": "test-product",
            "slice_id": slice_id,
            "contract_revision": "c1",
            "candidate_revision": "r1",
            "authority_status": "validated",
            "title": "Test Gate"
        },
        "sources": {"core_tension": None, "reality_anchors": []},
        "scope": {
            "topology_scope": {"coverage": "key-journey", "declared_surfaces": ["gate"], "primary_surface": "gate"},
            "build_scope": {"stage": "hero_probe", "selected_surfaces": ["gate"], "context_surfaces": []},
            "verification_scope": {"viewports": [1280], "required_states": ["draft"]}
        },
        "foundation": {"five_axes": {}},
        "state_model": {"domain_states": [], "interaction_states": [], "data_scenarios": [], "stress_fixtures": []},
        "actions": [],
        "invariants": [],
        "artifacts_binding": {
            "tokens_css": "prototype/shared/tokens.css",
            "tokens_json": "prototype/contracts/tokens/t1.json",
            "human_spec_md": f"prototype/specifications/{slice_id}/r1.spec.md",
            "prototype_html": f"prototype/experiments/{slice_id}/r1/index.html"
        }
    }
    (compiled_dir / "r1.spec.json").write_text(json.dumps(ir_data), encoding="utf-8")

    spec_dir = tmp_path / f"prototype/specifications/{slice_id}"
    spec_dir.mkdir(parents=True)
    (spec_dir / "r1.spec.md").write_text("# Spec", encoding="utf-8")

    envelope = assemble(tmp_path, slice_id, lint=True)
    # Authority status must carry through from canonical IR
    assert envelope["authority_status"] == "validated"
    # contract_lint must be populated (list, not absent)
    assert "contract_lint" in envelope
    assert isinstance(envelope["contract_lint"], list)


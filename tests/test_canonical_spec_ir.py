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

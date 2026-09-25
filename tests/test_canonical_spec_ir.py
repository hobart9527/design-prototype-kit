"""Tests for the Canonical Prototype Specification IR Compiler and Single-file Spec Projection."""

import json
from pathlib import Path
import subprocess
import sys
import pytest
import jsonschema

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from compile_spec_ir import (
    compile_canonical_ir,
    render_single_spec_md,
    SCHEMA_PATH,
    IncompleteStageContractError,
)

# Executable authoring example: every section the compiler requires non-empty.
# This fixture is the canonical "how an author must write discussion.md" proof.
COMPLETE_DISCUSSION = """# Design Discussion: Terminal Cluster Workbench

## 1. 业务与用户极端张力 (Core Tension)
- Operational through-put vs Catastrophic Bus-Hang Failures.

## 2. 现实双地锚 (Reality Benchmark Anchors)
- Operational Grounding: Slurm + Run:ai
- Kinetic Grounding: Vernier Caliper detents

## 3. 项目级状态模型 (State Model)
- `domain/cluster-nominal` (集群常态): 全部节点健康，张量流水线满负荷。
- `domain/incident-active` (故障激活): 单机 NVLink 挂起，等待排空。
- `interaction/inspecting` (检视中): 抽屉展开、等待确认。
- `interaction/committing` (提交中): 排空动作机械压感执行。
- `data/cold-metrics` (冷指标): 首次加载、缓存未命中、时序抖动。

## 4. 5-Dial 风格寄存器 (5-Dial Style Register)
- Density: dense
- Finish: machined-industrial
- Palette: plasma-cyan

## 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/cluster-overview`
- **上下文视图 (Contextual)**: `surfaces/incident-drawer`

## 6. Viewport 与强制测试状态
- `Viewport`: `390px` (phone) / `1280px` (desktop)
- `Required States`: `state-draft`, `state-sealed`

## 7. 破坏协议 (Break Protocol)
- `stress/bus-hang` | Vector: `NVLink 链路挂起 6 秒` | Expected: `2 秒内定位故障节点并显示降级徽标`。
- `stress/cold-boot` | Vector: `冷启动空缓存` | Expected: `骨架屏占位 + 降级徽标`。
"""


def test_schema_validates_canonical_ir(tmp_path: Path):
    """Verify that compiled IR strictly satisfies prototype-spec.v1.json schema."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text(COMPLETE_DISCUSSION, encoding="utf-8")

    ir = compile_canonical_ir(
        root=tmp_path,
        slice_id="cluster-overview",
        candidate_id="r1",
        stage="hero_probe",
    )

    # Validate with jsonschema (schema enforces minItems on the state/scope arrays)
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

    # Verify REAL extracted values (not arbitrary lower bounds).
    # Invariants are admitted only from an authored section: this discussion
    # authors none, so none may be injected.
    assert ir["invariants"] == []
    assert ir["spec_tier"] == "intent_spec"
    assert [s["id"] for s in ir["state_model"]["domain_states"]] == [
        "domain/cluster-nominal",
        "domain/incident-active",
    ]
    assert ir["state_model"]["interaction_states"] == [
        "interaction/inspecting",
        "interaction/committing",
    ]
    assert ir["state_model"]["data_scenarios"] == [
        {"id": "data/cold-metrics", "description": "首次加载、缓存未命中、时序抖动。"}
    ]
    assert ir["state_model"]["stress_fixtures"] == [
        {
            "id": "stress/bus-hang",
            "vector": "NVLink 链路挂起 6 秒",
            "expected_behavior": "2 秒内定位故障节点并显示降级徽标",
        },
        {
            "id": "stress/cold-boot",
            "vector": "冷启动空缓存",
            "expected_behavior": "骨架屏占位 + 降级徽标",
        },
    ]
    assert ir["scope"]["verification_scope"]["viewports"] == [390, 1280]
    assert ir["scope"]["verification_scope"]["required_states"] == [
        "state-draft",
        "state-sealed",
    ]


def test_missing_required_sections_fail_loudly(tmp_path: Path):
    """Core behavior: absent required sections raise a single actionable error."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text(
        """# Design Discussion: Incomplete
## 1. 业务与用户极端张力 (Core Tension)
- Through-put vs Latency.
""",
        encoding="utf-8",
    )

    with pytest.raises(IncompleteStageContractError) as excinfo:
        compile_canonical_ir(root=tmp_path, slice_id="incomplete-gate")

    message = str(excinfo.value)
    # Every missing item is reported at once, with its section and format.
    for key in (
        "domain_states",
        "interaction_states",
        "data_scenarios",
        "stress_fixtures",
        "viewports",
        "required_states",
    ):
        assert key in message
    assert "发现 7 项缺失" in message
    assert excinfo.value.violations
    assert "Stage 1 §3" in message


def test_allow_incomplete_bypasses_gate(tmp_path: Path):
    """The escape hatch suppresses the hard failure (debug path only)."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text("# Design Discussion: Incomplete\n## 1. 极端张力\n- x\n", encoding="utf-8")

    ir = compile_canonical_ir(
        root=tmp_path, slice_id="incomplete-gate", allow_incomplete=True
    )
    assert ir["state_model"]["domain_states"] == []
    assert ir["scope"]["verification_scope"]["viewports"] == []


def test_cli_fails_nonzero_and_lists_missing(tmp_path: Path):
    """The frozen CLI exits non-zero and prints the actionable missing list."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text("# Design Discussion: Incomplete\n## 1. 极端张力\n- x\n", encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "compile_spec_ir.py"),
            "--root",
            str(tmp_path),
            "--slice",
            "incomplete-gate",
            "--candidate",
            "r1",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "domain_states" in proc.stderr
    assert "missing" in proc.stderr or "缺少" in proc.stderr


def test_render_single_spec_md(tmp_path: Path):
    """Verify rendering of unified single-file RFC Specification."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text(COMPLETE_DISCUSSION, encoding="utf-8")

    ir = compile_canonical_ir(root=tmp_path, slice_id="cluster-overview")
    rendered_md = render_single_spec_md(ir)

    assert "# Prototype Specification: Terminal Cluster Workbench" in rendered_md
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


STAGE1_DISCUSSION = """# Design Discussion: Reading Sanctuary

## 1. 业务与用户极端张力 (Core Tension)
- Deep Contemplation vs Digital Attention Economy.

## 2. 现实双地锚 (Reality Benchmark Anchors)
- Operational Grounding: iA Writer
- Kinetic Grounding: Paperback page turns

## 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `reader/article-canvas`

## 8. Design Invariants (设计不变式)
- `inv/accent-seal` | Accent seal reserved for irreversible commits | severity: blocking | verification: computed_style | applies_to: draft, idle
"""


def _write_discussion(tmp_path: Path, text: str) -> Path:
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text(text, encoding="utf-8")
    return tmp_path


def test_stage1_intent_spec_compiles_and_validates(tmp_path: Path):
    """Positive specimen: thesis + topology + craft intent with no states admits intent_spec."""
    root = _write_discussion(tmp_path, STAGE1_DISCUSSION)

    ir = compile_canonical_ir(root=root, slice_id="reading-sanctuary", stage="hero_probe")

    assert ir["spec_tier"] == "intent_spec"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=ir, schema=schema)
    # No state_model requirement at Stage 1: the section may be wholly absent.
    assert ir["state_model"]["domain_states"] == []
    # Authored invariants are kept verbatim; nothing is injected.
    assert [i["id"] for i in ir["invariants"]] == ["inv/accent-seal"]
    assert ir["invariants"][0]["severity"] == "blocking"
    # Meso assembly slots: undeclared massing smooths to a fallback, unauthored
    # kinematics/data_syntax stay absent.
    assert ir["layout_directives"]["massing_pattern"]
    assert "interaction_spec" not in ir or "kinematics" not in ir.get("interaction_spec", {})
    assert "visual_directives" not in ir or "data_syntax" not in ir.get("visual_directives", {})


def test_authored_meso_slots_pass_through(tmp_path: Path):
    """Authored massing/kinematics/data_syntax declarations reach the IR verbatim."""
    root = _write_discussion(tmp_path, STAGE1_DISCUSSION.replace(
        "## 5. OOUX 实体拓扑与表面分配",
        "## 5. OOUX 实体拓扑与表面分配\n- `massing_pattern`: `split-stream`\n- `kinematics`: `focus-restore-250ms`\n- `data_syntax`: `micro-trend-compact`",
    ))
    ir = compile_canonical_ir(root=root, slice_id="reading-sanctuary")
    assert ir["layout_directives"]["massing_pattern"] == "split-stream"
    assert ir["interaction_spec"]["kinematics"] == "focus-restore-250ms"
    assert ir["visual_directives"]["data_syntax"] == "micro-trend-compact"


def test_stage1_only_ir_rejected_when_execution_spec_required(tmp_path: Path):
    """Boundary specimen: execution_spec demand on Stage-1-only IR names the missing states."""
    root = _write_discussion(tmp_path, STAGE1_DISCUSSION)

    with pytest.raises(IncompleteStageContractError) as excinfo:
        compile_canonical_ir(root=root, slice_id="reading-sanctuary", required_tier="execution_spec")

    message = str(excinfo.value)
    assert "execution_spec" in message
    assert "state_model" in message or "domain_states" in message


def test_whole_state_ids_survive_compilation(tmp_path: Path):
    """Full identifiers like `interaction/inspecting` reach state_model entries intact."""
    ir = compile_canonical_ir(
        root=_write_discussion(tmp_path, COMPLETE_DISCUSSION),
        slice_id="cluster-overview",
        stage="hero_probe",
    )
    assert "interaction/inspecting" in ir["state_model"]["interaction_states"]
    assert "interaction/committing" in ir["state_model"]["interaction_states"]


def test_unauthored_discussion_injects_no_invariants(tmp_path: Path):
    """An unauthored discussion yields an empty invariants array, never templates."""
    root = _write_discussion(tmp_path, COMPLETE_DISCUSSION)
    ir = compile_canonical_ir(root=root, slice_id="cluster-overview", stage="hero_probe")
    assert ir["invariants"] == []


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
        "spec_tier": "intent_spec",
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


def test_lint_canonical_spec_ir_schema_and_boundary(tmp_path: Path):
    from lint_spec_contracts import lint_canonical_spec_ir

    slice_id = "test-slice"
    compiled_dir = tmp_path / f"prototype/contracts/compiled/{slice_id}"
    compiled_dir.mkdir(parents=True)

    # Missing IR returns E001
    errors = lint_canonical_spec_ir(tmp_path, slice_id)
    assert any(e.rule == "E001_FILE_MISSING" for e in errors)

    # Valid IR passes
    valid_ir = {
        "schema_version": "prototype-spec/v1",
        "spec_tier": "execution_spec",
        "identity": {
            "product_id": "test",
            "slice_id": slice_id,
            "contract_revision": "c1",
            "candidate_revision": "r1",
            "authority_status": "draft",
            "title": "Test"
        },
        "sources": {
            "discussion_ref": "prototype/discussion.md",
            "discussion_sha256": "sha256:dummy",
            "core_tension": None,
            "reality_anchors": []
        },
        "scope": {
            "topology_scope": {"coverage": "key-journey", "declared_surfaces": ["s1"], "primary_surface": "s1"},
            "build_scope": {"stage": "hero_probe", "selected_surfaces": ["s1"], "context_surfaces": []},
            "verification_scope": {"viewports": [1280], "required_states": ["draft"]}
        },
        "foundation": {
            "five_axes": {
                "density": "dense",
                "energy": "quiet",
                "materiality": "subtle",
                "rhythm": "fluid",
                "character": "restrained"
            },
            "palette_discipline": {
                "accent_seal": "var(--accent-seal)",
                "accent_policy": "Forbidden on draft"
            }
        },
        "state_model": {
            "domain_states": [{"id": "d1", "label": "D1", "description": "desc"}],
            "interaction_states": ["i1"],
            "data_scenarios": [{"id": "data1", "description": "desc"}],
            "stress_fixtures": [{"id": "s1", "vector": "v", "expected_behavior": "b"}]
        },
        "actions": [],
        "invariants": [],
        "artifacts_binding": {
            "tokens_css": "prototype/shared/tokens.css",
            "tokens_json": "prototype/contracts/tokens/t1.json",
            "human_spec_md": f"prototype/specifications/{slice_id}/r1.spec.md",
            "prototype_html": f"prototype/experiments/{slice_id}/r1/index.html"
        }
    }
    (compiled_dir / "r1.spec.json").write_text(json.dumps(valid_ir), encoding="utf-8")
    errors = lint_canonical_spec_ir(tmp_path, slice_id)
    assert not errors


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
    parse_action_verbs,
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
- Physical Anchor: desktop workstation
- Operational Grounding: Slurm + Run:ai
- Kinetic Grounding: Vernier Caliper detents

- Scene sentence: A reviewer compares signal drift during a live run.
- Signature Relationship: Review evidence stays beside the decision.
- Anti-slop match-and-refuse bans:
  - No ornamental neon gradient.
  - No fake device chrome.

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
    assert ir["sources"]["design_intent"]["scene_sentence"] == (
        "A reviewer compares signal drift during a live run."
    )
    assert ir["sources"]["design_intent"]["signature_relationship"] == (
        "Review evidence stays beside the decision."
    )
    assert ir["sources"]["design_intent"]["anti_slop_bans"] == [
        "No ornamental neon gradient.", "No fake device chrome."
    ]

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


def test_contract_actions_yaml_is_authoritative_and_fails_closed():
    from compile_spec_ir import parse_action_verbs

    actions = """```contract:actions
- id: action-enter
  verb: submit
  trigger: Enter
  proximity_level: 4
  commit: Commit
  feedback: Saved
```"""
    parsed = parse_action_verbs(actions)
    assert [item["id"] for item in parsed] == ["action-enter"]
    assert parsed[0]["authority"] == "explicit"
    assert parsed[0]["feedback"] == "Saved"

    duplicate = actions.replace(
        "  feedback: Saved",
        "  feedback: Saved\n- id: action-enter\n  verb: submit\n  trigger: Enter\n  commit: Again",
    )
    with pytest.raises(ValueError, match="duplicate id"):
        parse_action_verbs(duplicate)
    with pytest.raises(ValueError, match="missing required"):
        parse_action_verbs("```contract:actions\n- id: action-enter\n  verb: submit\n```")
    with pytest.raises(ValueError, match="invalid contract:actions YAML"):
        parse_action_verbs("```contract:actions\n- id: [\n```")


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
    assert "Product-Validated Design Rules" in rendered_md
    assert "No validated shared rules compiled" in rendered_md
    assert "Glance Sentinel" not in rendered_md
    assert "Command Cockpit" not in rendered_md
    assert "No authored viewport" not in rendered_md
    assert "Font families, weights, sizes and line heights belong to the bound token artifact" in rendered_md
    assert "do not infer a layout mode from width alone" in rendered_md


def test_dial_alias_weight_maps_to_materiality():
    """Verify weight maps to materiality in compile_spec_ir (aligned with compile_tokens)."""
    from compile_spec_ir import parse_5_dial_register
    dials = parse_5_dial_register("- weight: dense-tactile")
    assert dials["materiality"] == "dense-tactile"

def test_undeclared_axes_and_accent_stay_open():
    """Unset Five Axes and signature accent are open design space, not defaults."""
    from compile_spec_ir import parse_5_dial_register, parse_palette_discipline
    assert parse_5_dial_register("- density: sparse") == {"density": "sparse"}
    assert parse_5_dial_register("plain prose") == {}
    assert parse_palette_discipline("no accent authored") == {}
    authored = parse_palette_discipline(
        "- `--accent-seal`: `#B3352B`\n- **Accent Policy**: only on the final commit")
    assert authored == {"accent_seal": "var(--accent-seal, #B3352B)",
                        "accent_policy": "only on the final commit"}


STAGE1_DISCUSSION = """# Design Discussion: Reading Sanctuary

## 1. 业务与用户极端张力 (Core Tension)
- Deep Contemplation vs Digital Attention Economy.

## 2. 现实双地锚 (Reality Benchmark Anchors)
- Physical Anchor: desktop workstation
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


def test_stage2_entry_requires_an_explicit_physical_anchor(tmp_path: Path):
    unanchored = STAGE1_DISCUSSION.replace("- Physical Anchor: desktop workstation\n", "")
    root = _write_discussion(tmp_path, unanchored)

    with pytest.raises(IncompleteStageContractError, match="physical_anchor"):
        compile_canonical_ir(
            root=root, slice_id="reading-sanctuary", stage="hero_probe", required_tier="stage2")

    disc = root / "prototype/discussion.md"
    disc.write_text(
        unanchored.replace(
            "## 2. 现实双地锚 (Reality Benchmark Anchors)",
            "## 2. 现实双地锚 (Reality Benchmark Anchors)\n- Physical Anchor: none",
        ),
        encoding="utf-8",
    )
    ir = compile_canonical_ir(
        root=root, slice_id="reading-sanctuary", stage="hero_probe", required_tier="stage2")
    assert ir["spec_tier"] == "intent_spec"


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


def test_intent_json_is_the_stage1_machine_contract(tmp_path: Path):
    """prototype/intent.json supplies Stage 1 fields without prose recovery."""
    root = _write_discussion(tmp_path, "# Design Discussion\n\nNo structured sections here.\n")
    (root / "prototype/intent.json").write_text(json.dumps({
        "schema_version": "intent.v1",
        "slice_id": "reading-sanctuary",
        "core_tension": "Quiet reading vs Notification gravity",
        "declared_surfaces": ["surfaces/reading-sanctuary"],
        "physical_anchor": "none",
    }), encoding="utf-8")

    ir = compile_canonical_ir(root=root, slice_id="reading-sanctuary", stage="hero_probe")

    assert ir["sources"]["core_tension"] == "Quiet reading vs Notification gravity"
    # Surface ids normalize to their leaf name, matching the prose path.
    assert ir["scope"]["topology_scope"]["declared_surfaces"] == ["reading-sanctuary"]


def test_intent_json_anchor_satisfies_the_stage2_gate(tmp_path: Path):
    """A declared anchor in intent.json admits Stage 2 exactly like the prose form."""
    root = _write_discussion(tmp_path, "# Design Discussion\n\nNo structured sections here.\n")
    (root / "prototype/intent.json").write_text(json.dumps({
        "schema_version": "intent.v1",
        "slice_id": "reading-sanctuary",
        "core_tension": "Quiet reading vs Notification gravity",
        "declared_surfaces": ["surfaces/reading-sanctuary"],
        "physical_anchor": "none",
    }), encoding="utf-8")

    ir = compile_canonical_ir(
        root=root, slice_id="reading-sanctuary", stage="hero_probe", required_tier="stage2")

    assert ir["spec_tier"] == "intent_spec"


def test_malformed_intent_json_aborts_rather_than_falling_back(tmp_path: Path):
    """A broken machine contract must not silently degrade to regex recovery."""
    root = _write_discussion(tmp_path, STAGE1_DISCUSSION)
    (root / "prototype/intent.json").write_text("{ not json", encoding="utf-8")

    with pytest.raises(IncompleteStageContractError, match="intent.json"):
        compile_canonical_ir(root=root, slice_id="reading-sanctuary", stage="hero_probe")


def test_intent_note_never_claims_compilation_stopped(tmp_path: Path, capsys):
    """The intent-tier NOTE compiles anyway, so it must not read as an abort."""
    root = _write_discussion(tmp_path, STAGE1_DISCUSSION)

    compile_canonical_ir(root=root, slice_id="reading-sanctuary", stage="hero_probe")

    err = capsys.readouterr().err
    assert "未中止" in err
    assert "编译中止" not in err


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
    assert pkt["candidate_id"] == "r1"
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
            "prototype_html": f"prototype/experiments/{slice_id}/anchor/index.html"
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
            "prototype_html": f"prototype/experiments/{slice_id}/anchor/index.html"
        }
    }
    (compiled_dir / "r1.spec.json").write_text(json.dumps(valid_ir), encoding="utf-8")
    errors = lint_canonical_spec_ir(tmp_path, slice_id)
    assert not errors


def test_google_design_md_frontmatter_and_standard_sections_compile_cleanly(tmp_path: Path):
    """Verify that a spec adhering to the Google Design.md architecture compiles cleanly."""
    spec_text = """---
spec_schema: "google-design-md/v2"
slice_id: "incident-commander"
authority: "sealed_provisional"
stage: "hero_probe"
viewports: [390, 1280]
required_states: [state-draft, state-sealed]
tokens_ref: "prototype/shared/tokens.css"
primary_surface: "cockpit-main"
---

# Surface Specification: Incident Commander Cockpit

## 1. Problem Framing & Drivers (支柱 1-2: 价值与真实地锚)
- Physical Anchor: desktop workstation
- **Core Tension**: `Throughput vs Liability` (秒级止血处置吞吐 vs 误操作责任风险).
- **Design Driver**: `tension` | `failure_mode` (脑裂状态下操作员盲目重启集群).
- **Reality Anchors**:
  - `Adopt`: Datadog 密集状态指示灯、Linear 键盘第一响应速度.
  - `Refuse`: 消费级多步配置向导、高侵入式全屏模态遮罩.
- **Ruthless Omissions (三大舍弃)**:
  1. 舍弃事后复盘报告与长篇图表生成 (由离线工单系统承担).
  2. 舍弃多集群全局拓扑编辑能力 (当前视口仅做应急隔离).
  3. 舍弃复杂的多级组织权限审批流 (仅保留本地物理签名核验).

## 2. Experience Foundation & Five Axes (支柱 6-7: 视觉刻度与五轴)
- **Five Axes Register**:
  - Density: dense
  - Energy: kinetic
  - Materiality: coated_instrument_dark
  - Rhythm: fluid
  - Character: technical
- **Seed Palette / Color Register**:
  - --bg-void: #0b0f10
  - --bg-surface: #121719
  - --accent-primary: #38bdf8
  - --accent-seal: #d93829

## 3. Spatial Anatomy & Surfaces (支柱 3 & 5: OOUX 与拓扑空间)
- **Surface Allocation**:
  - **主工作区 (Primary)**: `surface/cockpit-main`
  - **上下文视图 (Contextual)**: `surface/node-drawer`
  - **移动扫视图 (Glance)**: `surface/mobile-sentinel`
- **Meso Directives**:
  - `massing_pattern`: `canvas-inspector`
  - `kinematics`: `focus-restore-250ms`
  - `data_syntax`: `micro-trend-compact`

## 4. State Models & Action Lifecycle (支柱 4: 交互状态机)
- **Domain States**:
  - `domain/nominal` (集群常态): 全部节点健康，张量流水线满负荷吞吐。
  - `domain/degraded` (性能降级): 单机 NVLink 延迟超过 15%，触发预警。
  - `domain/breached` (止血阻断): 节点心跳超时，进入待隔离状态。
- **Interaction States**:
  - `interaction/idle`, `interaction/inspecting`, `interaction/armed`, `interaction/committing`
- **Data Scenarios**:
  - `data/cold-cache`: 首次加载、缓存未命中场景。
  - `data/burst-traffic`: 10x 流量峰值时的 UI 批处理渲染。
- **Action Verbs (Key Bindings & Triggers)**:
  - `Space` 键瞬时检视 (proximity: 1)
  - `Enter` 键机械压感提交 (proximity: 2)

## 5. Resilience, Reality Breakers & Invariants (支柱 8-9: 破坏协议与验收门禁)
- **Four-Dimensional Reality Breakers (Break Protocol)**:
  - `stress/long-service-name` | Vector: `120 字符超长微服务名称` ➔ Expected: `单行省略截断 + Tooltip 展示`
  - `stress/zero-alert` | Vector: `无告警空状态` ➔ Expected: `展示健康绿标与上次巡检时间戳`
  - `stress/network-lag` | Vector: `断网或 504 Gateway Timeout` ➔ Expected: `操作按钮进入禁用重试态`
- **Design Invariants**:
  - `inv/wcag-contrast` | 核心文本与背景对比度必须满足 WCAG AA 4.5:1 | severity: blocking | verif: computed_style
  - `inv/horizontal-fit` | 320px 视口无水平滚动条 | severity: blocking | verif: dom_query
  - `inv/destructive-guard` | 破坏性止血操作必须具备二次物理确认锁 | severity: blocking | verif: dom_query
"""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text(spec_text, encoding="utf-8")

    ir = compile_canonical_ir(
        root=tmp_path,
        slice_id="incident-commander",
    )

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=ir, schema=schema)

    assert ir["schema_version"] == "prototype-spec/v1"
    assert ir["identity"]["slice_id"] == "incident-commander"
    assert ir["identity"]["authority_status"] == "sealed_provisional"
    assert ir["identity"]["title"] == "Incident Commander Cockpit"
    assert ir["scope"]["verification_scope"]["viewports"] == [390, 1280]
    assert ir["scope"]["verification_scope"]["required_states"] == ["state-draft", "state-sealed"]
    assert ir["scope"]["topology_scope"]["primary_surface"] == "cockpit-main"
    assert ir["scope"]["topology_scope"]["declared_surfaces"] == ["cockpit-main", "node-drawer", "mobile-sentinel"]
    assert ir["scope"]["build_scope"]["context_surfaces"] == ["node-drawer", "mobile-sentinel"]
    assert "Throughput vs Liability" in ir["sources"]["core_tension"]
    assert len(ir["invariants"]) == 3
    assert any(i["id"] == "inv/wcag-contrast" and i["severity"] == "blocking" for i in ir["invariants"])
    assert len(ir["state_model"]["domain_states"]) == 3
    assert len(ir["state_model"]["stress_fixtures"]) == 3
    assert ir["layout_directives"]["massing_pattern"] == "canvas-inspector"


def test_execution_boundary_admits_workspace_and_relative_helper_scripts(tmp_path: Path):
    """Verify execution_boundary admits helpers invoked via workspace-relative or installed paths."""
    import execution_boundary

    fake_workspace = tmp_path / "custom-bench"
    skill_scripts = fake_workspace / ".claude/skills/spec-prototype/scripts"
    skill_scripts.mkdir(parents=True)
    helper = skill_scripts / "compile_spec_ir.py"
    helper.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

    # Workspace-local relative invocation
    execution_boundary.shell_read(f"python3 {helper} --slice test", fake_workspace)
    # Standard repository invocation
    execution_boundary.shell_read("python3 skills/spec-prototype/scripts/compile_tokens.py --discussion d.md", fake_workspace)
    # Node helpers
    execution_boundary.shell_read("node skills/spec-prototype/scripts/preview.mjs", fake_workspace)

    # Rogue script must still be rejected
    rogue = skill_scripts / "rogue_tool.py"
    rogue.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Only installed helpers run"):
        execution_boundary.shell_read(f"python3 {rogue}", fake_workspace)


def test_canonical_envelope_anchors_and_states_carry_derived_authority(tmp_path: Path):
    """Verify canonical IR envelope anchors and states carry derived authority to eliminate authority promotion."""
    import assemble_envelope

    disc_path = tmp_path / "prototype/discussion.md"
    disc_path.parent.mkdir(parents=True)
    disc_path.write_text(COMPLETE_DISCUSSION, encoding="utf-8")

    ir = compile_canonical_ir(root=tmp_path, slice_id="workbench")
    ir_path = tmp_path / "prototype/contracts/compiled/workbench/r1.spec.json"
    ir_path.parent.mkdir(parents=True)
    ir_path.write_text(json.dumps(ir), encoding="utf-8")

    spec_md = render_single_spec_md(ir)
    spec_path = tmp_path / "prototype/specifications/workbench/r1.spec.md"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(spec_md, encoding="utf-8")

    # Tokens file
    tokens_path = tmp_path / "prototype/shared/tokens.css"
    tokens_path.parent.mkdir(parents=True)
    tokens_path.write_text(":root { --accent-primary: #000; }", encoding="utf-8")

    env = assemble_envelope.assemble(tmp_path, "workbench")
    assert env["mode"] == "lean-builder-envelope"

    # Anchors must be derived, not explicit
    anchors = env["semantic_contract"]["anchors"]
    assert len(anchors) > 0
    for a in anchors:
        assert a["authority"] == "derived", f"Anchor {a} must carry derived authority"

    assert env["semantic_contract"]["primary_entities"] == []
    assert ir["state_model"]["domain_states"]
    # Domain states remain states and must be derived, not entities.
    domain_states = env["semantic_contract"]["domain_states"]
    assert len(domain_states) > 0
    for ds in domain_states:
        assert ds["authority"] == "derived", f"Domain state {ds} must carry derived authority"

    # Layout regions and directives must be derived, not explicit
    regions = env["layout_directives"]["regions"]
    for r in regions:
        assert r["authority"] == "derived", f"Region {r} must carry derived authority"
    assert env["layout_directives"]["authority"] == "derived"
    assert env["visual_directives"]["density_calibration"]["authority"] == "derived"


def test_surface_extraction_filters_out_viewport_and_testing_dimensions(tmp_path: Path):
    """Verify compile_spec_ir filters out Viewport/Screen/Breakpoint noise from declared surfaces."""
    disc_text = """
### Spatial Anatomy & Surface Topology
- `surfaces/cockpit-main` (主表面): 核心操作台
- `Viewport` (视口尺寸): 1280px / 390px
- `surfaces/incident-drawer` (抽屉表面): 详情检视
- `Breakpoint`: 320px fold
"""
    disc_path = tmp_path / "prototype/discussion.md"
    disc_path.parent.mkdir(parents=True)
    disc_path.write_text(disc_text, encoding="utf-8")

    ir = compile_canonical_ir(root=tmp_path, slice_id="cockpit-main", allow_incomplete=True)
    declared = ir["scope"]["topology_scope"]["declared_surfaces"]
    assert "cockpit-main" in declared
    assert "incident-drawer" in declared
    assert "Viewport" not in declared
    assert "Breakpoint" not in declared





# --- B1 regression locks: semantic lossless projection -----------------------


def test_navigation_topology_not_hardcoded(tmp_path: Path):
    """Regression: the compiler must not invent `workspace-inspector` for every product.

    Undeclared topology stays absent from the IR rather than being fabricated;
    an authored `navigation_topology:` declaration is taken verbatim.
    """
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text(
        "# Discussion\n- Product: Editorial Reader\n- Baseline: content flow\n",
        encoding="utf-8",
    )
    ir = compile_canonical_ir(root=tmp_path, slice_id="reader", allow_incomplete=True)
    assert "navigation_topology" not in ir["scope"]["topology_scope"]

    disc.write_text(
        "# Discussion\n- Product: Ops Console\n- navigation_topology: `pinned-master-detail`\n",
        encoding="utf-8",
    )
    ir2 = compile_canonical_ir(root=tmp_path, slice_id="ops", allow_incomplete=True)
    assert ir2["scope"]["topology_scope"]["navigation_topology"] == "pinned-master-detail"


def test_state_entries_preserve_label_and_description(tmp_path: Path):
    """Regression: state projection must not flatten id/label/description to name+type."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/spec-prototype/scripts"))
    import assemble_envelope

    ir = {
        "identity": {},
        "sources": {},
        "scope": {"topology_scope": {}, "verification_scope": {}},
        "foundation": {},
        "state_model": {
            "domain_states": [
                {"id": "node/draining", "label": "排空中",
                 "description": "节点正在逐批排空流量，未完成前不可收尾"},
            ],
            "interaction_states": [],
            "data_scenarios": [],
            "stress_fixtures": [],
        },
        "actions": [],
        "invariants": [],
    }
    fields = assemble_envelope._canonical_ir_fields(ir, "r1.spec.json")
    ds = fields["semantic_contract"]["domain_states"][0]
    assert ds["name"] == "node/draining"
    assert ds["label"] == "排空中"
    assert "排空" in ds["description"]


def test_action_contracts_preserve_commit_and_proximity(tmp_path: Path):
    """Regression: action projection must keep commit_action/proximity_level/origin."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/spec-prototype/scripts"))
    import assemble_envelope

    ir = {
        "identity": {}, "sources": {}, "foundation": {}, "invariants": [],
        "scope": {"topology_scope": {}, "verification_scope": {}},
        "state_model": {"domain_states": [], "interaction_states": [],
                        "data_scenarios": [], "stress_fixtures": []},
        "actions": [{
            "id": "action-resolve-incident", "verb": "收尾复盘", "trigger": "primary button",
            "proximity_level": 4, "commit_action": "双签确认 -> 排空完成 -> 关闭事故",
            "consequence": "事故关闭并进入复盘", "feedback": "事故已收尾",
            "authority": "explicit", "origin": "discussion.md#contract:actions",
        }],
    }
    fields = assemble_envelope._canonical_ir_fields(ir, "r1.spec.json")
    act = fields["action_contracts"][0]
    assert act["proximity_level"] == 4
    assert "排空完成" in act["commit_action"]
    assert act["origin"] == "discussion.md#contract:actions"
    assert act["consequence"] == "事故关闭并进入复盘"

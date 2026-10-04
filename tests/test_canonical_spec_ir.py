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
from spec_contract_blocks import read_design_record

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


def test_read_design_record_layered_layout_tracks_each_source_part(tmp_path: Path):
    proto = tmp_path / "prototype"
    (proto / "briefs").mkdir(parents=True)
    truth = proto / "truth.md"
    world = proto / "world.md"
    brief = proto / "briefs/reader.md"
    truth.write_text("# Product truth\nshared", encoding="utf-8")
    world.write_text("# World\ntokens", encoding="utf-8")
    brief.write_text("# Reader slice\nlocal", encoding="utf-8")

    record = read_design_record(tmp_path, "reader")

    assert record.path == truth
    assert record.missing == []
    assert record.shared == "# Product truth\nshared\n\n# World\ntokens"
    assert record.slice_block == "# Reader slice\nlocal"
    assert record.text == f"{record.shared}\n\n{record.slice_block}"
    assert set(record.parts) == {
        "prototype/truth.md", "prototype/world.md", "prototype/briefs/reader.md"}
    assert record.parts["prototype/truth.md"].startswith("sha256:")


def test_read_design_record_reports_missing_layered_brief_without_fabricating(tmp_path: Path):
    proto = tmp_path / "prototype"
    proto.mkdir()
    (proto / "truth.md").write_text("# Product", encoding="utf-8")
    (proto / "world.md").write_text("# World", encoding="utf-8")

    record = read_design_record(tmp_path, "reader")

    assert record.missing == ["prototype/briefs/reader.md"]
    assert record.slice_block is None
    assert record.text == "# Product\n\n# World"
    assert "prototype/briefs/reader.md" not in record.parts


def test_read_design_record_reports_missing_or_duplicate_single_record_slice(tmp_path: Path):
    proto = tmp_path / "prototype"
    proto.mkdir()
    discussion = proto / "discussion.md"
    discussion.write_text("# Shared\ncommon\n## Slice: writer\nother\n", encoding="utf-8")

    absent = read_design_record(tmp_path, "missing")
    assert absent.missing == ["prototype/discussion.md#Slice: missing"]
    assert absent.slice_block is None

    discussion.write_text("# Shared\ncommon\n## Slice: reader\nfirst\n## Slice: reader\nsecond\n",
                          encoding="utf-8")
    duplicate = read_design_record(tmp_path, "reader")
    assert duplicate.missing == ["prototype/discussion.md#Slice: reader"]
    assert duplicate.slice_block is None
    assert len(duplicate.parts) == 1


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
    # An unmarked entry is a designer's mechanism, not a user-confirmed fact.
    # The old default of `explicit` promoted every authored action into
    # user-confirmed authority and rode that claim into the Builder payload,
    # where `authority` separates user-stated domain states from derived ones.
    assert parsed[0]["authority"] == "derived"
    assert parsed[0]["feedback"] == "Saved"

    # The claim is authored, not assumed: marking it is honoured, and an
    # unknown level fails closed rather than defaulting to something.
    marked = actions.replace("  verb: submit", "  authority: explicit\n  verb: submit")
    assert parse_action_verbs(marked)[0]["authority"] == "explicit"
    with pytest.raises(ValueError, match="invalid authority"):
        parse_action_verbs(actions.replace("  verb: submit", "  authority: confirmed\n  verb: submit"))

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


def test_compiler_never_mints_frozen_approved(tmp_path: Path):
    """Only handoff.py freezes from a recorded approval; the compiler cannot claim it."""
    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True)
    disc.write_text(COMPLETE_DISCUSSION, encoding="utf-8")

    via_api = compile_canonical_ir(root=tmp_path, slice_id="s1", authority_status="frozen_approved")
    assert via_api["identity"]["authority_status"] == "sealed_provisional"

    disc.write_text("---\nauthority: frozen_approved\n---\n" + COMPLETE_DISCUSSION, encoding="utf-8")
    via_frontmatter = compile_canonical_ir(root=tmp_path, slice_id="s1")
    assert via_frontmatter["identity"]["authority_status"] == "sealed_provisional"

    cli = subprocess.run(
        [sys.executable, str(SCRIPTS / "compile_spec_ir.py"), "--root", str(tmp_path),
         "--slice", "s1", "--status", "frozen_approved"],
        capture_output=True, text=True)
    assert cli.returncode != 0 and "invalid choice" in cli.stderr


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


# One record partitioned by lifecycle: shared product truth and visual world,
# then one self-contained block per slice.
PARTITIONED_DISCUSSION = """# Design Discussion: Terminal Cluster Workbench

## 1. 业务与用户极端张力 (Core Tension)
- Operational through-put vs Catastrophic Bus-Hang Failures.

## 2. 现实双地锚 (Reality Benchmark Anchors)
- Physical Anchor: desktop workstation

## 4. 5-Dial 风格寄存器 (5-Dial Style Register)
- Density: dense

## Slice: cluster-overview

```yaml
---
slice_id: "cluster-overview"
---
```

### 3. 项目级状态模型 (State Model)
- `domain/cluster-nominal` (集群常态): 全部节点健康。
- `interaction/inspecting` (检视中): 抽屉展开。
- `data/cold-metrics` (冷指标): 首次加载。

### 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/cluster-overview`

### 6. Viewport 与强制测试状态
- `Viewport`: `390px` / `1280px`
- `Required States`: `state-draft`, `state-sealed`

### 7. 破坏协议 (Break Protocol)
- `stress/bus-hang` | Vector: `NVLink 挂起` | Expected: `定位故障节点`。

## Slice: archive-browser

### 3. 项目级状态模型 (State Model)
- `domain/archive-frozen` (归档冻结): 只读。
- `interaction/restoring` (恢复中): 恢复进行。
- `data/cold-archive` (冷归档): 远端存储。

### 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/archive-browser`

### 6. Viewport 与强制测试状态
- `Viewport`: `768px`
- `Required States`: `state-archived`

### 7. 破坏协议 (Break Protocol)
- `stress/cold-restore` | Vector: `远端冷恢复` | Expected: `进度与可取消`。
"""


def test_a_slice_block_does_not_leak_into_another_slice(tmp_path: Path):
    """Verification scope and states come from this slice's block only."""
    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION)

    ir = compile_canonical_ir(root=root, slice_id="cluster-overview", stage="hero_probe")

    assert ir["scope"]["verification_scope"]["viewports"] == [390, 1280]
    assert ir["scope"]["verification_scope"]["required_states"] == ["state-draft", "state-sealed"]
    assert [s["id"] for s in ir["state_model"]["domain_states"]] == ["domain/cluster-nominal"]
    assert [s["id"] for s in ir["state_model"]["stress_fixtures"]] == ["stress/bus-hang"]
    assert ir["scope"]["topology_scope"]["declared_surfaces"] == ["cluster-overview"]
    # Product truth is shared across slices.
    assert "Bus-Hang" in ir["sources"]["core_tension"]


def test_each_slice_compiles_from_its_own_block(tmp_path: Path):
    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION)

    ir = compile_canonical_ir(root=root, slice_id="archive-browser", stage="hero_probe")

    assert ir["scope"]["verification_scope"]["viewports"] == [768]
    assert ir["scope"]["verification_scope"]["required_states"] == ["state-archived"]
    assert [s["id"] for s in ir["state_model"]["domain_states"]] == ["domain/archive-frozen"]
    assert "Bus-Hang" in ir["sources"]["core_tension"]


def test_a_partitioned_record_without_the_slice_block_aborts(tmp_path: Path):
    """Falling back to the whole file would compile another slice's scope."""
    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION)

    with pytest.raises(IncompleteStageContractError, match="## Slice: billing"):
        compile_canonical_ir(root=root, slice_id="billing", stage="hero_probe")


def test_slice_scoped_contracts_above_the_heading_report_position_not_absence(tmp_path: Path):
    """r33: contracts written above `## Slice:` sit in the shared zone.

    The compiler still aborts (slice isolation is pinned above), but it must say
    the contracts are misplaced; "未提取到 / 请补齐" sent the author to rewrite
    what was already written.
    """
    text = """# Design Discussion: Avalanche

## 1. 业务与用户极端张力 (Core Tension)
- Operational through-put vs Catastrophic Bus-Hang Failures.

## 2. 现实双地锚 (Reality Benchmark Anchors)
- Physical Anchor: desktop workstation

### 3. 项目级状态模型 (State Model)
- `domain/nominal` (常态): 全部健康。
- `interaction/inspecting` (检视中): 抽屉展开。
- `data/cold-metrics` (冷指标): 首次加载。

### 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/avalanche-command`

### 6. Viewport 与强制测试状态
```contract:viewports
- 390
- 1280
```
```contract:required_states
- state-draft
```

### 7. 破坏协议 (Break Protocol)
- `stress/bus-hang` | Vector: `NVLink 挂起` | Expected: `定位故障节点`。

## Slice: avalanche-command

```yaml
---
slice_id: "avalanche-command"
---
```
- anchor only
"""
    root = _write_discussion(tmp_path, text)

    with pytest.raises(IncompleteStageContractError) as exc:
        compile_canonical_ir(root=root, slice_id="avalanche-command", stage="hero_probe")

    report = str(exc.value)
    assert "已声明但位置不对" in report
    assert "区块之外" in report
    assert "未提取到" not in report


def test_genuinely_absent_contracts_still_report_absence(tmp_path: Path):
    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION.replace(
        "- `Viewport`: `390px` / `1280px`\n", ""))

    with pytest.raises(IncompleteStageContractError) as exc:
        compile_canonical_ir(root=root, slice_id="cluster-overview", stage="hero_probe",
                             required_tier="execution_spec")

    assert "viewports" in str(exc.value)
    assert "未提取到" in str(exc.value)
    assert "位置不对" not in str(exc.value)


def test_a_slice_block_frontmatter_must_match_its_heading(tmp_path: Path):
    root = _write_discussion(
        tmp_path, PARTITIONED_DISCUSSION.replace('slice_id: "cluster-overview"', 'slice_id: "other"'))

    with pytest.raises(IncompleteStageContractError, match="slice_id"):
        compile_canonical_ir(root=root, slice_id="cluster-overview", stage="hero_probe")


def test_an_indented_contract_block_parses_like_a_flush_one():
    """A fence nested under a bullet carries a common indent.

    Stripping before dedenting removed it from the first line only, leaving the
    second at column 4 under a line-1 item at column 0, which PyYAML rejects as
    "mapping values are not allowed here".
    """
    indented = """- **Action Verb Lifecycle**:
  ```contract:actions
  - id: action-enter
    verb: submit
    trigger: Enter
    proximity_level: 4
    commit: Commit
    feedback: Saved
  ```"""
    parsed = parse_action_verbs(indented)
    assert [item["id"] for item in parsed] == ["action-enter"]
    assert parsed[0]["commit_action"] == "Commit"


def test_the_template_contract_block_is_machine_parseable():
    """The template is the authoring SSOT: its own actions block must parse."""
    template = (REPO / "skills/spec-prototype/templates/discussion.md").read_text(encoding="utf-8")
    assert [item["id"] for item in parse_action_verbs(template)] == [
        "action-space", "action-enter", "action-escape"]


def test_the_template_compiles_to_the_execution_tier(tmp_path: Path):
    """A record written to the template reaches Stage 5 without a late refusal.

    The template is what an author copies. If its own state model, invariants or
    stress fixtures are in a form the compiler does not admit, the gap surfaces
    only at the `execution_spec` boundary — after Stages 2-4 are already built.
    The template must therefore compile strict, with no missing-section note.
    """
    root = _write_discussion(
        tmp_path,
        (REPO / "skills/spec-prototype/templates/discussion.md")
        .read_text(encoding="utf-8").replace("<slice_id>", "cockpit"),
    )

    ir = compile_canonical_ir(root=root, slice_id="cockpit", stage="hero_probe")

    assert ir["spec_tier"] == "execution_spec"
    assert [s["id"] for s in ir["state_model"]["domain_states"]] == [
        "domain/nominal", "domain/avalanche-alert", "domain/quarantined"]
    assert ir["state_model"]["interaction_states"] == [
        "interaction/idle", "interaction/inspecting", "interaction/committing"]
    assert [d["id"] for d in ir["state_model"]["data_scenarios"]] == [
        "data/cold-cache", "data/burst-traffic"]
    assert [s["id"] for s in ir["state_model"]["stress_fixtures"]] == [
        "stress/unbreakable-string", "stress/zero-data", "stress/320px-fold"]
    assert [i["id"] for i in ir["invariants"]] == [
        "inv/wcag-contrast", "inv/token-inheritance",
        "inv/action-safety", "inv/discoverable-critical-path"]
    assert ir["scope"]["verification_scope"]["required_states"] == [
        "state-draft", "state-sealed"]
    # Every block the template ships must actually reach the IR. A block the
    # compiler never reads is a declaration dropped in silence, which is the
    # failure the blocks exist to remove — including for the template itself.
    assert ir["foundation"]["five_axes"] == {
        "density": "dense", "energy": "kinetic", "materiality": "coated_instrument_dark",
        "rhythm": "fluid", "character": "technical"}
    assert ir["foundation"]["palette_discipline"]["accent_seal"] == "var(--accent-seal, #ff3333)"
    assert ir["foundation"]["craft_stack"] == {
        "surface_optics": "coated_instrument_dark", "spatial_geometry": "concentric-nested",
        "micro_typography": "tabular-numeric", "data_marks": "micro-trend-compact"}
    assert ir["layout_directives"]["massing_pattern"] == "canvas-inspector"
    assert ir["interaction_spec"]["kinematics"] == "focus-restore-250ms"
    assert ir["visual_directives"]["data_syntax"] == "micro-trend-compact"

def test_the_template_declares_every_machine_list_as_a_contract_block():
    """The template's own form must be the authoritative one, not the prose one.

    Prose inference is the route with the silent-mis-parse history: every field
    it reads is guessed from a sentence. A template that teaches the prose form
    teaches the fragile form, so the shipped example must be blocks.
    """
    template = (REPO / "skills/spec-prototype/templates/discussion.md").read_text(encoding="utf-8")
    for kind in ("states", "stress", "invariants", "required_states", "viewports",
                 "actions", "axes", "craft", "tokens", "meso"):
        assert f"```contract:{kind}" in template, f"the template never declares contract:{kind}"
    # The contract kinds the loaders know and the ones the template teaches are
    # one list; a kind the template omits is a kind no author will write.
    from compile_spec_ir import _CONTRACT_KINDS
    for kind in _CONTRACT_KINDS:
        assert f"```contract:{kind}" in template, f"contract:{kind} has no shipped example"

def test_the_contract_block_outranks_the_frontmatter_carrier(tmp_path: Path):
    """One authoritative carrier, and it is the block.

    `viewports`/`required_states` were also readable from the slice frontmatter,
    and the frontmatter won — so `contract:viewports` was a block the compiler
    ignored, while the template taught writing it. Every other contract kind
    takes its block as authoritative; an ignored block is a declaration dropped
    in silence, which is what the blocks exist to remove.
    """
    record = (REPO / "skills/spec-prototype/templates/discussion.md").read_text(
        encoding="utf-8").replace("<slice_id>", "cockpit")
    record = (record
              .replace("viewports: [390, 1280]", "viewports: [777]")
              .replace("required_states: [state-draft, state-sealed]",
                       "required_states: [state-frontmatter]")
              .replace("```contract:viewports\n- 390\n- 1280\n```",
                       "```contract:viewports\n- 900\n- 1000\n```")
              .replace("```contract:required_states\n- state-draft\n- state-sealed\n```",
                       "```contract:required_states\n- state-block\n```"))
    # The exemplary prose keeps a `320px` figure, which is the stray token the
    # prose scan used to read out of a sentence and outrun the declared scope.
    assert "320px" in record

    ir = compile_canonical_ir(root=_write_discussion(tmp_path, record),
                              slice_id="cockpit", stage="hero_probe")

    assert ir["scope"]["verification_scope"]["viewports"] == [900, 1000]
    assert ir["scope"]["verification_scope"]["required_states"] == ["state-block"]

def test_the_verification_scope_falls_back_without_a_block(tmp_path: Path):
    """A record that predates the blocks still resolves: frontmatter, then prose."""
    from_frontmatter = (PARTITIONED_DISCUSSION
                        .replace('slice_id: "cluster-overview"',
                                 'slice_id: "cluster-overview"\nviewports: [1440]\nrequired_states: [state-fm]')
                        .replace("### 6. Viewport 与强制测试状态\n- `Viewport`: `390px` / `1280px`\n"
                                 "- `Required States`: `state-draft`, `state-sealed`", ""))
    ir = compile_canonical_ir(root=_write_discussion(tmp_path, from_frontmatter),
                              slice_id="cluster-overview", stage="hero_probe")
    assert ir["scope"]["verification_scope"]["viewports"] == [1440]
    assert ir["scope"]["verification_scope"]["required_states"] == ["state-fm"]

def test_a_stray_pixel_figure_does_not_outrun_a_declared_viewport(tmp_path: Path):
    """Prose is the last resort, because a sentence is not a breakpoint.

    The template's own exemplary prose names `320px`. When the prose scan ran
    before the frontmatter, that mention replaced the authored list.
    """
    from compile_spec_ir import _viewports_prose

    assert _viewports_prose("Do not use a 320px viewport here.") == [320]

    declared = (PARTITIONED_DISCUSSION
                .replace('slice_id: "cluster-overview"',
                         'slice_id: "cluster-overview"\nviewports: [390, 1280]')
                .replace("### 6. Viewport 与强制测试状态\n- `Viewport`: `390px` / `1280px`\n"
                         "- `Required States`: `state-draft`, `state-sealed`",
                         "- The 320px fold is a stress vector, not a breakpoint."))
    ir = compile_canonical_ir(root=_write_discussion(tmp_path, declared),
                              slice_id="cluster-overview", stage="hero_probe")
    assert ir["scope"]["verification_scope"]["viewports"] == [390, 1280]

def test_a_contract_states_block_is_the_machine_ssot(tmp_path: Path):
    """When a block exists it wins, and prose never becomes a second declaration."""
    from compile_spec_ir import (parse_data_scenarios, parse_domain_states,
                                 parse_interaction_states)

    doc = """## 3. State Model
- `domain/from-prose` (散文态): 只应被块覆盖。

```contract:states
- id: domain/from-block
  label: 块态
  description: 机器权威。
- id: interaction/idle
  description: 待命。
- id: data/cold-cache
  description: 冷缓存。
```
"""
    assert [s["id"] for s in parse_domain_states(doc)] == ["domain/from-block"]
    assert [s["label"] for s in parse_domain_states(doc)] == ["块态"]
    assert parse_interaction_states(doc) == ["interaction/idle"]
    assert [d["id"] for d in parse_data_scenarios(doc)] == ["data/cold-cache"]

def test_contract_blocks_fail_closed_on_an_authoring_error():
    """A declared block is deliberate, so an unknown value is an error, not a skip.

    The prose path falls back to a weaker enum value on a typo; the block path
    cannot, because the author stated it explicitly and a silent downgrade would
    ship a gate they never chose.
    """
    from compile_spec_ir import (_invariants_from_contract_block, _states_from_contract_block,
                                 _stress_from_contract_block)

    with pytest.raises(ValueError, match="unknown prefix"):
        _states_from_contract_block("```contract:states\n- id: widget/x\n  description: X\n```")
    with pytest.raises(ValueError, match="description"):
        _states_from_contract_block("```contract:states\n- id: domain/a\n```")
    with pytest.raises(ValueError, match="duplicate id"):
        _states_from_contract_block(
            "```contract:states\n- id: domain/a\n  description: A\n"
            "- id: domain/a\n  description: A\n```")
    with pytest.raises(ValueError, match="missing required"):
        _stress_from_contract_block("```contract:stress\n- id: stress/x\n  vector: v\n```")
    with pytest.raises(ValueError, match="invalid severity"):
        _invariants_from_contract_block(
            "```contract:invariants\n- id: inv/a\n  statement: s\n  severity: critical\n```")
    with pytest.raises(ValueError, match="invalid verification"):
        _invariants_from_contract_block(
            "```contract:invariants\n- id: inv/a\n  statement: s\n  verification: eyeball\n```")
    # No block at all is not an error: it selects the prose fallback.
    assert _states_from_contract_block("- `domain/a`: A\n") is None

def test_a_declaration_the_compiler_drops_is_reported_not_silently_lost(tmp_path: Path):
    """A machine-shaped bullet that parsed nothing out is a compile failure.

    This is the defect class that surfaced as a late `execution_spec` refusal:
    the author wrote a declaration, the parser admitted nothing, and the run
    continued with the field empty. The line that caused it must be named.
    """
    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION.replace(
        "- `stress/bus-hang` | Vector: `NVLink 挂起` | Expected: `定位故障节点`。",
        "- `stress/bus-hang` | Vector: `NVLink 挂起`。"))

    with pytest.raises(IncompleteStageContractError) as excinfo:
        compile_canonical_ir(root=root, slice_id="cluster-overview", stage="hero_probe")

    assert "unadmitted_machine_bullet" in str(excinfo.value)
    assert "stress/bus-hang" in str(excinfo.value)

def test_a_misspelled_contract_kind_is_reported_not_silently_ignored(tmp_path: Path):
    """A fence naming an unregistered kind reads as no block at all.

    The misspelling silently hands the field to the prose fallback, which is the
    same silent drop one level up: the author declared a contract and the
    compiler read nothing. The registry is what makes the fence meaningful, so a
    fence outside it is named.
    """
    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION.replace(
        "### 6. Viewport 与强制测试状态\n- `Viewport`: `390px` / `1280px`",
        "```contract:viewport\n- 390\n- 1280\n```"))

    with pytest.raises(IncompleteStageContractError) as excinfo:
        compile_canonical_ir(root=root, slice_id="cluster-overview", stage="hero_probe")

    assert "unknown_contract_kind" in str(excinfo.value)
    assert "contract:viewport" in str(excinfo.value)

def test_a_contract_states_block_missing_a_class_is_reported(tmp_path: Path):
    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION.replace(
        "### 3. 项目级状态模型 (State Model)\n"
        "- `domain/cluster-nominal` (集群常态): 全部节点健康。\n"
        "- `interaction/inspecting` (检视中): 抽屉展开。\n"
        "- `data/cold-metrics` (冷指标): 首次加载。",
        "### 3. 项目级状态模型 (State Model)\n"
        "```contract:states\n"
        "- id: domain/cluster-nominal\n  label: 集群常态\n  description: 全部节点健康。\n"
        "- id: interaction/inspecting\n  description: 抽屉展开。\n"
        "```"))

    with pytest.raises(IncompleteStageContractError) as excinfo:
        compile_canonical_ir(root=root, slice_id="cluster-overview", stage="hero_probe")

    assert "incomplete_state_block" in str(excinfo.value)
    assert "data_scenarios" in str(excinfo.value)


def test_a_state_named_in_prose_is_not_a_declaration():
    """Only a bullet declares a state; a token mentioned in a sentence does not.

    The partitioning preamble names `interaction/`-shaped tokens while explaining
    the record shape. An unanchored scan reads that sentence as a declaration and
    lets commentary invent states, which is how a stray token becomes a state the
    design never had.
    """
    from compile_spec_ir import parse_data_scenarios, parse_interaction_states

    prose = (
        "The record declares `interaction/inspecting` and `data/cold-cache` inside "
        "its state section, and `stress/bus-hang` inside the break protocol.\n"
        "- `interaction/committing` (提交中): 已触发。\n"
        "- `data/burst-traffic` (流量峰值): 批处理渲染。\n"
    )

    assert parse_interaction_states(prose) == ["interaction/committing"]
    assert [d["id"] for d in parse_data_scenarios(prose)] == ["data/burst-traffic"]


def test_a_required_states_label_needs_its_payload():
    """A sentence that names the label without one declares no states.

    The partitioning preamble says "required states — from that block". An
    unanchored label search admits the rest of that sentence, and the ordinary
    English words in it become test states.
    """
    from compile_spec_ir import parse_required_states

    prose = ("the compiler reads product-level facts from the shared zones and "
             "slice-level facts — surfaces, states, actions, invariants, "
             "required states — from that block, and the verification scope\n"
             "- `Required States`: `state-draft`, `state-sealed`\n")

    assert parse_required_states(prose) == ["state-draft", "state-sealed"]



def test_draw_seed_records_into_the_slice_block(tmp_path: Path):
    """The draw lands in this slice's block, and re-running replaces it."""
    from draw_seed import draw, load_challengers, render_block, write_block, VOCABULARY

    root = _write_discussion(tmp_path, PARTITIONED_DISCUSSION)
    record = root / "prototype/discussion.md"

    picks = draw(3, load_challengers(VOCABULARY))
    write_block(record, "cluster-overview", render_block(picks))
    write_block(record, "cluster-overview", render_block(draw(3, load_challengers(VOCABULARY))))

    text = record.read_text(encoding="utf-8")
    assert text.count("### Divergence seeds") == 1
    start = text.index("## Slice: cluster-overview")
    end = text.index("## Slice: archive-browser")
    assert "### Divergence seeds" in text[start:end]
    # The other slice's block is untouched, and its scope still compiles alone.
    assert "### Divergence seeds" not in text[end:]
    ir = compile_canonical_ir(root=root, slice_id="archive-browser", stage="hero_probe")
    assert ir["scope"]["verification_scope"]["viewports"] == [768]


def test_draw_seed_requires_the_slice_block(tmp_path: Path):
    """A seed belongs to a slice; there is nowhere to record it without one."""
    from draw_seed import DrawError, write_block

    root = _write_discussion(tmp_path, "# Design discussion\n\n## Product truth\n\nno slices here\n")
    with pytest.raises(DrawError, match="## Slice: cockpit"):
        write_block(root / "prototype/discussion.md", "cockpit", "### Divergence seeds\n")

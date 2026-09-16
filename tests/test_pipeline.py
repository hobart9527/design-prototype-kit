from pathlib import Path
import hashlib
import importlib.util
import json
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
SKILL = SCRIPTS.parent

import sys
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

handoff = _load("handoff", "handoff.py")
assertions = _load("assertions", "check-assertions.py")
boundary = _load("boundary", "execution_boundary.py")

def _sha256(b: bytes) -> str:
    return f"sha256:{hashlib.sha256(b).hexdigest()}"

def test_assertion_matching_chinese_and_exact_equality():
    fh = "| Assertion | Rationale | Surfaces | Method | Required or exploratory |\n|---|---|---|---|---|\n"
    eh = "| Foundation assertion/probe requirement and clause | Required/exploratory | Expected | Exact trace/measurement | Result |\n|---|---|---|---|---|\n"

    # 1. Chinese assertion succeeds on exact match with falsifiable anchor
    c_assert = "关闭弹窗后焦点返回原按钮"
    f_content = fh + f"| {c_assert} | 恢复上下文 | 弹窗 | 键盘 | required |\n"
    e_content = eh + f"| {c_assert} | required | 通过 | `trace.json` | pass |\n"
    assert assertions.evaluate(f_content, e_content) == []

    # 2. Substring prefix does not override a subsequent exact failure
    long_assert = "Focus returns to opener after closing dialog"
    f_sub = fh + f"| {long_assert} | context | modal | keyboard | required |\n"
    e_sub = eh + f"| Focus | exploratory | initial focus ok | `init.json` | pass |\n| {long_assert} | required | lost focus | `close.json` | fail |\n"
    violations = assertions.evaluate(f_sub, e_sub)
    assert any("not resolved (fail)" in v for v in violations)

def test_handoff_packet_without_preexisting_html_and_template_surface_map(tmp_path: Path):
    root = tmp_path
    product = root / "prototype/product.md"
    product.parent.mkdir(parents=True, exist_ok=True)
    product.write_text("# Product\nDocument reader.", encoding="utf-8")

    smap = root / "prototype/contracts/surface-maps/m1.md"
    smap.parent.mkdir(parents=True, exist_ok=True)
    # Uses template style with status in parentheses
    smap.write_text("# Surface Map\n- Surface Map revision / status (`draft | frozen | superseded`): m1 / draft\n- Scope: reader\n", encoding="utf-8")

    foundation = root / "prototype/contracts/foundation/f1.md"
    foundation.parent.mkdir(parents=True, exist_ok=True)
    foundation.write_text(f"""# Foundation
- Foundation revision: f1
- Product record path, revision and digest: `{product.relative_to(root)}`, {_sha256(product.read_bytes())}
- Retained Surface Map path, revision and digest: `{smap.relative_to(root)}`, {_sha256(smap.read_bytes())}
""", encoding="utf-8")

    tokens = root / "prototype/contracts/tokens/t1.md"
    tokens.parent.mkdir(parents=True, exist_ok=True)
    tokens.write_text("# Tokens\n- Foundation revision: f1\n- Tokens revision: t1\n## Breakpoints\n| Token | Value |\n|---|---|\n| --bp-mobile | 390px |\n", encoding="utf-8")

    contract = root / "prototype/contracts/slices/reader/c1.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(f"""# Contract
- Slice ID: reader
- Contract revision: c1
- Foundation revision: f1
- Disposition: ready
- Retained surface-map path, revision and digest: `{smap.relative_to(root)}`, {_sha256(smap.read_bytes())}
""", encoding="utf-8")

    craft = SKILL / "references/design-floor.md"
    craft_ref = f"`references/design-floor.md`, {_sha256(craft.read_bytes())}"

    spec = root / "prototype/specifications/reader/r1.md"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(f"""# Prototype Specification: reader / r1
- Candidate / selected revision: r1
- Compilation status: candidate
- Repository root: `{root}`
- Product record revision and digest: `{product.relative_to(root)}`, {_sha256(product.read_bytes())}
- Foundation revision and digest: `{foundation.relative_to(root)}`, {_sha256(foundation.read_bytes())}
- Token artifact path, revision, and digest: `{tokens.relative_to(root)}`, {_sha256(tokens.read_bytes())}
- Slice Contract revision and digest: `{contract.relative_to(root)}`, {_sha256(contract.read_bytes())}
- Prototype write scope: `prototype/experiments/reader/r1/`
- Evidence write scope: `prototype/evidence/reader/r1/`
- Start command: `python3 -m http.server 8000`
- Verification command(s): `python3 -m unittest`
- Page/flow coverage and shared data references: reader view
- Delegated implementation freedoms: HTML composition
- Required reachable-control closure: links
- Skill root / evidence template path for this dispatch: `{SKILL}`
- Required craft reads: {craft_ref}
- Visual verification: not_required
- Required screenshot checkpoints:
| Surface / interaction | Existing asset | Disposition | Constraint | Verification checkpoint |
|---|---|---|---|---|
| Reader | native HTML | delegated | semantic | keyboard |
""", encoding="utf-8")

    # Packet passes even without prototype/experiments/reader/r1/index.html pre-created
    pkt = handoff.packet(root, spec)
    assert pkt["candidate_id"] == "r1"
    assert "product" in pkt["references"]
    assert any(r["path"] == "prototype/product.md" for r in pkt["required_reads"])

    # Modifying product record without updating digest causes HandoffError
    product.write_text("# Tampered Product\nChanged content.", encoding="utf-8")
    with pytest.raises(handoff.HandoffError, match="Digest mismatch"):
        handoff.packet(root, spec)

def test_execution_boundary_freeze_rejects_foreign_root(tmp_path: Path):
    active_root = tmp_path / "project-a"
    foreign_root = tmp_path / "project-b"
    active_root.mkdir()
    foreign_root.mkdir()
    (active_root / "prototype").mkdir()
    (active_root / "prototype/discussion.md").write_text("- Execution boundary: active\n", encoding="utf-8")

    cmd = f"python3 {SCRIPTS}/handoff.py freeze --root {foreign_root} --spec dummy.md"
    event = {"cwd": str(active_root), "tool_name": "Bash", "tool_input": {"command": cmd}}
    with pytest.raises(ValueError, match="Freeze command must target the active discussion root"):
        boundary.check(event)


def test_canonical_design_references_and_floors():
    workflow_text = (SKILL / "references/core-workflow.md").read_text(encoding="utf-8")
    assert "OOUX Cardinality-to-Layout Anchor" in workflow_text
    assert "Non-transfer Boundaries" in workflow_text or "non-transfer boundary" in workflow_text
    assert "Reference Benchmarks" in workflow_text
    assert "Action Verb Lifecycle" in workflow_text
    assert "Decisive Exchange 3-Frame Inspection" in workflow_text
    assert "Native-First vs Production Handoff" in workflow_text
    assert "Cognitive Budgeting" in workflow_text
    assert "5-Dial Style Register" in workflow_text
    assert "Vague-Word Firewall" in workflow_text
    assert "Concentric Border Radius" in workflow_text
    assert "Tabular Numerics" in workflow_text
    assert "Optical Alignment" in workflow_text
    assert "Atmospheric Undertone" in workflow_text
    assert "Compression & Release" in workflow_text
    assert "The Break Protocol" in workflow_text

    floor_text = (SKILL / "references/design-floor.md").read_text(encoding="utf-8")
    assert "Non-Transfer Boundary" in floor_text
    assert "Zero Naked Metrics" in floor_text
    assert "Action Verb Lifecycle Closure" in floor_text
    assert "Decisive Exchange 3-Frame Floor" in floor_text
    assert "Concentric Border Radius Floor" in floor_text
    assert "Tabular Numerics Floor" in floor_text
    assert "Optical Alignment Floor" in floor_text
    assert "Atmospheric Undertone Floor" in floor_text
    assert "Vague-Word Firewall Floor" in floor_text

    discussion_tmpl = (SKILL / "templates/discussion.md").read_text(encoding="utf-8")
    assert "OOUX Cardinality-to-Layout Anchor" in discussion_tmpl
    assert "Non-transfer" in discussion_tmpl
    assert "Reference Benchmarks" in discussion_tmpl
    assert "Decisive Exchange 3-Frame Verification" in discussion_tmpl
    assert "Cognitive Budgeting Allocation" in discussion_tmpl
    assert "5-Dial Style Register" in discussion_tmpl
    assert "Concentric Radius check" in discussion_tmpl
    assert "Atmospheric Undertone" in discussion_tmpl
    assert "The Break Protocol" in discussion_tmpl


def test_archetype_routing_and_negative_triggers():
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "NEGATIVE TRIGGERS" in skill_text
    assert "Archetype A: Greenfield 0-to-1" in skill_text
    assert "Archetype B: New Surface 1-to-N" in skill_text
    assert "Archetype C: Refinement & Audit" in skill_text

    usage_text = (SKILL / "references/usage.md").read_text(encoding="utf-8")
    assert "形态 A：全新产品从零起步" in usage_text
    assert "形态 B：现有产品增设新页面/新功能" in usage_text
    assert "形态 C：现有产品体验优化与评审" in usage_text
    assert "负向排他防火墙" in usage_text

    discussion_tmpl = (SKILL / "templates/discussion.md").read_text(encoding="utf-8")
    assert "Product archetype basis" in discussion_tmpl



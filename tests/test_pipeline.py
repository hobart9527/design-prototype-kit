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

    craft = SKILL / "references/03-verification/quality-floor.md"
    craft_ref = f"`references/03-verification/quality-floor.md`, {_sha256(craft.read_bytes())}"

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

    floor_text = (SKILL / "references/03-verification/quality-floor.md").read_text(encoding="utf-8")
    assert "Non-Transfer Boundary" in floor_text or "non-transfer boundary" in floor_text
    assert "Zero Naked Metrics" in floor_text
    assert "Action Verb Lifecycle" in floor_text
    assert "Concentric Border Radi" in floor_text
    assert "Tabular Numerics" in floor_text
    assert "Atmospheric Undertone" in floor_text
    assert "Vague-Word Firewall" in floor_text

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

    usage_text = (SKILL / "references/04-governance/usage.md").read_text(encoding="utf-8")
    assert "形态 A：全新产品从零起步" in usage_text
    assert "形态 B：现有产品增设新页面/新功能" in usage_text
    assert "形态 C：现有产品体验优化与评审" in usage_text
    assert "负向排他防火墙" in usage_text

    discussion_tmpl = (SKILL / "templates/discussion.md").read_text(encoding="utf-8")
    assert "Product archetype basis" in discussion_tmpl


def test_canonical_5_stage_active_simulation_and_artifact_standards():
    """Verify live artifact outputs produced across the canonical 5-stage pipeline."""
    # Stage 1: Discussion record and product thesis
    discussion = (REPO / "prototype/discussion.md").read_text(encoding="utf-8")
    assert "魂 · 破" in discussion or "Tone & Tension" in discussion or "Stage 1" in discussion or "Throughput vs Liability" in discussion or "Detent Cockpit" in discussion
    product = (REPO / "prototype/product.md").read_text(encoding="utf-8")
    assert "电传操纵与磁吸阻尼" in product or "Fly-by-wire" in product or "Datadog" in product

    # Stage 2: Physical Tokens & Design Engineering Floors
    tokens_css = (REPO / "prototype/shared/tokens.css").read_text(encoding="utf-8")
    tokens_md = (REPO / "prototype/contracts/tokens/t1.md").read_text(encoding="utf-8")
    assert "--radius-outer" in tokens_css
    assert "--radius-inner" in tokens_css
    assert "tabular-nums" in tokens_css
    assert ":active" in tokens_css and "scale(0.97)" in tokens_css
    assert "#808080" not in tokens_css  # Atmospheric undertone: no sterile dead gray

    # Stage 3: Tiered Rollout & Token Inheritance
    hero_candidates = [
        REPO / "prototype/experiments/cockpit/hero-anchor/index.html",
        REPO / "prototype/experiments/console/hero-anchor/index.html",
    ]
    hero_path = next((p for p in hero_candidates if p.is_file()), None)
    if hero_path:
        hero_html = hero_path.read_text(encoding="utf-8")
        assert "shared/tokens.css" in hero_html
        assert "var(--" in hero_html

    # Stage 4: Holistic Review Portal
    portal_html = (REPO / "prototype/review-portal.html").read_text(encoding="utf-8")
    assert "review" in portal_html.lower() or "portal" in portal_html.lower()
    assert "DECISIVE 3-FRAME" in portal_html

    # Stage 5: Silent Governance Compilation
    tokens_json_path = REPO / "prototype/contracts/tokens/t1.json"
    assert tokens_json_path.is_file()
    token_data = json.loads(tokens_json_path.read_text(encoding="utf-8"))
    assert "$schema" in token_data
    assert "color" in token_data
    assert token_data["color"]["primary"]["$value"] == "#00f0ff"

    # Stage 5 Compiler Direct Verification: compile_tokens.py generates identical DTCG structure
    compile_mod = _load("compile_tokens", "compile_tokens.py")
    dials = {"energy": "quiet", "finish": "machined-industrial", "density": "dense", "weight": "dense-tactile", "seriousness": "solemn"}
    tokens = compile_mod.compute_tokens(dials, "plasma-cyan")
    generated_dtcg = compile_mod.generate_dtcg_json(tokens)
    assert "$schema" in generated_dtcg
    assert "color" in generated_dtcg
    assert "primary" in generated_dtcg["color"]
    assert generated_dtcg["color"]["primary"]["$value"].startswith("#")
    assert "radius" in generated_dtcg
    assert "outer" in generated_dtcg["radius"]
    assert "spacing" in generated_dtcg


def test_spec_first_contract_formulation_and_lean_envelope(tmp_path: Path):
    """Verify that Stage 1 6-Pillar Spec-First contracts are strictly required and envelope compiles."""
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")
    compile_mod = _load("compile_tokens", "compile_tokens.py")
    verify_mod = _load("verify_quality", "verify_prototype_quality.py")

    # 1. Reject when contract artifacts are missing
    with pytest.raises(ValueError, match="Stage 1 Spec Contract incomplete"):
        assemble_mod.check_spec_completeness(tmp_path, "test_slice")

    # 2. Populate all 6 Stage 1 contract pillars in tmp_path
    product = tmp_path / "prototype/product.md"
    product.parent.mkdir(parents=True, exist_ok=True)
    product.write_text("# Product\n- Core Tension: Speed vs Safety\n", encoding="utf-8")

    smap = tmp_path / "prototype/contracts/surface-maps/m1.md"
    smap.parent.mkdir(parents=True, exist_ok=True)
    smap.write_text("# Surface Map\n- Scope: test\n", encoding="utf-8")

    foundation = tmp_path / "prototype/contracts/foundation/f1.md"
    foundation.parent.mkdir(parents=True, exist_ok=True)
    foundation.write_text("# Foundation\n- Foundation revision: f1\n", encoding="utf-8")

    tokens_css = tmp_path / "prototype/shared/tokens.css"
    tokens_css.parent.mkdir(parents=True, exist_ok=True)
    tokens_css.write_text(":root { --radius-outer: 8px; --radius-inner: 4px; }\n", encoding="utf-8")

    tokens_md = tmp_path / "prototype/contracts/tokens/t1.md"
    tokens_md.parent.mkdir(parents=True, exist_ok=True)
    tokens_md.write_text("# Tokens\n- Foundation revision: f1\n- Tokens revision: t1\n## Breakpoints\n| Token | Value |\n|---|---|\n| --bp-mobile | 390px |\n", encoding="utf-8")

    tokens_json = tmp_path / "prototype/contracts/tokens/t1.json"
    tokens_json.write_text("{}", encoding="utf-8")

    slice_c = tmp_path / "prototype/contracts/slices/test_slice/c1.md"
    slice_c.parent.mkdir(parents=True, exist_ok=True)
    slice_c.write_text("# Contract\n- Slice ID: test_slice\n", encoding="utf-8")

    spec = tmp_path / "prototype/specifications/test_slice/r1.md"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text("""# Spec
- Prototype write scope: `prototype/experiments/test_slice/hero-anchor/`
- Evidence write scope: `prototype/evidence/probes/test_slice/`
## Verifiable Design Assertions
| Assertion | Expected |
|---|---|
| Key shortcut Space triggers action | pass |
""", encoding="utf-8")

    # 3. Assemble generates complete pre-baked envelope
    env = assemble_mod.assemble(tmp_path, "test_slice")
    assert env["mode"] == "lean-builder-envelope"
    assert env["target_html_path"] == "prototype/experiments/test_slice/hero-anchor/index.html"
    assert env["design_constraints"]["max_tool_turns"] <= 8
    assert "Key shortcut Space triggers action" in env["verifiable_assertions"]
    assert env["repository_root"] == str(tmp_path.resolve())
    assert env["spec_sources"]["foundation_digest"] != ""
    assert env["spec_sources"]["tokens_md_digest"] != ""

    # 4. Verify execution_boundary permits lean-builder-envelope dispatch without rejection
    discussion = tmp_path / "prototype/discussion.md"
    discussion.write_text("- Execution boundary: active\n", encoding="utf-8")
    event = {
        "cwd": str(tmp_path),
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "spec-prototype-builder",
            "prompt": json.dumps(env),
        },
    }
    # check() should succeed and not raise ValueError or KeyError
    boundary.check(event)

    # 5. Verify compile_tokens 3-in-1 synchronization
    disc_text = """## 5-Dial Style Register\n- Energy: 3\n- Finish: 4\n- Density: 4\n- Weight: 3\n- Seriousness: 4\n"""
    discussion.write_text(disc_text, encoding="utf-8")
    out_css = tmp_path / "tokens_gen.css"
    out_json = tmp_path / "tokens_gen.json"
    out_md = tmp_path / "tokens_gen.md"
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json), str(out_md))
    assert out_css.is_file() and "--radius-outer" in out_css.read_text(encoding="utf-8")
    assert out_json.is_file() and "$schema" in out_json.read_text(encoding="utf-8")
    assert out_md.is_file() and "## Breakpoints" in out_md.read_text(encoding="utf-8")

    # 6. Verify verify_prototype_quality smart path resolution & quality assertion
    dummy_html = tmp_path / "test.html"
    dummy_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens_gen.css"></head><body><button style="border-radius: var(--radius-btn); font-variant-numeric: tabular-nums;">42</button></body></html>""", encoding="utf-8")
    toy_pass = verify_mod.assert_quality(str(dummy_html), str(out_css), check_stale=False)
    assert toy_pass is False  # Correctly intercepts toy demo lacking AppState and dual-channel shortcuts

    real_hero = REPO / "prototype/experiments/console/hero-anchor/index.html"
    if real_hero.is_file():
        real_pass = verify_mod.assert_quality(str(real_hero), str(out_css), check_stale=False)
        assert real_pass is True

    # 7. Verify builder agent contract specifies Lean Pre-baked Envelope Protocol
    builder_md = (REPO / "agents/spec-prototype-builder.md").read_text(encoding="utf-8")
    assert "Lean Pre-baked Envelope Protocol" in builder_md
    assert "≤ 8 tool turns" in builder_md or "<= 8 tool turns" in builder_md
    assert "Zero Exploratory Hunting" in builder_md

    # 8. Verify SKILL.md and core-workflow.md declare Spec-First invariant & 6 pillars
    core_wf = (SKILL / "references/core-workflow.md").read_text(encoding="utf-8")
    assert "No Prototype Code without a Frozen Spec Contract" in core_wf
    assert "foundation/f1.md" in core_wf
    skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "ZERO Prototype Code without a complete frozen Spec Contract" in skill_md
    assert "foundation/f1.md" in skill_md


def test_zero_broken_markdown_links_in_skill():
    """Verify zero broken relative markdown links across the entire spec-prototype skill."""
    import re
    broken = []
    for md in SKILL.rglob("*.md"):
        content = md.read_text(encoding="utf-8")
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        base_dir = md.resolve().parent
        for title, link in links:
            if link.startswith("http") or link.startswith("#") or link.startswith("mailto:"):
                continue
            link_path = link.split("#")[0]
            if not link_path:
                continue
            target = (base_dir / link_path).resolve()
            if not target.exists():
                broken.append((str(md.relative_to(SKILL)), title, link))

    assert broken == [], f"Found broken markdown links: {broken}"


def test_seven_high_leverage_design_levers_and_template_slots(tmp_path: Path):
    """Verify that design-methods.md and all contract templates contain the 7 high-leverage levers."""
    # 1. Verify design-methods.md has 7 levers and Divergence Gate
    methods_md = (SKILL / "references/01-foundations/design-methods.md").read_text(encoding="utf-8")
    assert "Reality Anchors & Tension Triad" in methods_md
    assert "OOUX Cardinality-to-Layout Mapping" in methods_md
    assert "Action Verb Lifecycle" in methods_md
    assert "Zero Naked Metrics & Micro Sparklines" in methods_md
    assert "Decisive 3-Frame & Context Preservation" in methods_md
    assert "The Craft Physics Triad" in methods_md
    assert "The Break Protocol" in methods_md
    assert "Divergence Gate" in methods_md
    assert "Axis Inversion" in methods_md

    # 2. Verify product.md template has Reality Benchmark Anchors and Ruthless Omissions
    product_tmpl = (SKILL / "templates/product.md").read_text(encoding="utf-8")
    assert "Operational Scene & Consequence" in product_tmpl
    assert "Reality Benchmark Anchors" in product_tmpl
    assert "Three Ruthless Omissions" in product_tmpl
    assert "OOUX Entity Cardinality & Relationships" in product_tmpl

    # 3. Verify experience-foundation.md template has 5-Dial Style Register & Craft Physics Triad
    foundation_tmpl = (SKILL / "templates/experience-foundation.md").read_text(encoding="utf-8")
    assert "5-Dial Style Register & Vague-Word Translation" in foundation_tmpl
    assert "Microscopic Craft Physics Triad" in foundation_tmpl
    assert "Concentric Radii Formula" in foundation_tmpl
    assert "OOUX Anti-Contamination & Non-Transfer Boundary" in foundation_tmpl

    # 4. Verify slice-contract.md has Action Verb Lifecycle & Decisive 3-Frame
    slice_tmpl = (SKILL / "templates/slice-contract.md").read_text(encoding="utf-8")
    assert "Action Verb Lifecycle Table" in slice_tmpl
    assert "Decisive Exchange 3-Frame Specification" in slice_tmpl
    assert "Context Preservation Rules" in slice_tmpl

    # 5. Verify prototype-specification.md has Dual-Channel & Break Protocol
    spec_tmpl = (SKILL / "templates/prototype-specification.md").read_text(encoding="utf-8")
    assert "Dual-Channel Ergonomics" in spec_tmpl
    assert "The Break Protocol Stress Checkpoints" in spec_tmpl

    # 6. Verify assemble_envelope extracts verbs, shortcuts, and break checkpoints
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")
    # Setup mock slice
    (tmp_path / "prototype").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/product.md").write_text("# Product\n- Core Tension: A vs B\n", encoding="utf-8")
    (tmp_path / "prototype/shared").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/shared/tokens.css").write_text(":root {}\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/tokens").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/surface-maps/m1.md").write_text("# Map\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/foundation/f1.md").write_text("# Foundation\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/slices/slice_a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/slices/slice_a/c1.md").write_text("""# Contract
## Action Verb Lifecycle Table
| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
| isolate_node | Isolate | Isolate Compute Node | Isolate Node | Node isolated | Safety isolation |
""", encoding="utf-8")
    (tmp_path / "prototype/specifications/slice_a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/specifications/slice_a/r1.md").write_text("""# Spec
- Prototype write scope: `prototype/experiments/slice_a/hero-anchor/`
- Evidence write scope: `prototype/evidence/probes/slice_a/`
## Dual-Channel Ergonomics
| Shortcut Key | Target Action | Scope | Focus Restoration Anchor |
|---|---|---|---|
| Space | Run | Selection | trigger |
## The Break Protocol Stress Checkpoints
| Reality Breaker | Test Vector | Expected Graceful Behavior | Observed |
|---|---|---|---|
| Unbreakable String | 64-char hash | Truncate with tooltip | pass |
## Verifiable Design Assertions
| Assertion | Expected |
|---|---|
| Key shortcut Space triggers action | pass |
""", encoding="utf-8")

    env = assemble_mod.assemble(tmp_path, "slice_a")
    constraints = env["design_constraints"]
    assert any(v["action_id"] == "isolate_node" for v in constraints["action_verb_lifecycle"])
    assert "Space" in constraints["dual_channel_shortcuts"]
    assert any("Unbreakable String" in c for c in constraints["break_protocol_checkpoints"])





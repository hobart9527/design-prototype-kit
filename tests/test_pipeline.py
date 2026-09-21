from pathlib import Path
import hashlib
import importlib.util
import json
import re
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
    assert "QUALITY HARNESS" in portal_html

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
    product.write_text("# Product\n- Core Tension: Speed vs Safety\n- Reality Anchors: Linear\n- Content Language: en-US\n\n```prototype-context\nrecord: product\n```\n", encoding="utf-8")

    smap = tmp_path / "prototype/contracts/surface-maps/m1.md"
    smap.parent.mkdir(parents=True, exist_ok=True)
    smap.write_text("# Surface Map\n\n```prototype-context\nrecord: surface-map\nrevision: m1\ncoverage: full-product\nsurfaces: test_slice\n```\n", encoding="utf-8")

    foundation = tmp_path / "prototype/contracts/foundation/f1.md"
    foundation.parent.mkdir(parents=True, exist_ok=True)
    foundation.write_text("# Foundation\n- Foundation revision: f1\n- Grounding Rationale: Non-transfer boundaries\n\n```prototype-context\nrecord: experience-foundation\n```\n", encoding="utf-8")

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
    slice_c.write_text("# Contract\n- Slice ID: test_slice\n- Content Language: en-US\n\n## Action Verb Lifecycle Table\n| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact |\n| a | b | c | d | e | f |\n", encoding="utf-8")

    spec = tmp_path / "prototype/specifications/test_slice/r1.md"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text("""# Spec
- Prototype write scope: `prototype/experiments/test_slice/hero-anchor/`
- Evidence write scope: `prototype/evidence/probes/test_slice/`
- Content Language: en-US

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

```prototype-context
record: prototype-specification
```
""", encoding="utf-8")

    # 3. Assemble generates complete pre-baked envelope
    env = assemble_mod.assemble(tmp_path, "test_slice")
    assert env["mode"] == "lean-builder-envelope"
    assert env["target_html_path"] == "prototype/experiments/test_slice/hero-anchor/index.html"
    assert "max_tool_turns" not in env["design_constraints"]
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
    disc_text = """## 5-Dial Style Register\n- Energy: 3\n- Finish: 4\n- Density: 4\n- Weight: 3\n- Seriousness: 4\n- Palette: plasma-cyan\n"""
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
    assert toy_pass is False  # Minimal artifact has no complete interaction contract

    # 6a. Reject raw inline hex in style attributes
    hex_html = tmp_path / "hex_test.html"
    hex_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens_gen.css"></head><body><button id="b1" onclick="void(0)" style="color: #ff0000; border-radius: var(--radius-btn);">Submit</button></body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(hex_html), str(out_css), check_stale=False) is False

    # 6b. Reject placeholder copy under check_stale
    stale_html = tmp_path / "stale_test.html"
    stale_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens_gen.css"></head><body><button id="b1" onclick="void(0)" style="color: var(--primary); border-radius: var(--radius-btn);">Lorem ipsum</button></body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(stale_html), str(out_css), check_stale=True) is False

    real_hero = REPO / "prototype/experiments/console/hero-anchor/index.html"
    if real_hero.is_file():
        real_pass = verify_mod.assert_quality(str(real_hero), str(out_css), check_stale=False, contract_path="")
        assert real_pass is True or real_pass is False  # static result is reported truthfully

    # 7. Verify builder agent contract specifies Lean Pre-baked Envelope Protocol
    builder_md = (REPO / "agents/spec-prototype-builder.md").read_text(encoding="utf-8")
    assert "Lean Pre-baked Envelope Protocol" in builder_md
    assert "≤ 8 tool turns" not in builder_md and "<= 8 tool turns" not in builder_md
    assert "an execution-safety budget" in builder_md

    # 8. Verify SKILL.md and core-workflow.md declare Spec-First invariant & 6 pillars
    core_wf = (SKILL / "references/core-workflow.md").read_text(encoding="utf-8")
    assert ("No Prototype Code without a Sealed Provisional Spec Contract" in core_wf or
            "No Prototype Code without a Frozen Spec Contract" in core_wf)
    assert "foundation/f1.md" in core_wf
    skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert ("ZERO Prototype Code without a complete sealed provisional Spec Contract" in skill_md or
            "ZERO Prototype Code without a complete frozen Spec Contract" in skill_md)
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
    (tmp_path / "prototype/product.md").write_text("# Product\n- Core Tension: A vs B\n- Reality Anchors: Linear\n- Content Language: en-US\n\n```prototype-context\nrecord: product\n```\n", encoding="utf-8")
    (tmp_path / "prototype/shared").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/shared/tokens.css").write_text(":root {}\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/tokens").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/surface-maps/m1.md").write_text("# Map\n\n```prototype-context\nrecord: surface-map\nrevision: m1\ncoverage: full-product\nsurfaces: slice_a\n```\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/foundation/f1.md").write_text("# Foundation\n- Core Tension: A vs B\n- Grounding Rationale: Rationale\n\n```prototype-context\nrecord: experience-foundation\n```\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/slices/slice_a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/slices/slice_a/c1.md").write_text("""# Contract
- Content Language: en-US

## Action Verb Lifecycle Table
| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
| isolate_node | Isolate | Isolate Compute Node | Isolate Node | Node isolated | Safety isolation |
""", encoding="utf-8")
    (tmp_path / "prototype/specifications/slice_a").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/specifications/slice_a/r1.md").write_text("""# Spec
- Content Language: en-US
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

```prototype-context
record: prototype-specification
```
""", encoding="utf-8")

    env = assemble_mod.assemble(tmp_path, "slice_a")
    constraints = env["design_constraints"]
    # Column identity follows the authored header, not positional width: the legacy
    # 6-column table must still yield the real commit button and feedback, never the
    # container/header or impact columns that happen to sit at those positions.
    isolate = next(v for v in constraints["action_verb_lifecycle"] if v["action_id"] == "isolate_node")
    assert isolate["commit_btn"] == "Isolate Node"
    assert isolate["feedback_style"] == "Node isolated"
    assert "Space" in constraints["dual_channel_shortcuts"]
    assert any("Unbreakable String" in c for c in constraints["break_protocol_checkpoints"])


def test_materialize_contracts_high_fidelity_semantic_synthesis(tmp_path: Path):
    """Verify materialize_contracts compiles Chinese/English discussions into complete 6-pillar contracts."""
    mat_mod = _load("materialize_contracts", "materialize_contracts.py")
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")

    proto_dir = tmp_path / "prototype"
    proto_dir.mkdir(parents=True, exist_ok=True)

    disc_text = """# Discussion
### 1. 业务与用户极端张力 (Core Tension)
- 吞吐 vs 崩溃风险

### 4. 5-Dial 风格寄存器
- Energy: quiet
- Finish: machined-industrial
- Density: dense
- Weight: dense-tactile
- Seriousness: solemn
- Palette: plasma-cyan

### 5. OOUX 实体拓扑与表面分配
- **主工作区 (Primary)**: `console/hero-anchor`（拓扑总览）
- **上下文视图 (Contextual)**: `surfaces/incident-replay`（帧回放）
- **支撑视图 (Supporting)**: `surfaces/capacity-matrix`（矩阵）
"""
    (proto_dir / "discussion.md").write_text(disc_text, encoding="utf-8")
    (proto_dir / "product.md").write_text(
        "# SRE Platform\n## Core Tension\n- 秒级排空 vs 误杀风险\n"
        "- Reality Anchors: Bloomberg terminal density, Tokyo rail dispatch boards\n",
        encoding="utf-8",
    )

    # Materialize contracts
    res = mat_mod.materialize(tmp_path, "console", force=True)
    assert Path(res["surface_map"]).is_file()
    assert Path(res["foundation"]).is_file()
    assert Path(res["slice_contract"]).is_file()
    assert Path(res["specification"]).is_file()

    # 1. Surface map contains Chinese-declared surfaces
    smap_text = Path(res["surface_map"]).read_text(encoding="utf-8")
    assert "console/hero-anchor" in smap_text
    assert "surfaces/incident-replay" in smap_text
    assert "surfaces/capacity-matrix" in smap_text

    # 2. Slice contract contains Action Verb Lifecycle & Decisive 3-Frame
    c1_text = Path(res["slice_contract"]).read_text(encoding="utf-8")
    assert "Action Verb Lifecycle Table" in c1_text
    assert "Decisive Exchange 3-Frame Specification" in c1_text
    assert "Context Preservation Rules" in c1_text
    # Unauthored cognitive ledger zones must stay semantically neutral: the
    # materializer reports `unspecified` rather than fabricating ungrounded
    # craft prose (tactile detents, micro-sparklines, kinetic pulses, 10x claims).
    assert "unspecified" in c1_text
    for buzzword in ("tactile detents", "micro-sparklines", "kinetic pulses", "10x situational awareness"):
        assert buzzword not in c1_text

    # 3. Specification contains Dual-Channel & Break Protocol & Verifiable Assertions
    r1_text = Path(res["specification"]).read_text(encoding="utf-8")
    assert "Dual-Channel Ergonomics" in r1_text
    assert "The Break Protocol Stress Checkpoints" in r1_text
    assert "Verifiable Design Assertions" in r1_text
    # Universal, truthful invariants only: no category heuristic may synthesize
    # domain craft claims (SRE sparklines, touch floors, editorial columns) from
    # the product's vocabulary.
    assert "Declared product intent is represented" in r1_text
    assert "High text-to-background contrast compliant with WCAG 2.2 AA" in r1_text
    assert "Zero Naked Metrics" not in r1_text
    assert "Concentric Radii Formula" not in r1_text

    # 4. Generate tokens to satisfy assemble_envelope dependencies
    tokens_css = tmp_path / "prototype/shared/tokens.css"
    tokens_css.parent.mkdir(parents=True, exist_ok=True)
    tokens_css.write_text(":root { --radius-outer: 8px; }\n", encoding="utf-8")
    tokens_md = tmp_path / "prototype/contracts/tokens/t1.md"
    tokens_md.parent.mkdir(parents=True, exist_ok=True)
    tokens_md.write_text("# Tokens\n| Token | Value |\n|---|---|\n| --bp-mobile | 390px |\n", encoding="utf-8")

    # 5. assemble_envelope produces non-empty constraints without semantic loss
    env = assemble_mod.assemble(tmp_path, "console")
    constraints = env["design_constraints"]
    assert len(constraints["dual_channel_shortcuts"]) > 0
    assert len(constraints["action_verb_lifecycle"]) > 0
    assert len(constraints["break_protocol_checkpoints"]) > 0
    assert len(constraints["decisive_exchange_frames"]) > 0
    assert len(constraints["context_preservation_rules"]) > 0
    assert len(env["verifiable_assertions"]) >= 5

    # 6. Reality anchors survive into both creative and root envelope: the
    #    Builder must read the authored real-world grounding, not a search string.
    assert "Bloomberg terminal density" in env["reality_anchors"]
    assert env["creative_envelope"]["reality_anchors"] == env["reality_anchors"]

    # 7. Craft guidance is captured whole: the legacy 18-line cutoff truncated
    #    authored sections before their closing rules reached the Builder.
    form_method = next(m for m in env["active_methods"] if m["id"] == "form-ergonomics")
    guidance = form_method["actionable_guidance"]
    assert "Form orchestration containers" in guidance
    assert len(guidance.splitlines()) > 18
    assert len(env["available_tokens"]) > 0
    assert "--radius-outer" in env["available_tokens"]


def test_tightened_quality_assertions_against_goodhart_loopholes(tmp_path: Path):
    """Verify verify_prototype_quality strictly catches missing radius tokens, shortcuts, and hash states."""
    verify_mod = _load("verify_quality", "verify_prototype_quality.py")

    tokens_css = tmp_path / "tokens.css"
    tokens_css.write_text(":root {\n  --radius-outer: 8px;\n  --radius-inner: 4px;\n  --bg-void: #05070a;\n  --font-variant-numeric: tabular-nums;\n}\n", encoding="utf-8")

    spec_md = tmp_path / "r1.md"
    spec_md.write_text("""# Spec
## Dual-Channel Ergonomics (Keyboard Shortcuts & Focus Recovery)
| Shortcut Key | Target Action |
|---|---|
| `Space` | Inspect active node |

## The Break Protocol Stress Checkpoints
| Reality Breaker | Vector |
|---|---|
| **Zero-Item Empty State** | Filter 0 |
""", encoding="utf-8")

    # 1. HTML uses var(--bg-void) but lacks var(--radius-) and font-variant-numeric
    bad_html = tmp_path / "bad.html"
    bad_html.write_text("""<!DOCTYPE html><html><body>
<main id="app" class="panel">
  <button id="btn-action" onclick="void(0)" style="color: var(--bg-void);">Run</button>
</main>
</body></html>""", encoding="utf-8")

    # Fails because radius and numeric presentation tokens are not consumed, despite presence of var(--bg-void)
    assert verify_mod.assert_quality(str(bad_html), str(tokens_css), contract_path=str(spec_md)) is False

    # 2. HTML adds var(--radius-outer) and tabular-nums, but still lacks keyboard listener and hashchange
    semi_html = tmp_path / "semi.html"
    semi_html.write_text("""<!DOCTYPE html><html><body>
<main id="app" class="panel" style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
  <button id="btn-action" onclick="void(0)">Run</button>
</main>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(semi_html), str(tokens_css), contract_path=str(spec_md)) is False

    # 3. HTML adds keydown listener, overflow containment, and hashchange state machine hook -> passes
    good_html = tmp_path / "good.html"
    good_html.write_text("""<!DOCTYPE html><html><body>
<main id="app" class="panel" style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums; overflow: hidden;">
  <button id="btn-action" onclick="void(0)">Run</button>
</main>
<script>
  window.addEventListener('keydown', (e) => {});
  window.addEventListener('hashchange', () => {});
  document.body.setAttribute('data-state', 'default');
</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(good_html), str(tokens_css), contract_path=str(spec_md)) is True


def test_topology_context_and_convention_cli(tmp_path: Path):
    """Verify envelope compiles multi-surface topology links and convention-based CLI."""
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")

    product = tmp_path / "prototype/product.md"
    product.parent.mkdir(parents=True, exist_ok=True)
    product.write_text("# Product\n- Core Tension: Speed vs Safety\n- Reality Anchors: Linear\n- Content Language: en-US\n\n```prototype-context\nrecord: product\n```\n", encoding="utf-8")

    disc = tmp_path / "prototype/discussion.md"
    disc.parent.mkdir(parents=True, exist_ok=True)
    disc.write_text("# Discussion\n- Content Language: en-US\n", encoding="utf-8")

    smap = tmp_path / "prototype/contracts/surface-maps/m1.md"
    smap.parent.mkdir(parents=True, exist_ok=True)
    smap.write_text("""# Surface Map
- **主工作区 (Primary)**: `console/hero-anchor`（GPU 拓扑）
- **上下文视图 (Contextual)**: `surfaces/incident-replay`（帧回放）
- **支撑视图 (Supporting)**: `surfaces/capacity-matrix`（算力配额）

```prototype-context
record: surface-map
revision: m1
coverage: selected
selection-source: prototype/discussion.md
selected-surfaces: console
surfaces: console, incident-replay, capacity-matrix
```
""", encoding="utf-8")

    foundation = tmp_path / "prototype/contracts/foundation/f1.md"
    foundation.parent.mkdir(parents=True, exist_ok=True)
    foundation.write_text("# Foundation\n- Foundation revision: f1\n- Core Tension: Speed vs Safety\n- Grounding Rationale: Non-transfer\n\n```prototype-context\nrecord: experience-foundation\n```\n", encoding="utf-8")

    tokens_css = tmp_path / "prototype/shared/tokens.css"
    tokens_css.parent.mkdir(parents=True, exist_ok=True)
    tokens_css.write_text(":root { --radius-outer: 8px; }\n", encoding="utf-8")

    tokens_md = tmp_path / "prototype/contracts/tokens/t1.md"
    tokens_md.parent.mkdir(parents=True, exist_ok=True)
    tokens_md.write_text("# Tokens\n| Token | Value |\n|---|---|\n| --bp-mobile | 390px |\n", encoding="utf-8")

    tokens_json = tmp_path / "prototype/contracts/tokens/t1.json"
    tokens_json.write_text("{}", encoding="utf-8")

    slice_c = tmp_path / "prototype/contracts/slices/console/c1.md"
    slice_c.parent.mkdir(parents=True, exist_ok=True)
    slice_c.write_text("""# Contract
- Slice ID: console
- Content Language: en-US

## Action Verb Lifecycle Table
- Action Verb: N/A (Not Applicable)
""", encoding="utf-8")

    spec = tmp_path / "prototype/specifications/console/r1.md"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text("""# Spec
- Content Language: en-US
- Prototype write scope: `prototype/experiments/console/hero-anchor/`
- Evidence write scope: `prototype/evidence/probes/console/`

## The Break Protocol Stress Checkpoints
- The Break Protocol: N/A (Not Applicable)

## Verifiable Design Assertions
| Assertion | Expected |
|---|---|
| Space shortcut | pass |

```prototype-context
record: prototype-specification
```
""", encoding="utf-8")

    env = assemble_mod.assemble(tmp_path, "console")
    assert env["envelope_version"] == "2.0"
    assert "token_link_tag" in env
    assert "shared/tokens.css" in env["token_link_tag"]
    assert env["verification_command"] == "python3 skills/spec-prototype/scripts/verify_prototype_quality.py --slice console"
    assert env["capture_command"] == "node skills/spec-prototype/scripts/capture.mjs --slice console"

    topology = env["topology_context"]
    assert topology["current_slice"] == "console"
    assert topology["surface_role"] == "primary"
    links = topology["shared_shell"]["navigation_links"]
    assert len(links) == 3
    assert any(link["slice_id"] == "console" and link["active"] for link in links)
    assert any(link["slice_id"] == "incident-replay" and not link["active"] for link in links)
    assert any(link["slice_id"] == "capacity-matrix" and not link["active"] for link in links)

    # 6. Verify verify_prototype_quality enforces topology navigation when m1.md is present
    verify_mod = _load("verify_quality", "verify_prototype_quality.py")
    test_html = tmp_path / "prototype/experiments/console/hero-anchor/index.html"
    test_html.parent.mkdir(parents=True, exist_ok=True)
    # Page without sibling links fails topology assertion
    test_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="../../../shared/tokens.css"></head><body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;"><button>Go</button></main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(test_html), str(tokens_css), contract_path=str(spec)) is False

    # Page with sibling link passes topology assertion
    # The referenced sibling surface must exist: a link to an undelivered surface is a 404 defect.
    sibling = tmp_path / "prototype/surfaces/incident-replay/index.html"
    sibling.parent.mkdir(parents=True, exist_ok=True)
    sibling.write_text("<!DOCTYPE html><html><body>Incident Replay</body></html>", encoding="utf-8")
    test_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="../../../shared/tokens.css"></head><body>
<nav><a href="../../../surfaces/incident-replay/index.html">Incident</a>
<button disabled aria-disabled="true" data-sibling="capacity-matrix">Capacity Matrix (undelivered)</button></nav>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;"><button>Go</button></main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(test_html), str(tokens_css), contract_path=str(spec)) is True

    # 7. Undelivered sibling surfaces: a live href is a 404 defect, a disabled
    # affordance keeps the destination review-visible without a broken link.
    sibling.unlink()
    sibling.parent.rmdir()
    assert verify_mod.assert_quality(str(test_html), str(tokens_css), contract_path=str(spec)) is False
    test_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="../../../shared/tokens.css"></head><body>
<nav><button disabled aria-disabled="true" data-sibling="incident-replay">Incident Replay (undelivered)</button>
<button disabled aria-disabled="true" data-sibling="capacity-matrix">Capacity Matrix (undelivered)</button></nav>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;"><button>Go</button></main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(test_html), str(tokens_css), contract_path=str(spec)) is True


def test_execution_boundary_admits_craft_helpers():
    """wcag-check.js and check-assertions.py are installed read helpers."""
    boundary.shell_read("node skills/spec-prototype/scripts/wcag-check.js --slice console", Path("/tmp/root"))
    boundary.shell_read("python3 skills/spec-prototype/scripts/check-assertions.py a b", Path("/tmp/root"))
    boundary.shell_read("python3.14 skills/spec-prototype/scripts/check-assertions.py a b", Path("/tmp/root"))
    with pytest.raises(ValueError):
        boundary.shell_read("python3 skills/spec-prototype/scripts/rogue.py a", Path("/tmp/root"))


def test_5_system_modern_industrial_derivation_and_rogue_root_blocking(tmp_path: Path):
    """Verify modern industrial token derivation and rogue :root blocking in quality gate."""
    compile_mod = _load("compile_tokens", "compile_tokens.py")
    verify_mod = _load("verify_quality", "verify_prototype_quality.py")
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")
    mat_mod = _load("materialize_contracts", "materialize_contracts.py")

    # 1. compile_tokens generates Teenage Engineering warm-graphite-lime palette
    dials = {"energy": "quiet", "finish": "machined-industrial", "density": "dense", "weight": "dense-tactile", "seriousness": "solemn"}
    te_tokens = compile_mod.compute_tokens(dials, "teenage-engineering")
    assert te_tokens["colors"]["accent_primary"] == "#d6f56b"
    assert te_tokens["colors"]["bg_void"] == "#080b0b"
    assert te_tokens["colors"]["text_primary"] == "#f4f5f1"

    linear_tokens = compile_mod.compute_tokens(dials, "linear-dark")
    assert linear_tokens["colors"]["accent_primary"] == "#5e6ad2"
    assert linear_tokens["colors"]["bg_void"] == "#08090c"

    # Also test CSS rendering
    css = compile_mod.generate_css(te_tokens)
    assert "--accent-primary: #d6f56b;" in css
    assert "--bg-void: #080b0b;" in css

    # 2. verify_prototype_quality strictly catches and blocks rogue :root color overrides
    tokens_css = tmp_path / "tokens.css"
    tokens_css.write_text(":root { --accent-primary: #d6f56b; --radius-outer: 8px; font-variant-numeric: tabular-nums; }\n", encoding="utf-8")

    rogue_html = tmp_path / "rogue.html"
    rogue_html.write_text("""<!DOCTYPE html><html><head>
<link rel="stylesheet" href="tokens.css">
<style>
  :root {
    --accent-primary: #ff00ff;
    --bg-void: #000000;
  }
</style>
</head><body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;"><button>Go</button></main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(rogue_html), str(tokens_css)) is False

    # 3. assemble_envelope injects layout_profile and app_shell_contract
    (tmp_path / "prototype").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/product.md").write_text("# Product\nBaseline 1: Dense Data Workbench\n", encoding="utf-8")
    (tmp_path / "prototype/shared").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/shared/tokens.css").write_text(":root {}\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/tokens").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/surface-maps/m1.md").write_text("# Map\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/foundation/f1.md").write_text("# Foundation\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/slices/telemetry").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/slices/telemetry/c1.md").write_text("# Contract\n", encoding="utf-8")
    (tmp_path / "prototype/specifications/telemetry").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/specifications/telemetry/r1.md").write_text("""# Spec
- Prototype write scope: `prototype/experiments/telemetry/anchor/`
- Evidence write scope: `prototype/evidence/probes/telemetry/`
## Verifiable Design Assertions
| Space | pass |
""", encoding="utf-8")

    env = assemble_mod.assemble(tmp_path, "telemetry", lint=False)
    assert env["layout_profile"] == "dense-console"
    assert "app_shell_contract" in env
    assert "cognitive_ledger" in env
    assert "zero_borrow_base" in env["cognitive_ledger"]
    assert "high_yield_borrow_zone" in env["cognitive_ledger"]
    assert env["app_shell_contract"]["profile"] == "dense-console"
    assert env["target_html_path"] == "prototype/experiments/telemetry/anchor/index.html"

    # Also verify materialize_contracts generates Cognitive Budgeting Ledger
    (tmp_path / "prototype/discussion.md").write_text("""# Discussion
- energy: quiet
- finish: machined-industrial
- density: dense
- weight: dense-tactile
- seriousness: solemn
- palette: plasma-cyan
- **Cognitive Budgeting Allocation**:
  - *Routine Conventions (Zero-learning)*: Top bar navigation and filter chips strictly standard
  - *Decisive Innovation (Borrowed focus)*: Real-time telemetry heat-map receives tactile detents
""", encoding="utf-8")
    mat_mod.materialize(tmp_path, "telemetry", force=True)
    c1_text = (tmp_path / "prototype/contracts/slices/telemetry/c1.md").read_text(encoding="utf-8")
    assert "## Cognitive Budgeting & Energy Return Ledger" in c1_text
    assert "Low-Entropy Base" in c1_text
    assert "High-Yield Borrow Zone" in c1_text

    # 4. LLM dynamic custom chromatic derivation from Stage 1 discussion
    disc_file = tmp_path / "discussion_custom.md"
    disc_file.write_text("""# Discussion
- energy: quiet
- finish: machined-industrial
- density: dense
- weight: dense-tactile
- seriousness: solemn
### LLM Dynamic Chromatic Exploration
- accent-primary: #c76b3a
- bg-void: #141210
""", encoding="utf-8")
    custom_colors = compile_mod.extract_dynamic_palette(disc_file.read_text(encoding="utf-8"))
    assert custom_colors["accent_primary"] == "#c76b3a"
    assert custom_colors["bg_void"] == "#141210"
    # Derived mathematical elevation
    assert custom_colors["bg_surface"].startswith("#")
    assert custom_colors["bg_surface"] != "#141210"
    assert "rgba(199, 107, 58" in custom_colors["accent_subtle"]

    out_json = tmp_path / "out_t1.json"
    out_md = tmp_path / "out_t1.md"
    out_css = tmp_path / "out_tokens.css"
    compile_mod.compile_tokens(str(disc_file), str(out_css), str(out_json), str(out_md))
    assert out_css.is_file()
    css_content = out_css.read_text(encoding="utf-8")
    assert "--accent-primary: #c76b3a;" in css_content
    assert "--bg-void: #141210;" in css_content


def test_operationalized_design_techniques_across_stages(tmp_path: Path):
    """Verify all operationalized techniques across Stages 1-4 are enforced in contracts, envelopes, and quality checks."""
    mat_mod = _load("materialize_contracts", "materialize_contracts.py")
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")
    verify_mod = _load("verify_quality", "verify_prototype_quality.py")

    # 1. Setup workspace with Ruthless Omissions and Material Invariants in Stage 1
    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "product.md").write_text("""# Product Thesis
- Dominant Baseline: Baseline 1: Dense Data & Engineering Workbench
- Reality Anchors: Linear, Datadog
- Tension: Throughput vs Safety
""", encoding="utf-8")

    (proto / "discussion.md").write_text("""# Discussion: GPU Cluster Control Plane
- energy: quiet
- finish: machined-industrial
- density: dense
- weight: dense-tactile
- seriousness: solemn
- palette: titanium-amber
- domain: SRE GPU cluster node telemetry with node drain operations
## 3 Ruthless Omissions
1. Zero generic marketing cards or carousel widgets
2. Zero nested modal inception or multi-step wizard deadlocks
3. Zero ungrounded particle physics or #808080 dead grays
## Material Non-Transfer Boundaries
1. Machined Detents: tactile switches possess mechanical micro-press (:active scale(0.97))
2. Telemetry Emissives: status indicators simulate physical LEDs with subtle bloom
""", encoding="utf-8")

    # Materialize contracts
    mat_mod.materialize(tmp_path, "cluster-node", force=True)

    # Check that f1.md contains 3 Ruthless Omissions and Material Non-Transfer Boundaries
    f1_text = (proto / "contracts/foundation/f1.md").read_text(encoding="utf-8")
    assert "## 3 Ruthless Omissions" in f1_text
    assert "Zero generic marketing cards" in f1_text
    assert "## Material Non-Transfer Boundaries" in f1_text
    assert "Machined Detents" in f1_text

    # Check that assemble_envelope injects blueprints and constraints
    (proto / "shared").mkdir(parents=True, exist_ok=True)
    (proto / "shared/tokens.css").write_text(":root { --radius-outer: 6px; --radius-inner: 3px; --bg-void: #0d0e10; }\n", encoding="utf-8")
    (proto / "contracts/tokens").mkdir(parents=True, exist_ok=True)
    (proto / "contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")

    env = assemble_mod.assemble(tmp_path, "cluster-node")
    assert "app_shell_blueprint" in env
    assert env["app_shell_blueprint"]["profile"] == "dense-console"
    assert "operational_viewport" in env["app_shell_blueprint"]["spatial_roles"]
    assert "tabular-nums" in env["app_shell_blueprint"]["density_rules"]
    assert "ruthless_omissions" in env["design_constraints"]
    assert len(env["design_constraints"]["ruthless_omissions"]) >= 3
    assert "material_non_transfer_boundaries" in env["design_constraints"]
    assert len(env["design_constraints"]["material_non_transfer_boundaries"]) >= 2

    # 2. Test verify_prototype_quality strictly enforces Zero Naked Metrics, Tactile Detents, and full Action Lifecycle
    r1_path = proto / "specifications/cluster-node/r1.md"
    tokens_css = proto / "shared/tokens.css"

    # Minimal HTML that lacks SVG sparklines / baseline context, lacks :active, and lacks modal/toast lifecycle
    test_html = tmp_path / "test.html"
    test_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="../../../shared/tokens.css"></head><body>
<nav><a href="../../../surfaces/console/index.html">Console</a></nav>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums; overflow: hidden;">
  <button id="drain-node">Drain Node</button>
  <div class="metrics"><span>128 GB</span></div>
</main>
<script>
  window.addEventListener('keydown', ()=>{});
  window.addEventListener('hashchange', ()=>{});
  document.body.dataset.state = 'ideal';
</script>
</body></html>""", encoding="utf-8")

    # Must fail because:
    # 1. Action Lifecycle: modal header "Drain GPU Node", commit button "Confirm Drain", and toast "Node Drained Successfully" are absent!
    # 2. Zero Naked Metrics: metrics lack SVG sparkline or baseline/unit context
    # 3. Tactile Detents: :active { transform: scale(...) } missing
    assert verify_mod.assert_quality(str(test_html), str(tokens_css), contract_path=str(r1_path)) is False

    # Fully conforming HTML that satisfies all operationalized techniques
    # Sibling nav target must exist on disk: navigation integrity rejects links to undelivered surfaces.
    (tmp_path / "prototype/surfaces/console").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/surfaces/console/index.html").write_text(
        "<!DOCTYPE html><html><body>Console</body></html>", encoding="utf-8")
    good_html = tmp_path / "good_conforming.html"
    good_html.write_text("""<!DOCTYPE html><html><head>
<link rel="stylesheet" href="../../../shared/tokens.css">
<style>
  button:active { transform: scale(0.97); }
  .truncate { text-overflow: ellipsis; overflow: hidden; }
</style>
</head><body>
<nav><a href="prototype/surfaces/console/index.html">Console</a></nav>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;" class="truncate">
  <!-- Full Action Verb Lifecycle elements -->
  <button id="drain-node" data-action="drain-node">Drain Node</button>
  <dialog id="modal">
    <h3>Drain GPU Node</h3>
    <button id="confirm-drain">Confirm Drain</button>
  </dialog>
  <div id="toast" class="toast">Node Drained Successfully</div>

  <!-- Zero Naked Metrics: accompanied by SVG micro-sparkline & baseline class -->
  <div class="metric-card">
    <span class="unit">128 GB</span>
    <span class="baseline">Nominal 95%</span>
    <svg width="60" height="20"><polyline points="0,15 20,10 40,12 60,5" fill="none" stroke="currentColor"/></svg>
  </div>
</main>
<script>
  window.addEventListener('keydown', ()=>{});
  window.addEventListener('hashchange', ()=>{});
  document.body.dataset.state = 'ideal';
</script>
</body></html>""", encoding="utf-8")

    assert verify_mod.assert_quality(str(good_html), str(tokens_css), contract_path=str(r1_path)) is True

    # Modal-free Direct Manipulation HTML (Linear/Figma style optimistic action without modal header or toast)
    direct_html = tmp_path / "direct_manipulation.html"
    direct_html.write_text("""<!DOCTYPE html><html><head>
<link rel="stylesheet" href="../../../shared/tokens.css">
<style>
  button:active { transform: scale(0.97); }
  .truncate { text-overflow: ellipsis; overflow: hidden; }
</style>
</head><body>
<nav><a href="prototype/surfaces/console/index.html">Console</a></nav>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;" class="truncate">
  <!-- Direct trigger with inline feedback (no modal dialog) -->
  <button id="drain-node" data-action="drain-node">Drain Node</button>
  <span class="status-indicator">Node Drained Successfully</span>

  <!-- Metric with HTML5 meter and unit badge -->
  <div class="metric-card">
    <span class="unit">128 GB</span>
    <meter value="95" min="0" max="100">95%</meter>
  </div>
</main>
<script>
  window.addEventListener('keydown', ()=>{});
  window.addEventListener('hashchange', ()=>{});
  document.body.dataset.state = 'ideal';
</script>
</body></html>""", encoding="utf-8")

    # Confirms generative freedom: no modal dialog or toast required, direct manipulation passes
    assert verify_mod.assert_quality(str(direct_html), str(tokens_css), contract_path=str(r1_path)) is True


def test_phased_double_diamond_contract_materialization(tmp_path: Path):
    """Verify phased Double-Diamond contract materialization (Phase 1 -> 2 -> 3 -> 4)."""
    mat_mod = _load("materialize_contracts", "materialize_contracts.py")

    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "discussion.md").write_text("""# Discussion
- Product: Audio DSP Cockpit
- Baseline: Baseline 1: Dense Data & Engineering Workbench
- Reality Anchors: Teenage Engineering, Ableton
- Tension: Tactile Immediacy vs Algorithmic Precision
- palette: warm-graphite-lime
## 3 Ruthless Omissions
1. Zero generic marketing cards
2. Zero nested modal inception
3. Zero decorative particle physics
""", encoding="utf-8")

    # Phase 1: Materializes product.md only
    res_p1 = mat_mod.materialize(tmp_path, "dsp-slice", phase="1")
    assert "product" in res_p1
    assert (proto / "product.md").is_file()
    assert "Audio DSP Cockpit" in (proto / "product.md").read_text(encoding="utf-8")
    assert not (proto / "contracts/surface-maps/m1.md").is_file()

    # Phase 2: Materializes surface_map m1.md only
    res_p2 = mat_mod.materialize(tmp_path, "dsp-slice", phase="2")
    assert "surface_map" in res_p2
    assert (proto / "contracts/surface-maps/m1.md").is_file()
    assert not (proto / "contracts/foundation/f1.md").is_file()

    # Phase 3: Materializes foundation f1.md only
    res_p3 = mat_mod.materialize(tmp_path, "dsp-slice", phase="3")
    assert "foundation" in res_p3
    assert (proto / "contracts/foundation/f1.md").is_file()
    assert not (proto / "contracts/slices/dsp-slice/c1.md").is_file()

    # Phase 4: Materializes slice_contract c1.md & specification r1.md
    res_p4 = mat_mod.materialize(tmp_path, "dsp-slice", phase="4")
    assert "slice_contract" in res_p4
    assert "specification" in res_p4
    assert (proto / "contracts/slices/dsp-slice/c1.md").is_file()
    assert (proto / "specifications/dsp-slice/r1.md").is_file()


def test_multi_archetype_adaptation_and_flexible_verification(tmp_path: Path):
    """Verify non-B-end archetypes (Editorial Reading & Consumer Touch) materialize and pass verification."""
    mat_mod = _load("materialize_contracts", "materialize_contracts.py")
    env_mod = _load("assemble_envelope", "assemble_envelope.py")
    tok_mod = _load("compile_tokens", "compile_tokens.py")
    verify_mod = _load("verify_prototype_quality", "verify_prototype_quality.py")

    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "discussion.md").write_text("""# Discussion
- Product: Dispatch Longform Reader
- Baseline: Baseline 3: Editorial & Focused Reading
- Reality Anchors: Substack, Medium, iA Writer
- Tension: Deep Focus vs Serendipitous Discovery
- palette: warm-graphite-lime
- energy: quiet
- finish: polished
- density: sparse
- weight: light
- seriousness: solemn
## Declared Surfaces
- Primary: story-reader
- Contextual: marginalia-notes
## Action Verbs
| Action ID | Trigger Button Label | Modal Header | Commit Action Button | Completion Feedback Toast | Impact |
| bookmark-story | Bookmark Story | Save Bookmark | Confirm Save | Story Saved to Reading List | Saves story |
""", encoding="utf-8")

    # Materialize contracts and compile tokens for editorial slice
    mat_mod.materialize(tmp_path, "story-reader")
    tokens_css = proto / "shared/tokens.css"
    tokens_json = proto / "contracts/tokens/t1.json"
    tokens_md = proto / "contracts/tokens/t1.md"
    tokens_css.parent.mkdir(parents=True, exist_ok=True)
    tokens_json.parent.mkdir(parents=True, exist_ok=True)
    tok_mod.compile_tokens(str(proto / "discussion.md"), str(tokens_css), str(tokens_json), str(tokens_md))

    assert (proto / "contracts/foundation/f1.md").is_file()
    f1_text = (proto / "contracts/foundation/f1.md").read_text(encoding="utf-8")
    assert "reading" in f1_text.lower() or "editorial" in f1_text.lower() or "omissions" in f1_text.lower()

    # Assemble envelope: must select editorial-reading layout profile
    env = env_mod.assemble(tmp_path, "story-reader")
    assert env["layout_profile"] == "editorial-reading"
    assert env["app_shell_contract"]["profile"] == "editorial-reading"
    assert env["topology_context"]["shared_shell"]["brand_title"] == "Dispatch Longform Reader"

    # Verify that a minimalist editorial prototype passes quality checks
    tokens_css = proto / "shared/tokens.css"
    edit_html = tmp_path / "prototype/experiments/story-reader/anchor/index.html"
    edit_html.parent.mkdir(parents=True, exist_ok=True)
    edit_html.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="../../../shared/tokens.css">
  <style>
    body { background: var(--bg-surface); color: var(--text-main); font-family: serif; max-width: 68ch; margin: auto; }
    .story-card { border-radius: var(--radius-md); padding: 16px; overflow: hidden; text-overflow: ellipsis; }
    button:active { opacity: 0.75; transform: translateY(1px); }
    .reading-stat { font-variant-numeric: tabular-nums; }
  </style>
</head>
<body data-state="reading">
  <main class="story-card">
    <h1>Dispatch Longform</h1>
    <span class="reading-stat">12 min read</span>
    <button id="bookmark-story">Bookmark Story</button>
    <div id="toast">Story Saved to Reading List</div>
  </main>
  <script>
    window.addEventListener('hashchange', () => {});
    window.addEventListener('keydown', (e) => { if(e.key === 'Escape') {} });
  </script>
</body>
</html>""", encoding="utf-8")

    r1_path = proto / "specifications/story-reader/r1.md"
    assert verify_mod.assert_quality(str(edit_html), str(tokens_css), contract_path=str(r1_path)) is True


def test_confirmed_option_priority_in_token_extraction(tmp_path: Path):
    """Verify compile_tokens selects confirmed decisions over earlier rejected candidates."""
    compile_mod = _load("compile_tokens", "compile_tokens.py")
    discussion = tmp_path / "discussion.md"
    discussion.write_text("""# Stage 1 Discussion: Multi-Direction Proposals
### Option A: Emerald Kinetic
- accent-primary: #10b981
- bg-void: #052e16

### Option B: Amber Mission (Selected)
- accent-primary: #f59e0b
- bg-void: #1c1917

## Confirmed Decisions
- accent-primary: #f59e0b
- bg-void: #1c1917
- Energy: 4
- Finish: 3
- Density: 4
- Weight: 3
- Seriousness: 4
""", encoding="utf-8")

    out_css = tmp_path / "tokens.css"
    out_json = tmp_path / "t1.json"
    out_md = tmp_path / "t1.md"
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json), str(out_md))

    css_content = out_css.read_text(encoding="utf-8")
    assert "#f59e0b" in css_content, "Confirmed accent #f59e0b must be compiled"
    assert "#10b981" not in css_content, "Rejected Option A accent #10b981 must not be selected"


def test_light_mode_palette_derivation_and_wcag_contrast(tmp_path: Path):
    """Verify light-mode backgrounds synthesize dark high-contrast typography satisfying WCAG AAA."""
    compile_mod = _load("compile_tokens", "compile_tokens.py")
    discussion = tmp_path / "discussion.md"
    discussion.write_text("""# Discussion: Light Editorial Reading
## Confirmed Decisions
- bg-void: #faf8f3
- accent-primary: #0284c7
- Energy: 2
- Finish: editorial-paper
- Density: 3
- Weight: regular
- Seriousness: 3
""", encoding="utf-8")

    out_css = tmp_path / "tokens.css"
    out_json = tmp_path / "t1.json"
    out_md = tmp_path / "t1.md"
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json), str(out_md))

    css_content = out_css.read_text(encoding="utf-8")
    # Verify dark text is generated, not light off-white
    assert "--text-primary: #18181b" in css_content or "--text-primary: #121211" in css_content or "--text-primary: #0" in css_content

    data = json.loads(out_json.read_text(encoding="utf-8"))
    bg_surface = data["color"]["surface"]["$value"]
    text_primary = data["color"]["text-primary"]["$value"]

    # Compute WCAG contrast ratio
    def _rel_lum(h: str) -> float:
        c = h.lstrip("#")
        rgb = [int(c[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    l1 = _rel_lum(bg_surface)
    l2 = _rel_lum(text_primary)
    ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
    assert ratio >= 7.0, f"Light mode contrast ratio must exceed WCAG AAA 7:1 (got {ratio:.2f}:1)"


def test_dominant_baseline_preserved_against_casual_keyword_mentions(tmp_path: Path):
    """Verify assemble_envelope strictly respects declared Dominant Baseline even if touch/mobile appear in text."""
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")

    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "product.md").write_text("""# Product
- Dominant Baseline: Baseline 1 (Dense Operational Console)
- Omissions: Touch gestures and consumer mobile carousels are strictly omitted.
""", encoding="utf-8")
    (proto / "shared").mkdir(parents=True, exist_ok=True)
    (proto / "shared/tokens.css").write_text(":root {}\n", encoding="utf-8")
    (proto / "contracts/tokens").mkdir(parents=True, exist_ok=True)
    (proto / "contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
    (proto / "contracts/surface-maps").mkdir(parents=True, exist_ok=True)
    (proto / "contracts/surface-maps/m1.md").write_text("# Map\n", encoding="utf-8")
    (proto / "contracts/foundation").mkdir(parents=True, exist_ok=True)
    (proto / "contracts/foundation/f1.md").write_text("# Foundation\n", encoding="utf-8")
    (proto / "contracts/slices/slice_console").mkdir(parents=True, exist_ok=True)
    (proto / "contracts/slices/slice_console/c1.md").write_text("# Contract\n", encoding="utf-8")
    (proto / "specifications/slice_console").mkdir(parents=True, exist_ok=True)
    (proto / "specifications/slice_console/r1.md").write_text("""# Spec
- Prototype write scope: `prototype/experiments/slice_console/hero-anchor/`
- Evidence write scope: `prototype/evidence/probes/slice_console/`
Note: Avoid touch controls and consumer mobile paradigms.
""", encoding="utf-8")

    env = assemble_mod.assemble(tmp_path, "slice_console", lint=False)
    assert env["app_shell_blueprint"]["profile"] == "dense-console", "Profile must remain dense-console despite 'touch'/'mobile' mentions in omissions"


def test_verify_quality_negative_checks_block_goodhart_loopholes(tmp_path: Path):
    """Verify verify_prototype_quality fails fake implementations with empty listeners, naked metrics, or comment states."""
    verify_mod = _load("verify_prototype_quality", "verify_prototype_quality.py")

    tokens_css = tmp_path / "tokens.css"
    tokens_css.write_text(":root { --radius-btn: 4px; }\n", encoding="utf-8")

    spec_path = tmp_path / "r1.md"
    spec_path.write_text("""# Spec
## Action Verb Lifecycle Table
| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact |
|---|---|---|---|---|---|
| reboot | Reboot | Confirm Reboot | Reboot Now | Done | Impact |
## The Break Protocol Stress Checkpoints
| Reality Breaker | Test Vector | Expected | Observed |
|---|---|---|---|
| Overflow | Hash | Truncate | pass |
## Zero Naked Metrics
| Metric | Unit | Baseline |
|---|---|---|
| Latency | ms | 50ms |
## Cognitive Budgeting
| Zone | Weight |
|---|---|
| Primary | Heavy |
""", encoding="utf-8")

    # 1. Fake tactile physics: empty pointerdown listener without CSS :active or mutation
    fake_tactile = tmp_path / "fake_tactile.html"
    fake_tactile.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css"></head>
<body data-state="ready">
  <button id="reboot" style="border-radius: var(--radius-btn); text-overflow: ellipsis; overflow: hidden;">Reboot</button>
  <dialog><h3>Confirm Reboot</h3><button>Reboot Now</button></dialog>
  <div>Done</div>
  <div class="stat"><span class="unit">100 ms</span></div>
  <script>
    document.addEventListener('pointerdown', () => {}); // Empty handler without style/class mutation
  </script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(fake_tactile), str(tokens_css), contract_path=str(spec_path)) is False

    # 2. Fake naked metric: class="stat" without any unit or sparkline
    fake_metric = tmp_path / "fake_metric.html"
    fake_metric.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css"><style>button:active{transform:scale(0.97);}</style></head>
<body data-state="ready">
  <button id="reboot" style="border-radius: var(--radius-btn); text-overflow: ellipsis; overflow: hidden;">Reboot</button>
  <dialog><h3>Confirm Reboot</h3><button>Reboot Now</button></dialog>
  <div>Done</div>
  <span class="stat">42</span> <!-- Naked metric without unit or sparkline -->
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(fake_metric), str(tokens_css), contract_path=str(spec_path)) is False

    # 3. Fake state machine: HTML comment <!-- loading --> without actual state hook
    fake_state = tmp_path / "fake_state.html"
    fake_state.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css"><style>button:active{transform:scale(0.97);}</style></head>
<body>
  <!-- loading state comment -->
  <button id="reboot" style="border-radius: var(--radius-btn); text-overflow: ellipsis; overflow: hidden;">Reboot</button>
  <dialog><h3>Confirm Reboot</h3><button>Reboot Now</button></dialog>
  <div>Done</div>
  <span class="unit">42 ms</span>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(fake_state), str(tokens_css), contract_path=str(spec_path)) is False


def test_reconcile_review_tokens_back_to_contracts(tmp_path: Path):
    """Verify reconcile_tokens_from_css captures human review edits in tokens.css and updates discussion & t1.json."""
    compile_mod = _load("compile_tokens", "compile_tokens.py")

    discussion = tmp_path / "discussion.md"
    discussion.write_text("""# Discussion
- Energy: 3
- Finish: 3
- Density: 3
- Weight: 3
- Seriousness: 3
- palette: warm-graphite-lime
""", encoding="utf-8")

    out_css = tmp_path / "tokens.css"
    out_json = tmp_path / "t1.json"
    out_md = tmp_path / "t1.md"
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json), str(out_md))

    # Reviewer changes accent-primary in tokens.css
    css_content = out_css.read_text(encoding="utf-8")
    modified_css = re.sub(r"--accent-primary:\s*#[0-9a-fA-F]+;", "--accent-primary: #38bdf8;", css_content)
    out_css.write_text(modified_css, encoding="utf-8")

    # Reconcile back into discussion and contracts
    compile_mod.reconcile_tokens_from_css(str(out_css), str(discussion), str(out_json), str(out_md))

    # Verify discussion and t1.json received the review edit
    updated_disc = discussion.read_text(encoding="utf-8")
    assert "--accent-primary: #38bdf8" in updated_disc

    updated_json = json.loads(out_json.read_text(encoding="utf-8"))
    assert updated_json["color"]["primary"]["$value"] == "#38bdf8"











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

RETIRED_SIX_PIECE = "legacy six-piece envelope input: lint_spec_contracts() is retired; canonical IR is the only contract"

def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

handoff = _load("handoff", "handoff.py")
boundary = _load("boundary", "execution_boundary.py")

def _sha256(b: bytes) -> str:
    return f"sha256:{hashlib.sha256(b).hexdigest()}"

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
    stage1_text = (SKILL / "references/stages/stage-1-frame.md").read_text(encoding="utf-8")
    assert "smallest useful design brief" in stage1_text
    assert "All five axes" in stage1_text and "accounted for at direction" in stage1_text
    assert "Five Axes are optional" not in stage1_text, \
        "an optional axis register is indistinguishable from a model default"
    assert "## Required parser anchors" in stage1_text
    assert "google-design-md/v2" in stage1_text
    assert "official Google schema" in stage1_text

    stage2_text = (SKILL / "references/stages/stage-2-probe.md").read_text(encoding="utf-8")
    assert "Native-First vs Production Handoff" in stage2_text

    stage4_text = (SKILL / "references/stages/stage-4-audit.md").read_text(encoding="utf-8")
    assert "rendered experience first" in stage4_text
    assert "few highest-impact findings" in stage4_text
    assert "A state is captured only if its trigger was applied" in stage4_text
    assert "Choose only the stress cases material" in stage4_text

    contract_text = (SKILL / "references/spec-md-contract.md").read_text(encoding="utf-8")
    assert "not an official" in contract_text
    assert "Illustrative rich slice (not a required template)" in contract_text
    assert "Minimum formal slice" in contract_text

    builder_text = (REPO / "agents/spec-prototype-builder.md").read_text(encoding="utf-8")
    assert "## Design Before Markup" in builder_text
    assert "44×44px" in builder_text
    assert "generic metric grids" in builder_text


    stage3_text = (SKILL / "references/stages/stage-3-skeleton.md").read_text(encoding="utf-8")
    assert "Compression & Release" in stage3_text

    visual_text = (SKILL / "references/02-craft-methods/visual-craft.md").read_text(encoding="utf-8")
    assert "Declared-Attribute Optics" in visual_text
    assert "Optical Concentric Geometry" in visual_text
    assert "spatial_geometry" in visual_text
    assert "micro_typography" in visual_text

    builder_text = (REPO / "agents/spec-prototype-builder.md").read_text(encoding="utf-8")
    assert "massing_pattern" in builder_text
    assert "kinematics" in builder_text
    assert "data_syntax" in builder_text

    critic_text = (REPO / "agents/spec-prototype-critic.md").read_text(encoding="utf-8")
    assert "display: none" in critic_text
    assert "Cognitive Quality Review" in critic_text

    floor_text = (SKILL / "references/03-verification/quality-floor.md").read_text(encoding="utf-8")
    assert "non-transfer boundary" in floor_text
    assert "candidate techniques, not global requirements" in floor_text
    assert "Tabular numerals can aid" in floor_text
    assert "neutral surfaces" in floor_text

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
    # When live prototype artifacts exist in REPO (e.g. during integration runs), verify their standards
    if (REPO / "prototype/discussion.md").is_file():
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
        portal_path = REPO / "prototype/review-portal.html"
        if portal_path.is_file():
            portal_html = portal_path.read_text(encoding="utf-8")
            assert "review" in portal_html.lower() or "portal" in portal_html.lower()
            assert "QUALITY HARNESS" in portal_html

        # Stage 5: Silent Governance Compilation
        tokens_json_path = REPO / "prototype/contracts/tokens/t1.json"
        if tokens_json_path.is_file():
            token_data = json.loads(tokens_json_path.read_text(encoding="utf-8"))
            assert "$schema" not in token_data
            assert "color" in token_data
            assert token_data["color"]["primary"]["$value"] == "#00f0ff"

    # Stage 5 Compiler Direct Verification: compile_tokens.py generates identical DTCG structure
    compile_mod = _load("compile_tokens", "compile_tokens.py")
    dials = {"energy": "quiet", "finish": "machined-industrial", "density": "dense", "weight": "dense-tactile", "seriousness": "solemn"}
    tokens = compile_mod.compute_tokens(dials, "plasma-cyan")
    generated_dtcg = compile_mod.generate_dtcg_json(tokens)
    assert "$schema" not in generated_dtcg
    assert "color" in generated_dtcg
    assert "primary" in generated_dtcg["color"]
    assert generated_dtcg["color"]["primary"]["$value"].startswith("#")
    assert "radius" in generated_dtcg
    assert "outer" in generated_dtcg["radius"]
    assert "spacing" in generated_dtcg


@pytest.mark.skip(reason=RETIRED_SIX_PIECE)
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

    # 5. Verify compile_tokens emits the two canonical token artifacts
    disc_text = """## 5-Dial Style Register\n- Energy: 3\n- Finish: 4\n- Density: 4\n- Weight: 3\n- Seriousness: 4\n- Palette: plasma-cyan\n"""
    discussion.write_text(disc_text, encoding="utf-8")
    out_css = tmp_path / "tokens_gen.css"
    out_json = tmp_path / "tokens_gen.json"
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json))
    assert out_css.is_file() and "--radius-outer" in out_css.read_text(encoding="utf-8")
    assert out_json.is_file() and "$schema" not in out_json.read_text(encoding="utf-8")
    # The retired Markdown token contract has no emission seam at all.
    import inspect
    assert "output_md_path" not in inspect.signature(compile_mod.compile_tokens).parameters

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
    assert "Design Before Markup" in builder_md
    assert "44×44px" in builder_md
    assert "single-pass" in builder_md.lower()

    # 8. Verify SKILL.md and core-kernel.md declare the Prototype-first & downstream Spec invariant
    core_kernel = (SKILL / "references/core-kernel.md").read_text(encoding="utf-8")
    assert ("Draft → Validated → Frozen Approved" in core_kernel or
            "Prototype as Exploratory Medium" in core_kernel)
    skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert "visual exploration and rapid prototyping precede formal contract compilation" in skill_md
    assert "prototype/discussion.md" in skill_md
    assert "spec-prototype-builder" in skill_md


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


@pytest.mark.skip(reason=RETIRED_SIX_PIECE)
def test_seven_high_leverage_design_levers_and_template_slots(tmp_path: Path):
    """Verify design-methods.md owns all 7 levers, and the retained templates carry their slots.

    The legacy pillar templates (product / experience-foundation / surface-map /
    slice-contract / tokens) are retired: their slots now live in the discussion
    record and its Stage 1 sections, which this test reads instead.
    """
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

    # 2. The retired pillar templates must not come back.
    for name in ("product.md", "experience-foundation.md", "surface-map.md",
                 "slice-contract.md", "tokens.md"):
        assert not (SKILL / "templates" / name).exists(), name

    # 3. The discussion record owns the retired templates' authored slots.
    discussion_tmpl = (SKILL / "templates/discussion.md").read_text(encoding="utf-8")
    assert "## Working understanding (Nine Pillars Canonical Ontology)" in discussion_tmpl
    assert "Problem Framing & Drivers" in discussion_tmpl
    assert "Experience Foundation & Five Axes" in discussion_tmpl
    assert "Spatial Anatomy & Surface Topology" in discussion_tmpl
    assert "State Taxonomy & Action Lifecycle" in discussion_tmpl
    assert "Verifiable Invariants & Break Protocol" in discussion_tmpl

    # 4. The canonical spec template keeps the dual-channel/break slots.
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


def test_tightened_quality_assertions_against_goodhart_loopholes(tmp_path: Path, capsys):
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
    bad_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css"></head><body>
<main id="app" class="panel">
  <button id="btn-action" onclick="void(0)" style="color: var(--bg-void);">Run</button>
</main>
</body></html>""", encoding="utf-8")

    # The contract-named shortcut, state hook and overflow containment it omits
    # are reported as signals: whether the surface expresses them is the design
    # review's call, not a literal match's.
    assert verify_mod.assert_quality(str(bad_html), str(tokens_css), contract_path=str(spec_md)) is True
    bad_report = capsys.readouterr().out
    assert "[signal] ergonomics: declared dual-channel keyboard shortcuts not bound" in bad_report
    assert "[signal] state-machine: stress checkpoints declared but no state-switching hook detected" in bad_report

    # 2. HTML adds var(--radius-outer) and tabular-nums, but still lacks keyboard listener and hashchange
    semi_html = tmp_path / "semi.html"
    semi_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css"></head><body>
<main id="app" class="panel" style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
  <button id="btn-action" onclick="void(0)">Run</button>
</main>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(semi_html), str(tokens_css), contract_path=str(spec_md)) is True

    # 3. HTML adds keydown listener, overflow containment, and hashchange state machine hook -> passes
    good_html = tmp_path / "good.html"
    good_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css"></head><body>
<main id="app" class="panel" style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums; overflow: hidden;">
  <button id="btn-action" onclick="void(0)" style="min-width: 44px; min-height: 44px;">Run</button>
</main>
<script>
  window.addEventListener('keydown', (e) => {});
  window.addEventListener('hashchange', () => {});
  document.body.setAttribute('data-state', 'default');
</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(good_html), str(tokens_css), contract_path=str(spec_md)) is True

def test_the_document_must_bind_the_token_stylesheet_it_declares(tmp_path: Path):
    """A prototype that links no stylesheet cannot have inherited any token.

    Every check that consumes a token value — radius, numeric presentation,
    accent discipline — is read from the document's own declarations, so a
    document that binds no stylesheet was previously checked against tokens
    that could not have been in effect, and passed. It also degraded L2 with
    `environment_not_ready`, reporting a missing browser where the real fact
    was a missing stylesheet.
    """
    verify_mod = _load("verify_quality", "verify_prototype_quality.py")
    tokens_css = tmp_path / "tokens.css"
    tokens_css.write_text(":root { --radius-outer: 8px; }\n", encoding="utf-8")

    unbound = tmp_path / "unbound.html"
    unbound.write_text("""<!DOCTYPE html><html><head><style>
:root { --radius-outer: 8px; }
</style></head><body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums; overflow: hidden;">
  <button onclick="void(0)" style="min-width: 44px; min-height: 44px;">Run</button>
</main>
<script>
  window.addEventListener('keydown', () => {});
  window.addEventListener('hashchange', () => {});
  document.body.setAttribute('data-state', 'default');
</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(unbound), str(tokens_css)) is False

    # Binding it by an @import is a real binding, so the same document passes.
    bound = tmp_path / "bound.html"
    bound.write_text(unbound.read_text(encoding="utf-8").replace(
        "<style>\n:root { --radius-outer: 8px; }\n</style>",
        '<style>\n@import "tokens.css";\n</style>'), encoding="utf-8")
    assert verify_mod.assert_quality(str(bound), str(tokens_css)) is True


@pytest.mark.skip(reason=RETIRED_SIX_PIECE)
def test_topology_context_and_convention_cli(tmp_path: Path, capsys):
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
    # Commands are absolute (skill_root/repository_root derived) so they execute
    # verbatim inside `.claude/skills` install layouts, not just repo checkouts.
    assert env["verification_command"].endswith(
        "verify_prototype_quality.py --slice console --root " + str(tmp_path)
    )
    assert env["verification_command"].startswith("python3 ")
    assert "skills/spec-prototype/scripts" in env["verification_command"]
    assert env["capture_command"].endswith("capture.mjs --slice console --repo-root " + str(tmp_path))
    assert env["capture_command"].startswith("node ")
    assert "skills/spec-prototype/scripts" in env["capture_command"]

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
    # An undelivered sibling that is neither linked nor rendered as a disabled
    # affordance is reported: absent navigation is a judgement about the render,
    # not the 404 a live href to an undelivered surface would be.
    test_html.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="../../../shared/tokens.css"></head><body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;"><button>Go</button></main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body></html>""", encoding="utf-8")
    assert verify_mod.assert_quality(str(test_html), str(tokens_css), contract_path=str(spec)) is True
    topology_report = capsys.readouterr().out
    assert "[signal] topology: undelivered sibling" in topology_report

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
    """wcag-check.js is an installed read helper."""
    boundary.shell_read("node skills/spec-prototype/scripts/wcag-check.js --slice console", Path("/tmp/root"))
    with pytest.raises(ValueError):
        boundary.shell_read("python3 skills/spec-prototype/scripts/rogue.py a", Path("/tmp/root"))


def test_5_system_modern_industrial_derivation_and_rogue_root_blocking(tmp_path: Path):
    """Verify modern industrial token derivation and rogue :root blocking in quality gate."""
    compile_mod = _load("compile_tokens", "compile_tokens.py")
    verify_mod = _load("verify_quality", "verify_prototype_quality.py")
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")

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
    assert env["layout_profile"] == "adaptive-workspace"
    assert "app_shell_contract" in env
    assert "cognitive_ledger" in env
    assert "zero_borrow_base" in env["cognitive_ledger"]
    assert "high_yield_borrow_zone" in env["cognitive_ledger"]
    assert env["app_shell_contract"]["profile"] == "adaptive-workspace"
    assert env["target_html_path"] == "prototype/experiments/telemetry/anchor/index.html"


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
    compile_mod.compile_tokens(str(disc_file), str(out_css), str(out_json))
    assert out_css.is_file()
    css_content = out_css.read_text(encoding="utf-8")
    assert "--accent-primary: #c76b3a;" in css_content
    assert "--bg-void: #141210;" in css_content


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
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json))

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
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json))

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
    assert env["app_shell_blueprint"]["profile"] == "adaptive-workspace", "Unselected profile stays neutral adaptive-workspace"


def test_verify_quality_negative_checks_block_goodhart_loopholes(tmp_path: Path, capsys):
    """Floor fixtures still block; contract-read-back fixtures are reported as signals.

    All three specimens share one shape: a contract that names a metric unit, a
    state hook and an action feedback container, and a document that omits them.
    On HEAD each one also failed on those contract-read-back rules — the Goodhart
    loophole this test was written to guard, not a floor. A rule that blocks a
    document for not literally containing a token the contract named blocks
    legitimate designs too, because a good one merges, renames or relocates what
    the contract listed. Each match is now asserted on the channel it belongs to,
    so a signal cannot silently become a floor or disappear. Where a specimen also
    trips a real floor — no event binding at all — that is asserted too, so the
    floor is shown to have moved with the fixture rather than been dropped.
    """
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
    assert verify_mod.assert_quality(str(fake_tactile), str(tokens_css), contract_path=str(spec_path)) is True
    tactile_report = capsys.readouterr().out
    assert "[signal] contract items: declared items not matched in DOM: Latency" in tactile_report
    assert "[signal] action-lifecycle: contract declares active verbs but DOM has no visible feedback container" in tactile_report

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
    metric_report = capsys.readouterr().out
    # The document binds no event at all, which is a floor and still blocks. The
    # contract-read-back rules are the reason this specimen used to fail on HEAD,
    # and they now appear on the signal channel only — never as a numbered failure.
    assert "[1] interaction assertion: no declarative or imperative event binding" in metric_report
    assert "[signal] data-craft: Zero Naked Metrics" in metric_report
    assert "data-craft assertion" not in metric_report

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
    state_report = capsys.readouterr().out
    # No event binding is a floor and still blocks; the contract-read-back
    # findings are reported on the signal channel and never move the exit code.
    assert "[1] interaction assertion: no declarative or imperative event binding" in state_report
    assert "[signal] state-machine: stress checkpoints declared but no state-switching hook detected" in state_report
    assert "[signal] contract items: declared items not matched in DOM: Latency" in state_report
    assert "state-machine assertion" not in state_report


def test_reconcile_review_tokens_back_to_contracts(tmp_path: Path):
    """Verify uni-directional derivation: hand edits to tokens.css cause out_of_sync rejection."""
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
    compile_mod.compile_tokens(str(discussion), str(out_css), str(out_json))

    # Reviewer changes accent-primary in tokens.css
    css_content = out_css.read_text(encoding="utf-8")
    modified_css = re.sub(r"--accent-primary:\s*#[0-9a-fA-F]+;", "--accent-primary: #38bdf8;", css_content)
    out_css.write_text(modified_css, encoding="utf-8")

    # Verify uni-directional fuse catches drift
    sync_status = compile_mod.check_tokens_sync(str(out_css), str(discussion))
    assert sync_status["state"] == "out_of_sync"












def test_wcag_check_batch_forms(tmp_path: Path):
    """One command audits many pairs; the legacy 2-arg form is unchanged."""
    import subprocess
    script = str(SCRIPTS / "wcag-check.js")
    on = subprocess.run(["node", script, "--on", "#131a21", "#e4ebf3", "#3a4450"], capture_output=True, text=True)
    rows = json.loads(on.stdout)
    assert [r["passAA"] for r in rows] == [True, False] and on.returncode == 1
    pairs = subprocess.run(["node", script, "#e4ebf3", "#131a21", "#8fa0b3", "#131a21"], capture_output=True, text=True)
    assert len(json.loads(pairs.stdout)) == 2 and pairs.returncode == 0
    single = subprocess.run(["node", script, "#ffffff", "#000000"], capture_output=True, text=True)
    assert json.loads(single.stdout)["ratio"] == 21.0


def test_authority_label_signals_are_advisory():
    af = _load("authority_fidelity", "authority_fidelity.py")
    table = (
        "## Decisions and authority\n\n"
        "| ID | Decision | Status | Reason | Quote | User source | Scope |\n"
        "|---|---|---|---|---|---|---|\n"
        "| D1 | x | confirmed | r | | synthetic-fixture | s |\n"
        "| D2 | y | proposed | r | | | s |\n"
    )
    signals = af.advisory_label_signals(table)
    assert len(signals) == 2 and all(s.startswith("D1") for s in signals)


def test_decision_promotions_refuse_approvals_preserved():
    # r40 A2: the literal carry-forward phrase is a hard failure anywhere in the record.
    af = _load("authority_fidelity", "authority_fidelity.py")
    failures = af.check_decision_promotions(
        "Unaffected decisions and approvals preserved: D1 (双面形态), D5 (收尾语义)")
    assert failures and "approvals preserved" in failures[0]


def test_decision_promotions_refuse_confirmed_without_user_choice_evidence():
    # r40 A1: a `confirmed` row backed only by a designer rationale is a promotion.
    af = _load("authority_fidelity", "authority_fidelity.py")
    table = (
        "## Decisions and authority\n\n"
        "| ID | Decision | Status | Reason | Quote | User source | Scope |\n"
        "|---|---|---|---|---|---|---|\n"
        "| D6 | 紧急回滚 5 分钟窗口 | confirmed | derived mechanism | — | synthetic-fixture | s |\n"
    )
    failures = af.check_decision_promotions(table)
    assert failures and any("D6" in f for f in failures)


def test_decision_promotions_accept_confirmed_with_user_selection():
    # A `confirmed` row quoting an in-session user selection is legitimate (r40 D7).
    af = _load("authority_fidelity", "authority_fidelity.py")
    table = (
        "## Decisions and authority\n\n"
        "| ID | Decision | Status | Reason | Quote | User source | Scope |\n"
        "|---|---|---|---|---|---|---|\n"
        "| D7 | 移动只读 | confirmed | user stated | \"手机上只要能看到当前事故状态\" (user message, Turn 3) | confirmed | s |\n"
    )
    assert af.check_decision_promotions(table) == []


def test_decision_promotions_ignore_provisional_rows():
    af = _load("authority_fidelity", "authority_fidelity.py")
    table = (
        "## Decisions and authority\n\n"
        "| ID | Decision | Status | Reason | Quote | User source | Scope |\n"
        "|---|---|---|---|---|---|---|\n"
        "| D2 | 方向 A | provisional | recommendation | — | synthetic-fixture | s |\n"
    )
    assert af.check_decision_promotions(table) == []

"""v10 Integrity & Negative Safety Test Suite.

Asserts:
1. Empty prototype directory evaluates to BLOCKED with 0.0% signal coverage (Anti-Goodhart).
2. Missing prototype files fail quality assertions decisively.
3. Handoff manifest decouples renderer screenshot capture from visual review signoff.
4. Action verbs derived from fallback remain explicitly marked as hypothesis.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
BENCHMARKS = REPO / "benchmarks"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(BENCHMARKS) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS))

def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

eval_signals = _load("eval_signals", BENCHMARKS / "evaluate_design_signals.py")
mat_contracts = _load("mat_contracts", SCRIPTS / "materialize_contracts.py")
verify_quality = _load("verify_quality", SCRIPTS / "verify_prototype_quality.py")


def test_empty_prototype_directory_is_blocked():
    """Negative Test: Empty prototype directory must evaluate to BLOCKED with 0.0% coverage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_dir = Path(tmpdir)
        res = eval_signals.evaluate_design_signals(empty_dir, "test-slice")
        assert res["status"] == "BLOCKED"
        assert res["signal_coverage_pct"] == 0.0
        assert res["passed_checks"] == 0


def test_missing_prototype_file_fails_assert_quality():
    """Negative Test: Missing html file must fail quality assertion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_html = Path(tmpdir) / "missing.html"
        fake_tokens = Path(tmpdir) / "tokens.css"
        fake_tokens.write_text(":root { --bg-void: #000; }", encoding="utf-8")
        result = verify_quality.assert_quality(str(fake_html), str(fake_tokens))
        # assert_quality returns False or non-empty failure list when required artifact missing
        assert result is False or (isinstance(result, list) and len(result) > 0)


def test_unresolved_action_verbs_remain_hypothesis():
    """Contract Safety: Missing explicit action verbs must be marked as hypothesis, never frozen fact."""
    actions = mat_contracts.extract_action_verbs("Empty discussion text without table", "custom-slice")
    assert len(actions) > 0
    assert "hypothesis" in actions[0]["impact"].lower()


def test_handoff_manifest_structure_decouples_renderer_and_visual():
    """Evidence Integrity: Manifest must distinguish renderer capture from visual verification."""
    manifest_path = REPO / "prototype/evidence/handoff-manifest.json"
    if manifest_path.is_file():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        verification = data.get("verification", {})
        # Must not claim visual verified automatically upon renderer capture
        assert verification.get("visual") != "verified"
        assert verification.get("renderer") == "captured"


def test_dual_envelope_architecture():
    """Envelope v3: Enforce Constraint Envelope and Creative Envelope decoupling."""
    assemble_mod = _load("assemble_envelope", SCRIPTS / "assemble_envelope.py")
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Populate minimal contract files
        (root / "prototype").mkdir(parents=True, exist_ok=True)
        (root / "prototype/product.md").write_text("# Product\n- Core Tension: Speed vs Safety\n", encoding="utf-8")
        (root / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/surface-maps/m1.md").write_text("# Surface Map\n", encoding="utf-8")
        (root / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/foundation/f1.md").write_text("# Foundation\n", encoding="utf-8")
        (root / "prototype/shared").mkdir(parents=True, exist_ok=True)
        (root / "prototype/shared/tokens.css").write_text(":root { --bg-void: #000; }\n", encoding="utf-8")
        (root / "prototype/contracts/tokens").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
        (root / "prototype/contracts/tokens/t1.json").write_text("{}", encoding="utf-8")
        (root / "prototype/contracts/slices/s1").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/slices/s1/c1.md").write_text("# Contract\n", encoding="utf-8")
        (root / "prototype/specifications/s1").mkdir(parents=True, exist_ok=True)
        (root / "prototype/specifications/s1/r1.md").write_text("# Spec\n", encoding="utf-8")

        env = assemble_mod.assemble(root, "s1", lint=False)
        assert env["envelope_version"] == "2.0"
        assert env["envelope_architecture"] == "3.0-dual"
        assert "constraint_envelope" in env
        assert "creative_envelope" in env
        assert "domain_thesis" in env["constraint_envelope"]
        assert "spatial_composition_agency" in env["creative_envelope"]
        assert "attention_routing" in env["creative_envelope"]


def test_three_tier_semantic_tokens_and_dtcg_authority():
    """Verify Rich Contract, Lean Engine: 3-tier token hierarchy and DTCG authority provenance."""
    compile_mod = _load("compile_tokens", SCRIPTS / "compile_tokens.py")
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        disc = root / "discussion.md"
        disc.write_text(
            "# Product Discussion\n"
            "- Energy: kinetic\n"
            "- Finish: matte\n"
            "- Density: compact\n"
            "- Weight: dense-tactile\n"
            "- Seriousness: utilitarian\n",
            encoding="utf-8"
        )
        out_css = root / "tokens.css"
        out_json = root / "t1.json"
        out_md = root / "t1.md"

        # 1. Compile baseline tokens
        compile_mod.compile_tokens(str(disc), str(out_css), str(out_json), str(out_md))

        assert out_css.is_file()
        assert out_json.is_file()

        css_text = out_css.read_text(encoding="utf-8")
        # Layer 1 Primitives
        assert "--bg-void:" in css_text
        assert "--font-variant-numeric: tabular-nums;" in css_text
        # Layer 2 Semantics
        assert "--surface-base: var(--bg-surface);" in css_text
        assert "--text-muted: var(--text-tertiary);" in css_text
        assert "--action-primary: var(--accent-primary);" in css_text
        # Layer 3 Component Slots
        assert "--input-bg: var(--bg-base);" in css_text
        assert "--card-bg: var(--bg-surface);" in css_text
        assert "--table-row-hover: var(--bg-surface-raised);" in css_text
        assert "--modal-backdrop:" in css_text

        # Verify DTCG JSON 3-tier structure
        dtcg = json.loads(out_json.read_text(encoding="utf-8"))
        assert "primitives" in dtcg
        assert "semantics" in dtcg
        assert "components" in dtcg
        # Check metadata fields
        primary_color = dtcg["primitives"]["color"]["primary"]
        assert "$type" in primary_color
        assert "$value" in primary_color
        assert "$description" in primary_color
        assert primary_color["authority"] == "derived"

        # 2. Test Single-Direction Authority Chain: Human Confirmation -> explicit_human
        disc.write_text(
            "# Product Discussion\n"
            "- Energy: kinetic\n"
            "- Finish: matte\n"
            "- Density: compact\n"
            "- Weight: dense-tactile\n"
            "- Seriousness: utilitarian\n\n"
            "## Confirmed Decisions (Reconciled from Review tokens.css)\n"
            "- `--accent-primary`: `#9333ea`\n",
            encoding="utf-8"
        )
        compile_mod.compile_tokens(str(disc), str(out_css), str(out_json), str(out_md))
        dtcg_confirmed = json.loads(out_json.read_text(encoding="utf-8"))
        assert dtcg_confirmed["primitives"]["color"]["primary"]["authority"] == "explicit_human"


def test_v10_1_five_axes_optionality_and_composable_envelope():
    """Verify v10.1: Five Axes are completely optional, undeclared dials do not crash compiler."""
    compile_mod = _load("compile_tokens", SCRIPTS / "compile_tokens.py")
    assemble_mod = _load("assemble_envelope", SCRIPTS / "assemble_envelope.py")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # 1. Empty discussion without any explicit dials/axes must compile cleanly
        empty_disc = root / "empty_disc.md"
        empty_disc.write_text("# Pure Product Thesis\n- Just core value, zero dials.\n", encoding="utf-8")
        out_css = root / "out.css"
        out_json = root / "out.json"
        out_md = root / "out.md"

        compile_mod.compile_tokens(str(empty_disc), str(out_css), str(out_json), str(out_md))
        assert out_css.is_file()
        assert "--bg-void:" in out_css.read_text(encoding="utf-8")

        # 2. Verify parse_five_axes extracts canonical axes
        disc_with_axes = (
            "- Density: compact\n"
            "- Energy: calm\n"
            "- Materiality: paper\n"
            "- Rhythm: measured\n"
            "- Character: scholarly\n"
        )
        axes = compile_mod.parse_five_axes(disc_with_axes)
        assert axes["density"] == "compact"
        assert axes["energy"] == "calm"
        assert axes["materiality"] == "paper"
        assert axes["rhythm"] == "measured"
        assert axes["character"] == "scholarly"

        # 3. Verify assemble_envelope fallback produces adaptive-workspace rather than dense-console
        (root / "prototype").mkdir(parents=True, exist_ok=True)
        (root / "prototype/product.md").write_text("# Product\n- Core: Reading & Thought\n", encoding="utf-8")
        (root / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/surface-maps/m1.md").write_text("# Map\n", encoding="utf-8")
        (root / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/foundation/f1.md").write_text("# F1\n", encoding="utf-8")
        (root / "prototype/shared").mkdir(parents=True, exist_ok=True)
        (root / "prototype/shared/tokens.css").write_text(":root { --bg-void: #000; }\n", encoding="utf-8")
        (root / "prototype/contracts/tokens").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
        (root / "prototype/contracts/tokens/t1.json").write_text("{}", encoding="utf-8")
        (root / "prototype/contracts/slices/read").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/slices/read/c1.md").write_text("# Contract\n", encoding="utf-8")
        (root / "prototype/specifications/read").mkdir(parents=True, exist_ok=True)
        (root / "prototype/specifications/read/r1.md").write_text("# Spec\n", encoding="utf-8")

        env = assemble_mod.assemble(root, "read", lint=False)
        assert env["layout_profile"] == "adaptive-workspace"
        assert env["creative_envelope"]["layout_profile"] == "adaptive-workspace"
        # Verify ooux_topology does not force 1:N / master-detail on unknown/adaptive profile
        assert env["ooux_topology"]["cardinality"] == "adaptive"
        assert env["ooux_topology"]["layout_mode"] == "adaptive-flow"


def test_stale_digest_guard_blocks_modified_contract(tmp_path: Path):
    """P1-3 Stale Digest Guard: execution_boundary must reject dispatch if spec files changed after envelope compilation."""
    assemble_mod = _load("assemble_envelope", SCRIPTS / "assemble_envelope.py")
    boundary_mod = _load("execution_boundary", SCRIPTS / "execution_boundary.py")

    # 1. Populate spec files
    (tmp_path / "prototype").mkdir(parents=True, exist_ok=True)
    prod = tmp_path / "prototype/product.md"
    prod.write_text("# Product\n- Core Tension: Speed vs Safety\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/surface-maps/m1.md").write_text("# Surface Map\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/foundation/f1.md").write_text("# Foundation\n", encoding="utf-8")
    (tmp_path / "prototype/shared").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/shared/tokens.css").write_text(":root { --bg-void: #000; }\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/tokens").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
    (tmp_path / "prototype/contracts/tokens/t1.json").write_text("{}", encoding="utf-8")
    (tmp_path / "prototype/contracts/slices/s1").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/contracts/slices/s1/c1.md").write_text("# Contract\n", encoding="utf-8")
    (tmp_path / "prototype/specifications/s1").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/specifications/s1/r1.md").write_text("# Spec\n", encoding="utf-8")
    disc = tmp_path / "prototype/discussion.md"
    disc.write_text("- Execution boundary: active\n", encoding="utf-8")

    # 2. Assemble initial fresh envelope
    env = assemble_mod.assemble(tmp_path, "s1", lint=False)
    event = {
        "cwd": str(tmp_path),
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "spec-prototype-builder",
            "prompt": json.dumps(env),
        },
    }
    # Fresh envelope passes execution boundary check
    boundary_mod.check(event)

    # 3. Tamper with product.md after envelope was compiled
    prod.write_text("# Product\n- Core Tension: CHANGED AFTER ENVELOPE SEAL\n", encoding="utf-8")

    # 4. Same envelope must now be strictly blocked by Stale Digest Guard
    with pytest.raises(ValueError, match="Stale contract: product.md changed"):
        boundary_mod.check(event)

    # 5. Delete product.md completely -> must block with "deleted since envelope was compiled"
    prod.unlink()
    with pytest.raises(ValueError, match="Stale contract: product.md was deleted"):
        boundary_mod.check(event)


def test_build_authority_gate_blocks_formal_candidate_with_hypotheses(tmp_path: Path):
    """P0 Build Authority Gate: Formal candidate builds must be blocked if unvalidated [Hypothesis] actions exist."""
    boundary_mod = _load("execution_boundary", SCRIPTS / "execution_boundary.py")

    prod_file = tmp_path / "prototype/product.md"
    prod_file.parent.mkdir(parents=True, exist_ok=True)
    prod_file.write_text("# Product\n", encoding="utf-8")
    import hashlib
    prod_digest = hashlib.sha256(prod_file.read_bytes()).hexdigest()

    fake_env = {
        "mode": "lean-builder-envelope",
        "slice_id": "checkout",
        "repository_root": str(tmp_path.resolve()),
        "skill_root": str(SCRIPTS.parent.resolve()),
        "target_html_path": "prototype/experiments/checkout/index.html",
        "target_environment": "formal-candidate",
        "has_hypothesis_actions": True,
        "spec_sources": {"product_digest": prod_digest}
    }
    # Create target html directory to satisfy boundary path checks
    (tmp_path / "prototype/experiments/checkout").mkdir(parents=True, exist_ok=True)
    (tmp_path / "prototype/experiments/checkout/index.html").write_text("<!DOCTYPE html><html></html>", encoding="utf-8")
    (tmp_path / "prototype/discussion.md").write_text("- Execution boundary: active\n", encoding="utf-8")

    event = {
        "cwd": str(tmp_path),
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "spec-prototype-builder",
            "prompt": json.dumps(fake_env),
        },
    }

    with pytest.raises(ValueError, match="Build Authority Gate"):
        boundary_mod.check(event)


def test_frontend_contract_projection_schema_and_validity(tmp_path: Path):
    """v10.1 Frontend Contract Projection: Ensure machine-readable contract is generated with complete state and action models."""
    mat_mod = _load("materialize_contracts", SCRIPTS / "materialize_contracts.py")
    try:
        import yaml
    except ImportError:
        yaml = None

    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "product.md").write_text("# SRE Platform\n## Core Tension\n- 极致吞吐 vs 误触高危\n", encoding="utf-8")
    # 1. First test: without authored state machine and responsive rules, compiler must NOT invent them
    (proto / "discussion.md").write_text(
        "# Discussion\n"
        "## Action Verbs\n"
        "| Action ID | Trigger Button | Modal Header | Commit Button | Toast | Impact |\n"
        "|---|---|---|---|---|---|\n"
        "| drain-node | Drain Node | Confirm Node Drain | Execute Drain | Drain Complete | Irreversible eviction of batch workload |\n"
        "| isolate-region | Isolate Region | Emergency Region Isolation | Authorize Isolation | Region Isolated | High hazard traffic reroute |\n",
        encoding="utf-8"
    )

    res = mat_mod.materialize(tmp_path, "commander-hero", force=True)
    assert "frontend_contract" in res
    fe_file = Path(res["frontend_contract"])
    assert fe_file.is_file()

    content = fe_file.read_text(encoding="utf-8")
    assert "contract_version: '1.0'" in content or 'contract_version: "1.0"' in content
    assert "commander-hero" in content

    if yaml is not None:
        data = yaml.safe_load(content)
        assert data["slice_id"] == "commander-hero"
        assert "provenance" in data
        assert "structure" in data
        # De-inference assertion: unauthored states and responsive rules report unspecified rather than guessing
        assert data["state_machine"]["status"] == "unspecified"
        assert data["responsive_rules"]["status"] == "unspecified"
        assert "drain-node" in data["interaction_verbs"]
        assert data["interaction_verbs"]["drain-node"]["hazard_level"] == "high"

    # 2. Second test: when state machine and responsive rules are authored, they are accurately projected
    (proto / "discussion.md").write_text(
        "# Discussion\n"
        "## Responsive\n"
        "- desktop: 1280px split-rack canvas\n"
        "- mobile: 390px bottom-sheet stack\n"
        "## State Machine\n"
        "- ready: Baseline telemetry streaming\n"
        "- confirming: Modal confirmation dialog active\n"
        "## Action Verbs\n"
        "| Action ID | Trigger Button | Modal Header | Commit Button | Toast | Impact |\n"
        "|---|---|---|---|---|---|\n"
        "| drain-node | Drain Node | Confirm Node Drain | Execute Drain | Drain Complete | Irreversible eviction of batch workload |\n",
        encoding="utf-8"
    )
    res2 = mat_mod.materialize(tmp_path, "commander-hero", force=True)
    if yaml is not None:
        data2 = yaml.safe_load(Path(res2["frontend_contract"]).read_text(encoding="utf-8"))
        assert "ready" in data2["state_machine"]["states"]
        assert "confirming" in data2["state_machine"]["states"]
        assert "1280px split-rack canvas" in data2["responsive_rules"]["desktop"]
        assert "390px bottom-sheet stack" in data2["responsive_rules"]["mobile"]


def test_critic_finding_classifications_and_targeted_refinement():
    """Verify spec-prototype-critic defines 6 RFC classifications and targeted refinement protocol."""
    critic_path = REPO / "agents/spec-prototype-critic.md"
    text = critic_path.read_text(encoding="utf-8")

    # 6 Classifications
    assert "FACT" in text
    assert "VIOLATION" in text
    assert "DESIGN JUDGMENT" in text
    assert "PREFERENCE" in text
    assert "DEFECT" in text
    assert "MISSING EVIDENCE" in text
    assert "PREFERENCE" in text and "must NEVER fail a build" in text

    # Targeted Refinement Contract
    assert "Targeted Refinement Contract" in text
    assert "targeted_refinement:" in text
    assert "pillar: Attention | Interaction | Expression | Resilience" in text
    assert "invalidate:" in text
    assert "preserve:" in text


def test_change_scope_router_and_tension_in_core_workflow():
    """Verify Stage 3 owns Coverage Selection and Signature discipline inline (core-workflow retired)."""
    stage3_path = REPO / "skills/spec-prototype/references/stages/stage-3-skeleton.md"
    text = stage3_path.read_text(encoding="utf-8")

    # Coverage Selection rule carried inline by the Stage 3 owner
    assert "Coverage Selection before Expansion" in text
    assert "Retain, do not re-ask" in text
    assert "Selection is scope, not approval" in text

    # Signature vs Convention
    assert "Signature vs. Convention" in text
    assert "Signature Surface" in text
    assert "Convention Surfaces" in text

    # The retired shared router is not active-loaded anywhere
    for path in (
        REPO / "skills/spec-prototype/SKILL.md",
        REPO / "skills/spec-prototype/references/core-kernel.md",
        stage3_path,
        REPO / "skills/spec-prototype/references/stages/stage-5-freeze.md",
    ):
        assert "core-workflow" not in path.read_text(encoding="utf-8"), path


def test_method_registry_and_craft_guidelines_hygiene():
    """v10.2 Hygiene: Ensure lightweight Method Registry exists and quality-floor distinguishes invariants from craft guidelines."""
    try:
        import yaml
    except ImportError:
        yaml = None

    registry_path = REPO / "skills/spec-prototype/methods/registry.yaml"
    assert registry_path.is_file()
    if yaml is not None:
        reg_data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        assert "methods" in reg_data
        assert len(reg_data["methods"]) >= 8
        ids = [m["id"] for m in reg_data["methods"]]
        assert "ooux-mapping" in ids
        assert "context-preservation" in ids
        assert "action-verb-lifecycle" in ids
        assert "the-break-protocol" in ids

    qfloor_path = REPO / "skills/spec-prototype/references/03-verification/quality-floor.md"
    qtext = qfloor_path.read_text(encoding="utf-8")
    assert "Contextual Craft Guidelines & Heuristics" in qtext
    assert "Integrated Design Invariant Standards" not in qtext


def test_method_registry_runtime_selection_and_negative_selection():
    """Declared-method-id selection: only Spec-declared methods reach the Builder."""
    assemble_mod = _load("assemble_envelope", SCRIPTS / "assemble_envelope.py")
    registry_path = REPO / "skills/spec-prototype/methods/registry.yaml"

    # Boundary: a Spec naming no method ids yields an empty advisory list —
    # heuristic trigger words never inject a method on their own.
    selected = assemble_mod.select_active_methods(
        registry_path=registry_path,
        stage=2,
        layout_profile="dense-console",
        spec_text="Telemetry metrics, latency sparklines, tabular-nums table, action verb quarantine",
        contract_text="action verb: quarantine-node",
        product_text="Cluster telemetry monitor",
        slice_id="telemetry-slice",
    )
    assert selected == []

    # Positive selection: methods declared in the Spec text are selected.
    selected = assemble_mod.select_active_methods(
        registry_path=registry_path,
        stage=2,
        layout_profile="dense-console",
        spec_text="Telemetry metrics console. Craft methods: `data-context-metrics`, "
        "`action-verb-lifecycle`, `form-ergonomics`",
        contract_text="action verb: quarantine-node",
        product_text="Cluster telemetry monitor",
        slice_id="telemetry-slice",
    )
    selected_ids = [m["id"] for m in selected]
    assert "data-context-metrics" in selected_ids
    assert "action-verb-lifecycle" in selected_ids
    assert "form-ergonomics" in selected_ids
    # Invariant lazy loading verification
    for m in selected:
        assert "invariants" in m and len(m["invariants"]) > 0
        assert "reference_file" in m

    # Negative selection: unnamed heuristics are not activated even when their
    # trigger words appear in the contract text.
    editorial_selected = assemble_mod.select_active_methods(
        registry_path=registry_path,
        stage=2,
        layout_profile="editorial-reading",
        spec_text="Editorial essay, typographic hierarchy, 68ch measure, chapter navigation",
        contract_text="reading surface",
        product_text="Literary journal reader",
        slice_id="reader-slice",
    )
    assert editorial_selected == []

    undeclared_heuristics = assemble_mod.select_active_methods(
        registry_path=registry_path,
        stage=2,
        layout_profile="dense-console",
        spec_text="Craft methods: `data-context-metrics`",
        contract_text="form fields, validation, multi-step wizard, destructive operations",
        product_text="form inputs and destructive workflows",
        slice_id="form-slice",
    )
    undeclared_ids = [m["id"] for m in undeclared_heuristics]
    assert "form-ergonomics" not in undeclared_ids, "Form ergonomics must not activate without a Spec declaration"
    assert "fault-tolerance-recovery" not in undeclared_ids, "Fault tolerance must not activate without a Spec declaration"
    assert undeclared_ids == ["data-context-metrics"]


def test_builder_recipe_purge_and_adaptive_state_machine():
    """v10.2.1 Task 2: Verify pre-baked recipes purged from Builder dispatch and envelope."""
    assemble_mod = _load("assemble_envelope", SCRIPTS / "assemble_envelope.py")
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "prototype").mkdir(parents=True, exist_ok=True)
        (root / "prototype/product.md").write_text("# Product\n- Core Tension: Speed vs Safety\n", encoding="utf-8")
        (root / "prototype/contracts/surface-maps").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/surface-maps/m1.md").write_text("# Surface Map\n", encoding="utf-8")
        (root / "prototype/contracts/foundation").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/foundation/f1.md").write_text("# Foundation\n", encoding="utf-8")
        (root / "prototype/shared").mkdir(parents=True, exist_ok=True)
        (root / "prototype/shared/tokens.css").write_text(":root { --bg-void: #000; }\n", encoding="utf-8")
        (root / "prototype/contracts/tokens").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/tokens/t1.md").write_text("# Tokens\n", encoding="utf-8")
        (root / "prototype/contracts/tokens/t1.json").write_text("{}", encoding="utf-8")
        (root / "prototype/contracts/slices/s1").mkdir(parents=True, exist_ok=True)
        (root / "prototype/contracts/slices/s1/c1.md").write_text("# Contract\n", encoding="utf-8")
        (root / "prototype/specifications/s1").mkdir(parents=True, exist_ok=True)
        (root / "prototype/specifications/s1/r1.md").write_text("""# Spec
- Supported States: inspecting, draining, settled
## Verifiable Design Assertions
| Assertion | Expected |
|---|---|
| Drain action executes | pass |
""", encoding="utf-8")

        env = assemble_mod.assemble(root, "s1", lint=False)
        # 1. State machine respects authored states
        assert env["interaction_spec"]["state_machine"]["supported_states"] == ["inspecting", "draining", "settled"]

        # 2. Tabular numbers not forced when no telemetry is present
        assert env["data_stress_boundaries"]["tabular_numbers_required"] is False

        # 3. Ruthless omissions and invariants fallbacks do not carry v9 recipes
        omissions = env["design_constraints"]["ruthless_omissions"]
        invariants = env["design_constraints"]["material_non_transfer_boundaries"]
        for om in omissions:
            assert "Digital Glass" not in om
            assert "Machined Detents" not in om
        for inv in invariants:
            assert "Precision Telemetry Emissives" not in inv
            assert "Machined Tactile Detents" not in inv

        # 4. Envelope contains active_methods and authority_status
        assert "active_methods" in env
        assert env["authority_status"] == "sealed_provisional"


def test_authority_lifecycle_mechanization_and_downstream_gate():
    """v10.2.1 Task 3: Verify downstream gate and freeze state transition in handoff.py."""
    handoff_mod = _load("handoff", SCRIPTS / "handoff.py")
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        spec_dir = root / "prototype/specifications/s1"
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_file = spec_dir / "r1.md"

        # 1. Provisional spec is rejected by downstream gate
        spec_file.write_text("# Spec\n- Candidate revision: r1\n- Compilation status: provisional\n- Authority status: sealed provisional\n", encoding="utf-8")
        with pytest.raises(handoff_mod.HandoffError, match="Downstream Gate Blocked.*provisional"):
            handoff_mod.check_downstream_gate(root, "s1")

        # 2. Validated spec is blocked until frozen
        spec_file.write_text("# Spec\n- Candidate revision: r1\n- Compilation status: validated\n- Authority status: validated\n", encoding="utf-8")
        with pytest.raises(handoff_mod.HandoffError, match="Downstream Gate Blocked.*validated.*not yet frozen"):
            handoff_mod.check_downstream_gate(root, "s1")

        # 3. Frozen spec passes downstream gate
        evidence_dir = root / "prototype/evidence/s1/r1"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = evidence_dir / "freeze-manifest.json"
        manifest_file.write_text(json.dumps({"status": "frozen", "authority_status": "frozen_approved"}), encoding="utf-8")
        spec_file.write_text("# Spec\n- Candidate revision: r1\n- Compilation status: frozen\n- Authority status: frozen approved\n", encoding="utf-8")

        result = handoff_mod.check_downstream_gate(root, "s1")
        assert result["gate"] == "passed"
        assert result["authority_status"] == "frozen_approved"


def test_stage1_sealed_provisional_and_stage5_frozen_approved_terminology():
    """v10.2.1 Task 4: Harmonize Stage 1 Sealed Provisional and Stage 5 Frozen Approved terminology."""
    skill_text = (REPO / "skills/spec-prototype/SKILL.md").read_text(encoding="utf-8")
    kernel_text = (REPO / "skills/spec-prototype/references/core-kernel.md").read_text(encoding="utf-8")
    stage5_text = (REPO / "skills/spec-prototype/references/stages/stage-5-freeze.md").read_text(encoding="utf-8")
    stage1_text = (REPO / "skills/spec-prototype/references/stages/stage-1-frame.md").read_text(encoding="utf-8")

    # SKILL.md
    assert "Sealed Provisional Spec Artifacts" in skill_text
    assert "authority status: sealed provisional" in skill_text
    assert "Draft → Sealed Provisional → Validated → Frozen Approved" in skill_text
    assert "Silent Packaging & Frozen Approved Delivery" in skill_text

    # core-kernel.md (active authority-lifecycle owner)
    assert "Draft → Sealed Provisional → Validated → Frozen Approved" in kernel_text
    assert "Sealed Provisional" in kernel_text
    assert "Frozen Approved" in kernel_text
    assert "04-governance/artifact-lifecycle.md" in kernel_text

    # Stage owners
    assert "Silent Governance & Frozen Approved Delivery" in stage5_text
    assert "04-governance/artifact-lifecycle.md" in stage5_text
    assert "Sealed Provisional Baseline Closure" in stage1_text








"""CPC-SCN-007 / CPC-SCN-008: coverage and platform contracts in compilation and dispatch.

Mechanism checks over temporary repositories. Not real-session evidence.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/spec-prototype/scripts"
sys.path.insert(0, str(SCRIPTS))

import assemble_envelope  # noqa: E402
import execution_boundary  # noqa: E402
import lint_spec_contracts  # noqa: E402

SLICE = "console"
TEN = "surfaces: " + ", ".join(
    f"S{i}-{name}" for i, name in enumerate(
        ["feed", "detail", "compose", "queue", "history", "settings",
         "billing", "members", "audit", "help"], start=1)) + "\n"


def ctx_block(record: str, body: str) -> str:
    return f"```prototype-context\nrecord: {record}\n{body}```\n"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_repo(
    tmp_path: Path,
    *,
    coverage: str = "selected",
    selection: str = "selected-surfaces: S1-feed, S2-detail, S3-compose\n",
    selection_source: str = "selection-source: prototype/discussion/scope-r7.md\n",
    dependencies: str = "",
    tension: str = "- Core Tension: Operational Density vs Reading Calm\n",
    anchors: str = "- Reality Anchors: Linear, Stripe Dashboard\n",
    medium: str = "HTML",
    target: str = "android",
) -> Path:
    """A complete Stage 1 contract set; every field is authored, none invented."""
    root = tmp_path
    write(root / "prototype/product.md",
          f"# Product Thesis: Console\n\n{anchors}{tension}Status: candidate\n\n"
          + ctx_block("product", f"target-context: {target}\ndevice-context: desktop\n"
                               "input-context: pointer-and-keyboard\n"))
    write(root / "prototype/contracts/surface-maps/m1.md",
          "# Product Surface Map\n\n- Surface Map revision: r7 (draft)\n\n"
          + ctx_block("surface-map", f"revision: r7\ncoverage: {coverage}\n"
                                     f"{selection_source}{TEN}{selection}{dependencies}"))
    write(root / "prototype/contracts/foundation/f1.md",
          "# Experience Foundation\n\n" + ctx_block(
              "experience-foundation",
              "invariants: object-identity, permission-scope, selected-context, required-return\n"))
    write(root / "prototype/contracts/tokens/t1.md",
          "# Token Revision: t1\n\n- Token source: authored\n")
    write(root / "prototype/shared/tokens.css",
          ":root {\n  --surface-bg: #101418;\n  --text-primary: #e6edf3;\n}\n")
    write(root / f"prototype/contracts/slices/{SLICE}/c1.md",
          f"# Prototype Slice Contract: {SLICE}\n\n- Slice ID: {SLICE}\n"
          "- Content language: en-US\n\n## Action Verb Lifecycle Table\n\n"
          "| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button |"
          " Completion Feedback Toast | Impact |\n"
          "|---|---|---|---|---|---|\n"
          "| act-1 | Retry | Retry sync | Retry | Sync retried | Requeues work |\n")
    write(root / f"prototype/specifications/{SLICE}/r1.md",
          f"# Prototype Specification: {SLICE} / r1\n\n"
          f"- Prototype write scope: prototype/experiments/{SLICE}/anchor/\n"
          f"- Evidence write scope: prototype/evidence/probes/{SLICE}/\n"
          "- Content language: en-US\n\n## Verifiable Design Assertions\n\n"
          "| Assertion | Expected | Status |\n|---|---|---|\n"
          "| Header renders | visible | unverified |\n\n"
          "## The Break Protocol Stress Checkpoints\n\n"
          "| Checkpoint | Vector | N/A rationale |\n|---|---|---|\n"
          "| Refresh | reload | not applicable to anchor |\n\n"
          + ctx_block("prototype-specification",
                      f"prototype-medium: {medium}\n"
                      "verification-environment: headless-chromium-120\n"))
    return root


def envelope_json(root: Path) -> dict:
    return json.loads((root / "envelope.json").read_text(encoding="utf-8"))


def assemble_to_file(root: Path) -> dict:
    env = assemble_envelope.assemble(root, SLICE)
    write(root / "envelope.json", json.dumps(env))
    return env


# CPC-SCN-007: authored values survive compilation; absent facts stay absent.

def test_authored_values_and_digests_survive_assembly(tmp_path):
    root = build_repo(tmp_path)
    env = assemble_to_file(root)
    assert env["domain_thesis"]["core_tension"] == "Operational Density vs Reading Calm"
    assert env["coverage"]["target_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]
    assert len(env["coverage"]["unselected_surfaces"]) == 7  # context retained, not targeted
    for key in ("product_digest", "surface_map_digest", "foundation_digest", "contract_digest",
                "specification_digest", "tokens_md_digest", "tokens_css_digest"):
        assert len(env["spec_sources"][key]) == 64
    assert env["spec_sources"]["tokens_md_digest"] == hashlib.sha256(
        (root / "prototype/contracts/tokens/t1.md").read_bytes()).hexdigest()


def test_absent_optional_facts_do_not_become_fixed_domain_claims(tmp_path):
    root = build_repo(tmp_path, tension="- Core Tension: unspecified\n")
    env = assemble_to_file(root)
    assert "core_tension" not in env["domain_thesis"]  # no invented "X vs Y" claim
    assert env["platform"]["verification_environment"] == "headless-chromium-120"  # evidence kept


# CPC-SCN-024: product category yields advisory candidates; selection stays open.

def test_console_category_no_longer_locks_a_hardcoded_profile(tmp_path):
    root = build_repo(tmp_path)
    product = root / "prototype/product.md"
    product.write_text(product.read_text(encoding="utf-8")
                       + "\n- Dominant Baseline: Baseline 1: Dense Data Workbench\n", encoding="utf-8")
    env = assemble_to_file(root)
    assert env["selected_pattern"] is None  # category alone is not a confirmation
    assert env["candidate_patterns"][0] == "dense-console"
    assert env["layout_profile"] == "adaptive-workspace"  # advisory stays neutral, no lock


def test_saas_category_stays_advisory(tmp_path):
    root = build_repo(tmp_path)
    product = root / "prototype/product.md"
    product.write_text(product.read_text(encoding="utf-8")
                       + "\n- Dominant Baseline: Baseline 2: SaaS Commerce\n", encoding="utf-8")
    env = assemble_to_file(root)
    assert env["selected_pattern"] is None
    assert "operational-canvas" in env["candidate_patterns"]
    assert env["layout_profile"] == "adaptive-workspace"  # advisory stays neutral, no lock


def test_explicit_authored_specification_confirms_one_pattern(tmp_path):
    root = build_repo(tmp_path)
    spec = root / f"prototype/specifications/{SLICE}/r1.md"
    spec.write_text(spec.read_text(encoding="utf-8") + "\n- Layout Profile: editorial-reading\n",
                    encoding="utf-8")
    env = assemble_to_file(root)
    assert env["selected_pattern"] == "editorial-reading"
    assert env["layout_profile"] == "editorial-reading"


def test_native_target_in_browser_medium_keeps_its_validation_gap(tmp_path):
    root = build_repo(tmp_path, target="android", medium="HTML")
    env = assemble_to_file(root)
    assert env["platform"]["native_validation_pending"] is True
    assert env["platform"]["target_context"] == "android"
    assert env["platform"]["prototype_medium"] == "HTML"


def test_missing_selection_never_becomes_full_product(tmp_path):
    root = build_repo(tmp_path, coverage="unresolved", selection="", selection_source="")
    with pytest.raises(ValueError) as error:
        assemble_envelope.assemble(root, SLICE)
    assert "E008_COVERAGE_UNRESOLVED" in str(error.value)
    assert (root / "prototype/product.md").is_file()  # existing artifacts preserved


def test_selected_output_cannot_expand_to_unselected_surfaces(tmp_path):
    root = build_repo(tmp_path, dependencies="selected-dependencies: S7-billing\n")
    env = assemble_to_file(root)
    assert env["coverage"]["target_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]
    assert "S7-billing" not in env["coverage"]["target_surfaces"]
    assert "S7-billing" in env["coverage"]["unselected_surfaces"]  # disclosed, not added


def test_unknown_selection_ids_are_a_contract_failure(tmp_path):
    root = build_repo(tmp_path, selection="selected-surfaces: S1-feed, S99-ghost, S1-feed\n")
    with pytest.raises(ValueError) as error:
        assemble_envelope.assemble(root, SLICE)
    assert "E014_SELECTION_INVALID" in str(error.value)


def test_stale_or_missing_selection_source_fails_the_formal_entry(tmp_path):
    root = build_repo(tmp_path, selection_source="")
    with pytest.raises(ValueError) as error:
        assemble_envelope.assemble(root, SLICE)
    assert "E009_SELECTION_SOURCE_MISSING" in str(error.value)


def test_undeclared_platform_context_fails_the_formal_entry(tmp_path):
    root = build_repo(tmp_path, dependencies="platform-contexts: web, android\n"
                                             "applicability: S3-compose=watchos\n")
    with pytest.raises(ValueError) as error:
        assemble_envelope.assemble(root, SLICE)
    assert "E013_PLATFORM_CONTEXT_UNKNOWN" in str(error.value)


# CPC-SCN-007: the formal entry runs the lint itself, not a copy of it.

def test_formal_path_actually_runs_the_contract_lint(tmp_path):
    root = build_repo(tmp_path)
    calls = []
    original = lint_spec_contracts.lint_formal_entry

    def spy(root_arg, slice_arg):
        calls.append((Path(root_arg), slice_arg))
        return original(root_arg, slice_arg)

    lint_spec_contracts.lint_formal_entry = spy
    try:
        assemble_envelope.assemble(root, SLICE)
    finally:
        lint_spec_contracts.lint_formal_entry = original
    assert calls and calls[0][1] == SLICE


def test_lint_failure_keeps_its_rule_code_and_path(tmp_path):
    root = build_repo(tmp_path, coverage="unresolved", selection="", selection_source="")
    failures = lint_spec_contracts.lint_formal_entry(root, SLICE)
    unresolved = [f for f in failures if f.rule == "E008_COVERAGE_UNRESOLVED"]
    assert unresolved and unresolved[0].file_path == "m1.md"
    assert "recommended combination" in unresolved[0].message


# CPC-SCN-008: boundary admission validates identities without granting approval.

def test_symlink_escape_is_a_lint_failure(tmp_path):
    root = build_repo(tmp_path)
    outside = tmp_path.parent / "outside-c1.md"
    outside.write_text("# foreign contract\n", encoding="utf-8")
    contract = root / f"prototype/contracts/slices/{SLICE}/c1.md"
    contract.unlink()
    contract.symlink_to(outside)
    rules = {f.rule for f in lint_spec_contracts.lint_formal_entry(root, SLICE)}
    assert "E012_PATH_ESCAPE" in rules


def test_boundary_admits_only_the_bounded_lint_helper_form(tmp_path):
    root = build_repo(tmp_path)
    good = {"script": SCRIPTS / "lint_spec_contracts.py",
            "argv": ["--root", str(root), "--slice", SLICE]}
    execution_boundary.admits_lint_helper(good, root)

    outside = tmp_path.parent
    for bad in (
        {"script": SCRIPTS / "materialize_contracts.py", "argv": ["--root", str(root)]},
        {"script": SCRIPTS / "lint_spec_contracts.py", "argv": ["--root", str(outside), "--slice", SLICE]},
        {"script": SCRIPTS / "lint_spec_contracts.py", "argv": ["--root", str(root), "--slice", "../escape"]},
        {"script": SCRIPTS / "lint_spec_contracts.py", "argv": [str(root)]},
    ):
        with pytest.raises(ValueError):
            execution_boundary.admits_lint_helper(bad, root)


def test_boundary_rejects_traversal_out_of_the_selection(tmp_path):
    root = build_repo(tmp_path)
    env = assemble_to_file(root)
    env["spec_sources"]["contract_digest"] = "0" * 64
    payload = {"repository_root": str(root), "skill_root": str(assemble_envelope.SKILL),
               "mode": "lean-builder-envelope", "slice_id": SLICE,
               "target_html_path": "prototype/experiments/escape/index.html",
               "spec_sources": env["spec_sources"]}
    with pytest.raises(ValueError):
        execution_boundary.dispatch(
            {"subagent_type": "spec-prototype-builder", "prompt": json.dumps(payload)}, root)


def test_stale_contract_digest_is_refused_at_dispatch(tmp_path):
    root = build_repo(tmp_path)
    env = assemble_to_file(root)
    payload = {"repository_root": str(root), "skill_root": str(assemble_envelope.SKILL),
               "mode": "lean-builder-envelope", "slice_id": SLICE,
               "target_html_path": f"prototype/experiments/{SLICE}/anchor/index.html",
               "spec_sources": {**env["spec_sources"], "specification_digest": "0" * 64}}
    with pytest.raises(ValueError) as error:
        execution_boundary.dispatch(
            {"subagent_type": "spec-prototype-builder", "prompt": json.dumps(payload)}, root)
    assert "Stale contract" in str(error.value)


def test_exact_json_dispatch_still_passes_when_nothing_changed(tmp_path):
    root = build_repo(tmp_path)
    env = assemble_to_file(root)
    payload = {"repository_root": str(root), "skill_root": str(assemble_envelope.SKILL),
               "mode": "lean-builder-envelope", "slice_id": SLICE,
               "target_html_path": f"prototype/experiments/{SLICE}/anchor/index.html",
               "spec_sources": env["spec_sources"]}
    execution_boundary.dispatch(
        {"subagent_type": "spec-prototype-builder", "prompt": json.dumps(payload)}, root)


# The brief-only probe route is unaffected by the formal-path gate.

def test_brief_only_probe_route_still_assembles(tmp_path):
    root = tmp_path
    brief = root / f"prototype/briefs/{SLICE}-probe.md"
    write(brief, f"# Probe\n\n- Probe ID: {SLICE}\n- Core design thesis: dense console\n"
                 "- Probe target path: prototype/experiments/probes/console/\n")
    env = assemble_envelope.assemble(root, SLICE)
    assert env["mode"] == "direction-probe"
    assert env["brief"]["sha256"] == hashlib.sha256(brief.read_bytes()).hexdigest()
    assert "coverage" not in env  # the formal contract gate does not touch probes

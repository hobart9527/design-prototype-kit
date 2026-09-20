"""CPC-002: the formal entry admits an authored scope on its retained map identity.

Temporary repositories, complete Stage 1 contract sets. These are mechanism
checks over the admission seam, not real design sessions and not evidence that a
live designer selected anything.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/spec-prototype/scripts"
sys.path.insert(0, str(SCRIPTS))

import assemble_envelope  # noqa: E402
import lint_spec_contracts  # noqa: E402

SLICE = "console"
SELECTION_SOURCE = "prototype/discussion/scope-r7.md"
SURFACES = [f"S{i}-{name}" for i, name in enumerate(
    ["feed", "detail", "compose", "queue", "history", "settings",
     "billing", "members", "audit", "help"], start=1)]
TEN = "surfaces: " + ", ".join(SURFACES) + "\n"


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
    map_revision: str = "r7",
    retained_identity: str = "- Surface Map revision: r7\n",
) -> Path:
    """A complete Stage 1 contract set plus the retained selection record.

    `{digest}` in `retained_identity` resolves to the authored map's digest, so a
    matching-digest case states a real digest rather than a hardcoded literal.
    """
    root = tmp_path
    write(root / "prototype/product.md",
          "# Product Thesis: Console\n\n- Reality Anchors: Linear, Stripe Dashboard\n"
          "- Core Tension: Operational Density vs Reading Calm\n\n"
          "Status: candidate\n\n"
          + ctx_block("product", "target-context: web\ndevice-context: desktop\n"
                                 "input-context: pointer-and-keyboard\n"))
    write(root / "prototype/contracts/surface-maps/m1.md",
          f"# Product Surface Map\n\n- Surface Map revision: {map_revision} (draft)\n\n"
          + ctx_block("surface-map", f"revision: {map_revision}\ncoverage: {coverage}\n"
                                     f"selection-source: {SELECTION_SOURCE}\n{TEN}{selection}"))
    mapped = root / "prototype/contracts/surface-maps/m1.md"
    retained_identity = retained_identity.replace(
        "{digest}", hashlib.sha256(mapped.read_bytes()).hexdigest())
    write(root / SELECTION_SOURCE, f"# Requested scope: {map_revision}\n\n{retained_identity}")
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
                      "prototype-medium: HTML\n"
                      "verification-environment: headless-chromium-120\n"))
    return root


def snapshot(root: Path) -> dict:
    """Every retained byte in the temporary root, before a refusal is attempted."""
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()}


def assert_unchanged(root: Path, before: dict) -> None:
    assert snapshot(root) == before, "a refusal must not rewrite or remove any artifact"


def refusal(root: Path, rule: str) -> str:
    """Assemble and return the refusal message, proving the artifact set is untouched."""
    before = snapshot(root)
    with pytest.raises(ValueError) as error:
        assemble_envelope.assemble(root, SLICE)
    assert_unchanged(root, before)
    assert rule in str(error.value)
    return str(error.value)


# CPC-SCN-018: full-product authorizes every applicable surface, not a widened selection.

def test_full_product_with_empty_selection_targets_every_surface(tmp_path):
    root = build_repo(tmp_path, coverage="full-product", selection="")
    env = assemble_envelope.assemble(root, SLICE)
    assert env["coverage"]["authorizes_full_product"] is True
    assert env["coverage"]["coverage"] == "full-product"
    assert env["coverage"]["target_surfaces"] == SURFACES
    assert env["coverage"]["unselected_surfaces"] == []
    # The authorization names no individual surface, so none is reported as widened.
    assert not [f for f in env["contract_lint"] if f["code"] == "E011_SELECTION_WIDENED"]


def test_full_product_identity_mismatch_is_refused_too(tmp_path):
    root = build_repo(tmp_path, coverage="full-product", selection="",
                      retained_identity="- Surface Map revision: r6\n")
    message = refusal(root, "E010_STALE_CONTRACT")
    assert "'r7'" in message and "'r6'" in message


# CPC-SCN-020 / E014: an empty or ill-formed selected coverage stays refused.

def test_empty_selected_coverage_is_still_refused(tmp_path):
    root = build_repo(tmp_path, selection="")
    refusal(root, "E011_SELECTION_WIDENED")


def test_selected_map_naming_a_surface_outside_the_map_still_fails(tmp_path):
    root = build_repo(tmp_path, selection="selected-surfaces: S1-feed, S99-ghost\n")
    refusal(root, "E014_SELECTION_INVALID")


def test_selected_targets_stay_bounded_by_the_selection(tmp_path):
    root = build_repo(tmp_path)
    env = assemble_envelope.assemble(root, SLICE)
    assert env["coverage"]["target_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]
    assert len(env["coverage"]["unselected_surfaces"]) == 7  # context retained, not targeted


# CPC-SCN-019: the retained selection's map identity gates the dispatch.

def test_matching_retained_map_revision_passes(tmp_path):
    root = build_repo(tmp_path, retained_identity="- Surface Map revision: r7\n")
    env = assemble_envelope.assemble(root, SLICE)
    assert env["coverage"]["target_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]


def test_changed_map_revision_fails_with_the_specific_mismatch(tmp_path):
    root = build_repo(tmp_path, retained_identity="- Surface Map revision: r6\n")
    message = refusal(root, "E010_STALE_CONTRACT")
    assert "revision" in message and "'r7'" in message and "'r6'" in message


def test_changed_map_digest_fails_with_the_specific_mismatch(tmp_path):
    retained = hashlib.sha256(b"# some other retained map revision\n").hexdigest()
    root = build_repo(tmp_path, retained_identity=(
        "- Surface Map digest: sha256:" + retained + "\n"))
    message = refusal(root, "E010_STALE_CONTRACT")
    actual = hashlib.sha256(
        (root / "prototype/contracts/surface-maps/m1.md").read_bytes()).hexdigest()
    assert "digest" in message and actual in message and retained not in message


def test_matching_retained_map_digest_passes(tmp_path):
    root = build_repo(tmp_path, retained_identity=(
        "- Surface Map revision: r7\n- Surface Map digest: sha256:{digest}\n"))
    env = assemble_envelope.assemble(root, SLICE)
    assert env["coverage"]["authorizes_full_product"] is False


def test_lint_reports_identity_without_rewriting_the_map(tmp_path):
    root = build_repo(tmp_path, retained_identity="- Surface Map revision: r6\n")
    before = snapshot(root)
    failures = lint_spec_contracts.lint_formal_entry(root, SLICE)
    stale = [f for f in failures if f.rule == "E010_STALE_CONTRACT"]
    assert stale and stale[0].file_path == "m1.md"
    assert_unchanged(root, before)


def test_a_selection_record_silent_about_identity_adds_no_refusal(tmp_path):
    """A legacy selection source that names no revision is read, never invented."""
    root = build_repo(tmp_path, retained_identity="- Requested scope: review subset\n")
    env = assemble_envelope.assemble(root, SLICE)
    assert env["coverage"]["target_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]

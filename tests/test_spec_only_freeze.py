"""Spec-only freeze retains the design scope without a built prototype (CPC-007).

CPC-SCN-015: a user approval of a design specification without prototype
execution freezes the approved design scope without requiring an HTML artifact,
and implementation, platform and production validation stay explicitly pending.
CPC-SCN-024: a frozen scope that claims prototype implementation still requires
its HTML entry, and a refused freeze leaves existing artifacts intact.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
SKILL = SCRIPTS.parent

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


handoff = _load("handoff", "handoff.py")


def _sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


APPROVED_ROW = (
    "| D-1 | Reader slice design direction | confirmed | align on direction "
    "| \"explicit approval of the reader slice as specified\" (turn 4, 2026-09-01) "
    "| `prototype/specifications/reader/r1.md` |\n"
)
SPEC_ONLY_ROW = (
    "| D-1 | Spec-only design scope for reader | confirmed | design-only approval "
    "| \"确认封版 only the specification, no prototype execution\" (turn 7, 2026-09-02) "
    "| `prototype/specifications/reader/r1.md` |\n"
)
NO_DECISION_ROW = (
    "| D-1 | Reader slice design direction | proposed | still open "
    "| AI recommendation only | `prototype/specifications/reader/r1.md` |\n"
)


def _decision_block(row: str) -> str:
    return "# Design discussion\n\n## Decisions and authority\n\n" \
           "| ID | Decision | Status | Reason / evidence | Actual user quote + turn/date | Affected artifacts |\n" \
           "|---|---|---|---|---|---|\n" + row


def _build_root(root: Path, decision_row: str = APPROVED_ROW,
                prototype_entry: bool = True) -> Path:
    """Build the smallest root the strict packet admits, plus the approval record.

    With `prototype_entry` false the declared prototype write scope is not
    retained at all, which is the spec-only shape the scope claim guards.
    """
    if prototype_entry:
        (root / "prototype/experiments/reader/r1").mkdir(parents=True, exist_ok=True)
        (root / "prototype/experiments/reader/r1/index.html").write_text(
            "<!doctype html><title>reader</title>\n", encoding="utf-8")

    product = root / "prototype/product.md"
    product.parent.mkdir(parents=True, exist_ok=True)
    product.write_text("# Product\nDocument reader.\n", encoding="utf-8")

    smap = root / "prototype/contracts/surface-maps/m1.md"
    smap.parent.mkdir(parents=True, exist_ok=True)
    smap.write_text("# Surface Map\n- Surface Map revision / status (`draft | frozen | superseded`): m1 / draft\n"
                    "- Scope: reader\n", encoding="utf-8")

    foundation = root / "prototype/contracts/foundation/f1.md"
    foundation.parent.mkdir(parents=True, exist_ok=True)
    foundation.write_text(
        "# Foundation\n"
        "- Foundation revision: f1\n"
        f"- Product record path, revision and digest: `{product.relative_to(root)}`, {_sha256(product.read_bytes())}\n"
        f"- Retained Surface Map path, revision and digest: `{smap.relative_to(root)}`, {_sha256(smap.read_bytes())}\n",
        encoding="utf-8")

    tokens = root / "prototype/contracts/tokens/t1.md"
    tokens.parent.mkdir(parents=True, exist_ok=True)
    tokens.write_text("# Tokens\n- Foundation revision: f1\n- Tokens revision: t1\n"
                      "## Breakpoints\n| Token | Value |\n|---|---|\n| --bp-mobile | 390px |\n", encoding="utf-8")

    contract = root / "prototype/contracts/slices/reader/c1.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        "# Contract\n"
        "- Slice ID: reader\n"
        "- Contract revision: c1\n"
        "- Foundation revision: f1\n"
        "- Disposition: ready\n"
        f"- Retained surface-map path, revision and digest: `{smap.relative_to(root)}`, {_sha256(smap.read_bytes())}\n",
        encoding="utf-8")

    craft = SKILL / "references/03-verification/quality-floor.md"
    spec = root / "prototype/specifications/reader/r1.md"
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(
        "# Prototype Specification: reader / r1\n"
        "- Candidate / selected revision: r1\n"
        "- Compilation status: candidate\n"
        f"- Repository root: `{root}`\n"
        f"- Product record revision and digest: `{product.relative_to(root)}`, {_sha256(product.read_bytes())}\n"
        f"- Foundation revision and digest: `{foundation.relative_to(root)}`, {_sha256(foundation.read_bytes())}\n"
        f"- Token artifact path, revision, and digest: `{tokens.relative_to(root)}`, {_sha256(tokens.read_bytes())}\n"
        f"- Slice Contract revision and digest: `{contract.relative_to(root)}`, {_sha256(contract.read_bytes())}\n"
        "- Prototype write scope: `prototype/experiments/reader/r1/`\n"
        "- Evidence write scope: `prototype/evidence/reader/r1/`\n"
        "- Start command: `python3 -m http.server 8000`\n"
        "- Verification command(s): `python3 -m unittest`\n"
        "- Page/flow coverage and shared data references: reader view\n"
        "- Delegated implementation freedoms: HTML composition\n"
        "- Required reachable-control closure: links\n"
        f"- Skill root / evidence template path for this dispatch: `{SKILL}`\n"
        f"- Required craft reads: `references/03-verification/quality-floor.md`, {_sha256(craft.read_bytes())}\n"
        "- Visual verification: not_required\n"
        "- Required screenshot checkpoints:\n"
        "| Surface / interaction | Existing asset | Disposition | Constraint | Verification checkpoint |\n"
        "|---|---|---|---|---|\n"
        "| Reader | native HTML | delegated | semantic | keyboard |\n",
        encoding="utf-8")

    (root / "prototype/discussion.md").write_text(_decision_block(decision_row), encoding="utf-8")
    return spec


def _snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


MANIFEST = "prototype/evidence/reader/r1/freeze-manifest.json"


# --- CPC-SCN-015: a spec-only approval freezes without a built prototype -----

def test_spec_only_approval_freezes_without_html_artifact(tmp_path: Path):
    spec = _build_root(tmp_path, decision_row=SPEC_ONLY_ROW, prototype_entry=False)
    assert not list(tmp_path.rglob("*.html"))

    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    assert manifest["status"] == "frozen"
    assert manifest["authority_status"] == "frozen_approved"
    assert manifest["approval"]["spec_only"] is True
    assert manifest["approval"]["decision_id"] == "D-1"
    # Selecting a ready spec requires no build; the design scope is retained.
    assert manifest["approval"]["scope"] == {"slice_id": "reader", "candidate_id": "r1"}
    assert not list(tmp_path.rglob("*.html"))


def test_spec_only_freeze_keeps_implementation_validation_pending(tmp_path: Path):
    spec = _build_root(tmp_path, decision_row=SPEC_ONLY_ROW, prototype_entry=False)

    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    assert manifest["implementation_validation"] == {
        "implementation": "pending", "platform": "pending", "production": "pending"}
    persisted = json.loads((tmp_path / MANIFEST).read_text(encoding="utf-8"))
    assert persisted["implementation_validation"] == manifest["implementation_validation"]
    # Retaining the approved design scope admits downstream without a prototype.
    assert handoff.check_downstream_gate(tmp_path, "reader")["gate"] == "passed"


# --- CPC-SCN-024: a prototype claim still requires its entry -----------------

@pytest.mark.parametrize("shape, message", [
    ("claimed-no-entry", "no HTML entry"),
    ("claimed-no-scope", "not retained"),
])
def test_prototype_claim_without_entry_still_refused(tmp_path: Path, shape: str, message: str):
    # A confirmed (non spec-only) approval claims prototype implementation, so
    # the entry requirement still applies: a missing scope and a scope without
    # an HTML entry are each refused.
    if shape == "claimed-no-entry":
        spec = _build_root(tmp_path)
        (tmp_path / "prototype/experiments/reader/r1/index.html").unlink()
        (tmp_path / "prototype/experiments/reader/r1/notes.md").write_text(
            "# Notes\n", encoding="utf-8")
    else:
        spec = _build_root(tmp_path, prototype_entry=False)
    before = _snapshot(tmp_path)

    with pytest.raises(handoff.HandoffError, match=message):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    assert not (tmp_path / MANIFEST).exists()
    assert _snapshot(tmp_path) == before
    assert "Compilation status: candidate" in spec.read_text(encoding="utf-8")


def test_refused_freeze_leaves_existing_artifacts_intact(tmp_path: Path):
    spec = _build_root(tmp_path, prototype_entry=True)
    # A retained experiments directory whose entry is not an HTML artifact.
    (tmp_path / "prototype/experiments/reader/r1/index.html").unlink()
    (tmp_path / "prototype/experiments/reader/r1/notes.md").write_text(
        "# Notes\n", encoding="utf-8")
    before = _snapshot(tmp_path)

    with pytest.raises(handoff.HandoffError, match="no HTML entry"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    assert _snapshot(tmp_path) == before
    assert not (tmp_path / MANIFEST).exists()


def test_override_without_approval_cannot_manufacture_frozen_authority(tmp_path: Path):
    spec = _build_root(tmp_path, decision_row=NO_DECISION_ROW, prototype_entry=False)
    before = _snapshot(tmp_path)

    with pytest.raises(handoff.HandoffError, match="no actual approval"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert _snapshot(tmp_path) == before
    assert not (tmp_path / MANIFEST).exists()

    # The permissive CLI form does not manufacture frozen-approved status either.
    sys.argv = ["handoff.py", "freeze", "--root", str(tmp_path),
                "--spec", "prototype/specifications/reader/r1.md", "--force"]
    with pytest.raises(SystemExit):
        handoff.main()
    assert not (tmp_path / MANIFEST).exists()


# --- a valid prototype freeze is unchanged -----------------------------------

def test_valid_prototype_freeze_is_unchanged(tmp_path: Path):
    spec = _build_root(tmp_path)
    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    assert manifest["status"] == "frozen"
    assert manifest["authority_status"] == "frozen_approved"
    assert manifest["approval"]["spec_only"] is False
    assert manifest["implementation_validation"] == {
        "implementation": "pending", "platform": "pending", "production": "pending"}

    admitted = handoff.downstream_admission(tmp_path, "reader")
    assert admitted["gate"] == "passed"
    assert admitted["admission"] == "bound_to_frozen_revision"
    assert admitted["implementation_validation"]["production"] == "pending"


def test_freeze_preserves_spec_byte_immutability(tmp_path: Path):
    """Specification bytes must remain 100% immutable across freeze operations."""
    spec = _build_root(tmp_path)
    before_bytes = spec.read_bytes()

    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert manifest["status"] == "frozen"
    assert spec.read_bytes() == before_bytes, "Freeze must not mutate candidate specification markdown in-place"


def test_approval_must_bind_target_slice(tmp_path: Path):
    """Approval row in discussion.md must bind the target slice, not another slice."""
    other_slice_row = (
        "| D-1 | Billing slice approval | confirmed | align on billing "
        "| \"approved billing slice\" (turn 4, 2026-09-01) "
        "| `prototype/specifications/billing/r1.md` |\n"
    )
    spec = _build_root(tmp_path, decision_row=other_slice_row)

    with pytest.raises(handoff.HandoffError, match="no actual approval"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())


def test_freeze_projects_scope_and_platform_metadata(tmp_path: Path):
    """Freeze manifest must project scope and platform metadata for downstream consumers."""
    spec = _build_root(tmp_path)
    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert manifest["scope_projection"]["coverage"]
    # The reader marks an unexercised artifact 'unknown'; a None here means the
    # projection read the wrong context section and silently lost the fact.
    assert manifest["platform_projection"]["verification_environment"]


def test_approval_does_not_bind_a_longer_slice_name(tmp_path: Path):
    """A row naming slice 'readers-grid' must not authorize the 'reader' slice.

    Slice names nest (`reader` inside `readers-grid`), so binding on a plain
    substring would let one slice's approval freeze another's specification.
    """
    longer_slice_row = (
        "| D-1 | Readers-grid slice approval | confirmed | align on readers-grid "
        "| \"approved the readers-grid slice\" (turn 5, 2026-09-04) "
        "| `prototype/specifications/readers-grid/r1.md` |\n"
    )
    spec = _build_root(tmp_path, decision_row=longer_slice_row)

    with pytest.raises(handoff.HandoffError, match="no actual approval"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

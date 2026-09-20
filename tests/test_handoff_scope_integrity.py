"""Freeze approval binding, strict failure retention and downstream admission (CPC-007).

CPC-SCN-014: planned/negated approval, strict reference failure, approval-less
override and post-freeze source drift must not produce or admit an approved
intact handoff.
CPC-SCN-015: a spec-only approval retains the design scope while prototype,
platform and production implementation validation stay explicitly pending.
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
boundary = _load("boundary", "execution_boundary.py")


def _sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


APPROVED_ROW = (
    "| D-1 | Reader slice design direction | confirmed | align on direction "
    "| \"explicit approval of the reader slice as specified\" (turn 4, 2026-09-01) "
    "| `prototype/specifications/reader/r1.md` |\n"
)
PLANNED_ROW = (
    "| D-1 | Reader slice design direction | confirmed | align on direction "
    "| user will approve once evidence lands (planned) | `prototype/specifications/reader/r1.md` |\n"
)
NEGATED_ROW = (
    "| D-1 | Reader slice design direction | confirmed | align on direction "
    "| 用户明确批准 not approved; override without approval applied | `prototype/specifications/reader/r1.md` |\n"
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


def _build_root(root: Path, decision_row: str = APPROVED_ROW, status: str = "candidate") -> Path:
    """Build the smallest root the strict packet admits, plus the approval record."""
    (root / "prototype/experiments/reader/r1").mkdir(parents=True, exist_ok=True)
    (root / "prototype/experiments/reader/r1/index.html").write_text(
        "<!doctype html><title>reader</title>\n", encoding="utf-8")

    product = root / "prototype/product.md"
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
        f"- Compilation status: {status}\n"
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


def _html_snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


# --- CPC-SCN-015: an actual approval freezes; implementation stays pending ----

def test_valid_references_and_actual_approval_freeze(tmp_path: Path):
    spec = _build_root(tmp_path)
    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    assert manifest["status"] == "frozen"
    assert manifest["authority_status"] == "frozen_approved"
    assert manifest["approval"]["decision_id"] == "D-1"
    assert manifest["approval"]["scope"] == {"slice_id": "reader", "candidate_id": "r1"}
    assert manifest["approval"]["spec_only"] is False
    assert manifest["approval"]["record"]["path"] == "prototype/discussion.md"
    # Freezing a design scope never claims implementation was exercised.
    assert manifest["implementation_validation"] == {
        "implementation": "pending", "platform": "pending", "production": "pending"}

    admitted = handoff.downstream_admission(tmp_path, "reader")
    assert admitted["gate"] == "passed"
    assert admitted["admission"] == "bound_to_frozen_revision"
    assert admitted["implementation_validation"]["production"] == "pending"


def test_spec_only_approval_retains_design_scope(tmp_path: Path):
    spec = _build_root(tmp_path, decision_row=SPEC_ONLY_ROW)
    manifest = handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    assert manifest["authority_status"] == "frozen_approved"
    assert manifest["approval"]["spec_only"] is True
    assert set(manifest["implementation_validation"].values()) == {"pending"}
    # Retaining the design scope requires no prototype HTML beyond the entry the
    # strict packet already validated.
    assert handoff.check_downstream_gate(tmp_path, "reader")["gate"] == "passed"


# --- CPC-SCN-014: false approval and stale content are rejected --------------

@pytest.mark.parametrize("row", [PLANNED_ROW, NEGATED_ROW, NO_DECISION_ROW])
def test_planned_or_negated_approval_never_freezes(tmp_path: Path, row: str):
    spec = _build_root(tmp_path, decision_row=row)
    before = _html_snapshot(tmp_path)

    with pytest.raises(handoff.HandoffError, match="no actual approval"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    # Existing artifacts remain intact on rejection.
    assert _html_snapshot(tmp_path) == before
    assert not (tmp_path / "prototype/evidence/reader/r1/freeze-manifest.json").exists()
    assert "Compilation status: candidate" in spec.read_text(encoding="utf-8")


def test_approval_less_override_cannot_manufacture_frozen_status(tmp_path: Path):
    spec = _build_root(tmp_path, decision_row=NO_DECISION_ROW)
    before = _html_snapshot(tmp_path)

    with pytest.raises(handoff.HandoffError):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert _html_snapshot(tmp_path) == before

    # No forced or permissive admission form survives on the CLI.
    sys.argv = ["handoff.py", "freeze", "--root", str(tmp_path),
                "--spec", "prototype/specifications/reader/r1.md", "--force"]
    with pytest.raises(SystemExit):
        handoff.main()


def test_stale_source_digest_stays_failed(tmp_path: Path):
    spec = _build_root(tmp_path)
    (tmp_path / "prototype/product.md").write_text("# Tampered Product\n", encoding="utf-8")

    with pytest.raises(handoff.HandoffError, match="Digest mismatch"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert not (tmp_path / "prototype/evidence/reader/r1/freeze-manifest.json").exists()


def test_malformed_strict_packet_does_not_downgrade(tmp_path: Path):
    spec = _build_root(tmp_path)
    body = spec.read_text(encoding="utf-8").replace("- Disposition: ready\n", "")
    # Break a strict reference field so the packet cannot be compiled at all.
    spec.write_text(body.replace("- Slice Contract revision and digest:",
                                 "- Slice Contract revision and digest: "), encoding="utf-8")
    (tmp_path / "prototype/contracts/slices/reader/c1.md").write_text(
        "# Contract\n- Slice ID: reader\n- Contract revision: c1\n- Foundation revision: f1\n"
        "- Retained surface-map path, revision and digest: `prototype/contracts/surface-maps/m1.md`, "
        + _sha256((tmp_path / "prototype/contracts/surface-maps/m1.md").read_bytes()) + "\n",
        encoding="utf-8")

    with pytest.raises(handoff.HandoffError):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert not (tmp_path / "prototype/evidence/reader/r1/freeze-manifest.json").exists()


def test_malformed_freeze_manifest_is_refused_not_downgraded(tmp_path: Path):
    spec = _build_root(tmp_path)
    handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())

    manifest_path = tmp_path / "prototype/evidence/reader/r1/freeze-manifest.json"
    manifest_path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(handoff.HandoffError, match="malformed"):
        handoff.check_downstream_gate(tmp_path, "reader")

    # A well-formed manifest lacking frozen authority is refused too.
    manifest_path.write_text(json.dumps({"status": "sealed"}), encoding="utf-8")
    with pytest.raises(handoff.HandoffError, match="frozen_approved"):
        handoff.check_downstream_gate(tmp_path, "reader")


def test_changed_content_after_freeze_invalidates_admission(tmp_path: Path):
    spec = _build_root(tmp_path)
    handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())
    assert handoff.downstream_admission(tmp_path, "reader")["gate"] == "passed"

    (tmp_path / "prototype/discussion.md").write_text(
        _decision_block(NO_DECISION_ROW), encoding="utf-8")
    with pytest.raises(handoff.HandoffError, match="changed after freeze"):
        handoff.downstream_admission(tmp_path, "reader")


def test_freeze_rejects_less_privileged_scope_entry(tmp_path: Path):
    spec = _build_root(tmp_path)
    (tmp_path / "prototype/experiments/reader/r1/index.html").unlink()
    with pytest.raises(handoff.HandoffError, match="no HTML entry"):
        handoff.freeze(tmp_path, spec.relative_to(tmp_path).as_posix())


# --- execution boundary: no permissive freeze form survives ------------------

def test_boundary_refuses_force_flag_and_foreign_root(tmp_path: Path):
    active = tmp_path / "project-a"
    foreign = tmp_path / "project-b"
    active.mkdir()
    foreign.mkdir()
    (active / "prototype").mkdir()
    (active / "prototype/discussion.md").write_text(
        "- Execution boundary: active\n", encoding="utf-8")

    def event(command: str) -> dict:
        return {"cwd": str(active), "tool_name": "Bash", "tool_input": {"command": command}}

    forced = f"python3 {SCRIPTS}/handoff.py freeze --root {active} --spec prototype/specifications/reader/r1.md --force"
    with pytest.raises(ValueError, match="no force/permissive form"):
        boundary.check(event(forced))

    foreign_root = f"python3 {SCRIPTS}/handoff.py freeze --root {foreign} --spec dummy.md"
    with pytest.raises(ValueError, match="active discussion root"):
        boundary.check(event(foreign_root))

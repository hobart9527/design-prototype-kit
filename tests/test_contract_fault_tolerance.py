"""CRR-001/CRR-SCN-001/CRR-SCN-002: format-tolerant parsing and advisory digest.

Mechanism checks over authored contract text and the formal admission seam.
Not real-session evidence.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import lint_spec_contracts  # noqa: E402
import prototype_context  # noqa: E402

SLICE = "console"
SELECTION_SOURCE = "prototype/discussion/scope-r7.md"
SURFACES = [f"S{i}-{name}" for i, name in enumerate(
    ["feed", "detail", "compose", "queue", "history", "settings",
     "billing", "members", "audit", "help"], start=1)]

# A digest that belongs to some earlier retained map revision, never to the map.
FOREIGN_DIGEST = hashlib.sha256(b"an earlier retained map revision\n").hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def map_text(revision: str = "r7") -> str:
    return ("# Product Surface Map\n\n"
            "```prototype-context\n"
            "record: surface-map\n"
            f"revision: {revision}\n"
            "coverage: selected\n"
            f"selection-source: {SELECTION_SOURCE}\n"
            "surfaces: " + ", ".join(SURFACES) + "\n"
            "selected-surfaces: S1-feed, S2-detail, S3-compose\n"
            "```\n")


def retained_text(revision: str, digest: str) -> str:
    return (f"- Surface Map revision: {revision}\n"
            f"- Surface Map digest: sha256:{digest}\n")


def build_repo(tmp_path: Path, *, map_revision: str = "r7",
               retained_revision: str = "r7", digest: str = FOREIGN_DIGEST) -> Path:
    write(tmp_path / "prototype/contracts/surface-maps/m1.md", map_text(map_revision))
    write(tmp_path / SELECTION_SOURCE, retained_text(retained_revision, digest))
    return tmp_path


# CRR-SCN-001: formatted context parsing resilience.

def test_whitespace_comments_bullets_and_list_punctuation_parse():
    text = ("```prototype-context\n"
            "record: surface-map\n"
            "revision :   r7     # drafted, not yet approved\n"
            "- coverage:    selected\n"
            "selected-surfaces: S1-feed; S2-detail | `S3-compose`   # three\n"
            "platform-contexts: web; android\n"
            "```\n")
    section = prototype_context.parse_section(text)
    assert section["record"] == "surface-map"
    assert section["revision"] == "r7"
    assert section["coverage"] == "selected"
    assert section["selected_surfaces"] == ["S1-feed", "S2-detail", "S3-compose"]
    assert section["platform_contexts"] == ["web", "android"]


def test_comment_only_values_stay_empty_and_casing_normalizes():
    text = ("```prototype-context\n"
            "Record: surface-map\n"
            "Revision: r7\n"
            "Coverage:    # left for the selection record\n"
            "```\n")
    section = prototype_context.parse_section(text)
    assert section["record"] == "surface-map"
    assert section["coverage"] == ""


def test_tolerated_formatting_reaches_read_context_without_errors():
    doc = ("# Product Surface Map\n\n```prototype-context\n"
           "record: surface-map\n"
           "revision:   r7   # draft\n"
           "coverage: selected\n"
           "selection-source: prototype/discussion/scope-r7.md  # retained\n"
           "surfaces: " + ", ".join(SURFACES) + "\n"
           "selected-surfaces: S1-feed, S2-detail, S3-compose\n"
           "```\n")
    ctx = prototype_context.read_context(doc)
    assert ctx["surface_map"]["revision"] == "r7"
    assert ctx["surface_map"]["selection_source"] == "prototype/discussion/scope-r7.md"
    assert ctx["errors"] == []


# CRR-SCN-002: a matching revision admits dispatch; the digest difference is advisory.

def test_matching_revision_with_differing_digest_is_advisory(tmp_path):
    root = build_repo(tmp_path, digest=FOREIGN_DIGEST)
    failures = lint_spec_contracts.lint_formal_entry(root, SLICE)
    assert not [f for f in failures if f.rule == "E010_STALE_CONTRACT"]

    advisories = lint_spec_contracts.lint_formal_advisories(root, SLICE)
    assert [a.severity for a in advisories] == ["WARNING"]
    assert "digest" in str(advisories[0])

    context = lint_spec_contracts.read_formal_context(root, SLICE)
    assert not [e for e in context["errors"] if e["code"] == "stale_map_identity"]
    assert [d["code"] for d in context["diagnostics"]] == ["advisory_map_digest"]


def test_matching_revision_and_matching_digest_adds_no_diagnostic(tmp_path):
    root = build_repo(tmp_path)
    actual = hashlib.sha256(
        (root / "prototype/contracts/surface-maps/m1.md").read_bytes()).hexdigest()
    write(root / SELECTION_SOURCE, retained_text("r7", actual))
    assert lint_spec_contracts.lint_formal_advisories(root, SLICE) == []
    context = lint_spec_contracts.read_formal_context(root, SLICE)
    assert not [e for e in context["errors"] if e["code"] == "stale_map_identity"]
    assert context["diagnostics"] == []


# A differing logical revision still owns the blocking refusal.

def test_mismatched_revision_still_triggers_e010(tmp_path):
    root = build_repo(tmp_path, map_revision="r7", retained_revision="r6")
    failures = lint_spec_contracts.lint_formal_entry(root, SLICE)
    stale = [f for f in failures if f.rule == "E010_STALE_CONTRACT"]
    assert stale, "a differing logical revision must stay a blocking refusal"
    assert "revision" in stale[0].message
    assert "'r7'" in stale[0].message and "'r6'" in stale[0].message
    assert lint_spec_contracts.lint_formal_advisories(root, SLICE) == []


def test_mismatched_revision_with_matching_digest_is_not_admitted(tmp_path):
    """A digest that happens to agree never rescues a differing revision."""
    root = build_repo(tmp_path, map_revision="r7", retained_revision="r6")
    actual = hashlib.sha256(
        (root / "prototype/contracts/surface-maps/m1.md").read_bytes()).hexdigest()
    write(root / SELECTION_SOURCE, retained_text("r6", actual))
    failures = lint_spec_contracts.lint_formal_entry(root, SLICE)
    assert [f.rule for f in failures if f.rule == "E010_STALE_CONTRACT"]
    context = lint_spec_contracts.read_formal_context(root, SLICE)
    assert "revision" in [e.get("identity") for e in context["errors"]
                          if e["code"] == "stale_map_identity"]

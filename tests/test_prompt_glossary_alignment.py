"""Prompt prose and the controlled glossary stay one vocabulary.

The same concept drifted across the Skill, the agent prompts and the benchmark
judge prompts because `authority` names several distinct registers and the
evidence ladder is a fourth. Each check here pins one register to its schema or
its owning prose, so a synonym inserted in one file fails against the file that
owns the meaning.
"""
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/spec-prototype"
AGENTS = REPO / "agents"
PROMPTS = REPO / "benchmarks" / "prompts"

sys.path.insert(0, str(SKILL / "scripts"))
import detect  # noqa: E402


def _skill_prose() -> str:
    parts = [SKILL / "SKILL.md", SKILL / "CONTEXT.md"]
    parts += sorted((SKILL / "references").rglob("*.md"))
    parts += sorted(AGENTS.glob("*.md"))
    return "\n".join(p.read_text(encoding="utf-8") for p in parts if p.is_file())


def _schema() -> dict:
    return json.loads((SKILL / "schemas" / "prototype-spec.v1.json").read_text(encoding="utf-8"))


def _judge_prompt_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in PROMPTS.glob("*.txt"))


# --- the four registers stay distinct -------------------------------------

SPEC_AUTHORITY = ["draft", "sealed_provisional", "validated", "frozen_approved"]
ACTION_AUTHORITY = ["explicit", "derived", "proposed", "hypothesis"]
EVIDENCE_LADDER = ["explicit", "observed", "derived", "hypothesis", "unknown"]


def test_the_four_registers_are_named_where_they_are_owned():
    """Each register is stated once and the others do not borrow its values."""
    prose = _skill_prose()
    for term in SPEC_AUTHORITY:
        assert f"`{term}`" in prose, f"spec identity authority value {term} is not stated"
    for term in ACTION_AUTHORITY:
        assert f"`{term}`" in prose, f"action evidence authority value {term} is not stated"


def test_action_evidence_authority_matches_the_schema_enum():
    """Prose and schema agree on the action register; a synonym is a drift."""
    schema_enum = _schema()["properties"]["actions"]["items"]["properties"]["authority"]["enum"]
    assert schema_enum == ACTION_AUTHORITY, (
        f"actions[].authority enum drifted: {schema_enum} != {ACTION_AUTHORITY}"
    )


def test_spec_identity_authority_matches_the_schema_enum():
    """`identity.authority_status` is the slice-spec register, not the action one."""
    schema_enum = _schema()["properties"]["identity"]["properties"]["authority_status"]["enum"]
    assert schema_enum == SPEC_AUTHORITY, (
        f"identity.authority_status enum drifted: {schema_enum} != {SPEC_AUTHORITY}"
    )


def test_evidence_ladder_matches_the_judges_and_the_kernel():
    """The ladder is one string in core-kernel.md and the judge prompt reads it."""
    ladder = "explicit > observed > derived > hypothesis > unknown"
    kernel = (SKILL / "references" / "core-kernel.md").read_text(encoding="utf-8")
    assert ladder in kernel, "core-kernel.md no longer states the evidence ladder verbatim"
    judge = (PROMPTS / "semantic-judge.txt").read_text(encoding="utf-8")
    assert ladder in judge, (
        "semantic-judge.txt and core-kernel.md state the ladder differently; "
        "the judge reads evidence status by this exact ordering"
    )


# --- the same string owns the same meaning --------------------------------

def test_canonical_ir_is_named_consistently():
    """`Spec IR` and `canonical IR` are one artifact; the prose says so."""
    prose = _skill_prose()
    assert "Spec IR" in prose
    assert "canonical IR" in prose
    # A second, competing name for the compiled artifact would be the drift this
    # test exists to catch; `Execution Envelope` is not a term the tree uses.
    assert "Execution Envelope" not in prose, (
        "`Execution Envelope` is not a real term in this tree; use `Spec IR` / `canonical IR`"
    )


def test_craft_floor_rule_ids_are_not_silently_renamed():
    """The floor ids are the join between prose and detect.py; both directions."""
    floor = (SKILL / "references" / "02-craft-methods" / "craft-floor.md").read_text(encoding="utf-8")
    floor_flat = re.sub(r"\s+", " ", re.sub(r"\*\*|`", "", floor))
    missing = sorted(rid for rid in detect.RULES if rid not in floor_flat)
    assert not missing, f"craft-floor.md stopped naming registered rule ids: {missing}"

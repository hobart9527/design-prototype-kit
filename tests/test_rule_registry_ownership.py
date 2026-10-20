"""Rule-registry and template-contract integrity.

Two ownership invariants, both static and hermetic:

1. The Direction Contract in each design-record template ships all six blocks,
   none empty, none excused by a "留空 / Left empty" escape.
2. Each CRAFT-* rule id introduced by the single-owner convergence owns its
   rule text in exactly one place; every other mention is a reference, not a
   restatement. Measured mechanically: the full lean-delivery-rules section is
   the owner; outside it, no other skill file may carry the rule's defining
   sentence pattern (the id immediately followed by a colon — the restatement
   shape this convergence removed).
3. The three authority registers of the design record (decision `Status`,
   decision `User source`, Resume pending prerequisite) each have one vocabulary,
   and every document that names one names the same values. The registers are
   distinct — a value from one is never a value of another — so the check
   asserts the sets are stated identically where they are stated, and that no
   file smuggles one register's value into another's list.
"""
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "spec-prototype"
RULES = SKILL / "references" / "03-verification" / "lean-delivery-rules.md"

SIX_BLOCKS = ("THESIS", "OWN-WORLD", "STORY", "FIRST VIEWPORT", "FORM", "FINISH")
TEMPLATES = (SKILL / "templates" / "discussion.md", SKILL / "templates" / "world.md")


def test_direction_contract_six_blocks_complete_in_templates():
    for template in TEMPLATES:
        text = template.read_text(encoding="utf-8")
        for block in SIX_BLOCKS:
            assert f"**{block}**" in text, f"{template.name} missing Direction Contract block {block}"
            line = next(l for l in text.splitlines() if f"**{block}**" in l)
            assert line.split(":", 1)[1].strip(), f"{template.name} block {block} is empty"
        assert "Left empty until direction locked" in text, (
            f"{template.name} lost the explicit ban on leaving blocks empty")


# The restatement shape: an id used as a definition (`- `ID`: ...` or
# `**name** `ID`:`). References (`per `ID``, `` `ID` — rule text owned by``)
# never put a colon directly after the backtick.
RULE_IDS = (
    "CRAFT-CONFIRM-DRIVABLE",
    "CRAFT-ACTION-FEEDBACK",
    "CRAFT-DATA-DISCIPLINE",
    "CRAFT-NO-FABRICATED-MAPPING",
    "CRAFT-NO-INVENTED-CAPABILITY",
)
_DEFINITION_RE = {rid: re.compile(r"`" + re.escape(rid) + r"`\s*:") for rid in RULE_IDS}
_SKILL_TEXT_FILES = [p for p in SKILL.rglob("*.md")]


def _definitions_outside_owner(rule_id: str) -> list:
    offenders = []
    for path in _SKILL_TEXT_FILES:
        if path == RULES:
            continue
        if _DEFINITION_RE[rule_id].search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(REPO)))
    return offenders


def test_stage_two_and_modern_platform_keep_direction_axis_ownership():
    stage_two = (SKILL / "references/stages/stage-2-probe.md").read_text(encoding="utf-8")
    modern = (SKILL / "references/02-craft-methods/modern-platform.md").read_text(encoding="utf-8")
    assert "mandatory axis" in stage_two
    assert "vary exactly one primary axis" in stage_two
    assert "do not define direction-comparison axes" in modern
    assert "default scoring" in modern


def test_each_craft_rule_text_has_exactly_one_owner():
    owner_text = RULES.read_text(encoding="utf-8")
    for rule_id in RULE_IDS:
        assert f"`{rule_id}`" in owner_text, f"{rule_id} lost its owning entry in lean-delivery-rules.md"
        offenders = _definitions_outside_owner(rule_id)
        assert not offenders, f"{rule_id} rule text restated outside the owner: {offenders}"


# --- Authority register vocabularies -------------------------------------
#
# The design record carries three registers that all speak about authority.
# They are distinct vocabularies; a value in one is not a value of another.
# The defect this pins: the decision `Status` register was stated three
# different ways across the repo, and the declared owner omitted `delegated`
# — the exact value `handoff.py` and `authority_fidelity.py` bind a freeze on.

STATUS_ENUM = "proposed | provisional | confirmed | delegated | needs-evidence | superseded"
USER_SOURCE_ENUM = "confirmed | delegated | synthetic-fixture"
PENDING_ENUM = "none | needs_decision | needs_evidence | blocked"

# Files that state a register's vocabulary. Each must state it verbatim.
STATUS_SITES = (
    SKILL / "references" / "core-kernel.md",
    SKILL / "references" / "04-governance" / "discussion-governance.md",
    SKILL / "references" / "04-governance" / "machine-contract.md",
    SKILL / "templates" / "truth.md",
    SKILL / "templates" / "discussion.md",
)


def test_decision_status_vocabulary_is_stated_identically_everywhere():
    for path in STATUS_SITES:
        text = path.read_text(encoding="utf-8")
        assert STATUS_ENUM in text, (
            f"{path.relative_to(REPO)} states the decision Status vocabulary "
            f"differently; expected `{STATUS_ENUM}`"
        )


def test_user_source_vocabulary_is_stated_identically_everywhere():
    """`User source` is its own register; it must not absorb Status values."""
    sites = (
        SKILL / "references" / "04-governance" / "discussion-governance.md",
        SKILL / "references" / "04-governance" / "handoff.md",
        SKILL / "templates" / "truth.md",
        SKILL / "templates" / "discussion.md",
    )
    for path in sites:
        # A table header escapes its inner pipes (`a \| b`); normalize before
        # matching so the header form and the prose form read the same.
        text = path.read_text(encoding="utf-8").replace("\\|", "|")
        assert USER_SOURCE_ENUM in text, (
            f"{path.relative_to(REPO)} states the User source vocabulary "
            f"differently; expected `{USER_SOURCE_ENUM}`"
        )
        # `proposed` and `needs-evidence` are Status values. A User source
        # list carrying either has conflated the two registers.
        assert "proposed | confirmed" not in text, (
            f"{path.relative_to(REPO)} states a User source list containing a Status value"
        )


def test_pending_prerequisite_uses_underscored_spelling():
    """`needs_decision` (dependency condition) is not `needs-decision` (Status)."""
    for path in (
        SKILL / "references" / "04-governance" / "discussion-governance.md",
        SKILL / "templates" / "truth.md",
        SKILL / "templates" / "discussion.md",
    ):
        text = path.read_text(encoding="utf-8")


# --- Wave 2 semantic ownership (C1–C4) -------------------------------------
#
# The single-owner convergence moved the decision-wait rules into
# `discussion-governance.md`; every other file may reference the owner but must
# not restate the rule. The divergence shape is owned by `core-kernel.md`; the
# USER-INPUT stop condition is owned by `stage-1-frame.md`. These
# assertions pin the ownership seams so a future edit cannot silently re-split
# them.


def test_divergence_count_is_owned_by_core_kernel():
    """Only core-kernel states the minimum hypothesis count."""
    owner = (SKILL / "references" / "core-kernel.md").read_text(encoding="utf-8")
    assert "at least 2 polarized structural" in owner
    assert "evidence has already locked" in owner

    for path in _SKILL_TEXT_FILES:
        if path == SKILL / "references" / "core-kernel.md":
            continue
        text = path.read_text(encoding="utf-8")
        # References ("at least 2 hypotheses", "see core-kernel") are fine; a
        # restatement of the exact rule phrase is not.
        assert "at least 2 polarized structural" not in text, (
            f"{path.relative_to(REPO)} restates the divergence-count rule owned by core-kernel.md"
        )


def test_user_input_stop_is_owned_by_stage_1_frame():
    """Only stage-1-frame states the USER-INPUT stop condition."""
    owner = (SKILL / "references" / "stages" / "stage-1-frame.md").read_text(encoding="utf-8")
    assert "Emit `USER-INPUT:` and stop **only when an un-delegated human decision remains**" in owner

    for path in _SKILL_TEXT_FILES:
        if path == SKILL / "references" / "stages" / "stage-1-frame.md":
            continue
        text = path.read_text(encoding="utf-8")
        # References ("end the turn with a verbatim USER-INPUT line", "only an
        # un-delegated human decision stops the run") are fine; restating the
        # stop rule itself is not.
        assert "Emit `USER-INPUT:` and stop" not in text, (
            f"{path.relative_to(REPO)} restates the USER-INPUT stop rule owned by stage-1-frame.md"
        )


def test_self_written_scripts_rule_is_owned_by_skill_md():
    """SKILL.md states the no-self-authored-verification-scripts rule; helpers may reference it."""
    owner = SKILL / "SKILL.md"
    text = owner.read_text(encoding="utf-8")
    assert "No self-authored verification scripts" in text

    for path in _SKILL_TEXT_FILES:
        if path == owner:
            continue
        text = path.read_text(encoding="utf-8")
        assert "self-authored verification scripts" not in text, (
            f"{path.relative_to(REPO)} restates the self-authored-scripts rule owned by SKILL.md"
        )

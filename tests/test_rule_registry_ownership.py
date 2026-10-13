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


def test_each_craft_rule_text_has_exactly_one_owner():
    owner_text = RULES.read_text(encoding="utf-8")
    for rule_id in RULE_IDS:
        assert f"`{rule_id}`" in owner_text, f"{rule_id} lost its owning entry in lean-delivery-rules.md"
        offenders = _definitions_outside_owner(rule_id)
        assert not offenders, f"{rule_id} rule text restated outside the owner: {offenders}"

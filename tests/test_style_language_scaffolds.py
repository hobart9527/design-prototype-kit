"""P0 creative scaffolds: style language, reference deconstruction, levers, critique."""
from pathlib import Path
import subprocess
import sys

SKILL = Path(__file__).resolve().parents[1] / "skills/spec-prototype"
REFS = SKILL / "references"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_style_language_card_has_its_four_parts_and_tests():
    text = _read(REFS / "01-foundations/style-language.md")
    for part in ("Positions", "Vocabulary", "Counter-examples", "Signature"):
        assert part in text
    for test in ("Cover test", "Transfer test", "Cost test"):
        assert test in text


def test_world_template_carries_the_card_and_deconstruction_table():
    world = _read(SKILL / "templates/world.md")
    assert "## Style Language" in world and "## Reference Deconstruction" in world


def test_owners_link_to_the_new_references():
    assert "style-language.md" in _read(REFS / "stages/stage-1-frame.md")
    assert "style-language.md" in _read(REFS / "stages/stage-4-audit.md")
    assert "reference-deconstruction.md" in _read(REFS / "dialectic/01-metaphor-benchmark.md")


def test_generator_names_levers_and_keeps_structure_mandatory():
    text = " ".join(_read(REFS / "dialectic/01-metaphor-benchmark.md").split())
    assert "Creative levers" in text
    assert "Structure must be one of them" in text
    assert "expression axis" in text


def test_stage2_has_expression_study_and_blind_critique_without_a_gate():
    text = " ".join(_read(REFS / "stages/stage-2-probe.md").split())
    assert "Expression study" in text and "Blind critique" in text
    assert "never a gate" in text


def test_taste_statement_is_judgment_not_a_finding():
    text = _read(REFS / "stages/stage-4-audit.md")
    assert "Taste Statement" in text and "[taste]" in text
    assert "Taste is not evidence" in text


def test_every_challenger_entry_has_a_bar_and_is_drawable(tmp_path):
    vocab = REFS / "02-craft-methods/modern-style-vocabulary.md"
    text = _read(vocab)
    entries = text.count("\n### ") - text.count("\n### Sampling")
    assert entries >= 10
    assert text.count("QUALITY BAR") >= entries
    sys.path.insert(0, str(SKILL / "scripts"))
    import draw_seed
    assert len(draw_seed.load_challengers(vocab)) >= 10

"""P0 creative scaffolds: style language, reference deconstruction, levers, critique."""
from pathlib import Path
import subprocess
import sys

SKILL = Path(__file__).resolve().parents[1] / "skills/spec-prototype"
REFS = SKILL / "references"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_style_language_card_has_its_four_parts_and_tests():
    text = _read(REFS / "01-foundations/design-language.md")
    for part in ("Positions", "Vocabulary", "Counter-examples", "Signature"):
        assert part in text
    for test in ("Cover test", "Transfer test", "Cost test"):
        assert test in text


def test_world_template_carries_the_card_and_drops_the_duplicated_tables():
    """The card's four parts live in the world template; the reference tables do not.

    The Reference Deconstruction table and the Taste Ledger were a second place to
    record what truth.md's Reference Benchmarks and the `### Divergence` block
    already own. They are gone; the card stays.
    """
    world = _read(SKILL / "templates/world.md")
    for part in ("Positions", "Vocabulary", "Counter-examples", "Signature"):
        assert part in world, f"world.md lost the card part {part}"
    assert "## Reference Deconstruction" not in world
    assert "## Project Taste & Visual Language Ledger" not in world


def test_owners_link_to_the_new_references():
    """The card and the deconstruction method live in design-language.md now."""
    assert "design-language.md" in _read(REFS / "stages/stage-1-frame.md")
    assert "design-language.md" in _read(REFS / "stages/stage-4-audit.md")
    assert "design-language.md" in _read(REFS / "dialectic/01-metaphor-benchmark.md")
    assert "design-language.md" in _read(REFS / "stages/stage-2-probe.md")


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


def test_draw_seed_samples_by_archetype_while_preserving_default():
    vocab = REFS / "02-craft-methods/modern-style-vocabulary.md"
    sys.path.insert(0, str(SKILL / "scripts"))
    import draw_seed

    challengers = draw_seed.load_challengers(vocab)
    # Default without archetype
    default_picks = draw_seed.draw(3, challengers)
    assert len(default_picks) == 3
    assert all("Challenger" in p for p in default_picks)

    # Guided by archetype: every draw comes from the resolved pool, not the full set.
    pool = draw_seed._filter_challengers_by_archetype(challengers, "dense-workbench")
    assert pool != challengers
    assert len(pool) >= 3
    workbench_picks = draw_seed.draw(3, challengers, archetype="dense-workbench")
    assert len(workbench_picks) == 3
    wb_challenger_names = [p["Challenger"] for p in workbench_picks]
    assert len(set(wb_challenger_names)) == 3
    assert set(wb_challenger_names) <= set(pool)

    # An archetype name outside the vocabulary keeps the full pool instead of guessing.
    assert draw_seed._filter_challengers_by_archetype(challengers, "unmapped-thing") == challengers

    # Render block includes archetype note when supplied
    block = draw_seed.render_block(workbench_picks, archetype="dense-workbench")
    assert "dense-workbench" in block
    assert "### Divergence seeds" in block

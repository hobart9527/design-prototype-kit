"""Pins for the executable spine: Nine Pillars × Double Diamond × Five Axes.

The spine was all declaration: Double Diamond's Develop phase had no divergence
generator and its Deliver phase no convergence arbiter, so exploration collapsed
back to a fixed style menu and convergence was the model's own call. These pins
hold the mechanisms that make the spine execute, so a later edit cannot quietly
revert them to prose.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/spec-prototype"
REFS = SKILL / "references"

STAGE1 = REFS / "stages/stage-1-frame.md"
STAGE2 = REFS / "stages/stage-2-probe.md"
KERNEL = REFS / "core-kernel.md"
LANGUAGE = REFS / "01-foundations/design-language.md"
GENERATOR = REFS / "dialectic/01-metaphor-benchmark.md"
VOCABULARY = REFS / "02-craft-methods/modern-style-vocabulary.md"


def _read(path: Path) -> str:
    """Prose with emphasis markers dropped and whitespace collapsed.

    These pins assert *substance*; a sentence re-wrapped or a phrase half-bolded
    is a formatting change, not a contract change, and must not fail a pin.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\*\*|`", "", text)
    return re.sub(r"\s+", " ", text)


# -- Five Axes: required at lock, never silent ---------------------------------

def test_five_axes_are_required_at_direction_lock_not_optional():
    stage1 = _read(STAGE1)
    assert "All five axes" in stage1
    assert "accounted for at direction" in stage1
    assert "Five Axes are optional" not in stage1, \
        "an optional register is indistinguishable from a model default"
    assert "open" in stage1, "an unsettled axis must have a recorded outcome"


def test_kernel_forbids_the_silent_axis():
    kernel = _read(KERNEL)
    assert "required at direction lock" in kernel
    assert "open" in kernel, "the kernel must allow an explicit open axis"


def test_axis_without_evidence_stays_open_rather_than_invented():
    language = _read(LANGUAGE)
    assert "invalid derivation" in language
    assert "open" in language, \
        "an axis the evidence does not settle is recorded open, not filled"


# -- Innovation budget modulated by mode ---------------------------------------

def test_mode_modulates_the_innovation_budget():
    stage1 = _read(STAGE1)
    for mode in ("Operate", "Read", "Persuade", "Experience"):
        assert mode in stage1, f"mode {mode} missing from the budget table"
    assert "80 / 20" in stage1 and "60 / 40" in stage1
    assert "name the mode per surface" in stage1, \
        "a multi-mode product must not average its surfaces into one number"


# -- Divergence Generator: Double Diamond / Develop ----------------------------

def test_divergence_generator_owns_the_develop_phase():
    text = _read(GENERATOR)
    assert "## 4. Divergence Generator" in text
    assert "Owner: Double Diamond / Develop" in text
    for step in ("Name the rut", "Generate from the lifeworld", "Assign seeds",
                 "Fuse a challenger", "Two-axis verdict", "Donate the loser"):
        assert step in text, f"generator step missing: {step}"


def test_divergence_generator_sources_from_the_domain_not_the_catalog():
    text = _read(GENERATOR)
    assert "challenger source, not the generator" in text
    assert "two draws from one distribution" in text
    # Palette alone is never an axis: that is the failure the divergence judge catches.
    assert "Palette alone is never an axis" in text
    assert "fewer than two axes" in text


def test_style_vocabulary_is_a_challenger_source_with_quality_bars():
    text = _read(VOCABULARY)
    assert "challenger source, not a direction menu" in text
    assert "QUALITY BAR" in text
    # Every vocabulary entry carries a bar, not just techniques.
    assert text.count("QUALITY BAR") >= 5, \
        "each vocabulary needs a bar separating a fused technique from a costume"


def test_stage2_executes_the_generator_before_authoring():
    stage2 = _read(STAGE2)
    assert "Diverge before authoring" in stage2
    assert "two-axis verdict" in stage2
    assert "divergence judge" in stage2, \
        "the prose verdict is re-checked on the built slots"
    assert "challenger source, not a direction menu" in stage2


# -- Direction Contract is the chain, compressed -------------------------------

def test_direction_contract_is_the_compressed_causal_chain():
    language = _read(LANGUAGE)
    assert "## Direction Contract" in language
    assert "is this chain, compressed" in language
    for block in ("THESIS", "OWN-WORLD", "STORY", "FIRST VIEWPORT", "FORM", "FINISH"):
        assert block in language, f"contract block missing: {block}"
    # Steps 6 and 7 stay in the record; their absence is not permission to skip them.
    assert "no block" in language
    assert "not locked" in language


def test_contract_blocks_match_the_fidelity_judge():
    """The contract the Skill declares and the contract the judge reads are one list."""
    sys.path.insert(0, str(REPO / "benchmarks" / "judges"))
    import contract_fidelity_judge as cfj  # noqa: E402
    language = _read(LANGUAGE)
    for block in cfj.BLOCKS:
        assert block in language, f"judge block {block} is not declared by the Skill"

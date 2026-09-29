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

# -- P3: the build loop closes ------------------------------------------------

AUDIT = REFS / "stages/stage-4-audit.md"
REVIEW_TEMPLATE = SKILL / "templates/prototype-review.md"
METHODS = REFS / "01-foundations/design-methods.md"


def test_default_recipes_live_in_the_techniques_column():
    """A number belongs in the Techniques column; the Invariants column stays invariant."""
    methods = _read(METHODS)
    assert "--press-scale: 0.96" in methods, \
        "the press detent needs a default recipe, not just a shape"
    assert "Default recipe" in methods
    # The override rule: a recipe is a starting point, and an unstated default is
    # indistinguishable from an unmade choice.
    assert "starting points, not house numbers" in methods
    assert "reason in the brief" in methods


def test_the_review_reads_the_render_against_the_contract():
    audit = _read(AUDIT)
    assert "Read the render against the Direction Contract" in audit
    for block in ("THESIS", "OWN-WORLD", "STORY", "FIRST VIEWPORT", "FORM", "FINISH"):
        assert block in audit, f"the contract read does not check {block}"
    # A declared block that is not observable is a build finding, not a contract edit.
    assert "not the contract" in audit
    assert "not amend the contract to match what got built" in audit


def test_inspection_is_capped_at_two_batched_rounds():
    audit = _read(AUDIT)
    assert "Two batched inspection rounds" in audit
    assert "Round one" in audit and "Round two" in audit
    assert "record what remains open as a PARTIAL finding" in audit, \
        "an uncapped review never ends; the cap must name its exit"


def test_the_review_is_organised_by_pillar_with_unreviewed_named():
    audit = _read(AUDIT)
    assert "organised by Pillar" in audit
    for pillar in ("Value", "Research", "Object", "Journey", "Topology",
                   "Attention", "Expression", "Interaction", "Resilience"):
        assert pillar in audit, f"the pillar table omits {pillar}"
    assert "not reviewed" in audit
    assert "not a pass" in audit, \
        "an unreviewed pillar must not read as covered"


def test_review_template_carries_a_row_for_every_pillar():
    template = _read(REVIEW_TEMPLATE)
    assert "Pillar coverage" in template
    for pillar in ("Value", "Research", "Object", "Journey", "Topology",
                   "Attention", "Expression", "Interaction", "Resilience"):
        assert f"| {pillar} |" in template, f"the review template has no row for {pillar}"
    assert "Findings" in template
    # A finding names its owning pillar, so the same observation is filed once.
    assert "| Concern and location/state | Pillar |" in template

# -- P4: operators are single-axis moves --------------------------------------

OPERATORS = REFS / "operators.md"

OPERATOR_TABLE = ("bolder", "quieter", "distill", "typeset", "colorize",
                  "animate", "layout", "harden", "clarify")


def test_every_refine_operator_is_a_single_axis_move():
    operators = _read(OPERATORS)
    for name in OPERATOR_TABLE:
        assert f"| {name} |" in operators, f"operator missing from the table: {name}"
    # Each operator carries the four fields that make the delta reviewable.
    for field in ("Target", "From → To", "Held constant", "Falsifier"):
        assert field in operators, f"operator contract omits {field}"


def test_operators_speak_the_spine_language_not_a_house_style():
    """`bolder` is a move on Energy, not a mood — the target column says so."""
    operators = _read(OPERATORS)
    for axis in ("Density", "Energy", "Materiality", "Rhythm", "Character"):
        assert axis in operators, f"operator targets never name the {axis} axis"
    for pillar in ("Topology", "Resilience", "Value", "Journey"):
        assert pillar in operators, f"operator targets never name the {pillar} pillar"


def test_one_operator_per_pass_and_the_floor_never_trades():
    operators = _read(OPERATORS)
    assert "One operator per pass" in operators
    assert "The craft floor is not an axis and never trades against one" in operators


def test_a_move_that_cannot_name_its_target_is_a_redirection():
    """The boundary between refine and diverge must be stated, not implied."""
    operators = _read(OPERATORS)
    assert "it is a redirection, and" in operators
    assert "divergence generator" in operators


def test_variant_varies_exactly_one_axis():
    operators = _read(OPERATORS)
    for axis in ("Structure", "Density", "Emphasis", "Type", "Voice"):
        assert f"| {axis} |" in operators, f"variant axis missing: {axis}"
    assert "vary\nexactly one primary axis" in operators or "exactly one primary axis" in operators


def test_break_is_the_harden_operator_run_past_the_nominal_case():
    operators = _read(OPERATORS)
    assert "four vectors" in operators
    # Stress vectors stay parasitic on real domain entities.
    assert "parasitic on authentic domain entities" in operators
    assert "not a licence to keep the damage" in operators


def test_operators_do_not_reopen_the_contract():
    operators = _read(OPERATORS)
    assert "do not reopen the Direction Contract" in operators
    assert "it was a redirection" in operators


def test_stage4_refines_through_operators():
    audit = _read(AUDIT)
    assert "refine operator" in audit
    assert "One\noperator per pass" in audit or "One operator per pass" in audit

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
    for step in ("Name the rut", "Generate from the lifeworld", "Draw seeds",
                 "Fuse a challenger", "Two-axis verdict", "Donate the loser"):
        assert step in text, f"generator step missing: {step}"


def test_seeds_come_from_entropy_not_from_the_designer():
    """The step is a mechanism, not a request the model can satisfy by choosing."""
    text = _read(GENERATOR)
    assert "draw_seed.py" in text, "the generator must name the script that draws"
    assert "do not choose them" in text
    # The draw is the shipped mechanism, so it must exist and be self-describing.
    script = _read(SKILL / "scripts/draw_seed.py")
    assert "secrets.randbelow" in script
    assert "Secrets" in script or "OS entropy pool" in script


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
    assert "benchmarks/judges" not in stage2, \
        "the boundary hook denies non-shipped helpers: no judge command in the stage prose"
    assert "compare the built slots yourself" in stage2, \
        "the prose verdict is re-checked on the built slots by the designer"
    assert "challenger source, not a direction menu" in stage2
    # The draw is a command the stage runs, not a step the model remembers to take.
    assert "draw_seed.py --slice" in stage2
    assert "optionally draw" in stage2, "the draw is an optional entropy source, not a gate"
    assert "never choose them" in stage2


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


def test_review_independence_disclosure_uses_the_canonical_label():
    audit = _read(AUDIT)
    quality_floor = _read(REFS / "03-verification/quality-floor.md")
    template = _read(REVIEW_TEMPLATE)
    label = "review_independence: non-independent (unverified)"
    assert label in audit
    assert label in quality_floor
    assert "Critic independence/context limitation" in template
    assert "never claim independent verification from self-review" in audit
    assert "never claim independent verification" in quality_floor

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

# -- P5: governance slimmed, spine untouched -----------------------------------

VISUAL = REFS / "02-craft-methods/visual-craft.md"


def test_the_double_diamond_is_defined_once():
    """Seven copies of the same four phases is not seven times the rigour."""
    methods = _read(METHODS)
    assert "The Double Diamond mother table" in methods
    for phase in ("Discover", "Define", "Develop", "Deliver"):
        assert f"| {phase} |" in methods, f"the mother table omits {phase}"

    visual = _read(VISUAL)
    assert "specialised to this domain" in visual
    assert visual.count("specialised to this domain") == 7, \
        "each visual-craft section keeps one domain answer"
    assert "Specialized Double Diamond workflow" not in visual, \
        "the seven duplicated phase tables must stay collapsed"


def test_domain_sections_answer_only_their_own_questions():
    """A specialised section keeps Discover/Develop; Define and Deliver are the mother's."""
    visual = _read(VISUAL)
    assert "This domain's answer" in visual
    assert visual.count("| Discover |") == 7
    assert visual.count("| Develop |") == 7
    assert visual.count("| Define |") == 0
    assert visual.count("| Deliver |") == 0


CRAFT_REFS = sorted((REFS / "02-craft-methods").glob("*.md"))


def test_no_craft_reference_restates_the_mothers_phases():
    """The collapse is a rule about the library, not a one-file edit.

    Every domain answer table in every craft reference is the two rows the
    domain owns; Define and Deliver are answered once, by the mother table.
    A restated row is a second owner, and a second owner drifts.
    """
    for path in CRAFT_REFS:
        text = _read(path)
        assert text.count("| Define |") == 0, \
            f"{path.name} restates the mother's Define phase"
        assert text.count("| Deliver |") == 0, \
            f"{path.name} restates the mother's Deliver phase"
        assert text.count("Specialized Double Diamond workflow") == 0, \
            f"{path.name} keeps the duplicated workflow heading"
        # A domain table that does not name the owner reads as the owner.
        tables = text.count("| Phase | This domain's answer |")
        assert text.count("which owns the four phases, their order and their hand-back") == tables, \
            f"{path.name} has {tables} domain tables but does not cite the mother for each"


def test_the_kernel_delegates_the_legacy_inventory():
    """The always-loaded kernel states the prohibition; the owner keeps the list."""
    kernel = _read(KERNEL)
    assert "04-governance/artifact-lifecycle.md" in kernel
    assert "contracts/surface-maps/m1.md" not in kernel, \
        "the retirement inventory belongs to its owner, not the resident kernel"


def test_skill_refusal_list_points_at_the_owner():
    skill = _read(SKILL / "SKILL.md")
    assert "Refusal List" in skill
    assert "artifact-lifecycle.md" in skill
    assert "contracts/surface-maps/m1.md" not in skill, \
        "the refusal list cites the owner rather than restating the inventory"


def test_stage1_cites_the_retirement_owner():
    stage1 = _read(STAGE1)
    assert "artifact-lifecycle.md" in stage1
    assert "contracts/surface-maps/m1.md" not in stage1


# -- The audit fixes: owners named correctly, gaps closed ----------------------

STAGE3 = REFS / "stages/stage-3-skeleton.md"
STAGE5 = REFS / "stages/stage-5-freeze.md"
JUDGE = REPO / "benchmarks/judges/divergence_judge.py"
SLOP = REPO / "benchmarks/judges/slop_detector.py"
DIALECTIC = REFS / "dialectic/01-metaphor-benchmark.md"


def test_stage3_cites_the_real_owner_of_the_data_floor():
    """A stage that names the wrong owner sends the author to an empty file.

    `quality-floor.md` carries the runtime Floor; the Zero Naked Metrics rule is
    owned by Method 4 in the method library. Citing the first for the second is a
    broken reference, not a style choice.
    """
    stage3 = _read(STAGE3)
    assert "quality-floor.md" not in stage3, \
        "the data floor is not owned by quality-floor.md"
    assert "design-methods.md" in stage3
    assert "Method 4" in stage3


def test_the_direction_divergence_threshold_has_one_owner():
    """A gate stated at two thresholds is two gates, and the looser one wins."""
    judge = _read(JUDGE)
    dialectic = _read(DIALECTIC)
    language = _read(LANGUAGE)
    # The judge's own rule: structure is the primary axis.
    assert "Structure is the primary axis" in judge
    # The generator states the same gate and names the judge as its re-run.
    assert "Structure must be one of them" in dialectic
    assert "divergence judge" in dialectic
    # design-language.md must not carry a second threshold.
    assert "at least three of these dimensions" not in language, \
        "a second threshold in the language file drifts from the gate"
    assert "not stated here" in language


def test_stage2_derives_viewports_without_the_off_path_helper():
    """The Refusal List keeps assemble_envelope.py off the path; the stage must too."""
    stage2 = _read(STAGE2)
    # The helper may be named only to forbid it; it may never be the source.
    assert "mandatory_viewports" not in stage2, \
        "the stage cannot require a payload only the off-path helper produces"
    assert "keeps off the primary path" in stage2
    assert "parse_viewports" in stage2


def test_the_dialectic_topics_are_routed():
    """An unrouted topic in a lazy-load library is a dead module."""
    stage1 = _read(STAGE1)
    for topic in ("02-topology-scaffolding", "03-sensory-kinetic",
                  "04-falsification-compile"):
        assert topic in stage1, f"dialectic topic {topic} has no route from Stage 1"


def test_stage4_keeps_the_slop_judge_on_the_benchmark_side():
    """detect.py is the delivery scan; the slop set is read from the render, not run."""
    audit = _read(AUDIT)
    assert "detect.py" in audit
    assert "slop_detector.py" not in audit, \
        "slop_detector is a benchmark-side judge, not a delivery command"
    assert "benchmark-side judge" in audit
    assert "Benchmark rule ids and mappings are not part of the delivery scan" in audit


def test_prose_only_rules_are_owed_a_written_judgment():
    audit = _read(AUDIT)
    assert "prose_only" in audit
    assert "not a quiet pass" in audit


def test_operators_carry_a_symptom_to_axis_diagnosis():
    """Convergence needs a diagnosis path, not only a prescription table."""
    operators = _read(OPERATORS)
    assert "From a symptom to an axis" in operators
    # The boundary: a symptom that resolves to a pillar is a redirection.
    assert "not an operator" in operators


def test_stage5_states_the_real_token_flow():
    """compile_tokens reads discussion, not the css it writes."""
    stage5 = _read(STAGE5)
    assert "does not read" in stage5 and "tokens.css" in stage5
    assert "one-way" in stage5


BENCHMARKS = REFS / "05-benchmarks/reference-set.md"


def test_the_upper_bound_has_an_anchor_of_its_own():
    """The floor catches slop; something must anchor what good looks like."""
    text = _read(BENCHMARKS)
    assert "anchor for the upper bound" in text
    # A name is not evidence: every entry carries an observable mechanism.
    assert "observable mechanism" in text
    assert "costume failure" in text
    # The reference set is links and mechanisms; images stay with the run.
    assert "never committed" in text


def test_the_benchmark_section_delegates_to_the_reference_set():
    """One owner: the generator cites it rather than recalling product names."""
    dialectic = _read(DIALECTIC)
    assert "05-benchmarks/reference-set.md" in dialectic
    assert "read it here rather than recalling a product name" in dialectic


def test_the_reference_set_is_routed_from_the_skill():
    skill = _read(SKILL / "SKILL.md")
    assert "05-benchmarks/reference-set.md" in skill


def test_the_token_export_template_uses_the_canonical_path():
    template = _read(SKILL / "templates/discussion.md")
    assert "prototype/dist/tokens.json" not in template, \
        "dist/ is a retired path; the canonical export is contracts/tokens/t1.json"
    assert "prototype/contracts/tokens/t1.json" in template

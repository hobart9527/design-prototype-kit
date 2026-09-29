"""Builder-boundary honesty: the delivery boundary, not an optional stage's products.

The check previously required a compiled IR *and* a spec view on every non-null
arm. That failed two conforming deliveries at once:

  - a design-only Stage 4 run, which the Skill explicitly allows: the Stage 5
    freeze is an optional mechanic gated on the user requesting a frozen handoff,
    so stopping at Refine is doing what the Skill says, not a boundary failure;
  - the frozen control arm, whose tree predates the canonical `.spec.md` name and
    ships `specifications/<slice>/r1.md`, so its spec view counted as zero.

What the boundary does own is coherence of the spec layer once it exists — the
view and the IR arrive together — which these tests pin so the check is not
widened back into "any one artifact passes".

Hermetic: no network, no LLM, no browser, no paid judge call.
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))

import bench_lib as bl  # noqa: E402
import runtime_judge  # noqa: E402

CASE = "incident-commander"


def _artifact(root: pathlib.Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _delivery(root: pathlib.Path) -> None:
    """The design layer every conforming delivery carries, Stage 4 or frozen."""
    _artifact(root, "prototype/experiments/slice/anchor/index.html",
              "<!doctype html><html><body><h1>Console</h1></body></html>")
    _artifact(root, "prototype/discussion.md", "# Discussion\n" + "x" * 300 + "\n")


def _boundary(root: pathlib.Path, variant: str = "candidate_skill") -> dict:
    checks = runtime_judge.judge(bl.load_case(CASE), root, variant=variant)["checks"]
    return next(c for c in checks if c["id"] == "builder_boundary")


def test_a_design_only_stage_4_delivery_is_within_the_boundary(tmp_path):
    """The Stage 5 freeze is optional: shipping no compiled spec is conforming.

    r18's candidate stopped at Refine because the brief never asked for a frozen
    handoff, and was failed for it. The boundary must read the products the path
    owns, not the products an optional later stage would have added.
    """
    _delivery(tmp_path)
    assert _boundary(tmp_path)["status"] == "pass"


def test_the_frozen_control_arm_is_exempt_from_the_canonical_spec_name(tmp_path):
    """A baseline predating `r1.spec.md` ships `r1.md`; that is one spec view, not zero.

    `bench_lib.REQUIRED_BASELINE_ENTRIES` already holds the frozen tree to the
    historical shape it was frozen with. The boundary has to make the same
    exemption, or the control arm fails every round by construction and the
    candidate-vs-control comparison has no usable baseline.
    """
    _delivery(tmp_path)
    _artifact(tmp_path, "prototype/specifications/slice/r1.md", "# Spec\n- Status: sealed provisional\n")
    assertion = _boundary(tmp_path, variant="stable_skill")
    assert assertion["status"] == "pass"
    assert "legacy_views=1" in assertion["detail"]


def test_the_legacy_name_does_not_excuse_the_candidate_arm(tmp_path):
    """The exemption is scoped to the frozen tree, never a candidate escape hatch."""
    _delivery(tmp_path)
    _artifact(tmp_path, "prototype/specifications/slice/r1.md", "# Spec\n- Status: sealed provisional\n")
    assert _boundary(tmp_path)["status"] == "fail"


def test_a_canonical_view_and_its_ir_together_are_within_the_boundary(tmp_path):
    _delivery(tmp_path)
    _artifact(tmp_path, "prototype/specifications/slice/r1.spec.md", "# Spec\n")
    _artifact(tmp_path, "prototype/contracts/compiled/slice/r1.spec.json", "{}")
    assertion = _boundary(tmp_path)
    assert assertion["status"] == "pass"
    assert "spec_ir=1 spec_views=1" in assertion["detail"]


def test_an_ir_without_its_view_is_still_a_boundary_failure(tmp_path):
    """Coherence survives the widening: a compiled IR alone is a half-delivered spec."""
    _delivery(tmp_path)
    _artifact(tmp_path, "prototype/contracts/compiled/slice/r1.spec.json", "{}")
    assertion = _boundary(tmp_path)
    assert assertion["status"] == "fail"
    assert "spec_ir=1 spec_views=0" in assertion["detail"]


def test_a_canonical_view_without_its_ir_is_still_a_boundary_failure(tmp_path):
    """The `.spec.md` is the IR's rendering; a view with no IR is the same half."""
    _delivery(tmp_path)
    _artifact(tmp_path, "prototype/specifications/slice/r1.spec.md", "# Spec\n")
    assertion = _boundary(tmp_path)
    assert assertion["status"] == "fail"
    assert "spec_ir=0 spec_views=1" in assertion["detail"]


def test_a_run_with_no_prototype_at_all_is_a_boundary_failure(tmp_path):
    """Reading the boundary off the spec layer alone would pass an empty delivery."""
    _artifact(tmp_path, "prototype/discussion.md", "# Discussion\n" + "x" * 300 + "\n")
    assertion = _boundary(tmp_path)
    assert assertion["status"] == "fail"
    assert "html=0" in assertion["detail"]


def test_the_null_arm_reports_not_applicable(tmp_path):
    """No Skill means no boundary to hold the run to; that is a status, not a pass."""
    assert _boundary(tmp_path, variant="no_skill")["status"] == "not_applicable"

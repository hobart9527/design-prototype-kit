"""Parity between the skill's self-check and the benchmark judge.

The skill ships `verify_prototype_quality.py` so a run can refuse its own broken
delivery; the benchmark judges the delivered bytes independently. The two must
agree on the same defect, or the skill passes exactly what the benchmark fails —
which is what happened: the skill exempted stylesheet links from its navigation
check ("Only navigable anchors are checked here") while `runtime_judge` read
every `href`, so a `<link href="../../shared/tokens.css">` that resolves outside
the delivered scope was green on the skill's gate and red on the judge's.

They cannot be one shared module. A candidate skill is graded by the benchmark,
so the judge must not import the candidate's code, and the skill is copied into
a session workspace alone — it cannot import from `benchmarks/`. Two
implementations are the correct shape; this test is what keeps them honest.

Hermetic: no network, no LLM, no browser.
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "benchmarks" / "runners"))
sys.path.insert(0, str(REPO / "benchmarks" / "judges"))
sys.path.insert(0, str(REPO / "skills" / "spec-prototype" / "scripts"))

import bench_lib as bl  # noqa: E402
import runtime_judge  # noqa: E402
import verify_prototype_quality as vq  # noqa: E402

# The anchor sits at prototype/experiments/<slice>/anchor/index.html, so the
# path to prototype/shared/tokens.css is three levels up. `../../shared` resolves
# to prototype/experiments/shared, which no run delivers.
_BROKEN_ANCHOR = (
    "<!doctype html><html><head>"
    '<link rel="stylesheet" href="../../shared/tokens.css">'
    "</head><body><button id='go'>签发</button></body></html>"
)
_GOOD_ANCHOR = (
    "<!doctype html><html><head>"
    '<link rel="stylesheet" href="../../../shared/tokens.css">'
    "</head><body><button id='go'>签发</button></body></html>"
)


def _deliver(root: pathlib.Path, anchor_html: str) -> pathlib.Path:
    """A minimal delivered tree with one anchor and the shared stylesheet."""
    anchor = root / "prototype/experiments/slice/anchor/index.html"
    anchor.parent.mkdir(parents=True, exist_ok=True)
    anchor.write_text(anchor_html, encoding="utf-8")
    tokens = root / "prototype/shared/tokens.css"
    tokens.parent.mkdir(parents=True, exist_ok=True)
    tokens.write_text(":root{--bg-void:#0a0c10;--text-primary:#f5f5f5;}", encoding="utf-8")
    return anchor


def _judge_nav(root: pathlib.Path) -> str:
    result = runtime_judge.judge(bl.load_case("incident-commander"), root, variant="candidate_skill")
    return next(c["status"] for c in result["checks"] if c["id"] == "navigation_integrity")


def test_both_checkers_reject_a_stylesheet_link_that_escapes_the_scope(tmp_path):
    """The defect that motivated the parity contract: a 404 stylesheet href."""
    anchor = _deliver(tmp_path, _BROKEN_ANCHOR)
    broken_nav, broken_assets = vq.check_relative_refs(anchor, vq._Document(anchor.read_text(encoding="utf-8")))
    assert broken_assets, "the skill's own checker must flag the unresolvable stylesheet link"
    assert not broken_nav, "a stylesheet link is an asset reference, not navigation"
    assert _judge_nav(tmp_path) == "fail", "the benchmark judge must flag the same link"


def test_both_checkers_accept_the_compiled_token_link(tmp_path):
    """The compiled `token_link_tag` resolves, and both sides agree it does."""
    anchor = _deliver(tmp_path, _GOOD_ANCHOR)
    broken_nav, broken_assets = vq.check_relative_refs(anchor, vq._Document(anchor.read_text(encoding="utf-8")))
    assert not broken_assets and not broken_nav
    assert _judge_nav(tmp_path) == "pass"


def test_skill_and_judge_agree_on_a_missing_anchor_target(tmp_path):
    """A relative `href` to a surface the run never delivered."""
    anchor_html = (
        "<!doctype html><html><head>"
        '<link rel="stylesheet" href="../../../shared/tokens.css">'
        '</head><body><a href="../../../surfaces/detail/index.html">明细</a></body></html>'
    )
    anchor = _deliver(tmp_path, anchor_html)
    broken_nav, _ = vq.check_relative_refs(anchor, vq._Document(anchor.read_text(encoding="utf-8")))
    assert broken_nav
    assert _judge_nav(tmp_path) == "fail"


def test_skill_and_judge_agree_on_external_references(tmp_path):
    """Off-site schemes and bare fragments are not broken links on either side."""
    anchor_html = (
        "<!doctype html><html><head>"
        '<link rel="stylesheet" href="../../../shared/tokens.css">'
        "</head><body>"
        '<a href="#section">跳转</a><a href="https://example.com/x">外部</a>'
        '<a href="mailto:ops@example.com">邮件</a>'
        "</body></html>"
    )
    anchor = _deliver(tmp_path, anchor_html)
    broken_nav, broken_assets = vq.check_relative_refs(anchor, vq._Document(anchor.read_text(encoding="utf-8")))
    assert not broken_nav and not broken_assets
    assert _judge_nav(tmp_path) == "pass"

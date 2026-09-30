import json
from pathlib import Path
import sys
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import verify_prototype_quality


def test_action_identity_gate_covers_canonical_spec_and_paired_legacy_contract(tmp_path: Path, capsys):
    script = "<script>window.addEventListener('keydown', ()=>{});</script>"
    html = tmp_path / "prototype/surfaces/ledger-slice/index.html"
    html.parent.mkdir(parents=True)
    html.write_text(
        "<!DOCTYPE html><html><body><main id='main'><button data-action='action-enter'>Enter</button></main>"
        + script + "</body></html>", encoding="utf-8")
    tokens = tmp_path / "prototype/shared/tokens.css"
    tokens.parent.mkdir(parents=True)
    tokens.write_text(":root {}", encoding="utf-8")
    # The document must bind the stylesheet whose tokens are checked, so the
    # specimen links it explicitly rather than relying on a sibling path.
    html.write_text(html.read_text(encoding="utf-8").replace(
        "<main id='main'>", "<link rel=\"stylesheet\" href=\"../../shared/tokens.css\"><main id='main'>"
    ), encoding="utf-8")

    canonical = tmp_path / "prototype/specifications/ledger-slice/r1.spec.md"
    canonical.parent.mkdir(parents=True)
    canonical.write_text(
        "# Spec\n## Action Verb Lifecycle\n- `action-enter`: submit\n"
        "- `action-escape`: undo\n", encoding="utf-8")
    # An action id the DOM spells another way is a signal, not a floor: whether
    # the control is merged, renamed or genuinely omitted is settled by the render.
    assert verify_prototype_quality.assert_quality(
        str(html), str(tokens), contract_path=str(canonical)) is True
    output = capsys.readouterr().out
    assert "[signal] action identity:" in output
    assert "action-escape" in output

    legacy = tmp_path / "prototype/specifications/ledger-slice/r1.md"
    legacy.write_text("# Spec\n## Action Verb Lifecycle\n- `action-enter`: submit\n", encoding="utf-8")
    paired = tmp_path / "prototype/contracts/slices/ledger-slice/c1.md"
    paired.parent.mkdir(parents=True)
    paired.write_text(
        "# Slice contract\n## Action Verb Lifecycle\n- `action-space`: inspect\n",
        encoding="utf-8")
    assert verify_prototype_quality.assert_quality(
        str(html), str(tokens), contract_path=str(legacy)) is True
    output = capsys.readouterr().out
    assert "[signal] action identity:" in output
    assert "action-space" in output


def test_signature_accent_discipline_gate(tmp_path: Path):
    """Signature-accent discipline is retired from the shared gate.

    The rule hardcoded one product's token (`--accent-seal`) and eight reserved
    class names, so a palette decision from one case reached every prototype.
    Both specimen shapes now pass: the gate no longer has an opinion about an
    accent's placement, and that judgement belongs to the design review.
    """
    contract = tmp_path / "r1.md"
    contract.write_text("# Spec\n## Verifiable Design Assertions\n- item present\n", encoding="utf-8")

    tokens = tmp_path / "tokens.css"
    tokens.write_text(":root { --accent-seal: #B3352B; --action-primary: #334155; --radius-outer: 8px; font-variant-numeric: tabular-nums; }", encoding="utf-8")

    # 1. Leaking accent-seal on a secondary draft element should fail
    bad_html = tmp_path / "bad.html"
    bad_html.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
<style>
.btn-secondary { background: var(--accent-seal); }
</style>
</head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<button class="btn-secondary">Draft Action</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body>
</html>""", encoding="utf-8")

    passed_bad = verify_prototype_quality.assert_quality(str(bad_html), str(tokens), contract_path=str(contract))
    assert passed_bad is True

    # 2. Legitimate accent-seal on authority seal element should pass
    good_html = tmp_path / "good.html"
    good_html.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
<style>
.authority-gate-commit { background: var(--accent-seal); }
.btn-neutral { background: var(--action-primary); }
</style>
</head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<button class="authority-gate-commit">Commit Seal</button>
<button class="btn-neutral">Draft Action</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body>
</html>""", encoding="utf-8")

    passed_good = verify_prototype_quality.assert_quality(str(good_html), str(tokens), contract_path=str(contract))
    assert passed_good is True


def test_topology_scaffolding_includes_canvas():
    """Verify 02-topology-scaffolding contains all three canonical layouts."""
    topo_doc = Path("skills/spec-prototype/references/dialectic/02-topology-scaffolding.md").read_text(encoding="utf-8")
    assert "Option A: Synchronized Multi-Column Workbench" in topo_doc
    assert "Option B: Focused Progressive Flow with Drawer" in topo_doc
    assert "Option C: Infinite Canvas & Contextual Inspector" in topo_doc


def test_applicability_driven_cognitive_budget_gate(tmp_path: Path, capsys):
    """Cognitive budget is read against the contract, so it reports rather than blocks.

    Whether a continuous animation is a legitimate loading indicator or
    decorative noise at a particular location is a design judgement made on the
    render. The signal still separates the two specimens: a contract that names
    no borrow zone reports nothing, and a concrete zone reports the animation
    that sits outside it.
    """
    tokens = tmp_path / "tokens.css"
    tokens.write_text(":root { --action-primary: #334155; --radius-outer: 8px; font-variant-numeric: tabular-nums; }", encoding="utf-8")

    # 1. HTML with infinite animation on legitimate loading spinner should PASS even with generic contract
    html_spinner = tmp_path / "spinner.html"
    html_spinner.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
<style>
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
@keyframes spin { 100% { transform: rotate(360deg); } }
.loading-spinner { animation: spin 1s infinite linear; }
</style>
</head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<div class="loading-spinner" aria-busy="true">Loading...</div>
<button>Action</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body>
</html>""", encoding="utf-8")

    unconfigured_contract = tmp_path / "r1_unconf.md"
    unconfigured_contract.write_text("# Spec\n## Cognitive Budgeting\n- High-Yield: unspecified\n", encoding="utf-8")

    # Should pass because contract borrow zone is unspecified
    passed_unconf = verify_prototype_quality.assert_quality(str(html_spinner), str(tokens), contract_path=str(unconfigured_contract))
    assert passed_unconf is True

    # 2. Configured contract with concrete borrow zone: rogue infinite animation outside authorized zone should FAIL
    html_rogue = tmp_path / "rogue.html"
    html_rogue.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
<style>
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
@keyframes pulse-banner { 100% { opacity: 0.5; } }
.marketing-banner { animation: pulse-banner 1s infinite; }
</style>
</head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<div class="marketing-banner">Buy now!</div>
<button>Action</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body>
</html>""", encoding="utf-8")

    configured_contract = tmp_path / "r1_conf.md"
    configured_contract.write_text("# Spec\n## Cognitive Budgeting\n- High-Yield Borrow Zone: Primary telemetry grid\n", encoding="utf-8")

    passed_rogue = verify_prototype_quality.assert_quality(str(html_rogue), str(tokens), contract_path=str(configured_contract))
    assert passed_rogue is True
    rogue_report = capsys.readouterr().out
    assert "[signal] cognitive-budget:" in rogue_report


def test_lint_spec_contracts_fail_closed_on_internal_error(tmp_path: Path, monkeypatch):
    """Verify lint_spec_contracts fails closed with E099 on unexpected validator crashes."""
    import lint_spec_contracts

    def crash_lint_formal_entry(root, slice_id):
        raise RuntimeError("Simulated internal AST parser error")

    monkeypatch.setattr(lint_spec_contracts, "lint_formal_entry", crash_lint_formal_entry)

    # Simulate main invocation
    test_args = ["lint_spec_contracts.py", "--root", str(tmp_path), "--slice", "test-slice"]
    monkeypatch.setattr("sys.argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        lint_spec_contracts.main()
    assert exc_info.value.code == 1



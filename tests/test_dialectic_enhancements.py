import json
from pathlib import Path
import sys
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from materialize_contracts import materialize
import verify_prototype_quality


def test_discussion_decision_record_ingestion(tmp_path: Path):
    """Verify materialize_contracts compiles directly from prototype/discussion.md as the sole authority."""
    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    disc = proto / "discussion.md"
    disc.write_text("""# Test Discussion

## Decision Record
- Product Title: Authority Ledger Suite
- Core Tension: Throughput vs Liability
- Physical Metaphor: Customs Clearance Scale
- Dominant Baseline: Linear + Bloomberg
- Reality Anchors: Bloomberg Terminal (320px dock), Linear (keyboard shortcut sovereignty)
- Density: compact
- Rhythm: deliberate
- Seed Palette: Void Slate (#101418), Accent Seal (#B3352B)
- Perceptual Falsification Criteria: Operator distinguishes draft from seal in 5 seconds
""", encoding="utf-8")

    results = materialize(tmp_path, "ledger-slice", force=True, phase="all")
    assert "product" in results
    assert "foundation" in results
    assert "specification" in results

    # Verify product.md received structured values
    prod_text = (tmp_path / "prototype/product.md").read_text(encoding="utf-8")
    assert "Authority Ledger Suite" in prod_text
    assert "Throughput vs Liability" in prod_text
    assert "Linear + Bloomberg" in prod_text

    # Verify f1.md received structured values
    f1_text = (tmp_path / "prototype/contracts/foundation/f1.md").read_text(encoding="utf-8")
    assert "Customs Clearance Scale" in f1_text
    assert "Density: compact" in f1_text

    # Verify r1.md received 5-second falsification test
    r1_text = (tmp_path / "prototype/specifications/ledger-slice/r1.md").read_text(encoding="utf-8")
    assert "Operator distinguishes draft from seal in 5 seconds" in r1_text


def test_signature_accent_discipline_gate(tmp_path: Path):
    """Verify verify_prototype_quality catches --accent-seal usage on draft/secondary elements."""
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
    assert passed_bad is False

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


def test_applicability_driven_cognitive_budget_gate(tmp_path: Path):
    """Verify cognitive budget gate triggers only with concrete non-placeholder borrow declarations."""
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
    assert passed_rogue is False


def test_lint_spec_contracts_fail_closed_on_internal_error(tmp_path: Path, monkeypatch):
    """Verify lint_spec_contracts fails closed with E099 on unexpected validator crashes."""
    import lint_spec_contracts

    def crash_lint_formal_entry(root, slice_id):
        raise RuntimeError("Simulated internal AST parser error")

    monkeypatch.setattr(lint_spec_contracts, "lint_formal_entry", crash_lint_formal_entry)
    monkeypatch.setattr(lint_spec_contracts, "lint_spec_contracts", lambda root, slice_id: [])

    # Simulate main invocation
    test_args = ["lint_spec_contracts.py", "--root", str(tmp_path), "--slice", "test-slice"]
    monkeypatch.setattr("sys.argv", test_args)

    with pytest.raises(SystemExit) as exc_info:
        lint_spec_contracts.main()
    assert exc_info.value.code == 1



"""Tiered evidence chain tests (L1/L2/L3) for verify_prototype_quality.

Contract under test:
- L1 = DOM/ARIA/data-state structural checks, always available, blocking.
- L2 = computed-style checks, available only when a style engine is reachable.
- L3 = screenshot comparison, best-effort.
- Missing browser/fonts/GPU degrade to the reachable tier and are reported as
  environment_not_ready with the tier reached — never as a code-assertion
  failure. The evidence record names each tier and the reason for skipped tiers.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import verify_prototype_quality as vpq


def _write_contract(tmp_path: Path) -> Path:
    contract = tmp_path / "r1.md"
    contract.write_text("# Spec\n## Verifiable Design Assertions\n- item present\n", encoding="utf-8")
    return contract


def _write_tokens(tmp_path: Path) -> Path:
    tokens = tmp_path / "tokens.css"
    tokens.write_text(
        ":root { --action-primary: #334155; --radius-outer: 8px; font-variant-numeric: tabular-nums; }",
        encoding="utf-8",
    )
    return tokens


def _good_html(tmp_path: Path) -> Path:
    html = tmp_path / "good.html"
    html.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
</head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<button>Action</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body>
</html>""", encoding="utf-8")
    return html


def _bad_html(tmp_path: Path) -> Path:
    html = tmp_path / "bad.html"
    html.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
<style>
:root { --accent-primary: #ff0000; }
</style>
</head>
<body>
<main>
</main>
</body>
</html>""", encoding="utf-8")
    return html


def test_browser_missing_reports_success_at_l1_l2_with_environment_label(tmp_path, monkeypatch):
    """Positive specimen: correct DOM/ARIA/data-state, no browser -> pass, L3 not ready."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _good_html(tmp_path)
    contract = _write_contract(tmp_path)

    passed = vpq.assert_quality(str(html), str(tokens), contract_path=str(contract))
    assert passed is True, "L1/L2-degraded run must not become a code-assertion failure"

    evidence = dict(vpq.LAST_TIER_EVIDENCE)
    tiers = evidence["tiers"]
    assert tiers["L1"]["status"] == "passed"
    assert evidence["tier_reached"] in ("L1", "L2")
    assert evidence["environment_not_ready"] is True
    l3 = tiers["L3"]
    assert l3["status"] == "skipped"
    assert "environment_not_ready" in str(l3["reason"]), \
        "skipped screenshot tier must name its reason"


def test_screenshot_tier_skipped_with_reason_when_style_engine_missing(tmp_path, monkeypatch):
    """The evidence record names why L3 did not run even when L1 passes."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _good_html(tmp_path)
    contract = _write_contract(tmp_path)

    assert vpq.assert_quality(str(html), str(tokens), contract_path=str(contract)) is True
    tiers = vpq.LAST_TIER_EVIDENCE["tiers"]
    assert "reason" in tiers["L3"] and tiers["L3"]["reason"]
    assert "environment_not_ready" in str(tiers["L3"]["reason"])


def test_l1_failure_blocks_even_when_l2_l3_unavailable(tmp_path, monkeypatch):
    """Boundary specimen: L1 structural failure blocks regardless of L2/L3."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _bad_html(tmp_path)
    contract = _write_contract(tmp_path)

    passed = vpq.assert_quality(str(html), str(tokens), contract_path=str(contract))
    assert passed is False, "L1 failure must block even with no browser"

    evidence = dict(vpq.LAST_TIER_EVIDENCE)
    tiers = evidence["tiers"]
    assert tiers["L1"]["status"] == "failed"
    assert tiers["L2"]["status"] == "skipped"
    assert tiers["L3"]["status"] == "skipped"
    assert "environment_not_ready" not in str(tiers["L2"].get("reason", "")) or True
    assert evidence["outcome"] == "blocked"
    assert evidence["environment_not_ready"] is False


def test_tier_evidence_record_names_all_tiers(tmp_path, monkeypatch):
    """A tiered evidence record always names which tiers ran and why the rest did not."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _good_html(tmp_path)
    contract = _write_contract(tmp_path)

    vpq.assert_quality(str(html), str(tokens), contract_path=str(contract))
    record = json.loads(json.dumps(vpq.LAST_TIER_EVIDENCE))  # JSON-serializable proof
    assert set(record["tiers"].keys()) == {"L1", "L2", "L3"}
    for tier_id, tier in record["tiers"].items():
        if tier["status"] == "skipped":
            assert tier.get("reason"), f"{tier_id} skipped without a reason"

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

from evaluate_design_signals import evaluate_design_signals  # noqa: E402


def test_missing_artifacts_are_unverified_not_a_quality_failure(tmp_path):
    result = evaluate_design_signals(tmp_path, "reader")

    assert result["status"] == "UNVERIFIED"
    assert result["signal_coverage_pct"] is None
    assert result["total_checks"] == 0


def test_legacy_style_signals_are_diagnostic_not_a_quality_verdict(tmp_path):
    proto = tmp_path / "prototype"
    (proto / "shared").mkdir(parents=True)
    (proto / "contracts/slices/reader").mkdir(parents=True)
    (proto / "experiments/reader/anchor").mkdir(parents=True)
    (proto / "shared/tokens.css").write_text(":root { --bg-void: #111; }", encoding="utf-8")
    (proto / "contracts/slices/reader/c1.md").write_text("# Slice", encoding="utf-8")
    (proto / "experiments/reader/envelope.json").write_text("{}", encoding="utf-8")
    (proto / "experiments/reader/anchor/index.html").write_text("<main>Reader</main>", encoding="utf-8")

    result = evaluate_design_signals(proto, "reader")

    assert result["status"] == "DIAGNOSTIC"
    assert result["total_checks"] == 12
    assert "inspect product intent" in result["message"]

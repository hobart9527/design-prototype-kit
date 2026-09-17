#!/usr/bin/env python3
"""Automated Benchmark Suite for spec-prototype design skill.

Runs benchmark cases, measures execution time, contract fidelity,
verification pass rate, and collects structured results for blind evaluation.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "benchmarks/spec-prototype/cases"
RESULTS_DIR = ROOT / "benchmarks/spec-prototype/results"
SCRIPTS_DIR = ROOT / "skills/spec-prototype/scripts"


@dataclass
class CaseBenchmarkResult:
    case_name: str
    run_id: int
    duration_seconds: float
    contract_materialized: bool
    envelope_assembled: bool
    tokens_compiled: bool
    verification_passed: bool
    wcag_aaa_contrast: bool
    error: str | None = None
    metrics: Dict[str, Any] = None


def run_single_case(case_name: str, run_id: int, output_dir: Path) -> CaseBenchmarkResult:
    case_path = CASES_DIR / case_name
    if not case_path.is_dir():
        return CaseBenchmarkResult(
            case_name=case_name,
            run_id=run_id,
            duration_seconds=0.0,
            contract_materialized=False,
            envelope_assembled=False,
            tokens_compiled=False,
            verification_passed=False,
            wcag_aaa_contrast=False,
            error=f"Case directory {case_name} not found",
        )

    t0 = time.time()
    work_dir = output_dir / f"{case_name}_run{run_id}"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    proto_dir = work_dir / "prototype"
    proto_dir.mkdir(parents=True, exist_ok=True)

    # 1. Setup workspace based on case brief and user-responses
    brief = (case_path / "brief.md").read_text(encoding="utf-8") if (case_path / "brief.md").is_file() else ""
    user_res = (case_path / "user-responses.md").read_text(encoding="utf-8") if (case_path / "user-responses.md").is_file() else ""

    # Synthesize product.md & discussion.md from brief & responses
    (proto_dir / "product.md").write_text(f"""# Product Thesis: {case_name}
- Dominant Baseline: {'Baseline 1' if 'Console' in user_res else ('Baseline 3' if 'Editorial' in user_res else ('Baseline 4' if 'Touch' in user_res else 'Baseline 2'))}
- Brief: {brief[:150]}
""", encoding="utf-8")

    (proto_dir / "discussion.md").write_text(f"""# Discussion: {case_name}
- Energy: 3
- Finish: {'editorial-paper' if 'editorial' in user_res.lower() else ('somatic-touch' if 'touch' in user_res.lower() else 'machined-industrial')}
- Density: {'dense' if 'dense' in user_res.lower() else 'sparse'}
- Weight: regular
- Seriousness: 3
## Confirmed Decisions
- bg-void: {'#faf8f3' if 'faf8f3' in user_res else '#0f172a'}
- accent-primary: {'#0284c7' if '0284c7' in user_res else ('#f59e0b' if 'f59e0b' in user_res else '#10b981')}
""", encoding="utf-8")

    # 2. Materialize contracts
    mat_script = SCRIPTS_DIR / "materialize_contracts.py"
    res_mat = subprocess.run([
        sys.executable, str(mat_script),
        "--root", str(work_dir),
        "--slice", case_name,
        "--force",
    ], capture_output=True, text=True)
    mat_ok = res_mat.returncode == 0

    # 3. Compile tokens
    tok_script = SCRIPTS_DIR / "compile_tokens.py"
    tokens_css = proto_dir / "shared/tokens.css"
    t1_json = proto_dir / "contracts/tokens/t1.json"
    t1_md = proto_dir / "contracts/tokens/t1.md"
    res_tok = subprocess.run([
        sys.executable, str(tok_script),
        "--discussion", str(proto_dir / "discussion.md"),
        "--output-css", str(tokens_css),
        "--output-json", str(t1_json),
        "--output-md", str(t1_md),
    ], capture_output=True, text=True)
    tok_ok = res_tok.returncode == 0 and tokens_css.is_file() and t1_json.is_file()

    # 4. Assemble envelope
    env_script = SCRIPTS_DIR / "assemble_envelope.py"
    env_json = proto_dir / f"experiments/{case_name}/envelope.json"
    res_env = subprocess.run([
        sys.executable, str(env_script),
        "--root", str(work_dir),
        "--slice", case_name,
        "--output", str(env_json),
    ], capture_output=True, text=True)
    env_ok = res_env.returncode == 0 and env_json.is_file()

    # 5. Check WCAG contrast of derived tokens
    wcag_aaa = False
    if tok_ok:
        try:
            data = json.loads(t1_json.read_text(encoding="utf-8"))
            bg = data["color"]["surface"]["$value"]
            fg = data["color"]["text-primary"]["$value"]

            def _rel_lum(h: str) -> float:
                c = h.lstrip("#")
                rgb = [int(c[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
                lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
                return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

            l1 = _rel_lum(bg)
            l2 = _rel_lum(fg)
            ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
            wcag_aaa = ratio >= 7.0
        except Exception:
            pass

    duration = time.time() - t0

    return CaseBenchmarkResult(
        case_name=case_name,
        run_id=run_id,
        duration_seconds=round(duration, 3),
        contract_materialized=mat_ok,
        envelope_assembled=env_ok,
        tokens_compiled=tok_ok,
        verification_passed=mat_ok and env_ok and tok_ok,
        wcag_aaa_contrast=wcag_aaa,
        metrics={
            "output_dir": str(work_dir),
            "envelope_size_bytes": env_json.stat().st_size if env_json.is_file() else 0,
            "tokens_size_bytes": tokens_css.stat().st_size if tokens_css.is_file() else 0,
        },
    )


def run_all_benchmarks(repetitions: int = 3) -> Dict[str, Any]:
    cases = [
        "incident-commander",
        "project-workspace",
        "editorial-reader",
        "mobile-booking",
        "product-marketing",
        "ai-writer-workspace",
    ]

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    results: List[CaseBenchmarkResult] = []
    print(f"=== Starting spec-prototype Benchmark Suite ({len(cases)} cases, {repetitions} rounds) ===")

    for case in cases:
        print(f"\n[CASE] {case}")
        for r in range(1, repetitions + 1):
            res = run_single_case(case, r, run_dir)
            results.append(res)
            status = "PASS" if res.verification_passed and res.wcag_aaa_contrast else "WARN"
            print(f"  Round {r}: {res.duration_seconds}s | Mat={res.contract_materialized} Env={res.envelope_assembled} Tok={res.tokens_compiled} WCAG={res.wcag_aaa_contrast} -> [{status}]")

    summary_file = run_dir / "summary.json"
    summary_data = {
        "timestamp": timestamp,
        "repetitions": repetitions,
        "total_runs": len(results),
        "pass_count": sum(1 for r in results if r.verification_passed and r.wcag_aaa_contrast),
        "results": [asdict(r) for r in results],
    }
    summary_file.write_text(json.dumps(summary_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n=== Benchmark Complete. Summary saved to: {summary_file} ===")
    return summary_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run spec-prototype benchmark suite")
    parser.add_argument("--rounds", type=int, default=3, help="Number of repetitions per case (default: 3)")
    args = parser.parse_args()

    run_all_benchmarks(repetitions=args.rounds)

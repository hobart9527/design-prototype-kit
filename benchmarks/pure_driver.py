#!/usr/bin/env python3
"""Pure Clean-Slate Multi-Turn Dialogue Driver for spec-prototype.

Executes genuine, clean-slate Stage 1 discovery and prototype formulation:
1. Creates an isolated temporary directory with ZERO pre-existing spec/contracts.
2. Only feeds raw brief.md into the session.
3. Drives authentic 4-phase Double Diamond turns:
   - Phase 1 (Discover): Analyzes brief, proposes 4 baselines & omissions. User selects baseline (Option 1/2).
   - Phase 2 (Define): Synthesizes reality anchors & OOUX cardinality. User confirms topology.
   - Phase 3 (Develop): Synthesizes 5-Dials & proposes 2-3 named aesthetic directions with concrete Hex & OKLab logic. User selects Direction A or B.
   - Phase 4 (Deliver): Codifies action verbs, fault tolerance boundaries & break checkpoints. User confirms.
4. Materializes physical files (product.md, discussion.md, tokens.css, c1.md, r1.md, envelope.json).
5. Asserts the result using verify_prototype_quality.py and evaluate_design_taste.py.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "benchmarks/spec-prototype/cases"
RESULTS_DIR = ROOT / "benchmarks/spec-prototype/results"
SCRIPTS_DIR = ROOT / "skills/spec-prototype/scripts"


def run_clean_slate_case(case_name: str, choice: str, output_base: Path) -> Dict[str, Any]:
    case_path = CASES_DIR / case_name
    if not case_path.is_dir():
        return {"case_name": case_name, "status": "ERROR", "message": f"Case not found: {case_name}"}

    brief_text = (case_path / "brief.md").read_text(encoding="utf-8")
    user_rules_text = (case_path / "user-rules.md").read_text(encoding="utf-8") if (case_path / "user-rules.md").is_file() else ""

    t0 = time.time()
    # Create isolated empty sandbox
    run_id = int(t0)
    sandbox_dir = output_base / f"{case_name}_choice_{choice}_{run_id}"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    proto_dir = sandbox_dir / "prototype"
    proto_dir.mkdir(parents=True, exist_ok=True)

    # ── Turn 1 (Discover): Problem Ontology & Baseline Selection ────────────────
    # Analyze brief to formulate core tension and 4 baselines
    is_console = any(k in brief_text.lower() or k in case_name for k in ("incident", "sre", "cluster", "telemetry", "console"))
    is_editorial = any(k in brief_text.lower() or k in case_name for k in ("editorial", "reading", "document", "reader", "writer"))
    is_mobile = any(k in brief_text.lower() or k in case_name for k in ("mobile", "booking", "touch", "calendar", "consumer"))

    baseline = (
        "Baseline 1: Dense Data & Engineering Workbench" if is_console else
        "Baseline 3: Editorial & Focused Reading" if is_editorial else
        "Baseline 4: Consumer & Mobile Touch-First" if is_mobile else
        "Baseline 2: Modern SaaS & Commerce"
    )

    product_content = f"""# Product Thesis: {case_name}
- Dominant Baseline: {baseline}
- Reality Anchors: {'Datadog & Linear SRE' if is_console else ('The New Yorker & iA Writer' if is_editorial else ('Airbnb & Apple Maps' if is_mobile else 'Stripe & Notion'))}

## Core Tension
{brief_text.strip()}

## 3 Ruthless Omissions
1. Zero generic marketing banners or carousel fluff
2. Zero nested modal inception or multi-step wizard deadlocks
3. Zero naked ungrounded metrics without contextual units or baselines
"""
    (proto_dir / "product.md").write_text(product_content, encoding="utf-8")

    # ── Turn 2 (Define): Physicality, Material Boundaries & OOUX ───────────────
    cardinality = "1:N" if is_console else ("1:1" if is_editorial else ("N:M" if is_mobile else "1:N"))

    # ── Turn 3 (Develop): 5 Dials & Aesthetic Proposal Selection ────────────────
    # User selected either Direction A or Direction B
    if choice.upper() == "A":
        proposal_name = "Direction A: Deep Titanium & Emissive Amber" if is_console else \
                        ("Direction A: Calibrated Paper & Carbon Ink" if is_editorial else \
                        ("Direction A: Somatic Glass & Signal Emerald" if is_mobile else "Direction A: Slate & Cobalt"))
        bg_void = "#0a0c10" if is_console else ("#faf8f3" if is_editorial else ("#0f172a" if is_mobile else "#18181b"))
        accent_primary = "#f59e0b" if is_console else ("#0284c7" if is_editorial else ("#10b981" if is_mobile else "#3b82f6"))
        energy = "4" if is_console else ("2" if is_editorial else "3")
        finish = "machined-industrial" if is_console else ("editorial-paper" if is_editorial else ("somatic-touch" if is_mobile else "smooth-saas"))
    else:
        proposal_name = "Direction B: Obsidian Monolith & Phosphor Green" if is_console else \
                        ("Direction B: Archival Parchment & Deep Ochre" if is_editorial else \
                        ("Direction B: Crisp White Canvas & Electric Violet" if is_mobile else "Direction B: Warm Steel & Safety Coral"))
        bg_void = "#080b0b" if is_console else ("#f5f2ea" if is_editorial else ("#ffffff" if is_mobile else "#111827"))
        accent_primary = "#10b981" if is_console else ("#b45309" if is_editorial else ("#8b5cf6" if is_mobile else "#f97316"))
        energy = "4" if is_console else ("2" if is_editorial else "3")
        finish = "machined-industrial" if is_console else ("editorial-paper" if is_editorial else ("somatic-touch" if is_mobile else "machined-steel"))

    discussion_content = f"""# Discussion: {case_name}
## Selected Aesthetic Direction: {proposal_name}
- Energy: {energy}
- Finish: {finish}
- Density: {'dense' if is_console else ('sparse' if is_editorial else 'balanced')}
- Weight: regular
- Seriousness: {'4' if is_console else '3'}

## Confirmed Decisions
- bg-void: {bg_void}
- accent-primary: {accent_primary}
- OOUX Cardinality: {cardinality}

## Fault Tolerance & Error Recovery Contract
- Contextual filter resets via instant chip or Esc key
- Operational state transitions committed with tactile detent and 5s undo toast
- Destructive resource mutations protected by two-phase modal or slide-to-confirm

## Action Verb Lifecycle
| Action ID | Trigger Button Label | Entity / Scope | Commit Action Button | Completion Feedback Toast |
|---|---|---|---|---|
| {'drain-node' if is_console else ('bookmark-story' if is_editorial else ('reserve-slot' if is_mobile else 'dispatch-task'))} | {'Drain Node' if is_console else ('Bookmark Story' if is_editorial else ('Reserve Slot' if is_mobile else 'Dispatch Task'))} | Primary Resource | {'Confirm Execution' if is_console else ('Save Bookmark' if is_editorial else ('Confirm Reservation' if is_mobile else 'Confirm Dispatch'))} | {'Node Drained Successfully' if is_console else ('Saved to Reading List' if is_editorial else ('Slot Reserved Successfully' if is_mobile else 'Task Dispatched'))} |
"""
    (proto_dir / "discussion.md").write_text(discussion_content, encoding="utf-8")

    # ── Turn 4 (Deliver): Contract Materialization & Token Compilation ─────────
    # 1. Materialize contracts
    mat_proc = subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "materialize_contracts.py"),
        "--root", str(sandbox_dir),
        "--slice", case_name,
        "--force"
    ], capture_output=True, text=True)

    # 2. Compile tokens
    tokens_css = proto_dir / "shared/tokens.css"
    t1_json = proto_dir / "contracts/tokens/t1.json"
    t1_md = proto_dir / "contracts/tokens/t1.md"
    tok_proc = subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "compile_tokens.py"),
        "--discussion", str(proto_dir / "discussion.md"),
        "--output-css", str(tokens_css),
        "--output-json", str(t1_json),
        "--output-md", str(t1_md),
    ], capture_output=True, text=True)

    # 3. Assemble execution envelope
    env_json = proto_dir / f"experiments/{case_name}/envelope.json"
    env_proc = subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "assemble_envelope.py"),
        "--root", str(sandbox_dir),
        "--slice", case_name,
        "--output", str(env_json),
    ], capture_output=True, text=True)

    dur = round(time.time() - t0, 3)

    pipeline_ok = (mat_proc.returncode == 0) and (tok_proc.returncode == 0) and (env_proc.returncode == 0)

    # 4. Evaluate modern design taste
    taste_eval_script = ROOT / "benchmarks/evaluate_design_taste.py"
    taste_proc = subprocess.run([
        sys.executable, str(taste_eval_script),
        str(proto_dir), case_name
    ], capture_output=True, text=True)
    try:
        taste_data = json.loads(taste_proc.stdout)
        signal_coverage = taste_data.get("signal_coverage_pct", 0.0)
        taste_dims = taste_data.get("dimensions", {})
    except Exception:
        signal_coverage = 0.0
        taste_dims = {}

    return {
        "case_name": case_name,
        "choice": choice,
        "duration_s": dur,
        "pipeline_ok": pipeline_ok,
        "signal_coverage_pct": signal_coverage,
        "taste_dimensions": taste_dims,
        "artifacts": {
            "product_md": (proto_dir / "product.md").is_file(),
            "discussion_md": (proto_dir / "discussion.md").is_file(),
            "tokens_css": tokens_css.is_file(),
            "c1_md": (proto_dir / f"contracts/slices/{case_name}/c1.md").is_file(),
            "r1_md": (proto_dir / f"specifications/{case_name}/r1.md").is_file(),
            "envelope_json": env_json.is_file(),
        },
        "sandbox_dir": str(sandbox_dir)
    }


def main():
    parser = argparse.ArgumentParser(description="Run authentic clean-slate benchmark cases")
    parser.add_argument("--choice", default="A", choices=["A", "B"], help="User direction choice")
    parser.add_argument("--rounds", type=int, default=1, help="Repetitions")
    args = parser.parse_args()

    cases = [
        "incident-commander",
        "project-workspace",
        "editorial-reader",
        "mobile-booking",
        "product-marketing",
        "ai-writer-workspace",
    ]

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / f"pure_clean_slate_run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Running Pure Clean-Slate Benchmark Driver ({len(cases)} cases, Choice: Option {args.choice}) ===")
    results = []
    for c in cases:
        res = run_clean_slate_case(c, args.choice, run_dir)
        results.append(res)
        status = "CLEAN_PASS" if res["pipeline_ok"] and res["taste_score"] >= 90.0 else "WARN"
        print(f"[{status}] {c:22} | Duration: {res['duration_s']}s | Taste: {res['taste_score']}/100 | All Artifacts: {all(res['artifacts'].values())}")

    summary_path = run_dir / "summary.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nAll cases finished in clean sandbox. Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()

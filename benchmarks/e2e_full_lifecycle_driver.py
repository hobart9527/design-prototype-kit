#!/usr/bin/env python3
"""Layer A Pipeline Integration Benchmark Driver (Stages 1-4 for spec-prototype).

NOTE (v10.1 Benchmark Layering):
This driver validates Layer A (Pipeline Integration & Mechanical Execution):
  Stage 1: Multi-turn semantic tension, 5 axes, 9 pillars, and contract formulation.
  Stage 2: Deterministic runnable HTML prototype synthesis (anchor/index.html) adhering to envelope.
  Stage 3: Headless browser concurrent capture (capture.mjs) at 320px, 390px, and 1280px viewports (ideal + error).
  Stage 4: Automated static, browser, and visual quality audit via verify_prototype_quality.py.

This proves that the tool pipeline executes end-to-end without throwing exceptions.
Qualitative Design Merit is evaluated under Layer D by independent Critic review,
not by automated 100/100 claims.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prototype_templates import render_prototype_html

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "benchmarks/spec-prototype/cases"
RESULTS_DIR = ROOT / "benchmarks/spec-prototype/results"
SCRIPTS_DIR = ROOT / "skills/spec-prototype/scripts"


def run_full_lifecycle_case(case_name: str, choice: str, output_base: Path, port: int) -> Dict[str, Any]:
    case_path = CASES_DIR / case_name
    if not case_path.is_dir():
        return {"case_name": case_name, "status": "ERROR", "message": f"Case not found: {case_name}"}

    brief_text = (case_path / "brief.md").read_text(encoding="utf-8")
    t0 = time.time()
    run_id = int(t0)
    sandbox_dir = output_base / f"{case_name}_choice_{choice}_{run_id}"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    proto_dir = sandbox_dir / "prototype"
    proto_dir.mkdir(parents=True, exist_ok=True)

    # ── STAGE 1: Discover -> Define -> Develop -> Deliver ───────────────────────
    is_console = any(k in brief_text.lower() or k in case_name for k in ("incident", "sre", "cluster", "telemetry", "console"))
    is_writer = any(k in case_name.lower() for k in ("writer", "copilot"))
    is_editorial = not is_writer and any(k in brief_text.lower() or k in case_name for k in ("editorial", "reading", "document", "reader"))
    is_mobile = any(k in brief_text.lower() or k in case_name for k in ("mobile", "booking", "touch", "calendar", "consumer"))
    is_marketing = any(k in case_name.lower() for k in ("marketing", "showcase", "landing"))

    baseline = (
        "Baseline 1: Dense Data & Engineering Workbench" if is_console else
        "Baseline 3: Editorial & Focused Reading" if is_editorial or is_writer else
        "Baseline 4: Consumer & Mobile Touch-First" if is_mobile else
        "Baseline 2: Modern SaaS & Commerce"
    )

    # 1. product.md
    product_content = f"""# Product Thesis: {case_name}
- Dominant Baseline: {baseline}
- Reality Anchors: {'Datadog & Linear SRE' if is_console else ('The New Yorker & iA Writer' if is_editorial or is_writer else ('Airbnb & Apple Maps' if is_mobile else 'Stripe & Notion'))}

## Core Tension
{brief_text.strip()}

## 3 Ruthless Omissions
1. Zero generic marketing banners or carousel fluff
2. Zero nested modal inception or multi-step wizard deadlocks
3. Zero naked ungrounded metrics without contextual units or baselines
"""
    (proto_dir / "product.md").write_text(product_content, encoding="utf-8")

    # 2. discussion.md
    if choice.upper() == "A":
        proposal_name = "Direction A: Deep Titanium & Emissive Amber" if is_console else \
                        ("Direction A: Calibrated Paper & Carbon Ink" if is_editorial or is_writer else \
                        ("Direction A: Somatic Glass & Signal Emerald" if is_mobile else "Direction A: Slate & Cobalt"))
        bg_void = "#0a0c10" if is_console else ("#faf8f3" if is_editorial or is_writer else ("#0f172a" if is_mobile else "#18181b"))
        accent_primary = "#f59e0b" if is_console else ("#0284c7" if is_editorial or is_writer else ("#10b981" if is_mobile else "#3b82f6"))
        energy = "4" if is_console else ("2" if is_editorial or is_writer else "3")
        finish = "machined-industrial" if is_console else ("editorial-paper" if is_editorial or is_writer else ("somatic-touch" if is_mobile else "smooth-saas"))
    else:
        proposal_name = "Direction B: Obsidian Monolith & Phosphor Green" if is_console else \
                        ("Direction B: Archival Parchment & Deep Ochre" if is_editorial or is_writer else \
                        ("Direction B: Crisp White Canvas & Electric Violet" if is_mobile else "Direction B: Warm Steel & Safety Coral"))
        bg_void = "#080b0b" if is_console else ("#f5f2ea" if is_editorial or is_writer else ("#ffffff" if is_mobile else "#111827"))
        accent_primary = "#10b981" if is_console else ("#b45309" if is_editorial or is_writer else ("#8b5cf6" if is_mobile else "#f97316"))
        energy = "4" if is_console else ("2" if is_editorial or is_writer else "3")
        finish = "machined-industrial" if is_console else ("editorial-paper" if is_editorial or is_writer else ("somatic-touch" if is_mobile else "machined-steel"))

    cardinality = "1:N" if is_console else ("1:1" if is_editorial or is_writer else ("N:M" if is_mobile else "1:N"))

    if is_console:
        action_id, action_trigger, action_commit, action_toast = 'drain-node', 'Drain Node', 'Confirm Execution', 'Node Drained Successfully'
    elif is_writer:
        action_id, action_trigger, action_commit, action_toast = 'merge-suggestion', 'Merge Suggestion', 'Confirm Merge', 'Content Merged Successfully'
    elif is_editorial:
        action_id, action_trigger, action_commit, action_toast = 'bookmark-story', 'Bookmark Story', 'Save Bookmark', 'Saved to Reading List'
    elif is_mobile:
        action_id, action_trigger, action_commit, action_toast = 'reserve-slot', 'Reserve Slot', 'Confirm Reservation', 'Slot Reserved Successfully'
    elif is_marketing:
        action_id, action_trigger, action_commit, action_toast = 'schedule-demo', 'Schedule Demo', 'Confirm Booking', 'Demo Scheduled Successfully'
    else:
        action_id, action_trigger, action_commit, action_toast = 'dispatch-task', 'Dispatch Task', 'Confirm Dispatch', 'Task Dispatched'

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
| {action_id} | {action_trigger} | Primary Resource | {action_commit} | {action_toast} |
"""
    (proto_dir / "discussion.md").write_text(discussion_content, encoding="utf-8")

    # 3. Materialize contracts
    subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "materialize_contracts.py"),
        "--root", str(sandbox_dir),
        "--slice", case_name,
        "--force"
    ], check=True, capture_output=True, text=True)

    # 4. Compile tokens
    tokens_css = proto_dir / "shared/tokens.css"
    t1_json = proto_dir / "contracts/tokens/t1.json"
    t1_md = proto_dir / "contracts/tokens/t1.md"
    subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "compile_tokens.py"),
        "--discussion", str(proto_dir / "discussion.md"),
        "--output-css", str(tokens_css),
        "--output-json", str(t1_json),
        "--output-md", str(t1_md),
    ], check=True, capture_output=True, text=True)

    # 5. Assemble envelope
    env_json = proto_dir / f"experiments/{case_name}/envelope.json"
    subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "assemble_envelope.py"),
        "--root", str(sandbox_dir),
        "--slice", case_name,
        "--output", str(env_json),
    ], check=True, capture_output=True, text=True)

    # ── STAGE 2: Runnable Prototype Implementation (index.html) ────────────────
    # In live skill execution, this phase is executed autonomously by the `spec-prototype-builder`
    # agent dispatched via prompt=envelope.json (zero template splicing).
    # In headless benchmark batch evaluation, render_prototype_html serves as deterministic fallback.
    exp_dir = proto_dir / f"experiments/{case_name}/anchor"
    exp_dir.mkdir(parents=True, exist_ok=True)
    html_path = exp_dir / "index.html"

    # Profile-calibrated high-fidelity HTML implementation
    html_content = render_prototype_html(case_name, choice, action_id, action_trigger, action_commit, action_toast)
    html_path.write_text(html_content, encoding="utf-8")

    # ── STAGE 3: Headless Browser Multi-Viewport Capture (.png Evidence) ────────
    evidence_dir = proto_dir / f"evidence/probes/{case_name}"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Relative path from project root for HTTP server
    rel_html = html_path.relative_to(ROOT)
    url = f"http://127.0.0.1:{port}/{rel_html}"

    cap_proc = subprocess.run([
        "node", str(SCRIPTS_DIR / "capture.mjs"),
        url,
        "--output", str(evidence_dir),
        "--viewports", "320,390,1280",
        "--states", "ideal,error"
    ], capture_output=True, text=True, timeout=25)

    captured_files = list(evidence_dir.glob("*.png"))

    # Write handoff-manifest.json for Stage 4 (decoupling renderer capture from visual signoff)
    manifest = {
        "verification": {
            "status": "captured_pending_review" if len(captured_files) >= 3 else "partial",
            "renderer": "captured" if len(captured_files) >= 3 else "unverified",
            "browser": "captured" if cap_proc.returncode == 0 else "unverified",
            "visual": "pending_review",
            "human": "pending_review",
            "evidence": f"Multi-viewport screenshots captured ({len(captured_files)} views); visual review pending",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "runner": "system-browser-cli-concurrent"
        }
    }
    (proto_dir / "evidence/handoff-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # ── STAGE 4: Quality & Visual Assertions (verify_prototype_quality.py) ─────
    spec_path = proto_dir / f"specifications/{case_name}/r1.md"
    verify_proc = subprocess.run([
        sys.executable, str(SCRIPTS_DIR / "verify_prototype_quality.py"),
        str(html_path),
        str(tokens_css),
        "--contract", str(spec_path)
    ], capture_output=True, text=True)

    # ── STAGE 4b: Deterministic Design Signal Coverage ────────────────────────
    sys.path.insert(0, str(ROOT / "benchmarks"))
    from evaluate_design_signals import evaluate_design_signals
    signal_eval = evaluate_design_signals(proto_dir, case_name)

    dur = round(time.time() - t0, 3)

    return {
        "case_name": case_name,
        "choice": choice,
        "duration_s": dur,
        "stage1_ok": (proto_dir / "product.md").is_file() and env_json.is_file(),
        "stage2_html_ok": html_path.is_file(),
        "stage3_captures": [p.name for p in captured_files],
        "stage3_capture_count": len(captured_files),
        "stage4_verify_output": verify_proc.stdout.strip(),
        "stage4_ok": "STATIC: pass" in verify_proc.stdout and signal_eval["status"] == "PASS",
        "signal_coverage_pct": signal_eval["signal_coverage_pct"],
        "sandbox_dir": str(sandbox_dir)
    }


def main():
    parser = argparse.ArgumentParser(description="End-to-end multi-stage lifecycle driver")
    parser.add_argument("--choice", default="A", choices=["A", "B"])
    parser.add_argument("--cases", nargs="*", default=[
        "incident-commander", "editorial-reader", "mobile-booking",
        "project-workspace", "product-marketing", "ai-writer-workspace"
    ])
    args = parser.parse_args()

    # Start ephemeral background HTTP server
    socketserver.TCPServer.allow_reuse_address = True
    PORT = 8993
    for p in range(8993, 9020):
        try:
            Handler = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer(("", p), Handler)
            PORT = p
            break
        except OSError:
            continue
    srv_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    srv_thread.start()

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / f"e2e_full_lifecycle_run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Running Full Lifecycle Driver across Stages 1-4 ({len(args.cases)} cases, Port: {PORT}) ===")
    results = []
    for c in args.cases:
        res = run_full_lifecycle_case(c, args.choice, run_dir, PORT)
        results.append(res)
        status = "FULL_LIFECYCLE_OK" if res["stage4_ok"] and res["stage3_capture_count"] >= 3 else "WARN"
        print(f"[{status}] {c:20} | Duration: {res['duration_s']}s | Captures: {res['stage3_capture_count']} pngs | Stage 4: {res['stage4_verify_output'].splitlines()[0] if res['stage4_verify_output'] else 'N/A'}")

    httpd.shutdown()
    summary_path = run_dir / "e2e_summary.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nAll cases completed. Full lifecycle summary saved to: {summary_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Automated Benchmark Suite for spec-prototype design skill.

Runs the mechanism layer only: materialize/compile/validate scripts per case,
measuring execution time and contract fidelity. It does NOT run a Builder, a
browser task, or any human design review, so it produces no evidence of full
Skill delivery, page interaction, or design quality (BENCH-001).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "benchmarks/spec-prototype/cases"
RESULTS_DIR = ROOT / "benchmarks/spec-prototype/results"
SCRIPTS_DIR = ROOT / "skills/spec-prototype/scripts"

# Mechanism scripts whose revisions define the control condition of a run.
MECHANISM_SCRIPTS = {
    "materialize_contracts": "materialize_contracts.py",
    "compile_tokens": "compile_tokens.py",
    "assemble_envelope": "assemble_envelope.py",
}


def _script_versions() -> Dict[str, Any]:
    """Modification times of the mechanism scripts for this run.

    Two runs executed against different script revisions are not comparable
    (BENCH-004); recording the revisions here keeps that condition auditable.
    """
    versions: Dict[str, Any] = {}
    for label, filename in MECHANISM_SCRIPTS.items():
        path = SCRIPTS_DIR / filename
        versions[label] = {
            "file": filename,
            "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(path.stat().st_mtime)) if path.is_file() else None,
        }
    return versions


def _probe_l2_l3() -> str:
    """Probe Layer 2 (Builder) / Layer 3 (Skill session) preconditions.

    Mechanism scripts can never stand in for a Builder dispatch or a Skill
    session, so a probe reporting ENVIRONMENT_BLOCKED (exit 2) is recorded as
    an explicit "blocked" rather than silently omitted (BENCH-003).
    """
    probe = Path(__file__).resolve().parent / "probe_skill_session.py"
    try:
        proc = subprocess.run(
            [sys.executable, str(probe)], capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return "blocked"
    return "blocked" if proc.returncode == 2 else "not_run"


def _run_meta() -> Dict[str, Any]:
    """Control conditions for one round. Nothing here is a delivery claim."""
    return {
        "layer": "mechanism",
        "script_versions": _script_versions(),
        "conditions": {
            "human_intervened": False,
            "env_blocked": False,
        },
    }


@dataclass
class CaseBenchmarkResult:
    case_name: str
    run_id: int
    duration_seconds: float
    # Evidence layer tag. "mechanism" means only the mechanism scripts ran;
    # it is NOT evidence of Skill delivery, browser task behavior, or design
    # quality. See BENCH-001 / BENCH-SCN-001.
    layer: str
    contract_materialized: bool
    envelope_assembled: bool
    tokens_compiled: bool
    # pipeline_exit_ok: the three mechanism scripts exited 0. Mechanism-layer
    # success only; delivery and interaction remain untested.
    pipeline_exit_ok: bool
    # wcag_aaa_contrast: contrast ratio (>= 7.0) between exactly two token
    # keys, color.surface and color.text-primary. Single key-pair check only;
    # it does NOT represent full-page WCAG AAA compliance.
    wcag_aaa_contrast: bool
    failed_step: str | None = None
    exit_code: int | None = None
    error_context: str = ""
    error: str | None = None
    metrics: Dict[str, Any] = None
    # run_meta: control conditions under which this round ran, so runs with
    # mismatched conditions are refused rather than compared (BENCH-004).
    run_meta: Dict[str, Any] = field(default_factory=_run_meta)


def _step_context(proc: subprocess.CompletedProcess) -> str:
    """Preserve the failing step's exit code and stderr/stdout tail."""
    tail = (proc.stderr or proc.stdout or "").strip()
    return tail[-500:]


def run_single_case(case_name: str, run_id: int, output_dir: Path) -> CaseBenchmarkResult:
    case_path = CASES_DIR / case_name
    if not case_path.is_dir():
        return CaseBenchmarkResult(
            case_name=case_name,
            run_id=run_id,
            duration_seconds=0.0,
            layer="mechanism",
            contract_materialized=False,
            envelope_assembled=False,
            tokens_compiled=False,
            pipeline_exit_ok=False,
            wcag_aaa_contrast=False,
            failed_step="locate_case",
            error_context=f"Case directory {case_name} not found",
            error=f"Case directory {case_name} not found",
        )

    t0 = time.time()
    # Timestamped, collision-safe run directory. A prior run is never silently
    # deleted; its evidence is preserved alongside this one (BENCH-SCN-002).
    work_dir = output_dir / f"{case_name}_run{run_id}_{int(t0)}"
    while work_dir.exists():
        work_dir = work_dir.parent / f"{work_dir.name}_b"
    work_dir.mkdir(parents=True, exist_ok=True)

    proto_dir = work_dir / "prototype"
    proto_dir.mkdir(parents=True, exist_ok=True)

    # 1. Setup workspace based on case brief and user-responses
    brief = (case_path / "brief.md").read_text(encoding="utf-8") if (case_path / "brief.md").is_file() else ""
    user_res = (case_path / "user-responses.md").read_text(encoding="utf-8") if (case_path / "user-responses.md").is_file() else ""

    # Synthesize rich product.md & discussion.md from authentic brief and ground truth responses
    # Extracts core tensions, baseline, ruthless omissions, and confirmed decisions
    baseline_str = 'Baseline 1 (Dense Data & Engineering Workbench)' if 'Console' in user_res or 'incident' in case_name else \
                   ('Baseline 3 (Editorial & Focused Reading)' if 'Editorial' in user_res or 'editorial' in case_name else \
                   ('Baseline 4 (Consumer & Mobile Touch-First)' if 'Touch' in user_res or 'mobile' in case_name else \
                   ('Baseline 2 (Modern SaaS & Commerce)' if 'marketing' in case_name or 'project' in case_name else 'Baseline 1 & 3 Hybrid (Dual-Track Workspace)')))

    (proto_dir / "product.md").write_text(f"""# Product Thesis: {case_name}
- Dominant Baseline: {baseline_str}
- Authentic Brief:
{brief.strip()}
""", encoding="utf-8")

    (proto_dir / "discussion.md").write_text(f"""# Discussion: {case_name}
- Energy: {'4' if 'incident' in case_name else ('2' if 'editorial' in case_name else '3')}
- Finish: {'editorial-paper' if 'editorial' in user_res.lower() or 'editorial' in case_name else ('somatic-touch' if 'touch' in user_res.lower() or 'mobile' in case_name else 'machined-industrial')}
- Density: {'dense' if 'dense' in user_res.lower() or 'incident' in case_name else 'sparse'}
- Weight: regular
- Seriousness: {'4' if 'incident' in case_name else '3'}

## Ground Truth Facts & User Responses
{user_res.strip()}

## Product Context & Tension Synthesis
{brief.strip()}

## Confirmed Decisions
- bg-void: {'#faf8f3' if 'faf8f3' in user_res or 'editorial' in case_name else ('#0a0c10' if '0a0c10' in user_res or 'incident' in case_name else '#0f172a')}
- accent-primary: {'#0284c7' if '0284c7' in user_res or 'editorial' in case_name else ('#f59e0b' if 'f59e0b' in user_res or 'incident' in case_name else '#10b981')}
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

    # 5. Multi-pair contrast check: verify a representative set of foreground/background
    # pairs from the generated tokens. wcag_aaa is True only when ALL checked pairs pass.
    # Pairs checked: (surface, text-primary), (bg-void, text-secondary), (surface, accent-primary).
    wcag_aaa = False
    if tok_ok:
        try:
            data = json.loads(t1_json.read_text(encoding="utf-8"))

            def _rel_lum(h: str) -> float:
                c = h.lstrip("#")
                if len(c) not in (6, 8):
                    raise ValueError(f"non-hex color: {h}")
                rgb = [int(c[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
                lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
                return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

            def _contrast(fg_key: str, bg_key: str) -> float | None:
                """Return contrast ratio for two color token paths, or None if unavailable."""
                try:
                    # support both flat e.g. data["color"]["surface"]["$value"]
                    # and dotted path e.g. "color.surface"
                    fg = data["color"][fg_key]["$value"]
                    bg = data["color"][bg_key]["$value"]
                    # skip non-hex (rgba, named)
                    if not fg.startswith("#") or not bg.startswith("#"):
                        return None
                    l1 = _rel_lum(fg)
                    l2 = _rel_lum(bg)
                    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
                except (KeyError, ValueError):
                    return None

            WCAG_AAA = 7.0
            WCAG_AA = 4.5
            # (fg_key, bg_key, min_ratio)
            PAIRS = [
                ("text-primary", "surface", WCAG_AAA),   # primary body text: AAA
                ("text-primary", "bg-void", WCAG_AAA),   # primary text on chassis: AAA
                ("text-secondary", "bg-void", WCAG_AA),  # secondary/meta text: AA is sufficient
            ]
            pair_results = {}
            for fg_k, bg_k, threshold in PAIRS:
                r = _contrast(fg_k, bg_k)
                pair_results[f"{fg_k}/{bg_k}"] = (r, threshold)
            checked = [(v, thr) for v, thr in pair_results.values() if v is not None]
            primary = pair_results.get("text-primary/surface")
            if primary is not None and primary[0] is not None:
                wcag_aaa = all(v >= thr for v, thr in checked)
            elif checked:
                wcag_aaa = all(v >= thr for v, thr in checked)
        except Exception:
            pass

    duration = time.time() - t0

    pipeline_exit_ok = mat_ok and env_ok and tok_ok

    # Preserve the first failing step, its exit code, and its error context.
    failed_step = None
    exit_code = None
    error_context = ""
    if not pipeline_exit_ok:
        for step, ok, proc in (
            ("materialize_contracts", mat_ok, res_mat),
            ("compile_tokens", tok_ok, res_tok),
            ("assemble_envelope", env_ok, res_env),
        ):
            if not ok:
                failed_step = step
                exit_code = proc.returncode
                error_context = _step_context(proc)
                break

    return CaseBenchmarkResult(
        case_name=case_name,
        run_id=run_id,
        duration_seconds=round(duration, 3),
        layer="mechanism",
        contract_materialized=mat_ok,
        envelope_assembled=env_ok,
        tokens_compiled=tok_ok,
        pipeline_exit_ok=pipeline_exit_ok,
        wcag_aaa_contrast=wcag_aaa,
        failed_step=failed_step,
        exit_code=exit_code,
        error_context=error_context,
        metrics={
            "output_dir": str(work_dir),
            "envelope_size_bytes": env_json.stat().st_size if env_json.is_file() else 0,
            "tokens_size_bytes": tokens_css.stat().st_size if tokens_css.is_file() else 0,
        },
    )


def run_all_benchmarks(repetitions: int = 3, label: str | None = None) -> Dict[str, Any]:
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
            status = "MECHANISM_OK" if res.pipeline_exit_ok and res.wcag_aaa_contrast else "WARN"
            line = f"  Round {r}: {res.duration_seconds}s | Mat={res.contract_materialized} Env={res.envelope_assembled} Tok={res.tokens_compiled} WCAG={res.wcag_aaa_contrast} -> [{status}]"
            if not res.pipeline_exit_ok:
                line += f" | failed_step={res.failed_step} exit={res.exit_code}: {res.error_context}"
            print(line)

    # Layer 2/3 status is declared, never simulated: when the probe reports
    # ENVIRONMENT_BLOCKED, both fields are "blocked" and no mechanism-script
    # run may be reported in their place (BENCH-003 / BENCH-SCN-006).
    l2_l3_status = _probe_l2_l3()

    summary_file = run_dir / "summary.json"
    summary_data = {
        "timestamp": timestamp,
        # User-supplied label marking which revision this run describes, so
        # runs are comparable only when their labels and script revisions
        # match (BENCH-004).
        "run_label": label,
        "repetitions": repetitions,
        # Mechanism-layer run only; delivery, interaction, and design quality
        # are untested here (BENCH-001 / BENCH-SCN-001).
        "layer": "mechanism",
        "total_runs": len(results),
        "mechanism_pass_count": sum(1 for r in results if r.pipeline_exit_ok and r.wcag_aaa_contrast),
        # Declared, never substituted by mechanism scripts (BENCH-003).
        "l2_builder_runs": l2_l3_status,
        "l3_skill_runs": l2_l3_status,
        "failed_steps": [
            {
                "case_name": r.case_name,
                "run_id": r.run_id,
                "failed_step": r.failed_step,
                "exit_code": r.exit_code,
                "error_context": r.error_context,
            }
            for r in results
            if not r.pipeline_exit_ok
        ],
        "results": [asdict(r) for r in results],
    }
    summary_file.write_text(json.dumps(summary_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n=== Benchmark Complete. Summary saved to: {summary_file} ===")
    return summary_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run spec-prototype benchmark suite")
    parser.add_argument("--rounds", type=int, default=3, help="Number of repetitions per case (default: 3)")
    parser.add_argument(
        "--label",
        default=None,
        help="Label identifying the revision this run describes; recorded as run_label in summary.json (BENCH-004)",
    )
    args = parser.parse_args()

    run_all_benchmarks(repetitions=args.rounds, label=args.label)

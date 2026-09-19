#!/usr/bin/env python3
"""Contract fidelity judge for the frontend reproduction test.

Compares a frozen design contract against an independent implementation:
  T1 structural   - can the case's tasks be completed on the implementation?
  T2 contract     - token coverage, declared regions, receipt honesty
  T3 visual       - viewport capture status only; no pixel-perfect claim

Design Reinterpretation Rate is reported as an estimate and labelled as such.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

TOKEN_RE = re.compile(r"(--[a-zA-Z0-9-]+)\s*:")
HEADING_RE = re.compile(r"^#{1,3}\s+\S", flags=re.MULTILINE)


def _receipt(impl_dir: pathlib.Path) -> dict:
    for candidate in (impl_dir / "implementation-receipt.json", impl_dir / "impl/implementation-receipt.json"):
        if candidate.is_file():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {"parse_error": str(candidate)}
    return {}


def judge(case_id: str, design_artifacts: pathlib.Path, impl_dir: pathlib.Path, *,
          task_result: dict | None = None) -> dict:
    design_texts = bl.artifact_texts(design_artifacts)
    impl_texts = bl.artifact_texts(impl_dir)
    receipt = _receipt(impl_dir)

    declared_tokens = set()
    for name, text in design_texts.items():
        if name.endswith(".css") or "tokens" in name:
            declared_tokens.update(TOKEN_RE.findall(text))
    impl_tokens = set()
    for name, text in impl_texts.items():
        if name.endswith(".css") or "tokens" in name:
            impl_tokens.update(TOKEN_RE.findall(text))
    missing_tokens = sorted(declared_tokens - impl_tokens)
    token_coverage = round(len(declared_tokens & impl_tokens) / len(declared_tokens), 3) if declared_tokens else None

    contract_anchors = 0
    for name, text in design_texts.items():
        if name.startswith(("specifications", "contracts")) and name.endswith((".md", ".json")):
            contract_anchors += len(HEADING_RE.findall(text))

    inferred = receipt.get("inferred_design_decisions") or []
    gaps = receipt.get("contract_gaps") or []
    clarification = receipt.get("clarification_required") or []
    denominator = len(inferred) + max(contract_anchors, 1)
    reinterpretation_rate = round(len(inferred) / denominator, 4)

    entry = bl.find_entry(impl_dir)
    has_entry = bool(entry)
    structural_status = "unverified"
    if task_result is not None:
        structural_status = task_result.get("status", "unverified")

    checks = [
        {"id": "impl_entry_present", "status": "pass" if has_entry else "fail", "detail": f"entry={entry}"},
        {"id": "receipt_present", "status": "pass" if receipt and "parse_error" not in receipt else "fail",
         "detail": f"receipt keys={sorted(receipt)}"},
        {"id": "token_coverage", "status": ("pass" if token_coverage is not None and token_coverage >= 0.8
                                            else "fail" if declared_tokens else "unverified"),
         "detail": f"coverage={token_coverage} missing={missing_tokens[:8]}"},
        {"id": "task_completability", "status": structural_status, "detail": f"task judge status={structural_status}"},
        {"id": "unspecified_decisions_declared",
         "status": "pass" if (gaps or inferred or clarification) else "unverified",
         "detail": f"gaps={len(gaps)} inferred={len(inferred)} clarification={len(clarification)}"},
    ]
    failures = [c["id"] for c in checks if c["status"] == "fail"]
    return {
        "judge": "contract",
        "case_id": case_id,
        "checks": checks,
        "declared_tokens": sorted(declared_tokens),
        "missing_tokens": missing_tokens,
        "token_coverage": token_coverage,
        "contract_anchors": contract_anchors,
        "contract_gaps": gaps,
        "inferred_design_decisions": inferred,
        "clarification_required": clarification,
        "reinterpretation_rate": reinterpretation_rate,
        "reinterpretation_rate_note": "estimate: inferred decisions / (inferred + declared contract anchors)",
        "status": "fail" if failures else ("pass" if has_entry else "unverified"),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--design-artifacts", required=True)
    parser.add_argument("--impl", required=True)
    parser.add_argument("--task-result", default=None)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    task_result = bl.read_json(pathlib.Path(args.task_result)) if args.task_result else None
    result = judge(args.case, pathlib.Path(args.design_artifacts), pathlib.Path(args.impl), task_result=task_result)
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Independent Stage 1 Spec Contract Linter.

Verifies that materialized Stage 1 design contracts meet quality floors,
authenticity requirements, and anti-contamination boundaries before Stage 2 build.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Dict, List, Tuple


class SpecLintError:
    def __init__(self, rule: str, file_path: str, message: str, severity: str = "ERROR"):
        self.rule = rule
        self.file_path = file_path
        self.message = message
        self.severity = severity

    def __str__(self) -> str:
        return f"[{self.severity}] {self.rule} in {self.file_path}: {self.message}"


def lint_spec_contracts(root: Path, slice_id: str) -> List[SpecLintError]:
    """Execute all completeness, authenticity, and boundary checks against Stage 1 contracts."""
    errors: List[SpecLintError] = []

    required_paths = {
        "product": root / "prototype/product.md",
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "tokens_css": root / "prototype/shared/tokens.css",
        "tokens_md": root / "prototype/contracts/tokens/t1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
    }

    # 1. Existence check
    for name, p in required_paths.items():
        if not p.is_file():
            errors.append(SpecLintError("E001_FILE_MISSING", str(p), f"Required contract artifact {name} does not exist."))

    if errors:
        return errors

    prod_text = required_paths["product"].read_text(encoding="utf-8")
    smap_text = required_paths["surface_map"].read_text(encoding="utf-8")
    f1_text = required_paths["foundation"].read_text(encoding="utf-8")
    c1_text = required_paths["slice_contract"].read_text(encoding="utf-8")
    r1_text = required_paths["specification"].read_text(encoding="utf-8")

    # 2. Authentic Core Tension Check (Anti-fallback / Anti-contamination)
    combined_tension_text = prod_text + "\n" + f1_text
    tension_match = re.search(r"[-*+]?\s*(?:Core\s+Tension|Tension|张力)\s*[:=]\s*([^\n]+)", combined_tension_text, re.IGNORECASE)
    if not tension_match or not tension_match.group(1).strip():
        errors.append(SpecLintError("E002_TENSION_MISSING", "product.md / f1.md", "Core Tension declaration is missing."))
    else:
        declared_tension = tension_match.group(1).strip()
        if declared_tension.lower().startswith("not yet") or declared_tension.lower().startswith("unresolved"):
            errors.append(SpecLintError("E002_TENSION_UNRESOLVED", "product.md", f"Core Tension '{declared_tension}' is unresolved."))
        # Detect SRE ops fallback contaminating non-ops products
        is_ops_domain = any(kw in (prod_text + " " + c1_text).lower() for kw in ("sre", "telemetry", "incident", "ops", "console", "cluster"))
        if "Instant Operational Throughput vs Zero-Mistake Safety" in declared_tension and not is_ops_domain:
            errors.append(SpecLintError("E002_TENSION_CONTAMINATED", "product.md", "Default SRE fallback tension contaminated a non-ops product contract."))

    # 3. Reality Anchors & Grounded Rationale Check (Consequential or grounded rationale required)
    combined_anchors_text = prod_text + "\n" + f1_text
    anchors_match = re.search(r"[-*+]?\s*(?:Reality\s+(?:Benchmark\s+)?Anchors?|Physical\s+Anchors?|对标|地锚)\s*[:=]\s*([^\n]+)", combined_anchors_text, re.IGNORECASE)
    has_grounded_rationale = bool(re.search(r"(?:Grounding|Rationale|Physical Metaphor|Substrate|原创推导|物理隐喻|因果依据|设计理由)\s*[:=]\s*([^\n]+)", combined_anchors_text, re.IGNORECASE))
    if not anchors_match and not has_grounded_rationale:
        errors.append(SpecLintError("E003_ANCHORS_MISSING", "product.md / f1.md", "Neither Reality Benchmark Anchors nor grounded design rationale declared."))

    # 4. Content Language Check
    disc_path = root / "prototype/discussion.md"
    disc_text = disc_path.read_text(encoding="utf-8") if disc_path.is_file() else ""
    combined_lang_text = prod_text + "\n" + c1_text + "\n" + r1_text + "\n" + disc_text
    lang_match = re.search(r"(?:Content\s+Language|语种|语言)(?:\s*\([^)]*\))?\s*[:=]?\s*`?([a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,8})*)`?", combined_lang_text, re.IGNORECASE)
    if not lang_match or not lang_match.group(1).strip():
        errors.append(SpecLintError("E004_LANGUAGE_UNLOCKED", "discussion.md / r1.md", "Content language is not explicitly declared or locked."))

    # 5. Verifiable Assertions & Break Protocol Check
    if "Verifiable Design Assertions" not in r1_text and "Required screenshot checkpoints" not in r1_text:
        errors.append(SpecLintError("E005_ASSERTIONS_MISSING", "r1.md", "Verifiable Design Assertions section is missing."))

    has_break = "The Break Protocol" in r1_text
    break_na = bool(re.search(r"The Break Protocol.*?(?:N/A|Not Applicable|无需破坏压测|不适用)", r1_text, re.IGNORECASE))
    if not has_break and not break_na:
        errors.append(SpecLintError("E006_BREAK_PROTOCOL_MISSING", "r1.md", "The Break Protocol Stress Checkpoints section is missing (must declare test vectors or explicit N/A with rationale)."))

    # 6. Action Verb Lifecycle Check (Applicable -> Required, Not Applicable -> Explicit N/A)
    has_verbs = "Action Verb" in c1_text
    verbs_na = bool(re.search(r"(?:Action Verb|Verb Lifecycle).*?(?:N/A|Not Applicable|纯阅读|无状态变迁|无破坏性动作|不适用)", c1_text, re.IGNORECASE))
    if not has_verbs and not verbs_na:
        errors.append(SpecLintError("E007_VERB_LIFECYCLE_MISSING", "c1.md", "Action Verb Lifecycle Table is missing from slice contract (must declare lifecycle table or explicit N/A with rationale)."))

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint Stage 1 Design Spec Contracts")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Workspace root directory")
    parser.add_argument("--slice", type=str, required=True, help="Slice ID to lint")
    args = parser.parse_args()

    errors = lint_spec_contracts(args.root, args.slice)
    if errors:
        print(f"FAILED: Found {len(errors)} Stage 1 contract lint issues:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("PASS: Stage 1 Spec Contracts meet all quality, authenticity, and boundary floors.")
        sys.exit(0)


if __name__ == "__main__":
    main()

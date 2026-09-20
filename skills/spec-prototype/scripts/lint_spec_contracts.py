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
from typing import Dict, List, Optional, Tuple


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
        errors.append(SpecLintError("E002_TENSION_MISSING", "product.md / f1.md", "Core Tension declaration is missing. Define an authentic domain tension (e.g. 'Operational Throughput vs Incident Safety' or 'Frictionless Onboarding vs Deep Orchestration') in prototype/discussion.md before entering Stage 2."))
    else:
        declared_tension = tension_match.group(1).strip()
        if declared_tension.lower().startswith("not yet") or declared_tension.lower().startswith("unresolved"):
            errors.append(SpecLintError("E002_TENSION_UNRESOLVED", "product.md", f"Core Tension '{declared_tension}' is unresolved. As a P9 design copilot, establish a definitive business/UX tension in prototype/discussion.md to drive trade-off decisions."))
        # Detect SRE ops fallback contaminating non-ops products
        is_ops_domain = any(kw in (prod_text + " " + c1_text).lower() for kw in ("sre", "telemetry", "incident", "ops", "console", "cluster"))
        if "Instant Operational Throughput vs Zero-Mistake Safety" in declared_tension and not is_ops_domain:
            errors.append(SpecLintError("E002_TENSION_CONTAMINATED", "product.md", "Default SRE fallback tension ('Instant Operational Throughput vs Zero-Mistake Safety') contaminated a non-ops product contract. Formulate a domain-specific tension authentic to this product."))

    # 3. Reality Anchors & Grounded Rationale Check (Consequential or grounded rationale required)
    combined_anchors_text = prod_text + "\n" + f1_text
    anchors_match = re.search(r"[-*+]?\s*(?:Reality\s+(?:Benchmark\s+)?Anchors?|Physical\s+Anchors?|对标|地锚)\s*[:=]\s*([^\n]+)", combined_anchors_text, re.IGNORECASE)
    has_grounded_rationale = bool(re.search(r"(?:Grounding|Rationale|Physical Metaphor|Substrate|原创推导|物理隐喻|因果依据|设计理由)\s*[:=]\s*([^\n]+)", combined_anchors_text, re.IGNORECASE))
    if not anchors_match and not has_grounded_rationale:
        errors.append(SpecLintError("E003_ANCHORS_MISSING", "product.md / f1.md", "Neither Reality Benchmark Anchors nor grounded design rationale declared. Anchor the interface to real-world industrial or lifeworld baselines (e.g. Linear, Datadog, iA Writer, physical detents) in prototype/product.md."))

    # 4. Content Language Check
    disc_path = root / "prototype/discussion.md"
    disc_text = disc_path.read_text(encoding="utf-8") if disc_path.is_file() else ""
    combined_lang_text = prod_text + "\n" + c1_text + "\n" + r1_text + "\n" + disc_text
    lang_match = re.search(r"(?:Content\s+Language|语种|语言)(?:\s*\([^)]*\))?\s*[:=]?\s*`?([a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,8})*)`?", combined_lang_text, re.IGNORECASE)
    if not lang_match or not lang_match.group(1).strip():
        errors.append(SpecLintError("E004_LANGUAGE_UNLOCKED", "discussion.md / r1.md", "Content language is not explicitly declared or locked. Declare Content Language (e.g. 'zh-CN', 'en-US') in discussion.md or product.md to ensure copy consistency."))

    # 5. Verifiable Assertions & Break Protocol Check
    if "Verifiable Design Assertions" not in r1_text and "Required screenshot checkpoints" not in r1_text:
        errors.append(SpecLintError("E005_ASSERTIONS_MISSING", "r1.md", "Verifiable Design Assertions section is missing."))

    has_break = "The Break Protocol" in r1_text
    break_na = bool(re.search(r"The Break Protocol.*?(?:N/A|Not Applicable|无需破坏压测|不适用)", r1_text, re.IGNORECASE))
    if not has_break and not break_na:
        errors.append(SpecLintError("E006_BREAK_PROTOCOL_MISSING", "r1.md", "The Break Protocol Stress Checkpoints section is missing from r1.md (declare stress vectors such as 0/1/1000 items, long string overflows, 320px fold, or explicit N/A with rationale)."))

    # 6. Action Verb Lifecycle Check (Applicable -> Required, Not Applicable -> Explicit N/A)
    has_verbs = "Action Verb" in c1_text
    verbs_na = bool(re.search(r"(?:Action Verb|Verb Lifecycle).*?(?:N/A|Not Applicable|纯阅读|无状态变迁|无破坏性动作|不适用)", c1_text, re.IGNORECASE))
    if not has_verbs and not verbs_na:
        errors.append(SpecLintError("E007_VERB_LIFECYCLE_MISSING", "c1.md", "Action Verb Lifecycle Table is missing from slice contract c1.md (declare atomic Trigger->Context->Commit->Feedback verbs or explicit N/A with rationale)."))

    return errors


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


# The retained selection record declares the map identity the scope was chosen
# against. Accept the documented template wording and a bare key; a revision may
# carry the template's `/ status` tail, which is not part of the identity.
_SELECTION_REVISION_RE = re.compile(
    r"^[ \t\-*+]*(?:surface[ _-]?map[ _-]?)?revision[ \t]*[:=][ \t]*([^\n#]+)",
    re.IGNORECASE | re.MULTILINE)
_SELECTION_DIGEST_RE = re.compile(
    r"^[ \t\-*+]*(?:surface[ _-]?map[ _-]?)?digest[ \t]*[:=][ \t]*"
    r"(?:sha256:)?([0-9a-fA-F]{64})",
    re.IGNORECASE | re.MULTILINE)


def retained_map_identity(root: Path) -> Tuple[Optional[str], Optional[str]]:
    """The map revision and digest the retained selection was made against.

    `selection-source` names the record that chose this scope, so that record
    owns the identity the formal entry compares against — not the working file's
    current revision, which is what a stale map would present. A record that is
    absent, outside the repository or silent about identity yields no expectation
    and adds no refusal; the map's own facts still stand on their own.
    """
    import prototype_context

    resolved_root = root.resolve()
    map_text = _read(resolved_root / "prototype/contracts/surface-maps/m1.md")
    source = (prototype_context.read_context(map_text)["surface_map"]["selection_source"]
              or "").strip().strip("`'\"")
    if not source:
        return None, None
    record = resolved_root / source
    if not record.is_file() or not record.resolve().is_relative_to(resolved_root):
        return None, None
    text = record.read_text(encoding="utf-8")
    revision = _SELECTION_REVISION_RE.search(text)
    digest = _SELECTION_DIGEST_RE.search(text)
    expected_revision = revision.group(1).split("/")[0].split()[0].strip("`'\"") if revision else None
    return expected_revision, (digest.group(1).lower() if digest else None)


def read_formal_context(root: Path, slice_id: str) -> Dict[str, object]:
    """Normalize authored coverage/platform facts for the formal path.

    The retained selection supplies the expected map identity, so an authored map
    that moved past its retained revision or digest is reported here rather than
    dispatching against a scope nobody selected.
    """
    import prototype_context

    expected_revision, expected_digest = retained_map_identity(root)
    return prototype_context.read_context(
        _read(root / "prototype/contracts/surface-maps/m1.md"),
        _read(root / "prototype/product.md"),
        _read(root / "prototype/contracts/foundation/f1.md"),
        _read(root / f"prototype/specifications/{slice_id}/r1.md"),
        expected_map_revision=expected_revision,
        expected_map_digest=expected_digest,
    )


def lint_formal_entry(root: Path, slice_id: str) -> List[SpecLintError]:
    """Lint the formal entry itself: canonical paths, selected IDs, coverage authority.

    Content lint (lint_spec_contracts) is a subset of this. Every failure keeps the
    offending path and detail; nothing is repaired or widened on the caller's behalf.
    """
    errors: List[SpecLintError] = list(lint_spec_contracts(root, slice_id))
    resolved_root = root.resolve()

    # Canonical paths: no symlink and no escape out of the repository root.
    canonical = {
        "product": root / "prototype/product.md",
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
    }
    for name, path in canonical.items():
        if path.is_symlink():
            errors.append(SpecLintError("E012_PATH_ESCAPE", str(path),
                                        f"{name} must be a regular contract file, not a symlink."))
        elif path.is_file() and not path.resolve().is_relative_to(resolved_root):
            errors.append(SpecLintError("E012_PATH_ESCAPE", str(path),
                                        f"{name} resolves outside the repository root."))

    context = read_formal_context(root, slice_id)
    codes = {error["code"] for error in context["errors"]}
    map_facts = context["surface_map"]

    if context["recommendation_required"]:
        errors.append(SpecLintError(
            "E008_COVERAGE_UNRESOLVED", "m1.md",
            f"Coverage is {map_facts['coverage']!r}; a recommended combination must be "
            "selected and authored before a formal build. Absent selection is never full-product."))
    if "missing_selection_source" in codes:
        errors.append(SpecLintError("E009_SELECTION_SOURCE_MISSING", "m1.md",
                                    "A selected coverage declares no retained selection source."))
    stale = [error["detail"] for error in context["errors"]
             if error["code"] == "stale_map_identity"]
    if stale:
        errors.append(SpecLintError("E010_STALE_CONTRACT", "m1.md",
                                    "Surface Map identity does not match the retained selection: "
                                    f"{'; '.join(stale)}."))
    if "unknown_platform_context" in codes:
        errors.append(SpecLintError("E013_PLATFORM_CONTEXT_UNKNOWN", "m1.md",
                                    "Applicability references an undeclared platform context."))
    invalid = sorted(codes & {"duplicate_surface_id", "unknown_surface_id", "empty_selection"})
    if invalid:
        errors.append(SpecLintError("E014_SELECTION_INVALID", "m1.md",
                                    f"Selection identities are not well-formed: {', '.join(invalid)}."))

    # Widening asks whether a target was added outside the declared selection, so
    # it applies only to a `selected` coverage. A `full-product` selection names no
    # surface by design: it authorizes every applicable surface of the bound map
    # revision, and comparing that target set against an empty list is the wrong
    # question. An empty `selected` coverage still authorizes nothing and is refused.
    selected = list(map_facts["selected_surfaces"])
    if map_facts["coverage"] == "selected":
        widened = [s for s in map_facts["target_surfaces"] if s not in selected]
        if widened:
            errors.append(SpecLintError("E011_SELECTION_WIDENED", "m1.md",
                                        f"Target surfaces {widened} are outside the selected set {selected}."))
        if not selected:
            errors.append(SpecLintError("E011_SELECTION_WIDENED", "m1.md",
                                        "Selected coverage produced an empty target set."))

    return errors


def lint_formal_advisories(root: Path, slice_id: str) -> List[SpecLintError]:
    """Non-blocking diagnostics for the formal entry.

    The reader gates a differing logical revision, so a digest that drifted under a
    matched revision is surfaced here as a WARNING: the caller sees the drift without
    losing dispatch. Kept separate from `lint_formal_entry` so a refusal stays a
    refusal and no advisory is ever read as one.
    """
    context = read_formal_context(root, slice_id)
    return [SpecLintError("W010_ADVISORY_MAP_DIGEST", "m1.md",
                          "Surface Map digest does not match the retained selection "
                          f"(non-blocking; revision matches): {advisory['detail']}.",
                          severity="WARNING")
            for advisory in context["diagnostics"]]


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

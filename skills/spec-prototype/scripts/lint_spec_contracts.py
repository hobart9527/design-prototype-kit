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
    elif has_verbs:
        # A declared Proximity level must be a real level: the ladder is the
        # contract the Builder translates into a container, so an out-of-range
        # value silently becomes a wrong interaction shape downstream. Scoped to
        # the verb table so a "Level 5" elsewhere in the contract cannot trip it,
        # and only a table that opted into the column is checked; a legacy table
        # without it stays valid, its level inferred from the container.
        section = re.search(r"##[^\n]*Action Verb Lifecycle[^\n]*\n(.*?)(?=\n##|\Z)", c1_text, re.S)
        if section and "proximity" in section.group(1).lower():
            invalid = sorted({int(level) for level in re.findall(r"\bLevel\s*([0-9]+)\b", section.group(1))
                              if int(level) > 4})
            if invalid:
                errors.append(SpecLintError("E015_PROXIMITY_LEVEL_INVALID", "c1.md",
                                            f"Container Proximity Level(s) {invalid} are outside the defined 0~4 ladder. "
                                            "Levels above 4 have no container form; state the level that matches the hazard."))

    # 7. Cross-Artifact Lifecycle Consistency Check
    status_re = re.compile(r"^[ \t\-*+]*(?:Status|Lifecycle|Authority status)[ \t]*[:=][ \t]*`?([a-zA-Z0-9_\- ]+)`?", re.IGNORECASE | re.MULTILINE)
    statuses: Dict[str, str] = {}
    for name, text in [("f1", f1_text), ("c1", c1_text), ("r1", r1_text)]:
        m = status_re.search(text)
        if m:
            statuses[name] = m.group(1).strip().lower()

    if disc_text:
        m = status_re.search(disc_text)
        if m:
            statuses["discussion"] = m.group(1).strip().lower()

    # Check for glaring contradiction: draft/pending vs sealed/frozen
    is_sealed = any("sealed" in s or "frozen" in s for s in statuses.values())
    has_draft = any("draft" in s or "pending" in s for s in statuses.values())
    if is_sealed and has_draft:
        errors.append(SpecLintError(
            "E016_LIFECYCLE_CONTRADICTION", "contracts",
            f"Cross-artifact lifecycle contradiction detected across artifacts: {statuses}. "
            "Artifacts cannot simultaneously declare draft/pending and sealed provisional."
        ))

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


def lint_canonical_spec_ir(root: Path, slice_id: str, candidate_id: str = "r1") -> List[SpecLintError]:
    """Validate canonical specification IR against JSON Schema Draft 2020-12 and boundary gates.

    Tier-aware per the T-01 progressive schema: an `intent_spec` validates at
    its tier and is never demanded the `execution_spec`-only state machine and
    action contracts; only an IR that claims `execution_spec` must carry them.
    Also runs the tokens freshness fuse: hand-edited or stale tokens.css fails
    the lint with the drift named.
    """
    errors: List[SpecLintError] = []
    schema_path = root / "skills/spec-prototype/schemas/prototype-spec.v1.json"
    if not schema_path.is_file():
        # Fallback to relative from script
        schema_path = Path(__file__).resolve().parent.parent / "schemas/prototype-spec.v1.json"
    ir_path = root / f"prototype/contracts/compiled/{slice_id}/{candidate_id}.spec.json"

    if not ir_path.is_file():
        errors.append(SpecLintError("E001_FILE_MISSING", str(ir_path),
                                    f"Canonical Spec IR for slice '{slice_id}' does not exist."))
        return errors

    try:
        data = json.loads(ir_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(SpecLintError("E010_MALFORMED_JSON", str(ir_path), f"JSON parse error: {exc}"))
        return errors

    try:
        import jsonschema
        if schema_path.is_file():
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            jsonschema.validate(instance=data, schema=schema)
    except ImportError:
        pass
    except Exception as exc:
        errors.append(SpecLintError("E020_SCHEMA_VALIDATION_FAILED", str(ir_path), f"Schema validation error: {exc}"))

    spec_tier = data.get("spec_tier", "execution_spec")
    state_model = data.get("state_model") or {}
    actions = data.get("actions") or []

    # Tier admission: only an execution_spec claim demands the Stage 3/4 state
    # machine. An intent_spec validates at its tier — demanding execution_spec
    # fields here would reject every legitimate Stage 1 compilation.
    if spec_tier == "execution_spec":
        missing_tiers = [key for key in ("state_model", "actions") if not data.get(key)]
        empty_state = spec_tier == "execution_spec" and not any(
            (state_model.get(k) for k in ("domain_states", "interaction_states", "data_scenarios", "stress_fixtures"))
        )
        if missing_tiers or empty_state:
            errors.append(SpecLintError("E021_TIER_ADMISSION_FAILED", str(ir_path),
                                        f"IR declares spec_tier 'execution_spec' but lacks the Stage 3/4 "
                                        f"state machine and action contracts: missing={missing_tiers}, "
                                        f"empty_state_model={empty_state}."))

    # Tokens freshness fuse: the compiled stylesheet must still derive from its
    # source. Hand edits are a hard lint failure with the drift named, so the
    # build cannot silently admit someone else's palette.
    tokens_css = root / "prototype/shared/tokens.css"
    if tokens_css.is_file():
        try:
            import compile_tokens
            sync = compile_tokens.check_tokens_sync(str(tokens_css), str(root / "prototype/discussion.md"))
        except Exception as exc:
            sync = {"state": "out_of_sync", "drift": f"freshness fuse failed to run: {type(exc).__name__}: {exc}"}
        if sync.get("state") == "out_of_sync":
            errors.append(SpecLintError("E022_TOKENS_OUT_OF_SYNC", str(tokens_css),
                                        f"tokens.css is out_of_sync; downstream consumption is rejected. "
                                        f"Drift: {sync.get('drift', 'unknown')}."))

    # Boundary and integrity checks
    coverage = data.get("scope", {}).get("topology_scope", {}).get("coverage")
    if not coverage or coverage in ("unresolved", "legacy"):
        errors.append(SpecLintError("E008_COVERAGE_UNRESOLVED", str(ir_path),
                                    f"Canonical IR coverage is {coverage!r}; valid topology coverage must be selected."))

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
    parser.add_argument("--candidate", type=str, default="r1", help="Candidate revision (e.g. r1)")
    parser.add_argument("--canonical-only", action="store_true", help="Validate canonical IR schema and boundary only")
    parser.add_argument("--no-formal", action="store_true", help="Skip formal entry check")
    args = parser.parse_args()

    if args.canonical_only or (args.root / f"prototype/contracts/compiled/{args.slice}/{args.candidate}.spec.json").is_file():
        # When canonical IR is present or explicitly selected, run canonical IR schema and boundary lint
        errors = lint_canonical_spec_ir(args.root, args.slice, args.candidate)
    else:
        errors = lint_spec_contracts(args.root, args.slice)
        if not args.no_formal:
            try:
                formal_errors = lint_formal_entry(args.root, args.slice)
                errors.extend(formal_errors)
            except Exception as exc:
                errors.append(SpecLintError("E099_INTERNAL_VALIDATOR_ERROR", "linter", f"Internal validator unexpected error: {type(exc).__name__}: {exc}"))
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

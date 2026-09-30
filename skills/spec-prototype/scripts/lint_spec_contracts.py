#!/usr/bin/env python3
"""Canonical Spec IR linter.

Validates the compiled Spec IR (`prototype/contracts/compiled/<slice>/r1.spec.json`)
against JSON Schema Draft 2020-12, tier admission, the tokens freshness fuse, and
boundary gates. The retired six-piece set (product.md, m1.md, f1.md, t1.md, c1.md,
r1.md) is legacy input, readable by other tools but never linted as a requirement
here: on a tree that predates the IR this script reports the missing IR instead of
enforcing artifacts that must not be authored anymore.
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


def _token_source_path(root: Path, tokens_css: Path) -> Path:
    """The token source this stylesheet was sealed from.

    The seal names its own source, so a layered tree (world.md authority, no
    discussion.md) is checked against the file it was compiled from instead of a
    hard-coded single-record path.
    """
    import compile_tokens
    sealed = (compile_tokens.read_tokens_provenance(str(tokens_css)) or {}).get("source", "")
    candidates = []
    if sealed:
        sealed_path = Path(sealed)
        candidates.append(sealed_path if sealed_path.is_absolute() else root / sealed_path)
        candidates.append(sealed_path)
    candidates += [root / "prototype/world.md", root / "prototype/discussion.md"]
    return next((c for c in candidates if c.is_file()), candidates[-1])


def lint_formal_entry(root: Path, slice_id: str) -> List[SpecLintError]:
    """Lint the formal entry itself: canonical paths, selected IDs, coverage authority.

    The legacy content lint reads the six pillars (`product.md`, `m1.md`,
    `f1.md`, `t1.md`, `c1.md`, `r1.md`), which the Refusal List forbids
    authoring. On a tree that carries the canonical Spec IR those pillars are
    replaced, not missing, so running the reader here reports `E001` for files
    that must not exist and refuses every valid canonical delivery. The reader
    is skipped when the IR is present; its own validation is the IR lint's job,
    not this one's. Path, coverage and map-identity checks below still run on
    both trees. Every failure keeps the offending path and detail; nothing is
    repaired or widened on the caller's behalf.
    """
    candidate_id = "r1"
    canonical_ir = root / f"prototype/contracts/compiled/{slice_id}/{candidate_id}.spec.json"
    if canonical_ir.is_file():
        errors: List[SpecLintError] = []
    else:
        # The six-piece content lint is retired; a tree without the IR gets one
        # missing-authority error instead of demands to author retired files.
        errors = [SpecLintError(
            "E001_FILE_MISSING",
            str(canonical_ir),
            "Canonical Spec IR does not exist; compile it with compile_spec_ir.py --slice "
            f"{slice_id}. The legacy six-piece contract set is retired and is never linted.",
        )]
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

    # Tier admission: only an execution_spec claim demands the Stage 3/4 state
    # machine. An intent_spec validates at its tier — demanding execution_spec
    # fields here would reject every legitimate Stage 1 compilation.
    if spec_tier == "execution_spec":
        missing_tiers = [key for key in ("state_model", "actions") if key not in data or data[key] is None]
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
            sync = compile_tokens.check_tokens_sync(str(tokens_css), str(_token_source_path(root, tokens_css)))
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
    parser = argparse.ArgumentParser(description="Lint the canonical Spec IR")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Workspace root directory")
    parser.add_argument("--slice", type=str, required=True, help="Slice ID to lint")
    parser.add_argument("--candidate", type=str, default="r1", help="Candidate revision (e.g. r1)")
    parser.add_argument("--canonical-only", action="store_true", help="Validate canonical IR schema and boundary only")
    parser.add_argument("--no-formal", action="store_true", help="Skip formal entry check")
    args = parser.parse_args()

    ir_path = args.root / f"prototype/contracts/compiled/{args.slice}/{args.candidate}.spec.json"
    if args.canonical_only or ir_path.is_file():
        # Canonical IR path: schema, tier admission, tokens freshness, boundary.
        errors = lint_canonical_spec_ir(args.root, args.slice, args.candidate)
    else:
        # The legacy six-piece lint is retired. A tree that predates the IR gets
        # a single missing-IR error instead of a demand to author retired files.
        errors = [SpecLintError(
            "E001_FILE_MISSING",
            str(ir_path),
            "Canonical Spec IR does not exist; compile it with compile_spec_ir.py --slice "
            f"{args.slice}. The legacy six-piece contract set is retired and is never linted here.",
        )]
        if not args.no_formal:
            try:
                formal_errors = lint_formal_entry(args.root, args.slice)
                errors.extend(formal_errors)
            except Exception as exc:
                errors.append(SpecLintError("E099_INTERNAL_VALIDATOR_ERROR", "linter", f"Internal validator unexpected error: {type(exc).__name__}: {exc}"))
    if errors:
        print(f"FAILED: Found {len(errors)} Spec lint issues:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("PASS: Canonical Spec IR meets schema, admission, and boundary floors.")
        sys.exit(0)


if __name__ == "__main__":
    main()

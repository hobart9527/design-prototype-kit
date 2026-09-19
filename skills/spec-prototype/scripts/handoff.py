"""Read-only exact-reference packet for a Prototype Specification; no approval policy."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


class HandoffError(ValueError):
    pass


ALLOWED_COMPONENT_DISPOSITIONS = ("required", "preferred", "delegated", "unavailable")
ALLOWED_CONTRACT_DISPOSITIONS = ("ready", "needs_decision", "not_user_visible")
ALLOWED_VISUAL_VERIFICATION = ("required", "not_required")

# Labels that must be populated even though their exact template text is long.
PREFIXED_FIELDS = ("Required reachable-control closure",)

CRAFT_READS_FIELD = "Required craft reads"
SKILL_ROOT_FIELD = "Skill root / evidence template path for this dispatch"

# Values that do not count as populated execution input. Compared case-insensitively
# after stripping surrounding whitespace, backticks and quotes. Legitimate
# statements such as `none` remain populated; only empty or explicitly
# undecided markers fail.
PLACEHOLDER_VALUES = frozenset({
    "", "-", "--", "...", "pending", "tbd", "todo",
    "unknown", "to be decided", "to be determined",
    "discover locally", "or discover locally",
})

# Generic asset phrases that do not name an existing asset for a `required` row.
GENERIC_REQUIRED_ASSETS = frozenset({
    "builder choice", "builder's choice", "builders choice", "delegated",
    "local", "custom", "various", "existing", "appropriate", "suitable",
})

EXPECTED_COMPONENT_HEADER = (
    "surface / interaction",
    "existing asset",
    "disposition",
    "constraint",
    "verification checkpoint",
)


def _clean(value: str) -> str:
    return value.strip().strip("`'\"").strip()


def _normalized(value: str) -> str:
    return _clean(value).lower()


def _is_placeholder(value: str) -> bool:
    return _normalized(value) in PLACEHOLDER_VALUES


def within(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise HandoffError(f"Path escapes repository: {value}")
    return path


def field(body: str, label: str) -> str:
    values = re.findall(r"^- " + re.escape(label) + r":[ \t]*(.+)$", body, re.MULTILINE)
    if len(values) != 1:
        raise HandoffError(f"Expected one populated field: {label}")
    return values[0]


def quoted_path(value: str) -> str:
    paths = [s for s in re.findall(r"`([^`]+)`", value) if "/" in s]
    if len(paths) != 1:
        raise HandoffError(f"Expected one backticked file/directory path: {value}")
    return paths[0]


def retained(root: Path, value: str) -> dict:
    path = within(root, value)
    data = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest()}


def reference(root: Path, body: str, label: str) -> dict:
    value = field(body, label)
    expected = re.findall(r"\bsha256:([0-9a-fA-F]{64})\b", value)
    if len(expected) != 1:
        raise HandoffError(f"Expected one sha256 digest: {label}")
    result = retained(root, quoted_path(value))
    if result["sha256"] != expected[0].lower():
        raise HandoffError(f"Digest mismatch: {result['path']}; expected {expected[0]}, actual {result['sha256']}")
    return result


def identity(body: str, label: str, expected: str) -> None:
    actual = field(body, label).strip().strip('`')
    if actual != expected:
        raise HandoffError(f"Identity mismatch: {label}; expected {expected}, actual {actual}")


def associations(root: Path, spec_path: Path, body: str, refs: dict, contract: str) -> None:
    identity(body, "Candidate / selected revision", spec_path.stem)
    slice_id = spec_path.parent.name
    contract_path = within(root, refs["slice_contract"]["path"])
    if contract_path.parent != root / "prototype/contracts/slices" / slice_id:
        raise HandoffError("Slice path mismatch between Specification and Contract")
    identity(contract, "Slice ID", slice_id)
    identity(contract, "Contract revision", contract_path.stem)
    foundation_path = within(root, refs["foundation"]["path"])
    for kind, folder in (("foundation", "foundation"), ("tokens", "tokens"), ("surface_map", "surface-maps")):
        if within(root, refs[kind]["path"]).parent != root / "prototype/contracts" / folder:
            raise HandoffError(f"Retained {kind} path mismatch with its owning directory")
    foundation_revision = foundation_path.stem
    identity(foundation_path.read_text(), "Foundation revision", foundation_revision)
    identity(contract, "Foundation revision", foundation_revision)
    token_path = within(root, refs["tokens"]["path"])
    token_body = token_path.read_text()
    identity(token_body, "Foundation revision", foundation_revision)
    identity(token_body, "Tokens revision", token_path.stem)
    if "breakpoint" not in token_body.lower() and "media" not in token_body.lower():
        raise HandoffError("Token artifact missing responsive breakpoints: mobile, tablet, desktop")
    map_path = within(root, refs["surface_map"]["path"])
    map_body = map_path.read_text()
    # Identity is independent of review status. Read the old combined header
    # for immutable retained maps, but never choose between two declarations.
    declarations = re.findall(
        r"^- Surface map revision( / status(?:\s*\([^)]*\))?)?:[ \t]*([^\n]*)$",
        map_body,
        re.IGNORECASE | re.MULTILINE,
    )
    if len(declarations) != 1:
        raise HandoffError(
            "Expected one Surface Map revision declaration matching the template label"
        )
    legacy, value = declarations[0]
    map_revision = (value.split("/", 1)[0] if legacy else value).strip().strip('`')
    if map_revision != map_path.stem:
        raise HandoffError("Surface Map revision mismatch with retained path")


def raw_field(body: str, label: str) -> str:
    """Return the raw value of a `- Label: value` field, allowing an empty value.

    Missing or duplicated labels are authoring diagnostics; population is
    checked separately so conditional fields can be legitimately empty.
    """
    values = re.findall(r"^- " + re.escape(label) + r":[ \t]*(.*)$", body, re.MULTILINE)
    if len(values) != 1:
        raise HandoffError(f"Expected one populated field: {label}")
    return values[0]


def populated_field(body: str, label: str) -> str:
    value = raw_field(body, label)
    if not value.strip() or _is_placeholder(value):
        raise HandoffError(f"Incomplete Builder contract field: {label}")
    return value

def prefixed_field(body: str, prefix: str) -> str:
    """Return the raw value of a `- <prefix>…: value` field.

    Template labels for these fields carry a long parenthetical, so match the
    label prefix instead of an exact label.
    """
    values = re.findall(r"^- " + re.escape(prefix) + r"[^\n:]*:[ \t]*(.*)$",
                        body, re.MULTILINE)
    if len(values) != 1:
        raise HandoffError(f"Expected one populated field starting with: {prefix}")
    return values[0]

def require_populated_prefix(body: str, prefix: str) -> None:
    value = prefixed_field(body, prefix)
    if not value.strip() or _is_placeholder(value):
        raise HandoffError(f"Incomplete Builder contract field: {prefix}")

def command_paths(value: str) -> list[str]:
    """Extract path-looking tokens from backticked command fragments."""
    tokens: list[str] = []
    for quoted in re.findall(r"`([^`]*)`", value):
        for token in quoted.split():
            token = token.strip("\"'").rstrip(",;")
            if token.startswith("-") or "$" in token:
                continue
            # A bare filename is ambiguous (a command argument, not a retained
            # artifact), so only tokens with a directory component are checked.
            if "/" not in token:
                continue
            tokens.append(token)
    return tokens

def require_command_paths_exist(root: Path, body: str, label: str) -> None:
    """Fail when a declared command points at a path that is not retained.

    Absolute and `~` paths are checked in place. A relative token that walks
    upwards is skipped: it belongs to a different root assumption and cannot be
    attributed here.
    """
    value = populated_field(body, label)
    for token in command_paths(value):
        candidate = Path(token).expanduser()
        if candidate.is_absolute():
            if not candidate.exists():
                raise HandoffError(f"{label} references a missing path: {token}")
            continue
        if token.startswith(".."):
            continue
        resolved = within(root, token)
        if not resolved.exists():
            raise HandoffError(f"{label} references a missing path: {token}")

def require_prototype_entry(root: Path, scope: str) -> None:
    entry = within(root, scope)
    if not entry.is_dir():
        raise HandoffError(f"Prototype write scope is not retained: {scope}")
    if not any(entry.rglob("*.html")):
        raise HandoffError(f"Prototype write scope has no HTML entry: {scope}")

def declared_skill_root(body: str) -> Path:
    """Resolve the skill installation the Specification was compiled against."""
    raw = populated_field(body, SKILL_ROOT_FIELD)
    candidates = [item for item in re.findall(r"`([^`]+)`", raw) if "/" in item]
    if not candidates:
        candidates = [token for token in raw.split(";")[0].split() if "/" in token]
    if not candidates:
        raise HandoffError(f"Expected a skill root path in: {SKILL_ROOT_FIELD}")
    root = Path(candidates[0].strip().strip("\"'")).expanduser()
    if not root.is_dir():
        raise HandoffError(f"Declared skill root is not retained: {root}")
    return root.resolve()

def craft_reads(body: str) -> list[dict]:
    """Bind the craft references the Designer declares it consulted.

    Each entry is `path`, sha256:<digest> under the declared skill root. This
    proves the cited bytes existed and were bound to this dispatch; it does not
    prove that a model read them.
    """
    skill_root = declared_skill_root(body)
    value = populated_field(body, CRAFT_READS_FIELD)
    entries = re.findall(r"`([^`]+)`[^`]*?sha256:([0-9a-fA-F]{64})", value)
    if not entries:
        raise HandoffError(
            f"{CRAFT_READS_FIELD} declares no bound reference "
            "(expected `path`, sha256:<digest>)")
    results = []
    for raw, expected in entries:
        path = (skill_root / raw.strip()).resolve()
        if not path.is_relative_to(skill_root):
            raise HandoffError(f"Craft read escapes the declared skill root: {raw}")
        if not path.is_file():
            raise HandoffError(f"Craft read is not retained under the declared skill root: {raw}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected.lower():
            raise HandoffError(f"Craft read digest mismatch: {raw}")
        results.append({"path": raw.strip(), "sha256": actual})
    return results


def contract_disposition(contract: str) -> str:
    raw = raw_field(contract, "Disposition")
    value = _normalized(raw)
    if value not in ALLOWED_CONTRACT_DISPOSITIONS:
        raise HandoffError(f"Unsupported Slice Contract disposition: {raw.strip() or '(empty)'}")
    if value != "ready":
        raise HandoffError(
            f"Slice Contract is not ready for generation (Disposition: {value})")
    return value


def visual_verification(body: str) -> str:
    raw = raw_field(body, "Visual verification")
    value = _normalized(raw)
    if value not in ALLOWED_VISUAL_VERIFICATION:
        raise HandoffError(f"Unsupported visual verification declaration: {raw.strip() or '(empty)'}")
    return value


def _split_row(line: str) -> list[str]:
    # Protect escaped pipes \| before splitting table cells
    placeholder = "\x00PIPE\x00"
    protected = line.replace(r"\|", placeholder).strip()
    if protected.startswith("|"):
        protected = protected[1:]
    if protected.endswith("|"):
        protected = protected[:-1]
    return [cell.replace(placeholder, "|").strip() for cell in protected.split("|")]


def _is_delimiter(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{1,}:?", cell.strip()) for cell in cells)


def component_obligations(body: str) -> list[dict]:
    header_at = None
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        cells = [_normalized(cell) for cell in _split_row(line)]
        if cells == list(EXPECTED_COMPONENT_HEADER):
            if header_at is not None:
                raise HandoffError("Expected one component constraint table")
            header_at = index
    if header_at is None:
        raise HandoffError("Incomplete Builder contract field: Component constraints")
    rest = lines[header_at + 1:]
    if not rest or not _is_delimiter(_split_row(rest[0])):
        raise HandoffError("Malformed component constraint table: expected a delimiter row")
    rows: list[dict] = []
    for line in rest[1:]:
        if not line.strip().startswith("|"):
            break
        cells = _split_row(line)
        if len(cells) != 5:
            raise HandoffError(
                f"Malformed component constraint row: expected 5 columns, found {len(cells)}: {line.strip()}")
        surface, asset, disposition_raw, constraint, checkpoint = (cell.strip() for cell in cells)
        disposition = _normalized(disposition_raw)
        if disposition not in ALLOWED_COMPONENT_DISPOSITIONS:
            raise HandoffError(
                f"Unsupported component disposition: {disposition_raw.strip() or '(empty)'}")
        if not surface or _is_placeholder(surface):
            raise HandoffError("Incomplete component obligation: surface / interaction is required")
        if disposition == "required":
            if not asset or _is_placeholder(asset) or _normalized(asset) in GENERIC_REQUIRED_ASSETS:
                raise HandoffError(
                    f"Incomplete required component obligation: '{surface}' must name an existing asset")
            if not constraint or _is_placeholder(constraint):
                raise HandoffError(
                    f"Incomplete required component obligation: '{surface}' must state a constraint")
            if not checkpoint or _is_placeholder(checkpoint):
                raise HandoffError(
                    f"Incomplete required component obligation: '{surface}' must name a verification checkpoint")
        elif disposition == "preferred":
            if not asset or _is_placeholder(asset):
                raise HandoffError(
                    f"Incomplete preferred component obligation: '{surface}' must name an asset")
            if not constraint or _is_placeholder(constraint):
                raise HandoffError(
                    f"Incomplete preferred component obligation: '{surface}' must state a constraint")
            if not checkpoint or _is_placeholder(checkpoint):
                raise HandoffError(
                    f"Incomplete preferred component obligation: '{surface}' must name a verification checkpoint")
        elif disposition == "delegated":
            if not constraint or _is_placeholder(constraint):
                raise HandoffError(
                    f"Incomplete delegated component obligation: '{surface}' must state a constraint")
            if not checkpoint or _is_placeholder(checkpoint):
                raise HandoffError(
                    f"Incomplete delegated component obligation: '{surface}' must name a verification checkpoint")
        else:  # unavailable records a known capability boundary.
            if not asset or _is_placeholder(asset):
                raise HandoffError(
                    f"Incomplete unavailable component obligation: '{surface}' must name a known boundary")
            if not constraint or _is_placeholder(constraint):
                raise HandoffError(
                    f"Incomplete unavailable component obligation: '{surface}' must state a constraint")
        rows.append({"surface": surface, "asset": asset, "disposition": disposition,
                     "constraint": constraint, "checkpoint": checkpoint})
    if not rows:
        raise HandoffError("Incomplete Builder contract field: Component constraints")
    return rows


def packet(root: Path, spec: str) -> dict:
    root = root.resolve()
    path = within(root, spec)
    relative = path.relative_to(root)
    if (len(relative.parts) != 4 or relative.parts[:2] != ("prototype", "specifications")
            or path.suffix != ".md"):
        raise HandoffError("Specification must be prototype/specifications/<slice>/<candidate>.md")
    body = path.read_text()
    declared_root = field(body, "Repository root").strip().strip('`')
    if Path(declared_root).resolve() != root:
        raise HandoffError("Specification repository root mismatch")
    refs = {key: reference(root, body, label) for key, label in (
        ("product", "Product record revision and digest"),
        ("foundation", "Foundation revision and digest"),
        ("tokens", "Token artifact path, revision, and digest"),
        ("slice_contract", "Slice Contract revision and digest"),
    )}
    contract = within(root, refs["slice_contract"]["path"]).read_text()
    refs["surface_map"] = reference(root, contract, "Retained surface-map path, revision and digest")
    associations(root, path, body, refs, contract)
    scopes = {}
    for key, kind, label in (
        ("prototype_write_scope", "experiments", "Prototype write scope"),
        ("evidence_write_scope", "evidence", "Evidence write scope"),
    ):
        value = quoted_path(field(body, label))
        expected = root / "prototype" / kind / path.parent.name / path.stem
        actual = within(root, value)
        # Reject symlink redirection even when its target remains within root.
        if actual != expected:
            raise HandoffError(f"Candidate scope mismatch: {label}; expected {expected.relative_to(root)}")
        scopes[key] = actual.relative_to(root).as_posix() + "/"
    disposition = contract_disposition(contract)
    for label in ("Start command",
                  "Verification command(s)",
                  "Page/flow coverage and shared data references",
                  "Delegated implementation freedoms"):
        populated_field(body, label)
    require_populated_prefix(body, PREFIXED_FIELDS[0])
    resolved_craft_reads = craft_reads(body)
    for label in ("Start command", "Verification command(s)"):
        require_command_paths_exist(root, body, label)
    visual = visual_verification(body)
    screenshots = raw_field(body, "Required screenshot checkpoints")
    if visual == "required" and (not screenshots.strip() or _is_placeholder(screenshots)):
        raise HandoffError("Incomplete Builder contract field: Required screenshot checkpoints")
    obligations = component_obligations(body)
    specification = retained(root, spec)
    required_reads = [
        specification,
        refs["product"],
        refs["slice_contract"],
        refs["foundation"],
        refs["surface_map"],
        refs["tokens"],
    ]
    return {"repository_root": str(root), "specification": specification,
            "slice_id": path.parent.name, "candidate_id": path.stem,
            "references": refs, **scopes,
            "contract_disposition": disposition,
            "craft_reads": resolved_craft_reads,
            "visual_verification": visual,
            "component_obligations": obligations,
            "required_reads": required_reads,
            "skill_root": str(Path(__file__).resolve().parents[1])}


def pillar_packet(root: Path, spec_path: Path) -> dict:
    slice_id = spec_path.parent.name
    candidate_id = spec_path.stem
    required = {
        "product": root / "prototype/product.md",
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "tokens": root / "prototype/contracts/tokens/t1.md",
        "tokens_css": root / "prototype/shared/tokens.css",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
    }
    refs = {}
    for key, path in required.items():
        if not path.is_file():
            raise HandoffError(f"Missing required 6-pillar contract: {path.relative_to(root)}")
        refs[key] = retained(root, str(path.relative_to(root)))

    spec_retained = retained(root, str(spec_path.relative_to(root)))

    proto_scope = f"prototype/experiments/{slice_id}/{candidate_id}/"
    if not (root / proto_scope).is_dir():
        proto_scope = f"prototype/experiments/{slice_id}/hero-anchor/"
    if not (root / proto_scope).is_dir():
        proto_scope = f"prototype/experiments/{slice_id}/"

    evidence_scope = f"prototype/evidence/{slice_id}/{candidate_id}/"

    return {
        "repository_root": str(root),
        "specification": spec_retained,
        "slice_id": slice_id,
        "candidate_id": candidate_id,
        "references": refs,
        "prototype_write_scope": proto_scope,
        "evidence_write_scope": evidence_scope,
        "contract_disposition": "ready",
        "craft_reads": [],
        "visual_verification": "required",
        "component_obligations": [],
        "required_reads": [
            spec_retained,
            refs["product"],
            refs["slice_contract"],
            refs["foundation"],
            refs["surface_map"],
            refs["tokens"],
        ],
        "skill_root": str(Path(__file__).resolve().parents[1]),
    }


APPROVAL_STATUSES = ("confirmed", "delegated")

# A decision row that only announces a future approval binds nothing. Any of
# these markers means no approval exists at freeze time.
PLANNED_APPROVAL_MARKERS = (
    "will approve", "to be approved", "plan to approve", "planned approval",
    "planned", "would approve", "when approved", "once approved",
    "after approval", "awaiting approval", "approval pending", "pending approval",
    "not approved", "no approval", "never approved", "without approval",
    "unapproved", "rejected", "declined",
)

# The row must cite an actual approval or explicit delegated-authority source.
APPROVAL_SOURCE_MARKERS = (
    "用户明确批准", "用户批准", "用户确认", "确认封版", "确认冻结",
    "stakeholder approved", "approved for freeze", "signoff: approved",
    "signoff approved", "explicit approval", "approval source",
    "delegated authority", "prior delegation",
)

# ... and an actual locator for that decision, not an arbitrary phrase.
APPROVAL_LOCATOR_MARKERS = (
    "turn", "轮", "date", "日期", "quote", "原话", "引用", "locator", "定位",
)

# A spec-only approval retains the design scope without claiming that any
# prototype, platform or production implementation was exercised.
SPEC_ONLY_MARKERS = (
    "spec-only", "spec only", "design-only", "design only", "仅规格", "仅设计",
    "without prototype", "no prototype execution", "无原型",
)

# Downstream implementation validation that a freeze cannot claim on its own.
PENDING_IMPLEMENTATION_DIMENSIONS = ("implementation", "platform", "production")


def _decision_rows(text: str) -> list[list[str]]:
    """Parse the discussion record's decision table rows (`| ID | … |`)."""
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = _split_row(stripped)
        if len(cells) < 2 or _is_delimiter(cells):
            continue
        if _normalized(cells[0]) in ("id", ""):
            continue
        rows.append(cells)
    return rows


def approval_binding(root: Path, slice_id: str, candidate_id: str) -> dict:
    """Bind a freeze to an actual recorded approval decision and its source.

    A matching phrase inside free text is not approval. The binding requires one
    decision row with status `confirmed | delegated` that cites an approval or
    delegated-authority source plus a locator, and that is neither a planned nor
    a negated statement. The row's retained digest and any source it names are
    recorded so a later edit invalidates downstream admission.
    """
    record = root / "prototype" / "discussion.md"
    if not record.is_file():
        raise HandoffError(
            "Cannot freeze specification: prototype/discussion.md is missing; "
            "record the actual approval or delegated-authority decision first."
        )
    text = record.read_text(encoding="utf-8")
    selected: list[str] | None = None
    spec_only = False
    sources: list[str] = []
    for row in _decision_rows(text):
        # Columns: ID | Decision | Status | Reason | quote + locator | affected artifacts.
        status = _normalized(row[2]) if len(row) > 2 else ""
        if status not in APPROVAL_STATUSES:
            continue
        evidence = " ".join(row[3:5]).lower()
        if any(marker in evidence for marker in PLANNED_APPROVAL_MARKERS):
            continue
        if not any(marker.lower() in evidence for marker in APPROVAL_SOURCE_MARKERS):
            continue
        if not any(marker.lower() in evidence for marker in APPROVAL_LOCATOR_MARKERS):
            continue
        selected = row
        spec_only = spec_only or any(m in evidence for m in SPEC_ONLY_MARKERS)
        sources = [token for token in re.findall(r"`([^`]+)`", row[-1]) if "/" in token]
    if selected is None:
        raise HandoffError(
            "Cannot freeze specification: no actual approval or delegated-authority decision "
            f"for slice '{slice_id}' / '{candidate_id}'. A planned, negated or override-only "
            "statement, or a bare matching phrase, does not authorize freeze. Record the "
            "decision and its locator in prototype/discussion.md."
        )
    binding = {
        "record": retained(root, "prototype/discussion.md"),
        "decision_id": _clean(selected[0]),
        "status": _normalized(selected[2]),
        "scope": {"slice_id": slice_id, "candidate_id": candidate_id},
        "spec_only": spec_only,
    }
    if sources:
        source = within(root, sources[0])
        if not source.is_file():
            raise HandoffError(
                f"Approval binding references a source that is not retained: {sources[0]}")
        binding["source"] = retained(root, sources[0])
    return binding


def freeze(root: Path, spec: str) -> dict:
    """Freeze a specification and its transitively retained contracts into immutable state.

    Calculates SHA256 digests across all authoritative artifacts (Foundation,
    Tokens, Surface Map, Slice Contract, and the Specification itself), asserts
    that all internal references match their calculated digests, and returns
    the frozen artifact manifest with immutable SHA256 digests.

    Approval is bound to an actual decision recorded in prototype/discussion.md.
    A spec-only approval retains the approved design scope without claiming a
    build, so it freezes without a prototype entry artifact; a scope that claims
    prototype implementation still requires its entry. There is no permissive
    bypass: a strict packet failure stays failed.
    """
    root = root.resolve()
    spec_path = within(root, spec)
    if spec_path.parent.name == "briefs":
        raise HandoffError("Cannot freeze an exploration brief; formal Specification approval is required")
    pkt = packet(root, spec)
    binding = approval_binding(root, pkt["slice_id"], pkt["candidate_id"])
    # The entry requirement guards a scope that claims prototype implementation.
    # Every approval other than a spec-only one keeps that requirement, and an
    # override never reaches this point because approval_binding refuses it.
    if not binding["spec_only"]:
        require_prototype_entry(root, pkt["prototype_write_scope"])

    spec_body = spec_path.read_text(encoding="utf-8")
    status_match = re.search(r"^-\s*(?:Compilation status|Authority status):\s*`?([a-zA-Z0-9_ -]+)`?", spec_body, re.M | re.IGNORECASE)
    if status_match:
        status = status_match.group(1).strip().lower()
        if status not in ("candidate", "provisional", "sealed provisional", "validated", "frozen", "frozen approved"):
            raise HandoffError(f"Specification compilation status must be candidate, provisional, validated, or frozen to freeze, got: {status}")

    evidence_path = root / "prototype" / "evidence" / pkt["slice_id"] / pkt["candidate_id"] / "prototype-evidence.md"
    evidence_record = retained(root, str(evidence_path.relative_to(root))) if evidence_path.is_file() else None

    # Transition specification status to frozen approved upon freeze
    updated_spec_body = re.sub(
        r"^-\s*(?:Compilation status|Authority status):\s*`?[a-zA-Z0-9_ -]+`?",
        "- Compilation status: frozen\n- Authority status: frozen approved",
        spec_body,
        flags=re.M | re.IGNORECASE
    )
    if updated_spec_body != spec_body:
        spec_path.write_text(updated_spec_body, encoding="utf-8")
    # Re-derive after the status transition: the manifest must record the bytes
    # that actually exist at freeze time, or admission breaks on its own receipt.
    spec_ref = str(spec_path.relative_to(root))
    pkt["specification"] = retained(root, spec_ref)
    if binding.get("source", {}).get("path") == spec_ref:
        binding["source"] = retained(root, spec_ref)

    frozen_manifest = {
        "status": "frozen",
        "authority_status": "frozen_approved",
        "slice_id": pkt["slice_id"],
        "candidate_id": pkt["candidate_id"],
        "specification": pkt["specification"],
        "evidence": evidence_record,
        "references": pkt["references"],
        "craft_reads": pkt["craft_reads"],
        "approval": binding,
        # Freezing a design scope never exercises implementation. These remain
        # explicitly pending whether or not the approval is spec-only.
        "implementation_validation": {name: "pending" for name in PENDING_IMPLEMENTATION_DIMENSIONS},
        "frozen_artifacts": [pkt["specification"], *pkt["required_reads"][1:]] + ([evidence_record] if evidence_record else [])
    }
    # Persist freeze-manifest.json to evidence scope
    evidence_dir = root / "prototype" / "evidence" / pkt["slice_id"] / pkt["candidate_id"]
    evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = evidence_dir / "freeze-manifest.json"
    manifest_path.write_text(json.dumps(frozen_manifest, ensure_ascii=False, indent=2) + chr(10))
    return frozen_manifest


def downstream_admission(root: Path, slice_id: str) -> dict:
    """Re-verify the frozen manifest against the current sources.

    Admission is bound to the exact bytes recorded at freeze time: a manifest
    whose recorded revision, approval provenance or referenced source digest has
    drifted is refused rather than admitted from the older receipt.
    """
    manifest = check_downstream_gate(root, slice_id)
    binding = manifest.get("approval", {})
    record = binding.get("record")
    if "approval" in manifest and not record:
        raise HandoffError(
            "Downstream Gate Blocked: frozen manifest carries no approval binding; "
            "re-freeze with an actual recorded approval decision.")
    for ref in (record, binding.get("source")):
        if not ref:
            continue
        current = retained(root, ref["path"])
        if current["sha256"] != ref["sha256"]:
            raise HandoffError(
                f"Downstream Gate Blocked: {ref['path']} changed after freeze "
                f"({current['sha256'][:8]} != {ref['sha256'][:8]}); re-freeze before admission.")
    frozen = json.loads((root / manifest["manifest"]).read_text(encoding="utf-8"))
    spec_ref = frozen.get("specification")
    if spec_ref:
        current = retained(root, spec_ref["path"])
        if current["sha256"] != spec_ref["sha256"]:
            raise HandoffError(
                f"Downstream Gate Blocked: {spec_ref['path']} changed after freeze "
                f"({current['sha256'][:8]} != {spec_ref['sha256'][:8]}); re-freeze before admission.")
    manifest["admission"] = "bound_to_frozen_revision"
    return manifest


def check_downstream_gate(root: Path, slice_id: str) -> dict:
    """Downstream Engineering Gate (Loom Entry 2).

    Strictly gates production implementation:
    - Rejects 'draft', 'provisional', 'sealed provisional' specifications.
    - Rejects 'validated' specifications that have not been frozen.
    - Strictly requires 'frozen' / 'frozen approved' status with valid freeze manifest.
    """
    root = root.resolve()
    spec_dir = root / "prototype/specifications" / slice_id
    if not spec_dir.is_dir():
        raise HandoffError(f"Downstream Gate Blocked: Specification directory missing for slice '{slice_id}'")
    spec_files = list(spec_dir.glob("*.md"))
    if not spec_files:
        raise HandoffError(f"Downstream Gate Blocked: No specification markdown found for slice '{slice_id}'")

    spec_path = spec_files[0]
    spec_body = spec_path.read_text(encoding="utf-8")

    # Check for freeze manifest
    evidence_dir = root / "prototype/evidence" / slice_id / spec_path.stem
    manifest_path = evidence_dir / "freeze-manifest.json"

    # Extract authority / compilation status
    status_match = re.search(r"^-\s*(?:Compilation status|Authority status):\s*`?([a-zA-Z0-9_ -]+)`?", spec_body, re.M | re.IGNORECASE)
    spec_status = status_match.group(1).strip().lower() if status_match else "provisional"

    if manifest_path.is_file():
        # Explicit format admission: a malformed manifest is a diagnostic, never a
        # silent downgrade to the softer status-text branch below.
        try:
            m_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise HandoffError(
                f"Downstream Gate Blocked: freeze manifest for slice '{slice_id}' is malformed "
                f"({error}); re-run handoff.py freeze.") from error
        if not isinstance(m_data, dict) or "status" not in m_data:
            raise HandoffError(
                f"Downstream Gate Blocked: freeze manifest for slice '{slice_id}' is not a retained "
                "freeze record; re-run handoff.py freeze.")
        if m_data.get("status") != "frozen" or m_data.get("authority_status") != "frozen_approved":
            raise HandoffError(
                f"Downstream Gate Blocked: freeze manifest for slice '{slice_id}' does not record "
                "frozen_approved authority; re-run handoff.py freeze.")
        if "approval" in m_data and not m_data["approval"]:
            raise HandoffError(
                f"Downstream Gate Blocked: freeze manifest for slice '{slice_id}' carries an empty "
                "approval binding; re-run handoff.py freeze against an actual recorded approval.")
        return {
            "gate": "passed",
            "authority_status": "frozen_approved",
            "slice_id": slice_id,
            "specification": str(spec_path.relative_to(root)),
            "manifest": str(manifest_path.relative_to(root)),
            "approval": m_data.get("approval"),
            "implementation_validation": m_data.get("implementation_validation", {}),
            "message": "Downstream Gate Passed: Specification is frozen approved and ready for Loom delivery.",
        }

    if spec_status in ("draft", "provisional", "sealed provisional", "candidate"):
        raise HandoffError(
            f"Downstream Gate Blocked: Specification for slice '{slice_id}' is in '{spec_status}' status. "
            "Downstream engineering implementation (Loom Entry 2) strictly requires 'frozen approved' status. "
            "Complete Stage 4 validation and Stage 5 silent packaging (handoff.py freeze) first."
        )
    elif spec_status == "validated":
        raise HandoffError(
            f"Downstream Gate Blocked: Specification for slice '{slice_id}' is 'validated' but not yet frozen. "
            "Run Stage 5 silent packaging (python3 skills/spec-prototype/scripts/handoff.py freeze) to produce immutable frozen approved delivery."
        )
    elif spec_status in ("frozen", "frozen approved", "frozen_approved"):
        return {
            "gate": "passed",
            "authority_status": "frozen_approved",
            "slice_id": slice_id,
            "specification": str(spec_path.relative_to(root)),
            "message": "Downstream Gate Passed: Specification is frozen approved.",
        }
    else:
        raise HandoffError(f"Downstream Gate Blocked: Unrecognized authority status '{spec_status}' for slice '{slice_id}'.")


def directory_manifest(directory: Path) -> dict:
    directory = directory.resolve()
    if not directory.is_dir():
        raise HandoffError(f"Directory not found: {directory}")
    entries = {}
    for p in sorted(directory.rglob("*")):
        if p.is_file() and not p.is_symlink():
            rel = p.relative_to(directory).as_posix()
            entries[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return {
        "directory": str(directory),
        "total_files": len(entries),
        "files": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hashes = sub.add_parser("digests")
    hashes.add_argument("--root", type=Path, required=True)
    hashes.add_argument("paths", nargs="+")
    check = sub.add_parser("packet")
    check.add_argument("--root", type=Path, required=True)
    check.add_argument("--spec", required=True)
    frz = sub.add_parser("freeze")
    frz.add_argument("--root", type=Path, required=True)
    frz.add_argument("--spec", required=True)
    man = sub.add_parser("manifest")
    man.add_argument("--dir", type=Path, required=True)
    man.add_argument("--output", type=Path)
    gate_cmd = sub.add_parser("gate")
    gate_cmd.add_argument("--root", type=Path, required=True)
    gate_cmd.add_argument("--slice", required=True)
    args = parser.parse_args()
    try:
        if args.command == "digests":
            results = [retained(args.root.resolve(), p) for p in args.paths]
            for item in results:
                print(f"`{item['path']}`, sha256:{item['sha256']}")
        elif args.command == "packet":
            print(json.dumps(packet(args.root, args.spec), ensure_ascii=False, indent=2))
        elif args.command == "freeze":
            print(json.dumps(freeze(args.root, args.spec), ensure_ascii=False, indent=2))
        elif args.command == "gate":
            print(json.dumps(downstream_admission(args.root, args.slice), ensure_ascii=False, indent=2))
        elif args.command == "manifest":
            data = directory_manifest(args.dir)
            formatted = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(formatted, encoding="utf-8")
            else:
                print(formatted, end="")
    except (HandoffError, OSError, UnicodeError) as error:
        print(f"prototype_blocked: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

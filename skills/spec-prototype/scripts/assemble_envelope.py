#!/usr/bin/env python3
"""Synthesize a self-contained execution envelope for spec-prototype-builder.

Validates that Stage 1 Design Spec contracts exist and extracts all layout,
token, state machine, and assertion parameters into a single envelope JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional


SKILL = Path(__file__).resolve().parents[1]


def check_spec_completeness(root: Path, slice_id: str) -> Dict[str, Path]:
    """Verify that all required Stage 1 design contract artifacts exist."""
    required = {
        "product": root / "prototype/product.md",
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "tokens_css": root / "prototype/shared/tokens.css",
        "tokens_md": root / "prototype/contracts/tokens/t1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
    }
    missing = [name for name, p in required.items() if not p.is_file()]
    if missing:
        raise ValueError(
            f"Stage 1 Spec Contract incomplete. Missing required artifacts: {', '.join(missing)}. "
            f"All 6 contract pillars must be materialized before Stage 2 prototype building."
        )
    return required


def extract_field(content: str, label: str, default: str = "") -> str:
    pattern = rf"^- {re.escape(label)}:[ \t]*(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else default


def _brief_path(root: Path, slice_id: str) -> Optional[Path]:
    """Find the retained direction brief without treating it as a formal spec."""
    candidates = (
        root / f"prototype/briefs/{slice_id}-probe.md",
        root / f"prototype/briefs/{slice_id}.md",
    )
    return next((path for path in candidates if path.is_file()), None)


def _brief_scope(value: str, fallback: str) -> str:
    scope = value.strip("`'\" ") or fallback
    return scope.rstrip("/") + "/"


def assemble_direction(root: Path, slice_id: str, brief: Path) -> Dict[str, Any]:
    """Assemble a direction-probe envelope from one exploration brief."""
    content = brief.read_text(encoding="utf-8")
    probe_id = extract_field(content, "Probe ID", slice_id)
    target = _brief_scope(extract_field(content, "Probe target path"),
                          f"prototype/experiments/probes/{probe_id}/")
    evidence = _brief_scope(extract_field(content, "Evidence write scope"),
                            f"prototype/evidence/probes/{probe_id}/")
    return {
        "envelope_version": "1.0",
        "repository_root": str(root.resolve()),
        "skill_root": str(SKILL.resolve()),
        "slice_id": slice_id,
        "probe_id": probe_id,
        "mode": "direction-probe",
        "target_html_path": target if target.endswith(".html") else target + "index.html",
        "prototype_write_scope": target.rsplit("/", 1)[0] + "/" if target.endswith(".html") else target,
        "evidence_write_scope": evidence,
        "brief": {"path": brief.relative_to(root).as_posix(),
                  "sha256": hashlib.sha256(brief.read_bytes()).hexdigest()},
        "constraints": {"thesis": extract_field(content, "Core design thesis")},
    }


def assemble(root: Path, slice_id: str) -> Dict[str, Any]:
    """Assemble an envelope for either exploration or formal candidate work."""
    brief = _brief_path(root, slice_id)
    specification = root / f"prototype/specifications/{slice_id}/r1.md"
    if brief is not None and not specification.is_file():
        return assemble_direction(root, slice_id, brief)
    paths = check_spec_completeness(root, slice_id)

    product_content = paths["product"].read_text(encoding="utf-8")
    smap_content = paths["surface_map"].read_text(encoding="utf-8")
    contract_content = paths["slice_contract"].read_text(encoding="utf-8")
    spec_content = paths["specification"].read_text(encoding="utf-8")

    # Target scopes
    write_scope = extract_field(spec_content, "Prototype write scope", f"prototype/experiments/{slice_id}/hero-anchor/")
    write_scope_clean = write_scope.strip("`'\" ")
    if not write_scope_clean.endswith("/"):
        write_scope_clean += "/"

    target_html = write_scope_clean + "index.html"
    evidence_scope = extract_field(spec_content, "Evidence write scope", f"prototype/evidence/probes/{slice_id}/").strip("`'\" ")

    # Extract verifiable assertions & Break Protocol
    assertions: List[str] = []
    break_checkpoints: List[str] = []
    shortcuts: List[str] = []
    verb_lifecycle: List[Dict[str, str]] = []

    # Parse assertions
    in_section: Optional[str] = None
    for line in spec_content.splitlines():
        if "Verifiable Design Assertions" in line or "Required screenshot checkpoints" in line:
            in_section = "assertions"
            continue
        elif "The Break Protocol Stress Checkpoints" in line:
            in_section = "break"
            continue
        elif "Dual-Channel Ergonomics" in line:
            in_section = "shortcuts"
            continue
        elif line.startswith("#"):
            in_section = None
            continue

        if line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if not parts:
                continue
            if in_section == "assertions" and parts[0] not in ("Surface / interaction", "Assertion"):
                assertions.append(parts[0])
            elif in_section == "break" and parts[0] not in ("Reality Breaker",):
                break_checkpoints.append(f"{parts[0]}: {parts[1] if len(parts) > 1 else ''}")
            elif in_section == "shortcuts" and parts[0] not in ("Shortcut Key",):
                shortcuts.append(parts[0])

    # Parse Action Verb Lifecycle from slice contract
    in_verbs = False
    for line in contract_content.splitlines():
        if "Action Verb Lifecycle Table" in line:
            in_verbs = True
            continue
        elif line.startswith("#"):
            in_verbs = False
            continue
        if in_verbs and line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 4 and parts[0] not in ("Action ID",):
                verb_lifecycle.append({
                    "action_id": parts[0],
                    "trigger_btn": parts[1],
                    "modal_header": parts[2],
                    "commit_btn": parts[3],
                    "toast": parts[4] if len(parts) > 4 else "",
                })

    constraints = {
        "dual_channel_shortcuts": shortcuts,
        "action_verb_lifecycle": verb_lifecycle,
        "break_protocol_checkpoints": break_checkpoints,
    }
    explicit_turns = extract_field(spec_content, "Maximum operational repair attempts")
    if explicit_turns:
        constraints["maximum_operational_repair_attempts"] = explicit_turns

    envelope = {
        "envelope_version": "1.0",
        "repository_root": str(root.resolve()),
        "skill_root": str(SKILL.resolve()),
        "slice_id": slice_id,
        "mode": "lean-builder-envelope",
        "target_html_path": target_html,
        "evidence_output_dir": evidence_scope,
        "token_stylesheet_ref": "../../../shared/tokens.css",
        "specification": {
            "path": paths["specification"].relative_to(root).as_posix(),
            "sha256": hashlib.sha256(paths["specification"].read_bytes()).hexdigest(),
        },
        "spec_sources": {
            "product_digest": hashlib.sha256(paths["product"].read_bytes()).hexdigest(),
            "surface_map_digest": hashlib.sha256(paths["surface_map"].read_bytes()).hexdigest(),
            "foundation_digest": hashlib.sha256(paths["foundation"].read_bytes()).hexdigest(),
            "tokens_css_digest": hashlib.sha256(paths["tokens_css"].read_bytes()).hexdigest(),
            "tokens_md_digest": hashlib.sha256(paths["tokens_md"].read_bytes()).hexdigest(),
            "contract_digest": hashlib.sha256(paths["slice_contract"].read_bytes()).hexdigest(),
            "specification_digest": hashlib.sha256(paths["specification"].read_bytes()).hexdigest(),
        },
        # Only assertions present in the retained specification are constraints.
        "design_constraints": constraints,
        "verifiable_assertions": assertions,
    }

    return envelope


def main():
    parser = argparse.ArgumentParser(description="Assemble self-contained builder envelope")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--slice", type=str, required=True, help="Slice ID (e.g. console, cockpit)")
    parser.add_argument("--check-spec", action="store_true", help="Only verify Spec completeness")
    parser.add_argument("--output", type=Path, help="Write envelope JSON to file")

    args = parser.parse_args()
    root = args.root.resolve()

    if args.check_spec:
        try:
            check_spec_completeness(root, args.slice)
            print(json.dumps({"status": "spec_complete", "slice_id": args.slice}))
            sys.exit(0)
        except Exception as e:
            print(json.dumps({"status": "spec_incomplete", "error": str(e)}), file=sys.stderr)
            sys.exit(1)

    try:
        env = assemble(root, args.slice)
        out_json = json.dumps(env, indent=2, ensure_ascii=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out_json, encoding="utf-8")
        print(out_json)
    except Exception as e:
        print(f"Error assembling envelope: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

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


def check_spec_completeness(root: Path, slice_id: str) -> Dict[str, Path]:
    """Verify that all 5 required Stage 1 design contract artifacts exist."""
    required = {
        "product": root / "prototype/product.md",
        "tokens_css": root / "prototype/shared/tokens.css",
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
    }
    missing = [name for name, p in required.items() if not p.is_file()]
    if missing:
        raise ValueError(
            f"Stage 1 Spec Contract incomplete. Missing required artifacts: {', '.join(missing)}. "
            f"All 5 contract files must be materialized before Stage 2 prototype building."
        )
    return required


def extract_field(content: str, label: str, default: str = "") -> str:
    pattern = rf"^- {re.escape(label)}:[ \t]*(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else default


def assemble(root: Path, slice_id: str) -> Dict[str, Any]:
    """Assemble self-contained envelope for lean builder execution."""
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

    # Extract verifiable assertions
    assertions: List[str] = []
    in_assertions = False
    for line in spec_content.splitlines():
        if "Verifiable Design Assertions" in line or "Required screenshot checkpoints" in line:
            in_assertions = True
            continue
        if in_assertions:
            if line.startswith("#"):
                in_assertions = False
                continue
            if line.strip().startswith("|") and not line.strip().startswith("|---"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if parts and parts[0] not in ("Surface / interaction", "Assertion"):
                    assertions.append(parts[0])

    envelope = {
        "envelope_version": "1.0",
        "slice_id": slice_id,
        "mode": "lean-builder-envelope",
        "target_html_path": target_html,
        "evidence_output_dir": evidence_scope,
        "token_stylesheet_ref": "../../../shared/tokens.css",
        "spec_sources": {
            "product_digest": hashlib.sha256(paths["product"].read_bytes()).hexdigest()[:16],
            "tokens_css_digest": hashlib.sha256(paths["tokens_css"].read_bytes()).hexdigest()[:16],
            "surface_map_digest": hashlib.sha256(paths["surface_map"].read_bytes()).hexdigest()[:16],
            "contract_digest": hashlib.sha256(paths["slice_contract"].read_bytes()).hexdigest()[:16],
            "specification_digest": hashlib.sha256(paths["specification"].read_bytes()).hexdigest()[:16],
        },
        "design_constraints": {
            "max_tool_turns": 8,
            "target_tool_turns": 5,
            "zero_naked_metrics": True,
            "concentric_radii": True,
            "tabular_numerics": True,
            "dual_channel_shortcuts": ["Space", "P", "Esc"],
        },
        "verifiable_assertions": assertions[:8],
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

#!/usr/bin/env python3
"""Compile discussion and product records into generic design contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def extract_section(text: str, heading: str) -> str:
    pattern = rf"^##+\s+{re.escape(heading)}.*?\n(.*?)(?=\n##+|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else ""


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _bullets(text: str) -> list[str]:
    return [re.sub(r"^[-*+]\s+", "", line).strip() for line in text.splitlines() if re.match(r"^[-*+]\s+", line)]


def materialize(root: Path, slice_id: str, force: bool = False) -> dict[str, str]:
    disc_path = root / "prototype/discussion.md"
    prod_path = root / "prototype/product.md"
    if not disc_path.is_file():
        raise FileNotFoundError(f"Missing mandatory entry index: {disc_path}")
    if not prod_path.is_file():
        raise FileNotFoundError(f"Missing product intent file: {prod_path}")
    disc_text, prod_text = disc_path.read_text(encoding="utf-8"), prod_path.read_text(encoding="utf-8")
    product_title = next((line.lstrip("# ").strip() for line in prod_text.splitlines() if line.startswith("#")), "Product")
    tension = extract_section(prod_text, "Core Tension") or extract_section(disc_text, "Core Tension") or "Not yet decided"
    surfaces = _bullets(extract_section(disc_text, "Surface") or extract_section(prod_text, "Surface"))
    targets = {
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
    }
    created: dict[str, str] = {}
    for key, path in targets.items():
        if path.is_file() and not force:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if key == "surface_map":
            content = f"# Product Surface Map: m1\n\n- Product: {product_title}\n- Source discussion: `prototype/discussion.md`, {_digest(disc_path)}\n- Status: candidate\n\n## Declared surfaces\n" + "\n".join(f"- {s}" for s in surfaces or ["No surface decision recorded"]) + "\n"
        elif key == "foundation":
            content = f"# Project Experience Foundation: f1\n\n- Product: {product_title}\n- Product source: `prototype/product.md`, {_digest(prod_path)}\n- Core tension: {tension}\n- Status: candidate\n\n## Decisions\n{prod_text.strip()}\n"
        elif key == "slice_contract":
            content = f"# Prototype Slice Contract: {slice_id}\n\n- Slice ID: {slice_id}\n- Foundation revision: f1\n- Product source: `prototype/product.md`, {_digest(prod_path)}\n- Status: candidate\n\n## Intent\n{tension}\n\n## Declared interaction decisions\n" + "\n".join(f"- {s}" for s in _bullets(disc_text)[:20] or ["No interaction decision recorded"]) + "\n"
        else:
            content = f"# Prototype Specification: {slice_id} / r1\n\n- Candidate revision: r1\n- Compilation status: candidate\n- Product source: `prototype/product.md`, {_digest(prod_path)}\n- Discussion source: `prototype/discussion.md`, {_digest(disc_path)}\n- Prototype write scope: `prototype/experiments/{slice_id}/`\n- Evidence write scope: `prototype/evidence/probes/{slice_id}/`\n- Visual verification: unverified\n- Browser verification: unverified\n\n## Verifiable Design Assertions\n| Assertion | Expected | Observed |\n|---|---|---|\n| Declared product intent is represented | present | unverified |\n"
        path.write_text(content, encoding="utf-8")
        created[key] = str(path)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize generic Stage 1 contracts")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--slice", default="console")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps({"status": "ok", "slice_id": args.slice, "materialized": materialize(args.root.resolve(), args.slice, args.force)}, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

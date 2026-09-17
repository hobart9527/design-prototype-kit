#!/usr/bin/env python3
"""Compile discussion and product records into generic, high-fidelity design contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, List


def extract_section_by_patterns(text: str, patterns: list[str]) -> str:
    """Extract markdown section under headings matching any of the regex patterns."""
    for pat in patterns:
        m = re.search(rf"^##+[^\n]*?(?:{pat})[^\n]*\n(.*?)(?=\n##+|\Z)", text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ""


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _bullets(text: str) -> list[str]:
    return [re.sub(r"^[-*+]\s+", "", line).strip() for line in text.splitlines() if re.match(r"^[-*+]\s+", line)]


def extract_surfaces(disc_text: str, prod_text: str) -> list[str]:
    """Extract declared surfaces supporting both English and Chinese heading conventions."""
    surfaces_sec = extract_section_by_patterns(disc_text, ["Surface", "表面", "拓扑", "Topology"]) or \
                   extract_section_by_patterns(prod_text, ["Surface", "表面", "拓扑", "Topology"])
    surfaces = _bullets(surfaces_sec) if surfaces_sec else []
    if not surfaces:
        # Fallback: sweep entire disc_text for surface bullet declarations
        for line in disc_text.splitlines():
            if re.match(r"^[-*+]\s+.*?(?:主工作区|上下文|支撑|Primary|Contextual|Supporting|hero-anchor|surfaces/)", line):
                surfaces.append(re.sub(r"^[-*+]\s+", "", line).strip())
    return surfaces


def extract_action_verbs(disc_text: str, slice_id: str) -> list[dict[str, str]]:
    """Extract 4-phase action verb lifecycle table from discussion or derive grounded defaults."""
    verbs_sec = extract_section_by_patterns(disc_text, ["Action Verb", "动作动词", "Verb Lifecycle", "动作流转"])
    extracted: list[dict[str, str]] = []
    if verbs_sec:
        for line in verbs_sec.splitlines():
            if line.strip().startswith("|") and not line.strip().startswith("|---"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if parts and len(parts) >= 4 and parts[0].lower() not in ("action id", "action_id"):
                    extracted.append({
                        "action_id": parts[0],
                        "trigger_btn": parts[1],
                        "modal_header": parts[2],
                        "commit_btn": parts[3],
                        "toast": parts[4] if len(parts) > 4 else f"{parts[1]} Completed",
                        "impact": parts[5] if len(parts) > 5 else "Executes action",
                    })
    if not extracted:
        # Check if domain-specific verbs exist in discussion
        has_drain = bool(re.search(r"排空|drain", disc_text, re.IGNORECASE))
        has_preempt = bool(re.search(r"抢占|preempt", disc_text, re.IGNORECASE))
        if has_drain or has_preempt:
            if has_drain:
                extracted.append({
                    "action_id": "drain-node",
                    "trigger_btn": "Drain Node",
                    "modal_header": "Drain GPU Node",
                    "commit_btn": "Confirm Drain",
                    "toast": "Node Drained Successfully",
                    "impact": "Evicts active batch job and halts tensor stream",
                })
            if has_preempt:
                extracted.append({
                    "action_id": "preempt-vram",
                    "trigger_btn": "Preempt VRAM",
                    "modal_header": "Preempt VRAM Allocation",
                    "commit_btn": "Execute Preempt",
                    "toast": "VRAM Eviction Committed",
                    "impact": "Releases VRAM pool back to shared cluster",
                })
        else:
            action_id = f"execute-{slice_id}"
            extracted.append({
                "action_id": action_id,
                "trigger_btn": f"Commit {slice_id.capitalize()}",
                "modal_header": f"Confirm {slice_id.capitalize()} Action",
                "commit_btn": "Confirm",
                "toast": f"{slice_id.capitalize()} Action Completed",
                "impact": f"Executes decisive operational change for {slice_id}",
            })
    return extracted


def materialize(root: Path, slice_id: str, force: bool = False) -> dict[str, str]:
    disc_path = root / "prototype/discussion.md"
    prod_path = root / "prototype/product.md"
    if not disc_path.is_file():
        raise FileNotFoundError(f"Missing mandatory entry index: {disc_path}")
    if not prod_path.is_file():
        raise FileNotFoundError(f"Missing product intent file: {prod_path}")
    disc_text, prod_text = disc_path.read_text(encoding="utf-8"), prod_path.read_text(encoding="utf-8")
    product_title = next((line.lstrip("# ").strip() for line in prod_text.splitlines() if line.startswith("#")), "Product")
    tension = extract_section_by_patterns(prod_text, ["Core Tension", "Tension", "张力", "冲突"]) or \
              extract_section_by_patterns(disc_text, ["Core Tension", "Tension", "张力", "冲突"]) or \
              "Not yet decided"
    surfaces = extract_surfaces(disc_text, prod_text)
    action_verbs = extract_action_verbs(disc_text, slice_id)

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
            surface_lines = "\n".join(f"- {s}" for s in surfaces) if surfaces else "- No surface decision recorded"
            content = f"""# Product Surface Map: m1

- Product: {product_title}
- Source discussion: `prototype/discussion.md`, {_digest(disc_path)}
- Status: candidate

## Declared surfaces
{surface_lines}
"""
        elif key == "foundation":
            content = f"""# Project Experience Foundation: f1

- Product: {product_title}
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Core tension: {tension}
- Status: candidate

## Decisions
{prod_text.strip()}
"""
        elif key == "slice_contract":
            verb_table = "\n".join(
                f"| `{v['action_id']}` | `{v['trigger_btn']}` | `{v['modal_header']}` | `{v['commit_btn']}` | `{v['toast']}` | {v['impact']} |"
                for v in action_verbs
            )
            content = f"""# Prototype Slice Contract: {slice_id}

- Slice ID: {slice_id}
- Foundation revision: f1
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Status: candidate

## Intent
{tension}

## Action Verb Lifecycle Table (4-Phase Atomic Terminology)

| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
{verb_table}

## Decisive Exchange 3-Frame Specification (核心决定性交换三帧推演)

- **Frame 1 (Intent Input)**: Operator activates target trigger via mouse click or `Space` key; inspection drawer slides in with contextual parameters.
- **Frame 2 (Decisive Commit)**: Operator hits commit action; trigger undergoes tactile `:active scale(0.97)` mechanical response; inline state locks to prevent duplicate submissions.
- **Frame 3 (State Settlement & Focus Restoration)**: Target badge transitions state deterministically; feedback toast displays completion; focus deterministically restores to originating anchor.

## Context Preservation Rules (上下文绝对保持法则)

- **Draft Context**: Dismissing inspector or drawer without submitting preserves filter parameters and active tab.
- **Spatial & Filter Context**: Scroll offsets and active facet filters remain strictly pinned upon drawer close or return.
"""
        else:
            content = f"""# Prototype Specification: {slice_id} / r1

- Candidate revision: r1
- Compilation status: candidate
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Discussion source: `prototype/discussion.md`, {_digest(disc_path)}
- Prototype write scope: `prototype/experiments/{slice_id}/hero-anchor/`
- Evidence write scope: `prototype/evidence/probes/{slice_id}/`
- Visual verification: unverified
- Browser verification: unverified

## Dual-Channel Ergonomics (Keyboard Shortcuts & Focus Recovery)

| Shortcut Key | Target Action / Interaction | Scope | Focus Restoration Anchor |
|---|---|---|---|
| `Space` or `P` | Inspect active node / toggle inspector drawer | Active node tile or selection | Active selection anchor |
| `Esc` | Dismiss inspector drawer / modal | Global overlay | Restore focus to originating trigger |
| `J` / `K` | Navigate cluster node rows or items | Active list or matrix | Active selection index |

## The Break Protocol Stress Checkpoints (四维破坏性极限压测)

| Reality Breaker | Concrete Test Vector / Input | Expected Graceful Behavior | Observed Result |
|---|---|---|---|
| **Unbreakable String** | `node-cluster-uuid-00000000-0000-0000-0000-000000000000` | CSS ellipsis + title tooltip, zero container blowout | `pending` |
| **Zero-Item Empty State** | Filter: 0 results / empty list | Actionable empty card with reset filter button | `pending` |
| **Extreme 320px Fold** | 320px viewport width test | Horizontal scroll or vertical reflow, primary action reachable | `pending` |
| **Rapid Interruption** | Double-click / rapid Space hits | Debounced submission, single idempotency state transition | `pending` |

## Verifiable Design Assertions

| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| Zero Naked Metrics: every metric has reference baseline or micro sparkline | present | unverified |
| Tabular Numerics: font-variant-numeric: tabular-nums on all metrics | present | unverified |
| Concentric Radii Formula: outer radius >= inner radius + padding | present | unverified |
| Atmospheric undertone: zero sterile neutral gray #808080 | present | unverified |
| Dual-channel keyboard shortcuts (Space / Esc) operable | present | unverified |
| Action Verb Lifecycle closure: trigger -> drawer/modal -> commit -> toast | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |
"""
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

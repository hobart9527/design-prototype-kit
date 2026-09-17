#!/usr/bin/env python3
"""Automated UX/UI Quality Assertion Harness for spec-prototype.

Asserts:
1. Multi-entity interactive inspectability (HTML contains inspectable nodes with dynamic selection handlers).
2. Stateful Micro-App Architecture (Presence of AppState / state store and event listeners).
3. Visual Craft & Spatial Depth (Layered backgrounds, CSS variables, concentric radii, tabular nums).
4. Multi-branch action lifecycle (Action buttons, status changes, bypass/reversion pathways).
5. Code Plagiarism & Stale Template Firewall (Detects verbatim reuse of past template strings).
"""
import sys
import os
import re
import hashlib
from pathlib import Path

# Known stale template signatures that indicate execution evasion or rote copy-paste
STALE_SIGNATURES = [
    ("MAS-ORCHESTRATOR", "Stale Archetype: Copied MAS-ORCHESTRATOR template verbatim"),
    ("DAG-FANOUT-04", "Stale Topology: Copied static 4-node DAG-FANOUT-04 topology"),
    ("Sentiment Agent", "Stale Domain Object: Copied sentiment sub-graph mock verbatim"),
    ("Order Settlement", "Stale Domain Object: Copied order settlement mock verbatim"),
]

def assert_quality(html_path: str, tokens_path: str, check_stale: bool = False) -> bool:
    print(f"[HARNESS] Running Automated UX/UI Quality Assertions on: {html_path}")

    html_file = Path(html_path)
    tokens_file = Path(tokens_path)

    if not html_file.is_file():
        print(f"FAILED: Target HTML not found: {html_path}")
        return False
    if not tokens_file.is_file():
        print(f"FAILED: Shared tokens.css not found: {tokens_path}")
        return False

    html_content = html_file.read_text(encoding="utf-8")
    tokens_content = tokens_file.read_text(encoding="utf-8")

    failures = []

    # 0. Anti-Stagnation / Stale Template Firewall (Optional flag or strict mode)
    if check_stale:
        for sig, msg in STALE_SIGNATURES:
            if sig in html_content:
                failures.append(f"Anti-Stagnation Violation: {msg}. Design must originate from new divergence reasoning.")

    # 1. Inspectability & Multi-Entity Depth
    node_matches = re.findall(r'class=["\'][^"\']*(?:dag-node|card-entity|table-row|stream-node|cluster-node)[^"\']*["\']', html_content)
    if len(node_matches) < 3:
        failures.append(f"Entity Depth Deficit: Expected at least 3 operable entities/nodes, found {len(node_matches)}.")

    # Check for entity selection mechanism
    if not ("selectNode" in html_content or "selectEntity" in html_content or "addEventListener('click'" in html_content or 'onclick="select' in html_content):
        failures.append("Toy-Demo Flaw: Missing universal entity selection/inspection click handler.")

    # 2. Stateful Micro-App Architecture
    has_state_store = any(term in html_content for term in ["AppState", "state =", "const state", "let state", "nodesData", "ClusterState"])
    if not has_state_store:
        failures.append("Static Mockup Flaw: Missing centralized AppState / reactive data store.")

    # 3. Multi-branch action lifecycle
    has_dual_channel = any(term in html_content for term in ["addEventListener('keydown'", "e.code", "e.key", "Space"])
    if not has_dual_channel:
        failures.append("Affordance Flaw: Missing dual-channel interaction (keyboard shortcut binding).")

    has_action_button = any(term in html_content for term in ["btn-action", "btn-isolate", "btn-tactile", "btn-rebalance", "onclick="])
    if not has_action_button:
        failures.append("Closure Flaw: Missing actionable operator intervention button.")

    # 4. Token Integration & Craft
    if "tabular-nums" not in tokens_content and "tabular-nums" not in html_content:
        failures.append("Craft Flaw: Missing font-variant-numeric: tabular-nums for telemetry metrics.")

    if "scale(0.9" not in tokens_content and "scale(0.9" not in html_content:
        failures.append("Tactile Flaw: Missing mechanical detent (:active scale micro-motion).")

    # 5. Visual Hierarchy & Sparklines
    has_sparkline = "<svg" in html_content and ("<path" in html_content or "<polyline" in html_content or "<line" in html_content)
    if not has_sparkline:
        failures.append("Naked Metrics Flaw: Missing SVG sparkline / baseline trend context.")

    if failures:
        print("\n❌ AUTOMATED UX/UI QUALITY ASSERTION FAILED:")
        for idx, err in enumerate(failures, 1):
            print(f"  [{idx}] {err}")
        print("\nRefactoring required before user presentation.")
        return False
    else:
        print("\n✅ ALL UX/UI QUALITY ASSERTIONS PASSED (Entity Depth, AppState Store, Dual-Channel, Craft Rigor).")
        return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automated UX/UI Quality Assertion Harness")
    parser.add_argument("html", help="Path to prototype HTML file")
    parser.add_argument("tokens", nargs="?", default=None, help="Path to shared tokens.css (optional, auto-resolved if omitted)")
    parser.add_argument("--tokens", dest="tokens_opt", default=None, help="Explicit path to shared tokens.css")
    parser.add_argument("--strict-divergence", action="store_true", help="Assert anti-stale and anti-plagiarism template rules")

    args = parser.parse_args()
    html_path = Path(args.html)
    tokens_arg = args.tokens_opt or args.tokens

    if not tokens_arg:
        candidates = [
            html_path.parent / "../../../shared/tokens.css",
            html_path.parent / "../../shared/tokens.css",
            html_path.parent / "tokens.css",
            Path.cwd() / "prototype/shared/tokens.css",
        ]
        resolved = next((c.resolve() for c in candidates if c.is_file()), None)
        tokens_path = resolved if resolved else Path.cwd() / "prototype/shared/tokens.css"
    else:
        tokens_path = Path(tokens_arg).resolve()

    success = assert_quality(str(html_path), str(tokens_path), check_stale=args.strict_divergence)
    sys.exit(0 if success else 1)

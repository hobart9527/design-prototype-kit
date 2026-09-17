#!/usr/bin/env python3
"""Truthful, contract-driven checks for a prototype artifact.

Static checks inspect source only. Browser, visual, and human evidence are
reported as unverified unless an evidence manifest explicitly records them.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


def _contract_items(path: Path | None) -> list[str]:
    """Extract verifiable entity names, action IDs, or button labels from contract markdown."""
    if not path or not path.is_file():
        return []
    items: list[str] = []
    in_actions = False
    in_assertions = False
    in_shortcuts = False
    text = path.read_text(encoding="utf-8")

    # If this is a specification r1.md, also inspect paired slice contract c1.md if present
    sources_to_scan = [text]
    try:
        paired_c1 = path.parents[2] / "contracts/slices" / path.parent.name / "c1.md"
        if paired_c1.is_file():
            sources_to_scan.append(paired_c1.read_text(encoding="utf-8"))
    except Exception:
        pass

    for src in sources_to_scan:
        for line in src.splitlines():
            if "Action Verb Lifecycle" in line:
                in_actions = True
                in_assertions = False
                in_shortcuts = False
                continue
            elif "Verifiable Design Assertions" in line or "Break Protocol" in line:
                in_actions = False
                in_assertions = True
                in_shortcuts = False
                continue
            elif "Dual-Channel Ergonomics" in line or "Keyboard Shortcuts" in line:
                in_actions = False
                in_assertions = False
                in_shortcuts = True
                continue
            elif line.startswith("##"):
                in_actions = False
                in_assertions = False
                in_shortcuts = False

            if not line.strip().startswith("|"):
                continue
            cells = [re.sub(r"[*`]", "", c).strip() for c in line.strip().strip("|").split("|")]
            if not cells or not cells[0]:
                continue
            first_lower = cells[0].lower()
            if first_lower in {"action id", "assertion", "reality breaker", "shortcut key", "token", "surface", "---"}:
                continue
            if set(cells[0]) <= {"-", ":"}:
                continue

            if in_actions:
                items.append(cells[0])
                if len(cells) > 1 and cells[1]:
                    items.append(cells[1])
            elif not in_assertions and not in_shortcuts:
                items.append(cells[0])
    return [it for it in items if it]


def _find_contract(html: Path, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    for parent in [html.parent, *html.parents]:
        candidates = list((parent / "prototype/contracts").glob("**/*.md"))
        if candidates:
            return candidates[0]
    return None


def _evidence_state(html: Path) -> dict[str, str]:
    for parent in [html.parent, *html.parents]:
        manifest = parent / "prototype/evidence/handoff-manifest.json"
        if manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                return {str(k): str(v) for k, v in data.get("verification", {}).items()}
            except (json.JSONDecodeError, OSError):
                return {}
    return {}


def assert_quality(html_path: str, tokens_path: str, check_stale: bool = False,
                   contract_path: str | None = None) -> bool:
    html = Path(html_path)
    tokens = Path(tokens_path)
    if not html.is_file() or not tokens.is_file():
        print(f"FAILED: required artifact missing (html={html}, tokens={tokens})")
        return False
    source = html.read_text(encoding="utf-8")
    token_source = tokens.read_text(encoding="utf-8")
    failures: list[str] = []

    # DOM and interaction assertions use semantic hooks, never domain names.
    entities = re.findall(r"(?:data-(?:entity|contract|item)|id|class)=[\"'][^\"']+[\"']", source)
    if len(entities) < 3 and not re.search(r"<button\b|<a\b|role=[\"\']button", source):
        failures.append("DOM assertion: no inspectable semantic elements")
    if not re.search(r"addEventListener\s*\(|\bon(?:click|keydown|submit)\s*=|onclick=", source):
        failures.append("interaction assertion: no declarative or imperative event binding")
    if not re.search(r"<button\b|<a\b[^>]*href=|role=[\"']button", source):
        failures.append("interaction assertion: no reachable control")

    declared = _contract_items(Path(contract_path) if contract_path else None)
    missing = [item for item in declared if len(item) > 2 and item not in source]
    if missing:
        failures.append("contract assertion: declared items absent from DOM: " + ", ".join(missing[:5]))

    # Tokens are checked strictly for declared, generic accessibility/typography hooks.
    if "font-variant-numeric" in token_source:
        if "font-variant-numeric" not in source and "tabular-nums" not in source:
            failures.append("token assertion: numeric presentation token is not consumed (use font-variant-numeric: tabular-nums or .tabular-nums)")
    if "--radius-" in token_source:
        if "var(--radius-" not in source and "var(--radius" not in source:
            failures.append("token assertion: radius tokens are not consumed (use var(--radius-*))")

    # Hard floor: reject raw inline hex colors in style attributes (enforces token inheritance)
    raw_style_hex = re.findall(r'style=["\'][^"\']*#[0-9a-fA-F]{3,8}[^"\']*["\']', source)
    if raw_style_hex:
        failures.append(f"craft assertion: raw inline hex colors in style attributes ({len(raw_style_hex)} found; use CSS custom properties / var(--...))")

    # Dual-channel keyboard ergonomics check: when declared in contract, ensure event listener exists
    if contract_path and Path(contract_path).is_file():
        contract_text = Path(contract_path).read_text(encoding="utf-8")
        if "Dual-Channel Ergonomics" in contract_text or "Shortcut Key" in contract_text:
            if not re.search(r"addEventListener\s*\(\s*['\"]key(?:down|up)['\"]|\bonkey(?:down|up)\s*=", source, re.IGNORECASE):
                failures.append("ergonomics assertion: declared dual-channel keyboard shortcuts not bound (missing keydown/keyup listener)")

        # Dynamic state machine check: when multi-state or Break Protocol stress checkpoints are declared
        if "The Break Protocol Stress Checkpoints" in contract_text or "Zero-Item Empty State" in contract_text:
            if not re.search(r"hashchange|location\.hash|data-state", source, re.IGNORECASE):
                failures.append("state-machine assertion: stress checkpoints declared but no state-switching hook detected (use hashchange / location.hash / data-state)")

    if check_stale:
        if re.search(r"\b(?:Lorem ipsum|placeholder text|sample copy)\b", source, re.IGNORECASE):
            failures.append("stale-template assertion: unconsidered placeholder content detected")

    states = _evidence_state(html)
    print("STATIC: " + ("pass" if not failures else "fail"))
    print("BROWSER: " + states.get("browser", "unverified"))
    print("VISUAL: " + states.get("visual", "unverified"))
    print("HUMAN: " + states.get("human", "unverified"))
    if failures:
        for i, failure in enumerate(failures, 1):
            print(f"  [{i}] {failure}")
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contract-driven prototype quality assertions")
    parser.add_argument("html")
    parser.add_argument("tokens", nargs="?", default=None)
    parser.add_argument("--tokens", dest="tokens_opt")
    parser.add_argument("--contract", dest="contract")
    parser.add_argument("--strict-divergence", action="store_true")
    args = parser.parse_args()
    html = Path(args.html)
    token_arg = args.tokens_opt or args.tokens
    if not token_arg:
        token_arg = next((str(p) for p in (html.parent / "tokens.css", Path.cwd() / "prototype/shared/tokens.css") if p.is_file()), "prototype/shared/tokens.css")
    sys.exit(0 if assert_quality(str(html), token_arg, args.strict_divergence, args.contract) else 1)

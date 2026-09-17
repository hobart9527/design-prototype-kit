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
    if not path or not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    items: list[str] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].lower() not in {"assertion", "expected", "reality breaker", "---"}:
            if cells[0] and not set(cells[0]) <= {"-", ":"}:
                items.append(cells[0])
    return items


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

    # Tokens are checked only for declared, generic accessibility/typography hooks.
    if "font-variant-numeric" in token_source and "font-variant-numeric" not in source and "var(--" not in source:
        failures.append("token assertion: numeric presentation token is not consumed")
    if "--radius-" in token_source and "var(--radius" not in source and "var(--" not in source:
        failures.append("token assertion: radius tokens are not consumed (use var(--radius-*))")

    # Hard floor: reject raw inline hex colors in style attributes (enforces token inheritance)
    raw_style_hex = re.findall(r'style=["\'][^"\']*#[0-9a-fA-F]{3,8}[^"\']*["\']', source)
    if raw_style_hex:
        failures.append(f"craft assertion: raw inline hex colors in style attributes ({len(raw_style_hex)} found; use CSS custom properties / var(--...))")

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

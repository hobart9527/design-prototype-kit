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

    in_actions = False
    in_assertions = False
    in_shortcuts = False
    in_ledger = False

    for src in sources_to_scan:
        for line in src.splitlines():
            if "Action Verb Lifecycle" in line:
                in_actions = True
                in_assertions = False
                in_shortcuts = False
                in_ledger = False
                continue
            elif "Verifiable Design Assertions" in line or "Break Protocol" in line:
                in_actions = False
                in_assertions = True
                in_shortcuts = False
                in_ledger = False
                continue
            elif "Dual-Channel Ergonomics" in line or "Keyboard Shortcuts" in line:
                in_actions = False
                in_assertions = False
                in_shortcuts = True
                in_ledger = False
                continue
            elif "Cognitive Budgeting" in line or "Ledger" in line or "Omissions" in line or "Boundaries" in line:
                in_actions = False
                in_assertions = False
                in_shortcuts = False
                in_ledger = True
                continue
            elif line.startswith("##"):
                in_actions = False
                in_assertions = False
                in_shortcuts = False
                in_ledger = False

            if not line.strip().startswith("|"):
                continue
            cells = [re.sub(r"[*`]", "", c).strip() for c in line.strip().strip("|").split("|")]
            if not cells or not cells[0]:
                continue
            first_lower = cells[0].lower()
            if first_lower in {"action id", "assertion", "reality breaker", "shortcut key", "token", "surface", "ledger zone", "---"}:
                continue
            if set(cells[0]) <= {"-", ":"}:
                continue

            if in_actions:
                act_id = cells[0].strip()
                trig_lbl = cells[1].strip() if len(cells) > 1 else ""
                trigger_tuple = tuple(s for s in (act_id, trig_lbl) if s and s not in ("-", "---", "N/A", "Action ID", "Trigger Button Label"))
                if trigger_tuple:
                    items.append(trigger_tuple)

                commit_lbl = cells[3].strip() if len(cells) > 3 else ""
                toast_lbl = cells[4].strip() if len(cells) > 4 else ""
                feedback_tuple = tuple(s for s in (commit_lbl, toast_lbl) if s and s not in ("-", "---", "N/A", "Commit Action Button", "Completion Feedback Toast"))
                if feedback_tuple:
                    items.append(feedback_tuple)
            elif not in_assertions and not in_shortcuts and not in_ledger:
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
    missing: list[str] = []
    for item in declared:
        if isinstance(item, tuple):
            if not any(sub in source for sub in item if sub and len(sub) > 2):
                missing.append("/".join(sub for sub in item if sub))
        elif len(item) > 2 and item not in source:
            missing.append(item)
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

    # Hard floor: reject rogue :root color property redeclarations in <style>
    style_blocks = re.findall(r"<style\b[^>]*>(.*?)</style>", source, re.DOTALL | re.IGNORECASE)
    for sb in style_blocks:
        if re.search(r":root\s*\{[^}]*--(?:accent|bg|border|text)-[a-zA-Z0-9_-]+\s*:[^}]*\}", sb):
            failures.append("token assertion: rogue :root color tokens declared in <style> (shadows tokens.css; must consume tokens from tokens.css)")
            break

    # Dual-channel keyboard ergonomics check: when declared in contract, ensure event listener exists
    if contract_path and Path(contract_path).is_file():
        contract_text = Path(contract_path).read_text(encoding="utf-8")
        if "Dual-Channel Ergonomics" in contract_text or "Shortcut Key" in contract_text:
            if not re.search(r"addEventListener\s*\(\s*['\"]key(?:down|up)['\"]|\bonkey(?:down|up)\s*=", source, re.IGNORECASE):
                failures.append("ergonomics assertion: declared dual-channel keyboard shortcuts not bound (missing keydown/keyup listener)")

        # Dynamic state machine check: when multi-state or Break Protocol stress checkpoints are declared
        if "The Break Protocol Stress Checkpoints" in contract_text or "Zero-Item Empty State" in contract_text:
            has_state_hook = bool(re.search(
                r"hashchange|location\.hash|data-state|state-[a-zA-Z0-9_-]+|class=[\"'][^\"']*(?:empty|loading|view-mode|state-)[^\"']*[\"']|id=[\"'][^\"']*(?:empty|loading|view-mode)[^\"']*[\"']",
                source,
                re.IGNORECASE,
            ))
            if not has_state_hook:
                failures.append("state-machine assertion: stress checkpoints declared but no state-switching hook detected (use hashchange / location.hash / data-state / class empty|loading|view-mode)")
            if not re.search(r"text-overflow\s*:\s*ellipsis|overflow(?:-[xy])?\s*:\s*(?:hidden|auto|scroll)|break-word|break-all|truncate|clamp\(|overflow-wrap\s*:\s*(?:anywhere|break-word)|word-break\s*:\s*break-all", source, re.IGNORECASE):
                failures.append("break-protocol assertion: missing string overflow containment (use text-overflow: ellipsis, overflow containment, truncate, or word-break: break-all)")

        # Zero Naked Metrics / Contextual Data Floor check
        if "Zero Naked Metrics" in contract_text or "Micro Sparklines" in contract_text or "sparkline" in contract_text.lower():
            has_svg = bool(re.search(r"<svg\b[^>]*>(?:.*?<polyline|.*?<path|.*?<rect|.*?<line|.*?<circle)", source, re.DOTALL | re.IGNORECASE))
            has_html5_data = bool(re.search(r"<(?:meter|progress|data|canvas)\b", source, re.IGNORECASE))
            has_context_modifier = bool(re.search(r'class=["\'][^"\']*(?:unit|baseline|sparkline|threshold|reference|trend|delta|badge|status)[^"\']*["\']|data-(?:unit|baseline|threshold|trend|delta)=', source, re.IGNORECASE))
            has_metric_with_unit = bool(re.search(r'class=["\'][^"\']*(?:stat|metric|kpi|value|num|count)[^"\']*["\'][^>]*>\s*[\d.,]+\s*(?:[a-zA-Z%/$€¥°]|/[a-zA-Z]+)', source, re.IGNORECASE))
            if not has_svg and not has_html5_data and not has_context_modifier and not has_metric_with_unit:
                failures.append("data-craft assertion: Zero Naked Metrics violation (metrics must carry reference baseline, unit context, delta trend, or visual sparkline/meter/canvas)")

        # Tactile Detents / Interactive feedback check
        if "Cognitive Budgeting" in contract_text or "Decisive Exchange 3-Frame" in contract_text or "Tactile Detents" in contract_text:
            has_active = bool(re.search(r":active\s*\{[^}]*(?:transform|scale|translate|filter|box-shadow|inset|opacity|background|border)", source, re.IGNORECASE))
            has_tailwind_active = bool(re.search(r"active:(?:scale|translate|bg|shadow|opacity)-", source))
            has_focus_visible = bool(re.search(r":focus-visible\s*\{", source, re.IGNORECASE))
            has_transition = bool(re.search(r"transition\s*:\s*[^;]+(?:transform|all|ease|cubic)", source, re.IGNORECASE))
            has_pointer_mutation = bool(re.search(r"addEventListener\s*\(\s*['\"](?:pointerdown|touchstart|mousedown)['\"].*?(?:classList|style|scale|active|transform)", source, re.DOTALL | re.IGNORECASE))
            if not (has_active or has_tailwind_active) and not (has_focus_visible and has_transition) and not has_pointer_mutation:
                failures.append("tactile physics assertion: interactive controls missing tactile response states (:active { transform/filter/shadow/... }, :focus-visible with transition, or pointerdown with state mutation)")

        # Multi-surface topology navigation check: when surface map m1.md declares sibling surfaces
        smap_candidates = []
        for p in [Path(contract_path).resolve(), html.resolve()]:
            curr = p.parent
            depth = 0
            while curr != curr.parent and depth < 5:
                smap_candidates.extend([
                    curr / "contracts/surface-maps/m1.md",
                    curr / "prototype/contracts/surface-maps/m1.md"
                ])
                if (curr / ".git").is_dir() or (curr / "skills").is_dir():
                    break
                curr = curr.parent
                depth += 1
        smap_file = next((p for p in smap_candidates if p.is_file()), None)
        if smap_file:
            smap_text = smap_file.read_text(encoding="utf-8")
            declared_surfaces = []
            for line in smap_text.splitlines():
                m = re.search(r"\*\*(.+?)\*\*\s*:\s*`([^`]+)`", line)
                if m:
                    p_raw = m.group(2).strip()
                    sid = p_raw.split("/")[0] if ("hero-anchor" in p_raw or "anchor" in p_raw) else p_raw.replace("surfaces/", "")
                    declared_surfaces.append(sid)
            current_id = html.parent.parent.name if html.parent.name in ("hero-anchor", "anchor") else html.parent.name
            siblings = [sid for sid in declared_surfaces if sid != current_id]
            if siblings:
                has_sibling_link = any(re.search(rf"href=[\"'][^\"']*{re.escape(sid)}[^\"']*[\"']", source) for sid in siblings)
                if not has_sibling_link:
                    failures.append(f"topology assertion: multi-surface navigation links missing for sibling surfaces ({', '.join(siblings)})")

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
    parser.add_argument("html", nargs="?", default=None, help="Target HTML file")
    parser.add_argument("tokens", nargs="?", default=None, help="Shared tokens stylesheet")
    parser.add_argument("--slice", dest="slice_id", help="Slice ID for convention-over-configuration auto-resolution")
    parser.add_argument("--tokens", dest="tokens_opt")
    parser.add_argument("--contract", dest="contract")
    parser.add_argument("--strict-divergence", action="store_true")
    args = parser.parse_args()

    root = Path.cwd()
    if args.slice_id:
        slice_id = args.slice_id
        candidates = [
            root / f"prototype/experiments/{slice_id}/anchor/index.html",
            root / f"prototype/experiments/{slice_id}/hero-anchor/index.html",
            root / f"prototype/surfaces/{slice_id}/index.html",
        ]
        html_path = next((p for p in candidates if p.is_file()), candidates[0])
        token_path = root / "prototype/shared/tokens.css"
        spec_path = root / f"prototype/specifications/{slice_id}/r1.md"
        contract_path = str(spec_path) if spec_path.is_file() else (args.contract or "")
        sys.exit(0 if assert_quality(str(html_path), str(token_path), args.strict_divergence, contract_path) else 1)

    if not args.html:
        parser.error("Must provide HTML path or --slice <id>")

    html = Path(args.html)
    token_arg = args.tokens_opt or args.tokens
    if not token_arg:
        token_arg = next((str(p) for p in (html.parent / "tokens.css", root / "prototype/shared/tokens.css") if p.is_file()), "prototype/shared/tokens.css")
    sys.exit(0 if assert_quality(str(html), token_arg, args.strict_divergence, args.contract) else 1)

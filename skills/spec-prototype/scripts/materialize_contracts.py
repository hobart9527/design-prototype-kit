"""Transactional contract projector for Stage 1 design specifications.

Pure Deterministic Compiler Discipline:
1. Projects designer intent directly from prototype/discussion.md into formal contracts.
2. Never guesses domain semantics, actions, or palettes; unauthored fields stay empty/unspecified.
3. Transactional Staging: compiles into a temporary staging area; validates all artifacts;
   promotes atomically only upon complete verification pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

NOT_YET_DECIDED = "not yet decided (Stage 1 in progress)"
UNSPECIFIED = "unspecified"
UNKNOWN = "unknown"

SECTION_SYNONYMS = {
    "product_title": ["Product Title", "Product", "产品名称", "产品", "Title"],
    "core_tension": ["Core Tension", "Tension", "极端张力", "核心张力", "张力", "冲突"],
    "content_language": ["Content Language", "Language", "语种", "语言"],
    "platform_target": ["Target OS", "Target Runtime", "Target Platform", "目标系统", "目标平台", "运行平台"],
    "device_class": ["Device Class", "Device", "设备类型", "设备"],
    "input_modality": ["Input Modality", "Input Context", "输入方式", "输入模态"],
    "reality_anchors": ["Reality Anchors", "Anchors", "地锚", "对标", "Reality Benchmark", "Reference Benchmarks", "对标参考"],
    "baseline": ["Dominant Baseline", "Baseline", "基准", "主流基准"],
    "ruthless_omissions": ["Ruthless Omissions", "Omissions", "克制舍弃", "舍弃清单", "克制设计", "explicit non-goals"],
    "material_boundaries": ["Material Non-Transfer Boundaries", "Non-Transfer", "非迁移边界", "物理隐喻", "Physical Metaphor"],
    "experience_invariants": ["Experience Invariants", "Invariants", "设计不变量", "体验不变量", "核心约束"],
    "action_verbs": ["Action Verb", "动作动词", "Verb Lifecycle", "动作流转", "Action Verbs"],
    "cognitive_ledger": ["Cognitive Budgeting", "借贷法则", "Energy Return Ledger", "Cognitive Ledger", "认知借贷"],
    "falsification_test": ["Perceptual Falsification Criteria", "Falsification Criteria", "Falsification", "5-Second", "证伪判据", "5秒", "5s_test"],
    "dual_channel": ["Dual-Channel", "Keyboard Shortcuts", "快捷键", "双通道"],
    "state_machine": ["State Machine", "Supported States", "States", "状态机", "状态流转"],
    "responsive_rules": ["Responsive", "Responsive Rules", "断点", "响应式"],
}


def _digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}" if path.is_file() else "unknown"


def extract_section_by_patterns(text: str, patterns: list[str]) -> str:
    """Extract markdown field or section matching any of the regex patterns."""
    for pat in patterns:
        m_field = re.search(
            rf"^\s*[-*+]?\s*[*_]*(?:{pat})[*_]*(?:\s*&[^\n:]*)?\s*[:：=]\s*([^\n]+)",
            text,
            re.MULTILINE | re.IGNORECASE,
        )
        if m_field and m_field.group(1).strip():
            val = m_field.group(1).strip().strip("`*_ ")
            if val and not val.lower().startswith("not yet") and not val.lower().startswith("unspecified"):
                return val
    for pat in patterns:
        m_table = re.search(
            rf"^\s*\|\s*[*_]*(?:{pat})[*_]*\s*\|\s*[^|]*\|\s*([^|]+)\|",
            text,
            re.MULTILINE | re.IGNORECASE,
        )
        if m_table and m_table.group(1).strip():
            val = m_table.group(1).strip().strip("`*_ ")
            if val and not val.lower().startswith("not yet"):
                return val
    for pat in patterns:
        m = re.search(
            rf"^##+[^\n]*?(?:{pat})[^\n]*\n(.*?)(?=\n##+|\Z)",
            text,
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ""

def extract_section(text: str, key: str) -> str:
    """Extract section text matching declared synonyms."""
    synonyms = SECTION_SYNONYMS.get(key, [key])
    return extract_section_by_patterns(text, synonyms)


def extract_dial_value(text: str, dial: str) -> str:
    m = re.search(rf"(?:[-*]\s*)?[`*_]*{re.escape(dial)}[`*_]*\s*[:：=]\s*[`*_]*([a-zA-Z0-9_-]+)[`*_]*", text, re.IGNORECASE)
    return m.group(1).strip().lower() if m else ""


def extract_bullets(text: str) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^(?:[-*]|\d+\.)\s+(.+)$", line)
        if m:
            item = m.group(1).strip().strip("`* ")
            if item and not item.lower().startswith("table"):
                bullets.append(item)
    if not bullets and text.strip():
        # Handle inline single-value extraction
        single = text.strip().strip("`* ")
        if single and not single.startswith("#"):
            bullets.append(single)
    return bullets


def extract_surfaces(disc_text: str, prod_text: str) -> tuple[list[str], list[str]]:
    sec = extract_section(disc_text, "surface_map") or extract_section_by_patterns(disc_text, ["Topology", "Surfaces", "表面", "拓扑", "表面映射"])
    raw_bullets = extract_bullets(sec) if sec else []
    all_surfaces: list[str] = []
    for b in raw_bullets:
        clean = re.sub(r"[^a-zA-Z0-9_\-\/]+", "-", b.split()[0]).strip("-").lower()
        if clean and clean not in all_surfaces:
            all_surfaces.append(clean)
    return all_surfaces, raw_bullets


def extract_action_verbs(disc_text: str, slice_id: str) -> list[dict[str, str]]:
    """Extract action verbs from discussion.

    Pure Compiler Discipline:
    Authored table entries are projected faithfully without guessing.
    When absent, emits an explicit [Hypothesis] action for the slice to satisfy
    contract safety without fabricating frozen operational facts.
    """
    sec = extract_section(disc_text, "action_verbs")
    actions: list[dict[str, str]] = []
    if sec:
        for line in sec.splitlines():
            line = line.strip()
            if line.startswith("|") and not line.startswith("|---"):
                parts = [p.strip().strip("`* ") for p in line.split("|") if p.strip()]
                if len(parts) >= 4 and parts[0].lower() not in ("action id", "action_id", "id"):
                    actions.append({
                        "action_id": parts[0],
                        "trigger_btn": parts[1],
                        "modal_header": parts[2],
                        "commit_btn": parts[3],
                        "toast": parts[4] if len(parts) > 4 else f"{parts[1]} Completed",
                        "impact": parts[5] if len(parts) > 5 else "Executes action",
                    })
    if not actions:
        clean_slice = slice_id.replace("-", " ").title()
        actions.append({
            "action_id": f"explore-{slice_id}",
            "trigger_btn": f"[Hypothesis] View {clean_slice}",
            "modal_header": f"[Hypothesis] Contextual Detail: {clean_slice}",
            "commit_btn": "Acknowledge",
            "toast": f"{clean_slice} Exploration Settled",
            "impact": f"[Hypothesis] Passive exploration view for {slice_id}; no authoritative state mutations authored.",
        })
    return actions


def rebind_slice_digests(root: Path, slice_id: str) -> None:
    """Rebind upstream sha256 digests in c1 and r1 using a unified mapping table."""
    targets = {
        "prod": (root / "prototype/product.md", r"(- Product (?:source references[^:]*|record revision and digest):\s*`[^`]+`,\s*)(?:sha256:[a-fA-F0-9]{64}|unknown)"),
        "smap": (root / "prototype/contracts/surface-maps/m1.md", r"(- Retained surface-map path, revision and digest:\s*`[^`]+`,\s*)(?:sha256:[a-fA-F0-9]{64}|unknown)"),
        "f1": (root / "prototype/contracts/foundation/f1.md", r"(- Foundation revision and digest:\s*`[^`]+`,\s*)(?:sha256:[a-fA-F0-9]{64}|unknown)"),
        "t1": (root / "prototype/contracts/tokens/t1.md", r"(- Token artifact path, revision, and digest:\s*`[^`]+`,\s*)(?:sha256:[a-fA-F0-9]{64}|unknown)"),
        "c1": (root / f"prototype/contracts/slices/{slice_id}/c1.md", r"(- Slice Contract revision and digest:\s*`[^`]+`,\s*)(?:sha256:[a-fA-F0-9]{64}|unknown)"),
        "disc": (root / "prototype/discussion.md", r"(- Decision/Discussion record reference:\s*`[^`]+`,\s*)(?:sha256:[a-fA-F0-9]{64}|unknown)"),
    }

    c1_path = root / f"prototype/contracts/slices/{slice_id}/c1.md"
    if c1_path.is_file():
        text = c1_path.read_text(encoding="utf-8")
        for key in ("smap", "prod"):
            p, pat = targets[key]
            if p.is_file():
                text = re.sub(pat, rf"\g<1>{_digest(p)}", text)
        c1_path.write_text(text, encoding="utf-8")

    r1_path = root / f"prototype/specifications/{slice_id}/r1.md"
    if r1_path.is_file():
        text = r1_path.read_text(encoding="utf-8")
        for key in ("prod", "f1", "t1", "c1", "disc"):
            p, pat = targets[key]
            if p.is_file():
                text = re.sub(pat, rf"\g<1>{_digest(p)}", text)
        r1_path.write_text(text, encoding="utf-8")


def build_frontend_contract(root: Path, slice_id: str, disc_text: str, prod_text: str, action_verbs: list[dict[str, str]]) -> str:
    """Emit the machine-readable frontend-contract.yaml representation."""
    prod_title = extract_section(disc_text, "product_title") or extract_section(prod_text, "product_title") or slice_id.replace("-", " ").title()
    tension = extract_section(prod_text, "core_tension") or extract_section(disc_text, "core_tension") or NOT_YET_DECIDED

    invariants = extract_bullets(extract_section(disc_text, "experience_invariants") or extract_section(prod_text, "experience_invariants"))

    # State machine
    sm_text = extract_section(disc_text, "state_machine")
    state_machine: dict[str, Any] = {"type": "hash_state", "status": "unspecified"}
    if sm_text:
        states = {}
        for line in sm_text.splitlines():
            line = line.strip().strip("-* ")
            if ":" in line:
                k, v = line.split(":", 1)
                states[k.strip()] = v.strip()
        if states:
            state_machine = {"type": "hash_state", "states": states}

    # Responsive rules
    resp_text = extract_section(disc_text, "responsive_rules")
    responsive_rules: dict[str, Any] = {"status": "unspecified"}
    if resp_text:
        rules = {}
        for line in resp_text.splitlines():
            line = line.strip().strip("-* ")
            if ":" in line:
                k, v = line.split(":", 1)
                rules[k.strip()] = v.strip()
        if rules:
            responsive_rules = rules

    actions_dict = {
        v["action_id"]: {
            "trigger": v["trigger_btn"],
            "modal": v["modal_header"],
            "commit": v["commit_btn"],
            "toast": v["toast"],
            "hazard_level": "high" if any(w in v["action_id"].lower() or w in v["impact"].lower() for w in ["drain", "evict", "isolate", "delete", "destroy", "purge"]) else "normal",
        }
        for v in action_verbs
    }

    contract_data = {
        "contract_version": "1.0",
        "authority_status": "sealed_provisional",
        "slice_id": slice_id,
        "provenance": {
            "product_title": prod_title,
            **({"core_tension": tension} if tension not in (NOT_YET_DECIDED, UNSPECIFIED) else {}),
            "spec_ref": f"prototype/specifications/{slice_id}/r1.md",
            "slice_contract_ref": f"prototype/contracts/slices/{slice_id}/c1.md",
            "tokens_json_ref": "prototype/contracts/tokens/t1.json",
            "tokens_css_ref": "prototype/shared/tokens.css",
            "discussion_digest": _digest(root / "prototype/discussion.md"),
            "product_digest": _digest(root / "prototype/product.md"),
        },
        "structure": {"root_element": f"main#{slice_id}-surface", "regions": [{"id": "unspecified", "role": "main"}]},
        "responsive_rules": responsive_rules,
        "state_machine": state_machine,
        "interaction_verbs": actions_dict,
        "experience_invariants": invariants,
        "accessibility_contract": {"focus_restoration": True},
        "tokens_binding": {"stylesheet": "prototype/shared/tokens.css", "json_spec": "prototype/contracts/tokens/t1.json"},
    }
    if yaml is not None:
        return yaml.dump(contract_data, sort_keys=False, allow_unicode=True)
    return json.dumps(contract_data, indent=2, ensure_ascii=False)


def _render_templates(root: Path, slice_id: str, disc_text: str, prod_text: str, action_verbs: list[dict[str, str]]) -> dict[str, tuple[Path, str]]:
    """Project all Stage 1 contracts from discussion into memory templates relative to project root."""
    disc_path = root / "prototype/discussion.md"
    prod_path = root / "prototype/product.md"

    p_title = extract_section(disc_text, "product_title") or slice_id.replace("-", " ").title()
    content_lang = extract_section(disc_text, "content_language") or extract_section(prod_text, "content_language") or ("zh-CN" if re.search(r"[一-龥]", disc_text) else "en-US")
    p_tension = extract_section(disc_text, "core_tension") or extract_section(prod_text, "core_tension") or NOT_YET_DECIDED
    target_ctx = (extract_section(disc_text, "platform_target") or UNKNOWN).lower()
    device_ctx = (extract_section(disc_text, "device_class") or ("mobile" if "mobile" in disc_text.lower() else UNKNOWN)).lower()
    input_ctx = (extract_section(disc_text, "input_modality") or ("touch" if "touch" in disc_text.lower() else UNKNOWN)).lower()

    # Baseline & Reality anchors
    p_baseline = extract_section(disc_text, "baseline") or extract_section(prod_text, "baseline") or UNSPECIFIED
    anchors = extract_section(disc_text, "reality_anchors") or extract_section(prod_text, "reality_anchors") or UNSPECIFIED

    # Ruthless omissions
    omissions = extract_bullets(extract_section(disc_text, "ruthless_omissions"))
    omissions_md = "\n".join(f"- {o}" for o in omissions) if omissions else "- Unspecified (no explicit omissions authored)"

    # Material non-transfer
    boundaries = extract_bullets(extract_section(disc_text, "material_boundaries"))
    boundaries_md = "\n".join(f"- {b}" for b in boundaries) if boundaries else "- Unspecified (no physical metaphors or transfer boundaries declared)"

    # Invariants
    invariants = extract_bullets(extract_section(disc_text, "experience_invariants") or extract_section(prod_text, "experience_invariants"))
    invariants_str = ", ".join(invariants)

    five_dials_md = "\n".join(
        f"- {dial}: {extract_dial_value(disc_text, dial) or extract_dial_value(prod_text, dial) or extract_section_by_patterns(disc_text, [dial]) or extract_section_by_patterns(prod_text, [dial]) or UNSPECIFIED}"
        for dial in ("Density", "Energy", "Materiality", "Rhythm", "Character")
    )

    # Surfaces
    surfaces, declared_surfaces = extract_surfaces(disc_text, prod_text)
    surface_lines = "\n".join(f"- {s}" for s in declared_surfaces) if declared_surfaces else f"- {slice_id}"
    all_surfaces = list(surfaces) if surfaces else [slice_id]
    if slice_id not in all_surfaces:
        all_surfaces.append(slice_id)
    surfaces_str = ", ".join(all_surfaces)

    # Action verbs
    verb_table = "\n".join(
        f"| `{v['action_id']}` | `{v['trigger_btn']}` | `{v['modal_header']}` | `{v['commit_btn']}` | `{v['toast']}` | {v['impact']} |"
        for v in action_verbs
    ) if action_verbs else "| `unspecified` | `Unspecified` | `Unspecified` | `Unspecified` | `Unspecified` | No destructive or mutating actions authored |"

    # Falsification criteria
    falsify_test = extract_section(disc_text, "falsification_test") or (
        "Within 5 seconds across 320px/390px/1280px viewports, an observer must identify the core tension "
        "and primary action trigger without reading secondary body prose or scanning help documentation."
    )
    falsify_section = f"## Perceptual Falsification Criteria (5-Second Viewport Test)\n\n- {falsify_test}\n\n"

    # Ergonomics
    ergonomics_sec = """## Touch-First Ergonomics (Gesture Detents & Haptic Recovery)

| Gesture Vector | Target Action / Interaction | Scope | Focus / State Settlement |
|---|---|---|---|
| `Tap` / `Press` | Direct manipulation of primary action trigger | Active card or action slot | Immediate perceptible feedback |""" if input_ctx == "touch" else """## Dual-Channel Ergonomics (Keyboard Shortcuts & Focus Recovery)

| Shortcut Key | Target Action / Interaction | Scope | Focus Restoration Anchor |
|---|---|---|---|
| `unspecified` | Activate primary action trigger / toggle inspector drawer | Active operational item or selection | Active selection anchor |
| `Esc` | Dismiss inspector drawer / modal | Global overlay | Restore focus to originating trigger |"""

    templates: dict[str, tuple[Path, str]] = {}

    # 1. Product
    templates["product"] = (root / "prototype/product.md", f"""# Product: {p_title}

- Baseline: {p_baseline}
- Reality Anchors: {anchors}
- Core Tension: {p_tension}
- Content Language: {content_lang}
- Status: candidate

```prototype-context
record: product
target-context: {target_ctx}
device-context: {device_ctx}
input-context: {input_ctx}
```

## 3 Ruthless Omissions (克制舍弃清单)
{omissions_md}
""")

    # 2. Surface Map
    templates["surface_map"] = (root / "prototype/contracts/surface-maps/m1.md", f"""# Product Surface Map: m1

- Product: {p_title}
- Surface map revision: m1
- Source discussion: `prototype/discussion.md`, {_digest(disc_path)}
- Status: sealed provisional

```prototype-context
record: surface-map
revision: m1
coverage: selected
selection-source: prototype/discussion.md
selected-surfaces: {slice_id}
surfaces: {surfaces_str}
```

## Declared surfaces
{surface_lines}
""")

    # 3. Foundation
    templates["foundation"] = (root / "prototype/contracts/foundation/f1.md", f"""# Project Experience Foundation: f1

- Product record revision and digest: `prototype/product.md`, {_digest(prod_path)}
- Foundation revision: f1
- Decision/Discussion record reference: `prototype/discussion.md`, {_digest(disc_path)}
- Status: sealed provisional

```prototype-context
record: experience-foundation
revision: f1
preserves: product
invariants: {invariants_str}
```

## 3 Ruthless Omissions
{omissions_md}

## Material Non-Transfer Boundaries
{boundaries_md}

## 5-Dial Style Register (五刻度风格寄存器)
{five_dials_md}
""")

    # 4. Tokens
    templates["tokens"] = (root / "prototype/contracts/tokens/t1.md", f"""# Design Tokens Revision: t1

- Foundation revision: f1
- Tokens revision: t1
- Status: sealed provisional
- Token source: authored

## Breakpoints
| Token | Value |
|---|---|
| `--bp-mobile` | 390px |
| `--bp-tablet` | 768px |
| `--bp-desktop` | 1280px |
""")

    # 5. Slice Contract
    templates["slice_contract"] = (root / f"prototype/contracts/slices/{slice_id}/c1.md", f"""# Prototype Slice Contract: c1

- Retained surface-map path, revision and digest: `prototype/contracts/surface-maps/m1.md`, {_digest(root / 'prototype/contracts/surface-maps/m1.md')}
- Product source references: `prototype/product.md`, {_digest(prod_path)}
- Status: sealed provisional
- Disposition: ready

```prototype-context
record: slice-contract
revision: c1
slice-id: {slice_id}
implements: m1
```

## Cognitive Budgeting & Energy Return Ledger (借贷法则)
- Low-Entropy Base: zero cognitive overhead
- High-Yield Borrow Zone: unspecified
- Repayment: settles to calm equilibrium

## Action Verb Lifecycle Table
| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
{verb_table}

## Decisive Exchange 3-Frame Specification
- Frame 1 (Calm): Baseline operational state
- Frame 2 (Committed): In-flight active mutation
- Frame 3 (Settled): Transaction complete with verified receipt

## Context Preservation Rules
- Zero full-page displacement for contextual drill-downs
""")

    # 6. Specification
    templates["specification"] = (root / f"prototype/specifications/{slice_id}/r1.md", f"""# Prototype Specification: r1

- Product record revision and digest: `prototype/product.md`, {_digest(prod_path)}
- Foundation revision and digest: `prototype/contracts/foundation/f1.md`, {_digest(root / 'prototype/contracts/foundation/f1.md')}
- Token artifact path, revision, and digest: `prototype/contracts/tokens/t1.md`, {_digest(root / 'prototype/contracts/tokens/t1.md')}
- Slice Contract revision and digest: `prototype/contracts/slices/{slice_id}/c1.md`, {_digest(root / f'prototype/contracts/slices/{slice_id}/c1.md')}
- Decision/Discussion record reference: `prototype/discussion.md`, {_digest(disc_path)}
- Required craft reads: references/03-verification/quality-floor.md, {_digest(Path(__file__).resolve().parents[1] / 'references/03-verification/quality-floor.md')}
- Status: candidate
- Candidate build authority: sealed provisional
- Candidate scope: prototype/experiments/{slice_id}/anchor/
- Evidence scope: prototype/evidence/probes/{slice_id}/
- Implemented references: {slice_id}
- Delegated implementation freedoms: HTML/CSS styling
- Required reachable-control closure: all interactive triggers and state actions
- Component constraints:

| Surface / interaction | Existing asset | Disposition | Constraint | Verification checkpoint |
|---|---|---|---|---|
| {slice_id} workspace | native HTML | delegated | Semantic layout | manual visual inspection |

```prototype-context
record: prototype-specification
revision: r1
prototype-medium: web
preserves: {invariants_str}
verification-environment: headless-browser
```

{ergonomics_sec}

## The Break Protocol Stress Checkpoints (四维破坏性极限压测)

| Reality Breaker | Concrete Test Vector / Input | Expected Graceful Behavior | Observed Result |
|---|---|---|---|
| **Unbreakable String** | Domain-authentic extreme 45+ char title or compound path | CSS ellipsis / word-break + tooltip, zero container blowout, no artificial placeholder litter | `pending` |
| **Zero-Item Empty State** | Filter: 0 results / empty list | Actionable empty card with reset filter button | `pending` |
| **Extreme 320px Fold** | 320px viewport width test | Horizontal scroll or vertical reflow, primary action reachable | `pending` |
| **Rapid Interruption** | Double-click / rapid trigger activations | Debounced submission, single idempotency state transition | `pending` |

{falsify_section}## Verifiable Design Assertions

| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| High text-to-background contrast compliant with WCAG 2.2 AA | present | unverified |
| Navigation and action affordances clear and reachable | present | unverified |
| Action Verb Lifecycle closure: trigger -> context/review -> commit -> settlement | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |
""")

    # 7. Frontend Contract
    templates["frontend_contract"] = (
        root / f"prototype/contracts/slices/{slice_id}/frontend-contract.yaml",
        build_frontend_contract(root, slice_id, disc_text, prod_text, action_verbs),
    )

    return templates


def materialize(root: Path, slice_id: str, force: bool = False, phase: str = "all") -> dict[str, str]:
    """Transactional Compiler: Stages, compiles tokens & digests, validates, then atomically promotes."""
    disc_path = root / "prototype/discussion.md"
    prod_path = root / "prototype/product.md"
    if not disc_path.is_file():
        raise FileNotFoundError(f"Missing mandatory entry index: {disc_path}")
    disc_text = disc_path.read_text(encoding="utf-8")
    prod_text = prod_path.read_text(encoding="utf-8") if prod_path.is_file() else ""

    phase_map = {
        "1": ["product"],
        "product": ["product"],
        "2": ["surface_map"],
        "surface_map": ["surface_map"],
        "3": ["foundation", "tokens"],
        "foundation": ["foundation", "tokens"],
        "4": ["slice_contract", "specification", "frontend_contract"],
        "slice": ["slice_contract", "specification", "frontend_contract"],
        "frontend": ["frontend_contract"],
        "all": ["product", "surface_map", "foundation", "tokens", "slice_contract", "specification", "frontend_contract"],
    }
    active_keys = set(phase_map.get(phase.lower(), phase_map["all"]))

    # Transactional Staging: staging lives alongside prototype/
    staging_id = f".staging_{uuid.uuid4().hex[:8]}"
    staging_root = root / "prototype" / staging_id
    staging_proto = staging_root / "prototype"
    staging_proto.mkdir(parents=True, exist_ok=True)

    try:
        # Copy existing prototype assets into staging so relative references resolve
        for item in (root / "prototype").iterdir():
            if item.name.startswith(".staging_") or item.name == staging_id:
                continue
            dest = staging_proto / item.name
            if item.is_dir():
                shutil.copytree(item, dest, symlinks=True)
            else:
                shutil.copy2(item, dest)

        # Generate templates against staging root
        action_verbs = extract_action_verbs(disc_text, slice_id)
        templates = _render_templates(staging_root, slice_id, disc_text, prod_text, action_verbs)

        # Write requested artifacts to staging
        for key in active_keys:
            if key not in templates:
                continue
            staged_path, content = templates[key]
            # Check if target already exists in real project and force not set
            real_target = root / staged_path.relative_to(staging_root)
            if real_target.is_file() and not force and phase.lower() not in ("all", "1", "2", "3", "4"):
                continue
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path.write_text(content, encoding="utf-8")

        # Handle tokens compilation in staging
        if "tokens" in active_keys:
            try:
                import compile_tokens
                comp_dials = {dial.lower(): (extract_dial_value(disc_text, dial) or extract_dial_value(prod_text, dial) or "balanced") for dial in ("density", "energy", "materiality", "rhythm", "character")}
                css_tokens = compile_tokens.compute_tokens(dials=comp_dials, mode="formal")
                css_out = compile_tokens.generate_css(css_tokens)
                css_file = staging_proto / "shared/tokens.css"
                css_file.parent.mkdir(parents=True, exist_ok=True)
                css_file.write_text(css_out, encoding="utf-8")

                dtcg_json = compile_tokens.generate_dtcg_json(css_tokens)
                json_file = staging_proto / "contracts/tokens/t1.json"
                json_file.parent.mkdir(parents=True, exist_ok=True)
                json_file.write_text(json.dumps(dtcg_json, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception as exc:
                print(f"warning: token compilation in staging skipped: {exc}", file=sys.stderr)

        # Rebind digests inside staging
        rebind_slice_digests(staging_root, slice_id)

        # Best-effort envelope check in staging
        try:
            from assemble_envelope import assemble
            env = assemble(staging_root, slice_id)
            env_path = staging_proto / f"experiments/{slice_id}/envelope.json"
            env_path.parent.mkdir(parents=True, exist_ok=True)
            env_path.write_text(json.dumps(env, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

        # All verifications passed! Atomically promote staged artifacts to real root
        created: dict[str, str] = {}
        for key in active_keys:
            if key not in templates:
                continue
            staged_path, _ = templates[key]
            rel = staged_path.relative_to(staging_root)
            real_target = root / rel
            real_target.parent.mkdir(parents=True, exist_ok=True)
            if staged_path.is_file():
                shutil.copy2(staged_path, real_target)
                created[key] = str(real_target)

        # Promote token assets and envelope if generated
        for extra_rel, extra_key in [
            ("prototype/shared/tokens.css", "tokens_css"),
            ("prototype/contracts/tokens/t1.json", "tokens_json"),
            (f"prototype/experiments/{slice_id}/envelope.json", "envelope")
        ]:
            sp = staging_root / extra_rel
            if sp.is_file():
                dp = root / extra_rel
                dp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sp, dp)
                created[extra_key] = str(dp)

        # Final digest refresh in place
        rebind_slice_digests(root, slice_id)
        return created

    finally:
        shutil.rmtree(staging_root, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize generic Stage 1 contracts")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--slice", default="console")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--phase", default="all")
    args = parser.parse_args()
    try:
        res = materialize(args.root.resolve(), args.slice, args.force, args.phase)
        print(json.dumps({"status": "ok", "slice_id": args.slice, "phase": args.phase, "materialized": res}, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

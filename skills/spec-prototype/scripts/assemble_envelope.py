#!/usr/bin/env python3
"""Synthesize a self-contained execution envelope for spec-prototype-builder.

Validates that Stage 1 Design Spec contracts exist and extracts all layout,
token, state machine, and assertion parameters into a single envelope JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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


def extract_css_tokens(css_text: str) -> Dict[str, str]:
    """Parse flat CSS custom property dictionary from tokens.css."""
    tokens: Dict[str, str] = {}
    for m in re.finditer(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", css_text):
        tokens[m.group(1).strip()] = m.group(2).strip()
    return tokens


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

    # Target scopes: support both neutral anchor/ and legacy hero-anchor/
    default_scope = f"prototype/experiments/{slice_id}/anchor/"
    write_scope = extract_field(spec_content, "Prototype write scope", default_scope)
    write_scope_clean = write_scope.strip("`'\" ")
    if not write_scope_clean.endswith("/"):
        write_scope_clean += "/"

    target_html = write_scope_clean + "index.html"
    evidence_scope = extract_field(spec_content, "Evidence write scope", f"prototype/evidence/probes/{slice_id}/").strip("`'\" ")

    # Determine layout profile & composable context
    # v10.1: Reference patterns are composable guides; default is adaptive composite rather than forced dense-console
    baseline_match = re.search(r"^[-*+]?\s*(?:Dominant\s+Baseline|Baseline|基线|Reference\s+Pattern)\s*[:=]\s*([^\n]+)", product_content, re.MULTILINE | re.IGNORECASE)
    declared_baseline = baseline_match.group(1).strip() if baseline_match else ""

    if re.search(r"Baseline 4|Consumer|Mobile|Touch|消费|移动|触控|somatic", declared_baseline, re.IGNORECASE):
        layout_profile = "somatic-touchflow"
    elif re.search(r"Baseline 3|Editorial|Reading|阅读|文章|出版|editorial", declared_baseline, re.IGNORECASE):
        layout_profile = "editorial-reading"
    elif re.search(r"Baseline 2|SaaS|Commerce|Project|画布|业务|交易|canvas", declared_baseline, re.IGNORECASE):
        layout_profile = "operational-canvas"
    elif re.search(r"Baseline 1|Console|Control|工作台|控制台|运维|telemetry", declared_baseline, re.IGNORECASE):
        layout_profile = "dense-console"
    else:
        all_spec_text = product_content + " " + spec_content
        if re.search(r"\bBaseline 4\b|mobile-first|touch-friendly", all_spec_text, re.IGNORECASE):
            layout_profile = "somatic-touchflow"
        elif re.search(r"\bBaseline 3\b|editorial-reading|long-form", all_spec_text, re.IGNORECASE):
            layout_profile = "editorial-reading"
        elif re.search(r"\bBaseline 2\b|operational-canvas|master-detail", all_spec_text, re.IGNORECASE):
            layout_profile = "operational-canvas"
        elif re.search(r"\bBaseline 1\b|dense-console|telemetry-grid", all_spec_text, re.IGNORECASE):
            layout_profile = "dense-console"
        else:
            # v10.1: Composable adaptive workspace instead of rigid dense-console fallback
            layout_profile = "adaptive-workspace"

    # Extract verifiable assertions & Break Protocol
    assertions: List[str] = []
    break_checkpoints: List[str] = []
    shortcuts: List[str] = []
    verb_lifecycle: List[Dict[str, str]] = []
    decisive_frames: List[str] = []
    context_rules: List[str] = []

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

    # Parse Action Verb Lifecycle and Frame deduction from slice contract
    cognitive_ledger = {
        "zero_borrow_base": "Standard navigation, filter chips, and basic data tables must maintain zero cognitive friction with zero distracting motion.",
        "high_yield_borrow_zone": f"Primary operational {slice_id} workspace is granted visual energy budget: perceptible tactile feedback, baseline sparklines, and micro-flow liveliness.",
        "repayment_settlement": "Upon decisive action commit or inspector close, all dynamic visual indicators settle back into baseline calm equilibrium."
    }
    in_ledger = False
    in_verbs = False
    in_frames = False
    in_rules = False
    in_fault = False
    fault_tolerance: List[Dict[str, str]] = []
    for line in contract_content.splitlines():
        if "Cognitive Budgeting & Energy Return Ledger" in line:
            in_ledger = True
            in_verbs = False
            in_frames = False
            in_rules = False
            in_fault = False
            continue
        elif "Action Verb Lifecycle Table" in line:
            in_ledger = False
            in_verbs = True
            in_frames = False
            in_rules = False
            in_fault = False
            continue
        elif "Fault Tolerance & Error Recovery Contract" in line:
            in_ledger = False
            in_verbs = False
            in_frames = False
            in_rules = False
            in_fault = True
            continue
        elif "Decisive Exchange 3-Frame" in line:
            in_ledger = False
            in_verbs = False
            in_frames = True
            in_rules = False
            in_fault = False
            continue
        elif "Context Preservation Rules" in line:
            in_ledger = False
            in_verbs = False
            in_frames = False
            in_rules = True
            in_fault = False
            continue
        elif line.startswith("##"):
            in_ledger = False
            in_verbs = False
            in_frames = False
            in_rules = False
            in_fault = False
            continue

        if in_fault and line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [re.sub(r"[*`]", "", p).strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 3 and parts[0] not in ("Operation Category",):
                fault_tolerance.append({
                    "category": parts[0],
                    "hazard_level": parts[1] if len(parts) > 1 else "",
                    "defense": parts[2] if len(parts) > 2 else "",
                    "recovery": parts[3] if len(parts) > 3 else ""
                })

        if in_ledger and line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 2 and parts[0] not in ("Ledger Zone",):
                zone_name = parts[0].lower()
                if "zero" in zone_name or "base" in zone_name or "基座" in zone_name:
                    cognitive_ledger["zero_borrow_base"] = parts[1]
                elif "borrow" in zone_name or "特区" in zone_name or "溢价" in zone_name:
                    cognitive_ledger["high_yield_borrow_zone"] = parts[1]
                elif "repayment" in zone_name or "settle" in zone_name or "偿还" in zone_name:
                    cognitive_ledger["repayment_settlement"] = parts[1]
        elif in_verbs and line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [re.sub(r"[*`]", "", p).strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 4 and parts[0] not in ("Action ID",):
                verb_lifecycle.append({
                    "action_id": parts[0],
                    "trigger_btn": parts[1],
                    "modal_header": parts[2],
                    "commit_btn": parts[3],
                    "toast": parts[4] if len(parts) > 4 else "",
                })
        elif in_frames and line.strip().startswith("- "):
            decisive_frames.append(line.strip()[2:].strip())
        elif in_rules and line.strip().startswith("- "):
            context_rules.append(line.strip()[2:].strip())

    # Extract 3 Ruthless Omissions and Material Invariants from Foundation / Product
    f1_text = paths["foundation"].read_text(encoding="utf-8")
    omissions: List[str] = []
    invariants: List[str] = []
    in_om = False
    in_inv = False
    for line in f1_text.splitlines():
        if "3 Ruthless Omissions" in line:
            in_om = True
            in_inv = False
            continue
        elif "Material Non-Transfer" in line:
            in_om = False
            in_inv = True
            continue
        elif line.startswith("##"):
            in_om = False
            in_inv = False
            continue
        if in_om and line.strip().startswith("- "):
            omissions.append(line.strip()[2:].strip())
        elif in_inv and line.strip().startswith("- "):
            invariants.append(line.strip()[2:].strip())

    # For mobile/touch profiles, sanitize constraints to avoid desktop keybinding bleeds
    if layout_profile == "somatic-touchflow":
        shortcuts = ["`Tap` / `Press`", "`Swipe Down`", "`Edge Swipe`"]

    constraints = {
        "dual_channel_shortcuts": shortcuts,
        "action_verb_lifecycle": verb_lifecycle,
        "break_protocol_checkpoints": break_checkpoints,
        "decisive_exchange_frames": decisive_frames,
        "context_preservation_rules": context_rules,
        "ruthless_omissions": omissions or [
            "Zero generic marketing cards, promotional hero banners, or superficial carousel widgets.",
            "Zero nested modal inception or multi-step wizard deadlocks; interactions stay in-canvas or single contextual drawer.",
            "Zero ungrounded alien physics, gratuitous full-screen particles, or unconsidered neutral gray #808080 washes."
        ],
        "material_non_transfer_boundaries": invariants or [
            "Digital Surface Layering: Transparency expresses spatial depth hierarchy only, never gratuitous frosted blur that compromises contrast.",
            "Perceptible Action Feedback: Interactive controls possess immediate, perceptible feedback (e.g. tactile micro-press, subtle background shift, or border detent); never frictionless float.",
            "Precision Status Emissives: Status indicators provide calibrated visual signals; never raw flat neon washes."
        ],
    }
    explicit_turns = extract_field(spec_content, "Maximum operational repair attempts")
    if explicit_turns:
        constraints["maximum_operational_repair_attempts"] = explicit_turns

    spec_rel = paths["specification"].relative_to(root).as_posix()
    target_dir = (root / target_html).parent
    token_rel_href = os.path.relpath(paths["tokens_css"], target_dir)
    token_link_tag = f'<link rel="stylesheet" href="{token_rel_href}">'

    # Parse shared topology navigation from surface map
    nav_links = []
    current_role = "primary"
    for line in smap_content.splitlines():
        m = re.search(r"\*\*(.+?)\*\*\s*:\s*`([^`]+)`", line)
        if m:
            role_label, path_raw = m.group(1).strip(), m.group(2).strip()
            if "hero-anchor" in path_raw:
                surf_path = root / f"prototype/experiments/{path_raw}/index.html"
                sid = path_raw.split("/")[0]
            elif "anchor" in path_raw:
                surf_path = root / f"prototype/experiments/{path_raw}/index.html"
                sid = path_raw.split("/")[0]
            elif path_raw.startswith("surfaces/"):
                surf_path = root / f"prototype/{path_raw}/index.html"
                sid = path_raw.replace("surfaces/", "")
            else:
                p_anchor = root / f"prototype/experiments/{path_raw}/anchor/index.html"
                p_hero = root / f"prototype/experiments/{path_raw}/hero-anchor/index.html"
                if p_anchor.is_file():
                    surf_path = p_anchor
                elif p_hero.is_file():
                    surf_path = p_hero
                else:
                    surf_path = root / f"prototype/{path_raw}/index.html"
                sid = path_raw

            is_active = (sid == slice_id or path_raw == slice_id)
            if is_active:
                if "Primary" in role_label or "主工作区" in role_label:
                    current_role = "primary"
                elif "Contextual" in role_label or "上下文" in role_label:
                    current_role = "contextual"
                else:
                    current_role = "supporting"

            rel_href = os.path.relpath(surf_path, target_dir)
            label = sid.replace("-", " ").title()
            nav_links.append({
                "slice_id": sid,
                "label": label,
                "role": role_label,
                "href": rel_href,
                "active": is_active
            })

    verification_cmd = f"python3 skills/spec-prototype/scripts/verify_prototype_quality.py --slice {slice_id}"
    capture_cmd = f"node skills/spec-prototype/scripts/capture.mjs --slice {slice_id}"

    # Extract OOUX Cardinality & Spatial Mapping from surface map or profile defaults
    # v10.1: Cardinality constrains candidate structures; task/device/context determine layout mode.
    # Default is adaptive rather than forced master-detail.
    cardinality_match = re.search(r"(?:Cardinality|OOUX|实体基数|基数映射)[^\n]*[:=]?\s*(1:1|1:N|N:M)", smap_content + " " + spec_content, re.IGNORECASE)
    if cardinality_match:
        ooux_cardinality = cardinality_match.group(1).upper()
        if ooux_cardinality == "1:1":
            ooux_layout_mode = "focused-cockpit"
        elif ooux_cardinality == "1:N":
            ooux_layout_mode = "split-master-detail"
        elif ooux_cardinality == "N:M":
            ooux_layout_mode = "node-link-canvas"
        else:
            ooux_layout_mode = "adaptive"
    else:
        # Context/Profile-driven heuristics without forcing master-detail on unknown profiles
        if layout_profile == "dense-console":
            ooux_cardinality = "1:N"
            ooux_layout_mode = "split-master-detail"
        elif layout_profile == "editorial-reading":
            ooux_cardinality = "1:1"
            ooux_layout_mode = "focused-column"
        elif layout_profile == "operational-canvas":
            ooux_cardinality = "N:M"
            ooux_layout_mode = "interactive-workspace"
        elif layout_profile == "somatic-touchflow":
            ooux_cardinality = "1:N"
            ooux_layout_mode = "card-stream"
        else:
            # v10.1: adaptive topology for unknown products
            ooux_cardinality = "adaptive"
            ooux_layout_mode = "adaptive-flow"

    ooux_topology = {
        "cardinality": ooux_cardinality,
        "layout_mode": ooux_layout_mode,
        "spatial_rule": (
            "1:1 Focused Cockpit: Single focal instrument or deep reading column; zero split distraction."
            if ooux_cardinality == "1:1" else
            "1:N Master-Detail: High-density stream or list paired with sticky contextual parameter inspection."
            if ooux_cardinality == "1:N" else
            "N:M Relational Matrix / Canvas: Multi-node interconnected graph or multi-facet filtering grid."
            if ooux_cardinality == "N:M" else
            "Adaptive Flow: Spatial topology tailored to task context and primary object without forced split."
        )
    }

    # Profile-aware interaction_spec: only emit what the Builder must actually implement.
    # dense-console / operational-canvas: full lifecycle, shortcuts, sparklines.
    # editorial-reading: focus on typography reading experience; strip heavy action modals.
    # somatic-touchflow: strip desktop shortcuts; keep thumb-zone state machine only.
    _is_dense = layout_profile in ("dense-console", "operational-canvas")
    _is_editorial = layout_profile == "editorial-reading"
    _is_touch = layout_profile == "somatic-touchflow"

    interaction_spec: Dict[str, Any] = {
        "state_machine": {
            "type": "hash_state",
            "query_param": "state",
            "supported_states": ["ideal", "empty", "error"],
            "dom_hook": "document.body.dataset.state"
        },
        "break_protocol_checkpoints": break_checkpoints,
    }
    if _is_dense:
        # Full rich interaction contract for workbench/console profiles
        interaction_spec["dual_channel_shortcuts"] = shortcuts
        interaction_spec["action_verb_lifecycle"] = verb_lifecycle
        interaction_spec["decisive_exchange_frames"] = decisive_frames
        interaction_spec["context_preservation_rules"] = context_rules
        interaction_spec["profile_notes"] = (
            "dense-console: implement full Action Verb Lifecycle (trigger→drawer/modal→commit→toast), "
            "Space/Esc dual-channel shortcuts, tabular-nums telemetry, SVG micro-sparklines."
        )
    elif _is_editorial:
        # Reading profile: quiet interactions, no intrusive modals
        interaction_spec["profile_notes"] = (
            "editorial-reading: prioritize focused typography (max-width 68ch), paper-contrast palette, "
            "quiet inline feedback. Do NOT implement modal dialogs, action drawers, or telemetry sparklines. "
            "Reading metric labels (e.g. '8 min read') are sufficient interactive feedback."
        )
        interaction_spec["reading_ergonomics"] = {
            "measure_max": "68ch",
            "contrast_floor": ">7:1 text-to-background",
            "feedback_style": "inline non-blocking state labels only",
        }
    elif _is_touch:
        # Touch/mobile: thumb-zone ergonomics, spring physics
        interaction_spec["profile_notes"] = (
            "somatic-touchflow: implement 44px thumb-zone touch targets, spring physics gesture hints, "
            "bottom-sheet action trays. Desktop keyboard shortcuts are NOT required."
        )
        interaction_spec["touch_ergonomics"] = {
            "min_touch_target": "44px",
            "action_tray": "bottom-sheet",
            "gesture_hints": True,
        }
        interaction_spec["context_preservation_rules"] = context_rules
    else:
        # adaptive-workspace / custom-composite
        interaction_spec["profile_notes"] = (
            "adaptive-workspace: composable layout guided by product context and task requirements. "
            "Implement responsive hierarchy, clear state transitions, and accessible semantic interactions."
        )
        interaction_spec["dual_channel_shortcuts"] = shortcuts
        interaction_spec["action_verb_lifecycle"] = verb_lifecycle
        interaction_spec["decisive_exchange_frames"] = decisive_frames
        interaction_spec["context_preservation_rules"] = context_rules

    app_shell_blueprints = {
        "adaptive-workspace": {
            "profile": "adaptive-workspace",
            "spatial_roles": ["header_navigation", "primary_workspace", "contextual_inspector"],
            "density_rules": "fluid responsive layout, semantic spacing scale, zero rigid pixel clamping",
            "composition_guidance": "Design shell adapted to product thesis; structure surfaces for cognitive clarity and task continuity; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "dense-console": {
            "profile": "dense-console",
            "spatial_roles": ["global_nav", "operational_viewport", "context_inspector", "status_telemetry"],
            "density_rules": "4px micro-grid, 11-13px tabular-nums telemetry, multi-pane instrument rack, zero promotional banner",
            "composition_guidance": "Pin viewport height (100vh); enable independent scrolling within operational matrix and contextual inspector; no page-level runaway scroll; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "operational-canvas": {
            "profile": "operational-canvas",
            "spatial_roles": ["workspace_header", "entity_rail", "operational_canvas", "context_panel"],
            "density_rules": "8px grid rhythm, progressive visual elevation, master-detail hierarchy",
            "composition_guidance": "Support fluid zoom/pan or split-view master-detail; contextual inspectors should overlay or dock non-destructively; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "editorial-reading": {
            "profile": "editorial-reading",
            "spatial_roles": ["reading_header", "marginalia_nav", "reading_measure"],
            "density_rules": "68ch line-length measure, paper-contrast foundation, quiet marginalia",
            "composition_guidance": "Prioritize typographic rhythm, asymmetrical marginalia for citations/telemetry, and distraction-free central column; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "somatic-touchflow": {
            "profile": "somatic-touchflow",
            "spatial_roles": ["touch_header", "touch_surface", "thumb_zone_nav"],
            "density_rules": "44px thumb-zone touch targets, fluid spring curves, high-contrast expressive surfaces",
            "composition_guidance": "Anchor primary decisive actions to bottom thumb-reach reach zone; implement spring physics and gesture signifiers; enforce @media (prefers-reduced-motion: reduce) resilience."
        }
    }

    product_title_raw = next((line.lstrip("# ").strip() for line in product_content.splitlines() if line.startswith("#")), "Product")
    brand_title = re.sub(r"^Product(?:\s+Thesis)?\s*[:\-]\s*", "", product_title_raw, flags=re.IGNORECASE).strip() or "Product Console"

    app_shell_contracts = {
        "adaptive-workspace": {
            "profile": "adaptive-workspace",
            "header": "Responsive header adapted to product thesis with navigation and primary state indicator",
            "main_viewport": "Primary content/workspace slot structured according to OOUX entity topology",
            "context_drawer": "Contextual inspection panel, drawer, or modal invoked on demand",
            "status_bar": "Calm status/metadata bar providing contextual grounding and feedback"
        },
        "dense-console": {
            "profile": "dense-console",
            "header": "Top bar containing system title, active slice indicator, and topology navigation",
            "main_viewport": "Primary operational slot matching declared entity cardinality",
            "context_drawer": "Contextual parameter inspection drawer or modal",
            "status_bar": "Footer telemetry and shortcuts guide"
        },
        "operational-canvas": {
            "profile": "operational-canvas",
            "header": "Workspace header with breadcrumb navigation and primary actions",
            "main_viewport": "Fluid canvas or master-detail interactive work area",
            "context_drawer": "Contextual parameter inspector panel or drawer",
            "status_bar": "Canvas view controls and operational status indicator"
        },
        "editorial-reading": {
            "profile": "editorial-reading",
            "header": "Minimalist header with publication title, reading progress, and index toggle",
            "main_viewport": "Focused typography-driven reading column (68ch max width)",
            "context_drawer": "Asymmetrical marginalia for annotations, outline, or related links",
            "status_bar": "Calm reading footer with chapter navigation and font controls"
        },
        "somatic-touchflow": {
            "profile": "somatic-touchflow",
            "header": "Compact mobile header with contextual title and back action",
            "main_viewport": "Touch-friendly card feed with thumb-zone ergonomics and gesture hints",
            "context_drawer": "Bottom sheet or modal action tray for quick modifications",
            "status_bar": "Persistent bottom thumb navigation bar"
        }
    }

    # Extract product thesis, core tension and reality anchors
    prod_thesis_raw = ""
    prod_tension_raw = ""
    for line in product_content.splitlines():
        if "Core Tension:" in line or "Tension:" in line:
            prod_tension_raw = line.split(":", 1)[1].strip()
        elif line.startswith("# Product Thesis:"):
            prod_thesis_raw = line.split(":", 1)[1].strip()

    # Dual-Envelope Architecture (v10): Decouple rigid constraints from creative agency
    constraint_envelope = {
        "domain_thesis": {
            "title": brand_title,
            "product_thesis": prod_thesis_raw or brand_title,
            "core_tension": prod_tension_raw or "Operational Efficiency vs Cognitive Ergonomics",
        },
        "ooux_topology": ooux_topology,
        "interaction_spec": interaction_spec,
        "fault_tolerance_protocol": fault_tolerance,
        "data_stress_boundaries": {
            "overflow_protection": "text-overflow: ellipsis, overflow-wrap: anywhere, or word-break: break-all required on dynamic labels",
            "empty_state_guidance": (
                f"Actionable guidance: render meaningful empty illustration/icon paired with '{verb_lifecycle[0]['trigger_btn']}' primary recovery button"
                if verb_lifecycle else
                "Explicit guidance message required; provide action button if state is user-correctable"
            ),
            "tabular_numbers_required": True
        },
        "target_html_path": target_html,
        "token_stylesheet_ref": token_rel_href,
        "verifiable_assertions": assertions,
        "a11y_floors": {
            "contrast": "WCAG 2.2 AA compliant (>4.5:1 text, >3:1 UI components)",
            "motion": "@media (prefers-reduced-motion: reduce) override required",
            "min_touch_target": "44px on touch-first somatic, 32px on compact workbench"
        }
    }

    # Attention routing calibrated to product context, not rigid console prior
    if layout_profile == "editorial-reading":
        l1_scan = "Document title, reading progress, and primary reading actions"
        l2_inspect = "In-line annotations, footnotes, or chapter table-of-contents"
        l3_diag = "Bibliography, revision history, or document metadata"
    elif layout_profile == "somatic-touchflow":
        l1_scan = "Current step or primary entity status and decisive thumb-zone CTA"
        l2_inspect = "Contextual configuration sheet or secondary parameters"
        l3_diag = "Confirmation receipt, order/booking history, or terms"
    elif layout_profile == "operational-canvas":
        l1_scan = "Workspace title, active project state, and primary creation action"
        l2_inspect = "Selected entity properties, inline comments, or activity stream"
        l3_diag = "Version history, dependency matrix, or integration settings"
    elif layout_profile == "dense-console":
        l1_scan = "Persistent core identity, key system health/progress metrics, and primary action trigger"
        l2_inspect = "In-place details, expandable drawer, or docked inspection panel"
        l3_diag = "Full event logs, raw payload inspector, and historical audit trail"
    else:
        # adaptive-workspace
        l1_scan = f"Primary {slice_id} workspace status and primary decisive action trigger"
        l2_inspect = "Contextual entity inspection, inline details, or adaptive drawer"
        l3_diag = "Complete entity audit, auxiliary parameters, or secondary flow"

    creative_envelope = {
        "layout_profile": layout_profile,
        "spatial_composition_agency": "Builder owns layout rhythm, panel proportions, and responsive flow. No pre-baked rigid HTML scaffolding mandated.",
        "attention_routing": {
            "primary_visual_anchor": f"Primary {slice_id} focal workspace & status indicator",
            "disclosure_levels": {
                "l1_ambient_scan": l1_scan,
                "l2_contextual_inspection": l2_inspect,
                "l3_deep_diagnostics": l3_diag
            },
            "noise_budget": {
                "max_simultaneous_emissive_alerts": 3,
                "rule": "Avoid saturated multi-alert flashing; maintain atmospheric calm under normal operational states"
            }
        },
        "cognitive_ledger": cognitive_ledger,
        "suggested_blueprints": app_shell_blueprints.get(layout_profile, app_shell_blueprints["adaptive-workspace"]),
        "reference_pattern_guidance": app_shell_contracts.get(layout_profile, app_shell_contracts["adaptive-workspace"])
    }

    # P0-1: Build Authority Gate
    # In formal build mode (lean-builder-envelope), actions marked with [Hypothesis] cannot be built as frozen fact
    # unless explicitly allowed via probe mode or non-formal flag.
    has_hypothesis_action = False
    for v in verb_lifecycle:
        # Check action label, modal header or impact for hypothesis markers
        for val in v.values():
            if isinstance(val, str) and "[hypothesis]" in val.lower():
                has_hypothesis_action = True
                break
        if has_hypothesis_action:
            break

    # Determine build authority
    build_authority = "formal"
    if has_hypothesis_action:
        build_authority = "probe_only"

    envelope = {
        "envelope_version": "2.0",
        "envelope_architecture": "3.0-dual",
        "build_authority": build_authority,
        "has_hypothesis_actions": has_hypothesis_action,
        "repository_root": str(root.resolve()),
        "skill_root": str(SKILL.resolve()),
        "slice_id": slice_id,
        "mode": "lean-builder-envelope",
        "layout_profile": layout_profile,
        "constraint_envelope": constraint_envelope,
        "creative_envelope": creative_envelope,
        "domain_thesis": constraint_envelope["domain_thesis"],
        "ooux_topology": ooux_topology,
        "attention_routing": creative_envelope["attention_routing"],
        "data_stress_boundaries": constraint_envelope["data_stress_boundaries"],
        "app_shell_blueprint": creative_envelope["suggested_blueprints"],
        "app_shell_contract": creative_envelope["reference_pattern_guidance"],
        "target_html_path": target_html,
        "evidence_output_dir": evidence_scope,
        "token_stylesheet_ref": token_rel_href,
        "token_link_tag": token_link_tag,
        "topology_context": {
            "current_slice": slice_id,
            "surface_role": current_role,
            "shared_shell": {
                "brand_title": brand_title,
                "navigation_links": nav_links
            }
        },
        "verification_command": verification_cmd,
        "capture_command": capture_cmd,
        "cognitive_ledger": cognitive_ledger,
        "fault_tolerance_protocol": fault_tolerance,
        "available_tokens": extract_css_tokens(paths["tokens_css"].read_text(encoding="utf-8")),
        "interaction_spec": interaction_spec,
        "design_constraints": constraints,
        "verifiable_assertions": assertions,
        "specification": {
            "path": spec_rel,
            "sha256": hashlib.sha256(paths["specification"].read_bytes()).hexdigest(),
        },
        "spec_references": {
            "product_thesis": paths["product"].relative_to(root).as_posix(),
            "surface_topology": paths["surface_map"].relative_to(root).as_posix(),
            "foundation_craft": paths["foundation"].relative_to(root).as_posix(),
            "slice_contract": paths["slice_contract"].relative_to(root).as_posix(),
            "specification": paths["specification"].relative_to(root).as_posix(),
            "tokens_stylesheet": paths["tokens_css"].relative_to(root).as_posix(),
        },
        "spec_sources": {
            "product_digest": hashlib.sha256(paths["product"].read_bytes()).hexdigest(),
            "surface_map_digest": hashlib.sha256(paths["surface_map"].read_bytes()).hexdigest(),
            "foundation_digest": hashlib.sha256(paths["foundation"].read_bytes()).hexdigest(),
            "tokens_css_digest": hashlib.sha256(paths["tokens_css"].read_bytes()).hexdigest(),
            "tokens_md_digest": hashlib.sha256(paths["tokens_md"].read_bytes()).hexdigest(),
            "contract_digest": hashlib.sha256(paths["slice_contract"].read_bytes()).hexdigest(),
            "specification_digest": hashlib.sha256(paths["specification"].read_bytes()).hexdigest(),
        }
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

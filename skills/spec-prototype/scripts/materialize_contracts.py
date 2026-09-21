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

try:
    import yaml
except ImportError:
    yaml = None

# Provenance placeholders. A projection seam may not declare a fixed domain claim
# ("Core Tension: X vs Y", borrowed reference, fixed shortcut) that no author wrote.
# Marked text is machine-detectable so it can never read as an authored decision.
UNSPECIFIED = "unspecified"
NOT_YET_DECIDED = "Not yet decided"
# A platform fact no source authored. Device class, input modality and target
# runtime are independent: `unknown` is a retained fact, never a placeholder
# the compiler is allowed to upgrade into a default OS.
UNKNOWN = "unknown"

# Contract keys that require an authored source in the discussion/product records.
# Missing source => key is omitted, never defaulted.
AUTHORED_PROJECTION_KEYS = ("core_tension",)


def extract_section_by_patterns(text: str, patterns: list[str]) -> str:
    """Extract markdown field or section matching any of the regex patterns, supporting bullets, tables, and headings."""
    for pat in patterns:
        m_field = re.search(
            rf"^\s*[-*+]?\s*[*_]*(?:{pat})[*_]*(?:\s*&[^\n:]*)?\s*[:=]\s*([^\n]+)",
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
            re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ""


def extract_dial_value(text: str, dial: str) -> str:
    """Extract a single 5-dial register value from inline `Dial: value` prose.

    Discussion records commonly state the five dials on one sensory-calibration
    line (`Density: sparse. Energy: quiet. ...`) that is neither a bullet field
    nor a table row, so the section extractor misses it. This reads the scalar
    token directly.
    """
    m = re.search(rf"\b{dial}\b\s*[:=]\s*([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _bullets(text: str) -> list[str]:
    return [re.sub(r"^[-*+]\s+", "", line).strip() for line in text.splitlines() if re.match(r"^[-*+]\s+", line)]


def extract_surface_id(raw: str) -> str:
    m_code = re.search(r"`([^`]+)`", raw)
    candidate = m_code.group(1) if m_code else raw
    candidate = re.sub(r"^(?:surfaces|experiments)/", "", candidate)
    candidate = candidate.split("/")[0] if "/hero-anchor" in candidate or "/anchor" in candidate else candidate
    m_ident = re.search(r"([a-zA-Z0-9_-]+)", candidate)
    if m_ident:
        return m_ident.group(1)
    return candidate.strip()


def extract_surfaces(disc_text: str, prod_text: str) -> tuple[list[str], list[str]]:
    """Extract declared surfaces supporting both English and Chinese heading conventions.
    Returns (clean_surface_ids, raw_declared_surfaces).
    """
    surface_ids: list[str] = []
    declared_surfaces: list[str] = []
    for line in (disc_text + "\n" + prod_text).splitlines():
        clean_line = line.strip()
        m_surf = re.match(r"^[-*+]\s+[*_]*(?:[-*+]\s+)?(?:Primary|Secondary|Supporting|Contextual|主工作区|次级|支撑|上下文)[^:]*:\s*(.+)$", clean_line, re.IGNORECASE)
        if m_surf:
            raw_entry = clean_line.lstrip("-*+ ")
            if raw_entry not in declared_surfaces:
                declared_surfaces.append(raw_entry)
            sid = extract_surface_id(m_surf.group(1))
            if sid and sid not in surface_ids:
                surface_ids.append(sid)
            continue
        if "|" in clean_line and any(kw in clean_line for kw in ("Primary:", "Secondary:", "Supporting:", "Contextual:", "主工作区:", "次级:", "支撑:", "上下文:")):
            parts = re.findall(r"(?:Primary|Secondary|Supporting|Contextual|主工作区|次级|支撑|上下文)[^:]*:\s*([^.|;\n]+)", clean_line, re.IGNORECASE)
            for part in parts:
                entry = part.strip()
                if entry and entry not in declared_surfaces:
                    declared_surfaces.append(entry)
                sid = extract_surface_id(entry)
                if sid and sid not in surface_ids:
                    surface_ids.append(sid)
            continue
        if re.search(r"\b(?:surfaces/|hero-anchor/|anchor/)[a-zA-Z0-9_-]+", clean_line):
            raw_entry = clean_line.lstrip("-*+ ")
            if raw_entry not in declared_surfaces:
                declared_surfaces.append(raw_entry)
            m_path = re.search(r"\b(?:surfaces/|hero-anchor/|anchor/)([a-zA-Z0-9_-]+)", clean_line)
            if m_path:
                sid = m_path.group(1)
                if sid and sid not in surface_ids:
                    surface_ids.append(sid)
            continue
    if not declared_surfaces:
        surfaces_sec = extract_section_by_patterns(disc_text, ["Surface", "表面", "拓扑", "Topology"]) or \
                       extract_section_by_patterns(prod_text, ["Surface", "表面", "拓扑", "Topology"])
        if surfaces_sec:
            for b in _bullets(surfaces_sec):
                if any(bad in b for bad in ("Rhythm", "Data Floor", "Action Verb", "Strict Token", "WCAG", "Contrast", "Token Inheritance")):
                    continue
                if b not in declared_surfaces:
                    declared_surfaces.append(b)
                sid = extract_surface_id(b)
                if sid and sid not in surface_ids:
                    surface_ids.append(sid)
    seen = set()
    cleaned_ids = []
    for s in surface_ids:
        if s not in seen and len(s) > 1:
            seen.add(s)
            cleaned_ids.append(s)
    return cleaned_ids, declared_surfaces


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
        # 2. Extract action mentions from text — candidate verbs explicitly marked as derived from authored context
        action_verb_patterns = [
            (r"(?:node\s+)?drain(?:\s+operations|\s+node)?", "drain-node", "Drain Node", "Drain GPU Node", "Confirm Drain", "Node Drained Successfully", "[Derived] Evicts active batch workload from node"),
            (r"preempt(?:\s+vram)?", "preempt-vram", "Preempt VRAM", "Preempt VRAM Allocation", "Execute Preempt", "VRAM Eviction Committed", "[Derived] Releases VRAM pool back to shared cluster"),
            (r"isolate(?:\s+cluster|\s+region)?", "isolate-cluster", "Isolate Cluster", "Emergency Region Isolation", "Authorize Isolation", "Region Traffic Rerouted", "[Derived] Isolates failing region to contain blast radius"),
            (r"bookmark(?:\s+story|\s+article)?", "bookmark-story", "Bookmark Story", "Save Bookmark", "Confirm Save", "Story Saved to Reading List", "[Derived] Stores story to reading list"),
            (r"checkout|order", "checkout-order", "Proceed to Checkout", "Confirm Order Payment", "Authorize Payment", "Order Placed Successfully", "[Derived] Initiates checkout and order confirmation"),
            (r"publish(?:\s+document)?", "publish-document", "Publish Document", "Confirm Publication", "Publish Now", "Document Published to Feed", "[Derived] Publishes document across designated channels"),
            (r"accept(?:\s+ai|\s+diff)?", "accept-ai-diff", "Accept AI Revision", "Review AI Inline Revision", "Accept & Merge", "Paragraph Revised Successfully", "[Derived] Merges AI revision into draft"),
            (r"(?:confirm\s+)?booking|reservation", "confirm-reservation-slot", "Confirm Time Slot", "Review Booking Details", "Confirm & Reserve", "Appointment Slot Confirmed", "[Derived] Confirms appointment booking"),
        ]
        for pattern, act_id, trig, modal, commit, toast, imp in action_verb_patterns:
            if re.search(pattern, disc_text, re.IGNORECASE):
                extracted.append({
                    "action_id": act_id,
                    "trigger_btn": trig,
                    "modal_header": modal,
                    "commit_btn": commit,
                    "toast": toast,
                    "impact": imp,
                })
                if len(extracted) >= 2:
                    break

    if not extracted:
        # Generic Grammar Extraction: parse bullet action declarations matching phrases
        action_declarations = re.findall(
            r"(?:[-*]\s*[`*]?([A-Za-z0-9一-龥\s_-]+)[`*]?\s*[:：]\s*([^\n]+))",
            disc_text
        )
        for name, desc in action_declarations:
            name_clean = name.strip()
            if any(k in name_clean.lower() for k in ("bg-", "accent-", "energy", "finish", "density", "weight", "seriousness", "palette", "domain", "http", "ruthless", "material")):
                continue
            if 2 < len(name_clean) < 32 and not name_clean.startswith("#"):
                slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name_clean).strip("-").lower()
                if not slug:
                    slug = f"action-{len(extracted)+1}"
                act_label = name_clean.title() if name_clean.isascii() else name_clean
                extracted.append({
                    "action_id": slug,
                    "trigger_btn": act_label,
                    "modal_header": f"Confirm {act_label}",
                    "commit_btn": f"Execute {act_label}",
                    "toast": f"{act_label} Completed",
                    "impact": desc.strip()[:100],
                })
                if len(extracted) >= 3:
                    break

    # Tertiary Fallback: Unresolved candidate hypothesis — explicitly marked as unvalidated hypothesis, never forged as frozen operational fact
    if not extracted:
        clean_slice = slice_id.replace("-", " ").title()
        action_id = f"explore-{slice_id}"
        extracted.append({
            "action_id": action_id,
            "trigger_btn": f"[Hypothesis] View {clean_slice}",
            "modal_header": f"[Hypothesis] Contextual Detail: {clean_slice}",
            "commit_btn": "Acknowledge",
            "toast": f"{clean_slice} Exploration Settled",
            "impact": f"[Hypothesis] Passive exploration view for {slice_id}; no authoritative state mutations authored. Requires explicit user specification before formal candidate build.",
        })
    return extracted


def extract_cognitive_ledger(disc_text: str, slice_id: str) -> dict[str, str]:
    """Extract the Cognitive Budgeting & Energy Return Ledger from authored truth only.

    Unauthored zones report ``unspecified`` instead of receiving synthesized
    prose the author never wrote (no tactical detents, micro-sparklines,
    kinetic pulses, or 10x situational-awareness claims).
    """
    routine_m = re.search(r"(?:Routine Conventions|Zero-learning|零借贷区|低熵基座)[`*:]*\s*([^\n]+)", disc_text, re.IGNORECASE)
    decisive_m = re.search(r"(?:Decisive Innovation|Borrowed focus|高产出借贷区|能量溢价特区)[`*:]*\s*([^\n]+)", disc_text, re.IGNORECASE)
    repayment_m = re.search(r"(?:Repayment|Settlement|偿还机制|状态沉降)[`*:]*\s*([^\n]+)", disc_text, re.IGNORECASE)

    unspecified = "unspecified"
    return {
        "zero_borrow_base": routine_m.group(1).strip() if routine_m else unspecified,
        "high_yield_borrow_zone": decisive_m.group(1).strip() if decisive_m else unspecified,
        "repayment_settlement": repayment_m.group(1).strip() if repayment_m else unspecified,
    }


def extract_ruthless_omissions(disc_text: str, prod_text: str) -> list[str]:
    """Extract domain-aware Ruthless Omissions from authored source truth only. Never inject hardcoded recipes."""
    combined = disc_text + "\n" + prod_text
    m = re.search(r"(?:Ruthless Omission|Deliberately Excluded|Omission|舍弃|排除|非目标)[^\n]*\n((?:[ \t]*[-*0-9.]+[^\n]+\n?)+)", combined, re.IGNORECASE)
    if m:
        items = [re.sub(r"^[ \t]*[-*0-9.]+\s*", "", line).strip() for line in m.group(1).splitlines() if line.strip()]
        if len(items) >= 1:
            return items[:5]
    return []


def extract_material_invariants(disc_text: str, prod_text: str) -> list[str]:
    """Extract Material Non-Transfer Boundaries from authored source truth only. Never inject hardcoded recipes."""
    combined = disc_text + "\n" + prod_text
    m = re.search(r"(?:Material Non-Transfer|Material Invariant|材质不可跨界|材质边界|物理映射)[^\n]*\n((?:[ \t]*[-*0-9.]+[^\n]+\n?)+)", combined, re.IGNORECASE)
    if m:
        items = [re.sub(r"^[ \t]*[-*0-9.]+\s*", "", line).strip() for line in m.group(1).splitlines() if line.strip()]
        if len(items) >= 1:
            return items[:5]
    return []


def extract_declared_invariants(disc_text: str, prod_text: str) -> list[str]:
    """Authored invariant tokens only. No universal baseline list is fabricated.

    An invariant reaches f1/r1 solely because the author wrote it. Absent an
    authored declaration the list stays empty, so downstream records carry no
    borrowed `concentric-radii` / `tabular-numerics` / `touch-target-floor` /
    `break-protocol` claim the author never made.
    """
    for text in (disc_text, prod_text):
        if not text:
            continue
        for pat in ("Experience Invariants", "Material Invariants", "Invariants", "Preserves"):
            m = re.search(
                rf"^\s*[-*+]?\s*[*_]*(?:{pat})[*_]*\s*[:=]\s*([^\n]+)",
                text, re.MULTILINE | re.IGNORECASE)
            if not m:
                continue
            items = [tok.strip().strip("`*_ ") for tok in re.split(r"[,;|、]", m.group(1))]
            items = [tok for tok in items if tok]
            if items:
                return items
    return []


def build_frontend_contract(
    slice_id: str,
    prod_title: str,
    tension: str,
    surfaces: list[str],
    action_verbs: list[dict[str, str]],
    disc_text: str,
    prod_text: str,
    disc_digest: str,
    prod_digest: str,
) -> str:
    """Project machine-readable frontend contract from approved design truth without inventing unauthored behavior."""
    combined = disc_text + "\n" + prod_text

    # 1. Structure / Surface Regions: Project declared surface topology only
    surface_regions = []
    if surfaces:
        for s in surfaces:
            clean_name = re.sub(r"[`*]", "", s).strip()
            sid = extract_surface_id(s)
            slug = sid if sid else re.sub(r"[^a-zA-Z0-9_-]+", "-", clean_name.lower()).strip("-")
            role = "main" if any(k in clean_name.lower() for k in ("primary", "主工作区", "hero-anchor")) else \
                   "complementary" if any(k in clean_name.lower() for k in ("contextual", "上下文", "drawer", "inspector")) else \
                   "region"
            surface_regions.append({
                "id": slug or "surface-region",
                "role": role,
                "declared_surface": clean_name,
            })

    # 2. Responsive Rules: Project authored responsive decisions; mark unspecified if absent
    responsive_section = extract_section_by_patterns(combined, ["Responsive", "响应式", "Breakpoints", "视口", "Touch-First Ergonomics", "Dual-Channel Ergonomics"])
    responsive_rules: dict[str, Any] = {}
    if responsive_section:
        m_desktop = re.search(r"(?:desktop|1280|桌面)[`*:]*\s*([^\n]+)", responsive_section, re.IGNORECASE)
        m_mobile = re.search(r"(?:mobile|390|320|移动|触控)[`*:]*\s*([^\n]+)", responsive_section, re.IGNORECASE)
        if m_desktop:
            responsive_rules["desktop"] = m_desktop.group(1).strip()
        if m_mobile:
            responsive_rules["mobile"] = m_mobile.group(1).strip()
        if not responsive_rules:
            summary_lines = [line.strip() for line in responsive_section.splitlines() if line.strip().startswith(("-", "*", "|"))]
            if summary_lines:
                responsive_rules["declared_summary"] = summary_lines[:4]
    if not responsive_rules:
        responsive_rules = {
            "status": "unspecified",
            "note": "No explicit responsive layout rules declared in approved design spec"
        }

    # 3. Finite State Machine: Project authored states; mark unspecified if absent
    state_section = extract_section_by_patterns(combined, ["State Machine", "状态机", "States", "状态流转", "State Matrix"])
    state_machine: dict[str, Any] = {}
    if state_section:
        declared_states = re.findall(r"[-*]\s*[`*]?([a-zA-Z0-9_-]+)[`*]?\s*[:：]\s*([^\n]+)", state_section)
        if declared_states:
            states_dict = {}
            for s_name, s_desc in declared_states:
                states_dict[s_name.lower()] = {"description": s_desc.strip()}
            state_machine = {
                "initial": list(states_dict.keys())[0] if states_dict else "unspecified",
                "states": states_dict,
            }
        else:
            summary_lines = [line.strip() for line in state_section.splitlines() if line.strip()]
            state_machine = {
                "status": "authored_summary",
                "raw": summary_lines[:5]
            }
    else:
        state_machine = {
            "status": "unspecified",
            "note": "No explicit finite state machine authored in approved design spec"
        }

    # 4. Interaction Verbs: Direct projection from authored Action Verb Lifecycle table
    actions_dict: dict[str, Any] = {}
    for v in action_verbs:
        act_id = v["action_id"]
        entry: dict[str, Any] = {
            "trigger_label": v["trigger_btn"],
            "modal_header": v["modal_header"],
            "commit_label": v["commit_btn"],
            "feedback_toast": v["toast"],
            "consequence": v["impact"],
        }
        # Copy authored hazard / reversibility without guessing from arbitrary keywords
        imp_lower = v["impact"].lower()
        if any(h in imp_lower for h in ("irreversible", "destructive", "high-hazard", "high hazard", "high reversibility cost")):
            entry["hazard_level"] = "high"
        elif any(h in imp_lower for h in ("reversible", "low-hazard", "low hazard", "passive")):
            entry["hazard_level"] = "low"
        actions_dict[act_id] = entry

    # 5. Experience Invariants: Project authored invariants
    invariants = []
    cp_section = extract_section_by_patterns(disc_text, ["Context Preservation", "上下文保持", "上下文连续"])
    if cp_section:
        for b in _bullets(cp_section):
            invariants.append(f"context_preservation: {b}")
    ft_section = extract_section_by_patterns(disc_text, ["Fault Tolerance", "容错与撤销", "The Break Protocol", "破坏性极限"])
    if ft_section:
        for b in _bullets(ft_section):
            invariants.append(f"resilience: {b}")

    # 6. Accessibility: Base standard + authored shortcuts
    a11y_contract: dict[str, Any] = {
        "wcag_level": "WCAG 2.2 AA",
        "min_contrast_ratio": 4.5,
    }
    dual_channel = extract_section_by_patterns(disc_text, ["Dual-Channel", "双通道", "Keyboard Shortcuts", "快捷键"])
    if dual_channel:
        shortcuts = []
        for line in dual_channel.splitlines():
            if line.strip().startswith("|") and not line.strip().startswith("|---"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and parts[0].lower() not in ("shortcut", "shortcut key", "key"):
                    shortcuts.append({"key": parts[0], "action": parts[1]})
        if shortcuts:
            a11y_contract["keyboard_shortcuts"] = shortcuts

    contract_data: dict[str, Any] = {
        "contract_version": "1.0",
        "authority_status": "sealed_provisional",
        "slice_id": slice_id,
        "provenance": {
            "product_title": prod_title,
            # Projection seam: an unauthored tension is omitted, not defaulted to a
            # domain claim. Consumers treat the absent key as an unknown optional fact.
            **({"core_tension": tension} if tension not in (NOT_YET_DECIDED, UNSPECIFIED) else {}),
            "spec_ref": f"prototype/specifications/{slice_id}/r1.md",
            "slice_contract_ref": f"prototype/contracts/slices/{slice_id}/c1.md",
            "tokens_json_ref": "prototype/contracts/tokens/t1.json",
            "tokens_css_ref": "prototype/shared/tokens.css",
            "discussion_digest": disc_digest,
            "product_digest": prod_digest,
        },
        "structure": {
            "root_element": f"main#{slice_id}-surface",
            "regions": surface_regions if surface_regions else [{"id": "unspecified", "role": "main"}],
        },
        "responsive_rules": responsive_rules,
        "state_machine": state_machine,
        "interaction_verbs": actions_dict,
        "experience_invariants": invariants,
        "accessibility_contract": a11y_contract,
        "tokens_binding": {
            "stylesheet": "prototype/shared/tokens.css",
            "json_spec": "prototype/contracts/tokens/t1.json",
        },
    }

    if yaml is not None:
        return yaml.dump(contract_data, sort_keys=False, allow_unicode=True)
    return json.dumps(contract_data, indent=2, ensure_ascii=False)


def materialize(root: Path, slice_id: str, force: bool = False, phase: str = "all") -> dict[str, str]:
    disc_path = root / "prototype/discussion.md"
    prod_path = root / "prototype/product.md"
    if not disc_path.is_file():
        raise FileNotFoundError(f"Missing mandatory entry index: {disc_path}")
    disc_text = disc_path.read_text(encoding="utf-8")

    created: dict[str, str] = {}

    content_lang = extract_section_by_patterns(disc_text, ["Content Language", "Language", "语种", "语言"])
    if not content_lang and prod_path.is_file():
        content_lang = extract_section_by_patterns(prod_path.read_text(encoding="utf-8"), ["Content Language", "Language", "语种", "语言"])
    if not content_lang:
        content_lang = "zh-CN" if re.search(r"[一-鿿]", disc_text) else "en-US"

    is_mobile_intent = bool(re.search(r"Baseline 4|Consumer|Mobile|Touch|Booking|移动|预约|触控", disc_text, re.IGNORECASE))
    # Platform truth is three independent facts. A device class or an input
    # modality never promotes itself into an operating-system target: a consumer
    # booking mention with a mobile viewport is exactly the case that used to
    # fabricate an iOS runtime. Only an authored target statement sets the OS;
    # without one it stays `unknown`.
    target_ctx = (extract_section_by_patterns(
        disc_text, ["Target OS", "Target Runtime", "Target Platform", "目标系统", "目标平台", "运行平台"]) or UNKNOWN).lower()
    device_ctx = (extract_section_by_patterns(
        disc_text, ["Device Class", "Device", "设备类型", "设备"]) or (
        "mobile" if is_mobile_intent else UNKNOWN)).lower()
    input_ctx = (extract_section_by_patterns(
        disc_text, ["Input Modality", "Input Context", "输入方式", "输入模态"]) or (
        "touch" if is_mobile_intent else UNKNOWN)).lower()

    # Support Phase 1 synthesis of product.md if missing or requested
    if not prod_path.is_file() or (force and phase.lower() in ("1", "product")):
        p_title = extract_section_by_patterns(disc_text, ["Product Title", "Product", "产品名称", "产品"]) or slice_id.replace("-", " ").title()
        # No inferred baseline, borrowed reference, tension or omission is synthesized here.
        # An absent authored field stays marked, never promoted to a domain claim.
        p_baseline = extract_section_by_patterns(disc_text, ["Baseline", "基准"]) or UNSPECIFIED
        p_anchors = extract_section_by_patterns(disc_text, ["Reality Anchors", "Anchors", "地锚", "对标"]) or UNSPECIFIED
        p_tension = extract_section_by_patterns(disc_text, ["Core Tension", "Tension", "张力", "冲突"]) or UNSPECIFIED
        omissions = extract_ruthless_omissions(disc_text, "")
        omissions_md = "\n".join(f"- {o}" for o in omissions) if omissions else f"- {UNSPECIFIED} (preserve standard convention boundaries)"
        prod_content = f"""# Product Thesis: {p_title}

- Dominant Baseline: {p_baseline}
- Reality Anchors: {p_anchors}
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
"""
        prod_path.parent.mkdir(parents=True, exist_ok=True)
        prod_path.write_text(prod_content, encoding="utf-8")
        created["product"] = str(prod_path)

    prod_text = prod_path.read_text(encoding="utf-8")
    product_title = next((line.lstrip("# ").strip() for line in prod_text.splitlines() if line.startswith("#")), "Product")
    tension = extract_section_by_patterns(prod_text, ["Core Tension", "Tension", "张力", "冲突"]) or \
              extract_section_by_patterns(disc_text, ["Core Tension", "Tension", "张力", "冲突"]) or \
              NOT_YET_DECIDED
    surfaces, declared_surfaces = extract_surfaces(disc_text, prod_text)
    action_verbs = extract_action_verbs(disc_text, slice_id)

    # Authored invariant tokens only. f1 and r1 context records used to mint a
    # universal baseline list (`concentric-radii, tabular-numerics,
    # touch-target-floor`, defaulting to `break-protocol`) that no author wrote.
    # The same list now feeds both records, and stays empty when unauthored.
    declared_invariants = extract_declared_invariants(disc_text, prod_text)
    invariants_str = ", ".join(declared_invariants)

    # The compiler states only universally true invariants. Category matching
    # (reading / marketing / mobile / writer-canvas / telemetry) used to synthesize
    # craft assertions -- SRE sparklines, touch floors, editorial columns -- from a
    # product's vocabulary, which promoted a domain guess into an authored claim.
    # Craft adequacy belongs to the authored specification and Builder reasoning,
    # never to a regex over words the author happened to use.
    contract_assertions = """| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| High text-to-background contrast compliant with WCAG 2.2 AA | present | unverified |
| Navigation and action affordances clear and reachable | present | unverified |
| Action Verb Lifecycle closure: trigger -> context/review -> commit -> settlement | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |"""

    targets = {
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
        "frontend_contract": root / f"prototype/contracts/slices/{slice_id}/frontend-contract.yaml",
    }

    phase_map = {
        "1": ["product"],
        "product": ["product"],
        "2": ["surface_map"],
        "surface_map": ["surface_map"],
        "3": ["foundation"],
        "foundation": ["foundation"],
        "4": ["slice_contract", "specification", "frontend_contract"],
        "slice": ["slice_contract", "specification", "frontend_contract"],
        "frontend": ["frontend_contract"],
        "all": ["product", "surface_map", "foundation", "slice_contract", "specification", "frontend_contract"],
    }
    active_keys = set(phase_map.get(phase.lower(), phase_map["all"]))

    for key, path in targets.items():
        if key not in active_keys:
            continue
        if path.is_file() and not force:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if key == "surface_map":
            surface_lines = "\n".join(f"- {s}" for s in declared_surfaces) if declared_surfaces else f"- {slice_id}"
            all_surfaces = list(surfaces) if surfaces else [slice_id]
            if slice_id not in all_surfaces:
                all_surfaces.append(slice_id)
            surfaces_str = ", ".join(all_surfaces)
            content = f"""# Product Surface Map: m1

- Product: {product_title}
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
"""
        elif key == "foundation":
            omissions = extract_ruthless_omissions(disc_text, prod_text)
            omissions_md = "\n".join(f"- {o}" for o in omissions) if omissions else "- Unspecified (no explicit omissions authored; preserve standard convention boundaries)"
            invariants = extract_material_invariants(disc_text, prod_text)
            invariants_md = "\n".join(f"- {inv}" for inv in invariants) if invariants else "- Unspecified (maintain semantic neutrality without forced material metaphors)"
            grounding_rat = extract_section_by_patterns(disc_text, ["Grounding", "Rationale", "Physical Metaphor", "Substrate", "原创推导", "物理隐喻", "因果依据", "设计理由"]) or \
                            extract_section_by_patterns(prod_text, ["Grounding", "Rationale", "Physical Metaphor", "Substrate", "原创推导", "物理隐喻", "因果依据", "设计理由"]) or \
                            UNSPECIFIED
            # Token-compiler inputs are carried onto the foundation record so
            # `compile_tokens.py` can read f1.md directly instead of re-parsing
            # the free-form discussion. Absent authored values stay marked.
            anchors_md = extract_section_by_patterns(disc_text, ["Reality Benchmark Anchors", "Reality Anchors", "Anchors", "地锚", "对标"]) or \
                         extract_section_by_patterns(prod_text, ["Reality Benchmark Anchors", "Reality Anchors", "Anchors", "地锚", "对标"]) or \
                         UNSPECIFIED
            seed_palette = extract_section_by_patterns(disc_text, ["Seed Palette", "Color Register", "Palette", "色板", "色彩寄存器"]) or \
                           extract_section_by_patterns(prod_text, ["Seed Palette", "Color Register", "Palette", "色板", "色彩寄存器"]) or \
                           UNSPECIFIED
            five_dials_md = "\n".join(
                f"- {dial}: {extract_dial_value(disc_text, dial) or extract_dial_value(prod_text, dial) or extract_section_by_patterns(disc_text, [dial]) or extract_section_by_patterns(prod_text, [dial]) or UNSPECIFIED}"
                for dial in ("Density", "Energy", "Materiality", "Rhythm", "Character")
            )
            content = f"""# Project Experience Foundation: f1

- Product: {product_title}
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Core tension: {tension}
- Grounding Rationale: {grounding_rat}
- Status: sealed provisional

```prototype-context
record: experience-foundation
revision: f1
invariants: {invariants_str}
```

## Product Context & Alignment
{re.sub(r"## 3 Ruthless Omissions.*", "", prod_text, flags=re.DOTALL).strip()}

## 3 Ruthless Omissions (克制舍弃清单)
{omissions_md}

## Material Non-Transfer Boundaries (材质不可跨界定律)
{invariants_md}

## 5-Dial Style Register (五刻度风格寄存器)
{five_dials_md}

## Reality Benchmark Anchors (现实基准锚点)
{anchors_md}

## Seed Palette / Color Register (种子色板 / 色彩寄存器)
{seed_palette}
"""
        elif key == "slice_contract":
            c_ledger = extract_cognitive_ledger(disc_text, slice_id)
            verb_table = "\n".join(
                f"| `{v['action_id']}` | `{v['trigger_btn']}` | `{v['modal_header']}` | `{v['commit_btn']}` | `{v['toast']}` | {v['impact']} |"
                for v in action_verbs
            )
            content = f"""# Prototype Slice Contract: {slice_id}

- Slice ID: {slice_id}
- Foundation revision: f1
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Content Language: {content_lang}
- Canonical Ontology: Nine Pillars Mapping (Object, Journey, Attention, Interaction, Resilience)
- Status: sealed provisional

## Intent & Value Anchor
{tension}

## Cognitive Budgeting & Energy Return Ledger (认知借贷收支账本)

| Ledger Zone | Scope & Interaction Invariant | Allocation Rule | Cognitive Cost & Yield |
|---|---|---|---|
| **Low-Entropy Base (零借贷基座)** | {c_ledger['zero_borrow_base']} | 0 learning friction, zero distracting motion, standard UI conventions | Zero cognitive drain; preserves operator attention for decisive tasks |
| **High-Yield Borrow Zone (能量溢价特区)** | {c_ledger['high_yield_borrow_zone']} | Elevated visual attention proportional to authored decisive work; only authored craft techniques apply | Borrowed visual energy restores decisiveness where the author allocated focused attention |
| **Settlement & Repayment (闭环偿还机制)** | {c_ledger['repayment_settlement']} | Focus and state settle smoothly to steady state | Restores baseline low entropy immediately after decision execution |

## Action Verb Lifecycle Table (4-Phase Atomic Terminology)

| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
{verb_table}

## Fault Tolerance & Error Recovery Contract (容错与撤销边界 · Experience Invariants)

| Operation Category | Hazard / Reversibility Level | Defensive Invariant | Recovery Path & Candidate Techniques |
|---|---|---|---|
| **Contextual Parameter / Filter** | Low / Fully Reversible | Optimistic live update, zero blocking modal | Instant reset via reset chip or `Esc` key |
| **Operational State Transition** | Medium / Conditionally Reversible | Reversibility Invariant: clear temporal recovery path | Candidate: Undo toast, history rollback, or status revert |
| **Destructive Resource Mutation** | High / Irreversible | Commit Safety Invariant: deliberate confirmation proportional to hazard | Candidate: Confirmation dialog, hold-to-confirm, or explicit review step |

## Decisive Exchange 3-Frame Specification (核心决定性交换三帧推演 · Experience Invariants)

- **Frame 1 (Intent Input)**: Operator activates target trigger via primary pointer or keyboard; contextual parameters reveal smoothly without layout shift.
- **Frame 2 (Decisive Commit)**: Operator commits action; trigger delivers immediate perceptible feedback (Candidate: tactile press, border shift, or luminance response); state locks to prevent duplicate submissions.
- **Frame 3 (State Settlement & Focus Restoration)**: Target badge transitions state deterministically; completion feedback displays; focus deterministically restores to originating anchor; indicators settle into baseline calm.

## Context Preservation Rules (上下文绝对保持法则)

- **Draft Context**: Dismissing inspector or drawer without submitting preserves filter parameters and active tab.
- **Spatial & Filter Context**: Scroll offsets and active facet filters remain strictly pinned upon drawer close or return.
"""
        elif key == "frontend_contract":
            content = build_frontend_contract(
                slice_id=slice_id,
                prod_title=product_title,
                tension=tension,
                surfaces=declared_surfaces,
                action_verbs=action_verbs,
                disc_text=disc_text,
                prod_text=prod_text,
                disc_digest=_digest(disc_path),
                prod_digest=_digest(prod_path),
            )
        else:
            scope_suffix = "hero-anchor" if "hero-anchor" in disc_text else "anchor"
            # Touch ergonomics follow an authored input-modality declaration, not a
            # vocabulary guess; absent that declaration the keyboard channel stands.
            if input_ctx == "touch":
                ergonomics_section = """## Touch-First Ergonomics (Gesture Detents & Haptic Recovery)

| Gesture Vector | Target Action / Interaction | Scope | Focus / State Settlement |
|---|---|---|---|
| `Tap` / `Press` | Direct manipulation of primary action trigger | Active card or action slot | Immediate perceptible feedback (e.g. tactile scale or highlight) |
| `Swipe Down` | Dismiss modal sheet / parameter drawer | Bottom sheet overlay | Restore viewport to originating card |
| `Edge Swipe` | Navigate back through prior step | Global screen edge | Settle immediately into previous step |"""
            else:
                ergonomics_section = """## Dual-Channel Ergonomics (Keyboard Shortcuts & Focus Recovery)

| Shortcut Key | Target Action / Interaction | Scope | Focus Restoration Anchor |
|---|---|---|---|
| `unspecified` | Activate primary action trigger / toggle inspector drawer | Active operational item or selection | Active selection anchor |
| `Esc` | Dismiss inspector drawer / modal | Global overlay | Restore focus to originating trigger |"""

            proto_med = "web"
            content = f"""# Prototype Specification: {slice_id} / r1

- Candidate revision: r1
- Compilation status: sealed provisional
- Authority status: sealed provisional
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Discussion source: `prototype/discussion.md`, {_digest(disc_path)}
- Content Language: {content_lang}
- Prototype write scope: `prototype/experiments/{slice_id}/{scope_suffix}/`
- Evidence write scope: `prototype/evidence/probes/{slice_id}/`
- Visual verification: unverified
- Browser verification: unverified

```prototype-context
record: prototype-specification
revision: r1
prototype-medium: {proto_med}
preserves: {invariants_str}
verification-environment: headless-browser
```

{ergonomics_section}

## The Break Protocol Stress Checkpoints (四维破坏性极限压测)

| Reality Breaker | Concrete Test Vector / Input | Expected Graceful Behavior | Observed Result |
|---|---|---|---|
| **Unbreakable String** | Domain-authentic extreme 45+ char title or compound path | CSS ellipsis / word-break + tooltip, zero container blowout, no artificial placeholder litter | `pending` |
| **Zero-Item Empty State** | Filter: 0 results / empty list | Actionable empty card with reset filter button | `pending` |
| **Extreme 320px Fold** | 320px viewport width test | Horizontal scroll or vertical reflow, primary action reachable | `pending` |
| **Rapid Interruption** | Double-click / rapid trigger activations | Debounced submission, single idempotency state transition | `pending` |

## Verifiable Design Assertions

{contract_assertions}
"""
        path.write_text(content, encoding="utf-8")
        created[key] = str(path)

    # Auto-synthesize baseline execution envelope for Builder
    try:
        from assemble_envelope import assemble
        env = assemble(root, slice_id)
        env_path = root / f"prototype/experiments/{slice_id}/envelope.json"
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(json.dumps(env, indent=2, ensure_ascii=False), encoding="utf-8")
        created["envelope"] = str(env_path)
    except Exception as exc:
        # Envelope synthesis is a best-effort side artifact; surface the cause so a
        # missing envelope is diagnosable rather than silently unexplained.
        print(
            f"warning: envelope assembly skipped for slice {slice_id!r}: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )

    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize generic Stage 1 contracts")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--slice", default="console")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--phase", default="all", help="Diamond Phase to materialize: 1 (product), 2 (surface_map), 3 (foundation), 4 (slice), or all")
    args = parser.parse_args()
    try:
        print(json.dumps({"status": "ok", "slice_id": args.slice, "phase": args.phase, "materialized": materialize(args.root.resolve(), args.slice, args.force, args.phase)}, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""compile_spec_ir.py: Canonical Prototype Specification IR Compiler.

Parses prototype/discussion.md (and/or upstream OpenSpec declarations) into a strict,
Schema-validated Canonical IR (`prototype/contracts/compiled/<slice_id>/<candidate_id>.spec.json`),
and deterministically renders the single-file human RFC Specification view
(`prototype/specifications/<slice_id>/<candidate_id>.spec.md`).

This replaces the 6-file scatter (product.md, m1.md, f1.md, t1.md, c1.md, r1.md)
and eliminates bidirectional/circular SHA-256 hash rebinding.

Machine authority layers (two distinct schemas with disjoint field sets; do not conflate them):
- Canonical Spec IR (`prototype-spec/v1`): `r1.spec.json` - schema-validated,
  discussion-derived, the single source of machine-truth spec content. Produced
  by this script.
- Executable Design IR: embedded inside `envelope.json` - produced by
  `assemble_envelope.py`, consumed by the Builder. Derived from the Canonical
  Spec IR and the legacy 6-piece contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import jsonschema
except ImportError:
    jsonschema = None


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas/prototype-spec.v1.json"


def sha256_text(text: str) -> str:
    """Compute sha256 digest of utf-8 text."""
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def sha256_file(path: Path) -> str:
    """Compute sha256 digest of a file if it exists, else empty."""
    if not path.is_file():
        return ""
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def parse_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML-like frontmatter if present at the start of markdown text."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end_idx = i
            break
    if end_idx == -1:
        return {}, text

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None

    for line in fm_lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue
        # List item under current_key
        if line_str.startswith("- ") and current_key:
            item = line_str[2:].strip().strip("\"'")
            try:
                item_val: Any = int(item)
            except ValueError:
                item_val = item
            if isinstance(data.get(current_key), list):
                data[current_key].append(item_val)
            else:
                data[current_key] = [item_val]
            continue
        # Key-value pair
        m = re.match(r"^([A-Za-z0-9_-]+)\s*[:：]\s*(.*)$", line_str)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            # Strip trailing comments e.g. # comment
            if " #" in val:
                val = val.split(" #", 1)[0].strip()
            current_key = key
            if not val:
                data[key] = []
            elif val.startswith("[") and val.endswith("]"):
                raw_items = [x.strip().strip("\"'") for x in val[1:-1].split(",") if x.strip()]
                converted = []
                for x in raw_items:
                    try:
                        converted.append(int(x))
                    except ValueError:
                        converted.append(x)
                data[key] = converted
            else:
                data[key] = val.strip("\"'")
    return data, body


# ATX heading grammar: 1-6 `#`, at least one space, optional closing `#` run.
_ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)(?:\s+#+)?\s*$")


def extract_section(text: str, heading_pattern: str, next_heading_pattern: Optional[str] = None) -> str:
    """Extract markdown body under `heading_pattern` until the next same-or-higher heading.

    Termination is layer-aware: the start heading's `#` level is detected, and
    capture stops at the first ATX heading whose level is <= that level. This
    admits `### 2. ...` after `### 1. ...` (the legacy literal `^##\\s+`
    terminator required whitespace after `##` and therefore never matched a
    `###` heading, so capture ran to EOF and swallowed sibling sections).

    `next_heading_pattern` is retained as an explicit literal override for
    callers/tests that pinned the old behavior; when omitted, the default is
    level-aware and never fabricates a captured body.
    """
    lines = text.splitlines()
    capturing = False
    start_level: Optional[int] = None
    captured: List[str] = []
    h_re = re.compile(heading_pattern, re.IGNORECASE)
    next_re = re.compile(next_heading_pattern) if next_heading_pattern else None

    for line in lines:
        heading_m = _ATX_HEADING_RE.match(line)
        if not capturing:
            # A start anchor is only admitted on a real ATX heading line; a
            # pattern hit inside body prose cannot establish a level and must
            # not open a section of unknowable extent.
            if heading_m and h_re.search(line):
                capturing = True
                start_level = len(heading_m.group(1))
            continue
        if next_re is not None:
            if next_re.match(line):
                break
            captured.append(line)
            continue
        # Level-aware default: stop at the first heading at or above the start.
        if heading_m and start_level is not None and len(heading_m.group(1)) <= start_level:
            break
        captured.append(line)
    return "\n".join(captured).strip()


# ---------------------------------------------------------------------------
# Stage-boundary contract: sections the compiler REQUIRES in discussion.md.
#
# `discussion.md` is the Stage 1 authority and contains no state taxonomy or
# device/viewport declarations. The state model (domain states, interaction
# states, data scenarios, break-protocol fixtures) and the mandatory test
# states belong to later stages, while the device/viewport fact belongs to the
# OOUX surface allocation. The compiler does NOT fabricate them and does NOT
# silently emit empty arrays that would freeze downstream as an unverifiable
# spec: it hard-fails, naming every missing item and the exact authored form.
#
# `heading`  : human-readable section anchor the author must add.
# `required` : violation tuple fields: key, section, markdown form, example.
# ---------------------------------------------------------------------------
_STATE_SECTION = "Stage 1 §3 (项目级状态模型)"
_SURFACES_SECTION = "Stage 1 §5 (OOUX 实体拓扑与表面分配)"

_REQUIRED_SECTIONS: List[Dict[str, Any]] = [
    {
        "key": "domain_states",
        "label": "领域状态 (domain_states)",
        "section": _STATE_SECTION,
        "form": "- `domain/<state-id>` (业务状态名称): 一句话语义描述",
        "example": "- `domain/cluster-nominal` (集群常态): 全部节点健康、张量流水线满负荷吞吐。",
    },
    {
        "key": "interaction_states",
        "label": "交互状态 (interaction_states)",
        "section": _STATE_SECTION,
        "form": "- `interaction/<state-id>`: 一句话语义描述",
        "example": "- `interaction/inspecting` (检视中): 操作者命中节点、抽屉展开、等待确认。",
    },
    {
        "key": "data_scenarios",
        "label": "数据场景 (data_scenarios)",
        "section": _STATE_SECTION,
        "form": "- `data/<scenario-id>`: 一句话语义描述",
        "example": "- `data/cold-tensor-cache` (冷张量缓存): 首次加载、缓存未命中、指标抖动。",
    },
    {
        "key": "stress_fixtures",
        "label": "破坏性压测夹具 (stress_fixtures)",
        "section": "Stage 1 §4 (破坏协议 / Break Protocol)",
        "form": "- `stress/<fixture-id>` | Vector: `破坏向量` | Expected: `期望恢复行为`",
        "example": "- `stress/nvlink-bus-hang` | Vector: `NVLink 链路挂起 6 秒` | Expected: `2 秒内定位故障节点并显示降级徽标`。",
    },
    {
        "key": "viewports",
        "label": "目标视口宽度 (viewports)",
        "section": f"{_SURFACES_SECTION} 或 Stage 1 §6 (Viewport / 设备视口)",
        "form": "- `Viewport`: `320px` / `1280px`；行内出现 `NNNpx` 即被采纳",
        "example": "- `Viewport`: `390px` (phone) / `1280px` (desktop)",
    },
    {
        "key": "required_states",
        "label": "强制测试状态 (required_states)",
        "section": f"{_SURFACES_SECTION} 或 Stage 1 §6 (Viewport / 设备视口)",
        "form": "- `Required States`: `state-a`, `state-b`（行内以反引号包裹 `state-*` 标记，至少一项）",
        "example": "- `Required States`: `state-draft`, `state-sealed`",
    },
]

# Progressive tier admission: `intent_spec` (Stage 1) requires only the problem
# thesis, topology, and five-axis/craft intent — no state machine. The five-axis
# register always derives defaults, so the gate items an author can actually
# miss are the thesis and the declared topology. `execution_spec` (Stage 3/4)
# keeps the full gate in `_REQUIRED_SECTIONS` above.
_INTENT_REQUIRED_SECTIONS: List[Dict[str, Any]] = [
    {
        "key": "core_tension",
        "label": "问题论点 (core_tension)",
        "section": "Stage 1 §1 (业务与用户极端张力)",
        "form": "- <张力 A> vs <张力 B>",
        "example": "- Operational through-put vs Catastrophic Bus-Hang Failures.",
    },
    {
        "key": "declared_surfaces",
        "label": "拓扑声明表面 (declared_surfaces)",
        "section": _SURFACES_SECTION,
        "form": "- **主工作区 (Primary)**: `surface/<id>`",
        "example": "- **主工作区 (Primary)**: `console/cluster-overview`",
    },
]


class IncompleteStageContractError(ValueError):
    """Raised when discussion.md omits fields the canonical IR requires non-empty.

    Subclasses `ValueError` so callers/tests that catch `ValueError` still work.
    Carries the structured violation list so the message stays actionable and a
    single raise reports every missing item at once.
    """

    def __init__(self, violations: List[Dict[str, str]], header: str = ""):
        self.violations = violations
        report = format_missing_sections(violations)
        super().__init__(f"{header}\n{report}" if header else report)


def format_missing_sections(violations: List[Dict[str, str]]) -> str:
    """Render an actionable, multi-item report of every missing required section."""
    parts = [
        "compile_spec_ir: discussion.md 缺少 Canonical IR 必备字段，编译中止。",
        f"发现 {len(violations)} 项缺失：",
    ]
    for index, item in enumerate(violations, start=1):
        parts.append(
            f"  [{index}] {item['key']} ({item['label']}) 未提取到。\n"
            f"      期望章节: {item['section']}\n"
            f"      声明格式: {item['form']}\n"
            f"      样例:     {item['example']}"
        )
    parts.append(
        "请补齐上述章节后重试；确需越过校验（仅限调试）请显式传入 `--allow-incomplete`。"
    )
    return "\n".join(parts)


def parse_5_dial_register(text: str) -> Dict[str, str]:
    """Extract 5-dial style register attributes."""
    dials = {
        "density": "balanced",
        "energy": "focused",
        "materiality": "subtle",
        "rhythm": "fluid",
        "character": "restrained",
    }
    # Look for `- \`?(\w+)\`?: \`?([^\`\n]+)\`?`
    for line in text.splitlines():
        m = re.search(r"[-*]\s*`?([A-Za-z]+)`?:\s*`?([^`\n]+)`?", line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().lower()
            if key in dials:
                dials[key] = val
            # Legacy dial aliases mirror compile_tokens.LEGACY_DIAL_MAP exactly;
            # the same key never maps to two different axes.
            elif key == "finish":
                dials["materiality"] = val
            elif key == "weight":
                dials["materiality"] = val
            elif key == "seriousness":
                dials["character"] = val
    return dials


# Leading modifiers that decorate an authored action verb inside prose, e.g.
# "`Space` 键瞬时检视" -> verb "检视". Stripped only to recover the verb itself.
_ACTION_MODIFIER_RE = re.compile(r"^(?:瞬时|机械压感|机械|压感|立即|快速|直接)+")


def parse_ruthless_omissions(text: str) -> List[str]:
    """Extract the authored 三大冷酷舍弃 (Ruthless Omissions) bullets.

    Previously this authority source was parsed by nothing in this compiler and
    silently dropped. Returns [] when the section is absent.
    """
    sec = extract_section(text, r"###?\s*.*(?:Ruthless\s+Omissions|冷酷舍弃|舍弃)")
    items: List[str] = []
    for line in sec.splitlines():
        m = re.match(r"^(?:\d+[.)]|[-*])\s+(.*\S)\s*$", line.strip())
        if m:
            items.append(m.group(1).strip())
    return items


def parse_action_verbs(text: str) -> List[Dict[str, Any]]:
    """Derive action verbs from authored key bindings, or emit nothing.

    An action is emitted only where discussion.md binds a named key to a verb
    (e.g. "`Space` 键瞬时检视", "`Enter` 键机械压感提交"). The verb text is taken
    from the source; nothing is invented when no binding exists. Entries carry
    authority=inferred so downstream reads them as derived, not authored fact.
    """
    actions: List[Dict[str, Any]] = []
    seen: set = set()
    for m in re.finditer(r"`([A-Za-z][A-Za-z0-9+]*)`\s*键([^、，,。;；\n]*)", text):
        key = m.group(1)
        verb = _ACTION_MODIFIER_RE.sub("", m.group(2).strip()).strip()
        if not verb or key in seen:
            continue
        seen.add(key)
        actions.append({
            "id": f"action-{key.lower()}",
            "verb": verb,
            "trigger": f"{key} key",
            "proximity_level": 1,
            "commit_action": verb,
            "authority": "inferred",
            "origin": "discussion.md",
        })
    return actions


def parse_viewports(text: str) -> List[int]:
    """Extract authored viewport widths (`NNNpx`) from discussion.md, else []."""
    out: List[int] = []
    for m in re.finditer(r"(?<!\d)(\d{3,4})\s*px", text):
        v = int(m.group(1))
        if 200 <= v <= 4000 and v not in out:
            out.append(v)
    return sorted(out)


def _split_label_description(rest: str, fallback_label: str):
    """Split text after a state token into (label, description).

    Recognizes the authored `(中文标签)` / `(label)` lead-in; when no parenthetical
    label exists the authored id token is used verbatim as the label (never an
    invented humanization).
    """
    rest = rest.strip().lstrip(":：-—").strip()
    m = re.match(r"[（(]([^）)]+)[）)]\s*[:：]?\s*(.*)", rest)
    if m:
        label = m.group(1).strip()
        description = m.group(2).strip()
    else:
        label = fallback_label
        description = rest
    return (label or fallback_label), description


def parse_domain_states(text: str) -> List[Dict[str, Any]]:
    """Extract authored domain states declared as `domain/<id>` bullets."""
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for line in text.splitlines():
        m = re.search(r"[`*]*(domain/[a-z0-9][a-z0-9_-]*)[`*]*(.*)$", line, re.IGNORECASE)
        if not m:
            continue
        sid = m.group(1).lower()
        if sid in seen:
            continue
        seen.add(sid)
        label, description = _split_label_description(m.group(2), sid.split("/", 1)[1])
        out.append({"id": sid, "label": label, "description": description})
    return out


def parse_interaction_states(text: str) -> List[str]:
    """Extract authored interaction states declared as `interaction/<id>` tokens."""
    out: List[str] = []
    seen: set = set()
    for m in re.finditer(r"[`*]*(interaction/[a-z0-9][a-z0-9_-]*)[`*]*", text, re.IGNORECASE):
        tok = m.group(1).lower()
        if tok in seen:
            continue
        seen.add(tok)
        out.append(tok)
    return out


def parse_data_scenarios(text: str) -> List[Dict[str, Any]]:
    """Extract authored data scenarios declared as `data/<id>` bullets."""
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for m in re.finditer(r"[`*]*(data/[a-z0-9][a-z0-9_-]*)[`*]*([^\n]*)", text, re.IGNORECASE):
        tok = m.group(1).lower()
        if tok in seen:
            continue
        seen.add(tok)
        _, description = _split_label_description(m.group(2), tok.split("/", 1)[1])
        out.append({"id": tok, "description": description})
    return out


def _capture_field(text: str, label_pattern: str) -> str:
    """Capture one `Label: value` field, terminating at `|`, `➔`, or EOL."""
    m = re.search(label_pattern + r"\s*[:：]\s*[`*]+([^`*\n]+)[`*]+", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(label_pattern + r"\s*[:：]\s*([^\n|➔]+)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def parse_stress_fixtures(text: str) -> List[Dict[str, Any]]:
    """Extract break-protocol fixtures declared as `stress/<id>` bullets.

    A fixture is admitted only when BOTH its destructive Vector and its
    Expected recovery behavior are authored; a token without them is not a
    usable fixture and must not be counted as satisfying the contract.
    """
    out: List[Dict[str, Any]] = []
    for line in text.splitlines():
        m = re.search(r"[`*]*(stress/[a-z0-9][a-z0-9_-]*)[`*]*(.*)$", line, re.IGNORECASE)
        if not m:
            continue
        fid = m.group(1).lower()
        rest = m.group(2)
        vector = _capture_field(rest, r"Vector")
        expected = _capture_field(rest, r"Expected(?:\s+Behavior)?")
        if not expected:
            m_arrow = re.search(r"(?:➔|->)\s*(?:Expected:?\s*)?[`*]*([^`*\n|]+)", rest, re.IGNORECASE)
            if m_arrow:
                expected = m_arrow.group(1).strip()
        if not vector or not expected:
            continue
        out.append({
            "id": fid,
            "vector": vector,
            "expected_behavior": expected,
        })
    return out


def parse_required_states(text: str) -> List[str]:
    """Extract mandatory test-state identifiers.

    Admitted from: an explicit `Required States` line (or `Mandatory Test States`),
    or any standalone backticked `state-*` token. Nothing is derived or defaulted.
    """
    out: List[str] = []
    seen: set = set()

    def _add(tok: str) -> None:
        clean = tok.strip().strip("`*\"'").lower()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)

    for m in re.finditer(r"(?:Required[ \t]+States?|Mandatory[ \t]+Test[ \t]+States?|强制测试状态)[ \t]*[:：]?[ \t]*([^\n]*)", text, re.IGNORECASE):
        for tok in re.findall(r"[`*]?([a-z0-9][a-z0-9_-]*)[`*]?", m.group(1), re.IGNORECASE):
            _add(tok)
    for tok in re.findall(r"[`*]?(state-[a-z0-9][a-z0-9_-]*)[`*]?", text, re.IGNORECASE):
        _add(tok)
    return out


def parse_craft_stack(text: str, five_axes: Dict[str, str]) -> Dict[str, str]:
    """Extract the orthogonal 4-axis craft stack from discussion text, or derive defaults.

    Authored `surface_optics: ...`-style bullets are taken verbatim (lowercased,
    first match wins per axis). Absent axes compile from physical anchors: a
    light or energy-restrained register reads as a matte pigment wash, otherwise
    a coated instrument dark; the remaining three axes default to the soft bento
    pill, tight polarized display, and hatching-dither data marks.
    """
    axes = ("surface_optics", "spatial_geometry", "micro_typography", "data_marks")
    stack: Dict[str, str] = {}
    for line in text.splitlines():
        m = re.search(r"[`*]*(surface_optics|spatial_geometry|micro_typography|data_marks)[`*]*\s*[:：]\s*[`*]*([^`\n]+)[`*]*", line, re.IGNORECASE)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().lower().rstrip("`* \t")
            if val and key not in stack:
                stack[key] = val

    if "surface_optics" not in stack:
        lowered = text.lower()
        if "light" in lowered or five_axes.get("energy") == "restrained":
            stack["surface_optics"] = "matte_pigment_wash"
        else:
            stack["surface_optics"] = "coated_instrument_dark"
    stack.setdefault("spatial_geometry", "soft_bento_pill")
    stack.setdefault("micro_typography", "tight_display_polarized")
    stack.setdefault("data_marks", "hatching_dither")
    # Deterministic axis order regardless of authored bullet order.
    return {axis: stack[axis] for axis in axes}


def parse_authored_invariants(text: str) -> List[Dict[str, Any]]:
    """Extract authored design invariants from discussion.md, or emit none.

    Invariants are admitted ONLY from an authored section (Design Invariants /
    设计不变式 / Design Rules). The former hardcoded telemetry/4096 template
    invariants were never authored facts and are retired: an unauthored
    discussion yields `[]`, never injected heuristics.

    Authored line form:
      - `inv/<id>` | <statement> | severity: blocking | verification: computed_style
    `severity` defaults to advisory and `verification` to manual; unknown
    severities fall back to advisory rather than fabricating an enum value.
    """
    sec = extract_section(text, r"###?\s*.*(?:Invariants|不变式|Design\s+Invariants|Design\s+Rules|设计规则|Resilience|Acceptance\s+Gates?)")
    out: List[Dict[str, Any]] = []
    severities = {"blocking", "warning", "advisory"}
    verifications = {"computed_style", "dom_query", "screenshot_review", "manual"}
    for line in sec.splitlines():
        m = re.match(r"^[-*]\s*[`*]*(inv/[^`*|:：\s]+)[`*]*\s*[|:：]\s*(.+)$", line.strip())
        if not m:
            continue
        inv_id = m.group(1).strip()
        parts = [p.strip() for p in m.group(2).split("|")]
        statement = parts[0] if parts else ""
        if not inv_id or not statement:
            continue
        severity = "advisory"
        verification = "manual"
        applies_to: List[str] = []
        for tail in parts[1:]:
            sm = re.match(r"severity\s*[:：]\s*(\w+)", tail, re.IGNORECASE)
            if sm and sm.group(1).lower() in severities:
                severity = sm.group(1).lower()
            vm = re.match(r"verif(?:ication|ication_method)?\s*[:：]\s*(\w+)", tail, re.IGNORECASE)
            if vm and vm.group(1).lower() in verifications:
                verification = vm.group(1).lower()
            am = re.match(r"applies_to\s*[:：]\s*(.+)", tail, re.IGNORECASE)
            if am:
                applies_to = [t.strip() for t in re.split(r"[,，、]", am.group(1)) if t.strip()]
        out.append({
            "id": inv_id,
            "upstream_ref": "discussion.md",
            "statement": statement,
            "severity": severity,
            "applies_to": applies_to,
            "verification_method": verification,
            "authority": "authored",
        })
    return out


def parse_meso_directives(text: str, navigation_topology: str) -> Dict[str, Dict[str, str]]:
    """Extract authored meso assembly slots from discussion.md.

    Slots: `layout_directives.massing_pattern` (information-topology construct),
    `interaction_spec.kinematics` (spatio-temporal continuity protocol),
    `visual_directives.data_syntax` (data micro-construct syntax). Authored
    `` `massing_pattern`: <value> ``-style bullets are taken verbatim; an
    undeclared massing smooths to a topology-derived fallback without blocking
    compilation. Kinematics and data_syntax are emitted only when authored.
    """
    authored: Dict[str, str] = {}
    for line in text.splitlines():
        m = re.search(
            r"[`*]*(massing_pattern|kinematics|data_syntax)[`*]*\s*[:：]\s*[`]*([^`\n]+)",
            line,
            re.IGNORECASE,
        )
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().lower().rstrip("`* \t")
            if val and key not in authored:
                authored[key] = val

    if "massing_pattern" in authored:
        massing = authored["massing_pattern"]
    elif navigation_topology == "workspace-inspector":
        massing = "canvas-inspector"
    else:
        massing = "stacked-flow"

    directives: Dict[str, Dict[str, str]] = {"layout_directives": {"massing_pattern": massing}}
    if "kinematics" in authored:
        directives["interaction_spec"] = {"kinematics": authored["kinematics"]}
    if "data_syntax" in authored:
        directives["visual_directives"] = {"data_syntax": authored["data_syntax"]}
    return directives


def compile_canonical_ir(
    root: Path,
    slice_id: str,
    candidate_id: str = "r1",
    contract_rev: str = "c1",
    authority_status: str = "sealed_provisional",
    stage: str = "hero_probe",
    selected_surfaces: Optional[List[str]] = None,
    viewports: Optional[List[int]] = None,
    allow_incomplete: bool = False,
    fragment_path: Optional[Path] = None,
    required_tier: str = "intent_spec",
) -> Dict[str, Any]:
    """Compile prototype/discussion.md into Canonical Specification IR."""
    disc_path = root / "prototype/discussion.md"
    disc_text = disc_path.read_text(encoding="utf-8") if disc_path.is_file() else ""
    disc_digest = sha256_text(disc_text) if disc_text else ""
    fm_data, body_text = parse_frontmatter(disc_text)

    # Optional Stage 3/4 incremental verification fragment overlay
    # (e.g. prototype/contracts/compiled/<slice>/state_model.slice.json or explicit path)
    frag_data = {}
    candidate_fragments = []
    if fragment_path:
        candidate_fragments.append(fragment_path)
    else:
        candidate_fragments.append(root / f"prototype/contracts/compiled/{slice_id}/state_model.slice.json")
        candidate_fragments.append(root / f"prototype/contracts/slices/{slice_id}/state_model.json")
    for fpath in candidate_fragments:
        if fpath and fpath.is_file():
            try:
                frag_data = json.loads(fpath.read_text(encoding="utf-8"))
                break
            except Exception:
                pass

    # Extract Product / Identity (Frontmatter title or Markdown header)
    if fm_data.get("title"):
        product_title = str(fm_data["title"]).strip()
    else:
        title_m = re.search(r"#\s*(?:Design\s*Discussion|Surface\s*Specification|Prototype\s*Specification):\s*([^\n]+)", disc_text, re.IGNORECASE)
        product_title = title_m.group(1).strip() if title_m else slice_id.replace("-", " ").title()
    product_id = re.sub(r"[^a-z0-9]+", "-", product_title.lower()).strip("-") or "product"

    # Frontmatter authority / stage overrides
    if authority_status == "sealed_provisional" and fm_data.get("authority"):
        authority_status = str(fm_data["authority"]).strip()
    if stage == "hero_probe" and fm_data.get("stage"):
        stage = str(fm_data["stage"]).strip()

    # Extract Core Tension
    tension_text = extract_section(disc_text, r"###?\s*.*(?:Core\s+Tension|Problem\s+Framing|Tension|业务与用户极端张力|极端张力|张力)")
    if not tension_text and fm_data.get("core_tension"):
        tension_text = str(fm_data["core_tension"]).strip()
    if not tension_text:
        m_tension = re.search(r"[-*]?\s*\**Core\s+Tension\**\s*[:：]\s*`?([^`\n]+)`?", disc_text, re.IGNORECASE)
        if m_tension:
            tension_text = m_tension.group(1).strip()
    # Absent authored tension stays None: never fabricate a domain claim that
    # would propagate downstream as a real constraint.
    if not tension_text:
        tension_text = None

    # Extract Reality Anchors
    anchors_text = extract_section(disc_text, r"###?\s*.*(?:Reality.*Anchors?|现实双地锚|地锚|Industry\s+Benchmarks?|Benchmarks?)")
    anchors = []
    for line in anchors_text.splitlines():
        line = line.strip()
        if line.startswith(("-", "*", "1.", "2.", "3.")):
            anchors.append(re.sub(r"^[-*0-9.]+\s*", "", line).strip())
    # No invented fallback: absent authored anchors stay empty and are omitted
    # from the IR, so downstream reads "undeclared" instead of a plausible lie.

    # Extract 三大冷酷舍弃 (Ruthless Omissions) - a real authority source that
    # previously had no parser and was silently discarded.
    ruthless_omissions = parse_ruthless_omissions(disc_text)

    # Extract 5-Dial Register
    style_text = extract_section(disc_text, r"###?\s*.*(?:5-Dial|风格寄存器|Style Register)")
    five_axes = parse_5_dial_register(style_text or disc_text)

    # Orthogonal 4-axis craft stack: authored declarations or physical-anchor defaults.
    craft_stack = parse_craft_stack(style_text or disc_text, five_axes)

    # Extract OOUX / Surfaces
    surfaces_text = extract_section(disc_text, r"###?\s*.*(?:OOUX|实体拓扑|Surfaces?|Spatial\s+Anatomy|Anatomy|表面分配)")
    declared_surfaces = []
    primary_surface = fm_data.get("primary_surface")
    for line in surfaces_text.splitlines():
        line = line.strip()
        # Skip meso layout constructs
        if re.search(r"[`*]*(massing_pattern|kinematics|data_syntax)[`*]*\s*[:：]", line, re.IGNORECASE):
            continue
        # Skip OOUX entity declarations unless explicitly naming a surface
        if re.search(r"[`*]*(?:ooux|entity\s+model|实体模型|实体拓扑)[`*]*\s*[:：]", line, re.IGNORECASE) and not re.search(r"(?:surface|console|reader|workspace)/", line, re.IGNORECASE):
            continue

        m_surf = re.search(r"(?:surfaces?|consoles?|readers?|workspaces?)/([a-zA-Z0-9_\-]+)", line, re.IGNORECASE)
        if not m_surf and re.search(r"(?:primary|contextual|supporting|glance|surfaces?|主|上下文|辅助|扫视|表面|工作区)", line, re.IGNORECASE):
            m_surf = re.search(r"`([a-zA-Z0-9_\-]+)`", line)
        if m_surf:
            s_name = Path(m_surf.group(1)).name
            if s_name not in declared_surfaces:
                declared_surfaces.append(s_name)
            if ("primary" in line.lower() or "主" in line) and not primary_surface:
                primary_surface = s_name

    if fm_data.get("declared_surfaces") and isinstance(fm_data["declared_surfaces"], list):
        for s in fm_data["declared_surfaces"]:
            s_name = Path(str(s)).name
            if s_name not in declared_surfaces:
                declared_surfaces.append(s_name)

    if not declared_surfaces:
        # No fabricated "inspector"/"telemetry" surfaces: an undeclared topology
        # stays empty and is surfaced as such downstream.
        declared_surfaces = []
    if not primary_surface and declared_surfaces:
        primary_surface = declared_surfaces[0]

    # Build Scope vs Topology Scope separation.
    if selected_surfaces:
        active_build_surfaces = selected_surfaces
    elif stage in ("hero_probe", "surface_slice"):
        # In the absence of any declared surface there is nothing to select.
        active_build_surfaces = [primary_surface] if primary_surface else []
    else:
        active_build_surfaces = declared_surfaces

    context_surfaces = [s for s in declared_surfaces if s not in active_build_surfaces]

    # State Model — extracted strictly from authored tokens in discussion.md
    # or merged from an explicit Stage 3/4 verification fragment (state_model.slice.json).
    # No template value is injected: a missing taxonomy is a hard failure below,
    # not a silent empty array that would freeze downstream as unverifiable.
    domain_states = frag_data.get("domain_states") or parse_domain_states(disc_text)
    interaction_states = frag_data.get("interaction_states") or parse_interaction_states(disc_text)
    data_scenarios = frag_data.get("data_scenarios") or parse_data_scenarios(disc_text)
    stress_fixtures = frag_data.get("stress_fixtures") or parse_stress_fixtures(disc_text)

    # Invariants: ONLY discussion/Spec-authored invariants reach the IR. The
    # former hardcoded telemetry/4096 GPU template entries were injected
    # heuristics with no authored source and are retired: an unauthored
    # discussion emits `[]`, never a template.
    invariants = parse_authored_invariants(disc_text)

    # Actions: derived strictly from authored key bindings in discussion.md.
    # The former hardcoded "检视实体"/"确定隔离排空" verbs were never extracted from
    # the source and are removed; when no binding exists, actions stays empty.
    actions = parse_action_verbs(disc_text)

    # Meso assembly slots: authored massing/kinematics/data_syntax declarations,
    # with an undeclared massing smoothing to a topology-derived fallback.
    meso = parse_meso_directives(disc_text, "workspace-inspector")

    # Progressive tier stamping: the IR emits the tier it can legitimately
    # derive. A full state machine AND action contracts present (authored here
    # or merged from a Stage 3/4 fragment) earn `execution_spec`; otherwise the
    # Stage 1 `intent_spec` tier is stamped.
    has_state_machine = bool(
        domain_states and interaction_states and data_scenarios and stress_fixtures
    )
    has_action_contracts = bool(actions)
    spec_tier = "execution_spec" if (has_state_machine and has_action_contracts) else "intent_spec"

    fm_vps = fm_data.get("viewports")
    resolved_fm_vps = [int(v) for v in fm_vps if str(v).isdigit()] if (fm_vps and isinstance(fm_vps, list)) else []
    resolved_vps = list(viewports) if viewports else (frag_data.get("viewports") or (resolved_fm_vps if resolved_fm_vps else parse_viewports(disc_text)))

    fm_states = fm_data.get("required_states")
    resolved_fm_states = [str(s).strip() for s in fm_states if str(s).strip()] if (fm_states and isinstance(fm_states, list)) else []
    resolved_req_states = frag_data.get("required_states") or (resolved_fm_states if resolved_fm_states else parse_required_states(disc_text))

    ir = {
        "schema_version": "prototype-spec/v1",
        "spec_tier": spec_tier,
        "identity": {
            "product_id": product_id,
            "slice_id": slice_id,
            "contract_revision": contract_rev,
            "candidate_revision": candidate_id,
            "authority_status": authority_status,
            "title": product_title,
        },
        "sources": {
            "discussion_ref": "prototype/discussion.md",
            "discussion_sha256": disc_digest,
            # discussion.md carries no requirement/scenario taxonomy: emit none
            # rather than fabricate REQ-*/SCN-* identifiers downstream could treat
            # as traced upstream authority.
            "requirements": [],
            "reality_anchors": anchors,
            "core_tension": tension_text,
            "ruthless_omissions": ruthless_omissions,
        },
        "scope": {
            "topology_scope": {
                "coverage": "key-journey" if len(declared_surfaces) > 1 else "slice-isolated",
                "declared_surfaces": declared_surfaces,
                # Omit when undeclared: schema types primary_surface as string,
                # and a null would falsely imply an authored primary surface.
                **({"primary_surface": primary_surface} if primary_surface else {}),
                "navigation_topology": "workspace-inspector",
            },
            "build_scope": {
                "stage": stage,
                "selected_surfaces": active_build_surfaces,
                "context_surfaces": context_surfaces,
            },
            "verification_scope": {
                # Authored viewports win; otherwise fragment viewports, then widths parsed from
                # discussion.md. No fabricated device set.
                "viewports": resolved_vps,
                # Mandatory test states, parsed from authored declarations or fragment.
                "required_states": resolved_req_states,
            },
        },
        "foundation": {
            "five_axes": five_axes,
            "craft_stack": craft_stack,
            "palette_discipline": {
                "accent_seal": "var(--accent-seal, #D93829)",
                "accent_policy": "Forbidden in draft/pending states; reserved exclusively for irreversible authority seals.",
            },
        },
        "state_model": {
            "domain_states": domain_states,
            "interaction_states": interaction_states,
            "data_scenarios": data_scenarios,
            "stress_fixtures": stress_fixtures,
        },
        "actions": actions,
        "invariants": invariants,
        **meso,
        "artifacts_binding": {
            "tokens_css": "prototype/shared/tokens.css",
            "tokens_json": "prototype/contracts/tokens/t1.json",
            "human_spec_md": f"prototype/specifications/{slice_id}/{candidate_id}.spec.md",
            "prototype_html": f"prototype/experiments/{slice_id}/{candidate_id}/index.html",
        },
    }

    # Stage-boundary hard gate: enumerate EVERY non-empty contract the authored
    # discussion.md failed to supply. Verification scope is authored, so an
    # explicit --viewports override also satisfies the viewport contract.
    extracted: Dict[str, Any] = {
        "domain_states": domain_states,
        "interaction_states": interaction_states,
        "data_scenarios": data_scenarios,
        "stress_fixtures": stress_fixtures,
        "viewports": ir["scope"]["verification_scope"]["viewports"],
        "required_states": ir["scope"]["verification_scope"]["required_states"],
    }
    violations = [
        {"key": spec["key"], "label": spec["label"], "section": spec["section"],
         "form": spec["form"], "example": spec["example"]}
        for spec in _REQUIRED_SECTIONS
        if not extracted.get(spec["key"])
    ]
    intent_extracted: Dict[str, Any] = {
        "core_tension": tension_text,
        "declared_surfaces": declared_surfaces,
    }
    intent_violations = [
        {"key": spec["key"], "label": spec["label"], "section": spec["section"],
         "form": spec["form"], "example": spec["example"]}
        for spec in _INTENT_REQUIRED_SECTIONS
        if not intent_extracted.get(spec["key"])
    ]
    if violations and intent_violations:
        # Not even the Stage 1 intent tier is satisfiable: report everything.
        report = format_missing_sections(violations + intent_violations)
        if not allow_incomplete:
            raise IncompleteStageContractError(violations + intent_violations)
        sys.stderr.write(
            "WARNING: --allow-incomplete 已启用，跳过阶段边界校验。\n"
            "以下必备字段在 discussion.md 中缺失，产出的 IR 不合规且可能无法通过 schema：\n"
            f"{report}\n"
        )
    elif violations:
        # Stage 1 intent_spec admission passes with only the Stage 1 gate
        # active: missing later-stage state taxonomy stays a downstream
        # requirement, not a compilation blocker at this tier.
        report = format_missing_sections(violations)
        if spec_tier != "execution_spec":
            sys.stderr.write(
                "NOTE: 以下 execution_spec (Stage 3/4) 字段在 discussion.md 中缺失，"
                "本编译产物为 intent_spec 层级：\n"
                f"{report}\n"
            )
        elif not allow_incomplete:
            raise IncompleteStageContractError(violations)
        else:
            sys.stderr.write(
                "WARNING: --allow-incomplete 已启用，跳过阶段边界校验。\n"
                f"{report}\n"
            )

    # Validate against schema if jsonschema is available. A known-incomplete IR
    # (explicit --allow-incomplete) already violates minItems by definition, so
    # schema validation is skipped in that debug path only.
    if jsonschema and SCHEMA_PATH.is_file() and not (violations and allow_incomplete):
        schema_obj = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(instance=ir, schema=schema_obj)

    # Tier admission boundary: a consumer requiring `execution_spec` refuses a
    # Stage-1-only IR with the missing-state message instead of admitting it.
    if required_tier == "execution_spec" and spec_tier != "execution_spec":
        missing = format_missing_sections(violations) if violations else \
            "state_model (domain_states / interaction_states / data_scenarios / stress_fixtures) 或 actions 缺失"
        raise IncompleteStageContractError(
            violations
            or [{"key": "state_model", "label": "执行层级状态机 (state_model)",
                 "section": "Stage 3/4 (状态机与动作契约)",
                 "form": "完整的 domain/interaction/data/stress 状态模型与 action 契约",
                 "example": "- `domain/<state-id>` (业务状态名称): 一句话语义描述"}],
            header=f"execution_spec 层级不可达成：当前 discussion.md 仅满足 intent_spec。\n{missing}",
        )

    return ir


def render_single_spec_md(ir: Dict[str, Any]) -> str:
    """Render Canonical IR into a unified, human-readable single-file RFC Specification."""
    ident = ir["identity"]
    src = ir["sources"]
    scope = ir["scope"]
    fnd = ir["foundation"]
    states = ir.get("state_model") or {
        "domain_states": [], "interaction_states": [], "data_scenarios": [], "stress_fixtures": [],
    }

    md = []
    md.append(f"# Prototype Specification: {ident['title']} ({ident['slice_id']}/{ident['candidate_revision']})")
    md.append("")
    md.append(f"> **Authority Status**: `{ident['authority_status'].upper()}` | **Revision**: `{ident['contract_revision']}` / `{ident['candidate_revision']}` | **Spec Tier**: `{ir.get('spec_tier', 'execution_spec')}`")
    md.append(f"> **Source Reference**: `{src['discussion_ref']}` ({src.get('discussion_sha256', 'untracked')})")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Product & Architecture Context (Pillars: Value · Research)")
    md.append(f"- **Product ID**: `{ident['product_id']}`")
    if src.get("core_tension"):
        md.append(f"- **Core Tension**: {src['core_tension']}")
    else:
        md.append("- **Core Tension**: *(未从 discussion.md 提取到——请在 discussion 中明确描述核心张力)*")
    md.append("- **Reality Anchors**:")
    if src["reality_anchors"]:
        for a in src["reality_anchors"]:
            md.append(f"  - {a}")
    else:
        md.append("  - _None declared in discussion.md._")
    if src.get("ruthless_omissions"):
        md.append("- **Ruthless Omissions**:")
        for om in src["ruthless_omissions"]:
            md.append(f"  - {om}")
    md.append("")
    md.append("### Topology & IA Scope (Pillars: Object · Topology)")
    md.append(f"- **Coverage Mode**: `{scope['topology_scope']['coverage']}`")
    md.append(f"- **Navigation Topology**: `{scope['topology_scope']['navigation_topology']}`")
    md.append(f"- **Primary Surface**: `{scope['topology_scope'].get('primary_surface') or '_None declared_'}`")
    declared_str = ", ".join(f"`{s}`" for s in scope['topology_scope']['declared_surfaces'])
    md.append(f"- **Declared Surfaces**: {declared_str or '_None declared_'}")
    md.append(f"- **Active Build Stage**: `{scope['build_scope']['stage']}`")
    build_str = ", ".join(f"`{s}`" for s in scope['build_scope']['selected_surfaces'])
    md.append(f"- **Active Build Surfaces**: {build_str or '_None declared_'}")
    if scope['build_scope']['context_surfaces']:
        md.append(f"- **Context Surfaces**: {', '.join(f'`{s}`' for s in scope['build_scope']['context_surfaces'])}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Sensory Calibration & Token Discipline (Pillars: Expression · Attention · 5-Axes)")
    md.append("- **Five-Axis Sensory Register**:")
    for k, v in fnd["five_axes"].items():
        md.append(f"  - `{k}`: `{v}`")
    md.append(f"- **Signature Accent Policy**: {fnd['palette_discipline'].get('accent_policy', 'Strict')}")
    md.append("- **Orthogonal Craft Stack**:")
    for k, v in (fnd.get("craft_stack") or {}).items():
        md.append(f"  - `{k}`: `{v}`")
    md.append(f"- **Tokens Stylesheet**: `{ir['artifacts_binding']['tokens_css']}`")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. State Models & Action Lifecycle (Pillars: Journey · Interaction)")
    md.append("### Domain States")
    if states["domain_states"]:
        for ds in states["domain_states"]:
            md.append(f"- `{ds['id']}` ({ds['label']}): {ds.get('description', '')}")
    else:
        md.append("_None declared in discussion.md._")
    md.append("")
    interaction = ", ".join(f"`{s}`" for s in states["interaction_states"])
    md.append(f"### Interaction States: {interaction or '_None declared_' }")
    md.append("")
    md.append("### Actions Matrix")
    md.append("| Action ID | Verb | Trigger | Proximity | Commit Consequence | Feedback |")
    md.append("|---|---|---|---|---|---|")
    if ir["actions"]:
        for act in ir["actions"]:
            md.append(
                f"| `{act['id']}` | {act['verb']} | `{act.get('trigger', '')}` | L{act.get('proximity_level', 1)} | "
                f"{act.get('consequence', '')} | {act.get('feedback', '')} |"
            )
    else:
        md.append("_No authored actions declared in discussion.md._")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 4. Verifiable Design Invariants & Break Protocol (Pillar: Resilience)")
    md.append("### Verifiable Assertions")
    for inv in ir["invariants"]:
        md.append(f"- **[{inv['id']}]** (`{inv['severity']}` · `{inv['verification_method']}`): {inv['statement']}")
        md.append(f"  - Applies to states: {', '.join(f'`{s}`' for s in inv.get('applies_to', []))}")
    md.append("")
    md.append("### Break Protocol Stress Fixtures")
    if states["stress_fixtures"]:
        for sf in states["stress_fixtures"]:
            md.append(f"- **`{sf['id']}`**: Vector: `{sf['vector']}` ➔ Expected: *{sf['expected_behavior']}*")
    else:
        md.append("_None declared in discussion.md._")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 5. Verification Scope & Evidence Binding")
    vscope = scope["verification_scope"]
    viewports_str = ", ".join(f"{vp}px" for vp in vscope["viewports"])
    md.append(f"- **Target Viewports**: {viewports_str or '_None declared_'}")
    states_str = ", ".join(f"`{st}`" for st in vscope["required_states"])
    md.append(f"- **Mandatory Test States**: {states_str or '_None declared_'}")
    md.append(f"- **Prototype Implementation**: `{ir['artifacts_binding']['prototype_html']}`")
    proto_html = ir["artifacts_binding"]["prototype_html"]
    proto_scope = str(Path(proto_html).parent) + "/"
    evidence_scope = f"prototype/evidence/{ident['slice_id']}/{ident['candidate_revision']}/"
    md.append(f"- **Prototype write scope**: `{proto_scope}`")
    md.append(f"- **Evidence write scope**: `{evidence_scope}`")
    md.append(f"- **Authority status**: `{ident['authority_status']}`")
    md.append("")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="Compile canonical prototype specification IR and single-file spec view.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--slice", required=True, help="Slice identifier (e.g. sample-gate)")
    parser.add_argument("--candidate", default="r1", help="Candidate revision (e.g. r1)")
    parser.add_argument("--contract", default="c1", help="Contract revision (e.g. c1)")
    parser.add_argument("--status", default="sealed_provisional", choices=["draft", "sealed_provisional", "validated", "frozen_approved"])
    parser.add_argument("--stage", default="hero_probe", choices=["hero_probe", "walking_skeleton", "surface_slice", "full_product"])
    parser.add_argument("--surfaces", nargs="*", help="Override build scope surfaces")
    parser.add_argument("--viewports", nargs="*", type=int, help="Override authored verification viewports (px)")
    parser.add_argument("--output-ir", help="Output JSON IR path (default: prototype/contracts/compiled/<slice>/<cand>.spec.json)")
    parser.add_argument("--output-md", help="Output markdown path (default: prototype/specifications/<slice>/<cand>.spec.md)")
    parser.add_argument("--fragment", help="Optional Stage 3/4 verification JSON fragment path (default: prototype/contracts/compiled/<slice>/state_model.slice.json)")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="DEBUG ONLY: skip the stage-boundary completeness gate and emit IR with missing required sections (default: fail).",
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()

    try:
        ir = compile_canonical_ir(
            root=root,
            slice_id=args.slice,
            candidate_id=args.candidate,
            contract_rev=args.contract,
            authority_status=args.status,
            stage=args.stage,
            selected_surfaces=args.surfaces,
            viewports=args.viewports,
            allow_incomplete=args.allow_incomplete,
            fragment_path=Path(args.fragment).resolve() if args.fragment else None,
        )
    except IncompleteStageContractError as exc:
        sys.stderr.write(f"{exc}\n")
        raise SystemExit(2)

    out_ir = Path(args.output_ir) if args.output_ir else root / f"prototype/contracts/compiled/{args.slice}/{args.candidate}.spec.json"
    out_md = Path(args.output_md) if args.output_md else root / f"prototype/specifications/{args.slice}/{args.candidate}.spec.md"

    out_ir.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_ir.write_text(json.dumps(ir, indent=2, ensure_ascii=False), encoding="utf-8")
    rendered_md = render_single_spec_md(ir)
    out_md.write_text(rendered_md, encoding="utf-8")

    print(f"Compiled Canonical Spec IR: {out_ir}")
    print(f"Rendered Unified Spec MD: {out_md}")


if __name__ == "__main__":
    main()

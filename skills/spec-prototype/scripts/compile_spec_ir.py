#!/usr/bin/env python3
"""compile_spec_ir.py: Canonical Prototype Specification IR Compiler.

Parses prototype/discussion.md (and/or upstream OpenSpec declarations) into a strict,
Schema-validated Canonical IR (`prototype/contracts/compiled/<slice_id>/<candidate_id>.spec.json`),
and deterministically renders the single-file human RFC Specification view
(`prototype/specifications/<slice_id>/<candidate_id>.spec.md`).

This replaced the 6-file scatter (product.md, m1.md, f1.md, t1.md, c1.md, r1.md)
and eliminated bidirectional/circular SHA-256 hash rebinding. Those files are now
legacy inputs only: readable when a tree predates the canonical IR, never
generated, and never bound back in once this compiler has run.

Machine authority layers (two distinct schemas with disjoint field sets; do not conflate them):
- Canonical Spec IR (`prototype-spec/v1`): `r1.spec.json` - schema-validated,
  discussion-derived, the single source of machine-truth spec content. Produced
  by this script.
- Executable Design IR: embedded inside `envelope.json` - produced by
  `assemble_envelope.py`, consumed by the Builder. Projected from the Canonical
  Spec IR when it exists; the legacy pillar parse remains only as the fallback
  for a tree that has no canonical IR yet.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except ImportError:  # structured contract blocks require the authoritative YAML parser
    yaml = None

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
#
# `form` names the authoritative ```contract:<kind>``` block first and the prose
# fallback second. The block is what an author should write; the prose form is
# the compatibility route for a record that predates it, and it is the route
# with the silent-mis-parse history, so it is never the recommended one.
# ---------------------------------------------------------------------------
_STATE_SECTION = "Stage 1 §3 (项目级状态模型)"
_SURFACES_SECTION = "Stage 1 §5 (OOUX 实体拓扑与表面分配)"
_SURFACES_HEADING = r"###?\s*.*(?:OOUX|实体拓扑|Surfaces?|Spatial\s+Anatomy|Anatomy|表面分配)"

_REQUIRED_SECTIONS: List[Dict[str, Any]] = [
    {
        "key": "domain_states",
        "label": "领域状态 (domain_states)",
        "section": _STATE_SECTION,
        "form": "```contract:states``` → `- id: domain/<state-id>` + `description:`（回退散文形：`- `domain/<state-id>` (业务状态名称): 一句话语义描述`）",
        "example": "- `domain/cluster-nominal` (集群常态): 全部节点健康、张量流水线满负荷吞吐。",
    },
    {
        "key": "interaction_states",
        "label": "交互状态 (interaction_states)",
        "section": _STATE_SECTION,
        "form": "```contract:states``` → `- id: interaction/<state-id>` + `description:`（回退散文形：`- `interaction/<state-id>`: 一句话语义描述`）",
        "example": "- `interaction/inspecting` (检视中): 操作者命中节点、抽屉展开、等待确认。",
    },
    {
        "key": "data_scenarios",
        "label": "数据场景 (data_scenarios)",
        "section": _STATE_SECTION,
        "form": "```contract:states``` → `- id: data/<scenario-id>` + `description:`（回退散文形：`- `data/<scenario-id>`: 一句话语义描述`）",
        "example": "- `data/cold-tensor-cache` (冷张量缓存): 首次加载、缓存未命中、指标抖动。",
    },
    {
        "key": "stress_fixtures",
        "label": "破坏性压测夹具 (stress_fixtures)",
        "section": "Stage 1 §4 (破坏协议 / Break Protocol)",
        "form": "```contract:stress``` → `- id: stress/<fixture-id>` + `vector:` + `expected:`（回退散文形：`- `stress/<fixture-id>` | Vector: `破坏向量` | Expected: `期望恢复行为``）",
        "example": "- `stress/nvlink-bus-hang` | Vector: `NVLink 链路挂起 6 秒` | Expected: `2 秒内定位故障节点并显示降级徽标`。",
    },
    {
        "key": "viewports",
        "label": "目标视口宽度 (viewports)",
        "section": f"{_SURFACES_SECTION} 或 Stage 1 §6 (Viewport / 设备视口)",
        "form": "```contract:viewports``` → `- 390` / `- \"1280px\"`（回退散文形：`- `Viewport`: `320px` / `1280px``，行内出现 `NNNpx` 即被采纳）",
        "example": "- `Viewport`: `390px` (phone) / `1280px` (desktop)",
    },
    {
        "key": "required_states",
        "label": "强制测试状态 (required_states)",
        "section": f"{_SURFACES_SECTION} 或 Stage 1 §6 (Viewport / 设备视口)",
        "form": "```contract:required_states``` → `- state-a`（回退散文形：`- `Required States`: `state-a`, `state-b``）",
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


def _misplaced_in_shared(shared_text: Optional[str], slice_id: str,
                         violations: List[Dict[str, str]]) -> None:
    """Annotate a missing slice-scoped contract that sits outside its slice block.

    Viewports, required states and declared surfaces are read from the slice block
    alone. A record that wrote them above the `## Slice:` heading did not omit
    them; it placed them in the shared zone, and "请补齐" would send the author to
    re-write what is already there. Report the position, not an absence.
    """
    if not shared_text:
        return

    def _safe(fn):
        try:
            return fn(shared_text)
        except ValueError:
            return None

    present = {
        "viewports": lambda: _safe(_viewports_from_contract_block),
        "required_states": lambda: (_safe(_required_states_from_contract_block)
                                    or _required_states_labeled(shared_text)),
        "declared_surfaces": lambda: extract_section(shared_text, _SURFACES_HEADING),
    }
    for item in violations:
        probe = present.get(item["key"])
        if probe and probe():
            item["hint"] = (f"已写在 `## Slice: {slice_id}` 区块之外（共享区）；"
                            f"请把它移到该区块内（区块标题须在这些契约之前）")


class IncompleteStageContractError(ValueError):
    """Raised when discussion.md omits fields the canonical IR requires non-empty.

    Subclasses `ValueError` so callers/tests that catch `ValueError` still work.
    Carries the structured violation list so the message stays actionable and a
    single raise reports every missing item at once.
    """

    def __init__(self, violations: List[Dict[str, str]], header: str = ""):
        self.violations = violations
        report = format_missing_sections(violations, header=header or _MISSING_ABORT_HEADER)
        super().__init__(report)


_MISSING_ABORT_HEADER = "compile_spec_ir: discussion.md 缺少 Canonical IR 必备字段，编译中止。"
_MISSING_NOTE_HEADER = (
    "compile_spec_ir: 以下 Canonical IR 字段尚未在 discussion.md 中声明；"
    "本次按 intent_spec 层级继续编译，未中止。"
)


def format_missing_sections(violations: List[Dict[str, str]], header: str = _MISSING_ABORT_HEADER) -> str:
    """Render an actionable, multi-item report of every missing required section.

    `header` names the concrete consequence of this call site. The same report is
    reused for a hard abort and for an intent-tier note that compiles anyway, so
    a default that always reads `编译中止` would tell an author the run stopped
    when it did not. Aborting call sites take the default; continuing ones pass
    `_MISSING_NOTE_HEADER`, and an empty header suppresses the line.
    """
    parts = [header] if header else []
    parts.append(f"发现 {len(violations)} 项缺失：")
    for index, item in enumerate(violations, start=1):
        hint = item.get("hint")
        parts.append(
            f"  [{index}] {item['key']} ({item['label']}) "
            f"{'已声明但位置不对。' if hint else '未提取到。'}\n"
            + (f"      位置:     {hint}\n" if hint else "")
            + f"      期望章节: {item['section']}\n"
            f"      声明格式: {item['form']}\n"
            f"      样例:     {item['example']}"
        )
    parts.append(
        "请补齐上述章节后重试；确需越过校验（仅限调试）请显式传入 `--allow-incomplete`。"
    )
    return "\n".join(parts)


def parse_5_dial_register(text: str) -> Dict[str, str]:
    """Extract only the authored Five Axes; undeclared axes stay open.

    The Five Axes are optional calibration, so an unset axis is never filled
    with a default that would reach the Builder as if it were authored.

    Priority 0: a ```contract:axes``` block is the machine SSOT.
    """
    block = _axes_from_contract_block(text)
    if block is not None:
        return block
    axes = _AXES
    dials: Dict[str, str] = {}
    # Look for `- \`?(\w+)\`?: \`?([^\`\n]+)\`?`
    for line in text.splitlines():
        m = re.search(r"[-*]\s*`?([A-Za-z]+)`?:\s*`?([^`\n]+)`?", line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().lower()
            if key in axes:
                dials[key] = val
            elif key in _AXIS_ALIASES:
                dials[_AXIS_ALIASES[key]] = val
    return {axis: dials[axis] for axis in axes if axis in dials}

def parse_palette_discipline(text: str) -> Dict[str, str]:
    """Extract an authored signature accent and its policy, or nothing.

    A signature accent is a per-product decision; absent an authored
    `--accent-seal` token the compiler must not supply a colour or a rule.

    Priority 0: a ```contract:tokens``` block is the machine SSOT.
    """
    block = _tokens_from_contract_block(text)
    if block is not None:
        return block
    discipline: Dict[str, str] = {}
    seal = re.search(r"--accent-seal`?\s*[:：]\s*`?(#[0-9a-fA-F]{3,8})", text)
    if seal:
        discipline["accent_seal"] = f"var(--accent-seal, {seal.group(1)})"
    policy = re.search(r"(?:Signature\s+)?Accent\s+Policy[*`]*\s*[:：]\s*([^\n]+)", text, re.IGNORECASE)
    if policy:
        discipline["accent_policy"] = policy.group(1).strip().strip("`* ")
    return discipline


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


def parse_design_intent(text: str) -> Dict[str, Any]:
    """Retain authored proposition and anti-slop context for creative consumers."""
    fields = {
        "scene_sentence": r"Scene sentence|场景句",
        "signature_relationship": r"Signature Relationship|签名关系",
        "design_proposition": r"Design Proposition|设计命题|Core design thesis",
    }
    intent: Dict[str, Any] = {}
    for key, label in fields.items():
        match = re.search(rf"^\s*[-*]?\s*(?:\*\*)?(?:{label})(?:\*\*)?\s*[:：]\s*(.+?)\s*$",
                          text, re.IGNORECASE | re.MULTILINE)
        if match:
            intent[key] = match.group(1).strip().strip("`\\\"'")
    anti_slop = extract_section(text, r"###?\s*.*(?:Anti[- ]slop|Match-and-refuse|禁用项|反模板)")
    if not anti_slop:
        match = re.search(
            r"(?:Anti[- ]slop|Match-and-refuse|禁用项|反模板)[^\n]*\n((?:(?:\s*[-*]|\s*\d+[.)])\s+[^\n]*\n?)+)",
            text, re.IGNORECASE)
        anti_slop = match.group(1) if match else ""
    bans = [m.group(1).strip() for line in anti_slop.splitlines()
            if (m := re.match(r"^\s*(?:[-*]|\d+[.)])\s+(.+?)\s*$", line))]
    if bans:
        intent["anti_slop_bans"] = bans
    if intent:
        intent["source_ref"] = "prototype/discussion.md"
    return intent


# An authored lifecycle clause after the verb, e.g. "`Enter` 键机械压感双签隔离
# (Trigger: ... -> Commit: \"...\" -> Feedback: ...)" or the bullet form
# "- `action-enter`: 双签隔离 (Trigger: Space key / row click -> ...)".
# Capturing through the closing paren keeps the structured Trigger/Action/Commit/
# Feedback semantics instead of truncating at the first 中文逗号 and flattening
# the contract into a bare verb string.
_ACTION_CLAUSE_RE = re.compile(
    r"`([A-Za-z][A-Za-z0-9+]*)`\s*键([^(（\n]*)(?:[(（]([^)）\n]*)[)）])?"
)
_ACTION_FIELD_RE = re.compile(r"(Trigger|Action|Commit|Feedback)\s*[:：]\s*([^>-]+)")


def _parse_action_clause(clause: str) -> Dict[str, str]:
    """Split an authored lifecycle clause into its semantic fields."""
    fields: Dict[str, str] = {}
    for fm in _ACTION_FIELD_RE.finditer(clause):
        value = fm.group(2).strip().strip('"“”').strip()
        if value:
            fields[fm.group(1).lower()] = value
    return fields


# The machine contract blocks are loaded and admitted by their own module. Every
# name is re-exported here because this file stays the one import surface callers
# and tests use, and because the prose parsers below are the other half of the
# same contract — `_PROSE_ADMISSION` mirrors their admission rules, so the two
# cannot drift apart without a test noticing.
from spec_contract_blocks import (  # noqa: E402
    AUTHORITY_LEVELS,
    _AXES,
    _AXIS_ALIASES,
    _CONTRACT_KINDS,
    _CRAFT_AXES,
    _INV_SEVERITIES,
    _INV_VERIFICATIONS,
    _MESO_KEYS,
    _PROSE_ADMISSION,
    _STATE_PREFIXES,
    _axes_from_contract_block,
    _contract_yaml_values,
    _craft_from_contract_block,
    _invariants_from_contract_block,
    _machine_bullets,
    _meso_from_contract_block,
    _parse_contract_yaml_blocks,
    _require_mapping_entries,
    _required_states_from_contract_block,
    _scalar_list,
    _states_from_contract_block,
    _stress_from_contract_block,
    _tokens_from_contract_block,
    _unadmitted_machine_bullets,
    _unadmitted_state_kinds,
    _unknown_contract_kinds,
    _viewports_from_contract_block,
    read_design_record,
    split_slice_blocks,
    parse_block_frontmatter,
    _SLICE_HEADING_RE,
    _FENCE_RE,
    _ATX_HEADING_RE,
    _BLOCK_FRONTMATTER_RE,
)


def _action_from_contract_block(block: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize one contract:actions YAML entry to the IR action shape."""
    action_id = str(block.get("id") or "").strip()
    required = {"id": action_id, "verb": str(block.get("verb") or "").strip(),
                "trigger": str(block.get("trigger") or "").strip(),
                "commit": str(block.get("commit") or block.get("commit_action") or "").strip()}
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise ValueError("contract:actions entry missing required field(s): " + ", ".join(missing))
    try:
        proximity_level = int(block.get("proximity_level") or 1)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"contract:actions {action_id} has invalid proximity_level") from exc
    if proximity_level < 1:
        raise ValueError(f"contract:actions {action_id} proximity_level must be >= 1")
    # Authority is authored, not assumed. An action declared in the discussion's
    # contract block is a designer's mechanism unless the author marks it
    # otherwise, so the unmarked default is `derived` — never `explicit`, which
    # would promote an unconfirmed mechanism into a user-confirmed fact.
    authority = str(block.get("authority") or "derived").strip().lower()
    if authority not in AUTHORITY_LEVELS:
        raise ValueError(
            f"contract:actions {action_id} has invalid authority {authority!r}; "
            f"expected one of {', '.join(AUTHORITY_LEVELS)}"
        )
    entry: Dict[str, Any] = {
        "id": action_id,
        "verb": required["verb"],
        "trigger": required["trigger"],
        "proximity_level": proximity_level,
        "commit_action": required["commit"],
        "authority": authority,
        "origin": "discussion.md#contract:actions",
    }
    for opt in ("feedback", "consequence"):
        val = block.get(opt)
        if val:
            entry[opt] = str(val).strip()
    return entry


def _authored_action_ids(text: str) -> set:
    """Collect every action id the authored Action Verbs declarations name.

    Action declarations appear both as headings-with-bullets and as inline
    bullet anchors (`- **Action Verbs …**:` followed by indented items), so the
    scan walks the whole document from each Action Verbs anchor to the next
    same-depth anchor. Every form counts — the template bullet form
    (`action-space`: …), the prose key-binding form (`Space` 键…), and table
    rows (| `action-space` | …). This is the latch's ground truth: what the
    author wrote must equal what parse_action_verbs extracted, or compilation
    fails instead of silently dropping semantics.
    """
    ids: set = set()
    # Structured contract blocks declare their ids directly.
    for block in _parse_contract_yaml_blocks(text, "actions"):
        block_id = str(block.get("id") or "").strip()
        if block_id:
            ids.add(block_id)
    anchor_re = re.compile(r"(?:^|\n)\s*(?:#{2,6}\s.*|[*\-]\s*\*\*.*)?(?:Action\s+Verbs?|动作契约|动作词|键位与动作)", re.IGNORECASE)
    for anchor in anchor_re.finditer(text):
        body = text[anchor.end():anchor.end() + 4000]
        # Stop at the next structural boundary: a heading or a new bold bullet
        # label that is not part of this action list.
        stop = re.search(r"\n\s{0,2}(?:#{1,6}\s|[*\-]\s*\*\*[^*]+:\*\*)", body)
        section = body[:stop.start()] if stop else body
        for m in re.finditer(r"`(action-[a-z0-9]+(?:-[a-z0-9]+)*)`", section):
            ids.add(m.group(1))
        for m in re.finditer(r"`([A-Za-z][A-Za-z0-9+]*)`\s*键", section):
            ids.add(f"action-{m.group(1).lower()}")
        for line in section.splitlines():
            if not line.strip().startswith("|"):
                continue
            for c in (cell.strip() for cell in line.split("|")):
                cm = re.match(r"`?(action-[a-z0-9]+(?:-[a-z0-9]+)*)`?$", c)
                if cm:
                    ids.add(cm.group(1))
    return ids


def parse_action_verbs(text: str) -> List[Dict[str, Any]]:
    """Derive action verbs from authored key bindings, or emit nothing.

    The fenced ```contract:actions``` YAML block is the machine SSOT: when
    present it is authoritative and prose heuristics are skipped for this kind.
    Otherwise two authored prose forms are recognized — the prose binding
    ("`Space` 键瞬时检视 (Trigger: ... -> Feedback: ...)") and the template
    bullet ("`action-space`: 检视异常节点详情 (Trigger: Space key / row click ->
    Level 1 Flyout -> ...)"). In both, the verb keeps only its head; the
    structured Trigger/Commit/Feedback clause is preserved in `commit_action`,
    and the Feedback message lands in `feedback` instead of being truncated at
    the first 中文逗号 and lost. Proximity stays 1 unless the clause authors a
    higher container level. Nothing is invented when no binding exists. Entries carry authority=inferred so
    downstream reads them as derived, not authored fact.
    """
    actions: List[Dict[str, Any]] = []
    seen: set = set()

    # Priority 0: fenced contract:actions YAML blocks are the machine SSOT.
    contract_blocks = _parse_contract_yaml_blocks(text, "actions")
    if contract_blocks:
        for block in contract_blocks:
            entry = _action_from_contract_block(block)
            if entry["id"] in seen:
                raise ValueError(f"contract:actions contains duplicate id: {entry['id']}")
            seen.add(entry["id"])
            actions.append(entry)
        return actions

    def _emit(action_id: str, key: str, verb: str, clause: str) -> None:
        if not verb or action_id in seen:
            return
        seen.add(action_id)
        fields = _parse_action_clause(clause)
        proximity = 1
        level_match = re.search(r"Level\s*([0-4])", clause)
        if level_match:
            proximity = int(level_match.group(1))
        elif re.search(r"<dialog>|确认弹窗|modal", clause, re.IGNORECASE):
            proximity = 4
        entry: Dict[str, Any] = {
            "id": action_id,
            "verb": verb,
            "trigger": fields.get("trigger") or (f"{key} key" if key else ""),
            "proximity_level": proximity,
            "commit_action": fields.get("commit") or verb,
            # Read off a prose lifecycle clause rather than an authored
            # contract block, so nothing marked it. Same vocabulary as the
            # structured path: `derived` is the designer's mechanism.
            "authority": "derived",
            "origin": "discussion.md",
        }
        if fields.get("feedback"):
            entry["feedback"] = fields["feedback"]
        if fields.get("action"):
            entry["consequence"] = fields["action"]
        actions.append(entry)

    # Form 1: "`<Key>` 键<verb> (lifecycle clause)".
    for m in _ACTION_CLAUSE_RE.finditer(text):
        key = m.group(1)
        verb = _ACTION_MODIFIER_RE.sub("", m.group(2).strip()).strip()
        _emit(f"action-{key.lower()}", key, verb, (m.group(3) or "").strip())

    # Form 2 (Stage 1 template): "- `action-<slug>`: <verb> (Trigger: <Key> key
    # ... -> ... -> Feedback: ...)". The action id is authored directly; the
    # clause carries the structured lifecycle.
    for m in re.finditer(
        r"`(action-[a-z0-9]+(?:-[a-z0-9]+)*)`\s*[:：]\s*([^(`\n（]+)\s*(?:[(（]([^)）\n]*)[)）])?",
        text,
    ):
        _emit(m.group(1), "", _ACTION_MODIFIER_RE.sub("", m.group(2).strip()).strip(), (m.group(3) or "").strip())
    return actions


def parse_viewports(text: str) -> List[int]:
    """Extract authored viewport widths.

    Priority 0: a ```contract:viewports``` block is the machine SSOT. Otherwise
    the prose scan admits any `NNNpx` in the text, which is why the block exists:
    a stray pixel figure in a paragraph is not a declared breakpoint.
    """
    block = _viewports_from_contract_block(text)
    if block is not None:
        return block
    return _viewports_prose(text)
def _viewports_prose(text: str) -> List[int]:
    """The compatibility scan: any `NNNpx` in the text, most fragile route."""
    out: List[int] = []
    lines = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```") or line.strip().startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    clean_text = "\n".join(lines)
    for m in re.finditer(r"(?<!\d)(\d{3,4})\s*px", clean_text):
        v = int(m.group(1))
        if 200 <= v <= 4000 and v not in out:
            out.append(v)
    return sorted(out)


def parse_navigation_topology(text: str, fm_data: Dict[str, Any]) -> Optional[str]:
    """Extract the authored navigation/layout topology, else None.

    `navigation_topology` is a design decision (workspace-inspector vs
    editorial-flow vs stacked-flow, etc.). The compiler must NOT fabricate a
    default: frontmatter wins, then an explicit `navigation_topology:` /
    `导航拓扑:` declaration in discussion.md. Undeclared stays None so the IR
    omits the key rather than hard-coding one layout for every product.
    """
    fm_val = fm_data.get("navigation_topology") or fm_data.get("topology")
    if fm_val:
        return str(fm_val).strip()
    m = re.search(
        r"navigation[_\s-]?topology\s*[:：]\s*`?([A-Za-z0-9][A-Za-z0-9_-]*)`?",
        text,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    m = re.search(r"导航拓扑\s*[:：]\s*`?([A-Za-z0-9][A-Za-z0-9_-]*)`?", text)
    if m:
        return m.group(1).strip()
    return None


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
    """Extract authored domain states.

    Priority 0: a ```contract:states``` block is the machine SSOT. Otherwise the
    prose bullet form (`domain/<id>` (label): description) is read for records
    that predate the block.
    """
    block = _states_from_contract_block(text)
    if block is not None:
        return block[0]
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
    """Extract authored interaction states declared as `interaction/<id>` bullets.

    Admission is bullet-anchored: the token must be the first thing after the
    list marker. A token that merely appears inside a prose line is a mention,
    not a declaration, and admitting it would let commentary invent a state.
    Further tokens on the same bullet are admitted, so the authored
    `- `interaction/idle`, `interaction/inspecting`` form still reads.

    Priority 0: a ```contract:states``` block is the machine SSOT.
    """
    block = _states_from_contract_block(text)
    if block is not None:
        return block[1]
    out: List[str] = []
    seen: set = set()
    for line in text.splitlines():
        if not re.match(r"^\s*[-*]\s*[`*]*(?:interaction/|domain/|data/|stress/)",
                        line, re.IGNORECASE):
            continue
        for m in re.finditer(r"[`*]*(interaction/[a-z0-9][a-z0-9_-]*)[`*]*", line, re.IGNORECASE):
            tok = m.group(1).lower()
            if tok in seen:
                continue
            seen.add(tok)
            out.append(tok)
    return out


def parse_data_scenarios(text: str) -> List[Dict[str, Any]]:
    """Extract authored data scenarios declared as `data/<id>` bullets.

    Bullet-anchored for the same reason as `parse_interaction_states`: only a
    declared bullet is a scenario, and a token named in prose is not one.

    Priority 0: a ```contract:states``` block is the machine SSOT.
    """
    block = _states_from_contract_block(text)
    if block is not None:
        return block[2]
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]\s*[`*]*(data/[a-z0-9][a-z0-9_-]*)[`*]*(.*)$",
                     line, re.IGNORECASE)
        if not m:
            continue
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

    Priority 0: a ```contract:stress``` block is the machine SSOT. The block
    fails closed on a half-authored fixture, because there the author declared
    the fixture deliberately; the prose scan still drops one, because there the
    line may be a mention rather than a declaration.
    """
    block = _stress_from_contract_block(text)
    if block is not None:
        return block
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

    The label is anchored at line start. The contract prose names the label
    without one ("required states — from that block"), and an unanchored search
    turns that sentence into a declaration whose payload is the rest of the
    sentence, admitting ordinary English words as test states.

    Priority 0: a ```contract:required_states``` block is the machine SSOT.
    """
    block = _required_states_from_contract_block(text)
    if block is not None:
        return block
    return _required_states_labeled(text) or _required_states_prose(text)

def _required_states_labeled(text: str) -> List[str]:
    """The labelled prose form: `- Required States: state-a, state-b`."""
    out: List[str] = []
    seen: set = set()

    def _add(tok: str) -> None:
        clean = tok.strip().strip("`*\"'").lower()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)

    label = re.compile(r"^\s*[-*]?\s*[`*]*(?:Required[ \t]+States?|Mandatory[ \t]+Test[ \t]+States?|强制测试状态)[`*]*[ \t]*[:：]?[ \t]*(.*)$",
                       re.IGNORECASE)
    for line in text.splitlines():
        m = label.match(line)
        if not m:
            continue
        for tok in re.findall(r"[`*]?([a-z0-9][a-z0-9_-]*)[`*]?", m.group(1), re.IGNORECASE):
            _add(tok)
    return out

def _required_states_prose(text: str) -> List[str]:
    """The compatibility scan for required states, most fragile route.

    The bare `state-*` sweep is separate from the labelled form above: a record
    whose only declaration is the label must be resolved by `parse_required_states`
    before this wider sweep runs, or the sweep reads `state-` tokens out of the
    template's own frontmatter and prose and outruns the authored label.
    """
    out: List[str] = []
    seen: set = set()
    for tok in re.findall(r"[`*]?(state-[a-z0-9][a-z0-9_-]*)[`*]?", text, re.IGNORECASE):
        clean = tok.strip().strip("`*\"'").lower()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out


def parse_craft_stack(text: str, five_axes: Dict[str, str]) -> Dict[str, str]:
    """Extract only the authored axes of the orthogonal 4-axis craft stack.

    Unspecified axes remain open; they are not inferred from domain words or
    filled with a house style.

    Priority 0: a ```contract:craft``` block is the machine SSOT.
    """
    block = _craft_from_contract_block(text)
    if block is not None:
        return block
    axes = _CRAFT_AXES
    stack: Dict[str, str] = {}
    for line in text.splitlines():
        m = re.search(r"[`*]*(surface_optics|spatial_geometry|micro_typography|data_marks)[`*]*\s*[:：]\s*[`*]*([^`\n]+)[`*]*", line, re.IGNORECASE)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().lower().rstrip("`* \t")
            if val and key not in stack:
                stack[key] = val

    # Omitted craft is genuine design space, not a request for a preset.
    # Deterministic axis order regardless of authored bullet order.
    return {axis: stack[axis] for axis in axes if axis in stack}


def parse_authored_invariants(text: str, record_name: str = "design-record") -> List[Dict[str, Any]]:
    """Extract authored design invariants from discussion.md, or emit none.

    Invariants are admitted ONLY from an authored section (Design Invariants /
    设计不变式 / Design Rules). The former hardcoded telemetry/4096 template
    invariants were never authored facts and are retired: an unauthored
    discussion yields `[]`, never injected heuristics.

    Authored line form:
      - `inv/<id>` | <statement> | severity: blocking | verification: computed_style
    `severity` defaults to advisory and `verification` to manual; unknown
    severities fall back to advisory rather than fabricating an enum value.

    Priority 0: a ```contract:invariants``` block is the machine SSOT. It fails
    closed on an unknown severity or verification, because the author declared
    it; the prose form keeps its lenient fallback.
    """
    block = _invariants_from_contract_block(text)
    if block is not None:
        for invariant in block:
            invariant["upstream_ref"] = record_name
        return block
    sec = extract_section(text, r"###?\s*.*(?:Invariants|不变式|Design\s+Invariants|Design\s+Rules|设计规则|Resilience|Acceptance\s+Gates?)")
    out: List[Dict[str, Any]] = []
    severities = set(_INV_SEVERITIES)
    verifications = set(_INV_VERIFICATIONS)
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
            "upstream_ref": record_name,
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

    Priority 0: a ```contract:meso``` block is the machine SSOT.
    """
    block = _meso_from_contract_block(text)
    if block is not None:
        authored = block
    else:
        authored = {}
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


def resolve_token_link(root: Path, target_html: str) -> Dict[str, str]:
    """Compute the tokens stylesheet link from the anchor's real depth.

    The relative depth from `prototype/experiments/<slice>/anchor/index.html`
    to `prototype/shared/tokens.css` is a property of the tree, not a fact to
    be retyped in prose. Deriving it here means the Builder consumes a resolved
    link instead of miscalculating `../../` versus `../../../`, and the
    navigation check downstream can never disagree with the delivered file.
    """
    tokens_css = root / "prototype/shared/tokens.css"
    target_dir = (root / target_html).parent
    rel_href = os.path.relpath(tokens_css, target_dir).replace(os.sep, "/")
    return {
        "token_stylesheet_ref": rel_href,
        "token_link_tag": f'<link rel="stylesheet" href="{rel_href}">',
    }


NON_SURFACE_NAMES = {
    "viewport", "viewports", "screen", "screens", "breakpoint", "breakpoints",
    "device", "devices", "mobile", "desktop", "tablet", "width", "height",
    "dimension", "dimensions", "resolution", "resolutions",
}


def load_intent_contract(root: Path) -> Dict[str, Any]:
    """Read prototype/intent.json — the Stage 1 machine contract.

    Stage 1 fields arrive as a JSON object the author writes directly, so the
    compiler no longer has to recover them from prose. A malformed file is a
    hard error here rather than a silent fallback to regex, because falling
    back would let a broken contract compile as if it were authored.
    """
    path = root / "prototype/intent.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise IncompleteStageContractError(
            [{
                "key": "intent_json",
                "label": "Stage 1 机器契约 (prototype/intent.json)",
                "section": "Stage 1 (intent tier)",
                "form": '{"schema_version": "intent.v1", "slice_id": ..., "core_tension": ..., '
                        '"declared_surfaces": [...], "physical_anchor": ...}',
                "example": f"第 {error.lineno} 行第 {error.colno} 列 JSON 语法错误：{error.msg}",
            }],
            header="compile_spec_ir: prototype/intent.json 无法解析，编译中止。",
        ) from error
    if not isinstance(data, dict):
        raise IncompleteStageContractError(
            [{
                "key": "intent_json",
                "label": "Stage 1 机器契约 (prototype/intent.json)",
                "section": "Stage 1 (intent tier)",
                "form": "一个 JSON 对象",
                "example": "顶层必须是对象，而不是数组或标量。",
            }],
            header="compile_spec_ir: prototype/intent.json 顶层必须是对象，编译中止。",
        )
    return data


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
    # One seam loads the record, whichever layout the tree uses: the layered
    # truth/world/brief form, or the single discussion.md record. Everything
    # below parses that assembled text, so the two layouts share one code path
    # instead of forking the compiler.
    record = read_design_record(root, slice_id)
    disc_path = record.path
    disc_text = record.text
    disc_digest = record.digest
    fm_data, body_text = parse_frontmatter(disc_text)
    intent = load_intent_contract(root)

    # Lifecycle scope: product-level facts read the shared zones; slice-level
    # facts read the shared zones plus this slice's block; verification scope
    # reads this slice's block alone. The partition comes from the record seam,
    # which resolves it by construction in the layered layout and by `## Slice:`
    # splitting in the single-record one. A record the seam left unpartitioned
    # is a legacy tree and reads the whole file at every level.
    shared_text, slice_block = record.shared, record.slice_block
    if shared_text is None:
        product_text = scope_text = slice_text = disc_text
    elif slice_block is None:
        raise IncompleteStageContractError(
            [{
                "key": "slice_block",
                "label": f"slice 区块 ({slice_id})",
                "section": f"## Slice: {slice_id}",
                "form": "每个 slice 恰好一个 `## Slice: <slice_id>` 区块",
                "example": f"已声明的 slice: {', '.join(sorted(split_slice_blocks(disc_text)[1]))}",
            }],
            header=f"compile_spec_ir: 记录已按 slice 分区，但 slice `{slice_id}` 未声明其区块，编译中止。",
        )
    else:
        product_text = shared_text
        scope_text = shared_text + "\n" + slice_block
        slice_text = slice_block
        block_fm = parse_block_frontmatter(slice_block)
        if block_fm.get("slice_id") and str(block_fm["slice_id"]) != slice_id:
            raise IncompleteStageContractError(
                [{
                    "key": "slice_id",
                    "label": "slice 身份 (slice_id)",
                    "section": f"## Slice: {slice_id}",
                    "form": "区块 frontmatter 的 slice_id 必须等于区块标题",
                    "example": f"标题 `{slice_id}`，frontmatter `{block_fm['slice_id']}`",
                }],
                header="compile_spec_ir: slice 区块标题与其 frontmatter 的 slice_id 不一致，编译中止。",
            )
        # In the layered layout the brief is the slice's entire block. A brief
        # that omits the slice_id frontmatter cannot be told apart from a stray
        # file under `prototype/briefs/`, so require the field there; a
        # single-record tree keeps the field optional because the `## Slice:`
        # heading already names the slice.
        if record.path.name == "truth.md" and "slice_id" not in block_fm:
            raise IncompleteStageContractError(
                [{
                    "key": "slice_id",
                    "label": "slice 身份 (slice_id)",
                    "section": f"prototype/briefs/{slice_id}.md frontmatter",
                    "form": "frontmatter 必须声明 `slice_id` 字段且等于文件名",
                    "example": f"---\nslice_id: \"{slice_id}\"\n---",
                }],
                header="compile_spec_ir: brief 未声明 slice_id frontmatter，编译中止。",
            )
        fm_data = {**fm_data, **block_fm}

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
            except json.JSONDecodeError as error:
                raise IncompleteStageContractError(
                    [{
                        "key": "state_model_fragment",
                        "label": f"State model fragment ({fpath.relative_to(root).as_posix() if fpath.is_relative_to(root) else fpath.name})",
                        "section": "State model compilation",
                        "form": "Valid JSON file",
                        "example": f"第 {error.lineno} 行第 {error.colno} 列 JSON 语法错误：{error.msg}",
                    }],
                    header=f"compile_spec_ir: 状态模型片段 {fpath.name} 语法错误，编译中止。",
                ) from error

    # Extract Product / Identity (Frontmatter title or Markdown header)
    if fm_data.get("title"):
        product_title = str(fm_data["title"]).strip()
    else:
        title_m = re.search(r"#\s*(?:Design\s*Discussion|Surface\s*Specification|Prototype\s*Specification):\s*([^\n]+)", product_text, re.IGNORECASE)
        product_title = title_m.group(1).strip() if title_m else slice_id.replace("-", " ").title()
    product_id = re.sub(r"[^a-z0-9]+", "-", product_title.lower()).strip("-") or "product"

    # Frontmatter authority / stage overrides
    if authority_status == "sealed_provisional" and fm_data.get("authority"):
        authority_status = str(fm_data["authority"]).strip()
    if stage == "hero_probe" and fm_data.get("stage"):
        stage = str(fm_data["stage"]).strip()

    # Extract Core Tension. The Stage 1 machine contract wins when present;
    # prose recovery stays as the fallback for records that predate intent.json.
    tension_text = str(intent.get("core_tension") or "").strip() or None
    if not tension_text:
        tension_text = extract_section(product_text, r"###?\s*.*(?:Core\s+Tension|Problem\s+Framing|Tension|业务与用户极端张力|极端张力|张力)")
    if not tension_text and fm_data.get("core_tension"):
        tension_text = str(fm_data["core_tension"]).strip()
    if not tension_text:
        m_tension = re.search(r"[-*]?\s*\**Core\s+Tension\**\s*[:：]\s*`?([^`\n]+)`?", product_text, re.IGNORECASE)
        if m_tension:
            tension_text = m_tension.group(1).strip()
    # Absent authored tension stays None: never fabricate a domain claim that
    # would propagate downstream as a real constraint.
    if not tension_text:
        tension_text = None

    # Physical anchor is an explicit Stage 1 decision; category-based guesses
    # must not silently determine the device chassis.
    # Physical anchor: an explicit Stage 1 decision. The machine contract wins;
    # category-based guesses must not silently determine the device chassis.
    physical_anchor = str(intent.get("physical_anchor") or "").strip()
    if not physical_anchor:
        physical_anchor_match = re.search(
        r"^\s*[-*]?\s*(?:\*\*)?(?:Physical Anchor|physical_anchor)(?:\s+Declaration)?(?:\*\*)?\s*[:：]\s*([^\n]+)",
        product_text,
        re.IGNORECASE | re.MULTILINE,
    )
        physical_anchor = physical_anchor_match.group(1).strip().strip("`* ") if physical_anchor_match else ""
        physical_anchor = re.sub(r"^physical_anchor\s*:\s*", "", physical_anchor, flags=re.IGNORECASE).strip()

    # Extract Reality Anchors
    anchors_text = extract_section(product_text, r"###?\s*.*(?:Reality.*Anchors?|现实双地锚|地锚|Industry\s+Benchmarks?|Benchmarks?)")
    anchors = []
    for line in anchors_text.splitlines():
        line = line.strip()
        if line.startswith(("-", "*", "1.", "2.", "3.")):
            anchors.append(re.sub(r"^[-*0-9.]+\s*", "", line).strip())
    # No invented fallback: absent authored anchors stay empty and are omitted
    # from the IR, so downstream reads "undeclared" instead of a plausible lie.

    # Extract 三大冷酷舍弃 (Ruthless Omissions) - a real authority source that
    # previously had no parser and was silently discarded.
    ruthless_omissions = parse_ruthless_omissions(product_text)

    # Extract 5-Dial Register
    style_text = extract_section(product_text, r"###?\s*.*(?:5-Dial|风格寄存器|Style Register)")
    five_axes = parse_5_dial_register(style_text or product_text)

    # Optional craft declarations remain open when the author leaves them unset.
    # Read at slice scope, like the state model and the actions: the four craft
    # axes are per-surface decisions, and the template authors them inside the
    # slice block. Reading only `product_text` left a slice's `contract:craft`
    # block unread — a declaration the compiler silently dropped.
    craft_stack = parse_craft_stack(scope_text, five_axes)
    design_intent = parse_design_intent(product_text)

    # Extract OOUX / Surfaces
    surfaces_text = extract_section(slice_text, _SURFACES_HEADING)
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
            if s_name.lower() in NON_SURFACE_NAMES:
                continue
            if s_name not in declared_surfaces:
                declared_surfaces.append(s_name)
            if ("primary" in line.lower() or "主" in line) and not primary_surface:
                primary_surface = s_name

    if isinstance(intent.get("declared_surfaces"), list):
        for s in intent["declared_surfaces"]:
            s_name = Path(str(s)).name
            if s_name.lower() in NON_SURFACE_NAMES:
                continue
            if s_name not in declared_surfaces:
                declared_surfaces.append(s_name)

    if fm_data.get("declared_surfaces") and isinstance(fm_data["declared_surfaces"], list):
        for s in fm_data["declared_surfaces"]:
            s_name = Path(str(s)).name
            if s_name.lower() in NON_SURFACE_NAMES:
                continue
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
    domain_states = frag_data.get("domain_states") or parse_domain_states(scope_text)
    interaction_states = frag_data.get("interaction_states") or parse_interaction_states(scope_text)
    data_scenarios = frag_data.get("data_scenarios") or parse_data_scenarios(scope_text)
    stress_fixtures = frag_data.get("stress_fixtures") or parse_stress_fixtures(scope_text)

    # Invariants: ONLY discussion/Spec-authored invariants reach the IR. The
    # former hardcoded telemetry/4096 GPU template entries were injected
    # heuristics with no authored source and are retired: an unauthored
    # discussion emits `[]`, never a template.
    invariants = parse_authored_invariants(scope_text, disc_path.name)

    # Actions: derived strictly from authored key bindings in discussion.md.
    # The former hardcoded "检视实体"/"确定隔离排空" verbs were never extracted from
    # the source and are removed; when no binding exists, actions stays empty.
    actions = parse_action_verbs(scope_text)

    # Semantic latch: an authored Action Verbs section that fails to project
    # into IR actions is a silent semantic loss (format drift between template
    # and parser), not an empty contract. Fail loudly at compile time instead
    # of letting the Builder receive an empty action_contracts payload.
    authored_action_ids = _authored_action_ids(scope_text)
    extracted_action_ids = {a.get("id") for a in actions}
    if authored_action_ids and authored_action_ids != extracted_action_ids:
        missing = sorted(authored_action_ids - extracted_action_ids)
        extra = sorted(extracted_action_ids - authored_action_ids)
        detail = ", ".join(missing) if missing else ""
        if extra:
            detail = (detail + "; " if detail else "") + "spurious: " + ", ".join(extra)
        raise IncompleteStageContractError(
            [{
                "key": "actions_latch",
                "label": "动作契约语义闩锁 (action semantic latch)",
                "section": "discussion.md → Action Verbs",
                "form": "authored action ids must project 1:1 into IR actions",
                "example": f"authored={sorted(authored_action_ids)} extracted={sorted(extracted_action_ids)} ({detail})",
            }],
            header="动作契约提取不完整：discussion.md 的 Action Verbs 授权项未全部进入 IR actions。"
                   "这通常是格式漂移（模板改了、解析器没跟上）或章节残留空壳；修复作者格式或解析器后重试。",
        )

    # Meso assembly slots: authored massing/kinematics/data_syntax declarations,
    # with an undeclared massing smoothing to a topology-derived fallback.
    nav_topology = parse_navigation_topology(scope_text, fm_data)
    meso = parse_meso_directives(scope_text, nav_topology or "stacked-flow")

    # Progressive tier stamping: the IR emits the tier it can legitimately
    # derive. A full state machine AND action contracts present (authored here
    # or merged from a Stage 3/4 fragment) earn `execution_spec`; otherwise the
    # Stage 1 `intent_spec` tier is stamped.
    has_state_machine = bool(
        domain_states and interaction_states and data_scenarios and stress_fixtures
    )
    has_action_contracts = bool(actions)
    spec_tier = "execution_spec" if (has_state_machine and has_action_contracts) else "intent_spec"

    # Verification scope resolution order, most authoritative first:
    #   1. an explicit `--viewports` override (the caller's decision)
    #   2. this slice's `contract:` block
    #   3. a Stage 3/4 verification fragment (an explicit machine artifact)
    #   4. the slice frontmatter field (a declared compatibility carrier)
    #   5. the prose scan (inferred, most fragile)
    # The block outranks the frontmatter: every other contract kind takes its
    # block as authoritative, and a frontmatter that won would make
    # `contract:viewports` an authoritative-looking block the compiler ignores —
    # a declaration dropped in silence, which is what the blocks exist to remove.
    # Prose stays last so a stray `NNNpx` in a sentence never outruns a declared
    # viewport, which is how the template's exemplary `320px` prose used to
    # replace the frontmatter's authored list.
    resolved_vps = (list(viewports) if viewports
                    else (_viewports_from_contract_block(slice_text)
                          or frag_data.get("viewports")
                          or ([int(v) for v in fm_data.get("viewports", []) if str(v).isdigit()]
                              if isinstance(fm_data.get("viewports"), list) else [])
                          or _viewports_prose(slice_text)))
    resolved_req_states = (_required_states_from_contract_block(slice_text)
                           or _required_states_labeled(slice_text)
                           or frag_data.get("required_states")
                           or ([str(s).strip() for s in fm_data.get("required_states", []) if str(s).strip()]
                               if isinstance(fm_data.get("required_states"), list) else [])
                           or _required_states_prose(slice_text))

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
            # The primary record file the seam loaded: `discussion.md` on a
            # single-record tree, `truth.md` on a layered one. Naming
            # discussion.md unconditionally would point provenance at a file the
            # layered tree does not carry.
            "discussion_ref": record.path.relative_to(root).as_posix(),
            "discussion_sha256": disc_digest,
            # The assembled record carries no requirement/scenario taxonomy: emit
            # none rather than fabricate REQ-*/SCN-* identifiers downstream could
            # treat as traced upstream authority.
            "requirements": [],
            "reality_anchors": anchors,
            "core_tension": tension_text,
            "ruthless_omissions": ruthless_omissions,
            **({"design_intent": design_intent} if design_intent else {}),
        },
        "scope": {
            "topology_scope": {
                "coverage": "key-journey" if len(declared_surfaces) > 1 else "slice-isolated",
                "declared_surfaces": declared_surfaces,
                # Omit when undeclared: schema types primary_surface as string,
                # and a null would falsely imply an authored primary surface.
                **({"primary_surface": primary_surface} if primary_surface else {}),
                # Omit when undeclared: navigation_topology is an authored design
                # decision, not a constant the compiler may invent per product.
                **({"navigation_topology": nav_topology} if nav_topology else {}),
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
            "palette_discipline": parse_palette_discipline(product_text),
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
        "visual_directives": {
            **(meso.get("visual_directives") or {}),
            **resolve_token_link(root, f"prototype/experiments/{slice_id}/anchor/index.html"),
        },
        "artifacts_binding": {
            "tokens_css": "prototype/shared/tokens.css",
            "tokens_json": "prototype/contracts/tokens/t1.json",
            "human_spec_md": f"prototype/specifications/{slice_id}/{candidate_id}.spec.md",
            "prototype_html": f"prototype/experiments/{slice_id}/anchor/index.html",
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
    # A declaration the compiler dropped and a state class the block left empty
    # are structural, not "not yet authored": the author wrote them and the
    # compiler lost them. They abort at every tier — routing them through the
    # intent-tier note would report them as a stage the run has not reached yet,
    # which is how a silent drop stays silent.
    structural_violations = (_unadmitted_machine_bullets(scope_text)
                             + _unadmitted_state_kinds(scope_text)
                             + _unknown_contract_kinds(scope_text))
    if structural_violations and not allow_incomplete:
        raise IncompleteStageContractError(structural_violations)
    violations += structural_violations
    intent_extracted: Dict[str, Any] = {
        "core_tension": tension_text,
        "declared_surfaces": declared_surfaces,
        "physical_anchor": physical_anchor,
    }
    intent_violations = [
        {"key": spec["key"], "label": spec["label"], "section": spec["section"],
         "form": spec["form"], "example": spec["example"]}
        for spec in _INTENT_REQUIRED_SECTIONS
        if not intent_extracted.get(spec["key"])
    ]
    _misplaced_in_shared(shared_text, slice_id, violations + intent_violations)
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
        report = format_missing_sections(violations, header=_MISSING_NOTE_HEADER)
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
    if required_tier in {"stage2", "stage_2", "prototype"} and not physical_anchor:
        raise IncompleteStageContractError(
            [{
                "key": "physical_anchor",
                "label": "物理锚点 (physical_anchor)",
                "section": "Stage 1 §2 (Physical Anchor Declaration)",
                "form": "- Physical Anchor: <declared chassis or none>",
                "example": "- Physical Anchor: desktop workstation",
            }],
            header="Stage 2 原型入口被阻断：discussion.md 必须显式声明 Physical Anchor；无设备锚点时填写 none。",
        )

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
    design_intent = src.get("design_intent") or {}
    if design_intent:
        md.append("- **Authored Design Intent**:")
        for key, label in (("scene_sentence", "Scene sentence"),
                           ("signature_relationship", "Signature Relationship"),
                           ("design_proposition", "Design Proposition")):
            if design_intent.get(key):
                md.append(f"  - **{label}**: {design_intent[key]}")
        for ban in design_intent.get("anti_slop_bans") or []:
            md.append(f"  - **Anti-slop ban**: {ban}")
        md.append(f"  - **Source**: `{design_intent.get('source_ref', 'prototype/discussion.md')}`")
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
    md.append(f"- **Navigation Topology**: `{scope['topology_scope'].get('navigation_topology') or '_None declared_'}`")
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
    if not fnd["five_axes"]:
        md.append("  - _No axis declared; sensory calibration remains open design space._")
    palette = fnd.get("palette_discipline") or {}
    if palette.get("accent_seal") or palette.get("accent_policy"):
        md.append(f"- **Signature Accent**: `{palette.get('accent_seal', 'undeclared')}` — "
                  f"{palette.get('accent_policy', '_policy not authored_')}")
    else:
        md.append("- **Signature Accent**: _None declared._")
    md.append("- **Orthogonal Craft Stack**:")
    for k, v in (fnd.get("craft_stack") or {}).items():
        md.append(f"  - `{k}`: `{v}`")
    if not fnd.get("craft_stack"):
        md.append("  - _No craft axis declared; the Builder resolves craft within the open design space._")
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
    # Bound tokens and authored viewport intent constrain implementation;
    # this renderer must not invent a shared visual recipe.
    md.append("## 3.5 Product-Validated Design Rules")
    md.append("> Promote a rule only when retained evidence supports it; otherwise keep it open or provisional.")
    md.append("")
    md.append("| Decision | Value or behavior | Scope / variation | Evidence | Transfer boundary |")
    md.append("|---|---|---|---|---|")
    md.append("| _No validated shared rules compiled from this Spec IR._ | | | | |")
    md.append("")
    md.append("## 3.6 System Constants (Physical Reference Frame)")
    md.append("> Token values come from the bound stylesheet; avoid interpreting this table as a mandated aesthetic recipe.")
    md.append("")
    md.append("### Typography tokens")
    md.append("- Font families, weights, sizes and line heights belong to the bound token artifact and authored design rules.")
    md.append("")
    md.append("### Spacing and geometry tokens")
    md.append("- Use the bound `--space-*` and `--radius-*` tokens where they fit the validated design; component geometry may vary by component and platform.")
    md.append("")
    md.append("### Semantic color roles")
    md.append("- Surface, border, text, focus and status roles should remain distinguishable and meet applicable accessibility requirements; their palette and mapping are authored in the bound token artifact.")
    md.append("")
    md.append("## 3.7 Responsive Viewport Intent (authored constraints)")
    md.append("> Preserve declared viewport priorities; do not infer a layout mode from width alone.")
    md.append("")
    viewports = (ir.get("scope", {}).get("verification_scope", {}) or {}).get("viewports") or []
    primary = scope.get("topology_scope", {}).get("primary_surface") or ""
    if viewports:
        for vp in viewports:
            md.append(f"### {vp}px")
            md.append(f"- Declared primary surface: `{primary}`" if primary
                      else "- No primary surface declared.")
            md.append("")
    else:
        md.append("_No authored viewports declared in discussion.md._")
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
        "--required-tier",
        choices=["intent_spec", "execution_spec", "stage2"],
        default="intent_spec",
        help="Require Stage 2 anchor admission or the full execution-spec tier.",
    )
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
            required_tier=args.required_tier,
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

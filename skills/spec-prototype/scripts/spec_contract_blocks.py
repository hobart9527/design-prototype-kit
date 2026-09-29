#!/usr/bin/env python3
"""spec_contract_blocks.py: the machine contract block loader and its admit checks.

The compiler reads a small set of lists as fact. Each has exactly one
authoritative form — a fenced ```contract:<kind>``` YAML block — and one prose
form kept only for a record that predates the block. This module owns the
loading of those blocks, the normalisation of each kind into its IR shape, and
the structural checks that report a declaration the compiler dropped instead of
silently continuing with the field empty.

`compile_spec_ir.py` remains the parsing authority for the prose route and
re-exports every name here, so the two are one contract seen from two files.
"""

from __future__ import annotations

import re
import textwrap
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore
except ImportError:  # structured contract blocks require the authoritative YAML parser
    yaml = None

# A fence opens or closes a block; the loader and the section extractor share
# this so a `##` inside a fence is not read as a heading.
_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")

# How much authority an authored action carries. `explicit` is a claim that the
# user stated the mechanism, so it is never the unmarked default.
AUTHORITY_LEVELS = ("explicit", "derived", "proposed", "hypothesis")

# The machine contract kinds. Every list the compiler reads as fact has exactly
# one authoritative form — a fenced ```contract:<kind>``` YAML block — and one
# prose form kept only for records that predate the block. This tuple is the
# single declaration of what a kind is; the loaders below, the missing-section
# report and the unadmitted-bullet check all read it, so the format cannot be
# restated in four places and drift.
_CONTRACT_KINDS = ("actions", "states", "stress", "invariants", "required_states",
                   "viewports", "axes", "craft", "tokens", "meso")

def _contract_yaml_values(text: str, kind: str) -> List[Any]:
    """Load every fenced ```contract:<kind>``` block, raw, in document order.

    One fence is one YAML document, and the value may be a mapping, a list of
    mappings, or a list of scalars (`required_states`, `viewports`).
    Normalisation belongs to the caller, so this stays a loader.
    """
    matches = list(re.finditer(rf"^[ \t]*```contract:{kind}\s*\n(.*?)^[ \t]*```", text, re.DOTALL | re.MULTILINE))
    if matches and yaml is None:
        raise ValueError(f"contract:{kind} requires PyYAML to parse its authoritative block")
    values: List[Any] = []
    for m in matches:
        # Dedent before stripping: a fence nested under a bullet carries a common
        # indent, and `strip()` alone removes it from the first line only, leaving
        # line 2 at column 4 under a line-1 item at column 0 — which PyYAML reads
        # as an over-indented mapping ("mapping values are not allowed here").
        body = textwrap.dedent(m.group(1)).strip()
        try:
            values.append(yaml.safe_load(body))
        except yaml.YAMLError as exc:
            raise ValueError(f"invalid contract:{kind} YAML: {exc}") from exc
    return values

def _parse_contract_yaml_blocks(text: str, kind: str) -> List[Dict[str, Any]]:
    """Parse fenced ```contract:<kind>``` YAML blocks — the machine SSOT form.

    When the author writes structured contract blocks, they are authoritative:
    parse them with the YAML loader and skip prose heuristics for that kind.
    """
    blocks: List[Dict[str, Any]] = []
    for loaded in _contract_yaml_values(text, kind):
        entries = loaded if isinstance(loaded, list) else [loaded]
        if not entries or any(not isinstance(entry, dict) for entry in entries):
            raise ValueError(f"contract:{kind} must contain a mapping or list of mappings")
        blocks.extend(entries)
    return blocks

def _require_mapping_entries(kind: str, loaded: Any) -> List[Dict[str, Any]]:
    """Normalise one block document to a list of mappings, or fail closed."""
    entries = loaded if isinstance(loaded, list) else [loaded]
    if not entries or any(not isinstance(entry, dict) for entry in entries):
        raise ValueError(f"contract:{kind} must contain a mapping or list of mappings")
    return entries

def _scalar_list(raw: Any, kind: str, field: str) -> List[str]:
    """Normalise a scalar, a comma list, or a YAML list into trimmed strings."""
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = re.split(r"[,，、]", raw)
    if not isinstance(raw, list):
        raise ValueError(f"contract:{kind} {field} must be a list or a comma-separated string")
    return [str(item).strip() for item in raw if str(item).strip()]

_STATE_PREFIXES = ("domain", "interaction", "data")

def _states_from_contract_block(text: str):
    """Normalise ```contract:states``` into (domain, interaction, data), or None.

    None means no block is present, so the caller falls back to the prose form.
    Every other outcome fails closed: an unknown prefix, a missing description
    and a duplicate id are authoring errors, not entries to skip.

    `description` is required for `domain/` and `data/` because the IR carries
    it; `interaction_states` is a plain id list by contract, so an interaction
    entry needs no description and is not asked for one.
    """
    values = _contract_yaml_values(text, "states")
    if not values:
        return None
    domain: List[Dict[str, Any]] = []
    interaction: List[str] = []
    data: List[Dict[str, Any]] = []
    seen: set = set()
    for loaded in values:
        for entry in _require_mapping_entries("states", loaded):
            sid = str(entry.get("id") or "").strip().lower()
            if not sid:
                raise ValueError("contract:states entry missing required field(s): id")
            prefix = sid.split("/", 1)[0]
            if prefix not in _STATE_PREFIXES:
                raise ValueError(
                    f"contract:states {sid} has an unknown prefix; expected one of "
                    + ", ".join(f"{p}/" for p in _STATE_PREFIXES))
            if sid in seen:
                raise ValueError(f"contract:states contains duplicate id: {sid}")
            seen.add(sid)
            if prefix == "interaction":
                interaction.append(sid)
                continue
            description = str(entry.get("description") or "").strip()
            if not description:
                raise ValueError(f"contract:states {sid} missing required field(s): description")
            label = str(entry.get("label") or "").strip() or sid.split("/", 1)[1]
            if prefix == "domain":
                domain.append({"id": sid, "label": label, "description": description})
            else:
                data.append({"id": sid, "description": description})
    return domain, interaction, data

def _stress_from_contract_block(text: str):
    """Normalise ```contract:stress``` into break-protocol fixtures, or None."""
    values = _contract_yaml_values(text, "stress")
    if not values:
        return None
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for loaded in values:
        for entry in _require_mapping_entries("stress", loaded):
            fid = str(entry.get("id") or "").strip().lower()
            vector = str(entry.get("vector") or "").strip()
            expected = str(entry.get("expected") or entry.get("expected_behavior") or "").strip()
            missing = [k for k, v in (("id", fid), ("vector", vector), ("expected", expected)) if not v]
            if missing:
                raise ValueError("contract:stress entry missing required field(s): " + ", ".join(missing))
            if not fid.startswith("stress/"):
                raise ValueError(f"contract:stress {fid} must be named stress/<id>")
            if fid in seen:
                raise ValueError(f"contract:stress contains duplicate id: {fid}")
            seen.add(fid)
            out.append({"id": fid, "vector": vector, "expected_behavior": expected})
    return out

_INV_SEVERITIES = ("blocking", "warning", "advisory")
_INV_VERIFICATIONS = ("computed_style", "dom_query", "screenshot_review", "manual")

def _invariants_from_contract_block(text: str):
    """Normalise ```contract:invariants``` into authored invariants, or None.

    An unknown severity or verification fails closed. The prose form silently
    falls back to `advisory`/`manual`, which turns a typo into a weaker gate the
    author never chose; the block is explicit, so it can be held to that.
    """
    values = _contract_yaml_values(text, "invariants")
    if not values:
        return None
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for loaded in values:
        for entry in _require_mapping_entries("invariants", loaded):
            inv_id = str(entry.get("id") or "").strip()
            statement = str(entry.get("statement") or "").strip()
            missing = [k for k, v in (("id", inv_id), ("statement", statement)) if not v]
            if missing:
                raise ValueError("contract:invariants entry missing required field(s): " + ", ".join(missing))
            if not inv_id.startswith("inv/"):
                raise ValueError(f"contract:invariants {inv_id} must be named inv/<id>")
            if inv_id in seen:
                raise ValueError(f"contract:invariants contains duplicate id: {inv_id}")
            seen.add(inv_id)
            severity = str(entry.get("severity") or "advisory").strip().lower()
            if severity not in _INV_SEVERITIES:
                raise ValueError(
                    f"contract:invariants {inv_id} has invalid severity {severity!r}; "
                    f"expected one of {', '.join(_INV_SEVERITIES)}")
            verification = str(
                entry.get("verification") or entry.get("verification_method") or "manual").strip().lower()
            if verification not in _INV_VERIFICATIONS:
                raise ValueError(
                    f"contract:invariants {inv_id} has invalid verification {verification!r}; "
                    f"expected one of {', '.join(_INV_VERIFICATIONS)}")
            applies_to = entry.get("applies_to")
            out.append({
                "id": inv_id,
                "upstream_ref": "discussion.md",
                "statement": statement,
                "severity": severity,
                "applies_to": _scalar_list(applies_to, "invariants", "applies_to"),
                "verification_method": verification,
                "authority": "authored",
            })
    return out

def _required_states_from_contract_block(text: str):
    """Normalise ```contract:required_states``` into state ids, or None."""
    values = _contract_yaml_values(text, "required_states")
    if not values:
        return None
    out: List[str] = []
    seen: set = set()
    for loaded in values:
        raw = loaded.get("required_states", loaded.get("states")) if isinstance(loaded, dict) else loaded
        tokens = _scalar_list(raw, "required_states", "required_states")
        if not tokens:
            raise ValueError("contract:required_states must name at least one state")
        for token in tokens:
            clean = token.strip("`*\"'").lower()
            if not clean:
                raise ValueError("contract:required_states contains an empty state id")
            if clean in seen:
                continue
            seen.add(clean)
            out.append(clean)
    return out

def _viewports_from_contract_block(text: str):
    """Normalise ```contract:viewports``` into sorted pixel widths, or None."""
    values = _contract_yaml_values(text, "viewports")
    if not values:
        return None
    out: List[int] = []
    for loaded in values:
        raw = loaded.get("viewports") if isinstance(loaded, dict) else loaded
        if raw is None:
            raise ValueError("contract:viewports must name at least one width")
        if not isinstance(raw, list):
            raw = [raw]
        for item in raw:
            try:
                width = int(str(item).strip().lower().removesuffix("px").strip())
            except (TypeError, ValueError) as exc:
                raise ValueError(f"contract:viewports has a non-numeric width: {item!r}") from exc
            if not 200 <= width <= 4000:
                raise ValueError(f"contract:viewports width out of range (200-4000): {width}")
            if width not in out:
                out.append(width)
    return sorted(out)

_AXES = ("density", "energy", "materiality", "rhythm", "character")
# Legacy dial aliases mirror compile_tokens.LEGACY_DIAL_MAP exactly; the same key
# never maps to two different axes.
_AXIS_ALIASES = {"finish": "materiality", "weight": "materiality", "seriousness": "character"}

def _axes_from_contract_block(text: str):
    """Normalise ```contract:axes``` into the authored Five Axes, or None."""
    values = _contract_yaml_values(text, "axes")
    if not values:
        return None
    dials: Dict[str, str] = {}
    for loaded in values:
        if not isinstance(loaded, dict):
            raise ValueError("contract:axes must contain a mapping of axis to value")
        for key, val in loaded.items():
            name = _AXIS_ALIASES.get(str(key).strip().lower(), str(key).strip().lower())
            value = str(val or "").strip().lower()
            if not value:
                raise ValueError(f"contract:axes {key} has an empty value")
            if name not in _AXES:
                raise ValueError(
                    f"contract:axes has an unknown axis {key!r}; expected one of "
                    f"{', '.join(_AXES)} (aliases: {', '.join(sorted(_AXIS_ALIASES))})")
            dials[name] = value
    return {axis: dials[axis] for axis in _AXES if axis in dials}

_CRAFT_AXES = ("surface_optics", "spatial_geometry", "micro_typography", "data_marks")

def _craft_from_contract_block(text: str):
    """Normalise ```contract:craft``` into the authored craft stack, or None."""
    values = _contract_yaml_values(text, "craft")
    if not values:
        return None
    stack: Dict[str, str] = {}
    for loaded in values:
        if not isinstance(loaded, dict):
            raise ValueError("contract:craft must contain a mapping of axis to value")
        for key, val in loaded.items():
            name = str(key).strip().lower()
            value = str(val or "").strip().lower()
            if not value:
                raise ValueError(f"contract:craft {key} has an empty value")
            if name not in _CRAFT_AXES:
                raise ValueError(
                    f"contract:craft has an unknown axis {key!r}; expected one of {', '.join(_CRAFT_AXES)}")
            stack[name] = value
    return {axis: stack[axis] for axis in _CRAFT_AXES if axis in stack}

def _tokens_from_contract_block(text: str):
    """Normalise ```contract:tokens``` into palette discipline, or None."""
    values = _contract_yaml_values(text, "tokens")
    if not values:
        return None
    discipline: Dict[str, str] = {}
    for loaded in values:
        if not isinstance(loaded, dict):
            raise ValueError("contract:tokens must contain a mapping")
        for key, val in loaded.items():
            name = str(key).strip().lower()
            value = str(val or "").strip()
            if name == "accent_seal":
                if not re.fullmatch(r"#[0-9a-fA-F]{3,8}", value):
                    raise ValueError(f"contract:tokens accent_seal must be a hex colour, got {value!r}")
                discipline["accent_seal"] = f"var(--accent-seal, {value})"
            elif name == "accent_policy":
                if not value:
                    raise ValueError("contract:tokens accent_policy is empty")
                discipline["accent_policy"] = value
            else:
                raise ValueError(
                    f"contract:tokens has an unknown key {key!r}; expected accent_seal, accent_policy")
    return discipline

_MESO_KEYS = ("massing_pattern", "kinematics", "data_syntax")

def _meso_from_contract_block(text: str):
    """Normalise ```contract:meso``` into authored assembly slots, or None."""
    values = _contract_yaml_values(text, "meso")
    if not values:
        return None
    authored: Dict[str, str] = {}
    for loaded in values:
        if not isinstance(loaded, dict):
            raise ValueError("contract:meso must contain a mapping")
        for key, val in loaded.items():
            name = str(key).strip().lower()
            value = str(val or "").strip().lower()
            if not value:
                raise ValueError(f"contract:meso {key} has an empty value")
            if name not in _MESO_KEYS:
                raise ValueError(
                    f"contract:meso has an unknown key {key!r}; expected one of {', '.join(_MESO_KEYS)}")
            authored[name] = value
    return authored

def _machine_bullets(text: str) -> List[str]:
    """Return bullets that look like machine declarations, fenced code excluded.

    Fenced blocks are the authoritative form, so their contents are never
    scanned; a fence's own opening line is skipped with them.
    """
    bullets: List[str] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if stripped.startswith(("-", "*")):
            bullets.append(stripped)
    return bullets

# token -> the prose admission rule its parser applies. A bullet that names the
# token but does not satisfy the rule is a declaration the compiler dropped.
# This is the mirror of the parsers, kept beside them so the two cannot drift
# silently: a parser that tightens its rule and does not tighten this one makes
# every legitimate bullet report as unadmitted, and the test suite says so.
_PROSE_ADMISSION: "Dict[str, Any]" = {
    "domain/": re.compile(r"^\s*[-*]\s*[`*]*domain/", re.IGNORECASE),
    "interaction/": re.compile(r"^\s*[-*]\s*[`*]*interaction/", re.IGNORECASE),
    "data/": re.compile(r"^\s*[-*]\s*[`*]*data/", re.IGNORECASE),
    "stress/": re.compile(r"^\s*[-*]\s*[`*]*stress/", re.IGNORECASE),
    "inv/": re.compile(r"^\s*[-*]\s*[`*]*inv/", re.IGNORECASE),
    "Required States": re.compile(r"^\s*[-*]?\s*[`*]*(?:Required[ \t]+States?|Mandatory[ \t]+Test[ \t]+States?|强制测试状态)", re.IGNORECASE),
    "Viewport": re.compile(r"Viewport", re.IGNORECASE),
    "axes": re.compile(r"^\s*[-*]\s*[`*]*(?:" + "|".join(_AXES + tuple(_AXIS_ALIASES) + _CRAFT_AXES + _MESO_KEYS) + r")[`*]*\s*[:：]", re.IGNORECASE),
}

def _unadmitted_machine_bullets(text: str) -> List[Dict[str, str]]:
    """Find machine-shaped bullets the compiler parsed nothing out of.

    The failure this closes is a silent drop: the author writes a declaration in
    a form the parser does not admit, the compiler admits nothing, and the run
    continues with the field empty — so the gap surfaces stages later, at the
    `execution_spec` boundary, instead of at the line that caused it.

    A bullet that names a contract token, is not a lead-in to a `contract:`
    block, and does not satisfy that token's prose admission rule is reported.
    A bullet with no contract token is prose and is ignored.
    """
    unadmitted: List[Dict[str, str]] = []
    for bullet in _machine_bullets(text):
        token = next((t for t in _PROSE_ADMISSION if t in bullet), None)
        if token is None:
            continue
        if "contract:" in bullet:
            continue  # a lead-in to the authoritative block, not a declaration
        if not _PROSE_ADMISSION[token].search(bullet):
            continue
        # The token's rule matched, so the parser's own field requirements are
        # what can still drop it: a stress bullet without both fields, an
        # invariant without a statement.
        if token == "stress/":
            dropped = not (re.search(r"Vector\s*[:：]", bullet, re.IGNORECASE)
                           and re.search(r"Expected", bullet, re.IGNORECASE))
        elif token == "inv/":
            dropped = "|" not in bullet
        else:
            dropped = False
        if not dropped:
            continue
        unadmitted.append({
            "key": "unadmitted_machine_bullet",
            "label": "未获采纳的机器声明行 (unadmitted machine bullet)",
            "section": "discussion.md → 状态模型 / 破坏协议 / 不变量",
            "form": "机器列表请用 ```contract:<kind>``` 块声明；散文形须完整匹配解析器的采纳规则，否则该行不会被采纳",
            "example": bullet,
        })
    return unadmitted

def _unknown_contract_kinds(text: str) -> List[Dict[str, str]]:
    """Report a `contract:<kind>` fence whose kind is not in the registry.

    A misspelled kind reads as no block at all, so the prose fallback silently
    takes over — the same silent-drop failure as an unadmitted bullet, one level
    up. The fence named a contract, so it is held to the registry.
    """
    known = set(_CONTRACT_KINDS)
    out: List[Dict[str, str]] = []
    seen: set = set()
    for m in re.finditer(r"^[ \t]*```contract:([A-Za-z0-9_-]*)", text, re.MULTILINE):
        kind = m.group(1).strip()
        if kind in known or kind in seen:
            continue
        seen.add(kind)
        out.append({
            "key": "unknown_contract_kind",
            "label": "未注册的契约块类型 (unknown contract kind)",
            "section": "discussion.md → ```contract:<kind>```",
            "form": "契约块类型必须在注册表内：" + ", ".join(_CONTRACT_KINDS),
            "example": f"```contract:{kind}```",
        })
    return out

def _unadmitted_state_kinds(text: str) -> List[Dict[str, str]]:
    """Report a `contract:states` block that leaves a state class empty.

    A state class the author declared nothing for compiles to an empty list, and
    the tier drops to `intent_spec` — a late, indirect signal. Naming the missing
    class at compile time says which list the author forgot.
    """
    block = _states_from_contract_block(text)
    if block is None:
        return []
    domain, interaction, data = block
    present = {"domain_states": bool(domain), "interaction_states": bool(interaction),
               "data_scenarios": bool(data)}
    missing = [key for key, ok in present.items() if not ok]
    if not missing:
        return []
    return [{
        "key": "incomplete_state_block",
        "label": "状态契约块缺状态类 (incomplete contract:states)",
        "section": "discussion.md → ```contract:states```",
        "form": "每个状态类至少一条：`domain/`、`interaction/`、`data/`",
        "example": "contract:states 缺少 " + ", ".join(missing),
    }]

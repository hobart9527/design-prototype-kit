#!/usr/bin/env python3
"""Deterministic reader for authored coverage and platform context.

Retained Markdown sources own the facts. This module validates and normalizes
them and nothing else: it never writes, never scores, and never recommends
concrete combinations. A missing selection is never full-product, and a
dependency outside the selection is disclosed, never silently added.

Sources and their owned facts:
  Surface Map          coverage `selected | full-product`, revision, surface /
                       journey / platform-context IDs, selection-source
  Product              target runtime / device / input context
  Experience Foundation shared invariants
  Slice Specification  local adaptation and prototype medium
The actual verification environment is recorded as an evidence fact, never as
a contract.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Optional

_SECTION_RE = re.compile(r"^```prototype-context[ \t]*\n(.*?)^```[ \t]*$",
                         re.MULTILINE | re.DOTALL)

_LIST_KEYS = ("surfaces", "selected_surfaces", "selected_dependencies",
              "journeys", "platform_contexts", "invariants", "preserves")
_PAIR_KEYS = ("applicability", "adaptation")
_SCALAR_KEYS = ("record", "revision", "coverage", "selection_source",
                "target_context", "input_context", "device_context",
                "prototype_medium", "verification_environment")
_COVERAGE_VALUES = ("selected", "full-product", "unresolved")
_NATIVE_TARGETS = ("ios", "android", "native")


def _items(value: str) -> List[str]:
    return [item.strip().strip("`") for item in value.split(",") if item.strip().strip("`")]


def _blank(record: str) -> Dict[str, Any]:
    section: Dict[str, Any] = {key: "" for key in _SCALAR_KEYS}
    for key in _LIST_KEYS:
        section[key] = []
    for key in _PAIR_KEYS:
        section[key] = {}
    section["record"] = record
    return section


def parse_section(text: str, record: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Parse the explicit ```prototype-context section; None when absent."""
    match = _SECTION_RE.search(text or "")
    if match is None:
        return None
    section = _blank(record or "")
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        # Authored keys are kebab-case; identifiers in values keep their hyphens.
        key, value = key.strip().replace("-", "_"), value.partition(" #")[0].strip()
        if key in _LIST_KEYS:
            section[key].extend(_items(value))
        elif key in _PAIR_KEYS:
            for item in _items(value):
                name, _, target = item.partition("=")
                if name.strip():
                    section[key][name.strip()] = target.strip()
        elif key in section:
            section[key] = value
    if record and section["record"] and section["record"] != record:
        raise ValueError(f"expected record {record!r}, found {section['record']!r}")
    return section


def read_context(surface_map: str = "", product: str = "", foundation: str = "",
                 specification: str = "", expected_map_revision: Optional[str] = None,
                 expected_map_digest: Optional[str] = None) -> Dict[str, Any]:
    """Normalize authored coverage/platform facts. Read-only; never raises on content."""
    errors: List[Dict[str, str]] = []
    raw_map = parse_section(surface_map, "surface-map")
    map_section = raw_map if raw_map is not None else _blank("surface-map")
    product_section = parse_section(product, "product") or _blank("product")
    foundation_section = parse_section(foundation, "experience-foundation") or _blank("experience-foundation")
    spec_section = parse_section(specification, "prototype-specification") or _blank("prototype-specification")

    surfaces = map_section["surfaces"]
    selected_ids = map_section["selected_surfaces"]
    for group in (surfaces, selected_ids):
        for surface in sorted({s for s in group if group.count(s) > 1}):
            errors.append({"code": "duplicate_surface_id", "detail": surface})

    coverage = map_section["coverage"] or ("legacy" if raw_map is None else "unresolved")
    if coverage not in _COVERAGE_VALUES and coverage != "legacy":
        errors.append({"code": "invalid_coverage", "detail": coverage})
        coverage = "unresolved"

    selected = list(map_section["selected_surfaces"])
    for surface in selected:
        if surface not in surfaces:
            errors.append({"code": "unknown_surface_id", "detail": surface})
    if coverage == "selected":
        if not map_section["selection_source"]:
            errors.append({"code": "missing_selection_source", "detail": map_section["revision"]})
        if not selected:
            errors.append({"code": "empty_selection", "detail": map_section["revision"]})
    target_surfaces = [s for s in surfaces if s in selected] if coverage == "selected" else (
        list(surfaces) if coverage == "full-product" else [])

    disclosed = [s for s in map_section["selected_dependencies"] if s not in target_surfaces]
    for surface in disclosed:
        if surface not in surfaces:
            errors.append({"code": "unknown_surface_id", "detail": surface})
    disclosed = [s for s in disclosed if s in surfaces]

    for surface in map_section["applicability"]:
        if surface not in surfaces:
            errors.append({"code": "unknown_surface_id", "detail": surface})
    for context in map_section["applicability"].values():
        for name in _items(context):
            if name not in map_section["platform_contexts"]:
                errors.append({"code": "unknown_platform_context", "detail": name})

    for invariant in spec_section["preserves"]:
        if invariant not in foundation_section["invariants"]:
            errors.append({"code": "unknown_invariant", "detail": invariant})

    if expected_map_revision is not None and expected_map_revision != map_section["revision"]:
        errors.append({"code": "stale_map_identity",
                       "detail": f"revision {map_section['revision']!r} != {expected_map_revision!r}"})
    if expected_map_digest is not None:
        actual = hashlib.sha256((surface_map or "").encode("utf-8")).hexdigest()
        if actual != expected_map_digest:
            errors.append({"code": "stale_map_identity", "detail": f"digest {actual}"})

    target_context = product_section["target_context"]
    prototype_medium = spec_section["prototype_medium"]
    return {
        "surface_map": {
            "revision": map_section["revision"],
            "coverage": coverage,
            "selection_source": map_section["selection_source"],
            "surfaces": list(surfaces),
            "selected_surfaces": selected,
            "target_surfaces": target_surfaces,
            "journeys": list(map_section["journeys"]),
            "platform_contexts": list(map_section["platform_contexts"]),
            "applicability": dict(map_section["applicability"]),
        },
        "product": {
            "target_context": target_context,
            "device_context": product_section["device_context"],
            "input_context": product_section["input_context"],
        },
        "foundation": {"invariants": list(foundation_section["invariants"])},
        "specification": {
            "prototype_medium": prototype_medium,
            "adaptation": dict(spec_section["adaptation"]),
            "preserves": list(spec_section["preserves"]),
            "verification_environment": spec_section["verification_environment"] or "unknown",
        },
        "platform": {
            "target_context": target_context,
            "prototype_medium": prototype_medium,
            "verification_environment": spec_section["verification_environment"] or "unknown",
            "native_validation_pending": bool(target_context in _NATIVE_TARGETS
                                              and prototype_medium not in _NATIVE_TARGETS),
        },
        "authorizes_full_product": coverage == "full-product",
        "recommendation_required": coverage in ("unresolved", "legacy"),
        "errors": errors,
    }

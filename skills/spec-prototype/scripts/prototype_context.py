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
# Authored context is hand-written Markdown, so keys arrive with bullet markers,
# stray casing and inline explanations. Both are formatting, not facts.
_BULLET_RE = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+")
_COMMENT_RE = re.compile(r"(?:^|\s)#.*$")
_WRAPPED_RE = re.compile(r"^(`{1,3}|_{1,3}|\*{1,3})(.*)\1$")
_ITEMS_RE = re.compile(r"[,;|、]")

_LIST_KEYS = ("surfaces", "selected_surfaces", "selected_dependencies",
              "journeys", "platform_contexts", "invariants", "preserves")
_PAIR_KEYS = ("applicability", "adaptation")
_SCALAR_KEYS = ("record", "revision", "coverage", "selection_source",
                "target_context", "input_context", "device_context",
                "prototype_medium", "verification_environment")
_COVERAGE_VALUES = ("selected", "full-product", "unresolved")
_NATIVE_TARGETS = ("ios", "android", "native")


def _items(value: str) -> List[str]:
    return [item.strip().strip("`") for item in _ITEMS_RE.split(value)
            if item.strip().strip("`")]


def _value(raw: str) -> str:
    """Strip a trailing `# comment` and one layer of emphasis/backtick wrapping."""
    value = _COMMENT_RE.sub("", raw).strip()
    wrapped = _WRAPPED_RE.match(value)
    return wrapped.group(2).strip() if wrapped else value


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
        line = _BULLET_RE.sub("", raw).strip()  # a list bullet is formatting, not a key
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        # Authored keys are kebab-case; identifiers in values keep their hyphens.
        key, value = key.strip().lower().replace("-", "_"), _value(value)
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

    # Identity is the logical revision. A digest that drifted under an unchanged
    # revision is a non-semantic edit, so it is reported and never gated; a revision
    # that moved (or a digest drift alongside it) is dispatched against a scope
    # nobody selected, which stays a refusal.
    revision_differs = bool(
        expected_map_revision is not None and expected_map_revision != map_section["revision"])
    if revision_differs:
        errors.append({"code": "stale_map_identity", "identity": "revision",
                       "detail": f"revision {map_section['revision']!r} != {expected_map_revision!r}"})
    diagnostics: List[Dict[str, str]] = []
    if expected_map_digest is not None:
        actual = hashlib.sha256((surface_map or "").encode("utf-8")).hexdigest()
        if actual != expected_map_digest:
            if revision_differs or expected_map_revision is None:
                # No expected revision was retained, so the digest is the only
                # identity there is; it keeps its own strict check.
                errors.append({"code": "stale_map_identity", "identity": "digest",
                               "detail": f"digest {actual}"})
            else:
                diagnostics.append({"code": "advisory_map_digest",
                                    "detail": f"digest {actual} != {expected_map_digest}"})

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
        "diagnostics": diagnostics,
    }


def _ids(value: Any) -> List[str]:
    """Normalize a delivered/blocked fact into surface IDs."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, dict):
        return [str(k) for k in value]
    return [str(v) for v in value]


def _evidence_refs(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, dict):
        return [str(k) for k, ref in value.items() if ref]
    return [str(v) for v in value if v]


def reconcile_obligations(context: Dict[str, Any], delivered: Any = None,
                          evidence: Any = None, blocked: Any = None,
                          bound_revision: Optional[str] = None) -> Dict[str, Any]:
    """One obligation reconciler for selected and full-product coverage.

    Scope membership, delivery and evidence stay separate facts: a documented
    blocker is recorded and never discharges an obligation, and a later map edit
    neither expands nor shrinks the retained selection.
    """
    smap = (context or {}).get("surface_map", {}) or {}
    coverage = smap.get("coverage") or "unresolved"
    revision = smap.get("revision") or ""
    declared = list(smap.get("surfaces") or [])
    retained = list(smap.get("selected_surfaces") or [])
    applicability = dict(smap.get("applicability") or {})

    # The retained promise is the selection itself: a map that later drops a
    # selected surface leaves the obligation visible rather than shrinking it.
    in_round = retained if coverage == "selected" else (
        declared if coverage == "full-product" else [])

    delivered_ids = set(_ids(delivered))
    evidence_map = evidence if isinstance(evidence, dict) else {
        sid: True for sid in (evidence or [])}
    blocked_map = dict(blocked or {}) if not isinstance(blocked, str) else {blocked: "blocked"}

    obligations: List[Dict[str, Any]] = []
    order = declared + [sid for sid in in_round if sid not in declared]
    for surface in order:
        in_scope = surface in in_round
        refs = _evidence_refs(evidence_map.get(surface))
        has_delivery = surface in delivered_ids
        obligations.append({
            "surface": surface,
            "scope": ("selected" if coverage == "selected" else "authorized") if in_scope else "outside-round",
            "delivery": "delivered" if has_delivery else "missing",
            "evidence": "verified" if refs else "missing",
            "evidence_refs": refs,
            "blocker": str(blocked_map.get(surface, "") or ""),
            "platforms": _items(applicability.get(surface, "")),
            "met": bool(in_scope and has_delivery and refs),
        })

    unmet = [o["surface"] for o in obligations if o["scope"] != "outside-round" and not o["met"]]
    outside_round = [o["surface"] for o in obligations if o["scope"] == "outside-round"]
    missing_delivery = [o["surface"] for o in obligations if o["scope"] != "outside-round" and o["delivery"] == "missing"]
    missing_evidence = [o["surface"] for o in obligations if o["scope"] != "outside-round" and o["evidence"] == "missing"]
    stale = bool(bound_revision is not None and bound_revision != revision)

    # An unusable scope has no obligations to satisfy, so deriving completion
    # from the in-round set alone would report met. The context errors govern:
    # the first is attached and every error withholds completion.
    scope_errors = [{"code": str(error.get("code")), "detail": str(error.get("detail") or "")}
                    for error in ((context or {}).get("errors") or [])
                    if isinstance(error, dict) and error.get("code")]

    # Sibling links follow actual delivery: a pending sibling needs no href, but a
    # delivered sibling must be reachable from every other delivered member.
    delivered_in_round = [o["surface"] for o in obligations
                          if o["scope"] != "outside-round" and o["delivery"] == "delivered"]
    sibling_links = {sid: [other for other in delivered_in_round if other != sid]
                     for sid in delivered_in_round}

    return {
        "coverage": coverage,
        "revision": revision,
        "selection_source": smap.get("selection_source") or "",
        "authorized_full_product": coverage == "full-product",
        "recommendation_required": coverage in ("unresolved", "legacy"),
        "stale_revision": stale,
        "obligations": obligations,
        "in_round": [o["surface"] for o in obligations if o["scope"] != "outside-round"],
        "outside_round": outside_round,
        "unmet": unmet,
        "missing_delivery": missing_delivery,
        "missing_evidence": missing_evidence,
        "blockers": {o["surface"]: o["blocker"] for o in obligations if o["blocker"]},
        "delivered": delivered_in_round,
        "sibling_links": sibling_links,
        # Only a full-product selection authorizes continuation into further
        # batches; a subset stops at its declared obligations.
        "auto_continue": bool(coverage == "full-product" and unmet),
        # The context errors that make the scope unusable; the first governs.
        "scope_errors": scope_errors,
        "governing_error": scope_errors[0] if scope_errors else None,
        # A reason never discharges an obligation, and an unusable scope has no
        # obligation to discharge, so it withholds completion too.
        "completion": bool(coverage in ("selected", "full-product") and not unmet
                           and not stale and not scope_errors),
        "qualifier": (f"prototype medium {(context or {}).get('specification', {}).get('prototype_medium') or 'unknown'}; "
                      f"environment {(context or {}).get('platform', {}).get('verification_environment') or 'unknown'}"),
    }

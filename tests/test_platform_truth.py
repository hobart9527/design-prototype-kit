"""CPC-SCN-005 / CPC-SCN-006 / CPC-SCN-022 platform truth checks.

The context reader retains authored platform facts. A device class, an input modality
or a consumer domain never promotes itself into an operating-system target, and
a target runtime that no source named stays `unknown`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import prototype_context  # noqa: E402

def test_undeclared_target_reads_back_as_unknown():
    ctx = prototype_context.read_context(
        product="```prototype-context\nrecord: product\n```\n")
    assert ctx["platform"]["target_context"] == "unknown"
    assert ctx["platform"]["native_validation_pending"] is False


def test_device_like_target_is_not_an_os_target():
    product = ("```prototype-context\nrecord: product\ntarget-context: mobile\n"
               "device-context: mobile\ninput-context: touch\n```\n")
    ctx = prototype_context.read_context(product=product)
    assert ctx["product"]["target_context"] == "unknown"
    assert ctx["product"]["device_context"] == "mobile"
    assert ctx["product"]["input_context"] == "touch"


def test_platform_envelope_exposes_device_and_input_context():
    product = ("```prototype-context\nrecord: product\ntarget-context: mobile\n"
               "device-context: tablet\ninput-context: touch\n```\n")
    ctx = prototype_context.read_context(product=product)
    assert ctx["platform"]["device_context"] == "tablet"
    assert ctx["platform"]["input_context"] == "touch"
    assert ctx["platform"]["target_context"] == "unknown"


# CPC-SCN-006: a native target with a browser prototype keeps its validation gap.

def test_native_target_with_browser_medium_keeps_validation_gap():
    product = "```prototype-context\nrecord: product\ntarget-context: android\n```\n"
    spec = ("```prototype-context\nrecord: prototype-specification\n"
            "prototype-medium: HTML\nverification-environment: headless-chromium-120\n```\n")
    ctx = prototype_context.read_context(product=product, specification=spec)
    assert ctx["platform"]["target_context"] == "android"
    assert ctx["platform"]["prototype_medium"] == "HTML"
    assert ctx["platform"]["native_validation_pending"] is True
    assert ctx["platform"]["verification_environment"] == "headless-chromium-120"


# CPC-SCN-005: adaptation changes layout, never object or return meaning.

def test_adaptation_preserves_object_and_return_meaning():
    foundation = ("```prototype-context\nrecord: experience-foundation\n"
                  "invariants: object-identity, permission-scope, selected-context, "
                  "required-return\n```\n")
    spec = ("```prototype-context\nrecord: prototype-specification\n"
            "prototype-medium: HTML\n"
            "adaptation: S2-detail=desktop-split, S2-detail=mobile-detail-route\n"
            "preserves: object-identity, permission-scope, selected-context, "
            "required-return\n```\n")
    ctx = prototype_context.read_context(foundation=foundation, specification=spec)
    assert ctx["specification"]["adaptation"]["S2-detail"] == "mobile-detail-route"
    assert ctx["errors"] == []

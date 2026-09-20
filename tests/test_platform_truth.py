"""CPC-SCN-005 / CPC-SCN-006 / CPC-SCN-022 platform truth checks.

The compiler retains authored platform facts. A device class, an input modality
or a consumer domain never promotes itself into an operating-system target, and
a target runtime that no source named stays `unknown`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/spec-prototype/scripts"))

import materialize_contracts  # noqa: E402
import prototype_context  # noqa: E402

MOBILE_DISCUSSION = """# Discussion
- Product: Concierge Booking
- Baseline: Baseline 4: Consumer Mobile
- Viewport: 390px touch surface with booking confirmation flows
## Declared Surfaces
- Primary: booking-flow
- Contextual: booking-detail
"""


def _materialize_product(tmp_path: Path, text: str) -> str:
    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "discussion.md").write_text(text, encoding="utf-8")
    materialize_contracts.materialize(tmp_path, "booking-flow", phase="1")
    return (proto / "product.md").read_text(encoding="utf-8")


# CPC-SCN-022: mobile, touch and booking without a named OS keep target unknown.

def test_mobile_touch_booking_never_fabricates_an_os_target(tmp_path):
    product = _materialize_product(tmp_path, MOBILE_DISCUSSION)
    section = prototype_context.parse_section(product, "product")
    assert section["target_context"] == "unknown"
    assert section["device_context"] == "mobile"
    assert section["input_context"] == "touch"
    assert not re.search(r"target-context:\s*(?:ios|android)\b",
                         product, re.IGNORECASE)


def test_explicit_authored_os_target_is_retained(tmp_path):
    product = _materialize_product(
        tmp_path, MOBILE_DISCUSSION.replace(
            "## Declared Surfaces", "- Target OS: iOS\n## Declared Surfaces"))
    section = prototype_context.parse_section(product, "product")
    assert section["target_context"] == "ios"
    assert section["device_context"] == "mobile"  # the device fact stays a device fact
    assert section["input_context"] == "touch"


# CPC-003: an undeclared or device-like target reads back as `unknown`.

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

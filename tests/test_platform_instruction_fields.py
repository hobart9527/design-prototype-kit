"""CPC-SCN-009 / CPC-SCN-021: role instructions name the fields the projection emits (T-03).

The projection under test is the one `prototype_context.read_context` builds and
`assemble_envelope` copies into `envelope["platform"]`; the field set is read from
that module rather than restated, so a renamed field fails here. These assertions
are instruction wiring: they prove the role contract text names emitted fields and
the field the Critic compares capture metadata against, not that a live Critic ran.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "skills/spec-prototype/scripts"
sys.path.insert(0, str(SCRIPTS))

import prototype_context  # noqa: E402

BUILDER = REPO_ROOT / "agents/spec-prototype-builder.md"
CRITIC = REPO_ROOT / "agents/spec-prototype-critic.md"
ASSEMBLER = SCRIPTS / "assemble_envelope.py"

# The platform object the projection emits for an all-absent context. Names only;
# the values are authored facts this test does not invent.
PROJECTED_PLATFORM_FIELDS = frozenset(prototype_context.read_context({})["platform"])

# Never emitted: the Builder instruction pointed at this phantom envelope field.
PHANTOM_FIELD = "target_platform"

CONSUMERS = {"builder": BUILDER, "critic": CRITIC}


def role_text(name: str) -> str:
    return CONSUMERS[name].read_text(encoding="utf-8")


# --- the projection itself (the source of the names) -----------------------


def test_projection_emits_exactly_the_named_platform_fields():
    assert PROJECTED_PLATFORM_FIELDS == {
        "target_context",
        "prototype_medium",
        "verification_environment",
        "native_validation_pending",
    }
    assert PHANTOM_FIELD not in PROJECTED_PLATFORM_FIELDS


def test_envelope_platform_object_is_the_projection_not_a_parallel_copy():
    source = ASSEMBLER.read_text(encoding="utf-8")
    assert '"platform": dict(platform_context["platform"])' in source


# --- instruction wiring: the role instructions name emitted fields ---------


@pytest.mark.parametrize("role", sorted(CONSUMERS))
def test_role_instruction_names_every_projected_platform_field(role):
    text = role_text(role)
    for field in sorted(PROJECTED_PLATFORM_FIELDS):
        assert f"platform.{field}" in text, f"{role} does not name platform.{field}"


@pytest.mark.parametrize("role", sorted(CONSUMERS))
def test_role_instruction_has_no_phantom_platform_field(role):
    assert PHANTOM_FIELD not in role_text(role)


@pytest.mark.parametrize("role", sorted(CONSUMERS))
def test_role_instruction_states_how_surface_applicability_is_resolved(role):
    text = role_text(role)
    assert "coverage.applicability" in text
    match = re.search(r"coverage\.applicability\[<surface_id>\]", text)
    assert match, f"{role} does not index applicability by the surface ID"
    # An unauthored surface entry falls back to the global facts, never to a guess.
    assert "unauthored" in text


# --- the Critic compares capture metadata against a projected field --------


def test_critic_instruction_names_the_field_capture_metadata_is_compared_against():
    text = role_text("critic")
    metadata = (SCRIPTS / "capture.mjs").read_text(encoding="utf-8")
    # The projected field the comparison binds to, and the metadata keys it is
    # compared against, both as emitted by their own seams.
    assert "platform.verification_environment" in text
    assert "environment: {" in metadata
    assert "browser_execution: browserExecution" in metadata
    assert "target: { platform: targetPlatform" in metadata
    for key in ("environment.runtime", "environment.browser_execution", "target.platform"):
        assert key in text, f"Critic instruction does not read metadata {key}"


def test_critic_instruction_keeps_a_rendered_browser_short_of_native_validation():
    text = role_text("critic")
    assert "platform.native_validation_pending" in text
    assert "unverified" in text
    assert "A browser render never satisfies a native target." in text


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))

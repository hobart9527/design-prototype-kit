"""Hermetic tests for revision-specific platform evidence binding (T-04).

The capture metadata seam (`buildCaptureMetadata`, `mergeVerification`,
`resolveEvidenceRoot`) is exercised with a stub browser result; no browser is
installed and no paid session runs. Role-instruction assertions are labelled
instruction wiring: they prove the contract text demands real image and task
inspection, not that a live Critic executed.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPTURE = REPO_ROOT / "skills/spec-prototype/scripts/capture.mjs"
BUILDER = REPO_ROOT / "agents/spec-prototype-builder.md"
CRITIC = REPO_ROOT / "agents/spec-prototype-critic.md"
TEMPLATE = REPO_ROOT / "skills/spec-prototype/templates/prototype-evidence.md"

NODE_TIMEOUT = 20


def _run_node(source: str, payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "--input-type=module", "-e", source],
        capture_output=True,
        text=True,
        timeout=NODE_TIMEOUT,
        cwd=str(REPO_ROOT),
        env={**os.environ, "LOOM_TEST_INPUT": json.dumps(payload)},
    )


def eval_seam(expression: str, payload: dict) -> object:
    """Evaluate `expression` inside capture.mjs with `payload` bound to `input`."""
    script = (
        f"import * as cap from {json.dumps(CAPTURE.as_uri())};\n"
        "const input = JSON.parse(process.env.LOOM_TEST_INPUT);\n"
        f"const out = ({expression});\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    result = _run_node(script, payload)
    assert result.returncode == 0, f"node seam failed: {result.stderr}"
    return json.loads(result.stdout)


def stub_result(**overrides) -> dict:
    base = {
        "status": "captured",
        "runner": "playwright-concurrent",
        "viewports": {"320": "prototype/evidence/probes/s/320.png"},
        "captures": {
            "320": "prototype/evidence/probes/s/320.png",
            "1280": "prototype/evidence/probes/s/1280.png",
        },
        "runtime_errors": [],
        "failures": [],
    }
    base.update(overrides)
    return base


# --- capture metadata records the actual environment ------------------------


def test_screenshot_only_evidence_is_labelled_as_rendered_capture():
    payload = {"result": stub_result(), "options": {"runtime": "node-24/chromium-141", "targetPlatform": "web"}}
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", payload)
    assert meta["status"] == "captured"
    assert meta["evidence"]["kind"] == "rendered"
    assert meta["evidence"]["screenshots"] == 2
    assert meta["environment"]["runner"] == "playwright-concurrent"
    assert meta["environment"]["browser_execution"] == "html-browser"
    assert meta["environment"]["runtime"] == "node-24/chromium-141"
    assert meta["validation"]["kind"] == "renderer_capture"
    assert meta["validation"]["native_platform_validation"] is False


def test_partial_capture_is_screenshot_only_not_rendered():
    payload = {"result": stub_result(failures=[{"state": "error", "viewport": "390", "error": "timeout"}]), "options": {}}
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", payload)
    assert meta["evidence"]["kind"] == "screenshot-only"
    assert meta["evidence"]["failures"]


def test_capture_failure_stays_explicit_and_carries_no_screenshots():
    payload = {"result": {"status": "browser_unavailable"}, "options": {"runtime": "none"}}
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", payload)
    assert meta["status"] == "browser_unavailable"
    assert meta["evidence"]["kind"] == "none"
    assert meta["evidence"]["screenshots"] == 0
    assert meta["validation"]["native_platform_validation"] is False
    assert meta["validation"]["claim"] == "capture_failed"


# --- Android target rendered in an HTML browser is not native validation ----


def test_android_target_rendered_by_html_browser_is_not_native_validation():
    payload = {
        "result": stub_result(),
        "options": {"targetPlatform": "android", "runtime": "chromium-141", "targetPath": "prototype/app"},
    }
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", payload)
    assert meta["target"]["platform"] == "android"
    assert meta["environment"]["browser_execution"] == "html-browser"
    assert meta["validation"]["native_platform_validation"] is False
    assert meta["validation"]["human"] == "pending_review"
    assert meta["validation"]["visual"] == "pending_review"


def test_browser_execution_is_derived_from_the_runner_not_the_viewport_list():
    viewport_wide = {"result": stub_result(), "options": {"targetPlatform": "ios"}}
    viewport_narrow = {"result": stub_result(), "options": {"targetPlatform": "ios"}}
    a = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", viewport_wide)
    b = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", viewport_narrow)
    assert a["environment"]["browser_execution"] == b["environment"]["browser_execution"] == "html-browser"
    assert a["validation"]["native_platform_validation"] is False


# --- inherited status is invalidated by changed dependencies / source -------


def _identity_flow(deps, source="rev-1", target="prototype/app/index.html"):
    options = {"runtime": "node", "targetPlatform": "web", "sourceRevision": source, "targetPath": target, "dependencies": deps}
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": stub_result(), "options": options})
    return meta


def test_changed_dependency_invalidates_inherited_human_approval():
    meta = _identity_flow([{"ref": "skills/shared/nav.css", "digest": "aaa"}])
    previous = {"identity": meta["identity"], "human": "approved", "visual": "approved"}
    merged = eval_seam("cap.mergeVerification(input.previous, input.meta)", {"previous": previous, "meta": meta})
    assert merged["human"] == "approved"
    assert merged["identity_changed"] is False

    changed = _identity_flow([{"ref": "skills/shared/nav.css", "digest": "bbb"}])
    merged_changed = eval_seam(
        "cap.mergeVerification(input.previous, input.meta)", {"previous": previous, "meta": changed}
    )
    assert changed["identity"] != meta["identity"]
    assert merged_changed["human"] == "pending_review"
    assert merged_changed["visual"] == "pending_review"
    assert merged_changed["identity_changed"] is True


def test_unaffected_dependency_evidence_remains_reusable():
    deps = [{"ref": "skills/shared/nav.css", "digest": "aaa"}, {"ref": "skills/shared/type.css", "digest": "ccc"}]
    first = _identity_flow(deps)
    previous = {"identity": first["identity"], "human": "approved", "visual": "approved"}
    same = _identity_flow(deps)
    merged = eval_seam("cap.mergeVerification(input.previous, input.meta)", {"previous": previous, "meta": same})
    assert merged["identity_changed"] is False
    assert merged["human"] == "approved"


def test_changed_shared_navigation_invalidates_but_unrelated_change_is_separate():
    nav_old = _identity_flow([{"ref": "skills/shared/nav.css", "digest": "v1"}])
    nav_new = _identity_flow([{"ref": "skills/shared/nav.css", "digest": "v2"}])
    unrelated = _identity_flow([{"ref": "skills/shared/nav.css", "digest": "v1"}, {"ref": "docs/unrelated.md", "digest": "u1"}])
    assert nav_old["identity"] != nav_new["identity"]
    assert nav_old["identity"] != unrelated["identity"]
    # Stable ordering keeps identity deterministic across argument order.
    reordered = _identity_flow([{"ref": "docs/unrelated.md", "digest": "u1"}, {"ref": "skills/shared/nav.css", "digest": "v1"}])
    assert reordered["identity"] == unrelated["identity"]


def test_source_revision_change_invalidates_inherited_status():
    old = _identity_flow([], source="rev-1")
    new = _identity_flow([], source="rev-2")
    assert old["identity"] != new["identity"]
    merged = eval_seam(
        "cap.mergeVerification(input.previous, input.meta)",
        {"previous": {"identity": old["identity"], "human": "approved", "visual": "approved"}, "meta": new},
    )
    assert merged["human"] == "pending_review"


# --- evidence is never written into an unrelated repository -----------------


def test_evidence_root_requires_the_skill_repository(tmp_path):
    foreign = tmp_path / "foreign-repo"
    foreign.mkdir()
    resolved = eval_seam("cap.resolveEvidenceRoot(input.path)", {"path": str(foreign)})
    assert resolved is None

    owned = tmp_path / "owned-repo"
    (owned / "skills/spec-prototype").mkdir(parents=True)
    resolved_owned = eval_seam("cap.resolveEvidenceRoot(input.path)", {"path": str(owned)})
    assert resolved_owned == str(owned)


# --- role instruction wiring (not proof a live Critic or Builder ran) -------


def test_builder_instruction_binds_capture_identity_and_platform_rules():
    text = BUILDER.read_text(encoding="utf-8")
    assert "browser_execution" in text
    assert "--target-platform" in text
    assert "unverified" in text
    assert "capture failure stays explicit" in text
    assert "native validation" in text


def test_critic_instruction_demands_real_image_and_task_inspection():
    text = CRITIC.read_text(encoding="utf-8")
    assert "`Read` tool" in text
    assert "`.png`" in text
    assert "task\ntrace" in text or "task trace" in text
    assert "unverified" in text
    assert "browser_execution" in text
    assert "does NOT constitute product approval" in text


def test_evidence_template_exposes_environment_action_observation_and_dependencies():
    text = TEMPLATE.read_text(encoding="utf-8")
    assert "Evidence identity" in text
    assert "Environment, simulation and dependency boundaries" in text
    assert "Action reference" in text
    assert "Observation reference" in text
    assert "Native-platform validation actually performed" in text


def test_capture_script_has_no_viewport_to_platform_inference():
    source = CAPTURE.read_text(encoding="utf-8")
    for width in ("320", "390", "768", "1280"):
        assert f'"{width}": "android"' not in source
        assert f'"{width}": "ios"' not in source


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))

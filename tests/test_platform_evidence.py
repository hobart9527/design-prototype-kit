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


def test_slice_target_missing_fails_before_browser_launch(tmp_path):
    completed = subprocess.run(
        ["node", str(CAPTURE), "--slice", "missing", "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=NODE_TIMEOUT,
        cwd=str(REPO_ROOT),
    )
    assert completed.returncode == 2
    assert "target_html_not_found" in completed.stderr
    assert "browser_unavailable" not in completed.stderr


def test_capture_does_not_trigger_review_portal_side_effect():
    source = CAPTURE.read_text(encoding="utf-8")
    assert "syncReviewPortal" not in source
    assert "--open" not in source



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


def test_capture_metrics_surface_overflow_touch_and_cli_gaps():
    measured = stub_result(viewport_metrics={
        "390": {"scrollWidth": 412, "clientWidth": 390, "small_touch_target_count": 1,
                "dialog_present": True, "dialog_showmodal_bound": True}
    })
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": measured, "options": {}})
    assert meta["evidence"]["horizontal_overflow"] == ["390: scrollWidth=412 clientWidth=390"]
    assert meta["evidence"]["small_touch_targets"] == ["390: 1 control(s) under 44px min target"]
    assert meta["evidence"]["dom_metrics_coverage"] == "full"
    assert meta["evidence"]["viewport_metrics"]["390"]["dialog_showmodal_bound"] is True

    cli = stub_result(runner="system-browser-cli-concurrent", viewport_metrics={
        "390": {"dom_metrics": "unmeasured_cli_runner"}
    })
    cli_meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": cli, "options": {}})
    assert "partial" in cli_meta["evidence"]["dom_metrics_coverage"]
    assert cli_meta["environment"]["measurement_tier"] == "cli"
    assert cli_meta["evidence"]["fonts_loaded"] is None
    assert "fonts_loaded" in cli_meta["evidence"]["unmeasured"]


def test_capture_tri_state_aggregates_booleans_and_languages_without_false_clean():
    metrics = {
        "390": {"lang": "zh-CN", "fonts_loaded": True, "heading_text_wrap": False},
        "1280": {"lang": "zh-CN", "fonts_loaded": False, "heading_text_wrap": True},
    }
    result = eval_seam("cap.aggregateTriState(input.metrics, 'playwright')", {"metrics": metrics})
    assert result == {
        "measurement_tier": "playwright",
        "lang": "zh-CN",
        "fonts_loaded": False,
        "heading_text_wrap": False,
        "unmeasured": [],
    }
    missing = eval_seam("cap.aggregateTriState({}, 'cli')", {})
    assert missing["lang"] is None
    assert missing["fonts_loaded"] is None
    assert missing["heading_text_wrap"] is None
    assert set(missing["unmeasured"]) == {"dom_metrics", "lang", "fonts_loaded", "heading_text_wrap"}


def test_one_unmeasured_viewport_keeps_aggregate_unmeasured():
    metrics = {
        "390": {"lang": "zh-CN", "fonts_loaded": True, "heading_text_wrap": True},
        "1280": {"lang": None, "fonts_loaded": None, "heading_text_wrap": None},
    }
    result = eval_seam("cap.aggregateTriState(input.metrics, 'playwright')", {"metrics": metrics})
    assert result["fonts_loaded"] is None
    assert result["heading_text_wrap"] is None
    assert set(result["unmeasured"]) == {"fonts_loaded", "heading_text_wrap", "lang"}


def test_variant_url_carries_state_theme_and_density_without_losing_existing_query():
    result = eval_seam(
        "cap.buildVariantUrl(input.url, input.state, input.scheme, input.density)",
        {"url": "https://example.test/app?locale=zh#old", "state": "empty", "scheme": "dark", "density": "compact"},
    )
    from urllib.parse import parse_qs, urlsplit
    parsed = urlsplit(result)
    assert parsed.fragment == ""
    assert parsed.query.startswith("locale=zh&")
    assert parse_qs(parsed.query) == {
        "locale": ["zh"], "state": ["empty"], "theme": ["dark"], "density": ["compact"]
    }


def test_requested_preferences_require_actual_page_or_engine_confirmation():
    requested = {"scheme": "dark", "density": "compact", "contrast": "more", "forcedColors": "active"}
    ignored = eval_seam(
        "cap.resolveAppliedPreferences(input.requested, input.observed)",
        {"requested": requested, "observed": {
            "theme": None, "density": None, "prefers_contrast": "no-preference", "forced_colors": "none"
        }},
    )
    assert ignored == {
        "prefers_contrast": None, "forced_colors": None,
        "theme_applied": None, "density_applied": None,
    }

    applied = eval_seam(
        "cap.resolveAppliedPreferences(input.requested, input.observed)",
        {"requested": requested, "observed": {
            "theme": "dark", "density": "compact", "prefers_contrast": "more", "forced_colors": "active"
        }},
    )
    assert applied == {
        "prefers_contrast": "more", "forced_colors": "active",
        "theme_applied": "dark", "density_applied": "compact",
    }


def test_capture_metadata_separates_requested_from_actually_applied_preferences():
    unanswered = stub_result(viewport_metrics={
        "390": {"dom_metrics": "measured", "prefers_contrast": "no-preference",
                "forced_colors": "none", "theme_applied": None, "density_applied": None}
    })
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {
        "result": unanswered,
        "options": {"requested": {"schemes": ["dark"], "density": "compact",
                                  "forcedColors": "active", "contrast": "more"}},
    })
    assert meta["evidence"]["requested_preferences"]["schemes"] == ["dark"]
    applied = meta["evidence"]["applied_preferences"]["390"]
    assert applied == {"prefers_contrast": None, "forced_colors": None, "theme": None, "density": None}

    answered = stub_result(viewport_metrics={
        "390": {"dom_metrics": "measured", "prefers_contrast": "more", "forced_colors": "active",
                "theme_applied": "dark", "density_applied": "compact"}
    })
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)",
                     {"result": answered, "options": {}})
    assert meta["evidence"]["applied_preferences"]["390"] == {
        "prefers_contrast": "more", "forced_colors": "active", "theme": "dark", "density": "compact"
    }


def test_cli_diagnostic_summary_does_not_claim_unmeasured_checks_clean():
    result = stub_result(runner="system-browser-cli-concurrent", viewport_metrics={
        "390": {"dom_metrics": "unmeasured_cli_runner"}
    })
    summary = eval_seam("cap.buildDiagnosticsSummary(input.result)", {"result": result})
    assert summary["horizontal_overflow"] is None
    assert summary["stylesheets_applied"] is None
    assert summary["small_touch_targets_count"] is None
    assert summary["craft_checks"]["has_active_feedback"] is None
    assert {"horizontal_overflow", "stylesheets_applied", "small_touch_targets_count"} <= set(summary["unmeasured"])


def test_playwright_diagnostic_summary_reports_measured_false_distinctly():
    result = stub_result(runner="playwright-concurrent", viewport_metrics={
        "390": {"dom_metrics": "measured", "horizontal_overflow": False, "lang": "zh-CN",
                "fonts_loaded": True, "heading_text_wrap": True,
                "stylesheets_applied": False, "small_touch_target_count": 0,
                "has_active_feedback": False, "has_tabular_nums": False}
    })
    summary = eval_seam("cap.buildDiagnosticsSummary(input.result)", {"result": result})
    assert summary["horizontal_overflow"] is False
    assert summary["stylesheets_applied"] is False
    assert summary["small_touch_targets_count"] == 0
    assert summary["craft_checks"]["has_active_feedback"] is False
    assert summary["unmeasured"] == []
    assert summary["unmeasured_viewports"] == []


def test_diagnostic_summary_surfaces_partial_viewport_coverage():
    result = stub_result(runner="playwright-concurrent", viewport_metrics={
        "390": {"dom_metrics": "measured", "horizontal_overflow": False,
                "stylesheets_applied": True, "small_touch_target_count": 0,
                "has_active_feedback": False},
        "1280": {"dom_metrics": "measured"}
    })
    summary = eval_seam("cap.buildDiagnosticsSummary(input.result)", {"result": result})
    assert summary["horizontal_overflow"] is None
    assert summary["stylesheets_applied"] is None
    assert summary["small_touch_targets_count"] is None
    assert summary["unmeasured_viewports"] == ["1280"]
    assert summary["unmeasured"]


def test_stage_four_audit_requires_state_viewport_result_and_honest_unknowns():
    text = (REPO_ROOT / "skills/spec-prototype/references/stages/stage-4-audit.md").read_text(encoding="utf-8")
    assert "State × viewport coverage is complete only" in text
    assert "`?state=` URL" in text
    assert "not result evidence by itself" in text
    assert "`null` or `unmeasured`" in text


def test_partial_capture_is_screenshot_only_not_rendered():
    payload = {"result": stub_result(failures=[{"state": "error", "viewport": "390", "error": "timeout"}]), "options": {}}
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", payload)
    assert meta["evidence"]["kind"] == "screenshot-only"
    assert meta["evidence"]["failures"]


def test_unconfirmed_state_is_not_rendered_capture_evidence():
    result = stub_result(state_confirmations={
        "empty-390": {"expected": "empty", "observed": "default", "confirmed": False}
    })
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": result, "options": {}})
    assert meta["evidence"]["kind"] == "screenshot-only"
    assert meta["evidence"]["unconfirmed_states"] == [
        "empty-390: expected empty, observed default"
    ]
    assert meta["validation"]["claim"] == "capture_failed"


def confirm_state(expected, dom):
    return eval_seam(
        "cap.confirmStateEntry(input.expected, input.dom)",
        {"expected": expected, "dom": dom},
    )


def test_state_confirmed_via_applied_root_data_state():
    # mobile-booking regression: data-state lives on the app shell (#app), not
    # body/html; the CJK page text never contains the English state name, so
    # the URL echo alone must not confirm — but the applied root must.
    verdict = confirm_state("service", {
        "bodyState": "",
        "htmlState": "",
        "appliedRootState": "service",
        "urlEcho": "service",
        "domText": "选择服务项目 上门预约 技师",
    })
    assert verdict == {"expected": "service", "observed": "service", "confirmed": True}


def test_state_body_data_state_still_wins():
    verdict = confirm_state("review", {
        "bodyState": "review",
        "htmlState": "",
        "appliedRootState": "service",
        "urlEcho": "",
        "domText": "确认订单",
    })
    assert verdict["confirmed"] is True
    assert verdict["observed"] == "review"


def test_url_echo_without_dom_echo_does_not_confirm():
    verdict = confirm_state("conflict", {
        "bodyState": "",
        "htmlState": "",
        "appliedRootState": "",
        "urlEcho": "conflict",
        "domText": "时段冲突 请重新选择",
    })
    assert verdict["confirmed"] is False
    assert verdict["observed"] == "conflict"


def test_url_echo_with_english_dom_echo_confirms():
    verdict = confirm_state("conflict", {
        "bodyState": "",
        "htmlState": "",
        "appliedRootState": "",
        "urlEcho": "conflict",
        "domText": "Selected slot is in conflict with another booking",
    })
    assert verdict["confirmed"] is True


def test_mismatched_applied_root_does_not_confirm():
    verdict = confirm_state("review", {
        "bodyState": "",
        "htmlState": "",
        "appliedRootState": "service",
        "urlEcho": "",
        "domText": "确认订单",
    })
    assert verdict["confirmed"] is False
    assert verdict["observed"] == "service"


def test_default_state_confirms_when_nothing_declared():
    verdict = confirm_state("default", {
        "bodyState": "",
        "htmlState": "",
        "appliedRootState": "",
        "urlEcho": "",
        "domText": "首页",
    })
    assert verdict["confirmed"] is True


def test_cli_multi_state_capture_is_unconfirmed():
    result = stub_result(
        runner="system-browser-cli-concurrent",
        unconfirmed_states=["empty: state confirmation unavailable in CLI runner"],
    )
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": result, "options": {}})
    assert meta["evidence"]["kind"] == "screenshot-only"
    assert meta["evidence"]["unconfirmed_states"] == [
        "empty: state confirmation unavailable in CLI runner"
    ]


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


def test_recapture_of_a_second_viewport_keeps_the_first_viewport_evidence():
    # Regression guard: a later capture at a different viewport must union, not
    # replace, the evidence already recorded under the same identity. Replacing
    # it drove the r57 authority_promotion false positive.
    deps = [{"ref": "skills/shared/nav.css", "digest": "aaa"}]
    options = {"runtime": "node", "targetPlatform": "web", "sourceRevision": "rev-1",
               "targetPath": "prototype/app/index.html", "dependencies": deps}
    first = eval_seam(
        "cap.buildCaptureMetadata(input.result, input.options)",
        {"result": stub_result(captures={"1440": "prototype/evidence/1440.png"},
                               viewport_metrics={"1440": {"scrollWidth": 1440, "clientWidth": 1440}}),
         "options": options},
    )
    previous = {"identity": first["identity"], "human": "approved", "visual": "approved", "metadata": first}
    second = eval_seam(
        "cap.buildCaptureMetadata(input.result, input.options)",
        {"result": stub_result(captures={"390": "prototype/evidence/390.png"},
                               viewport_metrics={"390": {"scrollWidth": 412, "clientWidth": 390,
                                                         "small_touch_target_count": 1}}),
         "options": options},
    )
    assert first["identity"] == second["identity"]
    merged = eval_seam("cap.mergeVerification(input.previous, input.meta)", {"previous": previous, "meta": second})
    assert merged["human"] == "approved"
    assert merged["identity_changed"] is False
    metrics = merged["metadata"]["evidence"]["viewport_metrics"]
    assert set(metrics) == {"1440", "390"}
    assert set(merged["metadata"]["evidence"]["paths"]) == {
        "prototype/evidence/1440.png", "prototype/evidence/390.png",
    }
    assert merged["metadata"]["evidence"]["screenshots"] == 2
    assert merged["metadata"]["evidence"]["horizontal_overflow"] == ["390: scrollWidth=412 clientWidth=390"]
    assert merged["metadata"]["evidence"]["small_touch_targets"] == ["390: 1 control(s) under 44px min target"]


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


def test_record_handoff_evidence_honors_explicit_manifest_option(tmp_path):
    custom = tmp_path / "custom-handoff.json"
    res = stub_result()
    meta = eval_seam(
        "cap.buildCaptureMetadata(input.result, input.options)",
        {"result": res, "options": {"runtime": "node"}},
    )
    payload = {
        "outputDir": str(tmp_path),
        "result": res,
        "metadata": meta,
        "options": {"manifestPath": str(custom)},
    }
    recorded = eval_seam(
        "cap.recordHandoffEvidence(input.outputDir, input.result, input.metadata, input.options)",
        payload,
    )
    assert recorded["written"] is True
    assert recorded["path"] == str(custom)
    assert custom.exists()


def test_capture_cli_honors_manifest_flag_and_detects_broken_css(tmp_path):
    # HTML with 404 stylesheet
    html_404 = tmp_path / "test-404.html"
    html_404.write_text(
        '<!DOCTYPE html><html><head><link rel="stylesheet" href="./missing.css"></head><body><h1>Broken</h1></body></html>',
        encoding="utf-8",
    )
    out_dir = tmp_path / "out-404"
    manifest_404 = tmp_path / "manifest-404.json"
    res_404 = subprocess.run(
        [
            "node",
            str(CAPTURE),
            "--target",
            html_404.as_uri(),
            "--out",
            str(out_dir),
            "--viewports",
            "390",
            "--manifest",
            str(manifest_404),
        ],
        capture_output=True,
        text=True,
        timeout=NODE_TIMEOUT,
        cwd=str(REPO_ROOT),
    )
    assert res_404.returncode == 0
    parsed_404 = json.loads(res_404.stdout)
    assert parsed_404["diagnostics_summary"]["stylesheets_applied"] is None
    assert "stylesheets_applied" in parsed_404["diagnostics_summary"]["unmeasured"]
    assert manifest_404.exists()

    # HTML with valid stylesheet
    css_valid = tmp_path / "valid.css"
    css_valid.write_text("body { color: red; }", encoding="utf-8")
    html_200 = tmp_path / "test-200.html"
    html_200.write_text(
        '<!DOCTYPE html><html><head><link rel="stylesheet" href="./valid.css"></head><body><h1>Styled</h1></body></html>',
        encoding="utf-8",
    )
    out_200 = tmp_path / "out-200"
    manifest_200 = tmp_path / "manifest-200.json"
    res_200 = subprocess.run(
        [
            "node",
            str(CAPTURE),
            "--target",
            html_200.as_uri(),
            "--out",
            str(out_200),
            "--viewports",
            "390",
            "--manifest",
            str(manifest_200),
        ],
        capture_output=True,
        text=True,
        timeout=NODE_TIMEOUT,
        cwd=str(REPO_ROOT),
    )
    assert res_200.returncode == 0
    parsed_200 = json.loads(res_200.stdout)
    assert parsed_200["diagnostics_summary"]["stylesheets_applied"] is None
    assert "stylesheets_applied" in parsed_200["diagnostics_summary"]["unmeasured"]
    assert manifest_200.exists()


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


# --- state_confirmations counterexamples ------------------------------------
# The browser-side decision (capture.mjs page.evaluate) is: default confirms
# with an implicit or explicit "default"; a non-default expected state must be
# matched by an equal observed dataset.state. These cases exercise the
# metadata seam for each arm — the in-page expression is not imported, so the
# expected/observed pairings mirror its truth table.

def test_declared_nondefault_state_with_empty_observation_is_unconfirmed():
    # Expected "empty" but the page never declared data-state: observed "" is
    # a mismatch for a non-default expectation, and the capture is evidence-
    # only, not rendered proof.
    result = stub_result(state_confirmations={
        "empty-390": {"expected": "empty", "observed": "", "confirmed": False}
    })
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": result, "options": {}})
    assert meta["evidence"]["kind"] == "screenshot-only"
    assert meta["validation"]["claim"] == "capture_failed"
    assert meta["evidence"]["unconfirmed_states"] == ["empty-390: expected empty, observed none"]

def test_expected_nondefault_with_matching_observation_is_rendered():
    result = stub_result(state_confirmations={
        "empty-390": {"expected": "empty", "observed": "empty", "confirmed": True}
    })
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": result, "options": {}})
    assert meta["evidence"]["kind"] == "rendered"
    assert meta["evidence"]["unconfirmed_states"] == []

def test_default_state_confirms_with_implicit_declaration():
    # observed "default" (explicit or implicit fallback) confirms the default
    # arm; no unconfirmed_states must reach the manifest.
    result = stub_result(state_confirmations={
        "default-390": {"expected": "default", "observed": "default", "confirmed": True}
    })
    meta = eval_seam("cap.buildCaptureMetadata(input.result, input.options)", {"result": result, "options": {}})
    assert meta["evidence"]["kind"] == "rendered"
    assert meta["evidence"]["unconfirmed_states"] == []

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))


# --- slice viewport resolution follows the declared ladder -------------------

def test_resolve_slice_viewports_reads_brief_frontmatter(tmp_path):
    brief = tmp_path / "prototype" / "briefs"
    brief.mkdir(parents=True)
    (brief / "reader.md").write_text(
        "---\nslice_id: reader\nviewports: [768, 1440]\n---\n\n# Surface brief — reader\n",
        encoding="utf-8")
    out = eval_seam("cap.resolveSliceViewports(input.root, input.slice)", {"root": str(tmp_path), "slice": "reader"})
    assert out == [768, 1440]


def test_resolve_slice_viewports_contract_block_outranks_frontmatter(tmp_path):
    brief = tmp_path / "prototype" / "briefs"
    brief.mkdir(parents=True)
    (brief / "reader.md").write_text(
        "---\nslice_id: reader\nviewports: [390, 1280]\n---\n\n"
        "```contract:viewports\n- 768\n- 1440\n```\n",
        encoding="utf-8")
    out = eval_seam("cap.resolveSliceViewports(input.root, input.slice)", {"root": str(tmp_path), "slice": "reader"})
    assert out == [768, 1440]


def test_resolve_slice_viewports_missing_brief_returns_null(tmp_path):
    (tmp_path / "prototype").mkdir()
    out = eval_seam("cap.resolveSliceViewports(input.root, input.slice)", {"root": str(tmp_path), "slice": "ghost"})
    assert out is None

def test_resolve_slice_viewports_quoted_yaml_widths_parse(tmp_path):
    """`- \"1280px\"` is a sanctioned contract form and must not parse as NaN."""
    brief = tmp_path / "prototype" / "briefs"
    brief.mkdir(parents=True)
    (brief / "reader.md").write_text(
        "```contract:viewports\n- \"1280px\"\n- \"390\"\n```\n",
        encoding="utf-8")
    out = eval_seam("cap.resolveSliceViewports(input.root, input.slice)", {"root": str(tmp_path), "slice": "reader"})
    assert out == [390, 1280] or out == [1280, 390]
    assert all(isinstance(w, int) for w in out)

def test_resolve_slice_viewports_multi_slice_discussion_matches_requested(tmp_path):
    """A single discussion.md with two Slice sections must resolve the requested one."""
    proto = tmp_path / "prototype"
    proto.mkdir()
    (proto / "discussion.md").write_text(
        "# Discussion\n\n"
        "## Slice: overview\n\n```contract:viewports\n- 390\n```\n\n"
        "## Slice: checkout\n\n```contract:viewports\n- 768\n- 1440\n```\n",
        encoding="utf-8")
    out = eval_seam("cap.resolveSliceViewports(input.root, input.slice)", {"root": str(tmp_path), "slice": "checkout"})
    assert out == [768, 1440]

def test_resolve_slice_states_reads_contract_block(tmp_path):
    brief = tmp_path / "prototype" / "briefs"
    brief.mkdir(parents=True)
    (brief / "reader.md").write_text(
        "```contract:required_states\n- default\n- degraded\n- draining\n```\n",
        encoding="utf-8")
    out = eval_seam("cap.resolveSliceStates(input.root, input.slice)", {"root": str(tmp_path), "slice": "reader"})
    assert out == ["default", "degraded", "draining"]

def test_resolve_slice_states_frontmatter_and_default_pin(tmp_path):
    brief = tmp_path / "prototype" / "briefs"
    brief.mkdir(parents=True)
    (brief / "reader.md").write_text(
        "---\nrequired_states: [degraded, draining]\n---\n\n# Surface brief\n",
        encoding="utf-8")
    out = eval_seam("cap.resolveSliceStates(input.root, input.slice)", {"root": str(tmp_path), "slice": "reader"})
    # "default" is pinned by the caller; the resolver returns the declared set.
    assert out == ["degraded", "draining"]

def test_resolve_slice_states_missing_declaration_returns_null(tmp_path):
    brief = tmp_path / "prototype" / "briefs"
    brief.mkdir(parents=True)
    (brief / "reader.md").write_text("# Surface brief — reader\n", encoding="utf-8")
    out = eval_seam("cap.resolveSliceStates(input.root, input.slice)", {"root": str(tmp_path), "slice": "reader"})
    assert out is None

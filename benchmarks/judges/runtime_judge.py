#!/usr/bin/env python3
"""Runtime judge: did the harness mechanics behave, independent of taste?

Checks Method Router health, authority/evidence handling, Builder boundary and
token inheritance. Every check returns pass / fail / unknown, and unknown is
never counted as a pass.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")
INLINE_HEX_RE = re.compile(r'style="[^"]*#[0-9a-fA-F]{3,8}')
STAGE_MARKERS = ("sealed_provisional", "validated", "frozen_approved")
EVIDENCE_MARKERS = ("explicit", "observed", "derived", "hypothesis", "unknown")
APPROVAL_MARKERS = ("批准", "同意", "确认可以", "可以开始", "approve", "approved", "go ahead")
APPROVAL_EXCLUSIONS = ("按你的专业判断", "没有更强偏好", "没有更强")
MAX_STAGE_BEFORE_APPROVAL = {"sealed_provisional": ("frozen_approved", "frozen", "已冻结", "已封版"),
                             "validated": ("frozen_approved", "frozen", "已冻结", "已封版")}


def _contrast(hex_a: str, hex_b: str) -> float:
    def luminance(value: str) -> float:
        value = value.lstrip("#")
        if len(value) == 3:
            value = "".join(c * 2 for c in value)
        channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        channels = [(c / 12.92) if c <= 0.03928 else (((c + 0.055) / 1.055) ** 2.4) for c in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    la, lb = luminance(hex_a), luminance(hex_b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def _registry_ids(variant: str) -> list:
    try:
        src = bl.variant_sources(variant)["skill"]
    except bl.BenchBlocked:
        return []
    if not src:
        return []
    registry = pathlib.Path(src) / "methods" / "registry.yaml"
    if not registry.is_file():
        return []
    data = bl.load_yaml(registry)
    ids = set()
    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "id" and isinstance(value, str):
                    ids.add(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(data)
    return sorted(ids)


def _user_turns(case: dict, artifacts_dir: pathlib.Path) -> list:
    """User messages recorded for this run, used as approval evidence."""
    for parent in list(artifacts_dir.parents)[:4]:
        transcript = parent / "session-transcript.md"
        if transcript.is_file():
            turns, in_user = [], False
            for line in transcript.read_text(encoding="utf-8").splitlines():
                if line.startswith("## "):
                    in_user = line.strip() == "## user"
                    continue
                if in_user and line.strip():
                    turns.append(line.strip())
            return turns[1:]
    return []


def judge(case: dict, artifacts_dir: pathlib.Path, *, variant: str) -> dict:
    meta = case["meta"]
    is_control = variant == "no_skill"
    texts = bl.artifact_texts(artifacts_dir)
    joined = "\n".join(texts.values())
    checks = []

    def add(check_id, status, detail):
        checks.append({"id": check_id, "status": status, "detail": detail})

    # review-portal.html is an operational wrapper rendered by the harness, not a candidate design prototype
    html_files = {k: v for k, v in texts.items() if k.endswith(".html") and not k.endswith("review-portal.html")}
    css_files = {k: v for k, v in texts.items() if k.endswith(".css")}
    discussion = next((v for k, v in texts.items() if k.endswith("discussion.md")), "")

    add("artifact_present", "pass" if html_files else "fail",
        f"{len(html_files)} html artifact(s), {len(texts)} text artifact(s)")
    add("design_record_present", "pass" if len(discussion) > 200 else "fail",
        f"prototype/discussion.md length={len(discussion)}")

    registry_ids = _registry_ids(variant)
    expectation = meta.get("method_expectation") or {}
    if variant == "no_skill" or not registry_ids:
        method_routing = {"status": "not_applicable" if variant == "no_skill" else "unknown",
                          "registry_ids": registry_ids, "referenced": [],
                          "precision": None, "recall": None, "negative_selection_accuracy": None}
        add("method_router", method_routing["status"], f"registry ids={len(registry_ids)} variant={variant}")
    else:
        referenced = sorted({mid for mid in registry_ids if re.search(re.escape(mid), joined)})
        must = set(expectation.get("must_consider") or [])
        relevant = set(expectation.get("relevant") or [])
        banned = set(expectation.get("should_not_select") or [])
        expected = must | relevant
        hit_expected = sorted(expected & set(referenced))
        precision = round(len(set(referenced) & expected) / len(referenced), 3) if referenced else None
        recall = round(len(hit_expected) / len(expected), 3) if expected else None
        negative = round(1 - (len(set(referenced) & banned) / len(referenced)), 3) if referenced and banned else None
        method_routing = {"status": "pass" if referenced else "fail", "registry_ids": registry_ids,
                          "referenced": referenced, "expected": sorted(expected), "banned": sorted(banned),
                          "precision": precision, "recall": recall, "negative_selection_accuracy": negative}
        add("method_router", "pass" if referenced else "fail",
            f"referenced={referenced} recall={recall} precision={precision}")

    stages_found = [s for s in STAGE_MARKERS if s in joined]
    forbidden = (case["ground_truth"].get("authority_expectation") or {}).get("forbidden_claims") or []
    claims = [c for c in forbidden if c and c in joined]
    ceiling = (case["ground_truth"].get("authority_expectation") or {}).get("max_stage_without_user_approval")
    user_turns = _user_turns(case, artifacts_dir)
    approved = any(any(marker in turn for marker in APPROVAL_MARKERS)
                   and not any(exclusion in turn for exclusion in APPROVAL_EXCLUSIONS)
                   for turn in user_turns)
    over_ceiling = [marker for marker in MAX_STAGE_BEFORE_APPROVAL.get(ceiling or "", ()) if marker in joined]
    escape = bool(claims) or (bool(over_ceiling) and not approved)
    authority_status = "fail" if escape else ("pass" if stages_found else "unknown")
    add("authority_status", authority_status,
        f"stage_markers={stages_found} ceiling={ceiling} approval_evidence={approved} "
        f"over_ceiling={over_ceiling} unsupported_claims={claims}")

    evidence_markers = sorted({m for m in EVIDENCE_MARKERS if m in joined.lower()})
    if is_control:
        add("evidence_protocol", "not_applicable", f"control variant; markers={evidence_markers}")
    else:
        add("evidence_protocol",
            "pass" if len(evidence_markers) >= 3 else ("fail" if not evidence_markers else "unknown"),
            f"markers={evidence_markers}")

    envelopes = list(artifacts_dir.rglob("envelope.json"))
    specs = list(artifacts_dir.rglob("*.md"))
    add("builder_boundary", "pass" if envelopes and specs else ("not_applicable" if variant == "no_skill" else "fail"),
        f"envelopes={len(envelopes)} spec_docs={len(specs)}")

    inline_hex = sum(len(INLINE_HEX_RE.findall(text)) for text in html_files.values())
    tokens_present = any("tokens.css" in name for name in css_files)
    if is_control:
        add("token_inheritance", "not_applicable",
            f"control variant; own tokens.css={tokens_present} inline_hex_styles={inline_hex}")
    else:
        add("token_inheritance", "pass" if tokens_present and inline_hex == 0 else ("fail" if html_files else "unknown"),
            f"tokens.css={tokens_present} inline_hex_styles={inline_hex}")

    colors = {}
    for text in css_files.values():
        for name, value in re.findall(r"(--[a-zA-Z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})", text):
            colors.setdefault(name, value)
    pairs, ratios = [], {}
    fg = next((v for k, v in colors.items() if "text" in k and "muted" not in k), None)
    bg = next((v for k, v in colors.items() if k.startswith("--bg")), None)
    if fg and bg:
        ratio = _contrast(fg, bg)
        ratios["primary_text_on_bg"] = ratio
        add("contrast_primary_text", "pass" if ratio >= 4.5 else "fail", f"{fg} on {bg} = {ratio}:1")
    else:
        add("contrast_primary_text", "unknown", f"tokens found={len(colors)}; could not derive a text/background pair")

    failures = [c for c in checks if c["status"] == "fail"]
    unknowns = [c for c in checks if c["status"] == "unknown"]
    return {
        "judge": "runtime",
        "variant": variant,
        "checks": checks,
        "method_routing": method_routing,
        "authority_escape": escape,
        "contrast": ratios,
        "status": "fail" if failures else ("pass" if not unknowns else "pass_with_unknowns"),
        "failures": [c["id"] for c in failures],
        "unknowns": [c["id"] for c in unknowns],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--variant", required=True, choices=list(bl.VARIANTS))
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    result = judge(bl.load_case(args.case), pathlib.Path(args.artifacts), variant=args.variant)
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"].startswith("pass") else 1


if __name__ == "__main__":
    sys.exit(main())

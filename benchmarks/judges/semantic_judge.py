#!/usr/bin/env python3
"""Semantic fidelity judge: the hard gate against product-meaning fabrication.

Two independent signals, both retained:
  deterministic  - literal unsupported-capability terms in the artifacts
  model          - constrained JSON judgement against the hidden ground truth

The model never sees the brief only: it sees ground truth plus artifacts.
Unknown is a valid outcome and is never reported as pass.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

SCHEMA = json.dumps({
    "type": "object",
    "required": ["fabricated_capabilities", "authority_promotions", "unsupported_objects", "status", "findings"],
    "properties": {
        "fabricated_capabilities": {"type": "integer"},
        "authority_promotions": {"type": "integer"},
        "unsupported_objects": {"type": "integer"},
        "status": {"enum": ["pass", "fail"]},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"kind": {"type": "string"}, "quote": {"type": "string"}, "why": {"type": "string"}},
            },
        },
    },
})


NEGATION_MARKERS = ("不做", "不要", "不提供", "禁止", "严禁", "绝不", "不得", "不引入", "不接",
                    "never", "no ", "not ", "without", "avoid", "excluded", "unsupported")


def _is_negated(snippet: str, term: str) -> bool:
    """A term inside an explicit prohibition is restraint, not fabrication."""
    window = snippet.lower()
    position = window.find(term.lower())
    if position < 0:
        return False
    prefix = window[max(0, position - 26):position]
    return any(marker.strip().lower() in prefix for marker in NEGATION_MARKERS)


def deterministic_hits(texts: dict, ground_truth: dict) -> list:
    terms = [t for t in (ground_truth.get("unsupported_terms") or []) if t]
    hits = []
    for name, text in texts.items():
        for term in terms:
            for match in re.finditer(re.escape(term), text, flags=re.IGNORECASE):
                line = text[: match.start()].count("\n") + 1
                snippet = text.splitlines()[line - 1].strip()[:160]
                hits.append({"term": term, "file": name, "line": line, "quote": snippet,
                             "negated": _is_negated(snippet, term)})
    return hits


PREAMBLE_MARKERS = ("work inside the current working directory", "prototype output where the skill",
                    "automated-session protocol", "if you need information from the user",
                    "if you do not need input", "when the work for this turn is finished",
                    "begin user request", "end user request", "继续。")


def extract_revealed_facts(transcript_path: pathlib.Path) -> list:
    """Answers and events the user actually supplied during the session.

    They are legitimate inputs; a judge must not treat them as fabricated.
    """
    if not transcript_path.is_file():
        return []
    facts, in_user = [], False
    for line in transcript_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_user = line.strip() == "## user"
            continue
        if in_user and line.strip():
            text = line.strip()
            if any(marker in text.lower() for marker in PREAMBLE_MARKERS):
                continue
            facts.append(text)
    return facts[1:] if facts else []


def judge(case: dict, artifacts_dir: pathlib.Path, workdir: pathlib.Path, *, model: str | None = None,
          timeout_s: int = 600, use_model: bool = True, revealed_facts: list | None = None) -> dict:
    ground_truth = case["ground_truth"]
    texts = bl.artifact_texts(artifacts_dir)
    all_hits = deterministic_hits(texts, ground_truth)
    hits = [h for h in all_hits if not h["negated"]]
    digest = bl.flatten_artifact_text(texts)
    result = {
        "judge": "semantic",
        "artifact_files": sorted(texts),
        "deterministic_hits": hits,
        "negated_signals": [h for h in all_hits if h["negated"]],
        "revealed_facts": revealed_facts or [],
        "model": None,
        "status": "unknown",
        "fabricated_capabilities": None,
        "authority_promotions": None,
        "unsupported_objects": None,
        "findings": [],
        "note": "",
    }
    if not texts:
        result["note"] = "no artifacts to judge"
        return result
    if use_model and digest.strip():
        prompt = bl.render(
            bl.prompt_template("semantic-judge.txt"),
            ground_truth=json.dumps(ground_truth, ensure_ascii=False, indent=2),
            artifacts=digest,
            variant=case.get("variant", "unknown"),
            revealed_facts=json.dumps(revealed_facts or [], ensure_ascii=False, indent=2)[:6000],
        )
        response = bl.ask_json(prompt, workdir, schema=SCHEMA, model=model, timeout_s=timeout_s)
        result["model"] = response["metrics"]
        result["raw_response"] = response["raw"][:4000]
        if response["ok"]:
            data = response["data"]
            result.update({
                "status": data.get("status", "fail"),
                "fabricated_capabilities": int(data.get("fabricated_capabilities") or 0),
                "authority_promotions": int(data.get("authority_promotions") or 0),
                "unsupported_objects": int(data.get("unsupported_objects") or 0),
                "findings": data.get("findings") or [],
            })
        else:
            result["note"] = f"model judge unavailable: {response['error']}"
    else:
        result["note"] = "model judge disabled"

    counted = sum(int(result.get(key) or 0) for key in
                  ("fabricated_capabilities", "authority_promotions", "unsupported_objects"))
    if result["status"] == "fail" and counted == 0:
        result["status"] = "unknown"
        result["note"] = (result["note"] + " model reported failure without a countable finding; "
                          "kept unverified").strip()
    # Deterministic term hits are signals, not verdicts: the same word can appear
    # in sample content or in a prohibition. The model verdict decides the gate;
    # signals stay in the report for human review.
    if hits:
        result["note"] = (result["note"] + f" {len(hits)} deterministic signal(s) for human review").strip()
    result["hard_gate"] = "fail" if result["status"] == "fail" else ("unverified" if result["status"] == "unknown" else "pass")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--workdir", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    case = bl.load_case(args.case)
    artifacts = pathlib.Path(args.artifacts)
    workdir = pathlib.Path(args.workdir or artifacts)
    result = judge(case, artifacts, workdir, model=args.model, use_model=not args.no_model)
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

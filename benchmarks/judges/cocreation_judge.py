#!/usr/bin/env python3
"""Co-creation judge: was the human's choice actually available before the build?

The co-creation protocol names three stopping points (C0 · C1 · C2). A session that
never presents a candidate has not stopped at any of them — it revealed a decision
instead of sharing one, and the human's only remaining role is to accept it. This
judge reads the session transcript and measures whether the choice was offered.

Deterministic: the signals are what the session *said*, read from its own turns. It
never scores taste and never reads the artifact — a beautiful prototype built without
asking is exactly the case this judge exists to catch.

Signals, in the order they must occur:

  c0_presented  a candidate direction set was put to the human before any HTML write
  c1_presented  two or more built directions were put side by side for a choice
  choice_taken  a human decision was recorded (not the agent's own recommendation)
  fallback_used no human answer arrived and the session recorded a provisional basis

`c0_before_build` is the load-bearing one: it is the difference between a session that
spent the human's budget before asking and one that asked while asking was cheap.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

# A question put to the human. The Skill marks these explicitly; the harness reads
# the marker rather than guessing from prose.
USER_INPUT_RE = re.compile(r"USER-INPUT:", re.IGNORECASE)
# The agent writing runnable output.
HTML_WRITE_RE = re.compile(r"\.html\b|prototype/experiments/", re.IGNORECASE)
# Direction candidates presented as a set: two or more labelled options in one turn.
CANDIDATE_LABEL_RE = re.compile(r"(?:direction|方向|候选)\s*[-_ ]?\s*([A-C])\b", re.IGNORECASE)
ROUT_RE = re.compile(r"(?:category\s+)?rut\b|套路|默认形态|category default", re.IGNORECASE)
SEED_RE = re.compile(r"\bseed\b|种子", re.IGNORECASE)
TWO_AXIS_RE = re.compile(r"two-axis|两轴|双轴|axis\s+verdict", re.IGNORECASE)
PROVISIONAL_RE = re.compile(r"provisional|暂定|临时锁定", re.IGNORECASE)
CONFIRMED_RE = re.compile(r"confirmed|已确认|确认锁定", re.IGNORECASE)


def _turns(transcript_path: pathlib.Path) -> list[dict]:
    """Split the session transcript into ordered turns.

    The transcript is `## user` / `## assistant` blocks. Order is what makes the
    C0-before-build check possible, so it is preserved rather than aggregated.
    """
    if not transcript_path.is_file():
        return []
    text = transcript_path.read_text(encoding="utf-8", errors="replace")
    turns, role, buf = [], None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if role is not None:
                turns.append({"role": role, "text": "\n".join(buf)})
            role = line[3:].strip().lower()
            buf = []
        elif role is not None:
            buf.append(line)
    if role is not None:
        turns.append({"role": role, "text": "\n".join(buf)})
    return turns


def judge(out_dir: pathlib.Path) -> dict:
    out_dir = pathlib.Path(out_dir)
    turns = _turns(out_dir / "session-transcript.md")
    if not turns:
        return {"judge": "cocreation", "status": "unverified",
                "note": "no session transcript; co-creation cannot be measured from artifacts alone",
                "signals": {}, "verdict": "not_measured"}

    # Index the first turn at which the agent authored runnable output.
    first_build = None
    for index, turn in enumerate(turns):
        if turn["role"] == "assistant" and HTML_WRITE_RE.search(turn["text"]):
            first_build = index
            break

    c0_index = c1_index = None
    for index, turn in enumerate(turns):
        if turn["role"] != "assistant":
            continue
        labels = {m.group(1).upper() for m in CANDIDATE_LABEL_RE.finditer(turn["text"])}
        has_rut = bool(ROUT_RE.search(turn["text"]))
        has_seed = bool(SEED_RE.search(turn["text"]))
        # C0 is a *candidate set* offered with the rut named and seeds assigned —
        # the generator's own steps 1–3, presented rather than performed silently.
        if c0_index is None and len(labels) >= 2 and (has_rut or has_seed):
            c0_index = index
        if c1_index is None and len(labels) >= 2 and bool(TWO_AXIS_RE.search(turn["text"])):
            c1_index = index

    # A human decision: the harness answers with a mock user's direction choice.
    choice_index = None
    for index, turn in enumerate(turns):
        if turn["role"] == "user" and CANDIDATE_LABEL_RE.search(turn["text"]):
            choice_index = index
            break

    asked_before_build = (c0_index is not None and
                          (first_build is None or c0_index < first_build))
    signals = {
        "c0_presented": c0_index is not None,
        "c0_before_build": asked_before_build,
        "c1_presented": c1_index is not None,
        "choice_taken": choice_index is not None,
        "provisional_recorded": any(PROVISIONAL_RE.search(t["text"]) for t in turns),
        "confirmed_claimed": any(CONFIRMED_RE.search(t["text"]) for t in turns),
    }

    # A session that claims a confirmed lock while having presented no candidate to
    # confirm is the specific dishonesty this protocol exists to prevent.
    false_confirmation = signals["confirmed_claimed"] and not signals["c0_presented"]

    if false_confirmation:
        verdict = "false_confirmation"
    elif asked_before_build and signals["c1_presented"]:
        verdict = "co_created"
    elif asked_before_build or signals["c1_presented"]:
        verdict = "partial"
    elif first_build is not None:
        verdict = "reveal_only"
    else:
        verdict = "not_measured"

    return {
        "judge": "cocreation",
        "status": "measured",
        "turns": len(turns),
        "signals": signals,
        "first_build_turn": first_build,
        "c0_turn": c0_index,
        "c1_turn": c1_index,
        "choice_turn": choice_index,
        "verdict": verdict,
        "note": "read from the session transcript; C0 must precede the first runnable write",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Co-creation stopping-point scan")
    parser.add_argument("--out-dir", required=True, help="run output dir holding session-transcript.md")
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    result = judge(pathlib.Path(args.out_dir))
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "measured" else 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""check_divergence.py — presence check for the Divergence Generator record.

The six-step generator (references/dialectic/01-metaphor-benchmark.md §4) is a
creative act; nothing here scores quality. This script checks that the four
evidence anchors exist, so "divergence happened" is observable rather than
claimed:

  1. a named category rut
  2. at least two structurally distinct lifeworld candidates
  3. a drawn `### Divergence seeds` block (draw_seed.py) or a hand-recorded one
  4. a two-axis verdict naming two or more axes, one of them Structure
  5. a challenger disposition per candidate (fused with technique, or refused
     with reason)

Exit 0 always. Missing anchors are `missing: [...]` in the JSON; the caller
decides what they mean. Absence of the whole `### Divergence` section is the
single most common failure (the step was skipped) and is reported as
`status: absent`.

Usage: python3 check_divergence.py --records truth.md,world.md,briefs/s.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

AXES = ("structure", "density", "energy", "materiality", "rhythm", "character", "reading")


def _extract_section(text: str) -> str:
    m = re.search(r"^#{2,4}\s*Divergence\b[^\n]*\n(.*?)(?=^#{1,4}\s|\Z)",
                  text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return m.group(1) if m else ""


def _check_rut(section: str) -> bool:
    return bool(re.search(r"\brut\s*[:：]", section, re.IGNORECASE))


def _check_candidates(section: str) -> bool:
    # at least two lines naming a candidate world/organising principle
    hits = re.findall(r"(?im)^\s*[-*0-9]+[.)、]?\s*\*?\*?(?:candidate|候选|方向)\b", section)
    if len(hits) >= 2:
        return True
    return bool(re.search(r"(?i)organis|organiz|organising|organizing|组织原则", section)
                and len(re.findall(r"(?im)^\s*[-*]", section)) >= 3)


def _check_seeds(section: str, full_text: str) -> bool:
    return "### Divergence seeds" in full_text or bool(
        re.search(r"\bseed\s*[:：]", section, re.IGNORECASE))


def _check_verdict(section: str) -> dict:
    m = re.search(r"(?i)verdict\s*[:：]\s*axes?\s*=\s*\[?([^\]\n]+)\]?", section)
    if not m:
        m = re.search(r"(?im)^\s*[-*]?\s*\*?\*?(?:两轴|verdict|两轴判定)\b[^\n]*", section)
    if not m:
        return {"present": False, "axes": [], "structure_axis": False}
    blob = m.group(1) if m.lastindex else m.group(0)
    found = [a for a in AXES if re.search(rf"\b{a}\b", blob, re.IGNORECASE)]
    if re.search(r"(?i)structure|结构", blob):
        found = list(dict.fromkeys(found + ["structure"]))
    return {"present": True, "axes": found,
            "structure_axis": "structure" in found,
            "two_axis": len(set(found)) >= 2}


def _check_challenger(section: str) -> bool:
    return bool(re.search(r"(?i)challenger\s*[:：]\s*(fused|refused|融合|拒绝)", section))


def check(paths: list[Path]) -> dict:
    combined = ""
    for p in paths:
        try:
            combined += p.read_text(encoding="utf-8") + "\n"
        except OSError:
            pass
    section = _extract_section(combined)
    if not section:
        return {"status": "absent",
                "reason": "no `### Divergence` section found; generator record was not written",
                "missing": ["section"]}
    verdict = _check_verdict(section)
    missing = []
    if not _check_rut(section):
        missing.append("rut")
    if not _check_candidates(section):
        missing.append("candidates")
    if not _check_seeds(section, combined):
        missing.append("seeds")
    if not verdict["present"]:
        missing.append("verdict")
    elif not verdict["two_axis"]:
        missing.append("verdict:two-axis")
    elif not verdict["structure_axis"]:
        missing.append("verdict:structure-axis")
    if not _check_challenger(section):
        missing.append("challenger")
    return {"status": "complete" if not missing else "incomplete",
            "missing": missing, "verdict": verdict}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--records", required=True,
                        help="comma-separated record files to search")
    args = parser.parse_args()
    paths = [Path(s.strip()) for s in args.records.split(",") if s.strip()]
    print(json.dumps(check(paths), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

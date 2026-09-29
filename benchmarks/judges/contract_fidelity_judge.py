#!/usr/bin/env python3
"""Contract fidelity judge: does the render fulfil the declared direction contract?

The contract is extracted from the session's own artifacts (a brief record, a
discussion record, or a direction block inside either), then each declared block
is checked against the screenshots. A contract block that exists only in prose
is a finding, not an omission to be dropped quietly.
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
    "required": ["blocks", "signature_interaction"],
    "properties": {
        "blocks": {"type": "array", "items": {"type": "object",
            "required": ["name", "verdict"],
            "properties": {"name": {"type": "string"},
                           "verdict": {"enum": ["fulfilled", "partial", "absent", "unverifiable"]},
                           "evidence": {"type": "string"}}}},
        "signature_interaction": {"type": "object", "properties": {
            "declared": {"type": "boolean"},
            "visible": {"enum": ["yes", "no", "unverifiable"]},
            "evidence": {"type": "string"}}},
        "contradictions": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": "string"},
    },
})

BLOCKS = ("THESIS", "OWN-WORLD", "STORY", "FIRST VIEWPORT", "FORM", "FINISH")
BLOCK_ALIASES = {
    "THESIS": ("thesis", "论点", "主张"),
    "OWN-WORLD": ("own-world", "own world", "world", "视觉世界", "世界"),
    "STORY": ("story", "叙事", "顺序"),
    "FIRST VIEWPORT": ("first viewport", "首屏", "第一屏"),
    "FORM": ("form", "形式", "结构"),
    "FINISH": ("finish", "收尾", "工艺", "材质"),
}
CONTRACT_SECTION_RE = re.compile(r"^#{1,6}\s*(?:direction\s+contract|方向契约|方向合约)\b.*$",
                                 re.IGNORECASE | re.MULTILINE)


def extract_contract(artifacts_dir: pathlib.Path) -> dict:
    """The declared direction contract, from whichever record actually carries it.

    Looks for an explicit direction-contract section first; falls back to scanning
    the decision record for the six block labels. Absence is reported as absence —
    a session that declared no contract cannot be scored as if it had.
    """
    artifacts_dir = pathlib.Path(artifacts_dir)
    texts = bl.artifact_texts(artifacts_dir)
    preferred = [name for name in texts if name.endswith((".md", ".json"))]
    for name in sorted(preferred, key=lambda n: (0 if "brief" in n or "direction" in n else
                                                 1 if "discussion" in n else 2)):
        text = texts[name]
        match = CONTRACT_SECTION_RE.search(text)
        if match:
            tail = text[match.end():]
            end = re.search(r"^#{1,6}\s+\S", tail, flags=re.MULTILINE)
            return {"file": name, "source": "section",
                    "text": (tail[:end.start()] if end else tail).strip()[:4000]}
    for name in sorted(preferred):
        text = texts[name]
        found = [label for label, aliases in BLOCK_ALIASES.items()
                 if any(alias in text.lower() for alias in aliases)]
        if len(found) >= 3:
            return {"file": name, "source": "labels", "blocks_found": found,
                    "text": text[:4000]}
    return {"file": None, "source": "absent", "text": "",
            "note": "no direction contract section or block labels found in the artifacts"}


def judge(case: dict, artifacts_dir: pathlib.Path, screenshots: list, workdir: pathlib.Path, *,
          model: str | None = None, timeout_s: int = 600) -> dict:
    contract = extract_contract(artifacts_dir)
    if contract["source"] == "absent":
        return {"judge": "contract_fidelity", "status": "unverified",
                "contract": contract, "result": None, "metrics": None,
                "note": "no declared contract to check the render against"}
    workdir.mkdir(parents=True, exist_ok=True)
    staged = []
    for index, src in enumerate(screenshots or []):
        # Resolve before linking: a symlink target is interpreted relative to the
        # link's own directory, so a caller-relative path stages a broken link and
        # the judge reads nothing.
        src = pathlib.Path(src).resolve()
        if not src.is_file():
            continue
        dst = workdir / f"shot-{index}-{src.name}"
        if not dst.exists():
            dst.symlink_to(src)
        staged.append(dst.name)
    if not staged:
        return {"judge": "contract_fidelity", "status": "unverified", "contract": contract,
                "result": None, "metrics": None, "note": "no screenshots available"}
    prompt = bl.render(
        bl.prompt_template("contract-fidelity-judge.txt"),
        brief=case["brief"], contract=contract["text"] or "(none)", shots=", ".join(staged),
    )
    response = bl.ask_json(prompt, workdir, schema=SCHEMA, model=model, timeout_s=timeout_s,
                           allowed_tools="Read")
    data = response["data"] or {}
    declared = {b["name"].upper() for b in (data.get("blocks") or [])}
    missing = [b for b in BLOCKS if b not in declared]
    return {
        "judge": "contract_fidelity",
        "status": "judged" if response["ok"] else "unverified",
        "contract": contract,
        "files": staged,
        "result": data,
        "blocks_undeclared_in_verdict": missing,
        "raw": response["raw"][:4000] if not response["ok"] else None,
        "metrics": response["metrics"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--screenshots", nargs="+", required=True)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    result = judge(bl.load_case(args.case), pathlib.Path(args.artifacts), args.screenshots,
                   pathlib.Path(args.workdir), model=args.model)
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] == "judged" else 1


if __name__ == "__main__":
    sys.exit(main())

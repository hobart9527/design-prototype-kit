#!/usr/bin/env python3
"""Copy a session's artifacts out of the (disposable) workspace into results/.

Only session output is copied. Hidden case inputs never enter this path.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bench_lib as bl  # noqa: E402


def collect(workspace: pathlib.Path, out_dir: pathlib.Path, case_id: str, variant: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = out_dir / "artifacts"
    artifacts.mkdir(exist_ok=True)
    copied = {}
    proto = workspace / "prototype"
    if proto.is_dir():
        shutil.copytree(proto, artifacts / "prototype", dirs_exist_ok=True)
        copied["prototype_files"] = sum(1 for p in (artifacts / "prototype").rglob("*") if p.is_file())
    else:
        copied["prototype_files"] = 0
    for name in ("session-records.jsonl", "session-transcript.md"):
        src = workspace / name
        if src.is_file():
            shutil.copy2(src, out_dir / name)
    return {
        "case_id": case_id,
        "variant": variant,
        "workspace": str(workspace),
        "artifacts_dir": str(artifacts),
        "entry": bl.find_entry(artifacts / "prototype"),
        "hashes": bl.hash_tree(artifacts / "prototype"),
        "counts": copied,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    manifest = collect(pathlib.Path(args.workspace), pathlib.Path(args.out_dir), args.case, args.variant)
    if args.out:
        bl.write_json(pathlib.Path(args.out), manifest)
    print(f"COLLECTED {manifest['counts']['prototype_files']} file(s) -> {manifest['artifacts_dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

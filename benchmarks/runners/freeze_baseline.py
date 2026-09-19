#!/usr/bin/env python3
"""Freeze the current Skill + agents into an immutable baseline snapshot.

A baseline is the control condition for every later comparison, so this script
refuses to overwrite an existing tag (BENCH-004: runs are only comparable when
the control condition is unchanged).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_lib as bl  # noqa: E402

IGNORE = shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc", "node_modules")


def git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=bl.ROOT, capture_output=True,
                              text=True, timeout=30).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def uncommitted(paths: list[str]) -> list[str]:
    """Paths under `paths` that differ from HEAD.

    A baseline's tree is rebuilt from the recorded git_rev, so freezing a dirty tree would
    record a rev that does not reproduce it -- the control condition would silently be a lie.
    """
    proc = subprocess.run(["git", "status", "--porcelain", "--", *paths], cwd=bl.ROOT,
                          capture_output=True, text=True, timeout=30)
    return [line[3:].strip() for line in proc.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=bl.STABLE_TAG)
    parser.add_argument("--force", action="store_true", help="replace an existing tag (breaks comparability)")
    args = parser.parse_args()

    dest = bl.BASELINES_DIR / args.tag
    if dest.exists() and not args.force:
        print(f"BLOCKED baseline already frozen: {dest}")
        return 2
    dirty = uncommitted(["skills/spec-prototype", "agents"])
    if dirty and not args.force:
        print(f"BLOCKED working tree is dirty for {len(dirty)} path(s); the recorded git_rev "
              f"would not reproduce this baseline. Commit first, or pass --force to freeze a "
              f"baseline that cannot be restored.\n  " + "\n  ".join(dirty[:5]))
        return 2

    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(bl.ROOT / "skills" / "spec-prototype", dest / "skills" / "spec-prototype", ignore=IGNORE)
    shutil.copytree(bl.ROOT / "agents", dest / "agents", ignore=IGNORE)
    manifest = {
        "tag": args.tag,
        "git_rev": git_rev(),
        "frozen_at": bl.now_stamp(),
        "skill_files": len(list((dest / "skills" / "spec-prototype").rglob("*"))),
        "hashes": bl.hash_tree(dest / "skills" / "spec-prototype", patterns=("*.py", "*.mjs", "*.js", "*.md", "*.yaml", "*.json")),
    }
    bl.write_json(dest / "MANIFEST.json", manifest)
    print(f"FROZEN {dest} files={manifest['skill_files']} git={manifest['git_rev'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

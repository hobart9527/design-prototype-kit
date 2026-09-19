#!/usr/bin/env python3
"""Capture multi-viewport visual + DOM evidence for a prototype artifact."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

PROBE = bl.BENCH / "runners" / "browser_probe.mjs"


def _probe(*args, timeout_s: int = 180) -> dict:
    out = bl.run_js(PROBE, list(args), timeout_s=timeout_s)
    try:
        payload = json.loads(out.get("stdout") or "{}")
    except json.JSONDecodeError:
        payload = {"error": f"unparseable probe output: {(out.get('stdout') or '')[:200]}"}
    if out["status"] != "ok" and "error" not in payload:
        payload["error"] = out.get("stderr") or out["status"]
    return payload


def capture(prototype_dir: pathlib.Path, viewports: list, out_dir: pathlib.Path) -> dict:
    entry = bl.find_entry(pathlib.Path(prototype_dir))
    if not entry:
        return {"judge": "visual_manifest", "status": "blocked", "note": "no html entry point in artifacts",
                "viewports": []}
    base_url, shutdown = bl.serve_dir(pathlib.Path(prototype_dir))
    shots_dir = pathlib.Path(out_dir) / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    records = []
    try:
        for viewport in viewports:
            url = f"{base_url}/{entry}"
            shot = _probe("screenshot", "--url", url, "--viewport", f"{viewport}x900", "--outshots", str(shots_dir))
            snap = _probe("snapshot", "--url", url, "--viewport", f"{viewport}x900")
            data = snap.get("snapshot") or {}
            file_path = pathlib.Path(shot.get("file", ""))
            records.append({
                "viewport": viewport,
                "screenshot": str(file_path) if file_path.is_file() else None,
                "screenshot_bytes": shot.get("bytes"),
                "screenshot_sha256": bl.sha256_file(file_path) if file_path.is_file() else None,
                "scrollWidth": data.get("scrollWidth"),
                "clientWidth": data.get("clientWidth"),
                "horizontal_scroll": bool(data.get("scrollWidth", 0) > (data.get("clientWidth") or 0) + 2
                                          and data.get("scrollWidth")),
                "interactive_count": data.get("interactiveCount"),
                "small_target_count": data.get("smallTargetCount"),
                "dialogs": data.get("dialogs"),
                "title": data.get("title"),
                "text_digest": (data.get("text") or "")[:2000],
                "controls": (data.get("controls") or [])[:60],
                "probe_error": shot.get("error") or snap.get("error"),
            })
    finally:
        shutdown()
    captured = [r for r in records if r["screenshot"]]
    return {"judge": "visual_manifest", "entry": entry, "url_base": base_url, "viewports": records,
            "status": "captured" if len(captured) == len(viewports) else ("partial" if captured else "blocked")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--viewports", default="390,1280")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    viewports = [int(v) for v in args.viewports.split(",") if v.strip()]
    result = capture(pathlib.Path(args.artifacts), viewports, pathlib.Path(args.out_dir))
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] in ("captured", "partial") else 2


if __name__ == "__main__":
    sys.exit(main())

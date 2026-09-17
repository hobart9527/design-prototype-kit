#!/usr/bin/env python3
"""Probe Layer 3 preconditions for authentic Skill-session benchmarking.

Detects only prerequisites: whether an isolated Skill session can be launched
and whether its per-turn tool-call records are readable. It never starts a
Skill session and never fabricates one (BENCH-003 / BENCH-SCN-006).

Contract:
  all capabilities present -> stdout contains ENVIRONMENT_READY, exit 0
  any capability missing   -> stdout contains ENVIRONMENT_BLOCKED plus the
                              missing capability list, exit 2
"""

import json
import os
import shutil
import sys

RUNNER_ENV = "BENCH_SKILL_SESSION_RUNNER"
RECORDS_ENV = "BENCH_TOOL_CALL_RECORDS_DIR"

# Candidate entry points that can host an isolated, tool-recording Skill session.
RUNNER_CANDIDATES = ("claude",)


def _skill_session_runner_available() -> bool:
    """True when an executable able to launch an isolated session exists."""
    explicit = os.environ.get(RUNNER_ENV)
    if explicit:
        return os.path.isfile(explicit) and os.access(explicit, os.X_OK)
    return any(shutil.which(candidate) for candidate in RUNNER_CANDIDATES)


def _tool_call_records_available() -> bool:
    """True when a readable directory of per-turn tool-call records is declared."""
    records_dir = os.environ.get(RECORDS_ENV)
    if not records_dir:
        return False
    return os.path.isdir(records_dir) and os.access(records_dir, os.R_OK)


CHECKS = (
    ("skill_session_runner", _skill_session_runner_available),
    ("tool_call_records", _tool_call_records_available),
)


def main() -> int:
    missing = [name for name, probe in CHECKS if not probe()]
    if missing:
        print(
            "ENVIRONMENT_BLOCKED "
            + json.dumps({"missing_capabilities": missing}, ensure_ascii=False)
        )
        return 2
    print(
        "ENVIRONMENT_READY "
        + json.dumps({"capabilities": [name for name, _ in CHECKS]}, ensure_ascii=False)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

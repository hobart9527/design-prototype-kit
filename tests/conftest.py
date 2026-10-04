"""Test session defaults.

Unit tests assert on static signals; a real headless-Chrome spawn adds cold-start
wall time and, on a wedged machine, orphaned helper processes. Skip engine
probes by default in the suite; a single integration run can unset the variable
to exercise the real engine.
"""
import os

os.environ.setdefault("SPEC_PROTOTYPE_FAST_TEST", "1")

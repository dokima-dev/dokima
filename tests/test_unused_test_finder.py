"""The unused test finder is gone; what the planner needs stays.

Issue #765, story 6 of #739: `find_tests` in `dokima/checks.py` has no caller, so it is deleted. The planner imports
`PROVES` and `TEST_DEF` from the same module, so the test also checks those still load and still read a proof line.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_the_unused_test_finder_is_deleted(record_property):
    """The checks no longer hold the unused test finder.

    Proves 765.1. Loads `dokima.checks` and fails if `find_tests` is still there. Then loads `dokima.planner`, which imports
    `PROVES` and `TEST_DEF` from the checks, and checks both still read a test name and its criterion."""
    record_property("proves", "765.1")
    checks = importlib.import_module("dokima.checks")
    assert not hasattr(checks, "find_tests"), "765.1: dokima/checks.py still defines the unused find_tests"
    planner = importlib.import_module("dokima.planner")
    assert planner.TEST_DEF.match("def test_x(record_property):").group(1) == "test_x", (
        "765.1: deleting the finder broke TEST_DEF, which the planner still uses")
    assert planner.PROVES.findall('    record_property("proves", "765.1")') == ["765.1"], (
        "765.1: deleting the finder broke PROVES, which the planner still uses")

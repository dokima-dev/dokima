"""The manual fix check installs every package the all tests check installs (#646).

The manual fix row of the Acceptance criteria workflow runs the whole suite, but its job installed only `pytest`, while
the all tests check (`full-suite.yml`) installs `pytest pytest-xdist`. Tests that need `-n` then failed there and
passed in all tests, so a sound manual fix could never merge. Since #794 the packages come from the settings file, so
these tests run both jobs the way GitHub runs them, with the default settings, through
tests/test_settings_test_setup.py's machine, and check the criteria job installs, before it runs any test, everything
the all tests job installs.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_settings_test_setup import SetupRun  # noqa: E402


def test_the_manual_fix_check_installs_what_all_tests_installs(record_property, tmp_path):
    """The manual fix check installs every package all tests installs, before it runs the tests.

    Runs the all tests job with the default settings and reads what it installs before its tests (by default
    `pytest` and `pytest-xdist` among them), so a package added there later is required here too, then runs the
    Acceptance criteria check job and checks it installs each one before its tests run. Proves 646.1."""
    record_property("proves", "646.1")
    full = SetupRun(tmp_path / "full", "full-suite.yml", "all-tests", None).installed("646.1")
    assert "pytest" in full and "pytest-xdist" in full, f"646.1: could not read the all tests installs: {full}"
    check = SetupRun(tmp_path / "check", "acceptance-criteria.yml", "check", None).installed("646.1")
    missing = sorted(set(full) - set(check))
    assert not missing, (f"646.1: the manual fix check does not install {', '.join(missing)} before it runs the "
                         f"tests, though all tests installs it, so tests needing it fail only in this check")

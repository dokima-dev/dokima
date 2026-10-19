"""Tests for #887: the all tests check passes with no tests, and says so.

pytest exits 5 when it collects no tests. Each test runs the real all tests job of full-suite.yml on a temp repo, through
tests/test_settings_workflows.py's machine, with real pytest, in the merge queue, where every test runs. Beside each
empty repo runs a repo whose tests crash or one with a passing test, so a check that passes or speaks on anything fails.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from test_settings_workflows import Box  # noqa: E402

EMPTY = {"tests/.gitkeep": ""}
ONE = {"tests/test_one.py": "def test_one():\n    \"\"\"Passes.\"\"\"\n"}
BROKEN = {"tests/conftest.py": "raise RuntimeError('broken conftest')\n"}


def run_all_tests(tmp, files):
    """Run the all tests job on a temp repo holding FILES, with real pytest."""
    b = Box(tmp, None, files=files, real_tests=True)
    return b, b.run("full-suite.yml", "all-tests", event="merge_group")


def test_the_all_tests_check_passes_on_an_empty_tests_folder(tmp_path, record_property):
    """The all tests check on a repo with no tests succeeds.

    Runs the all tests job on a repo whose tests folder is empty and expects success; beside it, a repo whose test
    setup crashes must still fail, so a check that passes on anything fails this test. Proves 887.1."""
    record_property("proves", "887.1")
    b, result = run_all_tests(tmp_path / "empty", EMPTY)
    assert result == "success", f"887.1: the all tests check failed on a repo with no tests yet:\n{b.tail()}"
    b, result = run_all_tests(tmp_path / "broken", BROKEN)
    assert result == "failure", f"887.1: the all tests check passed although collecting the tests crashed:\n{b.tail()}"


def test_the_all_tests_check_says_the_repo_has_no_tests_yet(tmp_path, record_property):
    """The all tests check on a repo with no tests says so.

    Runs the all tests job on an empty tests folder and expects the No tests yet notice; beside it, a repo with one
    passing test must pass with no such notice, so a check that always prints it fails this test. Proves 887.2."""
    record_property("proves", "887.2")
    b, _ = run_all_tests(tmp_path / "empty", EMPTY)
    assert "::notice title=No tests yet::" in "\n".join(b.log), \
        f"887.2: the all tests check does not say the repo has no tests yet:\n{b.tail()}"
    b, result = run_all_tests(tmp_path / "one", ONE)
    assert result == "success", f"887.2: the all tests check failed on a repo with one passing test:\n{b.tail()}"
    assert "No tests yet" not in "\n".join(b.log), \
        f"887.2: the all tests check says no tests yet on a repo with one passing test:\n{b.tail()}"

"""Tests for #923: the all tests check collects only the settings' tests folder.

A stray test file outside `tests/` whose import fails must not turn the check red, in the merge queue (every test) or
on a pull request (affected tests, picked by testmon from a real baseline made on the repo before the run). Beside it,
a failing test inside `tests/` must still fail the check, so a check that passes on anything fails these tests.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from test_settings_workflows import Box, steps_of  # noqa: E402

STRAY = {"sandbox/test_exercise.py": "import a_module_ci_does_not_install\n\n\ndef test_exercise():\n    pass\n"}
PASS = {"tests/test_one.py": "def test_one():\n    assert True\n"}
FAIL = {"tests/test_one.py": "def test_one():\n    assert False, 'fails'\n"}
BASELINE = "python3 -m pytest -q --testmon tests || true\n"


def all_tests(tmp, files, mode):
    """Run the all tests job on a repo holding FILES, in MODE 'all' or 'affected'."""
    b = Box(tmp, None, files=files, real_tests=True)
    if mode == "all":
        return b, b.run("full-suite.yml", "all-tests", event="merge_group")
    _, steps = steps_of("full-suite.yml", "all-tests")
    steps = [{"name": s.get("name"), "if": s.get("if"), "run": BASELINE} if "actions/cache/restore" in str(s.get("uses"))
             else s for s in steps]
    return b, b.run("full-suite.yml", "all-tests", steps=steps, event="pull_request_target")


def test_a_stray_test_file_outside_the_tests_folder_never_fails_the_check(tmp_path):
    """Both modes ignore a broken stray test outside `tests/`, and fail on one inside."""
    for mode in ("all", "affected"):
        b, result = all_tests(tmp_path / f"{mode}-stray", {**STRAY, **PASS}, mode)
        assert result == "success", f"{mode}: a stray test outside tests/ failed the check:\n{b.tail()}"
        b, result = all_tests(tmp_path / f"{mode}-fail", {**STRAY, **FAIL}, mode)
        assert result == "failure", f"{mode}: a failing test inside tests/ passed the check:\n{b.tail()}"


def test_a_repo_with_no_tests_folder_passes_and_says_so(tmp_path):
    """Both modes pass with no tests folder, and say the repo has no tests yet."""
    for mode in ("all", "affected"):
        b, result = all_tests(tmp_path / mode, STRAY, mode)
        assert result == "success", f"{mode}: a repo with no tests folder failed the check:\n{b.tail()}"
        assert "::notice title=No tests yet::" in "\n".join(b.log), f"{mode}: no notice of no tests yet:\n{b.tail()}"

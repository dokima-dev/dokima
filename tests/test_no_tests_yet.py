"""Tests for #880: a repo with no tests yet passes the baseline and all tests.

pytest exits 5 when it collects no tests. Each test runs a real job of a workflow on a temp repo whose tests folder is
empty, through tests/test_settings_workflows.py's machine, with real pytest. `python3 -m pytest --testmon` runs real
pytest without testmon and leaves a baseline file, as pytest-testmon 2.2 does even when no test ran (checked by hand).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from test_settings_workflows import Box  # noqa: E402

PYTHON = '''#!/bin/sh
# A stand-in for python3: `-m pip` only logs; `-m pytest --testmon` runs real pytest and leaves a baseline file.
if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then shift 2; echo "pip $*" >> "$SETUP_LOG"; exit 0; fi
if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then shift 2; args=; mon=
  for a in "$@"; do if [ "$a" = --testmon ]; then mon=1; else args="$args $a"; fi; done
  [ -n "$mon" ] && echo baseline > .testmondata
  exec {real} -m pytest -p no:testmon $args; fi
exec {real} "$@"
'''
EMPTY = {"tests/.gitkeep": ""}
BROKEN = {"tests/conftest.py": "raise RuntimeError('broken conftest')\n"}


def box(tmp, files):
    """A repo holding FILES whose tests run for real, as testmon runs them."""
    b = Box(tmp, None, files=files, real_tests=True)
    path = f"{b.tmp}/bin/python3"
    open(path, "w").write(PYTHON.replace("{real}", sys.executable))
    os.chmod(path, 0o755)
    return b


def test_the_baseline_passes_on_an_empty_tests_folder(tmp_path):
    """The testmon baseline on an empty tests folder succeeds and says so.

    It saves the empty baseline; a crash while collecting still fails it."""
    b = box(tmp_path / "empty", EMPTY)
    result = b.run("testmon.yml", "baseline", event="push")
    assert result == "success", f"the baseline failed on a repo with no tests yet:\n{b.tail()}"
    assert "cache-saved" in b.lines(), f"no empty baseline was saved; log {b.lines()}"
    assert "No tests yet" in "\n".join(b.log), f"the run does not say the repo has no tests yet:\n{b.tail()}"
    b = box(tmp_path / "broken", BROKEN)
    assert b.run("testmon.yml", "baseline", event="push") == "failure", \
        f"the baseline passed although collecting the tests crashed:\n{b.tail()}"


def test_the_all_tests_check_passes_on_an_empty_tests_folder(tmp_path):
    """The all tests check on an empty tests folder succeeds and says so.

    A crash while collecting still fails it."""
    b = box(tmp_path / "empty", EMPTY)
    result = b.run("full-suite.yml", "all-tests", event="merge_group")
    assert result == "success", f"the all tests check failed on a repo with no tests yet:\n{b.tail()}"
    assert "No tests yet" in "\n".join(b.log), f"the run does not say the repo has no tests yet:\n{b.tail()}"
    b = box(tmp_path / "broken", BROKEN)
    assert b.run("full-suite.yml", "all-tests", event="merge_group") == "failure", \
        f"the all tests check passed although collecting the tests crashed:\n{b.tail()}"

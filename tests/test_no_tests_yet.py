"""Tests for #886: a repo with no tests yet passes the testmon baseline.

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
ONE = {"tests/test_one.py": "def test_one():\n    \"\"\"Passes.\"\"\"\n"}
BROKEN = {"tests/conftest.py": "raise RuntimeError('broken conftest')\n"}


def box(tmp, files):
    """A repo holding FILES whose tests run for real, as testmon runs them."""
    b = Box(tmp, None, files=files, real_tests=True)
    path = f"{b.tmp}/bin/python3"
    open(path, "w").write(PYTHON.replace("{real}", sys.executable))
    os.chmod(path, 0o755)
    return b


def notices(b):
    """The run's notice lines that say the repo has no tests yet."""
    lines = "\n".join(b.log).splitlines()
    return [l for l in lines if l.strip().startswith("::notice") and "No tests yet" in l]


def test_the_baseline_passes_on_an_empty_tests_folder(tmp_path, record_property):
    """The testmon baseline on an empty tests folder succeeds and saves an empty baseline.

    Proves 886.1. Runs the baseline job on a repo whose tests folder is empty and expects success and a saved cache; beside it, a
    repo whose test setup crashes must still fail, so a job that passes on anything fails this test."""
    record_property("proves", "886.1")
    b = box(tmp_path / "empty", EMPTY)
    result = b.run("testmon.yml", "baseline", event="push")
    assert result == "success", f"886.1: the baseline failed on a repo with no tests yet:\n{b.tail()}"
    assert "cache-saved" in b.lines(), f"886.1: no empty baseline was saved; log {b.lines()}"
    b = box(tmp_path / "broken", BROKEN)
    assert b.run("testmon.yml", "baseline", event="push") == "failure", \
        f"886.1: the baseline passed although collecting the tests crashed:\n{b.tail()}"


def test_the_baseline_says_the_repo_has_no_tests_yet(tmp_path, record_property):
    """The testmon baseline on an empty tests folder says the repo has no tests yet.

    Proves 886.2. Runs the baseline job on an empty tests folder and expects a `::notice` line, the run's notice, holding
    No tests yet; plain words in the log do not count. Beside it, a repo with one passing test must show no such notice,
    so a job that always prints it fails this test."""
    record_property("proves", "886.2")
    b = box(tmp_path / "empty", EMPTY)
    b.run("testmon.yml", "baseline", event="push")
    assert notices(b), f"886.2: the baseline shows no notice that the repo has no tests yet:\n{b.tail()}"
    b = box(tmp_path / "one", ONE)
    assert b.run("testmon.yml", "baseline", event="push") == "success", \
        f"886.2: the baseline failed on a repo with one passing test:\n{b.tail()}"
    assert not notices(b), \
        f"886.2: the baseline says no tests yet on a repo with one passing test:\n{b.tail()}"


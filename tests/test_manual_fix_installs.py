"""The manual fix check installs every package the all tests check installs (#646).

The manual fix row of the Acceptance criteria workflow runs the whole suite, but its job installed only `pytest`, while
the all tests check (`full-suite.yml`) installs `pytest pytest-xdist`. Tests that need `-n` then failed there and
passed in all tests, so a sound manual fix could never merge. These tests read the `pip install` lines of both jobs
and check the criteria job installs, before it runs any test, everything the all tests job installs.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = os.path.join(ROOT, ".github", "workflows", "full-suite.yml")
CRITERIA = os.path.join(ROOT, ".github", "workflows", "acceptance-criteria.yml")
RUN_STEP = "- name: Run this criterion's tests"


def job_lines(path, job):
    """The lines of one job of a workflow file, found by its key under `jobs:`."""
    lines = open(path).read().splitlines()
    start = next(i for i, l in enumerate(lines) if l == f"  {job}:")
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^  \S", lines[i])), len(lines))
    return lines[start:end]


def installs(lines):
    """The packages named by every `pip install` line, with their index in the lines."""
    found = {}
    for i, line in enumerate(lines):
        m = re.search(r"pip install (.*)$", line)
        if m:
            for word in m.group(1).split():
                if not word.startswith("-"):
                    found.setdefault(word, i)
    return found


def test_the_manual_fix_check_installs_what_all_tests_installs(record_property):
    """The manual fix check installs every package all tests installs, before it runs the tests.

    Reads the all tests job's `pip install` packages from `full-suite.yml` (today `pytest` and `pytest-xdist`), so a
    package added there later is required here too, and checks the Acceptance criteria check job installs each one
    before its "Run this criterion's tests" step. Proves 646.1."""
    record_property("proves", "646.1")
    full = installs(job_lines(FULL, "all-tests"))
    assert "pytest" in full and "pytest-xdist" in full, f"646.1: could not read the all tests installs: {full}"
    check = job_lines(CRITERIA, "check")
    run_at = next(i for i, l in enumerate(check) if l.strip() == RUN_STEP)
    have = {p: i for p, i in installs(check).items() if i < run_at}
    missing = sorted(set(full) - set(have))
    assert not missing, (f"646.1: the manual fix check does not install {', '.join(missing)} before it runs the "
                         f"tests, though all tests installs it, so tests needing it fail only in this check")

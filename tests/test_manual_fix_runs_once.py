"""A manual fix runs every test once, in the all tests check, never again in its own check (#840).

The manual fix check ran the whole test folder in one process while the all tests check, which main requires, already
runs every test with xdist in the merge queue: a manual fix waited about 20 minutes for a second, serial run. The
criterion step of acceptance-criteria.yml runs here in bash with a fake `pytest` that records each call.
"""
import os
import subprocess

import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")


def steps():
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github/workflows/acceptance-criteria.yml")))
    return {s.get("name"): s for s in wf["jobs"]["check"]["steps"] if s.get("name")}


def run_step(tmp_path, row_id, tests):
    tmp_path.mkdir(parents=True)
    log = tmp_path / "pytest.log"
    (tmp_path / "pytest").write_text(f"#!/bin/sh\necho \"$@\" >> '{log}'\n")
    (tmp_path / "pytest").chmod(0o755)
    env = {**os.environ, "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}", "ID": row_id, "TESTS": tests}
    env.pop("TESTS_RUN_ONE", None)
    done = subprocess.run(["bash", "-e", "-c", steps()["Run this criterion's tests"]["run"]], env=env, cwd=tmp_path,
                          capture_output=True, text=True)
    return done, (log.read_text() if log.exists() else "")


def test_a_manual_fix_s_check_runs_no_second_suite(record_property, tmp_path):
    """The manual fix check passes without running tests; a planned criterion still runs its own."""
    record_property("proves", "840.1")
    done, calls = run_step(tmp_path / "fix", "manual-fix", "tests")
    assert done.returncode == 0 and calls == "", f"840.1: the manual fix check ran the suite again: {calls!r} {done.stderr}"
    assert "all tests" in done.stdout, f"840.1: the manual fix check does not say where its tests run: {done.stdout}"
    done, calls = run_step(tmp_path / "planned", "12.1", "tests/test_x.py::test_one")
    assert done.returncode == 0 and "tests/test_x.py::test_one" in calls, f"840.1: a criterion's tests did not run: {calls!r}"
    assert "manual-fix" in steps()["Annotate the tests that ran"]["if"], "840.1: the manual fix check annotates a report it never wrote"

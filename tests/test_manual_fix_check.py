"""A manual fix by Dokima's app gets a merge check that runs all tests (#643).

`.github/workflows/fix.yml` (#589) opens an agent's manual fix as Dokima's app, with no linked issue and so no plan.
The required Acceptance criteria check then listed one failing "No approved plan found: no issue linked" row, so such a
fix could never merge. These tests run the real command the Acceptance criteria workflow runs,
`python3 -m dokima.checks matrix`, from the repo root with GitHub faked by a stub `gh` (the pull request changes
`dokima/checks.py`, so the text-only shortcut never applies), then run that workflow's own "Run this criterion's tests"
step with the row it got and a fake `pytest` on PATH that logs its arguments and passes or fails on demand.
Nothing here touches the network.
"""
import json
import os
import subprocess
import sys

from test_text_only import ROOT, STUB_GH, step_script

APP = "dokima-runtime[bot]"
OWNER = "RezaSoleymanifar"
NO_ISSUE = "No approved plan found: no issue linked"
PR = 901

QUEUE_GH = '''#!/usr/bin/env python3
"""A stand-in for the GitHub CLI that answers the queued pull request, else behaves like the text-only stub."""
import json, os, subprocess, sys
data = json.load(open(os.environ["STUB_DATA"]))
a = sys.argv[1:]
if a[:2] == ["api", "repos/o/r/pulls/%d" % data["pr"]]:
    print(json.dumps({"number": data["pr"], "head": {"ref": "fix/issue-77-typo"}, "body": data["body"],
                      "user": {"login": data["author"]}}))
    sys.exit(0)
sys.exit(subprocess.run([sys.executable, os.environ["STUB_BASE"], *a]).returncode)
'''


def run_matrix(tmp_path, author, body="", queue=False):
    """Run the matrix command for a code change opened by this author.

    With queue, the event is the merge queue's, whose branch names the pull request. Returns (rows or None, output)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    base = tmp_path / "base_gh.py"
    base.write_text(STUB_GH)
    gh = bin_dir / "gh"
    gh.write_text(QUEUE_GH)
    gh.chmod(0o755)
    data = tmp_path / "data.json"
    files = [{"filename": "dokima/checks.py", "status": "modified"}]
    data.write_text(json.dumps({"pr": PR, "pages": [files], "body": body, "author": author}))
    event = tmp_path / "event.json"
    if queue:
        event.write_text(json.dumps({"merge_group": {"head_ref": f"refs/heads/gh-readonly-queue/main/pr-{PR}-abc123",
                                                     "base_ref": "refs/heads/main"}}))
    else:
        event.write_text(json.dumps({"pull_request": {"number": PR, "head": {"ref": "fix/issue-77-typo"}, "body": body,
                                                      "user": {"login": author}}}))
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "GITHUB_REPOSITORY": "o/r",
           "GITHUB_EVENT_PATH": str(event), "STUB_DATA": str(data), "STUB_BASE": str(base), "GH_TOKEN": "x",
           "PYTHONPATH": ROOT}
    env.pop("DOKIMA_BOT", None)
    p = subprocess.run([sys.executable, "-m", "dokima.checks", "matrix"], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=30)
    rows = None
    for line in p.stdout.splitlines():
        if line.startswith("matrix="):
            rows = json.loads(line[len("matrix="):])
    return rows, f"exit {p.returncode}\n{p.stdout}{p.stderr}"


def run_check(tmp_path, row, tests_pass):
    """Run the workflow's "Run this criterion's tests" step for this row, with a fake pytest.

    Returns (exit code, output, pytest's arguments or None when it never ran)."""
    bin_dir = tmp_path / "stepbin"
    bin_dir.mkdir(exist_ok=True)
    log = tmp_path / "pytest-args"
    fake = bin_dir / "pytest"
    fake.write_text(f"#!/bin/sh\necho \"$@\" > '{log}'\nexit {0 if tests_pass else 1}\n")
    fake.chmod(0o755)
    # The step reads its test command from the settings' TESTS_RUN_ONE; the run that hosts these tests may set its
    # own, which would bypass the fake pytest, so the step gets none and runs its old `pytest` command.
    env = {**{k: v for k, v in os.environ.items() if k != "TESTS_RUN_ONE"},
           "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "ID": row["id"], "TESTS": row["tests"]}
    p = subprocess.run(["bash", "-e", "-c", step_script("Run this criterion's tests")], cwd=tmp_path,
                       capture_output=True, text=True, timeout=30, env=env)
    args = log.read_text().split() if log.exists() else None
    return p.returncode, p.stdout + p.stderr, args


def manual_fix_row(rows, output, criterion):
    """The one row a manual fix gets, failing with the criterion when it is missing."""
    assert rows is not None, f"{criterion}: the matrix command printed no check list:\n{output}"
    assert len(rows) == 1, f"{criterion}: a manual fix should get exactly one check, got {rows}"
    assert rows[0]["name"] != NO_ISSUE and rows[0]["id"] != "none", \
        f"{criterion}: a manual fix opened by Dokima's app still gets the failing '{NO_ISSUE}' check"
    return rows[0]


def test_a_manual_fix_by_dokimas_app_gets_a_check_that_runs_all_tests_and_passes(record_property, tmp_path):
    """A manual fix by Dokima's app gets a check that runs all tests and passes.

    Proves 643.1. Runs the matrix command for a pull request by Dokima's app with no linked issue, once as opened and once in the
    merge queue, then runs the workflow's own test step with that row and a passing fake pytest. The step must pass
    and must have run pytest on the whole tests folder."""
    record_property("proves", "643.1")
    for queue in (False, True):
        where = "in the merge queue" if queue else "on the pull request"
        rows, output = run_matrix(tmp_path, APP, queue=queue)
        row = manual_fix_row(rows, output, f"643.1 ({where})")
        code, out, args = run_check(tmp_path, row, tests_pass=True)
        assert args is not None, f"643.1 ({where}): the manual fix's check ran no tests:\n{out}"
        assert "tests" in args, f"643.1 ({where}): the manual fix's check did not run all tests, only {args}"
        assert code == 0, f"643.1 ({where}): the manual fix's check failed although all tests passed:\n{out}"


def test_a_manual_fix_check_fails_when_a_test_fails(record_property, tmp_path):
    """A manual fix's check fails when any test fails.

    Proves 643.2. Gets the row a manual fix opened by Dokima's app receives, then runs the workflow's own test step with a fake
    pytest that fails. The step must have run all tests and must fail."""
    record_property("proves", "643.2")
    rows, output = run_matrix(tmp_path, APP)
    row = manual_fix_row(rows, output, "643.2")
    code, out, args = run_check(tmp_path, row, tests_pass=False)
    assert args is not None and "tests" in args, f"643.2: the manual fix's check did not run all tests: {args}\n{out}"
    assert code != 0, f"643.2: the manual fix's check passed although a test failed:\n{out}"


def test_only_dokimas_app_gets_the_manual_fix_check(record_property, tmp_path):
    """A pull request with no issue, opened by anyone else, still fails.

    Proves 643.3. Runs the matrix command for the same code change twice: opened by a person, it must get only the failing
    no-plan check; opened by Dokima's app, it must get the manual fix check instead. Since 2026-10-17 every manual fix
    names the issue it fixes (owner, #830), so one by Dokima's app from its fix branch naming an issue still gets the
    manual fix check; a planned build from try/issue-N with no approved plan still fails (830.7)."""
    record_property("proves", "643.3")
    rows, output = run_matrix(tmp_path, OWNER)
    assert rows == [{"id": "none", "name": NO_ISSUE, "tests": ""}], \
        f"643.3: a pull request a person opened with no linked issue no longer fails '{NO_ISSUE}': {rows}\n{output}"
    rows, output = run_matrix(tmp_path, APP, body="Fixes #77")
    assert [r["id"] for r in rows or []] == ["manual-fix"], \
        f"643.3: a manual fix by Dokima's app naming the issue it fixes lost its manual fix check: {rows}\n{output}"
    rows, output = run_matrix(tmp_path, APP)
    manual_fix_row(rows, output, "643.3")


def test_a_manual_fix_naming_its_issue_still_gets_the_manual_fix_check(record_property):
    """Naming the issue it fixes ("Fixes #N") does not turn a manual fix into a planned build.

    Proves 830.7. Dokima's app opened it from a branch that is not try/issue-N, so it gets the one check that runs all
    tests, never "No approved plan found for issue #N". A pull request from try/issue-N with no approved plan still
    gets the failing no-plan check."""
    record_property("proves", "830.7")
    from dokima import checks
    rows = checks.build_matrix("807", [], APP, "fix/issue-77-typo")
    assert [r["id"] for r in rows] == ["manual-fix"], f"830.7: a manual fix naming its issue got {rows}"
    rows = checks.build_matrix("807", [], APP, "try/issue-807")
    assert rows[0]["id"] == "none", f"830.7: a planned build with no approved plan did not fail: {rows}"

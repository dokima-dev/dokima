"""The planner check on a re-plan (#201): a new test must fail on main's code, not on the branch's.

On a re-plan the issue's branch may already hold the worker's code, so a new test that proves that code passes on the
branch even though the feature is missing on main. Every test here runs `python3 -m dokima.planner check 9 OUT`
through planner.main, inside the temp git repo of the `check` fixture of tests/test_plan_check.py, set up like a real
re-plan: main is the fixture's starting commit (PLANNER_BASE), the branch adds the planner's first-round test and then
the worker's code (jobs.py, at PLANNER_RUN_BASE), and the re-plan writes its tests on top.
"""
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.test_plan_check import STORY, check  # noqa: E402,F401

# The worker's code: on the branch only, never on main.
WORKER_CODE = 'def make_job_id():\n    return "job-1"\n\n\ndef job_ids(n):\n    return ["job-%d" % i for i in range(n)]\n'

# Every new test file and test opens in the shape #707 asks for: a User line, a Verified by line, then an Agent part.
TEST_ID = ('"""User: Sample tests for slow calls.\n\nAgent: They fail until the job code exists.\n"""\n'
           'import os\nimport sys\n\n\ndef test_id(record_property):\n    """User: A slow call returns a job id.\n'
           '    Verified by: calling the job code.\n\n    Agent: Proves 9.1.\n    """\n'
           '    record_property("proves", "9.1")\n    sys.path.insert(0, os.getcwd())\n    from jobs import make_job_id\n'
           '    assert make_job_id() == "job-1", "9.1: no job id yet"\n')

# The re-plan's new test: it proves the worker's code, so it passes on the branch and fails on main.
NEEDS_WORKER = ('\n\ndef test_unique(record_property):\n    """User: Job ids never repeat.\n'
                '    Verified by: calling the job code.\n\n    Agent: Proves 9.2 and 9.3.\n    """\n'
                '    record_property("proves", "9.2")\n    sys.path.insert(0, os.getcwd())\n    from jobs import job_ids\n'
                '    assert len(set(job_ids(3))) == 3, "9.2: job ids repeat"\n')

# A new test that passes on main too: it needs only a helper the planner added under tests/, no worker code.
HELPER = 'def ids():\n    return ["a", "b", "c"]\n'
ON_MAIN = ('\n\ndef test_unique(record_property):\n    """User: Job ids never repeat.\n'
                '    Verified by: calling the job code.\n\n    Agent: Proves 9.2 and 9.3.\n    """\n'
           '    record_property("proves", "9.2")\n    from jobs_helper import ids\n'
           '    assert len(set(ids())) == 3, "9.2: job ids repeat"\n')


def git(*args):
    """Run git in the temp repo and return what it prints."""
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def write(path, text):
    """Write one file in the temp repo."""
    with open(path, "w") as f:
        f.write(text)


def worker_built(monkeypatch):
    """Turn the fixture's repo into a branch the worker already built on, as a re-plan finds it.

    Main stays at the fixture's starting commit (PLANNER_BASE). The branch adds the planner's first-round test
    (test_id), then the worker's jobs.py (with a .gitignore for Python's caches, as a real repo has); this run starts there (PLANNER_RUN_BASE). The fixture's own uncommitted
    tests/test_jobs.py is replaced first, so the re-plan writes its tests on a clean tree.
    """
    write("tests/test_jobs.py", TEST_ID)
    git("add", "tests/test_jobs.py")
    git("-c", "user.name=dokima-runtime[bot]", "commit", "-qm", "planner: first round")
    write("jobs.py", WORKER_CODE)
    write(".gitignore", "__pycache__/\n")
    git("add", "jobs.py", ".gitignore")
    git("-c", "user.name=dokima-runtime[bot]", "commit", "-qm", "worker: jobs")
    monkeypatch.setenv("PLANNER_RUN_BASE", git("rev-parse", "HEAD").strip())


def snapshot():
    """What the check must leave as it found it: HEAD, branch, worktrees, git status (bar Python's
    caches) and every file's content."""
    files = {}
    for root, dirs, names in os.walk("."):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".pytest_cache")]
        for n in names:
            p = os.path.join(root, n)
            files[p] = open(p, "rb").read()
    return (git("rev-parse", "HEAD"), git("branch", "--show-current"), git("worktree", "list", "--porcelain"),
            "".join(l for l in git("status", "--porcelain", "--untracked-files=all").splitlines(True)
                    if "__pycache__" not in l), files)


def test_a_replan_whose_new_tests_pass_only_thanks_to_the_workers_code_is_accepted(record_property, check, monkeypatch):
    """A re-plan is accepted when its new tests pass on the branch only because the worker built there, and fail on main.

    Builds a branch holding the planner's first-round test and the worker's jobs.py, then adds a re-plan test that
    proves the worker's code. First checks both tests really pass on the branch, so the case is real. Then runs the
    check and checks it passes with no reason: both new tests fail on main, where jobs.py does not exist.
    """
    record_property("proves", "201.1")
    worker_built(monkeypatch)
    write("tests/test_jobs.py", TEST_ID + NEEDS_WORKER)
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_jobs.py"],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"201.1: setup: the new tests should pass on the branch that holds the worker's code\n{r.stdout}"
    rc, why = check({"plan.json": STORY}, "201.1")
    assert rc == 0 and not why, \
        f"201.1: a re-plan whose new tests fail on main (they pass only thanks to the worker's code) was rejected: {why!r}"


def test_a_new_test_that_passes_on_main_is_rejected_on_a_first_plan_and_on_a_replan(record_property, check, monkeypatch):
    """A new test that already passes on main is rejected by name, on a first plan and on a re-plan.

    First plan: test_unique passes on main, using only a helper the planner added under tests/; the check fails naming
    test_unique and not test_id, which fails. Re-plan: the same test is added on a branch the worker already built on;
    the check must still fail naming test_unique and saying it passes today, but must not name test_id, which passes on
    the branch only thanks to the worker's code and fails on main. The helper sits only on the branch, so a check that
    left the planner's helper behind would see test_unique fail on main and wrongly let it through.
    """
    record_property("proves", "201.2")
    write("tests/jobs_helper.py", HELPER)
    write("tests/test_jobs.py", TEST_ID + ON_MAIN)
    rc, why = check({"plan.json": STORY}, "201.2")
    assert rc == 1, "201.2: on a first plan, a new test that passes on main was accepted"
    assert "test_unique" in why and "passes today" in why, \
        f"201.2: on a first plan, the reason does not name test_unique and say it passes today: {why!r}"
    assert "test_id" not in why, f"201.2: on a first plan, the reason also names test_id, which fails on main: {why!r}"

    os.remove("tests/jobs_helper.py")
    worker_built(monkeypatch)
    write("tests/jobs_helper.py", HELPER)
    write("tests/test_jobs.py", TEST_ID + ON_MAIN)
    rc, why = check({"plan.json": STORY}, "201.2")
    assert rc == 1, "201.2: on a re-plan, a new test that passes on main was accepted"
    assert "test_unique" in why and "passes today" in why, \
        f"201.2: on a re-plan, the reason does not name test_unique and say it passes today: {why!r}"
    assert "test_id" not in why, \
        f"201.2: on a re-plan, the reason names test_id, which fails on main and passes only on the worker's branch: {why!r}"


@pytest.mark.parametrize("accepted", [True, False], ids=["accepted re-plan", "rejected re-plan"])
def test_the_check_leaves_the_branch_and_the_planners_files_as_it_found_them(record_property, check, monkeypatch, accepted):
    """Judging new tests against main leaves the branch, the worker's code and the planner's files exactly as they were.

    Builds a re-plan on a branch the worker already built on, accepted (its new tests fail on main) or rejected (a new
    test passes on main), and records HEAD, the branch, the worktrees, git status and every file's bytes. Runs the
    check, checks it gave the expected verdict, then checks nothing of that changed: no checkout of main left behind,
    no stray worktree or folder in the repo, no file lost.
    """
    record_property("proves", "201.3")
    worker_built(monkeypatch)
    if accepted:
        write("tests/test_jobs.py", TEST_ID + NEEDS_WORKER)
    else:
        write("tests/jobs_helper.py", HELPER)
        write("tests/test_jobs.py", TEST_ID + ON_MAIN)
    before = snapshot()
    rc, why = check({"plan.json": STORY}, "201.3")
    if accepted:
        assert rc == 0, f"201.3: (via 201.1) a re-plan whose new tests fail on main was rejected: {why!r}"
    else:
        assert rc == 1 and "test_unique" in why and "test_id" not in why, \
            f"201.3: (via 201.2) the re-plan was not rejected naming only test_unique: rc={rc}, {why!r}"
    after = snapshot()
    for label, b, a in zip(("HEAD", "branch", "worktrees", "git status"), before, after):
        assert a == b, f"201.3: the check changed the repo's {label}: before {b!r}, after {a!r}"
    assert sorted(after[4]) == sorted(before[4]), \
        f"201.3: the check added or removed files: {sorted(set(after[4]) ^ set(before[4]))}"
    changed = [p for p in before[4] if after[4][p] != before[4][p]]
    assert not changed, f"201.3: the check changed these files: {changed}"

"""The planner check (#155): new tests need a one-sentence summary and must fail today; a rename is a change.

Every test here runs `python3 -m dokima.planner check 9 OUT` through planner.main, inside the temp git repo of the
`check` fixture of tests/test_plan_check.py: one older test at the starting commit, the planner's tests on top, and the
good story STORY, which names tests/test_jobs.py::test_id and ::test_unique. Each test rewrites the planner's files in
that repo, runs the check, and reads back the exit code and the reason saved for the issue.
"""
import json
import os
import signal
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402
from tests.test_plan_check import ROOT, STORY, check  # noqa: E402,F401


# Every new test file and test opens in the shape #707 asks for: a User line, a Verified by line, then an Agent part.
FILE_DOC = '"""User: Sample tests for slow calls.\n\nAgent: They fail until the job code exists.\n"""\n\n\n'


def jobs(id_doc='"""User: A slow call returns a job id.\n    Verified by: calling the job code.\n\n    Agent: Proves 9.1.\n    """', id_body='assert False, "9.1: no job id yet"',
         unique_doc='"""User: Job ids never repeat.\n    Verified by: calling the job code.\n\n    Agent: Proves 9.2 and 9.3.\n    """', unique_body='assert False, "9.2: no job ids yet"', top=""):
    """The planner's tests/test_jobs.py, with the two tests STORY names; by default both have a summary and fail."""
    def one(name, key, doc, body):
        lines = [f"def {name}(record_property):"] + ([f"    {doc}"] if doc else [])
        return "\n".join(lines + [f'    record_property("proves", "{key}")', f"    {body}"]) + "\n"
    return FILE_DOC + top + one("test_id", "9.1", id_doc, id_body) + "\n\n" + one("test_unique", "9.2", unique_doc, unique_body)


def write_jobs(text):
    """Write the planner's tests/test_jobs.py in the temp repo (the fixture runs each test from there)."""
    with open("tests/test_jobs.py", "w") as f:
        f.write(text)


def git(*args):
    """Run git in the temp repo and return what it prints."""
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


# An older test in the shape #707 asks for, since a changed or renamed test is held to it.
LEGACY = ('def test_legacy(record_property):\n    """User: An older test.\n    Verified by: asserting a constant.\n\n'
          '    Agent: Proves 50.2.\n    """\n    record_property("proves", "50.2")\n    assert True\n')


@pytest.fixture
def legacy(check, monkeypatch):
    """The `check` fixture with one more older test at the start: tests/test_legacy.py::test_legacy, which passes,
    so only a rename (never a new test) may get past the check with it."""
    with open("tests/test_legacy.py", "w") as f:
        f.write(LEGACY)
    git("add", "tests/test_legacy.py")
    git("commit", "-qm", "an older test with no docstring")
    head = git("rev-parse", "HEAD").strip()
    monkeypatch.setenv("PLANNER_BASE", head)
    monkeypatch.setenv("PLANNER_RUN_BASE", head)
    return check


CHANGED = "tests/test_legacy.py::test_legacy"


def change_legacy():
    """Change the body of the older test_legacy, keeping its name, docstring and a pass today.

    A changed test, not a new one, so neither new-test rule may reject it. Returns the plan with its reason under test_changes."""
    with open("tests/test_legacy.py", "w") as f:
        f.write(LEGACY.replace("assert True", "assert 1 == 1"))
    return dict(STORY, test_changes={CHANGED: "asserts a value instead of True"})


# 155.1: a new test needs a docstring whose first line is one plain sentence on one line

@pytest.mark.parametrize("doc", [
    None,
    '""""""',
    '"""A slow call returns a job id"""',
    '"""Job ids never repeat. They are unique."""',
    '"""Job ids never repeat; checked twice? Yes."""',
    '"""Job ids never\n    repeat."""',
    '"""\n    \n    """',
], ids=["no docstring", "empty", "no end mark", "two sentences", "two sentences ending in ?", "wrapped over two lines",
        "blank"])
def test_a_new_test_without_a_one_sentence_summary_is_rejected_naming_it(record_property, legacy, doc):
    """A new test with no docstring, or whose first line is not one sentence on one line, is rejected by name.

    Throughout, an older test is changed (same name, new body): only new tests are held to the rule, so it must never
    be rejected or named. First checks that new tests whose summaries end in '.', '?' or '!'
    (one with a dot inside, "1.5 s") pass beside it. Then gives test_unique a bad docstring, runs the check, and checks
    it fails with a reason naming test_unique and neither the good test_id nor the changed older test.
    """
    record_property("proves", "155.1")
    plan = change_legacy()
    for good in ('"""User: A slow call returns a job id within 1.5 s.\n    Verified by: calling the job code.\n\n    Agent: Proves 9.1.\n    """',
                 '"""User: Does a slow call return a job id?\n    Verified by: calling the job code.\n\n    Agent: Proves 9.1.\n    """',
                 '"""User: A slow call returns a job id!\n    Verified by: calling the job code.\n\n    Agent: Proves 9.1.\n    """',
                 '"""User: A slow call returns a job id.\n    Verified by: calling the job code.\n\n    Agent: More words. And more. Proves 9.1."""'):
        write_jobs(jobs(id_doc=good))
        rc, why = legacy({"plan.json": plan}, "155.1")
        assert rc == 0 and not why, \
            f"155.1: new tests with the good summary {good!r}, beside a changed older test, were rejected: {why!r}"
    write_jobs(jobs(unique_doc=doc))
    rc, why = legacy({"plan.json": plan}, "155.1")
    assert rc == 1, f"155.1: a new test with the docstring {doc!r} was accepted; it needs a one-sentence first line"
    assert "test_unique" in why, f"155.1: the reason does not name the test test_unique: {why!r}"
    assert "test_id" not in why, f"155.1: the reason also names test_id, whose summary is good: {why!r}"
    assert "test_legacy" not in why, \
        f"155.1: the reason names the changed older test test_legacy, which is not new and needs no summary: {why!r}"


# 155.2: every new test is run on today's code; one that passes or is skipped is rejected

@pytest.mark.parametrize("body", [
    "assert True",
    'pytest.skip("not yet")',
    "@skip",
], ids=["passes", "skips itself", "marked skip"])
def test_a_new_test_that_passes_or_skips_today_is_rejected_saying_so(record_property, legacy, body):
    """A new test that passes or is skipped on today's code is rejected, naming it and saying it passes today.

    Throughout, an older test is changed (same name, new body) and passes today: only new tests must fail, so it must
    never be rejected or named. First checks new tests that fail today pass the check beside it: a failing assert, a
    name the feature has not defined yet, and a whole file whose import of the missing feature errors. Then makes
    test_unique pass or skip, runs the check, and checks the reason names test_unique (not test_id, which still fails,
    nor the changed older test) and says it passes today.
    """
    record_property("proves", "155.2")
    plan = change_legacy()
    for good in (jobs(), jobs(id_body="assert make_job_id()"),
                 jobs(id_body="assert make_job_id()", top="from dokima_jobs_not_built_yet import make_job_id\n\n\n")):
        write_jobs(good)
        rc, why = legacy({"plan.json": plan}, "155.2")
        assert rc == 0 and not why, \
            f"155.2: new tests that fail today, beside a changed older test that passes today, were rejected: {why!r}\n{good}"
    if body == "@skip":
        text = jobs(top="import pytest\n\n\n").replace("def test_unique", '@pytest.mark.skip("not yet")\ndef test_unique')
    else:
        text = jobs(unique_body=body, top="import pytest\n\n\n")
    write_jobs(text)
    rc, why = legacy({"plan.json": plan}, "155.2")
    assert rc == 1, f"155.2: a new test that {body!r} today was accepted; every new test must fail today"
    assert "test_unique" in why and "passes today" in why, \
        f"155.2: the reason does not name test_unique and say it passes today: {why!r}"
    assert "test_id" not in why, f"155.2: the reason also names test_id, which fails today: {why!r}"
    assert "test_legacy" not in why, \
        f"155.2: the reason names the changed older test test_legacy, which is not new and may pass today: {why!r}"


def test_every_new_test_that_passes_today_is_named(record_property, check):
    """When two new tests pass today, the check names both.

    Makes test_id and test_unique both pass, runs the check, and checks the reason names each of them.
    """
    record_property("proves", "155.2")
    write_jobs(jobs(id_body="assert True", unique_body="assert True"))
    rc, why = check({"plan.json": STORY}, "155.2")
    assert rc == 1, "155.2: two new tests that pass today were accepted"
    for name in ("test_id", "test_unique"):
        assert name in why, f"155.2: the reason does not name {name}, which passes today: {why!r}"


# 155.3: a renamed older test is a change with a reason under its old name, not a new test

def renamed(body="assert True"):
    """tests/test_legacy.py with test_legacy renamed to test_legacy_proves_it, its body as given."""
    return LEGACY.replace("def test_legacy(", "def test_legacy_proves_it(").replace("assert True", body)


def test_a_renamed_older_test_needs_a_reason_under_its_old_name_and_nothing_more(record_property, legacy):
    """A renamed older test counts as a change: a reason under its old name lets it pass; without one it is rejected.

    The older test passes. First renames it and also changes its body: that is a new test, so it must be rejected
    for passing today. Then renames it alone, with a reason under its old name: the check passes, holding it to no
    must-fail rule. Then with no reason, or the reason only under its new name: the
    check fails naming the old test.
    """
    record_property("proves", "155.3")
    old, new = "tests/test_legacy.py::test_legacy", "tests/test_legacy.py::test_legacy_proves_it"
    with open("tests/test_legacy.py", "w") as f:
        f.write(renamed("assert 1 == 1"))
    rc, why = legacy({"plan.json": dict(STORY, test_changes={old: "renamed and rewritten"})}, "155.3")
    assert rc == 1 and "test_legacy_proves_it" in why, \
        f"155.3: a renamed test whose body also changed is a new test, and it passes today, yet it was not rejected by name: {why!r}"
    with open("tests/test_legacy.py", "w") as f:
        f.write(renamed())
    rc, why = legacy({"plan.json": dict(STORY, test_changes={old: "renamed to say what it proves"})}, "155.3")
    assert rc == 0 and not why, f"155.3: a pure rename with a reason under its old name was rejected: {why!r}"
    for reasons in ({}, {new: "renamed to say what it proves"}):
        rc, why = legacy({"plan.json": dict(STORY, test_changes=reasons)}, "155.3")
        assert rc == 1, f"155.3: a rename with reasons {reasons} (none under its old name) was accepted"
        assert old in why, f"155.3: the reason does not name the old test {old}: {why!r}"


# 155.4: a new test file the check cannot parse is rejected naming the file, never a crash

@pytest.mark.parametrize("content", [
    b'def test_broken(record_property:\n    """A broken test."""\n    record_property("proves", "9.1")\n',
    b'def test_broken(record_property):\n    """A broken test \xff\xfe."""\n    record_property("proves", "9.1")\n',
], ids=["not python", "not utf-8"])
def test_a_new_test_file_that_cannot_be_parsed_is_rejected_naming_it(record_property, check, content):
    """A new test file that is not valid Python, or not valid text, is rejected naming the file, never a crash.

    Adds tests/test_broken.py next to the good new tests, runs the check (a crash fails this test), and checks it
    fails with a reason naming tests/test_broken.py.
    """
    record_property("proves", "155.4")
    with open("tests/test_broken.py", "wb") as f:
        f.write(content)
    rc, why = check({"plan.json": STORY}, "155.4")
    assert rc == 1, "155.4: a new test file that cannot be parsed was accepted"
    assert "tests/test_broken.py" in why, f"155.4: the reason does not name the file tests/test_broken.py: {why!r}"


# 155.5: a new test still running after 60 s is stopped and rejected, naming it

def test_a_new_test_that_hangs_is_stopped_and_rejected_naming_it(record_property, check, tmp_path):
    """A new test still running at the limit (60 s) is stopped and rejected by name, so the check never hangs.

    Checks the limit, planner.NEW_TEST_TIMEOUT, is 60 seconds. Then makes test_unique sleep for two minutes and runs
    the check in its own process with the limit set to 2 s (so this test takes seconds, not minutes). The check must
    finish within 15 s, so the stop follows the limit, fail, and name test_unique but not test_id, which fails at
    once; if it is still running, it is killed and this test fails.
    """
    record_property("proves", "155.5")
    assert getattr(planner, "NEW_TEST_TIMEOUT", None) == 60, \
        "155.5: the check has no 60 s limit for one new test (planner.NEW_TEST_TIMEOUT)"
    write_jobs(jobs(unique_body="time.sleep(120)", top="import time\n\n\n"))
    out = tmp_path / "out"
    (out / "plan.json").write_text(json.dumps(STORY))
    code = ("import sys; sys.path.insert(0, sys.argv[1]); from dokima import planner; planner.NEW_TEST_TIMEOUT = 2; "
            "sys.exit(planner.main(['x', 'check', '9', sys.argv[2]]))")
    start = time.monotonic()
    proc = subprocess.Popen([sys.executable, "-c", code, os.path.abspath(ROOT), str(out)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        rc = proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        pytest.fail("155.5: the check was still running 15 s after a new test hung, with a 2 s limit; it was never stopped")
    rejected = out / "rejected.txt"
    why = rejected.read_text() if rejected.exists() else ""
    assert rc == 1, f"155.5: a new test that hung was accepted after {time.monotonic() - start:.0f} s"
    assert "test_unique" in why, f"155.5: the reason does not name the test that hung, test_unique: {why!r}"
    assert "test_id" not in why, f"155.5: the reason also names test_id, which failed at once and did not hang: {why!r}"

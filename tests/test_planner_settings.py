"""The planner's check times, finds and holds tests to docstrings by the repo's settings (#805).

Each test builds a small repo in a temp folder with a `.dokima/settings.yaml`, written the way an owner writes it, and
runs the real `python -m dokima.planner check 9 OUT` from there, through `make_repo` and `run_check` of
tests/test_test_settings.py. Running from the temp repo means the settings are read the way a real run reads them.
Nothing here touches the network.
"""
import os
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_plan_check import STORY  # noqa: E402
from test_test_settings import JOBS, make_repo, named, run_check  # noqa: E402

SLOW = '''import sys, time
time.sleep(float(sys.argv[1]))
sys.exit(1)
'''


def two_tests(first_doc, second_doc="Job ids never repeat."):
    """The plan's two new tests, failing today, with the given docstring first lines."""
    return (f'def test_id(record_property):\n    """{first_doc}\n\n    Proves 9.1.\n    """\n'
            '    record_property("proves", "9.1")\n    assert False, "9.1: no job id yet"\n\n\n'
            f'def test_unique(record_property):\n    """{second_doc}\n\n    Proves 9.2 and 9.3.\n    """\n'
            '    record_property("proves", "9.2")\n    assert False, "9.2: no job ids yet"\n')


# 805.1: the check that new tests fail today stops a test after the time limit setting

def test_the_new_test_check_stops_a_test_after_the_time_limit_setting(record_property, tmp_path):
    """A new test running past the repo's own time limit is stopped and rejected.

    Proves 805.1. The repo's run-one command is a runner that waits, then fails. With a time limit of 1 s and a 3 s
    wait, the check must reject the plan, saying each test was stopped after 1 s. With a 0.2 s wait, under the limit,
    the plan must pass.
    """
    record_property("proves", "805.1")
    runner = tmp_path / "slow.py"
    runner.write_text(SLOW)
    for wait, stopped in ((3, True), (0.2, False)):
        one = f"{shlex.quote(sys.executable)} {shlex.quote(str(runner))} {wait} {{test}}"
        sub = tmp_path / f"w{wait}"
        sub.mkdir()
        repo = make_repo(sub, {"tests": {"run_one": one, "new_test_timeout_s": 1}}, now={"tests/test_jobs.py": JOBS})
        rc, why = run_check(repo, STORY)
        if stopped:
            assert rc == 1 and "tests/test_jobs.py::test_id is a new test still running after 1 s" in why, \
                f"805.1: a test running 3 s was not stopped at the 1 s time limit setting: {why}"
        else:
            assert rc == 0, f"805.1: a test ending well within the time limit setting was rejected: {why}"


# 805.2: the planner's test files are found by the test folder and file pattern settings

HELPER = 'def test_like_value():\n    return 1\n'


def test_the_planners_test_files_follow_the_test_folder_and_file_pattern_settings(record_property, tmp_path):
    """Only files matching the repo's test pattern, in its test folder, are test files.

    Proves 805.2. The settings name `checks` as the test folder and `check_*.py` as the pattern. The planner adds
    `checks/check_jobs.py` with the plan's two tests, and `checks/helpers.py`, a helper with a `test_`-named function
    and no docstring. The helper is not a test file, so the plan must pass. With one more unplanned test in
    `checks/check_jobs.py`, the check must still find it and reject the plan.
    """
    record_property("proves", "805.2")
    settings = {"tests": {"dir": "checks", "file_pattern": "check_*.py"}}
    base = {"checks/check_old.py": "def test_old():\n    assert True\n"}
    plan = named("checks/check_jobs.py::test_id", "checks/check_jobs.py::test_unique")
    good = tmp_path / "good"
    good.mkdir()
    repo = make_repo(good, settings, base=base, now={"checks/check_jobs.py": JOBS, "checks/helpers.py": HELPER})
    rc, why = run_check(repo, plan)
    assert rc == 0, f"805.2: a helper outside the file pattern setting was read as a test file: {why}"
    extra = tmp_path / "extra"
    extra.mkdir()
    repo = make_repo(extra, settings, base=base,
                     now={"checks/check_jobs.py": JOBS + '\n\ndef test_extra():\n    """An unplanned test."""\n'
                                                         '    assert True\n'})
    rc, why = run_check(repo, plan)
    assert rc == 1 and "checks/check_jobs.py::test_extra" in why, \
        f"805.2: a test in a file matching the file pattern setting was not found: {why}"


# 805.3: turning docstrings off in settings stops the planner's check requiring them

BARE = ('def test_id(record_property):\n    record_property("proves", "9.1")\n    assert False, "9.1: no job id yet"\n\n\n'
        'def test_unique(record_property):\n    record_property("proves", "9.2")\n    assert False, "9.2: no job ids yet"\n')


def test_turning_docstrings_off_stops_the_planners_check_requiring_them(record_property, tmp_path):
    """With docstrings off in the repo's settings, new tests without docstrings pass the planner's check.

    Proves 805.3. The planner adds two failing tests with no docstrings. With `docstrings: off` written in the settings
    file, as an owner types it, the plan must pass. With no settings file, docstrings stay required and the plan must
    be rejected for the missing summary.
    """
    record_property("proves", "805.3")
    off = tmp_path / "off"
    off.mkdir()
    repo = make_repo(off, base={".dokima/settings.yaml": "style:\n  docstrings: off\n"}, now={"tests/test_jobs.py": BARE})
    rc, why = run_check(repo, STORY)
    assert rc == 0, f"805.3: with docstrings off in settings, the planner's check still required them: {why}"
    on = tmp_path / "on"
    on.mkdir()
    repo = make_repo(on, now={"tests/test_jobs.py": BARE})
    rc, why = run_check(repo, STORY)
    assert rc == 1 and "no one-sentence summary" in why, \
        f"805.3: with the default settings, a new test with no docstring was not rejected: {why}"


# 805.4: the planner's test docstring cap comes from settings

def test_the_planners_docstring_cap_comes_from_settings(record_property, tmp_path):
    """A new test's docstring is held to the repo's own docstring cap.

    Proves 805.4. With a cap of 5 in settings, a 7-word first line runs past the 6 words that still pass, so the check
    must reject the plan naming that test. With a cap of 10, the same tests must pass.
    """
    record_property("proves", "805.4")
    for cap, rejected in ((5, True), (10, False)):
        sub = tmp_path / f"cap{cap}"
        sub.mkdir()
        repo = make_repo(sub, {"style": {"docstring_cap": cap}}, now={"tests/test_jobs.py": JOBS})
        rc, why = run_check(repo, STORY)
        if rejected:
            assert rc == 1 and "tests/test_jobs.py::test_id has a docstring whose first line holds 7 words" in why, \
                f"805.4: a 7-word docstring passed a docstring cap setting of 5: {why}"
            assert "test_unique has a docstring" not in why, \
                f"805.4: a 4-word docstring was flagged under a docstring cap setting of 5: {why}"
        else:
            assert rc == 0, f"805.4: a 7-word docstring was rejected under a docstring cap setting of 10: {why}"


# 805.5: an empty planner test docstring cap turns that cap off

LONG = ("This one new test checks that a slow call to the service hands back a job id "
        "that the owner can use later to fetch its result once done.")


def test_an_empty_docstring_cap_turns_the_cap_off(record_property, tmp_path):
    """With the docstring cap left empty in settings, a long docstring passes the planner's check.

    Proves 805.5. A new test's docstring opens with a 29-word sentence. With `docstring_cap:` left empty in the
    settings file, the plan must pass. With no settings file, the shipped cap of 15 must reject it.
    """
    record_property("proves", "805.5")
    empty = tmp_path / "empty"
    empty.mkdir()
    repo = make_repo(empty, base={".dokima/settings.yaml": "style:\n  docstring_cap:\n"},
                     now={"tests/test_jobs.py": two_tests(LONG)})
    rc, why = run_check(repo, STORY)
    assert rc == 0, f"805.5: with an empty docstring cap setting, a 29-word docstring was still held to a cap: {why}"
    plain = tmp_path / "plain"
    plain.mkdir()
    repo = make_repo(plain, now={"tests/test_jobs.py": two_tests(LONG)})
    rc, why = run_check(repo, STORY)
    assert rc == 1 and "tests/test_jobs.py::test_id has a docstring whose first line holds 29 words" in why, \
        f"805.5: with the shipped docstring cap, a 29-word docstring was not rejected: {why}"

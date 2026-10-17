"""Dokima finds, links and runs tests by the repo's test settings (#804).

Each test builds a small repo in a temp folder, with a `.dokima/settings.yaml` naming only what differs from the shipped
defaults, and runs the real command from there: the planner's check, `python -m dokima.planner check 9 OUT`, or the merge
check's `python -m dokima.checks matrix` with GitHub faked by the stub `gh` of tests/test_text_only.py. Running from the
temp repo means the settings are read the way a real run reads them, from the repo the command runs in. Nothing here
touches the network.
"""
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_plan_check import STORY  # noqa: E402
from test_text_only import ROOT, STUB_GH, SHORTCUT, NO_ISSUE  # noqa: E402

ROOT = os.path.abspath(ROOT)
PR = 900
APP = "dokima-runtime[bot]"

# The planner's two new tests STORY names, each failing today because the job code does not exist.
JOBS = ('def test_id(record_property):\n    """A slow call returns a job id.\n\n    Proves 9.1.\n    """\n'
        '    record_property("proves", "9.1")\n    assert False, "9.1: no job id yet"\n\n\n'
        'def test_unique(record_property):\n    """Job ids never repeat.\n\n    Proves 9.2 and 9.3.\n    """\n'
        '    record_property("proves", "9.2")\n    assert False, "9.2: no job ids yet"\n')


def git(repo, *args):
    """Run git in REPO and return what it prints."""
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def make_repo(tmp_path, settings=None, base=None, now=None):
    """A temp git repo with SETTINGS and BASE committed and NOW written on top.

    Returns its path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "user.email", "t@t")
    files = dict(base or {})
    if settings is not None:
        files[".dokima/settings.yaml"] = yaml.safe_dump(settings)
    files.setdefault("README.md", "A repo.\n")
    for path, text in files.items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    for path, text in (now or {}).items():
        (repo / path).parent.mkdir(parents=True, exist_ok=True)
        (repo / path).write_text(text)
    return repo


def run_check(repo, plan):
    """Run the planner's check on issue #9 in REPO; returns its exit code and reason."""
    out = repo.parent / "out"
    out.mkdir(exist_ok=True)
    for old in out.iterdir():
        old.unlink()
    (out / "plan.json").write_text(json.dumps(plan))
    head = git(repo, "rev-parse", "HEAD").strip()
    env = {**os.environ, "PYTHONPATH": ROOT, "PLANNER_BASE": head, "PLANNER_RUN_BASE": head, "GITHUB_REPOSITORY": "o/r"}
    env.pop("PACK", None)
    p = subprocess.run([sys.executable, "-m", "dokima.planner", "check", "9", str(out)], cwd=repo, env=env,
                       capture_output=True, text=True, timeout=120)
    rejected = out / "rejected.txt"
    return p.returncode, (rejected.read_text() if rejected.exists() else "") + f"\n[output] {p.stdout}{p.stderr}"


def named(*pairs):
    """STORY with 9.1 filed under the first test id, 9.2 and 9.3 under the second."""
    first, second = pairs
    return dict(STORY, tests={"9.1": [first], "9.2": [second], "9.3": [second]})


def run_matrix(cwd, files, author="someone", work=None):
    """Run the merge check's matrix from CWD for an issueless pull request changing FILES.

    The stub `gh` and its data live in WORK (by default the folder holding CWD). Returns (rows or None, output)."""
    work = work or cwd.parent
    bin_dir = work / "bin"
    bin_dir.mkdir(exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(STUB_GH)
    gh.chmod(0o755)
    data = work / "data.json"
    data.write_text(json.dumps({"pr": PR, "pages": [[{"filename": f, "status": "modified"} for f in files]]}))
    event = work / "event.json"
    event.write_text(json.dumps({"pull_request": {"number": PR, "head": {"ref": "some/edit"}, "body": "",
                                                  "user": {"login": author}}}))
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "GITHUB_REPOSITORY": "o/r",
           "GITHUB_EVENT_PATH": str(event), "STUB_DATA": str(data), "GH_TOKEN": "x", "PYTHONPATH": ROOT}
    env.pop("DOKIMA_BOT", None)
    p = subprocess.run([sys.executable, "-m", "dokima.checks", "matrix"], cwd=cwd, env=env,
                       capture_output=True, text=True, timeout=30)
    rows = next((json.loads(line[len("matrix="):]) for line in p.stdout.splitlines() if line.startswith("matrix=")), None)
    return rows, f"exit {p.returncode}\n{p.stdout}{p.stderr}"


def names(rows):
    """The check names in a matrix, or None when it printed none."""
    return None if rows is None else [r["name"] for r in rows]


# 804.1: the call that links a test to its criterion is the test tag setting

OLDER_TAGGED = 'def test_old(proves_tag):\n    """An older test."""\n    proves_tag("proves", "50.1")\n    assert True\n'


def test_the_test_tag_setting_decides_which_call_links_a_test(record_property, tmp_path):
    """A test linked by the repo's own tag call counts as proving its criterion.

    Proves 804.1. The repo's settings name `proves_tag` as the tag. An older test proves 50.1, outside this plan, by
    calling `proves_tag("proves", "50.1")`; the planner changes its body. The check must see that the old test proved
    50.1 and reject the plan for changing it with no reason. With a reason in test_changes the same plan must pass.
    """
    record_property("proves", "804.1")
    repo = make_repo(tmp_path, {"tests": {"tag": "proves_tag"}}, base={"tests/test_old.py": OLDER_TAGGED},
                     now={"tests/test_old.py": OLDER_TAGGED.replace("assert True", "assert 1 == 1"),
                          "tests/test_jobs.py": JOBS})
    rc, why = run_check(repo, STORY)
    assert rc == 1 and "tests/test_old.py::test_old is an older test the planner changed" in why, \
        f"804.1: an older test linked to 50.1 by the tag setting's call was changed with no reason and not caught: {why}"
    rc, why = run_check(repo, dict(STORY, test_changes={"tests/test_old.py::test_old": "asserts a value"}))
    assert rc == 0, f"804.1: with a reason for the changed older test, the plan was still rejected: {why}"


# 804.2: tests written as methods of a test class are found

def class_jobs(first_doc=True):
    """The planner's two new tests as methods of class TestJobs.

    With first_doc False, test_id has no docstring."""
    doc = '        """A slow call returns a job id.\n\n        Proves 9.1.\n        """\n' if first_doc else ""
    return ('class TestJobs:\n    """Job tests."""\n\n'
            '    def test_id(self, record_property):\n' + doc +
            '        record_property("proves", "9.1")\n        assert False, "9.1: no job id yet"\n\n'
            '    def test_unique(self, record_property):\n        """Job ids never repeat.\n\n        Proves 9.2 and 9.3.\n'
            '        """\n        record_property("proves", "9.2")\n        assert False, "9.2: no job ids yet"\n')


def test_tests_written_as_methods_of_a_test_class_are_found(record_property, tmp_path):
    """A plan whose tests are methods of a test class passes the planner's check.

    Proves 804.2. The planner writes its two failing tests inside class TestJobs and names them by their full ids,
    `tests/test_jobs.py::TestJobs::test_id`. The check must find them and pass. Naming a method the class does not
    have must still be rejected as not in the repo.
    """
    record_property("proves", "804.2")
    repo = make_repo(tmp_path, now={"tests/test_jobs.py": class_jobs()})
    good = named("tests/test_jobs.py::TestJobs::test_id", "tests/test_jobs.py::TestJobs::test_unique")
    rc, why = run_check(repo, good)
    assert rc == 0, f"804.2: tests written as methods of a test class were not found: {why}"
    rc, why = run_check(repo, named("tests/test_jobs.py::TestJobs::test_gone", "tests/test_jobs.py::TestJobs::test_unique"))
    assert rc == 1 and "test_gone, which is not in the repo" in why, \
        f"804.2: a method the class does not have was accepted: {why}"


def test_a_class_method_test_still_needs_its_summary(record_property, tmp_path):
    """A new class method test with no docstring is rejected for having no summary.

    Proves 804.2. Found tests are checked like any other: the planner's test_id inside class TestJobs has no docstring,
    so the check must reject it, naming `TestJobs::test_id` as a new test with no one-sentence summary.
    """
    record_property("proves", "804.2")
    repo = make_repo(tmp_path, now={"tests/test_jobs.py": class_jobs(first_doc=False)})
    rc, why = run_check(repo, named("tests/test_jobs.py::TestJobs::test_id", "tests/test_jobs.py::TestJobs::test_unique"))
    assert rc == 1 and "TestJobs::test_id is a new test with no one-sentence summary" in why, \
        f"804.2: a class method test with no docstring was not held to the summary rule: {why}"


# 804.3: tests written as async functions are found

def test_tests_written_as_async_functions_are_found(record_property, tmp_path):
    """A plan whose tests are async functions has them found by the planner's check.

    Proves 804.3. The planner writes its two tests as `async def`. The check must not call them missing, nor say the
    plan came with no tests, nor leave a criterion without a test. Naming an async test that is not there must still be
    rejected as not in the repo.
    """
    record_property("proves", "804.3")
    repo = make_repo(tmp_path, now={"tests/test_jobs.py": JOBS.replace("def test_", "async def test_")})
    rc, why = run_check(repo, named("tests/test_jobs.py::test_id", "tests/test_jobs.py::test_unique"))
    for wrong in ("which is not in the repo", "the plan came with no tests", "has no test"):
        assert wrong not in why, f"804.3: tests written as async functions were not found ({wrong!r}): {why}"
    rc, why = run_check(repo, named("tests/test_jobs.py::test_gone", "tests/test_jobs.py::test_unique"))
    assert rc == 1 and "test_gone, which is not in the repo" in why, f"804.3: a missing async test was accepted: {why}"


# 804.4: tests indented under another block are found

def test_tests_indented_under_another_block_are_found(record_property, tmp_path):
    """A plan whose tests sit indented under an if block passes the planner's check.

    Proves 804.4. The planner writes its two failing tests inside `if sys.version_info >= (3,):`, where pytest still
    runs them. The check must find them and pass. Naming a test that is not there must still be rejected.
    """
    record_property("proves", "804.4")
    indented = "import sys\n\nif sys.version_info >= (3,):\n" + "".join(
        ("    " + line if line else line) + "\n" for line in JOBS.splitlines())
    repo = make_repo(tmp_path, now={"tests/test_jobs.py": indented})
    rc, why = run_check(repo, named("tests/test_jobs.py::test_id", "tests/test_jobs.py::test_unique"))
    assert rc == 0, f"804.4: tests indented under another block were not found: {why}"
    rc, why = run_check(repo, named("tests/test_jobs.py::test_gone", "tests/test_jobs.py::test_unique"))
    assert rc == 1 and "test_gone, which is not in the repo" in why, f"804.4: a missing indented test was accepted: {why}"


# 804.5: changes to Dokima's prompt folder no longer stop the text-only shortcut

def test_prompt_folder_changes_take_the_text_only_shortcut(record_property, tmp_path):
    """A pull request changing only a prompt file gets the text-only check.

    Proves 804.5. Runs the merge check from Dokima's own repo for a pull request with no issue that changes only
    `dokima/roles/planner.md`: it must get the text-only check. A Markdown file under `.github/` must still not.
    """
    record_property("proves", "804.5")
    rows, out = run_matrix(Path(ROOT), ["dokima/roles/planner.md"], work=tmp_path)
    assert names(rows) == [SHORTCUT], f"804.5: a prompt-only change did not get the text-only check: {rows}\n{out}"
    rows, out = run_matrix(Path(ROOT), [".github/PULL_REQUEST_TEMPLATE.md"], work=tmp_path)
    assert names(rows) == [NO_ISSUE], f"804.5: a Markdown file under .github/ took the text-only shortcut: {rows}\n{out}"


# 804.6: the folders that stop the text-only shortcut come from settings

def test_the_folders_that_stop_the_text_only_shortcut_come_from_settings(record_property, tmp_path):
    """The repo's own list of folders decides which Markdown changes skip the plan.

    Proves 804.6. In a repo whose settings list only `docs/` as not text, a Markdown change under `docs/` must get the
    full checks, and a Markdown change under `tests/`, no longer listed, must get the text-only check.
    """
    record_property("proves", "804.6")
    repo = make_repo(tmp_path, {"text_only": {"not_text": ["docs/"]}})
    rows, out = run_matrix(repo, ["docs/guide.md"])
    assert names(rows) == [NO_ISSUE], f"804.6: a Markdown file under a folder the settings list took the shortcut: {rows}\n{out}"
    rows, out = run_matrix(repo, ["tests/notes.md"])
    assert names(rows) == [SHORTCUT], f"804.6: a Markdown file under a folder the settings no longer list lost the shortcut: {rows}\n{out}"


# 804.7: the manual-fix check runs the tests in the test folder setting

def test_the_manual_fix_check_runs_the_test_folder_setting(record_property, tmp_path):
    """A manual fix's check runs the tests in the repo's own test folder.

    Proves 804.7. In a repo whose settings name `checks` as the test folder, a manual fix by Dokima's app must get one
    check that runs `checks`. In a repo with no settings file it must still run `tests`.
    """
    record_property("proves", "804.7")
    repo = make_repo(tmp_path, {"tests": {"dir": "checks"}})
    rows, out = run_matrix(repo, ["dokima/checks.py"], author=APP)
    assert rows is not None and len(rows) == 1 and rows[0]["tests"] == "checks", \
        f"804.7: the manual-fix check did not run the test folder setting (checks): {rows}\n{out}"
    plain = tmp_path / "plain"
    plain.mkdir()
    rows, out = run_matrix(plain, ["dokima/checks.py"], author=APP)
    assert rows is not None and len(rows) == 1 and rows[0]["tests"] == "tests", \
        f"804.7: with no settings file the manual-fix check no longer runs tests: {rows}\n{out}"


# 804.8: the planner's check refuses files outside the test folder setting

def test_the_planners_check_refuses_files_outside_the_test_folder_setting(record_property, tmp_path):
    """The planner may write only inside the repo's own test folder.

    Proves 804.8. The repo's settings name `checks` as the test folder. The planner writes its tests under `checks/`
    and one more file under `tests/`. The check must reject the plan naming the `tests/` file as outside the test
    folder, and must not name the file under `checks/`.
    """
    record_property("proves", "804.8")
    repo = make_repo(tmp_path, {"tests": {"dir": "checks"}}, base={"checks/test_old.py": "def test_old():\n    assert True\n"},
                     now={"checks/test_jobs.py": JOBS, "tests/helper.py": "VALUE = 1\n"})
    rc, why = run_check(repo, named("checks/test_jobs.py::test_id", "checks/test_jobs.py::test_unique"))
    assert rc == 1 and "tests/helper.py is outside" in why, \
        f"804.8: a file outside the test folder setting was not refused: {why}"
    assert "checks/test_jobs.py is outside" not in why, \
        f"804.8: a file inside the test folder setting was refused as outside it: {why}"


# 804.9: the planner's check lays the branch's test folder, from settings, over main

def test_the_new_test_check_lays_the_test_folder_setting_over_main(record_property, tmp_path):
    """New tests in the repo's own test folder run on main's code.

    Proves 804.9. The repo's settings name `checks` as the test folder. The planner adds `checks/test_jobs.py` with one
    test that passes today and one that fails. The check that new tests fail today must lay that folder over main and
    report the passing one, and only that one.
    """
    record_property("proves", "804.9")
    one = f"{shlex.quote(sys.executable)} -m pytest -q -p no:cacheprovider {{test}}"
    repo = make_repo(tmp_path, {"tests": {"dir": "checks", "run_one": one}},
                     base={"checks/test_old.py": "def test_old():\n    assert True\n"},
                     now={"checks/test_jobs.py": "def test_pass():\n    assert True\n\n\ndef test_fail():\n    assert False\n"})
    head = git(repo, "rev-parse", "HEAD").strip()
    code = ("import json, sys\nfrom dokima import planner\n"
            "print(json.dumps(planner.passing_today({'checks/test_jobs.py::test_pass': [], "
            "'checks/test_jobs.py::test_fail': []}, sys.argv[1])))")
    p = subprocess.run([sys.executable, "-c", code, head], cwd=repo, env={**os.environ, "PYTHONPATH": ROOT},
                       capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, f"804.9: the new-test check crashed: {p.stderr}"
    found = json.loads(p.stdout.strip().splitlines()[-1])
    assert any("checks/test_jobs.py::test_pass" in line for line in found), \
        f"804.9: a new test in the test folder setting was not run on main's code: {found}"
    assert not any("test_fail" in line for line in found), f"804.9: a failing new test was reported as passing: {found}"


# 804.10: the check that new tests fail today runs each with the run-one command setting

RUNNER = '''import sys
open(sys.argv[1], "a").write(sys.argv[3] + "\\n")
sys.exit(int(sys.argv[2]))
'''


def test_the_new_test_check_runs_each_test_with_the_run_one_setting(record_property, tmp_path):
    """Each new test is run with the repo's own run-one command.

    Proves 804.10. The repo's run-one command is a small runner that logs the test it is given and passes. The check
    must run it once per new test and so reject both as passing today. With a runner that fails, the plan must pass,
    and the log must still name both tests.
    """
    record_property("proves", "804.10")
    runner, log = tmp_path / "runner.py", tmp_path / "ran.log"
    runner.write_text(RUNNER)
    for verdict in (0, 1):
        one = f"{shlex.quote(sys.executable)} {shlex.quote(str(runner))} {shlex.quote(str(log))} {verdict} {{test}}"
        sub = tmp_path / f"v{verdict}"
        sub.mkdir()
        repo = make_repo(sub, {"tests": {"run_one": one}}, now={"tests/test_jobs.py": JOBS})
        if log.exists():
            log.unlink()
        rc, why = run_check(repo, STORY)
        ran = log.read_text().split() if log.exists() else []
        assert sorted(ran) == ["tests/test_jobs.py::test_id", "tests/test_jobs.py::test_unique"], \
            f"804.10: the run-one command setting did not run each new test once (ran {ran}): {why}"
        if verdict == 0:
            assert rc == 1 and "tests/test_jobs.py::test_id is a new test that passes today" in why, \
                f"804.10: the run-one command passed the tests but the check did not reject them: {why}"
        else:
            assert rc == 0, f"804.10: the run-one command failed the tests but the check rejected the plan: {why}"

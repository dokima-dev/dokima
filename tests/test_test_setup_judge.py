"""A pull request cannot change how its tests are judged through test setup files (#264).

Even with the all tests check running main's copy of its workflow (#263), pytest still reads setup and settings from
the files in the tree it runs in: every conftest.py, and pytest's settings in pytest.toml, .pytest.toml, pytest.ini,
.pytest.ini, pyproject.toml, setup.cfg and tox.ini, whether shipped as files or as links to files of the pull request's
own. A pull request that ships its own copy of one of them could make a failing test pass. These
tests play GitHub's part the way tests/test_all_tests_judge.py does (same tiny project, same step-by-step run of the
workflow): main's tree and the pull request's tree are written to temp folders, then every "all tests" job GitHub would
start, and the acceptance criteria check's per-criterion job of done-whens.yml, are run on the pull request. The
pull request's code is broken (its one test fails) and it adds, edits or deletes a setup file so that pytest would
report success; the check must still fail. A pull request with working code whose setup edits change nothing must pass, without its copies being read, and
main's own setup must still apply, so throwing every setup file away does not pass either.

The run is simulated the way tests/test_all_tests_judge.py does it: `actions/checkout` copies the tree its `ref` names
(with `path:` honoured) and every `run:` script runs with bash; the checkouts hold no git history. Like the real
checkout, the copy keeps symbolic links as links. Note that
tests/test_merge_queue.py also requires every `ref:` in full-suite.yml to name the queued commit in the merge queue.
"""
import os
import shutil

import pytest

import test_all_tests_judge as j
import test_start as ts

DONE_WHENS = os.path.join(j.WORKFLOWS, "done-whens.yml")

# main's own setup: a fixture in tests/conftest.py that one of main's tests needs.
MAIN_CONFTEST = '''"""Main's shared test setup."""
import pytest


@pytest.fixture
def answer():
    """The answer main's fixture test expects."""
    return 1
'''
TEST_FIXTURE = '''"""A test that only passes when main's tests/conftest.py is loaded."""


def test_answer(answer):
    assert answer == 1
'''

# Ways a conftest.py can turn a failing run into a passing one.
RIG_EXIT = '''def pytest_sessionfinish(session, exitstatus):
    session.exitstatus = 0
'''
RIG_REPORT = '''import pytest


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    report.outcome = "passed"
    return report
'''
# pytest settings that make it exit 0 without running a single test.
SKIP_ALL = "addopts = --collect-only\n"
SKIP_ALL_TOML = '[pytest]\naddopts = ["--collect-only"]\n'


class Link(str):
    """A symbolic link to write instead of a file, pointing at its text.

    The text is relative to the link's own folder."""

ATTACKS = {
    "adds a conftest.py at the root that turns the run's exit code to 0": {"conftest.py": RIG_EXIT},
    "adds a conftest.py in a folder under tests that turns the run's exit code to 0":
        {"tests/sub/conftest.py": RIG_EXIT, "tests/sub/__init__.py": ""},
    "edits main's tests/conftest.py to report every test as passed": {"tests/conftest.py": MAIN_CONFTEST + RIG_REPORT},
    "adds a pytest.ini that runs no test": {"pytest.ini": "[pytest]\n" + SKIP_ALL},
    "adds a .pytest.ini that runs no test": {".pytest.ini": "[pytest]\n" + SKIP_ALL},
    "adds a pyproject.toml whose pytest settings run no test":
        {"pyproject.toml": '[tool.pytest.ini_options]\naddopts = "--collect-only"\n'},
    "adds a setup.cfg whose pytest settings run no test": {"setup.cfg": "[tool:pytest]\n" + SKIP_ALL},
    "adds a tox.ini whose pytest settings run no test": {"tox.ini": "[pytest]\n" + SKIP_ALL},
    "adds a pytest.ini inside tests that runs no test": {"tests/pytest.ini": "[pytest]\n" + SKIP_ALL},
    "adds a pytest.toml that runs no test": {"pytest.toml": SKIP_ALL_TOML},
    "adds a .pytest.toml that runs no test": {".pytest.toml": SKIP_ALL_TOML},
    "adds a conftest.py at the root that is a link to its own file turning the run's exit code to 0":
        {"rig/hook.py": RIG_EXIT, "conftest.py": Link("rig/hook.py")},
    "replaces main's tests/conftest.py with a link to its own file reporting every test as passed":
        {"rig/report.py": MAIN_CONFTEST + RIG_REPORT, "tests/conftest.py": Link("../rig/report.py")},
    "adds a pytest.ini that is a link to its own file of settings that run no test":
        {"rig/settings.cfg": "[pytest]\n" + SKIP_ALL, "pytest.ini": Link("rig/settings.cfg")},
    "adds a pytest.toml that is a link to its own file of settings that run no test":
        {"rig/settings.toml": SKIP_ALL_TOML, "pytest.toml": Link("rig/settings.toml")},
}


@pytest.fixture(autouse=True)
def checkout_keeps_links(monkeypatch):
    """Copy trees keeping symbolic links as links, the way actions/checkout leaves them in the workspace."""
    copy = shutil.copytree

    def keep_links(src, dst, *args, **kwargs):
        if not args:
            kwargs.setdefault("symlinks", True)
        return copy(src, dst, *args, **kwargs)
    monkeypatch.setattr(shutil, "copytree", keep_links)



def harmless(marks):
    """Sets of setup edits that change no verdict but leave a mark when read.

    In the first set, a new conftest.py at the root and main's tests/conftest.py with a hook added each write a file
    when pytest loads them, and a new pyproject.toml asks pytest to write a JUnit report. pytest reads only one
    settings file, and pytest.toml comes before pyproject.toml, so a second set holds a new pytest.toml asking for a
    JUnit report, with a conftest.py in a folder under tests that is a link to a file of the pull request's own
    writing a file when loaded. None of them changes a test's verdict."""
    hook = "\n\ndef pytest_configure(config):\n    open({!r}, 'w').write('loaded')\n"
    return [{"conftest.py": '"""Nothing to set up."""' + hook.format(os.path.join(marks, "root-conftest")),
             "tests/conftest.py": MAIN_CONFTEST + hook.format(os.path.join(marks, "edited-conftest")),
             "pyproject.toml":
                 f'[tool.pytest.ini_options]\naddopts = "--junitxml={os.path.join(marks, "pyproject")}"\n'},
            {"pytest.toml": f'[pytest]\naddopts = ["--junitxml={os.path.join(marks, "pytest-toml")}"]\n',
             "rig/mark.py": '"""Nothing to set up."""' + hook.format(os.path.join(marks, "linked-conftest")),
             "tests/sub/conftest.py": Link("../../rig/mark.py"), "tests/sub/__init__.py": ""}]

# Main's settings turn every warning into a failure; the pull request's code warns and its copy deletes those settings.
STRICT = {"pytest.ini": "[pytest]\nfilterwarnings =\n    error::DeprecationWarning\n"}
APP_WARNS = "import warnings\n\n\ndef value():\n    warnings.warn('value() is old', DeprecationWarning)\n    return 1\n"
DELETES_STRICT = {"pytest.ini": None}


def write(tree, files):
    """Write files into a tree (path -> text); None deletes, a Link links.

    A Link replaces whatever is at its path with a symbolic link."""
    for rel, text in files.items():
        path = os.path.join(tree, rel)
        if os.path.lexists(path) and (text is None or isinstance(text, Link)):
            os.remove(path)
        if text is None:
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if isinstance(text, Link):
            os.symlink(str(text), path)
        else:
            open(path, "w").write(text)


def trees(tmp_path, app, main_files, pr_files):
    """Write main's tree and the pull request's: the tiny project, setup files and changes.

    Main's code is always the good one and both trees start with main's tests/conftest.py and fixture test, plus any
    main_files; the pull request's tree then gets pr_files on top, and its own app.py. Also writes a `pip` that does
    nothing. Returns (main's tree, the pull request's tree, the bin folder, the dump file)."""
    tmp_path = str(tmp_path)
    real = {n: open(os.path.join(j.WORKFLOWS, n)).read() for n in j.judge_files()}
    dump = os.path.join(tmp_path, "seen.jsonl")
    base, head = os.path.join(tmp_path, "main"), os.path.join(tmp_path, "pr")
    setup = {"tests/conftest.py": MAIN_CONFTEST, "tests/test_fixture.py": TEST_FIXTURE, **main_files}
    j.project(base, j.APP_GOOD, dump, real)
    j.project(head, app, dump, real)
    write(base, setup)
    write(head, setup)
    write(head, pr_files)
    shutil.copytree(os.path.join(j.ROOT, "dokima"), os.path.join(base, "dokima"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(os.path.join(j.ROOT, "dokima"), os.path.join(head, "dokima"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    bin_dir = os.path.join(tmp_path, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    open(os.path.join(bin_dir, "pip"), "w").write("#!/bin/sh\nexit 0\n")
    os.chmod(os.path.join(bin_dir, "pip"), 0o755)
    return base, head, bin_dir, dump


def all_tests(tmp_path, app, main_files=None, pr_files=None):
    """Run every all tests job GitHub would start on the pull request.

    Returns [(whose copy, conclusion, log)]."""
    base, head, bin_dir, _ = trees(tmp_path, app, main_files or {}, pr_files or {})
    runs = []
    for whose, tree, event in (("the pull request's", head, "pull_request"), ("main's", base, "pull_request_target")):
        for n in sorted(os.listdir(os.path.join(tree, ".github", "workflows"))):
            wf = ts.load_yaml(open(os.path.join(tree, ".github", "workflows", n)).read())
            if not isinstance(wf, dict) or not j.listens(wf, event):
                continue
            for job in (wf.get("jobs") or {}).values():
                if isinstance(job, dict) and job.get("name") == j.CHECK:
                    ws = os.path.join(str(tmp_path), f"run{len(runs)}", "ws")
                    os.makedirs(os.path.dirname(ws), exist_ok=True)
                    end, log = j.run_job(job, wf, event, base, head, ws, bin_dir)
                    runs.append((f"{whose} copy of {n}", end, log))
    return runs


def criterion_check(tmp_path, app, main_files=None, pr_files=None, monkeypatch=None):
    """Run main's per-criterion job of done-whens.yml for one criterion.

    The job's matrix is filled in as `python3 -m dokima.checks matrix` would for a plan whose criterion 1.1 lists
    tests/test_app.py and tests/test_fixture.py. Returns the job's conclusion and log."""
    base, head, bin_dir, _ = trees(tmp_path, app, main_files or {}, pr_files or {})
    wf = ts.load_yaml(open(DONE_WHENS).read())
    jobs = [job for job in (wf.get("jobs") or {}).values() if isinstance(job, dict) and "strategy" in job]
    assert len(jobs) == 1, "test setup: done-whens.yml no longer has exactly one per-criterion matrix job"
    job = {k: v for k, v in jobs[0].items() if k not in ("strategy", "needs", "if")}
    job["env"] = {**(job.get("env") or {}), "GITHUB_REPOSITORY": "o/r"}
    matrix = {"id": "1.1", "name": "1.1 works", "tests": "tests/test_app.py tests/test_fixture.py"}
    plain = j.context

    def with_matrix(event):
        ctx = plain(event)
        ctx["matrix"] = ts.Ctx(matrix)
        return ctx
    monkeypatch.setattr(j, "context", with_matrix)
    ws = os.path.join(str(tmp_path), "check", "ws")
    os.makedirs(os.path.dirname(ws), exist_ok=True)
    return j.run_job(job, wf, "pull_request_target", base, head, ws, bin_dir)


def test_main_test_setup_judges_and_the_pull_requests_copies_are_not_read(record_property, tmp_path, monkeypatch):
    """Main's test setup judges the pull request; its own copies are never read.

    Proves 264.1.
    A pull request with working code adds a conftest.py, edits main's tests/conftest.py and adds a pyproject.toml with
    pytest settings; another adds a pytest.toml and a conftest.py that is a link to a file of its own. Each of them
    leaves a file behind when pytest reads it. Both the all tests check and the
    acceptance criteria check must pass, run main's fixture test (it needs main's tests/conftest.py, so ignoring every
    conftest.py fails) and the app's test, and leave none of those files. Then main's settings make a deprecation
    warning fail: code that warns fails both checks and code that does not passes, so main's settings are applied."""
    record_property("proves", "264.1")
    for name, run in (("all tests", lambda d, f: all_tests(d, j.APP_GOOD, pr_files=f)),
                      ("the acceptance criteria check",
                       lambda d, f: [("main's done-whens.yml",) + criterion_check(d, j.APP_GOOD, None, f, monkeypatch)])):
        for k in range(len(harmless(""))):
            marks = str(tmp_path / f"marks-{len(name)}-{k}")
            os.makedirs(marks)
            runs = run(tmp_path / f"ok-{len(name)}-{k}", harmless(marks)[k])
            assert any(who.startswith("main's") for who, _, _ in runs), \
                f"264.1: GitHub would not run main's copy of {name}:\n{j.show(runs)}"
            assert j.green(runs), \
                f"264.1: a pull request with working code that only edits test setup did not pass {name}:\n" \
                f"{j.show(runs)}"
            for who, _, log in runs:
                assert "2 passed" in log, \
                    f"264.1: {who} did not run and pass both main's fixture test and the app's test:\n{log[-1500:]}"
            read = sorted(os.listdir(marks))
            assert not read, \
                f"264.1: {name} read the pull request's own test setup ({', '.join(read)}), not main's:\n" \
                f"{j.show(runs)}"
    runs = all_tests(tmp_path / "warns", APP_WARNS, main_files=STRICT)
    assert runs and not j.green(runs), \
        f"264.1: main's pytest settings were not applied: code that warns passed all tests:\n{j.show(runs)}"
    end, log = criterion_check(tmp_path / "warns-c", APP_WARNS, main_files=STRICT, monkeypatch=monkeypatch)
    assert end == "failure", \
        f"264.1: main's pytest settings were not applied: code that warns passed the acceptance criteria check:\n" \
        f"{log[-1500:]}"
    runs = all_tests(tmp_path / "strict-ok", j.APP_GOOD, main_files=STRICT)
    assert j.green(runs), f"264.1: working code did not pass all tests under main's settings:\n{j.show(runs)}"
    end, log = criterion_check(tmp_path / "strict-ok-c", j.APP_GOOD, main_files=STRICT, monkeypatch=monkeypatch)
    assert end == "success", \
        f"264.1: working code did not pass the acceptance criteria check under main's settings:\n{log[-1500:]}"


def test_editing_setup_files_cannot_make_failing_tests_pass_all_tests(record_property, tmp_path):
    """A failing test still fails all tests, whatever conftest.py or pytest settings are added.

    Proves 264.2.
    The pull request breaks the code its test checks, then ships one setup file at a time that would make pytest
    report success: a conftest.py at the root and one in a folder under tests that set the exit code to 0, main's own
    tests/conftest.py edited to report every test as passed, and pytest.toml, .pytest.toml, pytest.ini, .pytest.ini,
    pyproject.toml, setup.cfg, tox.ini and tests/pytest.ini each telling pytest to collect tests without running them.
    It then ships a root conftest.py, main's tests/conftest.py, a pytest.ini and a pytest.toml as links to rigged files
    of its own. Each time main's all tests
    run must still happen and fail, so the check fails."""
    record_property("proves", "264.2")
    for i, (how, files) in enumerate(ATTACKS.items()):
        runs = all_tests(tmp_path / f"a{i}", j.APP_BAD, pr_files=files)
        mains = [end for who, end, _ in runs if who.startswith("main's")]
        assert mains and "failure" in mains and not j.green(runs), \
            f"264.2: a pull request with a failing test that {how} passed all tests:\n{j.show(runs)}"


def test_deleting_mains_settings_cannot_make_failing_tests_pass_all_tests(record_property, tmp_path):
    """Deleting main's pytest settings does not stop them judging all tests.

    Proves 264.3.
    Main's pytest.ini turns every warning into a failure. The pull request's code warns, and its copy deletes main's
    pytest.ini, which would let the warning through. Main's all tests run must still happen and fail."""
    record_property("proves", "264.3")
    runs = all_tests(tmp_path, APP_WARNS, main_files=STRICT, pr_files=DELETES_STRICT)
    mains = [end for who, end, _ in runs if who.startswith("main's")]
    assert mains and "failure" in mains and not j.green(runs), \
        f"264.3: a pull request that deletes main's pytest.ini passed all tests with code main's settings fail:\n" \
        f"{j.show(runs)}"


def test_setup_files_cannot_make_failing_tests_pass_the_acceptance_criteria_check(record_property, tmp_path,
                                                                                  monkeypatch):
    """A failing criterion still fails its check, whatever setup files the pull request ships.

    Proves 264.4.
    Runs main's per-criterion job of done-whens.yml for a criterion proven by the app's test, on a pull request whose
    code breaks that test and which adds or edits each setup file of the all tests attacks, then on one whose code
    warns and which deletes main's pytest.ini that turns warnings into failures. Each run must fail."""
    record_property("proves", "264.4")
    cases = [(how, j.APP_BAD, {}, files) for how, files in ATTACKS.items()]
    cases.append(("deletes main's pytest.ini", APP_WARNS, STRICT, DELETES_STRICT))
    for i, (how, app, main_files, pr_files) in enumerate(cases):
        end, log = criterion_check(tmp_path / f"c{i}", app, main_files, pr_files, monkeypatch)
        assert end == "failure", \
            f"264.4: a pull request with a failing test that {how} passed the acceptance criteria check " \
            f"({end}):\n{log[-1500:]}"

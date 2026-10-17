"""Tests for #794: every test workflow sets up the repo's tests as the settings say.

The settings group is `setup:` in `.dokima/settings.yaml`, over the shipped defaults in `dokima/defaults.yaml`:

    setup:
      python: "3.12"                                  # the Python the repo's tests run on
      test_tools: pytest pytest-xdist pytest-testmon  # what each test workflow installs for the tests
      install: ""                                     # the repo's own install command, run before its tests

The test workflows are the all tests check (full-suite.yml), each criterion's check (acceptance-criteria.yml), the
testmon baseline (testmon.yml) and an agent's run (agent.yml), whose agent runs the repo's tests. Each test runs one
job's own steps the way GitHub runs them, through tests/test_start.py's machine: `if:` evaluated, `${{ }}` filled,
each script run with bash in a clone of a temp repo whose main holds the settings file. Here `pip`, `pip3`,
`pytest`, `python3 -m pip` and `python3 -m pytest` only log their arguments; a `setup-python` step logs the version it
was given (its `python-version`, expressions filled); the fake Claude Code logs when the agent starts. The log, in
order, shows what was installed, on which Python, before the repo's tests first ran. Nothing leaves the machine.
"""
import os
import shutil
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import test_start  # noqa: E402
from test_start import Ctx, Machine, N, SPLIT_PROPOSED, workflow  # noqa: E402

LOG_LINE = 'echo "{word} $*" >> "$SETUP_LOG"'
PYTHON = '''#!/bin/sh
# A stand-in for python3: `-m pytest` and `-m pip` only log; anything else runs the real Python.
if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then shift 2; echo "pytest $*" >> "$SETUP_LOG"; exit 0; fi
if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then shift 2; echo "pip $*" >> "$SETUP_LOG"; exit 0; fi
exec {real} "$@"
'''
CLAUDE = '''#!/bin/sh
# Notes that the agent, which runs the repo's tests, starts now; then runs the machine's fake Claude Code.
echo "agent-start" >> "$SETUP_LOG"
exec "$(dirname "$0")/claude-fake" "$@"
'''
DEFAULT_TOOLS = {"pytest", "pytest-xdist", "pytest-testmon"}
# What each job installed for the tests before #794, on Python 3.12: the list it falls back to.
OLD_TOOLS = {"full-suite.yml": {"pytest", "pytest-xdist"}, "acceptance-criteria.yml": {"pytest", "pytest-xdist"},
             "testmon.yml": {"pytest", "pytest-xdist", "pytest-testmon"},
             "agent.yml": {"pytest", "pytest-xdist", "pytest-testmon"}}
MAIN_BLOCK = '\nif __name__ == "__main__":'
OLD_MAIN = '''

del setup_lines


def main(argv=()):
    """The reader as #793 shipped it: prints every setting as JSON, whatever it is asked."""
    print(json.dumps(read(), indent=1))
    return 0
'''


def old_reader():
    """This checkout's settings reader without its setup mode, as #793 left it.

    It still reads the settings and prints them all as JSON, even when asked for `setup`, so a step that trusts it
    gets JSON where it expects `name=value` lines."""
    text = open(os.path.join(os.path.dirname(__file__), "..", "dokima", "settings.py")).read()
    assert MAIN_BLOCK in text, "794.8: dokima/settings.py has no main block to stand in for the old reader"
    head, tail = text.split(MAIN_BLOCK, 1)
    return head.rstrip() + "\n" + OLD_MAIN + MAIN_BLOCK + tail
JOBS = [("full-suite.yml", "all-tests"), ("acceptance-criteria.yml", "check"), ("testmon.yml", "baseline"),
        ("agent.yml", "run")]


class SetupRun(Machine):
    """One workflow job run on the machine, logging installs, Python versions and test runs."""

    def __init__(self, tmp, file, job, settings, reader=None):
        """Run JOB of workflow FILE with SETTINGS as main's settings file (None for none).

        READER, when given, is the text of `dokima/settings.py` in the Dokima code the run checks out from Dokima's own
        repo, in place of this checkout's: since #812 that is the only Dokima code a run uses."""
        files = {".dokima/settings.yaml": settings} if settings is not None else {}
        self.reader = reader
        super().__init__(tmp, SPLIT_PROPOSED if file == "agent.yml" else [], files=files)
        t = self.tmp
        self.setup_log = f"{t}/setup.log"
        open(self.setup_log, "w").close()
        tools = {"pip": LOG_LINE.format(word="pip"), "pip3": LOG_LINE.format(word="pip"),
                 "pytest": LOG_LINE.format(word="pytest")}
        for name, line in tools.items():
            open(f"{t}/bin/{name}", "w").write(f"#!/bin/sh\n{line}\n")
        for name in ("python3", "python"):
            open(f"{t}/bin/{name}", "w").write(PYTHON.replace("{real}", sys.executable))
        shutil.move(f"{t}/bin/claude", f"{t}/bin/claude-fake")
        open(f"{t}/bin/claude", "w").write(CLAUDE)
        for name in os.listdir(f"{t}/bin"):
            os.chmod(f"{t}/bin/{name}", 0o755)
        wf = workflow(file)
        steps = []
        for step in wf["jobs"][job].get("steps") or []:
            if "actions/setup-python" in str(step.get("uses") or ""):
                given = (step.get("with") or {}).get("python-version", "")
                step = {k: v for k, v in step.items() if k in ("id", "if", "name")}
                step.update({"env": {"PYVER": given}, "run": 'echo "python $PYVER" >> "$SETUP_LOG"\n'})
            steps.append(step)
        ctx = self.context(file)
        event = {"full-suite.yml": "pull_request_target", "acceptance-criteria.yml": "pull_request_target",
                 "testmon.yml": "push", "agent.yml": "workflow_dispatch"}[file]
        real = test_start.dokima_checkout
        test_start.dokima_checkout = self.checkout_with_reader(real)
        try:
            self.result, _ = self.run_job(job, {**wf["jobs"][job], "steps": steps}, ctx, event,
                                          [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        finally:
            test_start.dokima_checkout = real

    def checkout_with_reader(self, real):
        """The stand-in for checking out Dokima's repo, with this run's settings reader inside."""
        def checkout(step, ctx, status, into=None):
            """Check out Dokima's code as the machine does, then add the run's reader."""
            if into is None or self.reader is None:
                return real(step, ctx, status, into)
            dests = []
            found = real(step, ctx, status, into=lambda p: dests.append(into(p)) or dests[-1])
            for d in dests:
                open(os.path.join(d, "dokima", "settings.py"), "w").write(self.reader)
            return found
        return checkout

    def base_env(self, event_name):
        """The machine's environment, plus where the stand-ins log."""
        return {**super().base_env(event_name), "SETUP_LOG": self.setup_log}

    def context(self, file):
        """The GitHub contexts a run of FILE sees: a pull request or plan review."""
        pr = {"number": 60, "draft": False, "head": {"sha": ""}}
        github = Ctx(event_name="workflow_dispatch" if file == "agent.yml" else "pull_request_target", actor="owner-person",
                     event=Ctx(pull_request=pr) if file != "agent.yml" else Ctx(), run_id="42", run_attempt="1", sha="",
                     server_url="https://github.com", repository="o/r", token="fake-github-token")
        return {"inputs": Ctx(role="reviewer", stage="plan", issue=N), "github": github,
                "matrix": Ctx(tests="tests/test_x.py::test_a", id="9.1", name="9.1"),
                "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
                "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx(list=Ctx(outputs=Ctx(matrix="[]")))}

    def before_tests(self, crit):
        """The log lines before the repo's tests first ran; fails naming CRIT if never.

        The tests first run at the first pytest call, or when the agent starts, since agents run the tests."""
        lines = [l.strip() for l in open(self.setup_log).read().splitlines() if l.strip()]
        at = next((i for i, l in enumerate(lines) if l.split()[0] in ("pytest", "agent-start")), None)
        assert at is not None, (f"{crit}: the repo's tests never ran; the run stopped at '{self.failed_step}'; "
                                f"log {lines}\n{self.tail()}")
        return lines[:at]

    def installed(self, crit):
        """Every package pip was asked to install before the tests first ran."""
        out = []
        for line in self.before_tests(crit):
            words = line.split()
            if words[:2] != ["pip", "install"]:
                continue
            skip = False
            for w in words[2:]:
                if skip:
                    skip = False
                elif w in ("-r", "-c", "--requirement", "--constraint", "-e", "--editable"):
                    skip = True
                elif not w.startswith("-"):
                    out.append(w)
        return out


def where(file, job):
    """A job's name for a failure message."""
    return f"{file} job {job}"


@pytest.mark.parametrize("file,job", JOBS)
def test_the_repos_install_command_runs_before_its_tests(record_property, tmp_path, file, job):
    """In every test workflow, the install command the settings name runs before the repo's tests.

    Proves 794.7. Runs each test workflow's job with a settings file whose install command writes 'install-ran' to the
    log, and checks that line comes before the tests first run. Then runs it again with no install command, the
    default, and checks the tests still run."""
    record_property("proves", "794.7")
    settings = 'setup:\n  install: echo install-ran >> "$SETUP_LOG"\n'
    r = SetupRun(tmp_path / "with", file, job, settings)
    before = r.before_tests("794.7")
    assert "install-ran" in before, \
        f"794.7: in {where(file, job)} the repo's install command did not run before its tests; log before them: {before}"
    r = SetupRun(tmp_path / "without", file, job, 'setup:\n  install: ""\n')
    r.before_tests("794.7")


@pytest.mark.parametrize("file,job", JOBS)
def test_the_test_tools_installed_come_from_the_test_tools_setting(record_property, tmp_path, file, job):
    """Every test workflow installs exactly the test tools the settings name.

    Proves 794.8. Runs each test workflow's job with a settings file naming two made-up test tools, and checks both
    were installed before the tests first ran and none of the default tools was."""
    record_property("proves", "794.8")
    r = SetupRun(tmp_path / "run", file, job, "setup:\n  test_tools: odd-runner odd-plugin\n")
    got = r.installed("794.8")
    assert {"odd-runner", "odd-plugin"} <= set(got), \
        f"794.8: {where(file, job)} did not install the test tools the setting names (odd-runner odd-plugin); got {got}"
    extra = sorted(DEFAULT_TOOLS & set(got))
    assert not extra, f"794.8: {where(file, job)} installed default test tools {extra} the setting does not name"


@pytest.mark.parametrize("file,job", JOBS)
def test_the_repos_tests_run_on_the_python_the_settings_name(record_property, tmp_path, file, job):
    """Every test workflow runs the repo's tests on the Python version the settings name.

    Proves 794.9. Runs each test workflow's job with a settings file naming Python 3.11, and checks the last Python
    set up before the tests first ran was 3.11."""
    record_property("proves", "794.9")
    r = SetupRun(tmp_path / "run", file, job, 'setup:\n  python: "3.11"\n')
    versions = [l.split(None, 1)[1] if " " in l else "" for l in r.before_tests("794.9") if l.split()[0] == "python"]
    assert versions and versions[-1] == "3.11", \
        f"794.9: in {where(file, job)} the tests ran on Python {versions[-1] if versions else 'never set up'!r}, not 3.11"


@pytest.mark.parametrize("file,job", JOBS)
def test_a_reader_without_the_setup_mode_falls_back_to_the_old_install_list(record_property, tmp_path, file, job):
    """Test workflows follow settings only if the reader has a setup mode, else old tools.

    Proves 794.8, as the owner asked after the merge queue broke: check for the mode, not the file. Runs each test
    workflow's job twice with a settings file naming other tools and Python 3.11. With this checkout's reader the job
    must install the named tools. With the same reader stripped of its setup mode, as #793 left main, in the Dokima
    code the run checks out (#812), the job must still reach the repo's tests, having installed exactly the old list
    on Python 3.12 and none of the named tools."""
    record_property("proves", "794.8")
    settings = 'setup:\n  python: "3.11"\n  test_tools: odd-runner odd-plugin\n'
    r = SetupRun(tmp_path / "new", file, job, settings)
    got = set(r.installed("794.8"))
    assert {"odd-runner", "odd-plugin"} <= got, (f"794.8: with a settings reader that has a setup mode, "
                                                 f"{where(file, job)} did not install the tools the settings name; "
                                                 f"got {sorted(got)}")
    r = SetupRun(tmp_path / "old", file, job, settings, reader=old_reader())
    got = set(r.installed("794.8"))
    missing = sorted(OLD_TOOLS[file] - got)
    assert not missing, (f"794.8: with a settings reader that has no setup mode, {where(file, job)} did not install "
                         f"the old test tools {missing}; got {sorted(got)}")
    named = sorted({"odd-runner", "odd-plugin"} & got)
    assert not named, (f"794.8: with a settings reader that has no setup mode, {where(file, job)} installed {named}; "
                       f"it should fall back to the old list")
    versions = [l.split(None, 1)[1] if " " in l else "" for l in r.before_tests("794.8") if l.split()[0] == "python"]
    assert versions and versions[-1] == "3.12", (f"794.8: with a settings reader that has no setup mode, "
                                                 f"{where(file, job)} set up Python "
                                                 f"{versions[-1] if versions else 'never'!r}, not the old 3.12")

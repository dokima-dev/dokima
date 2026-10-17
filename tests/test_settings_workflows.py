"""Tests for #795: test commands, branches and the bot follow the repo's settings.

The settings live in `.dokima/settings.yaml` on the default branch, over Dokima's shipped defaults in
`dokima/defaults.yaml`. This story reads these of them:

    tests:
      run_all: pytest -q -p no:cacheprovider -n auto tests        # the all tests check's command
      run_one: python -m pytest -q -p no:cacheprovider {test}     # each criterion's check; {test} is its tests
      affected: testmon                                            # `all`: every test before review, no baseline
      dir: tests                                                   # the test folder
      exclude: []                                                  # tests the all tests check leaves out, by id
    branch:
      default: main                                                # where branches start and pull requests go
    records:
      branch: logs                                                 # where each run's conversation is saved
    bot:
      slug: dokima-runtime                                         # the bot that signals and commits

Each test runs real steps of a workflow the way GitHub runs them, through tests/test_start.py's machine: `if:`
evaluated, `${{ }}` filled, each script run with bash in a clone of a temp repo whose default branch holds the
settings file. `pip` only logs; unless a test runs the tests for real, `pytest`, `python3 -m pytest` and `python3 -m
pip` only log their arguments too, and testmon leaves a baseline file. A `setup-python` step logs its version; a cache restore step logs and leaves a
baseline file; a cache save step logs. Each job's log, in order, shows what ran. Nothing leaves the machine.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_start as ts  # noqa: E402
from test_start import Ctx, N  # noqa: E402

LOG_LINE = 'echo "{word} $*" >> "$SETUP_LOG"'
PYTHON = '''#!/bin/sh
# A stand-in for python3: `-m pytest` and `-m pip` only log, and `--testmon` leaves a baseline file, as testmon
# does; anything else runs the real Python.
if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then shift 2; echo "pytest $*" >> "$SETUP_LOG"
  case " $* " in *" --testmon "*) echo baseline > .testmondata ;; esac; exit 0; fi
if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then shift 2; echo "pip $*" >> "$SETUP_LOG"; exit 0; fi
exec {real} "$@"
'''
REAL_PYTHON = '''#!/bin/sh
# A stand-in for python3: `-m pip` only logs; anything else, the tests too, runs the real Python.
if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then shift 2; echo "pip $*" >> "$SETUP_LOG"; exit 0; fi
exec {real} "$@"
'''
REAL_PYTEST = '#!/bin/sh\nexec {real} -m pytest "$@"\n'
OTHER_BOT = "other-bot"
WIKI_URL = "https://x-access-token:fake-github-token@github.com/o/r.wiki.git"


class Box(ts.Machine):
    """A temp repo, its settings file on its default branch, where workflow steps run.

    SETTINGS is the text of `.dokima/settings.yaml` (None for none); FILES are more files on main. With real_tests the
    repo's tests run for real; otherwise pytest only logs. With no_identity the steps run with no git identity of
    the machine's own, as on GitHub, so a commit carries only the identity the workflow gives it."""

    def __init__(self, tmp, settings=None, files=None, real_tests=False, no_identity=False):
        """Set up the repo, its origin and the stand-ins."""
        self.no_identity = no_identity
        files = dict(files or {})
        if settings is not None:
            files[".dokima/settings.yaml"] = settings
        super().__init__(tmp, [], files=files)
        t = self.tmp
        self.src = f"{t}/src"
        self.setup_log = f"{t}/setup.log"
        open(self.setup_log, "w").close()
        stubs = {"pip": LOG_LINE.format(word="pip"), "pip3": LOG_LINE.format(word="pip")}
        for name, line in stubs.items():
            open(f"{t}/bin/{name}", "w").write(f"#!/bin/sh\n{line}\n")
        if real_tests:
            open(f"{t}/bin/pytest", "w").write(REAL_PYTEST.replace("{real}", sys.executable))
        else:
            open(f"{t}/bin/pytest", "w").write(f"#!/bin/sh\n{LOG_LINE.format(word='pytest')}\n")
        for name in ("python3", "python"):
            open(f"{t}/bin/{name}", "w").write((REAL_PYTHON if real_tests else PYTHON).replace("{real}", sys.executable))
        for name in os.listdir(f"{t}/bin"):
            os.chmod(f"{t}/bin/{name}", 0o755)

    def base_env(self, event_name):
        """The machine's environment, plus where the stand-ins log and a local wiki repo."""
        env = {**super().base_env(event_name), "SETUP_LOG": self.setup_log}
        if self.no_identity:
            for k in ("GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "GIT_COMMITTER_NAME", "GIT_COMMITTER_EMAIL"):
                env.pop(k, None)
            env["GIT_CONFIG_NOSYSTEM"], env["GIT_CONFIG_GLOBAL"] = "1", os.devnull
        n = int(env["GIT_CONFIG_COUNT"])
        env[f"GIT_CONFIG_KEY_{n}"], env[f"GIT_CONFIG_VALUE_{n}"] = f"url.file://{self.tmp}/wiki.git.insteadOf", WIKI_URL
        env["GIT_CONFIG_COUNT"] = str(n + 1)
        return env

    def commit(self, branch, files, message, start=None):
        """Commit FILES on BRANCH, made from START when given, and push it."""
        src = self.src
        if start is not None:
            ts.sh(src, "git", "checkout", "-q", "-B", branch, start)
        else:
            ts.sh(src, "git", "checkout", "-q", branch)
        for path, text in files.items():
            os.makedirs(os.path.dirname(f"{src}/{path}") or src, exist_ok=True)
            open(f"{src}/{path}", "w").write(text)
        ts.sh(src, "git", "add", "-A")
        ts.sh(src, "git", "commit", "-qm", message)
        ts.sh(src, "git", "push", "-q", "origin", branch)
        return ts.sh(src, "git", "rev-parse", "HEAD")

    def context(self, role="planner", stage="", event="workflow_dispatch", actor=ts.OWNER, tests="tests/test_x.py::test_a"):
        """The GitHub contexts one run sees."""
        pr = {"number": 60, "draft": False, "head": {"sha": ""}}
        github = Ctx(event_name=event, actor=actor, event=Ctx(pull_request=pr), run_id="42", run_attempt="1", sha="",
                     server_url="https://github.com", repository="o/r", repository_owner="o", token="fake-github-token",
                     ref="refs/heads/main", ref_name="main")
        return {"inputs": Ctx(role=role, stage=stage, issue=N, branch="fix/typo"), "github": github,
                "client_payload": Ctx(), "matrix": Ctx(tests=tests, id="9.1", name="9.1"),
                "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
                "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}

    def run(self, file, job, steps=None, name=None, env=None, **context):
        """Run JOB of workflow FILE, or only STEPS, on a fresh clone; its result.

        Each step that uses a GitHub action this machine cannot run is replaced by a stand-in that logs, keeping its
        `if:`. ENV is added to the job's own environment."""
        t = self.tmp
        wf = ts.workflow(file)
        whole = wf["jobs"][job]
        ctx = self.context(**context)
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": ctx["inputs"]["role"],
                                                                  "stage": ctx["inputs"]["stage"], "issue": N}}))
        body = {**whole, "env": {**(whole.get("env") or {}), **(env or {})},
                "steps": stand_ins(steps if steps is not None else whole.get("steps") or [])}
        self.failed_step = None
        result, _ = self.run_job(name or job, body, ctx, ctx["github"]["event_name"],
                                 [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        return result

    def run_workflow(self, file, **context):
        """Run every job of FILE in order, each when its `if:` holds; {job: result}."""
        t = self.tmp
        wf = ts.workflow(file)
        needs, results = {}, {}
        for name, job in wf["jobs"].items():
            ctx = {**self.context(**context), "needs": Ctx(needs)}
            failed = any(needs[n]["result"] != "success" for n in as_list(job.get("needs")) if n in needs)
            if not ts.evaluate(ts.condition(job.get("if")), ctx, {"failed": failed}):
                results[name] = "skipped"
                needs[name] = {"result": "skipped", "outputs": {}}
                continue
            body = {**job, "steps": stand_ins(job.get("steps") or [])}
            results[name], out = self.run_job(name, body, ctx, ctx["github"]["event_name"],
                                              [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
            needs[name] = {"result": results[name], "outputs": out}
        return results

    def lines(self):
        """The stand-ins' log, one entry per line."""
        return [l.strip() for l in open(self.setup_log).read().splitlines() if l.strip()]

    def origin(self, *args):
        """Run git in the temp origin; (exit code, output)."""
        p = subprocess.run(["git", "--git-dir", f"{self.tmp}/origin.git", *args], capture_output=True, text=True)
        return p.returncode, p.stdout.strip()

    def gh_calls(self, *start):
        """Every call to the fake gh that starts with START."""
        return [c for c in self.calls() if c[:len(start)] == list(start)]


def as_list(v):
    """A job's `needs`, as a list."""
    return [] if not v else [v] if isinstance(v, str) else list(v)


def stand_ins(steps):
    """STEPS with each action the machine cannot run swapped for a logging stand-in."""
    out = []
    for step in steps:
        uses = str(step.get("uses") or "")
        keep = {k: v for k, v in step.items() if k in ("id", "if", "name")}
        if "actions/setup-python" in uses:
            keep.update({"env": {"PYVER": str((step.get("with") or {}).get("python-version", ""))},
                         "run": 'echo "python $PYVER" >> "$SETUP_LOG"\n'})
        elif "actions/cache/save" in uses:
            keep["run"] = 'echo "cache-saved" >> "$SETUP_LOG"\n'
        elif "actions/cache/restore" in uses:
            keep["run"] = 'echo "cache-restored" >> "$SETUP_LOG"\necho baseline > .testmondata\n'
        else:
            keep = step
        out.append(keep)
    return out


def steps_of(file, job):
    """The steps of JOB in workflow FILE, by name, and in order."""
    steps = ts.workflow(file)["jobs"][job]["steps"]
    return {s.get("name"): s for s in steps if s.get("name")}, steps


def step_named(steps, start):
    """The first step whose name starts with START; fails naming it when none does."""
    found = next((s for s in steps if str(s.get("name", "")).startswith(start)), None)
    assert found is not None, f"agent.yml has no step named '{start}...'"
    return found


def through(steps, start):
    """A job's steps up to and including the first whose name starts with START."""
    return steps[:steps.index(step_named(steps, start)) + 1]


def app_step(steps):
    """The step that mints the app's token for the result."""
    return next(s for s in steps if s.get("id") == "app")


def stand_in(name, script):
    """A step standing in for an agent: makes its folders, then runs SCRIPT."""
    return {"name": name, "run": 'mkdir -p "$PACK" "$OUT"\n' + script}


def author_of(ws, ref="HEAD"):
    """The author name and email of a commit in the clone at WS."""
    return ts.sh(ws, "git", "log", "-1", "--format=%an|%ae", ref).split("|")


# 795.1 ------------------------------------------------------------------------------------------------------------

def test_the_all_tests_check_runs_the_all_tests_command_from_settings(record_property, tmp_path):
    """The all tests check runs the all-tests command the settings name.

    Proves 795.1. Runs the all tests job of full-suite.yml in the merge queue, where every test runs (on a pull
    request only the affected tests run, owner 2026-10-17), with a settings file whose all-tests command writes
    'all-ran' to the log, and checks it ran and pytest's default command did not. Then runs it with no settings file
    and checks the default command, pytest over the tests folder, still runs."""
    record_property("proves", "795.1")
    box = Box(tmp_path / "set", 'tests:\n  run_all: echo all-ran >> "$SETUP_LOG"\n')
    result = box.run("full-suite.yml", "all-tests", event="merge_group")
    lines = box.lines()
    assert "all-ran" in lines, (f"795.1: the all tests check did not run the all-tests command from settings; "
                                f"job {result}, log {lines}\n{box.tail()}")
    ran = [l for l in lines if l.startswith("pytest")]
    assert not ran, f"795.1: the all tests check still ran its own pytest command beside the setting's: {ran}"
    box = Box(tmp_path / "default", None)
    box.run("full-suite.yml", "all-tests", event="merge_group")
    ran = [l for l in box.lines() if l.startswith("pytest")]
    assert ran and ran[-1].split()[-1] == "tests", \
        f"795.1: with no settings file the all tests check no longer runs pytest over tests; log {box.lines()}"


# 795.2 ------------------------------------------------------------------------------------------------------------

READER_794 = os.path.join(os.path.dirname(__file__), "fixtures", "settings_before_795.py")


def test_each_criterions_check_runs_the_per_criterion_command_from_settings(record_property, tmp_path):
    """Each criterion's check runs the per-criterion command the settings name, on its own tests.

    Proves 795.2. Runs the check job of acceptance-criteria.yml for a criterion whose test is tests/test_x.py::test_a,
    with a settings file whose per-criterion command logs 'one-ran {test}', and checks it ran with the test filled in.
    Then: with no settings file the default pytest command runs that test and writes the report the annotations read.
    Last, with main's settings reader as it was before this change (the merge queue runs main's reader beside the
    new workflow), the criterion's test still runs."""
    record_property("proves", "795.2")
    box = Box(tmp_path / "set", 'tests:\n  run_one: echo one-ran {test} >> "$SETUP_LOG"\n')
    result = box.run("acceptance-criteria.yml", "check", event="pull_request_target")
    lines = box.lines()
    ran = [l for l in lines if l.startswith("one-ran")]
    assert ran, (f"795.2: the criterion's check did not run the per-criterion command from settings; job {result}, "
                 f"log {lines}\n{box.tail()}")
    assert "tests/test_x.py::test_a" in ran[0].split(), \
        f"795.2: the per-criterion command ran without the criterion's test in place of {{test}}: {ran[0]!r}"
    assert not [l for l in lines if l.startswith("pytest")], \
        f"795.2: the criterion's check still ran its own pytest command beside the setting's: {lines}"
    box = Box(tmp_path / "default", None)
    box.run("acceptance-criteria.yml", "check", event="pull_request_target")
    ran = [l for l in box.lines() if l.startswith("pytest")]
    assert ran and "tests/test_x.py::test_a" in ran[-1].split(), \
        f"795.2: with no settings file the criterion's check no longer runs pytest on its test; log {box.lines()}"
    assert "--junitxml" in ran[-1], \
        f"795.2: with no settings file the criterion's check no longer writes the report its annotations read: {ran[-1]!r}"
    box = Box(tmp_path / "old", 'tests:\n  run_one: echo one-ran {test} >> "$SETUP_LOG"\n',
              files={"dokima/settings.py": open(READER_794).read()})
    result = box.run("acceptance-criteria.yml", "check", event="pull_request_target")
    ran = [l for l in box.lines() if l.split()[0] in ("pytest", "one-ran") and "tests/test_x.py::test_a" in l.split()]
    assert ran, (f"795.2: with main's settings reader from before this change the criterion's test never ran; "
                 f"job {result}, log {box.lines()}\n{box.tail()}")


# 795.3 ------------------------------------------------------------------------------------------------------------

def review_run(tmp, settings):
    """A code review's run of agent.yml up to its test run; (box, result).

    The branch try/issue-57 exists. The starting pack is stood in for by an empty folder; the cache restore step
    leaves a baseline file, as GitHub's does when main has one."""
    box = Box(tmp, settings)
    box.commit(f"try/issue-{N}", {"app.py": "a = 1\n"}, "the work", start="main")
    _, steps = steps_of("agent.yml", "run")
    upto = through(steps, "Tests the change can affect")
    chosen = [stand_in("The starting pack", "") if s.get("name") == "Build the starting pack" else s for s in upto]
    result = box.run("agent.yml", "run", chosen, role="reviewer", stage="pr")
    return box, result


def test_setting_affected_tests_to_all_runs_every_test_before_review(record_property, tmp_path):
    """With affected tests set to all, a code review runs every test, never testmon.

    Proves 795.3. Runs a code review's run of agent.yml up to its test run, where main has a saved baseline, with a
    settings file saying `affected: all`, and checks pytest ran and never with testmon. Then runs it with no
    settings file and checks testmon picks the tests from the baseline, as today."""
    record_property("proves", "795.3")
    box, result = review_run(tmp_path / "all", "tests:\n  affected: all\n")
    ran = [l for l in box.lines() if l.startswith("pytest")]
    assert ran, f"795.3: the code review's tests never ran; job {result}, log {box.lines()}\n{box.tail()}"
    used = [l for l in ran if "--testmon" in l.split()]
    assert not used, f"795.3: with affected tests set to all, the review still ran tests from the baseline: {used}"
    box, result = review_run(tmp_path / "default", None)
    ran = [l for l in box.lines() if l.startswith("pytest")]
    assert any("--testmon" in l.split() for l in ran), \
        f"795.3: with no settings file the review no longer picks its tests from the baseline; log {box.lines()}"


def test_setting_affected_tests_to_all_saves_no_baseline_on_main(record_property, tmp_path):
    """With affected tests set to all, a push to main saves no testmon baseline.

    Proves 795.3. Runs every job of testmon.yml for a push to main with a settings file saying `affected: all`, and
    checks no baseline was saved, testmon never ran, and no job failed. Then runs it with no settings file and checks
    the baseline is saved, as today."""
    record_property("proves", "795.3")
    box = Box(tmp_path / "all", "tests:\n  affected: all\n")
    results = box.run_workflow("testmon.yml", event="push")
    lines = box.lines()
    assert "cache-saved" not in lines, f"795.3: with affected tests set to all, main still saved a baseline; log {lines}"
    assert not [l for l in lines if "--testmon" in l.split()], \
        f"795.3: with affected tests set to all, main still ran testmon; log {lines}"
    assert "failure" not in results.values(), \
        f"795.3: with affected tests set to all, testmon.yml failed: {results}\n{box.tail()}"
    box = Box(tmp_path / "default", None)
    box.run_workflow("testmon.yml", event="push")
    assert "cache-saved" in box.lines(), f"795.3: with no settings file main no longer saves a baseline; log {box.lines()}"


# 795.4 ------------------------------------------------------------------------------------------------------------

SPEC = "tests:\n  dir: spec\n"


def clash_box(tmp):
    """A repo testing in spec/, where main and the branch both changed notes.md.

    Base: notes.md and spec/test_x.py. The branch first took main's spec/test_x.py, then changed it (the planner's
    change). Main changed notes.md, changed spec/test_x.py and added spec/test_main.py."""
    box = Box(tmp, SPEC)
    base = box.commit("main", {"notes.md": "notes\n", "spec/test_x.py": "def test_a():\n    assert 0\n"}, "base")
    box.commit(f"try/issue-{N}", {"spec/test_x.py": "def test_a():\n    assert 'main'\n"}, "took main's test", start=base)
    box.commit(f"try/issue-{N}", {"notes.md": "notes, the branch's\n",
                                  "spec/test_x.py": "def test_a():\n    assert 'planner'\n"}, "the planner's change")
    box.commit("main", {"notes.md": "notes, main's\n", "spec/test_x.py": "def test_a():\n    assert 'main'\n",
                        "spec/test_main.py": "def test_m():\n    assert 1\n"}, "main moves on")
    return box


def test_a_planners_clash_with_main_takes_mains_tests_from_the_settings_test_folder(record_property, tmp_path):
    """A planner clashing with main is handed main's tests from the settings' test folder.

    Proves 795.4. The settings name spec/ as the test folder. Main added spec/test_main.py and the branch clashes
    with main in notes.md. Runs the planner's checkout of agent.yml and a stand-in planner that keeps what it found,
    and checks spec/test_main.py was there for it."""
    record_property("proves", "795.4")
    box = clash_box(tmp_path)
    _, steps = steps_of("agent.yml", "run")
    look = stand_in("The planner", "ls -R spec > /tmp/planner_saw.txt 2>&1 || true\n")
    result = box.run("agent.yml", "run", through(steps, "Starting branch") + [look], name="planner", role="planner")
    saw = open(f"{box.tmp}/planner_saw.txt").read().split() if os.path.exists(f"{box.tmp}/planner_saw.txt") else None
    assert saw is not None, f"795.4: the planner's run never reached the planner; job {result}\n{box.tail()}"
    assert "test_main.py" in saw, (f"795.4: on a clash with main, the planner was not handed main's new test in the "
                                   f"settings' test folder spec/; it saw {saw}")


def test_a_workers_clash_with_main_keeps_the_planners_test_in_the_settings_test_folder(record_property, tmp_path):
    """A worker's clash with main keeps the planner's test from the folder the settings name.

    Proves 795.4. The settings name spec/ as the test folder. The planner took main's spec/test_x.py, then changed
    it; main changed it again and clashes in notes.md too. Runs the worker's checkout of agent.yml and checks only
    notes.md is left for the worker to resolve, with spec/test_x.py as the planner wrote it."""
    record_property("proves", "795.4")
    box = clash_box(tmp_path)
    _, steps = steps_of("agent.yml", "run")
    look = stand_in("The worker", "cp spec/test_x.py /tmp/worker_saw.py\n")
    result = box.run("agent.yml", "run", through(steps, "Starting branch") + [look], name="worker", role="worker")
    clashed = open(f"{box.tmp}/clashed.txt").read().split() if os.path.exists(f"{box.tmp}/clashed.txt") else []
    assert "notes.md" in clashed, f"795.4: the worker's clash with main in notes.md was not listed; job {result}\n{box.tail()}"
    assert "spec/test_x.py" not in clashed, \
        f"795.4: the planner's test in the settings' test folder spec/ was handed to the worker as a clash: {clashed}"
    saw = open(f"{box.tmp}/worker_saw.py").read() if os.path.exists(f"{box.tmp}/worker_saw.py") else ""
    assert "'planner'" in saw, f"795.4: the worker did not get the planner's spec/test_x.py; it found {saw!r}"


# 795.5 ------------------------------------------------------------------------------------------------------------

def test_the_planners_push_holds_only_files_in_the_settings_test_folder(record_property, tmp_path):
    """The planner's push holds its tests in the settings' folder, and nothing else.

    Proves 795.5. The settings name spec/ as the test folder. A stand-in planner writes spec/test_new.py,
    tests/test_old.py and notes.md. Runs agent.yml's checkout and push for the planner and checks the pushed branch
    holds spec/test_new.py and neither of the others."""
    record_property("proves", "795.5")
    box = Box(tmp_path, SPEC)
    _, steps = steps_of("agent.yml", "run")
    write = stand_in("The planner", "mkdir -p spec tests\n"
                                    "printf 'def test_n():\\n    assert 0\\n' > spec/test_new.py\n"
                                    "printf 'def test_o():\\n    assert 0\\n' > tests/test_old.py\n"
                                    "echo stray > notes.md\n")
    push = step_named(steps, "Push the planner's tests")
    result = box.run("agent.yml", "run", through(steps, "Starting branch") + [write, app_step(steps), push],
                     name="planner", role="planner", env={"PASSED": "true", "STARTED": "true"})
    code, files = box.origin("ls-tree", "-r", "--name-only", f"try/issue-{N}")
    files = files.split() if code == 0 else []
    assert "spec/test_new.py" in files, (f"795.5: the planner's push did not hold its test in the settings' test "
                                         f"folder spec/; branch holds {files}; job {result}\n{box.tail()}")
    stray = sorted({"tests/test_old.py", "notes.md"} & set(files))
    assert not stray, f"795.5: the planner's push held files outside the settings' test folder spec/: {stray}"


# 795.6 ------------------------------------------------------------------------------------------------------------

GATE_TESTS = '''import os


def test_kept():
    """Runs, and says so."""
    open(os.environ["SETUP_LOG"], "a").write("kept-ran\\n")


def test_live():
    """A live network test the repo keeps off the merge gate."""
    open(os.environ["SETUP_LOG"], "a").write("live-ran\\n")
    assert False, "live network"
'''


def test_tests_on_the_exclude_list_stay_out_of_the_all_tests_check(record_property, tmp_path):
    """A test on the exclude list never runs in the all tests check; others do.

    Proves 795.6. The repo has two real tests: test_kept passes, test_live fails. Runs the all tests job of
    full-suite.yml for real with `exclude: [tests/test_gate.py::test_live]` and checks the job passed, test_kept ran
    and test_live did not. Then, with the default empty list, checks test_live runs and the job fails."""
    record_property("proves", "795.6")
    files = {"tests/test_gate.py": GATE_TESTS}
    box = Box(tmp_path / "set", "tests:\n  exclude: [tests/test_gate.py::test_live]\n", files=files, real_tests=True)
    result = box.run("full-suite.yml", "all-tests", event="pull_request_target")
    lines = box.lines()
    assert "live-ran" not in lines, f"795.6: the all tests check ran tests/test_gate.py::test_live, on the exclude list"
    assert "kept-ran" in lines, f"795.6: the all tests check did not run test_kept, not on the list; log {lines}\n{box.tail()}"
    assert result == "success", f"795.6: the all tests check failed with the failing test excluded:\n{box.tail()}"
    box = Box(tmp_path / "default", None, files=files, real_tests=True)
    result = box.run("full-suite.yml", "all-tests", event="pull_request_target")
    assert "live-ran" in box.lines() and result == "failure", \
        f"795.6: with no exclude list, the all tests check did not run and fail on test_live; job {result}"


# 795.7 ------------------------------------------------------------------------------------------------------------

TRUNK = "branch:\n  default: trunk\n"


def test_agents_base_their_branches_and_pull_requests_on_the_default_branch_setting(record_property, tmp_path):
    """A worker merges the default branch the settings name, and opens its pull request there.

    Proves 795.7. The settings name trunk as the default branch; trunk has a commit main lacks. Runs a worker's
    checkout, a stand-in worker that writes code.py, and the push of agent.yml. Checks the pushed branch holds
    trunk's commit and the pull request was opened with trunk as its base."""
    record_property("proves", "795.7")
    box = Box(tmp_path, TRUNK)
    box.commit(f"try/issue-{N}", {"app.py": "a = 1\n"}, "the work", start="main")
    trunk = box.commit("trunk", {"trunk.txt": "only on trunk\n"}, "trunk moves on", start="main")
    _, steps = steps_of("agent.yml", "run")
    work = stand_in("The worker", "echo 'c = 1' > code.py\n")
    push = step_named(steps, "Push the planner's tests")
    result = box.run("agent.yml", "run", through(steps, "Starting branch") + [work, app_step(steps), push],
                     name="worker", role="worker", env={"PASSED": "true", "STARTED": "true"})
    code, _ = box.origin("merge-base", "--is-ancestor", trunk, f"try/issue-{N}")
    assert code == 0, (f"795.7: the worker's branch was not brought up to trunk, the default branch the settings "
                       f"name; job {result}\n{box.tail()}")
    made = box.gh_calls("pr", "create")
    assert made, f"795.7: the worker opened no pull request; job {result}\n{box.tail()}"
    base = made[-1][made[-1].index("--base") + 1] if "--base" in made[-1] else None
    assert base == "trunk", f"795.7: the worker's pull request goes to {base!r}, not trunk, the default branch setting"


def test_a_planners_new_branch_starts_from_the_default_branch_setting(record_property, tmp_path):
    """A planner's new branch starts from the default branch the settings name.

    Proves 795.7. The settings name trunk as the default branch; trunk has a commit main lacks, and the issue has
    no branch yet. Runs a planner's checkout of agent.yml and a stand-in planner that notes whether trunk's commit
    is in what it starts from."""
    record_property("proves", "795.7")
    box = Box(tmp_path, TRUNK)
    trunk = box.commit("trunk", {"trunk.txt": "only on trunk\n"}, "trunk moves on", start="main")
    _, steps = steps_of("agent.yml", "run")
    look = stand_in("The planner", f"git merge-base --is-ancestor {trunk} HEAD && echo yes > /tmp/from_trunk.txt "
                                   "|| echo no > /tmp/from_trunk.txt\n")
    result = box.run("agent.yml", "run", through(steps, "Starting branch") + [look], name="planner", role="planner")
    seen = f"{box.tmp}/from_trunk.txt"
    saw = open(seen).read().strip() if os.path.exists(seen) else None
    assert saw is not None, f"795.7: the planner's run never reached the planner; job {result}\n{box.tail()}"
    assert saw == "yes", ("795.7: a planner with no branch yet did not start from trunk, the default branch the "
                          "settings name")


def test_a_manual_fix_opens_against_the_default_branch_setting(record_property, tmp_path):
    """A manual fix's pull request goes to the default branch the settings name.

    Proves 795.7. The settings name trunk as the default branch. Runs fix.yml for the pushed branch fix/typo and
    checks it looked for an open pull request into trunk and opened one into trunk."""
    record_property("proves", "795.7")
    box = Box(tmp_path, TRUNK)
    box.commit("fix/typo", {"fixed.txt": "fixed\n"}, "Fix the typo", start="main")
    results = box.run_workflow("fix.yml")
    made = box.gh_calls("pr", "create")
    assert made, f"795.7: the manual fix opened no pull request: {results}\n{box.tail()}"
    base = made[-1][made[-1].index("--base") + 1] if "--base" in made[-1] else None
    assert base == "trunk", f"795.7: the manual fix's pull request goes to {base!r}, not trunk, the default branch setting"
    listed = box.gh_calls("pr", "list")
    bases = [c[c.index("--base") + 1] for c in listed if "--base" in c]
    assert bases and set(bases) == {"trunk"}, f"795.7: the manual fix looked for open pull requests into {bases}, not trunk"


# 795.8 ------------------------------------------------------------------------------------------------------------

def test_each_runs_conversation_is_saved_on_the_records_branch_the_settings_name(record_property, tmp_path):
    """A run's conversation is saved on the records branch the settings name.

    Proves 795.8. The settings name history as the records branch. Runs a planner's checkout, a stand-in agent that
    leaves a session log, and agent.yml's step that saves the conversation. Checks the origin's history branch holds
    logs/57/42-planner.md, no logs branch gained it, and the record's conversation link points to it on history."""
    record_property("proves", "795.8")
    box = Box(tmp_path, "records:\n  branch: history\n")
    _, steps = steps_of("agent.yml", "run")
    agent = stand_in("The agent", 'mkdir -p /home/runner/.claude/projects/p\n'
                                  'echo \'{"message": {"role": "assistant", "content": "Done."}}\' '
                                  '> /home/runner/.claude/projects/p/s.jsonl\n')
    save = step_named(steps, "Save the conversation")
    link = stand_in("The record's link", 'echo "$LOG_URL" > /tmp/log_url.txt\n')
    result = box.run("agent.yml", "run", through(steps, "Starting branch") + [link, agent, app_step(steps), save],
                     name="planner", role="planner", env={"STARTED": "true"})
    path = f"logs/{N}/42-planner.md"
    code, _ = box.origin("cat-file", "-e", f"history:{path}")
    assert code == 0, (f"795.8: the run's conversation is not on history, the records branch the settings name; "
                       f"job {result}\n{box.tail()}")
    code, _ = box.origin("cat-file", "-e", f"logs:{path}")
    assert code != 0, "795.8: the run's conversation was saved on logs, not only on the records branch the settings name"
    url = open(f"{box.tmp}/log_url.txt").read().strip() if os.path.exists(f"{box.tmp}/log_url.txt") else ""
    want = f"https://github.com/o/r/blob/history/{path}"
    assert url == want, f"795.8: the record's conversation link is {url!r}, not {want!r} on the records branch history"


# 795.9 ------------------------------------------------------------------------------------------------------------

def signal_from(tmp, settings, sender):
    """Run agent.yml's code-owner gate for a next-step signal sent by SENDER; the job's result."""
    box = Box(tmp, settings)
    _, steps = steps_of("agent.yml", "run")
    gate = step_named(steps, "Only a code owner starts an agent")
    return box.run("agent.yml", "run", steps[:steps.index(gate) + 1], role="planner", event="repository_dispatch", actor=sender)


def test_only_the_bot_named_in_settings_may_send_the_next_step_signal(record_property, tmp_path):
    """The next-step signal starts an agent only when the bot the settings name sent it.

    Proves 795.9. The settings name other-bot as the bot. Runs agent.yml's steps up to its code-owner gate for a
    dokima-next signal: sent by other-bot[bot] it passes; sent by dokima-runtime[bot] it is refused. With no settings
    file, dokima-runtime[bot]'s signal still passes."""
    record_property("proves", "795.9")
    named = f"bot:\n  slug: {OTHER_BOT}\n"
    got = signal_from(tmp_path / "named", named, f"{OTHER_BOT}[bot]")
    assert got == "success", f"795.9: the next-step signal from {OTHER_BOT}[bot], the bot the settings name, was refused"
    got = signal_from(tmp_path / "other", named, "dokima-runtime[bot]")
    assert got == "failure", "795.9: a next-step signal from dokima-runtime[bot] passed though the settings name another bot"
    got = signal_from(tmp_path / "default", None, "dokima-runtime[bot]")
    assert got == "success", "795.9: with no settings file, the signal from dokima-runtime[bot] was refused"


# 795.10 -----------------------------------------------------------------------------------------------------------

def test_merging_main_into_a_branch_carries_the_git_identity_of_the_bot_named_in_settings(record_property, tmp_path):
    """Merging main into a worker's or planner's branch commits as the named bot.

    Proves 795.10. The settings name other-bot as the bot. Main moved on since the branch split off. Runs the worker's
    checkout of agent.yml, then the planner's, each on its own repo, and checks each merge commit's author is
    other-bot[bot], with that bot's noreply address."""
    record_property("proves", "795.10")
    for role in ("worker", "planner"):
        box = Box(tmp_path / role, f"bot:\n  slug: {OTHER_BOT}\n", no_identity=True)
        box.commit(f"try/issue-{N}", {"app.py": "a = 1\n"}, "the work", start="main")
        box.commit("main", {"other.py": "o = 1\n"}, "main moves on")
        _, steps = steps_of("agent.yml", "run")
        result = box.run("agent.yml", "run", through(steps, "Starting branch"), name=role, role=role)
        ws = f"{box.tmp}/jobs/{role}/ws"
        assert result == "success", f"795.10: the {role}'s checkout failed\n{box.tail()}"
        parents = ts.sh(ws, "git", "log", "-1", "--format=%P").split()
        assert len(parents) == 2, f"795.10: the {role}'s checkout made no merge commit, so its identity cannot be checked"
        name, email = author_of(ws)
        assert name == f"{OTHER_BOT}[bot]", f"795.10: the {role}'s merge of main is authored by {name!r}, not {OTHER_BOT}[bot]"
        assert email.endswith(f"+{OTHER_BOT}[bot]@users." + "noreply.github.com"), \
            f"795.10: the {role}'s merge of main carries the address {email!r}, not {OTHER_BOT}[bot]'s"


def test_the_wiki_sync_commits_as_the_bot_named_in_settings(record_property, tmp_path):
    """The wiki sync commits as the bot the settings name.

    Proves 795.10. The settings name other-bot as the bot, and main holds docs/wiki/Home.md. Runs wiki.yml against a
    local wiki repo and checks the commit it pushed is authored by other-bot[bot], with that bot's noreply address."""
    record_property("proves", "795.10")
    box = Box(tmp_path, f"bot:\n  slug: {OTHER_BOT}\n", files={"docs/wiki/Home.md": "# Home\n"},
              no_identity=True)
    ts.sh(box.tmp, "git", "init", "-q", "--bare", "-b", "master", f"{box.tmp}/wiki.git")
    seed = f"{box.tmp}/wiki-seed"
    ts.sh(box.tmp, "git", "init", "-q", "-b", "master", seed)
    open(f"{seed}/Old.md", "w").write("old\n")
    ts.sh(seed, "git", "add", "-A")
    ts.sh(seed, "git", "commit", "-qm", "old")
    ts.sh(seed, "git", "push", "-q", f"{box.tmp}/wiki.git", "master")
    results = box.run_workflow("wiki.yml", event="push")
    out = subprocess.run(["git", "--git-dir", f"{box.tmp}/wiki.git", "log", "-1", "--format=%an|%ae|%s", "master"],
                         capture_output=True, text=True).stdout.strip().split("|")
    assert len(out) == 3 and out[2] != "old", f"795.10: the wiki sync pushed nothing: {results}\n{box.tail()}"
    name, email = out[0], out[1]
    assert name == f"{OTHER_BOT}[bot]", f"795.10: the wiki sync commits as {name!r}, not {OTHER_BOT}[bot]"
    assert email.endswith(f"+{OTHER_BOT}[bot]@users." + "noreply.github.com"), \
        f"795.10: the wiki sync commits with the address {email!r}, not {OTHER_BOT}[bot]'s"

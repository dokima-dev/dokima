"""The planner starts with main merged in, so it can change tests main added (#475).

When a pull request clashes with main, its planner used to start on the old branch without main: a test main added
was not there to change, and only the worker's later merge showed the plan broken, costing an extra round.

These tests run the real steps of .github/workflows/agent.yml on the machine from test_start.py: a temp origin where
main adds tests/test_main.py after try/issue-57 split off. The planner's run is its checkout ("Starting branch"), a
stand-in for the agent that copies what it found and changes tests/test_main.py when it is there, and the push. Then
the worker's own "Starting branch" step runs on a fresh clone, as the next run would.

With clash=True, main and the branch both change app.py, so the branch clashes with main; with clash=False the
branch changes only near.py and merges cleanly. With rounds=2 the planner runs twice, as a re-plan does; with
change=False it only looks and leaves main's test as main has it.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_start as ts  # noqa: E402

MAINS_TEST = 'def test_m():\n    """Main\'s own test."""\n    assert True\n'
BRANCHS_TEST = 'def test_a():\n    """A."""\n'
PLANNERS_TEST = 'def test_m():\n    """Main\'s test, changed by the planner."""\n    assert 1 + 1 == 2\n'


class Branch(ts.Machine):
    """A planner run on #57 from checkout to push, then the worker's checkout.

    Main has moved on since the branch split off: it changed app.py and added tests/test_main.py."""

    def __init__(self, tmp, clash=True, rounds=1, change=True):
        super().__init__(tmp, [])
        t, src = self.tmp, f"{self.tmp}/src"

        def commit(files, message):
            for path, text in files.items():
                os.makedirs(os.path.dirname(f"{src}/{path}") or src, exist_ok=True)
                open(f"{src}/{path}", "w").write(text)
            ts.sh(src, "git", "add", "-A")
            ts.sh(src, "git", "commit", "-qm", message)
        commit({"app.py": "a = 1\n", "near.py": "n = 1\n"}, "base")
        ts.sh(src, "git", "push", "-q", "origin", "main")
        ts.sh(src, "git", "checkout", "-q", "-b", f"try/issue-{ts.N}")
        mine = {"app.py": "a = 2\n"} if clash else {"near.py": "n = 2\n"}
        commit({**mine, "tests/test_x.py": BRANCHS_TEST}, "the branch's work")
        ts.sh(src, "git", "push", "-q", "origin", f"try/issue-{ts.N}")
        ts.sh(src, "git", "checkout", "-q", "main")
        commit({"app.py": "a = 3\n", "tests/test_main.py": MAINS_TEST}, "main adds a test")
        ts.sh(src, "git", "push", "-q", "origin", "main")
        open(f"{t}/planners_test.py", "w").write(PLANNERS_TEST)
        # The stand-in planner: keeps what it found and the tests its plan check counts as the plan's own, then
        # changes main's test when it can see it.
        edits = ("mkdir -p \"$PACK\" \"$OUT\"\n"
                 "rm -f /tmp/seen.py /tmp/seen_x.py\n"
                 "git diff --name-only \"$PLANNER_BASE\" -- tests > /tmp/plans_tests.txt\n"
                 "if [ -f tests/test_x.py ]; then cp tests/test_x.py /tmp/seen_x.py; fi\n"
                 "if [ -f tests/test_main.py ]; then cp tests/test_main.py /tmp/seen.py; "
                 + ("cp /tmp/planners_test.py tests/test_main.py; " if change else "") + "fi\n")
        wf = ts.workflow("agent.yml")
        job = wf["jobs"]["run"]
        named = {s.get("name"): s for s in job["steps"]}
        app = next(s for s in job["steps"] if s.get("id") == "app")
        push = next(s for s in job["steps"] if str(s.get("name", "")).startswith("Push the planner's tests"))
        start = named["Starting branch"]
        planner = [named["Copy the runtime from main before touching any branch"], start,
                   {"name": "The planner changes main's test", "run": edits}, app, push]
        for k in range(rounds):
            self.planner = self.run_as("planner", wf, job, planner, f"planner{k + 1}")
            self.planner_log = "\n".join(self.log)
            if self.planner != "success":
                break
        if os.path.exists(f"{t}/clashed.txt"):
            os.remove(f"{t}/clashed.txt")
        self.failed_step = None
        self.worker = self.run_as("worker", wf, job, [named["Copy the runtime from main before touching any branch"], start])

    def run_as(self, role, wf, job, steps, name=None):
        """Run the given steps of agent.yml for `role` on a fresh clone; the job's result."""
        t = self.tmp
        open(f"{t}/event.json", "w").write('{"inputs": {"role": "%s", "stage": "", "issue": "%s"}}' % (role, ts.N))
        ctx = {"inputs": ts.Ctx(role=role, stage="", issue=ts.N),
               "github": ts.Ctx(event_name="workflow_dispatch", actor=ts.OWNER, event=ts.Ctx(), run_id="42", run_attempt="1",
                                server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": ts.Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": ts.Ctx(DOKIMA_APP_ID="1"), "needs": ts.Ctx()}
        job = {**job, "env": {**(job.get("env") or {}), "PASSED": "true", "STARTED": "true"}, "steps": steps}
        result, _ = self.run_job(name or role, job, ctx, "workflow_dispatch",
                                 [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        return result

    def seen(self):
        """Main's test as the planner found it, or None when it was not there."""
        path = f"{self.tmp}/seen.py"
        return open(path).read() if os.path.exists(path) else None

    def seen_branchs(self):
        """The branch's own test as the planner found it, or None when absent."""
        path = f"{self.tmp}/seen_x.py"
        return open(path).read() if os.path.exists(path) else None

    def plans_tests(self):
        """The tests the plan check counted as the plan's own when the newest round started."""
        path = f"{self.tmp}/plans_tests.txt"
        return open(path).read().split() if os.path.exists(path) else []

    def on_origin(self, *args):
        """Run git in the temp origin; its exit code."""
        return subprocess.run(["git", *args], cwd=f"{self.tmp}/origin.git", capture_output=True).returncode

    def workers(self, path):
        """A file's text in the worker's copy after its checkout, or None when absent."""
        p = f"{self.tmp}/jobs/worker/ws/{path}"
        return open(p).read() if os.path.exists(p) else None

    def clashed(self):
        """The files the worker's checkout listed as clashed with main, for it to resolve."""
        path = f"{self.tmp}/clashed.txt"
        return open(path).read().split() if os.path.exists(path) else []


def test_the_planner_on_a_branch_that_clashes_with_main_sees_the_tests_main_added(record_property, tmp_path):
    """On a branch that clashes with main, the planner finds the test main added.

    Proves 475.1.
    Runs the planner's real checkout on try/issue-57, which clashes with main in app.py, while main has since added
    tests/test_main.py. The planner's copy must hold that test exactly as main has it, and still hold the branch's own
    tests/test_x.py, so starting from main alone does not pass. Beside it, a branch that merges cleanly with main must
    give the planner both tests too.
    Then each branch gets a second planning round after a first that left main's test alone, as a re-plan does. The
    planner must still find both tests, and its plan check must count the branch's test as the plan's own but never
    main's test, which it would reject as a new test that already passes."""
    record_property("proves", "475.1")
    for rounds in (1, 2):
        for clash in (True, False):
            b = Branch(tmp_path / f"{'clash' if clash else 'clean'}{rounds}", clash=clash, rounds=rounds, change=False)
            kind = ("clashes with main" if clash else "merges cleanly with main") + \
                (", in its second planning round" if rounds == 2 else "")
            assert b.planner == "success", f"475.1: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
            assert b.seen() == MAINS_TEST, \
                (f"475.1: on a branch that {kind}, the planner started without the test main added "
                 f"(tests/test_main.py found: {b.seen()!r})")
            assert b.seen_branchs() == BRANCHS_TEST, \
                (f"475.1: on a branch that {kind}, the planner started without the branch's own test "
                 f"(tests/test_x.py found: {b.seen_branchs()!r})")
            assert "tests/test_main.py" not in b.plans_tests(), \
                (f"475.1: on a branch that {kind}, the plan check counts the test main added as the plan's own "
                 f"(plan's tests: {b.plans_tests()})")
            assert "tests/test_x.py" in b.plans_tests(), \
                (f"475.1: on a branch that {kind}, the plan check lost the branch's own test "
                 f"(plan's tests: {b.plans_tests()})")


def test_the_planners_change_to_a_test_main_added_reaches_the_worker(record_property, tmp_path):
    """The planner's change to a test main added is what the worker starts with.

    Proves 475.2.
    After the planner changes tests/test_main.py, the worker's real checkout runs on a fresh clone and merges main, as
    it does. Its copy must hold the planner's version of that test, not main's, with no extra planning round. On the
    clashing branch, app.py must still be listed for the worker to resolve, so main's change to it is not lost. Beside
    it, a branch that merges cleanly must hand the planner's change to the worker too."""
    record_property("proves", "475.2")
    for clash in (True, False):
        b = Branch(tmp_path / ("clash" if clash else "clean"), clash=clash)
        kind = "clashes with main" if clash else "merges cleanly with main"
        assert b.planner == "success", f"475.2: the planner on a branch that {kind} failed:\n{b.planner_log[-3000:]}"
        assert b.worker == "success", f"475.2: the worker's checkout after the planner failed:\n{b.tail()}"
        got = b.workers("tests/test_main.py")
        assert got == PLANNERS_TEST, \
            (f"475.2: on a branch that {kind}, the worker started without the planner's change to the test main "
             f"added; tests/test_main.py is {got!r}")
        assert "tests/test_main.py" not in b.clashed(), \
            f"475.2: on a branch that {kind}, the planner's change to the test main added clashed with main"
        if clash:
            assert "app.py" in b.clashed(), \
                f"475.2: app.py clashes with main but was not left for the worker to resolve: {b.clashed()}"


def test_a_planner_run_brings_its_branch_up_to_mains_newest_commit(record_property, tmp_path):
    """A planner run on a cleanly merging branch brings it up to main's newest commit.

    Proves 475.3.
    Runs the planner's real checkout and push on try/issue-57, which merges cleanly with main, while main has moved on
    since the branch split off. The branch the planner pushed must then hold main's newest commit, so a later move of
    main cannot clash with the planner's test changes. It must still hold the branch's own work too. Beside it, a
    branch that clashes with main must still finish the planner's run and keep its own work, for the worker to merge."""
    record_property("proves", "475.3")
    b = Branch(tmp_path / "clean", clash=False)
    assert b.planner == "success", f"475.3: the planner on a branch that merges cleanly failed:\n{b.planner_log[-3000:]}"
    branch = f"refs/heads/try/issue-{ts.N}"
    assert b.on_origin("merge-base", "--is-ancestor", "refs/heads/main", branch) == 0, \
        "475.3: after the planner's run on a branch that merges cleanly, its branch still lacks main's newest commit"
    assert b.on_origin("cat-file", "-e", f"{branch}:tests/test_x.py") == 0, \
        "475.3: after the planner's run, its branch lost its own tests/test_x.py"
    c = Branch(tmp_path / "clash", clash=True)
    assert c.planner == "success", f"475.3: the planner on a branch that clashes with main failed:\n{c.planner_log[-3000:]}"
    assert c.on_origin("cat-file", "-e", f"{branch}:tests/test_x.py") == 0, \
        "475.3: after the planner's run on a branch that clashes with main, its branch lost its own tests/test_x.py"

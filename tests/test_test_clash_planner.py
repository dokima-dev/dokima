"""A clash inside a test file goes to the planner, not the worker (#662).

The worker may not change tests: the fence puts every test file back as the planner committed it. So when a pull
request clashed with main inside a test file, the worker's resolution was dropped, its hand-back failed with "Conflict
markers are still in ...", and the issue stalled until someone resolved the clash by hand (#610 on 2026-10-14).

These tests run the real steps of .github/workflows/agent.yml on the machine from test_start.py: a temp origin where
main and try/issue-57 both changed tests/test_x.py after the branch split off, and, as on #610, also rules.md, a file
that is not a test. First the planner's run: its checkout ("Starting branch"), a stand-in planner that keeps what it
found and resolves tests/test_x.py when it holds conflict markers, and the push. Then the worker's run on a fresh
clone: its checkout, a stand-in worker that resolves rules.md when it holds markers and touches no test, the fence and
the push.

With tests=False the branch clashes with main only in rules.md, so no test file clashes.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import test_start as ts  # noqa: E402

MARKERS = re.compile(r"(?m)^(<<<<<<<|=======|>>>>>>>)( |$)")
BASE_TEST = 'def test_a():\n    """A."""\n    assert 1\n'
BRANCHS_TEST = 'def test_a():\n    """A, as the branch has it."""\n    assert "branch"\n'
MAINS_TEST = 'def test_a():\n    """A, as main has it."""\n    assert "main"\n'
RESOLVED_TEST = 'def test_a():\n    """A, resolved by the planner."""\n    assert "branch" and "main"\n'
RESOLVED_RULES = "rules, resolved by the worker\n"


class TestClash(ts.Machine):
    """A planner run on #57, then a worker run, each from checkout to push.

    Main and try/issue-57 both changed rules.md, and, with tests=True, both changed tests/test_x.py too."""

    def __init__(self, tmp, tests=True):
        super().__init__(tmp, [])
        t, src = self.tmp, f"{self.tmp}/src"

        def commit(files, message):
            for path, text in files.items():
                os.makedirs(os.path.dirname(f"{src}/{path}") or src, exist_ok=True)
                open(f"{src}/{path}", "w").write(text)
            ts.sh(src, "git", "add", "-A")
            ts.sh(src, "git", "commit", "-qm", message)
        commit({"rules.md": "rules\n", "tests/test_x.py": BASE_TEST}, "base")
        ts.sh(src, "git", "push", "-q", "origin", "main")
        ts.sh(src, "git", "checkout", "-q", "-b", f"try/issue-{ts.N}")
        commit({"rules.md": "rules, the branch's\n", **({"tests/test_x.py": BRANCHS_TEST} if tests else {})},
               "the branch's work")
        ts.sh(src, "git", "push", "-q", "origin", f"try/issue-{ts.N}")
        ts.sh(src, "git", "checkout", "-q", "main")
        commit({"rules.md": "rules, main's\n", **({"tests/test_x.py": MAINS_TEST} if tests else {})}, "main moves on")
        ts.sh(src, "git", "push", "-q", "origin", "main")
        self.main_sha = ts.sh(src, "git", "rev-parse", "HEAD")
        open(f"{t}/resolved_test.py", "w").write(RESOLVED_TEST)
        # The stand-in planner: keeps the test file it found, and resolves it when it holds conflict markers.
        planner_edits = ("mkdir -p \"$PACK\" \"$OUT\"\n"
                         "cp tests/test_x.py /tmp/planner_saw.py\n"
                         "if grep -qE '^(<<<<<<<|>>>>>>>)( |$)' tests/test_x.py; then "
                         "cp /tmp/resolved_test.py tests/test_x.py; fi\n")
        plan = json.dumps({"kind": "user_story", "scope": ["rules.md"]})
        # The stand-in worker: resolves rules.md when it holds conflict markers; it touches no test.
        worker_edits = (f"mkdir -p \"$PACK\" \"$OUT\" && echo '{plan}' > \"$PACK/plan.json\"\n"
                        "cp tests/test_x.py /tmp/worker_saw.py\n"
                        "if grep -qE '^(<<<<<<<|>>>>>>>)( |$)' rules.md; then "
                        f"printf '{RESOLVED_RULES.strip()}\\n' > rules.md; fi\n")
        wf = ts.workflow("agent.yml")
        job = wf["jobs"]["run"]
        steps = job["steps"]
        named = {s.get("name"): s for s in steps}
        # Dokima's code comes from the checkout of Dokima's own repo, played before the copy step (#812).
        dokima, copy, start = (named["Dokima's code from Dokima's own repo"],
                               named["Copy the runtime from main before touching any branch"], named["Starting branch"])
        key = next(s for s in steps if s.get("id") == "start-key")
        app = next(i for i, s in enumerate(steps) if s.get("id") == "app")
        end = next(i for i, s in enumerate(steps) if str(s.get("name", "")).startswith("Save the conversation"))
        push = next(s for s in steps if str(s.get("name", "")).startswith("Push the planner's tests"))
        fence = next(s for s in steps if str(s.get("name", "")).startswith("Fence"))
        self.planner = self.run_as("planner", wf, job, [dokima, copy, key, start, {"name": "The planner", "run": planner_edits},
                                                         steps[app], push])
        self.planner_log = "\n".join(self.log)
        for f in ("clashed.txt", "worker_saw.py"):
            if os.path.exists(f"{t}/{f}"):
                os.remove(f"{t}/{f}")
        self.failed_step = None
        self.worker = self.run_as("worker", wf, job, [dokima, copy, key, start, {"name": "The worker", "run": worker_edits},
                                                       fence] + steps[app:end])

    def run_as(self, role, wf, job, steps):
        """Run the given steps of agent.yml for `role` on a fresh clone; the job's result."""
        t = self.tmp
        open(f"{t}/event.json", "w").write('{"inputs": {"role": "%s", "stage": "", "issue": "%s"}}' % (role, ts.N))
        ctx = {"inputs": ts.Ctx(role=role, stage="", issue=ts.N),
               "github": ts.Ctx(event_name="workflow_dispatch", actor=ts.OWNER, event=ts.Ctx(), run_id="42", run_attempt="1",
                                server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": ts.Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": ts.Ctx(DOKIMA_APP_ID="1"), "needs": ts.Ctx()}
        job = {**job, "env": {**(job.get("env") or {}), "PASSED": "true", "STARTED": "true"}, "steps": steps}
        result, _ = self.run_job(role, job, ctx, "workflow_dispatch",
                                 [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        return result

    def saw(self, who):
        """tests/test_x.py as the planner or worker found it, or None if never reached."""
        path = f"{self.tmp}/{who}_saw.py"
        return open(path).read() if os.path.exists(path) else None

    def clashed(self):
        """The files the worker's checkout listed as clashed with main, for it to resolve."""
        path = f"{self.tmp}/clashed.txt"
        return open(path).read().split() if os.path.exists(path) else []

    def pushed(self, path):
        """A file's text on the pushed try/issue-57, or None when absent."""
        p = subprocess.run(["git", "--git-dir", f"{self.tmp}/origin.git", "show", f"try/issue-{ts.N}:{path}"],
                           capture_output=True, text=True)
        return p.stdout if p.returncode == 0 else None

    def pushed_files(self):
        """Every file on try/issue-57 in the origin after both runs."""
        return ts.sh(self.tmp, "git", "--git-dir", f"{self.tmp}/origin.git", "ls-tree", "-r", "--name-only",
                     f"try/issue-{ts.N}").split()

    def has_main(self):
        """True when main's newest commit is part of the pushed try/issue-57."""
        return subprocess.run(["git", "--git-dir", f"{self.tmp}/origin.git", "merge-base", "--is-ancestor", self.main_sha,
                               f"try/issue-{ts.N}"]).returncode == 0


def test_the_planner_is_handed_a_clash_inside_a_test_file(record_property, tmp_path):
    """The planner's run is handed a clash inside a test file, to resolve.

    Proves 662.1.
    Runs the planner's real checkout on try/issue-57, which clashes with main in tests/test_x.py and in rules.md, as
    #610 did. The test file the planner finds must hold the clash: conflict markers with both main's side and the
    branch's side. Today the planner starts from the branch's own version and never sees the clash. Beside it, a
    branch that clashes only in rules.md must hand the planner its test file with no conflict markers."""
    record_property("proves", "662.1")
    m = TestClash(tmp_path / "test")
    assert m.planner == "success", f"662.1: the planner on a branch that clashes in a test file failed:\n{m.planner_log[-3000:]}"
    saw = m.saw("planner") or ""
    assert MARKERS.search(saw) and '"main"' in saw and '"branch"' in saw, \
        ("662.1: the planner was not handed the clash in tests/test_x.py; it found no conflict markers holding both "
         f"main's and the branch's side, but:\n{saw}")
    c = TestClash(tmp_path / "rules-only", tests=False)
    assert c.planner == "success", f"662.1: the planner on a branch that clashes only in rules.md failed:\n{c.planner_log[-3000:]}"
    assert not MARKERS.search(c.saw("planner") or ""), \
        f"662.1: a test file that did not clash reached the planner with conflict markers:\n{c.saw('planner')}"


def test_the_worker_is_not_handed_a_clash_inside_a_test_file(record_property, tmp_path):
    """The worker is no longer handed a clash inside a test file.

    Proves 662.2.
    After the planner resolved tests/test_x.py, the worker's real checkout runs on a fresh clone and merges main, as it
    does. Its list of clashed files must not name tests/test_x.py, and its copy of that test must be the planner's
    resolution, with no conflict markers. Today the worker's merge clashes in that test file and lists it. rules.md,
    which is not a test, must still be listed for the worker to resolve, so a clash outside tests still goes to it."""
    record_property("proves", "662.2")
    m = TestClash(tmp_path)
    assert m.planner == "success", f"662.2: the planner's run failed:\n{m.planner_log[-3000:]}"
    assert m.saw("worker") is not None, f"662.2: the worker's checkout failed at {m.failed_step!r}:\n{m.tail()}"
    assert "tests/test_x.py" not in m.clashed(), \
        f"662.2: the worker was handed the clash inside tests/test_x.py: its clashed files are {m.clashed()}"
    assert m.saw("worker") == RESOLVED_TEST, \
        f"662.2: the worker did not start from the planner's resolution of tests/test_x.py, but from:\n{m.saw('worker')}"
    assert "rules.md" in m.clashed(), \
        f"662.2: the clash in rules.md, which is not a test, was not left for the worker: {m.clashed()}"


def test_a_clash_inside_a_test_file_no_longer_stalls_the_workers_run(record_property, tmp_path):
    """A clash inside a test file no longer fails the worker's hand-back.

    Proves 662.3.
    Runs the planner, then the worker's whole run as on #610: checkout, its edits, the fence and the push. The worker's
    run must succeed, the fence must drop no test file, and the pushed branch must hold main's newest commit, the
    planner's resolution of tests/test_x.py, the worker's resolution of rules.md, and no conflict marker anywhere.
    Today the fence fails with "Conflict markers are still in tests/test_x.py" and nothing is pushed."""
    record_property("proves", "662.3")
    m = TestClash(tmp_path)
    assert m.planner == "success", f"662.3: the planner's run failed:\n{m.planner_log[-3000:]}"
    assert m.worker == "success", f"662.3: the worker's run failed at {m.failed_step!r}:\n{m.tail()}"
    out = m.env.get("OUT", "")
    check = open(os.path.join(out, "check.txt")).read() if out and os.path.exists(os.path.join(out, "check.txt")) else ""
    assert "Conflict markers" not in check, f"662.3: the worker's hand-back was rejected on conflict markers:\n{check}"
    dropped = open(os.path.join(out, "dropped.txt")).read().split() if out and os.path.exists(os.path.join(out, "dropped.txt")) else []
    assert "tests/test_x.py" not in dropped, f"662.3: the fence dropped tests/test_x.py: {dropped}"
    assert m.has_main(), "662.3: the worker's pushed branch does not hold main's newest commit"
    marked = [f for f in m.pushed_files() if MARKERS.search(m.pushed(f) or "")]
    assert not marked, f"662.3: the pushed branch still holds conflict markers in {marked}"
    assert m.pushed("tests/test_x.py") == RESOLVED_TEST, \
        f"662.3: the pushed tests/test_x.py is not the planner's resolution:\n{m.pushed('tests/test_x.py')}"
    assert m.pushed("rules.md") == RESOLVED_RULES, f"662.3: the pushed rules.md is not the worker's resolution: {m.pushed('rules.md')!r}"

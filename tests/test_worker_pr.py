"""A finished worker always ends with its pull request open, even when it has nothing new to push (#257).

On #244 the planner had already pushed the whole fix, the worker had nothing new, the push step quit early and the
pull request was never opened. These tests run the real steps of .github/workflows/agent.yml that take a finished
run's work to GitHub, with the machine from test_start.py (a temp repo whose origin is a local bare repo, a fake
`gh` that records every call): copying the runtime, checking out try/issue-57, minting the app's key, then every step
from that key up to saving the conversation. The hand-back is taken as passed (PASSED=true), the way the run sets it
once the code's check accepts it. A pull request is opened when the fake `gh` is asked `gh pr create` for the head
try/issue-57; options.json's pr_open makes #60 already open for it.
"""

import test_start as ts
from test_start import N, OWNER, Ctx


def push_steps(change=None):
    """The steps of agent.yml that take a finished run's work to GitHub, with a step making `change` (a shell line)
    in the worker's checkout right after the branch is checked out, as the agent would."""
    wf = ts.workflow("agent.yml")
    job = wf["jobs"]["run"]
    steps = job["steps"]
    named = {s.get("name"): s for s in steps}
    app = next(i for i, s in enumerate(steps) if s.get("id") == "app")
    end = next(i for i, s in enumerate(steps) if s.get("name") == "Write this run's record")
    picked = [named["Copy the runtime from main before touching any branch"], named["Starting branch"]]
    if change:
        picked.append({"name": "The agent changes the code", "run": change})
    return wf, job, picked + steps[app:end]


class Finish(ts.Machine):
    """A run of `role` on issue #57 whose hand-back passed, from the moment it is checked out until its work is on
    GitHub; try/issue-57 already holds the planner's tests."""

    def __init__(self, tmp, role, change=None, pr_open=False):
        super().__init__(tmp, [], try_branch=True, options={"pr_open": pr_open})
        t = self.tmp
        open(f"{t}/event.json", "w").write('{"inputs": {"role": "%s", "stage": "", "issue": "%s"}}' % (role, N))
        ctx = {"inputs": Ctx(role=role, stage="", issue=N),
               "github": Ctx(event_name="workflow_dispatch", actor=OWNER, event=Ctx(), run_id="42", run_attempt="1",
                             server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}
        wf, job, steps = push_steps(change)
        job = {**job, "env": {**(job.get("env") or {}), "PASSED": "true", "STARTED": "true"}, "steps": steps}
        self.result, _ = self.run_job("run", job, ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))

    def opened(self):
        """Every `gh pr create` call, as argument lists."""
        return [c for c in self.calls() if c[:2] == ["pr", "create"]]

    def branch_files(self):
        """The files on try/issue-57 in the origin, after the run."""
        out = ts.sh(self.tmp, "git", "--git-dir", f"{self.tmp}/origin.git", "ls-tree", "-r", "--name-only", f"try/issue-{N}")
        return out.split()


def flag(call, name):
    """The value given to `name` in a gh call, or None."""
    return call[call.index(name) + 1] if name in call and call.index(name) + 1 < len(call) else None


def assert_opened_once(m, crit, case):
    """The run succeeded and asked GitHub for exactly one pull request from try/issue-57 into main."""
    assert m.result == "success", f"{crit}: {case}: the run failed at {m.failed_step!r}:\n{m.tail()}"
    opened = m.opened()
    assert len(opened) == 1, f"{crit}: {case}: expected exactly one pull request opened, got {len(opened)}: {opened}\n{m.tail()}"
    head, base = flag(opened[0], "--head") or flag(opened[0], "-H"), flag(opened[0], "--base") or flag(opened[0], "-B")
    assert head == f"try/issue-{N}", f"{crit}: {case}: the pull request was not opened from try/issue-{N}: {opened[0]}"
    assert base == "main", f"{crit}: {case}: the pull request was not opened into main: {opened[0]}"


def test_a_worker_with_nothing_new_to_push_still_opens_its_pull_request(record_property, tmp_path):
    """A worker with nothing new to push still ends with an open pull request for the issue.

    The planner's branch already holds everything and the worker changes nothing, as on #244. The real push steps of
    the agent workflow run, and the test checks the run succeeded and asked GitHub to open one pull request from
    try/issue-57 into main. Every story of a split is an issue built the same way, so this also pins that each story
    merges to main on its own pull request, with no parent branch (668.4)."""
    record_property("proves", "257.1")
    record_property("proves", "257.2")
    record_property("proves", "668.4")
    m = Finish(tmp_path, "worker")
    assert_opened_once(m, "257.1", "the worker had nothing new to push")


def test_only_a_finished_worker_opens_a_pull_request_and_only_when_none_is_open(record_property, tmp_path):
    """Only a finished worker opens a pull request, once, whether or not it pushed anything.

    Six runs of the agent workflow's real push steps: a worker with nothing new and a worker with new code, with no
    pull request open (each must open exactly one from try/issue-57 into main, and the new code must reach the branch);
    the same two with #60 already open (neither may open another); and a planner with nothing new and with a new test
    (neither may open one). Every case is run and every one that goes wrong is named."""
    record_property("proves", "257.1")
    fix, new_test = "echo 'x = 1' > fix.py", "printf 'def test_b():\\n    pass\\n' > tests/test_y.py"
    wrong = []
    for case, role, change, pr_open, want in (
            ("a worker with nothing new to push", "worker", None, False, 1),
            ("a worker that pushed new code", "worker", fix, False, 1),
            ("a worker with nothing new while #60 is open", "worker", None, True, 0),
            ("a worker that pushed new code while #60 is open", "worker", fix, True, 0),
            ("a planner with nothing new to push", "planner", None, False, 0),
            ("a planner that pushed a new test", "planner", new_test, False, 0)):
        m = Finish(tmp_path / case.replace(" ", "-").replace("#", ""), role, change=change, pr_open=pr_open)
        if m.result != "success":
            wrong.append(f"{case}: the run failed at {m.failed_step!r}:\n{m.tail()}")
            continue
        opened = m.opened()
        if len(opened) != want:
            wrong.append(f"{case}: expected {want} pull request(s) opened, got {len(opened)}: {opened}")
        elif want and ((flag(opened[0], "--head") or flag(opened[0], "-H")) != f"try/issue-{N}"
                       or (flag(opened[0], "--base") or flag(opened[0], "-B")) != "main"):
            wrong.append(f"{case}: the pull request was not opened from try/issue-{N} into main: {opened[0]}")
        if change == fix and "fix.py" not in m.branch_files():
            wrong.append(f"{case}: the worker's new code never reached try/issue-{N}: {m.branch_files()}")
    assert not wrong, "257.1: " + "\n257.1: ".join(wrong)

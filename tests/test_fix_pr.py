"""An agent's manual fix opens as Dokima's app, and all tests gate it (#589).

Story 3 of #580.

Hand-made fixes were opened with the owner's own token, so the owner was the author and could not approve them. Only
Actions hold the app's key, so a workflow opens them: `.github/workflows/fix.yml`, started by hand on main with the
name of the branch the agent pushed (input `branch`), mints the app's token and opens the pull request from that
branch into main with `gh pr create`. These tests run that workflow's own steps on the machine from test_start.py: a
temp repo whose origin is a local bare repo holding the pushed branch, and a fake `gh` that records every call and the
token it was made with. The app-token step gives `fake-token`; the workflow's own token is `fake-github-token`.
"""
import json
import os

import test_start as ts
from test_start import OWNER, Ctx

BRANCH = "fix/typo"
APP_TOKEN = "fake-token"
WORKFLOW = os.path.join(ts.ROOT, ".github", "workflows", "fix.yml")


def need_workflow(criterion):
    """Fail naming the criterion when no workflow opens a manual fix yet."""
    assert os.path.exists(WORKFLOW), (f"{criterion}: no workflow opens an agent's manual fix as Dokima's app "
                                      f"(.github/workflows/fix.yml is missing)")


class Fix(ts.Machine):
    """A run of fix.yml on main for the branch an agent pushed.

    The branch is `fix/typo`, with one commit on it."""

    def __init__(self, tmp, pr_open=False, gh_fail="", issue="7"):
        super().__init__(tmp, [], gh_fail=gh_fail, options={"pr_open": pr_open})
        t = self.tmp
        src = f"{t}/src"
        ts.sh(src, "git", "checkout", "-q", "-b", BRANCH)
        open(f"{src}/fixed.txt", "w").write("fixed\n")
        ts.sh(src, "git", "add", "-A")
        ts.sh(src, "git", "commit", "-qm", "Fix the typo")
        ts.sh(src, "git", "push", "-q", "origin", BRANCH)
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"branch": BRANCH, "issue": issue}}))
        ctx = {"inputs": Ctx(branch=BRANCH, issue=issue),
               "github": Ctx(event_name="workflow_dispatch", actor=OWNER, event=Ctx(inputs=Ctx(branch=BRANCH, issue=issue)),
                             ref="refs/heads/main", ref_name="main", run_id="42", run_attempt="1",
                             server_url="https://github.com", repository="o/r", repository_owner="o",
                             token="fake-github-token"),
               "secrets": Ctx(DOKIMA_APP_KEY="k"), "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}
        wf = ts.workflow("fix.yml")
        self.results = {}
        for name, job in (wf.get("jobs") or {}).items():
            self.results[name], _ = self.run_job(name, job, ctx, "workflow_dispatch",
                                                 [("/tmp/", f"{t}/")], wf.get("defaults"))

    def opened(self):
        """Every `gh pr create` call, each as {args, token}."""
        path = f"{self.tmp}/gh/calls-meta.jsonl"
        metas = [json.loads(l) for l in open(path)] if os.path.exists(path) else []
        return [m for m in metas if m["args"][:2] == ["pr", "create"]]

    def failed(self):
        """True when any job of the run failed."""
        return any(r != "success" for r in self.results.values())


def flag(args, name):
    """The value given to `name` in a gh call, or None."""
    return args[args.index(name) + 1] if name in args else None


def test_a_manual_fix_opens_as_dokimas_app(record_property, tmp_path):
    """A manual fix's pull request is opened with Dokima's app key, never the owner's.

    Proves 589.1.
    Runs the fix workflow for a pushed branch and checks it opened exactly one pull request from that branch, made
    with the token the app-token step minted."""
    record_property("proves", "589.1")
    need_workflow("589.1")
    run = Fix(tmp_path)
    assert not run.failed(), f"589.1: the fix workflow failed on a pushed branch\n{run.tail()}"
    opened = run.opened()
    assert len(opened) == 1, f"589.1: expected one pull request opened for {BRANCH}, got {len(opened)}\n{run.tail()}"
    assert flag(opened[0]["args"], "--head") == BRANCH, \
        f"589.1: the pull request is not opened from the pushed branch {BRANCH}: {opened[0]['args']}"
    assert opened[0]["token"] == APP_TOKEN, \
        f"589.1: the pull request was opened with {opened[0]['token']!r}, not Dokima's app token, so the app is not its author"


def test_a_second_run_for_the_same_branch_opens_no_second_pull_request(record_property, tmp_path):
    """Starting the fix again while its pull request is open opens no second one.

    Proves 589.1.
    Runs the fix workflow while GitHub already lists an open pull request for the branch, and checks no new one is
    asked for and the run passes."""
    record_property("proves", "589.1")
    need_workflow("589.1")
    run = Fix(tmp_path, pr_open=True)
    assert not run.opened(), f"589.1: a second pull request was opened for {BRANCH}: {run.opened()}"
    assert not run.failed(), f"589.1: the fix workflow failed when the branch's pull request was already open\n{run.tail()}"


def test_a_refused_pull_request_fails_the_run(record_property, tmp_path):
    """When GitHub refuses to open the pull request, the run fails.

    Proves 589.1.
    Makes the fake GitHub refuse `gh pr create` and checks the run ends failed."""
    record_property("proves", "589.1")
    need_workflow("589.1")
    run = Fix(tmp_path, gh_fail="pr create|HTTP 403: Resource not accessible by integration")
    assert run.failed(), "589.1: GitHub refused to open the fix's pull request, yet the run passed"


def test_a_manual_fix_cannot_merge_before_all_tests_pass(record_property, tmp_path):
    """A manual fix's pull request goes into main, which holds it until all tests pass.

    Proves 589.2.
    Runs the fix workflow and checks its pull request targets main and no merge or auto-merge is asked for; then
    checks main's branch rule requires the all tests check, and that check runs when a pull request opens or gets a commit."""
    record_property("proves", "589.2")
    need_workflow("589.2")
    run = Fix(tmp_path)
    opened = run.opened()
    assert opened, f"589.2: the fix workflow opened no pull request\n{run.tail()}"
    assert flag(opened[0]["args"], "--base") == "main", \
        f"589.2: the fix's pull request does not go into main, so main's required checks do not gate it: {opened[0]['args']}"
    merges = [c for c in run.calls() if c[:2] == ["pr", "merge"] or any("/merge" in x or "AutoMerge" in x for x in c)]
    assert not merges, f"589.2: the fix workflow asks GitHub to merge before all tests pass: {merges}"
    from dokima import manifest
    assert "all tests" in manifest.BRANCH_RULES["main"]["required_checks"], \
        "589.2: main's branch rule no longer requires all tests"
    suite = ts.workflow("full-suite.yml")
    on = suite.get("on") or suite.get(True) or {}
    types = (on.get("pull_request_target") or {}).get("types") if "pull_request_target" in on else []
    assert "pull_request_target" in on and (not types or {"opened", "synchronize", "reopened"} <= set(types)), \
        "589.2: the all tests check does not run when a pull request opens or gets a commit"
    assert any(j.get("name") == "all tests" for j in suite["jobs"].values()), "589.2: no job is named all tests"


def test_every_manual_fix_names_the_issue_it_fixes(record_property, tmp_path):
    """A manual fix's pull request says which issue it fixes; a run naming no issue opens nothing.

    Proves 830.5. Runs fix.yml naming issue #7 and checks the pull request's body says `Fixes #7`, so the issue closes
    when it merges and the fix is always traceable. Then runs it naming no issue, and naming one that is not a number,
    and checks each fails and opens no pull request."""
    record_property("proves", "830.5")
    need_workflow("830.5")
    run = Fix(tmp_path / "named")
    opened = run.opened()
    assert opened and "Fixes #7." in (flag(opened[0]["args"], "--body") or ""), \
        f"830.5: the manual fix's pull request does not name the issue it fixes: {opened}\n{run.tail()}"
    for bad in ("", "abc"):
        run = Fix(tmp_path / f"bad{bad or 'none'}", issue=bad)
        assert run.failed() and not run.opened(), f"830.5: a manual fix naming issue {bad!r} still opened: {run.opened()}"

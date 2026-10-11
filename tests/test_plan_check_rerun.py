"""An approved plan runs the pull request's plan check again on its current head (#295).

The plan check is the Acceptance criteria workflow (.github/workflows/acceptance-criteria.yml): its `list` job reads the issue's records
and builds one check per criterion of the approved plan, and its gate, "Acceptance criteria", fails with "No approved
plan found" while the newest plan has no approving review. It runs only when the pull request gets a new commit, so a
plan re-approved with nothing new to push kept its stale failure.

These tests run the whole agent workflow (agent.yml) for the plan reviewer on issue #57, whose pull request #60 is
open on try/issue-57, on the machine of test_start.py: every step's `if:` is evaluated and its script runs with bash
against a fake `gh`. The fake Claude Code hands back the review the test chose. Nothing is pushed by a plan review, so
the pull request's head stays the commit the test made: a re-approval with no new commit.

The fake GitHub of test_start.py is taught pull request #60 and GitHub Actions runs. Runs live in runs.json, each
{id, name, path, event, head_sha, head_branch, status, conclusion, run_attempt, matrix, reruns}. It answers:
  - `gh pr view 60|try/issue-57 --json ...` (number, headRefName, headRefOid, body, state, url, comments, reviews) and
    `gh api repos/o/r/pulls/60` (number, state, body, head.sha, head.ref), with -q/--jq a plain `.field` or `.head.sha`;
  - the runs: `gh api repos/o/r/actions/runs` and `repos/o/r/actions/workflows/acceptance-criteria.yml/runs` (the file name or
    the path), filtered by the query's head_sha, branch, event and status, newest first, as {total_count,
    workflow_runs}; `gh api repos/o/r/actions/runs/ID`; and `gh run list` with --workflow, --commit, --branch,
    --status, -L/--limit and --json (databaseId, headSha, status, conclusion, workflowName, event, number, attempt);
  - a re-run: `gh api -X POST repos/o/r/actions/runs/ID/rerun` or `.../rerun-failed-jobs`, and `gh run rerun ID`
    (with or without --failed).
A whole re-run runs the plan check again the way GitHub would: the fake runs Dokima's own `python3 -m dokima.checks
matrix` for pull request #60 against the fake GitHub as it is at that moment, and the gate passes exactly when the
plan check lists criteria and every one of them has a test (each test's own result is not what these tests judge).
Re-running only the failed jobs keeps the matrix the first attempt listed, as GitHub keeps a passed job's outputs, so
the gate fails again. GitHub refuses a re-run of a run that is still going ("HTTP 403: This workflow is already
running"), one asked with the workflow's own token, which agent.yml gives only read access ("HTTP 403: Resource not
accessible by integration"), and every re-run when the test made it refuse.
"""
import json
import os
import sys

import test_start as ts
from dokima import agent
from test_start import N, OWNER, Ctx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PR = 60
OLD = "0" * 40
REFUSED = "HTTP 403: Resource not accessible by integration"
STALE = [{"id": "none", "name": "No approved plan found for issue #57", "tests": ""}]

RUNS_GH = r'''
import subprocess
RUNS_FILE = os.path.join(d, "runs.json")
def runs():
    return json.load(open(RUNS_FILE)) if os.path.exists(RUNS_FILE) else []
def save_runs(rs):
    json.dump(rs, open(RUNS_FILE, "w"), indent=1)
def head():
    return open(os.path.join(d, "head.txt")).read().strip()
def pick(obj):
    q = (flag("-q", "--jq") or "").strip()
    if q.startswith(".") and all(p.isidentifier() for p in q[1:].split(".")):
        for p in q[1:].split("."):
            obj = obj.get(p, "") if isinstance(obj, dict) else ""
        print(obj if not isinstance(obj, (dict, list)) else json.dumps(obj))
    else:
        print(json.dumps(obj))
def rest_run(r):
    return {"id": r["id"], "name": r["name"], "path": r["path"], "event": r["event"], "head_sha": r["head_sha"],
            "head_branch": r["head_branch"], "status": r["status"], "conclusion": r["conclusion"],
            "run_attempt": r["run_attempt"], "html_url": f"https://github.com/o/r/actions/runs/{r['id']}"}
def gate(matrix):
    return "success" if matrix and all(row.get("tests") for row in matrix) else "failure"
def rerun(rid, failed_only):
    rs = runs()
    r = next((r for r in rs if r["id"] == int(rid)), None)
    if r is None:
        sys.stderr.write(f"HTTP 404: Not Found (https://api.github.com/repos/o/r/actions/runs/{rid})\n")
        sys.exit(1)
    if token != "fake-token":
        sys.stderr.write("HTTP 403: Resource not accessible by integration\n")
        sys.exit(1)
    if opts.get("refuse_rerun"):
        sys.stderr.write(opts["refuse_rerun"] + "\n")
        sys.exit(1)
    if r["status"] != "completed":
        sys.stderr.write("HTTP 403: This workflow is already running\n")
        sys.exit(1)
    matrix = r["matrix"]
    if not failed_only:
        ev = os.path.join(d, f"event-{rid}.json")
        json.dump({"pull_request": {"number": 60, "body": "Closes #57", "head": {"ref": "try/issue-57", "sha": r["head_sha"]}}}, open(ev, "w"))
        env = {**os.environ, "GITHUB_EVENT_PATH": ev, "GITHUB_REPOSITORY": "o/r", "PYTHONPATH": "@@ROOT@@",
               "PATH": os.path.dirname(os.path.abspath(sys.argv[0])) + os.pathsep + os.environ.get("PATH", "")}
        p = subprocess.run([sys.executable, "-m", "dokima.checks", "matrix"], env=env, capture_output=True, text=True, cwd=d)
        line = [l for l in p.stdout.splitlines() if l.startswith("matrix=")]
        matrix = json.loads(line[-1][len("matrix="):]) if p.returncode == 0 and line else []
    r["reruns"].append({"failed_only": failed_only, "token": token, "agent_started": started, "matrix": matrix})
    r.update(run_attempt=r["run_attempt"] + 1, matrix=matrix, conclusion=gate(matrix), status="completed")
    save_runs(rs)
def query(path):
    q = {}
    if "?" in path:
        for part in path.split("?", 1)[1].split("&"):
            k, _, v = part.partition("=")
            q[k] = v
    for i, x in enumerate(a):
        if x in ("-f", "-F", "--raw-field", "--field") and i + 1 < len(a) and "=" in a[i + 1]:
            k, _, v = a[i + 1].partition("=")
            q[k] = v
    return q
def listed(workflow, q):
    out = [r for r in runs() if not workflow or r["path"].endswith("/" + workflow.split("/")[-1]) or r["name"] == workflow]
    for key, field in (("head_sha", "head_sha"), ("branch", "head_branch"), ("event", "event")):
        if q.get(key):
            out = [r for r in out if r[field] == q[key]]
    if q.get("status"):
        out = [r for r in out if r["status"] == q["status"] or r["conclusion"] == q["status"]]
    return sorted(out, key=lambda r: -r["id"])
API_PATH = next((x.lstrip("/") for x in a[1:] if x.lstrip("/").startswith("repos/o/r/")), "") if a[:1] == ["api"] else ""
BARE = API_PATH.split("?", 1)[0]
if a[:2] == ["pr", "view"]:
    pick({"number": 60, "headRefName": "try/issue-57", "headRefOid": head(), "body": "Closes #57", "state": "OPEN",
          "url": "https://github.com/o/r/pull/60", "comments": comments_on("pr", 60), "reviews": []})
    sys.exit(0)
if BARE == "repos/o/r/pulls/60":
    pick({"number": 60, "state": "open", "body": "Closes #57", "head": {"sha": head(), "ref": "try/issue-57"}})
    sys.exit(0)
m = re.fullmatch(r"repos/o/r/actions/runs/(\d+)/(rerun|rerun-failed-jobs)", BARE)
if m:
    rerun(m.group(1), m.group(2) == "rerun-failed-jobs")
    print("{}")
    sys.exit(0)
m = re.fullmatch(r"repos/o/r/actions/runs/(\d+)", BARE)
if m:
    r = next((r for r in runs() if r["id"] == int(m.group(1))), None)
    if r is None:
        sys.stderr.write("HTTP 404: Not Found\n")
        sys.exit(1)
    pick(rest_run(r))
    sys.exit(0)
m = re.fullmatch(r"repos/o/r/actions/(?:workflows/(.+)/)?runs", BARE)
if m:
    rs = [rest_run(r) for r in listed(m.group(1), query(API_PATH))]
    pick({"total_count": len(rs), "workflow_runs": rs})
    sys.exit(0)
if a[:2] == ["run", "rerun"]:
    rid = next(x for x in a[2:] if x.isdigit())
    rerun(rid, "--failed" in a)
    sys.exit(0)
if a[:2] == ["run", "list"]:
    rs = listed(flag("--workflow", "-w"), {"head_sha": flag("--commit", "-c"), "branch": flag("--branch", "-b"),
                                           "status": flag("--status", "-s"), "event": flag("--event", "-e")})
    rs = rs[: int(flag("-L", "--limit") or 20)]
    pick([{"databaseId": r["id"], "headSha": r["head_sha"], "status": r["status"], "conclusion": r["conclusion"] or "",
           "workflowName": r["name"], "event": r["event"], "number": r["id"], "attempt": r["run_attempt"],
           "headBranch": r["head_branch"], "url": f"https://github.com/o/r/actions/runs/{r['id']}"} for r in rs])
    sys.exit(0)
'''


def fake_gh():
    """The fake GitHub of test_start.py, taught pull request #60 and the plan check's runs."""
    anchor = 'if a[:2] == ["issue", "view"]:'
    taught = ts.FAKE_GH.replace(anchor, RUNS_GH.replace("@@ROOT@@", ROOT) + anchor, 1)
    assert taught != ts.FAKE_GH, "test setup: could not teach the fake GitHub about runs"
    return taught.replace("#!/usr/bin/env python3", f"#!{sys.executable}")


def plan_run(rid, sha, status="completed", conclusion="failure", matrix=None):
    """One run of the plan check on commit `sha`, as GitHub keeps it."""
    return {"id": rid, "name": "Acceptance criteria", "path": ".github/workflows/acceptance-criteria.yml", "event": "pull_request_target",
            "head_sha": sha, "head_branch": "try/issue-57", "status": status,
            "conclusion": conclusion if status == "completed" else None, "run_attempt": 1,
            "matrix": STALE if matrix is None else matrix, "reruns": []}


def other_run(rid, sha):
    """A run of another workflow on the same commit."""
    return {**plan_run(rid, sha), "name": "full-suite", "path": ".github/workflows/full-suite.yml"}


# The issue's story: planned, approved, `/work`, then re-planned (code review sent a test back to the planner). The
# planner's push made the plan check fail with "No approved plan found", and the plan reviewer now looks again.
REPLANNED = ts.STORY_APPROVED + [ts.record_comment(ts.planner_record(ts.STORY), "2026-10-07T11:00:00Z")]
BLOCK = {**ts.APPROVE, "verdict": "block", "summary": "57.1's test proves nothing.",
         "raises": [{"kind": "blocker", "to": "planner", "label": "57.1", "text": "The test asserts nothing.", "evidence": "tests/test_x.py::test_a"}]}


class PlanReview(ts.Machine):
    """One plan review of issue #57, run through the whole agent workflow (agent.yml).

    Pull request #60 is open unless `pr_open` is False, the plan check's runs `runs` are on GitHub, and `options`
    reach the fake GitHub."""

    def __init__(self, tmp, runs, review=None, pr_open=True, options=None):
        super().__init__(tmp, REPLANNED, try_branch=True, options={"pr_open": pr_open, **(options or {})})
        t = self.tmp
        open(f"{t}/bin/gh", "w").write(fake_gh())
        os.chmod(f"{t}/bin/gh", 0o755)
        open(f"{t}/gh/head.txt", "w").write(self.try_sha)
        self.seeded_runs = [r(self.try_sha) if callable(r) else r for r in runs]
        json.dump(self.seeded_runs, open(f"{t}/gh/runs.json", "w"))
        if review is not None:
            json.dump(review, open(f"{t}/review.json", "w"))
        open(f"{t}/event.json", "w").write(json.dumps({"inputs": {"role": "reviewer", "stage": "plan", "issue": N}}))
        ctx = {"inputs": Ctx(role="reviewer", stage="plan", issue=N),
               "github": Ctx(event_name="workflow_dispatch", actor=OWNER, event=Ctx(), run_id="42", run_attempt="1",
                             server_url="https://github.com", repository="o/r", token="fake-github-token"),
               "secrets": Ctx(CLAUDE_CODE_OAUTH_TOKEN="fake-claude-token", DOKIMA_APP_KEY="k"),
               "vars": Ctx(DOKIMA_APP_ID="1"), "needs": Ctx()}
        wf = ts.workflow("agent.yml")
        self.result, _ = self.run_job("run", wf["jobs"]["run"], ctx, "workflow_dispatch",
                                      [("/tmp/", f"{t}/"), ("/home/runner/", f"{t}/home/")], wf.get("defaults"))
        self.failed = self.result == "failure"

    def runs(self):
        """Every run as GitHub holds it now, by id."""
        return {r["id"]: r for r in json.load(open(f"{self.tmp}/gh/runs.json"))}

    def rerun_calls(self):
        """Every call that asked GitHub to run a workflow run again."""
        return [c for c in self.calls() if c[:2] == ["run", "rerun"] or
                (c[:1] == ["api"] and any("/rerun" in x for x in c))]

    def review_card(self):
        """The plan review's record as posted on issue #57, or ''."""
        for c in self.comments():
            recs = agent.records([{"author": {"login": c["author"]}, "body": c["versions"][-1]}])
            if c["kind"] == "issue" and recs and recs[0].get("role") == "reviewer" and recs[0].get("stage") == "plan":
                return c["versions"][-1]
        return ""

    def pr_comments(self):
        """The bodies of the comments the bot wrote on pull request #60."""
        return [c["versions"][-1] for c in self.comments() if c["kind"] == "pr" and c["number"] == PR
                and c["author"] == agent.BOT]


def why(m):
    """What the machine saw, for a failure message."""
    return f"\nre-run calls: {m.rerun_calls()}\nruns: {json.dumps(m.runs(), indent=1)[-2500:]}\n{m.tail()}"


def test_a_reapproved_plan_with_no_new_commit_ends_with_a_passing_plan_check(record_property, tmp_path):
    """A re-approved plan with no new commit ends with a passing plan check.

    Proves 295.1. The plan check on the pull request's head failed with "No approved plan found" after the re-plan. The plan reviewer
    approves and nothing is pushed. The fake GitHub runs the plan check again exactly as asked, reading the issue's
    records at that moment, so the check passes only when it is run again in full, on the current head, after the
    approval is on the issue. An older run on an earlier commit stays as it was."""
    record_property("proves", "295.1")
    m = PlanReview(tmp_path, [plan_run(7000, OLD), lambda sha: plan_run(7001, sha), lambda sha: other_run(7002, sha)])
    assert not m.failed, f"295.1: the plan review's run failed at '{m.failed_step}'{why(m)}"
    assert m.review_card(), f"295.1: the plan review's record was not posted on the issue{why(m)}"
    runs = m.runs()
    assert runs[7001]["reruns"], f"295.1: the plan check on the head {m.try_sha[:7]} was not run again after the approval{why(m)}"
    assert runs[7001]["conclusion"] == "success", \
        f"295.1: the plan check on the head ran again but still fails (it ran before the approval was posted, or " \
        f"only its failed jobs ran again, keeping 'No approved plan found'){why(m)}"
    assert runs[7001]["matrix"] == [{"id": "57.1", "name": "57.1 · a", "tests": "tests/test_x.py::test_a"}], \
        f"295.1: the plan check that ran again did not list the approved plan's criterion{why(m)}"
    assert runs[7000] == m.seeded_runs[0], f"295.1: the plan check on an older commit was run again{why(m)}"
    assert len(runs[7001]["reruns"]) == 1, f"295.1: the plan check ran again more than once{why(m)}"


def test_only_an_approval_with_an_open_pull_request_runs_the_plan_check_again(record_property, tmp_path):
    """Only an approval with an open pull request runs the plan check again.

    Proves 295.2. A block runs nothing again, and an approval with no open pull request runs nothing and fails nothing.
    The same story, three ways: a block leaves the stale check alone (only an approval changes what the check reads);
    an approval with no pull request open asks GitHub to run nothing and still posts its record; and an approval with
    the pull request open runs it again, so the first two are not passing by doing nothing at all."""
    record_property("proves", "295.2")
    blocked = PlanReview(tmp_path / "block", [lambda sha: plan_run(7001, sha)], review=BLOCK)
    assert blocked.review_card(), f"295.2: the blocking plan review's record was not posted{why(blocked)}"
    assert not blocked.rerun_calls(), f"295.2: a plan review that blocked ran the plan check again{why(blocked)}"
    assert blocked.runs()[7001] == blocked.seeded_runs[0], f"295.2: a blocked plan changed the plan check{why(blocked)}"
    no_pr = PlanReview(tmp_path / "nopr", [], pr_open=False)
    assert not no_pr.failed, f"295.2: an approval with no open pull request failed the run at '{no_pr.failed_step}'{why(no_pr)}"
    assert no_pr.review_card(), f"295.2: the approval's record was not posted with no pull request open{why(no_pr)}"
    assert not no_pr.rerun_calls(), f"295.2: an approval with no open pull request asked GitHub to run something again{why(no_pr)}"
    approved = PlanReview(tmp_path / "approve", [lambda sha: plan_run(7001, sha)])
    assert approved.runs()[7001]["conclusion"] == "success", \
        f"295.2: an approval with the pull request open did not end with a passing plan check{why(approved)}"


def test_the_plan_check_runs_again_only_with_the_apps_key_after_the_agent_finished(record_property, tmp_path):
    """The plan check runs again only with Dokima's app key, after the agent finished.

    Proves 295.4. The app's manifest must also ask GitHub for that right. Every re-run call must carry the app's key (the workflow's own token is read-only and GitHub refuses it) and come
    after the agent ran, so no agent holds a key that can run workflows. The app's manifest, dokima/app.json, and
    Dokima's manifest in code, dokima/manifest.py, must both ask for write access to Actions, which GitHub requires to
    run a workflow again; with read access it refuses."""
    record_property("proves", "295.4")
    m = PlanReview(tmp_path, [lambda sha: plan_run(7001, sha)])
    meta = [json.loads(l) for l in open(f"{m.tmp}/gh/calls-meta.jsonl")]
    reruns = [c for c in meta if c["args"][:2] == ["run", "rerun"] or
              (c["args"][:1] == ["api"] and any("/rerun" in x for x in c["args"]))]
    assert reruns, f"295.4: the plan check was not run again{why(m)}"
    for c in reruns:
        assert c["token"] == "fake-token", f"295.4: the plan check was run again with {c['token']!r}, not the app's key"
        assert c["agent_started"], "295.4: the plan check was run again before the agent ran"
    manifest = json.load(open(os.path.join(ROOT, "dokima", "app.json")))
    assert manifest["default_permissions"].get("actions") == "write", \
        f"295.4: dokima/app.json asks for actions: {manifest['default_permissions'].get('actions')!r}; running the plan " \
        "check again needs write"
    from dokima.manifest import PERMISSIONS
    assert PERMISSIONS.get("actions") == "write", \
        f"295.4: dokima/manifest.py asks for actions: {PERMISSIONS.get('actions')!r}; running the plan check again " \
        "needs write, as dokima/app.json asks"

"""A check failed before plan approval no longer fails the merge gate (#620).

GitHub runs a pull request's checks only on a new commit or when a draft is readied. A plan approved with nothing new
to push keeps the checks that ran before the approval, and today Dokima's only way to start them again is to re-run
them, which GitHub refuses when the app lacks Actions: Read and write. The merge gate then reads the old red check and
fails, every time.

These tests run, in-process, what Dokima runs on GitHub: `agent recheck 57 OUT` once the plan review approved (the
step agent.yml runs after the record is up), then the merge gate on pull request #60 (built for issue #57 from
`try/issue-57`), against a fake GitHub that stands in for `dokima.agent_github.gh`. The fake holds:

- pull request #60, open, ready for review (not a draft), its head `HEAD`, through `gh pr list` and `gh pr view`;
- the Actions runs on its head, through `gh api repos/o/r/actions/runs?head_sha=..`; every re-run
  (`.../runs/ID/rerun`, `.../rerun-failed-jobs`, `gh run rerun`) is refused with "Resource not accessible by
  integration (HTTP 403)", as for an app without that permission;
- the check runs on its head, through `gh api repos/o/r/commits/SHA/check-runs` and `.../status`: before the
  approval, Acceptance criteria failed and all tests passed;
- turning it into a draft (`gh pr ready 60 --undo`, or GraphQL's convertPullRequestToDraft) and readying it
  (`gh pr ready 60`, or GraphQL's markPullRequestReadyForReview). Readying a draft starts its checks again, as
  GitHub's ready_for_review event does, and they now read the approved plan, so they pass. Readying a pull request
  that is not a draft starts nothing, as on GitHub;
- main's rule requiring both checks, a branch not behind main, and comments.

Time is faked, so the gate's 45-minute wait costs nothing. Any call the fake does not know fails, and is named in
the failure message.
"""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dokima import agent  # noqa: E402
from dokima import agent_autopilot  # noqa: E402
from dokima import agent_github  # noqa: E402

REPO = "o/r"
N = "57"
PR = 60
HEAD = "a" * 40
REQUIRED = ["all tests", "Acceptance criteria"]
DENIED = "gh: Resource not accessible by integration (HTTP 403)"


class FakeGitHub:
    """GitHub as these tests need it, in memory, answering `agent_github.gh(*args)`."""

    def __init__(self):
        self.draft = False
        self.clock = 0.0
        self.checks = [{"name": "Acceptance criteria", "head_sha": HEAD, "status": "completed", "conclusion": "failure"},
                       {"name": "all tests", "head_sha": HEAD, "status": "completed", "conclusion": "success"}]
        self.runs = [{"id": 7001, "name": "Acceptance criteria", "path": ".github/workflows/acceptance-criteria.yml",
                      "workflow_id": 1, "event": "pull_request_target", "head_sha": HEAD, "status": "completed",
                      "conclusion": "failure", "html_url": "https://github.com/o/r/actions/runs/7001"},
                     {"id": 7002, "name": "full suite", "path": ".github/workflows/full-suite.yml", "workflow_id": 2,
                      "event": "pull_request_target", "head_sha": HEAD, "status": "completed", "conclusion": "success",
                      "html_url": "https://github.com/o/r/actions/runs/7002"}]
        self.calls, self.unknown, self.comments, self.fresh_starts = [], [], [], 0

    def refuse(self, args, why):
        """Fail the call the way `gh` does, with GitHub's words on stderr."""
        raise subprocess.CalledProcessError(1, ["gh", *args], output="", stderr=why + "\n")

    def ready(self):
        """Ready the pull request: a draft's checks start again and pass on the approved plan."""
        if self.draft:
            self.draft = False
            self.fresh_starts += 1
            self.checks = [{"name": c, "head_sha": HEAD, "status": "completed", "conclusion": "success"}
                           for c in REQUIRED]

    def pr_field(self, field):
        """One field of pull request #60, as `gh pr view --json` gives it."""
        return {"number": PR, "headRefOid": HEAD, "isDraft": self.draft, "state": "OPEN",
                "headRefName": f"try/issue-{N}", "baseRefName": "main", "files": [{"path": "dokima/x.py"}]}.get(field)

    def __call__(self, *args):
        a = [str(x) for x in args]
        self.calls.append(a)
        query = a[a.index("-q") + 1] if "-q" in a else (a[a.index("--jq") + 1] if "--jq" in a else None)
        if a[:2] == ["pr", "list"]:
            if query and "number" in query:
                return f"{PR}\n"
            return json.dumps([{"number": PR, "headRefName": f"try/issue-{N}", "isDraft": self.draft}])
        if a[:2] == ["pr", "view"]:
            fields = a[a.index("--json") + 1].split(",") if "--json" in a else ["number"]
            if query and len(fields) == 1:
                v = self.pr_field(fields[0])
                return (json.dumps(v) if isinstance(v, bool) else str(v)) + "\n"
            return json.dumps({f: self.pr_field(f) for f in fields})
        if a[:2] == ["pr", "ready"]:
            if "--undo" in a:
                self.draft = True
            else:
                self.ready()
            return ""
        if a[:2] == ["pr", "comment"]:
            body = a[a.index("--body") + 1] if "--body" in a else open(a[a.index("--body-file") + 1]).read()
            self.comments.append(body)
            return "https://github.com/o/r/pull/60#issuecomment-1\n"
        if a[:2] == ["run", "rerun"]:
            self.refuse(a, DENIED)
        if a and a[0] == "api":
            method = a[a.index("-X") + 1] if "-X" in a else "GET"
            path = next((x for x in a[1:] if re.match(r"(repos|users|orgs)/|graphql$", x)), "")
            bare = path.split("?")[0]
            if bare == "graphql":
                text = " ".join(a)
                if "convertPullRequestToDraft" in text:
                    self.draft = True
                    return "{}"
                if "markPullRequestReadyForReview" in text:
                    self.ready()
                    return "{}"
            if re.fullmatch(r"repos/o/r/actions/runs/\d+/(rerun|rerun-failed-jobs)", bare):
                self.refuse(a, DENIED)
            if bare == "repos/o/r/actions/runs":
                return json.dumps({"total_count": len(self.runs), "workflow_runs": self.runs})
            m = re.fullmatch(r"repos/o/r/actions/runs/(\d+)", bare)
            if m and method == "GET":
                return json.dumps(next(r for r in self.runs if r["id"] == int(m.group(1))))
            if bare == "users/o":
                return "Organization\n" if query else json.dumps({"login": "o", "type": "Organization"})
            if bare == "repos/o/r/branches/main":
                return json.dumps({"name": "main", "protection": {"required_status_checks": {
                    "contexts": REQUIRED, "checks": [{"context": c} for c in REQUIRED]}}})
            if bare == f"repos/o/r/compare/main...{HEAD}":
                return json.dumps({"status": "ahead", "ahead_by": 1, "behind_by": 0})
            if bare == f"repos/o/r/commits/{HEAD}/check-runs":
                return json.dumps({"total_count": len(self.checks), "check_runs": self.checks})
            if bare == f"repos/o/r/commits/{HEAD}/status":
                return json.dumps({"state": "success", "statuses": []})
            if re.fullmatch(r"repos/o/r/issues/\d+/comments", bare) and method == "POST":
                self.comments.append(" ".join(a))
                return "{}"
        self.unknown.append(a)
        self.refuse(a, "fake gh does not support this call (HTTP 400)")

    def why(self):
        """What happened, for a failure message."""
        return (f"\ncalls the fake GitHub does not support: {self.unknown}\ncomments: {self.comments}"
                f"\nchecks on the head now: {self.checks}\ncalls: {self.calls[-30:]}")


def approve_plan(tmp_path, monkeypatch, fake):
    """Run `agent recheck 57 OUT` on an approved plan review, as agent.yml does."""
    monkeypatch.setattr(agent_github, "gh", fake)
    monkeypatch.setattr(time, "sleep", lambda s: setattr(fake, "clock", fake.clock + s))
    monkeypatch.setattr(time, "monotonic", lambda: fake.clock)
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    out = tmp_path / "out"
    out.mkdir()
    record = {"role": "reviewer", "stage": "plan", "issue": int(N), "check": {"passed": True, "problems": []},
              "handback": {"verdict": "approve", "summary": "The plan proves every criterion."}}
    (out / "record.json").write_text(json.dumps(record))
    agent.main(["agent", "recheck", N, str(out)])


def test_a_check_failed_before_approval_does_not_fail_the_merge_gate(record_property, tmp_path, monkeypatch):
    """A check failed before the plan's approval no longer fails the merge gate.

    Proves 620.1. Pull request #60 is ready for review, with Acceptance criteria red from before the plan was approved. The plan is
    approved, GitHub refuses every re-run for lack of permission, then the code review's merge gate runs on the same
    head. Only checks started after the approval read the approved plan and pass, so the gate passes only if Dokima
    got the checks started again some way other than a re-run. Today it reads the old red check and fails."""
    record_property("proves", "620.1")
    fake = FakeGitHub()
    approve_plan(tmp_path, monkeypatch, fake)
    state, head, why = agent_autopilot.merge_gate(REPO, PR)
    assert fake.fresh_starts >= 1, \
        ("620.1: after the plan was approved and re-runs were refused, the pull request's checks never started again, "
         f"so the merge gate read the check that failed before the approval (gate said {state}: {why}){fake.why()}")
    assert (state, head) == ("passed", HEAD), \
        f"620.1: the merge gate did not pass on {HEAD[:7]} with fresh green checks: {state}, {why}{fake.why()}"

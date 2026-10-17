"""Autopilot judges a pull request only by the checks main's branch rule requires (#561).

#528 taught autopilot to skip cancelled card runs, but other side runs are cancelled the same way: on #556 autopilot
stopped for the owner on "sync (cancelled)", board.yml's job, though every required check had passed. These tests call
autopilot's merge (`dokima.agent.automerge`) against a fake GitHub kept in memory: pull request #60 built for issue
#57 on main, its head commit, the check runs and commit statuses on that head, and merging.

Main's branch rule is read the way the drift audit reads it (dokima/audit.py): `gh api
repos/o/r/branches/main/protection` (or its `/required_status_checks`), which the app may NOT read (admin only; it reads `repos/o/r/branches/main` instead) with its
administration permission. It requires "all tests" and "Acceptance criteria", as Dokima's own rule does
(dokima/manifest.py). Rulesets (`repos/o/r/rules/branches/main`) answer an empty list, as on a repo protected the
classic way. The branch holds main's newest commit (`repos/o/r/compare/main...HEAD` answers `behind_by` 0). Time is faked: `time.sleep` only moves a fake clock that `time.time` and `time.monotonic` read, so a
wait costs no real time.
"""
import json
import subprocess
import time

from dokima import agent
from dokima import agent_github  # noqa: E402

REPO = "o/r"
ISSUE = 57
PR = 60
HEAD = "c3" * 20
REQUIRED = ["all tests", "Acceptance criteria"]
BAD_GATEWAY = "gh: HTTP 502: Bad Gateway"


def run(name, status="completed", conclusion="success"):
    """One check run on the head, as GitHub's check-runs API gives it."""
    return {"name": name, "head_sha": HEAD, "status": status, "conclusion": conclusion if status == "completed" else None}


GREEN = [run("all tests"), run("Acceptance criteria")]


class FakeGitHub:
    """The GitHub autopilot talks to while merging #60, remembering merges and comments."""

    def __init__(self, runs, statuses=(), required=REQUIRED, rule_fails=False):
        self.runs, self.statuses, self.required, self.rule_fails = list(runs), list(statuses), list(required), rule_fails
        self.merges, self.comments, self.clock = [], [], 1_000_000.0

    def gh(self, *args):
        """Answers one `gh` call the way GitHub would."""
        a = [str(x) for x in args]
        joined = " ".join(a)
        path = next((x.lstrip("/").split("?")[0] for x in a if x.lstrip("/").startswith("repos/")), "")
        if a[:2] == ["pr", "list"]:
            return f"{PR}\n"
        if a[:2] == ["pr", "view"]:
            pr = {"number": PR, "headRefOid": HEAD, "baseRefName": "main", "headRefName": f"try/issue-{ISSUE}", "isDraft": False}
            q = next((a[i + 1] for i, x in enumerate(a[:-1]) if x in ("-q", "--jq")), None)
            return (str(pr[q.lstrip(".")]) + "\n") if q else json.dumps(pr)
        if a[:2] == ["pr", "merge"]:
            self.merges.append(a)
            return ""
        if a[:2] in (["issue", "comment"], ["pr", "comment"]):
            self.comments.append(a)
            return ""
        if "graphql" in a:
            return json.dumps({"data": {"repository": {"pullRequest": {
                "state": "MERGED" if self.merges else "OPEN", "isInMergeQueue": False, "autoMergeRequest": None,
                "reviewDecision": None, "mergeStateStatus": "CLEAN"}}}})
        if path == f"repos/{REPO}/pulls/{PR}/files":
            return json.dumps([{"filename": "dokima/x.py"}])
        if path == f"repos/{REPO}/pulls/{PR}":
            return json.dumps({"number": PR, "head": {"sha": HEAD, "ref": f"try/issue-{ISSUE}"}, "base": {"ref": "main"},
                               "state": "open", "merged": False})
        if path in (f"repos/{REPO}/branches/main/protection", f"repos/{REPO}/branches/main/protection/required_status_checks"):
            # Admin-only: GitHub refuses Dokima's app here (#576), so the rule is read from the branch instead.
            raise subprocess.CalledProcessError(1, ["gh", *a], output="", stderr="Resource not accessible by integration (HTTP 403)")
        if path == f"repos/{REPO}":
            # The repo itself names its default branch, as GitHub does (#787).
            return json.dumps({"full_name": REPO, "default_branch": "main"})
        if path == f"repos/{REPO}/branches/main":
            if self.rule_fails:
                raise subprocess.CalledProcessError(1, ["gh", *a], output="", stderr=BAD_GATEWAY)
            inner = {"strict": True, "contexts": self.required,
                     "checks": [{"context": c, "app_id": None} for c in self.required]}
            return json.dumps({"name": "main", "protection": {"enabled": True, "required_status_checks": inner}})
        if path == f"repos/{REPO}/rules/branches/main":
            return "[]"
        if path.startswith(f"repos/{REPO}/compare/main..."):
            # The branch holds main's newest commit, so the merge gate has nothing to bring up to date (#596).
            return json.dumps({"status": "ahead", "ahead_by": 1, "behind_by": 0, "total_commits": 1})
        if path == f"repos/{REPO}/actions/variables/DOKIMA_AUTO_MERGE":
            # The auto-merge setting is unset here, as GitHub says for a variable never set (#557).
            raise subprocess.CalledProcessError(1, ["gh", *a], output="", stderr="HTTP 404: Not Found")
        if path == f"repos/{REPO}/commits/{HEAD}/check-runs":
            return json.dumps({"total_count": len(self.runs), "check_runs": self.runs})
        if path in (f"repos/{REPO}/commits/{HEAD}/status", f"repos/{REPO}/commits/{HEAD}/statuses"):
            return json.dumps(self.statuses if path.endswith("statuses")
                              else {"state": "success", "statuses": self.statuses})
        raise AssertionError(f"test setup: the fake GitHub does not know this call: gh {joined}")

    def sleep(self, seconds):
        """Moves the fake clock on instead of waiting."""
        self.clock += max(float(seconds), 0.0)


def merge(monkeypatch, runs, statuses=(), required=REQUIRED, rule_fails=False):
    """Runs autopilot's merge of #57's pull request on a fake GitHub.

    Returns how it went, why, and the merges asked."""
    fake = FakeGitHub(runs, statuses, required, rule_fails)
    monkeypatch.setattr(agent_github, "gh", fake.gh)
    monkeypatch.setattr(time, "sleep", fake.sleep)
    monkeypatch.setattr(time, "time", lambda: fake.clock)
    monkeypatch.setattr(time, "monotonic", lambda: fake.clock)
    _, how, why = agent.automerge(REPO, ISSUE)
    return how, why, fake.merges


def test_a_check_the_branch_rule_does_not_require_never_stops_autopilot(record_property, monkeypatch):
    """A pull request whose required checks passed merges, whatever the other checks on it show.

    Proves 561.1.
    Main requires All tests and Acceptance criteria, both green on #60's head. Beside them a side run that is not
    required is cancelled (board.yml's sync, as on #556), still running, or failed (a lint run, and a failed commit
    status): each time autopilot must merge #60 at that head. The same head with All tests cancelled instead must not
    merge, so autopilot is not simply ignoring cancelled runs. A head where a required check never ran must not merge,
    and when GitHub fails to give the branch rule nothing merges and the reason says what GitHub answered."""
    record_property("proves", "561.1")
    merging = (
        ("a cancelled sync, as on #556", GREEN + [run("sync", conclusion="cancelled")], ()),
        ("a side run still running", GREEN + [run("sync", status="in_progress")], ()),
        ("a failed side run", GREEN + [run("lint", conclusion="failure")], ()),
        ("a failed side commit status", GREEN, [{"context": "ci/coverage", "state": "failure"}]),
    )
    for case, runs, statuses in merging:
        how, why, merges = merge(monkeypatch, runs, statuses)
        assert how == "merged" and len(merges) == 1, \
            (f"561.1 ({case}): autopilot did not merge #60, though every check the branch rule requires passed: "
             f"how={how!r}, why={why!r}")
        assert HEAD in merges[0], f"561.1 ({case}): #60 was merged, but not pinned to the head whose checks were read: {merges[0]}"
    how, why, merges = merge(monkeypatch, [run("all tests", conclusion="cancelled"), run("Acceptance criteria"),
                                           run("sync", conclusion="cancelled")])
    assert not merges and how == "", \
        f"561.1 (required check cancelled): autopilot merged #60 though All tests, which main requires, was cancelled"
    how, why, merges = merge(monkeypatch, [run("Acceptance criteria"), run("sync")])
    assert not merges and how == "", \
        f"561.1 (required check never ran): autopilot merged #60 though All tests, which main requires, never ran on it"
    how, why, merges = merge(monkeypatch, GREEN, rule_fails=True)
    assert not merges and how == "", \
        f"561.1 (branch rule unreadable): autopilot merged #60 though GitHub did not say which checks main requires"
    assert "502" in (why or ""), \
        f"561.1 (branch rule unreadable): the reason autopilot gives does not say what GitHub answered: {why!r}"


def test_a_failed_required_check_still_stops_autopilot_and_names_it(record_property, monkeypatch):
    """A failed required check stops autopilot, and the reason names only that check.

    Proves 561.2.
    On #60's head All tests is green and Acceptance criteria, which main requires, failed, beside a failed lint run
    the rule does not require: autopilot must merge nothing and name Acceptance criteria, not lint. A required check
    given as a failed commit status stops it the same way, named. Beside them, the same head with Acceptance criteria
    green merges, so autopilot is not stopping on every head."""
    record_property("proves", "561.2")
    stopping = (
        ("a failed required check run", [run("all tests"), run("Acceptance criteria", conclusion="failure"),
                                         run("lint", conclusion="failure")], (), REQUIRED, "Acceptance criteria"),
        ("a failed required commit status", GREEN, [{"context": "ci/coverage", "state": "failure"}],
         REQUIRED + ["ci/coverage"], "ci/coverage"),
    )
    for case, runs, statuses, required, name in stopping:
        how, why, merges = merge(monkeypatch, runs, statuses, required)
        assert not merges and how == "", f"561.2 ({case}): autopilot merged #60 though {name}, which main requires, failed"
        assert name in (why or ""), f"561.2 ({case}): autopilot stopped but did not name {name}, the failed required check: {why!r}"
        assert "lint" not in (why or ""), \
            f"561.2 ({case}): autopilot named lint, a check the branch rule does not require, as a reason it stopped: {why!r}"
    how, why, merges = merge(monkeypatch, [run("all tests"), run("Acceptance criteria"), run("lint", conclusion="failure")])
    assert how == "merged" and len(merges) == 1, \
        (f"561.2 (required checks green): autopilot did not merge #60 though only lint, which main does not require, "
         f"failed: how={how!r}, why={why!r}")

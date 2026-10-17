"""A failed merge queue run puts its pull request back once, then sends it back to its worker (#830).

GitHub takes a pull request out of the merge queue when the queue's checks fail, and before #830 nothing noticed: the
pull request sat until someone looked. `agent_autopilot.queue_failed` is driven here with a fake `gh` that answers the
pull request, its comments, its files and the failed run's log, and records every write.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent_autopilot as ap, agent_records  # noqa: E402

REPO, PR, ISSUE, HEAD = "o/r", 830, 813, "a" * 40
QREF = f"gh-readonly-queue/main/pr-{PR}-{'b' * 40}"
LOG = "all tests\tRun\t2026Z FAILED tests/test_x.py::test_one - AssertionError\nERROR tests/test_y.py::test_two - boom\n"


class Gh:
    def __init__(self, comments=(), files=("dokima/x.py",), ref=f"try/issue-{ISSUE}"):
        self.comments, self.files, self.ref, self.calls = list(comments), list(files), ref, []

    def __call__(self, *a):
        self.calls.append(a)
        if a[:2] == ("api", f"repos/{REPO}/pulls/{PR}"):
            return json.dumps({"state": "open", "head": {"sha": HEAD, "ref": self.ref, "repo": {"full_name": REPO}}})
        if a[0] == "api" and a[1].startswith(f"repos/{REPO}/issues/{PR}/comments"):
            return json.dumps([{"body": b} for b in self.comments])
        if a[0] == "api" and a[1].startswith(f"repos/{REPO}/pulls/{PR}/files"):
            return json.dumps([{"filename": f} for f in self.files])
        if a[:2] == ("run", "view"):
            return LOG
        return ""

    def writes(self, kind):
        return [c for c in self.calls if c[:2] == kind]


def run(monkeypatch, gh, on=True, blocks=0, run_id="111"):
    monkeypatch.setattr(ap.agent_github, "gh", gh)
    monkeypatch.setattr(ap, "merge_method", lambda: "squash")
    monkeypatch.setattr(ap, "on_autopilot", lambda repo, n, strict=False: on)
    monkeypatch.setattr(ap, "conversation", lambda repo, n: ({}, []))
    monkeypatch.setattr(ap, "blocks_since_owner", lambda items, owners, stage: blocks)
    return ap.queue_failed(REPO, QREF, run_id, f"https://x/runs/{run_id}", ["owner"])


def test_the_first_queue_failure_puts_the_pull_request_back_once(record_property, monkeypatch):
    """The first failure on a head re-queues it at that head and says so on the PR, naming the failing tests."""
    record_property("proves", "830.1")
    gh = Gh()
    out = run(monkeypatch, gh)
    merges = gh.writes(("pr", "merge"))
    assert merges and "--match-head-commit" in merges[0] and HEAD in merges[0] and "--squash" in merges[0], \
        f"830.1: the pull request was not put back in the queue at its head: {gh.calls}"
    said = [c for c in gh.writes(("pr", "comment"))]
    assert said and agent_records.QUEUE_FAILED in said[0][-1] and "tests/test_x.py::test_one" in said[0][-1] \
        and "tests/test_y.py::test_two" in said[0][-1], f"830.1: the PR comment does not mark or name the failure: {said}"
    assert not gh.writes(("api", "-X")), f"830.1: a first failure must not start the worker: {gh.calls}"
    assert "re-queued" in out


def test_a_second_failure_on_the_same_head_sends_it_back_to_the_worker(record_property, monkeypatch):
    """The same head failing again goes back to the worker as a failed gate; at three blocks it stops for the owner."""
    record_property("proves", "830.2")
    mark = f"{agent_records.QUEUE_FAILED}<!-- head={HEAD} run=111 -->\nfirst"
    gh = Gh(comments=[mark])
    run(monkeypatch, gh, run_id="222")
    assert not gh.writes(("pr", "merge")), f"830.2: a second failure was re-queued again: {gh.calls}"
    issue = [c for c in gh.writes(("issue", "comment")) if c[2] == str(ISSUE)]
    assert issue and f"**Next:** {agent_records.GATE_FAILED}:" in issue[0][-1], f"830.2: no gate-failed record on #{ISSUE}: {gh.calls}"
    assert agent_records.gate_failed({"body": issue[0][-1]}), "830.2: the queue failure does not count as a block"
    dispatch = [c for c in gh.calls if "client_payload[role]=worker" in c]
    assert dispatch and f"client_payload[issue]={ISSUE}" in dispatch[0], f"830.2: the worker was not started: {gh.calls}"
    gh = Gh(comments=[mark])
    run(monkeypatch, gh, blocks=2, run_id="333")
    assert not [c for c in gh.calls if "client_payload[role]=worker" in c], "830.2: at three blocks the worker still started"
    assert "@owner" in gh.writes(("issue", "comment"))[0][-1], "830.2: at three blocks the owner is not mentioned"


def test_one_queue_run_is_handled_once_and_a_workflow_change_waits_for_the_owner(record_property, monkeypatch):
    """Both required checks failing on one run act once; a pull request changing a workflow is not re-queued by code."""
    record_property("proves", "830.3")
    gh = Gh(comments=[f"{agent_records.QUEUE_FAILED}<!-- head={HEAD} run=111 -->"])
    assert "handled already" in run(monkeypatch, gh, run_id="111")
    assert not [c for c in gh.calls if c[0] in ("pr", "issue") or "-X" in c], f"830.3: a handled run wrote again: {gh.calls}"
    gh = Gh(files=[".github/workflows/full-suite.yml"])
    run(monkeypatch, gh)
    assert not gh.writes(("pr", "merge")), "830.3: a workflow change was put back in the queue by code"
    assert "@owner" in gh.writes(("pr", "comment"))[0][-1], "830.3: the owner is not told to merge the workflow change"


def test_a_branch_that_is_not_the_queue_does_nothing(record_property, monkeypatch):
    """A run on any other branch (a pull request, main) is left alone."""
    record_property("proves", "830.4")
    gh = Gh()
    monkeypatch.setattr(ap.agent_github, "gh", gh)
    assert "not a merge queue branch" in ap.queue_failed(REPO, "try/issue-1", "1", "u", ["owner"])
    assert gh.calls == []


def test_a_manual_fix_that_fails_twice_tells_the_owner_on_its_issue(record_property, monkeypatch):
    """A manual fix has no plan, so no worker starts; the second failure is said on the PR and on the issue it fixes."""
    record_property("proves", "830.6")
    mark = f"{agent_records.QUEUE_FAILED}<!-- head={HEAD} run=111 -->"
    gh = Gh(comments=[mark], ref="fix/queue-failed")
    real = gh.__call__

    def with_body(*a):
        if a[:2] == ("api", f"repos/{REPO}/pulls/{PR}"):
            return json.dumps({"state": "open", "body": "Fixes #807. A manual fix.",
                               "head": {"sha": HEAD, "ref": "fix/queue-failed", "repo": {"full_name": REPO}}})
        return real(*a)
    gh.__call__ = with_body
    monkeypatch.setattr(ap.agent_github, "gh", lambda *a: (gh.calls.append(a), with_body(*a))[1] if a[:2] == ("api", f"repos/{REPO}/pulls/{PR}") else gh(*a))
    monkeypatch.setattr(ap, "merge_method", lambda: "squash")
    out = ap.queue_failed(REPO, QREF, "222", "https://x/runs/222", ["owner"])
    assert not [c for c in gh.calls if "client_payload[role]=worker" in c], "830.6: a manual fix started a worker"
    on807 = [c for c in gh.writes(("issue", "comment")) if c[2] == "807"]
    assert on807 and "@owner" in on807[0][-1], f"830.6: the failure was not said on the issue the fix names: {gh.calls}"
    assert "#807" in out

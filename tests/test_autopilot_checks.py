"""Autopilot ignores cancelled card runs and waits for checks still running (#528).

On #525 autopilot refused a green pull request because card redraws on its head were cancelled: GitHub's queue
cancels a redraw a newer one replaces, and a card run judges nothing. On #530 it stopped for the owner while All tests
was still running, minutes before it passed. These tests call autopilot's merge (`dokima.agent.automerge`) against a
fake GitHub kept in memory: pull request #60 built for issue #57, its head commit, the check runs and commit statuses
on that head, and merging. Each read of the head's check runs moves the fake on one step through the list of
check-run states the test gives, the last state staying for good, so a check can be still running and then finish.
Time is faked too: `time.sleep` only moves a fake clock that `time.time` and `time.monotonic` read, so waiting costs
no real time.
"""
import json
import time

import pytest

from dokima import agent

REPO = "o/r"
ISSUE = 57
PR = 60
HEAD = "a1" * 20


def run(name, status="completed", conclusion="success"):
    """One check run as GitHub's check-runs API gives it."""
    return {"name": name, "head_sha": HEAD, "status": status, "conclusion": conclusion if status == "completed" else None}


GREEN = [run("all tests"), run("528.1"), run("plan check")]
CANCELLED_CARDS = [run("card", conclusion="cancelled")] * 4


class FakeGitHub:
    """The GitHub autopilot talks to while merging #60, remembering merges and comments."""

    def __init__(self, steps, statuses=()):
        self.steps, self.statuses, self.reads = [list(s) for s in steps], list(statuses), 0
        self.merges, self.comments, self.clock = [], [], 1_000_000.0

    def gh(self, *args):
        """Answers one `gh` call the way GitHub would."""
        a = list(args)
        joined = " ".join(a)
        if a[:2] == ["pr", "list"]:
            return f"{PR}\n"
        if a[:2] == ["pr", "view"]:
            return HEAD + "\n"
        if a[:2] == ["pr", "merge"]:
            self.merges.append(a)
            return ""
        if a[:2] in (["issue", "comment"], ["pr", "comment"]):
            self.comments.append(a)
            return ""
        if "graphql" in a:
            merged = bool(self.merges)
            return json.dumps({"data": {"repository": {"pullRequest": {
                "state": "MERGED" if merged else "OPEN", "isInMergeQueue": False, "autoMergeRequest": None,
                "reviewDecision": None, "mergeStateStatus": "CLEAN"}}}})
        if f"pulls/{PR}/files" in joined:
            return json.dumps([{"filename": "dokima/x.py"}])
        if "/protection" in joined:
            # Main's branch rule requires every check the test gives except the card runs, which judge nothing (#561).
            req = sorted({r["name"] for s in self.steps for r in s if r["name"] != "card"}
                         | {s["context"] for s in self.statuses})
            inner = {"strict": True, "contexts": req, "checks": [{"context": c, "app_id": None} for c in req]}
            return json.dumps(inner if joined.split("?")[0].endswith("/required_status_checks")
                              else {"required_status_checks": inner})
        if "check-runs" in joined:
            self.reads += 1
            if self.reads > 500:
                raise AssertionError("autopilot read the checks 500 times without deciding")
            runs = self.steps[min(self.reads, len(self.steps)) - 1]
            return json.dumps({"total_count": len(runs), "check_runs": runs})
        if "/status" in joined:
            return json.dumps({"state": "success", "statuses": self.statuses})
        raise AssertionError(f"the fake GitHub does not know this call: gh {joined}")

    def sleep(self, seconds):
        """Moves the fake clock on instead of waiting."""
        self.clock += max(float(seconds), 0.0)


@pytest.fixture
def github(monkeypatch):
    """Puts a fake GitHub in place, given the check-run states the head goes through."""
    def make(steps, statuses=()):
        fake = FakeGitHub(steps, statuses)
        monkeypatch.setattr(agent, "gh", fake.gh)
        monkeypatch.setattr(time, "sleep", fake.sleep)
        monkeypatch.setattr(time, "time", lambda: fake.clock)
        monkeypatch.setattr(time, "monotonic", lambda: fake.clock)
        return fake
    return make


def merge(fake):
    """Runs autopilot's merge of #57's pull request; returns how, why and the merges asked."""
    pr, how, why = agent.automerge(REPO, ISSUE)
    return how, why, fake.merges


def test_cancelled_card_runs_no_longer_keep_autopilot_from_merging_a_green_pull_request(record_property, github):
    """A pull request with cancelled card runs merges when every other check passed.

    Proves 528.1.
    The head carries four cancelled card runs beside green All tests, criterion and plan checks, as on #525: autopilot
    must merge it at that head and say it merged. Beside it, the same head with All tests cancelled instead must not
    merge, so autopilot leaves out only the card runs, not every cancelled check."""
    record_property("proves", "528.1")
    fake = github([GREEN + CANCELLED_CARDS])
    how, why, merges = merge(fake)
    assert how == "merged" and len(merges) == 1, \
        (f"528.1: autopilot did not merge #60, whose only checks that did not pass are cancelled card runs: "
         f"how={how!r}, why={why!r}, merges asked={merges}")
    assert HEAD in merges[0], f"528.1: #60 was merged, but not pinned to the head whose checks were read: {merges[0]}"
    fake = github([[run("all tests", conclusion="cancelled"), run("528.1"), run("plan check")] + CANCELLED_CARDS])
    how, why, merges = merge(fake)
    assert not merges and how == "", \
        (f"528.1: autopilot merged #60 though All tests was cancelled on its head; only card runs may be left out: "
         f"how={how!r}, merges asked={merges}")
    assert "all tests" in why, f"528.1: autopilot did not say All tests kept it from merging: {why!r}"


def test_a_failed_check_still_stops_autopilot_and_names_it(record_property, github):
    """A failed check stops autopilot and names it, even after a wait.

    Proves 528.2.
    Three heads, none of which may merge: All tests failed with cancelled card runs beside it; a commit status failed
    beside green check runs; and All tests still running when autopilot first looks, then failing. Each time
    autopilot must merge nothing, return no outcome, and name the failed check in why it stopped."""
    record_property("proves", "528.2")
    cases = (
        ("All tests failed", [[run("all tests", conclusion="failure"), run("528.1")] + CANCELLED_CARDS], (), "all tests"),
        ("a commit status failed", [GREEN], [{"context": "ci/coverage", "state": "failure"}], "ci/coverage"),
        ("All tests failed after running", [[run("all tests", status="in_progress"), run("528.1")],
                                            [run("all tests", status="in_progress"), run("528.1")],
                                            [run("all tests", conclusion="failure"), run("528.1")]], (), "all tests"),
    )
    for case, steps, statuses, name in cases:
        fake = github(steps, statuses)
        how, why, merges = merge(fake)
        assert not merges and how == "", f"528.2 ({case}): autopilot merged #60 or claimed an outcome: how={how!r}, merges={merges}"
        assert name in why and "running" not in why, \
            f"528.2 ({case}): autopilot did not stop saying {name!r} failed: {why!r}"


def test_a_check_still_running_makes_autopilot_wait_and_merge_once_it_passes(record_property, github):
    """Autopilot waits for a running check, then merges once it passes.

    Proves 528.3.
    All tests is still running for autopilot's first three looks at the head, as on #530, and then passes, with the
    other checks green all along. Autopilot must keep waiting (the fake clock moves only when it sleeps), then merge
    #60 at that head and say it merged, rather than stop saying a check is still running."""
    record_property("proves", "528.3")
    running = [run("all tests", status="in_progress"), run("528.1"), run("plan check")]
    fake = github([running, running, running, GREEN])
    how, why, merges = merge(fake)
    assert how == "merged" and len(merges) == 1, \
        (f"528.3: autopilot did not wait for All tests to finish and then merge #60; it stopped with how={how!r}, "
         f"why={why!r}, after reading the checks {fake.reads} time(s)")
    assert fake.reads >= 4, f"528.3: autopilot merged before All tests finished: it read the checks {fake.reads} time(s)"
    assert HEAD in merges[0], f"528.3: #60 was merged, but not pinned to the head whose checks were read: {merges[0]}"

"""Cards stop looking up old work branches and old worker runs (#763).

The old label flow pushed to `work/issue-N` and ran `worker.yml`, whose runs were named `worker for #N`. Both are
gone (#516): agents push to `try/issue-N` and run in agent.yml. These tests fake GitHub with a stub that records
every call, so they check what Dokima asks GitHub, and what it finds, without the network.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dokima import agent, agent_github, card, plan  # noqa: E402

REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}


def branch_github(prs_by_branch, seen):
    """A faked GitHub serving each branch's pull requests, recording every call."""
    def gh(*args, **kw):
        args = [str(a) for a in args]
        seen.append(args)
        for branch, prs in prs_by_branch.items():
            if (args[:2] == ["pr", "list"] and branch in args) or any(f"head=o:{branch}" in a for a in args):
                return json.dumps([{"number": p} for p in prs])
        return "[]"
    return gh


def test_finding_an_issues_prs_never_looks_up_the_old_work_branch(record_property, monkeypatch):
    """Finding an issue's pull requests never asks GitHub about its old work branch.

    Proves 763.1. Fakes GitHub with a pull request only on `work/issue-40`, then asks both lookups (the agents' list of the issue's
    pull requests and the card's one pull request) for issue 40. Checks neither names the old branch to GitHub and
    neither finds that pull request."""
    record_property("proves", "763.1")
    seen = []
    fake = branch_github({"work/issue-40": [7]}, seen)
    monkeypatch.setattr(agent_github, "gh", fake)
    monkeypatch.setattr(card, "gh", fake)
    listed = agent_github.linked_prs(REPO, 40)
    found = card.issue_pr(REPO, 40)
    asked = [a for a in seen if any("work/issue-40" in x for x in a)]
    assert not asked, f"763.1: finding issue 40's pull requests still asked GitHub about work/issue-40: {asked}"
    assert listed == [], f"763.1: the issue's pull requests still include one from the old work branch: {listed}"
    assert found is None, f"763.1: the card still found PR #{found} on the old work branch"


def test_the_card_never_finds_its_issue_from_an_old_worker_runs_title(record_property, monkeypatch):
    """An old worker run's title no longer tells the card which issue to draw.

    Proves 763.3. Runs the card's event lookup with only a run title `worker for #40` and a commit with no pull request, as card.yml
    sets them after a run finishes. Checks the card finds no issue, where it used to take #40 from the title."""
    record_property("proves", "763.3")
    for name in ("ON_PR", "ISSUE_NUMBER", "PR_NUMBER"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("RUN_TITLE", "worker for #40")
    monkeypatch.setenv("HEAD_SHA", "abc")
    monkeypatch.setattr(card, "gh", branch_github({}, []))
    got = card.find_work(REPO)
    assert got == (None, None), f"763.3: the card still took its issue from the run title 'worker for #40': {got}"


def test_a_redraw_never_asks_github_for_old_worker_runs(record_property, monkeypatch, tmp_path):
    """Redrawing a card never asks GitHub for runs of the deleted worker workflow.

    Proves 763.4. The card must still draw. Runs the real gather for issue 40 against a faked GitHub that records every call, then draws the card from what it
    gathered. Checks no call asked for `worker.yml` runs and the card is drawn without a latest run link."""
    record_property("proves", "763.4")
    seen = []

    def gh(*args, **kw):
        args = [str(a) for a in args]
        seen.append(args)
        if args[:2] == ["issue", "view"]:
            return json.dumps({"number": 40, "title": "t", "body": "My ask.", "comments": []})
        if any("actions/workflows/worker.yml/runs" in a for a in args):
            return json.dumps({"workflow_runs": [{"display_title": "worker for #40", "status": "completed",
                                                  "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/13"}]})
        if any("/contents/" in a for a in args):
            raise subprocess.CalledProcessError(1, ["gh", *args], stderr="Not Found")
        return "[]"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("REPO", REPO)
    for module in (card, agent_github, plan):
        monkeypatch.setattr(module, "gh", gh)
    found = card.gather(REPO, 40, None)
    asked = [a for a in seen if any("worker.yml" in x for x in a)]
    assert not asked, f"763.4: redrawing the card still asked GitHub for old worker runs: {asked}"
    text = card.render(REPO, ISSUE, found)
    assert text.startswith(plan.CARD_START), "763.4: the card did not draw from what the redraw gathered"
    assert "latest run" not in text, "763.4: the card still links a latest run read from the old worker workflow"


def test_an_old_work_branch_no_longer_names_a_pull_requests_issue(record_property):
    """A pull request on an old work branch no longer names its issue by branch.

    Proves 763.6. Asks which issue a pull request on `work/issue-12` with no closing line was built for, and checks the answer is
    none, while one on `try/issue-12` still names issue 12."""
    record_property("proves", "763.6")
    got = agent.issue_of_pr("work/issue-12", "")
    assert got is None, f"763.6: a pull request on the old work branch is still matched to issue {got}"
    assert str(agent.issue_of_pr("try/issue-12", "")) == "12", "763.6: a pull request on the try branch lost its issue"


def test_no_test_still_fakes_the_deleted_lookups(record_property):
    """The old worker run lookup is gone, with every test that only exercised it.

    Proves 763.5. Checks the card no longer has the lookup, then reads every test file but this one for it, the old
    worker workflow's runs and the helper that played an old worker run finishing. This plan deletes those parts of
    the tests itself; the check fails today because the lookup they exercised is still there."""
    record_property("proves", "763.5")
    assert not hasattr(card, "latest_worker_run"), "763.5: the old worker run lookup the deleted tests exercised is still in the card"
    gone = ("latest_worker_run", "actions/workflows/worker.yml", "def worker_finished")
    here = os.path.dirname(os.path.abspath(__file__))
    left = [f"tests/{name}: {word}" for name in sorted(os.listdir(here))
            if name.endswith(".py") and name != os.path.basename(__file__)
            for word in gone if word in open(os.path.join(here, name), encoding="utf-8").read()]
    assert not left, f"763.5: tests still check the deleted code: {left}"

"""The Definition of Done shows Code review and All tests running while they run (#372).

Seen on #367: All tests had passed and the code review had been running for a minute, yet the card still said Code
review "not started". dokima/card.py's code_review() knew only a finished review, and card.yml skipped the bot's own
comments, so the review's live run card never redrew the card; and card.yml redrew only when the full suite finished,
never when it started.

The first test draws the card from records and comments alone, through dokima/card.py's render(). The others play
card.yml for one event at a time against a fake GitHub with tests/card_player.py, and read the cards it leaves on
issue #246 and its PR #260.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from card_player import (BOT, OWNER, REPOSITORY, Hub, done_of, issue_comment, must_redraw, pr_comment,  # noqa: E402
                         sender, stale_again)
from dokima import agent, card  # noqa: E402

RUNNING_ICON = "dokima/icons/running.svg"
REPO = "o/r"


def rec(role, stage=None, **handback):
    """A record that passed its check, as the card reads it."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/{REPO}/actions/runs/1"}


def built():
    """A plan, its approval, /work and the build: the steps before a code review."""
    plan = {"kind": "user_story", "summary": "A thing is built.", "user_story": "The owner sees the thing.",
            "acceptance_criteria": [{"text": "The thing shows.", "source": f"https://github.com/{REPO}/issues/1"}],
            "non_functional": [], "scope": ["app/x.py"], "out_of_scope": ["Nothing else."], "tests": {}}
    return [rec("planner", **plan), rec("reviewer", "plan", verdict="approve", blockers=[]), "/work", rec("worker")]


def live(role, stage, state, who=None):
    """The bot's live run card for one run of `role` at `stage`, in `state`.

    `state` is queued, setting-up, working or checking."""
    return {"author": {"login": who or BOT}, "body": agent.live_card(role, stage, state), "where": "PR #5"}


def items_of(steps):
    """The conversation the card reads, from records, owner words and live cards.

    Records and the owner's words go through card.as_items; live cards are kept as they are."""
    out = []
    for st in steps:
        out += [st] if isinstance(st, dict) and "author" in st else card.as_items([st], OWNER)
    for k, c in enumerate(out):
        c.setdefault("createdAt", f"2026-10-09T10:{k:02d}:00Z")
    return out


def review_row(steps):
    """The Code review part of the drawn Definition of Done, and the whole card."""
    items = items_of(steps)
    found = {"recs": agent.records(items), "items": items, "pr": {"number": 5, "merged": False, "state": "open"},
             "check_runs": [], "reviews": [], "owners": {OWNER}, "tests": {}, "worker": None, "children": []}
    os.environ.setdefault("GITHUB_REPOSITORY", REPO)
    text = card.render(REPO, {"number": 1, "url": f"https://github.com/{REPO}/issues/1"}, found)
    line = next((l for l in text.splitlines() if l.startswith("**Definition of Done:**")), "")
    part = next((p for p in line.split(" · ") if p.rstrip().endswith("Code review")), "")
    return part, text


def test_code_review_shows_running_from_its_queued_card_until_its_record(record_property):
    """Code review shows running from its queued run card until its record.

    Proves 372.1.
    Draws the card for a built issue with no code review yet (not started), then with the bot's code review run card
    queued, setting up, working and checking (running, drawn with dokima/icons/running.svg), then with the review's
    record after it (passed for an approve, failed for a block). A plan review's run card, a code review card from
    before the newest build, and the same card text pasted by someone other than the bot leave it not started."""
    record_property("proves", "372.1")

    def alt(part):
        return part.split('alt="', 1)[1].split('"', 1)[0] if 'alt="' in part else None

    part, text = review_row(built())
    assert alt(part) == "not started", \
        f"372.1: with no code review run card up, Code review should show not started, not {alt(part)!r}: {part!r}"
    for state in ("queued", "setting-up", "working", "checking"):
        part, text = review_row(built() + [live("reviewer", "pr", state)])
        assert alt(part) == "running", (f"372.1: with the code review's run card up and {state}, the Definition of "
                                        f"Done should show Code review running, not {alt(part)!r}: {part!r}")
        assert RUNNING_ICON in part.split("Code review")[0].split("<img")[1], \
            f"372.1: a running Code review should be drawn with {RUNNING_ICON}, the card's in-progress icon: {part!r}"
    for verdict, want in (("approve", "passed"), ("block", "failed")):
        part, _ = review_row(built() + [live("reviewer", "pr", "working"),
                                        rec("reviewer", "pr", verdict=verdict, blockers=[])])
        assert alt(part) == want, \
            f"372.1: once the code review's record says {verdict}, Code review should show {want}, not {alt(part)!r}"
    for what, steps in (
            ("a plan review's run card", built() + [live("reviewer", "plan", "working")]),
            ("a worker's run card", built() + [live("worker", "", "working")]),
            ("a code review card from before the newest build", built()[:-1] + [live("reviewer", "pr", "working"),
                                                                                  rec("worker")]),
            ("the code review card's text pasted by the owner", built() + [live("reviewer", "pr", "working", OWNER)])):
        part, _ = review_row(steps)
        assert alt(part) == "not started", f"372.1: {what} should leave Code review not started, not {alt(part)!r}"


def suite(n, p, action, status):
    """A workflow_run event for the full suite on PR p, at `action` (requested, in_progress, completed)."""
    run = {"name": "full suite", "head_sha": f"sha{p}", "head_branch": f"try/issue-{n}", "display_title": f"Issue {n}",
           "event": "pull_request", "status": status, "conclusion": "success" if status == "completed" else None,
           "pull_requests": [{"number": p, "head": {"ref": f"try/issue-{n}", "sha": f"sha{p}"}, "base": {"ref": "main"}}]}
    return "workflow_run", {"action": action, "workflow": {"name": "full suite"}, "workflow_run": run,
                            "sender": sender("bot"), "repository": REPOSITORY}


def set_all_tests(hub, p, status):
    """Put PR p's all tests check in `status` on its newest commit."""
    s = hub.load()
    for c in s["checks"][f"sha{p}"]:
        if c["name"] == "all tests":
            c["status"], c["conclusion"] = status, "success" if status == "completed" else None
    hub.save()


def test_all_tests_shows_running_once_the_full_suite_starts(tmp_path, record_property):
    """All tests shows running on both cards once the full suite starts.

    Proves 372.2.
    Plays card.yml for the full suite's run being requested (its all tests check queued) and then starting (in
    progress), and checks the issue's and the PR's cards both show All tests running. Then the suite finishes and both
    cards show it passed."""
    record_property("proves", "372.2")
    hub = Hub(tmp_path)
    set_all_tests(hub, 260, "queued")
    hub.run(*suite(246, 260, "requested", "queued"), "372.2")
    set_all_tests(hub, 260, "in_progress")
    hub.run(*suite(246, 260, "in_progress", "in_progress"), "372.2")
    for where, text in (("issue #246", hub.issue_body(246)), ("PR #260", hub.pr_body(260))):
        got = done_of(text).get("All tests")
        assert got == "running", (f"372.2: the full suite started on PR #260, but {where}'s card shows All tests as "
                                  f"{got!r}, not running; card.yml redraws only when the suite ends:\n{hub.log[-2000:]}")
    set_all_tests(hub, 260, "completed")
    must_redraw(hub, suite(246, 260, "completed", "completed"), "372.2")
    for where, text in (("issue #246", hub.issue_body(246)), ("PR #260", hub.pr_body(260))):
        assert done_of(text).get("All tests") == "passed", \
            f"372.2: once the full suite passed, {where}'s card should show All tests passed: {done_of(text)}"


def review_queued(hub, n=246, p=260):
    """Drop the code review record and put its queued run card on PR p.

    Takes away issue n's code review record and posts the queued card as the bot does.

    Returns the card's text."""
    s = hub.load()
    s["issues"][str(n)]["comments"] = [c for c in s["issues"][str(n)]["comments"]
                                       if not ('"role": "reviewer"' in c["body"] and '"stage": "pr"' in c["body"])]
    text = agent.live_card("reviewer", "pr", "queued")
    s["prs"][str(p)]["comments"].append({"login": BOT, "body": text, "at": "2026-10-09T05:00:00Z"})
    hub.save()
    return text


def test_the_code_reviews_queued_card_redraws_the_issue_and_pr_cards(tmp_path, record_property):
    """Both cards redraw when the code review's run card goes up, showing it running.

    Proves 372.3.
    Puts the bot's queued code review card on PR #260 after the worker's build, plays card.yml for the comment event
    GitHub sends, and checks it redraws both cards and both show Code review running."""
    record_property("proves", "372.3")
    hub = Hub(tmp_path)
    text = review_queued(hub)
    must_redraw(hub, pr_comment(246, 260, who="bot", text=text), "372.3")
    for where, body in (("issue #246", hub.issue_body(246)), ("PR #260", hub.pr_body(260))):
        got = done_of(body).get("Code review")
        assert got == "running", \
            f"372.3: the code review's run card went up on PR #260, but {where}'s card shows Code review {got!r}"


def play(hub, event, k):
    """Play one event with every card stale, and return the queues it took.

    Returns the card job's queues, every queue taken, and the ones that cancel."""
    stale_again(hub)
    r = must_redraw(hub, event, k)
    return r.card_groups(), r.all_groups(), r.cancelling_groups()


def test_the_redraw_on_the_queued_card_waits_in_the_issues_own_queue(tmp_path, record_property):
    """The redraw on the run card waits in the issue's own queue.

    Proves 372.4.
    Plays card.yml for the queued code review card on PR #260 and for a comment on issue #246, and checks the card
    job of both waits in the same queue (#346), that queue cancels no running redraw, and #312's queue is another."""
    record_property("proves", "372.4")
    hub = Hub(tmp_path)
    text = review_queued(hub)
    review_q, _, cancelling = play(hub, pr_comment(246, 260, who="bot", text=text), "372.4")
    issue_q, _, _ = play(hub, issue_comment(246), "372.4")
    other_q, _, _ = play(hub, issue_comment(312), "372.4")
    assert review_q and None not in review_q, "372.4: the redraw on the code review's run card waits in no queue"
    assert review_q == issue_q, (f"372.4: the redraw on the code review's run card waits in {review_q}, not in issue "
                                 f"#246's own queue {issue_q}")
    assert review_q != other_q, f"372.4: #246's and #312's redraws share the queue {review_q}"
    assert not cancelling, f"372.4: the redraw on the code review's run card cancels a running one: {cancelling}"

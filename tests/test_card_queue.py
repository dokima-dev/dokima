"""Each issue's card redraws wait in their own queue, never cancelling another issue's (#346).

All card redraws used to share one queue (card.yml's single concurrency group `card`), and GitHub keeps only one waiting
run per queue: a redraw for one issue waiting there was dropped when a redraw for another issue arrived, which is how
#312's card missed its update. Now an issue and its pull request share one queue that keeps the newest redraw, and two
issues never share one.

These tests play card.yml for one event at a time against a fake GitHub, with tests/card_player.py (the player #332's
planner wrote on branch try/issue-332), and read the concurrency groups every run took a place in. The events are the
ones card.yml redraws on today: the issue changing or getting a comment, the pull request merged, the checks of the pull
request finishing (Acceptance criteria and full suite), and the worker finishing.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from card_player import (OWNER, Hub, checks_finished, issue_comment, issue_event, must_redraw,  # noqa: E402
                         pr_comment, pr_event, schedule, stale_again, worker_finished)

def events_about(n, p):
    """Every event card.yml redraws on today about issue n or its pull request p.

    As {what: (event name, payload)}."""
    return {"the issue edited": issue_event(n, "edited"),
            "a comment on the issue": issue_comment(n),
            "the pull request merged by the owner": pr_event(n, p, "closed", OWNER, merged=True),
            "the pull request merged by the bot on autopilot": pr_event(n, p, "closed", "bot", merged=True),
            "the criteria checks finishing": checks_finished(n, p, "Acceptance criteria"),
            "the full suite finishing": checks_finished(n, p, "full suite"),
            "the worker finishing": worker_finished(n)}


def play(hub, event, k):
    """Play one event with every card stale, and return the queues its run took.

    Returns (the queues the card-writing jobs waited in, every queue taken, the queues that cancel the run in them)."""
    stale_again(hub)
    r = must_redraw(hub, event, k)
    return r.card_groups(), r.all_groups(), r.cancelling_groups()


def test_every_redraw_about_an_issue_or_its_pr_waits_in_a_queue_of_its_own_that_keeps_the_newest(tmp_path, record_property):
    """Redraws about an issue or its PR wait in its own queue, keeping the newest.

    Proves 346.1.     Plays card.yml for each event card.yml redraws on about #246 or its PR #260 (the issue edited, a comment on it, the
    merge by the owner and by the bot, the Acceptance criteria and full suite checks finishing, the worker finishing), and the
    same for #312 and PR #314. Every run must redraw, the job that writes the cards must wait in a named queue, all of
    one issue's runs in the same one, and that queue must be its own: #312's redraws wait in a different one. No queue
    any run takes a place in may cancel the run already in it, so GitHub lets the running redraw finish and keeps the
    newest waiting one."""
    record_property("proves", "346.1")
    hub = Hub(tmp_path)
    own = {}
    for n, p in ((246, 260), (312, 314)):
        queues = {}
        for what, event in events_about(n, p).items():
            card, _, cancelling = play(hub, event, "346.1")
            assert card, f"346.1: on {what} for #{n} no job of card.yml wrote the stale cards"
            assert None not in card, f"346.1: on {what} for #{n} the job that writes the cards waits in no queue at all"
            assert not cancelling, \
                f"346.1: on {what} for #{n} card.yml takes a queue that cancels the redraw already running: {cancelling}"
            queues[what] = card
        found = set().union(*queues.values())
        assert len(found) == 1, f"346.1: #{n}'s and PR #{p}'s redraws wait in more than one queue: {queues}"
        own[n] = found.pop()
    assert own[246] != own[312], \
        f"346.1: #246's and #312's redraws wait in the same queue {own[246]!r}, so it is not a queue of their own"


def test_a_redraw_for_one_issue_never_shares_a_queue_with_another_issue_or_the_sweep(tmp_path, record_property):
    """One issue's redraw never shares a queue with another issue's or the sweep's.

    Proves 346.2.     Plays card.yml for every event about #246 or PR #260, every event about #312 or PR #314, and the 15-minute sweep,
    and collects every concurrency group each run takes a place in (the workflow's and each job's). No group #246's
    runs take may be one #312's or the sweep's take, and no group #312's runs take may be the sweep's, so a waiting
    redraw for one is never dropped for a newer redraw of the other. Each issue's own runs still find a queue: a run
    taking no group at all would let two redraws of one issue run at once."""
    record_property("proves", "346.2")
    hub = Hub(tmp_path)
    places = {}
    for who, events in ((246, events_about(246, 260)), (312, events_about(312, 314)), ("sweep", {"the sweep": schedule()})):
        for what, event in events.items():
            card, taken, _ = play(hub, event, "346.2")
            if who != "sweep":
                assert card and None not in card, f"346.2: on {what} for #{who} the redraw waits in no queue"
            places.setdefault(who, set()).update(taken)
    for a, b in ((246, 312), (246, "sweep"), (312, "sweep")):
        shared = places[a] & places[b]
        assert not shared, (f"346.2: redraws for {'#' if a != 'sweep' else ''}{a} and {'#' if b != 'sweep' else ''}{b} "
                            f"share the queue {sorted(shared)}, so a newer one drops the other's waiting redraw")

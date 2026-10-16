"""Every change on an issue or its PR redraws its card, from card.yml alone (#438).

Story 2 of #425, re-planned as one story of three criteria.

#419: the code review had passed, yet the card said Code review running for 30 minutes. card.yml picked its moments:
it skipped the bot's own edits and comments (except a code review's run card on a pull request) and redrew on a run's
start only for the full suite. The review's record is the bot's edit of its run card, so nothing redrew. Beside
card.yml, the plan approval (`python3 -m dokima.agent next`, dokima/agent.py record_links) drew the cards of the issues
its links touched. The play-through (.github/workflows/playthrough.yml) ran only from the Run workflow button.

These tests play card.yml one event at a time on the fake GitHub of tests/card_player.py, run the plan approval
against a fake, read .github/workflows/playthrough.yml, and run `python3 -m dokima.playthrough`
with a temp git repo standing in for a pull request. Nothing calls real GitHub.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from card_player import (BOT, OWNER, REPOSITORY, Hub, checks_finished, issue_comment, issue_event,  # noqa: E402
                         line_note, pr_comment, pr_event, review_event, sender, stale_again)
import card_player  # noqa: E402
from test_start import Ctx, condition, evaluate, fill, load_yaml  # noqa: E402
from dokima import agent, body  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
N, P = 246, 260
# The activity types GitHub starts a workflow on when its `on:` names the event with no `types:`.
DEFAULT_TYPES = {"pull_request_target": ("opened", "synchronize", "reopened"),
                 "pull_request": ("opened", "synchronize", "reopened"),
                 "workflow_run": ("requested", "completed")}


# --- helpers -------------------------------------------------------------------------------------------------------

def github_starts(wf, event_name, event):
    """True when GitHub itself would start `wf` on this event, default activity types included.

    tests/card_player.py starts a workflow on any action when its `on:` lists no types; GitHub does not for
    pull_request_target and workflow_run, so this checks the types GitHub really uses."""
    if not card_player.starts(wf, event_name, event):
        return False
    t = card_player.triggers(wf)[event_name]
    types = card_player.listed(t.get("types")) if isinstance(t, dict) else []
    action = event.get("action")
    return bool(types) or event_name not in DEFAULT_TYPES or action in DEFAULT_TYPES[event_name]


def reaches_card(event_name, event):
    """True when GitHub starts card.yml on this event, itself or through a relay."""
    if github_starts(card_player.workflow(), event_name, event):
        return True
    return any(github_starts(wf, event_name, event) for _, wf in card_player.relays(event_name, event))


def run_started(n, p, workflow, state):
    """A workflow_run event: `workflow` on PR p started (in_progress) or was requested."""
    name, event = checks_finished(n, p, workflow)
    event["action"] = state
    event["workflow_run"].update(status="in_progress" if state == "in_progress" else "queued", conclusion=None)
    return name, event


def every_change(n=N, p=P):
    """Every change GitHub announces on issue n or its pull request p.

    As {what: (event name, payload)}.

    Edits, comments and labels by a person and by the bot, a run's start and its result, the pull request's own
    changes, reviews and line notes. The merge is last, so the ones before it find the pull request open."""
    live = agent.live_card("reviewer", "pr", "queued")
    return {
        "the owner opens the issue": issue_event(n, "opened"),
        "the owner edits the issue": issue_event(n, "edited"),
        "the bot edits the issue": issue_event(n, "edited", who="bot"),
        "the bot labels the issue": issue_event(n, "labeled", who="bot"),
        "the owner unlabels the issue": issue_event(n, "unlabeled"),
        "the owner closes the issue": issue_event(n, "closed"),
        "the owner reopens the issue": issue_event(n, "reopened"),
        "the owner comments on the issue": issue_comment(n),
        "the bot comments on the issue": issue_comment(n, who="bot", text="Autopilot: plan approved, starting work"),
        "the bot edits its comment on the issue": issue_comment(n, who="bot", action="edited", text="A record."),
        "the owner deletes a comment on the issue": issue_comment(n, action="deleted"),
        "the owner comments on the pull request": pr_comment(n, p),
        "the bot puts up a run card on the pull request": pr_comment(n, p, who="bot", text=live),
        "the bot posts a plain comment on the pull request": pr_comment(n, p, who="bot", text="A note from the bot."),
        "the bot edits its run card into a record on the pull request": pr_comment(n, p, who="bot", action="edited",
                                                                                   text="A record."),
        "the bot opens the pull request": pr_event(n, p, "opened"),
        "the owner edits the pull request": pr_event(n, p, "edited", who=OWNER),
        "the bot pushes a commit to the pull request": pr_event(n, p, "synchronize"),
        "the owner closes the pull request unmerged": pr_event(n, p, "closed", who=OWNER),
        "the owner reopens the pull request": pr_event(n, p, "reopened", who=OWNER),
        "the owner reviews the pull request": review_event(n, p),
        "the owner writes a note on a line": line_note(n, p),
        "the Acceptance criteria run starts": run_started(n, p, "Acceptance criteria", "in_progress"),
        "the Acceptance criteria run ends": checks_finished(n, p, "Acceptance criteria"),
        "the full suite starts": run_started(n, p, "full suite", "in_progress"),
        "the full suite ends": checks_finished(n, p, "full suite"),
        "the bot merges the pull request": pr_event(n, p, "closed", who="bot", merged=True),
    }


def both_redrawn(hub, n=N, p=P):
    """The cards that still hold the old card, by name; empty when both were redrawn."""
    old = "An old card, drawn before the last event."
    return [where for where, text in ((f"issue #{n}", hub.issue_body(n)), (f"PR #{p}", hub.pr_body(p))) if old in text]


def play_change(hub, what, event, k):
    """Play one change with both cards stale; card.yml's run, once it redrew both."""
    stale_again(hub)
    assert reaches_card(*event), f"{k}: card.yml does not start when {what}, so its cards keep what they showed"
    r = hub.run(*event, k)
    assert r.started and r.card_ran(), f"{k}: card.yml started when {what} but its card job did not run"
    assert not r.failed(), f"{k}: card.yml's run when {what} failed:\n{r.log[-3000:]}"
    left = both_redrawn(hub)
    assert not left, f"{k}: when {what}, card.yml left the old card on {', '.join(left)}"
    return r


# --- 438.1: every change on an issue or its pull request redraws both cards --------------------------------------

def test_every_change_on_an_issue_or_its_pull_request_redraws_both_cards(tmp_path, record_property):
    """Every change on an issue or its pull request redraws both cards.

    Proves 438.1.
    Plays card.yml on the fake GitHub for every change GitHub announces about issue #246 or its PR #260, with both
    cards stale each time: the issue opened, edited (by the owner and by the bot), labeled, closed and reopened; a
    comment posted, edited and deleted on the issue and on the pull request, the bot's included; a run card going up
    and being edited into its record; the pull request opened, edited, pushed to, closed, reopened, reviewed, noted on
    a line and merged; the Acceptance criteria and full suite runs starting and ending. GitHub
    must start card.yml for each (counting only the activity types GitHub really sends), and the run must leave
    neither card old. One missed change turns it red, naming it."""
    record_property("proves", "438.1")
    hub = Hub(tmp_path)
    missed = []
    for what, event in every_change().items():
        if what == "the bot merges the pull request":
            hub.merge(N, P, by=BOT)
        try:
            play_change(hub, what, event, "438.1")
        except AssertionError as e:
            missed.append(str(e).splitlines()[0])
    assert not missed, "438.1: not every change redraws both cards:\n" + "\n".join(missed)


# --- 438.2: only card.yml writes the card ------------------------------------------------------------------------

def approval_saves_no_card(tmp_path):
    """Approving a plan saves no card; card.yml's redraw then shows its links on every card.

    Runs the plan approval (`python3 -m dokima.agent next` on an approving plan review) on the fake GitHub of
    tests/test_plan_links_recorded.py, for a plan that says #252 is blocked by #301, blocks #302 and relates to #303.
    The approval must still record the blocking links on GitHub, and must write no issue body at all. Then card.yml's
    own redraw of #252 (`python3 dokima/card.py`, as on the record's comment) must leave #252's card showing all three
    links and #301, #302 and #303 each showing its link from its own side, with every owner's ask kept."""
    import test_plan_links_recorded as tl
    hub = tl.Hub(tmp_path)
    hub.post(tl.plan(tl.links([301], [302], [303])))
    rec = tl.review("approve")
    hub.next(rec)
    saved = sorted({w["issue"] for w in hub.writes("body")})
    assert not saved, f"438.2: the plan approval saved the card of {', '.join(f'#{n}' for n in saved)} itself"
    assert hub.blocked_by(tl.N) == [301] and hub.blocked_by(302) == [tl.N], \
        f"438.2: the plan approval no longer records its blocking links: {hub.load()['deps']}"
    hub.post(rec)
    hub.redraw(tl.N)
    assert hub.card_links(tl.N) == {"blocked_by": {301}, "blocks": {302}, "relates_to": {303}}, \
        f"438.2: after card.yml's redraw, #{tl.N}'s card does not show its links: {hub.card_links(tl.N)}"
    expected = {301: {"blocked_by": set(), "blocks": {tl.N}, "relates_to": set()},
                302: {"blocked_by": {tl.N}, "blocks": set(), "relates_to": set()},
                303: {"blocked_by": set(), "blocks": set(), "relates_to": {tl.N}}}
    for n, want in expected.items():
        assert hub.card_links(n) == want, \
            f"438.2: after card.yml's redraw of #{tl.N}, #{n}'s card should show {want}, shows {hub.card_links(n)}"
        assert body.ask(hub.body(n)) == hub.asks[n], f"438.2: the owner's ask on #{n} changed"


def test_only_card_yml_writes_the_card(tmp_path, record_property):
    """The plan approval saves no card; card.yml shows its links.

    Proves 438.2.
    Runs the plan approval (`python3 -m dokima.agent next` on an approving plan review) on the fake GitHub of
    tests/test_plan_links_recorded.py, for a plan that says #252 is blocked by #301, blocks #302 and relates to #303:
    it must still record the blocking links and write no issue body, and card.yml's own redraw of #252 must then show
    all three links on every card involved."""
    record_property("proves", "438.2")
    approval_saves_no_card(tmp_path / "approval")


# --- 438.3: the play-through runs by itself on a pull request changing card, board or workflow code -----------------

def git(cwd, *args):
    """Run git in `cwd` as a test user; its output."""
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()

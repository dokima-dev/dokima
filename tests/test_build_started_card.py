"""Once a build has started, the card says Work and stops asking for /work.

Issue #439, story 3 of #425.
Before this, dokima/card.py status() placed the card from the newest record alone. After a plan review approved, it
said Plan with Needs you: Say /work to build the plan until the worker's record arrived, even while the worker was
building. The board already follows AGENTS.md (The board): a build starts with a code owner's `/work`, the bot's line
`Autopilot: plan approved, starting work` or the worker's run card, and the same words from anyone else start nothing.
These tests hold the issue card and the PR card to that same rule. They use test_card_status's in-memory history:
records the bot posted and comments, drawn with card.render on the issue page and on the pull request page.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import test_card_status as tcs  # noqa: E402
from dokima import agent, card  # noqa: E402
from tests.agent_patch import patch_agent  # noqa: E402

STRANGER = "passer-by"
SAY_WORK = "Say /work to build the plan"


@pytest.fixture(autouse=True)
def bot(monkeypatch):
    patch_agent(monkeypatch, "BOT", tcs.BOT)


def approved_then(*extra):
    """What the card is drawn from after an approved plan and the `extra` comments.

    Each extra comment is a (login, words) pair. The pull request is open, as it is when a plan is re-approved while it waits."""
    items = tcs.said(tcs.PLANNED, tcs.PLAN_OK)
    for i, (login, words) in enumerate(extra, len(items)):
        items.append(tcs.comment(login, words, i))
    return dict(tcs.found_for([tcs.PLANNED, tcs.PLAN_OK], pr=tcs.PR, check_runs=tcs.GREEN),
                items=items, recs=agent.records(items))


def both_lines(found):
    """The status line of the issue card and of the PR card."""
    return {page: tcs.status_line(card.render(tcs.REPO, tcs.ISSUE, found, page=page)) for page in ("issue", "pr")}


STARTS = [
    ("the code owner's /work", lambda: (tcs.OWNER, "/work")),
    ("the code owner's /work with words after it", lambda: (tcs.OWNER, "/work go ahead")),
    ("the bot's Autopilot line", lambda: (tcs.BOT, "Autopilot: plan approved, starting work")),
    ("the worker's queued run card", lambda: (tcs.BOT, agent.live_card("worker", "", "handoff"))),
    ("the worker's run card once it works", lambda: (tcs.BOT, agent.live_card("worker", "", "working"))),
]


@pytest.mark.parametrize("name,start", STARTS, ids=[s[0] for s in STARTS])
def test_once_a_build_has_started_both_cards_say_work_and_need_no_one(record_property, name, start):
    """Once a build starts, the issue and PR cards say Work, with no Needs you.

    Proves 439.1.
    After an approved plan, starts the build each way it can start: the code owner's /work, the bot's Autopilot line,
    or the worker's run card, queued or working. Then checks card.status says Work with nothing for the owner, and that
    the status line of both cards starts with Work and never says Needs you or Say /work."""
    record_property("proves", "439.1")
    found = approved_then(start())
    stage, todo = card.status(tcs.ISSUE, found)
    assert (stage, todo) == ("Work", None), \
        f"439.1: after {name} the card says {stage} with to-do {todo!r}; a started build is Work with nothing for you"
    for page, line in both_lines(found).items():
        assert tcs.bare(line).startswith("Work"), f"439.1: after {name} the {page} card's status line is “{line}”, not Work"
        assert "Needs you" not in line and "/work" not in line, \
            f"439.1: after {name} the {page} card still asks for you: “{line}”"


def test_a_build_started_then_a_stranger_speaking_still_says_work(record_property):
    """A started build stays Work whatever anyone else says after it.

    Proves 439.1.
    After the code owner's /work, someone who is not a code owner comments; both cards still say Work with no
    Needs you."""
    record_property("proves", "439.1")
    found = approved_then((tcs.OWNER, "/work"), (STRANGER, "Any news?"))
    assert card.status(tcs.ISSUE, found) == ("Work", None), \
        f"439.1: a comment after /work moved the card to {card.status(tcs.ISSUE, found)}, not Work with nothing for you"


NOT_STARTED = [
    ("nothing said yet", ()),
    ("someone who is not a code owner says /work", ((STRANGER, "/work"),)),
    ("someone who is not a code owner posts the Autopilot line", ((STRANGER, "Autopilot: plan approved, starting work"),)),
    ("someone who is not a code owner copies the worker's run card", ((STRANGER, "RUN_CARD"),)),
    ("the code owner only comments", ((tcs.OWNER, "Looks good, thanks"),)),
]


@pytest.mark.parametrize("name,extra", NOT_STARTED, ids=[c[0] for c in NOT_STARTED])
def test_an_approved_plan_whose_build_has_not_started_still_asks_for_work(record_property, name, extra):
    """An approved plan not yet being built still asks you to say /work.

    Proves 439.2.
    It says Plan with Needs you: Say /work to build the plan.
    After an approved plan, either nothing is said, or someone who is not a code owner says /work, posts the
    Autopilot line or copies the worker's run card, or the code owner comments without a command. Each time both cards
    must still say Plan with Needs you: Say /work to build the plan. Then the code owner says /work, and the card must
    turn to Work with nothing for the owner, so a card that never moves on fails too."""
    record_property("proves", "439.2")
    extra = tuple((who, agent.live_card("worker", "", "handoff") if words == "RUN_CARD" else words) for who, words in extra)
    found = approved_then(*extra)
    stage, todo = card.status(tcs.ISSUE, found)
    assert stage == "Plan" and todo is not None and tcs.bare(todo) == SAY_WORK, \
        f"439.2: when {name}, the card says {stage} with to-do {todo!r}; it must say Plan with Needs you: {SAY_WORK}"
    for page, line in both_lines(found).items():
        assert tcs.bare(line).startswith("Plan"), f"439.2: when {name}, the {page} card's status line is “{line}”, not Plan"
        assert "Needs you" in line and SAY_WORK in tcs.bare(line), \
            f"439.2: when {name}, the {page} card's status line “{line}” does not say Needs you: {SAY_WORK}"
    after = approved_then(*extra, (tcs.OWNER, "/work"))
    assert card.status(tcs.ISSUE, after) == ("Work", None), \
        f"439.2: when {name} and then the code owner says /work, the card says {card.status(tcs.ISSUE, after)}, not Work"

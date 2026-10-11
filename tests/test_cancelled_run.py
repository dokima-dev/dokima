"""A cancelled run says so quietly, the owner is mentioned on a real rejection, and nothing restarts by itself (#188).

These tests run the agent workflow (.github/workflows/agent.yml) the way GitHub runs it, with the machine from
test_start.py, and cancel some runs part way, the way the Cancel button on the Actions page does: at the code-owner
gate (before the run's card is up), while the tools install (card up, no agent yet), while the agent works, and after
the agent's hand-back passed code's check. Other runs are not cancelled and end the usual ways: a hand-back code
rejects, a step that fails before the agent, and a blocking plan review that the river sends back to the planner.
Each scenario runs once per module and the tests read what it left on the fake GitHub: its comments, and every call
that could start a run.
"""
import os
import re

import pytest

import test_start as ts
from test_start import APPROVE, N, OWNER, PIP_BROKEN, PR, STORY, STORY_APPROVED, STORY_PLANNED, Run, owner_comment

from dokima import agent

LIVE = "<!-- dokima-live -->"
MENTION = re.compile(r"(?<![\w/@.`])@[A-Za-z0-9][A-Za-z0-9-]*")
ICON = re.compile(r"/dokima/icons/([A-Za-z0-9_-]+)\.svg")
BAD_REVIEW = {"verdict": "maybe"}
# A blocking review of the one-story plan (only criterion: 57.1), so every ask it lists is matched to 57.1 (#215).
BLOCK = dict(APPROVE, verdict="block", summary="57.1 has no test that would fail without the work.",
             asks=[dict(a, criterion="57.1") for a in APPROVE["asks"]],
             raises=[{"kind": "blocker", "to": "planner", "label": "57.1", "text": "The test only checks a file exists.", "evidence": "tests/test_x.py::test_a"}])
AGENT = "The agent (Claude Code)"

# Runs cancelled part way: name -> (role, stage, history, options, review, the step it is cancelled at, where its card is).
CANCELLED = {
    "gate": ("reviewer", "plan", STORY_PLANNED, None, None, "Only a code owner starts an agent", ("issue", N)),
    "install": ("worker", "", STORY_APPROVED, None, None, "Install pytest and Claude Code", ("issue", N)),
    "planner": ("planner", "", [owner_comment("/plan", "2026-10-07T10:00:00Z")], None, None, AGENT, ("issue", N)),
    "reviewer": ("reviewer", "plan", STORY_PLANNED, None, None, AGENT, ("issue", N)),
    "worker": ("worker", "", STORY_APPROVED, {"pr_open": True}, None, AGENT, ("pr", PR)),
    "after-check": ("reviewer", "plan", STORY_PLANNED, None, BLOCK, "Code checks the hand-back", ("issue", N)),
}


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    """Every scenario these tests read, each run once through the whole agent workflow."""
    t = tmp_path_factory.mktemp("cancel")
    out = {name: Run(t / name, role, stage, hist, try_branch=True, options=opts, review=review, cancel_at=at)
           for name, (role, stage, hist, opts, review, at, _) in CANCELLED.items()}
    out["rejected"] = Run(t / "rejected", "reviewer", "plan", STORY_PLANNED, try_branch=True, review=BAD_REVIEW)
    out["no-tools"] = Run(t / "no-tools", "worker", "", STORY_APPROVED, try_branch=True, broken={"pip": PIP_BROKEN})
    out["blocked"] = Run(t / "blocked", "reviewer", "plan", STORY_PLANNED, try_branch=True, review=BLOCK)
    return out


def visible(body):
    """A body without its folded JSON record: the part the owner reads."""
    return re.sub(r"```json\n.*?\n```", "", body, flags=re.S)


def only_comment(r, crit, name):
    """The one comment a run left, as it stands now, checked to be the only one and posted by Dokima's bot."""
    cs = r.comments()
    assert len(cs) == 1, (f"{crit} ({name}): the run left {len(cs)} comments, expected exactly one card: "
                          f"{[(c['kind'], c['number'], c['versions'][-1][:150]) for c in cs]}\n{r.tail()}")
    assert cs[0]["author"] == agent.BOT, f"{crit} ({name}): the run's card was posted by {cs[0]['author']}, not Dokima's bot"
    return cs[0]


def cancelled(r, crit, name):
    """Checks the scenario really was cancelled where it should be."""
    at = CANCELLED[name][5]
    assert r.cancelled_step == at, f"{crit} ({name}): setup: the run was not cancelled at '{at}':\n{r.tail()}"
    assert (name in ("gate", "install")) != r.agent_started(), \
        f"{crit} ({name}): setup: the agent {'started' if r.agent_started() else 'never started'} in this scenario"


def start_calls(r):
    """Every call the run made that starts or restarts a run: a dispatch, a re-run, or a workflow started by hand."""
    return [c for c in r.calls() if any("dispatches" in x or "rerun" in x for x in c)
            or c[:2] in (["workflow", "run"], ["run", "rerun"])]


def test_a_cancelled_run_says_so_on_its_card_and_mentions_no_one(record_property, runs):
    """A run cancelled at any point leaves one card that says it was cancelled, mentions no one and is not a failure.

    Cancels runs at the code-owner gate, while the tools install, while the planner, the plan reviewer and the worker
    (whose card is on its open pull request) work, and after a review's hand-back passed code's check. Each must leave
    exactly one comment, in the right place, that says it was cancelled, no longer says getting ready or working,
    names no one with an @, shows no running, queued or failed icon, does not say any hand-back was rejected or that a
    step failed, and ends with a Next line.
    Runs that end without a cancel (a rejected hand-back, a failed install, a blocking review) must leave their record
    and never say cancelled in any comment they leave, including the next stage's queued card a hand-off posts."""
    record_property("proves", "188.1")
    for name, spec in CANCELLED.items():
        r = runs[name]
        cancelled(r, "188.1", name)
        c = only_comment(r, "188.1", name)
        kind, number = spec[6]
        assert (c["kind"], str(c["number"])) == (kind, str(number)), \
            f"188.1 ({name}): the cancelled run's card is on {c['kind']} #{c['number']}, expected {kind} #{number}"
        body = visible(c["versions"][-1])
        assert re.search(r"\bcancell?ed\b", body, re.I), f"188.1 ({name}): the card does not say the run was cancelled:\n{body[:900]}"
        assert LIVE not in body and "working since" not in body and "getting ready" not in body, \
            f"188.1 ({name}): the card still shows the run as getting ready or working:\n{body[:900]}"
        assert not {"running", "queued", "failed"} & set(ICON.findall(body)) and 'alt="failed"' not in body, \
            f"188.1 ({name}): the card still shows a running, queued or failed icon: {ICON.findall(body)}"
        assert not MENTION.findall(body), f"188.1 ({name}): the cancelled run's card mentions {MENTION.findall(body)}:\n{body[-700:]}"
        assert "rejected" not in body.lower() and "failed" not in re.sub(r"<img[^>]*>", "", body).lower(), \
            f"188.1 ({name}): the cancelled run's card reads as a failure, not a cancel:\n{body[:900]}"
        lines = [l for l in body.split(agent.STATS)[0].splitlines() if l.strip()]
        assert lines and lines[-1].startswith("**Next:**"), \
            f"188.1 ({name}): the cancelled run's card does not end with a Next line:\n{body[-600:]}"
    for name in ("rejected", "no-tools", "blocked"):
        r = runs[name]
        assert r.cancelled_step is None and r.agent_started() == (name != "no-tools"), f"188.1 ({name}): setup went wrong:\n{r.tail()}"
        cs = r.comments()
        records = [c for c in cs if c["versions"][-1].startswith("<!-- dokima-record -->")]
        assert len(records) == 1, f"188.1 ({name}): the run left {len(records)} records, expected one: {[c['versions'][-1][:150] for c in cs]}"
        for c in cs:
            body = visible(c["versions"][-1])
            assert not re.search(r"\bcancell?ed\b", body, re.I), f"188.1 ({name}): a run nobody cancelled says it was cancelled:\n{body[:900]}"


def test_the_owner_is_mentioned_on_a_real_rejection_and_not_on_a_cancel(record_property, runs):
    """When code rejects a hand-back the card mentions the owner; a run cancelled while its agent worked does not.

    A plan review whose hand-back code rejects must leave one card that says the hand-back was rejected and ends with
    a Next line mentioning @owner-person. The planner, plan reviewer and worker cancelled while they worked hand back
    nothing, which code would otherwise reject: their cards must neither say rejected nor mention anyone."""
    record_property("proves", "188.2")
    r = runs["rejected"]
    assert r.agent_started() and r.cancelled_step is None, f"188.2: setup: the rejected review did not run its agent:\n{r.tail()}"
    body = visible(only_comment(r, "188.2", "rejected")["versions"][-1])
    assert "rejected" in body.lower(), f"188.2: the card of a hand-back code rejected does not say so:\n{body[:900]}"
    nxt = [l for l in body.splitlines() if l.startswith("**Next:**")]
    assert nxt and f"@{OWNER}" in nxt[-1], f"188.2: the card of a rejected hand-back does not mention the owner on its Next line: {nxt}"
    for name in ("planner", "reviewer", "worker"):
        r = runs[name]
        cancelled(r, "188.2", name)
        body = visible(only_comment(r, "188.2", name)["versions"][-1])
        assert f"@{OWNER}" not in body and not MENTION.findall(body), \
            f"188.2 ({name}): a run cancelled while its agent worked mentions {MENTION.findall(body)}:\n{body[-700:]}"
        assert "rejected" not in body.lower(), f"188.2 ({name}): a run cancelled while its agent worked says rejected:\n{body[:900]}"


def test_nothing_starts_by_itself_after_a_cancel_or_a_failure(record_property, runs):
    """After a cancel or a failure no run starts by itself: no next stage, no re-run, until a command starts one.

    Every cancelled run (including one cancelled after its blocking review had passed code's check, which the river
    would otherwise send back to the planner), a review code rejected and a run whose tools failed to install must
    make no call that starts or re-runs a run, and each must still have been seen as cancelled or failed. Beside them,
    the same blocking review not cancelled must start exactly the planner, so the river itself still flows. That review
    is a fake of a one-story plan whose only criterion is 57.1: it must match every ask to 57.1 and its hand-back must
    pass code's check, or the run would stop on a rejection instead of reaching the river (#215)."""
    record_property("proves", "188.3")
    record_property("proves", "215.1")
    for name in CANCELLED:
        r = runs[name]
        cancelled(r, "188.3", name)
        assert start_calls(r) == [], f"188.3 ({name}): after a cancel the run started another run by itself: {start_calls(r)}"
    for name in CANCELLED:
        body = visible(only_comment(runs[name], "188.3", name)["versions"][-1])
        assert re.search(r"\bcancell?ed\b", body, re.I), f"188.3 ({name}): the run's card does not say it was cancelled:\n{body[:600]}"
    for name in ("rejected", "no-tools"):
        r = runs[name]
        assert r.failed, f"188.3 ({name}): setup: the run did not fail:\n{r.tail()}"
        assert start_calls(r) == [], f"188.3 ({name}): after a failure the run started another run by itself: {start_calls(r)}"
    ids = agent.plan_criteria(STORY, N)
    wrong = [a for a in BLOCK["asks"] if a.get("criterion") not in ids]
    assert not wrong, f"215.1: the fake blocking review matches asks to criteria its fake plan does not have ({ids}): {wrong}"
    r = runs["blocked"]
    recs = agent.records([{"author": {"login": agent.BOT}, "body": p["body"]} for p in r.posted()])
    assert [(x["role"], x["stage"], x["check"]["passed"]) for x in recs] == [("reviewer", "plan", True)], \
        f"215.1: code's check rejected the fake blocking review, so it never reached the river: {[x['check'] for x in recs]}"
    calls = start_calls(r)
    assert len(calls) == 1 and "client_payload[role]=planner" in calls[0], \
        f"188.3: a blocking plan review that nobody cancelled no longer starts the planner: {calls}\n{r.tail()}"


def test_a_cancelled_run_does_not_put_needs_you_on_the_board(record_property, runs):
    """A cancelled run leaves its card on the board without Needs you, since nothing waits for the owner.

    Reads where each run left its card for the board step (its column, then needs or none). Every cancelled run must
    say none; a run whose hand-back code rejected and one whose tools failed to install, which do stop for the owner,
    must still say needs."""
    record_property("proves", "188.4")
    for name in CANCELLED:
        r = runs[name]
        cancelled(r, "188.4", name)
        place = r.board()
        assert place.endswith(" none"), f"188.4 ({name}): a cancelled run left its card as {place!r}, expected no Needs you"
    for name in ("rejected", "no-tools"):
        place = runs[name].board()
        assert place.endswith(" needs"), f"188.4 ({name}): a run that stops for the owner left its card as {place!r}, expected Needs you"

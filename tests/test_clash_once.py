"""A clash with main is re-planned once, on autopilot only, then rebuilt (#369).

On 2026-10-09 PR #323 clashed with main, and every later merge sent issue #284 back to its planner again: the re-plan
passed review but nothing rebuilt the pull request, so the clash stayed and the next merge started the same round.
These tests hold the owner's rule: a clash starts the planner by itself only on autopilot; off autopilot the issue says
it needs a re-plan and waits for `/plan`; a clash already sent back and not rebuilt since (no worker record after the
newest clash record) is not sent back again; and an approved clash re-plan goes to the worker on autopilot, or stops
for the owner saying `/work` rebuilds the pull request off autopilot.

`dokima.uptodate.clash(repo, base, sha, pr, rest=..., files=..., owners=...)` is driven with the in-process fake
GitHub from test_clash.py, which also answers GET repos/o/r/issues/N with the issue's labels (autopilot is the issue's
own `autopilot` label) or GitHub's refusal. The river is `dokima.agent.next_step`; the card is `dokima.card.status`.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dokima import agent, card  # noqa: E402
import test_clash as tc  # noqa: E402
import test_start as ts  # noqa: E402

ISSUE, PR = 7, 70


def comment(login, body, t):
    """A comment as the river reads it from GitHub's issue view."""
    return {"author": {"login": login}, "body": body, "createdAt": t}


def clash_record(labels=("autopilot",), comments=None):
    """The clash record one merge leaves on issue #7, with the fake GitHub it ran on."""
    gh = tc.FakeGitHub(labels=labels, comments=comments)
    tc.clash(gh, tc.pr(PR, f"try/issue-{ISSUE}"))
    on7 = [b for n, b in gh.posted() if n == ISSUE]
    assert len(on7) == 1, f"369: the clash should post one record on #{ISSUE}, got {gh.posted()}"
    return on7[0], gh


def rest(body, t):
    """A bot comment as GitHub's REST API returns it, for the fake's history."""
    return tc.rest_comment(tc.BOT_REST, body, t)


def plan_round():
    """The bot's planner record and its passed plan review approving it, as REST comments."""
    approve = {**ts.APPROVE, "summary": "The plan keeps every promise.", "asks": []}
    return [rest(agent.render(ts.planner_record(ts.STORY)), "2026-10-08T13:00:00Z"),
            rest(agent.render(ts.review_record(approve)), "2026-10-08T13:10:00Z")]


# 369.1: a clash starts the planner by itself only on autopilot; off autopilot the issue says it needs a re-plan

def test_a_clash_starts_the_planner_only_on_autopilot(record_property):
    """A clash starts the planner only on autopilot; otherwise it asks you for `/plan`.

    Proves 369.1.
    Off autopilot (issue #7 carries no autopilot label), a clash on its PR #70 must post one record on #7 whose visible
    text says it "needs a re-plan", names `/plan` and mentions both code owners; no signal may start any stage; and the
    card must show Plan with Needs you. On autopilot, the same clash must send exactly one dokima-next signal for the
    planner on #7, mention no code owner, and the card must show Plan with nothing for the owner."""
    record_property("proves", "369.1")
    body, gh = clash_record(labels=())
    shown = tc.visible(body)
    assert gh.dispatches() == [], f"369.1: off autopilot the clash started a stage: {gh.dispatches()}"
    assert "needs a re-plan" in shown.lower(), f"369.1: off autopilot the clash record does not say the issue needs a re-plan:\n{shown}"
    assert "`/plan`" in shown, f"369.1: off autopilot the clash record does not tell the owner to say `/plan`:\n{shown}"
    for o in tc.OWNERS:
        assert f"@{o}" in shown, f"369.1: off autopilot the clash record does not mention the code owner @{o}:\n{shown}"
    items = [comment(agent.BOT, body, "2026-10-08T12:00:00Z")]
    found = {"recs": agent.records(items), "items": items, "pr": None, "check_runs": [], "owners": set(tc.OWNERS)}
    stage, todo = card.status({"number": ISSUE}, found)
    assert stage == "Plan" and todo, f"369.1: off autopilot the card after a clash should be in Plan with Needs you, got {(stage, todo)}"
    body, gh = clash_record(labels=("autopilot",))
    sent = [(e, p.get("role"), p.get("issue")) for e, p in gh.dispatches()]
    assert sent == [("dokima-next", "planner", str(ISSUE))], f"369.1: on autopilot the clash should start the planner once, got {sent}"
    shown = tc.visible(body)
    assert not any(f"@{o}" in shown for o in tc.OWNERS), f"369.1: on autopilot the clash record mentions the owner:\n{shown}"
    items = [comment(agent.BOT, body, "2026-10-08T12:00:00Z")]
    found = {"recs": agent.records(items), "items": items, "pr": None, "check_runs": [], "owners": set(tc.OWNERS)}
    got = card.status({"number": ISSUE}, found)
    assert got == ("Plan", None), f"369.1: on autopilot the card after a clash should be Plan with nothing for the owner, got {got}"


# 369.2: a clash sent back and not rebuilt since is not sent back again by the next merge

def test_a_clash_already_sent_back_is_not_sent_back_again(record_property):
    """A clash sent back and not rebuilt since is not sent back again.

    Proves 369.2.
    Three histories of issue #7, each ending in no worker record after its clash record: the clash on autopilot then
    the planner and its approved plan review; the clash on autopilot alone; and the clash off autopilot, waiting for
    `/plan`. A clash from the next merge must post nothing on #7 and start nothing. Once the worker's record follows
    the clash, the next clash must leave one new clash record on #7 and, on autopilot, start the planner once."""
    record_property("proves", "369.2")
    on, _ = clash_record(labels=("autopilot",))
    off, _ = clash_record(labels=())
    for case, history, labels in (("re-planned and approved", [rest(on, "2026-10-08T12:00:00Z")] + plan_round(), ("autopilot",)),
                                  ("planner still waiting", [rest(on, "2026-10-08T12:00:00Z")], ("autopilot",)),
                                  ("off autopilot, waiting for /plan", [rest(off, "2026-10-08T12:00:00Z")], ())):
        gh = tc.FakeGitHub(merged=(301,), comments={ISSUE: history}, labels=labels)
        tc.clash(gh, tc.pr(PR, f"try/issue-{ISSUE}"), sha="d00d" * 10)
        again = [b for n, b in gh.posted() if n == ISSUE]
        assert again == [], f"369.2 ({case}): the next merge sent the clash back again with a new comment on #{ISSUE}"
        assert gh.dispatches() == [], f"369.2 ({case}): the next merge started a stage again: {gh.dispatches()}"
    history = [rest(on, "2026-10-08T12:00:00Z")] + plan_round() + [rest(agent.render(tc.WORKER), "2026-10-08T14:00:00Z")]
    gh = tc.FakeGitHub(merged=(302,), comments={ISSUE: history})
    tc.clash(gh, tc.pr(PR, f"try/issue-{ISSUE}"), sha="beef" * 10)
    posted = [b for n, b in gh.posted() if n == ISSUE]
    assert len(posted) == 1 and [r.get("role") for r in agent.records([comment(agent.BOT, posted[0], "t")])] == ["updater"], \
        f"369.2: after the worker rebuilt, a new clash should leave one clash record on #{ISSUE}, got {gh.posted()}"
    roles = [p.get("role") for _, p in gh.dispatches()]
    assert roles == ["planner"], f"369.2: after the worker rebuilt, a new clash on autopilot should start the planner once, got {roles}"


# 369.3: an approved clash re-plan goes to the worker on autopilot, or stops for the owner saying so

def river_after_approval(clash_first, owner_plan, on):
    """The river's next step after a plan review approves a re-plan of issue #7.

    The history: the first plan, its approval, the owner's `/work`, the worker, then (when `clash_first`) a clash
    record, (when `owner_plan`) the owner's `/plan`, and the re-plan; `on` is what autopilot reads."""
    approve = {**ts.APPROVE, "summary": "The plan keeps every promise.", "asks": []}
    owner = tc.OWNERS[0]
    items = [comment(agent.BOT, agent.render(ts.planner_record(ts.STORY)), "2026-10-08T09:00:00Z"),
             comment(agent.BOT, agent.render(ts.review_record(approve)), "2026-10-08T09:10:00Z"),
             comment(owner, "/work", "2026-10-08T09:20:00Z"),
             comment(agent.BOT, agent.render(tc.WORKER), "2026-10-08T10:00:00Z")]
    if clash_first:
        body, _ = clash_record(labels=("autopilot",) if on else ())
        items.append(comment(agent.BOT, body, "2026-10-08T12:00:00Z"))
    if owner_plan:
        items.append(comment(owner, "/plan", "2026-10-08T12:30:00Z"))
    items.append(comment(agent.BOT, agent.render(ts.planner_record(ts.STORY)), "2026-10-08T13:00:00Z"))
    rec = ts.review_record(approve)
    return agent.next_step(items, rec, set(tc.OWNERS), autopilot=lambda: on, body="", number=str(ISSUE))


def test_an_approved_clash_re_plan_rebuilds_on_autopilot_or_stops_saying_so(record_property):
    """An approved clash re-plan starts the worker on autopilot, or asks you for `/work`.

    Proves 369.3.
    On autopilot the step after the approving plan review must start the worker. Off autopilot, after the owner's
    `/plan`, it must stop for the owner, and its words must name the clash with main and `/work`. A plain approved
    re-plan with no clash must still stop with today's words, so only a clash re-plan says so."""
    record_property("proves", "369.3")
    step = river_after_approval(clash_first=True, owner_plan=False, on=True)
    assert step[:2] == ("start", "worker"), f"369.3: on autopilot an approved clash re-plan should start the worker, got {step}"
    step = river_after_approval(clash_first=True, owner_plan=True, on=False)
    assert step[0] == "stop", f"369.3: off autopilot an approved clash re-plan should stop for the owner, got {step}"
    assert "clash" in step[1].lower() and "`/work`" in step[1], \
        f"369.3: off autopilot the stop does not say the pull request clashes with main and `/work` rebuilds it: {step[1]!r}"
    plain = river_after_approval(clash_first=False, owner_plan=True, on=False)
    assert plain == ("stop", "The plan is approved. Say `/work` to build it, or `/plan` with changes."), \
        f"369.3: an approved re-plan with no clash should keep today's words, got {plain}"


# 369.4: `/autopilot stop` said on a pull request takes the label off that pull request (in test_autopilot_stop_pr.py)

# 369.5: when GitHub cannot say whether the issue is on autopilot, the clash starts nothing and says why

def test_when_autopilot_cannot_be_read_a_clash_starts_nothing_and_says_why(record_property):
    """When autopilot cannot be read, a clash starts nothing and says why.

    Proves 369.5.
    GitHub refuses to give issue #7. A clash must still post one record on #7 whose visible text says autopilot could
    not be read and mentions both code owners, and no signal may start any stage."""
    record_property("proves", "369.5")
    gh = tc.FakeGitHub(unreadable=True)
    try:
        tc.clash(gh, tc.pr(PR, f"try/issue-{ISSUE}"))
    except subprocess.CalledProcessError:
        pass
    assert gh.dispatches() == [], f"369.5: with autopilot unreadable the clash started a stage: {gh.dispatches()}"
    on7 = [b for n, b in gh.posted() if n == ISSUE]
    assert len(on7) == 1, f"369.5: with autopilot unreadable the clash should still say so on #{ISSUE}, got {gh.posted()}"
    shown = tc.visible(on7[0])
    assert re.search(r"autopilot could not be read", shown, re.I), f"369.5: the record does not say autopilot could not be read:\n{shown}"
    for o in tc.OWNERS:
        assert f"@{o}" in shown, f"369.5: the record does not mention the code owner @{o}:\n{shown}"


def test_main_moving_during_plan_review_re_plans_before_building(record_property):
    """When main clashes while a plan is in review, the approval re-plans instead of building the old plan.

    Proves 812.river. The history: the plan, then a clash record (main moved after the plan was written), then the
    plan review approves that old plan. On autopilot the next step must start the planner, never the worker or a split.
    Once the re-plan exists (planner record after the clash), its approval goes to the worker as before (369.3)."""
    record_property("proves", "812.river")
    approve = {**ts.APPROVE, "summary": "The plan keeps every promise.", "asks": []}
    body, _ = clash_record(labels=("autopilot",))
    items = [comment(agent.BOT, agent.render(ts.planner_record(ts.STORY)), "2026-10-08T09:00:00Z"),
             comment(agent.BOT, body, "2026-10-08T09:05:00Z")]
    step = agent.next_step(items, ts.review_record(approve), set(tc.OWNERS), autopilot=lambda: True, body="", number=str(ISSUE))
    assert step[:2] == ("start", "planner"), f"812: an approval of a plan older than the clash should re-plan, got {step}"
    items.append(comment(agent.BOT, agent.render(ts.planner_record(ts.STORY)), "2026-10-08T09:30:00Z"))
    step = agent.next_step(items, ts.review_record(approve), set(tc.OWNERS), autopilot=lambda: True, body="", number=str(ISSUE))
    assert step[:2] == ("start", "worker"), f"812: the approved re-plan should go to the worker, got {step}"

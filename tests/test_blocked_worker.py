"""On autopilot, a blocked issue plans only after its blockers merge (#353, which reverses #253).

Before #353 a blocked issue on autopilot planned early, and its approved plan waited for its blockers with the bot's
line `Autopilot: plan approved, waiting for #A to close`; when they closed, its worker built that old plan, with
`Autopilot: blockers closed, starting work`. A plan written while its blockers are still open goes stale when they
merge, so now nothing waits with an approved plan. Each moment runs the real code against a fake GitHub:

- The plan review approves. `python3 -m dokima.agent next N OUT` (the step of agent.yml that decides what follows a
  run) runs on the review's record, on the fake GitHub of test_plan_links_recorded.py (issue #252 there). An issue on
  autopilot that GitHub still has blocked by an open issue builds nothing: no worker starts, no line stands in for
  `/work`, and the card's Next line names the open issues it waits for and says it plans again, mentioning no one.
- An issue closes. autopilot.yml runs the way GitHub runs it, on the machine of test_autopilot_close.py (issue #57
  there). When the last open blocker of such an issue closes, autopilot starts a fresh planner run once, with
  `Autopilot: blockers merged, starting plan`, and never the worker of the old plan.
- A command the owner types by hand runs as today, through commands.yml, and a later close never overrides it.

Where GitHub cannot list an issue's blockers, the fake answers that read with "HTTP 502: Server Error" and nothing
may start, with GitHub's reason on the issue.
"""
import json
import os
import re

import test_autopilot_close as tc
import test_autopilot_river as ar
import test_plan_links_recorded as pl
import test_start as ts
from dokima import agent

OLD_WAIT = "Autopilot: plan approved, waiting for"
OLD_GO = "Autopilot: blockers closed, starting work"
LINE = "Autopilot: blockers merged, starting plan"
LABEL = "autopilot"
ERROR = "HTTP 502: Server Error (blocked_by)"


# The plan review approves: `agent next` on #252 ---------------------------------------------------------------------

def hub(tmp, closed=(), autopilot=True, deps=None, fail_read=False):
    """The fake GitHub of test_plan_links_recorded, with these issues closed.

    With fail_read, every read of #252's blocker list fails."""
    h = pl.Hub(tmp, deps=deps, autopilot=autopilot)
    s = h.load()
    for n in closed:
        s["issues"][str(n)]["state"] = "closed"
    s["fail_read"] = [pl.N] if fail_read else []
    h.save()
    src = 'if method == "GET":\n            out([obj(b) for b in deps(n)])'
    fake = pl.FAKE_GH.replace(src, 'if method == "GET":\n            if n in S.get("fail_read", []):\n'
                                   f'                fail({ERROR!r})\n            out([obj(b) for b in deps(n)])', 1)
    assert fake != pl.FAKE_GH, "test setup: could not teach the fake GitHub to fail a read of the blockers"
    gh = os.path.join(h.dir, "bin", "gh")
    open(gh, "w").write(f"#!{pl.sys.executable}\nBOT_LOGIN = {pl.BOT!r}\nOWNER_LOGIN = {pl.OWNER!r}\n" + fake)
    return h


def new_comments(h):
    """The comments the commands wrote on #252, apart from records.

    The run's own record is posted later, by the workflow."""
    return [c["body"].strip() for c in h.comments(pl.N) if agent.MARK not in c["body"]]


def next_line(comment):
    """The card's Next line."""
    return next((l for l in comment.splitlines() if l.startswith("**Next:**")), "")


def approve_on(h, links, crit, case):
    """The river runs on a plan with these links, then on its approving review.

    Asserts the plan goes to the plan review as usual; returns what the river said on the approval."""
    rec = pl.plan(links)
    step, _, _ = h.next(rec)
    assert step == "start reviewer plan", \
        f"{crit} ({case}): the plan of a blocked issue did not go to the plan review as usual, the river said {step!r}"
    h.post(rec)
    return h.next(pl.review())


def old_lines(said):
    """The lines #253 posted for a waiting worker, among these comments."""
    return [c for c in said if c.startswith(OLD_WAIT) or OLD_GO in c]


def test_an_approved_plan_with_an_open_blocker_builds_nothing_and_says_what_it_waits_for(tmp_path, record_property):
    """A plan approved while a blocker is open builds nothing; its card names the blockers.

    Proves 353.2.
    #252 is on autopilot. Its plan says blocked by #301 (open) and #302 (closed), and GitHub already has #252 blocked
    by #304 (open) by hand. The plan goes to its review as usual; when the review approves, no stage starts, no line
    stands in for `/work`, neither of #253's lines (`Autopilot: plan approved, waiting for ...`, `Autopilot: blockers
    closed, starting work`) is posted, and the card's Next line names #301 and #304 but not #302, says the issue plans
    again (the word "plan"), never says a worker starts, and mentions no one. The run places the card in Plan without
    Needs you. Beside it: with every blocker closed the worker starts as usual, and off autopilot the blocked plan
    stops for the owner as before, with no line."""
    record_property("proves", "353.2")
    h = hub(tmp_path / "blocked", closed=[302], deps={pl.N: [304]})
    step, comment, out = approve_on(h, pl.links([301, 302]), "353.2", "blocked")
    assert not step.startswith("start"), f"353.2: a plan approved with open blockers started {step!r}"
    assert not os.path.exists(os.path.join(out, "autopilot.md")), "353.2: the worker's Autopilot line was still written"
    assert h.writes("dispatch") == [], f"353.2: a stage was signalled: {h.writes('dispatch')}"
    assert old_lines(new_comments(h)) == [], f"353.2: #253's waiting-worker lines were posted: {new_comments(h)}"
    nxt = next_line(comment)
    assert nxt, f"353.2: the card has no Next line: {comment[-600:]!r}"
    assert "#301" in nxt and "#304" in nxt, f"353.2: the Next line does not name both open blockers #301 and #304: {nxt!r}"
    assert "#302" not in nxt, f"353.2: the Next line names #302, which is already closed: {nxt!r}"
    assert "@" not in nxt, f"353.2: the Next line mentions someone while the issue only waits on its blockers: {nxt!r}"
    assert "worker" not in nxt.lower(), f"353.2: the Next line still says a worker will build the old plan: {nxt!r}"
    assert "plan" in nxt.lower(), f"353.2: the Next line does not say the issue plans again when they close: {nxt!r}"
    assert open(os.path.join(out, "board.txt")).read().split() == ["Plan", "none"], \
        f"353.2: the run placed the waiting card at {open(os.path.join(out, 'board.txt')).read().strip()!r}, not in Plan without Needs you"

    h = hub(tmp_path / "all-closed", closed=[301, 302])
    step, comment, out = approve_on(h, pl.links([301, 302]), "353.2", "all closed")
    assert step == "start worker", f"353.2 (all closed): with every blocker closed the worker should start, not {step!r}"
    assert os.path.exists(os.path.join(out, "autopilot.md")), "353.2 (all closed): the Autopilot line is missing"

    h = hub(tmp_path / "off", autopilot=False)
    step, comment, out = approve_on(h, pl.links([301]), "353.2", "off autopilot")
    assert step == "stop" and f"@{pl.OWNER}" in next_line(comment), \
        f"353.2 (off autopilot): the approval should stop for the owner: {step!r} {next_line(comment)!r}"
    assert new_comments(h) == [], f"353.2 (off autopilot): a line was written: {new_comments(h)}"


def test_when_github_cannot_list_the_blockers_the_worker_waits_and_the_issue_says_why(tmp_path, record_property):
    """When GitHub cannot list the blockers, no worker starts and the card says why.

    #252 is on autopilot with a plan that has no links, and every read of #252's blocked-by list fails with
    "HTTP 502: Server Error (blocked_by)". When the review approves, no stage starts, no Autopilot line is written,
    and the record's comment, which the workflow posts on the issue, quotes GitHub's error. Beside it, the same plan
    with the list readable starts the worker. Proves 253.4."""
    record_property("proves", "253.4")
    h = hub(tmp_path / "readable")
    step, _, _ = approve_on(h, pl.links(), "253.4", "readable")
    assert step == "start worker", f"253.4 (readable): with nothing blocking it the worker should start, not {step!r}"

    h = hub(tmp_path / "unreadable", fail_read=True)
    step, comment, out = approve_on(h, pl.links(), "253.4", "unreadable")
    assert not step.startswith("start"), f"253.4: the worker started though GitHub could not list the blockers: {step!r}"
    assert not os.path.exists(os.path.join(out, "autopilot.md")), "253.4: the worker's Autopilot line was still written"
    assert h.writes("dispatch") == [], f"253.4: a stage was signalled: {h.writes('dispatch')}"
    assert ERROR in comment, f"253.4: the issue does not say why the worker did not start (GitHub's error): {comment[-800:]!r}"


# An issue closes: autopilot.yml on #57 ------------------------------------------------------------------------------

def bot_line(text, t):
    """A comment the bot posted on #57, as GitHub returns it."""
    return {"author": {"login": agent.BOT}, "body": text, "createdAt": t}


APPROVED = ts.STORY_PLANNED + [ts.record_comment(ts.review_record(ar.APPROVE), "2026-10-07T10:20:00Z")]
WORKER = {"role": "worker", "stage": None, "run_id": "3", "run": "https://github.com/o/r/actions/runs/3",
          "models": ["claude-opus-5-5"], "handback": {"summary": "Built it."}, "check": {"passed": True, "problems": []}}


def repo(tmp, history, closed=(102,), on=True, fail_read=False):
    """#57, blocked by #101 and #102, with this history and on autopilot unless told.

    With fail_read, every read of #57's blocker list fails."""
    m = tc.Repo(tmp, {}, {57: [LABEL]} if on else {}, deps={57: [101, 102]}, closed=closed, history=history)
    if fail_read:
        anchor = 'm_dep = re.fullmatch(r"repos/o/r/issues/(\\d+)/dependencies/blocked_by", API or "")\nif m_dep:\n    n = m_dep.group(1)\n'
        fake = tc.fake_gh()
        patched = fake.replace(anchor, anchor + '    if method() == "GET" and n in opts.get("fail_deps", []):\n'
                                                f'        sys.stderr.write({ERROR!r} + "\\n")\n        sys.exit(1)\n', 1)
        assert patched != fake, "test setup: could not teach the fake GitHub to fail a read of the blockers"
        open(f"{m.tmp}/bin/gh", "w").write(patched)
        json.dump({"running_runs": [], "fail_deps": ["57"]}, open(f"{m.tmp}/gh/options.json", "w"))
    return m


def workers(m, crit):
    """How many times #57's worker was started by a signal that starts agent.yml."""
    return sum(1 for s in m.signals() if s["event_type"] == "dokima-next" and s["payload"].get("role") == "worker"
               and s["payload"].get("issue") == "57")


def assert_plans_again_once(m, crit, case):
    """#57's planner started once, with one `Autopilot: blockers merged, starting plan`, and no worker."""
    assert not m.failed, f"{crit} ({case}): a workflow failed: {m.failures}\n{m.tail()}"
    assert workers(m, crit) == 0, f"{crit} ({case}): #57's worker started on its old plan, though only a fresh plan may follow"
    assert not any(OLD_GO in b for b in m.new_comments(57)), f"{crit} ({case}): #57 got {OLD_GO!r}: {m.new_comments(57)}"
    started = m.planners_started(crit)
    assert started.get(57) == 1, f"{crit} ({case}): #57's planner started {started.get(57, 0)} times, expected once\n{m.tail()}"
    assert m.autopilot_lines(57) == 1, \
        f"{crit} ({case}): #57 should get exactly one {LINE!r} comment: {m.new_comments(57)}"


def assert_starts_nothing(m, crit, case):
    """Neither #57's planner nor its worker started, and no line starts either."""
    assert not m.failed, f"{crit} ({case}): a workflow failed: {m.failures}\n{m.tail()}"
    assert workers(m, crit) == 0, f"{crit} ({case}): #57's worker started, though nothing may start"
    assert 57 not in m.planners_started(crit), f"{crit} ({case}): #57's planner started, though nothing may start"
    assert m.autopilot_lines(57) == 0 and not any(OLD_GO in b for b in m.new_comments(57)), \
        f"{crit} ({case}): #57 got a line that starts a stage, though nothing may start: {m.new_comments(57)}"


def test_the_last_blocker_closing_starts_a_fresh_plan_never_the_old_plans_worker(tmp_path, record_property):
    """The last blocker closing plans the issue again once, never building the old plan.

    Proves 353.3.
    #57 is on autopilot, blocked by #101 and #102 (#102 closed), and its plan was approved while #101 was open, so
    nothing was built. Closing #101 starts #57's planner exactly once, by Dokima's own signal, with exactly one comment
    reading `Autopilot: blockers merged, starting plan`, and starts no worker. Another close right after starts
    nothing more. With #102 still open, or off autopilot, closing #101 starts nothing. Nor does it once something
    already started after the approval: the planner's run card, a newer plan under review, the line above from an
    earlier close, a worker record or the worker's Autopilot line."""
    record_property("proves", "353.3")
    m = repo(tmp_path / "last", APPROVED)
    m.close(101)
    assert_plans_again_once(m, "353.3", "last blocker closed")
    m.close(110)
    assert_plans_again_once(m, "353.3", "a later close")

    for case, kw in (("one still open", dict(closed=())), ("off autopilot", dict(on=False))):
        m = repo(tmp_path / case.replace(" ", "-"), APPROVED, **kw)
        m.close(101)
        assert_starts_nothing(m, "353.3", case)

    t = "2026-10-07T10:30:00Z"
    replan = ts.record_comment(ts.planner_record(ts.STORY), t)
    for case, extra in (("planner's run card up", bot_line(agent.live_card("planner", "", "handoff"), t)),
                        ("newer plan under review", replan),
                        ("already started by a close", bot_line(LINE, t)),
                        ("worker record", ts.record_comment(WORKER, t)),
                        ("worker started by autopilot", bot_line("Autopilot: plan approved, starting work", t))):
        m = repo(tmp_path / case.replace(" ", "-").replace("'", ""), APPROVED + [extra])
        m.close(101)
        assert_starts_nothing(m, "353.3", case)


def test_a_command_the_owner_types_while_it_waits_runs_and_no_close_overrides_it(tmp_path, record_property):
    """While it waits, the owner's own `/plan` or `/work` runs and no close overrides it.

    Proves 353.3.
    #57 is on autopilot, its plan approved while #101 was still open. The code owner's `/plan` and `/work` on it each
    start their stage through the listener as today. Once the owner has said either one after the approval, closing
    #101, its last open blocker, starts neither #57's planner nor its worker."""
    record_property("proves", "353.3")
    for said in ("/plan", "/work"):
        m = repo(tmp_path / f"listen-{said[1:]}", APPROVED, closed=())
        called = m.listen(said)
        assert not m.failed and called, f"353.3: the owner's {said} on the waiting #57 did not start its stage:\n{m.tail()}"
        m = repo(tmp_path / f"close-{said[1:]}", APPROVED + [ts.owner_comment(said, "2026-10-07T10:30:00Z")])
        m.close(101)
        assert_starts_nothing(m, "353.3", f"the owner said {said}")


def test_a_close_that_cannot_list_the_blockers_starts_nothing_and_says_why(tmp_path, record_property):
    """When a close cannot list the blockers, nothing starts and the issue says GitHub's reason.

    Proves 353.5.
    #57 is on autopilot, its plan approved while #101 was open, blocked by #101 and #102 (#102 closed), and every read
    of #57's blocked-by list fails with "HTTP 502: Server Error (blocked_by)". Closing #101 starts neither #57's
    planner nor its worker and leaves a new comment on #57 quoting GitHub's error. Beside it, the same close with the
    list readable plans #57 again once."""
    record_property("proves", "353.5")
    m = repo(tmp_path / "readable", APPROVED)
    m.close(101)
    assert_plans_again_once(m, "353.5", "readable")

    m = repo(tmp_path / "unreadable", APPROVED, fail_read=True)
    m.close(101)
    assert workers(m, "353.5") == 0, "353.5: #57's worker started though GitHub could not list its blockers"
    assert 57 not in m.planners_started("353.5"), "353.5: #57's planner started though GitHub could not list its blockers"
    assert any(ERROR in b for b in m.new_comments(57)), \
        f"353.5: #57 does not say why nothing started (GitHub's error): {m.new_comments(57)}\n{m.tail()}"


def test_a_blocked_issue_on_autopilot_never_starts_its_planner_by_itself(tmp_path, record_property):
    """On autopilot, an issue with an open blocker never starts its planner by itself.

    Proves 353.1.
    Three moments, each run the way GitHub runs it. Switch-on: the code owner's `/autopilot start` on #57, blocked by
    #110 (open), starts no planner and posts no Autopilot line; beside it, with #110 closed, #57's planner starts once.
    A split filed: `/work` on #57 on autopilot files stories #900 and #901, #901 blocked by #900; #900's planner
    starts and #901's does not. A close: #57, blocked by #101 and #102 (both open), once with no plan and once with a
    plan approved while blocked; closing #101 leaves #102 open and starts nothing, no planner and no worker; closing
    #102 then starts #57's planner once and never its worker."""
    record_property("proves", "353.1")
    switch = "Autopilot: switched on, starting plan"
    for case, closed, want in (("blocked", (), {}), ("blocker closed", (110,), {57: 1})):
        m = tc.Repo(tmp_path / f"switch-{case.replace(' ', '-')}", {}, {}, deps={57: [110]}, closed=closed)
        m.listen("/autopilot start")
        assert not m.failed, f"353.1 (switch-on, {case}): the listener failed on /autopilot start:\n{m.tail()}"
        started = m.planners_started("353.1")
        assert started == want, f"353.1 (switch-on, {case}): /autopilot start started planners {started}, expected {want}"
        said = sum(1 for b in m.new_comments(57) if b.strip() == switch)
        assert said == sum(want.values()), \
            f"353.1 (switch-on, {case}): #57 got {said} {switch!r} lines, expected {sum(want.values())}: {m.new_comments(57)}"

    m = tc.Repo(tmp_path / "split", {}, {57: [LABEL]}, history=ts.SPLIT_APPROVED)
    m.listen("/work")
    assert not m.failed, f"353.1 (split filed): the listener failed on /work:\n{m.tail()}"
    assert json.load(open(f"{m.tmp}/gh/tree.json")).get("57") == [900, 901], \
        f"353.1 (split filed): /work did not file the two stories as #900 and #901:\n{m.tail()}"
    started = m.planners_started("353.1")
    assert started == {900: 1}, f"353.1 (split filed): planners started {started}; only #900, which waits on nothing, may start"
    assert m.autopilot_lines(901) == 0, f"353.1 (split filed): #901, blocked by #900, got an Autopilot line: {m.new_comments(901)}"

    for case, history in (("no plan", None), ("plan approved while blocked", APPROVED)):
        m = repo(tmp_path / f"close-{case.replace(' ', '-')}", history, closed=())
        m.close(101)
        assert_starts_nothing(m, "353.1", f"{case}, #102 still open")
        m.close(102)
        assert_plans_again_once(m, "353.1", f"{case}, last blocker closed")


# The code and AGENTS.md ---------------------------------------------------------------------------------------------

def test_agents_md_says_a_blocked_issue_plans_only_after_its_blockers_merge(record_property):
    """AGENTS.md says a blocked issue plans only after its blockers merge, with no waiting worker.

    Proves 353.4.
    One paragraph of AGENTS.md's The flow section must say, word for word, "a blocked issue plans only after its
    blockers merge", "nothing is built" and "a fresh planner", and name `Autopilot: blockers merged, starting plan`.
    Nowhere may AGENTS.md still say "a blocked issue still plans", "its worker waits until every blocker closes",
    `Autopilot: plan approved, waiting for`, `Autopilot: blockers closed, starting work` or #343's "also while it
    waits on a blocker"."""
    record_property("proves", "353.4")
    text = open(os.path.join(ts.ROOT, "AGENTS.md")).read()
    sections = {m.group(1).strip(): m.group(2) for m in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M)}
    flow = next((v for k, v in sections.items() if k.startswith("The flow")), "")
    assert flow, "353.4: AGENTS.md has no The flow section"
    want = ("a blocked issue plans only after its blockers merge", "nothing is built", "a fresh planner", f"`{LINE}`")
    best = max(flow.split("\n\n"), key=lambda p: sum(w in p for w in want))
    missing = [w for w in want if w not in best]
    assert not missing, f"353.4: no paragraph of AGENTS.md's The flow says the new rule; the closest misses {missing}"
    stale = [w for w in ("a blocked issue still plans", "its worker waits until every blocker closes", OLD_WAIT, OLD_GO,
                         "also while it waits on a blocker") if w in text]
    assert not stale, f"353.4: AGENTS.md still describes the waiting worker of #253 or #343's rule for it: {stale}"

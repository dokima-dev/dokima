"""Every 15 minutes, any card that does not match its issue's state is redrawn (#347).

The scheduled run of card.yml used to redraw only the cards whose blocked-by links changed, so a card whose redraw was
missed (a dropped event, a merge before the PR card was written) stayed wrong for good. Now the sweep also redraws
every issue card and PR card that does not show its issue's state now, looking only at the issues and pull requests
GitHub says were updated since the last sweep that succeeded, so it stays cheap on a large repo. When GitHub cannot
say what changed, or no sweep has succeeded yet, it rechecks every card instead of none.

These tests reuse the player and fake GitHub of tests/card_player.py (lifted from #332's tests on branch
try/issue-332, whose sweep tests these adapt): card.yml is played the way GitHub runs it for the 15-minute schedule,
running the real `python3 dokima/card.py` against the fake GitHub. The fake is extended here with two things GitHub
has and the sweep needs:
- `gh api repos/o/r/actions/workflows/card.yml/runs` (and the repo-wide `repos/o/r/actions/runs`) lists the runs
  of card.yml the test recorded (newest first), filtered by the `event`, `status` and `branch` query parameters as
  GitHub filters them (`status` matches a run's status or its conclusion); it can be told to refuse with HTTP 502.
  Other workflows' runs are answered by the player's fake as before (none).
- `gh api repos/o/r/issues?since=T` lists only the issues and pull requests whose updated_at is T or later.
Every call the card code makes is logged in calls.jsonl, which is how a test sees what the sweep looked at.

The fixtures: issue #246 with PR #260 and issue #312 with PR #314, each fully planned, built and approved with every
check passed, and every card stale (an old Review card). All are last updated at 01:00 on 2026-10-09, before the
sweeps the tests record; a card the code writes updates its issue or PR at 12:00 or later.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from card_player import (FAKE_GH, STALE_CARD, Hub, card_of, issue_comment, must_redraw, schedule,  # noqa: E402
                         stage_of, triggers, listed, without_issue_link, workflow)

DEFS_AT = 'if a[:2] == ["issue", "view"]:\n'
CALL_AT = '    method = (flag("-X", "--method") or ("POST" if f and route != "graphql" else "GET")).upper()\n'
SWEEP_DEFS = r'''
from urllib.parse import unquote


def sweep_calls(route, params, method):
    """The workflow runs list and the issues list with `since`, as GitHub answers them."""
    if method != "GET":
        return
    params = {k: unquote(v) for k, v in params.items()}
    m = re.fullmatch(r"repos/o/r/actions/(?:workflows/([^/]+)/)?runs", route)
    if m and m.group(1) in (None, "card.yml"):
        if S.get("runs_refused"):
            fail(f"HTTP 502: Server Error (https://api.github.com/{route})")
        runs = [r for r in S.get("runs", {}).get("card.yml", [])
                if params.get("event") in (None, r["event"]) and params.get("branch") in (None, r["head_branch"])
                and params.get("status") in (None, r["status"], r["conclusion"])]
        runs = sorted(runs, key=lambda r: r["run_started_at"], reverse=True)
        per = int(params.get("per_page") or 30)
        out({"total_count": len(runs), "workflow_runs": runs[:per]})
        sys.exit(0)
    if route == "repos/o/r/issues" and params.get("since"):
        st = params.get("state", "open")
        nums = sorted({int(k) for k in S["issues"]} | {int(k) for k in S["prs"]})
        found = [issue_rest(n) for n in nums]
        out([i for i in found if (st == "all" or i["state"] == st) and i["updated_at"] >= params["since"]])
        sys.exit(0)
'''


class SweepHub(Hub):
    """The player's fake GitHub, plus workflow runs and the issues list's `since`."""

    def __init__(self, tmp):
        super().__init__(tmp)
        assert FAKE_GH.count(DEFS_AT) == 1 and FAKE_GH.count(CALL_AT) == 1, \
            "test setup: the fake GitHub of tests/card_player.py changed shape"
        fake = FAKE_GH.replace(DEFS_AT, SWEEP_DEFS + DEFS_AT).replace(
            CALL_AT, CALL_AT + "    sweep_calls(route, params, method)\n")
        gh = os.path.join(self.dir, "bin", "gh")
        head = open(gh).read().split(FAKE_GH, 1)[0]
        open(gh, "w").write(head + fake)

    def last_sweep(self, at, conclusion="success", event="schedule", ended=None):
        """Record a finished run of card.yml started at `at`, as GitHub lists it.

        It ended at `ended` when given, else at `at`."""
        s = self.load()
        runs = s.setdefault("runs", {}).setdefault("card.yml", [])
        runs.append({"id": 1000 + len(runs), "name": "card", "path": ".github/workflows/card.yml", "event": event,
                     "status": "completed", "conclusion": conclusion, "head_branch": "main",
                     "run_started_at": at, "created_at": at, "updated_at": ended or at,
                     "html_url": f"https://github.com/o/r/actions/runs/{1000 + len(runs)}"})
        self.save()

    def refuse_runs(self):
        """GitHub refuses to list card.yml's runs (and the repo's runs) with HTTP 502."""
        s = self.load()
        s["runs_refused"] = True
        self.save()

    def touch(self, kind, n, at):
        """Mark issue or pr n as last updated at `at`, as any change does."""
        s = self.load()
        s["issues" if kind == "issue" else "prs"][str(n)]["updated_at"] = at
        self.save()

    def clear_calls(self):
        """Forget the GitHub calls so far."""
        open(os.path.join(self.dir, "calls.jsonl"), "w").close()

    def calls(self):
        """Every GitHub call made since the calls were last cleared, as argument lists."""
        path = os.path.join(self.dir, "calls.jsonl")
        return [json.loads(line) for line in open(path)] if os.path.exists(path) else []


def stale(hub, n=None, p=None):
    """True when issue n's or PR p's card is still the old one, or missing."""
    text = hub.issue_body(n) if n is not None else hub.pr_body(p)
    return card_of(text) in (None, card_of(STALE_CARD))


def looked_at(calls, n):
    """The calls that read or wrote issue or PR n, besides its blocked-by links."""
    word = re.compile(rf"(?<![\d.]){n}(?!\d)|issue-{n}\b")
    return [c for c in calls if any(word.search(str(x)) for x in c)
            and not any(re.search(rf"issues/{n}/dependencies/", str(x)) for x in c)]


def every_minutes():
    """The longest gap in minutes between two scheduled runs of card.yml, or None."""
    best = None
    for cron in [c.get("cron") for c in listed(triggers(workflow()).get("schedule")) if isinstance(c, dict)]:
        f = (cron or "").split()
        if len(f) == 5 and f[1:] == ["*"] * 4:
            mins = set()
            for part in f[0].split(","):
                rng, _, step = part.partition("/")
                lo, hi = (0, 59) if rng == "*" else (int(rng.split("-")[0]),
                                                     int(rng.split("-")[-1]) if "-" in rng else (59 if step else int(rng)))
                mins |= set(range(lo, hi + 1, int(step) if step else 1))
            ms = sorted(mins)
            gap = max((ms[(i + 1) % len(ms)] - ms[i]) % 60 or 60 for i in range(len(ms)))
            best = gap if best is None else min(best, gap)
    return best


def stale_repo(tmp):
    """A fake GitHub whose last sweep succeeded at 05:00, with three stale issues since.

    #246 is closed with PR #260 merged at 09:00, both cards still the old open card; PR #314 was updated at 06:00
    and holds no card, while its issue #312 was not updated since; #320 was updated at 06:00 and has a plan its
    card does not show yet."""
    hub = SweepHub(tmp)
    hub.merge(246, 260)
    hub.no_pr_card(314, 312)
    hub.state = hub.load()
    hub.add_issue(320)
    hub.state["issues"]["320"]["comments"] = hub.state["issues"]["320"]["comments"][:1]
    hub.save()
    hub.touch("pr", 314, "2026-10-09T06:00:00Z")
    hub.touch("issue", 320, "2026-10-09T06:00:00Z")
    hub.last_sweep("2026-10-09T05:00:00Z")
    return hub


# 347.1 -----------------------------------------------------------------------------------------------------------

def test_the_sweep_redraws_every_stale_card_updated_since_the_last_sweep_open_or_closed(tmp_path, record_property):
    """Every 15 minutes the sweep redraws every stale card, open or closed.

    card.yml's schedule fires at least every 15 minutes, every hour. The last sweep succeeded at 05:00; since then
    #246 closed with PR #260 merged (both cards still the old open card), PR #314 was updated and has no card, and
    #320 was updated with a plan its card does not show. After one scheduled run, #246's and #260's cards say Merged,
    #312's card is redrawn and PR #314 shows the same card, and #320's card shows its plan. A person's comment on
    each issue afterwards changes no card: the sweep left each one as GitHub's state draws it. Proves 347.1."""
    record_property("proves", "347.1")
    gap = every_minutes()
    assert gap is not None and gap <= 15, f"347.1: card.yml's schedule leaves {gap} minutes between sweeps, not 15 or less"
    hub = stale_repo(tmp_path)
    must_redraw(hub, schedule(), "347.1")
    assert stage_of(hub.issue_body(246)) == "Merged" and stage_of(hub.pr_body(260)) == "Merged", \
        f"347.1: the sweep left closed #246 or merged PR #260 showing an old card: " \
        f"{stage_of(hub.issue_body(246))!r}, {stage_of(hub.pr_body(260))!r}"
    assert not stale(hub, 312), f"347.1: PR #314 was updated but the sweep left #312's old card: {hub.issue_body(312)!r}"
    assert card_of(hub.pr_body(314)) and without_issue_link(card_of(hub.pr_body(314)), 312) == card_of(hub.issue_body(312)), \
        f"347.1: the sweep did not write #312's card on PR #314: {hub.pr_body(314)!r}"
    assert "The owner sees issue 320 done." in (card_of(hub.issue_body(320)) or ""), \
        f"347.1: the sweep left #320's card without its plan: {card_of(hub.issue_body(320))!r}"
    swept = {n: hub.issue_body(n) for n in (246, 312, 320)}
    swept_prs = {p: hub.pr_body(p) for p in (260, 314)}
    for n in (246, 312, 320):
        must_redraw(hub, issue_comment(n), "347.1")
    assert {n: hub.issue_body(n) for n in (246, 312, 320)} == swept, \
        "347.1: a redraw after the sweep changed an issue card, so the sweep did not leave it as GitHub's state draws it"
    assert {p: hub.pr_body(p) for p in (260, 314)} == swept_prs, \
        "347.1: a redraw after the sweep changed a PR card, so the sweep did not leave it as GitHub's state draws it"


def test_an_issue_updated_since_the_last_sweep_gets_its_pr_card_redrawn_too(tmp_path, record_property):
    """An issue updated since the last sweep gets its pull request's card redrawn too.

    The last sweep succeeded at 05:00. Issue #312 was updated at 06:00, but its PR #314, which holds no card, was not.
    After one scheduled run, #312's card is redrawn and PR #314 shows the same card, but for its link back to #312
    (#452), with its closing line kept, by the issue's full address. Proves 347.1."""
    record_property("proves", "347.1")
    hub = SweepHub(tmp_path)
    hub.no_pr_card(314, 312)
    hub.touch("issue", 312, "2026-10-09T06:00:00Z")
    hub.last_sweep("2026-10-09T05:00:00Z")
    must_redraw(hub, schedule(), "347.1")
    assert not stale(hub, 312), f"347.1: #312 was updated but the sweep left its old card: {hub.issue_body(312)!r}"
    assert without_issue_link(card_of(hub.pr_body(314)), 312) == card_of(hub.issue_body(312)), \
        f"347.1: #312 was updated but the sweep did not write its card on PR #314: {hub.pr_body(314)!r}"
    assert "Closes" not in hub.pr_body(314), "347.1: PR #314 still carries a Closes line (#416 dropped it)"


def test_a_card_that_already_shows_its_state_is_not_rewritten(tmp_path, record_property):
    """A card already showing its issue's state is not rewritten, even when updated.

    The first sweep puts the stale cards right. Then a sweep succeeds at 11:00 and every issue and pull request is
    updated after it (the card writes themselves, and the owner touching #246 and PR #314 at 13:00). The next sweep
    writes no issue body and no pull request body. Proves 347.1."""
    record_property("proves", "347.1")
    hub = stale_repo(tmp_path)
    must_redraw(hub, schedule(), "347.1")
    assert not stale(hub, 246) and not stale(hub, 320) and not stale(hub, p=314), \
        "347.1: the first sweep did not put the stale cards of #246, #320 and PR #314 right, so nothing can be compared"
    hub.last_sweep("2026-10-09T11:00:00Z")
    hub.touch("issue", 246, "2026-10-09T13:00:00Z")
    hub.touch("pr", 314, "2026-10-09T13:00:00Z")
    hub.clear_writes()
    must_redraw(hub, schedule(), "347.1")
    wrote = [w for w in hub.writes() if w["op"] in ("issue-body", "pr-body")]
    assert not wrote, f"347.1: the sweep rewrote cards that already showed their issue's state: {wrote}"


# 347.2 -----------------------------------------------------------------------------------------------------------

def test_the_sweep_only_looks_at_issues_and_prs_updated_since_the_last_sweep(tmp_path, record_property):
    """The sweep looks only at the issues and pull requests updated since the last sweep.

    The last sweep succeeded at 05:00, and every card is stale. Only #246 was updated since, at 06:00. After one
    scheduled run, #246's and PR #260's cards are redrawn, while #312 and PR #314 keep their old cards and the sweep
    made no call about either of them beyond listing #312's blocked-by links. Proves 347.2."""
    record_property("proves", "347.2")
    hub = SweepHub(tmp_path)
    hub.touch("issue", 246, "2026-10-09T06:00:00Z")
    hub.last_sweep("2026-10-09T05:00:00Z")
    hub.clear_calls()
    must_redraw(hub, schedule(), "347.2")
    assert not stale(hub, 246) and not stale(hub, p=260), \
        f"347.2: #246 was updated since the last sweep but its cards were not redrawn: " \
        f"{card_of(hub.issue_body(246))!r}, {card_of(hub.pr_body(260))!r}"
    assert stale(hub, 312) and stale(hub, p=314), \
        "347.2: #312 and PR #314 were not updated since the last sweep, yet the sweep redrew their cards"
    calls = hub.calls()
    for n in (312, 314):
        seen = looked_at(calls, n)
        assert not seen, f"347.2: the sweep looked at #{n}, not updated since the last sweep: {seen[:5]}"


def test_a_failed_sweep_does_not_count_as_the_last_sweep(tmp_path, record_property):
    """A failed sweep does not count; only the last sweep that succeeded does.

    The last sweep that succeeded started at 05:00; a newer one at 07:00 failed. #246 was updated at 06:00, between
    the two, and #312 not since 01:00. After one scheduled run, #246's and PR #260's cards are redrawn, and #312's
    and PR #314's are not. Proves 347.2."""
    record_property("proves", "347.2")
    hub = SweepHub(tmp_path)
    hub.touch("issue", 246, "2026-10-09T06:00:00Z")
    hub.last_sweep("2026-10-09T05:00:00Z")
    hub.last_sweep("2026-10-09T07:00:00Z", conclusion="failure")
    must_redraw(hub, schedule(), "347.2")
    assert not stale(hub, 246) and not stale(hub, p=260), \
        "347.2: #246 was updated after the last sweep that succeeded, but a newer failed sweep kept it from a redraw"
    assert stale(hub, 312) and stale(hub, p=314), \
        "347.2: #312 was not updated since the last sweep that succeeded, yet its cards were redrawn"


def test_only_a_scheduled_sweep_counts_as_the_last_sweep(tmp_path, record_property):
    """Only the 15-minute sweep counts as the last sweep, not card.yml's event runs.

    card.yml also runs on every issue event, comment and merge, and those runs redraw only their own issue's card.
    The last scheduled sweep succeeded at 05:00; #246 was updated at 06:00; then card.yml ran for an issue event at
    07:00 and for a comment at 07:30, both successfully. After one scheduled run, #246's and PR #260's cards are
    redrawn, and #312's and PR #314's are not. Proves 347.2."""
    record_property("proves", "347.2")
    hub = SweepHub(tmp_path)
    hub.touch("issue", 246, "2026-10-09T06:00:00Z")
    hub.last_sweep("2026-10-09T05:00:00Z")
    hub.last_sweep("2026-10-09T07:00:00Z", event="issues")
    hub.last_sweep("2026-10-09T07:30:00Z", event="issue_comment")
    must_redraw(hub, schedule(), "347.2")
    assert not stale(hub, 246) and not stale(hub, p=260), \
        "347.2: #246 was updated after the last scheduled sweep, but a newer card.yml run on an issue event or " \
        "comment was taken as the last sweep and #246's cards were not redrawn"
    assert stale(hub, 312) and stale(hub, p=314), \
        "347.2: #312 was not updated since the last scheduled sweep, yet its cards were redrawn"


def test_a_change_made_while_the_last_sweep_ran_is_not_missed(tmp_path, record_property):
    """A change made while the last sweep ran is picked up by the next one.

    The last sweep started at 05:00 and finished at 05:10; #246 was updated at 05:05, while it ran. After one
    scheduled run, #246's and PR #260's cards are redrawn, so the sweep counts from when the last one started, not
    from when it ended; #312, updated at 01:00, keeps its old card. Proves 347.2."""
    record_property("proves", "347.2")
    hub = SweepHub(tmp_path)
    hub.touch("issue", 246, "2026-10-09T05:05:00Z")
    hub.last_sweep("2026-10-09T05:00:00Z", ended="2026-10-09T05:10:00Z")
    must_redraw(hub, schedule(), "347.2")
    assert not stale(hub, 246) and not stale(hub, p=260), \
        "347.2: #246 was updated while the last sweep ran (05:05, between its start 05:00 and end 05:10), " \
        "but the next sweep counted from the end and did not redraw its cards"
    assert stale(hub, 312) and stale(hub, p=314), \
        "347.2: #312 was not updated since the last sweep, yet its cards were redrawn"


# 347.3 -----------------------------------------------------------------------------------------------------------

def test_when_github_cannot_say_what_changed_every_card_is_rechecked(tmp_path, record_property):
    """When GitHub cannot say what changed, the sweep rechecks every card and says why.

    GitHub refuses to list card.yml's runs with HTTP 502, and every card is stale, including closed #246 with merged
    PR #260. The scheduled run still passes, puts every card right (#246 and #260 say Merged, #312's card is redrawn
    and PR #314 shows it), and its log carries GitHub's reason, HTTP 502. Proves 347.3."""
    record_property("proves", "347.3")
    hub = SweepHub(tmp_path)
    hub.merge(246, 260)
    hub.last_sweep("2026-10-09T23:00:00Z")
    hub.refuse_runs()
    r = must_redraw(hub, schedule(), "347.3")
    assert stage_of(hub.issue_body(246)) == "Merged" and stage_of(hub.pr_body(260)) == "Merged", \
        "347.3: GitHub could not say what changed, and the sweep left closed #246 or merged PR #260 stale"
    assert not stale(hub, 312) and without_issue_link(card_of(hub.pr_body(314)), 312) == card_of(hub.issue_body(312)), \
        "347.3: GitHub could not say what changed, and the sweep left #312's or PR #314's card stale"
    assert "502" in r.log, f"347.3: the sweep's log does not say why it rechecked every card:\n{r.log[-2000:]}"


def test_with_no_sweep_that_succeeded_yet_every_card_is_rechecked(tmp_path, record_property):
    """With no sweep that succeeded yet, the first sweep rechecks every card, open or closed.

    GitHub lists no successful run of card.yml (only a failed one), and every card is stale, including closed #246
    with merged PR #260. After one scheduled run, #246 and #260 say Merged and #312's card is redrawn, PR #314
    showing it. Proves 347.3."""
    record_property("proves", "347.3")
    hub = SweepHub(tmp_path)
    hub.merge(246, 260)
    hub.last_sweep("2026-10-09T23:00:00Z", conclusion="failure")
    must_redraw(hub, schedule(), "347.3")
    assert stage_of(hub.issue_body(246)) == "Merged" and stage_of(hub.pr_body(260)) == "Merged", \
        "347.3: with no sweep that succeeded yet, the sweep left closed #246 or merged PR #260 stale"
    assert not stale(hub, 312) and without_issue_link(card_of(hub.pr_body(314)), 312) == card_of(hub.issue_body(312)), \
        "347.3: with no sweep that succeeded yet, the sweep left #312's or PR #314's card stale"


# 347.4 -----------------------------------------------------------------------------------------------------------

def test_the_sweep_names_a_card_it_cannot_redraw_fails_and_puts_the_rest_right(tmp_path, record_property):
    """The sweep names a card it cannot redraw, fails, and still puts the rest right.

    The last sweep succeeded at 05:00 and #246, PR #314 and #320 were updated since. GitHub refuses every read of
    #312. The scheduled run fails with an error line naming #312, and still leaves #246 and #260 saying Merged and
    #320 showing its plan; no error line names #246, #260 or #320. Proves 347.4."""
    record_property("proves", "347.4")
    hub = stale_repo(tmp_path)
    hub.refuse("read-issue", 312)
    r = hub.run(*schedule(), "347.4")
    assert r.card_ran(), "347.4: the scheduled run did not run the card job"
    assert r.failed(), f"347.4: the scheduled run passed although #312's card could not be redrawn:\n{r.log[-2000:]}"
    errors = r.errors()
    assert any("#312" in e for e in errors), f"347.4: no error line names #312: {errors}\n{r.log[-2000:]}"
    assert not [e for e in errors if re.search(r"#(246|260|320)\b", e)], \
        f"347.4: an error names a card that was fine: {errors}"
    assert stage_of(hub.issue_body(246)) == "Merged" and stage_of(hub.pr_body(260)) == "Merged", \
        "347.4: one unreadable issue kept #246 and PR #260 from being put right"
    assert "The owner sees issue 320 done." in (card_of(hub.issue_body(320)) or ""), \
        "347.4: one unreadable issue kept #320's card from being put right"

"""A blocked-by link added or removed by hand shows on both cards (#254).

Story 5 of #231.

GitHub Actions has no event for a blocked-by link being added or removed, so, as the owner answered on #254, the cards
update on every event GitHub does announce on either issue, with a schedule only as a backstop. card.yml runs
`python3 dokima/card.py` on every issues and issue_comment event a person causes on an issue (ISSUE_NUMBER is that
issue, GITHUB_EVENT_NAME issues or issue_comment): it redraws that issue's card and the card of every issue it blocks
or is blocked by, on GitHub now or on its card before, so a link removed by hand leaves the other card too. card.yml
also runs on a cron (GITHUB_EVENT_NAME=schedule, no ISSUE_NUMBER), and then card.py sweeps every open issue. Both read
GitHub's own blocked-by links (GET repos/o/r/issues/N/dependencies/blocked_by and .../blocking) and rewrite another
issue's card only when its blocking links, or loop of issues blocking each other, differ from what its card shows.
Every redraw draws the Blocked by and Blocks lines from GitHub's links read right then.

Every test runs the real `python3 dokima/card.py` as a subprocess against the fake GitHub of
tests/test_plan_links_recorded.py (a `gh` first on PATH keeping its state in one JSON file), extended here with two
things: GitHub failing to list one issue's blocked-by links (state "unreadable": {issue: GitHub's error}), and a
project board reached through dokima.board.Board's own GraphQL calls, as DOKIMA_BOARD="o/1" names it, whose Action
writes are logged as {"op": "field", "item": "ITEM_issue_N", "field": "Action", "option": "Needs you" or None}.
The sweep lists open issues with `gh api repos/o/r/issues`, which the fake answers. card.yml itself is read as text:
its triggers, and its job's one-line `if:` evaluated against the events GitHub would send.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_plan_links_recorded import FAKE_GH, LABELS, N, OWNER, ROOT, Hub, links  # noqa: E402
from dokima import body  # noqa: E402

CARD_YML = os.path.join(ROOT, ".github", "workflows", "card.yml")

EXTRA_DEFS = r'''
def extra(route, method, f):
    m = re.fullmatch(r"repos/o/r/issues/(\d+)/dependencies/(blocked_by|blocking)", route)
    if m and method == "GET" and m.group(1) in S.get("unreadable", {}):
        fail(S["unreadable"][m.group(1)])
    if route != "graphql":
        return
    q = f.get("query", "")
    board = S.setdefault("board", {})
    if "fields(first" in q and "projectV2(number" in q:
        out({"data": {"organization": {"projectV2": {"id": "P1", "fields": {"nodes": [
            {"id": "F_Status", "name": "Status", "options": [{"id": "S_" + c, "name": c} for c in
                                                            ("Backlog", "Plan", "Work", "Review", "Done")]},
            {"id": "F_Action", "name": "Action", "options": [{"id": "A_Needs you", "name": "Needs you"},
                                                            {"id": "A_Autopilot", "name": "Autopilot"}]}]}}}}})
        sys.exit(0)
    if "views(first" in q:
        out({"data": {"organization": {"projectV2": {"views": {"nodes": []}}}}})
        sys.exit(0)
    if "projectItems" in q:
        kind = "pullRequest" if "pullRequest(number" in q else "issue"
        n = int(f["n"])
        out({"data": {"repository": {kind: {"id": f"NODE_{kind}_{n}", "projectItems": {"nodes": [
            {"id": f"ITEM_{'pr' if kind == 'pullRequest' else 'issue'}_{n}", "project": {"id": "P1"}}]}}}}})
        sys.exit(0)
    if "labels(first" in q:
        kind = "pullRequest" if "pullRequest(number" in q else "issue"
        labels = issue(int(f["n"])).get("labels", []) if kind == "issue" else []
        out({"data": {"repository": {kind: {"labels": {"nodes": [{"name": l} for l in labels]}}}}})
        sys.exit(0)
    if "pullRequests(headRefName" in q:
        out({"data": {"repository": {"pullRequests": {"nodes": []}}}})
        sys.exit(0)
    if "parent{" in q:
        out({"data": {"repository": {"issue": {"parent": None}}}})
        sys.exit(0)
    if "fieldValueByName" in q:
        name = board.get(f["i"], {}).get(f["f"])
        out({"data": {"node": {"fieldValueByName": {"name": name} if name else None}}})
        sys.exit(0)
    if "updateProjectV2ItemFieldValue" in q or "clearProjectV2ItemFieldValue" in q:
        field = {"F_Status": "Status", "F_Action": "Action"}[f["f"]]
        option = f["o"].split("_", 1)[1] if "o" in f else None
        board.setdefault(f["i"], {})[field] = option
        write({"op": "field", "item": f["i"], "field": field, "option": option})
        save()
        out({"data": {}})
        sys.exit(0)
    if "updateProjectV2ItemPosition" in q or "addProjectV2ItemById" in q:
        out({"data": {"addProjectV2ItemById": {"item": {"id": "ITEM_new"}}}})
        sys.exit(0)


'''
DEFS_AT = 'if a[:2] == ["issue", "view"]:\n'
CALL_AT = '    if route == "graphql":\n'


class HandHub(Hub):
    """Story 3's fake GitHub, plus failing link lists and a project board."""

    def __init__(self, tmp, **kw):
        super().__init__(tmp, **kw)
        assert FAKE_GH.count(DEFS_AT) == 1 and FAKE_GH.count(CALL_AT) == 1, \
            "test setup: the fake GitHub of test_plan_links_recorded.py changed shape"
        fake = FAKE_GH.replace(DEFS_AT, EXTRA_DEFS + DEFS_AT).replace(CALL_AT, "    extra(route, method, f)\n" + CALL_AT)
        gh = os.path.join(self.dir, "bin", "gh")
        head = open(gh).read().split(FAKE_GH, 1)[0]
        open(gh, "w").write(head + fake)
        self.env["DOKIMA_BOARD"] = "o/1"

    def set_links(self, deps):
        """Make GitHub's blocked-by links exactly `deps` ({issue: [its blockers]}), as a person would by hand."""
        s = self.load()
        s["deps"] = {str(k): list(v) for k, v in deps.items()}
        self.save()

    def label(self, n, *labels):
        """Give issue n exactly these labels."""
        s = self.load()
        s["issues"][str(n)]["labels"] = list(labels)
        self.save()

    def unreadable(self, n, why):
        """Make GitHub fail with `why` whenever it lists issue n's links."""
        s = self.load()
        s.setdefault("unreadable", {})[str(n)] = why
        self.save()

    def sweep(self, k):
        """Run card.yml's scheduled run, `python3 dokima/card.py` with GITHUB_EVENT_NAME=schedule; fails naming k."""
        env = {**self.env, "GITHUB_EVENT_NAME": "schedule"}
        for name in ("ISSUE_NUMBER", "RUN_TITLE", "PR_NUMBER", "HEAD_SHA"):
            env.pop(name, None)
        p = subprocess.run([sys.executable, "dokima/card.py"], cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=120)
        assert p.returncode == 0, (f"{k}: the scheduled run of card.yml (`python3 dokima/card.py`, event schedule) "
                                   f"failed instead of sweeping the cards: {p.stderr[-1500:]}")

    def event(self, n, name, k):
        """Run card.yml for a person's change on issue n: `python3 dokima/card.py` with ISSUE_NUMBER=n and
        GITHUB_EVENT_NAME `name` (issues or issue_comment); fails naming k."""
        env = {**self.env, "ISSUE_NUMBER": str(n), "GITHUB_EVENT_NAME": name}
        for v in ("RUN_TITLE", "PR_NUMBER", "HEAD_SHA"):
            env.pop(v, None)
        p = subprocess.run([sys.executable, "dokima/card.py"], cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=120)
        assert p.returncode == 0, f"{k}: card.yml's run for a change on #{n} ({name}) failed: {p.stderr[-1500:]}"

    def top(self, n):
        """The card part of issue n's body, above the owner's part."""
        return self.body(n).split(body.MARKER, 1)[0]

    def loop_line(self, n):
        """The line on #n's card saying which issues block each other, or None."""
        return next((l for l in self.top(n).splitlines() if "block each other" in l.lower()), None)

    def actions(self, n):
        """Every Action value the commands set on issue n's board card, in order."""
        return [w["option"] for w in self.writes("field") if w["item"] == f"ITEM_issue_{n}" and w["field"] == "Action"]

    def bot_comments(self, n):
        """The comments the bot posted on issue n."""
        return [c for c in self.comments(n) if c["author"]["login"] != OWNER]


def numbers(line):
    """The issue numbers a line names."""
    return {int(x) for x in re.findall(r"(?:#|/issues/)(\d+)", line or "")}


# 254.1 ---------------------------------------------------------------------------------------------------------------

def test_a_link_added_by_hand_shows_on_both_cards_with_no_comment(tmp_path, record_property):
    """A blocked-by link added by hand shows on both cards, and no comment is posted.

    With no plan and no command, GitHub gets #252 blocked by #301 by hand. After the scheduled run, #252's card shows
    #301 on its Blocked by line and #301's card shows #252 on its Blocks line, nothing else, and neither issue has a
    new comment. Proves 254.1."""
    record_property("proves", "254.1")
    hub = HandHub(tmp_path)
    hub.set_links({N: [301]})
    hub.sweep("254.1")
    assert hub.card_links(N) == {"blocked_by": {301}, "blocks": set(), "relates_to": set()}, \
        f"254.1: #252's card does not show the hand-made link #252 blocked by #301: {hub.card_links(N)}"
    assert hub.card_links(301) == {"blocked_by": set(), "blocks": {N}, "relates_to": set()}, \
        f"254.1: #301's card does not show it blocks #252: {hub.card_links(301)}"
    for n in (N, 301):
        assert hub.comments(n) == [], f"254.1: a comment was posted on #{n} for the link: {hub.comments(n)}"


def test_a_link_removed_by_hand_leaves_both_cards_with_no_comment(tmp_path, record_property):
    """A blocked-by link removed by hand leaves both cards, and no comment is posted.

    An approved plan records #252 blocked by #301 and both cards show it. A person removes the link by hand on
    GitHub. After the scheduled run, neither card shows it and no new comment is on either issue. Proves 254.1."""
    record_property("proves", "254.1")
    hub = HandHub(tmp_path)
    hub.approve(links(blocked_by=[301]))
    assert hub.card_links(N)["blocked_by"] == {301} and hub.card_links(301)["blocks"] == {N}, \
        "test setup: the approved plan's link is not on both cards"
    before = {n: len(hub.comments(n)) for n in (N, 301)}
    hub.set_links({})
    hub.sweep("254.1")
    assert hub.card_links(N)["blocked_by"] == set(), f"254.1: #252's card still shows #301: {hub.card_links(N)}"
    assert hub.card_links(301)["blocks"] == set(), f"254.1: #301's card still shows it blocks #252: {hub.card_links(301)}"
    for n in (N, 301):
        assert len(hub.comments(n)) == before[n], f"254.1: a comment was posted on #{n} for the removed link"


def test_a_hand_link_between_two_other_issues_shows_on_their_cards_only(tmp_path, record_property):
    """A hand link between two other issues shows on their two cards and nowhere else.

    GitHub gets #303 blocked by #302 by hand. After the scheduled run #303 shows Blocked by #302, #302 shows Blocks
    #303, and #252's card shows no link. Proves 254.1."""
    record_property("proves", "254.1")
    hub = HandHub(tmp_path)
    hub.set_links({303: [302]})
    hub.sweep("254.1")
    assert hub.card_links(303)["blocked_by"] == {302}, f"254.1: #303's card misses #302: {hub.card_links(303)}"
    assert hub.card_links(302)["blocks"] == {303}, f"254.1: #302's card misses #303: {hub.card_links(302)}"
    assert hub.card_links(N) == {k: set() for k in LABELS}, f"254.1: #252's card shows a link: {hub.card_links(N)}"


def test_a_change_on_the_blocked_issue_redraws_the_blocker_right_away(tmp_path, record_property):
    """A person's change on the blocked issue updates both cards right away, with no schedule.

    GitHub gets #252 blocked by #301 by hand, then a person changes #252 (an issues event). That one run, with no
    scheduled run, shows #301 on #252's Blocked by line and #252 on #301's Blocks line, posts no comment, and leaves
    the unrelated #302 and #303 untouched. Proves 254.1."""
    record_property("proves", "254.1")
    hub = HandHub(tmp_path)
    hub.set_links({N: [301]})
    hub.event(N, "issues", "254.1")
    assert hub.card_links(N) == {"blocked_by": {301}, "blocks": set(), "relates_to": set()}, \
        f"254.1: a change on #252 did not show its hand-made link to #301 on its card: {hub.card_links(N)}"
    assert hub.card_links(301) == {"blocked_by": set(), "blocks": {N}, "relates_to": set()}, \
        f"254.1: a change on #252 did not update #301's card to show it blocks #252: {hub.card_links(301)}"
    for n in (N, 301):
        assert hub.comments(n) == [], f"254.1: a comment was posted on #{n} for the link: {hub.comments(n)}"
    touched = {w["issue"] for w in hub.writes("body")}
    assert not touched & {302, 303}, f"254.1: a change on #252 rewrote unrelated cards: {sorted(touched & {302, 303})}"


def test_a_comment_on_the_blocker_redraws_the_blocked_issue_right_away(tmp_path, record_property):
    """A person's comment on the blocker updates both cards right away, with no schedule.

    GitHub gets #252 blocked by #301 by hand, then a person comments on #301 (an issue_comment event). That one run
    shows #252 on #301's Blocks line and #301 on #252's Blocked by line, with no comment from the bot. Proves 254.1."""
    record_property("proves", "254.1")
    hub = HandHub(tmp_path)
    hub.set_links({N: [301]})
    hub.event(301, "issue_comment", "254.1")
    assert hub.card_links(301)["blocks"] == {N}, \
        f"254.1: a comment on #301 did not show on its card that it blocks #252: {hub.card_links(301)}"
    assert hub.card_links(N)["blocked_by"] == {301}, \
        f"254.1: a comment on #301 did not update #252's card to show #301 blocks it: {hub.card_links(N)}"
    for n in (N, 301):
        assert hub.bot_comments(n) == [], f"254.1: the bot posted a comment on #{n} for the link"


def test_a_link_removed_by_hand_leaves_both_cards_on_a_change_to_either_issue(tmp_path, record_property):
    """A link removed by hand leaves both cards once a person changes either issue.

    An approved plan records #252 blocked by #301; a person removes it by hand and then changes #301, the blocker:
    neither card shows the link. Then #303 blocked by #302 is added by hand and both cards show it after a change on
    #303; it is removed by hand and a change on #303, the blocked issue, clears #302's card too. No comment is posted
    for any of it. Proves 254.1."""
    record_property("proves", "254.1")
    hub = HandHub(tmp_path)
    hub.approve(links(blocked_by=[301]))
    assert hub.card_links(N)["blocked_by"] == {301} and hub.card_links(301)["blocks"] == {N}, \
        "test setup: the approved plan's link is not on both cards"
    before = {n: len(hub.comments(n)) for n in (N, 301, 302, 303)}
    hub.set_links({})
    hub.event(301, "issues", "254.1")
    assert hub.card_links(301)["blocks"] == set(), \
        f"254.1: after a change on #301, its card still shows it blocks #252: {hub.card_links(301)}"
    assert hub.card_links(N)["blocked_by"] == set(), \
        f"254.1: a change on #301 did not clear the removed link from #252's card: {hub.card_links(N)}"
    hub.set_links({303: [302]})
    hub.event(303, "issues", "254.1")
    assert hub.card_links(303)["blocked_by"] == {302} and hub.card_links(302)["blocks"] == {303}, \
        f"254.1: a change on #303 did not show #303 blocked by #302 on both cards: {hub.card_links(303)}, {hub.card_links(302)}"
    hub.set_links({})
    hub.event(303, "issues", "254.1")
    assert hub.card_links(303)["blocked_by"] == set(), f"254.1: #303's card still shows #302: {hub.card_links(303)}"
    assert hub.card_links(302)["blocks"] == set(), \
        f"254.1: a change on #303 did not clear the removed link from #302's card: {hub.card_links(302)}"
    for n in (N, 301, 302, 303):
        assert len(hub.comments(n)) == before[n], f"254.1: a comment was posted on #{n} for a link"


# 254.2 ---------------------------------------------------------------------------------------------------------------

def test_two_issues_blocking_each_other_by_hand_are_named_on_both_cards(tmp_path, record_property):
    """Two issues a person made block each other are named on both cards.

    GitHub has #252 blocked by #301 and, by hand, #301 blocked by #252, off autopilot. After the scheduled run both
    cards have a line saying #252 and #301 block each other; no comment and no Needs you pill, as nothing runs. Proves 254.2."""
    record_property("proves", "254.2")
    hub = HandHub(tmp_path)
    hub.set_links({N: [301], 301: [N]})
    hub.sweep("254.2")
    for n in (N, 301):
        line = hub.loop_line(n)
        assert line and numbers(line) == {N, 301}, \
            f"254.2: #{n}'s card has no line saying exactly #252 and #301 block each other: {hub.top(n)!r}"
        assert hub.bot_comments(n) == [], f"254.2: off autopilot a comment was posted on #{n}"
        assert "Needs you" not in hub.actions(n), f"254.2: off autopilot #{n} got the Needs you pill"


def test_a_loop_through_other_issues_names_every_issue_on_every_card_in_it(tmp_path, record_property):
    """A loop through other issues is named in full on each of its cards.

    GitHub has #302 blocked by #252, #301 blocked by #302 and, by hand, #252 blocked by #301. After the scheduled
    run the cards of #252, #301 and #302 each name all three as blocking each other; #303's card has no such line. Proves 254.2."""
    record_property("proves", "254.2")
    hub = HandHub(tmp_path)
    hub.set_links({302: [N], 301: [302], N: [301]})
    hub.sweep("254.2")
    for n in (N, 301, 302):
        line = hub.loop_line(n)
        assert line and numbers(line) == {N, 301, 302}, \
            f"254.2: #{n}'s card does not name exactly #252, #301 and #302 as blocking each other: {line!r}"
    assert hub.loop_line(303) is None, f"254.2: #303 is not in the loop but its card says it is"


def test_the_loop_line_stays_on_a_later_redraw_and_leaves_once_the_loop_is_gone(tmp_path, record_property):
    """The loop stays named on later redraws and goes once it is broken.

    After the scheduled run names #252 and #301 blocking each other, the owner edits #252 and card.yml redraws it:
    the line is still there. Then the link #301 blocked by #252 is removed by hand: after the next scheduled run
    neither card has the line. Proves 254.2."""
    record_property("proves", "254.2")
    hub = HandHub(tmp_path)
    hub.set_links({N: [301], 301: [N]})
    hub.sweep("254.2")
    hub.redraw(N)
    assert hub.loop_line(N) and numbers(hub.loop_line(N)) == {N, 301}, \
        f"254.2: card.yml's redraw of #252 dropped the line naming the loop: {hub.top(N)!r}"
    hub.set_links({N: [301]})
    hub.sweep("254.2")
    for n in (N, 301):
        assert hub.loop_line(n) is None, f"254.2: #{n}'s card still names a loop that is gone: {hub.loop_line(n)!r}"


def test_on_autopilot_a_hand_made_loop_stops_the_river_for_the_owner_once(tmp_path, record_property):
    """On autopilot, a hand-made loop stops the river for the owner, once.

    #252 and #301 are on autopilot and a person makes them block each other. After the scheduled run each issue has
    one bot comment mentioning the owner and naming #252 and #301, and its board card has the Needs you pill. A
    second scheduled run posts no second comment. Proves 254.2."""
    record_property("proves", "254.2")
    hub = HandHub(tmp_path)
    hub.label(N, "autopilot")
    hub.label(301, "autopilot")
    hub.set_links({N: [301], 301: [N]})
    hub.sweep("254.2")
    for n in (N, 301):
        said = [c["body"] for c in hub.bot_comments(n)]
        assert len(said) == 1, f"254.2: #{n} should get exactly one comment stopping for the owner, got {said}"
        assert f"@{OWNER}" in said[0], f"254.2: the comment on #{n} does not mention the owner: {said[0]!r}"
        assert numbers(said[0]) >= {N, 301}, f"254.2: the comment on #{n} does not name #252 and #301: {said[0]!r}"
        assert hub.actions(n) and hub.actions(n)[-1] == "Needs you", \
            f"254.2: #{n}'s board card was not given the Needs you pill: {hub.actions(n)}"
    hub.sweep("254.2")
    for n in (N, 301):
        assert len(hub.bot_comments(n)) == 1, f"254.2: the next scheduled run stopped for the owner again on #{n}"


# 254.3 ---------------------------------------------------------------------------------------------------------------

def test_any_redraw_shows_the_links_github_has_right_then(tmp_path, record_property):
    """Every redraw shows GitHub's blocking links as they are right then.

    An approved plan records #252 blocked by #301; a person then removes it and adds #252 blocked by #302 by hand.
    card.yml's own redraw (ISSUE_NUMBER) of #252, #301 and #302 shows #252 blocked by #302 only, #302 blocking #252,
    and #301 blocking nothing, with no scheduled run in between. Proves 254.3."""
    record_property("proves", "254.3")
    hub = HandHub(tmp_path)
    hub.approve(links(blocked_by=[301]))
    hub.set_links({N: [302]})
    for n in (N, 301, 302):
        hub.redraw(n)
    assert hub.card_links(N)["blocked_by"] == {302}, \
        f"254.3: #252's card does not show GitHub's links as they are now (blocked by #302 only): {hub.card_links(N)}"
    assert hub.card_links(302)["blocks"] == {N}, f"254.3: #302's card does not show it blocks #252: {hub.card_links(302)}"
    assert hub.card_links(301)["blocks"] == set(), \
        f"254.3: #301's card still shows a blocking link GitHub no longer has: {hub.card_links(301)}"


def test_a_card_says_when_github_cannot_list_its_links(tmp_path, record_property):
    """When GitHub cannot list an issue's links, its card says so with GitHub's reason.

    GitHub answers every request for #252's blocked-by links with "HTTP 502: Server Error". card.yml's redraw of
    #252 still writes its card, and the card shows that reason; once GitHub answers again, the reason is gone. Proves 254.3."""
    record_property("proves", "254.3")
    why = "HTTP 502: Server Error"
    hub = HandHub(tmp_path)
    hub.set_links({N: [301]})
    hub.unreadable(N, why)
    hub.redraw(N)
    assert hub.writes("body"), "254.3: the card was not written when GitHub could not list the links"
    assert why in hub.top(N), f"254.3: #252's card does not say GitHub could not list its links: {hub.top(N)!r}"
    s = hub.load()
    s["unreadable"] = {}
    hub.save()
    hub.redraw(N)
    assert why not in hub.top(N) and hub.card_links(N)["blocked_by"] == {301}, \
        f"254.3: once GitHub answers, #252's card should show #301 and no failure: {hub.top(N)!r}"


def test_the_scheduled_run_goes_on_when_one_issue_cannot_be_read(tmp_path, record_property):
    """One issue GitHub cannot read does not stop the other cards from updating.

    GitHub fails to list #301's links, and a person adds #252 blocked by #302 by hand. The scheduled run still
    finishes and both #252's and #302's cards show the link. Proves 254.3."""
    record_property("proves", "254.3")
    hub = HandHub(tmp_path)
    hub.unreadable(301, "HTTP 502: Server Error")
    hub.set_links({N: [302]})
    hub.sweep("254.3")
    assert hub.card_links(N)["blocked_by"] == {302} and hub.card_links(302)["blocks"] == {N}, \
        f"254.3: one unreadable issue kept the others from updating: #252 {hub.card_links(N)}, #302 {hub.card_links(302)}"


# 254.4 ---------------------------------------------------------------------------------------------------------------

def minutes(field):
    """The minutes of the hour a cron minute field fires on."""
    out = set()
    for part in field.split(","):
        rng, _, step = part.partition("/")
        lo, hi = (0, 59) if rng == "*" else tuple(int(x) for x in rng.split("-")) if "-" in rng else (int(rng), int(rng) if not step else 59)
        out |= set(range(lo, hi + 1, int(step) if step else 1))
    return sorted(out)


def on_block(text):
    """The lines of card.yml's `on:` block."""
    m = re.search(r"^on:\n((?:[ \t]+.*\n|\n)+)", text, re.M)
    return m.group(1) if m else ""


def trigger(on, name):
    """The activity types card.yml lists for one trigger.

    None when the trigger is absent, "all" when it lists no types."""
    lines = on.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(\s+)" + re.escape(name) + r":\s*(\{\}|null)?\s*$", line)
        if not m:
            continue
        indent, block = len(m.group(1)), []
        for nxt in lines[i + 1:]:
            if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                break
            block.append(nxt)
        text = "\n".join(block)
        if "types:" not in text:
            return "all"
        inline = re.search(r"types:\s*\[([^\]]*)\]", text)
        if inline:
            return {t.strip().strip("'\"") for t in inline.group(1).split(",") if t.strip()}
        return set(re.findall(r"^\s*-\s*['\"]?(\w+)", text.split("types:", 1)[1], re.M))
    return None


def job_if(text):
    """card.yml's job condition, a one-line GitHub expression, as a function of the `github` context.

    Reads the first `if:` under `jobs:` and turns GitHub's ==, !=, &&, || and ! on context paths and quoted strings
    into Python; a missing path is null, as on GitHub. A job with no `if:` runs on every event."""
    jobs = text.split("\njobs:", 1)[1]
    m = re.search(r"^\s+if:\s*(.+?)\s*$", jobs, re.M)
    if not m:
        return lambda ctx: True
    expr = m.group(1).strip()
    if expr[:1] in "'\"" and expr[-1:] == expr[:1]:
        expr = expr[1:-1]
    expr = re.sub(r"^\$\{\{(.*)\}\}$", r"\1", expr.strip()).strip()
    out = []
    for tok in re.findall(r"'[^']*'|&&|\|\||==|!=|!|\(|\)|[A-Za-z_][\w.\-]*|\S", expr):
        if tok.startswith("'"):
            out.append(repr(tok[1:-1]))
        elif tok in ("&&", "||", "!"):
            out.append({"&&": " and ", "||": " or ", "!": " not "}[tok])
        elif tok in ("==", "!=", "(", ")"):
            out.append(f" {tok} ")
        elif tok in ("true", "false", "null"):
            out.append({"true": "True", "false": "False", "null": "None"}[tok])
        elif re.fullmatch(r"[A-Za-z_][\w.\-]*", tok):
            out.append(f"get({tok!r})")
        else:
            raise AssertionError(f"254.4: card.yml's job `if:` uses {tok!r}, which this test cannot read: {expr}")
    code = "".join(out)

    def run(ctx):
        def get(path):
            v = ctx
            for part in path.split("."):
                v = v.get(part) if isinstance(v, dict) else None
            return v
        return bool(eval(code, {"get": get}))
    return run


def ctx(event, action=None, sender="User", pr=False):
    """The `github` context of one event GitHub would send card.yml."""
    if event == "schedule":
        e = {}
    elif event == "workflow_run":
        e = {"action": "completed", "sender": {"type": "Bot"}, "workflow_run": {"head_sha": "abc"}}
    else:
        e = {"action": action, "sender": {"type": sender},
             "issue": {"number": N, **({"pull_request": {"url": "u"}} if pr else {})}}
    return {"github": {"event_name": event, "event": e}}


def test_card_yml_starts_on_every_change_a_person_makes_and_on_a_schedule(record_property):
    """card.yml starts on a person's every change to an issue, and every 15 minutes.

    Reads .github/workflows/card.yml. Its issues trigger covers opening, editing, closing, reopening, labelling and
    assigning (or lists no types), and it has an issue_comment trigger for new, edited and deleted comments. Its job's
    `if:` lets every one of those through when a person causes it, lets the schedule, workflow_run and the bot opening
    an issue through as today (the bot's own edits and comments, and comments on a pull request, are #438's). Its
    schedule fires every hour of every day with no gap over 15 minutes, its step still runs `python3 dokima/card.py`
    with the event's issue as ISSUE_NUMBER, and it is given DOKIMA_BOARD so a loop on autopilot can set Needs you.
    Proves 254.4."""
    record_property("proves", "254.4")
    text = open(CARD_YML).read()
    on = on_block(text)
    issues = trigger(on, "issues")
    want = {"opened", "edited", "closed", "reopened", "labeled", "unlabeled", "assigned", "unassigned"}
    assert issues == "all" or (issues and want <= issues), \
        f"254.4: card.yml's issues trigger misses changes a person makes: {sorted(want - (issues or set()))}"
    comments = trigger(on, "issue_comment")
    assert comments == "all" or (comments and {"created", "edited", "deleted"} <= comments), \
        f"254.4: card.yml does not start on every comment on an issue (issue_comment trigger: {comments})"
    allowed = job_if(text)
    for kind in sorted(want):
        assert allowed(ctx("issues", kind)), f"254.4: card.yml's job skips a person's issues event {kind!r}"
    for kind in ("created", "edited", "deleted"):
        assert allowed(ctx("issue_comment", kind)), f"254.4: card.yml's job skips a person's comment ({kind}) on an issue"
    assert allowed(ctx("issues", "opened", sender="Bot")), \
        "254.4: card.yml's job no longer draws a card on an issue the bot opens"
    assert allowed(ctx("schedule")), "254.4: card.yml's job skips its scheduled run"
    assert allowed(ctx("workflow_run")), "254.4: card.yml's job skips workflow_run, the checks and worker finishing"
    assert re.search(r"^\s+schedule:", on, re.M), "254.4: card.yml has no schedule trigger"
    crons = re.findall(r"cron:\s*['\"]([^'\"]+)['\"]", on)
    assert crons, "254.4: card.yml's schedule has no cron"
    best = None
    for cron in crons:
        f = cron.split()
        if len(f) == 5 and f[1:] == ["*"] * 4:
            ms = minutes(f[0])
            gap = max((ms[(i + 1) % len(ms)] - ms[i]) % 60 or 60 for i in range(len(ms)))
            best = gap if best is None else min(best, gap)
    assert best is not None and best <= 15, f"254.4: card.yml's schedule {crons} leaves more than 15 minutes between runs"
    assert re.search(r"run:\s*python3 dokima/card\.py\s*$", text, re.M), "254.4: card.yml no longer runs dokima/card.py"
    assert re.search(r"ISSUE_NUMBER:\s*\$\{\{\s*github\.event\.issue\.number\s*\}\}", text), \
        "254.4: card.yml's step is not given the event's issue as ISSUE_NUMBER"
    assert re.search(r"DOKIMA_BOARD:\s*\$\{\{\s*vars\.DOKIMA_BOARD\s*\}\}", text), \
        "254.4: card.yml's step is not given DOKIMA_BOARD, so a loop cannot set Needs you"


# 254.5 ---------------------------------------------------------------------------------------------------------------

def test_the_scheduled_run_redraws_only_cards_whose_links_changed(tmp_path, record_property):
    """The scheduled run rewrites the cards whose links changed, and nothing when nothing changed.

    A person adds #252 blocked by #301 by hand: the scheduled run rewrites the cards of #252 and #301 (since #347 it
    also draws any card that does not show its issue's state, such as an issue with no card yet). The next scheduled
    run, with nothing changed, writes nothing on GitHub at all. Proves 254.5."""
    record_property("proves", "254.5")
    hub = HandHub(tmp_path)
    hub.set_links({N: [301]})
    hub.sweep("254.5")
    first = {w["issue"] for w in hub.writes("body")}
    assert {N, 301} <= first, f"254.5: the scheduled run should rewrite #252 and #301, it rewrote {sorted(first)}"
    count = len(hub.writes())
    hub.sweep("254.5")
    assert hub.writes()[count:] == [], f"254.5: a scheduled run with nothing changed wrote {hub.writes()[count:]}"


def test_a_run_for_one_issue_rewrites_no_other_card_whose_links_did_not_change(tmp_path, record_property):
    """A change on one issue rewrites another issue's card only when that card's links changed.

    A person adds #252 blocked by #301 by hand and changes #252: #301's card is rewritten, #302's and #303's are not.
    A second change on #252, a comment with no link changed, rewrites no card but #252's own. Proves 254.5."""
    record_property("proves", "254.5")
    hub = HandHub(tmp_path)
    hub.set_links({N: [301]})
    hub.event(N, "issues", "254.5")
    first = {w["issue"] for w in hub.writes("body")}
    assert 301 in first and not first & {302, 303}, \
        f"254.5: a change on #252 should rewrite #301's card and no unrelated one; it rewrote {sorted(first)}"
    count = len(hub.writes())
    hub.event(N, "issue_comment", "254.5")
    again = {w["issue"] for w in hub.writes()[count:] if w["op"] == "body"}
    assert again <= {N}, f"254.5: a change on #252 with no link changed rewrote other cards: {sorted(again - {N})}"

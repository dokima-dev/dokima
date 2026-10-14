"""The board's Blocker pill is computed from blocked-by links, never set by hand (#294).

An open issue that blocks at least one other open issue shows Priority Blocker. The board sync recomputes it when an
issue closes or reopens and on a schedule every 15 minutes (GitHub starts no workflow when a link is added or removed),
and no label moves the pill. Without Blocker, Priority is empty: no label sets priority.

Most tests fake dokima.board.Board itself and read the board's end state. What the fake Board offers, and the code is
expected to use (the first group exists today; the second is new):
    Board(spec, repo, q, rest)          the board
    .fields                             {"Status": ..., "Action": ..., "Priority": (id, {option: id})}
    .item(kind, n) / .set(item, field, option or None) / .value(item, field)
    .autopilot(kind, n) / .open_pr(n) / .parent(n) / .label(kind, n, on) / .views() / .add_view(...)

    .blocking(n) -> [{"number", "state"}]     the issues n blocks, each with its state ("open" or "closed")
    .blocked_by(n) -> [{"number", "state"}]   the issues blocking n, each with its state
    .open_issues() -> [n, ...]                every open issue of the repo, pull requests left out
    .labels(kind, n) -> {name, ...}           the labels the issue carries

The new reads raise subprocess.CalledProcessError when GitHub refuses, as Board's REST calls do today. The last tests
run the real Board against a faked GitHub, so those reads truly reach GitHub's issue dependencies API
(repos/{owner}/{repo}/issues/{n}/dependencies/blocking and .../blocked_by, the same API dokima/agent.py reads).
"""
import json
import os
import re
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, board  # noqa: E402
from dokima import agent_github  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "board.yml")
SPEC, REPO = "dokima-dev/1", "o/r"
SCHEDULE = {"schedule": "*/15 * * * *"}


class World:
    """The GitHub the fake board sees: issues, their labels, blocked-by links and card fields."""

    def __init__(self, issues, links=(), cards=None, fail=(), priority_field=True):
        # issues: {n: ("open" | "closed", [labels])}; links: (a, b) means #a is blocked by #b.
        self.issues = {n: {"state": s, "labels": set(ls)} for n, (s, ls) in issues.items()}
        self.links = set(links)
        self.cards = {("issue", n): dict(c) for n, c in (cards or {}).items()}
        self.fail = set(fail)
        self.priority_field = priority_field
        self.writes, self.reads = [], []

    def pill(self, n):
        """The Priority pill on the issue's card, or None."""
        return self.cards.get(("issue", n), {}).get("Priority")

    def deps(self, n, side):
        self.reads.append((side, n))
        if n in self.fail:
            raise subprocess.CalledProcessError(1, ["gh", "api"], stderr="HTTP 502: Bad Gateway")
        pairs = [(a, b) for a, b in self.links if (b if side == "blocking" else a) == n]
        other = [(a if side == "blocking" else b) for a, b in pairs]
        return [{"number": m, "state": self.issues[m]["state"]} for m in sorted(other)]


def fake_board(world):
    """A stand-in for dokima.board.Board that reads and writes the world."""

    class FakeBoard:
        def __init__(self, *a, **k):
            self.fields = {"Status": ("S", {o: "s-" + o for o in ("Backlog", "Plan", "Work", "Review", "Done")}),
                           "Action": ("W", {"Needs you": "w-you", "Autopilot": "w-auto"})}
            if world.priority_field:
                self.fields["Priority"] = ("PRI", {o: "p-" + o for o in ("Blocker",)})

        def item(self, kind, n):
            world.cards.setdefault((kind, int(n)), {})
            return (kind, int(n))

        def set(self, iid, field, option):
            if field not in self.fields:
                return
            world.writes.append((iid, field, option))
            card = world.cards.setdefault(iid, {})
            if option is None:
                card.pop(field, None)
            elif option in self.fields[field][1]:
                card[field] = option

        def value(self, iid, field):
            return world.cards.get(iid, {}).get(field)

        def autopilot(self, kind, n):
            return False

        def open_pr(self, n):
            return None

        def parent(self, n):
            return None

        def label(self, kind, n, on):
            pass

        def views(self):
            return ["Autopilot"]

        def add_view(self, *a):
            pass

        def labels(self, kind, n):
            return set(world.issues[int(n)]["labels"])

        def blocking(self, n):
            return world.deps(int(n), "blocking")

        def blocked_by(self, n):
            return world.deps(int(n), "blocked_by")

        def state(self, kind, n):
            return world.issues[int(n)]["state"] if int(n) in world.issues else "open"

        def cards(self):
            return [{"kind": k, "number": n, "status": c.get("Status"), "action": c.get("Action"),
                     "closed": world.issues.get(n, {}).get("state") == "closed", "autopilot": False}
                    for (k, n), c in sorted(world.cards.items())]

        def open_issues(self):
            world.reads.append(("open_issues", None))
            return sorted(n for n, i in world.issues.items() if i["state"] == "open")

    return FakeBoard


@pytest.fixture
def make(monkeypatch):
    """Wire a world into dokima.board.Board and return it."""

    def wire(**kw):
        world = World(**kw)
        monkeypatch.setattr(board, "Board", fake_board(world))
        # Each issue has no record yet, so the board's recompute of its column reads no network.
        monkeypatch.setattr(agent_github, "gh", lambda *a: json.dumps({"number": int(a[2]), "title": "", "body": "", "comments": []})
                            if a[:2] == ("issue", "view") else "[]")
        return world

    return wire


def issue_event(action, n, world, label=None):
    """An issues payload for #n as GitHub sends it, with labels after the change."""
    p = {"action": action, "issue": {"number": n, "state": world.issues[n]["state"],
                                     "labels": [{"name": l} for l in sorted(world.issues[n]["labels"])]}}
    if label:
        p["label"] = {"name": label}
    return p


def priority_writes(world):
    return [(iid[1], option) for iid, field, option in world.writes if field == "Priority"]


# 294.1: an open issue that blocks an open issue shows Blocker, computed from its links

def test_an_issue_blocking_an_open_issue_gets_the_blocker_pill(record_property, make):
    """Only an open issue that blocks another open issue gets the Blocker pill.

    Proves 294.1. Runs the scheduled board sync over five open issues: #10 blocks open #11, #12 blocks only closed #13, #14 blocks
    nothing, #15 is blocked by #10 and labeled high, and #16 labeled high blocks open #11. Checks #10 and #16 show
    Blocker, and #12, #14 and #15 show no pill: the high label sets nothing."""
    record_property("proves", "294.1")
    w = make(issues={10: ("open", []), 11: ("open", []), 12: ("open", []), 13: ("closed", []), 14: ("open", []),
                     15: ("open", ["high"]), 16: ("open", ["high"])},
             links=[(11, 10), (13, 12), (15, 10), (11, 16)])
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    got = {n: w.pill(n) for n in (10, 12, 14, 15, 16)}
    assert got == {10: "Blocker", 12: None, 14: None, 15: None, 16: "Blocker"}, \
        f"294.1: after the scheduled sync the pills are {got}; only open issues blocking an open issue show Blocker, " \
        f"and the rest show none, whatever their labels"


def test_the_scheduled_sync_writes_only_pills_that_change(record_property, make):
    """The scheduled sync writes a card's Priority only when its pill changes.

    Proves 294.1. Runs the scheduled sync on a board already right (#20 shows Blocker and blocks open #21, #21, labeled high, shows
    no pill) and checks nothing is written to Priority; then on one wrong card (#22 blocks open #21 but shows nothing)
    and checks the only write is Blocker on #22."""
    record_property("proves", "294.1")
    w = make(issues={20: ("open", []), 21: ("open", ["high"])}, links=[(21, 20)],
             cards={20: {"Priority": "Blocker"}})
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert priority_writes(w) == [], f"294.1: the scheduled sync rewrote pills that were already right: {priority_writes(w)}"
    w = make(issues={20: ("open", []), 21: ("open", ["high"]), 22: ("open", [])}, links=[(21, 20), (21, 22)],
             cards={20: {"Priority": "Blocker"}})
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert priority_writes(w) == [(22, "Blocker")], \
        f"294.1: with only #22 wrong, the scheduled sync wrote {priority_writes(w)}, not Blocker on #22 alone"


# 294.2: when the last issue it blocks closes, the pill goes away in the same run; a reopen brings it back

def test_closing_the_last_blocked_issue_clears_the_pill(record_property, make):
    """Closing the last open issue it blocks clears an issue's Blocker pill at once.

    Proves 294.2. #30 blocks #31 only; #32 blocks #31 and #33; #34, labeled high, blocks #31 only. #31 closes. Checks #30's pill
    is cleared, #32 keeps Blocker (it still blocks open #33), and #34's is cleared too: its high label sets nothing."""
    record_property("proves", "294.2")
    w = make(issues={30: ("open", []), 31: ("closed", []), 32: ("open", []), 33: ("open", []), 34: ("open", ["high"])},
             links=[(31, 30), (31, 32), (33, 32), (31, 34)],
             cards={30: {"Priority": "Blocker"}, 32: {"Priority": "Blocker"}, 34: {"Priority": "Blocker"}})
    board.sync("issues", issue_event("closed", 31, w), SPEC, REPO)
    got = {n: w.pill(n) for n in (30, 32, 34)}
    assert got == {30: None, 32: "Blocker", 34: None}, \
        f"294.2: after #31 closed the pills are {got}; #30 and #34 should lose Blocker and #32 keep it"


def test_a_closed_issue_loses_its_own_blocker_pill(record_property, make):
    """An issue that closes loses its own Blocker pill, even while it still blocks.

    Proves 294.2. #40 shows Blocker and blocks open #41, then #40 closes. Checks #40's pill is cleared, since only open issues are
    blockers, and its card still moves to Done."""
    record_property("proves", "294.2")
    w = make(issues={40: ("closed", []), 41: ("open", [])}, links=[(41, 40)], cards={40: {"Priority": "Blocker"}})
    board.sync("issues", issue_event("closed", 40, w), SPEC, REPO)
    assert w.pill(40) is None, f"294.2: the closed issue #40 still shows {w.pill(40)}"
    assert w.cards[("issue", 40)].get("Status") == "Done", "294.2: closing #40 no longer moves its card to Done"


def test_reopening_an_issue_brings_the_pill_back(record_property, make):
    """Reopening an issue brings Blocker back on the issues blocking it.

    Proves 294.2. #50 blocks #51 only and shows no pill; #51 blocks open #52. #51 reopens. Checks #50 and #51 both show Blocker."""
    record_property("proves", "294.2")
    w = make(issues={50: ("open", []), 51: ("open", []), 52: ("open", [])}, links=[(51, 50), (52, 51)])
    board.sync("issues", issue_event("reopened", 51, w), SPEC, REPO)
    got = {n: w.pill(n) for n in (50, 51)}
    assert got == {50: "Blocker", 51: "Blocker"}, f"294.2: after #51 reopened the pills are {got}, not Blocker on both"


def test_the_workflow_runs_on_close_and_reopen(record_property):
    """The board workflow runs when an issue closes or reopens.

    Proves 294.2. Reads the issues triggers of the board workflow and checks they include closed and reopened."""
    record_property("proves", "294.2")
    found = re.search(r"^  issues:\n    types: \[([^\]]*)\]", open(WORKFLOW).read(), re.M)
    assert found, "294.2: the board workflow no longer runs on issue events"
    types = [t.strip() for t in found.group(1).split(",")]
    assert "closed" in types and "reopened" in types, \
        f"294.2: the board workflow's issue triggers are {types}; a close or reopen never reaches the pill"


# 294.3: a link added or removed, by hand or by code, reaches the pill within 15 minutes

def test_a_link_added_or_removed_reaches_the_pill_on_the_next_scheduled_run(record_property, make):
    """A blocked-by link added or removed reaches the pill on the next scheduled run.

    Proves 294.3. Starts with no links and no pills, adds the link #61 blocked by #60 and runs the scheduled sync: #60 shows
    Blocker. Removes the link and runs it again: #60 loses the pill, and still has none with the high label on it."""
    record_property("proves", "294.3")
    w = make(issues={60: ("open", []), 61: ("open", [])})
    w.links.add((61, 60))
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert w.pill(60) == "Blocker", f"294.3: after the link was added, #60 shows {w.pill(60)}, not Blocker"
    w.links.clear()
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert w.pill(60) is None, f"294.3: after the link was removed, #60 still shows {w.pill(60)}"
    w.links.add((61, 60))
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    w.links.clear()
    w.issues[60]["labels"].add("high")
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert w.pill(60) is None, f"294.3: with the link removed and the high label on, #60 shows {w.pill(60)}, not none"


def test_the_workflow_runs_every_15_minutes(record_property):
    """The board workflow runs on a schedule every 15 minutes.

    Proves 294.3. Reads the board workflow and checks it has a schedule trigger with the cron */15 * * * *."""
    record_property("proves", "294.3")
    text = open(WORKFLOW).read()
    found = re.search(r"^  schedule:\n((?:    - cron: .*\n)+)", text, re.M)
    assert found, "294.3: the board workflow has no schedule trigger, so a link changed by hand never reaches the pill"
    crons = re.findall(r"cron: ['\"]([^'\"]+)['\"]", found.group(1))
    assert crons == ["*/15 * * * *"], f"294.3: the board workflow's schedule is {crons}, not every 15 minutes"


def test_without_a_board_or_priority_field_nothing_is_read(record_property, make, monkeypatch):
    """Without a board or a Priority field, the scheduled sync reads and writes nothing.

    Proves 294.3. First checks a board with a Priority field does get Blocker, so the rest is not passing by doing nothing. Then
    runs the scheduled sync with no board set and a Board that fails if built, and against a board with no Priority
    field, checking no link is read and no field is written."""
    record_property("proves", "294.3")
    w = make(issues={70: ("open", []), 71: ("open", [])}, links=[(71, 70)])
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert w.pill(70) == "Blocker", "294.3: a board with a Priority field did not get Blocker"
    w = make(issues={70: ("open", []), 71: ("open", [])}, links=[(71, 70)], priority_field=False)
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert w.writes == [] and w.reads == [], f"294.3: a board with no Priority field was read {w.reads} and written {w.writes}"

    def explode(*a, **k):
        raise AssertionError("294.3: the board was built with no board set")
    monkeypatch.setattr(board, "Board", explode)
    assert board.sync("schedule", SCHEDULE, "", REPO) == []
    assert board.sync("issues", {"action": "reopened", "issue": {"number": 70, "labels": []}}, "", REPO) == []


# 294.4: no one sets or clears it by hand

def test_the_blocker_label_no_longer_moves_the_pill(record_property, make):
    """No label sets or clears the pill: only the links do.

    Proves 294.4. Adds the blocker label to #80, which blocks nothing, and checks it shows no Blocker. Removes the blocker label
    from #81, which blocks open #82 and shows Blocker, and checks it keeps Blocker. Adds the high label to #81 and
    checks it still shows Blocker, then adds high to #80 and checks it still shows no pill."""
    record_property("proves", "294.4")
    w = make(issues={80: ("open", ["blocker"]), 81: ("open", []), 82: ("open", [])}, links=[(82, 81)],
             cards={81: {"Priority": "Blocker"}})
    board.sync("issues", issue_event("labeled", 80, w, label="blocker"), SPEC, REPO)
    assert w.pill(80) is None, f"294.4: adding the blocker label to #80, which blocks nothing, set {w.pill(80)}"
    board.sync("issues", issue_event("unlabeled", 81, w, label="blocker"), SPEC, REPO)
    assert w.pill(81) == "Blocker", f"294.4: removing the blocker label from #81, which blocks #82, left {w.pill(81)}"
    w.issues[81]["labels"].add("high")
    board.sync("issues", issue_event("labeled", 81, w, label="high"), SPEC, REPO)
    assert w.pill(81) == "Blocker", f"294.4: adding high to #81, which blocks #82, replaced Blocker with {w.pill(81)}"
    w.issues[80]["labels"].add("high")
    board.sync("issues", issue_event("labeled", 80, w, label="high"), SPEC, REPO)
    assert w.pill(80) is None, f"294.4: adding high to #80, which blocks nothing, set {w.pill(80)}"


def test_a_blocker_pill_set_by_hand_is_corrected(record_property, make):
    """A Blocker pill set or cleared by hand is fixed by the next scheduled run.

    Proves 294.4. #90 blocks nothing but shows Blocker, set by hand; #91 blocks open #92 but someone cleared its pill. Runs the
    scheduled sync and checks #90 shows no pill and #91 shows Blocker."""
    record_property("proves", "294.4")
    w = make(issues={90: ("open", []), 91: ("open", []), 92: ("open", [])}, links=[(92, 91)],
             cards={90: {"Priority": "Blocker"}})
    board.sync("schedule", SCHEDULE, SPEC, REPO)
    got = {n: w.pill(n) for n in (90, 91)}
    assert got == {90: None, 91: "Blocker"}, f"294.4: after the scheduled sync the pills are {got}, not none on #90 and Blocker on #91"


def test_dokima_no_longer_declares_a_blocker_label(record_property):
    """Dokima declares no label that sets priority: no blocker, high or parked label.

    Proves 294.4. Checks the manifest's labels leave out blocker, high and parked, and that Blocker is the Priority
    field's only option."""
    record_property("proves", "294.4")
    from dokima import manifest
    assert "blocker" not in manifest.LABELS, "294.4: the manifest still declares a blocker label to set by hand"
    assert "high" not in manifest.LABELS and "parked" not in manifest.LABELS, "294.4: the manifest still has a high or parked label"
    assert set(manifest.FIELDS["Priority"]) == {"Blocker"}, f"294.4: Priority's options are {list(manifest.FIELDS['Priority'])}, not Blocker alone"


# 294.5: when GitHub cannot list an issue's links, its pill stays and the run fails saying why

def test_unread_links_leave_the_pill_and_fail_the_run(record_property, make):
    """Unread links leave the pill as it is, and the run fails naming the issue.

    Proves 294.5. #100 shows Blocker and GitHub fails to list what it blocks; #101 blocks open #102 and shows nothing. The
    scheduled sync must still give #101 Blocker, keep #100's Blocker, and then fail with a message naming #100 and
    GitHub's answer. Then #103 closes and GitHub fails to list what blocks it: the run fails naming #103."""
    record_property("proves", "294.5")
    w = make(issues={100: ("open", []), 101: ("open", []), 102: ("open", [])}, links=[(102, 101)],
             cards={100: {"Priority": "Blocker"}}, fail=[100])
    with pytest.raises(RuntimeError) as e:
        board.sync("schedule", SCHEDULE, SPEC, REPO)
    assert "#100" in str(e.value) and "502" in str(e.value), \
        f"294.5: the failed run says {str(e.value)!r}, not naming #100 and GitHub's answer"
    assert w.pill(100) == "Blocker", f"294.5: #100's links could not be read, yet its pill became {w.pill(100)}"
    assert w.pill(101) == "Blocker", f"294.5: one unread issue stopped #101 from getting Blocker: {w.pill(101)}"
    w = make(issues={103: ("closed", []), 104: ("open", [])}, links=[(103, 104)], cards={104: {"Priority": "Blocker"}},
             fail=[103])
    with pytest.raises(RuntimeError) as e:
        board.sync("issues", issue_event("closed", 103, w), SPEC, REPO)
    assert "#103" in str(e.value), f"294.5: the failed close run says {str(e.value)!r}, not naming #103"
    assert w.pill(104) == "Blocker", f"294.5: with #103's links unread, #104's pill became {w.pill(104)}"


def test_main_reports_the_failure_and_exits_1(record_property, make, monkeypatch, tmp_path, capsys):
    """The scheduled board run with unread links exits 1 with an error saying why.

    Proves 294.5. Runs dokima.board's main as the scheduled workflow does, with GitHub failing to list #110's links, and checks it
    returns 1 and prints a ::error:: line naming #110."""
    record_property("proves", "294.5")
    make(issues={110: ("open", []), 111: ("open", [])}, links=[(111, 110)], fail=[110])
    event = tmp_path / "event.json"
    event.write_text('{"schedule": "*/15 * * * *"}')
    monkeypatch.setenv("DOKIMA_BOARD", SPEC)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    code = board.main()
    out = capsys.readouterr().out
    assert code == 1, f"294.5: the run with unread links exited {code}, not 1"
    assert "::error::" in out and "#110" in out, f"294.5: the run printed {out!r}, not an error naming #110"


# The real Board reads the links, open issues and labels from GitHub

class FakeGitHub:
    """GitHub's GraphQL and REST answers for repo o/r and a board with Priority."""

    ISSUES = {5: {"state": "open", "labels": ["high", "bug"]}, 6: {"state": "open", "labels": []},
              7: {"state": "closed", "labels": []}}
    LINKS = [(6, 5), (7, 5)]  # #6 and #7 are blocked by #5

    def __init__(self):
        self.calls = []

    def q(self, query, **v):
        self.calls.append(("graphql", query, v))
        if "organization" in query:
            return {"organization": {"projectV2": {"id": "P", "fields": {"nodes": [
                {"id": "PRI", "name": "Priority", "options": [{"id": "p-" + o, "name": o} for o in ("Blocker",)]}]}}}}
        if "repository" in query and "labels" in query:
            n = int(v.get("n"))
            labels = {"nodes": [{"name": l} for l in self.ISSUES[n]["labels"]]}
            return {"repository": {"issue": {"labels": labels}, "pullRequest": {"labels": labels}}}
        return {}

    def issue(self, n):
        return {"id": 1000 + n, "number": n, "state": self.ISSUES[n]["state"],
                "labels": [{"name": l} for l in self.ISSUES[n]["labels"]]}

    def rest(self, method, path, **fields):
        self.calls.append(("rest", method, path, fields))
        path = path.lstrip("/").split("?")[0]
        m = re.fullmatch(r"repos/o/r/issues/(\d+)/dependencies/(blocking|blocked_by)", path)
        if m and method == "GET":
            n, side = int(m.group(1)), m.group(2)
            other = [a if side == "blocking" else b for a, b in self.LINKS if (b if side == "blocking" else a) == n]
            return [self.issue(x) for x in sorted(other)]
        m = re.fullmatch(r"repos/o/r/issues/(\d+)", path)
        if m and method == "GET":
            return self.issue(int(m.group(1)))
        if path == "repos/o/r/issues" and method == "GET":
            pr = {"id": 2009, "number": 9, "state": "open", "labels": [], "pull_request": {"url": "x"}}
            return [self.issue(n) for n, i in self.ISSUES.items() if i["state"] == "open"] + [pr]
        raise AssertionError(f"unexpected GitHub call {method} {path}")


def test_the_real_board_reads_links_open_issues_and_labels_from_github(record_property):
    """The board reads blocked-by links, open issues and labels from GitHub itself.

    Proves 294.1. Builds the real Board against a faked GitHub where #5 (labeled high and bug) blocks open #6 and closed #7, and
    pull request #9 is open. Checks blocking(5) names #6 open and #7 closed, blocked_by(6) names #5, open_issues()
    is #5 and #6 without the pull request, and labels() of #5 is high and bug."""
    record_property("proves", "294.1")
    gh = FakeGitHub()
    b = board.Board(SPEC, REPO, q=gh.q, rest=gh.rest)
    got = sorted((i["number"], i["state"]) for i in b.blocking(5))
    assert got == [(6, "open"), (7, "closed")], f"294.1: the board read #5 as blocking {got}, not #6 open and #7 closed"
    got = sorted(i["number"] for i in b.blocked_by(6))
    assert got == [5], f"294.1: the board read #6 as blocked by {got}, not #5"
    assert sorted(b.open_issues()) == [5, 6], f"294.1: the board read the open issues as {b.open_issues()}, not #5 and #6"
    assert set(b.labels("issue", 5)) == {"high", "bug"}, f"294.1: the board read #5's labels as {b.labels('issue', 5)}"


def test_the_real_board_says_when_github_refuses_the_links(record_property):
    """When GitHub refuses the links, the board's read fails instead of answering none.

    Proves 294.5. Builds the real Board against a GitHub whose dependency calls fail, and checks blocking() raises rather than
    returning an empty list that would clear a real Blocker."""
    record_property("proves", "294.5")
    gh = FakeGitHub()

    def refuse(method, path, **fields):
        if "dependencies" in path:
            raise subprocess.CalledProcessError(1, ["gh", "api", path], stderr="HTTP 502: Bad Gateway")
        return gh.rest(method, path, **fields)
    b = board.Board(SPEC, REPO, q=gh.q, rest=refuse)
    with pytest.raises(Exception) as e:
        b.blocking(5)
    assert not isinstance(e.value, AttributeError), "294.5: the board has no blocking() read yet"

"""The board shows what runs on autopilot: an Autopilot pill, Needs you in its place when the river stops, one view (#210).

The first ten tests fake dokima.board.Board itself, so they read the board's end state, never the GraphQL queries
that reach it. The tests at the end run the real Board against a faked GitHub, so the new reads and writes below truly
reach GitHub. The fake keeps, in memory, one world shared with a fake `gh`:

- cards: each card's Status and Action (the single-select field holding "Needs you" and now "Autopilot");
- labels: the labels each issue and pull request carries; `autopilot` is autopilot's state (story 1, #209);
- the open pull request of each issue (branch try/issue-N, body "Closes #N");
- the parent issue of each sub-issue;
- the board's views by name.

What the fake Board offers, and the code is expected to use:
    Board(spec, repo, q)               the board, as today
    .fields                            {"Status": (id, {option: id}), "Action": (id, {option: id})}, as today
    .item(kind, n) -> item id          as today; kind is "issue" or "pr"
    .set(item, field, option or None)  as today: an unknown field or option is ignored, None clears
    .value(item, field) -> option      the card's current option of that field, or None
    .autopilot(kind, n) -> bool        whether that issue or pull request carries the `autopilot` label
    .open_pr(n) -> number or None      the open pull request built for issue n
    .parent(n) -> number or None       the issue's parent issue (GitHub's native sub-issues), or None
    .label(kind, n, on)                put the `autopilot` label on (True) or off (False) that issue or pull request
    .views() -> [name, ...]            the board's views
    .add_view(name, layout, filter)    add a view to the board

The fake `gh` answers `pr list` (the issue's open pull request), `issue view` and `api repos/o/r/issues/N` (with
labels), `issue create`, sub-issue and blocked-by links, and labels added through `issue create --label`,
`issue edit --add-label/--remove-label` or the REST labels API, all against the same world.
"""
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, board  # noqa: E402
from test_agent import GOOD_REVIEW, SPLIT, rec  # noqa: E402

LABEL = "autopilot"
SPEC, REPO = "dokima-dev/1", "dokima-dev/dokima"
BOT, YOU = {"type": "Bot"}, {"type": "User"}


class World:
    """The GitHub the board and `gh` both see: cards, labels, open pull requests and views."""

    def __init__(self, labels=None, prs=None, cards=None, views=("Needs you",), options=("Needs you", "Autopilot"), parents=None):
        self.labels = {k: set(v) for k, v in (labels or {}).items()}
        self.parents = dict(parents or {})
        self.prs = dict(prs or {})
        self.cards = {k: dict(v) for k, v in (cards or {}).items()}
        self.view_list = [{"name": v, "layout": "table", "filter": ""} for v in views]
        self.options = options
        self.created = 200
        self.calls = []

    def action(self, kind, n):
        """The card's Action pill: "Needs you", "Autopilot" or None."""
        return self.cards.get((kind, n), {}).get("Action")

    def status(self, kind, n):
        return self.cards.get((kind, n), {}).get("Status")

    def has(self, kind, n):
        return LABEL in self.labels.get((kind, n), set())

    def put(self, kind, n, on):
        s = self.labels.setdefault((kind, n), set())
        s.add(LABEL) if on else s.discard(LABEL)


def fake_board(world):
    """A stand-in for dokima.board.Board that reads and writes the world."""

    class FakeBoard:
        def __init__(self, *a, **k):
            self.fields = {"Status": ("S", {o: "s-" + o for o in ("Backlog", "Plan", "Work", "Review", "Done")}),
                           "Action": ("W", {o: "w-" + o for o in world.options})}

        def item(self, kind, n):
            world.cards.setdefault((kind, int(n)), {})
            return (kind, int(n))

        def set(self, iid, field, option):
            if field not in self.fields:
                return
            card = world.cards.setdefault(iid, {})
            if option is None:
                card.pop(field, None)
            elif option in self.fields[field][1]:
                card[field] = option

        def value(self, iid, field):
            return world.cards.get(iid, {}).get(field)

        def autopilot(self, kind, n):
            return world.has(kind, int(n))

        def open_pr(self, n):
            return world.prs.get(int(n))

        def parent(self, n):
            return world.parents.get(int(n))

        def label(self, kind, n, on):
            world.put(kind, int(n), on)

        def views(self):
            return [v["name"] for v in world.view_list]

        def add_view(self, name, layout, filter):
            world.view_list.append({"name": name, "layout": layout, "filter": filter})

    return FakeBoard


def fake_gh(world):
    """A stand-in for agent.gh that answers from the world."""

    def gh(*args):
        world.calls.append(args)
        a = list(args)
        if a[:2] == ["pr", "list"]:
            head = a[a.index("--head") + 1]
            n = world.prs.get(int(head.rsplit("-", 1)[1]))
            return f"{n}\n" if n else "\n"
        if a[:2] == ["issue", "view"]:
            n = int(a[2])
            return json.dumps({"number": n, "title": "Parent", "body": "", "comments": [],
                               "labels": [{"name": l} for l in sorted(world.labels.get(("issue", n), set()))]})
        if a[:2] == ["issue", "create"]:
            world.created += 1
            n = world.created
            if "--label" in a and LABEL in a[a.index("--label") + 1].split(","):
                world.put("issue", n, True)
            return f"https://github.com/o/r/issues/{n}\n"
        if a[:2] == ["issue", "edit"]:
            n = int(a[2])
            if "--add-label" in a and LABEL in a[a.index("--add-label") + 1].split(","):
                world.put("issue", n, True)
            if "--remove-label" in a and LABEL in a[a.index("--remove-label") + 1].split(","):
                world.put("issue", n, False)
            return ""
        if a[:1] == ["api"]:
            path = next((x for x in a[1:] if x.lstrip("/").startswith("repos/")), "").lstrip("/")
            method = a[a.index("-X") + 1].upper() if "-X" in a else ("POST" if any(x in ("-f", "-F") for x in a) else "GET")
            m_lab = re.fullmatch(r"repos/o/r/issues/(\d+)/labels(?:/(.+))?", path)
            if m_lab:
                n = int(m_lab.group(1))
                if method == "DELETE":
                    world.put("issue", n, False)
                elif method in ("POST", "PUT") and any(x in (f"labels[]={LABEL}", f"labels={LABEL}") for x in a):
                    world.put("issue", n, True)
                return "[]"
            m_iss = re.fullmatch(r"repos/o/r/issues/(\d+)", path)
            if m_iss and method == "GET":
                n = int(m_iss.group(1))
                return json.dumps({"id": 9000 + n, "number": n,
                                   "labels": [{"name": l} for l in sorted(world.labels.get(("issue", n), set()))]})
            return "{}"
        return ""

    return gh


@pytest.fixture
def make(monkeypatch):
    """Wire a world into dokima.board.Board and dokima.agent.gh, and return it."""

    def wire(**kw):
        world = World(**kw)
        monkeypatch.setattr(board, "Board", fake_board(world))
        monkeypatch.setattr(agent, "gh", fake_gh(world))
        return world

    return wire


def label_event(action, name, labels, number=57):
    """An issues labeled/unlabeled payload; labels are the issue's labels after the change, as GitHub sends them."""
    return {"action": action, "label": {"name": name}, "issue": {"number": number, "labels": [{"name": n} for n in labels]}}


def comment_event(number, body, labels, user=BOT):
    return {"action": "created", "issue": {"number": number, "labels": [{"name": n} for n in labels]},
            "comment": {"user": user, "body": body}}


def pr_event(action, number, issue):
    return {"action": action, "pull_request": {"number": number, "body": f"Closes #{issue}", "merged": False,
                                               "head": {"ref": f"try/issue-{issue}"}, "labels": []}}


# 210.1: every card in a tree on autopilot shows the Autopilot pill, and loses it once off autopilot

def test_switching_autopilot_on_puts_the_pill_on_the_issue_and_its_pull_request(record_property, make):
    """Switching an issue on autopilot puts the Autopilot pill on its card and its open pull request's card.

    The `autopilot` label is added to #57 (open PR #60) and to #101 (no PR), as `/autopilot start` does for every issue
    in a tree; each label event reaches the board sync. Both issue cards and PR #60 show Autopilot and no card's stage
    moves. A `bug` label on #58, which is not on autopilot, puts no Autopilot pill anywhere."""
    record_property("proves", "210.1")
    w = make(labels={("issue", 57): {LABEL}, ("issue", 101): {LABEL}}, prs={57: 60},
             cards={("issue", 57): {"Status": "Plan"}, ("pr", 60): {"Status": "Review"}, ("issue", 101): {"Status": "Backlog"}})
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 57), SPEC, REPO)
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 101), SPEC, REPO)
    for kind, n in (("issue", 57), ("pr", 60), ("issue", 101)):
        assert w.action(kind, n) == "Autopilot", f"210.1: {kind} #{n} on autopilot shows {w.action(kind, n)!r}, not the Autopilot pill"
    assert (w.status("issue", 57), w.status("pr", 60), w.status("issue", 101)) == ("Plan", "Review", "Backlog"), \
        "210.1: switching autopilot on moved a card to another column"
    w.labels[("issue", 58)] = {"bug"}
    w.cards[("issue", 58)] = {"Status": "Plan"}
    board.sync("issues", label_event("labeled", "bug", ["bug"], 58), SPEC, REPO)
    assert w.action("issue", 58) is None, "210.1: an issue that is not on autopilot got the Autopilot pill"


def test_switching_autopilot_off_takes_the_pill_away(record_property, make):
    """Switching an issue off autopilot takes the Autopilot pill off its card and its open pull request's card.

    #57 and its PR #60 show Autopilot; the `autopilot` label is removed from #57, as `/autopilot stop` does. Both
    cards end with no pill and stay in their columns."""
    record_property("proves", "210.1")
    w = make(labels={("issue", 57): set(), ("pr", 60): {LABEL}}, prs={57: 60},
             cards={("issue", 57): {"Status": "Work", "Action": "Autopilot"}, ("pr", 60): {"Status": "Review", "Action": "Autopilot"}})
    board.sync("issues", label_event("unlabeled", LABEL, [], 57), SPEC, REPO)
    assert w.action("issue", 57) is None, f"210.1: issue #57 off autopilot still shows {w.action('issue', 57)!r}"
    assert w.action("pr", 60) is None, f"210.1: PR #60, whose issue is off autopilot, still shows {w.action('pr', 60)!r}"
    assert (w.status("issue", 57), w.status("pr", 60)) == ("Work", "Review"), "210.1: switching autopilot off moved a card"


def test_stage_moments_keep_the_pill_on_issues_on_autopilot_only(record_property, make):
    """When the board moves a card to the next stage, a card on autopilot keeps its Autopilot pill; others get none.

    Runs the board sync's stage moments (the work label, a pull request opened, changes requested) for #57, on autopilot
    with PR #60, and for #58, not on autopilot, with PR #61. Every #57 and #60 card ends in the new column with
    Autopilot; every #58 and #61 card ends in the new column with no pill."""
    record_property("proves", "210.1")
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}, ("issue", 58): set()}, prs={57: 60, 58: 61})
    board.sync("issues", label_event("labeled", "work", [LABEL, "work"], 57), SPEC, REPO)
    board.sync("issues", label_event("labeled", "work", ["work"], 58), SPEC, REPO)
    assert (w.status("issue", 57), w.action("issue", 57)) == ("Work", "Autopilot"), \
        f"210.1: #57 on autopilot moved to Work shows {w.action('issue', 57)!r}, not Autopilot"
    assert (w.status("issue", 58), w.action("issue", 58)) == ("Work", None), "210.1: #58, not on autopilot, got a pill"
    board.sync("pull_request_target", pr_event("opened", 60, 57), SPEC, REPO)
    board.sync("pull_request_target", pr_event("opened", 61, 58), SPEC, REPO)
    for kind, n in (("pr", 60), ("issue", 57)):
        assert (w.status(kind, n), w.action(kind, n)) == ("Review", "Autopilot"), \
            f"210.1: {kind} #{n} on autopilot in Review shows {w.action(kind, n)!r}, not Autopilot"
    for kind, n in (("pr", 61), ("issue", 58)):
        assert (w.status(kind, n), w.action(kind, n)) == ("Review", None), f"210.1: {kind} #{n}, not on autopilot, got a pill"
    review = {"action": "submitted", "review": {"state": "changes_requested"}, "pull_request": {"number": 60, "body": "Closes #57"}}
    board.sync("pull_request_review", review, SPEC, REPO)
    assert (w.status("pr", 60), w.action("pr", 60)) == ("Work", "Autopilot"), "210.1: PR #60 sent back to Work lost its Autopilot pill"


def test_the_river_keeps_the_pill_when_it_moves_a_card_on_autopilot(record_property, make):
    """When the river starts the next stage, the issue and its pull request keep the Autopilot pill while on autopilot.

    Calls the river's card move (agent.move_card, as `agent board` does after every run) for #57, on autopilot with
    open PR #60, and for #58, not on autopilot, with open PR #61. #57 and #60 land in Review with Autopilot; #58 and
    #61 land in Review with no pill."""
    record_property("proves", "210.1")
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}, ("issue", 58): set()}, prs={57: 60, 58: 61})
    agent.move_card("o/r", "57", "Review", False, "o/1")
    agent.move_card("o/r", "58", "Review", False, "o/1")
    for kind, n in (("issue", 57), ("pr", 60)):
        assert (w.status(kind, n), w.action(kind, n)) == ("Review", "Autopilot"), \
            f"210.1: the river moved {kind} #{n}, on autopilot, and it shows {w.action(kind, n)!r}, not Autopilot"
    for kind, n in (("issue", 58), ("pr", 61)):
        assert (w.status(kind, n), w.action(kind, n)) == ("Review", None), f"210.1: the river gave {kind} #{n}, not on autopilot, a pill"


# 210.2: children filed by a split under a parent on autopilot are on autopilot too

def split_main(monkeypatch, w, parent=139):
    """Run `agent split PARENT` for an approved split, the way the /work command does, against the world."""
    recs = [rec("planner", handback=SPLIT), rec("reviewer", "plan", {**GOOD_REVIEW, "verdict": "approve", "blockers": []})]
    monkeypatch.setattr(agent, "conversation", lambda repo, n: ({}, []))
    monkeypatch.setattr(agent, "records", lambda items: list(recs))
    monkeypatch.setenv("GITHUB_REPOSITORY", "o/r")
    monkeypatch.setenv("CARD_ID", "")
    return agent.main(["agent", "split", str(parent)])


def test_a_split_under_a_parent_on_autopilot_files_children_on_autopilot(record_property, make, monkeypatch):
    """Stories filed by a split under a parent on autopilot get the autopilot label and the Autopilot pill; others don't.

    Files an approved two-story split of #139, which carries the `autopilot` label, on a board. Both new issues carry
    the label, land in Backlog with Autopilot, and #139 shows Work with Autopilot. Then files the same split of a #139
    not on autopilot: no new issue carries the label and no card shows Autopilot."""
    record_property("proves", "210.2")
    w = make(labels={("issue", 139): {LABEL}})
    monkeypatch.setenv("DOKIMA_BOARD", "o/1")
    assert split_main(monkeypatch, w) == 0
    children = [n for (kind, n) in w.cards if kind == "issue" and n != 139]
    assert sorted(children) == [201, 202], f"210.2: the split's stories were not placed on the board: {children}"
    for n in (201, 202):
        assert w.has("issue", n), f"210.2: story #{n}, filed under #139 on autopilot, does not carry the autopilot label"
        assert (w.status("issue", n), w.action("issue", n)) == ("Backlog", "Autopilot"), \
            f"210.2: story #{n} landed as {w.status('issue', n)!r} with {w.action('issue', n)!r}, not Backlog with Autopilot"
    assert (w.status("issue", 139), w.action("issue", 139)) == ("Work", "Autopilot"), \
        f"210.2: parent #139 on autopilot shows {w.action('issue', 139)!r} after its split, not Autopilot"
    w = make(labels={("issue", 139): {"bug"}})
    assert split_main(monkeypatch, w) == 0
    for n in (201, 202):
        assert not w.has("issue", n), f"210.2: story #{n}, under a parent not on autopilot, was put on autopilot"
        assert (w.status("issue", n), w.action("issue", n)) == ("Backlog", None), f"210.2: story #{n}, not on autopilot, got a pill"
    assert w.action("issue", 139) is None, "210.2: parent #139, not on autopilot, got the Autopilot pill"


# 210.3: Needs you takes the Autopilot pill's place when the river stops for the owner, never both

def test_needs_you_replaces_autopilot_when_the_river_stops_and_autopilot_returns_after(record_property, make):
    """When the river stops for the owner on an issue on autopilot, its card shows Needs you instead; Autopilot returns after.

    For #57 on autopilot with PR #60: the river stops (move_card with Needs you) and both cards show Needs you; it goes
    on (move_card without) and both show Autopilot again. The board sync does the same: a planner question shows Needs
    you on #57, the work label after it shows Autopilot, and the Acceptance criteria checks finishing on PR #60 shows Needs you on it."""
    record_property("proves", "210.3")
    w = make(labels={("issue", 57): {LABEL}, ("pr", 60): {LABEL}}, prs={57: 60})
    agent.move_card("o/r", "57", "Plan", True, "o/1")
    for kind, n in (("issue", 57), ("pr", 60)):
        assert w.action(kind, n) == "Needs you", f"210.3: the river stopped for the owner and {kind} #{n} shows {w.action(kind, n)!r}"
    agent.move_card("o/r", "57", "Work", False, "o/1")
    for kind, n in (("issue", 57), ("pr", 60)):
        assert w.action(kind, n) == "Autopilot", f"210.3: the river went on and {kind} #{n} shows {w.action(kind, n)!r}, not Autopilot"
    board.sync("issue_comment", comment_event(57, "**Planner question**\n\nWhich?", [LABEL]), SPEC, REPO)
    assert w.action("issue", 57) == "Needs you", f"210.3: a question for the owner on #57 shows {w.action('issue', 57)!r}"
    board.sync("issues", label_event("labeled", "work", [LABEL, "work"], 57), SPEC, REPO)
    assert w.action("issue", 57) == "Autopilot", f"210.3: #57 went on after the question and shows {w.action('issue', 57)!r}"
    board.sync("workflow_run", {"action": "completed", "workflow_run": {"pull_requests": [{"number": 60}]}}, SPEC, REPO)
    assert w.action("pr", 60) == "Needs you", f"210.3: PR #60 waiting on the owner shows {w.action('pr', 60)!r}"


def test_switching_autopilot_never_hides_needs_you(record_property, make):
    """Switching autopilot on or off while the card waits on the owner leaves Needs you, so no card shows both or loses it.

    #57 and PR #60 show Needs you. Adding the `autopilot` label keeps Needs you on both; removing it keeps Needs you
    on both. A card off autopilot that shows Autopilot by mistake loses it, so the switch does act."""
    record_property("proves", "210.3")
    w = make(labels={("issue", 57): {LABEL}}, prs={57: 60},
             cards={("issue", 57): {"Status": "Plan", "Action": "Needs you"}, ("pr", 60): {"Status": "Review", "Action": "Needs you"}})
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 57), SPEC, REPO)
    for kind, n in (("issue", 57), ("pr", 60)):
        assert w.action(kind, n) == "Needs you", f"210.3: switching autopilot on replaced Needs you on {kind} #{n} with {w.action(kind, n)!r}"
    w.labels[("issue", 57)] = set()
    board.sync("issues", label_event("unlabeled", LABEL, [], 57), SPEC, REPO)
    for kind, n in (("issue", 57), ("pr", 60)):
        assert w.action(kind, n) == "Needs you", f"210.3: switching autopilot off cleared Needs you on {kind} #{n}"
    w.cards[("issue", 58)] = {"Status": "Plan", "Action": "Autopilot"}
    board.sync("issues", label_event("unlabeled", LABEL, [], 58), SPEC, REPO)
    assert w.action("issue", 58) is None, "210.3: switching autopilot off left the Autopilot pill on #58"


# 210.4: one Autopilot table view lists every issue and pull request on autopilot

def test_the_board_gets_one_autopilot_table_view(record_property, make):
    """The first issue switched on autopilot gives the board an Autopilot view, a table showing only what carries the label.

    On a board with only the Needs you view, switching #57 on autopilot adds exactly one view: named Autopilot, laid
    out as a table, filtered to label:autopilot is:open (#278). Switching #101 on afterwards adds no second view, and a stage moment
    on a board without the view adds none."""
    record_property("proves", "210.4")
    w = make(labels={("issue", 57): {LABEL}, ("issue", 101): {LABEL}, ("issue", 58): set()})
    board.sync("issues", label_event("labeled", "work", ["work"], 58), SPEC, REPO)
    assert [v["name"] for v in w.view_list] == ["Needs you"], "210.4: a board change unrelated to autopilot added a view"
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 57), SPEC, REPO)
    added = [v for v in w.view_list if v["name"] != "Needs you"]
    assert added == [{"name": "Autopilot", "layout": "table", "filter": f"label:{LABEL} is:open"}], \
        f"210.4: switching autopilot on added {added}, not one Autopilot table view filtered to label:{LABEL} is:open"
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 101), SPEC, REPO)
    assert [v["name"] for v in w.view_list].count("Autopilot") == 1, "210.4: the Autopilot view was added twice"


def test_pull_requests_on_autopilot_carry_the_label_so_the_view_lists_them(record_property, make):
    """A pull request built for an issue on autopilot carries the autopilot label, so the view lists it; it loses it after.

    Switching #57 on autopilot labels its open PR #60; switching it off removes the label. A PR opened for #57 while on
    autopilot (#62) is labeled when it opens; one opened for #58, not on autopilot (#61), is not."""
    record_property("proves", "210.4")
    w = make(labels={("issue", 57): {LABEL}, ("issue", 58): set()}, prs={57: 60, 58: 61})
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 57), SPEC, REPO)
    assert w.has("pr", 60), "210.4: PR #60, built for #57 on autopilot, does not carry the autopilot label"
    w.labels[("issue", 57)] = set()
    board.sync("issues", label_event("unlabeled", LABEL, [], 57), SPEC, REPO)
    assert not w.has("pr", 60), "210.4: PR #60 still carries the autopilot label after #57 went off autopilot"
    w.labels[("issue", 57)] = {LABEL}
    w.prs[57] = 62
    board.sync("pull_request_target", pr_event("opened", 62, 57), SPEC, REPO)
    board.sync("pull_request_target", pr_event("opened", 61, 58), SPEC, REPO)
    assert w.has("pr", 62), "210.4: PR #62, opened for #57 on autopilot, does not carry the autopilot label"
    assert not w.has("pr", 61), "210.4: PR #61, built for #58 not on autopilot, was labeled autopilot"


# 210.5: in a repo without a board, autopilot still works and nothing fails

def test_without_a_board_autopilot_still_works_and_nothing_fails(record_property, make, monkeypatch):
    """Without a board, the label events touch nothing and a split under a parent on autopilot still labels its stories.

    Runs the board sync for the autopilot label with no board set, handing it both of the board's ways to reach GitHub
    (GraphQL and the REST call it uses for labels and the view), each failing on any call; then files a split of #139 on
    autopilot with no DOKIMA_BOARD, with the Board failing if built: it succeeds and both new issues carry the autopilot
    label."""
    record_property("proves", "210.5")
    ready("210.5", sync=True)

    def explode(*a, **k):
        raise AssertionError("210.5: the board was reached without a board set")

    for action, labels in (("labeled", [LABEL]), ("unlabeled", [])):
        assert not board.sync("issues", label_event(action, LABEL, labels), "", "o/r", q=explode, rest=explode)
    w = make(labels={("issue", 139): {LABEL}})
    monkeypatch.setattr(board, "Board", explode)
    monkeypatch.delenv("DOKIMA_BOARD", raising=False)
    assert split_main(monkeypatch, w) == 0, "210.5: filing a split failed without a board"
    for n in (201, 202):
        assert w.has("issue", n), f"210.5: without a board, story #{n} under #139 on autopilot was not labeled autopilot"


# The real dokima.board.Board, against a faked GitHub (B1, B2 of the plan review)
#
# The tests above fake the Board itself. These run the real Board, so its new reads and writes must truly reach GitHub.
# Only GitHub is faked: `q` answers GraphQL the way GitHub does, and `rest` answers the REST calls. The real Board is
#     Board(spec, repo, q=gql, rest=api)   and   sync(event, payload, spec, repo, q=gql, rest=api)
# where rest(method, path, **fields) sends one REST call (as `gh api -X METHOD path -f k=v`), returns its parsed JSON,
# and raises subprocess.CalledProcessError when GitHub refuses it.
# GitHub has a call that adds a view: POST orgs/{org}/projectsV2/{number}/views with name, layout ("table") and filter
# (https://docs.github.com/en/rest/projects/views). The board's views are read in GraphQL: projectV2 { views { nodes {
# name layout filter } } }. Labels may be read and written either in GraphQL (labels, label(name:),
# addLabelsToLabelable, removeLabelsFromLabelable) or in REST (repos/{repo}/issues/{n} and its /labels); the fake
# answers both. A card's current option is read in GraphQL from the item: node(id:) { ... on ProjectV2Item {
# fieldValueByName(name:) { ... on ProjectV2ItemFieldSingleSelectValue { name } } } } (fieldValues is answered too).
# An issue's open pull request is read from repository { pullRequests(headRefName: "try/issue-N", states: OPEN) }.
# An issue's parent is read in GraphQL from repository { issue(number:) { parent { number labels { ... } } } }, or in
# REST from repos/{repo}/issues/{n}/parent (GitHub answers 404 when there is none); the fake answers both.
# With stale_views, every read of the views returns the views the board had before the test, the way parallel board
# runs all read the views before any of them has added one.

import subprocess  # noqa: E402


class FakeGitHub:
    """GitHub as the real Board sees it: one project with Status and Action, issues, pull requests, labels and views."""

    def __init__(self, labels=None, prs=None, closed_prs=None, cards=None, views=("Needs you",), refuse_views=False,
                 parents=None, stale_views=False, filters=None, refuse_updates=False):
        self.labels = {n: set(v) for n, v in (labels or {}).items()}  # issue and PR numbers share one space, as on GitHub
        self.parents = dict(parents or {})  # sub-issue number -> parent issue number
        self.prs = dict(prs or {})  # issue number -> open PR number
        self.closed_prs = dict(closed_prs or {})  # issue number -> a closed PR on the same branch
        self.kinds = {**{n: "pr" for n in list(self.prs.values()) + list(self.closed_prs.values())}}
        self.cards = {}  # item id -> {field: option}
        self.items = {}  # (kind, n) -> item id
        for (kind, n), fields in (cards or {}).items():
            self.items[(kind, n)] = f"ITEM_{kind}_{n}"
            self.cards[f"ITEM_{kind}_{n}"] = dict(fields)
        self.views = [{"id": f"PVTV_{i}", "name": v, "layout": "TABLE_LAYOUT", "filter": (filters or {}).get(v, "")}
                      for i, v in enumerate(views)]
        self.refuse_updates, self.updates = refuse_updates, []  # updateProjectV2View calls: (view id, filter)
        self.before = [dict(x) for x in self.views]
        self.refuse_views, self.stale_views = refuse_views, stale_views
        self.rest_calls = []

    def kind(self, n):
        return self.kinds.get(n, "issue")

    def action(self, kind, n):
        return self.cards.get(self.items.get((kind, n)), {}).get("Action")

    def put(self, n, on):
        s = self.labels.setdefault(n, set())
        s.add(LABEL) if on else s.discard(LABEL)

    def content(self, node_id):
        """The number behind a node id like I_57 or PR_60."""
        return int(str(node_id).split("_")[-1])

    def item_node(self, kind, n, parent=True):
        iid = self.items.get((kind, n))
        card = self.cards.get(iid, {})
        nodes = [{"id": iid, "project": {"id": "P"},
                  "fieldValueByName": {"name": card["Action"]} if card.get("Action") else None}] if iid else []
        node = {"id": ("I_" if kind == "issue" else "PR_") + str(n), "number": n, "projectItems": {"nodes": nodes},
                "labels": {"nodes": [{"name": l} for l in sorted(self.labels.get(n, set()))]}}
        if kind == "issue" and parent:
            up = self.parents.get(n)
            node["parent"] = self.item_node("issue", up, parent=False) if up else None
        return node

    def view_nodes(self, text):
        """The board's views with only the fields the query selects, as GitHub answers (#278).

        Real GitHub returns only what a query names: a query of views{nodes{name}} gets no id or filter back."""
        m = re.search(r"views\s*\([^)]*\)\s*\{\s*nodes\s*\{([^{}]*)\}", text)
        asked = set(re.findall(r"\w+", m.group(1))) if m else set()
        return [{k: x[k] for k in x if k in asked} for x in (self.before if self.stale_views else self.views)]

    def q(self, query, **v):
        """Answer one GraphQL call the way GitHub would."""
        text = " ".join(query.split())
        values = [str(x) for x in v.values()]
        if "organization" in text:
            return {"organization": {"projectV2": {"id": "P", "fields": {"nodes": [
                {"id": "S", "name": "Status", "options": [{"id": "s-" + o, "name": o} for o in ("Backlog", "Plan", "Work", "Review", "Done")]},
                {"id": "W", "name": "Action", "options": [{"id": "w-you", "name": "Needs you"}, {"id": "w-auto", "name": "Autopilot"}]}]},
                "views": {"nodes": self.view_nodes(text)}}}}
        if "updateProjectV2View" in text:
            # GitHub's UpdateProjectV2ViewInput takes the view as viewId and the new filter as filter.
            if not re.search(r"\bviewId\s*:", text) or not re.search(r"\bfilter\s*:", text):
                raise subprocess.CalledProcessError(1, ["gh", "api", "graphql"], output="",
                                                    stderr="updateProjectV2View needs input {viewId, filter}")
            view_id = v.get("viewId") or v.get("v") or next((x for x in values if x.startswith("PVTV_")), None) \
                or re.search(r'viewId:\s*"([^"]+)"', text).group(1)
            new = v.get("filter")
            if new is None:
                new = next((x for x in values if x.startswith("label:")), None)
            if new is None:
                new = re.search(r'filter:\s*"([^"]*)"', text).group(1)
            if self.refuse_updates:
                raise subprocess.CalledProcessError(1, ["gh", "api", "graphql"], output="", stderr="Resource not accessible by integration")
            self.updates.append((view_id, new))
            for x in self.views:
                if x["id"] == view_id:
                    x["filter"] = new
            return {"updateProjectV2View": {"projectV2View": {"id": view_id, "filter": new}}}
        if "addProjectV2ItemById" in text:
            n = self.content(v.get("c") or next(x for x in values if x.startswith(("I_", "PR_"))))
            kind = "issue" if str(v.get("c", "I_")).startswith("I_") else "pr"
            self.items[(kind, n)] = f"ITEM_{kind}_{n}"
            self.cards.setdefault(f"ITEM_{kind}_{n}", {})
            return {"addProjectV2ItemById": {"item": {"id": f"ITEM_{kind}_{n}"}}}
        if "updateProjectV2ItemPosition" in text:
            return {}
        if "updateProjectV2ItemFieldValue" in text or "clearProjectV2ItemFieldValue" in text:
            iid = next(x for x in values if x.startswith("ITEM_"))
            field = {"S": "Status", "W": "Action"}[v.get("f") or next(x for x in values if x in ("S", "W"))]
            if "clearProjectV2ItemFieldValue" in text:
                self.cards[iid].pop(field, None)
            else:
                opt = v.get("o") or next(x for x in values if x.startswith(("s-", "w-")))
                self.cards[iid][field] = {"w-you": "Needs you", "w-auto": "Autopilot"}.get(opt, opt[2:])
            return {}
        if "addLabelsToLabelable" in text or "removeLabelsFromLabelable" in text:
            assert "LA_autopilot" in text + " ".join(values), "the label call names no autopilot label id"
            n = self.content(next(x for x in values if x.startswith(("I_", "PR_"))))
            self.put(n, "addLabelsToLabelable" in text)
            return {}
        if "node(" in text:
            iid = next(x for x in values if x.startswith("ITEM_"))
            card = self.cards.get(iid, {})
            field = next((f for f in ("Action", "Status") if f in values or f'"{f}"' in text), None)
            return {"node": {"id": iid,
                             "fieldValueByName": {"name": card[field]} if field and card.get(field) else None,
                             "fieldValues": {"nodes": [{"name": o, "field": {"name": f}} for f, o in card.items()]}}}
        if "repository" in text:
            repo = {}
            if "pullRequests(" in text:
                head = next((x for x in values if x.startswith("try/issue-")), None) or re.search(r"try/issue-\d+", text).group(0)
                n = int(head.rsplit("-", 1)[1])
                nodes = []
                if n in self.closed_prs and "OPEN" not in text:
                    nodes.append({"number": self.closed_prs[n], "state": "CLOSED"})
                if n in self.prs:
                    nodes.append({"number": self.prs[n], "state": "OPEN"})
                repo["pullRequests"] = {"nodes": nodes}
            if "label(" in text:
                repo["label"] = {"id": "LA_autopilot", "name": LABEL} if LABEL in text + " ".join(values) else None
            for field, kind in (("issue(", "issue"), ("pullRequest(", "pr")):
                if field in text:
                    n = next((x for x in v.values() if isinstance(x, int)), None)
                    if n is None:
                        n = int(re.search(field.replace("(", r"\(") + r"\s*number:\s*(\d+)", text).group(1))
                    repo[field[:-1]] = self.item_node(kind, n)
            return {"repository": repo}
        return {}

    def rest(self, method, path, **fields):
        """Answer one REST call the way GitHub would; refuse the view call when told to."""
        method, path = method.upper(), path.lstrip("/")
        self.rest_calls.append((method, path, fields))
        if path == "orgs/dokima-dev/projectsV2/1/views" and method == "POST":
            if self.refuse_views:
                raise subprocess.CalledProcessError(1, ["gh", "api", path], output="", stderr="Resource not accessible by integration")
            self.views.append({"id": f"PVTV_{len(self.views)}", "name": fields.get("name"), "layout": {"table": "TABLE_LAYOUT"}.get(fields.get("layout"), fields.get("layout")),
                               "filter": fields.get("filter")})
            return {"id": 9, "name": fields.get("name")}
        m = re.fullmatch(r"repos/dokima-dev/dokima/issues/(\d+)/parent", path)
        if m and method == "GET":
            up = self.parents.get(int(m.group(1)))
            if not up:
                raise subprocess.CalledProcessError(1, ["gh", "api", path], output="", stderr="Not Found (HTTP 404)")
            return {"number": up, "labels": [{"name": l} for l in sorted(self.labels.get(up, set()))]}
        m = re.fullmatch(r"repos/dokima-dev/dokima/issues/(\d+)(/labels(?:/(.+))?)?", path)
        if m:
            n = int(m.group(1))
            if m.group(2) and method == "DELETE" and m.group(3) == LABEL:
                self.put(n, False)
            elif m.group(2) and method in ("POST", "PUT") and LABEL in " ".join(str(x) for x in fields.values()):
                self.put(n, True)
            return {"number": n, "labels": [{"name": l} for l in sorted(self.labels.get(n, set()))]}
        return {}


def ready(criterion, *methods, sync=False):
    """Fail in plain words, naming the criterion, while the real Board lacks what these tests run."""
    import inspect
    if "rest" not in inspect.signature(board.Board).parameters:
        pytest.fail(f"{criterion}: the real Board takes no rest= call yet, so it cannot reach GitHub's REST API")
    if sync and "rest" not in inspect.signature(board.sync).parameters:
        pytest.fail(f"{criterion}: board.sync takes no rest= call yet")
    missing = [m for m in methods if not callable(getattr(board.Board, m, None))]
    if missing:
        pytest.fail(f"{criterion}: the real Board has no {', '.join(missing)} yet")


def real_board(gh):
    return board.Board(SPEC, REPO, q=gh.q, rest=gh.rest)


def test_the_real_board_reads_whether_an_issue_or_pull_request_is_on_autopilot(record_property):
    """The board tells an issue or pull request on autopilot from one that is not, by reading its labels on GitHub.

    Runs the real Board against a faked GitHub: issue #57 (labels autopilot and bug) and PR #60 (autopilot) are on
    autopilot; issue #58 (bug) and PR #61 (no labels) are not."""
    record_property("proves", "210.1")
    ready("210.1", "autopilot")
    gh = FakeGitHub(labels={57: {LABEL, "bug"}, 60: {LABEL}, 58: {"bug"}, 61: set()}, prs={57: 60, 58: 61})
    b = real_board(gh)
    for kind, n, on in (("issue", 57, True), ("pr", 60, True), ("issue", 58, False), ("pr", 61, False)):
        assert b.autopilot(kind, n) is on, f"210.1: the board read {kind} #{n} as {'off' if on else 'on'} autopilot"


def test_the_real_board_finds_the_open_pull_request_of_an_issue(record_property):
    """The board finds the open pull request built for an issue, and none when there is none.

    Issue #57 has open PR #60 and an older closed PR #55 on the same branch; issue #58 has none."""
    record_property("proves", "210.1")
    ready("210.1", "open_pr")
    gh = FakeGitHub(prs={57: 60}, closed_prs={57: 55})
    b = real_board(gh)
    assert b.open_pr(57) == 60, f"210.1: the open pull request of #57 read as {b.open_pr(57)!r}, not #60"
    assert b.open_pr(58) is None, f"210.1: #58 has no pull request, but the board found {b.open_pr(58)!r}"


def test_the_real_board_reads_back_the_pill_it_sets(record_property):
    """The board reads a card's current pill, Needs you, Autopilot or none, so it never writes over Needs you blindly.

    The real Board reads #57's card (Needs you), #58's (Autopilot) and #59's (no pill), then sets Autopilot on #59 and
    clears #58, and reads both back."""
    record_property("proves", "210.3")
    ready("210.3", "value")
    gh = FakeGitHub(cards={("issue", 57): {"Status": "Plan", "Action": "Needs you"},
                           ("issue", 58): {"Status": "Work", "Action": "Autopilot"}, ("issue", 59): {"Status": "Work"}})
    b = real_board(gh)
    i57, i58, i59 = (b.item("issue", n) for n in (57, 58, 59))
    assert b.value(i57, "Action") == "Needs you", f"210.3: #57's card read as {b.value(i57, 'Action')!r}, not Needs you"
    assert b.value(i58, "Action") == "Autopilot", f"210.3: #58's card read as {b.value(i58, 'Action')!r}, not Autopilot"
    assert b.value(i59, "Action") is None, f"210.3: #59's card has no pill but read as {b.value(i59, 'Action')!r}"
    b.set(i59, "Action", "Autopilot")
    b.set(i58, "Action", None)
    assert (b.value(i59, "Action"), b.value(i58, "Action")) == ("Autopilot", None), "210.3: the board did not read back what it set"


def test_the_real_board_puts_the_autopilot_label_on_and_off_a_pull_request(record_property):
    """The board puts the autopilot label on a pull request and takes it off, leaving its other labels alone.

    The real Board labels PR #60 (which carries bug) and then unlabels it; #61 is never touched."""
    record_property("proves", "210.4")
    ready("210.4", "label")
    gh = FakeGitHub(labels={60: {"bug"}, 61: {"bug"}}, prs={57: 60, 58: 61})
    b = real_board(gh)
    b.label("pr", 60, True)
    assert gh.labels[60] == {"bug", LABEL}, f"210.4: labelling PR #60 left it with {sorted(gh.labels[60])}"
    b.label("pr", 60, False)
    assert gh.labels[60] == {"bug"}, f"210.4: unlabelling PR #60 left it with {sorted(gh.labels[60])}"
    assert gh.labels[61] == {"bug"}, "210.4: labelling PR #60 changed PR #61"


def test_the_real_board_lists_its_views_and_adds_the_autopilot_table_view(record_property):
    """The board reads its views from GitHub and adds the Autopilot view with GitHub's create-view call.

    The real Board reads the views (only Needs you), adds one named Autopilot, table layout, filter label:autopilot,
    with exactly one POST to orgs/dokima-dev/projectsV2/1/views, and then reads both views back."""
    record_property("proves", "210.4")
    ready("210.4", "views", "add_view")
    gh = FakeGitHub()
    b = real_board(gh)
    assert b.views() == ["Needs you"], f"210.4: the board read its views as {b.views()}"
    b.add_view("Autopilot", "table", f"label:{LABEL}")
    sent = [c for c in gh.rest_calls if c[1].endswith("/views")]
    assert sent == [("POST", "orgs/dokima-dev/projectsV2/1/views", {"name": "Autopilot", "layout": "table", "filter": f"label:{LABEL}"})], \
        f"210.4: adding the view sent {sent}, not one create-view call with name, table layout and filter"
    assert real_board(gh).views() == ["Needs you", "Autopilot"], "210.4: the added view is not read back"


def test_switching_autopilot_on_reaches_github_end_to_end(record_property):
    """Switching #57 on autopilot, through the real board sync, gives #57 and its PR the pill, the PR the label, and one view.

    Runs board.sync with the real Board against a faked GitHub. #57 (on Plan) and its PR #60 get Autopilot, PR #60
    carries the autopilot label, and the board gains one Autopilot table view filtered to label:autopilot is:open. A second
    issue switched on adds no second view. #58, already showing Needs you when switched on, keeps Needs you."""
    record_property("proves", "210.1")
    ready("210.1", sync=True)
    gh = FakeGitHub(labels={57: {LABEL}, 58: {LABEL}, 101: {LABEL}}, prs={57: 60},
                    cards={("issue", 57): {"Status": "Plan"}, ("pr", 60): {"Status": "Review"},
                           ("issue", 58): {"Status": "Plan", "Action": "Needs you"}})
    for n in (57, 58, 101):
        board.sync("issues", label_event("labeled", LABEL, [LABEL], n), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert (gh.action("issue", 57), gh.action("pr", 60), gh.action("issue", 101)) == ("Autopilot",) * 3, \
        f"210.1: on GitHub the cards show {gh.action('issue', 57)!r}, {gh.action('pr', 60)!r}, {gh.action('issue', 101)!r}"
    assert gh.action("issue", 58) == "Needs you", f"210.3: switching #58 on replaced Needs you with {gh.action('issue', 58)!r}"
    assert LABEL in gh.labels.get(60, set()), "210.4: on GitHub PR #60 does not carry the autopilot label"
    assert [x["name"] for x in gh.views].count("Autopilot") == 1, f"210.4: the board has views {[x['name'] for x in gh.views]}"
    view = next(x for x in gh.views if x["name"] == "Autopilot")
    assert (view["layout"], view["filter"]) == ("TABLE_LAYOUT", f"label:{LABEL} is:open"), f"210.4: the Autopilot view is {view}"


def test_a_refused_view_never_stops_the_pills_and_says_why(record_property):
    """If GitHub refuses to add the Autopilot view, the pills are still set and the board run fails naming the view.

    The faked GitHub refuses the create-view call. Switching #57 on autopilot still gives #57 and PR #60 the
    Autopilot pill and labels PR #60, then the sync raises an error whose message names the Autopilot view."""
    record_property("proves", "210.4")
    ready("210.4", sync=True)
    gh = FakeGitHub(labels={57: {LABEL}}, prs={57: 60}, cards={("issue", 57): {"Status": "Plan"}}, refuse_views=True)
    with pytest.raises(Exception) as failed:
        board.sync("issues", label_event("labeled", LABEL, [LABEL], 57), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert "Autopilot view" in str(failed.value), f"210.4: the failure does not say the Autopilot view could not be added: {failed.value}"
    assert (gh.action("issue", 57), gh.action("pr", 60)) == ("Autopilot", "Autopilot"), \
        "210.4: a refused view stopped the Autopilot pills from being set"
    assert LABEL in gh.labels.get(60, set()), "210.4: a refused view stopped PR #60 from being labelled"


# 210.4: switching a whole tree on adds the Autopilot view once, even when the tree's board runs overlap (B1 of the
# code review). /autopilot start labels every issue of a tree within seconds, and each label starts its own board run
# in parallel, so each run may read the views before any has added the Autopilot view. Only the run of the tree's top
# issue, the one switched on whose parent is not on autopilot, adds the view.

def creates(gh):
    """The create-view calls the board sent to GitHub."""
    return [c for c in gh.rest_calls if c[0] == "POST" and c[1].endswith("/views")]


def test_the_real_board_reads_an_issues_parent(record_property):
    """The board finds the parent of a sub-issue on GitHub, and none for an issue at the top of its tree.

    Runs the real Board against a faked GitHub where #71 and #72 are sub-issues of #70 and #73 is a sub-issue of #71:
    the parents read are #70, #70 and #71, and #70 has none."""
    record_property("proves", "210.4")
    ready("210.4", "parent")
    gh = FakeGitHub(parents={71: 70, 72: 70, 73: 71})
    b = real_board(gh)
    for n, up in ((71, 70), (72, 70), (73, 71), (70, None)):
        assert b.parent(n) == up, f"210.4: the board read the parent of #{n} as {b.parent(n)!r}, not {up!r}"


def start_tree(gh, monkeypatch, top, tree):
    """Run the real /autopilot start labeling (agent.switch_autopilot) on top, with labels landing on the faked GitHub.

    tree maps each issue to its sub-issues. Returns the issues in the order their autopilot label was added."""
    added = []

    def fake(*args):
        path = next(x for x in args if x.startswith("repos/"))
        m = re.fullmatch(r"repos/o/r/issues/(\d+)/sub_issues\?per_page=100", path)
        if m:
            return json.dumps([{"number": c} for c in tree.get(int(m.group(1)), [])])
        m = re.fullmatch(r"repos/o/r/issues/(\d+)/labels", path)
        if m:
            added.append(int(m.group(1)))
            gh.put(int(m.group(1)), True)
            return "[]"
        n = int(path.rsplit("/", 1)[1])
        return json.dumps({"number": n, "labels": [{"name": l} for l in sorted(gh.labels.get(n, set()))]})

    monkeypatch.setattr(agent, "gh", fake)
    agent.switch_autopilot("o/r", top, "start")
    return added


def test_switching_a_whole_tree_on_adds_the_view_once_even_when_runs_overlap(record_property, monkeypatch):
    """Switching a whole tree on autopilot adds exactly one Autopilot view, even when every board run reads the views at once.

    #70 has sub-issues #71 and #72, and #71 has #73. The real /autopilot start labeling puts all four on autopilot,
    each parent before its sub-issues. The faked GitHub then answers every read of the views with the board as it was
    before (only Needs you), the way parallel runs all read before any adds. The board sync runs for each label event,
    sub-issues first: none of theirs adds a view, #70's sends exactly one create-view call (Autopilot, table,
    label:autopilot is:open), and all cards show Autopilot. A story filed later under #70 (#74) adds no second view."""
    record_property("proves", "210.4")
    ready("210.4", "parent", sync=True)
    parents = {71: 70, 72: 70, 73: 71, 74: 70}
    gh = FakeGitHub(parents=parents, stale_views=True)
    added = start_tree(gh, monkeypatch, 70, {70: [71, 72], 71: [73]})
    assert sorted(added) == [70, 71, 72, 73], f"210.4: /autopilot start labeled {added}, not the whole tree of #70"
    for child, up in ((71, 70), (72, 70), (73, 71)):
        assert added.index(up) < added.index(child), f"210.4: #{child} was put on autopilot before its parent #{up}: {added}"
    for n in (73, 72, 71):
        board.sync("issues", label_event("labeled", LABEL, [LABEL], n), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert creates(gh) == [], f"210.4: a sub-issue whose parent is on autopilot added the Autopilot view: {creates(gh)}"
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 70), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert len(creates(gh)) == 1, f"210.4: switching the tree of #70 on sent {len(creates(gh))} create-view calls, not exactly one"
    assert creates(gh)[0][2] == {"name": "Autopilot", "layout": "table", "filter": f"label:{LABEL} is:open"}, \
        f"210.4: the top of the tree added {creates(gh)[0][2]}, not the Autopilot table view filtered to label:{LABEL} is:open"
    gh.put(74, True)
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 74), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert len(creates(gh)) == 1, "210.4: a story filed later under #70 on autopilot added the Autopilot view a second time"
    for n in (70, 71, 72, 73, 74):
        assert gh.action("issue", n) == "Autopilot", f"210.4: #{n} in the tree shows {gh.action('issue', n)!r}, not Autopilot"

def test_a_sub_issue_switched_on_alone_still_gets_the_view(record_property):
    """A sub-issue switched on by itself, under a parent not on autopilot, is the top of what was switched and adds the view.

    #81 is a sub-issue of #80, which is not on autopilot; only #81 carries the label. Its board run sends exactly one
    create-view call. On a second board, #91 has no parent at all and is switched on: one create-view call too."""
    record_property("proves", "210.4")
    ready("210.4", "parent", sync=True)
    gh = FakeGitHub(labels={80: {"bug"}, 81: {LABEL}}, parents={81: 80}, stale_views=True)
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 81), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert len(creates(gh)) == 1, f"210.4: #81, switched on under #80 not on autopilot, sent {len(creates(gh))} create-view calls"
    gh = FakeGitHub(labels={91: {LABEL}}, stale_views=True)
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 91), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert len(creates(gh)) == 1, f"210.4: #91, switched on with no parent, sent {len(creates(gh))} create-view calls"


# #278: the Autopilot view lists only open issues and pull requests. A new view is filtered to label:autopilot is:open,
# so anything merged or closed, which keeps its label, leaves it. A view still filtered to the old label:autopilot is
# fixed by the board run of the next merge, so the board's view is fixed right after #278 merges. Views are read in
# GraphQL with their id and filter (projectV2 { views { nodes { id name filter } } }); the faked GitHub, like the real
# one, returns only the fields a query names. The filter is changed with updateProjectV2View(input: {viewId, filter}).

OPEN = f"label:{LABEL} is:open"
OLD = f"label:{LABEL}"


def updates(gh):
    """The filter changes the board sent to GitHub: (view id, new filter)."""
    return list(gh.updates)


def merged(number, issue):
    """A pull_request_target closed payload for a merged pull request, as board.yml receives it."""
    event = pr_event("closed", number, issue)
    event["pull_request"]["merged"] = True
    return event


def status(gh, kind, n):
    return gh.cards.get(gh.items.get((kind, n)), {}).get("Status")


def test_a_new_autopilot_view_lists_only_open_issues_and_pull_requests(record_property):
    """A new Autopilot view lists only open issues and pull requests.

    Proves 278.1. Runs the real board sync against a faked GitHub with only the Needs you view. Switching #57 on autopilot sends
    exactly one create-view call, named Autopilot, table layout, filter label:autopilot is:open, and changes no view."""
    record_property("proves", "278.1")
    gh = FakeGitHub(labels={57: {LABEL}}, cards={("issue", 57): {"Status": "Plan"}})
    board.sync("issues", label_event("labeled", LABEL, [LABEL], 57), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert creates(gh) == [("POST", "orgs/dokima-dev/projectsV2/1/views", {"name": "Autopilot", "layout": "table", "filter": OPEN})], \
        f"278.1: switching autopilot on sent {creates(gh)}, not one Autopilot table view filtered to {OPEN}"
    assert updates(gh) == [], f"278.1: adding the new view also changed a view: {updates(gh)}"


def test_merging_a_pull_request_fixes_the_old_autopilot_view(record_property):
    """Right after a merge, an old Autopilot view is fixed to show only open items.

    Proves 278.2. The faked GitHub has an Autopilot view filtered to label:autopilot and answers each views query with only the
    fields it names, as GitHub does. The board run for the merge of PR #60 (Closes #57) changes that same view
    (PVTV_1) to label:autopilot is:open with one update call, adds no view, leaves Needs you alone, and still moves
    PR #60 and #57 to Done."""
    record_property("proves", "278.2")
    gh = FakeGitHub(prs={57: 60}, cards={("issue", 57): {"Status": "Review"}, ("pr", 60): {"Status": "Review"}},
                    views=("Needs you", "Autopilot"), filters={"Autopilot": OLD})
    board.sync("pull_request_target", merged(60, 57), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert updates(gh) == [("PVTV_1", OPEN)], \
        f"278.2: the merge run sent {updates(gh)}, not one change of the Autopilot view (PVTV_1, {OLD}) to {OPEN}"
    assert creates(gh) == [] and [x["name"] for x in gh.views] == ["Needs you", "Autopilot"], \
        f"278.2: fixing the view changed the board's views to {[x['name'] for x in gh.views]}, creates {creates(gh)}"
    assert next(x for x in gh.views if x["name"] == "Needs you")["filter"] == "", "278.2: fixing the view changed the Needs you view"
    assert (status(gh, "pr", 60), status(gh, "issue", 57)) == ("Done", "Done"), \
        f"278.2: the merge no longer moved PR #60 and #57 to Done: {status(gh, 'pr', 60)}, {status(gh, 'issue', 57)}"


def test_the_fix_is_made_once_across_merges(record_property):
    """Two merges in a row fix the old view once, never twice.

    Proves 278.2. The Autopilot view starts on label:autopilot. PR #60 merges, then PR #61: exactly one update is sent, to
    label:autopilot is:open, and no view is created."""
    record_property("proves", "278.2")
    gh = FakeGitHub(prs={57: 60, 58: 61}, views=("Needs you", "Autopilot"), filters={"Autopilot": OLD})
    board.sync("pull_request_target", merged(60, 57), SPEC, REPO, q=gh.q, rest=gh.rest)
    board.sync("pull_request_target", merged(61, 58), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert updates(gh) == [("PVTV_1", OPEN)] and creates(gh) == [], \
        f"278.2: two merges sent updates {updates(gh)} and creates {creates(gh)}, not one fix to {OPEN}"


def test_a_view_already_right_is_left_alone(record_property):
    """An Autopilot view already right, or filtered by the owner, is never rewritten.

    Proves 278.3. Three boards, each through the board run of a merged PR #60: one whose Autopilot view is already
    label:autopilot is:open, as the owner set it by hand; one whose owner chose label:autopilot is:open -label:parked;
    and one with no Autopilot view at all. None gets an update call or a create-view call. Beside them, a board still
    on label:autopilot gets its one fix, so the run truly reads the filter rather than never touching any view."""
    record_property("proves", "278.3")
    old = FakeGitHub(prs={57: 60}, views=("Needs you", "Autopilot"), filters={"Autopilot": OLD})
    board.sync("pull_request_target", merged(60, 57), SPEC, REPO, q=old.q, rest=old.rest)
    assert updates(old) == [("PVTV_1", OPEN)], \
        f"278.3: a merge never fixed a view still on {OLD} (sent {updates(old)}), so leaving right views alone proves nothing"
    for views, filters in ((("Needs you", "Autopilot"), {"Autopilot": OPEN}),
                           (("Needs you", "Autopilot"), {"Autopilot": f"{OPEN} -label:parked"}),
                           (("Needs you",), {})):
        gh = FakeGitHub(prs={57: 60}, views=views, filters=filters)
        board.sync("pull_request_target", merged(60, 57), SPEC, REPO, q=gh.q, rest=gh.rest)
        assert updates(gh) == [] and creates(gh) == [], \
            f"278.3: a merge on a board with views {views} filtered {filters} sent updates {updates(gh)}, creates {creates(gh)}"


def test_a_refused_fix_still_moves_the_cards_and_says_why(record_property):
    """A refused fix still moves the merged cards, and the run says why.

    Proves 278.4. The faked GitHub refuses updateProjectV2View. The board run for the merge of PR #60 (Closes #57) still moves both
    cards to Done, then raises an error whose message names the Autopilot view."""
    record_property("proves", "278.4")
    gh = FakeGitHub(prs={57: 60}, cards={("issue", 57): {"Status": "Review"}, ("pr", 60): {"Status": "Review"}},
                    views=("Needs you", "Autopilot"), filters={"Autopilot": OLD}, refuse_updates=True)
    with pytest.raises(Exception) as failed:
        board.sync("pull_request_target", merged(60, 57), SPEC, REPO, q=gh.q, rest=gh.rest)
    assert "Autopilot view" in str(failed.value), f"278.4: the failure does not name the Autopilot view: {failed.value!r}"
    assert (status(gh, "pr", 60), status(gh, "issue", 57)) == ("Done", "Done"), \
        "278.4: a refused fix stopped the merged cards from moving to Done"

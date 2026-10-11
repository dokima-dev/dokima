import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest  # noqa: E402

from dokima import agent, board  # noqa: E402

WORKFLOW = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "board.yml")
BOT, YOU = {"type": "Bot"}, {"type": "User"}


def pr(action, number=7, body="Closes #5", merged=False):
    return {"action": action, "pull_request": {"number": number, "body": body, "merged": merged}}


# 116.1: every stage moment sets the stage and whose turn it is

@pytest.fixture(autouse=True)
def no_history(monkeypatch):
    """Every issue here is open with no record yet, so the board reads no network."""
    monkeypatch.setattr(board.Board, "state", lambda self, kind, n: "open")
    monkeypatch.setattr(agent, "gh", lambda *a: json.dumps({"number": int(a[2]), "title": "", "body": "", "comments": []})
                        if a[:2] == ("issue", "view") else "[]")


# 116.2: new items land on top

class FakeGitHub:
    def __init__(self, on_board=False):
        self.calls, self.on_board = [], on_board

    def __call__(self, query, **v):
        self.calls.append((query.split("(")[0].split("{")[0].strip(), v))
        if "organization" in query:
            return {"organization": {"projectV2": {"id": "P", "fields": {"nodes": [
                {"id": "S", "name": "Status", "options": [{"id": "s-" + o, "name": o} for o in ("Plan", "Work", "Review", "Done")]},
                {"id": "W", "name": "Action", "options": [{"id": "w-you", "name": "Needs you"}]}]}}}}
        if query.startswith("query") and "repository" in query:
            kind = "issue" if "issue(" in query else "pullRequest"
            items = [{"id": "ITEM", "project": {"id": "P"}}] if self.on_board else []
            # The issue or PR carries no labels and has no open PR, as GitHub answers for them (#210).
            return {"repository": {kind: {"id": "C", "projectItems": {"nodes": items}, "labels": {"nodes": []}},
                                   "pullRequests": {"nodes": []}}}
        if query.startswith("query") and "node(" in query:
            # The card has no Action pill yet, as GitHub answers for it (#210).
            return {"node": {"fieldValueByName": None, "fieldValues": {"nodes": []}}}
        if "addProjectV2ItemById" in query:
            return {"addProjectV2ItemById": {"item": {"id": "NEW"}}}
        return {}


def test_new_item_is_added_at_the_top(record_property):
    record_property("proves", "116.2")
    gh = FakeGitHub(on_board=False)
    board.sync("issues", {"action": "labeled", "label": {"name": "work"}, "issue": {"number": 5}}, "dokima-dev/1", "dokima-dev/dokima", q=gh)
    positions = [v for _, v in gh.calls if v.get("i") == "NEW" and set(v) == {"p", "i"}]
    assert positions, "116.2: new item was not placed"
    assert all("a" not in v for v in positions), "116.2: new item was placed after another item, not on top"


# 116.3: without a board, nothing happens and nothing fails

def test_no_board_means_no_calls(record_property):
    record_property("proves", "116.3")
    def explode(*a, **k):
        raise AssertionError("116.3: GitHub was called without a board")
    assert board.sync("issues", {"action": "closed", "issue": {"number": 5}}, "", "o/r", q=explode) == []


def test_workflow_skips_without_the_board_setting(record_property):
    record_property("proves", "116.3")
    assert "if: vars.DOKIMA_BOARD != ''" in open(WORKFLOW).read()


# 202: the Priority pill follows the issue's priority label

class PriorityGitHub(FakeGitHub):
    """The fake board, with a Priority field whose options are Blocker, High and Parked."""

    def __call__(self, query, **v):
        out = super().__call__(query, **v)
        if "organization" in query:
            out["organization"]["projectV2"]["fields"]["nodes"].append(
                {"id": "PRI", "name": "Priority", "options": [{"id": "p-" + o, "name": o} for o in ("Blocker", "High", "Parked")]})
        return out


def label_event(action, name, labels, number=5):
    """An issues labeled/unlabeled payload; labels are the issue's labels after the change, as GitHub sends them."""
    return {"action": action, "label": {"name": name}, "issue": {"number": number, "labels": [{"name": n} for n in labels]}}


def priority_calls(gh):
    """Every write to the Priority field: an option id when set, None when cleared."""
    return [v.get("o") for name, v in gh.calls if name == "mutation" and v.get("f") == "PRI"]


def other_field_calls(gh):
    """Every write to any field other than Priority (Status, Action)."""
    return [v for name, v in gh.calls if name == "mutation" and v.get("f") in ("S", "W")]


def test_adding_a_priority_label_sets_the_matching_pill(record_property):
    """Adding the high label sets the High pill, and nothing else (the parked label is gone, #320).

    Sends a labeled event for the high label to the board sync with a fake board, and checks the one write
    to Priority is the matching option, while the card's Status and Needs you pill are left as they were. Then adds and
    removes bug and plan on an issue labeled high, and checks Priority is never written. (Blocker follows blocked-by links since #294, not a label.)"""
    record_property("proves", "202.1")
    for label, option in (("high", "p-High"),):
        gh = PriorityGitHub(on_board=True)
        board.sync("issues", label_event("labeled", label, [label]), "dokima-dev/1", "dokima-dev/dokima", q=gh)
        assert priority_calls(gh) == [option], f"202.1: adding the {label} label wrote {priority_calls(gh)} to Priority, not {option}"
        assert other_field_calls(gh) == [], f"202.1: adding the {label} label also changed Status or Needs you: {other_field_calls(gh)}"
    for action in ("labeled", "unlabeled"):
        for label in ("bug", "plan"):
            gh = PriorityGitHub(on_board=True)
            board.sync("issues", label_event(action, label, ["high"]), "dokima-dev/1", "dokima-dev/dokima", q=gh)
            assert priority_calls(gh) == [], f"202.1: {action} {label} wrote {priority_calls(gh)} to Priority; only priority labels move the pill"


def test_removing_the_priority_label_clears_the_pill(record_property):
    """Removing the only priority label clears the Priority pill.

    Sends an unlabeled event for each priority label, with no priority label left on the issue, and checks Priority
    is cleared and nothing else on the card changes."""
    record_property("proves", "202.1")
    for label in ("high",):
        gh = PriorityGitHub(on_board=True)
        board.sync("issues", label_event("unlabeled", label, ["bug"]), "dokima-dev/1", "dokima-dev/dokima", q=gh)
        assert priority_calls(gh) == [None], f"202.1: removing the {label} label wrote {priority_calls(gh)} to Priority instead of clearing it"
        assert other_field_calls(gh) == [], f"202.1: removing the {label} label also changed Status or Needs you"


def test_a_parked_label_left_on_an_issue_moves_no_pill(record_property):
    """A parked label left on an old issue counts for nothing: only high moves the pill (#320).

    Adds parked to an issue labeled high (pill stays High), and removes high while parked remains (pill clears).
    A blocker label left on the issue counts for nothing since #294."""
    record_property("proves", "202.1")
    cases = [(("labeled", "high", ["parked", "high"]), "p-High"),
             (("labeled", "parked", ["parked"]), None),
             (("unlabeled", "high", ["parked", "blocker"]), None)]
    for (action, label, labels), option in cases:
        gh = PriorityGitHub(on_board=True)
        board.sync("issues", label_event(action, label, labels), "dokima-dev/1", "dokima-dev/dokima", q=gh)
        want = [option] if (action, label) != ("labeled", "parked") else []
        assert priority_calls(gh) == want, f"202.1: {action} {label} with labels {labels} wrote {priority_calls(gh)}, not {want}"


def test_workflow_runs_on_label_removal(record_property):
    """The board workflow runs when a label is removed, so removing a priority label reaches the board.

    Reads the issues triggers of the board workflow and checks they include unlabeled next to labeled."""
    record_property("proves", "202.1")
    import re
    found = re.search(r"^  issues:\n    types: \[([^\]]*)\]", open(WORKFLOW).read(), re.M)
    assert found, "202.1: the board workflow no longer runs on issue events"
    types = [t.strip() for t in found.group(1).split(",")]
    assert "labeled" in types and "unlabeled" in types, f"202.1: the board workflow's issue triggers are {types}; removing a label never reaches the board"


def test_new_issue_with_a_priority_label_lands_with_its_pill(record_property):
    """An issue filed with the high label lands on the board with the High pill.

    GitHub sends a labeled event for each label an issue is filed with. Sends that event for an issue not yet on the
    board, and checks the issue is added to the board and its new card gets Priority High."""
    record_property("proves", "202.2")
    gh = PriorityGitHub(on_board=False)
    board.sync("issues", label_event("labeled", "high", ["high", "bug"], number=201), "dokima-dev/1", "dokima-dev/dokima", q=gh)
    assert any(name == "mutation" and "c" in v for name, v in gh.calls), "202.2: the new issue was not added to the board"
    writes = [(v.get("i"), v.get("o")) for name, v in gh.calls if name == "mutation" and v.get("f") == "PRI"]
    assert writes == [("NEW", "p-High")], f"202.2: the new card's Priority writes were {writes}, not High on the new card"


def test_no_board_or_no_priority_field_is_left_alone(record_property):
    """Without a board, or on a board with no Priority field, a priority label writes nothing and fails nothing.

    First checks a board with a Priority field does get High, so the rest is not passing by doing nothing. Then runs
    the sync for a high label with no board set and a GitHub stand-in that fails on any call, and against a board
    with only Status and Action, checking no field is written."""
    record_property("proves", "202.3")
    gh = PriorityGitHub(on_board=True)
    board.sync("issues", label_event("labeled", "high", ["high"]), "dokima-dev/1", "dokima-dev/dokima", q=gh)
    assert priority_calls(gh) == ["p-High"], "202.3: a board with a Priority field did not get High"
    def explode(*a, **k):
        raise AssertionError("202.3: GitHub was called without a board")
    board.sync("issues", label_event("labeled", "high", ["high"]), "", "o/r", q=explode)
    board.sync("issues", label_event("unlabeled", "high", []), "", "o/r", q=explode)
    for action, labels in (("labeled", ["high"]), ("unlabeled", [])):
        gh = FakeGitHub(on_board=True)
        board.sync("issues", label_event(action, "high", labels), "dokima-dev/1", "dokima-dev/dokima", q=gh)
        assert [v for name, v in gh.calls if name == "mutation" and "f" in v] == [], f"202.3: {action} high wrote a field on a board without Priority"

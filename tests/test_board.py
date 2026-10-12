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


# 202: no label sets Priority any more; only blocked-by links do (Blocker), so a label never writes the pill

class PriorityGitHub(FakeGitHub):
    """The fake board, with a Priority field whose one option is Blocker."""

    def __call__(self, query, **v):
        out = super().__call__(query, **v)
        if "organization" in query:
            out["organization"]["projectV2"]["fields"]["nodes"].append(
                {"id": "PRI", "name": "Priority", "options": [{"id": "p-" + o, "name": o} for o in ("Blocker",)]})
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


def test_no_label_moves_the_priority_pill(record_property):
    """Adding or removing any label writes nothing to Priority: the pill comes only from blocked-by links.

    Sends labeled and unlabeled events for high, parked, blocker and bug to the board sync with a fake board that has a
    Priority field, on an issue already on the board and on a new one, and checks Priority is never written and the
    card's Status and Needs you pill are left as they were."""
    record_property("proves", "202.1")
    for on_board in (True, False):
        for action in ("labeled", "unlabeled"):
            for label in ("high", "parked", "blocker", "bug"):
                labels = [label, "bug"] if action == "labeled" else ["bug"]
                gh = PriorityGitHub(on_board=on_board)
                board.sync("issues", label_event(action, label, labels), "dokima-dev/1", "dokima-dev/dokima", q=gh)
                where = "a card on the board" if on_board else "a new issue"
                assert priority_calls(gh) == [], f"202.1: {action} {label} on {where} wrote {priority_calls(gh)} to Priority"
                assert other_field_calls(gh) == [], f"202.1: {action} {label} on {where} changed Status or Needs you"


def test_workflow_runs_on_label_removal(record_property):
    """The board workflow runs when a label is removed, so taking autopilot off reaches the board.

    Reads the issues triggers of the board workflow and checks they include unlabeled next to labeled."""
    record_property("proves", "202.1")
    import re
    found = re.search(r"^  issues:\n    types: \[([^\]]*)\]", open(WORKFLOW).read(), re.M)
    assert found, "202.1: the board workflow no longer runs on issue events"
    types = [t.strip() for t in found.group(1).split(",")]
    assert "labeled" in types and "unlabeled" in types, f"202.1: the board workflow's issue triggers are {types}; removing a label never reaches the board"


def test_no_board_or_no_priority_field_is_left_alone(record_property):
    """Without a board, or on a board with no Priority field, a label event writes no field and fails nothing.

    Runs the sync for adding and removing high with no board set and a GitHub stand-in that fails on any call, then
    against a board with only Status and Action, checking no field is written."""
    record_property("proves", "202.3")
    def explode(*a, **k):
        raise AssertionError("202.3: GitHub was called without a board")
    board.sync("issues", label_event("labeled", "high", ["high"]), "", "o/r", q=explode)
    board.sync("issues", label_event("unlabeled", "high", []), "", "o/r", q=explode)
    for action, labels in (("labeled", ["high"]), ("unlabeled", [])):
        gh = FakeGitHub(on_board=True)
        board.sync("issues", label_event(action, "high", labels), "dokima-dev/1", "dokima-dev/dokima", q=gh)
        assert [v for name, v in gh.calls if name == "mutation" and "f" in v] == [], f"202.3: {action} high wrote a field on a board without Priority"

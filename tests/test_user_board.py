"""#944: DOKIMA_BOARD names an organization's project (`org/number`) or a user's project (`user:login/number`), and
every board read asks GitHub for it under that owner."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest  # noqa: E402

from dokima import audit, board  # noqa: E402

FIELDS = [{"id": "S", "name": "Status", "options": [{"id": "s-work", "name": "Work", "color": "BLUE", "description": ""}]},
          {"id": "A", "name": "Action", "options": [{"id": "a-you", "name": "Needs you", "color": "RED", "description": ""}]},
          {"id": "P", "name": "Priority", "options": [{"id": "p-b", "name": "Blocker", "color": "RED", "description": ""}]}]
ITEM = {"fieldValueByName": {"name": "Needs you"}, "status": {"name": "Work"},
        "content": {"__typename": "Issue", "number": 5, "state": "OPEN", "labels": {"nodes": []}}}


class FakeGitHub:
    """Answers board reads only under the owner type and login that own the board."""

    def __init__(self, kind, login):
        self.kind, self.login, self.roots, self.rest_calls = kind, login, [], []

    def __call__(self, query, **v):
        root = re.search(r"\{(\w+)\(login:\$o\)", query).group(1)
        self.roots.append(root)
        if root != self.kind or v["o"] != self.login or v["n"] != 3:
            return {root: None}
        return {root: {"projectV2": {"id": "PROJ", "fields": {"nodes": FIELDS},
                                     "items": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [ITEM]},
                                     "views": {"nodes": [{"id": "V", "name": "Board", "layout": "BOARD_LAYOUT", "filter": ""}]}}}}

    def rest(self, method, path, **fields):
        self.rest_calls.append((method, path))
        return {}


@pytest.mark.parametrize("spec,kind,login", [("acme/3", "organization", "acme"), ("user:ann/3", "user", "ann")])
def test_every_board_read_asks_for_the_project_under_its_owner(spec, kind, login):
    gh = FakeGitHub(kind, login)
    b = board.Board(spec, "ann/repo", q=gh, rest=gh.rest)
    assert b.id == "PROJ"
    assert set(b.fields) == {"Status", "Action", "Priority"}
    assert [c["number"] for c in b.cards()] == [5]
    assert b.views() == ["Board"]
    b.add_view("Mine", "table", "")
    assert set(gh.roots) == {kind}, f"{spec}: board reads went to {set(gh.roots)}, not {kind}"
    assert gh.rest_calls == [("POST", f"{'users' if kind == 'user' else 'orgs'}/{login}/projectsV2/3/views")]


@pytest.mark.parametrize("spec,kind,login", [("acme/3", "organization", "acme"), ("user:ann/3", "user", "ann")])
def test_the_audit_checks_the_board_fields_the_same_way_on_both(monkeypatch, spec, kind, login):
    gh = FakeGitHub(kind, login)
    monkeypatch.setattr(board, "gql", gh)
    live = audit.GitHub(spec)
    assert set(live.fields()) == {"Status", "Action", "Priority"}
    assert live.fields()["Action"] == {"Needs you": {"color": "RED", "description": ""}}
    assert set(live.views()) == {"Board"}
    assert set(gh.roots) == {kind}


def test_a_board_spec_with_an_unknown_owner_type_is_refused():
    with pytest.raises(ValueError):
        board.parse("team:acme/3")
    assert board.parse("org:acme/3") == ("organization", "acme", 3)

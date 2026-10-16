"""A story holds at most 10 criteria; a larger group of criteria sharing code files splits wide, into consecutive
stories that take turns, never deeper. An agent gets 100 turns."""
import json

import pytest

from dokima import planner
from test_story_groups import crit, story, feature, rejected, SRC


def chained(*sizes, files=("dokima/hub.py",)):
    """A split of one group of criteria sharing a code file, cut into stories of these sizes, each depending on the
    one before."""
    k = iter(range(1, 1000))
    f = feature(*[[crit(f"Rule {next(k)} holds.", files) for _ in range(n)] for n in sizes])
    for i, s in enumerate(f["stories"]):
        s["depends_on"] = [i - 1] if i else []
    return f


def test_a_story_of_ten_criteria_is_accepted(tmp_path):
    """Ten criteria on one code file are one story."""
    assert rejected(tmp_path, story(*[crit(f"Rule {k} holds.", ["dokima/hub.py"]) for k in range(1, 11)])) is None


def test_a_story_of_eleven_criteria_is_refused(tmp_path):
    """Eleven criteria in one story are refused, asking for a split."""
    why = rejected(tmp_path, story(*[crit(f"Rule {k} holds.", ["dokima/hub.py"]) for k in range(1, 12)]))
    assert why and "more than the 10" in why, why


def test_a_large_group_splits_wide_into_chained_stories(tmp_path):
    """Twenty-three criteria on one code file split into stories of 10, 10 and 3, each depending on the one before."""
    assert rejected(tmp_path, chained(10, 10, 3)) is None


def test_chained_stories_must_depend_on_the_one_before(tmp_path):
    """Stories cut from one group that do not depend on the one before are refused."""
    f = chained(10, 10, 3)
    f["stories"][2]["depends_on"] = []
    why = rejected(tmp_path, f)
    assert why and "must depend on story 2" in why, why


def test_a_small_group_is_never_cut(tmp_path):
    """A group of ten or fewer criteria sharing a code file stays one story."""
    why = rejected(tmp_path, chained(4, 4))
    assert why and "belong in the same story" in why, why


def test_a_story_of_a_parent_over_ten_splits_wide(tmp_path, monkeypatch):
    """A story of a parent holding more than ten criteria splits the same way; at ten or fewer it never splits."""
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / "parent.json").write_text(json.dumps({"number": 330}))
    for k, v in {"PACK": str(pack), "GITHUB_REPOSITORY": "o/r", "GITHUB_SERVER_URL": "https://github.com"}.items():
        monkeypatch.setenv(k, v)
    mine = "https://github.com/o/r/issues/331"

    def nested(content):
        content = json.loads(json.dumps(content).replace(SRC, mine).replace('"9.', '"331.'))
        (tmp_path / "plan.json").write_text(json.dumps(content))
        try:
            planner.read_output(str(tmp_path), 331)
        except planner.Garbled as e:
            return str(e)
        return None

    assert nested(chained(10, 5)) is None
    why = nested(chained(3, 3))
    assert why and "never splits again" in why, why


def test_the_cap_can_be_changed(monkeypatch, tmp_path):
    """The cap comes from DOKIMA_MAX_CRITERIA until the settings file holds it."""
    monkeypatch.setattr(planner, "MAX_CRITERIA", 5)
    why = rejected(tmp_path, story(*[crit(f"Rule {k} holds.", ["dokima/hub.py"]) for k in range(1, 7)]))
    assert why and "more than the 5" in why, why


def test_an_agent_gets_one_hundred_turns():
    """Claude runs with 100 turns unless DOKIMA_MAX_TURNS names another number."""
    src = open("dokima/agent_claude.py").read()
    assert '"--max-turns", os.environ.get("DOKIMA_MAX_TURNS") or "100"' in src

"""Each story holds up to five criteria, with no cap on stories (#642).

The owner wants narrow tasks: a story never holds more than five criteria, but there is no cap on how many stories an
issue splits into. These tests run the plan check itself and read the rules every agent is given."""
import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
from dokima import agent, planner  # noqa: E402

SRC = "https://github.com/dokima-dev/dokima/issues/642"
C = {"text": "a", "source": SRC}


def sized(k):
    """A story holding k acceptance criteria."""
    return {"acceptance_criteria": [C] * k, "non_functional": []}


def feature(*sizes):
    """A split whose stories hold the given numbers of criteria, none waiting on another."""
    return {"kind": "feature", "title": "t", "summary": "s", "feature": "f",
            "stories": [{"title": f"s{n}", "user_story": "u", "acceptance_criteria": [C] * k, "non_functional": [],
                         "depends_on": []} for n, k in enumerate(sizes)]}


def refused(stories, nested=False):
    """The size check's refusal of these stories, or None when it lets them through."""
    try:
        planner.check_size(stories, nested)
    except planner.Garbled as e:
        return str(e)
    return None


def test_a_story_holds_up_to_five_criteria(record_property):
    """A story of four or five criteria passes; a story of six is refused.

    Runs the size check on one story of 4, one of 5, and a story of 5 that is already a story of its parent; all pass.
    A story of 6, alone, beside a story of 5, or as a story of its parent, is refused.

    Proves 642.1."""
    record_property("proves", "642.1")
    for k in (4, 5):
        why = refused([sized(k)])
        assert why is None, f"642.1: one story of {k} criteria was refused, though up to five are allowed: {why}"
    why = refused([sized(5)], nested=True)
    assert why is None, f"642.1: a parent's story of 5 criteria was refused, though up to five are allowed: {why}"
    assert refused([sized(6)]), "642.1: one story of 6 criteria passed, though a story holds at most five"
    assert refused([sized(5), sized(6)]), "642.1: a split with a story of 6 criteria passed"
    assert refused([sized(6)], nested=True), "642.1: a parent's story of 6 criteria passed"


def test_a_split_may_have_any_number_of_stories(record_property):
    """A split into seven stories passes the plan check.

    Hands the plan check a feature of seven stories, then one of three stories of one criterion each: both are read
    as a feature. A split of one story is still refused, since a split needs at least two.

    Proves 642.2."""
    record_property("proves", "642.2")
    for sizes in ((5, 5, 5, 5, 5, 5, 1), (1, 1, 1)):
        try:
            kind = planner.from_kind(feature(*sizes))[0]
        except planner.Garbled as e:
            pytest.fail(f"642.2: a split into {len(sizes)} stories of {list(sizes)} criteria was refused: {e}")
        assert kind == "feature", f"642.2: a split into {len(sizes)} stories was not read as a feature"
    with pytest.raises(planner.Garbled):
        planner.from_kind(feature(3))


OLD = ("criteria / 3", "2 to 5", "1 to 3", "at most 3,", "more than 15", "up to five stories", "than 15 criteria")


def test_the_rules_agents_read_say_five_per_story_and_no_cap(record_property):
    """The agents' rules say 1 to 5 criteria per story, no cap on stories.

    Reads the planner prompt, the plan grade and the reviewer prompt: each says "1 to 5 criteria" and "no cap", and none
    keeps the old rule (three per story, two to five stories, fifteen at most). AGENTS.md no longer says "2 to 5
    children", and the reviewer's empty size line asks about 1 to 5 criteria.

    Proves 642.3."""
    record_property("proves", "642.3")
    for name in ("planner.md", "plan-grade.md", "reviewer.md"):
        text = " ".join(open(os.path.join(ROOT, "dokima", "roles", name)).read().split())
        assert "1 to 5 criteria" in text, f"642.3: {name} never says a story holds 1 to 5 criteria"
        assert "no cap" in text, f"642.3: {name} never says there is no cap on stories"
        old = [o for o in OLD if o in text]
        assert not old, f"642.3: {name} still states the old size rule: {old}"
    agents = " ".join(open(os.path.join(ROOT, "AGENTS.md")).read().split())
    assert "2 to 5 children" not in agents, "642.3: AGENTS.md still caps a split at 2 to 5 children"
    said = " ".join(agent.problems_size({"verdict": "approve"}))
    assert "1 to 5 criteria" in said and "1 to 3" not in said, \
        f"642.3: the reviewer's empty size line still asks about the old rule: {said}"

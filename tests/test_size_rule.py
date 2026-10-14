"""The size rule: five criteria per story, at most 3 questions, a size verdict."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import agent, planner  # noqa: E402

C = {"text": "t", "source": "s"}


def story(k):
    return {"acceptance_criteria": [C] * k, "non_functional": []}


@pytest.mark.parametrize("sizes", [[1], [3], [2, 2], [3, 3], [3, 3, 1], [3, 3, 3, 3, 3]])
def test_the_right_number_of_stories_passes(sizes):
    """Stories of 1 to 5 criteria each pass (#642)."""
    planner.check_size([story(k) for k in sizes])


def test_more_than_three_questions_stops_even_on_autopilot():
    """A plan with 4 questions for the owner stops, whatever autopilot says."""
    q = {"kind": "question", "to": "owner", "id": "P1", "text": "q"}
    rec = {"role": "planner", "handback": {"raises": [q] * 4}, "check": {"passed": True}}
    step = agent.next_step([], rec, ["boss"], autopilot=lambda: True)
    assert step[0] == "stop" and "not ready" in step[1]


def test_a_plan_review_needs_a_size_verdict_and_never_approves_a_broken_size():
    """No size line, or approve with a broken size, is refused."""
    assert agent.problems_size({"verdict": "approve"})
    assert agent.problems_size({"verdict": "approve", "size": "story 1 bundles two behaviors"})
    assert not agent.problems_size({"verdict": "approve", "size": "ok"})
    assert not agent.problems_size({"verdict": "block", "size": "story 1 bundles two behaviors"})


def test_every_criterion_is_judged_one_behavior_and_a_bundle_breaks_size():
    """Each criterion needs a one-behavior judgment; a bundled one cannot pass as ok."""
    ok = {"verdict": "approve", "size": "ok",
          "behaviors": [{"criterion": "7.1", "one_behavior": True, "why": "one result"}]}
    assert not agent.problems_size(ok, ["7.1"])
    assert agent.problems_size(dict(ok, behaviors=[]), ["7.1"])
    bundled = dict(ok, behaviors=[{"criterion": "7.1", "one_behavior": False, "why": "X and Y"}])
    assert agent.problems_size(bundled, ["7.1"])


def test_every_test_is_judged_and_a_test_checking_more_never_approves():
    """Each test the plan names needs a judgment; one checking more than its behavior cannot pass."""
    plan = {"tests": {"7.1": ["tests/t.py::a"]}}
    ok = {"verdict": "approve", "tests": [{"test": "tests/t.py::a", "only_its_behavior": True, "why": "one result"}]}
    assert not agent.problems_tests(ok, plan)
    assert agent.problems_tests(dict(ok, tests=[]), plan)
    wide = dict(ok, tests=[{"test": "tests/t.py::a", "only_its_behavior": False, "why": "also checks links"}])
    assert agent.problems_tests(wide, plan)
    assert not agent.problems_tests(dict(wide, verdict="block"), plan)


def test_a_story_of_a_parent_never_splits_again():
    """A parent's story holds at most 5 criteria and never becomes a feature (#642)."""
    planner.check_size([story(5)], nested=True)
    for sizes in ([6], [2, 2]):
        with pytest.raises(planner.Garbled, match="never splits again"):
            planner.check_size([story(k) for k in sizes], nested=True)

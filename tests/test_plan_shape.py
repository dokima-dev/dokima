"""The planner's hand-back: one plan.json in the agreed shape, read by code, shown on the run page.

Covers #138: the prompt teaches the agreed terms and examples, code accepts the story and feature
kinds (#154 took the lone question away), test labels come from what the plan declares, and every run shows what it handed back.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROMPT = " ".join(open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read().split())
SRC = "https://github.com/o/r/issues/9"
STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id instead of timing out.", "user_story": "Slow calls return a job id.",
         "acceptance_criteria": [{"text": "A slow call returns a job id within 20 s.", "source": SRC}],
         "non_functional": [{"text": "Job ids never repeat.", "why": "two jobs would share results", "principle": "fail closed"}],
         "scope": ["dokima/jobs.py"], "out_of_scope": ["No retries."],
         "tests": {"9.1": ["tests/test_jobs.py::test_id"], "9.2": ["tests/test_jobs.py::test_unique"]}}


def hand_back(tmp_path, content):
    (tmp_path / "plan.json").write_text(json.dumps(content))
    return planner.read_output(str(tmp_path))


def test_prompt_teaches_the_terms_voice_and_every_example(record_property):
    """The planner's prompt teaches the agreed terms, the product voice and an example for every rule.

    Reads the prompt and looks for each term, each of the owner's six approved examples, and one
    example per rule (user story, feature, bug fix, non-functional, scope, docstring, question, concern).
    """
    record_property("proves", "138.1")
    for term in ["User story", "Feature", "Acceptance criteria", "Non-functional requirements", "Definition of Done",
                 "Scope", "Out of scope", "third person", '"All tests", never "Full suite"', "Docstrings"]:
        assert term in PROMPT, f"138.1: the prompt never mentions {term!r}"
    for approved in ["Agents can change workflow files, but only", '"Waiting on me" always shows exactly',
                     "Work starts with a comment, the way you'd ask", "The planner may change or delete older tests, and the owner",
                     "A rejected plan never fails silently", "Repos without a board are left alone"]:
        assert approved in PROMPT, f"138.1: the owner's approved example is missing: {approved!r}"
    for rule in ["- User story:", "- Feature:", "- Bug fix as a criterion:", "- Non-functional with reason",
                 "- Scope:", "- Test docstring:", "- Question:", "- Concern:"]:
        assert rule in PROMPT, f"138.1: no example for {rule!r}"
    assert "Objective:" not in PROMPT and "Non-goals:" not in PROMPT, "138.1: the prompt still uses Objective or Non-goals"


def test_a_story_is_read_with_criteria_then_non_functional(record_property, tmp_path):
    """A story's acceptance criteria come first and its non-functional requirements follow, numbered in that order.

    Hands back a story with one criterion and one non-functional requirement and checks both reach the plan.
    """
    record_property("proves", "138.2")
    kind, p = hand_back(tmp_path, STORY)
    assert kind == "plan" and p["objective"] == "Slow calls return a job id.", "138.2: the user story was not read"
    assert p["criteria"][0] == "A slow call returns a job id within 20 s.", "138.2: acceptance criterion not first"
    assert p["criteria"][1].startswith("Job ids never repeat."), "138.2: non-functional requirement not second"
    assert p["non_goals"] == ["No retries."], "138.2: out of scope was lost"


@pytest.mark.parametrize("change,why", [
    (lambda s: s["acceptance_criteria"][0].pop("source"), "no source link"),
    (lambda s: s["non_functional"][0].pop("why"), "text and why"),
    (lambda s: s.pop("tests"), "tests as a map"),
    (lambda s: s.update(user_story=" "), "user_story"),
    (lambda s: s.update(kind="essay"), "user_story"),
])
def test_a_story_missing_a_rule_is_rejected_with_why(record_property, tmp_path, change, why):
    """A story with a criterion with no source, a requirement with no reason, or no declared tests is rejected, saying why.

    Breaks one rule at a time and checks the rejection names it.
    """
    record_property("proves", "138.2")
    broken = json.loads(json.dumps(STORY))
    change(broken)
    with pytest.raises(planner.Garbled, match=why):
        hand_back(tmp_path, broken)


def test_a_feature_is_shown_as_handed_back(record_property, tmp_path):
    """A feature is handed back in plan.json and shown to the owner, not rejected.

    Hands back a feature with two stories and checks it is read; a feature with one story is rejected.
    """
    record_property("proves", "138.2")
    story = {"title": "t", "user_story": "u", "acceptance_criteria": [{"text": "a", "source": SRC}] * 3, "depends_on": []}
    assert hand_back(tmp_path, {"kind": "feature", "summary": "s", "feature": "f", "stories": [story, story]})[0] == "feature", "138.2: feature not read"
    with pytest.raises(planner.Garbled, match="2 to 5"):
        hand_back(tmp_path, {"kind": "feature", "summary": "s", "feature": "f", "stories": [story]})


def test_labels_come_from_the_plan_not_from_test_text(record_property):
    """A test that contains sample test code, or a renamed older test, is judged by what the plan declares.

    Replays tonight's two false rejections on #138: sample text inside a test, and a rename that kept its old label.
    """
    record_property("proves", "138.3")
    sample = 'def test_x(record_property):\\n    record_property("pro" + "ves", "7.1")\\n'
    before = {"tests/t.py": 'def test_old(record_property):\n    record_property("proves", "80.1")\n'}
    after = {"tests/t.py": 'def test_new_name(record_property):\n    record_property("proves", "80.1")\n\n'
                           'def test_checker(record_property):\n    record_property("proves", "9.1")\n'
                           f'    src = """{sample}"""\n'}
    tc = planner.test_changes(["tests/t.py"], lambda p: before.get(p, ""), lambda p: after.get(p, ""))
    declared = {"9.1": ["tests/t.py::test_checker"], "9.2": ["tests/t.py::test_new_name"]}
    tc = planner.declared_labels(tc, declared)
    p = {"criteria": ["a", "b"], "test_changes": {"tests/t.py::test_old": "renamed to test_new_name for the new words"}}
    assert planner.problems("9", p, ["tests/t.py"], tc) == [], "138.3: a declared plan was still rejected"


def test_every_run_shows_what_the_planner_handed_back(record_property):
    """Every planner run shows the plan.json it handed back on the run's page, even when the plan is rejected.

    Reads the planner workflow and checks the step that writes plan.json into the run summary always runs, before the check.
    """
    record_property("proves", "138.4")
    wf = open(os.path.join(ROOT, ".github", "workflows", "planner.yml")).read()
    show = wf.index("- name: Show what the planner handed back")
    assert show < wf.index("- name: Check what the planner handed back"), "138.4: shown only after the check"
    step = wf[show:wf.index("- name: Check what the planner handed back")]
    assert "if: always()" in step and "GITHUB_STEP_SUMMARY" in step and "plan.json" in step, "138.4: plan.json not shown on every run"

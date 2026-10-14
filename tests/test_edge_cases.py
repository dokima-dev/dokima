"""Every plan lists each criterion's edge cases with their tests, or why there are none.

Covers #536, story 1 of #531. The planner's hand-back gives each criterion either `edge_cases`, a list of
{"case": ..., "test": "path::name"} where the test is one the plan files under that criterion, or `no_edge_cases`, the
reason it has none. The plan check rejects a criterion with neither, naming it, and the planner's prompt teaches the
guiding kinds (error, timeout, bad data, empty) with examples, saying other kinds count too.
"""
import copy
import json
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import planner  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROMPT = open(os.path.join(ROOT, "dokima", "roles", "planner.md")).read()
SRC = "https://github.com/o/r/issues/9"
STORY = {"kind": "user_story", "summary": "Slow calls hand back a job id instead of timing out.",
         "user_story": "Slow calls return a job id.",
         "acceptance_criteria": [
             {"text": "A slow call returns a job id within 20 s.", "source": SRC, "files": ["dokima/jobs.py"],
              "edge_cases": [{"case": "The service times out.", "test": "tests/test_jobs.py::test_timeout"},
                             {"case": "The call has no body.", "test": "tests/test_jobs.py::test_id"}]},
             {"text": "The job id is shown on the page.", "source": SRC, "files": ["dokima/jobs.py"],
              "no_edge_cases": "the page only prints the id the call returned"}],
         "non_functional": [{"text": "Job ids never repeat.", "why": "two jobs would share results", "files": ["dokima/jobs.py"],
                             "edge_cases": [{"case": "Two calls in the same second.", "test": "tests/test_jobs.py::test_unique"}]}],
         "scope": ["dokima/jobs.py"],
         "tests": {"9.1": ["tests/test_jobs.py::test_id", "tests/test_jobs.py::test_timeout"],
                   "9.2": ["tests/test_jobs.py::test_page"], "9.3": ["tests/test_jobs.py::test_unique"]}}


def hand_back(tmp_path, content):
    """Writes plan.json into a fresh hand-back folder and runs the plan check's reader on it."""
    (tmp_path / "plan.json").write_text(json.dumps(content))
    return planner.read_output(str(tmp_path))


def rejection(tmp_path, content):
    """The plan check's reason for rejecting this hand-back, or None when it is accepted."""
    try:
        hand_back(tmp_path, content)
    except planner.Garbled as e:
        return str(e)
    return None


def test_a_plan_lists_each_criterions_edge_cases_each_with_its_test(record_property, tmp_path):
    """A plan lists each criterion's edge cases with their tests, or why there are none.

    Proves 536.1. Hands back a plan whose criteria list edge cases with their tests, or a reason for none, and checks
    it is accepted with the lists kept; then checks an edge case with no test, or with a test not filed under its
    criterion, is rejected naming that criterion; and that the prompt's hand-back shape teaches both fields.
    """
    record_property("proves", "536.1")
    why = rejection(tmp_path, STORY)
    assert why is None, f"536.1: a plan listing every criterion's edge cases with their tests was rejected: {why}"
    kind, p = hand_back(tmp_path, STORY)
    assert p["raw"]["acceptance_criteria"][0]["edge_cases"] == STORY["acceptance_criteria"][0]["edge_cases"], \
        "536.1: the plan's edge cases were not kept as handed back"

    no_test = copy.deepcopy(STORY)
    del no_test["acceptance_criteria"][0]["edge_cases"][0]["test"]
    why = rejection(tmp_path, no_test)
    assert why and "acceptance criterion 1" in why, \
        f"536.1: an edge case with no test was not rejected naming acceptance criterion 1: {why!r}"

    no_case = copy.deepcopy(STORY)
    no_case["acceptance_criteria"][0]["edge_cases"][0]["case"] = " "
    why = rejection(tmp_path, no_case)
    assert why and "acceptance criterion 1" in why, \
        f"536.1: an edge case with no words saying what it is was not rejected naming acceptance criterion 1: {why!r}"

    elsewhere = copy.deepcopy(STORY)
    elsewhere["acceptance_criteria"][0]["edge_cases"][0]["test"] = "tests/test_jobs.py::test_page"
    why = rejection(tmp_path, elsewhere)
    assert why and "acceptance criterion 1" in why, \
        f"536.1: an edge case whose test is filed under another criterion was not rejected naming acceptance criterion 1: {why!r}"

    nfr = copy.deepcopy(STORY)
    nfr["non_functional"][0]["edge_cases"][0]["test"] = "tests/test_jobs.py::test_ghost"
    why = rejection(tmp_path, nfr)
    assert why and "non-functional requirement 1" in why, \
        f"536.1: a requirement's edge case with a test the plan never names was not rejected naming it: {why!r}"

    shape = PROMPT[PROMPT.index("# What you hand back"):]
    assert '"edge_cases"' in shape and '"no_edge_cases"' in shape, \
        "536.1: the planner's prompt never shows edge_cases and no_edge_cases in the plan.json it hands back"


@pytest.mark.parametrize("gap", ["missing", "empty list", "blank reason"])
def test_a_criterion_with_neither_edge_cases_nor_a_reason_is_rejected_naming_it(record_property, tmp_path, gap):
    """A criterion with neither edge cases nor a reason is rejected, naming it.

    Proves 536.2. Takes a good plan, strips the second criterion's reason (left out, an empty list of edge cases, or a
    blank reason) and checks the plan check rejects it naming acceptance criterion 2 and only that one; does the same
    to the non-functional requirement.
    """
    record_property("proves", "536.2")
    assert rejection(tmp_path, STORY) is None, "536.2: the good plan beside the bad one was rejected"
    bad = copy.deepcopy(STORY)
    c = bad["acceptance_criteria"][1]
    del c["no_edge_cases"]
    if gap == "empty list":
        c["edge_cases"] = []
    elif gap == "blank reason":
        c["no_edge_cases"] = "  "
    why = rejection(tmp_path, bad)
    assert why is not None, f"536.2 ({gap}): a criterion with neither edge cases nor a reason was accepted"
    assert "acceptance criterion 2" in why and "acceptance criterion 1" not in why, \
        f"536.2 ({gap}): the rejection does not name acceptance criterion 2 alone: {why!r}"

    bad = copy.deepcopy(STORY)
    c = bad["non_functional"][0]
    del c["edge_cases"]
    if gap == "empty list":
        c["edge_cases"] = []
    elif gap == "blank reason":
        c["no_edge_cases"] = ""
    why = rejection(tmp_path, bad)
    assert why and "non-functional requirement 1" in why, \
        f"536.2 ({gap}): a requirement with neither edge cases nor a reason was not rejected naming it: {why!r}"


def section(text, title):
    """The markdown section under the heading starting with title, up to the next heading."""
    found = re.search(rf"^#+ {re.escape(title)}[^\n]*\n(.*?)(?=^#|\Z)", text, re.S | re.M)
    return found.group(1) if found else None


def test_the_planners_prompt_gives_the_guiding_kinds_with_examples_and_says_other_kinds_count(record_property):
    """The planner's prompt gives guiding kinds of edge cases with examples, saying others count.

    Proves 536.3. Reads the prompt's Edge cases section and checks it holds one bullet per kind, starting with the
    kind in bold and giving an example after "Example:", and a line saying other kinds count too.
    """
    record_property("proves", "536.3")
    body = section(PROMPT, "Edge cases")
    assert body is not None, "536.3: the planner's prompt has no Edge cases section"
    for kind in ["Error", "Timeout", "Bad data", "Empty"]:
        bullet = re.search(rf"^- \*\*{kind}[^*]*\*\*(.*)$", body, re.M)
        assert bullet, f"536.3: the Edge cases section has no bullet for {kind}"
        example = bullet.group(1).partition("Example:")[2].strip()
        assert example, f"536.3: the {kind} bullet gives no example after 'Example:'"
    assert re.search(r"other kinds count", body, re.I), \
        "536.3: the Edge cases section never says other kinds count too"

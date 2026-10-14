"""Each criterion on the card shows its edge cases, or why it has none (#538).

The planner lists each criterion's edge cases, each with its test, or says why there are none (#531). These tests draw
the issue card and the PR card with `dokima/card.py` for a plan of issue #40 whose criteria carry edge cases, a reason
for none, or neither (a plan written before edge cases existed), and read the lines under each criterion. Each
criterion is sourced from the parent #30, so its Source line shows and the edge case line can be placed between
Verified by and Source.

Since #628 the card draws what the owner approved on the card of #557: a test's Verified by line is labelled
Acceptance test, and the edge cases sit in one closed fold titled Edge cases, one list item per case.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest

from dokima import card, plan  # noqa: E402

REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
PARENT = "https://github.com/o/r/issues/30"
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40", "html_url": "https://github.com/o/r/pull/5",
      "merged_by": None}
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}
CASES = ["GitHub answers 500 while the card is redrawn", "An issue with no comments", "A plan whose tests field is a list"]
REASON = "it only renames a label the owner sees"
CRITERIA = [
    {"text": "Cases thing works", "words": "one card", "source": PARENT,
     "edge_cases": [{"case": c, "test": "tests/test_a.py::test_1"} for c in CASES]},
    {"text": "Reason thing works", "words": "one card", "source": PARENT, "no_edge_cases": REASON},
    {"text": "Older thing works", "words": "one card", "source": PARENT},
]
PLAN = {"kind": "user_story", "summary": "Owners see one card.", "user_story": "Owners see one card on every issue.",
        "acceptance_criteria": CRITERIA, "non_functional": [], "scope": ["dokima/card.py"],
        "tests": {f"40.{k}": [f"tests/test_a.py::test_{k}"] for k in range(1, len(CRITERIA) + 1)},
        "links": {"blocked_by": [], "blocks": [], "relates_to": []}}
TESTS = {f"tests/test_a.py::test_{k}": {"verified_by": f"Thing {k} runs.",
                                        "url": f"https://github.com/o/r/blob/abc/tests/test_a.py#L{k}"}
         for k in range(1, len(CRITERIA) + 1)}


def rec(role, stage=None, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}"}


FOUND = {"recs": [rec("planner", n=11, **PLAN), rec("reviewer", "plan", n=12, verdict="approve"), rec("worker", n=13)],
         "pr": PR, "check_runs": [], "reviews": [], "owners": {"boss"}, "tests": TESTS, "worker": DONE, "children": []}


def draw(page):
    """The card's markdown between its markers, on the issue or on its pull request."""
    text = card.render(REPO, ISSUE, dict(FOUND), page=page)
    assert plan.CARD_START in text and plan.CARD_END in text, "the card has no markers"
    return text[text.index(plan.CARD_START) + len(plan.CARD_START):text.index(plan.CARD_END)]


def under(text, words):
    """The indented lines under the criterion whose sentence is `words`."""
    lines = text.splitlines()
    at = [i for i, l in enumerate(lines) if l.startswith("- ") and words in l]
    assert len(at) == 1, f"the card has {len(at)} criteria saying “{words}”"
    out = []
    for l in lines[at[0] + 1:]:
        if not l.startswith("  "):
            break
        out.append(l)
    return out


def between(lines, crit, page):
    """The lines strictly between the criterion's last Verified by line and its Source line."""
    vb = [i for i, l in enumerate(lines) if "Acceptance test</a>" in l]
    src = [i for i, l in enumerate(lines) if "Source" in l]
    assert vb and src, f"{crit}: on the {page} card the criterion lost its Verified by or Source line: {lines}"
    return lines[vb[-1] + 1:src[0]]


@pytest.mark.parametrize("page", ["issue", "pr"])
def test_edge_cases_show_on_one_line_between_verified_by_and_source(record_property, page):
    """Edge cases show in one fold between Verified by and Source, one item each.

    Draws both cards for a criterion with three edge cases and checks exactly one line sits between its Verified by
    and Source lines: a closed fold titled Edge cases holding the three cases in order, one list item each. Proves
    538.1."""
    record_property("proves", "538.1")
    mid = between(under(draw(page), "Cases thing works"), "538.1", page)
    assert len(mid) == 1, f"538.1: on the {page} card the edge cases are not one line between Verified by and Source: {mid}"
    line = mid[0]
    missing = [c for c in CASES if c not in line]
    assert not missing, f"538.1: on the {page} card the edge case line misses {missing}: {line}"
    assert re.match(r"\s*<details><summary>.*Edge cases.*</summary>", line) and line.endswith("</details>"), \
        f"538.1: on the {page} card the edge cases are not one closed fold titled Edge cases: {line}"
    items = [re.sub(r"<[^>]*>", "", i) for i in re.findall(r"<li>(.*?)</li>", line)]
    assert items == CASES, f"538.1: on the {page} card the edge cases are not one list item each, in order: {items}"


@pytest.mark.parametrize("page", ["issue", "pr"])
def test_no_edge_cases_shows_none_because_and_the_reason(record_property, page):
    """A criterion with no edge cases shows "none, because" and its reason on that line.

    Draws both cards for a criterion whose plan says why it has no edge cases and checks the one line between its
    Verified by and Source lines reads "none, because" followed by that reason. A criterion from a plan written before
    edge cases existed, with neither field, must show no such line, so an empty "none, because" never appears. Proves 538.2."""
    record_property("proves", "538.2")
    text = draw(page)
    older = between(under(text, "Older thing works"), "538.2", page)
    assert not older, f"538.2: on the {page} card a criterion with no edge case fields shows: {older}"
    mid = between(under(text, "Reason thing works"), "538.2", page)
    assert len(mid) == 1, f"538.2: on the {page} card the line for no edge cases is missing or split: {mid}"
    assert f"none, because {REASON}" in mid[0], \
        f"538.2: on the {page} card the line does not read 'none, because {REASON}': {mid[0]}"


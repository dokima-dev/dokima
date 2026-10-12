"""A criterion's Source shows only when it points away from its issue (#526).

Most criteria quote the owner's issue, so a Source line naming the issue it sits on tells the owner nothing (#524).
These tests draw the issue card and the PR card with `dokima/card.py` for a plan of issue #40 whose criteria are
sourced from the issue itself, a comment on it, its parent #30 and a comment on the parent, and read each criterion's
lines. That the other sources still show is pinned by `tests/test_card_refs.py` (526.2), and that every source is
still recorded and checked by `tests/test_parent_source.py` (526.3).
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest

from dokima import card, plan  # noqa: E402

REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
COMMENT = "https://github.com/o/r/issues/40#issuecomment-111"
PARENT = "https://github.com/o/r/issues/30"
PARENT_COMMENT = "https://github.com/o/r/issues/30#issuecomment-222"
PR = {"number": 5, "merged": False, "state": "open", "body": "Closes #40", "html_url": "https://github.com/o/r/pull/5",
      "merged_by": None}
DONE = {"status": "completed", "conclusion": "success", "html_url": "https://github.com/o/r/actions/runs/1"}
CRITERIA = [("Own issue thing works", ISSUE["url"]), ("Own comment thing works", COMMENT),
            ("Parent thing works", PARENT), ("Parent comment thing works", PARENT_COMMENT)]
PLAN = {"kind": "user_story", "summary": "Owners see one card.", "user_story": "Owners see one card on every issue.",
        "acceptance_criteria": [{"text": t, "words": "one card", "source": s} for t, s in CRITERIA],
        "non_functional": [], "scope": ["dokima/card.py"], "out_of_scope": [],
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


def source_lines(text, words):
    """The Source lines under the criterion whose sentence is `words`, without their bullet."""
    return [re.sub(r"^\s*-\s*", "", l) for l in under(text, words) if "Source" in l]


@pytest.mark.parametrize("page", ["issue", "pr"])
def test_a_criterion_sourced_from_its_own_issue_shows_no_source_line(record_property, page):
    """A criterion quoting its own issue shows no Source line on either card.

    Draws both cards of issue #40 and checks the criterion whose source is the issue's own link has no Source line
    under it, while the criterion sourced from the parent on the same card still shows one, so dropping every Source
    line does not pass. Proves 526.1."""
    record_property("proves", "526.1")
    text = draw(page)
    own = source_lines(text, "Own issue thing works")
    assert not own, f"526.1: on the {page} card the criterion sourced from its own issue still shows: {own}"
    assert source_lines(text, "Parent thing works"), \
        f"526.1: on the {page} card the criterion sourced from the parent lost its Source line too"

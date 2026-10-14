"""A criterion with no automated test shows on the card as not verified.

Issue #670, from #661. The owner: "An ask that can't be checked becomes a question to me, or shows on the card as not
verified."

Each test draws the issue card with `dokima/card.render` from an approved plan in which some criteria list a test and
others list none, then reads the words under each criterion's bullet: the bullet itself and the indented lines below
it, up to the next criterion. A criterion with no test must read "not verified" there; one with a test must not.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dokima import card, plan  # noqa: E402

REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
ASK = "https://github.com/o/r/issues/40"
TESTS = {"tests/test_a.py::test_one": {"verified_by": "The first thing runs.",
                                       "url": "https://github.com/o/r/blob/abc/tests/test_a.py#L1"}}


def story(tests, nfr=()):
    """An approved plan's hand-back with two acceptance criteria, the non-functional ones `nfr`, and `tests`."""
    return {"kind": "user_story", "summary": "Owners see one card.", "user_story": "Owners see one card on every issue.",
            "acceptance_criteria": [{"text": "First thing works", "source": ASK},
                                    {"text": "Second thing looks right", "source": ASK}],
            "non_functional": [{"text": t, "why": "It matters.", "source": ASK} for t in nfr],
            "scope": ["dokima/card.py"], "tests": tests, "test_changes": {}}


def rec(role, stage=None, n=1, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": f"https://github.com/o/r/actions/runs/{n}"}


def draw(handback):
    """The card for issue 40 once `handback` is approved, with no pull request yet."""
    recs = [rec("planner", n=11, **handback), rec("reviewer", "plan", n=12, verdict="approve")]
    found = {"recs": recs, "pr": None, "check_runs": [], "reviews": [], "owners": {"boss"}, "tests": TESTS,
             "worker": None, "children": []}
    return card.render(REPO, ISSUE, found)


def plain(html):
    """The words a reader sees: no images, tags, italic or bold markers."""
    text = re.sub(r"<img [^>]*>", "", html)
    text = re.sub(r"</?[a-zA-Z][^>]*>", "", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("*", "").replace("_", "")).strip()


def under(text, words, k):
    """The words a reader sees on the bullet holding `words` and below it.

    Fails naming criterion k unless the card holds exactly one bullet with those words."""
    assert plan.CARD_START in text and plan.CARD_END in text, f"{k}: the text holds no card between its markers"
    lines = text[text.index(plan.CARD_START):text.index(plan.CARD_END)].splitlines()
    starts = [i for i, l in enumerate(lines) if l.lstrip().startswith("- ") and words in l]
    assert len(starts) == 1, f"{k}: expected one bullet holding “{words}”, found {len(starts)}:\n" + "\n".join(lines)
    i = starts[0]
    indent = len(lines[i]) - len(lines[i].lstrip())
    block = [lines[i]]
    for line in lines[i + 1:]:
        if not line.strip() or len(line) - len(line.lstrip()) <= indent:
            break
        block.append(line)
    return plain("\n".join(block))


def test_a_criterion_with_no_test_shows_as_not_verified(record_property):
    """A criterion with no test reads not verified; one with a test does not.

    Draws the card of a plan whose first criterion lists a test and whose second lists none, then checks the second
    criterion's bullet reads not verified, and the first's does not. Proves 670.3."""
    record_property("proves", "670.3")
    text = draw(story({"40.1": ["tests/test_a.py::test_one"]}))
    seen = under(text, "Second thing looks right", "670.3")
    assert "not verified" in seen.lower(), \
        f"670.3: the criterion with no test does not show as not verified on the card: {seen}"
    seen = under(text, "First thing works", "670.3")
    assert "not verified" not in seen.lower(), \
        f"670.3: the criterion with a test shows as not verified on the card: {seen}"


def test_a_criterion_filed_with_an_empty_test_list_shows_as_not_verified(record_property):
    """A criterion filed with an empty list of tests reads not verified.

    Draws the card of a plan whose tests map gives the second criterion an empty list, and checks its bullet reads
    not verified. Proves 670.3."""
    record_property("proves", "670.3")
    text = draw(story({"40.1": ["tests/test_a.py::test_one"], "40.2": []}))
    seen = under(text, "Second thing looks right", "670.3")
    assert "not verified" in seen.lower(), \
        f"670.3: the criterion filed with no tests does not show as not verified on the card: {seen}"


def test_a_non_functional_requirement_with_no_test_shows_as_not_verified(record_property):
    """A non-functional requirement with no test reads not verified in its fold.

    Draws the card of a plan with one non-functional requirement and no test filed for it, and checks its bullet,
    inside the Non-functional requirements fold, reads not verified. Proves 670.3."""
    record_property("proves", "670.3")
    text = draw(story({"40.1": ["tests/test_a.py::test_one"], "40.2": ["tests/test_a.py::test_one"]},
                      nfr=["Nothing leaks"]))
    seen = under(text, "Nothing leaks", "670.3")
    assert "not verified" in seen.lower(), \
        f"670.3: the non-functional requirement with no test does not show as not verified on the card: {seen}"

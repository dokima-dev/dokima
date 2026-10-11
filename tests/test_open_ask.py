"""The owner's folded text is never changed by a redraw, nor read as the plan.

Issue #237, story 4 of #230, opened the owner's ask below the card; issue #373 folds every ask again under a closed
`<details><summary>Original issue</summary>` (tests/test_card_folds.py proves that). What #237 kept still holds: an
issue whose body is a split's story, quoted by code from the parent's approved plan (dokima/agent.py story_body),
keeps the fold; a redraw that would change the owner's text is refused, leaving the body as it was and saying why on
the issue; and the owner's old checkboxes are never read as the plan.

GitHub is faked by the same recorder tests/test_body.py uses; the card's main runs as in those tests.
"""
import re
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dokima import agent, body, plan, planner  # noqa: E402
from test_body import NUMBER, PLAN_TOP, REPO, TRICKY, github, run_card  # noqa: E402,F401

FOLD_SUMMARY = "<summary>Original issue</summary>"
OLD_FOLD_START = "\n<details><summary>Original issue</summary>\n\n"
OLD_FOLD_END = "\n\n</details>"

STORY = {"title": "Open asks", "user_story": "The owner's ask reads open.",
         "context": "dokima/body.py folds the ask.",
         "acceptance_criteria": [{"text": "The ask shows open.", "source": "https://github.com/o/r/issues/230"}],
         "non_functional": [{"text": "Refusals still say why.", "why": "the owner's words are never rewritten"}]}


def below(text):
    """Everything below the one marker."""
    assert text.count(body.MARKER) == 1, f"expected exactly one marker, found {text.count(body.MARKER)}"
    return text.split(body.MARKER, 1)[1]


def assert_folded(k, new, ask):
    """Fail naming criterion k unless the ask sits inside one closed Original issue fold."""
    part = re.sub(r"\n\n<!-- dokima-done -->\n[^\n]*$", "", below(new).rstrip("\n"))  # since #416 Done sits last, after the fold
    assert body.ask(new) == ask, f"{k}: the quoted ask does not read back byte for byte"
    head = part.lstrip()
    assert head.startswith("<details>" + FOLD_SUMMARY), f"{k}: the ask is not folded under Original issue"
    assert part.rstrip().endswith("</details>"), f"{k}: the Original issue fold is not closed after the quoted story"
    assert ask in part, f"{k}: the quoted story is not inside the fold as written"


def old_folded(top, ask):
    """A body saved before this change: the card, the marker, and the ask in the closed Original issue fold."""
    return top.rstrip("\n") + "\n\n" + body.MARKER + OLD_FOLD_START + ask + OLD_FOLD_END


# 237.3: where the owner's text is quoted from somewhere else, like a split's sub-issues, it stays folded

def test_a_split_story_stays_folded(record_property):
    """A split's sub-issue, whose text is quoted from the parent's approved plan, keeps it folded.

    Draws a story body the way code files a split's sub-issue, redraws it fresh and again, and checks the quoted
    story sits in one closed Original issue fold below the marker, byte for byte. Beside it, an owner's ask on the
    same redraw is folded the same way."""
    record_property("proves", "237.3")
    quoted = agent.story_body(230, 4, STORY, "Cards show everything")
    new = body.redraw(quoted, "the card")
    assert_folded("237.3", new, quoted)
    again = body.redraw(new, "another card")
    assert_folded("237.3", again, quoted)
    assert below(again) == below(new), "237.3: a redraw changed the part below the marker of a split's story"
    assert_folded("237.3", body.redraw("An owner's own ask.", "the card"), "An owner's own ask.")


def test_a_split_story_folded_today_stays_folded(record_property, monkeypatch, github):
    """A split's sub-issue already folded today stays folded when the card is drawn again.

    Runs the card's main on an old folded body holding a split's story and checks the saved body keeps it in the
    Original issue fold, byte for byte, with no refusal posted. Beside it, a folded owner's ask stays folded."""
    record_property("proves", "237.3")
    quoted = agent.story_body(230, 2, STORY, "Cards show everything")
    saved = run_card(monkeypatch, github, old_folded(PLAN_TOP, quoted))
    assert saved is not None, "237.3: the card saved nothing on a split's story"
    assert_folded("237.3", saved, quoted)
    assert not github.comments, "237.3: redrawing a split's story posted a refusal"
    owners = run_card(monkeypatch, github, old_folded(PLAN_TOP, "An owner's own ask."))
    assert owners is not None, "237.3: the card saved nothing on an owner's ask"
    assert_folded("237.3", owners, "An owner's own ask.")


def test_the_card_folds_a_fresh_split_story(record_property, monkeypatch, github):
    """The first card drawn on a freshly filed sub-issue folds its quoted story.

    Runs the card's main on a sub-issue body exactly as a split files it and checks the saved body keeps the story in
    the Original issue fold, byte for byte. Beside it, a fresh owner's ask is folded the same way."""
    record_property("proves", "237.3")
    quoted = agent.story_body(230, 3, STORY, "Cards show everything")
    saved = run_card(monkeypatch, github, quoted)
    assert saved is not None, "237.3: the card saved nothing on a fresh split story"
    assert_folded("237.3", saved, quoted)
    owners = run_card(monkeypatch, github, "An owner's own ask.")
    assert owners is not None, "237.3: the card saved nothing on an owner's ask"
    assert_folded("237.3", owners, "An owner's own ask.")


# 237.4: a redraw that would change the owner's text is still refused, the body left alone and the reason on the issue

def test_a_redraw_that_would_change_the_ask_is_still_refused(record_property):
    """A redraw that would change the owner's text is refused; a good one goes through.

    Draws a card that holds the marker itself on a folded owner's ask, an old folded ask and a split's story, and
    checks each is refused with a reason; the same bodies with a plain card redraw fine, the ask staying folded."""
    record_property("proves", "237.4")
    quoted = agent.story_body(230, 4, STORY, "Cards show everything")
    assert_folded("237.4", body.redraw("My ask.", "old card"), "My ask.")
    for current in (body.redraw("My ask.", "old card"), old_folded("old card", "My ask."), body.redraw(quoted, "old")):
        with pytest.raises(body.Refused) as refused:
            body.redraw(current, f"a card that quotes {body.MARKER} in a criterion")
        assert str(refused.value).strip(), "237.4: the refusal gives no reason"
        body.redraw(current, "a card that quotes nothing")
    assert_folded("237.4", body.redraw(old_folded("old card", "My ask."), "a card"), "My ask.")


def test_a_refused_save_leaves_the_body_and_says_why(record_property, github):
    """When the owner's text would change, nothing is saved and one comment says why.

    Saves a bad card on a folded ask and on an old folded ask: the body is never written, one comment with the reason
    is posted to this issue each time and the save reports False; a good card then saves with no comment."""
    record_property("proves", "237.4")
    for current in (body.redraw("My ask.", "old card"), old_folded("old card", "My ask.")):
        github.saves.clear()
        github.comments.clear()
        bad = f"a card that quotes {body.MARKER}"
        with pytest.raises(body.Refused) as refused:
            body.redraw(current, bad)
        assert body.save(REPO, NUMBER, current, bad) is False, "237.4: a refused save did not report False"
        assert github.saves == [], "237.4: the body was written although the owner's text would change"
        assert len(github.comments) == 1, f"237.4: expected one comment saying why, got {len(github.comments)}"
        args, text = github.comments[0]
        assert any(a == str(NUMBER) or f"issues/{NUMBER}/" in a for a in args), "237.4: the reason went somewhere other than this issue"
        assert str(refused.value) in (text or ""), "237.4: the comment does not say why the save was refused"
        assert body.save(REPO, NUMBER, current, "good card") is True, "237.4: a good save did not report True"
        assert len(github.saves) == 1 and body.ask(github.saves[0]) == "My ask.", "237.4: a good save changed the owner's text"
        assert len(github.comments) == 1, "237.4: a good save posted a refusal"
        assert_folded("237.4", github.saves[0], "My ask.")


def test_the_owners_text_is_never_read_as_plan(record_property):
    """The owner's old checkboxes, folded, never become plan goals or criteria.

    Writes a plan into an issue whose ask holds old plan checkboxes and checks the plan reads back with only the
    planner's one goal and criterion, the same as for an ask with no checkboxes."""
    record_property("proves", "237.5")
    story = {"objective": "Slow calls return a job id", "criteria": ["A slow call returns a job id within 20 s"],
             "non_goals": [], "scope": ["dokima/jobs.py"], "test_changes": {}}
    ask = "- [ ] Goal: an old goal\n  - [ ] Done when: an old criterion\n- [ ] Objective: another old goal\n"
    new = planner.render("9", ask, story, {})
    assert_folded("237.5", new, ask)
    parsed = plan.parse(new)
    assert [g["text"] for g in parsed["goals"]] == ["Slow calls return a job id"], \
        "237.5: the owner's old checkboxes were read as plan goals"
    assert [c["text"] for c in parsed["goals"][0]["criteria"]] == ["A slow call returns a job id within 20 s"], \
        "237.5: the owner's old checkboxes were read as plan criteria"
    plain = plan.parse(planner.render("9", "No checkboxes here.", story, {}))
    assert [g["text"] for g in plain["goals"]] == ["Slow calls return a job id"], "237.5: a plain ask lost the plan's goal"

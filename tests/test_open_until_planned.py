"""A new issue shows the owner's text open until planned, then folded under Original issue.

Issue #407. #237 promised the owner's ask reads open on the issue they wrote; #373 then folded the owner's text on
every card and #371 put the Definition of Done below that fold, so a brand-new issue showed only a closed "Original
issue" fold and the Definition of Done. The owner asked (2026-10-09) that until an issue has a plan, its original text
shows open, read first, with the Definition of Done below it; once a plan exists the text moves into its Original
issue fold, as today.

A split's sub-issue is not the owner's own text: code quotes it from the parent's approved plan, and #237 (237.3)
decided it stays folded. It keeps its fold here too.

The card is drawn by dokima/card.py render and saved by card.draw through dokima/body.py. These tests run card.draw
with GitHub faked by the recorder in tests/test_body.py (via the helpers of tests/test_new_issue_card.py) and read the
body it saves the way the owner reads the issue.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dokima import agent, body, card, plan, planner  # noqa: E402
from test_body import TRICKY, github  # noqa: E402,F401
from test_new_issue_card import (NO_PLAN, OLD_TOP, PLAN, REPO, SUMMARY, TOPS, draw, found_for, rec,  # noqa: E402
                                 without_comments)

ROOT = os.path.join(os.path.dirname(__file__), "..")
FOLD_START = "\n<details><summary>Original issue</summary>\n\n"
FOLD_END = "\n\n</details>"
OPEN_START = "\n\n"
SUMMARY_TAG = "<summary>Original issue</summary>"
DOD = "**Definition of Done:**"
ASKS = ("Please show my words open.\n", TRICKY, "",
        "<details><summary>My own fold</summary>\n\nA detail I folded myself.\n\n</details>\n",
        "\n\nI started with blank lines.")
STORY = {"title": "Open asks", "user_story": "The owner's ask reads open.", "context": "dokima/body.py",
         "acceptance_criteria": [{"text": "The ask shows open.", "source": "https://github.com/o/r/issues/230"}],
         "non_functional": []}


def folded_new_issue(ask, recs=()):
    """A new issue as #371 saved it: the owner's text folded, the DoD below."""
    return ("<!-- dokima-card -->\n**Backlog**\n\n<!-- /dokima-card -->\n\n" + body.MARKER + FOLD_START + ask
            + FOLD_END + "\n\n" + body.DONE + "\n" + card.done_row(REPO, found_for(list(recs)), None))


def assert_open(k, saved, ask, recs):
    """Fail naming k unless the body reads: card, owner's open text, Definition of Done.

    The card above the one marker has its status line and no Definition of Done; right below the marker the owner's
    text follows byte for byte, in no Original issue fold; after it comes exactly the Definition of Done line the
    card draws, and nothing else the owner can see."""
    assert saved is not None, f"{k}: the card saved nothing on the issue"
    assert saved.count(body.MARKER) == 1, f"{k}: expected exactly one marker, found {saved.count(body.MARKER)}"
    top, below = saved.split(body.MARKER, 1)
    assert "**Backlog**" in top, f"{k}: the card above the owner's text lost its status line:\n{top}"
    assert DOD not in top, f"{k}: the Definition of Done comes before the owner's text:\n{top}"
    assert below.count(SUMMARY_TAG) == ask.count(SUMMARY_TAG), \
        f"{k}: an issue with no plan still folds the owner's text under Original issue:\n{below!r}"
    assert below.startswith(OPEN_START + ask), \
        f"{k}: the owner's text does not show open, byte for byte, right below the card:\n{below!r}"
    after = without_comments(below[len(OPEN_START + ask):]).strip()
    assert after == card.done_row(REPO, found_for(recs), None), \
        f"{k}: below the owner's open text the issue should show only the Definition of Done line, not:\n{after!r}"
    assert saved.count(DOD) == ask.count(DOD) + 1, f"{k}: the Definition of Done shows {saved.count(DOD)} times"
    assert body.ask(saved) == ask, f"{k}: the owner's text does not read back byte for byte: {body.ask(saved)!r}"


def assert_planned_fold(k, saved, ask):
    """Fail naming k unless the owner's text sits alone in the closed Original issue fold."""
    assert saved is not None, f"{k}: the card saved nothing on the planned issue"
    assert saved.count(body.MARKER) == 1, f"{k}: expected exactly one marker, found {saved.count(body.MARKER)}"
    top, below = saved.split(body.MARKER, 1)
    below = re.sub(r"\n\n<!-- dokima-done -->\n[^\n]*$", "", below)  # since #416 Done sits last, after the fold
    assert below == FOLD_START + ask + FOLD_END, \
        f"{k}: once planned, the owner's text is not alone in its closed Original issue fold:\n{below!r}"
    assert body.ask(saved) == ask, f"{k}: the owner's text does not read back byte for byte"


# 407.1: until an issue has a plan, the owner's text shows open, with the Definition of Done below it

def test_a_new_issue_shows_the_owners_text_open(record_property, monkeypatch, github):
    """A new issue shows the owner's text open, with the Definition of Done below.

    Proves 407.1. Draws the card of an issue with no plan (no record, or only a rejected plan) for five asks (plain words, one full
    of Windows line ends and stray markup, an empty one, one with the owner's own fold and one starting with blank
    lines), and checks the saved issue shows the card, then the owner's text byte for byte in no Original issue fold,
    then the Definition of Done line and nothing else."""
    record_property("proves", "407.1")
    for name, recs in NO_PLAN.items():
        for ask in ASKS:
            assert_open(f"407.1 ({name})", draw(monkeypatch, github, ask, recs), ask, recs)
    assert not github.comments, "407.1: drawing a new issue's card posted a refusal"


def test_a_new_issue_folded_today_opens_on_its_next_redraw(record_property, monkeypatch, github):
    """A new issue folded today opens on its next redraw, even by the sweep.

    Proves 407.1. Builds issues with no plan saved as #371 left them (the owner's text folded, the Definition of Done below the
    fold), as before #371 (the Definition of Done above the folded text) and fresh with no marker; redraws each the
    way the 15-minute sweep does (only when it changed) and checks each is rewritten with the owner's text open."""
    record_property("proves", "407.1")
    for ask in ASKS:
        for current in (folded_new_issue(ask), body.MARKER.join([OLD_TOP + "\n\n", FOLD_START + ask + FOLD_END]),
                        ask):
            assert_open("407.1", draw(monkeypatch, github, current, [], changed_only=True), ask, [])


def test_an_open_new_issue_is_not_rewritten_when_nothing_changed(record_property, monkeypatch, github):
    """An open new issue is left alone by the sweep and matches the scan.

    Proves 407.1. Draws a new issue's card, then draws it again the way the 15-minute sweep does and checks nothing is saved; drawn
    again in full it saves the very same body; and the card check the scan uses (card.shows) finds the saved issue
    shows the card Dokima draws now, so it is never flagged or rewritten forever."""
    record_property("proves", "407.1")
    for ask in ASKS:
        saved = draw(monkeypatch, github, ask, [])
        assert_open("407.1", saved, ask, [])
        assert draw(monkeypatch, github, saved, [], changed_only=True) is None, \
            "407.1: the sweep rewrote a new issue whose card had not changed"
        assert draw(monkeypatch, github, saved, []) == saved, "407.1: redrawing a new issue's card changed its body"
        assert card.shows(saved, TOPS[-1]), "407.1: the scan's card check says a freshly saved new issue is out of date"


# 407.2: once a plan exists, the owner's text moves into its closed Original issue fold, as today

def test_once_planned_the_owners_text_folds(record_property, monkeypatch, github):
    """Once planned, the owner's text folds under Original issue, the DoD back in the card.

    Proves 407.2.
    Saves each ask open on a new issue, then records a plan and redraws, also the way the sweep does, and checks the
    owner's text now sits alone in its closed Original issue fold, the Definition of Done shows once as the card's
    last line above it, and the card shows the plan's summary."""
    record_property("proves", "407.2")
    recs = [rec("planner", **PLAN)]
    for ask in ASKS:
        fresh = draw(monkeypatch, github, ask, [])
        assert_open("407.2", fresh, ask, [])
        for changed_only in (False, True):
            saved = draw(monkeypatch, github, fresh, recs, changed_only=changed_only)
            assert_planned_fold("407.2", saved, ask)
            top = saved.split(body.MARKER, 1)[0]
            last = saved.rstrip("\n").splitlines()[-1]
            # Since #416 the Definition of Done is the body's last line, below the Original issue fold.
            assert saved.count(DOD) == ask.count(DOD) + 1 and last.startswith(DOD) and SUMMARY in top, \
                f"407.2: with a plan, the Definition of Done is not the body's last line once: {last!r}"


def test_the_planner_folds_an_open_new_issue(record_property):
    """The planner's save folds a new issue's open text under Original issue.

    Proves 407.2.
    Builds a new issue showing the owner's text open with its Definition of Done below, renders the planner's body on
    it and checks the owner's text sits alone in the closed Original issue fold, read back byte for byte."""
    record_property("proves", "407.2")
    story = {"objective": "Fold the ask", "criteria": ["The ask is folded"], "non_goals": [],
             "scope": ["dokima/body.py"], "test_changes": {}}
    for ask in ASKS:
        open_issue = ("<!-- dokima-card -->\n**Backlog**\n\n<!-- /dokima-card -->\n\n" + body.MARKER + OPEN_START
                      + ask + "\n\n" + body.DONE + "\n" + card.done_row(REPO, found_for([]), None))
        assert_planned_fold("407.2", planner.render("9", open_issue, story, {}), ask)


# 407.3: a split's sub-issue, quoted by code from the parent's plan, keeps its fold before its own plan (237.3)

def test_a_split_story_stays_folded_before_its_own_plan(record_property, monkeypatch, github):
    """A split's sub-issue keeps its quoted story folded before its own plan.

    Proves 407.3.
    Draws the card of a freshly filed sub-issue with no plan of its own and checks the quoted story sits byte for
    byte in the closed Original issue fold with only the Definition of Done after it, redrawn the same; beside it,
    an owner's own ask on the same draw shows open."""
    record_property("proves", "407.3")
    quoted = agent.story_body(230, 3, STORY, "Cards show everything")
    saved = draw(monkeypatch, github, quoted, [])
    assert saved is not None, "407.3: the card saved nothing on a split's story"
    below = saved.split(body.MARKER, 1)[1]
    fold = FOLD_START + quoted + FOLD_END
    assert below.startswith(fold), f"407.3: a split's story with no plan is not in its Original issue fold:\n{below!r}"
    assert without_comments(below[len(fold):]).strip() == card.done_row(REPO, found_for([]), None), \
        "407.3: something other than the Definition of Done follows a split story's fold"
    assert body.ask(saved) == quoted, "407.3: the quoted story does not read back byte for byte"
    assert draw(monkeypatch, github, saved, []) == saved, "407.3: redrawing a split story's card changed its body"
    assert_open("407.3", draw(monkeypatch, github, "An owner's own ask.", []), "An owner's own ask.", [])


# 407.4: the owner's text is never changed: kept byte for byte, or the save is refused and says why

ODD_ASKS = ("My ask.\n\n" + body.DONE + "\nmy own line",
            "My ask.\n\n</details>\n\n<!-- a comment of mine -->\n**Definition of Done:** x",
            "I quoted the fold." + FOLD_START + "inside" + FOLD_END,
            "I quoted the card's end.\n<!-- /dokima-card -->\n\n</details>\n\n")


def test_the_owners_text_is_kept_or_the_save_refused(record_property, monkeypatch, github):
    """The owner's text is kept byte for byte, or the save is refused saying why.

    Proves 407.4.
    Draws a new issue's card on asks that hold the Definition of Done's own marker, a closing fold, a quoted Original
    issue fold and the card's end marker, then redraws with no plan and with a plan; at every save the owner's text
    reads back exactly as written, and a save that cannot keep it is refused with a comment on the issue, never saved
    altered. A plain ask is saved open, not refused."""
    record_property("proves", "407.4")
    for ask in ODD_ASKS:
        current = ask
        for recs in ([], [], [rec("planner", **PLAN)], [rec("planner", **PLAN)]):
            comments = len(github.comments)
            saved = draw(monkeypatch, github, current, recs)
            if saved is None:
                assert len(github.comments) > comments, \
                    f"407.4: a save of {ask!r} was neither made nor refused with a comment on the issue"
                break
            assert body.ask(saved) == ask, f"407.4: the owner's text {ask!r} was saved as {body.ask(saved)!r}"
            current = saved
    github.comments.clear()
    assert_open("407.4", draw(monkeypatch, github, "A plain ask.", []), "A plain ask.", [])
    assert not github.comments, "407.4: a plain ask was refused"


# 407.5: AGENTS.md says a new issue's text shows open until it has a plan

def test_agents_md_says_the_text_shows_open_until_planned(record_property):
    """AGENTS.md says the owner's text shows open until planned, then folds.

    Proves 407.5.
    Reads AGENTS.md's The issue body section and checks one sentence says an issue with no plan shows the owner's
    text open with its Definition of Done below it, that the text folds under Original issue once a plan exists, and
    that it no longer says a new issue's Definition of Done sits below the Original issue fold."""
    record_property("proves", "407.5")
    text = open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read()
    m = re.search(r"^## The issue body\n(.*?)(?=^## )", text, flags=re.S | re.M)
    assert m, "407.5: AGENTS.md has no '## The issue body' section"
    section = m.group(1)
    sentences = re.split(r"(?<=[.;])\s+", section)
    assert any("no plan" in s and " open" in s and "Definition of Done" in s for s in sentences), \
        "407.5: AGENTS.md's The issue body does not say an issue with no plan shows the owner's text open, " \
        "with its Definition of Done"
    assert any("Original issue" in s and re.search(r"\bplan(ned)?\b", s) and "fold" in s and "no plan" not in s
               for s in sentences), \
        "407.5: AGENTS.md's The issue body does not say the owner's text folds under Original issue once planned"
    assert "Definition of Done sits below the Original issue fold" not in section, \
        "407.5: AGENTS.md's The issue body still says a new issue's Definition of Done sits below the Original issue fold"
    assert "Code only writes above the marker" in section and "checks the owner's part is unchanged" in section, \
        "407.5: AGENTS.md's The issue body no longer says code keeps the owner's part unchanged"

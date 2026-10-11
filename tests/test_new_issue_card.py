"""A new issue shows the owner's text first, then the Definition of Done, with no "no plan yet".

Issue #371. The owner asked (2026-10-09) that when an issue is first posted and has no plan yet, the Definition of
Done line no longer comes before the owner's original issue text: it moves below that text, and the line "This issue
has no plan yet." goes away. Since #407 the owner's text shows open below the card's marker until the issue has a plan,
so on an issue with no plan the body reads: the card's status and link lines, the owner's text, then the Definition of
Done. Once the issue has a plan, the card is drawn as before, with the Definition of Done at its bottom, above the
owner's text in its closed Original issue fold.

The card is drawn by dokima/card.py render and saved by card.draw through dokima/body.py, which keeps the owner's text
byte for byte or refuses. These tests run card.draw with GitHub faked by the recorder in tests/test_body.py, and read
the body it saves the way the owner reads the issue.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dokima import body, card, plan  # noqa: E402
from test_body import TRICKY, github  # noqa: E402,F401

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
SRC = "https://github.com/o/r/issues/40"
FOLD_START = "\n<details><summary>Original issue</summary>\n\n"
FOLD_END = "\n\n</details>"
DOD = "**Definition of Done:**"
SUMMARY = "Every new issue reads its owner's words first."
PLAN = {"kind": "user_story", "summary": SUMMARY, "user_story": "The owner reads their own words first.",
        "acceptance_criteria": [{"text": "The owner's text comes first.", "source": SRC}],
        "non_functional": [], "scope": ["dokima/card.py"], "out_of_scope": [], "tests": {}}
ASKS = ("Please show my words first.\n", TRICKY, "",
        "<details><summary>My own fold</summary>\n\nA detail I folded myself.\n\n</details>\n")
# Today's card on a new issue: the no-plan line and the Definition of Done above the owner's folded text.
OLD_TOP = ("<!-- dokima-card -->\n**Backlog**\n\n[issue #40](https://github.com/o/r/issues/40)\n\n"
           "This issue has no plan yet.\n\n**Definition of Done:** All tests · Code review · Owner approval\n\n"
           "<!-- /dokima-card -->")


def rec(role, passed=True, **handback):
    """One agent record, as dokima.agent.records reads it from a bot comment."""
    return {"role": role, "stage": None, "handback": handback, "check": {"passed": passed, "problems": []},
            "run": "https://github.com/o/r/actions/runs/1", "run_id": "1"}


NO_PLAN = {"no record": [], "only a rejected plan": [rec("planner", passed=False, **PLAN)]}


def found_for(recs):
    """What issue #40's card is drawn from: these records, no PR, checks or reviews."""
    return {"recs": list(recs), "items": [], "pr": None, "check_runs": [], "reviews": [], "owners": {"boss"},
            "tests": {}, "worker": None, "children": []}


def issue_of(current):
    return {"number": 40, "title": "t", "url": SRC, "approved_at": None, "changes": [], "plan": None,
            "current_body": current, "body": current, "state": "open"}


TOPS = []


def draw(monkeypatch, github, current, recs, changed_only=False):
    """Run the card's draw on issue #40 with no PR; return the body saved, or None.

    The issue's body is `current`.
    Every card the draw renders is kept in TOPS, so a test can check the saved body against the card drawn now."""
    render = card.render

    def keep(*a, **kw):
        TOPS.append(render(*a, **kw))
        return TOPS[-1]
    monkeypatch.setattr(card, "render", keep)
    monkeypatch.setattr(card.plan, "fetch_issue", lambda repo, n: issue_of(current))
    monkeypatch.setattr(card, "gather", lambda repo, n, p: found_for(recs))
    monkeypatch.setattr(card, "github_links", lambda repo, n, cache: {"blocked_by": [], "blocks": [], "loop": []})
    monkeypatch.setattr(card, "their_links", lambda *a, **k: {"relates_to": []})
    saves = len(github.saves)
    card.draw(REPO, 40, None, changed_only=changed_only)
    return github.saves[-1] if len(github.saves) > saves else None


def without_comments(text):
    """The text as the owner sees it: HTML comments taken out."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def assert_new_issue_layout(k, saved, ask, recs):
    """Fail naming k unless the body reads: card, owner's open text, Definition of Done.

    The card above the marker holds the status line and no Definition of Done; the owner's text follows byte for byte,
    open, not folded (#407); after it comes exactly the Definition of Done line the card draws, and nothing else the
    owner can see."""
    assert saved is not None, f"{k}: the card saved nothing on the issue"
    assert saved.count(body.MARKER) == 1, f"{k}: expected exactly one marker, found {saved.count(body.MARKER)}"
    top, below = saved.split(body.MARKER, 1)
    assert "**Backlog**" in top, f"{k}: the card above the owner's text lost its status line:\n{top}"
    assert DOD not in top, f"{k}: the Definition of Done still comes before the owner's text:\n{top}"
    fold = "\n\n" + ask
    assert below.startswith(fold) and not below.startswith(FOLD_START), \
        f"{k}: the owner's text does not come first below the card, byte for byte and open:\n{below!r}"
    after = without_comments(below[len(fold):]).strip()
    expected = card.done_row(REPO, found_for(recs), None)
    assert after == expected, \
        f"{k}: below the owner's text the issue should show only the Definition of Done line, not:\n{after!r}"
    assert saved.count(DOD) == ask.count(DOD) + 1, f"{k}: the Definition of Done shows {saved.count(DOD)} times"
    assert body.ask(saved) == ask, f"{k}: the owner's text does not read back byte for byte"


# 371.1: a card with no plan has no "This issue has no plan yet." line

def test_a_card_with_no_plan_has_no_no_plan_line(record_property, monkeypatch, github):
    """A new issue's card no longer says "This issue has no plan yet.".

    Proves 371.1. Draws the card of an issue with no record and of one with only a rejected plan, and checks neither
    the card nor the saved issue says it has no plan yet, while both still show the status line and the Definition of
    Done; an issue with a plan shows its summary, as before."""
    record_property("proves", "371.1")
    for name, recs in NO_PLAN.items():
        drawn = card.render(REPO, issue_of("My ask."), found_for(recs))
        saved = draw(monkeypatch, github, "My ask.", recs)
        for where, text in (("card", drawn), ("saved issue", saved or "")):
            assert "no plan yet" not in text.lower(), f"371.1: with {name}, the {where} still says it has no plan yet"
            assert "**Backlog**" in text and DOD in text, \
                f"371.1: with {name}, the {where} lost its status line or its Definition of Done:\n{text}"
    planned = card.render(REPO, issue_of("My ask."), found_for([rec("planner", **PLAN)]))
    assert SUMMARY in planned and "no plan yet" not in planned.lower(), \
        "371.1: a card with a plan does not show its summary, or says it has no plan"


# 371.2: on an issue with no plan, the owner's text comes first and the Definition of Done below it

def test_a_new_issue_shows_the_owners_text_then_the_definition_of_done(record_property, monkeypatch, github):
    """On a new issue the owner's text comes first, the Definition of Done below it.

    Proves 371.2. Draws the card of an issue with no plan (no record, or only a rejected plan) for four asks (plain
    words, one full of Windows line ends and stray markup, an empty one and one with the owner's own fold), and
    checks the saved issue shows the status line above the marker with no Definition of Done there, then the owner's
    text byte for byte and open (#407), then the Definition of Done line and nothing else."""
    record_property("proves", "371.2")
    for name, recs in NO_PLAN.items():
        for ask in ASKS:
            assert_new_issue_layout(f"371.2 ({name})", draw(monkeypatch, github, ask, recs), ask, recs)
    assert not github.comments, "371.2: drawing a new issue's card posted a refusal"


def test_an_issue_showing_todays_card_moves_its_definition_of_done_below(record_property, monkeypatch, github):
    """An issue showing today's card moves its Definition of Done below on its next redraw.

    Proves 371.2. Builds issues saved with today's card (the no-plan line and the Definition of Done above the owner's
    folded text), with the owner's text open as before #373, and fresh with no marker, redraws each with no plan, and
    checks each now reads the card, the owner's text, then the Definition of Done."""
    record_property("proves", "371.2")
    for ask in ASKS:
        for current in (body.redraw(ask, OLD_TOP), OLD_TOP + "\n\n" + body.MARKER + "\n\n" + ask, ask):
            assert_new_issue_layout("371.2", draw(monkeypatch, github, current, []), ask, [])


def test_a_new_issues_card_is_not_rewritten_when_nothing_changed(record_property, monkeypatch, github):
    """A saved new issue is not rewritten by the sweep and matches what the scan expects.

    Proves 371.2. Draws a new issue's card, then draws it again the way the 15-minute sweep does (only when it
    changed) and checks nothing is saved; drawn again in full it saves the very same body; and the card check the
    scan uses (card.shows) finds the saved issue shows the card Dokima draws now, so no card is flagged or rewritten
    forever."""
    record_property("proves", "371.2")
    for ask in ASKS:
        saved = draw(monkeypatch, github, ask, [])
        assert_new_issue_layout("371.2", saved, ask, [])
        assert draw(monkeypatch, github, saved, [], changed_only=True) is None, \
            "371.2: the sweep rewrote a new issue's card that had not changed"
        assert draw(monkeypatch, github, saved, []) == saved, "371.2: redrawing a new issue's card changed its body"
        assert card.shows(saved, TOPS[-1]), "371.2: the scan's card check says a freshly saved new issue is out of date"


# 371.3: once the issue has a plan, the Definition of Done stays at the bottom of the card, above the owner's text

def test_a_planned_issue_keeps_its_definition_of_done_in_the_card(record_property, monkeypatch, github):
    """Once planned, the Definition of Done is the card's last line, above the owner's text.

    Proves 371.3. Saves a new issue's card with no plan and checks its Definition of Done sits below the owner's
    text, then records a plan and redraws, and checks the Definition of Done shows exactly once, as the card's last line above the marker,
    and the owner's text is alone in its Original issue fold with nothing after it."""
    record_property("proves", "371.3")
    for ask in ASKS:
        fresh = draw(monkeypatch, github, ask, [])
        assert_new_issue_layout("371.3", fresh, ask, [])
        for current in (fresh, ask):
            recs = [rec("planner", **PLAN)]
            saved = draw(monkeypatch, github, current, recs)
            assert saved is not None, "371.3: the card saved nothing on the planned issue"
            top, below = saved.split(body.MARKER, 1)
            below = re.sub(r"\n\n<!-- dokima-done -->\n[^\n]*$", "", below)  # since #416 Done sits last, after the fold
            assert below == FOLD_START + ask + FOLD_END, \
                f"371.3: with a plan, something other than the owner's fold sits below the card:\n{below!r}"
            # Since #416 the Definition of Done is the body's last line, once, below the Original issue fold.
            last = saved.rstrip("\n").splitlines()[-1]
            assert saved.count(DOD) == ask.count(DOD) + 1 and last.startswith(DOD) and SUMMARY in top, \
                f"371.3: with a plan, the Definition of Done is not the body's last line once: {last!r}"


# 371.4: the owner's text is never changed: kept byte for byte, or the save is refused and says why

ODD_ASKS = ("My ask.\n\n**Definition of Done:** my own idea of done\n",
            "My ask.\n\n</details>\n\n<!-- a comment of mine -->\n**Definition of Done:** x",
            "I quoted the card's end.\n<!-- /dokima-card -->\n\n</details>\n\n")


def test_the_owners_text_is_kept_or_the_save_refused(record_property, monkeypatch, github):
    """The owner's text is kept byte for byte, or the save is refused and says why.

    Proves 371.4. Draws a new issue's card on asks that hold their own Definition of Done line, a closing fold and
    comments, and the card's own end marker, then redraws with a plan; at every save the owner's text reads back
    exactly as written, a saved new issue shows that text first and its Definition of Done below it, and a save that cannot keep it is refused with a comment on the issue, never saved altered. A plain ask
    is saved, not refused."""
    record_property("proves", "371.4")
    for ask in ODD_ASKS:
        for recs in ([], [rec("planner", **PLAN)]):
            comments = len(github.comments)
            saved = draw(monkeypatch, github, ask, recs)
            if saved is None:
                assert len(github.comments) > comments, \
                    f"371.4: a save of {ask!r} was neither made nor refused with a comment on the issue"
                continue
            assert body.ask(saved) == ask, f"371.4: the owner's text {ask!r} was saved as {body.ask(saved)!r}"
            if not recs:
                assert_new_issue_layout("371.4", saved, ask, recs)
            again = draw(monkeypatch, github, saved, [rec("planner", **PLAN)])
            assert again is None or body.ask(again) == ask, \
                f"371.4: a later redraw changed the owner's text {ask!r} into {body.ask(again)!r}"
    github.comments.clear()
    assert draw(monkeypatch, github, "A plain ask.", []) is not None and not github.comments, \
        "371.4: a plain ask was refused"


# 371.5: AGENTS.md says where a new issue's Definition of Done sits

def test_agents_md_says_a_new_issues_definition_of_done_sits_below_the_owners_text(record_property):
    """AGENTS.md says a new issue's Definition of Done sits below the owner's text.

    Proves 371.5. Reads AGENTS.md's The issue body section and checks it names the Definition of Done and says where
    it sits on an issue with no plan, below the owner's text (open since #407), and still says code never changes the
    owner's text."""
    record_property("proves", "371.5")
    text = open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read()
    m = re.search(r"^## The issue body\n(.*?)(?=^## )", text, flags=re.S | re.M)
    assert m, "371.5: AGENTS.md has no '## The issue body' section"
    section = m.group(1)
    sentences = [s for s in re.split(r"(?<=[.;])\s+", section) if "Definition of Done" in s]
    assert any("no plan" in s and "below" in s for s in sentences), \
        "371.5: AGENTS.md's The issue body does not say an issue with no plan shows its Definition of Done below the " \
        "owner's text"
    assert "Code only writes above the marker" in section and "checks the owner's part is unchanged" in section, \
        "371.5: AGENTS.md's The issue body no longer says code keeps the owner's part unchanged"

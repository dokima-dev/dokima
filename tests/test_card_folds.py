"""Scope shows as code on one line; Out of scope, requirements and the owner's text fold.

Issue #373. The owner asked (2026-10-09) that on the issue and PR card the Scope lists its files as code fields,
`dokima/card.py`, all on one line instead of one line per file, and that the original issue text, the non-functional
requirements and Out of scope sit in folds, closed by default. Answering the plan's question (2026-10-10), the owner
added that the PR card also carries the original issue text in its own fold, so the issue and PR cards stay identical.

The card is drawn by dokima/card.py render (the same card on the issue and the PR, which card.pr_body saves on the PR);
the owner's text below the card's marker is kept by dokima/body.py redraw and saved by the card's main and the planner,
and card.pr_body(card, pr_body, ask) puts the same Original issue fold on the PR, between the card and its Closes line.
These tests draw the card from records the way tests/test_card_records.py does and redraw bodies the way
tests/test_body.py does, with GitHub faked by its recorder.
"""
import os
import re
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dokima import agent, body, card, planner  # noqa: E402
from test_body import PLAN_TOP, TRICKY, github, run_card, text_of  # noqa: E402,F401

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPO = "o/r"
ISSUE = {"number": 40, "url": "https://github.com/o/r/issues/40"}
SRC = "https://github.com/o/r/issues/40"
SCOPE = ["dokima/card.py", "tests/test_card.py", "dokima/body.py::redraw"]
OUT = ["The journey diagram; that's another issue.", "Run comments keep their own folds."]
NFR = [{"text": "A refused save says why.", "why": "nothing fails silently", "principle": "Fail closed"}]


def plan_of(scope=SCOPE, out=OUT, nfr=NFR):
    return {"kind": "user_story", "summary": "Cards fold what the owner rarely reads.",
            "user_story": "The owner reads a short card.",
            "acceptance_criteria": [{"text": "Scope shows on one line.", "source": SRC}],
            "non_functional": nfr, "scope": scope, "out_of_scope": out, "tests": {}}


def rec(role, stage=None, **handback):
    return {"role": role, "stage": stage, "handback": handback, "check": {"passed": True, "problems": []},
            "run": "https://github.com/o/r/actions/runs/1"}


def cards(**kw):
    """The issue card and the PR description, for a plan with `kw` replaced."""
    found = {"recs": [rec("planner", **plan_of(**kw))], "pr": None, "check_runs": [], "reviews": [],
             "owners": {"boss"}, "tests": {}, "worker": None}
    issue_card = card.render(REPO, ISSUE, found, page="issue")
    drawn = card.render(REPO, ISSUE, dict(found, pr={"number": 5, "merged": False, "state": "open"}), page="pr")
    pr_card = card.pr_body(drawn, "Closes #40", "My ask.", issue_url=SRC)
    return {"issue card": issue_card, "PR card": pr_card}


def outside_folds(text):
    """The card's text with every fold (<details> ... </details>) taken out."""
    return re.sub(r"<details[^>]*>.*?</details>", "", text, flags=re.S)


def folds(text):
    """Every fold in the card as (opening tag, summary text, the lines inside it)."""
    found = []
    for m in re.finditer(r"(<details[^>]*>)<summary>(.*?)</summary>(.*?)</details>", text, flags=re.S):
        found.append((m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip(), m.group(3)))
    return found


def fold_named(k, where, text, title):
    """The one fold titled `title`, closed by default; fails naming criterion k otherwise."""
    named = [f for f in folds(text) if f[1] == title]
    assert len(named) == 1, f"{k}: the {where} has {len(named)} folds titled {title!r}, expected exactly one:\n{text}"
    tag, _, inside = named[0]
    assert tag == "<details>", f"{k}: the {title} fold on the {where} is not closed by default: {tag}"
    return inside


# 373.1: Scope lists its files as code on one line, separated by commas

def test_scope_shows_every_file_as_code_on_one_line(record_property):
    """Scope lists every file as code on one line, comma separated, on both cards.

    Proves 373.1. Draws the card of a plan with three scope entries and checks both cards hold exactly the line
    **Scope:** `dokima/card.py`, `tests/test_card.py`, `dokima/body.py::redraw`, in the plan's order, and no line
    per file anywhere; a plan with one file shows just that file as code."""
    record_property("proves", "373.1")
    for where, text in cards().items():
        lines = text.splitlines()
        scope_lines = [ln for ln in lines if "Scope:" in ln and "Out of scope" not in ln]
        assert scope_lines == ["**Scope:** `dokima/card.py`, `tests/test_card.py`, `dokima/body.py::redraw`"], \
            f"373.1: the {where} does not show Scope as code on one line, comma separated; its Scope lines are {scope_lines}"
        for path in SCOPE:
            assert sum(path in ln for ln in lines) == 1, f"373.1: on the {where}, {path} shows on more than one line"
            assert not any(re.match(rf"\s*-\s*`?{re.escape(path)}`?\s*$", ln) for ln in lines), \
                f"373.1: on the {where}, {path} still has a line of its own"
    for where, text in cards(scope=["app/jobs.py"]).items():
        assert "**Scope:** `app/jobs.py`" in text.splitlines(), \
            f"373.1: the {where} does not show a one-file Scope as **Scope:** `app/jobs.py`"


# 373.2: Out of scope and the non-functional requirements sit in folds, closed by default

def test_out_of_scope_sits_in_a_closed_fold(record_property):
    """Out of scope sits in a closed fold on the issue and PR cards.

    Proves 373.2. Draws the card of a plan with two Out of scope sentences and checks each sits inside one closed
    fold titled Out of scope, with no Out of scope heading or sentence left open on the card; Scope stays open
    beside it."""
    record_property("proves", "373.2")
    for where, text in cards().items():
        inside = fold_named("373.2", where, text, "Out of scope")
        for sentence in OUT:
            assert sentence in inside, f"373.2: on the {where}, {sentence!r} is not inside the Out of scope fold"
        rest = outside_folds(text)
        assert "Out of scope" not in rest, f"373.2: the {where} still shows an Out of scope heading outside its fold"
        assert not any(s in rest for s in OUT), f"373.2: the {where} still shows an Out of scope sentence open"
        assert "**Scope:** `dokima/card.py`" in rest, f"373.2: the {where} folded Scope too; it should stay open"


def test_non_functional_requirements_sit_in_a_closed_fold_beside_out_of_scope(record_property):
    """The non-functional requirements sit in their own closed fold on both cards.

    Proves 373.2. Draws the card of a plan with a non-functional requirement and checks it is inside one closed fold
    titled Non-functional requirements and nowhere open on the card, and that Out of scope has its own closed fold."""
    record_property("proves", "373.2")
    for where, text in cards().items():
        inside = fold_named("373.2", where, text, "Non-functional requirements")
        assert NFR[0]["text"] in inside, f"373.2: on the {where}, the requirement is not in its fold"
        assert NFR[0]["text"] not in outside_folds(text), f"373.2: on the {where}, the requirement also shows open"
        fold_named("373.2", where, text, "Out of scope")


# 373.3: the owner's original issue text sits in a fold titled Original issue, closed by default

ASKS = ("Please fold my words.\n- [ ] Goal: an old goal\n", TRICKY, "",
        "<details><summary>My own fold</summary>\n\nA detail I folded myself.\n\n</details>\n")
FOLD_START = "\n<details><summary>Original issue</summary>\n\n"
FOLD_END = "\n\n</details>"


def assert_folded(k, new, ask):
    """Fail naming criterion k unless the owner's text sits alone in a closed fold.

    It must sit below the one marker, byte for byte, and read back as written."""
    assert new.count(body.MARKER) == 1, f"{k}: expected exactly one marker, found {new.count(body.MARKER)}"
    below = re.sub(r"\n\n<!-- dokima-done -->\n[^\n]*$", "", new.split(body.MARKER, 1)[1])  # since #416 Done sits last, after the fold
    assert below == FOLD_START + ask + FOLD_END, \
        f"{k}: the owner's text is not alone inside a closed Original issue fold below the card:\n{below!r}"
    assert body.ask(new) == ask, f"{k}: the owner's text does not read back byte for byte"


def open_body(top, ask):
    """A body saved before this change, the owner's text open below the marker."""
    return top.rstrip("\n") + "\n\n" + body.MARKER + "\n\n" + ask


def test_the_owners_text_is_folded_below_the_card(record_property):
    """The owner's text sits below the card in a closed fold titled Original issue.

    Proves 373.3. Redraws four asks (plain words, one full of Windows line ends and stray markup, an empty one and
    one with the owner's own fold) fresh and again, and checks each sits byte for byte inside one closed Original
    issue fold below the card, the same after every redraw."""
    record_property("proves", "373.3")
    for ask in ASKS:
        new = body.redraw(ask, "the card")
        assert new.split(body.MARKER, 1)[0].strip() == "the card", "373.3: the card is not alone above the marker"
        assert_folded("373.3", new, ask)
        again = body.redraw(new, "another card")
        assert_folded("373.3", again, ask)


def test_an_open_ask_folds_on_its_next_redraw(record_property):
    """An ask that shows open today folds under Original issue on its next redraw.

    Proves 373.3. Builds bodies with the owner's text open below the marker, as saved before this change, redraws
    each and checks it is saved, not refused, with the text byte for byte in the closed Original issue fold."""
    record_property("proves", "373.3")
    for ask in ASKS:
        try:
            new = body.redraw(open_body("old card", ask), "new card")
        except body.Refused as e:
            pytest.fail(f"373.3: folding an open ask was refused: {e}")
        assert_folded("373.3", new, ask)


def test_the_card_and_the_planner_fold_the_owners_text(record_property, monkeypatch, github):
    """The card and the planner both save the owner's text folded under Original issue.

    Proves 373.3. Runs the card's main on a fresh ask and on an ask open today, and the planner's render on a fresh
    ask, and checks every saved body keeps the owner's text byte for byte in the closed Original issue fold with no
    refusal posted; a split's quoted story stays folded the same way."""
    record_property("proves", "373.3")
    for current in (TRICKY, open_body(PLAN_TOP, TRICKY)):
        saved = run_card(monkeypatch, github, current)
        assert saved is not None, "373.3: the card saved nothing on the issue"
        assert_folded("373.3", saved, TRICKY)
    assert not github.comments, "373.3: folding the owner's text posted a refusal"
    story = {"objective": "Fold the ask", "criteria": ["The ask is folded"], "non_goals": [],
             "scope": ["dokima/body.py"], "test_changes": {}}
    assert_folded("373.3", planner.render("9", "My own words.", story, {}), "My own words.")
    quoted = agent.story_body(230, 4, {"title": "Folds", "user_story": "Folded.", "context": "c",
                                       "acceptance_criteria": [{"text": "Folded.", "source": SRC}],
                                       "non_functional": []}, "Cards show everything")
    assert_folded("373.3", body.redraw(quoted, "the card"), quoted)


def test_a_redraw_that_would_change_the_folded_text_is_refused(record_property):
    """A redraw that would change the owner's folded text is still refused.

    Proves 373.3. A good one goes through. Draws a card that holds the marker itself on a folded ask and on an ask
    open today, and checks each is refused with a reason, while a plain card on the same bodies folds the text as
    written."""
    record_property("proves", "373.3")
    for current in (body.redraw("My ask.", "old card"), open_body("old card", "My ask.")):
        with pytest.raises(body.Refused) as refused:
            body.redraw(current, f"a card that quotes {body.MARKER} in a criterion")
        assert str(refused.value).strip(), "373.3: the refusal gives no reason"
        assert_folded("373.3", body.redraw(current, "a card"), "My ask.")


# 373.3: the PR card carries the same Original issue fold, so the issue and PR cards stay identical

PR = 5


def draw_both(monkeypatch, github, current, pr_text, changed_only=False):
    """Run the card's draw on issue 40 and its open PR 5, returning both saved bodies.

    Returns (the issue body saved, the PR description written), each None when not written. GitHub is faked: the issue's text is `current`, the PR's description `pr_text`, and the card is drawn from one
    plan record, as tests/test_body.py run_card does."""
    issue = {"number": 40, "title": "t", "url": SRC, "approved_at": None, "changes": [], "plan": None,
             "current_body": current, "body": current}
    pr = {"number": PR, "merged": False, "state": "open", "body": pr_text, "head": {"sha": "abc", "ref": "try/issue-40"}}
    found = {"recs": [rec("planner", **plan_of())], "pr": pr, "check_runs": [], "reviews": [], "owners": {"boss"},
             "tests": {}, "worker": None}
    monkeypatch.setattr(card.plan, "fetch_issue", lambda repo, n: issue)
    monkeypatch.setattr(card, "gather", lambda repo, n, p: dict(found))
    monkeypatch.setattr(card, "github_links", lambda repo, n, cache: {"blocked_by": [], "blocks": [], "loop": []})
    monkeypatch.setattr(card, "their_links", lambda *a, **k: {"relates_to": []})
    saves, calls = len(github.saves), len(github.calls)
    card.draw(REPO, 40, PR, changed_only=changed_only)
    written = [text_of(c, {}) for c in github.calls[calls:] if "PATCH" in c and any(a.endswith(f"pulls/{PR}") for a in c)]
    return (github.saves[-1] if len(github.saves) > saves else None), (written[-1] if written else None)


CLOSES_40 = f"Closes {SRC}"


def on_pr(top):
    """The issue's card as the PR shows it, with the issue's link back.

    Since #452 only the PR's top row links the issue."""
    return top.replace(f"https://github.com/o/r/pull/{PR}", f"{SRC} · https://github.com/o/r/pull/{PR}", 1)


def assert_pr_folded(k, pr_text, top, ask, closes=CLOSES_40):
    """Fail naming criterion k unless the PR shows the card, the owner's fold, then its Closes line.

    `top` is the issue's card; the PR shows it with the issue's own link back in its top row (#452). The owner's text
    must sit byte for byte in one closed Original issue fold, followed only by the closing line."""
    top = on_pr(top)
    fold = FOLD_START + ask + FOLD_END
    assert pr_text is not None, f"{k}: the PR description was not written"
    assert pr_text.startswith(top.rstrip("\n")), f"{k}: the PR description does not open with the card:\n{pr_text!r}"
    rest = pr_text[len(top.rstrip("\n")):]
    assert rest.count(fold) == 1, \
        f"{k}: the PR does not carry the owner's text byte for byte in one closed Original issue fold:\n{rest!r}"
    before, after = rest.split(fold, 1)
    assert not before.replace(body.MARKER, "").strip(), f"{k}: something other than the marker sits between the card " \
                                                         f"and the Original issue fold on the PR: {before!r}"
    after = re.sub(r"^\s*<!-- dokima-done -->\n[^\n]*", "", after)  # since #416 Done sits right after the fold
    assert not after.strip(), f"{k}: after the fold the PR should end, with no Closes line since #416, not {after!r}"
    assert [f for f in folds(pr_text) if f[1] == "Original issue"][0][0] == "<details>", \
        f"{k}: the Original issue fold on the PR is not closed by default"


QUOTED_STORY = agent.story_body(230, 4, {"title": "Folds", "user_story": "Folded.", "context": "c",
                                         "acceptance_criteria": [{"text": "Folded.", "source": SRC}],
                                         "non_functional": []}, "Cards show everything")


def test_the_pr_card_carries_the_same_original_issue_fold(record_property, monkeypatch, github):
    """The PR card carries the same closed Original issue fold as the issue.

    Proves 373.3. Draws the card of an issue and its open PR for five asks (plain words, one full of Windows line ends
    and stray markup, an empty one, one with the owner's own fold and a split's quoted story), each fresh and open
    today, and checks the PR description is the card, then the owner's text byte for byte in one closed Original issue
    fold, the very fold the issue shows, then the PR's Closes line by the issue's full address; a PR with no Closes
    line gains one (#452)."""
    record_property("proves", "373.3")
    for ask in ASKS + (QUOTED_STORY,):
        for current in (ask, open_body("old card", ask)):
            saved, pr_text = draw_both(monkeypatch, github, current, "old card\n\nCloses #40")
            assert saved is not None, "373.3: the card saved nothing on the issue"
            assert_folded("373.3", saved, ask)
            top = saved.split(body.MARKER, 1)[0]
            assert_pr_folded("373.3", pr_text, top, ask)
            assert saved.split(body.MARKER, 1)[1] in pr_text, \
                "373.3: the PR's Original issue fold is not the very fold the issue shows"
    saved, pr_text = draw_both(monkeypatch, github, "My ask.", "A PR with no closing line.")
    assert_pr_folded("373.3", pr_text, saved.split(body.MARKER, 1)[0], "My ask.")


def test_an_old_pr_card_gains_the_fold_on_its_next_redraw(record_property, monkeypatch, github):
    """An older PR card gains the Original issue fold on its next redraw, then stays.

    Proves 373.3. The 15-minute sweep redraws only cards that changed: a PR whose description is today's card and
    Closes line, with no fold, is rewritten with the fold; one that already carries it is left alone, so the sweep
    neither misses old PRs nor rewrites every PR every time."""
    record_property("proves", "373.3")
    saved, _ = draw_both(monkeypatch, github, "My ask.", "Closes #40")
    top = saved.split(body.MARKER, 1)[0].rstrip("\n")
    github.saves.clear()
    _, pr_text = draw_both(monkeypatch, github, saved, on_pr(top) + "\n\n" + CLOSES_40, changed_only=True)
    assert pr_text is not None, "373.3: an old PR card with no Original issue fold was not redrawn by the sweep"
    assert_pr_folded("373.3", pr_text, top, "My ask.")
    _, again = draw_both(monkeypatch, github, saved, pr_text, changed_only=True)
    assert again is None, f"373.3: a PR that already carries the fold was rewritten again:\n{again!r}"


# 373.4: AGENTS.md says the owner's text is folded, so every agent reads the decision

def issue_body_section():
    text = open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read()
    m = re.search(r"^## The issue body\n(.*?)(?=^## )", text, flags=re.S | re.M)
    assert m, "373.4: AGENTS.md has no '## The issue body' section"
    return m.group(1)


def test_agents_md_says_the_owners_text_is_folded(record_property):
    """AGENTS.md says the owner's ask is folded under Original issue, on the issue and PR.

    Proves 373.4. Reads AGENTS.md's The issue body section and checks it names the Original issue fold, closed by
    default, says the pull request carries the same fold, no longer says the ask is open or that a folded ask opens,
    and still says code writes only above the marker."""
    record_property("proves", "373.4")
    section = issue_body_section()
    assert "Original issue" in section and "closed by default" in section, \
        "373.4: AGENTS.md's The issue body does not say the owner's ask is folded under Original issue, closed by default"
    assert "pull request" in section, \
        "373.4: AGENTS.md's The issue body does not say the pull request carries the same Original issue fold"
    for stale in ("open, exactly as written", "opens on its next redraw", "keeps it folded under Original issue"):
        assert stale not in section, f"373.4: AGENTS.md's The issue body still says {stale!r}"
    assert "Code only writes above the marker" in section, \
        "373.4: AGENTS.md's The issue body no longer says code only writes above the marker"


# 373.5: the owner's text on the PR never closes or links another issue

KEYWORDS = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s+(?:(?:[\w.-]+/[\w.-]+)?#\d+"
                      r"|https://github\.com/[\w.-]+/[\w.-]+/(?:issues|pull)/\d+)", re.I)


def test_the_owners_closing_words_on_the_pr_close_nothing(record_property, monkeypatch, github):
    """The owner's "fixes #99", copied onto the PR, closes nothing; the PR still closes its issue.

    Proves 373.5. GitHub closes every issue a PR's description names after a closing keyword, and Dokima reads the
    PR's issue from its first one. Draws the PR of an ask that says "fixes #99", "Closes: #12", "resolved o/r#7"
    and plain "#5", twice, and checks the only closing reference on the PR, by GitHub's keywords and by Dokima's own
    readers (agent.issue_of_pr), is the PR's own trailing Closes line, by the issue's full address since #452, that
    each `#` after a keyword is written `&#35;` (which shows the same), that the plain #5 and the issue's own copy are
    untouched, and that a second redraw keeps that Closes line."""
    record_property("proves", "373.5")
    ask = "This fixes #99.\nCloses: #12 and resolved o/r#7, see #5.\n"
    shown = "This fixes &#35;99.\nCloses: &#35;12 and resolved o/r&#35;7, see #5.\n"
    saved, pr_text = draw_both(monkeypatch, github, ask, "Closes #40")
    assert_folded("373.5", saved, ask)
    top = saved.split(body.MARKER, 1)[0]
    assert_pr_folded("373.5", pr_text, top, shown)
    found = [m.group(0) for m in KEYWORDS.finditer(pr_text)]
    # Since #416 the PR carries no Closes line; the owner's words still close nothing.
    assert found == [], f"373.5: the PR's description holds closing references: {found}"
    assert agent.issue_of_pr("", pr_text) is None, "373.5: Dokima reads the PR's issue from the owner's words"
    _, again = draw_both(monkeypatch, github, saved, pr_text)
    assert again is None or KEYWORDS.findall(again) == [], \
        f"373.5: a second redraw picked up a closing reference from the owner's words:\n{again!r}"
